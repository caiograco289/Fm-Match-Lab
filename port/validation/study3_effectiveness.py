"""Study 3 (docs/studies): tactical familiarity, i.e. FM27's tactical-effectiveness record, on the real saved matches.

FM27 shows familiarity as "Tactical Effectiveness" (Training > Tactical Effectiveness). Its parts sit in the 33-byte
record per player (port/map/exec_record.py), identified against the game's panel on two matches (03 page):
  areas  8 triples (+1..+0x18), one per tactical area (In Possession Shape, Passing Style, Build Up, Chance Creation,
         Out Of Possession Shape, Line Of Engagement, Pressing Intensity, Pressing Trap). Byte 2 of each triple is
         match exposure (rose ~2 for every starter after one match, capped at 100); byte 1 (and its copy, byte 0)
         is the training contribution for that area.
  0x19   team tactical complexity (higher = lower effectiveness); 0x1a per-role complexity
  0x00   player tactical ability = (median of Anticipation, Decisions, Composure, Concentration, Versatility on
         the 1-20 scale - 1) * 100/19 (44/44 players)
Each condition holds fields at one value for every player of the team (data writes after preparation and before every
step, FM27_MAC_EXEC_FIELDS), on the 10 matches x seeds 1-30 of Study 1, which also supplies the natural baseline.

  python port/validation/study3_effectiveness.py build OUT STUDY1_DIR
  FM27_STUDY_HOST=... python port/validation/overnight.py run OUT 6
  python port/validation/study3_effectiveness.py analyse OUT
"""
import json, math, sys
from pathlib import Path

TRIPLES = range(1, 25, 3)
EXPOSURE = [o + 2 for o in TRIPLES]
TRAINING = [o + k for o in TRIPLES for k in (0, 1)]
GROUPS = {
    'exposure': (EXPOSURE, [0, 25, 50, 75, 100]),
    'training': (TRAINING, [0, 25, 50, 75, 100]),
    'areas': (EXPOSURE + TRAINING, [0, 50, 100]),
    'complexity': ([0x19], [0, 50, 100]),
    'role_complexity': ([0x1a], [0, 100]),
    'tactical_ability': ([0x00], [25, 50, 75, 100]),
}


def build(out, study1):
    out.mkdir(parents=True, exist_ok=True)
    meta = json.load(open(study1 / 'meta.json'))
    naturals = [j for j in json.load(open(study1 / 'jobs.json')) if j[1].endswith('|natural')]
    jobs = []
    for j in naturals:
        match = j[1].split('|')[0]; side = meta['sides'][match]
        jobs.append(['F', f'{match}|natural', j[2], j[3], {}, j[5]])
        for group, (offsets, levels) in GROUPS.items():
            for v in levels:
                spec = ','.join(f'{side}:{o}={v}' for o in offsets)
                jobs.append(['F', f'{match}|{group}={v}', j[2], j[3], {'FM27_MAC_EXEC_FIELDS': spec}, j[5]])
    (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps(meta | {'groups': {g: [o, l] for g, (o, l) in GROUPS.items()}}))
    print(len(jobs), 'jobs,', sum(j[5] for j in jobs), 'matches')


def own(r, s):
    o = 1 - s
    return {'pts': 3 if r['score'][s] > r['score'][o] else 1 if r['score'][s] == r['score'][o] else 0,
            'GF': r['score'][s], 'GA': r['score'][o], 'xGF': r['xg'][s], 'xGA': r['xg'][o],
            'xGD': r['xg'][s] - r['xg'][o], 'shots': r['shots'][s], 'shotsA': r['shots'][o]}


def stats(v):
    n = len(v); m = sum(v) / n; sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1)) if n > 1 else 0
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def analyse(out):
    meta = json.load(open(out / 'meta.json'))
    data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); match, cond = r['cond'].split('|')
        data.setdefault(cond, {})[(match, r['seed'])] = own(r, meta['sides'][match])
    base = data['natural']
    result = {'natural': {m: sum(x[m] for x in base.values()) / len(base) for m in ('pts', 'GF', 'GA', 'xGF', 'xGA', 'xGD', 'shots', 'shotsA')} | {'n': len(base)}}
    for cond, rows in sorted(data.items()):
        if cond == 'natural': continue
        keys = [k for k in rows if k in base]
        result[cond] = {m: stats([rows[k][m] - base[k][m] for k in keys]) for m in ('pts', 'GF', 'GA', 'xGF', 'xGA', 'xGD', 'shots', 'shotsA')} | {'n': len(keys)}
        print(f"{cond:22} n={len(keys):3}  ppg {result[cond]['pts'][0]:+.3f} ({result[cond]['pts'][1]:+.1f})  xGD {result[cond]['xGD'][0]:+.3f} ({result[cond]['xGD'][1]:+.1f})  xGF {result[cond]['xGF'][0]:+.3f}  xGA {result[cond]['xGA'][0]:+.3f}")
    json.dump(result, open(out / 'effects.json', 'w'), indent=1)


if __name__ == '__main__':
    mode, out = sys.argv[1], Path(sys.argv[2])
    build(out, Path(sys.argv[3])) if mode == 'build' else analyse(out)
