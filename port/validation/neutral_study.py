"""Neutral-ground studies from a specification (the research roadmap's Studies 9b-21, see roadmap_studies.py).

Every study is a set of groups (a tested style, squad tiers, opponents, templates); every group has the unchanged
side ('none') and conditions, each a change to the scenario. Every condition replays the same template, opponent,
venue and seed as 'none', so differences are paired. Fixtures alternate between the group's templates by seed.

  python port/validation/neutral_study.py build NAME OUT          # NAME: a key of roadmap_studies.STUDIES
  python port/validation/neutral_study.py pilot OUT [--workers 7]  # the first seeds only, then the checks
  python port/validation/neutral_study.py run OUT [--workers 7]    # everything (resumable)
  python port/validation/neutral_study.py report OUT               # OUT/report.md

The checks (written to OUT/checks.md, exit code 1 if any fails): every condition's intended changes (the scenario
before validation, against 'none') survive the app's validator unchanged and nothing else changes on the edited
side's players; its encoded scenario differs from 'none'; and in the pilot every job produced a result.
"""
import argparse, copy, hashlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ('scripts', 'src', 'port/validation'): sys.path.insert(0, str(ROOT / p))

DEFAULT_TEMPLATES = ['Leeds_United_v_Tottenham_Hotspur_2535055280_VER_fm.pkm', 'Everton_v_West_Ham_United_2316362433_VER_fm.pkm']
PANEL = ['Gegenpress', 'Control Possession', 'Park the Bus', 'Route One']

# slot codes in a tactic's phases -> the player's position-rating index (catalogue attribute ids 0-14)
RATING = {'GK': 0, 'DL': 2, 'DC': 3, 'DR': 4, 'DM': 5, 'ML': 6, 'MC': 7, 'MR': 8, 'AML': 9, 'AMC': 10, 'AMR': 11,
          'ST': 12, 'WBL': 13, 'WBR': 14}


def rating_index(code):
    if code in RATING: return RATING[code]
    for k in ('AMC', 'DM', 'MC', 'DC', 'ST'):
        if code.startswith(k): return RATING[k]
    raise KeyError(code)


def position_group(code):
    i = rating_index(code)
    return {0: 'GK', 3: 'CB', 2: 'FB', 4: 'FB', 13: 'FB', 14: 'FB', 5: 'DM/CM', 7: 'DM/CM', 6: 'AM/W', 8: 'AM/W',
            9: 'AM/W', 10: 'AM/W', 11: 'AM/W', 12: 'ST'}[i]


def starters(team):
    """[(player index, in-possession slot code, out-of-possession slot code)] for the starting XI."""
    ph = team['phases']
    return [(i, ph[0][k]['position'], ph[-1][k]['position']) for k, i in enumerate(team['lineup'])]


def attribute_ids():
    import study
    return {name: aid for name, (aid, _) in study.attribute_ids().items()}


def ids(names):
    a = attribute_ids()
    return [a[n.lower().replace(' ', '')] for n in names]


def template_path(name):
    import match_backup
    for folder in (match_backup.backup_folder() / 'Other_clubs', match_backup.backup_folder()):
        hit = sorted(folder.rglob(name))
        if hit: return str(hit[0].resolve())
    raise SystemExit(f'Template {name} not found in the match backup')


def set_instructions(A, team, choices):
    by_name = {g['name']: g for g in A.GROUPS.values()}
    for gname, label in choices.items():
        g = by_name[gname]
        team['instructions'][str(g['id'])] = next(o['id'] for o in g['options'] if o['label'] == label)


def player_diff(a, b):
    """Changed (player, field) -> (before, after) for one team's players."""
    out = {}
    for i, (p, q) in enumerate(zip(a['players'], b['players'])):
        for j, (x, y) in enumerate(zip(p['attributes'], q['attributes'])):
            if x != y: out[(i, f'attr{j}')] = (x, y)
        for k in set(p['native_profile']) | set(q['native_profile']):
            if p['native_profile'].get(k) != q['native_profile'].get(k): out[(i, k)] = (p['native_profile'].get(k), q['native_profile'].get(k))
    return out


