"""Which matchups stand out in a league? Head to head in expected points, against what overall strength predicts.

For any league folder (the app's League page: data/leagues/<id>, or `scripts/study.py league`): the table, and the
head to head in expected points (xPts: 3 x P(win) + P(draw) from both sides' xG), which is about 2.4 times steadier
per match than actual points. Each pairing is compared with what the two tactics' overall strengths predict (an
additive model: xPts of A against B = mean + strength A - strength B, fitted to all pairings); pairings that differ
from it by three standard errors or more are listed. With n tactics there are n(n-1) pairings, so at two standard
errors several would appear by chance; at three, about one in 370.

  python port/validation/league_matchups.py LEAGUE_FOLDER [--min-z 3] [--out report.md]
"""
import argparse, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import league


def analyse(folder):
    folder = Path(folder); meta = json.loads((folder / 'meta.json').read_text(encoding='utf8'))
    names = [t['name'] for t in meta['teams']]; n = len(names)
    tactic = {t['name']: t['tactic'].replace('Preset: ', '') for t in meta['teams']}
    shown = [tactic[x] if x.startswith('Team ') else x for x in names]
    cells = {}
    for line in open(folder / 'results.jsonl'):
        r = json.loads(line); _, i, j = r['cond'].split('|'); i, j = int(i), int(j)
        for me, them, s in ((i, j, 0), (j, i, 1)):
            cells.setdefault((me, them), []).append(league.xpts(r['xg'][s], r['xg'][1 - s]))
    mean = {k: sum(v) / len(v) for k, v in cells.items()}
    se = {k: math.sqrt(sum((x - mean[k]) ** 2 for x in v) / (len(v) - 1) / len(v)) for k, v in cells.items() if len(v) > 2}
    mu = sum(mean.values()) / len(mean)
    # least squares for xPts(i, j) = mu + a_i - a_j with sum a = 0: a_i = (row mean - column mean) / 2 (balanced design)
    strength = [(sum(mean[(i, j)] for j in range(n) if j != i) - sum(mean[(j, i)] for j in range(n) if j != i)) / (2 * (n - 1)) for i in range(n)]
    out = []
    for (i, j), m in mean.items():
        exp = mu + strength[i] - strength[j]
        if (i, j) in se and se[(i, j)] > 0: out.append((shown[i], shown[j], m, exp, (m - exp) / se[(i, j)], len(cells[(i, j)])))
    return shown, mean, strength, out, meta


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('folder'); p.add_argument('--min-z', type=float, default=3.0); p.add_argument('--out')
    a = p.parse_args()
    res = league.table(a.folder)
    shown, mean, strength, out, meta = analyse(a.folder)
    order = sorted(range(len(shown)), key=lambda k: -strength[k])
    lines = ['## Table', '', '| # | Tactic | Points | ± | Points per game | xPts per game | xG for | xG against |', '|---|---|---|---|---|---|---|---|']
    tactic = {t['name']: t['tactic'].replace('Preset: ', '') for t in meta['teams']}
    for r in res['table']:
        name = tactic[r['team']] if r['team'].startswith('Team ') else r['team']
        lines.append(f"| {r['rank']} | {name} | {r['Pts']:.1f} | {r['Pts_sd']:.1f} | **{r['PPG']:.2f}** | {r['xPts'] / max(1, r['P']):.2f} | {r['xGF']:.2f} | {r['xGA']:.2f} |")
    lines += ['', '## Head to head in expected points', '', 'Expected points per match of the row tactic against the column tactic (both venues, all seasons), ordered by overall strength.', '',
              '| | ' + ' | '.join(str(k + 1) for k in range(len(order))) + ' |', '|---|' + '---|' * len(order)]
    for r_, i in enumerate(order):
        lines.append(f'| {r_ + 1} {shown[i]} | ' + ' | '.join('·' if i == j else f'{mean[(i, j)]:.2f}' for j in order) + ' |')
    flagged = sorted([x for x in out if abs(x[4]) >= a.min_z], key=lambda x: -abs(x[4]))
    lines += ['', f'## Matchups that stand out (|z| ≥ {a.min_z:g})', '',
              'Expected points of the first tactic against the second, compared with what their overall strengths predict.', '']
    if flagged:
        lines += ['| Tactic | Against | xPts per match | Predicted | Difference | z | Matches |', '|---|---|---|---|---|---|---|']
        lines += [f'| {t} | {o} | {m:.2f} | {e:.2f} | {m - e:+.2f} | {z:+.1f} | {k} |' for t, o, m, e, z, k in flagged]
    else: lines.append('None: every pairing is within three standard errors of what overall strength predicts.')
    near = sorted([x for x in out if 2 <= abs(x[4]) < a.min_z], key=lambda x: -abs(x[4]))
    lines += ['', f'Between 2 and {a.min_z:g} standard errors (about {len(out) * 0.0455:.0f} expected by chance): {len(near)}.']
    text = '\n'.join(lines) + '\n'
    if a.out: Path(a.out).write_text(text, encoding='utf8')
    print(text)


if __name__ == '__main__':
    main()
