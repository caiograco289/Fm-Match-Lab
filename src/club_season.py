"""A season for one club, on FM27's engine: its real league fixtures and opponents from an FM27 save, played with each
candidate tactic on the same seeds, for a quick number per tactic.

Shared by `scripts/season.py` (and later the app). A season run is a folder with config.json, jobs.json /
results.jsonl (the resumable runner, port/validation/overnight.py) and meta.json.

What is real and what is not:
- **Real:** the club's league and opponents (from the save's fixtures for the current season), every squad (the
  save's players, best current ability first, XI picked by position for the tactic).
- **Opponents' tactics:** the AI does not store a tactic in the save, so each opponent gets a tactic the game's AI
  actually picked in a match it played: that club's own, when an imported match has it, otherwise the one picked by
  the AI club whose situation was closest (strength of its XI and the gap to its opponent). The AI then manages the
  opponent from kick-off (in-match management "AI"), so it adjusts roles, duties and mentality to the match as it
  does in the game; with opponent_management 'assistant' it keeps that tactic and only makes substitutions.
- **The club:** each candidate tactic, the assistant managing in the match (substitutions), as in an instant result.
- **Not modelled:** cups, injuries, suspensions, rotation, form and morale over the season, the club's own ground
  (fixtures are played on template matches from the same league where there are some). Both sides start alike, with
  tactical familiarity held at the same level.

Every tactic plays the same fixtures on the same seeds, so tactics are compared match by match. Season s = every
fixture on seed s.
"""
import copy, json, math, os, statistics, time
from pathlib import Path

import league

ROOT = league.ROOT
LIBRARY = ROOT / 'private/ai_tactics.json'   # derived from the user's matches: never committed
HOME_ADVANTAGE = ROOT / 'private/ground_home_advantage.json'   # per imported ground, from Study 15b; optional
TACTIC_FIELDS = ('mentality', 'instructions', 'phases', 'native_extra_team_bits')


# ---- the league and its clubs, from the save ----
def club_league(save, club):
    """(the club's name as the save spells it, sorted names of the clubs in its league this season)."""
    import fmsave, collections, warnings
    warnings.simplefilter('ignore')
    with fmsave.open(save) as s:
        name = {t.team_id: c.name for c in s.clubs() for t in c.teams if t.slot == 0}   # first teams only (not reserves or U21)
        year = s.info.game_date.year
        fixtures = [f for f in s.fixtures() if f.season_start_year in (year, year - 1)]
    found = next((n for n in set(name.values()) if n.lower() == club.lower()), None)
    if not found: raise ValueError(f'No club called {club!r} in the save')
    for season in (year, year - 1):   # the season about to start, or the one running
        by = collections.defaultdict(set); games = collections.Counter()
        for f in fixtures:
            if f.season_start_year != season: continue
            by[f.competition_id] |= {name.get(f.home_team_id), name.get(f.away_team_id)}; games[f.competition_id] += 1
        leagues = [cs for cid, cs in by.items() if found in cs and None not in cs and len(cs) >= 10 and games[cid] == len(cs) * (len(cs) - 1)]
        if leagues: return found, sorted(max(leagues, key=len))
    raise ValueError(f'No league (a full double round robin) with {found} in the save')


def capacities(save, clubs):
    """Each club's home stadium capacity this season (None where the save has none)."""
    import fmsave, warnings
    warnings.simplefilter('ignore')
    with fmsave.open(save) as s:
        uid, wanted = {}, set(clubs)
        for c in s.clubs():   # men's clubs first: women's sides share the name
            if c.name in wanted and getattr(c.gender, 'raw', 0) == 0: uid.setdefault(c.name, c.uid)
        cap = {}
        for x in s.stadiums():
            for u in x.home_club_uids or (): cap.setdefault(u, x.total_capacity)
    return {c: cap.get(uid.get(c)) for c in clubs}


BIG_GROUND = 40000   # Study 15b: grounds of 40,000 or more give about twice the home advantage of smaller ones


