"""Are in-match substitutions decided live, or replayed from the saved match? Replays one .pkm on its own seed and on
seeds 1..N (one worker process), and lists each side's substitutions per seed.

A substitution = a player whose on-pitch flag goes off with lineup slot 255, paired with a player coming on at the same
clock (host event native_on_pitch_change). Brief off/on flips with an unchanged slot (treatment) are ignored.

  python port/validation/subs_check.py PKM N OUT_DIR [HOST]
"""
import collections, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def subs(path):
    by_clock = collections.defaultdict(lambda: {'off': [], 'on': []})
    score = None
    for line in open(path):
        e = json.loads(line)
        if e.get('event') == 'natural_match_finished': score = e['score']
        if e.get('event') != 'native_on_pitch_change': continue
        key = (e['side'], e['clock'])
        if not e['on'] and e['slot'] == 255: by_clock[key]['off'].append(e['roster_index'])
        elif e['on']: by_clock[key]['on'].append((e['roster_index'], e['slot']))
    out = []
    for (side, clock), v in sorted(by_clock.items(), key=lambda x: x[0][1]):
        if v['off'] and v['on'] and len(v['off']) == len(v['on']):
            out.append((side, round(clock / 240, 1), tuple(sorted(v['off'])), tuple(sorted(i for i, _ in v['on']))))
    return score, out


def main():
    pkm, n, out = Path(sys.argv[1]).resolve(), int(sys.argv[2]), Path(sys.argv[3]).resolve()
    host = Path(sys.argv[4]).resolve() if len(sys.argv) > 4 else ROOT / 'private/engine/fm27_native/fm27_mac_host'
    out.mkdir(parents=True, exist_ok=True)
    own = int(pkm.stem.replace('_VER_fm', '').rsplit('_', 1)[1])
    seeds = [own] + list(range(1, n + 1))
    lines = ['FM27DW1']
    for s in seeds: lines += [str(pkm), '', str(out / f'{s}.jsonl'), str(s), '-']
    (out / 'manifest').write_text('\n'.join(lines) + '\n')
    env = dict(os.environ, FM27_ENGINE_PATH='fixture')
    code = subprocess.run([str(host), '--worker-manifest', str(out / 'manifest'), '--output', str(out / 'startup.jsonl'),
                           '--cancel-event', str(out / 'cancel')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    result = {}
    for s in seeds:
        p = out / f'{s}.jsonl'
        if p.exists(): result[s] = subs(p)
    (out / 'subs.json').write_text(json.dumps({str(k): v for k, v in result.items()}))
    print(f'{pkm.stem}: host exit {code}, {len(result)}/{len(seeds)} seeds')
    for s, (score, ss) in result.items():
        tag = 'OWN ' if s == own else '    '
        for side in (0, 1):
            print(f'{tag}seed {s:>10} {str(score):8s} side {side}: ' + '  '.join(f"{m}' {list(o)}->{list(i)}" for sd, m, o, i in ss if sd == side))


if __name__ == '__main__':
    main()