def team_diff(a, b):
    out = {(None, k): (a[k], b[k]) for k in ('mentality', 'instructions', 'lineup', 'phases') if a.get(k) != b.get(k)}
    out.update(player_diff(a, b)); return out


def build(a):
    import study, league, roadmap_studies
    spec = roadmap_studies.STUDIES[a.name]()
    A = study.app(); out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True); (out / 'bins').mkdir(exist_ok=True)
    b = league.Builder(A, out); fam = spec.get('familiarity', 80)
    env = {'FM27_MAC_EXEC_FIELDS': ','.join(f'{x}:{o}={fam}' for x in (0, 1) for o in league.AREAS) + ',' +
           ','.join(f'{x}:{o}=50' for x in (0, 1) for o in (0x19, 0x1a))}
    jobs, checks, n, bases, meta_groups = [], [], 0, {}, []
    for g in spec['groups']:
        templates = [template_path(t) for t in g.get('templates', DEFAULT_TEMPLATES)]
        panel = g.get('panel', PANEL); venues = g.get('venues', (0, 1)); seeds = g.get('seeds', spec['seeds'])
        conds = [('none', None)] + list(g['conds'])
        meta_groups.append({'name': g['name'], 'conds': [c for c, _ in conds], 'panel': panel, 'venues': list(venues), 'seeds': seeds,
                            'templates': [Path(t).name for t in templates], 'style': g.get('style'), 'tier': g.get('tier', 'pl-middle'),
                            'opp_tier': g.get('opp_tier', g.get('tier', 'pl-middle'))})
        for k, path in enumerate(templates):
            if path not in bases: bases[path] = league.same_squad_size(A.validate_scenario(A.SAVED_MATCHES.open(path).default))
            for opp in panel:
                for venue in venues:
                    s0 = b.side(copy.deepcopy(bases[path]), venue, {'squad': {'kind': 'reference', 'tier': g.get('tier', 'pl-middle')},
                                                                     'tactic': {'kind': 'preset', 'style': g['style']}})
                    if g.get('instructions'): set_instructions(A, s0['teams'][venue], g['instructions'])
                    s0 = b.side(s0, 1 - venue, {'squad': {'kind': 'reference', 'tier': g.get('opp_tier', g.get('tier', 'pl-middle'))},
                                                'tactic': {'kind': 'preset', 'style': opp}})
                    league.equalise(s0)
                    if g.get('setup'): g['setup'](A, s0, venue)
                    s0 = A.validate_scenario(s0); base_blob = A.encode_scenario(s0)
                    for cname, edit in conds:
                        if edit is None: s, blob = s0, base_blob
                        else:
                            s = copy.deepcopy(s0); edit(A, s, venue)
                            intended = {(side,) + key: v for side in (0, 1) for key, v in team_diff(s0['teams'][side], s['teams'][side]).items()}
                            v = A.validate_scenario(copy.deepcopy(s))
                            kept = {(side,) + key: val for side in (0, 1) for key, val in team_diff(s0['teams'][side], v['teams'][side]).items()}
                            blob = A.encode_scenario(v)
                            problems = []
                            if not intended: problems.append('the edit changes nothing')
                            if kept != intended:
                                lost = [k for k in intended if intended[k] != kept.get(k)]; extra = [k for k in kept if k not in intended]
                                problems.append(f'validator changed {len(lost)} intended fields (e.g. {lost[:3]}) and {len(extra)} others (e.g. {extra[:3]})')
                            if blob == base_blob: problems.append('the encoded scenario equals the unchanged one')
                            if k == 0 and opp == panel[0] and venue == venues[0]:
                                sample = list(intended.items())[:4]
                                checks.append({'group': g['name'], 'cond': cname, 'changes': len(intended), 'sample': [[list(map(str, x)), list(map(str, y))] for x, y in sample], 'problems': problems})
                            elif problems:
                                checks.append({'group': g['name'], 'cond': cname, 'opp': opp, 'venue': venue, 'template': k, 'problems': problems})
                        f = out / 'bins' / f'{hashlib.sha1(blob).hexdigest()[:16]}.bin'
                        if not f.exists(): f.write_bytes(blob)
                        n += 1
                        cond = f"{g['name']}|{cname}|{opp}|{venue}|{k}"
                        jobs += [['N', cond, path, str(f), env, 1, s_] for s_ in range(1, seeds + 1) if (s_ - 1) % len(templates) == k]
        print('built', g['name'], flush=True)
    jobs.sort(key=lambda j: j[6])
    (out / 'jobs_all.json').write_text(json.dumps(jobs)); (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'build_checks.json').write_text(json.dumps(checks, indent=1))
    (out / 'meta.json').write_text(json.dumps({'name': a.name, 'title': spec['title'], 'seeds': spec['seeds'], 'pilot_seeds': spec.get('pilot_seeds'),
                                               'familiarity': fam, 'groups': meta_groups, 'notes': spec.get('notes', '')}, indent=1))
    bad = [c for c in checks if c['problems']]
    print(len(jobs), 'matches;', n, 'scenarios;', len(bad), 'with problems')
    for c in bad[:20]: print('  PROBLEM', c)