def expected_home_advantage(caps):
    """The league's typical home advantage (xG per match) from its clubs' capacities and the measured grounds."""
    if not HOME_ADVANTAGE.is_file(): return None
    known = json.loads(HOME_ADVANTAGE.read_text())['grounds'].values()
    def band(big):
        g = [(1 / x['se'] ** 2, x['xg_home_advantage']) for x in known if (x['capacity'] >= BIG_GROUND) == big]
        return sum(w * y for w, y in g) / sum(w for w, _ in g)
    level = {True: band(True), False: band(False)}
    caps = [c for c in caps.values() if c]
    return statistics.mean(level[c >= BIG_GROUND] for c in caps) if caps else None


def xi_strength(players):
    """Average current ability of the best eleven."""
    cas = sorted((p.get('current_ability') or 0 for p in players), reverse=True)[:11]
    return sum(cas) / max(1, len(cas))


# ---- the AI's own tactics, from matches between other clubs ----
def library(A, refresh=False, say=print):
    """Every AI-picked tactic in the imported matches between other clubs, with its situation; cached."""
    import match_backup
    folder = match_backup.backup_folder() / 'Other_clubs'
    files = sorted(str(p) for p in folder.glob('*_VER_fm.pkm'))
    if LIBRARY.is_file() and not refresh:
        lib = json.loads(LIBRARY.read_text(encoding='utf8'))
        if lib.get('files') == files: return lib
    entries = []
    for f in files:
        try: s = A.validate_scenario(A.SAVED_MATCHES.open(f).default)
        except Exception: continue   # a match the editor cannot represent (for example the user's own club)
        strength = [xi_strength([t['players'][i]['native_profile'] for i in t['lineup']]) for t in s['teams']]
        for k, t in enumerate(s['teams']):
            entries.append({'club': t['name'], 'file': f, 'side': k, 'mtime': os.path.getmtime(f),
                            'strength': round(strength[k], 1), 'gap': round(strength[k] - strength[1 - k], 1),
                            'home': k == 0, 'tactic': {f_: t[f_] for f_ in TACTIC_FIELDS}})
    lib = {'files': files, 'entries': entries}
    LIBRARY.parent.mkdir(parents=True, exist_ok=True); LIBRARY.write_text(json.dumps(lib), encoding='utf8')
    say(f'AI tactic library: {len(entries)} tactics from {len(files)} matches between other clubs')
    return lib


def norm(x): return ''.join(c for c in x.lower() if c.isalnum())


def ai_tactic(lib, club, strength, gap, home, own_first=True):
    """The tactic the AI is most likely to pick: the club's own newest one (preferring the same venue), else the one
    from the closest situation (strength of the XI, gap to the opponent, venue). own_first=False always takes the
    closest situation among other clubs (to check what the fallback costs)."""
    own = [e for e in lib['entries'] if norm(e['club']) == norm(club)]
    if not own_first:
        others = [e for e in lib['entries'] if norm(e['club']) != norm(club)]
        e = min(others, key=lambda e: abs(e['strength'] - strength) / 10 + abs(e['gap'] - gap) / 10 + (e['home'] != home) * 0.3)
        return e, f"closest situation ({e['club']})"
    if own:
        e = max(own, key=lambda e: (e['home'] == home, e['mtime'])); return e, 'its own'
    if not lib['entries']: return None, 'none'
    e = min(lib['entries'], key=lambda e: abs(e['strength'] - strength) / 10 + abs(e['gap'] - gap) / 10 + (e['home'] != home) * 0.3)
    return e, f"closest situation ({e['club']})"


def put_tactic(A, team, tactic):
    import desktop_source_plans, study6_tactics
    team.update(copy.deepcopy(tactic)); desktop_source_plans.sign(A, team)
    study6_tactics.pick_xi(team); team['tactic_name'] = 'AI'


