# GOKIT Plan

## 1. Goal
Build a new command-line tool named `gokit` for fast, reproducible, and workflow-friendly Gene Ontology enrichment analysis.

Primary outcomes:
- Correctness-first GOEA results with explicit provenance.
- Faster runtime and lower memory use on large datasets.
- Batch-friendly CLI for repeated study comparisons.
- Deterministic outputs suitable for CI and scientific pipelines.

## 2. Product Scope
`gokit` will provide a modern CLI and core engine for:
- Over-representation analysis for GO terms.
- Multiple testing correction with deterministic modes.
- Support for common annotation formats (GAF, GPAD, gene2go, id2gos).
- Namespace-aware and grouped reporting.
- Structured machine-readable outputs (JSONL/Parquet/TSV).

Out of scope for v1:
- Full UI/web interface.
- Distributed compute cluster execution.

## 3. Key Design Principles
- Scientific correctness before speed.
- Explicit reproducibility controls (`--seed`, run manifest, exact ontology/version metadata).
- Stable output ordering and schema versioning.
- Memory-efficient defaults with opt-in detail expansion.
- Backward-compatible migration path from existing GOATOOLS workflows.

## 4. CLI Surface (Proposed)
Top-level command:
- `gokit` (with subcommands)

Core subcommands:
- `gokit enrich`: Run GO enrichment for one or many study sets.
- `gokit validate`: Validate study/population/association/ontology inputs.
- `gokit benchmark`: Run built-in benchmark suite for local perf checks.
- `gokit cache`: Inspect/build/clear ontology and propagation caches.
- `gokit explain`: Explain one result row with calculation trace.

`gokit enrich` core flags:
- `--study FILE` or `--studies FILE` (batch mode)
- `--population FILE`
- `--assoc FILE`
- `--assoc-format {auto,gaf,gpad,gene2go,id2gos}`
- `--obo FILE`
- `--namespace {BP,MF,CC,all}`
- `--method` (multiple correction methods)
- `--alpha FLOAT`
- `--seed INT`
- `--fdr-resamples INT`
- `--store-items {auto,always,never}`
- `--relationships LIST`
- `--out PREFIX`
- `--out-formats {tsv,xlsx,jsonl,parquet}`
- `--manifest FILE`

## 5. Engine Architecture
Proposed package layout:
- `gokit/cli/`: command wiring, argument parsing, help text.
- `gokit/io/`: readers/writers for GO and association formats.
- `gokit/core/`: enrichment calculations and correction methods.
- `gokit/cache/`: DAG cache and ancestor propagation cache.
- `gokit/report/`: deterministic rendering and exports.
- `gokit/bench/`: benchmark scenarios and fixtures.

Core execution pipeline:
1. Parse and validate inputs.
2. Load ontology with versioned cache.
3. Load associations with strict schema checks.
4. Build/reuse propagation maps.
5. Compute enrichment in count-first mode.
6. Apply multiple testing correction.
7. Materialize item-level details only when requested.
8. Emit deterministic outputs + manifest.

## 6. Performance Strategy
High-impact optimizations for v1:
- Fix namespace merge semantics by unioning per-gene GO sets across namespaces.
- Cache `term_pop` and reuse across repeated runs.
- Add count-first result objects with lazy item expansion.
- Memoize contingency-table p-value calls where counts repeat.
- Cache ancestor closures keyed by ontology+relationships config.
- Add optional on-disk OBO parse cache with strict invalidation.

Performance guardrails:
- Built-in benchmark corpus and fixed fixtures.
- CI performance lane with regression thresholds.
- Deterministic random controls for FDR simulations.

## 7. Correctness and Reproducibility
Required guarantees:
- Deterministic result ordering with explicit tie-breakers.
- Stable output schema and schema version.
- Run manifest including:
  - ontology path + version + hash
  - association source + hash
  - methods, alpha, relationships, seed, resamples
  - tool version and Python version
  - timestamp and command line

Validation strategy:
- Golden tests versus known outputs.
- Cross-check mode against established GOATOOLS outputs.
- Numerical equivalence tests before and after optimizations.

## 8. Developer Experience
- Typed Python codebase (mypy/ruff/pytest).
- Clear API for embedding in notebooks/pipelines.
- Rich errors with actionable messages.
- `gokit doctor` (later phase) for environment diagnostics.

## 9. Delivery Plan
Phase 0: Foundation (1-2 weeks)
- Repo scaffolding, packaging, CLI skeleton, docs.
- Input validation command.
- Baseline fixtures and test harness.

Phase 1: Correctness MVP (2-3 weeks)
- `enrich` command end-to-end for single study.
- Correct namespace association merge behavior.
- Deterministic output sorting.
- Manifest output.

Phase 2: Performance MVP (2-3 weeks)
- Count-first/lazy item mode.
- `term_pop` and propagation caching.
- OBO cache.
- Local benchmark command.

Phase 3: Batch + Formats (2 weeks)
- Multi-study batch mode.
- JSONL/Parquet exporters.
- Improved grouped reporting.

Phase 4: CI Hardening (1-2 weeks)
- Benchmark CI thresholds.
- Compatibility tests across Python versions.
- Release candidate and migration docs.

## 10. Success Metrics
- 2x faster repeated-run throughput on standard benchmark datasets.
- 30-50% lower peak memory in default mode.
- Deterministic re-run outputs (byte-identical for same inputs/seed).
- 90%+ command-level test coverage for CLI critical paths.
- Zero known correctness regressions against golden fixtures.

## 11. Immediate Next Steps
1. Initialize `gokit` package skeleton and `enrich` command contract.
2. Implement strict input validators and manifest schema.
3. Implement correctness-critical namespace merge and regression tests.
4. Add benchmark fixtures and baseline timing report.
