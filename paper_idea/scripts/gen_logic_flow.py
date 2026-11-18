"""gen_logic_flow.py — paper argument chain (为什么做 → 做法 → 发现 → 验证 → 结论) as one SVG.

Usage:  python -I gen_logic_flow.py spec.json out.svg
Spec:   {"title": str, "subtitle": str?, "footer": str?,
         "sections": [{"title": str, "color": "#rrggbb",
            "rows": [{"title": str,
                      "nodes": [{"type": why|do|find|chk|con|lim, "fig": str, "text": str, "label": str}],
                      "lim": {"text": str, "label": str}?}]}]}
`label` of node k = the word on the arrow INTO node k (for node 0 = the dashed connector from the previous row).
`lim` is drawn as a red dashed box at the end of the same row, after the last node.
Geometry is fixed on purpose: the style is a contract, only the spec changes per paper.
"""
import html
import io
import json
import re
import sys

NW, NH, GAP, LM = 232, 156, 44, 40
PITCH = NW + GAP
FS = 13
BANNER_H, ROWGAP, SECGAP = 34, 74, 138
MAX_LINES = 6

ST = {
    "why":  ("#FFF3DC", "#E0A030", "为什么做"),
    "do":   ("#EEF0F3", "#7C8696", "做法"),
    "find": ("#DDF3EE", "#2E9C86", "发现"),
    "chk":  ("#E3F3D8", "#5FA33A", "验证"),
    "con":  ("#EBE3F8", "#7A5BC4", "结论"),
    "lim":  ("#FBE4E1", "#D2554A", "局限"),
}
TOK = re.compile(r"[A-Za-z0-9.,%²≈<>=/±+:∩'\-–_αβγκ~]+|.", re.S)
NOSTART = set("，。；、）」：？！")


def est(t):
    return sum(FS if ord(c) > 0x2E7F else FS * 0.55 for c in t)


def wrap(t, w):
    out, cur = [], ""
    for tk in TOK.findall(t):
        if est(cur + tk) > w and cur and tk not in NOSTART:
            out.append(cur)
            cur = tk.lstrip()
        else:
            cur += tk
    if cur:
        out.append(cur)
    return out


