#!/usr/bin/env python3
"""Phase 3: calibrate Mac struct layouts against upstream's Windows dump of the same fixture.

Windows ground truth: private/engine/fm27_native/editor_manual_default.json (written by the Windows host's
dump_match_input after native preparation). Mac side: FM27_MAC_RAW_DUMP output of port/mac_host (same fixture,
same point in the pipeline). Both files are local, derived from game runtime state, and never committed.

Method: slide 8-byte windows of each Windows region over the Mac blob; keep windows that are informative (not
all zero / 0xff, no Windows heap pointer) and occur exactly once on the Mac side; report delta runs
(Windows offset range -> Mac delta). Players are located by their 69 attribute bytes (Windows player+0x480).

Usage: layout_align.py <mac raw dump.json> [--windows-dump editor_manual_default.json]
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def informative(w):
    if w.count(0) >= 6 or w.count(0xff) >= 6:
        return False
    for i in range(0, len(w) - 7, 8):
        q = int.from_bytes(w[i:i + 8], "little")
        if 0x10000000000 <= q <= 0x7fffffffffff:      # looks like a heap/image pointer
            return False
    return True


def runs(win_bytes, win_base, mac, L=8, step=4):
    """[(win_offset, delta)] for unique informative windows."""
    out = []
    for i in range(0, len(win_bytes) - L + 1, step):
        w = win_bytes[i:i + L]
        if not informative(w):
            continue
        j = mac.find(w)
        if j < 0 or mac.find(w, j + 1) >= 0:
            continue
        out.append((win_base + i, j - (win_base + i)))
    return out


def summarize(points):
    """Merge consecutive points with the same delta into ranges."""
    segs = []
    for off, d in points:
        if segs and segs[-1][2] == d and off - segs[-1][1] <= 0x40:
            segs[-1][1] = off
            segs[-1][3] += 1
        else:
            segs.append([off, off, d, 1])
    return [s for s in segs if s[3] >= 2]


def show(title, segs):
    print(f"== {title}")
    for a, b, d, n in segs:
        print(f"   win {a:#7x}..{b + 8:#7x}  delta {'+' if d >= 0 else '-'}{abs(d):#x}  ({n} windows)")


def main():
    mac_dump = json.loads(Path(sys.argv[1]).read_text())
    wpath = ROOT / "private/engine/fm27_native/editor_manual_default.json"
    if "--windows-dump" in sys.argv:
        wpath = Path(sys.argv[sys.argv.index("--windows-dump") + 1])
    win = json.loads(wpath.read_text())
    result = {}
    for side in (0, 1):
        wt, mt = win["teams"][side], mac_dump["teams"][side]
        team = bytes.fromhex(mt["team"])
        manager = bytes.fromhex(mt["manager"])
        targets = {int(k): bytes.fromhex(v) for k, v in mt["targets"].items()}
        print(f"\n######## side {side}: Windows count {wt['count']}")
        # team header (Windows team+0..0x138)
        show("team header (Windows team+0x0..0x138)", summarize(runs(bytes.fromhex(wt["header_hex"]), 0, team)))
        # roster: find each player's attribute bytes among pointer targets
        roster = {}
        for p in wt["players"]:
            attrs = bytes(p["attributes"])
            hits = [(slot, blob.find(attrs)) for slot, blob in targets.items() if blob.find(attrs) >= 0]
            roster[p["index"]] = hits
        slots = Counter(slot - 8 * idx for idx, hits in roster.items() for slot, _ in hits)
        attr_offs = Counter(o for hits in roster.values() for _, o in hits)
        print("== roster base slot votes (team offset of player[0] pointer):", slots.most_common(3))
        print("== player attribute offset votes (Windows 0x480):", [(hex(o), n) for o, n in attr_offs.most_common(3)])
        if slots:
            base_slot = slots.most_common(1)[0][0]
            p0 = targets.get(base_slot)
            if p0:
                wp = wt["players"][0]
                show("player prefix (Windows player+0x0..0x80)", summarize(runs(bytes.fromhex(wp["prefix_hex"]), 0, p0)))
                show("player state (Windows player+0x2e0..0x4e0)", summarize(runs(bytes.fromhex(wp["state_hex"]), 0x2e0, p0)))
                if "input_tail_hex" in wp:
                    show("player tail (Windows player+0x4c5..)", summarize(runs(bytes.fromhex(wp["input_tail_hex"]), 0x4c5, p0)))
            result[f"side{side}"] = {"roster_slot": base_slot, "attributes_offset": attr_offs.most_common(1)[0][0] if attr_offs else None}
        # manager
        show("manager tactical (Windows manager+0x2e0..0x2f10)", summarize(runs(bytes.fromhex(wt["manager_tactical_hex"]), 0x2e0, manager)))
        show("creator (Windows manager+0x2848)", summarize(runs(bytes.fromhex(wt["creator_hex"]), 0x2848, manager, step=1)))
        flags = int(wt["manager_input_flags"]).to_bytes(4, "little")
        hits = [i for i in range(0, len(manager) - 3, 4) if manager[i:i + 4] == flags]
        print(f"== manager_input_flags {wt['manager_input_flags']} (Windows +0x30a0) found at Mac", [hex(h) for h in hits][:6])
        slots_hex = [bytes.fromhex(x) for phase in wt["tactical_slots"] for x in phase]
        cell_hits = []
        for k, cell in enumerate(slots_hex):
            key = cell[:8]   # position u32 + pad (informative enough together with role at +0x40)
            role = cell[0x40:0x48]
            for i in range(0, len(manager) - 0x48, 8):
                if manager[i:i + 8] == key and manager[i + 0x40:i + 0x48] == role:
                    cell_hits.append((k, i))
        print("== canonical tactical cells (Windows manager+0x2768+(phase?0x438:0x118)+slot*0x48):",
              [(k, hex(i)) for k, i in cell_hits][:30])
    print("\nsummary:", result)


if __name__ == "__main__":
    main()