def pilot(a):
    import overnight
    out = Path(a.out).resolve(); meta = json.loads((out / 'meta.json').read_text())
    jobs = json.loads((out / 'jobs_all.json').read_text())
    p = meta.get('pilot_seeds') or max(2, math.ceil(meta['seeds'] * 0.05))
    pj = [j for j in jobs if j[6] <= p]
    (out / 'jobs.json').write_text(json.dumps(pj))
    overnight.run(out, a.workers)
    (out / 'jobs.json').write_text(json.dumps(jobs))
    done = {(r['cond'], r['seed']) for r in map(json.loads, open(out / 'results.jsonl'))} if (out / 'results.jsonl').exists() else set()
    missing = [j for j in pj if (j[1], j[6]) not in done]
    checks = json.loads((out / 'build_checks.json').read_text())
    bad = [c for c in checks if c['problems']]
    lines = [f"# Pilot checks: {meta['title']}", '', f'Pilot: seeds 1-{p}, {len(pj)} matches, {len(pj) - len(missing)} with a result.', '']
    lines += ['## Scenario checks', '', f'{len(checks)} checked scenarios, {len(bad)} with problems.', '']
    for c in checks:
        if 'sample' in c: lines.append(f"- {c['group']} / {c['cond']}: {c['changes']} fields changed; e.g. {c['sample'][:2]}" + (f" **PROBLEMS: {c['problems']}**" if c['problems'] else ''))
    for c in bad:
        if 'sample' not in c: lines.append(f"- PROBLEM {c}")
    lines += ['', '## Pilot effects (sanity only, few seeds)', '']
    lines += summary_lines(out, meta)
    ok = not bad and not missing
    lines += ['', 'RESULT: ' + ('PASS' if ok else f'FAIL ({len(bad)} scenario problems, {len(missing)} missing results)')]
    (out / 'checks.md').write_text('\n'.join(lines) + '\n'); print('\n'.join(lines))
    sys.exit(0 if ok else 1)


def run(a):
    import overnight
    out = Path(a.out).resolve()
    (out / 'jobs.json').write_text((out / 'jobs_all.json').read_text())
    overnight.run(out, a.workers)


def load(out):
    """{(group, cond): {(opp, venue, template, seed): measures of the tested side}}"""
    import league
    data = {}
    for line in open(Path(out) / 'results.jsonl'):
        r = json.loads(line); g, c, opp, venue, k = r['cond'].split('|'); me = int(venue); o = 1 - me
        gf, ga = r['score'][me], r['score'][o]
        sh = r.get('shots') or [0, 0]; sot = r.get('shots_on_target') or [0, 0]
        passes = (r.get('passes') or [0, 0])[me]; comp = (r.get('completed_passes') or [0, 0])[me]
        poss = (r.get('possession') or [None, None])[me]
        data.setdefault((g, c), {})[(opp, venue, k, r['seed'])] = {
            'pts': 3 if gf > ga else 1 if gf == ga else 0, 'xPts': league.xpts(r['xg'][me], r['xg'][o]), 'xGD': r['xg'][me] - r['xg'][o],
            'xGF': r['xg'][me], 'xGA': r['xg'][o], 'GF': gf, 'GA': ga, 'shots': sh[me], 'shots_against': sh[o], 'sot': sot[me],
            'sot_against': sot[o], 'saves': sot[o] - ga, 'poss': None if poss is None else 100 * poss if poss <= 1 else poss,
            'passes': passes, 'completion': 100 * comp / passes if passes else None,
            'home_xg': r['xg'][0], 'away_xg': r['xg'][1], 'home_goals': r['score'][0], 'away_goals': r['score'][1]}
    return data


