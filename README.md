# gokit

`gokit` is a command-line toolkit scaffold for Gene Ontology enrichment workflows.

## Install

```bash
pip install -e .[dev]
```

## Commands

- `gokit enrich`
- `gokit validate`
- `gokit benchmark`
- `gokit cache`
- `gokit explain`
- Shorthand aliases: `gk_enrich`, `gk_validate`, `gk_benchmark`, `gk_cache`, `gk_explain`

## Quick start

```bash
gokit validate --study study.txt --population population.txt --assoc assoc.txt --obo go-basic.obo

gokit enrich \
  --study study.txt \
  --population population.txt \
  --assoc assoc.txt \
  --obo go-basic.obo \
  --out results/goea
```

Format-specific examples:

```bash
# id2gos
gokit enrich --study study.txt --population population.txt --assoc assoc.id2gos --assoc-format id2gos --obo go-basic.obo --out out/id2gos

# GAF
gokit enrich --study study.txt --population population.txt --assoc goa_human.gaf --assoc-format gaf --obo go-basic.obo --out out/gaf

# GPAD
gokit enrich --study study.txt --population population.txt --assoc goa_human.gpad --assoc-format gpad --obo go-basic.obo --out out/gpad

# gene2go
gokit enrich --study study.txt --population population.txt --assoc gene2go --assoc-format gene2go --id-type auto --obo go-basic.obo --out out/gene2go
```

Batch mode:

```bash
gokit enrich \
  --studies studies.tsv \
  --population population.txt \
  --assoc assoc.txt \
  --assoc-format id2gos \
  --obo go-basic.obo \
  --out results_batch \
  --out-formats tsv,jsonl \
  --compare-semantic \
  --semantic-metric wang \
  --semantic-top-k 5 \
  --semantic-namespace all \
  --semantic-min-padjsig 0.05
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
- single-study ORA with Fisher right-tail + Benjamini-Hochberg correction
- deterministic TSV/JSONL output ordering
- ID normalization control:
  - `--id-type auto` (default, overlap-based inference)
  - `--id-type str`
  - `--id-type int` (normalizes numeric IDs like `00101` -> `101`)
- batch mode via `--studies` with per-study + combined outputs
- grouped summaries:
  - single-study: `<out>.summary.tsv`
  - batch: `grouped_summary.tsv` + per-study `*.summary.tsv`
- parquet output via `--out-formats parquet` (requires optional dependency):
  - `pip install 'gokit[io]'`
- ontology-aware cross-study similarity matrix (`--compare-semantic`) with metrics:
  - `jaccard` (ancestor-closure set overlap)
  - `resnik` (IC-based BMA)
  - `lin` (IC-based BMA)
  - `wang` (graph contribution BMA)
- top contributing term-pair explanations in `semantic_top_pairs.tsv` (`--semantic-top-k`)
- pairwise semantic summary stats in `semantic_pair_summary.tsv`
- semantic pre-filters:
  - `--semantic-namespace {BP,MF,CC,all}`
  - `--semantic-min-padjsig FLOAT`
