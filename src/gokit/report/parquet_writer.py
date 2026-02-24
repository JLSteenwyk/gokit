"""Parquet output helpers (optional pyarrow dependency)."""

from __future__ import annotations

from pathlib import Path

from gokit.core.enrichment import EnrichmentResult


def _require_pyarrow():
    try:
        import pyarrow as pa  # type: ignore
        import pyarrow.parquet as pq  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Parquet export requires optional dependency 'pyarrow'. "
            "Install with: pip install 'gokit[io]'"
        ) from exc
    return pa, pq


def write_results_parquet(path: Path, results: list[EnrichmentResult]) -> None:
    pa, pq = _require_pyarrow()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "go_id": [r.go_id for r in results],
        "namespace": [r.namespace for r in results],
        "direction": [r.direction for r in results],
        "study_count": [r.study_count for r in results],
        "study_n": [r.study_n for r in results],
        "pop_count": [r.pop_count for r in results],
        "pop_n": [r.pop_n for r in results],
        "p_uncorrected": [r.p_uncorrected for r in results],
        "p_adjusted": [r.p_adjusted for r in results],
        "study_items": [sorted(r.study_items) if r.study_items is not None else None for r in results],
        "pop_items": [sorted(r.pop_items) if r.pop_items is not None else None for r in results],
    }
    table = pa.table(payload)
    pq.write_table(table, path)


def write_combined_parquet(path: Path, rows: list[tuple[str, EnrichmentResult]]) -> None:
    pa, pq = _require_pyarrow()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "study_id": [sid for sid, _ in rows],
        "go_id": [r.go_id for _, r in rows],
        "namespace": [r.namespace for _, r in rows],
        "direction": [r.direction for _, r in rows],
        "study_count": [r.study_count for _, r in rows],
        "study_n": [r.study_n for _, r in rows],
        "pop_count": [r.pop_count for _, r in rows],
        "pop_n": [r.pop_n for _, r in rows],
        "p_uncorrected": [r.p_uncorrected for _, r in rows],
        "p_adjusted": [r.p_adjusted for _, r in rows],
    }
    table = pa.table(payload)
    pq.write_table(table, path)
