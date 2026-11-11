"""Locate the tactical-effectiveness record builder and sampler in a new build, and check the record layout.

update_rvas.py cannot match these two by signature when their code changed, and they have no named callers. Here:
1. old call sites of each function (call rel32 scan) -> their caller functions;
2. callers matched in the new build by signature (update_rvas.find_function);
3. the call at the same ordinal among the caller's calls gives the new function (votes over all callers);
4. layout check: the builder's stores through its record pointer (size, offset), old vs new; and the
   player-relative operands each function uses in the record range (+0xca0..+0xcf0). A sampler that reads the record
   through a helper (27.0.1: accessor 0x4e49020 with an offset table) shows fewer direct operands; check that helper
   by hand (port/REPORT.md, "Tactical-effectiveness record on 27.0.1").

  python port/map/exec_locate.py OLD_SLICE NEW_SLICE OLD_BUILDER OLD_SAMPLER
"""
import collections, json, sys
from pathlib import Path

import capstone
import numpy as np
from capstone import x86

sys.path.insert(0, str(Path(__file__).resolve().parent))
from update_rvas import Image, find_function, rip_target


def call_sites(img, target):
    t = np.frombuffer(img.text, dtype=np.uint8)
    pos = np.nonzero(t[:-5] == 0xE8)[0]
    rel = (t[pos + 1].astype(np.int64) | t[pos + 2].astype(np.int64) << 8 | t[pos + 3].astype(np.int64) << 16 | t[pos + 4].astype(np.int64) << 24)
    rel = np.where(rel >= 1 << 31, rel - (1 << 32), rel)
    hit = pos[(img.text_addr + pos + 5 + rel) == target]
    return [int(img.text_addr + p) for p in hit]


def calls(img, f):
    return [(ins.address, rip_target(ins)) for ins in img.insns(f, 1 << 20) if ins.group(capstone.CS_GRP_CALL)]


def setup(img, f):
    """Per call: the non-RIP memory displacements used in the 12 instructions before it (the argument set-up)."""
    ins = img.insns(f, 1 << 20); out = []
    for i, x in enumerate(ins):
        if x.group(capstone.CS_GRP_CALL):
            d = {op.mem.disp for y in ins[max(0, i - 12):i] for op in y.operands if op.type == x86.X86_OP_MEM and op.mem.base not in (0, x86.X86_REG_RIP, x86.X86_REG_RSP, x86.X86_REG_RBP)}
            out.append((x.address, rip_target(x), d))
    return out


def record_stores(img, f):
    """Stores at small displacements from a register (the builder writes through its record pointer)."""
    c = collections.Counter()
    for x in img.insns(f, 1 << 20):
        if x.operands and x.operands[0].type == x86.X86_OP_MEM and x.mnemonic.startswith('mov'):
            m = x.operands[0].mem
            if m.base not in (0, x86.X86_REG_RIP, x86.X86_REG_RBP, x86.X86_REG_RSP) and m.index == 0 and 0 <= m.disp <= 0x24:
                c[(x.operands[0].size, m.disp)] += 1
    return c


def displacements(img, f, lo=0xca0, hi=0xcf0):
    seen = collections.Counter()
    for ins in img.insns(f, 1 << 20):
        for op in ins.operands:
            if op.type == x86.X86_OP_MEM and op.mem.base not in (0, x86.X86_REG_RIP) and lo <= op.mem.disp < hi:
                seen[(ins.mnemonic, op.size, op.mem.disp)] += 1
    return seen


def locate(old, new, target, matched, depth=3):
    votes = collections.Counter(); evidence = []
    for site in call_sites(old, target):
        caller = old.func_of(site)
        new_caller = matched.get(caller)
        if caller not in matched:
            new_caller, how = find_function(old, new, caller, [(o, n) for o, n in matched.items() if n])
            if not new_caller and depth:   # the caller changed too: locate it through its own callers
                new_caller = locate(old, new, caller, matched, depth - 1)[0]
            matched[caller] = new_caller
        if not new_caller: evidence.append({'caller': hex(caller), 'new': None}); continue
        oc, nc = calls(old, caller), calls(new, new_caller)
        k = [a for a, _ in oc].index(site)
        cand, how = (nc[k][1], 'ordinal') if k < len(nc) and len(oc) == len(nc) else (None, None)
        if cand is None:   # call count changed (inlining): the call with the same argument set-up
            want = next(d for a, _, d in setup(old, caller) if a == site)
            scored = sorted(((len(want & d) / len(want | d) if want | d else 0, t) for _, t, d in setup(new, new_caller)), reverse=True)
            if scored and scored[0][0] >= 0.8 and (len(scored) == 1 or scored[1][0] < scored[0][0]): cand, how = scored[0][1], f'argument set-up {scored[0][0]:.2f}'
        evidence.append({'caller': hex(caller), 'new_caller': hex(new_caller), 'ordinal': k, 'calls': [len(oc), len(nc)], 'how': how, 'candidate': hex(cand) if cand else None})
        if cand: votes[cand] += 1
    best = votes.most_common(1)[0][0] if votes else None
    return best, dict(votes), evidence


def main():
    old, new = Image(sys.argv[1]), Image(sys.argv[2])
    matched, report = {}, {}
    for name, addr in (('fn_exec_build', int(sys.argv[3], 16)), ('fn_exec_sample', int(sys.argv[4], 16))):
        best, votes, evidence = locate(old, new, addr, matched)
        entry = {'old': hex(addr), 'new': hex(best) if best else None, 'votes': {hex(k): v for k, v in votes.items()}, 'evidence': evidence,
                 'old_len': old.flen(addr), 'new_len': new.flen(best) if best else None}
        if best:
            do, dn = displacements(old, addr), displacements(new, best)
            entry['record_operands_old'] = sorted(f'{m} {s} +{d:#x} x{c}' for (m, s, d), c in do.items())
            entry['record_operands_new'] = sorted(f'{m} {s} +{d:#x} x{c}' for (m, s, d), c in dn.items())
            entry['record_operand_set_equal'] = set(do) == set(dn)
            if name == 'fn_exec_build':
                so, sn = record_stores(old, addr), record_stores(new, best)
                entry['record_stores_old'] = sorted(f'{s}B +{d:#x} x{c}' for (s, d), c in so.items())
                entry['record_stores_new'] = sorted(f'{s}B +{d:#x} x{c}' for (s, d), c in sn.items())
                entry['record_stores_equal'] = so == sn
        report[name] = entry
    json.dump(report, sys.stdout, indent=1)


if __name__ == '__main__':
    main()
