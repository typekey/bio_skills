#!/usr/bin/env python
"""Render the four-level "paper data & method" mind map as an SVG.

Usage:  python -I gen_mindmap.py spec.json out.svg

Levels (left to right):
  L1  source group           (e.g. 本文 / 外部)   neutral box, no colour
  L2  sample / resource      "{name} (condition) [amount]" + tag at the end
                             tag 体外 = green text, 体内 = red text, anything else = grey text
  L3  assay / sequencing method, coloured BY METHOD (same method -> same colour)
  L4  analysis methods, inherit the colour of their L3 parent

The geometry (columns, row heights, 680 px viewBox width) is fixed on purpose so every
paper's map looks identical. Overflowing text is reported on stderr.
"""
import html
import io
import json
import sys

# ---- fixed style contract ---------------------------------------------------
X1, W1 = 2, 50       # L1
X2, W2 = 60, 228     # L2
X3, W3 = 298, 168    # L3
X4, W4 = 476, 202    # L4
RIGHT = X4 + W4      # 678
L4_H, L4_STEP = 22, 25
L3_H = 26
L3_GAP = 8           # between L3 boxes of one L2
L2_GAP = 12          # between L2 boxes
L1_GAP = 24          # between L1 groups
L2_MIN_H = 48
TOP = 14
PALETTE = ["purple", "blue", "pink", "teal", "green", "amber", "coral", "red"]
LINE = "#888780"
TAG_FILL = {
    "体外": "var(--text-success)", "in vitro": "var(--text-success)", "ex vivo": "var(--text-success)",
    "体内": "var(--text-danger)", "in vivo": "var(--text-danger)",
}
DEFAULT_TAG_FILL = "var(--text-secondary)"
GRAY_TAGS = {"存档", "注释", "archive", "annotation", "resource"}


def esc(s):
    return html.escape(str(s), quote=False)


def est(text, size):
    """Rough rendered width: CJK / full-width = 1 em, everything else ~0.48 em (calibrated on rendered output)."""
    return sum(size if ord(c) > 0x2E7F else size * 0.48 for c in str(text))


def warn(msg):
    sys.stderr.write("WARN overflow: " + msg + "\n")


def curve(x1, y1, x2, y2, w):
    y1, y2 = round(y1, 1), round(y2, 1)
    if abs(y1 - y2) < 0.01:
        return f'<path d="M{x1} {y1:g}L{x2} {y2:g}" fill="none" stroke="{LINE}" stroke-width="{w}"/>'
    xm = (x1 + x2) / 2
    return (f'<path d="M{x1} {y1:g}C{xm:g} {y1:g} {xm:g} {y2:g} {x2} {y2:g}" '
            f'fill="none" stroke="{LINE}" stroke-width="{w}"/>')


