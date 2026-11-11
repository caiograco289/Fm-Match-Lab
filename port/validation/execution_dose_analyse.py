"""Summarise execution_dose.py output: per pair, results and per-side means; paired deltas against a reference pair."""
import json, math, sys


def mean_sd(v):
    m = sum(v) / len(v); return m, math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) if len(v) > 1 else 0.0


def paired_t(a, b):
    d = [y - x for x, y in zip(a, b)]; m, s = mean_sd(d)
    return m, (m / (s / math.sqrt(len(d))) if s else float('nan'))


def main():
    data = json.load(open(sys.argv[1]))
    print(f"{'pair':>8} {'W-D-L':>10} {'goals':>11} {'xG':>11} {'shots':>11} {'poss':>6}")
    for key, runs in data.items():
        w = sum(r['score'][0] > r['score'][1] for r in runs); d = sum(r['score'][0] == r['score'][1] for r in runs)
        col = lambda f, i: sum(f(r)[i] for r in runs) / len(runs)
        print(f"{key:>8} {f'{w}-{d}-{len(runs) - w - d}':>10} {col(lambda r: r['score'], 0):5.2f}-{col(lambda r: r['score'], 1):<5.2f}"
              f" {col(lambda r: r['xg'], 0):5.2f}-{col(lambda r: r['xg'], 1):<5.2f} {col(lambda r: r['shots'], 0):5.1f}-{col(lambda r: r['shots'], 1):<5.1f}"
              f" {100 * col(lambda r: r['possession'], 0):5.1f}")
    for ref, keys in (('50x50', [k for k in data if k.endswith('x50') and k != '50x50']),
                      ('off', [k for k in data if k != 'off' and len(set(k.split('x'))) == 1])):
        if ref not in data: continue
        base = {r['seed']: r for r in data[ref]}
        print(f'\npaired against {ref} (same seeds): delta and t')
        for k in keys:
            runs = [r for r in data[k] if r['seed'] in base]; old = [base[r['seed']] for r in runs]
            stats = []
            for name, f in (('home xG', lambda r: r['xg'][0]), ('away xG', lambda r: r['xg'][1]),
                            ('xGD', lambda r: r['xg'][0] - r['xg'][1]), ('GD', lambda r: r['score'][0] - r['score'][1]),
                            ('total xG', lambda r: r['xg'][0] + r['xg'][1])):
                m, t = paired_t([f(r) for r in old], [f(r) for r in runs]); stats.append(f'{name} {m:+.2f} (t={t:+.1f})')
            print(f'{k:>8}: ' + ', '.join(stats))


if __name__ == '__main__':
    main()
