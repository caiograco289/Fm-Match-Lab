"""Studies on your own saved matches: what is a change worth, measured over many replays.

Each condition changes one thing for your team and replays every chosen match on the same seeds as the unchanged
match (the "natural" replay), so each comparison is paired. The report gives, per condition, the average difference
in points per game and expected-goal difference (xGD) with a t value: |t| >= 2 is about 95% confidence, |t| >= 3 solid.

  .venv/bin/python scripts/study.py new runs/my-study --team "Your Club" [--newest 10] [--seeds 30]
  .venv/bin/python scripts/study.py add runs/my-study attribute:Pace attribute:Finishing familiarity:20 ...
  .venv/bin/python scripts/study.py run runs/my-study [--workers 6]       # resumable; FM27 may stay open
  .venv/bin/python scripts/study.py report runs/my-study                  # writes runs/my-study/report.md

  .venv/bin/python scripts/study.py new runs/vs-gegenpress --team "Your Club" --opponent-tactic "preset:Gegenpress"
  .venv/bin/python scripts/study.py league runs/league --team "Your Club" --tactics presets "tactics:~/FM27/tactics"

Condition specs (your team only; the opponent is unchanged):
  attribute:NAME[:STEP]      whole squad -STEP and +STEP in-game points (default 5); reported per point
  attributes[:STEP]          every attribute, as above (109 conditions)
  familiarity:LEVEL          the eight tactical areas of every player's effectiveness record held at LEVEL (0-100)
  area:NAME=LEVEL            one tactical area only (in-possession-shape, passing-style, build-up, chance-creation,
                             out-of-possession-shape, line-of-engagement, pressing-intensity, pressing-trap)
  start:FIELD=VALUE          start state for the whole squad: condition=90 (percent), sharpness=75 (percent),
                             morale=1-20, team_cohesion=low|high|0-100, club_cohesion=0-100
  mentality:+1 / mentality:-2
  instruction:GROUP=OPTION   one team instruction, by its English names, e.g. "instruction:Pressing trap=Show outside"
  instructions               every option of every team instruction, one at a time
  in-match:ai|assistant|fixed   who manages your team during the match
  tactic:FILE.fmf            play this FM27 tactic file (through the game's parser); tactics:FOLDER for every file
  tweak:NAME                 one of FM27's in-match Tactical Tweaks applied from kick-off, e.g. tweak:PressAggressively
                             (the game's own definition: team instructions set or shifted, player instructions,
                             mentality); tweaks for all of them (Swap Wings is not supported: it has no instructions)

Tactic specs (--opponent-tactic, league --tactics): FILE.fmf, tactics:FOLDER (every .fmf in it), preset:STYLE (one
installed FM27 preset, e.g. preset:Gegenpress) or presets (one per style). Every side that changes tactic picks its
starting XI from its matchday squad by position rating, as the app's "Pick by position", and is managed during the
match by the assistant (an AI-managed side would replace the tactic with its own at kick-off).

League: every tactic plays every other at home and away on one saved match (default: the team's newest), with both
sides' tactical familiarity held at the same level, and prints a table (points, goals for and against, xG) and the
head-to-head points. --squad SAVE.fm:Club puts one club's players from an FM27 save on both sides (needs fmsave;
see scripts/squad_from_save.py), so only the tactics differ.

Matches are FM27's own saved matches (matches/automatic, or FM27_SAVED_MATCHES). Results stay in the study folder;
keep it outside the repository or under a git-ignored folder (runs/ is ignored).
"""
import argparse, base64, copy, json, math, os, re, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'port/validation')); sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('FM27_ENGINE_ROOT', str(ROOT / 'private/engine'))
os.environ.setdefault('FM27_DESKTOP_DATA', tempfile.mkdtemp(prefix='fm27-study-'))
AREAS = [o + k for o in range(1, 25, 3) for k in (0, 1, 2)]   # the 24 area bytes of the effectiveness record
AREA_NAMES = ['in-possession-shape', 'passing-style', 'build-up', 'chance-creation', 'out-of-possession-shape',
              'line-of-engagement', 'pressing-intensity', 'pressing-trap']   # the record's eight triples, in order
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


