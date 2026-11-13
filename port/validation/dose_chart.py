"""Small-multiples SVG of a dose-response study (one panel per attribute): effect per level with 95% bars.

    .venv/bin/python port/validation/dose_chart.py runs/roadmap/12 docs/studies/img/12-dose-response.svg [--measure xPts]
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dose_response as dr  # noqa: E402


def main():
    p = argparse.ArgumentParser(); p.add_argument('out'); p.add_argument('svg'); p.add_argument('--measure', default='xPts')
    a = p.parse_args()
    res = sorted(dr.analyse(a.out, a.measure).items(), key=lambda kv: -kv[1]['slope'])
    lo = min(min(m - 2 * s for m, s in zip(r['means'], r['se'])) for _, r in res)
    hi = max(max(m + 2 * s for m, s in zip(r['means'], r['se'])) for _, r in res)
    lo, hi = min(lo, -0.1), max(hi, 0.1)
    cols, W, H, pad = 5, 200, 150, 34
    rows = (len(res) + cols - 1) // cols
    sx = lambda lv: pad + (lv - 1) / 19 * (W - pad - 10)
    sy = lambda v: 22 + (hi - v) / (hi - lo) * (H - 22 - 22)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{cols*W}" height="{rows*H+24}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
           f'<rect width="100%" height="100%" fill="#ffffff"/>',
           f'<text x="8" y="{rows*H+16}" fill="#555">{a.measure} per game against the unchanged squad (natural values about 9-17), whole squad set to each level; bars: 95%. Dashed: zero.</text>']
    for i, ((g, at), r) in enumerate(res):
        ox, oy = (i % cols) * W, (i // cols) * H
        out.append(f'<g transform="translate({ox},{oy})">')
        out.append(f'<text x="{pad}" y="14" font-weight="bold" fill="#222">{at}</text>')
        out.append(f'<line x1="{pad}" x2="{W-10}" y1="{sy(0):.1f}" y2="{sy(0):.1f}" stroke="#999" stroke-dasharray="3,3"/>')
        for v in [x / 2 for x in range(int(lo * 2) - 1, int(hi * 2) + 2) if lo <= x / 2 <= hi]:
            out.append(f'<text x="{pad-4}" y="{sy(v)+4:.1f}" text-anchor="end" fill="#777">{v:+.1f}</text>')
        for lv in (1, 6, 12, 18):
            out.append(f'<text x="{sx(lv):.1f}" y="{H-8}" text-anchor="middle" fill="#777">{lv}</text>')
        out.append(f'<line x1="{pad}" x2="{pad}" y1="22" y2="{H-22}" stroke="#ccc"/>')
        pts = ' '.join(f'{sx(l):.1f},{sy(m):.1f}' for l, m in zip(r['levels'], r['means']))
        out.append(f'<polyline points="{pts}" fill="none" stroke="#2f6db5" stroke-width="2"/>')
        for l, m, s in zip(r['levels'], r['means'], r['se']):
            out.append(f'<line x1="{sx(l):.1f}" x2="{sx(l):.1f}" y1="{sy(m-1.96*s):.1f}" y2="{sy(m+1.96*s):.1f}" stroke="#2f6db5" stroke-opacity="0.5"/>')
            out.append(f'<circle cx="{sx(l):.1f}" cy="{sy(m):.1f}" r="2.5" fill="#2f6db5"/>')
        out.append('</g>')
    out.append('</svg>')
    Path(a.svg).write_text('\n'.join(out))


if __name__ == '__main__':
    main()
