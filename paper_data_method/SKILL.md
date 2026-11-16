---
name: paper_data_method
description: Use when the user gives a paper (PDF/path/DOI) and wants a mind map of its data, samples, experimental/sequencing methods and analysis methods — "论文数据思维导图", "paper_data_method", "整理这篇文章用到的数据和方法". Produces the same four-level SVG map every time (source → sample + in vivo/in vitro → assay → analysis).
---

# paper_data_method — 论文「数据 / 方法」四级思维导图

Turns any paper into one fixed-style mind map. The style is a contract: do **not** redesign it per paper. Geometry and colours live in `scripts/gen_mindmap.py`; you only fill in a JSON spec.

## The four levels

| Level | Content | Style |
|---|---|---|
| L1 | Source: `本文` / `外部` (other levels of source are allowed, e.g. a second cohort) | neutral box, **no colour** |
| L2 | `{样本名} (条件) [数据量]` + tag at the right end | neutral box; tag colour is **text only**: 体外 green, 体内 red, 存档 / 注释 grey |
| L3 | Experimental or sequencing method | box coloured **by method** — same method = same colour everywhere |
| L4 | Analysis methods applied to that data | same colour as its L3 parent, smaller boxes |

Rules that keep the maps consistent:
- Colour encodes the **method**, never the source (本文 vs 外部) and never in vivo/in vitro.
- Archives (GEO/SRA/Zenodo/...) and annotation resources (MSigDB, GO, gene lists) get their own L2 with tag 存档 / 注释; their L3 are grey, archives use `"wide": true` and have no L4.
- Include **everything**, uncertain items too. Mark inferred items by ending the text with ` ?` and tell the user which they are. Do not guess numbers: write `[人数见 table S1]` style placeholders when the main text lacks a count.
- 体内 = state of the donor/patient not treated ex vivo (serum, genomic DNA, patient PBMC). 体外 = cells taken out and treated/cultured (including ex vivo infection of primary cells). Say so in the reply if a call is borderline (e.g. donor DNA is tagged 体内).
- No root/centre node. Keep the viewBox width at 680.

## Workflow

1. **Get the text.** The Read tool's PDF mode needs poppler and often fails on Windows. Use Git Bash:
   `pdftotext -layout "<paper.pdf>" <scratchpad>/paper.txt` (fallback: `python -c "import pypdf"`). Output may be GBK-garbled in the terminal; read the saved file with the Read tool instead.
2. **Read all of it**, not just Results: Methods, figure legends, acknowledgments (facilities, kits), author contributions (who ran which assay), data availability (accession numbers), references for any external dataset that is re-analysed. Supplement only if the user provides it; otherwise say what lives there.
3. **Collect** every wet-lab sample/cohort/cell type with its condition and amount; every assay or sequencing method; every external dataset actually *used* (not merely cited); every archive accession; every annotation resource or gene list; every analysis/statistical method and which dataset it consumes.
   - Analyses depending on a resource (GSEA, ClueGO, gene lists) go under that resource's L3; analyses on a dataset go under the assay that produced it. Don't duplicate.
   - Results (specific genes, effect sizes) are not methods — leave them out.
4. **Write the spec** (see `examples/randolph2021.json`, which reproduces the reference map (body identical)):
   ```json
   {"title": "...",
    "samples": [{"l1": "本文", "name": "PBMC (mock/IAV, 6 hpi)", "detail": "[90 男性 · 235,161 细胞]", "tag": "体外",
      "methods": [{"text": "scRNA-seq", "analyses": ["limma 差异表达", "..."]},
                  {"text": "bulk RNA-seq (同样本)", "method": "bulk RNA-seq"}]}]}
   ```
   - `method`: colour-identity key; give the same key to entries that must share a colour (default = `text`). Optional `color` forces a ramp (`purple blue pink teal green amber coral red gray`). Palette auto-assigns in order of first appearance.
   - Text budget (12 px; CJK = 1 em): L2 line 1 ≈ 14 chars incl. tag, L2 line 2 ≈ 17 chars, L3 ≈ 13 chars, L4 ≈ 15 chars. The script prints `WARN overflow` on stderr — shorten and rerun rather than changing geometry.
5. **Generate.** Always write UTF-8 and force Python's encoding on Windows:
   `PYTHONIOENCODING=utf-8 python -I <skill>/scripts/gen_mindmap.py spec.json <scratchpad>/map.svg`
   Keep spec and svg in the scratchpad, not in the user's project.
6. **Render.** Load the `mcp__visualize__read_me` tool (module `diagram`) silently once, `Read` the generated SVG, and paste it unchanged into `mcp__visualize__show_widget` (raw `<svg>`; the script already escapes `<`/`&`). Call with a snake_case title like `<firstauthor><year>_data_method_mindmap`.
7. **Reply** (short, Chinese if the user writes Chinese): what each colour/tag means in one line; which items are inferred (`?`) and why; what is missing because the supplement/Methods were not available; what was deliberately left out (results, specific genes). Do not restate the diagram's content.

## Lessons from testing on a second paper (Liu 2025 Cell, wet-lab heavy)

- **Many methods (> 8 colours).** The palette has 8 ramps + gray. When a paper has more assays than that, colour by **method family**, not by assay: give every member the same `color` and the same `method` key (e.g. perturbation = coral: LNA/ASO/siRNA knockdown, steric block, overexpression, drug treatment; readout = green: RT-qPCR, ELISA, Western, reporter; fractionation/IP = amber; chemistry / in vitro RNA / mass spec = red; proximity-ligation sequencing = purple). Say in `legend_note` (list of strings, one per line) which family each colour is. Put the family names in the reply.
- **Cell-line papers.** Cultured cell lines are 体外; mouse tissue taken straight from the animal is 体内 (flag the choice in the reply). Reagent preparation (dendrimer synthesis, virus stock, ASO design) is an L3/L4 item, not a sample.
- **Key resources table.** In two-column PDFs `pdftotext -layout` scrambles the STAR Methods key resources table, so accession ↔ dataset pairs may be misaligned. Never guess an accession for an external dataset: list only accessions stated in prose (Data availability), and tell the user which external accessions need checking against the original table.
- **Resource-dependent analyses** (GO, Rfam, PDB, secretome lists) go under that resource's gray L3; **statistics shared by many assays** (e.g. paired t-test) go once under the assay where they are first used. Don't repeat.
- **Length.** A full STAR-Methods paper produced ~45 L3 / ~100 L4 and a 2700 px tall SVG (~43 KB). That is expected; do not trim to fit, but do fix every `WARN overflow`.
- `legend` is one line (≤ ~48 CJK chars); `legend_note` may be a list — the script warns if a line is too wide.

## Terminology (user's preference, keep consistent)

- genetic ancestry → **遗传祖源**, ancestry proportion → **祖源成分比例** (not 祖先 / 谱系); popDE → 人群差异表达基因.
- Chinese labels with English tool/assay names kept in English (scRNA-seq, limma, mash, Luminex).
- Reply and labels in the user's language; assay names stay English.

## Files

- `scripts/gen_mindmap.py` — the renderer (fixed columns X: L1 2, L2 60, L3 298, L4 476).
- `examples/randolph2021.json` — reference spec (Randolph et al., *Science* 2021; patient/donor cohort, 4 analysis-heavy levels).
- `examples/liu2025.json` — reference spec (Liu et al., *Cell* 2025; cell lines + mouse tissue, many wet-lab assays, family colours).
