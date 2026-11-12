"""Study 5 follow-up (docs/studies/05-everything-else.md).

1. Confirmation: the screen's uncertain effects rerun on seeds 31-120 (90 more per match, 900 pairs per condition),
   reusing the screen's encoded scenarios, with the natural baseline on the same seeds.
2. Goalkeeper check: "positions all natural" also made every outfield starter a natural goalkeeper. The check sets
   the 14 outfield position ratings to 20 and leaves the goalkeeper rating as stored, on seeds 1-30, against the
   screen's natural rows.

  python port/validation/study5_confirm.py build OUT STUDY5_DIR          # app environment, as study5_everything.py
  FM27_STUDY_HOST=... python port/validation/overnight.py run OUT 6
  python port/validation/study5_confirm.py analyse OUT STUDY5_DIR
"""
import copy, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
CONFIRM_SEEDS = 90
CONFIRM = ['mentality +1', 'TI PressingTrap=Show outside', 'TI PressingTrap=Show inside', 'pressure=18',
           'temperament=5', 'professionalism=18', 'age-5', 'condition=100%', 'sharpness=100%', 'TI Tempo=Higher',
           'TI ProgressThrough=Left', 'TI AttackingTransition=Standard', 'TI AttackingTransition=Regroup',
           'TI SupportingRuns=Standard', 'TI GoalkeeperDistributionSpeed=Balanced', 'TI Dribbling=Standard',
           'TI PassingDirectness=Standard']


def build(out, study5):
    import fm27_tactics_server as app
    out.mkdir(parents=True, exist_ok=True); bins = out / 'bins'; bins.mkdir(exist_ok=True)
    meta = json.load(open(study5 / 'meta.json')); screen = json.load(open(study5 / 'jobs.json'))
    jobs = []
    for exp, cond, pkm, b, env, n in screen:
        name = cond.split('|', 1)[1]
        if name == 'natural' or name in CONFIRM or name.startswith('team_cohesion='):
            jobs.append(['CT', cond, pkm, b, env, CONFIRM_SEEDS])
    for exp, cond, pkm, b, env, n in screen:
        if not cond.endswith('|natural'): continue
        match = cond.split('|')[0]; side = meta['sides'][match]
        s = app.validate_scenario(app.SAVED_MATCHES.open(pkm).default)
        t = s['teams'][side]
        for i in t['lineup']:
            a = t['players'][i]['attributes']
            for j in range(1, 15): a[j] = 20
        f = bins / f'{len(jobs)}.bin'; f.write_bytes(app.encode_scenario(app.validate_scenario(s)))
        jobs.append(['G', f'{match}|positions natural, goalkeeper as stored', pkm, str(f), {}, 30])
    (out / 'jobs.json').write_text(json.dumps(jobs)); (out / 'meta.json').write_text(json.dumps(meta))
    print(len(jobs), 'jobs,', sum(j[5] for j in jobs), 'matches')


def own(r, s):
    o = 1 - s
    return {'pts': 3 if r['score'][s] > r['score'][o] else 1 if r['score'][s] == r['score'][o] else 0,
            'xGF': r['xg'][s], 'xGA': r['xg'][o], 'xGD': r['xg'][s] - r['xg'][o]}


def stats(v):
    if not v: return float('nan'), float('nan')
    n = len(v); m = sum(v) / n; sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1)) if n > 1 else 0
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def load(*dirs):
    data = {}
    for d in dirs:
        meta = json.load(open(d / 'meta.json'))
        for line in open(d / 'results.jsonl'):
            r = json.loads(line); match, cond = r['cond'].split('|', 1)
            data.setdefault(cond, {})[(match, r['seed'])] = own(r, meta['sides'][match]) | {'match': match}
    return data


def analyse(out, study5):
    data = load(study5, out); base = data['natural']; result = {}
    cohesion = {}
    for cond, rows in data.items():
        if cond.startswith('team_cohesion='):
            for k, v in rows.items(): cohesion.setdefault(k[0], {})[int(cond.split('=')[1])] = cohesion.get(k[0], {}).get(int(cond.split('=')[1]), {}) | {k[1]: v}
    def diff(rows, seeds):
        keys = [k for k in rows if k in base and seeds(k[1])]
        return {m: stats([rows[k][m] - base[k][m] for k in keys]) for m in ('pts', 'xGD', 'xGF', 'xGA')} | {'n': len(keys)}
    for name in CONFIRM + ['positions all natural', 'positions natural, goalkeeper as stored']:
        if name not in data: continue
        result[name] = {'screen (seeds 1-30)': diff(data[name], lambda s: s <= 30), 'confirm (seeds 31-120)': diff(data[name], lambda s: s > 30)}
    lo_hi = {'pts': [], 'xGD': []}
    for match, levels in cohesion.items():
        lo, hi = levels[min(levels)], levels[max(levels)]
        for s in lo:
            if s in hi and s > 30:
                for m in lo_hi: lo_hi[m].append(hi[s][m] - lo[s][m])
    if lo_hi['pts']: result['team cohesion high vs low'] = {'confirm (seeds 31-120)': {m: stats(v) for m, v in lo_hi.items()} | {'n': len(lo_hi['pts'])}}
    for name, parts in result.items():
        print(name)
        for part, v in parts.items():
            if not v['n']: continue
            print(f"   {part:24} n={v['n']:4}  ppg {v['pts'][0]:+.3f} ({v['pts'][1]:+.1f})  xGD {v['xGD'][0]:+.3f} ({v['xGD'][1]:+.1f})")
    json.dump(result, open(out / 'effects.json', 'w'), indent=1)


if __name__ == '__main__':
    mode, out, study5 = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    build(out, study5) if mode == 'build' else analyse(out, study5)
