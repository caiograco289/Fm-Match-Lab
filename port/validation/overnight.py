"""Overnight sensitivity study on the Mac host (FM27 engine path). Resumable; one summary line per match.

  python port/validation/overnight.py build OUT DEFAULTS.json PRESETS.jsonl TEAM [FMF ...]   # needs the app server
  python port/validation/overnight.py run OUT PARALLEL
  python port/validation/overnight.py analyse OUT                                          # writes OUT/report.md

Base scenario: the default fixture's 4-3-3 on both sides, every player 13 in every attribute (raw 65), natural (20)
in every position, 180 cm / 70 kg, controlled start. Changes are made to the home side (side 0) only and compared
with the base on the same seeds. Lineup slots: GK 0, FB 1+4, CB 2+3, MID 5-7, W 8+9, ST 10.

Experiments (in run order):
  E  start state (whole home team): condition, sharpness, fatigue, morale, team and club cohesion
  CT tactical-effectiveness record fields on the user's real saved matches (TEAM's side), against natural records
  CP tactical-effectiveness record (overall, buy-in, next-match) by position group on the base scenario
  A  each attribute at 3 / 8 / 18 for the whole home team (13 = base)
  D  tactics (one installed preset per style + importable .fmf files) vs a benchmark, at low and high effectiveness
  B  each attribute at 3 and 18 for one position group
"""
import base64, copy, glob, json, math, os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOST = Path(os.environ.get('FM27_STUDY_HOST') or ROOT / 'private/engine/fm27_native/fm27_mac_host')   # a frozen copy keeps long runs on one binary
FIXTURE = ROOT / 'private/engine/fm27_native/fixtures/match.pkm'
SAVED = Path.home() / 'Library/Application Support/Sports Interactive/Football Manager 27/matches/automatic'
BASE_LEVEL = 13
GROUPS = {'GK': [0], 'FB': [1, 4], 'CB': [2, 3], 'MID': [5, 6, 7], 'W': [8, 9], 'ST': [10]}
GK_ONLY = {'Handling', 'AerialReach', 'CommandOfArea', 'Communication', 'Kicking', 'Throwing', 'OneOnOnes', 'Reflexes',
           'RushingOut', 'TendencyToPunch', 'Eccentricity'}
EXEC = {'raw': 0x1c, 'role': 0x1d, 'overall': 0x1e, 'buyin': 0x1f, 'next': 0x20}
START = {'condition': ([40, 60, 80], lambda v: {'condition': v * 100}),
         'sharpness': ([25, 50, 75], lambda v: {'sharpness': v * 100, 'sharpness_secondary': v * 100}),
         'fatigue': ([16000, 32000, 48000, 65535], lambda v: {'fatigue_raw': v}),
         'morale': ([1, 5, 10, 15], lambda v: {'morale': v}),
         'team_cohesion': ([45, 55, 65, 85], lambda v: {'team_cohesion': v}),
         'club_cohesion': ([0, 25, 50, 75], lambda v: {'club_cohesion': v})}
SEEDS = {'base': 60, 'E': 60, 'CT': 20, 'CP': 40, 'A': 40, 'D': 30, 'B': 30}


def server():
    sys.path.insert(0, str(ROOT / 'build/source'))
    import fm27_tactics_server as app
    return app


def level(team, value):
    for p in team['players']:
        for i in range(15): p['attributes'][i] = 20
        for i in range(15, 69): p['attributes'][i] = value * 5
        p['native_profile'].update(height_cm=180, weight_kg=70)


def fields(side, values, slots=None):
    where = f"{side}@{'.'.join(map(str, slots))}" if slots else str(side)
    return ','.join(f'{where}:{EXEC[k]}={v}' for k, v in values.items())