def presets(folder):
    """{style: plan} for the installed FM27 presets, exported by the host from the game's data (cached in the study)."""
    cache = folder / 'presets.jsonl'
    if not cache.is_file():
        import subprocess
        fixture = ROOT / 'private/engine/fm27_native/fixtures/match.pkm'
        env = {k: v for k, v in os.environ.items() if not k.startswith('FM27_MAC_')} | {'FM27_COACH_PRESET_EXPORT': '1'}
        subprocess.run([str(ROOT / 'private/engine/fm27_native/fm27_mac_host'), '--fixture', str(fixture), '--inspect-fixture',
                        '--output', str(cache)], env=env, capture_output=True, timeout=300)
    out = {}
    for line in cache.read_text(encoding='utf8').splitlines():
        r = json.loads(line)
        if r.get('event') == 'installed_tactic_preset':
            out.setdefault(bytes.fromhex(r['name_utf8_hex']).decode().replace('Custom ', ''), r)
    if not out: raise SystemExit('Could not export the installed presets (is Steam running and FM27 closed?)')
    return out


def tactic_sources(specs, folder):
    """Tactic specs -> list of (name, kind, source)."""
    out = []
    for spec in specs:
        kind, _, arg = spec.partition(':')
        if spec.endswith('.fmf'): out.append((Path(spec).stem, 'fmf', str(Path(spec).expanduser().resolve())))
        elif kind == 'tactics': out += [(f.stem, 'fmf', str(f)) for f in sorted(Path(arg).expanduser().glob('*.fmf'))]
        elif kind == 'preset':
            p = presets(folder); name = next((n for n in p if n.lower() == arg.lower()), None)
            if not name: raise SystemExit(f'No installed preset {arg!r}; available: {", ".join(sorted(p))}')
            out.append((f'preset {name}', 'preset', name))
        elif spec == 'presets': out += [(f'preset {n}', 'preset', n) for n in sorted(presets(folder))]
        else: raise SystemExit(f'Unknown tactic {spec!r}')
    return out


def apply_tactic(s, side, source, folder):
    """Put a tactic on one side of a scenario and pick that side's XI by position."""
    import study6_tactics
    A = app(); name, kind, src = source
    if kind == 'fmf':
        s = A.import_fmf({'side': side, 'scenario': s, 'file_base64': base64.b64encode(Path(src).read_bytes()).decode()})['scenario']
    else:
        A.desktop_tactic_plan.apply(A, s['teams'][side], presets(folder)[src]); s['teams'][side]['tactic_name'] = name
    study6_tactics.pick_xi(s['teams'][side])
    s['teams'][side]['in_match'] = 'assistant'   # an AI-managed side would replace the tactic with its own at kick-off
    return s


def load(out): return json.loads((out / 'study.json').read_text(encoding='utf8'))
def save(out, s): (out / 'study.json').write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding='utf8')


def cmd_new(a):
    import exec_real
    found = exec_real.matches(a.team.replace(' ', '_'))
    if not found: raise SystemExit(f'No saved matches with {a.team} in {exec_real.SAVED}')
    found.sort(key=lambda m: Path(m[1]).stat().st_mtime, reverse=True)
    if a.newest: found = found[:a.newest]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    opponent = tactic_sources([a.opponent_tactic], out)[0] if a.opponent_tactic else None
    save(out, {'team': a.team, 'seeds': a.seeds, 'matches': [{'name': n, 'path': str(Path(p).resolve()), 'side': s} for n, p, s in found],
               'conditions': [], 'opponent_tactic': opponent})
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
    if kind == 'area':
        area, _, level = arg.partition('=')
        if area not in AREA_NAMES: raise SystemExit(f'Unknown area {area!r}; one of {", ".join(AREA_NAMES)}')
        k = AREA_NAMES.index(area)
        return [{'name': f'{area} {int(level)}', 'kind': 'familiarity', 'level': int(level), 'offsets': [1 + 3 * k + j for j in range(3)]}]
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
    if kind == 'tweak':
        t = tweak(arg)
        return [{'name': f'tweak {t["m_Name"]}', 'kind': 'tweak', 'tweak': t['m_Name']}]
    if kind == 'tweaks':
        return [{'name': f'tweak {t["m_Name"]}', 'kind': 'tweak', 'tweak': t['m_Name']} for t in tweaks()]
    raise SystemExit(f'Unknown condition {spec!r} (see --help)')


