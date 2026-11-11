"""Study 1 page helper: per-attribute effects on the 27.0.1 run, side by side with the 27.0 run (same matches, seeds
and design). Effect per +1 in-game point = (plus - minus) / 2 / 5, paired by match and seed.

  python port/validation/study1_compare.py NEW_DIR OLD_DIR > table.md
"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEASURES = ('pts', 'xGD', 'xGF', 'xGA', 'GF', 'GA', 'shots', 'shotsA')


def load(out):
    meta = json.load(open(out / 'meta.json')); data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); match, cond = r['cond'].split('|')
        s = meta['sides'][match]; o = 1 - s
        data.setdefault(cond, {})[(match, r['seed'])] = {
            'pts': 3 if r['score'][s] > r['score'][o] else 1 if r['score'][s] == r['score'][o] else 0,
            'xGD': r['xg'][s] - r['xg'][o], 'xGF': r['xg'][s], 'xGA': r['xg'][o], 'GF': r['score'][s], 'GA': r['score'][o],
            'shots': r['shots'][s], 'shotsA': r['shots'][o]}
    return data, meta


def stats(v):
    n = len(v)
    if n < 3: return float('nan'), float('nan')
    m = sum(v) / n; sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def effects(data, step):
    out = {}
    names = sorted({c[:-1] for c in data if c[-1:] in '+-'})
    for n in names:
        lo, hi = data.get(n + '-', {}), data.get(n + '+', {})
        keys = [k for k in lo if k in hi]
        if not keys: continue
        out[n] = {m: stats([(hi[k][m] - lo[k][m]) / 2 / step for k in keys]) for m in MEASURES} | {'n': len(keys)}
    return out


def main(new, old):
    nd, nm = load(new); od, om = load(old)
    ne, oe = effects(nd, nm['delta'] / 5), effects(od, om['delta'] / 5)
    base = nd.get('natural', {})
    print(f"Natural 27.0.1 (n={len(base)}): ppg {sum(v['pts'] for v in base.values()) / max(1, len(base)):.2f}, "
          f"xG {sum(v['xGF'] for v in base.values()) / max(1, len(base)):.2f}-{sum(v['xGA'] for v in base.values()) / max(1, len(base)):.2f}\n")
    print('| Attribute | ppg per point (t) | xGD per point (t) | xG for | xG against | 27.0: ppg | 27.0: xGD | n |')
    print('|---|---|---|---|---|---|---|---|')
    for n, v in sorted(ne.items(), key=lambda kv: -kv[1]['xGD'][0]):
        o = oe.get(n)
        f = lambda x: f'{x[0]:+.3f} ({x[1]:+.1f})'
        print(f"| {n} | {f(v['pts'])} | {f(v['xGD'])} | {v['xGF'][0]:+.3f} | {v['xGA'][0]:+.3f} | "
              f"{o['pts'][0]:+.3f} | {o['xGD'][0]:+.3f} | {v['n']} |" if o else f"| {n} | {f(v['pts'])} | {f(v['xGD'])} | {v['xGF'][0]:+.3f} | {v['xGA'][0]:+.3f} | | | {v['n']} |")
    common = [n for n in ne if n in oe and not math.isnan(ne[n]['xGD'][0])]
    if len(common) > 2:
        xs = [ne[n]['xGD'][0] for n in common]; ys = [oe[n]['xGD'][0] for n in common]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        r = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
        print(f'\nCorrelation of per-attribute xGD effects, 27.0.1 vs 27.0: r = {r:.2f} over {len(common)} attributes')


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
