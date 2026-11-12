"""Keep every match FM27 saves: FM27 keeps only your last 10 in matches/automatic and deletes older ones.

sync() copies each saved match (*_VER_fm.pkm) that is not in the backup yet into the backup folder, by competition,
and never deletes anything. It also keeps the game's inputs for other clubs' matches, which FM27 leaves for a while in
its Temporary folder (*.apm); scripts/import_other_matches.py turns them into matches the app and the scripts open.
The app, scripts/study.py and scripts/optimise.py call it and then read matches from the backup, so a match is kept
as long as one of them runs before FM27 has saved 10 newer ones (or run scripts/backup_matches.py yourself).

Backup folder: FM27_MATCH_BACKUP, default ~/fm27-port-work/saved_matches (FM27_WORK_DIR moves the default with it).
FM27_SAVED_MATCHES still overrides everything: matches are then read from that folder only, with no backup.
The backup holds your own matches (with your manager name inside); it stays outside the repository.
"""
import os, shutil
from pathlib import Path

GAME = Path.home() / 'Library/Application Support/Sports Interactive/Football Manager 27/matches/automatic'
TEMPORARY = GAME.parents[1] / 'Temporary'   # the game's inputs for other clubs' matches (*.apm), deleted by the game later


def backup_folder():
    custom = os.environ.get('FM27_MATCH_BACKUP')
    if custom: return Path(custom).expanduser()
    return Path(os.environ.get('FM27_WORK_DIR') or Path.home() / 'fm27-port-work').expanduser() / 'saved_matches'


def copy_new(files, folder):
    copied = 0
    for f in files:
        dest = folder / f.name
        if dest.is_file() and dest.stat().st_size == f.stat().st_size: continue
        try:
            folder.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix('.part'); shutil.copy2(f, tmp); tmp.replace(dest); copied += 1
        except OSError:
            continue   # a file FM27 is still writing: picked up next time
    return copied


def sync(sources=None):
    """Copy new saved matches (and the game's other-club match inputs) into the backup; returns the number copied."""
    target = backup_folder(); copied = copy_new(sorted(TEMPORARY.glob('*.apm')), target / 'temporary') if TEMPORARY.is_dir() else 0
    sources = sources if sources is not None else [GAME]
    for source in sources:
        if not source.is_dir(): continue
        for folder in sorted(p for p in source.iterdir() if p.is_dir()):
            copied += copy_new(sorted(folder.glob('*_VER_fm.pkm')), target / folder.name)
    return copied


def source_folder():
    """Where saved matches are read from: FM27_SAVED_MATCHES if set, else the backup (synced first)."""
    custom = os.environ.get('FM27_SAVED_MATCHES')
    if custom: return Path(custom).expanduser()
    sync()
    target = backup_folder()
    return target if target.is_dir() else GAME
