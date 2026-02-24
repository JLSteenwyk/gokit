# Migration Notes

## From legacy GOEA scripts to `gokit`

This document maps common legacy usage patterns to `gokit`.

## Basic enrichment
Legacy (example):
- `python scripts/find_enrichment.py study population association`

`gokit`:
- `gokit enrich --study study.txt --population population.txt --assoc association.txt --assoc-format id2gos --obo go-basic.obo --out results/goea`

Supported association formats in `gokit`:
- `id2gos`
- `gaf`
- `gpad`
- `gene2go`
- `auto` (detected from extension/header/content)

ID handling:
- Use `--id-type auto` to infer string vs integer-style IDs by overlap.
- Use `--id-type int` to normalize leading-zero IDs (e.g., `00101` -> `101`).
- Use `--id-type str` for strict string matching.

## Batch enrichment
Legacy:
- loop over multiple study files manually

`gokit`:
- `gokit enrich --studies studies.tsv --population population.txt --assoc association.txt --assoc-format id2gos --obo go-basic.obo --out results_batch --out-formats tsv,jsonl`

## Semantic comparison across studies
Legacy:
- custom post-processing

`gokit`:
- add `--compare-semantic --semantic-metric wang` to batch mode.
- outputs `semantic_similarity.tsv` and `semantic_top_pairs.tsv`.

## Output formats
- TSV/JSONL are available by default.
- Parquet is optional and requires `pyarrow`:
  - `pip install 'gokit[io]'`

## Behavior notes
- Association propagation to ancestor GO terms is ON by default.
- Disable propagation with `--no-propagate-counts`.
- Results are deterministically sorted by adjusted p-value, uncorrected p-value, then GO ID.
