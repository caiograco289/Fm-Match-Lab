"""Study 2 (docs/studies): attribute values on levelled squads, to compare with the real-match study (Study 1).

Arm B: the 10 real saved matches, both squads levelled (every non-position attribute 12 = 60 stored; positions,
       body, start state, tactics and in-match management as saved). The team's whole squad then gets one
       attribute at 12 ± 5 (35 / 85 stored).
Arm C: the bundled sample match levelled as in the earlier tests (every non-position attribute 12, natural in every
       position, 180 cm / 70 kg), assistant managing both sides; the home side gets one attribute at 12 ± 5.
Seeds 1-30 per real match (300 pairs), seeds 1-300 for the sample match. Scenario files are encoded by the app's own
encoder (validated like any app run). Results go to OUT/results.jsonl via port/validation/overnight.py.

  FM27_SAVED_MATCHES=<folder with the 27.0 matches> python port/validation/study2_levelled.py build OUT
  python port/validation/overnight.py run OUT 6
  python port/validation/study2_levelled.py analyse OUT
Run from the repo root with the app's environment (FM27_ENGINE_ROOT, FM27_DESKTOP_DATA, FM27_GAME_ROOT).
"""
import copy, json, math, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'build/source')); sys.path.insert(0, str(Path(__file__).resolve().parent))
TEAM = os.environ.get('FM27_STUDY_TEAM', '')   # your team, as in the saved match file names
LEVEL, DELTA = 60, 25


def attributes():
    return [a for a in json.load(open(ROOT / 'private/catalog.json'))['attributes'] if not a['position']]


def level(team, positions=False):
    for p in team['players']:
        for i in range(15, 69): p['attributes'][i] = LEVEL
        if positions:
            for i in range(15): p['attributes'][i] = 20
            p['native_profile'].update(height_cm=180, weight_kg=70)


def build(out):
    import fm27_tactics_server as app, exec_real
    out.mkdir(parents=True, exist_ok=True); bins = out / 'bins'; bins.mkdir(exist_ok=True)
    jobs, sides = [], {}
    conds = [('natural', None, None)] + [(f'{a["name"]}{s}', a['id'], LEVEL + (DELTA if s == '+' else -DELTA)) for a in attributes() for s in '-+']
    for name, path, side in exec_real.matches(TEAM):
        base = app.SAVED_MATCHES.open(path); sides[name] = side
        levelled = copy.deepcopy(base.default)
        for t in levelled['teams']: level(t)
        for cond, attr, value in conds:
            s = copy.deepcopy(levelled)
            if attr is not None:
                for p in s['teams'][side]['players']: p['attributes'][attr] = value
            f = bins / f'B_{name}_{cond}.bin'; f.write_bytes(app.encode_scenario(s))
            jobs.append(['B', f'{name}|{cond}', str(base.pkm), str(f), {}, 30])
    sample = copy.deepcopy(app.DEFAULT)
    for t in sample['teams']: level(t, positions=True); t['in_match'] = 'assistant'
    for cond, attr, value in conds:
        s = copy.deepcopy(sample)
        if attr is not None:
            for p in s['teams'][0]['players']: p['attributes'][attr] = value
        f = bins / f'C_{cond}.bin'; f.write_bytes(app.encode_scenario(s))
        jobs.append(['C', f'sample|{cond}', str(app.BUNDLED.pkm), str(f), {}, 300])
    (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps({'team': TEAM, 'sides': sides, 'sample_side': 0, 'level': LEVEL, 'delta': DELTA}))
    print(len(jobs), 'jobs,', sum(j[5] for j in jobs), 'matches')


def stats(v):
    n = len(v)
    if n < 2: return float('nan'), float('nan')
    m = sum(v) / n; sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def own(r, s):
    o = 1 - s
    return {'pts': 3 if r['score'][s] > r['score'][o] else 1 if r['score'][s] == r['score'][o] else 0,
            'GF': r['score'][s], 'GA': r['score'][o], 'xGF': r['xg'][s], 'xGA': r['xg'][o], 'xGD': r['xg'][s] - r['xg'][o],
            'shots': r['shots'][s]}


def effects(rows, side_of):
    """Per arm and attribute: (plus − minus) / 2, i.e. the effect of +5 in-game, paired by match and seed."""
    data = {}
    for r in rows:
        match, cond = r['cond'].split('|'); data.setdefault((r['exp'], cond), {})[(match, r['seed'])] = r
    result = {}
    for arm in sorted({k[0] for k in data}):
        for a in attributes():
            lo, hi = data.get((arm, a['name'] + '-'), {}), data.get((arm, a['name'] + '+'), {})
            keys = [k for k in lo if k in hi]
            if not keys: continue
            result[(arm, a['name'])] = {m: stats([(own(hi[k], side_of(k[0]))[m] - own(lo[k], side_of(k[0]))[m]) / 2 for k in keys])
                                        for m in ('pts', 'xGD', 'GF', 'GA', 'shots')} | {'n': len(keys)}
    return result


def analyse(out):
    meta = json.load(open(out / 'meta.json'))
    rows = [json.loads(l) for l in open(out / 'results.jsonl')]
    side_of = lambda match: meta['sides'].get(match, meta['sample_side'])
    res = effects(rows, side_of)
    json.dump({f'{a}|{n}': v for (a, n), v in res.items()}, open(out / 'effects.json', 'w'), indent=0)
    for arm in ('B', 'C'):
        ranked = sorted(((v['pts'][0], n, v) for (a, n), v in res.items() if a == arm), key=lambda x: -x[0])
        print(f'arm {arm}: top', [(n, round(v['pts'][0], 3), round(v['pts'][1], 1)) for _, n, v in ranked[:8]])


if __name__ == '__main__':
    mode, out = sys.argv[1], Path(sys.argv[2])
    build(out) if mode == 'build' else analyse(out)
