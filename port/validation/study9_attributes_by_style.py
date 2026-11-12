"""Study 9: are attribute values tied to the tactic? Physical and passing attributes under five playing styles.

The question (from a reader): attribute tests usually run "meta" tactics (high press, high tempo, counter-attack), so
physical attributes dominate because they suit the tactic. Would passing attributes matter more under a possession
system?

Design (neutral ground, as Study 7): both sides have the same synthetic reference squad (Premier League middle
eight), start alike and have tactical familiarity held at 80. The tested side plays one of five styles; its whole
squad gets +5 in-game points in one attribute group, and every result is paired with the same match and seed without
the change. Opponents: a panel of four presets of different styles, home and away; fixtures alternate between two
template matches of other clubs (by seed).

  python port/validation/study9_attributes_by_style.py build OUT TEMPLATE.pkm [TEMPLATE.pkm ...] [--seeds 50]
  python port/validation/study9_attributes_by_style.py run OUT [--workers 6]
  python port/validation/study9_attributes_by_style.py report OUT          # writes OUT/report.md
"""
import argparse, copy, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts')); sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'port/validation'))
STYLES = ['Gegenpress', 'Tiki-Taka', 'Control Possession', 'Direct Counter-Attack', 'Neutral']
NEUTRAL_SHAPE = 'Gegenpress'   # the neutral style: this preset's shape and roles, every team instruction on its standard option
GROUPS = {'physical': ['Pace', 'Acceleration', 'Stamina', 'Work Rate', 'Aggression'],
          'passing': ['Passing', 'Technique', 'Vision', 'Decisions', 'First Touch', 'Composure']}
PANEL = ['Gegenpress', 'Control Possession', 'Park the Bus', 'Route One']
FAMILIARITY, STEP = 80, 5


def neutral(A, team):
    """Every team instruction on its standard option (Standard / Balanced / Mixed, else the middle one); mentality Balanced."""
    for g in A.GROUPS.values():
        opts = g['options']
        pick = next((o for o in opts if o['label'].lower() in ('standard', 'balanced', 'mixed')), None)
        if pick is None:   # on/off choices and time wasting: the plain option (no, stay back, keep ball in play, never)
            pick = opts[0] if len(opts) == 2 or g.get('name') == 'TimeWasting' else opts[len(opts) // 2]
        team['instructions'][str(g['id'])] = pick['id']
    team['mentality'] = next(m['id'] for m in A.CATALOG['mentalities'] if m['label'] == 'Balanced')


def boost(team, ids):
    for p in team['players']:
        for a in ids: p['attributes'][a] = min(100, p['attributes'][a] + STEP * 5)


def build(a):
    import study, league
    A = study.app(); out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True); (out / 'bins').mkdir(exist_ok=True)
    templates = [str(Path(t).expanduser().resolve()) for t in a.templates]
    bases = [league.same_squad_size(A.validate_scenario(A.SAVED_MATCHES.open(t).default)) for t in templates]
    ids = study.attribute_ids(); groups = {g: [ids[n.lower().replace(' ', '')][0] for n in names] for g, names in GROUPS.items()}
    squad = {'kind': 'reference', 'tier': 'pl-middle'}; b = league.Builder(A, out)
    env = {'FM27_MAC_EXEC_FIELDS': ','.join(f'{x}:{o}={FAMILIARITY}' for x in (0, 1) for o in league.AREAS) + ',' +
           ','.join(f'{x}:{o}=50' for x in (0, 1) for o in (0x19, 0x1a))}
    jobs, n = [], 0
    for style in STYLES:
        for group in [None] + list(GROUPS):
            for opp in PANEL:
                for venue in (0, 1):
                    for k, (base, path) in enumerate(zip(bases, templates)):
                        s = b.side(copy.deepcopy(base), venue, {'squad': squad, 'tactic': {'kind': 'preset', 'style': NEUTRAL_SHAPE if style == 'Neutral' else style}})
                        if style == 'Neutral': neutral(A, s['teams'][venue])
                        if group: boost(s['teams'][venue], groups[group])
                        s = b.side(s, 1 - venue, {'squad': squad, 'tactic': {'kind': 'preset', 'style': opp}})
                        league.equalise(s); blob = A.encode_scenario(A.validate_scenario(s))
                        f = out / 'bins' / f'{n}.bin'; f.write_bytes(blob); n += 1
                        cond = f'A|{style}|{group or "none"}|{opp}|{venue}'
                        jobs += [['A', cond, path, str(f), env, 1, s_] for s_ in range(1, a.seeds + 1) if (s_ - 1) % len(templates) == k]
        print('built', style, flush=True)
    jobs.sort(key=lambda j: j[6])
    (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps({'styles': STYLES, 'groups': GROUPS, 'panel': PANEL, 'seeds': a.seeds, 'step': STEP,
                                               'familiarity': FAMILIARITY, 'templates': [Path(t).name for t in templates]}, indent=1))
    print(len(jobs), 'matches')