# ---- templates ----
def templates_for(clubs, limit=4, target=None):
    """Imported matches between two clubs of the league (their stadium and conditions); with a target home advantage
    (xG per match) and measured grounds, those closest to it, else the newest."""
    import match_backup
    files = sorted((match_backup.backup_folder() / 'Other_clubs').glob('*_VER_fm.pkm'), key=os.path.getmtime, reverse=True)
    names = {norm(c) for c in clubs}
    def both_in(f):
        home, _, rest = f.name.partition('_v_'); away = rest.rsplit('_', 3)[0]
        return norm(home) in names and norm(away) in names
    same = [f for f in files if both_in(f)]
    if target is not None and HOME_ADVANTAGE.is_file():
        import itertools
        known = json.loads(HOME_ADVANTAGE.read_text())['grounds']
        measured = [f for f in same if f.name in known][:16]
        if len(measured) >= limit:   # the set whose average is closest to the target, preferring grounds near it
            x = lambda f: known[f.name]['xg_home_advantage']
            best = min(itertools.combinations(measured, limit), key=lambda c: abs(statistics.mean(map(x, c)) - target)
                       + 0.25 * statistics.mean(abs(x(f) - target) for f in c))
            same = list(best)
    return [str(f) for f in same[:limit]], bool(same)


# ---- build ----
def build(A, cfg, out, say=print):
    """cfg: save, club, tactics (league.py tactic dicts with a 'name'), seeds, familiarity, templates (optional),
    opponents ('ai' or a preset style). Writes jobs.json and meta.json; returns the number of matches."""
    out = Path(out); out.mkdir(parents=True, exist_ok=True); (out / 'bins').mkdir(exist_ok=True)
    (out / 'config.json').write_text(json.dumps(cfg, indent=1, ensure_ascii=False), encoding='utf8')
    import squad_from_save
    save = Path(cfg['save']).expanduser()
    club, clubs = club_league(save, cfg['club'])
    squads = {c: squad_from_save.read_club(save, c) for c in clubs}
    strength = {c: xi_strength(squads[c]) for c in clubs}
    opponents = [c for c in clubs if c != club]
    templates = cfg.get('templates') or []
    league_grounds = True
    target = expected_home_advantage(capacities(save, clubs))
    if not templates: templates, league_grounds = templates_for(clubs, target=target)
    if not templates: raise ValueError('No template match: import matches between other clubs first (scripts/import_other_matches.py)')
    templates = [str(Path(t).expanduser().resolve()) for t in templates]
    bases = [league.same_squad_size(A.validate_scenario(A.SAVED_MATCHES.open(p).default)) for p in templates]
    lib = library(A, say=say) if cfg.get('opponents', 'ai') == 'ai' else None
    manage = cfg.get('opponent_management') or ('ai' if lib is not None else None)   # 'ai' or 'assistant'
    b = league.Builder(A, out); fam = int(cfg.get('familiarity', 80))
    seeds = int(cfg.get('seeds', 10)); per = math.ceil(seeds / len(templates))
    complexity = ','.join(f'{x}:{o}=50' for x in (0, 1) for o in (0x19, 0x1a))
    env = {'FM27_MAC_EXEC_FIELDS': ','.join(f'{x}:{o}={fam}' for x in (0, 1) for o in league.AREAS) + ',' + complexity}
    mine, theirs, picked, jobs, skipped = {}, {}, {}, [], []
    for k, base in enumerate(bases):
        first = k * per + 1; n = min(per, seeds - k * per)
        if n <= 0: continue
        for c, tactic in enumerate(cfg['tactics']):
            for v in (0, 1):   # v: the club's side (0 home)
                if (c, k, v) not in mine:
                    s = b.side(copy.deepcopy(base), v, {'squad': {'kind': 'save', 'save': str(save), 'club': club}, 'tactic': tactic})
                    mine[(c, k, v)] = s['teams'][v]
                for o in opponents:
                    if (o, k, v) not in theirs:
                        s = copy.deepcopy(base); u = 1 - v
                        s = squad_from_save.apply_squad(A, s, u, squads[o])
                        if lib is not None:
                            e, why = ai_tactic(lib, o, strength[o], strength[o] - strength[club], u == 0, cfg.get('own_tactics', True))
                            put_tactic(A, s['teams'][u], e['tactic'])
                            picked.setdefault(o, {})['home' if u == 0 else 'away'] = why
                        else:
                            s = b.tactic(A.validate_scenario(s), u, {'kind': 'preset', 'style': cfg['opponents']})
                        if manage: s['teams'][u]['in_match'] = manage
                        theirs[(o, k, v)] = A.validate_scenario(s)['teams'][u]
                    try:
                        s = copy.deepcopy(base); s['teams'][v] = copy.deepcopy(mine[(c, k, v)]); s['teams'][1 - v] = copy.deepcopy(theirs[(o, k, v)])
                        league.equalise(s)
                        blob = A.encode_scenario(A.validate_scenario(s))
                    except Exception as e:
                        skipped.append(f'{tactic["name"]} v {o}: {str(e)[:160]}'); continue
                    f = out / 'bins' / f'{c}_{opponents.index(o)}_{v}_{k}.bin'; f.write_bytes(blob)
                    jobs.append(['S', f'S|{c}|{opponents.index(o)}|{v}', templates[k], str(f), env, n, first])
        say(f'built template {k + 1} of {len(bases)}')
    infos = [(x.get('match_base') or {}) for x in bases]
    meta = {'club': club, 'save': save.name, 'clubs': len(clubs), 'opponents': opponents,
            'tactics': [t['name'] for t in cfg['tactics']], 'seeds': seeds, 'familiarity': fam,
            'strength': {c: round(strength[c], 1) for c in clubs}, 'rank_by_strength': sorted(clubs, key=lambda c: -strength[c]).index(club) + 1,
            'templates': [f"{x.get('home', '')} v {x.get('away', '')}" for x in infos], 'templates_from_league': league_grounds,
            'home_advantage_target': target and round(target, 3),
            'opponent_management': manage or 'default', 'opponent_tactics': picked if lib is not None else f"preset {cfg['opponents']}", 'skipped': skipped, 'created': time.time()}
    (out / 'jobs.json').write_text(json.dumps(jobs)); (out / 'meta.json').write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    return sum(j[5] for j in jobs)


