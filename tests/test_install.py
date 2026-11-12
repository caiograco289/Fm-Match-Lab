"""The one-line installer: it parses under macOS's own bash 3.2 (what `curl ... | bash` runs), and the README shows
the line the script itself prints."""
import re, subprocess, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/install.sh'


class InstallerTests(unittest.TestCase):
    @unittest.skipUnless(Path('/bin/bash').is_file(), 'needs /bin/bash')
    def test_parses_under_system_bash(self):
        c = subprocess.run(['/bin/bash', '-n', str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(c.returncode, 0, c.stderr)

    def test_readme_shows_the_same_line(self):
        line = re.search(r'^LINE="(.+)"$', SCRIPT.read_text(encoding='utf8'), re.M).group(1)
        self.assertIn(line, (ROOT / 'README.md').read_text(encoding='utf8'))

    def test_runs_everything_inside_main(self):   # a partly downloaded script must not run part-way
        self.assertEqual(SCRIPT.read_text(encoding='utf8').rstrip().splitlines()[-1], 'main "$@" < /dev/null')


if __name__ == '__main__':
    unittest.main()
