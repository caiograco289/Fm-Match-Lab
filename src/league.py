"""Leagues of tactics: every team plays every other at home and away, over several seasons, on FM27's engine.

Shared by the app's League page and `scripts/study.py league`, so both build and score a league the same way.

A league is a folder with config.json (the teams and settings), jobs.json / results.jsonl (the resumable runner,
port/validation/overnight.py) and meta.json (what was built). A team is a name, a tactic, a squad and a familiarity
level. Every fixture starts from one saved match (the template: stadium, conditions, the engine's player records);
each side gets its team's squad and tactic, picks its XI by position for that tactic, and is managed by the assistant
during the match. A season is one double round robin on one seed; season k uses seed k for every fixture.

Squads:
  {"kind": "reference", "tier": "pl-middle"}    synthetic reference squad (src/reference_squads.json)
  {"kind": "match", "match": PATH, "side": 0}    the players of one side of a saved or imported match
  {"kind": "save", "save": PATH, "club": NAME}   a club's current players from an FM27 save (needs fmsave)
  {"kind": "levelled", "value": 12}              the template side's players with every match attribute at VALUE
  {"kind": "natural"}                            the template's own players on whichever side the team plays
Tactics: {"kind": "preset", "style": "Gegenpress"} or {"kind": "fmf", "path": PATH}.
"""
import copy, csv, io, json, math, os, statistics, time
from pathlib import Path

# the repository (the app runs from a copy of src/ in build/source; FM27_ENGINE_ROOT is the repository's private/engine)
ROOT = Path(os.environ['FM27_ENGINE_ROOT']).resolve().parents[1] if os.environ.get('FM27_ENGINE_ROOT') else Path(__file__).resolve().parents[1]
REFERENCE = ROOT / 'src/reference_squads.json'
AREAS = [o + k for o in range(1, 25, 3) for k in (0, 1, 2)]   # the 24 tactical-area bytes of the effectiveness record
EQUAL_START = {'condition': 10000, 'sharpness': 10000, 'sharpness_secondary': 10000, 'fatigue_raw': 0, 'morale': 15, 'club_cohesion': 100}
LEVELLED_NOTE = ('Levelled squads on a single test match can shrink or hide attribute and tactic effects (Study 2). '
                 'Synthetic or real squads are better for that reason.')


def xpts(a, b, cap=12):
    """Expected points: 3 P(win) + P(draw), each side's goals Poisson around its xG."""
    pa = [math.exp(-a) * a ** k / math.factorial(k) for k in range(cap)]
    pb = [math.exp(-b) * b ** k / math.factorial(k) for k in range(cap)]
    return 3 * sum(pa[i] * pb[j] for i in range(cap) for j in range(i)) + sum(pa[i] * pb[i] for i in range(cap))


def reference_squads():
    return json.loads(REFERENCE.read_text(encoding='utf8'))


def squad_label(sq):
    k = sq.get('kind', 'reference')
    if k == 'reference': return 'Synthetic ' + reference_squads()['tiers'][sq.get('tier', 'pl-middle')]['label']
    if k == 'match': return f"{Path(sq['match']).name.replace('_VER_fm.pkm', '').replace('_', ' ')}, {'home' if int(sq.get('side', 0)) == 0 else 'away'} side"
    if k == 'save': return f"{sq['club']} (from a save)"
    if k == 'levelled': return f"Levelled: every attribute {int(sq.get('value', 12))}"
    return 'The template match\'s own players'


def tactic_label(t): return f"Preset: {t['style']}" if t['kind'] == 'preset' else Path(t['path']).stem


def level(team, value):
    """Every match attribute (not the 15 position ratings) of every player at VALUE (1-20)."""
    for p in team['players']:
        for i in range(15, len(p['attributes'])): p['attributes'][i] = int(value) * 5


def transplant(A, team, source):
    """The source team's players (best current ability first) into this team's slots; XI picked later."""
    import study6_tactics
    src = sorted(source['players'][:source.get('roster_size', len(source['players']))],
                 key=lambda p: -(p['native_profile'].get('current_ability') or 0))
    size = team.get('roster_size', len(team['players']))
    for j, p in enumerate(src[:size]):
        q = team['players'][j]
        q['attributes'] = list(p['attributes']); q['name'] = p['name']
        q['native_profile'].update({k: v for k, v in p['native_profile'].items() if k not in EQUAL_START and k != 'team_cohesion'})
    study6_tactics.pick_xi(team)