def run(out, workers=6, stop=None):
    league.run(out, workers, stop)


# ---- results ----
def results(out):
    """Per tactic: season averages, and the difference from the first tactic on the same fixtures and seeds."""
    out = Path(out); meta = json.loads((out / 'meta.json').read_text(encoding='utf8'))
    rows = {}   # (tactic, opponent, venue, seed) -> (points, goals for, against, xg for, against)
    if (out / 'results.jsonl').is_file():
        for line in open(out / 'results.jsonl'):
            r = json.loads(line); _, c, o, v = r['cond'].split('|'); c, o, v = int(c), int(o), int(v)
            g, a = r['score'][v], r['score'][1 - v]; xf, xa = r['xg'][v], r['xg'][1 - v]
            rows[(c, o, v, r['seed'])] = (3 if g > a else 1 if g == a else 0, g, a, xf, xa, league.xpts(xf, xa))
    games = 2 * len(meta['opponents'])
    keys0 = {k[1:] for k in rows if k[0] == 0}
    table = []
    for c, name in enumerate(meta['tactics']):
        mine = {k[1:]: v for k, v in rows.items() if k[0] == c}
        if not mine: table.append({'tactic': name, 'matches': 0}); continue
        mean = lambda i, d=mine: sum(x[i] for x in d.values()) / len(d)
        row = {'tactic': name, 'matches': len(mine), 'seasons': len(mine) / games,
               'Pts': mean(0) * games, 'GF': mean(1) * games, 'GA': mean(2) * games, 'xGF': mean(3) * games, 'xGA': mean(4) * games,
               'xPts': mean(5) * games,
               'W': sum(x[1] > x[2] for x in mine.values()) / len(mine) * games,
               'D': sum(x[1] == x[2] for x in mine.values()) / len(mine) * games}
        row['L'] = games - row['W'] - row['D']
        if c:
            common = sorted(set(mine) & keys0)
            for f, i in (('Pts', 0), ('xPts', 5)):
                d = [mine[k][i] - rows[(0,) + k][i] for k in common]
                if len(d) > 1:
                    m = statistics.mean(d); se = statistics.stdev(d) / math.sqrt(len(d))
                    row[f'd{f}'] = m * games; row[f'd{f}_t'] = m / se if se else None
            d = [(mine[k][1] - mine[k][2]) - (rows[(0,) + k][1] - rows[(0,) + k][2]) for k in common]
            if len(d) > 1: row['dGD'] = statistics.mean(d) * games
        table.append(row)
    done, total = league.progress(out)
    return {'meta': meta, 'table': table, 'games': games, 'completed': done, 'total': total}
