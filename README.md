# gokit

`gokit` is a command-line toolkit scaffold for Gene Ontology enrichment workflows.

## Install

```bash
pip install -e .[dev]
```

For figure generation:

```bash
pip install -e .[plot]
```

`gokit plot` uses color palettes from `pypubfigs`.

## Commands

- `gokit enrich`
- `gokit validate`
- `gokit benchmark`
- `gokit cache`
- `gokit explain`
- `gokit plot`
- `gokit download`
- `gokit report`
- Shorthand aliases: `gk_enrich`, `gk_validate`, `gk_benchmark`, `gk_cache`, `gk_explain`, `gk_plot`, `gk_download`, `gk_report`

## Command status

| Command | Status | What it does |
|---|---|---|
| `gokit enrich` | Supported | Runs GO enrichment (single or batch), writes deterministic TSV/JSONL/parquet outputs, semantic comparisons, optional auto-plot emission, and a reproducibility manifest. |
| `gokit validate` | Supported | Validates required input files and basic readiness checks before enrichment. |
| `gokit benchmark` | Supported | Runs a local synthetic benchmark to measure runtime and cache speedup behavior. |
| `gokit cache` | Supported | Manages and inspects ontology cache artifacts used to accelerate repeated runs. |
| `gokit plot` | Supported | Generates publication-style figures from enrichment tables and semantic similarity matrices. |
| `gokit download` | Supported | Downloads `go-basic.obo` and `goslim_generic.obo` from Gene Ontology endpoints. |
| `gokit report` | Supported | Builds a consolidated markdown report summarizing outputs, top terms, and run metadata. |
| `gokit explain` | Placeholder | Current scaffold only: prints a result object or GO ID stub; full statistical/ancestor trace explanation is planned. |

## Quick start

```bash
gokit download

gokit validate --study study.txt --population population.txt --assoc assoc.txt

gokit enrich \
  --study study.txt \
  --population population.txt \
  --assoc assoc.txt \
  --out results/goea

gokit report --run results/goea
```

`--obo` defaults to `./go-basic.obo`, and `--assoc-format` defaults to `auto`.

Format-specific examples:

```bash
# id2gos
gokit enrich --study study.txt --population population.txt --assoc assoc.id2gos --assoc-format id2gos --out out/id2gos

# GAF
gokit enrich --study study.txt --population population.txt --assoc goa_human.gaf --assoc-format gaf --out out/gaf

# GPAD
gokit enrich --study study.txt --population population.txt --assoc goa_human.gpad --assoc-format gpad --out out/gpad

# gene2go
gokit enrich --study study.txt --population population.txt --assoc gene2go --assoc-format gene2go --id-type auto --out out/gene2go
```

Batch mode:

```bash
gokit enrich \
  --studies studies.tsv \
  --population population.txt \
  --assoc assoc.txt \
  --assoc-format id2gos \
  --out results_batch \
  --out-formats tsv,jsonl \
  --compare-semantic \
  --semantic-metric wang \
  --semantic-top-k 5 \
  --semantic-namespace all \
  --semantic-min-padjsig 0.05
```

Download command behavior is equivalent to:
- `wget http://current.geneontology.org/ontology/go-basic.obo`
- `wget http://current.geneontology.org/ontology/subsets/goslim_generic.obo`

Figure generation:

```bash
gokit plot \
  --input results_batch/all_studies.tsv \
  --study-id study_a \
  --kind term-bar \
  --direction both \
  --top-n 20 \
  --out figures/study_a_terms \
  --format png

gokit plot \
  --input results_batch/all_studies.tsv \
  --study-id study_a \
  --kind direction-summary \
  --alpha 0.05 \
  --out figures/study_a_direction_summary.svg

gokit plot \
  --input results_batch/semantic_similarity.tsv \
  --kind semantic-network \
  --min-similarity 0.25 \
  --max-edges 40 \
  --out figures/semantic_network.png

# optional: have enrich auto-emit plots
gokit enrich \
  --studies studies.tsv \
  --population population.txt \
  --assoc assoc.txt \
  --out results_batch \
  --compare-semantic \
  --emit-plots term-bar,direction-summary,semantic-network \
  --plot-format png
```

`studies.tsv` supports:
- `study_name<TAB>/path/to/study.txt`
- `/path/to/study.txt` (name inferred from filename)

Current status: single-study enrichment is implemented for `id2gos`; broader format support and performance phases are in progress.

Current enrichment support:
- association formats:
  - `id2gos`
  - `gaf`
  - `gpad`
  - `gene2go`
  - `auto` detection by extension/header
- single-study ORA with Fisher exact testing + Benjamini-Hochberg correction
- multiple-testing correction via `--method`:
  - `fdr_bh` (default)
  - `fdr_by`
  - `bonferroni`
  - `holm`
  - `none`
- directional testing for over/under enrichment:
  - `--test-direction both` (default)
  - `--test-direction over`
  - `--test-direction under`
- deterministic TSV/JSONL output ordering
- ID normalization control:
  - `--id-type auto` (default, overlap-based inference)
  - `--id-type str`
  - `--id-type int` (normalizes numeric IDs like `00101` -> `101`)
- batch mode via `--studies` with per-study + combined outputs
- grouped summaries:
  - single-study: `<out>.summary.tsv`
  - batch: `grouped_summary.tsv` + per-study `*.summary.tsv`
  - includes direction-aware fields:
    - `over_terms`, `under_terms`
    - `over_significant_terms`, `under_significant_terms`
- parquet output via `--out-formats parquet` (requires optional dependency):
  - `pip install 'gokit[io]'`
- ontology-aware cross-study similarity matrix (`--compare-semantic`) with metrics:
  - `jaccard` (ancestor-closure set overlap)
  - `resnik` (IC-based BMA)
  - `lin` (IC-based BMA)
  - `wang` (graph contribution BMA)
- top contributing term-pair explanations in `semantic_top_pairs.tsv` (`--semantic-top-k`)
- pairwise semantic summary stats in `semantic_pair_summary.tsv`
- figure generation from TSV outputs via `gokit plot`:
  - `term-bar`: top terms by `-log10(p_adjusted)` colored by direction
  - `direction-summary`: significant over/under counts by namespace
  - `semantic-network`: cross-study graph from `semantic_similarity.tsv`
- optional auto-plot emission in `gokit enrich` via `--emit-plots`
- consolidated markdown report via `gokit report --run <output-prefix-or-dir>`
- semantic pre-filters:
  - `--semantic-namespace {BP,MF,CC,all}`
  - `--semantic-min-padjsig FLOAT`
