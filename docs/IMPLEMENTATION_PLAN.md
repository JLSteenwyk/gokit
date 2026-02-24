# GOKIT Implementation Plan

## Scope
This plan tracks implementation of v1 only. Item 10 (post-v1 roadmap) was intentionally removed.

## Milestones
- [x] M0: Scaffold package, CLI, manifest, aliases
- [x] M1: Single-study enrichment engine (correctness MVP, id2gos path)
- [x] M2: Performance MVP (count-first + caching)
- [x] M3: Batch and expanded formats
- [x] M4: CI hardening and release prep

## M1 Tasks (Current)
- [x] Define CLI contract and command surface
- [x] Implement strict input existence/emptiness validation
- [x] Implement normalized parsers for study/population/associations/obo
- [x] Implement ORA Fisher exact + BH correction
- [x] Implement deterministic output sorting and stable schemas
- [x] Write TSV and JSONL result emitters
- [x] Add single-study integration tests and golden fixture

## M2 Tasks
- [x] `store_items` memory modes
- [x] `term_pop` caching for repeated runs
- [x] ancestor propagation caching
- [x] OBO on-disk cache and invalidation
- [x] benchmark suite + baseline metrics

## M3 Tasks
- [x] `--studies` batch mode
- [x] cross-study ontology-aware similarity matrix (`--compare-semantic`, ancestor-closure Jaccard)
- [x] parquet export
- [x] grouped reporting improvements
- [x] advanced semantic metrics (Resnik/Lin/Wang) and top-pair explanations

## M4 Tasks
- [x] benchmark gates in CI
- [x] py-version matrix expansion
- [x] release docs and migration notes

## Acceptance Criteria
- `gokit enrich` computes real enriched GO terms for `id2gos` input in v1 path.
- Output ordering is deterministic across repeated runs.
- Manifest contains reproducibility metadata for every run.
