"""Storage limits for rebuildable save research and desktop preparation."""
from pathlib import Path
import shutil

RESERVE_BYTES=20*1024**3

def require_space(path,additional_bytes=0):
    p=Path(path).resolve()
    while not p.exists():p=p.parent
    free=shutil.disk_usage(p).free
    if free-additional_bytes<RESERVE_BYTES:
        raise ValueError('Not enough disk space: keep at least 20 GB free; stopped writing intermediate files')

def bounded_output(path,limit_bytes=256*1024**2):
    require_space(path)
    folder=Path(path)
    size=sum(p.stat().st_size for p in folder.rglob('*')if p.is_file())if folder.exists()else 0
    if size>limit_bytes:raise ValueError('This preparation folder exceeds the 256 MB limit; check the intermediate files first')
