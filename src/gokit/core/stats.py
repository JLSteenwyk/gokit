"""Statistical helpers for enrichment analysis."""

from __future__ import annotations

from math import comb


def fisher_right_tail(*, pop_n: int, pop_count: int, study_n: int, study_count: int) -> float:
    if pop_n <= 0 or study_n <= 0:
        return 1.0
    if pop_count <= 0 or study_count <= 0:
        return 1.0

    max_k = min(pop_count, study_n)
    if study_count > max_k:
        return 1.0

    denom = comb(pop_n, study_n)
    if denom == 0:
        return 1.0

    p = 0.0
    for k in range(study_count, max_k + 1):
        left = comb(pop_count, k)
        right = comb(pop_n - pop_count, study_n - k)
        p += (left * right) / denom
    return min(max(p, 0.0), 1.0)


def bh_adjust(pvalues: list[float]) -> list[float]:
    m = len(pvalues)
    if m == 0:
        return []

    ranked = sorted(enumerate(pvalues), key=lambda x: x[1])
    adjusted = [1.0] * m
    running_min = 1.0

    for rank in range(m, 0, -1):
        idx, pval = ranked[rank - 1]
        raw = (pval * m) / rank
        running_min = min(running_min, raw)
        adjusted[idx] = min(max(running_min, 0.0), 1.0)

    return adjusted
