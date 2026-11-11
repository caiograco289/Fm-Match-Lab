"""The maintainers' local work folder (game file copies, Ghidra projects, feature dumps), outside the repository.

Set FM27_WORK_DIR to choose it; the default is ~/fm27-port-work. Nothing in it is ever committed."""
import os
from pathlib import Path

WORK_DIR = Path(os.environ.get('FM27_WORK_DIR') or Path.home() / 'fm27-port-work').expanduser()
FEATURES = WORK_DIR / 'features'
