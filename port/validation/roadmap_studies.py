"""The research roadmap's neutral-ground studies as specifications for neutral_study.py.

Each entry returns {'title', 'seeds', 'groups': [...]}; a group names the tested side's preset ('style'), optional
team-instruction overrides, squad tiers, opponents, templates and its conditions [(name, edit(A, s, side))]. Attribute
values are stored as in-game value x 5 (1-100); position ratings and personality fields as in-game values (1-20).
"""
from neutral_study import ids, starters, position_group, rating_index

TOP10 = ['Pace', 'Acceleration', 'Jumping Reach', 'Stamina', 'Anticipation', 'Dribbling', 'Concentration', 'Balance',
         'Composure', 'Work Rate']   # Study 1's ten largest effects
EUROPEAN = ['A_Madrid_v_FC_Bayern_M_nchen_2098014266_VER_fm.pkm', 'Arsenal_v_Borussia_Dortmund_2389949539_VER_fm.pkm',
            'Bergamo_v_Manchester_City_2458966288_VER_fm.pkm', 'Football_Club_K_benhavn_v_Manchester_United_139096718_VER_fm.pkm']
STADIUMS = ['Arsenal_v_Fulham_2398175457_VER_fm.pkm', 'Everton_v_Newcastle_United_2316349471_VER_fm.pkm',
            'Leeds_United_v_Tottenham_Hotspur_2535055280_VER_fm.pkm', 'Burnley_v_West_Ham_United_2378689327_VER_fm.pkm',
            'Brentford_v_Southampton_135129997_VER_fm.pkm', 'Birmingham_City_v_Bolton_Wanderers_2390345548_VER_fm.pkm',
            'Bristol_Rovers_v_Oldham_Athletic_2458886975_VER_fm.pkm', 'Barnet_v_Colchester_United_2535072817_VER_fm.pkm',
            'Boreham_Wood_v_Woking_2097066184_VER_fm.pkm', 'Chester_v_Yeovil_Town_2147899757_VER_fm.pkm',
            'Dartford_v_Ebbsfleet_United_2478449961_VER_fm.pkm', 'AFC_Fylde_v_Boreham_Wood_2096998971_VER_fm.pkm']


# ---- edits -------------------------------------------------------------------------------------------------------
def everyone(t): return range(len(t['players']))


def in_group(group):
    return lambda t: [i for i, ip, _ in starters(t) if position_group(ip) == group]


def slots(codes):
    return lambda t: [i for i, ip, _ in starters(t) if ip in codes]


def add(names, step=5, who=everyone, sides='me'):
    def edit(A, s, side):
        for x in ((side,) if sides == 'me' else (0, 1)):
            t = s['teams'][x]
            for i in who(t):
                a = t['players'][i]['attributes']
                for j in ids(names): a[j] = min(100, max(5, a[j] + step * 5))
    return edit


def set_attr(names, level, who=everyone):
    def edit(A, s, side):
        t = s['teams'][side]
        for i in who(t):
            for j in ids(names): t['players'][i]['attributes'][j] = level * 5
    return edit


def profile(field, value, sides='me', who=everyone):
    def edit(A, s, side):
        for x in ((side,) if sides == 'me' else (0, 1)):
            t = s['teams'][x]
            for i in who(t): t['players'][i]['native_profile'][field] = value
    return edit


def both(*edits):
    def edit(A, s, side):
        for e in edits: e(A, s, side)
    return edit


def name(names): return names[0] if len(names) == 1 else '+'.join(names)


