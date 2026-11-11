"""Prepare the public repository: a separate git repository that never contains this repository's history.

Copies every tracked file of the current commit into DEST (a new folder the first time, the same folder for later
updates), removes files no longer tracked, commits under the anonymous identity, and runs the tests there with
FM27_PUBLISH_CHECK=1 (anonymous authors only, UTC commit times, no personal terms, no game files). It never pushes: it prints the
command for you to run once you have checked the result.

  .venv/bin/python scripts/public_snapshot.py DEST [-m "message"]

DEST should be outside this repository. Your git-ignored private/personal_terms.txt is copied to DEST's own ignored
private/ folder so the check can use it; it is never committed.
"""
import argparse, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME, EMAIL = 'FM27 Match Lab', 'fm27-match-lab@users.noreply.invalid'


def git(cwd, *args, env=None):
    r = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, env=env)
    if r.returncode: raise SystemExit(f'git {" ".join(args)} failed in {cwd}:\n{r.stderr}')
    return r.stdout


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('dest'); p.add_argument('-m', '--message')
    a = p.parse_args()
    dest = Path(a.dest).expanduser().resolve()
    if dest == ROOT or ROOT in dest.parents: raise SystemExit('DEST must be outside this repository')
    if git(ROOT, 'status', '--porcelain', '--untracked-files=no').strip():
        raise SystemExit('Commit or stash your changes first: the snapshot is taken from the current commit.')
    first = not (dest / '.git').is_dir()
    if first:
        dest.mkdir(parents=True, exist_ok=True)
        git(dest, 'init', '-q', '-b', 'main')
    git(dest, 'config', 'user.name', NAME); git(dest, 'config', 'user.email', EMAIL)
    tracked = [f for f in git(ROOT, 'ls-files', '-z').split('\0') if f]
    for f in git(dest, 'ls-files', '-z').split('\0'):   # files removed here are removed there
        if f and f not in tracked: (dest / f).unlink(missing_ok=True)
    for f in tracked:
        target = dest / f; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / f, target)
    terms = ROOT / 'private/personal_terms.txt'
    if terms.is_file():
        (dest / 'private').mkdir(exist_ok=True); shutil.copy2(terms, dest / 'private/personal_terms.txt')
    else:
        print('warning: no private/personal_terms.txt; the personal-terms check will be skipped')
    git(dest, 'add', '-A')
    if not git(dest, 'status', '--porcelain').strip():
        print('Nothing changed since the last snapshot.'); return
    source = git(ROOT, 'rev-parse', '--short', 'HEAD').strip()
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+0000')   # no local time zone in the public history
    utc = dict(os.environ, TZ='UTC', GIT_AUTHOR_DATE=now, GIT_COMMITTER_DATE=now)
    git(dest, 'commit', '-q', '-m', a.message or ('FM27 Match Lab for macOS' if first else 'Update'), env=utc)
    env = dict(os.environ, FM27_PUBLISH_CHECK='1')
    r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', 'tests'], cwd=dest, env=env, capture_output=True, text=True)
    print(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else '')
    if r.returncode:
        if first: git(dest, 'update-ref', '-d', 'HEAD')   # undo the commit, keep the files for inspection
        else: git(dest, 'reset', '-q', '--soft', 'HEAD~1')
        raise SystemExit(f'Publish checks FAILED; nothing to push. Output:\n{r.stderr[-3000:]}')
    log = git(dest, 'log', '--format=%h %an <%ae> %s', '-n', '3')
    print(f'Snapshot of {source} committed in {dest}:\n{log}')
    remote = git(dest, 'remote').strip()
    if not remote:
        print('Next (once): git -C "%s" remote add origin https://github.com/<account>/<repository>.git' % dest)
    print('To publish:  git -C "%s" push -u origin main' % dest)


if __name__ == '__main__':
    main()
