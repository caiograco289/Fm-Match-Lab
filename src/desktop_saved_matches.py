"""Matches saved by FM27 itself as bases for the scenario editor (macOS).

FM27 stores the matches it plays as instant results or watches (not holiday matches on 27.0.1) under
matches/automatic/<Competition>/<Home>_v_<Away>_<seed>_VER_fm.pkm. Opening one copies it into the app's data folder
(the game may delete old matches) and reads its teams with the host (--inspect-fixture --dump-input: no simulation).
The scenario editor then works on the real squads; an unedited scenario on the match's own seed replays it exactly
(same engine build), and every edit is a what-if on top of the saved match. Nothing is written to the game's folder.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

NAME = re.compile(r'^(?P<home>.+)_v_(?P<away>.+)_(?P<seed>\d+)_VER_fm\.pkm$')
GAME_VERSIONS = {0x1b000000: '27.0', 0x1b000100: '27.0.1'}
KEY = re.compile(r'^saved:[0-9a-f]{16}$')


def source_folder():
    custom = os.environ.get('FM27_SAVED_MATCHES')
    if custom: return Path(custom)
    return Path.home() / 'Library/Application Support/Sports Interactive/Football Manager 27/matches/automatic'


def management(word):
    """Who ran a side in the saved match, from its manager input flags (manager+0x30d0): bit 0 = you (managed or
    watched: your own recorded decisions replay, a watched side makes none); assistant bits (instant result,
    holiday: 0x25306) = your assistant; otherwise the AI."""
    if word & 1: return 'human'
    if word & 0x1306: return 'assistant'
    return 'ai'


def game_version(word):
    return GAME_VERSIONS.get(word, f'0x{word:08x}' if isinstance(word, int) else None)


class SavedMatches:
    def __init__(self, app):
        self.app = app
        self.root = Path(os.environ['FM27_DESKTOP_DATA']) / 'saved_matches'
        self.lock = threading.Lock(); self.bases = {}; self.digests = {}

    def digest(self, path):
        stat = path.stat(); stamp = (str(path), stat.st_mtime_ns, stat.st_size)
        if stamp not in self.digests: self.digests[stamp] = hashlib.sha256(path.read_bytes()).hexdigest()
        return self.digests[stamp]

    def info(self, key):
        path = self.root / key.split(':')[1] / 'info.json'
        return json.loads(path.read_text(encoding='utf8')) if path.is_file() else None

    def list(self):
        folder = source_folder(); rows = []
        for path in (folder.glob('*/*_VER_fm.pkm') if folder.is_dir() else []):
            match = NAME.match(path.name)
            if not match: continue
            stat = path.stat(); key = 'saved:' + self.digest(path)[:16]; info = self.info(key)
            rows.append({'path': str(path), 'competition': path.parent.name.replace('_', ' '), 'home': match['home'].replace('_', ' '),
                         'away': match['away'].replace('_', ' '), 'seed': int(match['seed']), 'modified': stat.st_mtime, 'key': key,
                         'opened': info is not None, 'game_version': info and info['game_version'], 'managed_by': self.managed_by(key)})
        known = {r['key'] for r in rows}
        for folder_ in (sorted(self.root.iterdir()) if self.root.is_dir() else []):   # opened earlier, since removed by the game
            info = self.info('saved:' + folder_.name)
            if info and info['key'] not in known:
                rows.append({**{k: info[k] for k in ('competition', 'home', 'away', 'seed', 'key', 'game_version')}, 'path': None,
                             'modified': info['source_modified'], 'opened': True, 'kept_copy_only': True})
        rows.sort(key=lambda r: -r['modified'])
        return {'folder': str(folder), 'available': folder.is_dir(), 'installed_engine_version': self.app.desktop_platform.mac_engine_version(self.app.NATIVE),
                'installed_game_version': game_version(self.app.desktop_platform.mac_engine_version(self.app.NATIVE)), 'matches': rows}

    def managed_by(self, key):
        path = self.root / key.split(':')[1] / 'snapshot.json'
        if not path.is_file(): return None
        return [management(t['manager_input_flags']) for t in json.loads(path.read_text(encoding='utf8'))['teams']]

    def open(self, path):
        """Copy a saved match into the data folder and read its teams; returns its base."""
        source = Path(str(path)).resolve(); folder = source_folder().resolve()
        if folder not in source.parents or not NAME.match(source.name) or not source.is_file():
            raise ValueError('Only FM27  automatically saved match files can be opened (matches/automatic)')
        digest = self.digest(source); key = 'saved:' + digest[:16]
        with self.lock:
            if key in self.bases: return self.bases[key]
            target = self.root / digest[:16]
            if not (target / 'info.json').is_file():
                if target.exists(): shutil.rmtree(target)
                target.mkdir(parents=True)
                shutil.copy2(source, target / 'match.pkm')
                if hashlib.sha256((target / 'match.pkm').read_bytes()).hexdigest() != digest: raise ValueError('Match file copy failed verification')
                self.inspect(target)
                snapshot = json.loads((target / 'snapshot.json').read_text(encoding='utf8'))
                match = NAME.match(source.name); word = snapshot['match']['engine_version']
                info = {'key': key, 'sha256': digest, 'source': str(source), 'source_modified': source.stat().st_mtime,
                        'competition': source.parent.name.replace('_', ' '), 'home': match['home'].replace('_', ' '), 'away': match['away'].replace('_', ' '),
                        'seed': snapshot['match']['seed'], 'engine_version': word, 'game_version': game_version(word), 'opened': time.time()}
                if info['seed'] != int(match['seed']): raise ValueError('Match file seed does not match the file name')
                (target / 'info.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf8')
            return self.load(key)

    def inspect(self, target):
        app = self.app
        env = {k: v for k, v in os.environ.items() if not k.startswith(('FM27_IMPORT_', 'FM27_EXPORT_', 'FM27_MAC_'))}
        env.update(FM27_ENGINE_PATH='fixture', FM27_GAME_ROOT=os.environ.get('FM27_GAME_ROOT', ''),
                   FM27_EXPECTED_DLL_SHA256=os.environ.get('FM27_EXPECTED_DLL_SHA256', ''))
        with app.IMPORT_LOCK:
            app.desktop_engine.require_available(app.ENGINE_COMPATIBILITY)
            try:
                result = subprocess.run([str(app.NATIVE / app.desktop_platform.HOST_NAME), '--fixture', str(target / 'match.pkm'),
                                         '--dump-input', str(target / 'snapshot.json'), '--inspect-fixture', '--output', str(target / 'inspect.jsonl')],
                                        cwd=app.ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
            except subprocess.TimeoutExpired: raise ValueError('Reading the match file timed out')
        if result.returncode or not (target / 'snapshot.json').is_file():
            raise ValueError(f'The game’s engine could not read this match file (exit code {result.returncode}); a match saved by a different game version needs that version’s engine')

    def load(self, key):
        info = self.info(key); folder = self.root / key.split(':')[1]
        if not info: raise ValueError('Saved match has not been opened')
        snapshot = json.loads((folder / 'snapshot.json').read_text(encoding='utf8'))
        info = {k: info[k] for k in ('key', 'competition', 'home', 'away', 'seed', 'engine_version', 'game_version', 'sha256')}
        info['managed_by'] = [management(t['manager_input_flags']) for t in snapshot['teams']]
        info['installed_game_version'] = game_version(self.app.desktop_platform.mac_engine_version(self.app.NATIVE))
        info['exact_replay'] = info['engine_version'] == self.app.desktop_platform.mac_engine_version(self.app.NATIVE)
        base = self.app.MatchBase(key, snapshot, folder / 'match.pkm', True, f"{info['home']} v {info['away']}",
                                  team_names=[info['home'], info['away']], info=info)
        self.bases[key] = base
        return base

    def base(self, key):
        if not isinstance(key, str) or not KEY.match(key): raise ValueError('Scenario format or match sample does not match')
        with self.lock:
            return self.bases.get(key) or self.load(key)