# ---- studies -----------------------------------------------------------------------------------------------------
def s09b():
    st = [('Stamina+5', add(['Stamina']))]
    # the Gegenpress preset is already at the top of all three (Much more often, Much Higher, High press)
    return {'title': 'Study 9b: Stamina under high and low intensity', 'seeds': 50, 'pilot_seeds': 4, 'groups': [
        {'name': 'High intensity', 'style': 'Gegenpress', 'conds': st},
        {'name': 'Standard intensity', 'style': 'Gegenpress', 'conds': st,
         'instructions': {'TriggerPress': 'Standard', 'Tempo': 'Standard', 'LineOfEngagement': 'Mid block'}},
        {'name': 'Low intensity', 'style': 'Gegenpress', 'conds': st,
         'instructions': {'TriggerPress': 'Much less often', 'Tempo': 'Much Lower', 'LineOfEngagement': 'Low block'}}],
        'notes': 'One shape (Gegenpress) at three intensities: the preset itself (pressing Much more often, tempo Much '
                 'Higher, High press), all three Standard / Mid block, and all three at the bottom (Much less often, Much '
                 'Lower, Low block).'}


COMBOS = {'Playmaking': ['Passing', 'Vision', 'Technique', 'Decisions'],
          'Ball carrying': ['Dribbling', 'Balance', 'Concentration', 'Long Shots'],
          'Defending': ['Tackling', 'Marking', 'Positioning', 'Anticipation'],
          'Aerial': ['Jumping Reach', 'Heading', 'Strength', 'Bravery']}


def combo_conds(groups):
    out = []
    for g, names in groups.items():
        out += [(f'{n}+5', add([n])) for n in names] + [(f'{g} group+5', add(names))]
    return out


def s10():
    return {'title': 'Study 10: attribute combinations', 'seeds': 100, 'pilot_seeds': 4, 'groups': [
        {'name': 'Gegenpress', 'style': 'Gegenpress', 'conds': combo_conds(COMBOS)},
        {'name': 'Tiki-Taka', 'style': 'Tiki-Taka', 'conds': combo_conds({'Playmaking': COMBOS['Playmaking']})}]}


def s11():
    conds = []
    for a in ['Consistency', 'Important Matches', 'Injury Proneness', 'Dirtiness', 'Versatility']:
        conds += [(f'{a}={v}', set_attr([a], v)) for v in (1, 10, 20)]
    for f in ['pressure', 'professionalism', 'temperament']:
        conds += [(f'{f}={v}', profile(f, v)) for v in (1, 10, 20)]
    for f in ['sportsmanship', 'ambition', 'loyalty', 'adaptability']:
        conds += [(f'{f}={v}', profile(f, v)) for v in (1, 20)]
    big = [(f'{a}={v}', set_attr([a], v)) for a in ('Important Matches', 'Consistency') for v in (1, 20)] + \
          [(f'pressure={v}', profile('pressure', v)) for v in (1, 20)]
    return {'title': 'Study 11: hidden and personality attributes', 'seeds': 40, 'pilot_seeds': 4, 'groups': [
        {'name': 'League', 'style': 'Gegenpress', 'conds': conds},
        {'name': 'European nights', 'style': 'Gegenpress', 'conds': big, 'templates': EUROPEAN}],
        'notes': 'Controversy is not a field of the match input, so it is not tested. "European nights" uses four real '
                 'European fixtures between other clubs as templates; the match input has no editable importance field.'}


THRESHOLD = ['Pace', 'Acceleration', 'Stamina', 'Work Rate', 'Anticipation', 'Strength', 'Jumping Reach',
             'Concentration', 'Balance', 'Dribbling', 'Passing', 'Decisions', 'Finishing']
LEVELS = [1, 3, 6, 9, 12, 15, 18, 20]


def s12():
    return {'title': 'Study 12: thresholds (dose response)', 'seeds': 25, 'pilot_seeds': 2, 'groups': [
        {'name': 'Gegenpress', 'style': 'Gegenpress', 'conds': [(f'{a}={v}', set_attr([a], v)) for a in THRESHOLD for v in LEVELS]}]}


COUNT_ORDER = ['DMR', 'DCR', 'STR', 'AMR', 'DR', 'DML', 'DCL', 'STL', 'AML', 'DL', 'GK']   # Gegenpress slots


