#!/usr/bin/env python3
"""Call-site voting: independent evidence for a Windows->Mac function mapping.

For a Windows target T, every Windows caller C that has a matched Mac twin C' votes:
the ordered call lists of C and C' are aligned (LCS over calls already matched elsewhere),
and the Mac call in the same gap position as T is the vote. Protected Windows stubs are
resolved to their protected body RVA, which is what callers' ordered call lists contain.

Usage: callsite_vote.py <win rva>...      (prints votes)
       callsite_vote.py --targets         (all code targets; writes port/map/callsite_votes.json)
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from workdir import FEATURES as FEAT   # $FM27_WORK_DIR/features
PROT = re.compile(r"EXT_FUN_([0-9a-fA-F]+)$")


def load(name):
    funcs = {}
    base = 0
    with open(FEAT / name) as fh:
        for i, line in enumerate(fh):
            d = json.loads(line)
            if i == 0:
                base = int(d["meta"]["image_base"], 16)
                continue
            funcs[d["rva"]] = d
    return funcs, base


def lcs_pairs(a, b):
    """Index pairs (i, j) of an LCS of a and b; None in a never matches."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            dp[i][j] = dp[i + 1][j + 1] + 1 if a[i] is not None and a[i] == b[j] else max(dp[i + 1][j], dp[i][j + 1])
    i = j = 0
    out = []
    while i < n and j < m:
        if a[i] is not None and a[i] == b[j]:
            out.append((i, j))
            i += 1
            j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1
    return out


class Voter:
    def __init__(self):
        self.win, self.wbase = load("game_plugin.dll.jsonl")
        self.mac, _ = load("game_plugin_x86_64.jsonl")
        m = json.loads((FEAT / "all_matches_x86_64.json").read_text())
        self.w2m = {int(w, 16): int(v[0], 16) for w, v in m.items()}
        self.callers = defaultdict(set)
        for r, d in self.win.items():
            for c in d.get("calls", []):
                self.callers[c].add(r)

    def key(self, t):
        d = self.win.get(t)
        if d and d.get("thunk"):
            mm = PROT.search(d["name"])
            if mm:
                return int(mm.group(1), 16) - self.wbase
        return t

    def votes(self, t):
        k = self.key(t)
        tally = Counter()
        detail = []
        for c in self.callers.get(k, ()):
            cm = self.w2m.get(c)
            if cm is None or cm not in self.mac:
                continue
            sw = self.win[c].get("calls", [])[:256]
            sm = self.mac[cm].get("calls", [])[:256]
            mapped = [None if x == k else self.w2m.get(x) for x in sw]
            pairs = lcs_pairs(mapped, sm)
            if len(pairs) < 1:
                continue
            anchors = [(-1, -1)] + pairs + [(len(sw), len(sm))]
            for i, x in enumerate(sw):
                if x != k:
                    continue
                before = max(p for p in anchors if p[0] < i)
                after = min(p for p in anchors if p[0] > i)
                if after[0] - before[0] == after[1] - before[1]:
                    j = before[1] + (i - before[0])
                    if 0 <= j < len(sm):
                        tally[sm[j]] += 1
                        detail.append((hex(c), hex(cm)))
        return k, tally, detail


def main():
    v = Voter()
    if sys.argv[1:] == ["--targets"]:
        targets = json.loads((ROOT / "port" / "map" / "targets.json").read_text())["targets"]
        out = {}
        for t in targets:
            if not t["region"].startswith("code"):
                continue
            w = int(t["win_rva"], 16)
            k, tally, _ = v.votes(w)
            out[t["win_rva"]] = {"key": hex(k), "votes": {hex(a): n for a, n in tally.most_common(5)},
                                 "callers_voting": sum(tally.values())}
        (ROOT / "port" / "map" / "callsite_votes.json").write_text(json.dumps(out, indent=1) + "\n")
        for w, r in out.items():
            print(w, r["key"], r["votes"])
        return
    for a in sys.argv[1:]:
        k, tally, detail = v.votes(int(a, 16))
        print(a, "key", hex(k), {hex(x): n for x, n in tally.most_common(5)}, "via", detail[:4])


if __name__ == "__main__":
    main()
