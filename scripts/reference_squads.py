"""Synthetic reference squads: one invented 23-man squad per tier, calibrated on FM27's player database.

The squads give every user the same realistic teams for tactic tests, without anyone's save. They are synthetic:
invented names, and every player drawn at random from a statistical profile, then checked to be no closer to any
real player than real players are to each other. Only the generated squads (src/reference_squads.json) and this
script are in the repository; the save, the real players and the profiles stay in the git-ignored private/ folder.

  .venv/bin/python scripts/reference_squads.py profile SAVE.fm     # local: tiers and profiles -> private/reference/
  .venv/bin/python scripts/reference_squads.py generate            # squads -> src/reference_squads.json (+ distance check)
  .venv/bin/python scripts/reference_squads.py check               # each squad's averages by position against its tier

Calibration (profile, needs fmsave): a save made on day 1 of the Premier League season. The 20 Premier League clubs
(found from the fixtures) are ranked by the average current ability of their best 18 players and split into tiers:
top 6, middle 8, bottom 6. Lower English leagues are used too when the save has them loaded. Per tier and position
group (goalkeeper, centre-back, right and left full-back, defensive midfielder, central midfielder, attacking
midfielder, right and left winger, striker): the mean and spread of every attribute (hidden ones included), position
rating, foot, height, age, current ability and personality value, from each club's first-team players (best 25 by
current ability). Correlations between those values come from every player of that position group in the database,
so that, for example, a quick winger tends to have good acceleration too.

Generation: each player is drawn from a multivariate normal with the tier's means and spreads and the group's
correlations (shrunk towards independence), clipped to the range seen in real players and rounded; his main position
rating is 20. Per position group, many candidate players are drawn and the set whose averages are closest to the
tier's is kept, so each squad is representative of its tier and not of one lucky or unlucky draw.
"""
import argparse, collections, json, math, random, re, sys, warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
PRIVATE = ROOT / 'private/reference'
OUT = ROOT / 'src/reference_squads.json'
POSITIONS = ('gk', 'sw', 'dl', 'dc', 'dr', 'dm', 'ml', 'mc', 'mr', 'aml', 'amc', 'amr', 'stc', 'wbl', 'wbr')   # fmsave order = engine order
GROUPS = {'GK': ('gk',), 'CB': ('dc',), 'RB': ('dr', 'wbr'), 'LB': ('dl', 'wbl'), 'DM': ('dm',), 'CM': ('mc',),
          'AM': ('amc',), 'RW': ('amr', 'mr'), 'LW': ('aml', 'ml'), 'ST': ('stc',)}
SHAPE = {'GK': 3, 'CB': 4, 'RB': 2, 'LB': 2, 'DM': 2, 'CM': 3, 'AM': 1, 'RW': 2, 'LW': 2, 'ST': 2}   # 23 players
TIERS = {'pl-top': 'Premier League, top six', 'pl-middle': 'Premier League, middle eight', 'pl-bottom': 'Premier League, bottom six',
         'championship': 'Championship', 'league-two': 'League Two'}
SEED = 27
SHRINK = 0.3   # correlation shrinkage towards independence
SETS = 400     # candidate sets per position group


def group_of(positions):
    """The player's main position group: the group of his best position rating."""
    best = max(range(15), key=lambda i: (positions[i] or 0))
    if POSITIONS[best] == 'sw': return 'CB'
    return next(g for g, ps in GROUPS.items() if POSITIONS[best] in ps)


def vector_keys(row):
    return ([f'raw.{k}' for k in sorted(row['raw'])] + [f'pos.{p}' for p in POSITIONS] +
            ['left_foot', 'right_foot', 'height_cm', 'age', 'current_ability'] + [f'per.{k}' for k in sorted(row['personality'])])


def vector(row, keys):
    out = []
    for k in keys:
        kind, _, name = k.partition('.')
        v = row['raw'].get(name) if kind == 'raw' else row['positions'][POSITIONS.index(name)] if kind == 'pos' else \
            row['personality'].get(name) if kind == 'per' else row.get(k)
        out.append(v)
    return out


