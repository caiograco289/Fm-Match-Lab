"""Copy every match FM27 has saved into the backup folder (FM27 keeps only your last 10). Never deletes anything.

  .venv/bin/python scripts/backup_matches.py [--from FOLDER ...]   # --from: also import an older copy of saved matches

The app, study.py and optimise.py do this themselves each time they start; run it by hand (or on a schedule) if you
play more than 10 matches between runs. See src/match_backup.py.
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import match_backup

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('--from', dest='sources', nargs='+', default=[], help='other folders of saved matches to import')
a = p.parse_args()
n = match_backup.sync([match_backup.GAME] + [Path(s).expanduser() for s in a.sources])
total = len(list(match_backup.backup_folder().glob('*/*_VER_fm.pkm')))
print(f'{n} new; {total} saved matches in {match_backup.backup_folder()}')
