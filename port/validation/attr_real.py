"""Attribute sensitivity on the user's real saved FM27 matches, replayed by the Mac host.

For every saved match of TEAM (matches/automatic/*.pkm) and seeds 1..N, TEAM's whole squad has one attribute moved by
-DELTA or +DELTA stored points (5 stored points = 1 on the in-game 1-20 scale; clamped to 1-100) with FM27_MAC_ATTR,
written before preparation and read back after it. The opponent is unchanged. Results are paired by (match, seed)
against the natural replay.

  python port/validation/attr_real.py build OUT TEAM N [DELTA]   # writes OUT/jobs.json (default DELTA 25 = 5 in-game)
  python port/validation/overnight.py run OUT PARALLEL           # shared resumable runner
  python port/validation/attr_real.py analyse OUT TEAM           # writes OUT/report.md
"""
import json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exec_real

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'private/catalog.json'
FIRST = ['Finishing', 'Passing', 'Technique', 'FirstTouch', 'Composure', 'Decisions', 'Anticipation', 'OffTheBall',
         'Dribbling', 'Vision', 'Pace', 'Acceleration']   # run first: the open question, plus two physical controls


def attributes():
    rows = [a for a in json.load(open(CATALOG))['attributes'] if not a['position']]
    order = {n: i for i, n in enumerate(FIRST)}
    return sorted(rows, key=lambda a: (order.get(a['name'], len(FIRST)), a['id']))


def build(out, team, n, delta):
    out.mkdir(parents=True, exist_ok=True)
    found = exec_real.matches(team)
    jobs = [['R', f'{name}|natural', str(Path(path).resolve()), '', {}, n] for name, path, side in found]
    for a in attributes():
        for sign in '-+':
            for name, path, side in found:
                jobs.append(['R', f'{name}|{a["name"]}{sign}', str(Path(path).resolve()), '',
                             {'FM27_MAC_ATTR': f'{side}:{a["id"]}{sign}{delta}'}, n])
    (out / 'jobs.json').write_text(json.dumps(jobs))
    meta = {'team': team, 'sides': {name: side for name, _, side in found}, 'delta': delta, 'seeds': n}
    (out / 'meta.json').write_text(json.dumps(meta))
    print(f'{len(found)} matches, {len(jobs)} jobs, {len(jobs) * n} matches to run')


def stats(diffs):
    k = len(diffs)
    if k < 2: return float('nan'), float('nan')
    m = sum(diffs) / k; sd = math.sqrt(sum((v - m) ** 2 for v in diffs) / (k - 1))
    return m, (m / (sd / math.sqrt(k)) if sd else 0.0)


def analyse(out, team):
    meta = json.load(open(out / 'meta.json')); sides = meta['sides']
    data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); name, cond = r['cond'].split('|')
        data.setdefault(cond, {})[(name, r['seed'])] = r
    nat = data.get('natural', {})

    def own(r, name):
        s = sides[name]; o = 1 - s
        pts = 3 if r['score'][s] > r['score'][o] else 1 if r['score'][s] == r['score'][o] else 0
        return {'pts': pts, 'GF': r['score'][s], 'GA': r['score'][o], 'xGF': r['xg'][s], 'xGA': r['xg'][o],
                'GF-xGF': r['score'][s] - r['xg'][s], 'shots': r['shots'][s], 'SoT': r['shots_on_target'][s],
                'pass%': 100 * r['completed_passes'][s] / max(1, r['passes'][s]), 'share': 100 * r['possession'][s]}

    keys = ['pts', 'GF', 'GA', 'xGF', 'xGA', 'GF-xGF', 'shots', 'SoT', 'pass%', 'share']
    base = [own(r, k[0]) for k, r in nat.items()]
    lines = [f'# Attribute sensitivity on real saved matches ({team})', '',
             f'{len(sides)} saved matches × seeds 1-{meta["seeds"]}; {team}\'s whole squad moved by ±{meta["delta"]} stored '
             f'(±{meta["delta"] / 5:g} in-game), opponent unchanged. Effect = (plus − minus) / 2 per in-game step of '
             f'{meta["delta"] / 5:g}, paired by match and seed: mean (t). |t| ≥ 3 bold (about 54 attributes × 10 measures).', '',
             f'Natural (n={len(base)}): ' + ', '.join(f'{k} {sum(b[k] for b in base) / len(base):.2f}' for k in keys), '',
             '| attribute | n | ' + ' | '.join(keys) + ' |', '|---|---|' + '---|' * len(keys)]
    rows = []
    for a in attributes():
        lo, hi = data.get(a['name'] + '-', {}), data.get(a['name'] + '+', {})
        both = [k for k in lo if k in hi]
        if not both: continue
        cells, sort_key = [], 0
        for key in keys:
            m, t = stats([(own(hi[k], k[0])[key] - own(lo[k], k[0])[key]) / 2 for k in both])
            cell = f'{m:+.2f} ({t:+.1f})'; cells.append(f'**{cell}**' if abs(t) >= 3 else cell)
            if key == 'pts': sort_key = m
        rows.append((sort_key, f'| {a["name"]} | {len(both)} | ' + ' | '.join(cells) + ' |'))
    lines += [r for _, r in sorted(rows, reverse=True)]
    (out / 'report.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    mode, out = sys.argv[1], Path(sys.argv[2])
    if mode == 'build': build(out, sys.argv[3], int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 25)
    elif mode == 'analyse': analyse(out, sys.argv[3])
    else: raise SystemExit(__doc__)
