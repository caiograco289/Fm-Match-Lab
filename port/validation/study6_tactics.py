"""Study 6 (docs/studies): tactics on the real saved matches, at the squad's own familiarity and at low familiarity.

The team plays each tactic in the 10 matches of Study 1 (seeds 1-20, 200 pairs per tactic and level); the opponent
keeps its saved tactic and players. Tactics: one installed FM27 preset per style (exported by the host from the
game's own data) and the user's .fmf files, imported through the game's own parser. Players keep their saved lineup
slots; roles, duties, instructions and mentality come from the tactic.

Familiarity (Study 3): "own" leaves the effectiveness record as the game builds it; "low" holds the eight tactical
areas (training and match-exposure bytes) at LOW for every player of the team. The baseline is the saved tactic.

  python port/validation/study6_tactics.py build OUT STUDY1_DIR PRESETS.jsonl FMF_DIR   # app environment
  FM27_STUDY_HOST=... python port/validation/overnight.py run OUT 6
  python port/validation/study6_tactics.py analyse OUT
"""
import base64, copy, glob, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src')); sys.path.insert(0, str(Path(__file__).resolve().parent))
SEEDS = 20
LOW = 20
AREAS = [o + k for o in range(1, 25, 3) for k in (0, 1, 2)]
TEAM_KEYS = ('phases', 'instructions', 'mentality', 'native_extra_team_bits', 'native_source_plan', 'tactic_name')


def low_fields(side):
    return ','.join(f'{side}:{o}={LOW}' for o in AREAS)


def tactics(app, presets, fmf_dir, base, side):
    """name -> team fields, each parsed once (presets through the plan applier, .fmf through the game's parser)."""
    result = {}
    rows = [json.loads(l) for l in open(presets)]
    for t in (r for r in rows if r.get('event') == 'installed_tactic_preset'):
        name = 'FM preset ' + bytes.fromhex(t['name_utf8_hex']).decode().replace('Custom ', '')
        if name in result: continue
        s = copy.deepcopy(base)
        try:
            app.desktop_tactic_plan.apply(app, s['teams'][side], t); s['teams'][side]['tactic_name'] = name
            s = app.validate_scenario(s)
        except Exception as e:
            print('skip', name, str(e)[:100]); continue
        result[name] = {k: copy.deepcopy(s['teams'][side].get(k)) for k in TEAM_KEYS}
    for f in sorted(glob.glob(str(Path(fmf_dir) / '*.fmf'))):
        try:
            s = app.import_fmf({'side': side, 'scenario': copy.deepcopy(base), 'file_base64': base64.b64encode(open(f, 'rb').read()).decode()})['scenario']
        except Exception as e:
            print('skip', Path(f).stem, str(e)[:100]); continue
        result[Path(f).stem] = {k: copy.deepcopy(s['teams'][side].get(k)) for k in TEAM_KEYS}
    return result


def build(out, study1, presets, fmf_dir):
    import fm27_tactics_server as app
    out.mkdir(parents=True, exist_ok=True); bins = out / 'bins'; bins.mkdir(exist_ok=True)
    meta = json.load(open(study1 / 'meta.json'))
    naturals = [j for j in json.load(open(study1 / 'jobs.json')) if j[1].endswith('|natural')]
    jobs, skipped, plans = [], {}, None
    for j in naturals:
        match = j[1].split('|')[0]; side = meta['sides'][match]
        base = app.validate_scenario(app.SAVED_MATCHES.open(j[2]).default)
        if plans is None: plans = tactics(app, presets, fmf_dir, base, side)
        for name, fields in [('saved tactic', None)] + list(plans.items()):
            s = copy.deepcopy(base)
            try:
                if fields: s['teams'][side].update(copy.deepcopy(fields))
                s = app.validate_scenario(s); blob = app.encode_scenario(s)
            except Exception as e:
                skipped.setdefault(name, []).append(f'{match}: {str(e)[:100]}'); continue
            f = bins / f'{len(jobs)}.bin'; f.write_bytes(blob)
            jobs.append(['T', f'{match}|{name}|own', j[2], str(f), {}, SEEDS])
            jobs.append(['T', f'{match}|{name}|low', j[2], str(f), {'FM27_MAC_EXEC_FIELDS': low_fields(side)}, SEEDS])
    (out / 'jobs.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps(meta | {'skipped': skipped, 'tactics': sorted(plans), 'low': LOW, 'seeds': SEEDS}))
    print(len(jobs), 'jobs,', sum(j[5] for j in jobs), 'matches,', len(plans), 'tactics; skipped:', {k: len(v) for k, v in skipped.items()})


def own(r, s):
    o = 1 - s
    return {'pts': 3 if r['score'][s] > r['score'][o] else 1 if r['score'][s] == r['score'][o] else 0,
            'GF': r['score'][s], 'GA': r['score'][o], 'xGD': r['xg'][s] - r['xg'][o], 'xGF': r['xg'][s], 'xGA': r['xg'][o]}


def stats(v):
    n = len(v); m = sum(v) / n; sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1)) if n > 1 else 0
    return m, (m / (sd / math.sqrt(n)) if sd else 0.0)


def analyse(out):
    meta = json.load(open(out / 'meta.json')); data = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); match, name, level = r['cond'].split('|')
        data.setdefault((name, level), {})[(match, r['seed'])] = own(r, meta['sides'][match])
    result = {}
    for level in ('own', 'low'):
        base = data[('saved tactic', 'own')]
        for (name, lv), rows in data.items():
            if lv != level: continue
            keys = [k for k in rows if k in base]
            result[f'{name}|{level}'] = {m: stats([rows[k][m] - base[k][m] for k in keys]) for m in ('pts', 'xGD', 'GF', 'GA', 'xGF', 'xGA')} | \
                {'n': len(keys), 'ppg': sum(rows[k]['pts'] for k in keys) / len(keys)}
    names = sorted({n for n, _ in data}, key=lambda n: -result.get(f'{n}|own', {'xGD': (0, 0)})['xGD'][0])
    print(f"{'tactic':44} {'own ppg':>8} {'own dxGD':>9} {'low ppg':>8} {'low dxGD':>9}")
    for n in names:
        a, b = result.get(f'{n}|own'), result.get(f'{n}|low')
        if a and b: print(f"{n[:44]:44} {a['ppg']:8.2f} {a['xGD'][0]:+9.3f} {b['ppg']:8.2f} {b['xGD'][0]:+9.3f}")
    json.dump(result, open(out / 'effects.json', 'w'), indent=1)


if __name__ == '__main__':
    mode, out = sys.argv[1], Path(sys.argv[2])
    build(out, Path(sys.argv[3]), sys.argv[4], sys.argv[5]) if mode == 'build' else analyse(out)