def build(spec):
    secs = spec["sections"]
    rows = [(si, r) for si, s in enumerate(secs) for r in s["rows"]]
    ncols = max(len(r["nodes"]) + (1 if r.get("lim") else 0) for _, r in rows)
    W = LM * 2 + ncols * PITCH - GAP
    # vertical layout
    y = 92
    banner_y, rowy = {}, {}
    ri = 0
    for si, s in enumerate(secs):
        banner_y[si] = y
        y += BANNER_H + 42
        for k, r in enumerate(s["rows"]):
            rowy[ri] = y
            ri += 1
            y += NH + (ROWGAP if k < len(s["rows"]) - 1 else SECGAP)
    H = int(y - SECGAP + 80)
    o = []
    a = o.append
    warns = []
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="Microsoft YaHei, PingFang SC, sans-serif">')
    a('<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
      '<path d="M1 1L9 5L1 9z" fill="#6B7280"/></marker></defs>')
    a(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
    a(f'<text x="{LM}" y="40" font-size="24" font-weight="700" fill="#1F2937">{html.escape(spec["title"])}</text>')
    sub = spec.get("subtitle", "每行 = 一轮「为什么做 → 做法 → 发现 → 验证 → 结论」；上一行的结论引出下一行的追问（橙色虚线）。红色虚线框 = 局限 / 我的判断。")
    a(f'<text x="{LM}" y="66" font-size="14" fill="#6B7280">{html.escape(sub)}</text>')
    lx = W - LM - 6 * 98
    for k, t in enumerate(["why", "do", "find", "chk", "con", "lim"]):
        f, s_, tag = ST[t]
        a(f'<rect x="{lx + k * 98}" y="22" width="16" height="16" rx="4" fill="{f}" stroke="{s_}" stroke-width="1.5"/>'
          f'<text x="{lx + k * 98 + 22}" y="35" font-size="13" fill="#374151">{tag}</text>')

    def lab(x, yy, t):
        if not t:
            return
        w = est(t) * 11 / 13 + 10
        a(f'<rect x="{x - w / 2}" y="{yy - 9}" width="{w}" height="17" rx="8" fill="#F8FAFC"/>'
          f'<text x="{x}" y="{yy + 4}" font-size="11" text-anchor="middle" fill="#6B7280">{html.escape(t)}</text>')

    for si, s in enumerate(secs):
        w = est(s["title"]) * 17 / 13 + 60
        a(f'<rect x="{W / 2 - w / 2}" y="{banner_y[si]}" width="{w}" height="{BANNER_H}" rx="17" fill="{s["color"]}"/>')
        a(f'<text x="{W / 2}" y="{banner_y[si] + 23}" font-size="17" font-weight="700" fill="#FFFFFF" '
          f'text-anchor="middle">{html.escape(s["title"])}</text>')
    for i, (si, r) in enumerate(rows):
        top = rowy[i] - 26
        h = NH + 38
        col = secs[si]["color"]
        a(f'<rect x="14" y="{top}" width="{W - 28}" height="{h}" rx="14" fill="#F8FAFC" stroke="#E5E7EB"/>')
        a(f'<rect x="14" y="{top + 8}" width="6" height="{h - 16}" rx="3" fill="{col}"/>')
        a(f'<text x="{W - 28}" y="{top + 17}" font-size="13" font-weight="700" fill="#9CA3AF" '
          f'text-anchor="end">{html.escape(r["title"])}</text>')

    def pos(i, c):
        return LM + c * PITCH, rowy[i]

    def arrow(i, c, lb, color="#6B7280"):
        px, yy = pos(i, c - 1)
        yy += NH / 2
        a(f'<line x1="{px + NW + 1}" y1="{yy}" x2="{px + NW + GAP - 3}" y2="{yy}" stroke="{color}" '
          f'stroke-width="1.8" marker-end="url(#ar)"/>')
        lab(px + NW + GAP / 2, yy - 12, lb)

    for i, (si, r) in enumerate(rows):
        nodes = r["nodes"]
        for c in range(1, len(nodes)):
            arrow(i, c, nodes[c].get("label", ""))
        if r.get("lim"):
            arrow(i, len(nodes), r["lim"].get("label", "但是"), "#D2554A")
        if i < len(rows) - 1:
            sx, sy = pos(i, len(nodes) - 1)
            dx, dy = pos(i + 1, 0)
            x1, y1, x2, y2 = sx + NW / 2, sy + NH + 1, dx + NW / 2, dy - 3
            ym = y1 + 36
            a(f'<path d="M{x1} {y1}V{ym}H{x2}V{y2}" fill="none" stroke="#B45309" stroke-width="2.2" '
              f'stroke-dasharray="7 4" marker-end="url(#ar)"/>')
            lab((x1 + x2) / 2 if abs(x1 - x2) > 200 else x1 + 60, ym, rows[i + 1][1]["nodes"][0].get("label", "引出追问"))

    def box(t, fig, txt, x, yy, where):
        f, s_, tag = ST[t]
        dash = ' stroke-dasharray="6 4"' if t == "lim" else ""
        a(f'<rect x="{x}" y="{yy}" width="{NW}" height="{NH}" rx="10" fill="{f}" stroke="{s_}" stroke-width="2"{dash}/>')
        a(f'<text x="{x + 12}" y="{yy + 22}" font-size="12.5" font-weight="700" fill="{s_}">{tag}</text>')
        if fig:
            a(f'<text x="{x + NW - 12}" y="{yy + 22}" font-size="12" text-anchor="end" fill="#6B7280">{html.escape(fig)}</text>')
        lines = wrap(txt, NW - 24)
        if len(lines) > MAX_LINES:
            warns.append(f"WARN overflow {where}: {len(lines)} lines > {MAX_LINES}")
        for k, line in enumerate(lines):
            a(f'<text x="{x + 12}" y="{yy + 46 + k * 19}" font-size="{FS}" fill="#1F2937">{html.escape(line)}</text>')

    for i, (si, r) in enumerate(rows):
        for c, n in enumerate(r["nodes"]):
            if n["type"] not in ST:
                raise SystemExit(f"unknown node type {n['type']!r}")
            x, yy = pos(i, c)
            box(n["type"], n.get("fig", ""), n["text"], x, yy, f"{r['title']}#{c}")
        if r.get("lim"):
            x, yy = pos(i, len(r["nodes"]))
            box("lim", r["lim"].get("fig", "我的判断"), r["lim"]["text"], x, yy, f"{r['title']}#lim")
    if spec.get("footer"):
        a(f'<text x="{LM}" y="{H - 34}" font-size="13" fill="#6B7280">{html.escape(spec["footer"])}</text>')
    a("</svg>")
    return "\n".join(o), W, H, warns


if __name__ == "__main__":
    spec = json.load(io.open(sys.argv[1], encoding="utf-8"))
    svg, W, H, warns = build(spec)
    io.open(sys.argv[2], "w", encoding="utf-8", newline="").write(svg)
    for w in warns:
        sys.stderr.write(w + "\n")
    print(W, H)
