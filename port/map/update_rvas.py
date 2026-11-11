"""Carry the host's code and data RVAs from one FM27 Mac build to the next (x86_64 slices, local files only).

Functions: the old function's bytes, with RIP-relative displacements and relative branch targets masked, are searched
in the new __text at function starts (LC_FUNCTION_STARTS). A unique hit is accepted; otherwise the window grows, and
remaining ties are settled by the displacement of already-matched neighbours.
Data (g_*, vt_*, tlv_*): every RIP-relative reference to the old address is found in old code, its function is matched
as above, and the instruction at the same index in the new function gives the new address. Sites vote.
Output: JSON {name: {old, new, method, votes}} on stdout. Nothing derived from game bytes is written to the repo.

  python port/map/update_rvas.py OLD_SLICE NEW_SLICE > $FM27_WORK_DIR/mac/<new>/rva_update.json
"""
import bisect, json, re, struct, sys
from pathlib import Path
import numpy as np
import capstone
from capstone import x86

ROOT = Path(__file__).resolve().parents[2]
HEADERS = [ROOT / 'port/mac_host/fm27_mac_x86_64.h', ROOT / 'port/mac_host/fm27_mac_results.h']
CODE_PREFIX = ('fn_',)
DATA_PREFIX = ('g_', 'vt_', 'tlv_')


def uleb(buf, i):
    v = s = 0
    while True:
        b = buf[i]; i += 1; v |= (b & 0x7f) << s; s += 7
        if b < 0x80: return v, i


class Image:
    def __init__(self, path):
        self.raw = Path(path).read_bytes()
        magic, _, _, _, ncmds, _, _, _ = struct.unpack_from('<8I', self.raw, 0)
        assert magic == 0xfeedfacf, 'need a thin x86_64 slice'
        self.segs, self.sects, starts, off = [], {}, None, 32
        for _ in range(ncmds):
            cmd, size = struct.unpack_from('<2I', self.raw, off)
            if cmd == 0x19:   # LC_SEGMENT_64
                name = self.raw[off + 8:off + 24].rstrip(b'\0').decode()
                vm, vms, fo, fs = struct.unpack_from('<4Q', self.raw, off + 24)
                self.segs.append((name, vm, vms, fo, fs))
                nsect = struct.unpack_from('<I', self.raw, off + 64)[0]
                for k in range(nsect):
                    s = off + 72 + 80 * k
                    sn = self.raw[s:s + 16].rstrip(b'\0').decode(); sg = self.raw[s + 16:s + 32].rstrip(b'\0').decode()
                    addr, ssz, sfo = struct.unpack_from('<2QI', self.raw, s + 32)
                    self.sects[(sg, sn)] = (addr, ssz, sfo)
            elif cmd == 0x26:   # LC_FUNCTION_STARTS
                starts = struct.unpack_from('<2I', self.raw, off + 8)
            elif cmd == 0x1b:
                self.uuid = self.raw[off + 8:off + 24].hex().upper()
            off += size
        text_vm = next(s for s in self.segs if s[0] == '__TEXT')[1]
        do, ds = starts; i, a, self.fstarts = do, text_vm, []
        while i < do + ds:
            d, i = uleb(self.raw, i)
            if d == 0: break
            a += d; self.fstarts.append(a)
        self.fset = set(self.fstarts)
        self.text_addr, self.text_size, self.text_off = self.sects[('__TEXT', '__text')]
        self.text = self.raw[self.text_off:self.text_off + self.text_size]
        self.md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64); self.md.detail = True

    def read(self, va, n):
        for _, vm, vms, fo, fs in self.segs:
            if vm <= va < vm + fs: return self.raw[fo + va - vm:fo + va - vm + n]
        raise ValueError(hex(va))

    def flen(self, start):
        i = bisect.bisect_right(self.fstarts, start)
        return (self.fstarts[i] if i < len(self.fstarts) else self.text_addr + self.text_size) - start

    def func_of(self, va):
        i = bisect.bisect_right(self.fstarts, va) - 1
        return self.fstarts[i] if i >= 0 else None

    def insns(self, start, limit=None):
        n = min(self.flen(start), limit or 1 << 16)
        return list(self.md.disasm(self.read(start, n), start))


def rip_target(ins):
    for op in ins.operands:
        if op.type == x86.X86_OP_MEM and op.mem.base == x86.X86_REG_RIP: return ins.address + ins.size + op.mem.disp
    if ins.group(capstone.CS_GRP_JUMP) or ins.group(capstone.CS_GRP_CALL):
        for op in ins.operands:
            if op.type == x86.X86_OP_IMM: return op.imm
    return None


def pattern(img, start, length, loose=False):
    out = b''
    for ins in img.md.disasm(img.read(start, length), start):
        if ins.address + ins.size > start + length: break
        b = bytearray(ins.bytes); mask = [False] * len(b)
        dsp, dsz, imo, isz = ins.disp_offset, ins.disp_size, ins.imm_offset, ins.imm_size
        rel = ins.group(capstone.CS_GRP_JUMP) or ins.group(capstone.CS_GRP_CALL)
        if dsz and (rip_target(ins) is not None or loose):
            for k in range(dsp, dsp + dsz): mask[k] = True
        if isz and (rel or (loose and isz >= 4)):
            for k in range(imo, imo + isz): mask[k] = True
        out += b''.join(b'.' if m else re.escape(bytes([c])) for c, m in zip(b, mask))
    return out


