"""Statistical helpers for enrichment analysis."""

from __future__ import annotations

from math import comb


def _hypergeom_pmf(*, pop_n: int, pop_count: int, study_n: int, k: int) -> float:
    denom = comb(pop_n, study_n)
    if denom == 0:
        return 0.0
    left = comb(pop_count, k)
    right = comb(pop_n - pop_count, study_n - k)
    return (left * right) / denom


def fisher_right_tail(*, pop_n: int, pop_count: int, study_n: int, study_count: int) -> float:
    if pop_n <= 0 or study_n <= 0:
        return 1.0
    if pop_count <= 0 or study_count <= 0:
        return 1.0

    max_k = min(pop_count, study_n)
    if study_count > max_k:
        return 1.0

    p = 0.0
    for k in range(study_count, max_k + 1):
        p += _hypergeom_pmf(pop_n=pop_n, pop_count=pop_count, study_n=study_n, k=k)
    return min(max(p, 0.0), 1.0)


def fisher_left_tail(*, pop_n: int, pop_count: int, study_n: int, study_count: int) -> float:
    if pop_n <= 0 or study_n <= 0:
        return 1.0
    if pop_count <= 0:
        return 1.0

    min_k = max(0, study_n - (pop_n - pop_count))
    max_k = min(pop_count, study_n)
    if study_count < min_k:
        return 0.0
    if study_count >= max_k:
        return 1.0

    p = 0.0
    for k in range(min_k, study_count + 1):
        p += _hypergeom_pmf(pop_n=pop_n, pop_count=pop_count, study_n=study_n, k=k)
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


def _clip01(p: float) -> float:
    return min(max(p, 0.0), 1.0)


def bonferroni_adjust(pvalues: list[float]) -> list[float]:
    m = len(pvalues)
    if m == 0:
        return []
    return [_clip01(p * m) for p in pvalues]


def holm_adjust(pvalues: list[float]) -> list[float]:
    m = len(pvalues)
    if m == 0:
        return []

    ranked = sorted(enumerate(pvalues), key=lambda x: x[1])
    adjusted = [1.0] * m
    running_max = 0.0
    for rank, (idx, pval) in enumerate(ranked, start=1):
        raw = (m - rank + 1) * pval
        running_max = max(running_max, raw)
        adjusted[idx] = _clip01(running_max)
    return adjusted


def by_adjust(pvalues: list[float]) -> list[float]:
    m = len(pvalues)
    if m == 0:
        return []
    c_m = sum(1.0 / k for k in range(1, m + 1))
    ranked = sorted(enumerate(pvalues), key=lambda x: x[1])
    adjusted = [1.0] * m
    running_min = 1.0
    for rank in range(m, 0, -1):
        idx, pval = ranked[rank - 1]
        raw = (pval * m * c_m) / rank
        running_min = min(running_min, raw)
        adjusted[idx] = _clip01(running_min)
    return adjusted


def adjust_pvalues(pvalues: list[float], method: str) -> list[float]:
    m = method.lower()
    if m == "fdr_bh":
        return bh_adjust(pvalues)
    if m == "fdr_by":
        return by_adjust(pvalues)
    if m == "bonferroni":
        return bonferroni_adjust(pvalues)
    if m == "holm":
        return holm_adjust(pvalues)
    if m in {"none", "raw"}:
        return [_clip01(p) for p in pvalues]
    raise ValueError(f"Unsupported multiple-testing method: {method}")
