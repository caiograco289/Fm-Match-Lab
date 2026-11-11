"""Make one of your own saved matches the app's sample match (replaces the sample from upstream's release).

Copies the match file into private/engine/fm27_native/fixtures/match.pkm and asks the host to dump its match input
(--dump-input --inspect-fixture: read only, nothing is played). The dump serves as the editor's default, advanced and
set-piece snapshots, exactly as for any saved match the app opens.

  .venv/bin/python scripts/prepare_sample.py [MATCH_VER_fm.pkm]     # default: your newest saved match

Needs Steam running, FM27 closed and the host built (scripts/build_native_mac.py).
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE = Path(os.environ.get('FM27_ENGINE_ROOT') or ROOT / 'private/engine') / 'fm27_native'
SAVED = Path.home() / 'Library/Application Support/Sports Interactive/Football Manager 27/matches/automatic'
SNAPSHOTS = ('editor_manual_default.json', 'editor_advanced_snapshot.json', 'editor_setpieces_default.json')


def newest():
    files = sorted(SAVED.glob('**/*_VER_fm.pkm'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files: raise SystemExit(f'No saved matches in {SAVED}. Play a match in FM27 (instant result is fine) first.')
    return files[0]


def main():
    source = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else newest()
    host = NATIVE / 'fm27_mac_host'
    if not host.is_file(): raise SystemExit('Build the host first: .venv/bin/python scripts/build_native_mac.py')
    with tempfile.TemporaryDirectory() as folder:
        snapshot, log = Path(folder) / 'snapshot.json', Path(folder) / 'inspect.jsonl'
        env = {k: v for k, v in os.environ.items() if not k.startswith('FM27_MAC_')}
        code = subprocess.run([str(host), '--fixture', str(source), '--dump-input', str(snapshot), '--inspect-fixture',
                               '--output', str(log)], env=env, capture_output=True, timeout=120).returncode
        if code or not snapshot.is_file():
            raise SystemExit(f'The engine could not read {source.name} (exit {code}). A match saved by another game version '
                             'needs that version; pick a match saved by your installed FM27.')
        data = json.loads(snapshot.read_text(encoding='utf8'))
        (NATIVE / 'fixtures').mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, NATIVE / 'fixtures/match.pkm')
        for name in SNAPSHOTS: (NATIVE / name).write_text(json.dumps(data), encoding='utf8')
    print(f'Sample match: {source.name} (seed {data.get("match", {}).get("seed")})')


if __name__ == '__main__':
    main()
