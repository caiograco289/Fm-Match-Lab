"""A quick number per tactic: one club's league season from an FM27 save, played on FM27's engine with each tactic.

  .venv/bin/python scripts/season.py OUT --save SAVE.fm --club "Club" --tactic preset:Gegenpress --tactic my.fmf
      [--seeds 10] [--familiarity 80] [--opponents ai|STYLE] [--opponent-management ai|assistant] [--workers 6]
  .venv/bin/python scripts/season.py OUT --report

The club plays its real league fixtures (from the save's current season) against every opponent's real squad, once
per seed and tactic; the first tactic is the baseline the others are compared with, on the same fixtures and seeds.
Opponents use a tactic the game's AI picked in a real match (that club's own where an imported match has it, else
the closest situation) and are managed by the AI during the match; with --opponents STYLE they all use that preset.
See src/club_season.py for what is and is not modelled. Needs fmsave, and imported matches between other clubs
(scripts/import_other_matches.py) for the opponents' tactics and the grounds.

Tactic specs: FILE.fmf or preset:STYLE (the installed FM27 presets). About 38 matches per seed and tactic in a
20-club league; 6 workers play about 6,000 matches an hour.
"""
import argparse, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'port/validation')); sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('FM27_ENGINE_ROOT', str(ROOT / 'private/engine'))


def tactic(spec):
    if spec.startswith('preset:'): return {'name': spec[7:], 'kind': 'preset', 'style': spec[7:]}
    p = Path(spec).expanduser().resolve()
    if p.suffix.lower() != '.fmf' or not p.is_file(): raise SystemExit(f'Not a tactic file or preset: {spec}')
    return {'name': p.stem, 'kind': 'fmf', 'path': str(p)}


def report(out):
    import club_season as season
    res = season.results(out); m = res['meta']; g = res['games']
    lines = [f"# {m['club']}: a season with each tactic", '',
             f"{m['clubs']}-club league ({g} matches a season), {m['club']} {m['rank_by_strength']} of {m['clubs']} by the strength of its XI; "
             f"{m['seeds']} seasons per tactic; tactical familiarity {m['familiarity']} for every side; grounds: "
             + '; '.join(m['templates']) + ('' if m['templates_from_league'] else ' (not from this league)') + '.', '',
             '| Tactic | Points | W-D-L | Goals | xG | xPts | Points v first (t) | xPts v first (t) | Goal difference v first |',
             '|---|---|---|---|---|---|---|---|---|']
    for r in res['table']:
        if not r.get('matches'): lines.append(f"| {r['tactic']} | not played yet | | | | | | | |"); continue
        cmp = lambda f: (f"{r[f'd{f}']:+.1f} ({r[f'd{f}_t']:+.1f})" if r.get(f'd{f}_t') is not None else '') if f'd{f}' in r else 'baseline'
        lines.append(f"| {r['tactic']} | {r['Pts']:.1f} | {r['W']:.0f}-{r['D']:.0f}-{r['L']:.0f} | {r['GF']:.0f}-{r['GA']:.0f} | "
                     f"{r['xGF']:.0f}-{r['xGA']:.0f} | {r['xPts']:.1f} | {cmp('Pts')} | {cmp('xPts')} | "
                     + (f"{r['dGD']:+.1f}" if 'dGD' in r else '') + ' |')
    lines += ['', 'Per season. Differences are paired (same fixtures, same seeds); |t| ≥ 2 is about 95% confidence.']
    ot = m['opponent_tactics']
    if isinstance(ot, dict):
        own = sum('its own' in v.get('home', '') for v in ot.values())
        lines += ['', f"Opponents' tactics: {own} of {len(ot)} clubs with their own tactic from an imported match; the rest from the closest situation."]
    else: lines += ['', f"Opponents' tactics: {ot}."]
    if m['skipped']: lines += ['', f"Skipped: {len(m['skipped'])} fixtures (" + '; '.join(m['skipped'][:3]) + ')']
    if res['completed'] < res['total']: lines += ['', f"Incomplete: {res['completed']} of {res['total']} matches played."]
    text = '\n'.join(lines) + '\n'
    (Path(out) / 'report.md').write_text(text, encoding='utf8'); print(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('out'); p.add_argument('--save'); p.add_argument('--club'); p.add_argument('--tactic', action='append', default=[])
    p.add_argument('--seeds', type=int, default=10); p.add_argument('--familiarity', type=int, default=80)
    p.add_argument('--opponents', default='ai'); p.add_argument('--template', action='append', default=[])
    p.add_argument('--workers', type=int, default=6); p.add_argument('--report', action='store_true')
    p.add_argument('--build-only', action='store_true')
    p.add_argument('--opponent-management', choices=('ai', 'assistant'),
                   help="who manages the opponents during the match: the AI (adapts roles, duties and mentality; default with "
                        "--opponents ai) or the assistant (keeps their tactic, substitutions only)")
    p.add_argument('--no-own-tactics', action='store_true', help="give every opponent the closest situation's tactic, never its own")
    a = p.parse_args(); out = Path(a.out).resolve()
    if a.report: return report(out)
    if not (a.save and a.club and a.tactic): raise SystemExit('Give --save, --club and at least one --tactic')
    import study, club_season as season
    cfg = {'save': a.save, 'club': a.club, 'tactics': [tactic(t) for t in a.tactic], 'seeds': a.seeds,
           'familiarity': a.familiarity, 'opponents': a.opponents, 'templates': a.template, 'own_tactics': not a.no_own_tactics,
           'opponent_management': a.opponent_management}
    total = season.build(study.app(), cfg, out)
    print(f'{total} matches (about {max(1, round(total / (1000 * a.workers) * 60))} min with {a.workers} workers)', flush=True)
    if a.build_only: return
    season.run(out, a.workers)
    report(out)


if __name__ == '__main__':
    main()
