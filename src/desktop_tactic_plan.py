"""Apply a tactic plan parsed by the game's own FMF parser to a scenario team, and sign it so role and instruction
combinations the game itself produced are kept even where the editor's stricter rules would refuse them."""
import desktop_source_plans


def apply(app, team, plan):
    bits = int.from_bytes(bytes.fromhex(plan['team_bits']), 'little')
    team.update(mentality=plan['mentality'], native_extra_team_bits=str(bits & ~app.TEAM_KNOWN_MASK))
    for g in app.GROUPS.values():
        values = [o['id'] for o in g['options'] if o['native_bit'] and bits >> o['native_bit'] & 1]
        if len(values) > 1:
            raise ValueError('Source tactic has same-group instructions that cannot be represented without loss')
        team['instructions'][str(g['id'])] = values[0] if values else next(o['id'] for o in g['options'] if not o['native_bit'])
    mapping = [i if v == 255 else v for i, v in enumerate(plan['mapping'])]
    if sorted(mapping) != list(range(11)):
        raise ValueError('Invalid two-phase mapping in the source tactic')
    known = sum(1 << v for v in {o['id'] for g in app.PIS.values() for o in g['options'] if o['id']})
    for phase in range(2):
        for i in range(11):
            r = plan['phases'][phase][mapping[i] if phase else i]
            pos = next((p['id'] for p in app.POSITIONS.values() if p['mask'] == r['position']), None)
            flags = int(r['role_flags'])
            role = next((v['id'] for v in app.ROLES.values() if v['phase'] == phase and int(v['flags']) == flags & app.ROLE_MASK), None)
            if pos is None or role is None:
                raise ValueError('Source tactic contains a position or role that is not mapped yet')
            pi = int(r['pi_flags'])
            if pi & ~known:
                raise ValueError('Source tactic contains a player instruction not mapped yet; not dropped silently')
            if any(sum(bool(pi >> o['id'] & 1) for o in g['options'] if o['id']) > 1 for g in app.PIS.values()):
                raise ValueError('Source tactic has same-group player instructions that cannot be represented without loss')
            team['phases'][phase][i] = {'position': pos, 'role': role, 'duty': str(flags & ~app.ROLE_MASK),
                'instructions': {str(g['id']): next((o['id'] for o in g['options'] if o['id'] and pi >> o['id'] & 1), 0) for g in app.PIS.values()},
                'target_player': r['target_player'], 'target_position': r['target_position']}
    desktop_source_plans.sign(app, team)