def equalise(s):
    """Both sides start alike: full condition and sharpness, no fatigue, the same morale and cohesion (team
    cohesion 80, or the nearest value both sides can take)."""
    ranges = (s.get('match_base') or {}).get('cohesion_ranges') or [None, None]
    lo = max((r[0] for r in ranges if r), default=0); hi = min((r[1] for r in ranges if r), default=100)
    for side, t in enumerate(s['teams']):
        r = ranges[side] if side < len(ranges) and ranges[side] else (0, 100)
        cohesion = min(hi, max(lo, 80)) if lo <= hi else min(r[1], max(r[0], 80))
        for p in t['players']: p['native_profile'].update(EQUAL_START, team_cohesion=cohesion)


class Builder:
    def __init__(self, A, out):
        import study
        self.A, self.study, self.out = A, study, out; self.cache = {}

    def squad(self, s, side, sq):
        A, k = self.A, sq.get('kind', 'reference')
        if k == 'natural': return s
        if k == 'levelled':
            level(s['teams'][side], sq.get('value', 12)); return s
        import squad_from_save
        if k == 'reference':
            return squad_from_save.apply_squad(A, s, side, reference_squads()['tiers'][sq.get('tier', 'pl-middle')]['players'])
        if k == 'save':
            return squad_from_save.apply_squad(A, s, side, squad_from_save.read_club(Path(sq['save']).expanduser(), sq['club']))
        if k == 'match':
            key = (sq['match'], int(sq.get('side', 0)))
            if key not in self.cache: self.cache[key] = A.validate_scenario(A.SAVED_MATCHES.open(sq['match']).default)['teams'][key[1]]
            transplant(A, s['teams'][side], self.cache[key]); return s
        raise ValueError(f'Unknown squad kind {k!r}')

    def tactic(self, s, side, t):
        if t['kind'] == 'preset': source = (f"preset {t['style']}", 'preset', t['style'])
        else: source = (Path(t['path']).stem, 'fmf', str(Path(t['path']).expanduser().resolve()))
        return self.study.apply_tactic(s, side, source, self.out)

    def side(self, s, side, team):
        s = self.squad(s, side, team['squad'])
        return self.tactic(self.A.validate_scenario(s), side, team['tactic'])


def build(A, cfg, out, say=print):
    """Write jobs.json and meta.json for a league config; returns the number of matches."""
    out = Path(out); out.mkdir(parents=True, exist_ok=True); (out / 'bins').mkdir(exist_ok=True)
    (out / 'config.json').write_text(json.dumps(cfg, indent=1, ensure_ascii=False), encoding='utf8')
    teams, seasons = cfg['teams'], int(cfg.get('seasons', 1))
    if not 2 <= len(teams) <= 20: raise ValueError('A league needs 2 to 20 teams')
    base_path = str(Path(cfg['base_match']).expanduser().resolve())
    base = A.validate_scenario(A.SAVED_MATCHES.open(base_path).default)
    b = Builder(A, out); jobs, skipped = [], []
    complexity = ','.join(f'{x}:{o}=50' for x in (0, 1) for o in (0x19, 0x1a))
    for i, home in enumerate(teams):
        for j, away in enumerate(teams):
            if i == j or (not cfg.get('home_and_away', True) and j < i): continue
            try:
                s = b.side(b.side(copy.deepcopy(base), 0, home), 1, away)
                if cfg.get('equal_start', True): equalise(s)
                blob = A.encode_scenario(A.validate_scenario(s))
            except Exception as e:
                skipped.append(f'{home["name"]} v {away["name"]}: {str(e)[:160]}'); continue
            f = out / 'bins' / f'{i}_{j}.bin'; f.write_bytes(blob)
            fam = ','.join(f'{x}:{o}={int(t.get("familiarity", cfg.get("familiarity", 70)))}' for x, t in ((0, home), (1, away)) for o in AREAS)
            jobs.append(['L', f'L|{i}|{j}', base_path, str(f), {'FM27_MAC_EXEC_FIELDS': fam + ',' + complexity}])
        say(f'built {home["name"]}')
    jobs = [j + [1, s] for s in range(1, seasons + 1) for j in jobs]   # season by season: seasons finish in order
    info = (base.get('match_base') or {})
    meta = {'teams': [{'name': t['name'], 'tactic': tactic_label(t['tactic']), 'squad': squad_label(t['squad']),
                       'familiarity': int(t.get('familiarity', cfg.get('familiarity', 70)))} for t in teams],
            'base_match': f"{info.get('home', '')} v {info.get('away', '')}".strip() or Path(base_path).name,
            'base_match_file': Path(base_path).name, 'base_match_game_version': info.get('game_version'),
            'engine': (getattr(A, 'ENGINE_COMPATIBILITY', {}) or {}).get('profile'),
            'seasons': seasons, 'home_and_away': cfg.get('home_and_away', True), 'equal_start': cfg.get('equal_start', True),
            'reference_squads': reference_squads()['calibration'] if any(t['squad'].get('kind', 'reference') == 'reference' for t in teams) else None,
            'skipped': skipped, 'created': time.time(), 'sides': {'L': 0}}
    (out / 'jobs.json').write_text(json.dumps(jobs)); (out / 'meta.json').write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    return sum(j[5] for j in jobs)


