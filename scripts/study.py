"""Studies on your own saved matches: what is a change worth, measured over many replays.

Each condition changes one thing for your team and replays every chosen match on the same seeds as the unchanged
match (the "natural" replay), so each comparison is paired. The report gives, per condition, the average difference
in points per game and expected-goal difference (xGD) with a t value: |t| >= 2 is about 95% confidence, |t| >= 3 solid.

  .venv/bin/python scripts/study.py new runs/my-study --team "Your Club" [--newest 10] [--seeds 30]
  .venv/bin/python scripts/study.py add runs/my-study attribute:Pace attribute:Finishing familiarity:20 ...
  .venv/bin/python scripts/study.py run runs/my-study [--workers 6]       # resumable; FM27 must be closed
  .venv/bin/python scripts/study.py report runs/my-study                  # writes runs/my-study/report.md

Condition specs (your team only; the opponent is unchanged):
  attribute:NAME[:STEP]      whole squad -STEP and +STEP in-game points (default 5); reported per point
  attributes[:STEP]          every attribute, as above (109 conditions)
  familiarity:LEVEL          the eight tactical areas of every player's effectiveness record held at LEVEL (0-100)
  start:FIELD=VALUE          start state for the whole squad: condition=90 (percent), sharpness=75 (percent),
                             morale=1-20, team_cohesion=low|high|0-100, club_cohesion=0-100
  mentality:+1 / mentality:-2
  instruction:GROUP=OPTION   one team instruction, by its English names, e.g. "instruction:Pressing trap=Show outside"
  instructions               every option of every team instruction, one at a time
  in-match:ai|assistant|fixed   who manages your team during the match
  tactic:FILE.fmf            play this FM27 tactic file (through the game's parser); tactics:FOLDER for every file

Matches are FM27's own saved matches (matches/automatic, or FM27_SAVED_MATCHES). Results stay in the study folder;
keep it outside the repository or under a git-ignored folder (runs/ is ignored).
"""
import argparse, base64, copy, json, math, os, re, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'port/validation')); sys.path.insert(0, str(ROOT / 'src'))
os.environ.setdefault('FM27_ENGINE_ROOT', str(ROOT / 'private/engine'))
os.environ.setdefault('FM27_DESKTOP_DATA', tempfile.mkdtemp(prefix='fm27-study-'))
AREAS = [o + k for o in range(1, 25, 3) for k in (0, 1, 2)]   # the 24 area bytes of the effectiveness record
MEASURES = ('pts', 'xGD', 'xGF', 'xGA', 'GF', 'GA', 'shots', 'shotsA')
_app = None


def app():
    global _app
    if _app is None:
        web = ROOT / 'src/tactics_ui/catalog.json'   # the server reads its git-ignored copy of the catalogue
        if not web.is_file(): web.write_bytes((ROOT / 'private/catalog.json').read_bytes())
        import fm27_tactics_server
        _app = fm27_tactics_server
    return _app


def load(out): return json.loads((out / 'study.json').read_text(encoding='utf8'))
def save(out, s): (out / 'study.json').write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding='utf8')


def cmd_new(a):
    import exec_real
    found = exec_real.matches(a.team.replace(' ', '_'))
    if not found: raise SystemExit(f'No saved matches with {a.team} in {exec_real.SAVED}')
    found.sort(key=lambda m: Path(m[1]).stat().st_mtime, reverse=True)
    if a.newest: found = found[:a.newest]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    save(out, {'team': a.team, 'seeds': a.seeds, 'matches': [{'name': n, 'path': str(Path(p).resolve()), 'side': s} for n, p, s in found],
               'conditions': []})
    print(f'{len(found)} matches of {a.team}, seeds 1-{a.seeds}: {len(found) * a.seeds} matches per condition')


def attribute_ids():
    return {x['name'].lower(): (x['id'], x['name']) for x in json.loads((ROOT / 'private/catalog.json').read_text(encoding='utf8'))['attributes'] if not x['position']}


