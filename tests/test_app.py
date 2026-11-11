"""App tests that run without the game. Tests that need the private inputs (made by scripts/setup.py) are skipped
when those files are missing.
Run: .venv/bin/python -m unittest discover tests"""
import copy, json, os, re, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'port/map'))
PRIVATE = ROOT / 'private'
HAVE_PRIVATE = (PRIVATE / 'catalog.json').is_file() and (PRIVATE / 'engine/fm27_native/editor_manual_default.json').is_file()


class RecordFormula(unittest.TestCase):
    """The tactical-effectiveness accessor (port/map/exec_record.py) against the values in port/REPORT.md."""
    def test_all_bytes_equal(self):
        import exec_record
        table = {1: {0: 33, 10: 47, 25: 67, 50: 100, 100: 100}, 2: {0: 50, 25: 66, 50: 81, 100: 100},
                 3: {0: 50, 50: 75, 100: 100}, 4: {0: 25, 25: 48, 50: 70, 75: 93, 100: 100}}
        for mode, rows in table.items():
            for v, expected in rows.items():
                self.assertEqual(exec_record.value(bytes([v] * 33 + [mode]), 0), expected, (mode, v))


class SavedMatchNames(unittest.TestCase):
    def test_file_name_and_management(self):
        import desktop_saved_matches as sm
        m = sm.NAME.match('Man_City_v_Example_FC_156592098_VER_fm.pkm')
        self.assertEqual((m['home'], m['away'], m['seed']), ('Man_City', 'Example_FC', '156592098'))
        self.assertIsNone(sm.NAME.match('Man_City_v_Example_FC_156592098_fm.rec'))
        self.assertEqual(sm.management(0x25306), 'assistant')
        self.assertEqual(sm.management(0x24000), 'ai')
        self.assertEqual(sm.management(0x24001), 'human')
        self.assertEqual(sm.game_version(0x1b000100), '27.0.1')


class LineupChanges(unittest.TestCase):
    def test_substitution_and_minutes(self):
        import fm27_match_events as ev
        per = ev.CLOCK_PER_MINUTE
        scenario = {'teams': [{'players': [{'name': f'H{i}'} for i in range(14)]}, {'players': [{'name': f'A{i}'} for i in range(14)]}]}
        rows = [{'event': 'native_on_pitch_initial', 'side': s, 'roster_indices': list(range(11))} for s in (0, 1)]
        rows += [{'event': 'native_on_pitch_change', 'side': 0, 'roster_index': 9, 'on': False, 'slot': 255, 'clock': 60 * per},
                 {'event': 'native_on_pitch_change', 'side': 0, 'roster_index': 12, 'on': True, 'slot': 9, 'clock': 60 * per},
                 {'event': 'native_on_pitch_change', 'side': 1, 'roster_index': 3, 'on': False, 'slot': 3, 'clock': 30 * per},
                 {'event': 'native_on_pitch_change', 'side': 1, 'roster_index': 3, 'on': True, 'slot': 3, 'clock': 32 * per},
                 {'event': 'natural_match_finished', 'clock': 90 * per}]
        out = ev.lineup_changes(rows, scenario)
        self.assertEqual([(s['side'], s['minute'], s['off']['name'], s['on']['name']) for s in out['substitutions']], [(0, 60, 'H9', 'H12')])
        minutes = {(m['side'], m['name']): m['minutes'] for m in out['minutes']}
        self.assertEqual(minutes[(0, 'H9')], 60.0); self.assertEqual(minutes[(0, 'H12')], 30.0); self.assertEqual(minutes[(1, 'A3')], 88.0)


@unittest.skipUnless(HAVE_PRIVATE, 'private inputs not prepared')
class Catalog(unittest.TestCase):
    def test_english_labels(self):
        import catalog_en
        catalog = catalog_en.translate(json.loads((PRIVATE / 'catalog.json').read_text(encoding='utf8')))
        used = {k: catalog[k] for k in ('team_instructions', 'roles', 'player_instructions', 'mentalities', 'attributes', 'positions')}
        self.assertIsNone(re.search('[' + chr(0x4e00) + '-' + chr(0x9fff) + ']', json.dumps(used, ensure_ascii=False)))


@unittest.skipUnless(HAVE_PRIVATE, 'private inputs not prepared')
class Encoding(unittest.TestCase):
    """The server's validator and encoder on the bundled sample match (no engine run)."""
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault('FM27_ENGINE_ROOT', str(PRIVATE / 'engine'))
        os.environ.setdefault('FM27_DESKTOP_DATA', tempfile.mkdtemp())
        web = ROOT / 'src/tactics_ui/catalog.json'
        if not web.is_file(): web.write_bytes((PRIVATE / 'catalog.json').read_bytes())   # git-ignored copy
        import fm27_tactics_server
        cls.app = fm27_tactics_server

    def test_default_is_stable(self):
        a = self.app.encode_scenario(self.app.validate_scenario(copy.deepcopy(self.app.DEFAULT)))
        b = self.app.encode_scenario(self.app.validate_scenario(copy.deepcopy(self.app.DEFAULT)))
        self.assertEqual(a, b); self.assertTrue(a.startswith(b'FM27CFG1')); self.assertEqual((len(a) - 12) % 20, 0)

    def test_in_match_modes(self):
        s = copy.deepcopy(self.app.DEFAULT)
        for mode, word in (('assistant', 0x25306), ('ai', 0x24000)):
            s['teams'][0]['in_match'] = mode
            blob = self.app.encode_scenario(self.app.validate_scenario(s))
            records = [tuple(int.from_bytes(blob[12 + 20 * i + 4 * k:16 + 20 * i + 4 * k], 'little') for k in range(5)) for i in range((len(blob) - 12) // 20)]
            self.assertIn((62, 0, 0, 0, word), records)
        s['teams'][0]['in_match'] = 'nonsense'
        with self.assertRaises(ValueError): self.app.validate_scenario(s)

    def test_attribute_bounds(self):
        s = copy.deepcopy(self.app.DEFAULT); s['teams'][0]['players'][0]['attributes'][20] = 101
        with self.assertRaises(ValueError): self.app.validate_scenario(s)


if __name__ == '__main__':
    unittest.main()