def run(a):
    import overnight
    overnight.run(Path(a.out).resolve(), a.workers)


def stat(v):
    if len(v) < 3: return float('nan'), float('nan'), float('nan')
    m = sum(v) / len(v); sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)); se = sd / math.sqrt(len(v))
    return m, (m / se if se else 0.0), se


def report(a):
    import league
    out = Path(a.out); meta = json.loads((out / 'meta.json').read_text()); data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); _, style, group, opp, venue = r['cond'].split('|'); me = int(venue); o = 1 - me
        g, c = r['score'][me], r['score'][o]
        data.setdefault((style, group), {})[(opp, venue, r['seed'])] = {
            'pts': 3 if g > c else 1 if g == c else 0, 'xPts': league.xpts(r['xg'][me], r['xg'][o]), 'xGD': r['xg'][me] - r['xg'][o],
            'xGF': r['xg'][me], 'xGA': r['xg'][o], 'GF': g, 'GA': c, 'poss': r.get('possession', [None, None])[me],
            'passes': r.get('passes', [None, None])[me]}
    f = lambda x: f'{x[0]:+.2f} ({x[1]:+.1f})'
    lines = ['# Attributes by playing style', '', f"Synthetic Premier League middle-eight squads on both sides; the tested side's whole squad +{meta['step']} "
             f"in one group; opponents {', '.join(meta['panel'])}, home and away; seeds 1-{meta['seeds']}; familiarity {meta['familiarity']}; "
             f"templates {', '.join(meta['templates'])}. Differences are paired by match and seed; t in brackets.", '',
             '## The styles, unchanged', '', '| Style | Points per game | xG for | xG against | Possession | Passes |', '|---|---|---|---|---|---|']
    avg = lambda rows, m: sum(r[m] for r in rows if r[m] is not None) / max(1, sum(r[m] is not None for r in rows))
    for style in meta['styles']:
        rows = list(data.get((style, 'none'), {}).values())
        if rows: lines.append(f"| {style} | {avg(rows, 'pts'):.2f} | {avg(rows, 'xGF'):.2f} | {avg(rows, 'xGA'):.2f} | {100 * avg(rows, 'poss') if avg(rows, 'poss') <= 1 else avg(rows, 'poss'):.0f}% | {avg(rows, 'passes'):.0f} |")
    effects = {}
    lines += ['', f"## Effect of +{meta['step']} in each group", '', '| Style | Group | Points | xPts | xG difference | xG for | xG against | Goals for | Goals against | Pairs |', '|---|---|---|---|---|---|---|---|---|---|']
    for style in meta['styles']:
        base = data.get((style, 'none'), {})
        for group in meta['groups']:
            d = data.get((style, group), {}); keys = [k for k in d if k in base]
            if not keys: continue
            e = {m: stat([d[k][m] - base[k][m] for k in keys]) for m in ('pts', 'xPts', 'xGD', 'xGF', 'xGA', 'GF', 'GA')}; effects[(style, group)] = e
            lines.append(f"| {style} | {group} | {f(e['pts'])} | {f(e['xPts'])} | {f(e['xGD'])} | {e['xGF'][0]:+.2f} | {e['xGA'][0]:+.2f} | {e['GF'][0]:+.2f} | {e['GA'][0]:+.2f} | {len(keys)} |")
    lines += ['', '## Does the style change what a group is worth?', '', 'Each group\'s xG-difference effect under a style minus its effect under Gegenpress (t from both standard errors):', '',
              '| Group | ' + ' | '.join(s for s in meta['styles'] if s != 'Gegenpress') + ' |', '|---|' + '---|' * (len(meta['styles']) - 1)]
    for group in meta['groups']:
        ref = effects.get(('Gegenpress', group))
        cells = []
        for style in meta['styles']:
            if style == 'Gegenpress': continue
            e = effects.get((style, group))
            if not (e and ref): cells.append(''); continue
            dm = e['xGD'][0] - ref['xGD'][0]; se = math.sqrt(e['xGD'][2] ** 2 + ref['xGD'][2] ** 2)
            cells.append(f'{dm:+.2f} ({dm / se:+.1f})')
        lines.append(f'| {group} | ' + ' | '.join(cells) + ' |')
    (out / 'report.md').write_text('\n'.join(lines) + '\n'); print('\n'.join(lines))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('build'); s.add_argument('out'); s.add_argument('templates', nargs='+'); s.add_argument('--seeds', type=int, default=50)
    s = sub.add_parser('run'); s.add_argument('out'); s.add_argument('--workers', type=int, default=6)
    s = sub.add_parser('report'); s.add_argument('out')
    a = p.parse_args()
    {'build': build, 'run': run, 'report': report}[a.cmd](a)
