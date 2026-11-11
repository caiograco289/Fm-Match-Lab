"""Study 5 (docs/studies): everything else the app can change, one condition at a time, for the team only, on the
10 real saved matches x seeds 1-30 of Study 1 (300 pairs per condition). Each scenario is the saved match opened
by the app and edited through the app's own validator and encoder; the baseline is the unedited scenario.

Groups: start state, body, person (personality, age, ability, reputation), position familiarity, mentality, every
team-instruction option, opposition instructions, in-match management.

  python port/validation/study5_everything.py build OUT STUDY1_DIR       # app environment (FM27_ENGINE_ROOT, ...)
  FM27_STUDY_HOST=... python port/validation/overnight.py run OUT 6
  python port/validation/study5_everything.py analyse OUT
"""
import copy, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))


def squad(team):
    return team['players'][:team.get('roster_size', len(team['players']))]


def conditions(app, base, side):
    """(name, edit(scenario) -> None) for one base; edits change the team (side) only."""
    out = []
    def prof(name, fn):
        def edit(s):
            for p in squad(s['teams'][side]): fn(p['native_profile'])
        out.append((name, edit))
    for v in (8000, 9000, 10000): prof(f'condition={v // 100}%', lambda q, v=v: q.update(condition=v))
    for v in (5000, 7500, 10000): prof(f'sharpness={v // 100}%', lambda q, v=v: q.update(sharpness=v, sharpness_secondary=v))
    for v in (5, 12, 20): prof(f'morale={v}', lambda q, v=v: q.update(morale=v))
    low, high = base['match_base']['cohesion_ranges'][side] if base.get('match_base', {}).get('cohesion_ranges') else (0, 100)
    for v in (low, high): prof(f'team_cohesion={v}', lambda q, v=v: q.update(team_cohesion=v))
    for v in (25, 100): prof(f'club_cohesion={v}', lambda q, v=v: q.update(club_cohesion=v))
    for d in (-10, 10): prof(f'height{d:+}cm', lambda q, d=d: q.update(height_cm=min(220, max(140, q['height_cm'] + d))))
    for d in (-10, 10): prof(f'weight{d:+}kg', lambda q, d=d: q.update(weight_kg=min(140, max(40, q['weight_kg'] + d))))
    for d in (-5, 5): prof(f'age{d:+}', lambda q, d=d: q.update(age=min(60, max(14, q['age'] + d))))
    for d in (-20, 20): prof(f'current_ability{d:+}', lambda q, d=d: q.update(current_ability=min(200, max(0, q['current_ability'] + d))))
    for k in ('professionalism', 'loyalty', 'sportsmanship', 'temperament', 'pressure', 'ambition', 'adaptability'):
        for v in (5, 18): prof(f'{k}={v}', lambda q, k=k, v=v: q.update({k: v}))
    for f in (0.5, 1.5):
        prof(f'reputation x{f}', lambda q, f=f: q.update({k: min(10000, int(q[k] * f)) for k in ('home_reputation', 'current_reputation', 'world_reputation')}))
    def positions(cap):
        def edit(s):
            t = s['teams'][side]
            for i in t['lineup']:
                a = t['players'][i]['attributes']
                for j in range(15): a[j] = 20 if cap == 20 else min(a[j], cap)
        return edit
    for cap in (20, 15, 10): out.append((f'positions {"all natural" if cap == 20 else f"capped at {cap}"}', positions(cap)))
    mentalities = sorted(m['id'] for m in app.CATALOG['mentalities'])
    current = base['teams'][side]['mentality']
    if current in mentalities:
        i = mentalities.index(current)
        for d in (-2, -1, 1, 2):
            if 0 <= i + d < len(mentalities):
                out.append((f'mentality {d:+}', lambda s, m=mentalities[i + d]: s['teams'][side].update(mentality=m)))
    for g in app.GROUPS.values():
        now = base['teams'][side]['instructions'].get(str(g['id']))
        for o in g['options']:
            if o['id'] == now: continue
            out.append((f'TI {g["name"]}={o["label"]}', lambda s, g=g, o=o: s['teams'][side]['instructions'].__setitem__(str(g['id']), o['id'])))
    neutral = app.unpack_oi(0x80000)
    out.append(('OI none', lambda s: s['teams'][side]['opposition'].__setitem__('players', [copy.deepcopy(neutral) for _ in s['teams'][side]['opposition']['players']])))
    for mode in ('assistant', 'ai'):
        out.append((f'in-match {mode}', lambda s, mode=mode: s['teams'][side].__setitem__('in_match', mode)))
    return out


