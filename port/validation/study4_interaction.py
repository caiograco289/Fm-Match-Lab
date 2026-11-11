"""Study 4 (docs/studies): attributes x tactical familiarity.

For each chosen attribute, the team's whole squad moves by -5 / +5 in-game (FM27_MAC_ATTR, before preparation, as
in Study 1) while the eight tactical areas of the effectiveness record are held LOW or HIGH for every player of
the team (FM27_MAC_EXEC_FIELDS, as in Study 6). 10 real matches x seeds 1-30 (Study 1's).

Interaction = (effect of +5 at HIGH) - (effect of +5 at LOW), each effect being (plus - minus) / 2 paired on match
and seed. Positive: the attribute is worth more with a familiar tactic.

  python port/validation/study4_interaction.py build OUT STUDY1_DIR Attr1,Attr2,...
  FM27_STUDY_HOST=... python port/validation/overnight.py run OUT 6
  python port/validation/study4_interaction.py analyse OUT
"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = {'low': 20, 'high': 80}
AREAS = [o + k for o in range(1, 25, 3) for k in (0, 1, 2)]
DELTA = 25


def build(out, study1, names):
    out.mkdir(parents=True, exist_ok=True)
    meta = json.load(open(study1 / 'meta.json'))
    attrs = {a['name']: a['id'] for a in json.load(open(ROOT / 'private/catalog.json'))['attributes']}
    missing = [n for n in names if n not in attrs]
    if missing: raise SystemExit(f'unknown attributes: {missing}')
    naturals = [j for j in json.load(open(study1 / 'jobs.json')) if j[1].endswith('|natural')]
    jobs = []
    for j in naturals:
        match = j[1].split('|')[0]; side = meta['sides'][match]
        for level, v in LEVELS.items():
            fields = ','.join(f'{side}:{o}={v}' for o in AREAS)
            jobs.append(['I', f'{match}|{level}|base', j[2], '', {'FM27_MAC_EXEC_FIELDS': fields}, j[5]])
            for n in names:
                for sign in '-+':
                    jobs.append(['I', f'{match}|{level}|{n}{sign}', j[2], '',
                                 {'FM27_MAC_EXEC_FIELDS': fields, 'FM27_MAC_ATTR': f'{side}:{attrs[n]}{sign}{DELTA}'}, j[5]])
    (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps(meta | {'attributes': names, 'levels': LEVELS, 'delta': DELTA}))
    print(len(jobs), 'jobs,', sum(j[5] for j in jobs), 'matches')


def own(r, s):
    o = 1 - s
    return {'pts': 3 if r['score'][s] > r['score'][o] else 1 if r['score'][s] == r['score'][o] else 0,
            'xGD': r['xg'][s] - r['xg'][o], 'GF': r['score'][s], 'GA': r['score'][o]}


def stats(v):
    n = len(v); m = sum(v) / n; sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1)) if n > 1 else 0
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def analyse(out):
    meta = json.load(open(out / 'meta.json')); data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); match, level, cond = r['cond'].split('|')
        data.setdefault((level, cond), {})[(match, r['seed'])] = own(r, meta['sides'][match])
    result = {}
    lo, hi = data[('low', 'base')], data[('high', 'base')]
    keys = [k for k in lo if k in hi]
    result['familiarity high-low'] = {m: stats([hi[k][m] - lo[k][m] for k in keys]) for m in ('pts', 'xGD')}
    for n in meta['attributes']:
        eff = {}
        for level in LEVELS:
            p, q = data.get((level, n + '+'), {}), data.get((level, n + '-'), {})
            eff[level] = {k: {m: (p[k][m] - q[k][m]) / 2 for m in ('pts', 'xGD')} for k in p if k in q}
        common = [k for k in eff['low'] if k in eff['high']]
        result[n] = {f'{level} {m}': stats([eff[level][k][m] for k in common]) for level in LEVELS for m in ('pts', 'xGD')} | \
            {f'interaction {m}': stats([eff['high'][k][m] - eff['low'][k][m] for k in common]) for m in ('pts', 'xGD')} | {'n': len(common)}
        v = result[n]
        print(f"{n:16} +5 at low: xGD {v['low xGD'][0]:+.3f} ({v['low xGD'][1]:+.1f})  at high: {v['high xGD'][0]:+.3f} ({v['high xGD'][1]:+.1f})  "
              f"interaction {v['interaction xGD'][0]:+.3f} ({v['interaction xGD'][1]:+.1f})")
    f = result['familiarity high-low']; print(f"familiarity high vs low: ppg {f['pts'][0]:+.3f} ({f['pts'][1]:+.1f}) xGD {f['xGD'][0]:+.3f} ({f['xGD'][1]:+.1f})")
    json.dump(result, open(out / 'effects.json', 'w'), indent=1)


if __name__ == '__main__':
    mode, out = sys.argv[1], Path(sys.argv[2])
    build(out, Path(sys.argv[3]), sys.argv[4].split(',')) if mode == 'build' else analyse(out)
