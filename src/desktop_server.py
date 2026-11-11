"""Isolated desktop service, using the existing native engine installation."""
import os
import desktop_platform
from pathlib import Path
import sys

root=Path(os.environ['FM27_ENGINE_ROOT']).resolve()
required=['fm27_native/'+desktop_platform.HOST_NAME,'fm27_native/editor_manual_default.json','fm27_native/editor_advanced_snapshot.json','fm27_native/editor_setpieces_default.json','fm27_research/setpiece_enum_catalog.json']
missing=[name for name in required if not(root/name).is_file()]
if missing:raise SystemExit('Engine workspace is incomplete: '+', '.join(missing))
from fm27_tactics_server import main
main()
