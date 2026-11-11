"""Tactical-effectiveness dose-response on the Mac port (scenario experimental_execution, kind 61).

Mirror match: identical levelled squads (as in tactic_league.py), the same installed preset on both sides. The away
records are held at each HOMExAWAY pair ("off" = no experiment: the normal 0x1a080000 run); the same seeds 1..N for
every pair (common random numbers). Writes <out>/dose.json.
  python port/validation/execution_dose.py OUT_DIR PRESETS.jsonl DEFAULTS.json N PAIR [PAIR ...]   # PAIR: 30x50 or off
Optional env: DOSE_ATTRIBUTE (1-20, default 12) for every non-position attribute; DOSE_FMF (an .fmf imported through
the app for both sides instead of the Gegenpress preset).
"""
import base64, copy, json, os, sys
from pathlib import Path
sys.path.insert(0, 'port/validation'); sys.path.insert(0, 'build/source')
import fm27_tactics_server as app
from tactic_league import api, level, run


def main():
    out, presets, defaults, n = Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4])
    pairs = sys.argv[5:]
    out.mkdir(parents=True, exist_ok=True)
    base = json.load(open(defaults)); base = base.get('scenario', base)
    attribute = int(os.environ.get('DOSE_ATTRIBUTE', 12))
    for team in base['teams']:
        level(team)
        for p in team['players']:
            for i in range(15, 69): p['attributes'][i] = attribute * 5
    templates = [r for r in map(json.loads, open(presets)) if r['event'] == 'installed_tactic_preset']
    bench = templates[16]
    for team in base['teams']:
        app.desktop_tactic_plan.apply(app, team, bench); team['tactic_name'] = 'Gegenpress 433-433'
    if os.environ.get('DOSE_FMF'):
        data = base64.b64encode(open(os.environ['DOSE_FMF'], 'rb').read()).decode()
        base = app.validate_scenario(base)
        for side in (0, 1):
            base = api('/api/import-fmf', {'side': side, 'scenario': base, 'file_base64': data})['scenario']
    results = json.load(open(out / 'dose.json')) if (out / 'dose.json').exists() else {}
    for key in pairs:
        if key in results: continue
        s = copy.deepcopy(base)
        if key != 'off': s['experimental_execution'] = [int(v) for v in key.split('x')]
        s = app.validate_scenario(s)
        results[key] = run(s, list(range(1, n + 1)), f'execution {key}')
        r = results[key]
        print(key, 'home W', sum(x['score'][0] > x['score'][1] for x in r), 'D', sum(x['score'][0] == x['score'][1] for x in r),
              'xG', round(sum(x['xg'][0] for x in r) / n, 2), round(sum(x['xg'][1] for x in r) / n, 2), flush=True)
        (out / 'dose.json').write_text(json.dumps(results))


if __name__ == '__main__':
    main()
