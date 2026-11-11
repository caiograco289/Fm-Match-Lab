"""Tactical-effectiveness on real saved FM27 matches (matches/automatic/*.pkm), replayed by the Mac host.

For every saved match and seed, the managed side (TEAM in the file name) is run with its natural records and with
record fields held at fixed values (FM27_MAC_EXEC_FIELDS, data writes between steps); the opponent keeps its natural
records. Results go to OUT/<match>/<condition>_<seed>.jsonl; `analyse` prints paired differences against natural.
  python port/validation/exec_real.py run OUT TEAM N [PARALLEL]
  python port/validation/exec_real.py analyse OUT TEAM
"""
import glob, json, math, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HOST = 'private/engine/fm27_native/fm27_mac_host'
SAVED = Path(os.environ.get('FM27_SAVED_MATCHES') or Path.home() / 'Library/Application Support/Sports Interactive/Football Manager 27/matches/automatic')   # override: e.g. a backup of matches the game has deleted
CONDITIONS = {'natural': None,
              'all33_30': {o: 30 for o in range(33)}, 'all33_90': {o: 90 for o in range(33)},
              'overall_30': {0x1e: 30}, 'overall_90': {0x1e: 90},
              'buyin_30': {0x1f: 30}, 'buyin_90': {0x1f: 90},
              'next_30': {0x20: 30}, 'next_90': {0x20: 90}}


def matches(team):
    out = []
    for f in sorted(glob.glob(str(SAVED / '*/*.pkm'))):
        name = Path(f).stem.replace('_VER_fm', '')
        home, away = name.rsplit('_', 1)[0].split('_v_')
        if team in (home, away): out.append((name, f, 0 if home == team else 1))
    return out


def run_one(args):
    out, name, path, side, cond, seed = args
    target = out / name / f'{cond}_{seed}.jsonl'
    if target.exists() and 'natural_match_finished' in target.read_text(): return
    env = dict(os.environ, FM27_ENGINE_PATH='fixture')
    if CONDITIONS[cond]: env['FM27_MAC_EXEC_FIELDS'] = ','.join(f'{side}:{o}={v}' for o, v in CONDITIONS[cond].items())
    subprocess.run([HOST, '--fixture', path, '--seed', str(seed), '--output', str(target)], env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def load(path):
    r = {}
    for line in open(path):
        e = json.loads(line)
        if e['event'] == 'natural_match_finished': r['score'] = e['score']
        if e['event'] == 'native_match_statistics': r['xg'] = [t['xg'] for t in e['teams']]
    return r if 'score' in r and 'xg' in r else None


def main():
    mode, out, team = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    found = matches(team)
    if mode == 'run':
        n, parallel = int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 3
        for name, _, _ in found: (out / name).mkdir(parents=True, exist_ok=True)
        jobs = [(out, name, path, side, cond, seed) for seed in range(1, n + 1) for name, path, side in found for cond in CONDITIONS]
        with ThreadPoolExecutor(parallel) as pool: list(pool.map(run_one, jobs))
        return
    rows = {c: [] for c in CONDITIONS}   # per (match, seed): own goals, opp goals, own xG, opp xG, points
    for name, _, side in found:
        for path in glob.glob(str(out / name / 'natural_*.jsonl')):
            seed = path.rsplit('_', 1)[1][:-6]
            for cond in CONDITIONS:
                r = load(out / name / f'{cond}_{seed}.jsonl') if (out / name / f'{cond}_{seed}.jsonl').exists() else None
                if not r: break
                g, x = r['score'], r['xg']
                own, opp = g[side], g[1 - side]
                rows[cond].append((name, seed, own, opp, x[side], x[1 - side], 3 if own > opp else 1 if own == opp else 0))
    base = {(r[0], r[1]): r for r in rows['natural']}
    n = len(base)
    print(f'{team}: {len(found)} matches, {n} paired match-seeds')
    print(f"{'condition':>11} {'W-D-L':>11} {'ppg':>5} {'goals':>10} {'xG':>10} | paired vs natural: xGD, GD, ppg")
    for cond, rs in rows.items():
        rs = [r for r in rs if (r[0], r[1]) in base]
        if not rs: continue
        w = sum(r[6] == 3 for r in rs); d = sum(r[6] == 1 for r in rs)
        mean = lambda i: sum(r[i] for r in rs) / len(rs)
        line = f"{cond:>11} {f'{w}-{d}-{len(rs) - w - d}':>11} {mean(6):5.2f} {mean(2):4.2f}-{mean(3):<4.2f} {mean(4):4.2f}-{mean(5):<4.2f}"
        if cond != 'natural':
            for f in (lambda r: r[4] - r[5], lambda r: r[2] - r[3], lambda r: r[6]):
                diffs = [f(r) - f(base[(r[0], r[1])]) for r in rs]
                m = sum(diffs) / len(diffs); sd = math.sqrt(sum((v - m) ** 2 for v in diffs) / (len(diffs) - 1))
                line += f" | {m:+.2f} (t={m / (sd / math.sqrt(len(diffs))) if sd else 0:+.1f})"
        print(line)


if __name__ == '__main__':
    main()