def build(out, study1):
    import fm27_tactics_server as app
    out.mkdir(parents=True, exist_ok=True); bins = out / 'bins'; bins.mkdir(exist_ok=True)
    meta = json.load(open(study1 / 'meta.json'))
    naturals = [j for j in json.load(open(study1 / 'jobs.json')) if j[1].endswith('|natural')]
    jobs, skipped, names = [], {}, set()
    for j in naturals:
        match = j[1].split('|')[0]; side = meta['sides'][match]
        base = app.validate_scenario(app.SAVED_MATCHES.open(j[2]).default)
        for name, edit in [('natural', lambda s: None)] + conditions(app, base, side):
            s = copy.deepcopy(base)
            try:
                edit(s); s = app.validate_scenario(s); blob = app.encode_scenario(s)
            except Exception as e:
                skipped.setdefault(name, []).append(f'{match}: {str(e)[:100]}'); continue
            f = bins / f'{len(jobs)}.bin'; f.write_bytes(blob)
            jobs.append(['G', f'{match}|{name}', j[2], str(f), {}, j[5]]); names.add(name)
    (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps(meta | {'skipped': skipped}))
    print(len(jobs), 'jobs,', sum(j[5] for j in jobs), 'matches,', len(names), 'conditions; skipped:', {k: len(v) for k, v in skipped.items()})


def own(r, s):
    o = 1 - s
    return {'pts': 3 if r['score'][s] > r['score'][o] else 1 if r['score'][s] == r['score'][o] else 0,
            'GF': r['score'][s], 'GA': r['score'][o], 'xGF': r['xg'][s], 'xGA': r['xg'][o],
            'xGD': r['xg'][s] - r['xg'][o], 'shots': r['shots'][s], 'shotsA': r['shots'][o]}


def stats(v):
    n = len(v); m = sum(v) / n; sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1)) if n > 1 else 0
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def analyse(out):
    meta = json.load(open(out / 'meta.json')); data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); match, cond = r['cond'].split('|', 1)
        data.setdefault(cond, {})[(match, r['seed'])] = own(r, meta['sides'][match])
    base = data['natural']; result = {}
    for cond, rows in data.items():
        if cond == 'natural': continue
        keys = [k for k in rows if k in base]
        result[cond] = {m: stats([rows[k][m] - base[k][m] for k in keys]) for m in ('pts', 'GF', 'GA', 'xGF', 'xGA', 'xGD', 'shots', 'shotsA')} | {'n': len(keys)}
    for cond, v in sorted(result.items(), key=lambda kv: -abs(kv[1]['xGD'][1])):
        print(f"{cond:48} n={v['n']:3}  ppg {v['pts'][0]:+.3f} ({v['pts'][1]:+.1f})  xGD {v['xGD'][0]:+.3f} ({v['xGD'][1]:+.1f})  xGF {v['xGF'][0]:+.3f}  xGA {v['xGA'][0]:+.3f}")
    json.dump(result, open(out / 'effects.json', 'w'), indent=1)


if __name__ == '__main__':
    mode, out = sys.argv[1], Path(sys.argv[2])
    build(out, Path(sys.argv[3])) if mode == 'build' else analyse(out)
