"""Dose response of attributes set to fixed levels for the whole squad (Study 12): linear vs two-segment fits.

    .venv/bin/python port/validation/dose_response.py runs/roadmap/12 [--measure xPts]

Conditions are named '<Attribute>=<level>'. For each attribute the effect at each level (paired against the
unchanged matches) is fitted by generalised least squares, with the covariance of the level means estimated from
the paired data (every level shares the same matches and seeds). Models: a straight line, and a continuous
two-segment line with the knee anywhere from 3 to 18. Prints the level means, the slope per point, the best knee,
the slopes either side of it and the improvement in chi-square (with a knee searched over 16 positions, an
improvement below about 8 is what chance gives).
"""
import argparse, json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import neutral_study as ns  # noqa: E402


def gls(X, y, Wi):
    A = X.T @ Wi @ X
    beta = np.linalg.solve(A, X.T @ Wi @ y)
    r = y - X @ beta
    return beta, float(r @ Wi @ r), np.sqrt(np.diag(np.linalg.inv(A)))


def analyse(out, measure='xPts'):
    data = ns.load(out)
    groups = sorted({g for g, _ in data})
    res = {}
    for g in groups:
        base = data[(g, 'none')]
        attrs = {}
        for (gg, c) in data:
            if gg == g and '=' in c:
                a, lv = c.rsplit('=', 1)
                attrs.setdefault(a, []).append(int(lv))
        for a, lvls in attrs.items():
            lvls = sorted(lvls)
            keys = [k for k in base if all(k in data[(g, f'{a}={l}')] for l in lvls)]
            D = np.array([[data[(g, f'{a}={l}')][k][measure] - base[k][measure] for l in lvls] for k in keys])
            n = len(keys)
            y = D.mean(0)
            C = np.cov(D, rowvar=False) / n
            Wi = np.linalg.inv(C)
            x = np.array(lvls, float)
            X1 = np.column_stack([np.ones_like(x), x])
            b1, chi1, se1 = gls(X1, y, Wi)
            best = None
            for knee in range(3, 19):
                X2 = np.column_stack([np.ones_like(x), np.minimum(x, knee), np.maximum(x - knee, 0)])
                b2, chi2, se2 = gls(X2, y, Wi)
                if best is None or chi2 < best[1]:
                    best = (knee, chi2, b2, se2)
            res[(g, a)] = dict(levels=lvls, means=y.tolist(), se=np.sqrt(np.diag(C)).tolist(), n=n,
                               slope=b1[1], slope_se=se1[1], chi_lin=chi1, knee=best[0], chi_knee=best[1],
                               below=best[2][1], below_se=best[3][1], above=best[2][2], above_se=best[3][2])
    return res


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('out'); p.add_argument('--measure', default='xPts'); p.add_argument('--json')
    a = p.parse_args()
    res = analyse(a.out, a.measure)
    lv = next(iter(res.values()))['levels']
    print('| Attribute | ' + ' | '.join(str(l) for l in lv) + ' | Slope per point | Best knee | Below | Above | Chi-square gain |')
    print('|---|' + '---|' * len(lv) + '---|---|---|---|---|')
    for (g, at), r in sorted(res.items(), key=lambda kv: -kv[1]['slope']):
        cells = ' | '.join(f'{m:+.2f}' for m in r['means'])
        print(f"| {at} | {cells} | {r['slope']:+.4f} (t {r['slope']/r['slope_se']:+.1f}) | {r['knee']} | "
              f"{r['below']:+.4f} | {r['above']:+.4f} | {r['chi_lin']-r['chi_knee']:.1f} |")
    if a.json:
        Path(a.json).write_text(json.dumps({f'{g}|{at}': r for (g, at), r in res.items()}, indent=1, default=float))


if __name__ == '__main__':
    main()