# ---- profile (local) ----
def leagues(save):
    """Tiers -> club names, from the save's fixtures (league = a competition with a full double round robin)."""
    import fmsave
    with fmsave.open(save) as s:
        clubs = {c.name: c for c in s.clubs()}; fixtures = list(s.fixtures())
    by = collections.defaultdict(set); games = collections.Counter()
    for f in fixtures:
        by[f.competition_id] |= {f.home_club_name, f.away_club_name}; games[f.competition_id] += 1
    english = []
    for cid, cs in by.items():
        n = len(cs)
        if n >= 18 and games[cid] == n * (n - 1) and all(c in clubs and clubs[c].nation_id == clubs.get('Arsenal', clubs[next(iter(cs))]).nation_id for c in cs):
            english.append((sum(clubs[c].reputation or 0 for c in cs) / n, sorted(cs)))
    english.sort(reverse=True)
    if not english or 'Arsenal' not in english[0][1]: raise SystemExit('No Premier League found in the save (a full 20-club double round robin)')
    out = {'premier-league': english[0][1]}
    rest = [cs for _, cs in english[1:] if len(cs) == 24]
    if rest: out['championship'] = rest[0]
    if len(rest) >= 3: out['league-two'] = rest[2]
    return out


def cmd_profile(a):
    import squad_from_save, fmsave
    import numpy as np
    warnings.simplefilter('ignore')
    save = Path(a.save).expanduser()
    with fmsave.open(save) as s: info = s.info
    clubs = squad_from_save.read_clubs(save); found = leagues(save)
    strength = {c: np.mean([r['current_ability'] or 0 for r in clubs.get(c, [])[:18]]) for c in found['premier-league']}
    pl = sorted(found['premier-league'], key=lambda c: -strength[c])
    tiers = {'pl-top': pl[:6], 'pl-middle': pl[6:14], 'pl-bottom': pl[14:]}
    for t in ('championship', 'league-two'):
        if t in found: tiers[t] = found[t]
    sample_row = next(r for rows in clubs.values() for r in rows if r['personality'])
    keys = vector_keys(sample_row)
    usable = lambda r: r['personality'] and all(v is not None for v in vector(r, keys))
    everyone = [r for rows in clubs.values() for r in rows if usable(r)]
    by_group = collections.defaultdict(list)
    for r in everyone: by_group[group_of(r['positions'])].append(vector(r, keys))
    corr = {}
    for g, vs in by_group.items():
        x = np.array(vs, float); sd = x.std(0); sd[sd == 0] = 1
        c = np.nan_to_num(np.corrcoef(((x - x.mean(0)) / sd).T)); np.fill_diagonal(c, 1)   # a value that never varies: no correlation
        corr[g] = c.tolist()
    profiles = {}
    for tier, names in tiers.items():
        rows = [r for c in names for r in clubs.get(c, [])[:25] if usable(r)]
        groups = collections.defaultdict(list)
        for r in rows: groups[group_of(r['positions'])].append(vector(r, keys))
        profiles[tier] = {g: {'n': len(vs), 'mean': np.array(vs, float).mean(0).tolist(), 'sd': np.array(vs, float).std(0).tolist(),
                              'min': np.array(vs, float).min(0).tolist(), 'max': np.array(vs, float).max(0).tolist()}
                          for g, vs in groups.items()}
        profiles[tier]['_reputation'] = np.median([r['reputation'] for r in rows if None not in r['reputation']], axis=0).tolist()
        profiles[tier]['_clubs'] = len(names)
    real = {'keys': keys, 'raw': [vector(r, keys)[:52] for r in everyone], 'group': [group_of(r['positions']) for r in everyone]}
    PRIVATE.mkdir(parents=True, exist_ok=True)
    (PRIVATE / 'profiles.json').write_text(json.dumps({'keys': keys, 'tiers': {t: profiles[t] for t in tiers}, 'correlations': corr,
                                                      'game_build': info.build, 'database': info.db_version, 'game_date': str(info.game_date),
                                                      'tier_sizes': {t: len(v) for t, v in tiers.items()}}))
    (PRIVATE / 'real_players.json').write_text(json.dumps(real))
    print(f'{info.build} (database {info.db_version}), {info.game_date}: tiers ' +
          ', '.join(f'{t} {len(v)} clubs' for t, v in tiers.items()) + f'; {len(everyone)} players for correlations -> {PRIVATE}')


