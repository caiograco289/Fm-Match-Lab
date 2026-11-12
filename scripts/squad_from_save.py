"""Put any club's squad from an FM27 save onto a side of a saved match (needs fmsave: .venv/bin/pip install fmsave).

The saved match is the container (fixture, stadium, the engine's player records); the save supplies the players:
the 15 position ratings, all 54 attributes on the engine's 1-100 scale, footedness, personality, height, age,
current ability and reputation. Condition and match sharpness stay the saved match's own start values per slot. The club's best players by current ability fill the
side's matchday squad (its size is fixed by the saved match, usually 18-23), and the starting XI is picked by
position for the side's tactic. Player traits (preferred moves) are not carried over. The result is a scenario the
app opens with "Open full scenario JSON", and study.py uses the same code for leagues (--squad).

  .venv/bin/python scripts/squad_from_save.py SAVE.fm "Club name" MATCH_VER_fm.pkm --side home|away|both -o scenario.json

Checked on a 27.0.1 save against a match saved at the same moment: 19 of 19 players, every position rating and
all 969 attribute values identical.
"""
import argparse, copy, json, os, re, sys, tempfile, warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(ROOT / 'port/validation'))
os.environ.setdefault('FM27_ENGINE_ROOT', str(ROOT / 'private/engine'))
os.environ.setdefault('FM27_DESKTOP_DATA', tempfile.mkdtemp(prefix='fm27-squad-'))
ALIASES = {'tendencytopunch': 'punching'}   # engine attribute name -> fmsave field, where they differ
PERSONALITY = ('professionalism', 'loyalty', 'sportsmanship', 'temperament', 'pressure', 'ambition', 'adaptability')
_cache = {}


def norm(x): return re.sub(r'[^a-z]', '', x.lower())


def read_clubs(save):
    """{club name: players, best current ability first} for every club in a save (one pass; cached per save)."""
    key = str(save)
    if key in _cache: return _cache[key]
    try: import fmsave
    except ImportError: raise SystemExit('fmsave is needed: .venv/bin/pip install fmsave')
    warnings.simplefilter('ignore'); clubs = {}
    with fmsave.open(save) as s:
        for p in sorted(s.players(), key=lambda p: -(p.ability.current or 0) if p.ability else 0):
            if not p.club_name or not p.positions or not p.raw_attributes: continue
            clubs.setdefault(p.club_name, []).append({
                'name': p.name, 'positions': [getattr(p.positions, f) for f in type(p.positions).__dataclass_fields__],
                'raw': {norm(f): getattr(p.raw_attributes, f) for f in type(p.raw_attributes).__dataclass_fields__},
                'left_foot': p.raw_left_foot, 'right_foot': p.raw_right_foot, 'height_cm': p.height_cm, 'age': p.age,
                'current_ability': p.ability.current if p.ability else None,
                'reputation': (p.reputation.home, p.reputation.current, p.reputation.world) if p.reputation else (None, None, None),
                'personality': {k: getattr(p.personality, k) for k in PERSONALITY} if p.personality else {},
                'condition': p.raw_condition, 'sharpness': p.raw_match_sharpness})
    _cache[key] = clubs
    return clubs


def read_club(save, club):
    """Players of a club in a save, best current ability first."""
    clubs = read_clubs(save)
    found = next((v for k, v in clubs.items() if k.lower() == club.lower()), None)
    if not found:
        close = sorted(k for k in clubs if club.lower() in k.lower())[:10]
        raise SystemExit(f'No club {club!r} in the save' + (f'; did you mean: {", ".join(close)}' if close else ''))
    return found


def apply_squad(app, scenario, side, rows):
    """Overwrite one side's matchday squad with the given players (best first) and pick its XI by position."""
    import study6_tactics
    t = scenario['teams'][side]; size = t.get('roster_size', len(t['players']))
    attrs = {a['id']: norm(a['name']) for a in app.CATALOG['attributes'] if not a['position']}
    for j, row in enumerate(rows[:size]):
        p = t['players'][j]; a = p['attributes']
        # a value fmsave could not read keeps the match's own value for that slot
        for i, v in enumerate(row['positions'][:15]):
            if v is not None: a[i] = v
        for aid, name in attrs.items():
            v = row['left_foot'] if name == 'leftfoot' else row['right_foot'] if name == 'rightfoot' else row['raw'].get(ALIASES.get(name, name))
            if v is not None: a[aid] = min(100, max(1, v))
        q = p['native_profile']; clamp = lambda v, lo, hi: None if v is None else min(hi, max(lo, v))
        values = {k: v for k, v in row['personality'].items()} | {
            'height_cm': clamp(row['height_cm'], 140, 220), 'age': clamp(row['age'], 14, 60), 'current_ability': clamp(row['current_ability'], 0, 200),
            'home_reputation': row['reputation'][0], 'current_reputation': row['reputation'][1], 'world_reputation': row['reputation'][2]}
        # condition and sharpness stay the saved match's own per-slot start values: written from the save, the engine
        # did not always keep them (a readback check failed for one away player), so they are left alone
        q.update({k: v for k, v in values.items() if v is not None})
        p['name'] = row['name']
    study6_tactics.pick_xi(t)
    return scenario


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('save'); p.add_argument('club'); p.add_argument('match')
    p.add_argument('--side', choices=('home', 'away', 'both'), default='both'); p.add_argument('-o', '--out', required=True)
    a = p.parse_args()
    import fm27_tactics_server as app
    s = app.validate_scenario(app.SAVED_MATCHES.open(str(Path(a.match).expanduser().resolve())).default)
    rows = read_club(a.save, a.club)
    for side in {'home': (0,), 'away': (1,), 'both': (0, 1)}[a.side]: s = apply_squad(app, s, side, rows)
    s = app.validate_scenario(s)
    Path(a.out).write_text(json.dumps(s, ensure_ascii=False), encoding='utf8')
    print(f'{a.club}: {min(len(rows), len(s["teams"][0]["players"]))} players on the {a.side} side(s) of {Path(a.match).name} -> {a.out}')


if __name__ == '__main__':
    main()
