"""The tactical-effectiveness record (33 bytes at match-player +0xcb2, Windows +0xcba) as the sampler reads it.

Reconstructed from FM27 27.0.1's accessor 0x4e49020 (macOS x86_64), which 27.0 had inline in the sampler (same bytes
read, see port/REPORT.md). value(record, category) gives what the sampler uses for one action category, 0-100.
Checked against the game's own function on 20,000 random records (port/mac_host host research mode
FM27_MAC_EXEC_ACCESSOR_TEST): `python port/map/exec_record.py check TEST.jsonl`.

Layout (offsets in the record; the mode byte sits just past it, at +0x21):
  +0x00        player-level byte (signed)
  +0x01..+0x18 eight 3-byte triples; category c uses the triple at TRIPLE[c] (+1 and +2, signed); the first byte of
               each triple is not read here
  +0x19..+0x1b three signed bytes combined into one team-level score S (weights depend on the mode)
  +0x1c..+0x20 raw ability, role suitability, overall, buy-in, next-match information (builder arguments; not read by
               the accessor)
  +0x21        mode (1..3 in practice; 27.0 range-checks mode-1 < 3)
"""
import json, sys

TRIPLE = (13, 16, 19, 1, 4, 7, 10, 22, 10)   # category 0..8 -> triple offset (categories 6 and 8 share one)


def s8(b): return b - 256 if b >= 128 else b


def f32(x):
    import struct; return struct.unpack('<f', struct.pack('<f', x))[0]


def rnd(x):   # the engine's rounding: half away from zero, then truncate (single precision)
    return int(f32(x + (0.5 if x >= 0 else -0.5)))


def value(rec, category):
    mode = rec[0x21]
    t1, t2 = (s8(rec[TRIPLE[category] + 1]), s8(rec[TRIPLE[category] + 2])) if category <= 8 else (0, 0)
    a, b, c = s8(rec[0x19]), s8(rec[0x1a]), s8(rec[0x1b])
    if mode == 1: S = f32(f32(f32(a * f32(0.45)) + f32(b * f32(0.35))) + f32(c * f32(0.2)))
    else: S = f32(f32(f32(a * f32(0.6)) + f32(b * f32(0.3))) + f32(c * f32(0.1)))
    T = rnd(S)
    k = f32(1 / 3) if mode == 1 else 0.25 if mode in (2, 3) else 0.5
    p0 = f32(1 / 3) if mode == 1 else 0.5 if mode in (2, 3) else 0.25
    p1 = f32(1 / 3) if mode == 1 else 0.25
    g = 1.0 if mode == 1 else f32(0.7) if mode == 2 else f32(0.6)
    gap = s8((100 - T) & 0xff); r0 = s8(rec[0])
    A = f32(f32(f32(r0 * p1) + f32(f32(k * t2) * g)) + f32(gap * p0))
    B = f32(t1 * g)
    total = s8(rnd(A) & 0xff) + s8(rnd(B) & 0xff)
    return max(0, min(100, total))


def check(path):
    bad = n = 0
    for line in open(path):
        e = json.loads(line)
        if e.get('event') != 'exec_accessor': continue
        n += 1; rec = bytes.fromhex(e['record'])
        if value(rec, e['idx']) != e['value']:
            bad += 1
            if bad <= 5: print('mismatch', e, value(rec, e['idx']))
    print(f'{n} records, {bad} mismatches')


if __name__ == '__main__':
    check(sys.argv[2])
