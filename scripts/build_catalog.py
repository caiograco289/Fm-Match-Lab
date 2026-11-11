"""Build the tactic catalogue from the user's own FM27 install (no upstream release needed).

Sources, all read from the installed game without changing it:
  - Unity static data (StreamingAssets/aa/StandaloneOSX/ui-staticdataentries_assets_all.bundle, read with UnityPy):
    team instructions, player instructions, roles and their default player instructions, formations, mentalities,
    tactical tweaks;
  - the IL2CPP metadata (global-metadata.dat, read as data by port/map/il2cpp_enums.py): role engine bits, duty bits;
  - the game's own engine functions, through the host: team-instruction engine bits (--option-bits), role masks per
    position and player-instruction policies (--policy-audit).
Small interface constants (position masks, mentality ids, the attribute layout) are this project's own
metadata in port/map/catalog_constants.json.

  .venv/bin/python scripts/build_catalog.py [--out build/catalog.json] [--compare private/catalog.json]

Needs Steam running and FM27 closed (the host loads the engine), and UnityPy (pip install UnityPy) for this step only.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'port/map')); sys.path.insert(0, str(ROOT / 'src'))
HOST = ROOT / 'private/engine/fm27_native/fm27_mac_host'
CONSTANTS = ROOT / 'port/map/catalog_constants.json'


def game_paths():
    import desktop_platform
    root = Path(desktop_platform.default_game_root() if hasattr(desktop_platform, 'default_game_root') else '')
    app = next((p for p in [root, *root.parents] if p.name == 'fm.app'), None)
    if app is None:
        app = Path.home() / 'Library/Application Support/Steam/steamapps/common/Football Manager 27/fm.app'
    data = app / 'Contents/Resources/Data'
    return data / 'StreamingAssets/aa/StandaloneOSX/ui-staticdataentries_assets_all.bundle', data / 'il2cpp_data/Metadata/global-metadata.dat'


def unity_objects(bundle):
    try: import UnityPy
    except ImportError: raise SystemExit('UnityPy is needed for this step: .venv/bin/pip install UnityPy')
    out = {}
    for o in UnityPy.load(str(bundle)).objects:
        if o.type.name != 'MonoBehaviour': continue
        try: t = o.read_typetree()
        except Exception: continue
        for k in ('m_GameObject', 'm_Enabled', 'm_Script'): t.pop(k, None)
        out.setdefault(t.get('m_Name') or str(o.path_id), t)
    return out


def host(*args):
    with tempfile.TemporaryDirectory() as folder:
        log = Path(folder) / 'out.jsonl'
        code = subprocess.run([str(HOST), *args, '--output', str(log)], capture_output=True).returncode
        if code: raise SystemExit(f'host {args[0]} failed (exit {code}); is Steam running and FM27 closed?')
        return [json.loads(line) for line in log.read_text(encoding='utf8').splitlines() if line.startswith('{')]


def option_bits(ids):
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
        f.write('\n'.join(map(str, ids)) + '\n'); path = f.name
    try: return {e['value']: e['bit'] for e in host('--option-bits', path) if e.get('event') == 'option_bit'}
    finally: Path(path).unlink()


def build():
    import il2cpp_enums
    bundle, metadata = game_paths()
    const = json.loads(CONSTANTS.read_text(encoding='utf8'))
    u = unity_objects(bundle)
    _, enums = il2cpp_enums.enums(metadata)
    ip_enum = next(m for m in enums.values() if 'PlaymakingWinger' in m)
    op_enum = next(m for m in enums.values() if 'OPGoalkeeper' in m)

    # team instructions: Unity entries plus the one group the static data lacks; bits from the game's resolver
    groups = sorted((t for t in u.values() if 'm_instructionID' in t), key=lambda t: t['m_instructionID'])
    extra = const['team_instruction_groups_not_in_static_data']
    ids = [o['m_optionID'] for g in groups for o in g['m_instructionOptionEntries']] + [o['id'] for g in extra for o in g['options']]
    bits = option_bits(ids)
    phase_of = {}
    for row in next(t for t in u.values() if 'm_phasesAndTeamInstructions' in t)['m_phasesAndTeamInstructions']:
        for gid in row['TeamInstructionsForPhase']: phase_of.setdefault(gid, row['TeamInstructionPhaseID'])
    # the UI's sub-phases 0-3 are in possession, 4-7 out of possession; a group missing from that table (Supporting Runs,
    # secondary) takes the side of a group with the same phase id
    side = {gid: int(p >= 4) for gid, p in phase_of.items()}
    by_phase = {g['m_phaseID']: side[g['m_instructionID']] for g in groups if g['m_instructionID'] in side}
    possession = lambda g: side.get(g['m_instructionID'], by_phase.get(g['m_phaseID']))
    team = []
    for g in groups:
        team.append({'id': g['m_instructionID'], 'name': g['m_Name'], 'phase': g['m_phaseID'],
                     'possession_phase': possession(g),
                     'options': [{'id': o['m_optionID'], 'native_bit': bits[o['m_optionID']],
                                  'translation_id': o['m_nameTranslationID']['GameID'],
                                  'source_gif': o.get('m_pitchGIF') or o.get('m_pitchImage') or ''}
                                 for o in g['m_instructionOptionEntries']]})
    for g in extra:
        team.append({**{k: v for k, v in g.items() if k != 'options'},
                     'options': [{**o, 'native_bit': bits[o['id']]} for o in g['options']]})

    # roles: Unity order and defaults, engine bits from the managed enums
    roles = []
    for t in (t for t in u.values() if 'm_roleID' in t):
        rid = t['m_roleID']; op = rid.startswith('OP')
        value = op_enum.get(rid) if op else ip_enum.get(rid)
        if value is None: raise SystemExit(f'no engine bit for role {rid}')
        roles.append({'id': rid, 'phase': 1 if op else 0, 'flags': str(value), 'defaults': t.get('m_rolePlayerInstructions', [])})

    # player instructions: Unity groups; phase from the game's policy functions (below)
    pig = next(t for t in u.values() if 'm_playerInstructionGroups' in t)['m_playerInstructionGroups']
    player = [{'id': g['m_groupID'], 'options': [{'id': o['m_instructionID'], 'source_gif': o.get('m_pitchGIF', '')}
                                                  for o in g['m_playerInstructionOptionEntries']]} for g in pig]
    # the game's own role-mask and player-instruction policy functions (host --policy-audit)
    audit = host('--policy-audit')
    pos_name = {p['mask']: p['id'] for p in const['positions']}
    role_name = {(r['phase'], int(r['flags'])): r['id'] for r in roles}
    eligibility = {}
    for e in (e for e in audit if e.get('event') == 'role_policy'):
        mask = int(e['mask'])
        names = [r['id'] for r in roles if r['phase'] == e['phase'] and int(r['flags']) & mask]
        if e['cb'] not in (0, 3) or e['dm'] not in (0, 1): continue   # the contexts the app distinguishes
        eligibility.setdefault(f"{e['cb']}:{e['dm']}", {}).setdefault(pos_name[e['position']], [[], []])[e['phase']] = names
    editable = {0: 0, 1: 0}
    for e in (e for e in audit if e.get('event') == 'pi_policy'): editable[e['phase']] |= int(e['editable'])
    for g in player:
        ids = [o['id'] for o in g['options'] if o['id']]
        on = [ph for ph in (0, 1) if any(editable[ph] >> i & 1 for i in ids)]
        if len(on) != 1: raise SystemExit(f'player instruction group {g["id"]}: phase not determined ({on})')
        g['phase'] = on[0]
    in_phase = {ph: {o['id'] for g in player if g['phase'] == ph for o in g['options'] if o['id']} for ph in (0, 1)}
    policies = {}
    for e in (e for e in audit if e.get('event') == 'pi_policy'):
        key = f"{e['phase']}:{pos_name[e['position']]}:{role_name[(e['phase'], int(e['role']))]}:{e['duty']}"
        statuses = ''.join(c if i == 0 or i in in_phase[e['phase']] else '1' for i, c in enumerate(e['statuses']))
        policies.setdefault(key, {})[f"{e['version']:08x}"] = statuses
    return {'schema_version': 1, 'source': 'user install (scripts/build_catalog.py)', 'team_instructions': team,
            'role_eligibility_context': eligibility, 'pi_policies': policies,
            'policy_versions': sorted({v for p in policies.values() for v in p}),
            'roles': roles, 'player_instructions': player, 'positions': const['positions'],
            'mentalities': const['mentalities'], 'attributes': const['attributes'],
            'duties': ['0'] + [str(v) for k, v in op_enum.items() if k.endswith('Duty')],
            'team_conflicting_bits': const['team_conflicting_bits'], 'phase_input_schema': const['phase_input_schema'],
            'raw_roles': [t for t in u.values() if 'm_roleID' in t],
            'raw_tactical_tweaks': [t for t in u.values() if 'm_tweakID' in t],
            'raw_player_instructions': next(t for t in u.values() if 'm_playerInstructionGroups' in t),
            'raw_formations': next(t for t in u.values() if 'm_formationOptionEntries' in t),
            'raw_mentalities': next(t for t in u.values() if 'm_mentalityOptionEntries' in t)}


def compare(new, old):
    """Every field the app reads, against upstream's catalogue. Returns a list of differences."""
    diffs = []
    def check(label, a, b):
        if a != b: diffs.append(f'{label}: generated {str(a)[:160]} != upstream {str(b)[:160]}')
    ng = {g['id']: g for g in new['team_instructions']}
    for g in old['team_instructions']:
        n = ng.get(g['id'])
        if not n: diffs.append(f'team instruction {g["id"]} {g["name"]} missing'); continue
        check(f'TI {g["id"]} name', n['name'], g['name']); check(f'TI {g["id"]} phase', n['phase'], g['phase'])
        check(f'TI {g["id"]} possession_phase', n.get('possession_phase'), g.get('possession_phase'))
        check(f'TI {g["id"]} options', [(o['id'], o['native_bit']) for o in n['options']], [(o['id'], o['native_bit']) for o in g['options']])
    check('team instruction groups', sorted(ng), sorted(g['id'] for g in old['team_instructions']))
    nr = {r['id']: r for r in new['roles']}
    for r in old['roles']:
        n = nr.get(r['id'])
        if not n: diffs.append(f'role {r["id"]} missing'); continue
        for k in ('phase', 'flags', 'defaults'): check(f'role {r["id"]} {k}', n[k], r[k])
    check('role order', [r['id'] for r in new['roles']], [r['id'] for r in old['roles']])
    np_ = {g['id']: g for g in new['player_instructions']}
    for g in old['player_instructions']:
        check(f'PI group {g["id"]} options', [o['id'] for o in np_.get(g['id'], {}).get('options', [])], [o['id'] for o in g['options']])
        if 'phase' in np_.get(g['id'], {}): check(f'PI group {g["id"]} phase', np_[g['id']]['phase'], g['phase'])
    for k in ('positions', 'duties', 'team_conflicting_bits', 'phase_input_schema'): check(k, new[k], old[k])
    for ctx, table in old['role_eligibility_context'].items():
        for pos, lists in table.items():
            got = new['role_eligibility_context'].get(ctx, {}).get(pos)
            if got is None: diffs.append(f'eligibility {ctx} {pos} missing'); continue
            check(f'eligibility {ctx} {pos} (as sets)', [sorted(x) for x in got], [sorted(x) for x in lists])
            if [sorted(x) for x in got] == [sorted(x) for x in lists] and got != lists: diffs.append(f'eligibility {ctx} {pos}: same roles, different order')
    for key, versions in old['pi_policies'].items():
        for v, statuses in versions.items():
            check(f'policy {key} {v}', new['pi_policies'].get(key, {}).get(v), statuses)
    check('mentality ids', [m['id'] for m in new['mentalities']], [m['id'] for m in old['mentalities']])
    check('attributes', [(a['id'], a['name'], a.get('position')) for a in new['attributes']], [(a['id'], a['name'], a.get('position')) for a in old['attributes']])
    return diffs


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out', default=str(ROOT / 'build/catalog.json'))
    p.add_argument('--compare', help="upstream's catalog.json to check against")
    p.add_argument('--setpieces', help='also write the set-piece option catalogue here (fm27_research/setpiece_enum_catalog.json)')
    a = p.parse_args()
    catalog = build()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(catalog, ensure_ascii=False), encoding='utf8')
    print('written', a.out)
    if a.setpieces:
        const = json.loads(CONSTANTS.read_text(encoding='utf8'))['setpieces']
        enums = {k: [{**x, 'label': x['english']} for x in v] if isinstance(v, list) else v for k, v in const.items()}
        Path(a.setpieces).parent.mkdir(parents=True, exist_ok=True)
        Path(a.setpieces).write_text(json.dumps(enums, ensure_ascii=False), encoding='utf8'); print('written', a.setpieces)
    if a.compare:
        diffs = compare(catalog, json.loads(Path(a.compare).read_text(encoding='utf8')))
        print(f'{len(diffs)} differences'); print('\n'.join(diffs[:60]))


if __name__ == '__main__':
    main()