def find_function(old, new, start, anchors):
    full = old.flen(start)
    for loose in (False, True):
        for length in (64, 160, 512, 2048, full):
            length = min(length, full)
            pat = re.compile(pattern(old, start, length, loose), re.S)
            hits = [new.text_addr + m.start() for m in pat.finditer(new.text) if new.text_addr + m.start() in new.fset]
            if len(hits) == 1: return hits[0], f'signature{"-loose" if loose else ""}:{length}'
            if hits and length == full: break
            if not hits: break
        if len(hits) > 1 and anchors:   # tie: nearest to the displacement of matched neighbours
            near = sorted(anchors, key=lambda a: abs(a[0] - start))[:4]
            delta = sorted(n - o for o, n in near)[len(near) // 2]
            best = min(hits, key=lambda h: abs(h - (start + delta)))
            return best, f'signature-tie({len(hits)})->neighbour-delta'
    return None, 'not-found'


def ref_sites(img, target, span=0x20):
    sites = set()
    t = np.frombuffer(img.text, dtype=np.uint8)
    for k in range(4):
        n = (len(t) - k - 8) // 4
        disp = np.frombuffer(img.text[k:k + 4 * n], dtype='<i4').astype(np.int64)
        pos = img.text_addr + k + 4 * np.arange(n, dtype=np.int64)
        for trail in (0, 1, 2, 4):
            hit = np.nonzero(((pos + 4 + trail + disp) >= target) & ((pos + 4 + trail + disp) < target + span))[0]
            sites.update(int(p) for p in pos[hit])
    return sorted(sites)


def find_data(old, new, addr, func_map, cache, limit=12, span=0x20):
    votes, used = {}, 0
    for site in ref_sites(old, addr, span):
        f = old.func_of(site)
        if f is None or f == addr or used >= limit: continue
        idx = [(i, ins) for i, ins in enumerate(cache.setdefault(('o', f), old.insns(f)))
               if ins.address <= site < ins.address + ins.size and rip_target(ins) is not None and addr <= rip_target(ins) < addr + span]
        if not idx: continue
        i, ins = idx[0]
        nf = func_map.get(f)
        if nf is None:
            nf, _ = find_function(old, new, f, [(o, n) for o, n in func_map.items() if n])
            func_map[f] = nf
        if nf is None: continue
        ni = cache.setdefault(('n', nf), new.insns(nf))
        if i >= len(ni) or ni[i].mnemonic != ins.mnemonic or rip_target(ni[i]) is None: continue
        cand = rip_target(ni[i]) - (rip_target(ins) - addr)
        votes[cand] = votes.get(cand, 0) + 1; used += 1
    if not votes: return None, 'no-sites', {}
    best = max(votes, key=votes.get)
    return best, f'refs {votes[best]}/{sum(votes.values())}', {hex(k): v for k, v in votes.items()}


def main():
    old, new = Image(sys.argv[1]), Image(sys.argv[2])
    names = {}
    for h in HEADERS:
        for name, value in re.findall(r'^\s*(\w+)\s*=\s*(?:FM27_RVA\(\w+,\s*)?(0x[0-9a-fA-F]+)\)?\s*,', h.read_text(), re.M):
            if name.startswith(CODE_PREFIX + DATA_PREFIX): names[name] = int(value, 16)
    out, func_map, cache = {'_uuid': {'old': old.uuid, 'new': new.uuid}}, {}, {}
    for name, addr in sorted(names.items(), key=lambda x: x[1]):
        if not name.startswith(CODE_PREFIX): continue
        if addr not in old.fset: out[name] = {'old': hex(addr), 'new': None, 'method': 'old address is not a function start'}; continue
        got, how = find_function(old, new, addr, [(o, n) for o, n in func_map.items() if n])
        if got: func_map[addr] = got
        out[name] = {'old': hex(addr), 'new': hex(got) if got else None, 'method': how,
                     'old_len': old.flen(addr), 'new_len': new.flen(got) if got else None}
        print(name, out[name], file=sys.stderr, flush=True)
    for name, addr in sorted(names.items(), key=lambda x: x[1]):   # callers vote for every function (check or rescue)
        if not name.startswith(CODE_PREFIX): continue
        got, how, votes = find_data(old, new, addr, func_map, cache, span=1)
        o = out[name]; o['callers'] = how; o['caller_votes'] = votes
        if got and o['new'] is None: o['new'], o['method'] = hex(got), 'callers ' + how
        elif got and o['new'] != hex(got):
            if 'tie' in o['method']: o['new'], o['method'] = hex(got), o['method'] + ' -> overridden by callers'   # a guess loses to evidence
            else: o['conflict'] = True
        if got and not o.get('conflict'): func_map[addr] = int(o['new'], 16)
        print(name, o, file=sys.stderr, flush=True)
    for name, addr in sorted(names.items(), key=lambda x: x[1]):
        if name.startswith(CODE_PREFIX): continue
        got, how, votes = find_data(old, new, addr, func_map, cache)
        out[name] = {'old': hex(addr), 'new': hex(got) if got else None, 'method': how, 'votes': votes}
        print(name, out[name], file=sys.stderr, flush=True)
    for seg in ('__TEXT', '__DATA_CONST', '__DATA'):
        o = next((s for s in old.segs if s[0] == seg), None); n = next((s for s in new.segs if s[0] == seg), None)
        if o and n: out['segment ' + seg] = {'old': [hex(o[1]), hex(o[1] + o[2])], 'new': [hex(n[1]), hex(n[1] + n[2])]}
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