def expand(spec):
    """A spec string -> list of conditions {'name', 'kind', ...}."""
    kind, _, arg = spec.partition(':')
    if kind == 'attributes':
        step = int(arg or 5)
        return [c for _, name in sorted(attribute_ids().values()) for c in expand(f'attribute:{name}:{step}')]
    if kind == 'attribute':
        name, _, step = arg.partition(':'); step = int(step or 5)
        aid, label = attribute_ids().get(name.lower().replace(' ', ''), (None, None))
        if aid is None: raise SystemExit(f'Unknown attribute {name!r}')
        return [{'name': f'{label}{sign}{step}', 'kind': 'attribute', 'id': aid, 'stored': (-1 if sign == '-' else 1) * step * 5, 'pair': label, 'step': step}
                for sign in '-+']
    if kind == 'familiarity':
        return [{'name': f'familiarity {int(arg)}', 'kind': 'familiarity', 'level': int(arg)}]
    if kind == 'start':
        field, _, value = arg.partition('=')
        return [{'name': f'{field}={value}', 'kind': 'start', 'field': field, 'value': value}]
    if kind == 'mentality':
        return [{'name': f'mentality {int(arg):+d}', 'kind': 'mentality', 'step': int(arg)}]
    if kind == 'instruction':
        group, _, option = arg.partition('=')
        return [{'name': f'TI {group}={option}', 'kind': 'instruction', 'group': group, 'option': option}]
    if kind == 'instructions':
        return [{'name': f'TI {g["label"]}={o["label"]}', 'kind': 'instruction', 'group': g['label'], 'option': o['label']}
                for g in app().GROUPS.values() for o in g['options']]
    if kind == 'in-match':
        return [{'name': f'in-match {arg}', 'kind': 'in_match', 'mode': arg}]
    if kind == 'tactic':
        return [{'name': f'tactic {Path(arg).stem}', 'kind': 'tactic', 'path': str(Path(arg).expanduser().resolve())}]
    if kind == 'tactics':
        return [c for f in sorted(Path(arg).expanduser().glob('*.fmf')) for c in expand(f'tactic:{f}')]
    raise SystemExit(f'Unknown condition {spec!r} (see --help)')


def cmd_add(a):
    out = Path(a.out); s = load(out); names = {c['name'] for c in s['conditions']}
    new = [c for spec in a.specs for c in expand(spec) if c['name'] not in names]
    s['conditions'] += new; save(out, s)
    print(f'{len(new)} conditions added, {len(s["conditions"])} in total')


def edit_scenario(base, side, c):
    """Apply a scenario condition to a copy of the saved match's scenario, through the app's own validator."""
    A = app(); s = copy.deepcopy(base); t = s['teams'][side]
    squad = t['players'][:t.get('roster_size', len(t['players']))]
    if c['kind'] == 'start':
        f, v = c['field'], c['value']
        if f == 'team_cohesion' and v in ('low', 'high'): v = base['match_base']['cohesion_ranges'][side][v == 'high']
        v = int(v)
        upd = {'condition': {'condition': v * 100}, 'sharpness': {'sharpness': v * 100, 'sharpness_secondary': v * 100},
               'morale': {'morale': v}, 'team_cohesion': {'team_cohesion': v}, 'club_cohesion': {'club_cohesion': v}}.get(f)
        if upd is None: raise ValueError(f'unknown start field {f}')
        for p in squad: p['native_profile'].update(upd)
    elif c['kind'] == 'mentality':
        ids = sorted(m['id'] for m in A.CATALOG['mentalities']); i = ids.index(t['mentality']) + c['step']
        if not 0 <= i < len(ids): raise ValueError('mentality out of range')
        t['mentality'] = ids[i]
    elif c['kind'] == 'instruction':
        norm = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
        g = next((g for g in A.GROUPS.values() if norm(c['group']) in (norm(g['label']), norm(g.get('name', '')))), None)
        o = g and next((o for o in g['options'] if norm(o['label']) == norm(c['option'])), None)
        if not o: raise ValueError(f'unknown instruction {c["group"]}={c["option"]}')
        if t['instructions'].get(str(g['id'])) == o['id']: raise ValueError('already the saved setting')
        t['instructions'][str(g['id'])] = o['id']
    elif c['kind'] == 'in_match':
        t['in_match'] = c['mode']
    elif c['kind'] == 'tactic':
        s = A.import_fmf({'side': side, 'scenario': s, 'file_base64': base64.b64encode(Path(c['path']).read_bytes()).decode()})['scenario']
    return A.encode_scenario(A.validate_scenario(s))


def build_jobs(out, s):
    jobs, skipped = [], {}
    bins = out / 'bins'; bins.mkdir(exist_ok=True)
    for m in s['matches']:
        jobs.append(['S', f'{m["name"]}|natural', m['path'], '', {}, s['seeds']])
        base = None
        for c in s['conditions']:
            env, blob = {}, None
            if c['kind'] == 'attribute':
                env['FM27_MAC_ATTR'] = f'{m["side"]}:{c["id"]}{c["stored"]:+d}'
            elif c['kind'] == 'familiarity':
                env['FM27_MAC_EXEC_FIELDS'] = ','.join(f'{m["side"]}:{o}={c["level"]}' for o in AREAS)
            else:
                if base is None: base = app().validate_scenario(app().SAVED_MATCHES.open(m['path']).default)
                try: blob = edit_scenario(base, m['side'], c)
                except Exception as e: skipped.setdefault(c['name'], []).append(f'{m["name"]}: {str(e)[:120]}'); continue
            f = ''
            if blob is not None:
                f = str(bins / f'{len(jobs)}.bin'); Path(f).write_bytes(blob)
            jobs.append(['S', f'{m["name"]}|{c["name"]}', m['path'], f, env, s['seeds']])
    (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps({'team': s['team'], 'sides': {m['name']: m['side'] for m in s['matches']}, 'skipped': skipped}))
    for name, why in skipped.items(): print(f'skipped {name}: {why[0]}' + (f' (+{len(why) - 1} more)' if len(why) > 1 else ''))
    return jobs


