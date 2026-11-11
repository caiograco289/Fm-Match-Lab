"""Publishing boundary: the repository must hold no game files, nothing derived from them beyond addresses, digests
and metadata, and no personal paths. Run: .venv/bin/python -m unittest discover tests"""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY_SUFFIXES = {'.exe', '.dll', '.dylib', '.so', '.bundle', '.pyd', '.pkm', '.fm', '.fmf', '.dat', '.bin', '.png'}
PRIVATE_FOLDERS = {'private', 'build', 'data', 'dist'}
HEX_RUN = re.compile(rb'[0-9a-fA-F]{65,}')            # longer than a SHA-256: would be raw bytes
PERSONAL = re.compile(rb'/Users/[A-Za-z]|sibuilder|teamcity|\.local>')


def tracked():
    out = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True).stdout
    return [Path(p) for p in out.decode().split('\0') if p]


# docs/images holds screenshots of the app in sample mode only (generic names, no save data); review each one.
class BoundaryTests(unittest.TestCase):
    def test_no_private_folders_or_binaries(self):
        bad = [str(p) for p in tracked() if p.parts[0] in PRIVATE_FOLDERS
               or (p.suffix.lower() in BINARY_SUFFIXES and not (p.parent == Path('docs/images') and p.suffix == '.png'))]
        self.assertEqual(bad, [])

    def test_no_raw_bytes_or_personal_paths(self):
        bad = []
        for p in tracked():
            if p == Path('tests/test_boundary.py'):
                continue
            data = (ROOT / p).read_bytes()
            if HEX_RUN.search(data):
                bad.append(f'{p}: hex run')
            if PERSONAL.search(data):
                bad.append(f'{p}: personal or build path')
        self.assertEqual(bad, [])

    def test_english_only(self):
        """All text is English."""
        cjk = re.compile('[一-鿿]')
        bad = [str(p) for p in tracked() if p != Path('tests/test_boundary.py')
               and p.suffix in {'.py', '.js', '.html', '.css', '.md', '.json', '.h', '.cpp'}
               and cjk.search((ROOT / p).read_text(encoding='utf-8', errors='replace'))]
        self.assertEqual(bad, [])

    def test_no_personal_terms(self):
        """Terms that must never be published (your name, user name, machine name), one per line in the git-ignored
        private/personal_terms.txt. Checked case-insensitively in every tracked file's contents and path."""
        terms_file = ROOT / 'private/personal_terms.txt'
        if not terms_file.is_file(): self.skipTest('no private/personal_terms.txt')
        terms = [t.strip().lower().encode() for t in terms_file.read_text(encoding='utf8').splitlines() if t.strip() and not t.startswith('#')]
        bad = [f'{p}: {t.decode()}' for p in tracked() for t in terms
               if t in str(p).lower().encode() or t in (ROOT / p).read_bytes().lower()]
        self.assertEqual(bad, [])

    def test_publish_identity(self):
        """Before publishing (FM27_PUBLISH_CHECK=1): every commit on the branch is by the anonymous identity, so the
        public history (scripts/public_snapshot.py) carries no names, addresses or machine names."""
        import os
        if os.environ.get('FM27_PUBLISH_CHECK') != '1': self.skipTest('set FM27_PUBLISH_CHECK=1 before publishing')
        log = subprocess.run(['git', 'log', '--format=%an <%ae>|%cn <%ce>'], cwd=ROOT, capture_output=True, check=True, text=True).stdout
        others = sorted({who for line in log.splitlines() for who in line.split('|')} - {'FM27 Match Lab <fm27-match-lab@users.noreply.invalid>'})
        self.assertEqual(others, [])

    def test_publish_utc_dates(self):
        """Before publishing (FM27_PUBLISH_CHECK=1): every author and committer date is in UTC (+0000), so the public
        history doesn't reveal the author's time zone."""
        import os
        if os.environ.get('FM27_PUBLISH_CHECK') != '1': self.skipTest('set FM27_PUBLISH_CHECK=1 before publishing')
        log = subprocess.run(['git', 'log', '--format=%ai|%ci'], cwd=ROOT, capture_output=True, check=True, text=True).stdout
        offsets = sorted({d.rsplit(' ', 1)[-1] for line in log.splitlines() for d in line.split('|')})
        self.assertEqual(offsets, ['+0000'])

    def test_private_folders_ignored(self):
        ignore = (ROOT / '.gitignore').read_text()
        for folder in ('/private/', '/build/', '/data/'):
            self.assertIn(folder, ignore)


if __name__ == '__main__':
    unittest.main()
