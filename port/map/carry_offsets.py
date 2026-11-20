#!/usr/bin/env python3
"""Carry struct offsets (not function RVAs) from one Mac build to the next.

For an old offset X, every matched function that uses X votes for the delta d such that the
instruction at the same index in the new twin uses X+d. Only instructions whose mnemonic matches
are counted. Output: votes per offset.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_rvas

if len(sys.argv) != 4:
    raise SystemExit('usage: carry_offsets.py OLD_SLICE NEW_SLICE RVA_UPDATE.json')
OLD, NEW, MAP = sys.argv[1], sys.argv[2], sys.argv[3]

CONSTS = {
    'm_teams': 0x15370, 'm_score_context': 0x14e90, 'm_restart_team': 0x12d40,
    'm_deadball': 0x12d60, 'm_clock': 0x15454, 'm_tick': 0x154dc,
    't_manager': 0x640, 't_roster': 0x140, 't_count': 0x73d, 't_statistics': 0x6a0,
    'p_cell_ip': 0xcd8, 'p_cell_oop': 0xdb0, 'p_attributes': 0x478, 'p_native_id': 0x48,
    'p_identity': 0x20, 'mg_map_live': 0x1fb4, 'mg_input_flags': 0x30d0, 'mg_plan': 0x1800,
    'mg_routines': 0x8e8, 'mg_selection': 0x6e0, 'mg_captain_slot': 0x3521,
    'mg_cells_live': 0x1808, 'mg_cells_canon': 0x2788, 'mg_creator_live': 0x18e0,
    'mg_creator_input': 0x2860, 'mg_creator_mid': 0x20a0, 'mg_version': 0x18f0,
    'cell_ip_offset': 0x118, 'cell_oop_offset': 0x438, 'cell_stride': 0x48, 'cell_role': 0x40,
    'p_cell_ip_win': 0xce0, 'p_cell_oop_win': 0xdb8,
}


def disp(ins):
    for op in ins.operands:
        if op.type == update_rvas.capstone.x86.X86_OP_MEM:
            return op.mem.disp
    return None


def main():
    old, new = update_rvas.Image(OLD), update_rvas.Image(NEW)
    table = json.load(open(MAP))
    pairs = [(int(v['old'], 16), int(v['new'], 16)) for k, v in table.items()
             if k.startswith('fn_') and v.get('new')]
    print(f'{len(pairs)} matched functions', file=sys.stderr)
    for name, X in CONSTS.items():
        votes = Counter()
        voters = 0
        for o, n in pairs:
            oi = [i for i in old.insns(o) if disp(i) == X]
            if not oi:
                continue
            ni = list(new.insns(n))
            for ins in oi:
                idx = next((k for k, cand in enumerate(old.insns(o)) if cand.address == ins.address), None)
                if idx is None or idx >= len(ni):
                    continue
                if ni[idx].mnemonic != ins.mnemonic:
                    continue
                d = disp(ni[idx])
                if d is None or abs(d - X) > 0x800:
                    continue
                voters += 1
                votes[d - X] += 1
        top = votes.most_common(3)
        out = ', '.join(f'{d:+#x}->{X + d:#x} ({c})' for d, c in top) or 'no votes'
        print(f'{name:16s} old {X:#08x}  voters={voters:3d}  {out}')


if __name__ == '__main__':
    main()