def cmd_run(a):
    import overnight
    out = Path(a.out).resolve(); s = load(out)
    if os.system('pgrep -f "fm.app/Contents/MacOS/Football Manager 27" >/dev/null') == 0: raise SystemExit('Close FM27 first.')
    jobs = build_jobs(out, s)
    total = sum(j[5] for j in jobs); hours = total / (1100 * a.workers)
    print(f'{len(jobs)} jobs, {total} matches (about {f"{hours:.1f} h" if hours >= 1 else f"{max(1, round(hours * 60))} min"} with {a.workers} workers)', flush=True)
    overnight.run(out, a.workers)


def stats(v):
    n = len(v)
    if n < 3: return float('nan'), float('nan')
    m = sum(v) / n; sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def cmd_report(a):
    out = Path(a.out); s = load(out); meta = json.loads((out / 'meta.json').read_text())
    data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); match, cond = r['cond'].split('|', 1); side = meta['sides'][match]; o = 1 - side
        data.setdefault(cond, {})[(match, r['seed'])] = {
            'pts': 3 if r['score'][side] > r['score'][o] else 1 if r['score'][side] == r['score'][o] else 0,
            'xGD': r['xg'][side] - r['xg'][o], 'xGF': r['xg'][side], 'xGA': r['xg'][o], 'GF': r['score'][side], 'GA': r['score'][o],
            'shots': r['shots'][side], 'shotsA': r['shots'][o]}
    base = data.get('natural', {})
    if not base: raise SystemExit('No natural replays yet.')
    f = lambda x: f'{x[0]:+.3f} ({x[1]:+.1f})'
    mean = lambda k: sum(v[k] for v in base.values()) / len(base)
    lines = [f'# Study: {s["team"]}', '', f'{len(s["matches"])} saved matches × seeds 1-{s["seeds"]}. Unchanged: {mean("pts"):.2f} points per game, '
             f'xG {mean("xGF"):.2f} for and {mean("xGA"):.2f} against ({len(base)} replays). Differences are paired by match and seed; t in brackets.', '']
    rows = []
    for c in s['conditions']:
        d = data.get(c['name'], {}); keys = [k for k in d if k in base]
        if keys: rows.append((c['name'], {m: stats([d[k][m] - base[k][m] for k in keys]) for m in MEASURES}, len(keys)))
    if rows:
        lines += ['## Each condition against the unchanged match', '', '| Condition | Points per game | xGD | xG for | xG against | n |', '|---|---|---|---|---|---|']
        for name, v, n in sorted(rows, key=lambda r: -abs(r[1]['xGD'][1])):
            lines.append(f"| {name} | {f(v['pts'])} | {f(v['xGD'])} | {v['xGF'][0]:+.3f} | {v['xGA'][0]:+.3f} | {n} |")
    pairs = {}
    for c in s['conditions']:
        if c['kind'] == 'attribute': pairs.setdefault(c['pair'], {})['+' if c['stored'] > 0 else '-'] = c
    slope = []
    for label, p in pairs.items():
        if set(p) != {'+', '-'}: continue
        lo, hi = data.get(p['-']['name'], {}), data.get(p['+']['name'], {}); keys = [k for k in lo if k in hi]
        if keys: slope.append((label, {m: stats([(hi[k][m] - lo[k][m]) / (2 * p['+']['step']) for k in keys]) for m in MEASURES}, len(keys)))
    if slope:
        lines += ['', '## Attributes: effect per in-game point (whole squad)', '', '| Attribute | Points per game | xGD | xG for | xG against | n |', '|---|---|---|---|---|---|']
        for name, v, n in sorted(slope, key=lambda r: -r[1]['xGD'][0]):
            lines.append(f"| {name} | {f(v['pts'])} | {f(v['xGD'])} | {v['xGF'][0]:+.3f} | {v['xGA'][0]:+.3f} | {n} |")
    if meta.get('skipped'): lines += ['', 'Skipped (the app rejected the change): ' + ', '.join(sorted(meta['skipped']))]
    lines += ['', 'With many conditions a few |t| of 2-3 appear by chance; rerun the interesting ones with more seeds before relying on them.']
    (out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf8'); print('\n'.join(lines))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    n = sub.add_parser('new'); n.add_argument('out'); n.add_argument('--team', required=True)
    n.add_argument('--newest', type=int, help='only the N most recent matches'); n.add_argument('--seeds', type=int, default=30)
    d = sub.add_parser('add'); d.add_argument('out'); d.add_argument('specs', nargs='+')
    r = sub.add_parser('run'); r.add_argument('out'); r.add_argument('--workers', type=int, default=6)
    t = sub.add_parser('report'); t.add_argument('out')
    a = p.parse_args()
    {'new': cmd_new, 'add': cmd_add, 'run': cmd_run, 'report': cmd_report}[a.cmd](a)


if __name__ == '__main__':
    main()