# ---- generate ----
FIRST = ('Aaron', 'Adam', 'Alan', 'Alex', 'Andrew', 'Ben', 'Callum', 'Chris', 'Dan', 'David', 'Dean', 'Ethan', 'Gary', 'Harry',
         'Ian', 'Jack', 'Jake', 'James', 'Joe', 'John', 'Josh', 'Kevin', 'Kyle', 'Lewis', 'Liam', 'Luke', 'Mark', 'Matt', 'Neil',
         'Nick', 'Oliver', 'Owen', 'Paul', 'Peter', 'Ryan', 'Sam', 'Scott', 'Sean', 'Simon', 'Tom', 'Tony', 'Will')
PARTS = (('Al', 'Ash', 'Bar', 'Brack', 'Cal', 'Craw', 'Dal', 'Elm', 'Fen', 'Garn', 'Hal', 'Hart', 'Kel', 'Lang', 'Mar', 'Nor',
          'Pen', 'Quill', 'Rad', 'Ren', 'Shel', 'Stan', 'Tal', 'Thorn', 'Ward', 'Wes'),
         ('bridge', 'brook', 'by', 'combe', 'den', 'field', 'ford', 'gate', 'ham', 'holt', 'ley', 'mere', 'more', 'ridge',
          'shaw', 'stead', 'ton', 'well', 'wick', 'worth'))


def invented_names(rng, n, banned):
    out, seen = [], set()
    while len(out) < n:
        name = f'{rng.choice(FIRST)} {rng.choice(PARTS[0])}{rng.choice(PARTS[1])}'
        if name in seen or any(b in name.lower() for b in banned): continue
        seen.add(name); out.append(name)
    return out


