"""Tactic league on the Mac port: every tactic against one benchmark, home and away, on identical squads.

Squads: every player 12 in every non-position attribute (raw 60), natural (20) in every position, 180 cm / 70 kg, so
only the tactic differs. Each tactic plays the benchmark at home on seeds 1..N and away on seeds 1..N (common random
numbers across tactics). Tactics: the user's .fmf files (imported through the app, i.e. the game's own parser) and one
installed preset per style (from the host's preset export). Results go to <out>/league.json.

Run with the app server up (scripts/run.py) and the env of the server (FM27_ENGINE_ROOT, FM27_DESKTOP_DATA=data, ...):
  python port/validation/tactic_league.py OUT_DIR PRESETS.jsonl DEFAULTS.json N [FMF ...]
"""
import base64, copy, json, sys, time, urllib.request
from pathlib import Path
sys.path.insert(0, 'build/source')
import fm27_tactics_server as app

B = 'http://127.0.0.1:18765'


def api(path, data=None):
    request = urllib.request.Request(B + path, data=None if data is None else json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
    try:
        return json.loads(urllib.request.urlopen(request, timeout=300).read())
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode()[:300])


def level(team):
    for p in team['players']:
        for i in range(15): p['attributes'][i] = 20
        for i in range(15, 69): p['attributes'][i] = 60
        p['native_profile'].update(height_cm=180, weight_kg=70)


def run(scenario, seeds, name):
    job = api('/api/run', {'scenario': scenario, 'seeds': seeds, 'workers': 3, 'event_details': False, 'name': name})
    while True:
        time.sleep(3)
        job = api(f"/api/jobs/{job['id']}")
        if job['status'] not in ('queued', 'running'): break
    if job['status'] != 'complete' or job['failures']: raise ValueError(f"{name}: {job['status']} failures={len(job['failures'])}")
    return [{'seed': r['seed'], 'score': r['result']['score'], 'xg': [t['xg'] for t in r['statistics']['teams']],
             'possession': [t['possession'] for t in r['statistics']['teams']], 'shots': [t['shots'] for t in r['statistics']['teams']]} for r in job['runs']]


def main():
    out, presets, defaults, n = Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4])
    out.mkdir(parents=True, exist_ok=True)
    base = json.load(open(defaults)); base = base.get('scenario', base)
    for team in base['teams']: level(team)
    rows = [json.loads(l) for l in open(presets)]
    templates = [r for r in rows if r['event'] == 'installed_tactic_preset']
    for t in templates: t['name'] = bytes.fromhex(t['name_utf8_hex']).decode()
    bench = templates[16]   # Custom Gegenpress 433-433
    tactics = []
    seen = set()
    for t in templates:   # first installed template of each style
        style = t['name'].replace('Custom ', '')
        if style in seen: continue
        seen.add(style); tactics.append(('preset', 'FM preset: ' + style, t))
    for path in sys.argv[5:]:
        tactics.append(('fmf', Path(path).stem, path))
    seeds = list(range(1, n + 1))
    results = json.load(open(out / 'league.json')) if (out / 'league.json').exists() else {}
    for kind, name, source in tactics:
        if name in results: continue
        sides = []
        try:
            for side in (0, 1):
                s = copy.deepcopy(base)
                app.desktop_tactic_plan.apply(app, s['teams'][1 - side], bench); s['teams'][1 - side]['tactic_name'] = 'Gegenpress 433-433'
                if kind == 'preset':
                    app.desktop_tactic_plan.apply(app, s['teams'][side], source); s['teams'][side]['tactic_name'] = name
                    s = app.validate_scenario(s)
                else:
                    s = app.validate_scenario(s)
                    s = api('/api/import-fmf', {'side': side, 'scenario': s, 'file_base64': base64.b64encode(open(source, 'rb').read()).decode()})['scenario']
                sides.append(run(s, seeds, f'league {name} {"home" if side == 0 else "away"}'))
        except (ValueError, KeyError) as e:
            results[name] = {'kind': kind, 'error': str(e)}
            print(name, 'ERROR', str(e)[:200], flush=True)
        else:
            results[name] = {'kind': kind, 'home': sides[0], 'away': sides[1]}
            w = sum(r['score'][0] > r['score'][1] for r in sides[0]) + sum(r['score'][1] > r['score'][0] for r in sides[1])
            print(name, f'win {w / (2 * n):.3f}', flush=True)
        (out / 'league.json').write_text(json.dumps(results))


if __name__ == '__main__':
    main()
