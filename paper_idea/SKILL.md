---
name: paper_idea
description: Use when the user gives a paper (PDF/path/DOI) and wants its argument / evidence chain drawn as a logic flow — "为什么做 → 做法 → 发现 → 验证 → 结论", "论文逻辑图 / 证据链 / 论证逻辑 / paper_idea". Produces one detailed left-to-right SVG+PNG (rows = inference loops, grouped into section banners), not a mind map and not a design grid.
---

# paper_idea — 论文「论证逻辑链」流程图

Turns a paper into a **logic chain**: why they did it → what they did → what they found → how they verified → what they concluded → the follow-up question that starts the next loop. The renderer is fixed (`scripts/gen_logic_flow.py`); you only write a JSON spec. Style is a contract — do not redesign per paper.

Companion skill: `paper_data_method` (data/method mind map). This one is about **inference**, not inventory.

## What the user wants (learned the hard way)

- It must be a **flow of reasoning**, not a mind map, not a swimlane grid, not a 4×3 matrix. Counts per row differ; never pad to align.
- **Detailed**: concrete numbers, tests, cohorts, effect sizes, controls, external datasets, figure refs. A 5-box flowchart is rejected as "太简单 / low / 不专业".
- Left → right inside a row; rows top → bottom; the previous row's conclusion (or finding) **raises the next row's question** (dashed orange connector, label = the question's origin).
- **Limitations are not a row of their own**: they hang at the end of the same row (red dashed box after the conclusion).
- **Sections are visibly separated** by a coloured banner and a larger gap (one section ≈ one main figure/part of the paper). Rows inside a section keep the normal gap.
- Terminology: genetic ancestry → **遗传祖源**, ancestry proportion → **祖源成分比例**, popDE → 人群差异表达基因 (keep popDE in boxes if space is tight). Tool/assay names stay English.

## Node types

| type | tag | use for |
|---|---|---|
| `why` | 为什么做 | motivation, gap, the follow-up question that opens a row |
| `do` | 做法 | design, assay, model, test, parameters |
| `find` | 发现 | an observation with its numbers |
| `chk` | 验证 | replication, control, exclusion of an alternative, orthogonal data |
| `con` | 结论 | what the authors conclude from the row |
| `lim` | 局限 | caveat; **my own judgement is labelled `我的判断`** and kept apart from the authors' claims |

A row is not forced to follow why→do→find→chk→con; use the order the logic actually has. Typical row: `why → do → find → (find) → chk → con` + optional `lim`.

## Workflow

1. **Get the text** (Git Bash): `pdftotext -layout "<paper.pdf>" <scratchpad>/paper.txt`; read it with the Read tool (terminal output may be GBK-garbled). Read **all** of it: intro motivation, every Results paragraph, figure legends, Discussion. Supplement only if provided — otherwise mark supplement-only numbers as unverified in your reply.
2. **Split into sections** = main figures / parts (背景与设计, Fig 1, Fig 2 …, 讨论). Give each a colour (`#rrggbb`, distinct).
3. **Within a section, one row per inference loop.** Ask for each row: what question opens it (comes from the previous conclusion), what was done, what was found, what check backs it, what is concluded, what is the caveat.
4. **Write the spec** (see `examples/randolph2021.json`, 6 sections / 10 rows / 67 nodes):
   ```json
   {"title": "...", "footer": "evidence strength …",
    "sections": [{"title": "Fig 2 · …", "color": "#3B82C4",
      "rows": [{"title": "三 · 祖源效应", "nodes": [
          {"type": "why",  "fig": "追问",  "text": "…", "label": "引出追问"},
          {"type": "do",   "fig": "Fig 2A", "text": "…", "label": "为此做"},
          {"type": "find", "fig": "Fig 2A", "text": "…", "label": "得到"}],
        "lim": {"text": "我的判断：…", "label": "但是"}}]}]}
   ```
   - `label` of node *k* is the word on the arrow **into** node *k*. For node 0 of a row it is the label of the dashed connector from the previous row (use `引出追问` or a short cue).
   - Good arrow words: 为此做 / 得到 / 细看 / 验证 / 排除 / 再验证 / 说明 / 但是 / 同时发现 / 并且.
   - Text budget: a box holds ≈ 14 CJK chars × 6 lines (~80 chars). The script warns `WARN overflow …` on stderr → shorten the text, don't change geometry.
   - Up to 8 boxes per row incl. the `lim` box is comfortable; wider is allowed (image gets wider) but merge nodes first.
5. **Generate**: `PYTHONIOENCODING=utf-8 python -I <skill>/scripts/gen_logic_flow.py spec.json <scratchpad>/flow.svg`
6. **Render PNG** (headless Chrome/Edge): `python -I <skill>/scripts/render_png.py flow.svg flow.png`, then `Read` the PNG and check: no overlapping labels, no clipped text, connectors land on the first box of the next row, banners sit between sections.
7. **Deliver** with `SendUserFile`: PNG (`display: "render"`) and SVG (`display: "attach"`). The image is ~2200 px wide — far wider than the 680 px visualize widget, so do **not** use `show_widget`. Keep files in the user's project docs folder if they ask; spec and scratch in the scratchpad.
8. **Reply short, in the user's language**: what each colour means (one line), which numbers were **not** re-verified (supplement, earlier notes), what are my own judgements (red boxes), any correction to something said earlier.

## Content rules

- Every number comes from the paper; if from memory or supplement not re-read, say so in the reply. Do not invent a verification step the paper lacks (a row without `chk` is fine).
- Separate **authors' conclusion** (`con`) from **my judgement** (`lim` with `我的判断`). Give evidence strength in `footer` if the user has asked for it.
- Direction of effects matters: state which group is higher (e.g. 欧洲祖源更高), and note sign conventions (correlation with African proportion is negative when European is higher).
- Note reverse-causation / confounding traps the paper glosses over, as `lim` boxes, not as authors' claims.

## Files

- `scripts/gen_logic_flow.py` — renderer (fixed geometry: box 232×156, section banners, row backgrounds with section-colour bar).
- `scripts/render_png.py` — SVG → PNG via headless Chrome/Edge.
- `examples/randolph2021.json` — reference spec (Randolph et al., *Science* 2021, genetic ancestry & viral infection).
- `tests/run_tests.py` — regression: every example must regenerate its expected SVG with no overflow (`--update` to accept style changes).
