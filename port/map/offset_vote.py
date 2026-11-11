#!/usr/bin/env python3
"""Phase 3: vote on the Mac equivalent of a Windows struct offset (>= 0x1000).

Memory-operand displacements appear in the exported 'consts'. For Windows offset X, every Windows
function using X that has a matched Mac twin votes for each delta d (|d| <= window) such that the
twin uses X+d. The delta found in most twins wins. Only matches with string/const/callseq/decomp
evidence are used as voters when --strict is given.

Usage: offset_vote.py [--strict] 0x15380 0x14ea0 ...
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workdir import FEATURES as FEAT   # $FM27_WORK_DIR/features


def load(name):
    out = {}
    with open(FEAT / name) as fh:
        for i, line in enumerate(fh):
            if i:
                d = json.loads(line)
                out[d["rva"]] = set(d["consts"]) | set(d.get("disps", []))
    return out


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]
    win, mac = load("game_plugin.dll.jsonl"), load("game_plugin_x86_64.jsonl")
    matches = json.loads((FEAT / "all_matches_x86_64.json").read_text())
    strong = {"string", "const", "callseq", "strings_sim", "consts_sim"}
    pairs = [(int(w, 16), int(m, 16)) for w, (m, ev) in matches.items()
             if not strict or strong & set(ev)]
    for a in args:
        x = int(a, 16)
        window = 0x80 if x >= 0x1000 else 0x40
        votes, voters = Counter(), 0
        for w, m in pairs:
            if x not in win.get(w, ()) or m not in mac:
                continue
            voters += 1
            for d in {c - x for c in mac[m] if abs(c - x) <= window}:
                votes[d] += 1
        top = votes.most_common(4)
        print(f"{a}: voters={voters} " + ", ".join(f"{'+' if d >= 0 else '-'}{abs(d):#x}->{x + d:#x} ({n})" for d, n in top))


if __name__ == "__main__":
    main()
