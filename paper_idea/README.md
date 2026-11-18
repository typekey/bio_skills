# paper_idea

Claude Code skill: turn any paper into a detailed **argument / evidence-chain flow** (SVG + PNG).

```
为什么做 → 做法 → 发现 → 验证 → 结论  ⇢ (追问) ⇢  下一轮 …      局限挂在同一行末尾
rows = inference loops · sections = main figures, separated by coloured banners
```

- `SKILL.md` — instructions Claude follows (workflow, style contract, what the user rejected before)
- `scripts/gen_logic_flow.py` — renderer: `python -I scripts/gen_logic_flow.py spec.json out.svg`
- `scripts/render_png.py` — SVG → PNG via headless Chrome/Edge: `python -I scripts/render_png.py out.svg out.png`
- `examples/randolph2021.json` — reference spec (Science 2021; 6 sections, 10 rows, 67 nodes)
- `tests/` — regression test: `python -I tests/run_tests.py` (`--update` to accept style changes)

Install: copy this folder to `~/.claude/skills/paper_idea/`.
On Windows set `PYTHONIOENCODING=utf-8` when running the generator.
Sibling skill: [`paper_data_method`](../paper_data_method) (data / methods mind map).