def s13():
    conds = [(f'{a}+5 {g}', add([a], who=in_group(g))) for a in TOP10[:8] for g in ('CB', 'FB', 'DM/CM', 'AM/W', 'ST')]
    conds += [(f'{a}+5 {n} players', add([a], who=slots(COUNT_ORDER[:n]))) for a in ('Pace', 'Jumping Reach') for n in (1, 3, 6, 11)]
    return {'title': 'Study 13: attribute value by position', 'seeds': 40, 'pilot_seeds': 2, 'groups': [
        {'name': 'Gegenpress', 'style': 'Gegenpress', 'conds': conds}],
        'notes': 'Position groups are the starting XI by in-possession slot (Gegenpress: CB = DCR, DCL; FB = DR, DL; '
                 'DM/CM = DMR, DML; AM/W = AMR, AML; ST = STR, STL); substitutes are unchanged. Player counts follow '
                 + ', '.join(COUNT_ORDER) + '.'}


def s14():
    conds = [(f'{a}+5', add([a])) for a in TOP10]
    pairs = [('top v top', 'pl-top', 'pl-top'), ('middle v middle', 'pl-middle', 'pl-middle'), ('bottom v bottom', 'pl-bottom', 'pl-bottom'),
             ('top v bottom', 'pl-top', 'pl-bottom'), ('bottom v top', 'pl-bottom', 'pl-top')]
    return {'title': 'Study 14: team strength', 'seeds': 20, 'pilot_seeds': 2, 'groups': [
        {'name': n, 'style': 'Gegenpress', 'tier': a, 'opp_tier': b, 'conds': conds} for n, a, b in pairs]}


def s15():
    return {'title': 'Study 15: home advantage and morale', 'seeds': 40, 'pilot_seeds': 4, 'groups': [
        {'name': 'Home advantage', 'style': 'Gegenpress', 'panel': ['Gegenpress'], 'venues': (0,), 'templates': STADIUMS,
         'seeds': 1200, 'conds': []},
        {'name': 'Morale', 'style': 'Gegenpress', 'conds': [(f'morale={v}', profile('morale', v)) for v in (5, 10, 20)]}],
        'notes': 'Home advantage: identical squads and tactics (Gegenpress mirror) on twelve stadiums from the Premier '
                 'League to non-league, 100 seeds each; the home side is side 0. Morale: the tested side only (the '
                 'equal start is morale 15).'}


def natural_both(A, s, side):
    """Starters whose in- and out-of-possession positions use different ratings: both ratings natural (20)."""
    t = s['teams'][side]
    for i, ip, oop in starters(t):
        a, b = rating_index(ip), rating_index(oop)
        if a != b: t['players'][i]['attributes'][a] = t['players'][i]['attributes'][b] = 20


def cap(which, level=10):
    def edit(A, s, side):
        t = s['teams'][side]
        for i, ip, oop in starters(t):
            a, b = rating_index(ip), rating_index(oop)
            if a == b: continue
            for r in ((a,) if which == 'in' else (b,) if which == 'out' else (a, b)): t['players'][i]['attributes'][r] = level
    return edit


def s17():
    conds = [('in-possession position at 10', cap('in')), ('out-of-possession position at 10', cap('out')), ('both positions at 10', cap('both'))]
    return {'title': 'Study 17: roles out of possession', 'seeds': 50, 'pilot_seeds': 4, 'groups': [
        {'name': style, 'style': style, 'setup': natural_both, 'conds': conds} for style in ('Fluid Counter-Attack', 'Vertical Tiki-Taka')],
        'notes': 'Only starters whose in- and out-of-possession positions use different position ratings are changed '
                 '(Fluid Counter-Attack: MCL/DML, MCR/STR, AMR/MR, AML/ML; Vertical Tiki-Taka: MCL/ML, MCR/MR, AMC/DMR). '
                 'In every condition, including the unchanged one, those players start natural (20) in both positions.'}