def run(out, workers=6, stop=None):
    import overnight
    overnight.run(Path(out).resolve(), workers, stop=stop)


def progress(out):
    out = Path(out)
    total = sum(j[5] for j in json.loads((out / 'jobs.json').read_text())) if (out / 'jobs.json').is_file() else 0
    done = sum(1 for _ in open(out / 'results.jsonl')) if (out / 'results.jsonl').is_file() else 0
    return done, total


def table(out):
    """League table averaged over seasons (with the spread across seasons), head to head, and the settings."""
    out = Path(out); meta = json.loads((out / 'meta.json').read_text(encoding='utf8')); names = [t['name'] for t in meta['teams']]
    n = len(names); per = {}   # (season, team) -> totals
    h2h = [[[0, 0] for _ in range(n)] for _ in range(n)]
    rows = (json.loads(l) for l in open(out / 'results.jsonl')) if (out / 'results.jsonl').is_file() else ()
    for r in rows:
        _, i, j = r['cond'].split('|'); i, j = int(i), int(j)
        for side, me, them in ((0, i, j), (1, j, i)):
            g, c = r['score'][side], r['score'][1 - side]; xf, xa = r['xg'][side], r['xg'][1 - side]
            t = per.setdefault((r['seed'], me), dict(P=0, W=0, D=0, L=0, GF=0, GA=0, xGF=0.0, xGA=0.0, xPts=0.0, Pts=0))
            pts = 3 if g > c else 1 if g == c else 0
            t['P'] += 1; t['W' if g > c else 'D' if g == c else 'L'] += 1; t['GF'] += g; t['GA'] += c
            t['xGF'] += xf; t['xGA'] += xa; t['xPts'] += xpts(xf, xa); t['Pts'] += pts
            h2h[me][them][0] += pts; h2h[me][them][1] += 1
    seasons = sorted({s for s, _ in per})
    rows = []
    for k, name in enumerate(names):
        mine = [per[(s, k)] for s in seasons if (s, k) in per]
        if not mine: rows.append({'team': name, **meta['teams'][k], 'seasons': 0}); continue
        avg = lambda f: sum(m[f] for m in mine) / len(mine)
        pts = [m['Pts'] for m in mine]; games = avg('P') or 1
        rows.append({'team': name, **{f: meta['teams'][k][f] for f in ('tactic', 'squad', 'familiarity')}, 'seasons': len(mine),
                     'P': avg('P'), 'W': avg('W'), 'D': avg('D'), 'L': avg('L'), 'GF': avg('GF'), 'GA': avg('GA'),
                     'xGF': avg('xGF') / games, 'xGA': avg('xGA') / games, 'xPts': avg('xPts'), 'Pts': avg('Pts'),
                     'Pts_sd': statistics.stdev(pts) if len(pts) > 1 else None, 'PPG': avg('Pts') / games})
    rows.sort(key=lambda r: -(r.get('Pts') or -1))
    for pos, r in enumerate(rows, 1): r['rank'] = pos
    grid = {names[a]: {names[b]: (h2h[a][b][0] / h2h[a][b][1] if h2h[a][b][1] else None) for b in range(n) if b != a} for a in range(n)}
    done, total = progress(out)
    return {'table': rows, 'head_to_head': grid, 'order': [r['team'] for r in rows], 'meta': meta, 'completed': done, 'total': total,
            'seasons_complete': len([s for s in seasons if all((s, k) in per and per[(s, k)]['P'] == 2 * (n - 1) for k in range(n))])}


def to_csv(result):
    f = io.StringIO(); w = csv.writer(f)
    cols = ['rank', 'team', 'tactic', 'squad', 'familiarity', 'seasons', 'P', 'W', 'D', 'L', 'GF', 'GA', 'xGF', 'xGA', 'xPts', 'Pts', 'Pts_sd', 'PPG']
    w.writerow(cols)
    for r in result['table']:
        w.writerow([round(r[c], 3) if isinstance(r.get(c), float) else r.get(c) for c in cols])
    w.writerow([]); w.writerow(['head to head: points per match of the row team against the column team'])
    order = result['order']; w.writerow([''] + order)
    for a in order: w.writerow([a] + ['' if a == b else (round(result['head_to_head'][a][b], 3) if result['head_to_head'][a][b] is not None else '') for b in order])
    m = result['meta']; w.writerow([])
    for k in ('base_match', 'base_match_game_version', 'engine', 'seasons', 'equal_start'): w.writerow([k, m.get(k)])
    return f.getvalue()