def build(spec):
    samples = spec["samples"]

    # colour per method name: same method -> same ramp; explicit "color" wins
    ramp_of, next_i = {}, 0
    for s in samples:
        gray_sample = str(s.get("tag", "")).lower() in GRAY_TAGS
        for m in s["methods"]:
            key = m.get("method") or m["text"].rstrip(" ?")
            if m.get("color"):
                ramp_of.setdefault(key, m["color"])
            elif gray_sample or m.get("wide"):
                ramp_of.setdefault(key, "gray")
            elif key not in ramp_of:
                ramp_of[key] = PALETTE[next_i % len(PALETTE)]
                next_i += 1

    # ---- vertical layout ----
    y, prev, lay = TOP, None, []
    for s in samples:
        if prev is not None and s["l1"] != prev:
            y += L1_GAP - L2_GAP
        prev = s["l1"]
        rows = []
        cur = y
        for m in s["methods"]:
            n = len(m.get("analyses", []))
            h = max(n * L4_STEP - 3, L3_H) if n else L3_H
            rows.append((cur, h))
            cur += h + L3_GAP
        gh = cur - L3_GAP - y
        if gh < L2_MIN_H:
            off = (L2_MIN_H - gh) / 2
            rows = [(a + off, h) for a, h in rows]
            gh = L2_MIN_H
        lay.append((y + gh / 2, rows))
        y += gh + L2_GAP
    bottom = y - L2_GAP

    l1_order = []
    for s in samples:
        if s["l1"] not in l1_order:
            l1_order.append(s["l1"])
    l1_y = {}
    for L in l1_order:
        cs = [c for s, (c, _) in zip(samples, lay) if s["l1"] == L]
        l1_y[L] = (cs[0] + cs[-1]) / 2

    out = []
    a = out.append

    for L in l1_order:
        if est(L, 14) > W1 - 8:
            warn(f"L1 '{L}'")
        a(f'<g><rect class="box" x="{X1}" y="{l1_y[L]-20:g}" width="{W1}" height="40" rx="8" stroke-width="0.5"/>'
          f'<text class="th" x="{X1+W1/2:g}" y="{l1_y[L]:g}" text-anchor="middle" dominant-baseline="central">{esc(L)}</text></g>')

    for s, (c, rows) in zip(samples, lay):
        tag = s.get("tag", "")
        tfill = TAG_FILL.get(str(tag).lower(), DEFAULT_TAG_FILL)
        if est(s["name"], 14) + est(tag, 14) + 8 > W2 - 20:
            warn(f"L2 line1 '{s['name']}'")
        if est(s.get("detail", ""), 12) > W2 - 20:
            warn(f"L2 line2 '{s.get('detail','')}'")
        a(curve(X1 + W1, l1_y[s["l1"]], X2, c, 0.5))
        a(f'<g><rect class="box" x="{X2}" y="{c-24:g}" width="{W2}" height="48" rx="8" stroke-width="0.5"/>'
          f'<text class="th" x="{X2+10}" y="{c-9:g}" dominant-baseline="central">{esc(s["name"])}</text>'
          f'<text class="th" x="{X2+W2-10}" y="{c-9:g}" text-anchor="end" dominant-baseline="central" style="fill:{tfill}">{esc(tag)}</text>'
          f'<text class="ts" x="{X2+10}" y="{c+11:g}" dominant-baseline="central">{esc(s.get("detail",""))}</text></g>')
        for m, (top, h) in zip(s["methods"], rows):
            key = m.get("method") or m["text"].rstrip(" ?")
            r = ramp_of[key]
            an = m.get("analyses", [])
            wide = bool(m.get("wide"))
            w3 = (RIGHT - X3) if wide else W3
            lc = top + h / 2
            if est(m["text"], 12) > w3 - 20:
                warn(f"L3 '{m['text']}'")
            a(curve(X2 + W2, c, X3, lc, 0.5))
            a(f'<g class="c-{r}"><rect x="{X3}" y="{lc-L3_H/2:g}" width="{w3}" height="{L3_H}" rx="6" stroke-width="1"/>'
              f'<text class="ts" x="{X3+10}" y="{lc:g}" dominant-baseline="central">{esc(m["text"])}</text></g>')
            if an:
                s0 = lc - (len(an) - 1) * L4_STEP / 2
                for i, t in enumerate(an):
                    ly = s0 + i * L4_STEP
                    if est(t, 12) > W4 - 16:
                        warn(f"L4 '{t}'")
                    a(curve(X3 + W3, lc, X4, ly, 0.5))
                    a(f'<g class="c-{r}"><rect x="{X4}" y="{ly-L4_H/2:g}" width="{W4}" height="{L4_H}" rx="5" stroke-width="0.5"/>'
                      f'<text class="ts" x="{X4+8}" y="{ly:g}" dominant-baseline="central">{esc(t)}</text></g>')

    ly = bottom + 30
    legend = spec.get("legend", "字色 = 样本类型；框色 = 实验 / 测序方法（灰 = 存档、注释、临床分级）")
    notes = spec.get("legend_note", "三级 = 实验 / 测序方法；四级 = 分析方法；名称末尾 ? = 正文未明说，为推断")
    notes = [notes] if isinstance(notes, str) else list(notes)   # one string per line
    if est(legend, 12) > 680 - 96 - 8:
        warn(f"legend '{legend}'")
    a(f'<text class="th" x="12" y="{ly:g}" dominant-baseline="central" style="fill:var(--text-success)">体外</text>'
      f'<text class="th" x="52" y="{ly:g}" dominant-baseline="central" style="fill:var(--text-danger)">体内</text>'
      f'<text class="ts" x="96" y="{ly:g}" dominant-baseline="central">{esc(legend)}</text>')
    for i, line in enumerate(notes):
        if est(line, 12) > 680 - 24:
            warn(f"legend_note line {i+1}: '{line}' (split it into more lines)")
        a(f'<text class="ts" x="12" y="{ly+22*(i+1):g}" dominant-baseline="central">{esc(line)}</text>')
    height = int(ly + 22 * len(notes) + 24)

    title = esc(spec.get("title", "Paper data, methods and analyses"))
    head = (f'<svg width="100%" viewBox="0 0 680 {height}" role="img"><title>{title}</title>'
            f'<desc>L1 source, L2 sample with in vitro / in vivo tag, L3 assay method, L4 analysis method</desc>')
    return head + "\n" + "\n".join(out) + "\n</svg>", height


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with io.open(sys.argv[1], encoding="utf-8") as f:
        spec = json.load(f)
    svg, height = build(spec)
    with io.open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {sys.argv[2]} (viewBox 680x{height}, {len(svg)} chars)")


if __name__ == "__main__":
    main()
