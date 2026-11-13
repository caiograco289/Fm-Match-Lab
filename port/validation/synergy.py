"""Synergy of an attribute group in a neutral-ground study: (group effect) - (sum of single effects), paired.

    .venv/bin/python port/validation/synergy.py runs/roadmap/10

For each style group in the study and each '<Name> group+5' condition whose single conditions are present, prints
the sum of the single effects and the synergy with t values. Every condition shares the unchanged matches, so the
synergy is computed match by match: (group - base) - sum(single - base).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import neutral_study as ns  # noqa: E402

GROUPS = {
    'Playmaking': ['Passing', 'Vision', 'Technique', 'Decisions'],
    'Ball carrying': ['Dribbling', 'Balance', 'Concentration', 'Long Shots'],
    'Defending': ['Tackling', 'Marking', 'Positioning', 'Anticipation'],
    'Aerial': ['Jumping Reach', 'Heading', 'Strength', 'Bravery'],
}


def mean_t(vals):
    n = len(vals)
    mu = sum(vals) / n
    sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / (n - 1))
    return mu, mu / (sd / math.sqrt(n)) if sd else float('nan')


def main(out):
    data = ns.load(out)
    styles = sorted({g for g, _ in data})
    print('| Style | Group | Measure | Group effect | Sum of singles | Synergy (group - sum) | Pairs |')
    print('|---|---|---|---|---|---|---|')
    for style in styles:
        base = data.get((style, 'none'))
        if not base:
            continue
        for grp, singles in GROUPS.items():
            gkey = (style, f'{grp} group+5')
            if gkey not in data or any((style, f'{s}+5') not in data for s in singles):
                continue
            for m in ('xPts', 'xGD'):
                g_eff, s_sum, syn = [], [], []
                for k, b in base.items():
                    try:
                        s = sum(data[(style, f'{x}+5')][k][m] - b[m] for x in singles)
                        g = data[gkey][k][m] - b[m]
                    except KeyError:
                        continue
                    g_eff.append(g)
                    s_sum.append(s)
                    syn.append(g - s)
                cells = [f'{mu:+.2f} ({t:+.1f})' for mu, t in (mean_t(g_eff), mean_t(s_sum), mean_t(syn))]
                print(f'| {style} | {grp} | {m} | ' + ' | '.join(cells) + f' | {len(syn)} |')


if __name__ == '__main__':
    main(sys.argv[1])
