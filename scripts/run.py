"""Run the source edition in a browser; Ctrl+C stops the loopback service."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ASSETS = ('fm27_native/editor_manual_default.json', 'fm27_native/editor_advanced_snapshot.json',
          'fm27_native/editor_setpieces_default.json', 'fm27_native/fixtures/match.pkm', 'fm27_research/setpiece_enum_catalog.json')

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import desktop_platform  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def stage_source(destination):
    destination.mkdir(parents=True, exist_ok=True)
    for path in (ROOT / 'src').rglob('*'):
        if path.is_file() and path.suffix in {'.py', '.js', '.css', '.html'} and '__pycache__' not in path.parts:
            target = destination / path.relative_to(ROOT / 'src')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    shutil.copy2(ROOT / 'private/catalog.json', destination / 'tactics_ui/catalog.json')


def check_inputs():
    needed = [ROOT / 'private/engine' / name for name in ASSETS]
    needed += [ROOT / 'private/catalog.json',
               ROOT / 'private/engine/fm27_native' / desktop_platform.HOST_NAME,
               ROOT / 'private/engine/fm27_native/engine_compat_profile.json']
    missing = [str(path.relative_to(ROOT)) for path in needed if not path.is_file()]
    if missing:
        raise ValueError('Run the set-up first (.venv/bin/python scripts/setup.py). Missing:\n' + '\n'.join(missing))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', type=Path, help='FM27 install (optional; Steam libraries are searched)')
    parser.add_argument('--port', type=int, default=18765)
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12) or not desktop_platform.IS_MAC:
        raise SystemExit('Requires Python 3.12 on macOS, with FM27 for macOS installed and Steam running.')
    if args.game_root is None:
        args.game_root = desktop_platform.find_game_root()
        if args.game_root is None:
            raise SystemExit('FM27 for macOS not found; pass --game-root.')
    check_inputs()
    source = ROOT / 'build/source'
    stage_source(source)
    data = ROOT / 'data'
    data.mkdir(exist_ok=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith('FM27_')}
    env.update(FM27_ENGINE_ROOT=str(ROOT / 'private/engine'), FM27_GAME_ROOT=str(args.game_root.resolve()),
               FM27_DESKTOP_DATA=str(data), PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    print(f'Open http://127.0.0.1:{args.port} after the service reports ready.', flush=True)
    try:
        subprocess.run([sys.executable, str(source / 'desktop_server.py'), '--port', str(args.port)],
                       env=env, check=True)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
