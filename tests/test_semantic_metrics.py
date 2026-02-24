from __future__ import annotations

from gokit.core.semantic import StudyTermSet, pairwise_semantic_similarity


def _fixture():
    studies = [
        StudyTermSet(study_id="a", go_ids={"GO:0000002"}),
        StudyTermSet(study_id="b", go_ids={"GO:0000003"}),
    ]
    go_to_anc = {
        "GO:0000002": {"GO:0000001"},
        "GO:0000003": {"GO:0000001"},
        "GO:0000001": set(),
    }
    go_to_parents = {
        "GO:0000002": {"GO:0000001"},
        "GO:0000003": {"GO:0000001"},
        "GO:0000001": set(),
    }
    go_to_pop = {
        "GO:0000001": 100,
        "GO:0000002": 30,
        "GO:0000003": 20,
    }
    pop_n = 100
    return studies, go_to_anc, go_to_parents, go_to_pop, pop_n


def test_resnik_and_lin_and_wang_compute() -> None:
    studies, go_to_anc, go_to_parents, go_to_pop, pop_n = _fixture()

    for metric in ["resnik", "lin", "wang"]:
        matrix, top_pairs = pairwise_semantic_similarity(
            studies,
            go_to_anc,
            metric=metric,
            go_to_pop_count=go_to_pop,
            pop_n=pop_n,
            go_to_parents=go_to_parents,
            top_k=3,
        )
        assert ("a", "b") in matrix
        assert 0.0 <= matrix[("a", "b")]
        assert ("a", "b") in top_pairs


def test_jaccard_path_works() -> None:
    studies, go_to_anc, _, _, _ = _fixture()
    matrix, _ = pairwise_semantic_similarity(studies, go_to_anc, metric="jaccard")
    assert 0.0 <= matrix[("a", "b")] <= 1.0