def cmd_generate(a):
    import numpy as np
    prof = json.loads((PRIVATE / 'profiles.json').read_text()); real = json.loads((PRIVATE / 'real_players.json').read_text())
    keys = prof['keys']; rng = np.random.default_rng(a.seed); names_rng = random.Random(a.seed)
    real_x = np.array(real['raw'], float) / 5   # in-game 1-20 scale
    real_g = np.array(real['group'])
    # threshold per position group: how close real players of that group are to their nearest other real player
    # (5th percentile), on all 52 attributes; goalkeepers sit much closer to each other than outfield players
    thresholds = {}
    for g in SHAPE:
        idx = np.flatnonzero(real_g == g); pick = np.random.default_rng(0).choice(idx, min(600, len(idx)), replace=False)
        nn = []
        for v in real_x[pick]:
            d = np.sqrt(((real_x - v) ** 2).sum(1)); d.sort(); nn.append(d[1])
        thresholds[g] = float(np.percentile(nn, 5))
    banned = []
    terms = ROOT / 'private/personal_terms.txt'
    if terms.is_file(): banned = [t.strip().lower() for t in terms.read_text().splitlines() if t.strip()]
    out = {'about': 'Synthetic reference squads: invented players, calibrated on the FM27 player database. Not real players.',
           'calibration': {'game_build': prof['game_build'], 'database': prof['database'], 'game_date': prof['game_date'],
                           'source': 'Premier League clubs at the start of the season' + (' and lower English leagues' if len(prof['tiers']) > 3 else ''),
                           'tier_sizes': prof['tier_sizes']},
           'generator': {'script': 'scripts/reference_squads.py', 'seed': a.seed, 'correlation_shrinkage': SHRINK},
           'distance_check': {}, 'tiers': {}}
    for tier, groups in prof['tiers'].items():
        players, closest = [], math.inf
        names = invented_names(names_rng, 23, banned)
        for g, count in SHAPE.items():
            p = groups.get(g)
            if not p: raise SystemExit(f'{tier}: no {g} players in the calibration')
            mean, sd = np.array(p['mean']), np.array(p['sd']); lo, hi = np.array(p['min']), np.array(p['max'])
            corr = np.array(prof['correlations'][g]); corr = (1 - SHRINK) * corr + SHRINK * np.eye(len(corr))
            cov = np.outer(sd, sd) * corr
            def draw():
                for attempt in range(200):
                    v = np.clip(np.round(rng.multivariate_normal(mean, cov, method='eigh')), lo, hi)
                    d = float(np.sqrt(((real_x - v[:52] / 5) ** 2).sum(1)).min())
                    if d > thresholds[g]: return v, d
                raise SystemExit(f'{tier} {g}: could not draw a player far enough from every real player')
            # each player is random, but the group is representative: of SETS candidate sets, keep the one whose
            # averages are closest to the tier's (standardised), so one unlucky draw does not misplace a squad
            pool = [draw() for _ in range(count * 12)]; scale = np.where(sd > 0, sd, 1)
            weight = np.ones(len(keys)); weight[keys.index('current_ability')] = 20   # ability above all: it sets the tier
            best = min((rng.choice(len(pool), count, replace=False) for _ in range(SETS)),
                       key=lambda ix: float((weight * ((np.mean([pool[i][0] for i in ix], 0) - mean) / scale) ** 2).sum()))
            for i in best:
                v, d = pool[i]
                closest = min(closest, d / thresholds[g])
                row = {'name': names[len(players)], 'group': g, 'raw': {}, 'personality': {}, 'positions': [None] * 15}
                for k, x in zip(keys, v.tolist()):
                    kind, _, name = k.partition('.')
                    if kind == 'raw': row['raw'][name] = int(x)
                    elif kind == 'pos': row['positions'][POSITIONS.index(name)] = int(min(20, max(1, x)))
                    elif kind == 'per': row['personality'][name] = int(x)
                    else: row[k] = int(x)
                row['positions'][POSITIONS.index(GROUPS[g][0])] = 20
                row['reputation'] = [int(x) for x in groups['_reputation']]
                row['condition'] = row['sharpness'] = None
                players.append(row)
        players.sort(key=lambda r: -r['current_ability'])
        out['tiers'][tier] = {'label': TIERS[tier], 'players': players}
        out['distance_check'][tier] = {'closest_to_any_real_player_relative_to_threshold': round(closest, 2)}
    out['distance_check']['thresholds'] = {g: round(v, 2) for g, v in thresholds.items()}
    out['distance_check']['measure'] = ('Euclidean distance to the nearest real player in the database over all 52 attributes on the '
                                        '1-20 scale; it must exceed the position group\'s threshold, the 5th percentile of real players\' '
                                        'distance to their nearest other real player (ratio above 1 = farther than that)')
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf8')
    print(f'{OUT.relative_to(ROOT)}: ' + ', '.join(f'{t} {len(v["players"])} players' for t, v in out['tiers'].items()) +
          f'; closest to a real player, relative to the threshold: '
          + ', '.join(f'{t} {out["distance_check"][t]["closest_to_any_real_player_relative_to_threshold"]}' for t in out['tiers']))


def cmd_check(a):
    """Each synthetic squad's average by position group against its tier's real profile, on key attributes."""
    prof = json.loads((PRIVATE / 'profiles.json').read_text()); squads = json.loads(OUT.read_text()); keys = prof['keys']
    show = ['current_ability', 'raw.pace', 'raw.acceleration', 'raw.passing', 'raw.tackling', 'raw.finishing', 'raw.reflexes']
    for tier, sq in squads['tiers'].items():
        print(f'\n{tier}: synthetic (real tier average)')
        for g in SHAPE:
            rows = [r for r in sq['players'] if r['group'] == g]
            cells = []
            for k in show:
                i = keys.index(k); real_m = prof['tiers'][tier][g]['mean'][i]
                mine = sum(vector(r, keys)[i] for r in rows) / len(rows)
                cells.append(f'{k.split(".")[-1][:6]} {mine:5.0f} ({real_m:5.0f})')
            print(f'  {g:3} ' + '  '.join(cells))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('profile'); s.add_argument('save')
    s = sub.add_parser('generate'); s.add_argument('--seed', type=int, default=SEED)
    sub.add_parser('check')
    a = p.parse_args()
    {'profile': cmd_profile, 'generate': cmd_generate, 'check': cmd_check}[a.cmd](a)


if __name__ == '__main__':
    main()
