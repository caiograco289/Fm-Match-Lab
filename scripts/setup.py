"""One-off set-up from your own FM27 install (and again after a game update).

  1. builds the engine host for the installed FM27 (scripts/build_native_mac.py);
  2. builds the tactic catalogue and the set-piece options from the game's own data (scripts/build_catalog.py);
  3. makes one of your saved matches the sample match, unless one is already set (scripts/prepare_sample.py).

Everything it writes goes to the git-ignored private/ folder. Needs Steam running and logged in, FM27 closed, the
Xcode command line tools, and UnityPy for step 2 (.venv/bin/pip install UnityPy).

  .venv/bin/python scripts/setup.py [--sample MATCH_VER_fm.pkm] [--game-root DIR]
"""
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'private'


def step(title, args):
    print(f'\n== {title}', flush=True)
    if subprocess.run([sys.executable, *map(str, args)], cwd=ROOT).returncode: raise SystemExit(f'{title}: failed')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--sample', help='saved match to use as the sample (default: your newest)')
    p.add_argument('--game-root', help='FM27 install, if it is not found automatically')
    a = p.parse_args()
    if subprocess.run(['pgrep', '-f', 'fm.app/Contents/MacOS/Football Manager 27'], capture_output=True).returncode == 0:
        raise SystemExit('Close FM27 first.')
    step('Engine host', [ROOT / 'scripts/build_native_mac.py', *(['--game-root', a.game_root] if a.game_root else [])])
    step('Tactic catalogue', [ROOT / 'scripts/build_catalog.py', '--out', PRIVATE / 'catalog.json',
                              '--setpieces', PRIVATE / 'engine/fm27_research/setpiece_enum_catalog.json'])
    if a.sample or not (PRIVATE / 'engine/fm27_native/fixtures/match.pkm').is_file():
        step('Sample match', [ROOT / 'scripts/prepare_sample.py', *([a.sample] if a.sample else [])])
    print('\nReady: .venv/bin/python scripts/run.py, then open http://127.0.0.1:18765')


if __name__ == '__main__':
    main()