def stat(v):
    v = [x for x in v if x is not None]
    if len(v) < 3: return float('nan'), float('nan'), float('nan'), len(v)
    m = sum(v) / len(v); sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)); se = sd / math.sqrt(len(v))
    return m, (m / se if se else 0.0), se, len(v)


def effect(data, g, c, measure, base='none'):
    d, b = data.get((g, c), {}), data.get((g, base), {})
    keys = [k for k in d if k in b]
    return stat([None if d[k][measure] is None or b[k][measure] is None else d[k][measure] - b[k][measure] for k in keys])


def summary_lines(out, meta):
    if not (Path(out) / 'results.jsonl').exists(): return ['(no results)']
    data = load(out); f = lambda e: f'{e[0]:+.2f} ({e[1]:+.1f})' if e[3] >= 3 else '·'
    lines = []
    for g in meta['groups']:
        base = list(data.get((g['name'], 'none'), {}).values())
        if base:
            avg = lambda m: (lambda v: sum(v) / len(v) if v else float('nan'))([r[m] for r in base if r[m] is not None])
            lines += [f"### {g['name']}", '', f"Unchanged: {len(base)} matches; points per game {avg('pts'):.2f}, xG {avg('xGF'):.2f} for and {avg('xGA'):.2f} against, "
                      f"shots {avg('shots'):.1f} for and {avg('shots_against'):.1f} against, possession {avg('poss'):.0f}%, passes {avg('passes'):.0f} ({avg('completion'):.1f}% completed).", '']
        lines += ['| Condition | xPts | xG difference | Points | xG for | xG against | Goals for | Goals against | Shots | Shots against | Possession | Pass completion | Pairs |',
                  '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for c in g['conds']:
            if c == 'none': continue
            e = {m: effect(data, g['name'], c, m) for m in ('xPts', 'xGD', 'pts', 'xGF', 'xGA', 'GF', 'GA', 'shots', 'shots_against', 'poss', 'completion')}
            lines.append(f"| {c} | {f(e['xPts'])} | {f(e['xGD'])} | {f(e['pts'])} | {e['xGF'][0]:+.2f} | {e['xGA'][0]:+.2f} | {e['GF'][0]:+.2f} | {e['GA'][0]:+.2f} | "
                         f"{e['shots'][0]:+.2f} | {e['shots_against'][0]:+.2f} | {e['poss'][0]:+.2f} | {e['completion'][0]:+.2f} | {e['xPts'][3]} |")
        lines.append('')
    return lines


def report(a):
    out = Path(a.out); meta = json.loads((out / 'meta.json').read_text())
    lines = [f"# {meta['title']}", '', 'Neutral ground: synthetic reference squads, both sides starting alike, tactical familiarity held at '
             f"{meta['familiarity']}, the assistant managing both sides. Each condition is paired with the unchanged side on the same template, opponent, venue "
             'and seed. Per game; t in brackets (|t| ≥ 4 established, 3-4 likely).', '']
    for g in meta['groups']:
        lines.append(f"Group **{g['name']}**: {g['style']}, squads {g['tier']} v {g['opp_tier']}, opponents {', '.join(g['panel'])}, venues {g['venues']}, "
                     f"seeds 1-{g['seeds']}, templates {', '.join(g['templates'])}.")
    if meta.get('notes'): lines += ['', meta['notes']]
    lines += [''] + summary_lines(out, meta)
    (out / 'report.md').write_text('\n'.join(lines) + '\n'); print('\n'.join(lines))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('build'); s.add_argument('name'); s.add_argument('out')
    for c in ('pilot', 'run'):
        s = sub.add_parser(c); s.add_argument('out'); s.add_argument('--workers', type=int, default=7)
    s = sub.add_parser('report'); s.add_argument('out')
    a = p.parse_args()
    {'build': build, 'pilot': pilot, 'run': run, 'report': report}[a.cmd](a)
