#!/usr/bin/env python3
"""Quick lookups over the exported features (local helper for Phase 2/3 alignment).

  xref.py callers win 0xe06b60        functions calling a function
  xref.py callees mac 0x4872f60       callees in call order
  xref.py info win 0xc53910           size, strings, consts, callers/callees counts
  xref.py match 0xc53910              matcher's Mac counterpart (Windows RVA in)
  xref.py rmatch 0x4861420            matcher's Windows counterpart (Mac RVA in)
  xref.py range mac 0x48622c0 0x4862890   functions whose entry is in [a, b]
  xref.py globalrefs win 0x56f3c28    functions touching a data global
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workdir import FEATURES as FEAT   # $FM27_WORK_DIR/features
FILES = {"win": "game_plugin.dll.jsonl", "mac": "game_plugin_x86_64.jsonl"}


def load(side):
    funcs = {}
    with open(FEAT / FILES[side]) as fh:
        for i, line in enumerate(fh):
            if i:
                d = json.loads(line)
                funcs[d["rva"]] = d
    return funcs


def h(x):
    return int(x, 16)


def main():
    cmd = sys.argv[1]
    if cmd in ("match", "rmatch"):
        m = json.loads((FEAT / "all_matches_x86_64.json").read_text())
        if cmd == "match":
            print(m.get(hex(h(sys.argv[2]))))
        else:
            want = hex(h(sys.argv[2]))
            print([(w, v) for w, v in m.items() if v[0] == want])
        return
    side = sys.argv[2]
    f = load(side)
    if cmd == "callers":
        t = h(sys.argv[3])
        for r, d in f.items():
            if t in d["callees"]:
                print(hex(r), d["insns"], d["name"], d["strings"][:3])
    elif cmd == "callees":
        d = f[h(sys.argv[3])]
        print("calls in order:", [hex(c) for c in d.get("calls", [])])
    elif cmd == "info":
        d = f.get(h(sys.argv[3]))
        if not d:
            print("no function at", sys.argv[3])
            return
        print({k: (v[:12] if isinstance(v, list) else v) for k, v in d.items()})
        print("globals:", [hex(g) for g in d["globals"][:20]])
    elif cmd == "range":
        a, b = h(sys.argv[3]), h(sys.argv[4])
        for r in sorted(f):
            if a <= r <= b:
                d = f[r]
                print(hex(r), d["insns"], d["name"], d["strings"][:2], "calls:", [hex(c) for c in d.get("calls", [])][:8])
    elif cmd == "globalrefs":
        g = h(sys.argv[3])
        for r, d in f.items():
            if g in d["globals"]:
                print(hex(r), d["insns"], d["name"], d["strings"][:2])


if __name__ == "__main__":
    main()