def build(out, defaults, presets, team, fmfs):
    app = server(); out.mkdir(parents=True, exist_ok=True); bins = out / 'bins'; bins.mkdir(exist_ok=True)
    attributes = [a['name'] for a in json.load(open(ROOT / 'private/catalog.json'))['attributes']]
    base = json.load(open(defaults)); base = base.get('scenario', base)
    for t in base['teams']: level(t, BASE_LEVEL)
    base = app.validate_scenario(base)
    jobs = []   # (exp, cond, fixture, bin, env, seeds)

    def write(name, scenario):
        path = bins / f'{name}.bin'; path.write_bytes(app.encode_scenario(scenario)); return str(path)

    base_bin = write('base', base)
    jobs.append(('base', 'base', str(FIXTURE), base_bin, '', SEEDS['base']))
    for key, (levels, make) in START.items():
        for v in levels:
            s = copy.deepcopy(base); s['initial_state'] = 'custom'
            for p in s['teams'][0]['players']: p['native_profile'].update(make(v))
            jobs.append(('E', f'{key}={v}', str(FIXTURE), write(f'E_{key}_{v}', app.validate_scenario(s)), '', SEEDS['E']))
    for f in sorted(glob.glob(str(SAVED / '*/*.pkm'))):
        name = Path(f).stem.replace('_VER_fm', ''); home, away = name.rsplit('_', 1)[0].split('_v_')
        if team not in (home, away): continue
        side = 0 if home == team else 1
        jobs.append(('CT', f'{name}|natural', f, '', '', SEEDS['CT']))
        for k in EXEC:
            for v in (10, 50, 90):
                jobs.append(('CT', f'{name}|{k}={v}', f, '', fields(side, {k: v}), SEEDS['CT']))
    record = lambda v: {'overall': v, 'buyin': v, 'next': v}
    for v in (10, 90):
        jobs.append(('CP', f'team={v}', str(FIXTURE), base_bin, fields(0, record(v)), SEEDS['CP']))
        for g, slots in GROUPS.items():
            jobs.append(('CP', f'{g}={v}', str(FIXTURE), base_bin, fields(0, record(v), slots), SEEDS['CP']))
    for a in range(15, 69):
        for v in (3, 8, 18):
            s = copy.deepcopy(base)
            for p in s['teams'][0]['players']: p['attributes'][a] = v * 5
            jobs.append(('A', f'{attributes[a]}={v}', str(FIXTURE), write(f'A_{a}_{v}', app.validate_scenario(s)), '', SEEDS['A']))
    # D: tactics vs the benchmark (installed Gegenpress 433-433), tactic on either side, record low / high.
    rows = [json.loads(l) for l in open(presets)]
    templates = [r for r in rows if r['event'] == 'installed_tactic_preset']
    for t in templates: t['name'] = bytes.fromhex(t['name_utf8_hex']).decode()
    bench = templates[16]; tactics = []; seen = set()
    for t in templates:
        style = t['name'].replace('Custom ', '')
        if style not in seen: seen.add(style); tactics.append(('preset', 'FM preset ' + style, t))
    for f in fmfs: tactics.append(('fmf', Path(f).stem, f))
    import urllib.request
    def api(path, data):
        r = urllib.request.Request('http://127.0.0.1:18765' + path, json.dumps(data).encode(), {'Content-Type': 'application/json'})
        return json.loads(urllib.request.urlopen(r, timeout=300).read())
    for kind, name, source in tactics:
        for side in (0, 1):
            try:
                s = copy.deepcopy(base)
                app.desktop_tactic_plan.apply(app, s['teams'][1 - side], bench)
                if kind == 'preset':
                    app.desktop_tactic_plan.apply(app, s['teams'][side], source); s = app.validate_scenario(s)
                else:
                    s = app.validate_scenario(s)
                    s = api('/api/import-fmf', {'side': side, 'scenario': s, 'file_base64': base64.b64encode(open(source, 'rb').read()).decode()})['scenario']
                b = write(f'D_{len(jobs)}', s)
            except Exception as e:
                print('D skip', name, side, str(e)[:120], flush=True); break
            for v in (20, 80):
                jobs.append(('D', f'{name}|side={side}|record={v}', str(FIXTURE), b, fields(side, record(v)), SEEDS['D']))
    for g, slots in GROUPS.items():
        for a in range(15, 69):
            if g != 'GK' and attributes[a] in GK_ONLY: continue
            for v in (3, 18):
                s = copy.deepcopy(base)
                for i in slots: s['teams'][0]['players'][s['teams'][0]['lineup'][i]]['attributes'][a] = v * 5
                jobs.append(('B', f'{g}|{attributes[a]}={v}', str(FIXTURE), write(f'B_{g}_{a}_{v}', app.validate_scenario(s)), '', SEEDS['B']))
    (out / 'jobs.json').write_text(json.dumps(jobs))
    print(len(jobs), 'conditions,', sum(j[5] for j in jobs), 'matches')


