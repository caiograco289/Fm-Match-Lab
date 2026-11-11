#!/usr/bin/env python3
"""Phase 2 step 1: build port/map/targets.json from upstream's native sources.

Collects every Windows RVA the host depends on:
  * hex literals inside at(...)            -> kind "at"   (function or data, by section)
  * RVAs passed to execution_redirect(...) -> kind "redirect" (function hooked in memory)
  * RVAs compared against an instruction pointer -> kind "rip_compare"
  * profile_metadata.json data_addresses and ranges
For "at" call sites it also records the function-pointer cast, which gives the implied signature.
Reads only upstream source/metadata; it writes no game bytes.
"""
import json
import os
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NATIVE = Path(os.environ.get("FM27_UPSTREAM", ROOT / "../fm-tactics-lab")) / "native"  # upstream checkout (reference only)
META = json.loads((NATIVE / "profile_metadata.json").read_text())

SECTIONS = sorted(s["rva"] for s in META["sections"])
FLAGS = {s["rva"]: s["memory_flags"] for s in META["sections"]}
EXEC = 0x20000000
WRITE = 0x80000000
HEX = re.compile(r"0x[0-9a-fA-F]+")


def section_of(rva):
    best = None
    for s in SECTIONS:
        if s <= rva:
            best = s
    return best


def region(rva):
    s = section_of(rva)
    if s is None:
        return "header"
    f = FLAGS[s]
    if f & EXEC:
        return "code" if s == SECTIONS[0] else "code_rwx"
    return "data_rw" if f & WRITE else "data_ro"


def matching_open(text, close_idx):
    depth = 0
    for i in range(close_idx, -1, -1):
        if text[i] == ")":
            depth += 1
        elif text[i] == "(":
            depth -= 1
            if depth == 0:
                return i
    return None


def matching_close(text, open_idx):
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return None


def cast_before(text, at_idx):
    """For '((SIG)at(0x..))' return SIG, for '(T*)at(...)' return T*."""
    j = at_idx - 1
    while j >= 0 and text[j].isspace():
        j -= 1
    if j < 0 or text[j] != ")":
        return None
    o = matching_open(text, j)
    return None if o is None else re.sub(r"\s+", " ", text[o + 1 : j]).strip()


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def main():
    targets = OrderedDict()

    def add(rva, kind, file, line, signature=None, snippet=None):
        t = targets.setdefault(rva, {
            "win_rva": hex(rva), "region": region(rva), "kinds": [], "signatures": [], "sites": [],
        })
        if kind not in t["kinds"]:
            t["kinds"].append(kind)
        if signature and signature not in t["signatures"]:
            t["signatures"].append(signature)
        t["sites"].append({"file": file, "line": line, "snippet": snippet})

    for path in sorted(list(NATIVE.glob("*.h")) + list(NATIVE.glob("*.cpp"))):
        text = path.read_text(errors="replace")
        rel = str(path.relative_to(ROOT))
        for m in re.finditer(r"(?<![A-Za-z0-9_])at\(", text):
            close = matching_close(text, m.end() - 1)
            arg = text[m.end():close]
            sig = cast_before(text, m.start())
            for h in HEX.finditer(arg):
                rva = int(h.group(), 16)
                if rva < 0x1000:
                    continue
                snippet = text[max(0, m.start() - 80): close + 1].split("\n")[-1].strip()[-200:]
                add(rva, "at", rel, line_of(text, m.start()), sig, snippet)
        for m in re.finditer(r"execution_redirect\((0x[0-9a-fA-F]+)", text):
            add(int(m.group(1), 16), "redirect", rel, line_of(text, m.start()))
        for m in re.finditer(r"\(unsigned char\*\)module\s*\+\s*(0x[0-9a-fA-F]+)", text):
            add(int(m.group(1), 16), "module_offset", rel, line_of(text, m.start()))
        for m in re.finditer(r"native_base\s*==\s*(0x[0-9a-fA-F]+)", text):
            add(int(m.group(1), 16), "rip_compare", rel, line_of(text, m.start()))

    for d in META["data_addresses"]:
        t = targets.get(d["rva"])
        if t is None:
            add(d["rva"], "metadata_data", "native/profile_metadata.json", None)
            t = targets[d["rva"]]
        t["metadata_data_size"] = d["size"]

    # Attach compatibility ranges (function bodies / vtables) to targets they cover.
    ranges = []
    for i, r in enumerate(META["ranges"]):
        covered = [hex(rva) for rva in targets if r["rva"] <= rva < r["rva"] + r["size"]]
        ranges.append({"index": i, "win_rva": hex(r["rva"]), "size": r["size"], "purpose": r["purpose"],
                       "region": region(r["rva"]), "covers_targets": covered})
        for rva in targets:
            if r["rva"] <= rva < r["rva"] + r["size"]:
                targets[rva].setdefault("compat_ranges", []).append(i)

    out = {
        "source": "upstream lqf0624/fm-tactics-lab v1108.5 native/",
        "reference_build": json.loads((NATIVE / "adapter_version.json").read_text())["version"],
        "counts": {
            "targets": len(targets),
            "functions": sum(1 for t in targets.values() if t["region"].startswith("code")),
            "data": sum(1 for t in targets.values() if t["region"].startswith("data")),
            "compat_ranges": len(ranges),
            "compat_ranges_without_target": sum(1 for r in ranges if not r["covers_targets"]),
        },
        "targets": sorted(targets.values(), key=lambda t: int(t["win_rva"], 16)),
        "compat_ranges": ranges,
    }
    dst = ROOT / "port" / "map" / "targets.json"
    dst.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["counts"]))


if __name__ == "__main__":
    main()
