"""Cross-study semantic similarity helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import log

SemanticMetric = str


@dataclass
class StudyTermSet:
    study_id: str
    go_ids: set[str]


def _expanded_terms(go_ids: set[str], go_to_ancestors: dict[str, set[str]]) -> set[str]:
    expanded = set(go_ids)
    for goid in go_ids:
        expanded.update(go_to_ancestors.get(goid, set()))
    return expanded


@dataclass
class PairwiseSemanticSummary:
    study_a: str
    study_b: str
    raw_a_terms: int
    raw_b_terms: int
    raw_overlap_terms: int
    raw_union_terms: int
    expanded_a_terms: int
    expanded_b_terms: int
    expanded_overlap_terms: int
    expanded_union_terms: int
    similarity_score: float


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a.intersection(b))
    union = len(a.union(b))
    return inter / union if union else 0.0


def _anc_with_self(goid: str, go_to_ancestors: dict[str, set[str]]) -> set[str]:
    return set(go_to_ancestors.get(goid, set())).union({goid})


def _ic(goid: str, go_to_pop_count: dict[str, int], pop_n: int) -> float:
    if pop_n <= 0:
        return 0.0
    cnt = go_to_pop_count.get(goid, 0)
    if cnt <= 0:
        return 0.0
    p = cnt / pop_n
    if p <= 0:
        return 0.0
    return -log(p)


def _mica_ic(
    a: str,
    b: str,
    go_to_ancestors: dict[str, set[str]],
    go_to_pop_count: dict[str, int],
    pop_n: int,
) -> float:
    common = _anc_with_self(a, go_to_ancestors).intersection(_anc_with_self(b, go_to_ancestors))
    if not common:
        return 0.0
    return max(_ic(goid, go_to_pop_count, pop_n) for goid in common)


def _resnik_term(
    a: str,
    b: str,
    go_to_ancestors: dict[str, set[str]],
    go_to_pop_count: dict[str, int],
    pop_n: int,
) -> float:
    return _mica_ic(a, b, go_to_ancestors, go_to_pop_count, pop_n)


def _lin_term(
    a: str,
    b: str,
    go_to_ancestors: dict[str, set[str]],
    go_to_pop_count: dict[str, int],
    pop_n: int,
) -> float:
    mica = _mica_ic(a, b, go_to_ancestors, go_to_pop_count, pop_n)
    ia = _ic(a, go_to_pop_count, pop_n)
    ib = _ic(b, go_to_pop_count, pop_n)
    denom = ia + ib
    if denom <= 0:
        return 0.0
    return (2.0 * mica) / denom


def _wang_sv(
    goid: str,
    go_to_parents: dict[str, set[str]],
    edge_weight: float = 0.8,
) -> dict[str, float]:
    # Highest decayed contribution from term to each ancestor.
    sv: dict[str, float] = {goid: 1.0}
    stack: list[str] = [goid]
    while stack:
        cur = stack.pop()
        cur_val = sv[cur]
        for parent in go_to_parents.get(cur, set()):
            cand = cur_val * edge_weight
            if cand > sv.get(parent, 0.0):
                sv[parent] = cand
                stack.append(parent)
    return sv


def _wang_term(a: str, b: str, go_to_parents: dict[str, set[str]]) -> float:
    sva = _wang_sv(a, go_to_parents)
    svb = _wang_sv(b, go_to_parents)
    common = set(sva).intersection(set(svb))
    if not common:
        return 0.0
    num = sum(sva[x] + svb[x] for x in common)
    den = sum(sva.values()) + sum(svb.values())
    if den <= 0:
        return 0.0
    return num / den


def _bma(
    a_terms: set[str],
    b_terms: set[str],
    sim_func,
) -> tuple[float, list[tuple[str, str, float]]]:
    if not a_terms and not b_terms:
        return 1.0, []
    if not a_terms or not b_terms:
        return 0.0, []

    best_pairs: list[tuple[str, str, float]] = []
    scores_ab: list[float] = []
    for a in a_terms:
        best_b = ""
        best = -1.0
        for b in b_terms:
            s = sim_func(a, b)
            if s > best:
                best = s
                best_b = b
        scores_ab.append(best if best >= 0 else 0.0)
        best_pairs.append((a, best_b, best if best >= 0 else 0.0))

    scores_ba: list[float] = []
    for b in b_terms:
        best = -1.0
        for a in a_terms:
            s = sim_func(a, b)
            if s > best:
                best = s
        scores_ba.append(best if best >= 0 else 0.0)

    left = sum(scores_ab) / len(scores_ab) if scores_ab else 0.0
    right = sum(scores_ba) / len(scores_ba) if scores_ba else 0.0
    return (left + right) / 2.0, best_pairs


def pairwise_semantic_similarity(
    studies: list[StudyTermSet],
    go_to_ancestors: dict[str, set[str]],
    *,
    metric: SemanticMetric = "jaccard",
    go_to_pop_count: dict[str, int] | None = None,
    pop_n: int | None = None,
    go_to_parents: dict[str, set[str]] | None = None,
    top_k: int = 5,
) -> tuple[dict[tuple[str, str], float], dict[tuple[str, str], list[tuple[str, str, float]]]]:
    expanded = {
        s.study_id: _expanded_terms(s.go_ids, go_to_ancestors)
        for s in studies
    }

    sim: dict[tuple[str, str], float] = {}
    top_pairs: dict[tuple[str, str], list[tuple[str, str, float]]] = {}
    ids = [s.study_id for s in studies]

    metric = metric.lower()
    if metric not in {"jaccard", "resnik", "lin", "wang"}:
        raise ValueError(f"Unsupported semantic metric: {metric}")

    for i, ida in enumerate(ids):
        for j, idb in enumerate(ids):
            if j < i:
                continue

            if metric == "jaccard":
                score = jaccard(expanded[ida], expanded[idb])
                pairs = []
            elif metric == "resnik":
                if go_to_pop_count is None or pop_n is None:
                    raise ValueError("resnik metric requires go_to_pop_count and pop_n")
                score, pairs = _bma(
                    expanded[ida],
                    expanded[idb],
                    lambda a, b: _resnik_term(a, b, go_to_ancestors, go_to_pop_count, pop_n),
                )
            elif metric == "lin":
                if go_to_pop_count is None or pop_n is None:
                    raise ValueError("lin metric requires go_to_pop_count and pop_n")
                score, pairs = _bma(
                    expanded[ida],
                    expanded[idb],
                    lambda a, b: _lin_term(a, b, go_to_ancestors, go_to_pop_count, pop_n),
                )
            else:
                if go_to_parents is None:
                    raise ValueError("wang metric requires go_to_parents")
                score, pairs = _bma(
                    expanded[ida],
                    expanded[idb],
                    lambda a, b: _wang_term(a, b, go_to_parents),
                )

            best = sorted(pairs, key=lambda x: (x[2], x[0], x[1]), reverse=True)[:top_k]
            sim[(ida, idb)] = score
            sim[(idb, ida)] = score
            top_pairs[(ida, idb)] = best
            top_pairs[(idb, ida)] = [(b, a, s) for (a, b, s) in best]
    return sim, top_pairs


def pairwise_semantic_summary(
    studies: list[StudyTermSet],
    go_to_ancestors: dict[str, set[str]],
    pairwise_scores: dict[tuple[str, str], float],
) -> list[PairwiseSemanticSummary]:
    raw = {s.study_id: set(s.go_ids) for s in studies}
    expanded = {
        s.study_id: _expanded_terms(s.go_ids, go_to_ancestors)
        for s in studies
    }

    out: list[PairwiseSemanticSummary] = []
    ids = [s.study_id for s in studies]
    for i, ida in enumerate(ids):
        for j, idb in enumerate(ids):
            if j < i:
                continue
            raw_a = raw[ida]
            raw_b = raw[idb]
            exp_a = expanded[ida]
            exp_b = expanded[idb]
            out.append(
                PairwiseSemanticSummary(
                    study_a=ida,
                    study_b=idb,
                    raw_a_terms=len(raw_a),
                    raw_b_terms=len(raw_b),
                    raw_overlap_terms=len(raw_a.intersection(raw_b)),
                    raw_union_terms=len(raw_a.union(raw_b)),
                    expanded_a_terms=len(exp_a),
                    expanded_b_terms=len(exp_b),
                    expanded_overlap_terms=len(exp_a.intersection(exp_b)),
                    expanded_union_terms=len(exp_a.union(exp_b)),
                    similarity_score=pairwise_scores.get((ida, idb), 0.0),
                )
            )
    return out