def summarise(path):
    r = {'goals': [[], []], 'cards': [0, 0]}
    for line in open(path):
        e = json.loads(line)
        ev = e.get('event')
        if ev == 'natural_match_finished': r['score'] = e['score']
        elif ev == 'native_match_statistics':
            for k in ('xg', 'shots', 'shots_on_target', 'possession', 'passes', 'completed_passes'):
                r[k] = [round(t[k], 4) if isinstance(t[k], float) else t[k] for t in e['teams']]
        elif ev == 'native_final_incident_registry':
            for i in e.get('incidents', []):
                # 1 = goal, 3 = penalty goal (scorer's side); 2 = own goal (registry side = the player's team, credited
                # to the other side, as fm27_match_events.collect does)
                if i['native_type'] in (1, 3) and i['side'] < 2: r['goals'][i['side']].append(i['nominal_minute'] + i['added_minute'])
                if i['native_type'] == 2 and i['side'] < 2: r['goals'][1 - i['side']].append(i['nominal_minute'] + i['added_minute'])
                if i['native_type'] == 38 and i['side'] < 2: r['cards'][i['side']] += 1
    return r if 'score' in r and 'xg' in r else None


def run(out, parallel):
    jobs = json.load(open(out / 'jobs.json'))
    done = set()
    results = out / 'results.jsonl'
    if results.exists():
        for line in open(results):
            r = json.loads(line); done.add((r['exp'], r['cond'], r['seed']))
    out = out.resolve(); work = out / 'work'; shutil.rmtree(work, ignore_errors=True); work.mkdir()
    chunks = []
    for exp, cond, fixture, b, env, n in jobs:
        todo = [s for s in range(1 if exp != 'CT' else 31, (1 if exp != 'CT' else 31) + n) if (exp, cond, s) not in done]
        for i in range(0, len(todo), 30): chunks.append((exp, cond, fixture, b, env, todo[i:i + 30]))
    print(f'{len(chunks)} chunks, {sum(len(c[5]) for c in chunks)} matches to run', flush=True)
    log = open(out / 'run.log', 'a')

    def one(index_chunk):
        index, (exp, cond, fixture, b, env, seeds) = index_chunk
        d = work / str(index); d.mkdir()
        lines = ['FM27DW1']
        b = str(Path(b).resolve()) if b else ''; fixture = str(Path(fixture).resolve())
        for s in seeds: lines += [fixture, b, str(d / f'{s}.jsonl'), str(s), '-']
        (d / 'manifest').write_text('\n'.join(lines) + '\n')
        e = dict(os.environ); e.pop('FM27_MAC_EXEC_FIELDS', None)
        if isinstance(env, dict): e.update(env)   # e.g. {'FM27_MAC_ATTR': ...}
        elif env: e['FM27_MAC_EXEC_FIELDS'] = env
        code = subprocess.run([str(HOST), '--worker-manifest', str(d / 'manifest'), '--output', str(d / 'startup.jsonl'),
                               '--cancel-event', str(d / 'cancel')], env=e, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        rows = []
        for s in seeds:
            p = d / f'{s}.jsonl'
            r = summarise(p) if p.exists() else None
            if r: rows.append(dict(exp=exp, cond=cond, seed=s, **r))
        return index, code, len(seeds), rows, d

    began = time.time(); total = 0
    with ThreadPoolExecutor(parallel) as pool, open(results, 'a') as sink:
        for index, code, n, rows, d in pool.map(one, enumerate(chunks)):
            for r in rows: sink.write(json.dumps(r) + '\n')
            sink.flush(); total += len(rows)
            if code or len(rows) != n: log.write(f'chunk {index} {chunks[index][:2]} exit {code}: {len(rows)}/{n}\n'); log.flush()
            shutil.rmtree(d, ignore_errors=True)
            if index % 20 == 0:
                log.write(f'{time.strftime("%H:%M")} {total} matches, {total / max(1, time.time() - began) * 3600:.0f}/h\n'); log.flush()
    log.write(f'{time.strftime("%H:%M")} finished: {total} matches\n'); log.close()


def stats(diffs):
    n = len(diffs)
    if n < 2: return float('nan'), float('nan')
    m = sum(diffs) / n; sd = math.sqrt(sum((v - m) ** 2 for v in diffs) / (n - 1))
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def analyse(out):
    data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); data.setdefault((r['exp'], r['cond']), {})[r['seed']] = r
    base = data.get(('base', 'base'), {})
    pts = lambda r, s=0: 3 if r['score'][s] > r['score'][1 - s] else 1 if r['score'][0] == r['score'][1] else 0
    xgd = lambda r, s=0: r['xg'][s] - r['xg'][1 - s]
    gd = lambda r, s=0: r['score'][s] - r['score'][1 - s]
    lines = ['# Overnight sensitivity study (FM27 engine path, Mac host)', '',
             'Paired by seed against the base unless stated: mean difference (t). |t| ≥ 2 is marked **bold**.', '']

    def fmt(m, t):
        s = f'{m:+.2f} ({t:+.1f})'
        return f'**{s}**' if abs(t) >= 2 else s

    def paired(rows, ref, f):
        keys = [k for k in rows if k in ref]
        return stats([f(rows[k]) - f(ref[k]) for k in keys]) + (len(keys),)

    def describe(rows, side=0):
        n = len(rows); rs = list(rows.values())
        if not n: return '', 0
        w = sum(pts(r, side) == 3 for r in rs); d = sum(pts(r, side) == 1 for r in rs)
        return f"{w}-{d}-{n - w - d}", sum(pts(r, side) for r in rs) / n

    if base:
        rec, ppg = describe(base)
        g = [sum(r['score'][i] for r in base.values()) / len(base) for i in (0, 1)]
        x = [sum(r['xg'][i] for r in base.values()) / len(base) for i in (0, 1)]
        lines += [f'Base (n={len(base)}): home {rec}, {ppg:.2f} ppg, goals {g[0]:.2f}-{g[1]:.2f}, xG {x[0]:.2f}-{x[1]:.2f}', '']

    def table(title, exp, note=''):
        conds = [c for (e, c) in data if e == exp]
        if not conds: return
        lines.extend([f'## {title}', note, '', '| condition | n | W-D-L | ppg | Δ points | Δ GD | Δ xGD | Δ xG for | Δ xG against |', '|---|---|---|---|---|---|---|---|---|'])
        for c in conds:
            rows = data[(exp, c)]; rec, ppg = describe(rows)
            p = paired(rows, base, pts); g = paired(rows, base, gd); x = paired(rows, base, xgd)
            xf = paired(rows, base, lambda r: r['xg'][0]); xa = paired(rows, base, lambda r: r['xg'][1])
            lines.append(f'| {c} | {p[2]} | {rec} | {ppg:.2f} | {fmt(*p[:2])} | {fmt(*g[:2])} | {fmt(*x[:2])} | {fmt(*xf[:2])} | {fmt(*xa[:2])} |')
        lines.append('')

    table('E. Start state (whole home team)', 'E', 'Base: condition 100%, sharpness 100%, fatigue 0, morale 20, team cohesion 80, club cohesion 100.')
    table('CP. Tactical-effectiveness record by position group (overall, buy-in, next-match held at the value)', 'CP',
          'The base has the engine\'s own records for this fixture (overall ≈ 17-21, buy-in and next-match 0).')
    # A: matrix
    attrs = sorted({c.split('=')[0] for (e, c) in data if e == 'A'}, key=lambda a: a)
    if attrs:
        lines += ['## A. Attributes, whole home team (base 13)', '', 'Δ xGD per match against the base (t); Δ points for 3 and 18.', '',
                  '| attribute | 3: Δ xGD | 8: Δ xGD | 18: Δ xGD | 3: Δ pts | 18: Δ pts | range xGD (18 − 3) |', '|---|---|---|---|---|---|---|']
        rows_out = []
        for a in attrs:
            cells = {v: data.get(('A', f'{a}={v}'), {}) for v in (3, 8, 18)}
            xs = {v: paired(cells[v], base, xgd) for v in cells}; ps = {v: paired(cells[v], base, pts) for v in cells}
            spread = xs[18][0] - xs[3][0]
            rows_out.append((spread, f'| {a} | {fmt(*xs[3][:2])} | {fmt(*xs[8][:2])} | {fmt(*xs[18][:2])} | {fmt(*ps[3][:2])} | {fmt(*ps[18][:2])} | {spread:+.2f} |'))
        lines += [r for _, r in sorted(rows_out, key=lambda x: -abs(x[0]) if not math.isnan(x[0]) else 0)] + ['']
    # B: per group, 18 vs 3 (unpaired across conditions but same seeds -> paired by seed)
    groups = sorted({c.split('|')[0] for (e, c) in data if e == 'B'})
    if groups:
        lines += ['## B. Attributes by position group: 18 vs 3 (same seeds)', '',
                  'Δ = (group at 18) − (group at 3), others at 13. Top 12 per group by |Δ xGD|.', '']
        for g in GROUPS:
            if g not in groups: continue
            res = []
            for a in sorted({c.split('|')[1].split('=')[0] for (e, c) in data if e == 'B' and c.startswith(g + '|')}):
                hi, lo = data.get(('B', f'{g}|{a}=18'), {}), data.get(('B', f'{g}|{a}=3'), {})
                x = paired(hi, lo, xgd); p = paired(hi, lo, pts); xf = paired(hi, lo, lambda r: r['xg'][0]); xa = paired(hi, lo, lambda r: r['xg'][1])
                if not math.isnan(x[0]): res.append((abs(x[1]), a, x, p, xf, xa))
            res.sort(reverse=True)
            lines += [f'### {g} (slots {GROUPS[g]})', '', '| attribute | n | Δ xGD | Δ points | Δ xG for | Δ xG against |', '|---|---|---|---|---|---|']
            lines += [f'| {a} | {x[2]} | {fmt(*x[:2])} | {fmt(*p[:2])} | {fmt(*xf[:2])} | {fmt(*xa[:2])} |' for _, a, x, p, xf, xa in res[:12]] + ['']
    # CT: real matches, managed side
    ct = {c for (e, c) in data if e == 'CT'}
    if ct:
        lines += ['## CT. Record fields on the real saved matches (managed side; opponent natural)', '',
                  'Paired by match and seed against the natural records. Points, GD and xGD from the managed side.', '',
                  '| field = value | n | ppg | Δ points | Δ GD | Δ xGD |', '|---|---|---|---|---|---|']
        matches = sorted({c.split('|')[0] for c in ct})
        team = os.environ.get('OVERNIGHT_TEAM') or sys.exit('set OVERNIGHT_TEAM to your team (as in the saved match file names)')
        def side_of(m): return 0 if m.split('_v_')[0] == team else 1
        for k in EXEC:
            for v in (10, 50, 90):
                pairs = {'p': [], 'g': [], 'x': []}; total = 0; n = 0
                for m in matches:
                    s = side_of(m); nat = data.get(('CT', f'{m}|natural'), {}); cur = data.get(('CT', f'{m}|{k}={v}'), {})
                    for seed in cur:
                        if seed not in nat: continue
                        pairs['p'].append(pts(cur[seed], s) - pts(nat[seed], s)); pairs['g'].append(gd(cur[seed], s) - gd(nat[seed], s))
                        pairs['x'].append(xgd(cur[seed], s) - xgd(nat[seed], s)); total += pts(cur[seed], s); n += 1
                if n: lines.append(f"| {k} = {v} | {n} | {total / n:.2f} | {fmt(*stats(pairs['p']))} | {fmt(*stats(pairs['g']))} | {fmt(*stats(pairs['x']))} |")
        nat_pts = [pts(r, side_of(m)) for m in matches for r in data.get(('CT', f'{m}|natural'), {}).values()]
        if nat_pts: lines.append(f'| natural | {len(nat_pts)} | {sum(nat_pts) / len(nat_pts):.2f} | | | |')
        lines.append('')
    # D: tactics x effectiveness
    dconds = [c for (e, c) in data if e == 'D']
    if dconds:
        names = sorted({c.split('|')[0] for c in dconds})
        res = []
        for nme in names:
            out_row = [nme]
            for v in (20, 80):
                ps = []; xs = []
                for side in (0, 1):
                    for r in data.get(('D', f'{nme}|side={side}|record={v}'), {}).values(): ps.append(pts(r, side)); xs.append(xgd(r, side))
                out_row.append((sum(ps) / len(ps) if ps else float('nan'), sum(xs) / len(xs) if xs else float('nan'), len(ps)))
            res.append(out_row)
        lines += ['## D. Tactics vs the benchmark (Gegenpress 433-433, natural records) at low and high effectiveness', '',
                  'Tactic side record (overall, buy-in, next-match) held at 20 (low) or 80 (high); home and away pooled.', '',
                  '| tactic | low: ppg | low: xGD | high: ppg | high: xGD | rank low | rank high |', '|---|---|---|---|---|---|---|']
        low_rank = {r[0]: i + 1 for i, r in enumerate(sorted(res, key=lambda r: -r[1][0]))}
        high_rank = {r[0]: i + 1 for i, r in enumerate(sorted(res, key=lambda r: -r[2][0]))}
        for r in sorted(res, key=lambda r: -r[2][0]):
            lines.append(f'| {r[0]} | {r[1][0]:.2f} | {r[1][1]:+.2f} | {r[2][0]:.2f} | {r[2][1]:+.2f} | {low_rank[r[0]]} | {high_rank[r[0]]} |')
        lines.append('')
    (out / 'report.md').write_text('\n'.join(lines))
    print('\n'.join(lines[:12]))


if __name__ == '__main__':
    mode, out = sys.argv[1], Path(sys.argv[2])
    if mode == 'build': build(out, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6:])
    elif mode == 'run': run(out, int(sys.argv[3]))
    elif mode == 'analyse': analyse(out)
