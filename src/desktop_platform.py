"""macOS platform layer for the desktop service.

The native host is `fm27_mac_host` (x86_64, runs under Rosetta) and loads the unchanged
`game_plugin.bundle` from the user's FM27 install; Steam must be running and logged in.
"""
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

IS_MAC = sys.platform == 'darwin'   # the tool runs on macOS only; scripts/run.py refuses anything else
HOST_NAME = 'fm27_mac_host'
MAC_APP_ID = '4530370'


def mac_engine_version(native):
    """Engine version word of the installed build (written by scripts/build_native_mac.py; 27.0 default)."""
    import json
    try:return int(json.loads((Path(native)/'engine_compat_profile.json').read_text(encoding='utf8')).get('engine_version',0x1b000000))
    except (OSError,ValueError):return 0x1b000000


def host_path(native):
    return Path(native) / HOST_NAME


def data_dir():
    """Default per-user state folder."""
    return Path.home() / 'Library/Application Support/FMTacticsLabMac'


def steam_libraries():
    """Steam library folders from libraryfolders.vdf (as FMSuperScout's server does)."""
    root = Path.home() / 'Library/Application Support/Steam'
    folders = [root]
    vdf = root / 'steamapps/libraryfolders.vdf'
    try:
        folders += [Path(p.replace('\\\\', '\\')) for p in re.findall(r'"path"\s+"([^"]+)"', vdf.read_text(encoding='utf8', errors='replace'))]
    except OSError:
        pass
    return list(dict.fromkeys(folders))


def find_game_root():
    """The folder holding FM27's engine resources: on macOS game_plugin.bundle/Contents/Resources."""
    for library in steam_libraries():
        game = library / 'steamapps/common/Football Manager 27'
        candidate = mac_resources(game)
        if candidate and candidate.is_dir():
            return candidate
    return None


def mac_resources(path):
    """Accept the Steam game folder, fm.app, the bundle or Resources itself."""
    path = Path(path)
    for candidate in (path, path / 'Contents/Resources', path / 'Contents/PlugIns/game_plugin.bundle/Contents/Resources',
                      path / 'fm.app/Contents/PlugIns/game_plugin.bundle/Contents/Resources'):
        if (candidate / '../MacOS/game_plugin').is_file() and (candidate / 'icudt65l.dat').is_file():
            return candidate.resolve()
    return None


def engine_files(game):
    """Engine files whose identity and availability gate a session."""
    game = Path(game)
    frameworks = game / '../Frameworks'
    files = {'game_plugin': game / '../MacOS/game_plugin', 'icudt65l.dat': game / 'icudt65l.dat',
             'shared/data/simatch.fmf': game / 'shared/data/simatch.fmf',
             'shared/data/simatchshared.fmf': game / 'shared/data/simatchshared.fmf'}
    for name in ['libsteam_api.dylib', 'libEOSSDK-Mac-Shipping.dylib']:
        files['Frameworks/' + name] = frameworks / name
    return files, files['game_plugin']


class FileLease:
    """Keeps an engine file open for the session and detects replacement."""
    def __init__(self, path):
        self.path = Path(path)
        self.stream = open(self.path, 'rb')
        stat = os.fstat(self.stream.fileno())
        self.identity = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)

    def unchanged(self):
        try:
            stat = os.stat(self.path)
        except OSError:
            return False
        return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns) == self.identity

    def close(self):
        self.stream.close()


def memory_available_gib():
    try:
        total = int(subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True, timeout=5).stdout)
        return total // (1024 ** 3) // 2   # half of physical memory
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return 8


class FileCancellation:
    """Per-match cancellation: the host polls for this file (`--cancel-event` takes its path)."""
    def __init__(self, folder=None):
        folder = Path(folder or os.environ.get('TMPDIR', '/tmp'))
        self.name = str(folder / f'fm27_cancel_{os.getpid()}_{uuid.uuid4().hex}')
        self.handle = None

    def signal(self):
        Path(self.name).touch()

    def close(self):
        try:
            os.unlink(self.name)
        except OSError:
            pass


def choose_file(title, patterns):
    """Native file picker (AppleScript); returns None when cancelled."""
    script = f'POSIX path of (choose file with prompt "{title}")'
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    path = result.stdout.strip()
    return path or None
