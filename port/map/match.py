#!/usr/bin/env python3
"""Phase 2 step 3: match Windows game_plugin.dll functions to the Mac slice.

Inputs (outside the repo, produced by port/ghidra_scripts/ExportFunctionFeatures.java):
  $FM27_WORK_DIR/features/game_plugin.dll.jsonl
  $FM27_WORK_DIR/features/game_plugin_<slice>.jsonl
Output: port/map/rva_map.json (RVAs + evidence only; no game bytes).

Evidence kinds (the plan needs >= 2 independent kinds for "verified"):
  string     - shares a string that only this function references on both sides
  const      - shares a distinctive constant unique to this function on both sides
  strings_sim- high Jaccard similarity of all referenced strings (with >= 2 strings)
  consts_sim - high overlap of distinctive constants (>= 3 shared)
  callgraph  - unique best candidate among callers/callees of an already matched pair
  callseq    - the function's calls to already matched functions occur in the same order on both
               sides (LCS >= 3 calls and >= 60% of the longer sequence). Structural: compares the body,
               not how the pair was found, but it builds on other matches, so it's weaker than string/const
  size       - instruction count within a compiler-tolerant ratio (supporting only, never sufficient)
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from workdir import FEATURES as FEAT   # $FM27_WORK_DIR/features

# Constants that are compiler/ABI noise rather than program meaning.
def keep_const(v):
    if v >= 0xFFFF0000 and v <= 0xFFFFFFFF:      # small negative 32-bit (stack offsets)
        return False
    if v >= 0xFFFFFFFFFFFF0000:                     # small negative 64-bit
        return False
    if v in (0x7FFFFFFF, 0x80000000, 0xFFFF, 0x10000, 0x7FFFFFFFFFFFFFFF, 0x8000000000000000):
        return False
    return True


PROTECTED_RE = re.compile(r"EXT_FUN_([0-9a-fA-F]+)$")


def load(path, image_base=None):
    """Load features. On Windows, functions whose bodies were moved into the excluded `.sbss`
    section are seen only as EXT_FUN_<va> call targets (or thunk_EXT_FUN_<va> stubs). Each gets a
    body-less pseudo node (protected=True) keyed by its RVA, so it can be matched through callers."""
    funcs = {}
    meta = None
    pending_ext = defaultdict(set)   # caller rva -> protected rvas
    thunk_to = {}
    with open(path) as fh:
        for i, line in enumerate(fh):
            d = json.loads(line)
            if i == 0 and "meta" in d:
                meta = d["meta"]
                continue
            base = int(meta["image_base"], 16) if meta else 0
            for s_ in d["strings"]:
                mm = PROTECTED_RE.search(s_) if s_.startswith("@import:") else None
                if mm:
                    pending_ext[d["rva"]].add(int(mm.group(1), 16) - base)
            mm = PROTECTED_RE.search(d["name"]) if d.get("thunk") else None
            if mm:
                thunk_to[d["rva"]] = int(mm.group(1), 16) - base
            d["strings"] = [s for s in d["strings"] if not s.startswith("@import:")]
            d["consts"] = [c for c in d["consts"] if keep_const(c)]
            d["sset"] = frozenset(d["strings"])
            d["cset"] = frozenset(d["consts"])
            funcs[d["rva"]] = d
    for caller, prots in pending_ext.items():
        for p_ in prots:
            funcs[caller]["callees"].append(p_)
    for p_ in set(thunk_to.values()) | {p_ for v in pending_ext.values() for p_ in v}:
        funcs.setdefault(p_, {"rva": p_, "size": 0, "insns": 0, "name": f"protected_{p_:x}", "callers": 0,
                              "strings": [], "consts": [], "callees": [], "globals": [], "calls": [],
                              "sset": frozenset(), "cset": frozenset(), "protected": True})
    callers = defaultdict(set)
    for rva, d in funcs.items():
        for c in d["callees"]:
            if c in funcs:
                callers[c].add(rva)
    for rva, d in funcs.items():
        d["callers_set"] = callers.get(rva, set())
        d["callees_set"] = {c for c in d["callees"] if c in funcs}
    return meta, funcs, thunk_to


def index(funcs, key):
    idx = defaultdict(list)
    for rva, d in funcs.items():
        for v in d[key]:
            idx[v].append(rva)
    return idx


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def lcs(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def size_ok(w, m):
    if w.get("protected") or m.get("protected"):
        return True
    a, b = max(w["insns"], 1), max(m["insns"], 1)
    return 0.4 <= a / b <= 2.5


class Matcher:
    def __init__(self, win, mac):
        self.win, self.mac = win, mac
        self.w2m, self.m2w = {}, {}
        self.evidence = defaultdict(set)   # (w, m) -> {kinds}
        self.notes = defaultdict(list)

    def add(self, w, m, kind, note=None):
        if self.w2m.get(w, m) != m or self.m2w.get(m, w) != w:
            return False                  # conflicts with an existing match
        new = w not in self.w2m
        self.w2m[w], self.m2w[m] = m, w
        self.evidence[(w, m)].add(kind)
        if note and len(self.notes[(w, m)]) < 6:
            self.notes[(w, m)].append(note)
        return new

    def unique_feature_anchors(self, key, kind, min_len=0):
        wi, mi = index(self.win, key), index(self.mac, key)
        votes = defaultdict(list)
        for v, ws in wi.items():
            if len(ws) != 1:
                continue
            ms = mi.get(v)
            if not ms or len(ms) != 1:
                continue
            if isinstance(v, str) and len(v) < min_len:
                continue
            votes[(ws[0], ms[0])].append(v)
        # a function pair is accepted if no competing pair claims either side
        by_w, by_m = defaultdict(set), defaultdict(set)
        for (w, m) in votes:
            by_w[w].add(m)
            by_m[m].add(w)
        added = 0
        for (w, m), vals in votes.items():
            if len(by_w[w]) == 1 and len(by_m[m]) == 1:
                added += self.add(w, m, kind, f"{kind}:{str(vals[0])[:60]}")
            else:
                # inlining can spread a string over several functions; keep the strongest
                best = max(by_w[w], key=lambda mm: len(votes.get((w, mm), [])))
                if best == m and len(vals) >= 2 and max(len(votes.get((ww, m), [])) for ww in by_m[m]) == len(vals):
                    added += self.add(w, m, kind, f"{kind}(plural):{str(vals[0])[:60]}")
        return added

    def similarity_evidence(self):
        for (w, m) in list(self.evidence):
            dw, dm = self.win[w], self.mac[m]
            if len(dw["sset"]) >= 2 and jaccard(dw["sset"], dm["sset"]) >= 0.6:
                self.evidence[(w, m)].add("strings_sim")
            if len(dw["cset"] & dm["cset"]) >= 3:
                self.evidence[(w, m)].add("consts_sim")
            if size_ok(dw, dm):
                self.evidence[(w, m)].add("size")
            # neighbourhood agreement: an already matched caller/callee on both sides
            agree = sum(1 for c in dw["callees_set"] if self.w2m.get(c) in dm["callees_set"]) + \
                    sum(1 for c in dw["callers_set"] if self.w2m.get(c) in dm["callers_set"])
            if agree:
                self.evidence[(w, m)].add("callgraph")
            sw = [self.w2m[c] for c in dw.get("calls", []) if c in self.w2m]
            sm = [c for c in dm.get("calls", []) if c in self.m2w]
            if sw and sm:
                n = lcs(sw[:200], sm[:200])
                if n >= 3 and n >= 0.6 * max(len(sw), len(sm)):
                    self.evidence[(w, m)].add("callseq")
                    if len(self.notes[(w, m)]) < 6:
                        self.notes[(w, m)].append(f"callseq {n}/{max(len(sw), len(sm))}")

    def score(self, dw, dm):
        if dw.get("protected"):
            agree = sum(1 for c in dw["callers_set"] if self.w2m.get(c) in dm["callers_set"])
            return agree if agree >= 2 else 0.0
        s = 0.0
        s += 3 * jaccard(dw["sset"], dm["sset"])
        s += 2 * jaccard(dw["cset"], dm["cset"])
        a, b = max(dw["insns"], 1), max(dm["insns"], 1)
        s += 1 - min(abs(a - b) / max(a, b), 1)
        # matched neighbours in common
        s += 0.5 * sum(1 for c in dw["callees_set"] if self.w2m.get(c) in dm["callees_set"])
        s += 0.5 * sum(1 for c in dw["callers_set"] if self.w2m.get(c) in dm["callers_set"])
        return s

    def propagate(self, rounds=8):
        total = 0
        for _ in range(rounds):
            added = 0
            for w, m in list(self.w2m.items()):
                dw, dm = self.win[w], self.mac[m]
                for rel in ("callees_set", "callers_set"):
                    cw = [x for x in dw[rel] if x not in self.w2m]
                    cm = [x for x in dm[rel] if x not in self.m2w]
                    if not cw or not cm or len(cw) > 40 or len(cm) > 40:
                        continue
                    scores = {(a, b): self.score(self.win[a], self.mac[b]) for a in cw for b in cm}
                    for a in cw:
                        row = sorted(((scores[(a, b)], b) for b in cm), reverse=True)
                        best, bm = row[0]
                        second = row[1][0] if len(row) > 1 else -1
                        col_best = max(scores[(x, bm)] for x in cw)
                        if best >= 1.6 and best - second >= 0.5 and col_best == best and \
                                size_ok(self.win[a], self.mac[bm]):
                            added += self.add(a, bm, "callgraph", f"via {hex(w)}<->{hex(m)} {rel[:-4]}")
            total += added
            if not added:
                break
        return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", default="x86_64")
    args = ap.parse_args()
    wmeta, win, win_thunk_to = load(FEAT / "game_plugin.dll.jsonl")
    mmeta, mac, _ = load(FEAT / f"game_plugin_{args.slice}.jsonl")
    print(f"win protected pseudo-functions: {sum(1 for d in win.values() if d.get('protected'))}")
    print(f"win functions {len(win)}, mac functions {len(mac)}")

    mt = Matcher(win, mac)
    print("string anchors:", mt.unique_feature_anchors("strings", "string", min_len=6))
    print("const anchors:", mt.unique_feature_anchors("consts", "const"))
    print("callgraph propagation:", mt.propagate())
    print("string anchors (2nd pass):", mt.unique_feature_anchors("strings", "string", min_len=6))
    print("callgraph propagation (2nd):", mt.propagate())
    mt.similarity_evidence()
    print(f"total matched: {len(mt.w2m)}")

    targets = json.loads((ROOT / "port" / "map" / "targets.json").read_text())
    out, summary = [], defaultdict(int)
    for t in targets["targets"]:
        w = int(t["win_rva"], 16)
        rec = {"win_rva": t["win_rva"], "region": t["region"], "kinds": t["kinds"],
               "signatures": t["signatures"], f"mac_{args.slice}_rva": None,
               "evidence": [], "confidence": "unmapped"}
        if w in win_thunk_to:
            rec["win_protected_body_rva"] = hex(win_thunk_to[w])
            rec["note"] = "Windows stub jumps into the excluded section; body mapped via callers"
            w = win_thunk_to[w]
        if t["region"].startswith("code"):
            m = mt.w2m.get(w)
            if m is not None:
                ev = sorted(mt.evidence[(w, m)] - {"size"})
                rec[f"mac_{args.slice}_rva"] = hex(m)
                rec["evidence"] = ev + (["size"] if "size" in mt.evidence[(w, m)] else [])
                rec["notes"] = mt.notes[(w, m)]
                rec["confidence"] = "verified" if len(ev) >= 2 else "unverified"
                if win[w].get("protected"):
                    rec["confidence"] = "unverified"   # no Windows body to compare: needs Mac-side proof
                rec["mac_size_insns"] = mac[m]["insns"]
                rec["win_size_insns"] = win[w]["insns"]
            elif w not in win:
                rec["confidence"] = "blocked"
                rec["blocked_reason"] = "not a function start in the Windows analysis (dropped section or mid-function)"
        else:
            rec["confidence"] = "data_pending"
        summary[rec["confidence"]] += 1
        out.append(rec)

    allm = FEAT / f"all_matches_{args.slice}.json"
    allm.write_text(json.dumps({hex(w): [hex(m), sorted(mt.evidence[(w, m)])] for w, m in mt.w2m.items()}))
    dst = ROOT / "port" / "map" / "rva_map.json"
    dst.write_text(json.dumps({
        "slice": args.slice, "win_meta": wmeta, "mac_meta": mmeta,
        "global_match_count": len(mt.w2m), "summary": dict(summary), "targets": out}, indent=1) + "\n")
    print("targets:", dict(summary))


if __name__ == "__main__":
    main()
