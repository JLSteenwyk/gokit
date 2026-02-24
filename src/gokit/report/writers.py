"""Result writers."""

from __future__ import annotations

import json
from pathlib import Path

from gokit.core.enrichment import EnrichmentResult
from gokit.core.semantic import PairwiseSemanticSummary


def write_tsv(path: Path, results: list[EnrichmentResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(
            "GO\tNS\tstudy_count\tstudy_n\tpop_count\tpop_n\tp_uncorrected\tp_adjusted\n"
        )
        for row in results:
            handle.write(
                "\t".join(
                    [
                        row.go_id,
                        row.namespace,
                        str(row.study_count),
                        str(row.study_n),
                        str(row.pop_count),
                        str(row.pop_n),
                        f"{row.p_uncorrected:.6g}",
                        f"{row.p_adjusted:.6g}",
                    ]
                )
                + "\n"
            )


def write_jsonl(path: Path, results: list[EnrichmentResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in results:
            payload = {
                "go_id": row.go_id,
                "namespace": row.namespace,
                "study_count": row.study_count,
                "study_n": row.study_n,
                "pop_count": row.pop_count,
                "pop_n": row.pop_n,
                "p_uncorrected": row.p_uncorrected,
                "p_adjusted": row.p_adjusted,
            }
            if row.study_items is not None:
                payload["study_items"] = sorted(row.study_items)
            if row.pop_items is not None:
                payload["pop_items"] = sorted(row.pop_items)
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def write_combined_tsv(path: Path, rows: list[tuple[str, EnrichmentResult]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(
            "study_id\tGO\tNS\tstudy_count\tstudy_n\tpop_count\tpop_n\tp_uncorrected\tp_adjusted\n"
        )
        for study_id, row in rows:
            handle.write(
                "\t".join(
                    [
                        study_id,
                        row.go_id,
                        row.namespace,
                        str(row.study_count),
                        str(row.study_n),
                        str(row.pop_count),
                        str(row.pop_n),
                        f"{row.p_uncorrected:.6g}",
                        f"{row.p_adjusted:.6g}",
                    ]
                )
                + "\n"
            )


def write_combined_jsonl(path: Path, rows: list[tuple[str, EnrichmentResult]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for study_id, row in rows:
            payload = {
                "study_id": study_id,
                "go_id": row.go_id,
                "namespace": row.namespace,
                "study_count": row.study_count,
                "study_n": row.study_n,
                "pop_count": row.pop_count,
                "pop_n": row.pop_n,
                "p_uncorrected": row.p_uncorrected,
                "p_adjusted": row.p_adjusted,
            }
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def write_similarity_matrix(
    path: Path,
    study_ids: list[str],
    pairwise: dict[tuple[str, str], float],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("study_id\t" + "\t".join(study_ids) + "\n")
        for row_id in study_ids:
            vals = [f"{pairwise.get((row_id, col_id), 0.0):.6f}" for col_id in study_ids]
            handle.write(row_id + "\t" + "\t".join(vals) + "\n")


def write_similarity_top_pairs(
    path: Path,
    top_pairs: dict[tuple[str, str], list[tuple[str, str, float]]],
    study_ids: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("study_a\tstudy_b\trank\tgo_a\tgo_b\tscore\n")
        for a in study_ids:
            for b in study_ids:
                if a == b:
                    continue
                rows = top_pairs.get((a, b), [])
                for rank, (ga, gb, score) in enumerate(rows, start=1):
                    handle.write(f"{a}\t{b}\t{rank}\t{ga}\t{gb}\t{score:.6f}\n")


def write_semantic_pair_summary(path: Path, rows: list[PairwiseSemanticSummary]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(
            "study_a\tstudy_b\traw_a_terms\traw_b_terms\traw_overlap_terms\traw_union_terms\t"
            "expanded_a_terms\texpanded_b_terms\texpanded_overlap_terms\texpanded_union_terms\t"
            "similarity_score\n"
        )
        for r in rows:
            handle.write(
                f"{r.study_a}\t{r.study_b}\t{r.raw_a_terms}\t{r.raw_b_terms}\t"
                f"{r.raw_overlap_terms}\t{r.raw_union_terms}\t{r.expanded_a_terms}\t"
                f"{r.expanded_b_terms}\t{r.expanded_overlap_terms}\t{r.expanded_union_terms}\t"
                f"{r.similarity_score:.6f}\n"
            )


def write_grouped_summary_single(path: Path, results: list[EnrichmentResult], alpha: float) -> None:
    by_ns: dict[str, list[EnrichmentResult]] = {}
    for row in results:
        by_ns.setdefault(row.namespace, []).append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("namespace\ttotal_terms\tsignificant_terms\talpha\n")
        for ns in sorted(by_ns):
            rows = by_ns[ns]
            sig = sum(1 for r in rows if r.p_adjusted <= alpha)
            handle.write(f"{ns}\t{len(rows)}\t{sig}\t{alpha}\n")


def write_grouped_summary_batch(
    path: Path,
    rows: list[tuple[str, EnrichmentResult]],
    alpha: float,
) -> None:
    grouped: dict[tuple[str, str], list[EnrichmentResult]] = {}
    for study_id, row in rows:
        grouped.setdefault((study_id, row.namespace), []).append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("study_id\tnamespace\ttotal_terms\tsignificant_terms\talpha\n")
        for (study_id, ns) in sorted(grouped):
            vals = grouped[(study_id, ns)]
            sig = sum(1 for r in vals if r.p_adjusted <= alpha)
            handle.write(f"{study_id}\t{ns}\t{len(vals)}\t{sig}\t{alpha}\n")
