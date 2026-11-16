# paper_data_method

Claude Code skill: turn any paper into a fixed-style, four-level mind map of its **data, samples,
experimental/sequencing methods and analysis methods** (SVG).

```
L1 source (本文 / 外部)  →  L2 sample (condition) [amount] + 体外/体内 tag  →  L3 assay  →  L4 analysis
```

- `SKILL.md` — instructions Claude follows (workflow, style contract, lessons learned)
- `scripts/gen_mindmap.py` — renderer: `python -I scripts/gen_mindmap.py spec.json out.svg`
- `examples/` — reference specs: `randolph2021.json` (Science 2021, donor cohort),
  `liu2025.json` (Cell 2025, cell lines + mouse tissue, family colours)
- `tests/` — regression test: `python -I tests/run_tests.py` (`--update` to accept style changes)

Install: copy this folder to `~/.claude/skills/paper_data_method/`.
On Windows set `PYTHONIOENCODING=utf-8` when running the generator.