def s20():
    one = [(f'CA={v}', profile('current_ability', v)) for v in (40, 80, 120, 160, 200)]
    one += [(f'CA={c}', profile('current_ability', c)) for c in (60, 180)]
    one += [(f'CA={c} {a}+5', both(profile('current_ability', c), add([a]))) for c in (60, 180) for a in ('Passing', 'Decisions')]
    two = [(f'CA={v} both sides', profile('current_ability', v, sides='both')) for v in (40, 80, 120, 160, 200)]
    return {'title': 'Study 20: Current Ability in the match', 'seeds': 40, 'pilot_seeds': 4, 'groups': [
        {'name': 'One side', 'style': 'Gegenpress', 'conds': one},
        {'name': 'Both sides', 'style': 'Gegenpress', 'conds': two}],
        'notes': 'Every attribute is fixed; only the Current Ability field changes (whole squad).'}


GK_ATTRS = ['Reflexes', 'Agility', 'Aerial Reach', 'Handling', 'Command Of Area', 'Communication', 'One On Ones',
            'Rushing Out', 'Kicking', 'Throwing', 'Tendency To Punch', 'First Touch', 'Passing', 'Positioning',
            'Concentration', 'Decisions', 'Anticipation', 'Jumping Reach']


def s21():
    return {'title': 'Study 21: goalkeepers', 'seeds': 50, 'pilot_seeds': 4, 'groups': [
        {'name': 'Gegenpress', 'style': 'Gegenpress', 'conds': [(f'{a}+5', add([a], who=in_group('GK'))) for a in GK_ATTRS]}],
        'notes': 'The starting goalkeeper only.'}


def cap_ratings(who='outfield', which='all', level=10):
    """Cap starters' position ratings: who = 'outfield', 'goalkeeper' or 'all'; which = 'all' 15 ratings or 'own' (the
    ratings of the positions the player takes in and out of possession)."""
    def edit(A, s, side):
        t = s['teams'][side]
        for i, ip, oop in starters(t):
            gk = rating_index(ip) == 0
            if (who == 'outfield' and gk) or (who == 'goalkeeper' and not gk): continue
            idx = range(15) if which == 'all' else {rating_index(ip), rating_index(oop)}
            a = t['players'][i]['attributes']
            for r in idx: a[r] = min(a[r], level)
    return edit


def s17b():
    conds = [('outfield starters: own positions at 10', cap_ratings('outfield', 'own')),
             ('outfield starters: every position at 10', cap_ratings('outfield', 'all')),
             ('goalkeeper: every position at 10', cap_ratings('goalkeeper', 'all')),
             ('all starters: every position at 10 (as Study 5)', cap_ratings('all', 'all'))]
    return {'title': 'Study 17b: where the cost of playing out of position comes from', 'seeds': 40, 'pilot_seeds': 2,
            'groups': [{'name': 'Gegenpress', 'style': 'Gegenpress', 'conds': conds}],
            'notes': 'Position ratings capped at 10 (never raised); the goalkeeper is the starter in the GK slot.'}


def s21b():
    gk = in_group('GK')
    keeping = ['Reflexes', 'Agility', 'Aerial Reach', 'Handling', 'Command Of Area', 'Communication', 'One On Ones',
               'Rushing Out', 'Kicking', 'Throwing']
    conds = [('every goalkeeping attribute+5', add(keeping, who=gk)),
             ('every goalkeeper attribute+5', add(GK_ATTRS, who=gk)),
             ('Reflexes+Agility+5', add(['Reflexes', 'Agility'], who=gk)),
             ('goalkeeper rating 15', cap_ratings('goalkeeper', 'own', 15)),
             ('goalkeeper rating 10', cap_ratings('goalkeeper', 'own', 10))]
    return {'title': 'Study 21b: the goalkeeper as a whole', 'seeds': 50, 'pilot_seeds': 2, 'groups': [
        {'name': 'Gegenpress', 'style': 'Gegenpress', 'conds': conds}],
        'notes': 'The starting goalkeeper only. Goalkeeping attributes: the ten goalkeeper-only ones; goalkeeper '
                 'attributes: those plus the eight general ones of Study 21. Rating: his goalkeeper position rating (natural 20).'}


STUDIES = {'09b': s09b, '10': s10, '11': s11, '12': s12, '13': s13, '14': s14, '15': s15, '17': s17, '17b': s17b, '20': s20, '21': s21, '21b': s21b}
