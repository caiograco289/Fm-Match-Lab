"""English labels for the tactic catalogue, keyed by the game's ids and names (works on any catalogue source).

Applied in memory when the server loads the catalog; the private file is not changed. Where the catalog already
carries English (role ids, attribute names, team-instruction source names, the set-piece catalog's "english" field)
the label is derived from it; the rest is translated here.
"""
import re

FIXES = {'No Nonsense': 'No-Nonsense', 'Ball Playing': 'Ball-Playing', 'Box To Box': 'Box-to-Box', 'Deep Lying': 'Deep-Lying',
         'Centre Back': 'Centre-Back', 'Full Back': 'Full-Back', 'Wing Back': 'Wing-Back', 'Half Back': 'Half-Back',
         'Off The Ball': 'Off the Ball', 'Command Of Area': 'Command of Area', 'One On Ones': 'One on Ones',
         'Tendency To Punch': 'Tendency to Punch'}


def humanize(name):
    text = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', name)
    for a, b in FIXES.items(): text = text.replace(a, b)
    return text


POSITION_ATTRIBUTES = {'GK': 'Goalkeeper', 'UnusedSweeper': 'Sweeper (unused)', 'DL': 'Defender (L)', 'DC': 'Defender (C)',
                       'DR': 'Defender (R)', 'DM': 'Defensive Midfielder', 'ML': 'Midfielder (L)', 'MC': 'Midfielder (C)',
                       'MR': 'Midfielder (R)', 'AML': 'Attacking Midfielder (L)', 'AMC': 'Attacking Midfielder (C)',
                       'AMR': 'Attacking Midfielder (R)', 'ST': 'Striker', 'WBL': 'Wing-Back (L)', 'WBR': 'Wing-Back (R)'}

TEAM_GROUPS = {'PassingDirectness': 'Passing directness', 'AttackingTransition': 'When possession is won', 'AttackingWidth': 'Attacking width',
               'CreativeFreedom': 'Creative freedom', 'PlayForSetPieces': 'Set pieces', 'TimeWasting': 'Time wasting',
               'LineOfEngagement': 'Line of engagement', 'DefensiveLine': 'Defensive line', 'TriggerPress': 'Pressing intensity',
               'DefensiveTransition': 'When possession is lost', 'Tackling': 'Tackling', 'DefensiveLineBehaviour': 'Defensive line behaviour',
               'GoalkeeperDistributionTarget': 'Goalkeeper distribution target', 'GoalkeeperDistributionSpeed': 'Goalkeeper distribution speed',
               'Patience': 'Final third', 'Dribbling': 'Dribbling', 'PassReception': 'Pass reception', 'Tempo': 'Tempo',
               'CrossEngagement': 'Crossing engagement', 'PreventShortGKDistribution': 'Prevent short GK distribution',
               'BuildUpStrategy': 'Build-up', 'PressingTrap': 'Pressing trap', 'Crossing': 'Crossing', 'ShotsFromDistance': 'Shots from distance',
               'SupportingRuns': 'Underlaps', 'GoalKicks': 'Goal kicks', 'ProgressThrough': 'Progress through',
               'SupportingRunsSecondary': 'Overlaps', 'GoalkeeperUpForAttackingSetPieces': 'Goalkeeper up for attacking set pieces'}

# Team-instruction option labels, by the game's option id (one line per group)
TEAM_OPTIONS = {
    1985571685: 'Much Shorter', 1146434657: 'Shorter', 1483944022: 'Standard', 2019653698: 'More Direct', 1867543624: 'Much More Direct',   # PassingDirectness
    1450726497: 'Regroup', 846284410: 'Standard', 1734436950: 'Counter Attack',   # AttackingTransition
    1716541542: 'Much narrower', 1111652208: 'Narrower', 1951095402: 'Standard', 1244744824: 'Wider', 1347573861: 'Much wider',   # AttackingWidth
    1752052821: 'More disciplined', 1934574368: 'Standard', 1297429358: 'More expressive',   # CreativeFreedom
    1869829494: 'Keep ball in play', 896626297: 'Play for set pieces',   # PlayForSetPieces
    1315850041: 'Never', 1329030726: 'Sometimes', 1733973351: 'Frequently',   # TimeWasting
    927550517: 'Low block', 1196979288: 'Mid block', 2033537859: 'High press',   # LineOfEngagement
    2003456321: 'Much deeper', 807423041: 'Deeper', 894978671: 'Standard', 1329018200: 'Higher', 1735747406: 'Much higher',   # DefensiveLine
    1500664391: 'Much less often', 1985168495: 'Less often', 1313689463: 'Standard', 2000905329: 'More often', 1450268022: 'Much more often',   # TriggerPress
    2001753209: 'Regroup', 1396068403: 'Standard', 928473934: 'Counter-Press',   # DefensiveTransition
    896480825: 'Stay on feet', 1297249398: 'Standard', 1498428227: 'Get stuck in',   # Tackling
    825575765: 'Step up more', 1397124971: 'Balanced', 1466132292: 'Drop off more',   # DefensiveLineBehaviour
    1398290509: 'Balanced', 1097811032: 'Centre-backs', 1732531317: 'Full-backs', 2001361485: 'Flanks', 543316536: 'Playmaker', 1362654530: 'Target forward', 1664119088: 'Over the opposition defence',   # GoalkeeperDistributionTarget
    1936095309: 'Slow pace down', 842232368: 'Balanced', 1380137303: 'Distribute quickly',   # GoalkeeperDistributionSpeed
    844190326: 'Hit Early Crosses', 1364668513: 'Standard', 1196903216: 'Work Into The Box',   # Patience
    946684999: 'Discourage', 1480870768: 'Standard', 1313559094: 'Encourage',   # Dribbling
    1817268034: 'Pass Into Feet', 1196126273: 'Standard', 1987666283: 'Pass Into Space',   # PassReception
    1498756423: 'Much Lower', 1311996258: 'Lower', 1496610426: 'Standard', 1345339954: 'Higher', 543778113: 'Much Higher',   # Tempo
    1684615797: 'Stop crosses', 1097682775: 'Standard', 1280010857: 'Invite crosses',   # CrossEngagement
    1667524405: 'No', 1748587383: 'Yes',   # PreventShortGKDistribution
    1365857100: 'Play Through Press', 1732331848: 'Standard', 1702379875: 'Bypass Press',   # BuildUpStrategy
    1870092139: 'Show inside', 844782149: 'Standard', 1381658469: 'Show outside',   # PressingTrap
    1817334343: 'Balanced', 1649964405: 'Floated Crosses', 1850439286: 'Whipped Crosses', 542589235: 'Low Crosses',   # Crossing
    2021157752: 'Fewer shots from distance', 1951290700: 'Standard', 1799907952: 'More shots from distance',   # ShotsFromDistance
    1128871265: 'Standard', 1246451814: 'Left underlap', 894725200: 'Right underlap', 1848850767: 'Both underlap',   # SupportingRuns
    1730167140: 'Short', 1248478788: 'Mixed', 1749839698: 'Long',   # GoalKicks
    1800754547: 'Balanced', 1465200750: 'Centre', 2001548153: 'Left', 1299723626: 'Right', 1849981002: 'Both Flanks',   # ProgressThrough
    1700947790: 'Standard', 1496789296: 'Left overlap', 1484157235: 'Right overlap', 809924212: 'Both overlap',   # SupportingRunsSecondary
    1466265977: 'Stay back', 1968654134: 'Go up',   # GoalkeeperUpForAttackingSetPieces
}

