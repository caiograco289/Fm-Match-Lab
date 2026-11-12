"""Turn the game's inputs for other clubs' matches into matches the app and the scripts open.

FM27 leaves the input of some matches between other clubs in its Temporary folder (*.apm), and the backup keeps them
(src/match_backup.py). They are the same format as a saved match apart from the header: a type tag, one flag byte and
a version string. This script rewrites the header as a saved match's (the rest is unchanged), reads the match through
the game's own engine (seed, players), names the clubs from your newest FM27 save (by where the players are now; needs
fmsave, otherwise "Unknown"; each file is named from the first save made after it, where the players were still at
those clubs) and writes it to the backup as Other_clubs/<Home>_v_<Away>_<seed>_VER_fm.pkm.

Checked: 25 of 28 such matches, played on their own seed, give a score recorded in the save, so the game played them
on this engine with exactly this input.

  .venv/bin/python scripts/import_other_matches.py [--save SAVE.fm]

Nothing here touches the game's files; everything stays in the backup folder, outside the repository.
"""
import argparse, collections, json, os, re, subprocess, sys, tempfile, warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import match_backup

HOST = ROOT / 'private/engine/fm27_native/fm27_mac_host'
GAMES = match_backup.GAME.parents[1] / 'games'


def convert(raw):
    """The .apm bytes with a saved match's header, or None if the layout is not the known one."""
    if len(raw) < 32 or raw[2:6] != b'mpa.' or raw[8] != 1: return None
    rest = raw[9:]; n = int.from_bytes(rest[12:16], 'little')
    if n > 64: return None
    return raw[:2] + b'mkp.' + b'\x00\x00' + rest[:12] + (0).to_bytes(4, 'little') + rest[16 + n:]


def read(path, work):
    """(seed, [home player names, away player names]) through the game's engine, or None."""
    snap = work / (path.stem + '.json')
    env = {k: v for k, v in os.environ.items() if not k.startswith('FM27_MAC_')}
    r = subprocess.run([str(HOST), '--fixture', str(path), '--dump-input', str(snap), '--inspect-fixture', '--output', str(work / (path.stem + '.jsonl'))],
                       env=env, capture_output=True, timeout=120)
    if r.returncode or not snap.is_file(): return None
    s = json.loads(snap.read_text(encoding='utf8'))
    return s['match']['seed'], [[p.get('name') or '' for p in t['players']] for t in s['teams']]


def club_finder(save):
    if not save: return lambda names: 'Unknown'
    try: import fmsave
    except ImportError: print('fmsave not installed: clubs are named "Unknown"'); return lambda names: 'Unknown'
    warnings.simplefilter('ignore'); where = {}
    with fmsave.open(save) as s:
        for p in s.players():
            if p.name and p.club_name: where.setdefault(p.name, collections.Counter())[p.club_name] += 1

    def club(names):
        votes = collections.Counter(c for n in names for c in where.get(n, ()))
        if not votes: return 'Unknown'
        name, n = votes.most_common(1)[0]
        return name if n >= len(names) / 3 else 'Unknown'
    return club


def safe(name): return re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_') or 'Unknown'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--save', help='FM27 save to name the clubs from (default: the first of your saves made after each match)')
    a = p.parse_args()
    match_backup.sync()
    backup = match_backup.backup_folder(); raw_dir = backup / 'temporary'; out_dir = backup / 'Other_clubs'
    done_file = raw_dir / 'imported.json'
    done = json.loads(done_file.read_text()) if done_file.is_file() else {}
    todo = [f for f in sorted(raw_dir.glob('*.apm')) if f.name not in done]
    if not todo: print(f'nothing new; {len(list(out_dir.glob("*.pkm")))} other-club matches in {out_dir}'); return
    saves = sorted(GAMES.glob('*.fm'), key=os.path.getmtime) if GAMES.is_dir() else []
    work = Path(tempfile.mkdtemp(prefix='fm27-apm-'))

    def one(f):
        data = convert(f.read_bytes())
        if data is None: return f, 'unknown layout'
        tmp = work / (f.stem + '.pkm'); tmp.write_bytes(data)
        got = read(tmp, work)
        return f, (data, *got) if got else 'not readable by the engine'

    with ThreadPoolExecutor(6) as ex: read_ = list(ex.map(one, todo))   # read every file through the engine first
    by_save = {}   # then name the clubs, one save at a time: the first save made after the match
    for f, got in read_:
        if isinstance(got, str): done[f.name] = got; continue
        save = a.save or next((s for s in saves if os.path.getmtime(s) >= f.stat().st_mtime), saves[-1] if saves else None)
        by_save.setdefault(save, []).append((f, got))
    for save, items in by_save.items():
        club = club_finder(save)
        for f, (data, seed, players) in items:
            dest = out_dir / f'{safe(club(players[0]))}_v_{safe(club(players[1]))}_{seed}_VER_fm.pkm'
            out_dir.mkdir(parents=True, exist_ok=True); dest.write_bytes(data); os.utime(dest, (f.stat().st_atime, f.stat().st_mtime))
            done[f.name] = dest.name
    done_file.write_text(json.dumps(done, indent=1))
    ok = [r for r in done.values() if r.endswith('.pkm')]
    print(f'{len(todo)} new files: {sum(done[f.name].endswith(".pkm") for f in todo)} imported; {len(ok)} other-club matches in {out_dir}')


if __name__ == '__main__':
    main()
