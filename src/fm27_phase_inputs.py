"""Explicit dual-phase input format; native team bits retain their original layout."""
import copy
PHASE_NAMES=('in_possession','out_of_possession')
# Installed instruction entries use general/subphase IDs, not a 0/1 boolean.
IP_SUBPHASES={0,1,2,3,8,9,11,12}
OOP_SUBPHASES={4,5,6,7,10}

def annotate(catalog):
    for group in catalog['team_instructions']:
        raw=group['phase']
        if raw not in IP_SUBPHASES|OOP_SUBPHASES:raise ValueError('unknown original instruction subphase')
        group['possession_phase']=int(raw in OOP_SUBPHASES)
    catalog['phase_input_schema']=4
    return catalog

def unpack(data,catalog):
    """Convert schema4 into the existing validated native-input adapter."""
    if not isinstance(data,dict)or data.get('schema')!=4:return data
    result=copy.deepcopy(data);result['schema']=3
    for team in result['teams']:
        if 'phases'in team or'instructions'in team:raise ValueError('The two-phase format cannot also contain old-style tactic fields')
        plans=team.pop('phase_plans')
        if not isinstance(plans,list)or len(plans)!=2:raise ValueError('Both in-possession and out-of-possession phase plans are required')
        team['instructions']={};team['phases']=[]
        for phase,plan in enumerate(plans):
            if plan['phase']!=PHASE_NAMES[phase]:raise ValueError('Phase name or order does not match')
            allowed={str(g['id'])for g in catalog['team_instructions']if g['possession_phase']==phase}
            values=plan['team_instructions']
            if not isinstance(values,dict)or set(values)!=allowed:raise ValueError('Team instruction missing or belongs to the other phase')
            team['instructions'].update(values);cells=plan['assignments']
            for cell in cells:
                provided=cell['instructions'];allowed_pi={str(g['id'])for g in catalog['player_instructions']if g['phase']==phase}
                if not isinstance(provided,dict)or set(provided)!=allowed_pi:raise ValueError('Player instruction missing or belongs to the other phase')
                cell['instructions']={str(g['id']):provided.get(str(g['id']),0)for g in catalog['player_instructions']}
            team['phases'].append(cells)
    return result

def pack(normalized,catalog):
    result=copy.deepcopy(normalized);result['schema']=4
    for team in result['teams']:
        instructions=team.pop('instructions');cells=team.pop('phases');team['phase_plans']=[]
        for phase in range(2):
            for cell in cells[phase]:cell['instructions']={str(g['id']):cell['instructions'][str(g['id'])]for g in catalog['player_instructions']if g['phase']==phase}
            team['phase_plans'].append({'phase':PHASE_NAMES[phase],'team_instructions':{str(g['id']):instructions[str(g['id'])]for g in catalog['team_instructions']if g['possession_phase']==phase},'assignments':cells[phase]})
    return result
