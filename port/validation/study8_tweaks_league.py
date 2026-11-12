"""Study 8 on neutral ground: FM27's in-match Tactical Tweaks applied to many base tactics, with synthetic squads.

Every one of the 10 installed presets is the base tactic in turn; each Tactical Tweak (as the game defines it) is
applied to it from kick-off, and the team plays a panel of opponent presets at home and away. Each tweaked team is
compared with the same preset without the tweak, on the same seeds (paired). Both sides have the same synthetic
reference squad (src/reference_squads.json, Premier League middle eight), start alike, and have their tactical
familiarity held at the same level; fixtures alternate between template matches of other clubs (by seed), so no
user's team or tactic is involved.

  python port/validation/study8_tweaks_league.py build OUT TEMPLATE.pkm [TEMPLATE.pkm ...] [--seeds 6]
  python port/validation/study8_tweaks_league.py run OUT [--workers 6]
  python port/validation/study8_tweaks_league.py report OUT          # writes OUT/report.md
"""
import argparse, copy, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts')); sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'port/validation'))
PANEL = ['Gegenpress', 'Control Possession', 'Park the Bus', 'Route One']   # opponents of different styles
FAMILIARITY = 80


def build(a):
    import study, league
    A = study.app(); out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True); (out / 'bins').mkdir(exist_ok=True)
    templates = [str(Path(t).expanduser().resolve()) for t in a.templates]
    bases = [league.same_squad_size(A.validate_scenario(A.SAVED_MATCHES.open(t).default)) for t in templates]
    presets = sorted(study.presets(out)); tweaks = [t['m_Name'] for t in study.tweaks()]
    squad = {'kind': 'reference', 'tier': 'pl-middle'}; b = league.Builder(A, out)
    env = {'FM27_MAC_EXEC_FIELDS': ','.join(f'{x}:{o}={FAMILIARITY}' for x in (0, 1) for o in league.AREAS) + ',' +
           ','.join(f'{x}:{o}=50' for x in (0, 1) for o in (0x19, 0x1a))}
    jobs, skipped, n = [], {}, 0
    for base_tactic in presets:
        for tweak in [None] + tweaks:
            for opp in PANEL:
                if opp == base_tactic: continue
                for venue in (0, 1):
                    for k, (base, path) in enumerate(zip(bases, templates)):
                        try:
                            s = b.side(copy.deepcopy(base), venue, {'squad': squad, 'tactic': {'kind': 'preset', 'style': base_tactic}})
                            if tweak: s = study.apply_tweak(A, s, venue, tweak)
                            s = b.side(s, 1 - venue, {'squad': squad, 'tactic': {'kind': 'preset', 'style': opp}})
                            league.equalise(s); blob = A.encode_scenario(A.validate_scenario(s))
                        except Exception as e:
                            skipped.setdefault(f'{base_tactic} + {tweak}', str(e)[:120]); continue
                        f = out / 'bins' / f'{n}.bin'; f.write_bytes(blob); n += 1
                        cond = f'T|{base_tactic}|{tweak or "none"}|{opp}|{venue}'
                        jobs += [['T', cond, path, str(f), env, 1, s] for s in range(1, a.seeds + 1) if (s - 1) % len(templates) == k]
        print('built', base_tactic, flush=True)
    jobs.sort(key=lambda j: j[6])
    (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps({'presets': presets, 'tweaks': tweaks, 'panel': PANEL, 'seeds': a.seeds, 'familiarity': FAMILIARITY,
                                               'templates': [Path(t).name for t in templates], 'skipped': skipped}, indent=1))
    print(len(jobs), 'matches;', len(skipped), 'tweak/base combinations skipped (the tweak changes nothing there)')


def run(a):
    import overnight
    overnight.run(Path(a.out).resolve(), a.workers)


def stat(v):
    if len(v) < 3: return float('nan'), float('nan')
    m = sum(v) / len(v); sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))
    return m, (m / (sd / math.sqrt(len(v))) if sd else 0.0)


def report(a):
    import league
    out = Path(a.out); meta = json.loads((out / 'meta.json').read_text()); data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); _, base, tweak, opp, venue = r['cond'].split('|'); me = int(venue); o = 1 - me
        g, c = r['score'][me], r['score'][o]
        data.setdefault(tweak, {})[(base, opp, venue, r['seed'])] = {
            'pts': 3 if g > c else 1 if g == c else 0, 'xPts': league.xpts(r['xg'][me], r['xg'][o]), 'xGD': r['xg'][me] - r['xg'][o],
            'GF': g, 'GA': c}
    none = data.get('none', {})
    rows = []
    for tweak in meta['tweaks']:
        d = data.get(tweak, {}); keys = [k for k in d if k in none]
        if not keys: continue
        eff = {m: stat([d[k][m] - none[k][m] for k in keys]) for m in ('pts', 'xPts', 'xGD', 'GF', 'GA')}
        by_base = {}
        for base in meta['presets']:
            kb = [k for k in keys if k[0] == base]
            if kb: by_base[base] = sum(d[k]['xGD'] - none[k]['xGD'] for k in kb) / len(kb)
        rows.append((tweak, eff, len(keys), by_base))
    rows.sort(key=lambda r: -r[1]['xGD'][0])
    f = lambda x: f'{x[0]:+.2f} ({x[1]:+.1f})'
    lines = ['# Tactical Tweaks on neutral ground', '', f"Base tactics: the {len(meta['presets'])} presets; opponents: {', '.join(meta['panel'])}; "
             f"synthetic Premier League middle-eight squads on both sides; familiarity {meta['familiarity']}; seeds 1-{meta['seeds']}; templates "
             f"{', '.join(meta['templates'])}. Differences: tweak minus the same preset without it, paired; t in brackets.", '',
             '| Tweak | Points | xPts | xG difference | Goals for | Goals against | Pairs |', '|---|---|---|---|---|---|---|']
    for tweak, e, n, _ in rows:
        lines.append(f"| {tweak} | {f(e['pts'])} | {f(e['xPts'])} | {f(e['xGD'])} | {e['GF'][0]:+.2f} | {e['GA'][0]:+.2f} | {n} |")
    bases = meta['presets']
    lines += ['', '## xG difference by base tactic', '', '| Tweak | ' + ' | '.join(bases) + ' |', '|---|' + '---|' * len(bases)]
    for tweak, _, _, by in rows:
        lines.append(f'| {tweak} | ' + ' | '.join(f'{by[b]:+.2f}' if b in by else '' for b in bases) + ' |')
    if meta.get('skipped'): lines += ['', 'Skipped (the tweak changes nothing on that preset): ' + '; '.join(sorted(meta['skipped']))]
    (out / 'report.md').write_text('\n'.join(lines) + '\n'); print('\n'.join(lines))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('build'); s.add_argument('out'); s.add_argument('templates', nargs='+'); s.add_argument('--seeds', type=int, default=6)
    s = sub.add_parser('run'); s.add_argument('out'); s.add_argument('--workers', type=int, default=6)
    s = sub.add_parser('report'); s.add_argument('out')
    a = p.parse_args()
    {'build': build, 'run': run, 'report': report}[a.cmd](a)