def cmd_add(a):
    out = Path(a.out); s = load(out); names = {c['name'] for c in s['conditions']}
    new = [c for spec in a.specs for c in expand(spec) if c['name'] not in names]
    s['conditions'] += new; save(out, s)
    print(f'{len(new)} conditions added, {len(s["conditions"])} in total')


def tweaks():
    """FM27's Tactical Tweaks that carry instructions (Swap Wings has none), from the game's own static data."""
    rows = sorted(app().CATALOG.get('raw_tactical_tweaks', []), key=lambda t: t['m_tweakID'])
    return [t for t in rows if t.get('m_teamInstructionAbsoluteOverrides') or t.get('m_teamInstructionShiftOverrides')
            or t.get('m_playerInstructionAbsoluteOverrides') or t.get('m_playerInstructionShiftOverrides') or t.get('m_mentalityOverride')]


def tweak(name):
    key = re.sub(r'[^a-z]', '', name.lower())
    t = next((t for t in tweaks() if t['m_Name'].lower() == key), None)
    if not t: raise SystemExit(f'Unknown or unsupported tweak {name!r}; available: {", ".join(x["m_Name"] for x in tweaks())}')
    return t


def apply_tweak(A, s, side, name):
    """Apply a Tactical Tweak to one side as the game defines it: team instructions set (absolute) or moved one option
    up or down (shift; the options run from lowest to highest), player instructions set for every player whose role
    allows them, and the mentality."""
    t = tweak(name); team = s['teams'][side]; changed = 0
    for o in t.get('m_teamInstructionAbsoluteOverrides', []):
        g = A.GROUPS.get(o['m_instruction'])
        if g and any(x['id'] == o['m_absoluteValue'] for x in g['options']):
            changed += team['instructions'].get(str(g['id'])) != o['m_absoluteValue']; team['instructions'][str(g['id'])] = o['m_absoluteValue']
    for o in t.get('m_teamInstructionShiftOverrides', []):
        g = A.GROUPS.get(o['m_instruction']);
        if not g: continue
        ids = [x['id'] for x in g['options']]; cur = team['instructions'].get(str(g['id']), ids[len(ids) // 2])
        i = min(len(ids) - 1, max(0, ids.index(cur) + (1 if o['m_direction'] == 0 else -1)))
        changed += ids[i] != cur; team['instructions'][str(g['id'])] = ids[i]
    if t.get('m_mentalityOverride'):
        changed += team['mentality'] != t['m_mentalityOverride']; team['mentality'] = t['m_mentalityOverride']
    base = A.base_of(s)
    for o in t.get('m_playerInstructionAbsoluteOverrides', []):
        g = A.PIS.get(o['m_instruction'])
        if not g: continue
        for phase in (0, 1):
            if g['phase'] != phase: continue
            for i, cell in enumerate(team['phases'][phase]):
                if i == 0 and cell['position'] == 'GK': continue
                value = o['m_absoluteValue']
                policy = A.cell_policy(side, phase, i, cell, base)
                if value and (value >= len(policy) or policy[value] != '0'): continue
                changed += cell['instructions'].get(str(g['id'])) != value; cell['instructions'][str(g['id'])] = value
    if not changed: raise ValueError(f'tweak {name} changes nothing here')
    return s


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
    elif c['kind'] == 'tweak':
        s = apply_tweak(A, s, side, c['tweak'])
    elif c['kind'] == 'tactic':
        s = A.import_fmf({'side': side, 'scenario': s, 'file_base64': base64.b64encode(Path(c['path']).read_bytes()).decode()})['scenario']
    return A.encode_scenario(A.validate_scenario(s))


def build_jobs(out, s):
    jobs, skipped = [], {}
    bins = out / 'bins'; bins.mkdir(exist_ok=True)
    opponent = s.get('opponent_tactic')
    for m in s['matches']:
        base, natural = None, ''
        if opponent:   # every replay, the natural one included, has the opponent on the chosen tactic
            base = app().validate_scenario(apply_tactic(app().validate_scenario(app().SAVED_MATCHES.open(m['path']).default), 1 - m['side'], opponent, out))
            natural = str(bins / f'natural_{len(jobs)}.bin'); Path(natural).write_bytes(app().encode_scenario(base))
        jobs.append(['S', f'{m["name"]}|natural', m['path'], natural, {}, s['seeds']])
        for c in s['conditions']:
            env, blob = {}, None
            if c['kind'] == 'attribute':
                env['FM27_MAC_ATTR'] = f'{m["side"]}:{c["id"]}{c["stored"]:+d}'
            elif c['kind'] == 'familiarity':
                env['FM27_MAC_EXEC_FIELDS'] = ','.join(f'{m["side"]}:{o}={c["level"]}' for o in c.get('offsets', AREAS))
            else:
                if base is None: base = app().validate_scenario(app().SAVED_MATCHES.open(m['path']).default)
                try: blob = edit_scenario(base, m['side'], c)
                except Exception as e: skipped.setdefault(c['name'], []).append(f'{m["name"]}: {str(e)[:120]}'); continue
            f = natural
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
             f'goals {mean("GF"):.2f}-{mean("GA"):.2f}, xG {mean("xGF"):.2f}-{mean("xGA"):.2f} ({len(base)} replays)' + (f', opponent on {s["opponent_tactic"][0]}' if s.get('opponent_tactic') else '') + '. Differences are paired by match and seed; t in brackets.', '']
    rows = []
    for c in s['conditions']:
        d = data.get(c['name'], {}); keys = [k for k in d if k in base]
        if keys: rows.append((c['name'], {m: stats([d[k][m] - base[k][m] for k in keys]) for m in MEASURES}, len(keys)))
    if rows:
        lines += ['## Each condition against the unchanged match', '', '| Condition | Points per game | xGD | Goals for | Goals against | xG for | xG against | n |', '|---|---|---|---|---|---|---|---|']
        for name, v, n in sorted(rows, key=lambda r: -abs(r[1]['xGD'][1])):
            lines.append(f"| {name} | {f(v['pts'])} | {f(v['xGD'])} | {f(v['GF'])} | {f(v['GA'])} | {v['xGF'][0]:+.3f} | {v['xGA'][0]:+.3f} | {n} |")
    pairs = {}
    for c in s['conditions']:
        if c['kind'] == 'attribute': pairs.setdefault(c['pair'], {})['+' if c['stored'] > 0 else '-'] = c
    slope = []
    for label, p in pairs.items():
        if set(p) != {'+', '-'}: continue
        lo, hi = data.get(p['-']['name'], {}), data.get(p['+']['name'], {}); keys = [k for k in lo if k in hi]
        if keys: slope.append((label, {m: stats([(hi[k][m] - lo[k][m]) / (2 * p['+']['step']) for k in keys]) for m in MEASURES}, len(keys)))
    if slope:
        lines += ['', '## Attributes: effect per in-game point (whole squad)', '', '| Attribute | Points per game | xGD | Goals for | Goals against | xG for | xG against | n |', '|---|---|---|---|---|---|---|---|']
        for name, v, n in sorted(slope, key=lambda r: -r[1]['xGD'][0]):
            lines.append(f"| {name} | {f(v['pts'])} | {f(v['xGD'])} | {f(v['GF'])} | {f(v['GA'])} | {v['xGF'][0]:+.3f} | {v['xGA'][0]:+.3f} | {n} |")
    if meta.get('skipped'): lines += ['', 'Skipped (the app rejected the change): ' + ', '.join(sorted(meta['skipped']))]
    lines += ['', 'With many conditions a few |t| of 2-3 appear by chance; rerun the interesting ones with more seeds before relying on them.']
    (out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf8'); print('\n'.join(lines))


def cmd_league(a):
    """Round robin of tactics on one saved match, through the shared league code (src/league.py, also behind the
    app's League page): each pair plays at home and away, on seeds 1..SEEDS (one "season" per seed)."""
    import exec_real, league
    out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    if a.match: path = str(Path(a.match).expanduser().resolve())
    else:
        found = sorted(exec_real.matches((a.team or '').replace(' ', '_')), key=lambda m: Path(m[1]).stat().st_mtime, reverse=True)
        if not found: raise SystemExit('Give --team (with saved matches) or --match')
        path = str(Path(found[0][1]).resolve())
    sources = tactic_sources(a.tactics, out)
    if len(sources) < 2: raise SystemExit('A league needs at least two tactics')
    if a.reference: squad = {'kind': 'reference', 'tier': a.reference}
    elif a.squad:
        save, _, club = a.squad.partition(':'); squad = {'kind': 'save', 'save': str(Path(save).expanduser()), 'club': club}
    else: squad = {'kind': 'natural'}   # each side keeps the saved match's own players (Study 7)
    teams = [{'name': name, 'tactic': {'kind': 'preset', 'style': src} if kind == 'preset' else {'kind': 'fmf', 'path': src},
              'squad': squad, 'familiarity': a.familiarity} for name, kind, src in sources]
    cfg = {'teams': teams, 'base_match': path, 'seasons': a.seeds, 'familiarity': a.familiarity, 'equal_start': a.equal_start,
           'home_and_away': True}
    total = league.build(app(), cfg, out, say=lambda s: None)
    print(f'{len(teams)} tactics, {total} matches (about {max(1, round(total / (1100 * a.workers) * 60))} min)', flush=True)
    league.run(out, a.workers)
    league_report(out)


def league_report(out):
    import league
    res = league.table(out); m = res['meta']; rows = res['table']
    lines = [f'# Tactic league on {m["base_match"]}', '', f'Every tactic plays every other at home and away, {m["seasons"]} season(s) '
             f'(one seed each); each side picks its XI by position and is managed by the assistant; '
             f'{"both sides start alike (condition, sharpness, morale, cohesion); " if m.get("equal_start") else ""}engine {m.get("engine")}.', '',
             '| # | Tactic | Squad | Familiarity | W | D | L | Goals for | Goals against | xG for | xG against | xPts | Points | ± (seasons) | Points per game |',
             '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        if not r.get('seasons'): continue
        spread = '' if r['Pts_sd'] is None else f"{r['Pts_sd']:.1f}"
        lines.append(f"| {r['rank']} | {r['team']} | {r['squad']} | {r['familiarity']} | {r['W']:.1f} | {r['D']:.1f} | {r['L']:.1f} | "
                     f"{r['GF']:.1f} | {r['GA']:.1f} | {r['xGF']:.2f} | {r['xGA']:.2f} | {r['xPts']:.1f} | {r['Pts']:.1f} | "
                     f"{spread} | **{r['PPG']:.2f}** |")
    order = res['order']
    lines += ['', '## Head to head: points per match of the row tactic against the column tactic', '',
              '| | ' + ' | '.join(str(k) for k in range(1, len(order) + 1)) + ' |', '|---|' + '---|' * len(order)]
    for k, a in enumerate(order, 1):
        cells = ['·' if a == b else ('' if res['head_to_head'][a][b] is None else f"{res['head_to_head'][a][b]:.1f}") for b in order]
        lines.append(f'| {k} {a} | ' + ' | '.join(cells) + ' |')
    if m.get('skipped'): lines += ['', 'Skipped fixtures: ' + '; '.join(m['skipped'])]
    (Path(out) / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf8'); print('\n'.join(lines))
    (Path(out) / 'table.csv').write_text(league.to_csv(res), encoding='utf8')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    n = sub.add_parser('new'); n.add_argument('out'); n.add_argument('--team', required=True)
    n.add_argument('--newest', type=int, help='only the N most recent matches'); n.add_argument('--seeds', type=int, default=30)
    n.add_argument('--opponent-tactic', help='play every replay against this tactic (see Tactic specs)')
    lg = sub.add_parser('league'); lg.add_argument('out'); lg.add_argument('--team', help='use this team\'s newest saved match')
    lg.add_argument('--match', help='a saved match file instead'); lg.add_argument('--tactics', nargs='+', required=True)
    lg.add_argument('--seeds', type=int, default=20); lg.add_argument('--familiarity', type=int, default=80)
    lg.add_argument('--workers', type=int, default=6)
    lg.add_argument('--squad', help='SAVE.fm:Club - put this club\'s players from an FM27 save on both sides (needs fmsave)')
    lg.add_argument('--reference', help='a synthetic reference squad on both sides: pl-top, pl-middle or pl-bottom (src/reference_squads.json)')
    lg.add_argument('--equal-start', action='store_true', help='both sides start alike (condition, sharpness, morale, cohesion), as the League page does')
    d = sub.add_parser('add'); d.add_argument('out'); d.add_argument('specs', nargs='+')
    r = sub.add_parser('run'); r.add_argument('out'); r.add_argument('--workers', type=int, default=6)
    t = sub.add_parser('report'); t.add_argument('out')
    a = p.parse_args()
    {'new': cmd_new, 'add': cmd_add, 'run': cmd_run, 'report': cmd_report, 'league': cmd_league}[a.cmd](a)


if __name__ == '__main__':
    main()
