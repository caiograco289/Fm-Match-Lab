"""Diagnostics for a positions JSONL from the macOS host (FM27_POSITIONS_JSONL).

Answers one question: does the ball field behave like a live ball? A live ball is within a couple of
yards of a player almost always, moves every tick, and sits at the carrier's feet when slow. Run:

  .venv/bin/python scripts/ball_diagnostics.py /tmp/pos.jsonl
"""
import json
import math
import statistics as st
import sys
from collections import defaultdict


def load(path):
    ball, play = {}, defaultdict(dict)
    for line in open(path):
        r = json.loads(line)
        t = r["tick"]
        ball[t] = (r["ball_x"], r["ball_y"])
        play[t][(r["side"], r["slot"])] = (r["x"], r["y"])
    return ball, play


def nearest(ball, players):
    return min(math.hypot(ball[0] - x, ball[1] - y) for x, y in players.values())


def main(path):
    ball, play = load(path)
    ticks = [t for t in sorted(ball) if len(play[t]) >= 20]
    if len(ticks) < 100:
        sys.exit("not enough ticks with 22 players")

    near = [nearest(ball[t], play[t]) for t in ticks]
    print("ticks %d" % len(ticks))
    print("nearest player to ball: <2 yd %.0f%%  <5 yd %.0f%%  <10 yd %.0f%%  >20 yd %.0f%%" % (
        100 * sum(1 for d in near if d < 2) / len(near),
        100 * sum(1 for d in near if d < 5) / len(near),
        100 * sum(1 for d in near if d < 10) / len(near),
        100 * sum(1 for d in near if d > 20) / len(near)))

    # how often does the ball move at all, and how far between samples?
    steps = [math.hypot(ball[b][0] - ball[a][0], ball[b][1] - ball[a][1]) for a, b in zip(ticks, ticks[1:])]
    static = sum(1 for d in steps if d < 0.01)
    moved = [d for d in steps if d >= 0.01]
    print("ball static on %.0f%% of ticks" % (100 * static / len(steps)))
    if moved:
        print("step when it moves: median %.1f yd, p90 %.1f yd" % (st.median(moved), sorted(moved)[int(len(moved) * .9)]))

    # time alignment: could the ball belong to another tick?
    best = max((sum(1 for t in ticks if t + lag in play and nearest(ball[t], play[t + lag]) < 3) / len(ticks), lag)
               for lag in range(-8, 9))
    print("best time alignment: lag %+d, %.0f%% within 3 yd (lag 0: %.0f%%)" % (
        best[1], 100 * best[0],
        100 * sum(1 for t in ticks if nearest(ball[t], play[t]) < 3) / len(ticks)))

    # coordinate transforms: a frame/orientation error would show up here
    forms = {
        "as-is": lambda x, y: (x, y), "flip x": lambda x, y: (-x, y), "flip y": lambda x, y: (x, -y),
        "flip both": lambda x, y: (-x, -y), "swap": lambda x, y: (y, x),
    }
    for name, fn in forms.items():
        hit = sum(1 for t in ticks if nearest(fn(*ball[t]), play[t]) < 3)
        print("  %-10s within 3 yd: %.0f%%" % (name, 100 * hit / len(ticks)))

    # is the (static) ball ahead of the nearest player's movement? a target would be
    ahead = total = 0
    for a, b in zip(ticks, ticks[1:]):
        if math.hypot(ball[b][0] - ball[a][0], ball[b][1] - ball[a][1]) >= 0.01:
            continue
        best_key, best_d = None, 1e9
        for k, (x, y) in play[a].items():
            if k not in play[b]:
                continue
            d = math.hypot(ball[a][0] - x, ball[a][1] - y)
            if d < best_d:
                best_key, best_d = k, d
        if best_key is None or best_d > 25:
            continue
        x, y = play[a][best_key]
        vx, vy = play[b][best_key][0] - x, play[b][best_key][1] - y
        speed = math.hypot(vx, vy)
        if speed < 0.05:
            continue
        total += 1
        ahead += 1 if ((ball[a][0] - x) * vx + (ball[a][1] - y) * vy) / (speed * max(best_d, 1e-6)) > 0.3 else 0
    if total:
        print("static ball ahead of the nearest player's movement: %.0f%% (n=%d)" % (100 * ahead / total, total))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