MENTALITIES = {1: 'Very defensive', 2: 'Defensive', 3: 'Cautious', 4: 'Balanced', 5: 'Positive', 6: 'Attacking', 7: 'Very attacking'}

PLAYER_GROUPS = {0: 'Attacking position', 1: 'Run with ball', 2: 'Dribbling', 3: 'Forward runs', 4: 'Movement', 5: 'Hold up ball',
                 6: 'Shooting', 7: 'Passing distance', 8: 'Passing risk', 9: 'Cross target', 10: 'Cross from', 11: 'Pressing',
                 12: 'Marking', 13: 'Tackling', 14: 'Specific marking', 15: 'Box attack channel', 16: 'Box attack depth'}
PLAYER_OPTIONS = {25: 'Stay wider', 26: 'Sit narrower', 27: 'Hug line / roam half-spaces', 15: 'Run down flank', 16: 'Cut inside',
                  13: 'Dribble more', 14: 'Dribble less', 22: 'Get further forward', 23: 'Hold position', 24: 'Roam from position',
                  18: 'Shoot more often', 19: 'Shoot less often', 17: 'Yes', 1: 'Shorter passing', 2: 'More direct passing',
                  3: 'Take more risks', 4: 'Take fewer risks', 10: 'Far post', 11: 'Centre', 9: 'Near post', 12: 'Target forward',
                  7: 'Cross early', 8: 'Cross from byline', 29: 'Press more', 30: 'Press less', 33: 'Mark tighter',
                  31: 'Get stuck in', 32: 'Stay on feet', 34: 'Mark specific player', 35: 'Mark specific position',
                  36: 'Centre', 37: 'Left', 38: 'Right', 39: 'Near post', 40: 'Far post', 41: 'Attack the front zone', 42: 'Arrive late'}
PLAYER_ZERO = {5: 'No', 4: 'Hold zone', 9: 'Mixed', 14: 'None'}   # option 0 per group where it is not "Standard"


def translate(catalog):
    for a in catalog.get('attributes', []):
        a['label'] = POSITION_ATTRIBUTES.get(a['name'], a['name']) if a.get('position') else humanize(a['name'])
    for r in catalog.get('roles', []):
        base = humanize(r['id'][2:] if r['id'].startswith('OP') else r['id'])
        r['label'] = base
    for g in catalog.get('team_instructions', []):
        g['label'] = TEAM_GROUPS.get(g.get('name'), g.get('name') or g.get('label'))
        for o in g['options']:
            o['label'] = TEAM_OPTIONS.get(o['id'], o.get('label') or str(o['id']))
    for m in catalog.get('mentalities', []):
        m['label'] = MENTALITIES.get(m['id'], m.get('label') or str(m['id']))
    for g in catalog.get('player_instructions', []):
        g['label'] = PLAYER_GROUPS.get(g['id'], g.get('label') or str(g['id']))
        for o in g['options']:
            o['label'] = PLAYER_ZERO.get(g['id'], 'Standard') if o['id'] == 0 else PLAYER_OPTIONS.get(o['id'], o.get('label') or str(o['id']))
    return catalog


def translate_setpieces(enums):
    """The set-piece enum catalog carries English names next to the labels."""
    def walk(o):
        if isinstance(o, dict):
            if 'english' in o and 'label' in o: o['label'] = o['english']
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(enums)
    return enums
