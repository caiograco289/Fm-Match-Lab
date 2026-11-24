"""Engine integration test (needs FM27 installed, Steam running and FM27 itself closed). Opt in:
  FM27_INTEGRATION=1 .venv/bin/python -m unittest tests.test_integration
It checks native goal/card totals against the final incident registry, and replays the newest saved match twice
to check deterministic results. Compare the score with what the game showed (an exact replay matches it)."""
import glob, json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
HOST = ROOT / 'private/engine/fm27_native/fm27_mac_host'


@unittest.skipUnless(os.environ.get('FM27_INTEGRATION') == '1' and HOST.is_file(), 'opt-in engine test')
class SavedMatchReplay(unittest.TestCase):
    def run_host(self, pkm, seed, out):
        import desktop_platform
        env = dict(os.environ, FM27_ENGINE_ROOT=str(ROOT / 'private/engine'),
                   FM27_GAME_ROOT=os.environ.get('FM27_GAME_ROOT') or str(desktop_platform.find_game_root()))
        subprocess.run([str(HOST), '--fixture', pkm, '--seed', str(seed), '--output', str(out)], env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600, check=True)
        rows = [json.loads(l) for l in open(out)]
        finish = next(r for r in rows if r.get('event') == 'natural_match_finished')
        stats = next(r for r in rows if r.get('event') == 'native_match_statistics')
        return finish, stats, rows

    def test_goals_and_cards_match_native_totals(self):
        import desktop_saved_matches as sm
        import fm27_match_events
        files = sorted((f for f in glob.glob(str(sm.source_folder() / '*/*_VER_fm.pkm')) if '/Other_clubs/' not in f), key=os.path.getmtime)
        if not files: self.skipTest('no saved matches')
        pkm = files[-1]; match = sm.NAME.match(Path(pkm).name)
        self.assertIsNotNone(match)
        assert match is not None
        seed = int(match['seed'])
        with tempfile.TemporaryDirectory() as d:
            finish, _, rows = self.run_host(pkm, seed, Path(d) / 'events.jsonl')
        self.assertTrue(finish['full_match_completed'])
        identity = next(r for r in rows if r.get('event') == 'native_player_statistics_identity_verified')
        self.assertTrue(identity['verified'])
        players = next(r['players'] for r in rows if r.get('event') == 'native_player_match_totals')
        scenario = {'teams': [{'players': [p for p in players if p['side'] == side]} for side in (0, 1)]}
        events = fm27_match_events.collect(rows, scenario, {})
        self.assertTrue(events.get('scorers_verified_against_native_totals'), events['integrity'])
        self.assertTrue(events.get('cards_verified_against_native_totals'), events['integrity'])
        self.assertTrue(events['integrity']['registry_verified'], events['integrity'])
        self.assertEqual(events['integrity']['goal_differences'], [])
        self.assertEqual(events['integrity']['card_differences'], [])

    def test_replay_is_deterministic(self):
        import desktop_saved_matches as sm
        files = sorted((f for f in glob.glob(str(sm.source_folder() / '*/*_VER_fm.pkm')) if '/Other_clubs/' not in f), key=os.path.getmtime)   # your own matches
        if not files: self.skipTest('no saved matches')
        pkm = files[-1]; seed = int(sm.NAME.match(Path(pkm).name)['seed'])
        with tempfile.TemporaryDirectory() as d:
            a, sa, rows = self.run_host(pkm, seed, Path(d) / 'a.jsonl')
            b, sb, _ = self.run_host(pkm, seed, Path(d) / 'b.jsonl')
        self.assertTrue(a['full_match_completed'])
        self.assertTrue(any(r.get('event') == 'native_scenario_readback_verified' or r.get('event') == 'layout_check' for r in rows))
        self.assertEqual((a['score'], sa), (b['score'], sb))
        print(f"\n{Path(pkm).name}: {a['score'][0]}-{a['score'][1]} (compare with the game's result)")


if __name__ == '__main__':
    unittest.main()
