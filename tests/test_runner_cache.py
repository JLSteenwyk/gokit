from __future__ import annotations

from gokit.core.enrichment import OraRunner, run_ora


def test_runner_matches_one_off_run() -> None:
    population = {"g1", "g2", "g3", "g4"}
    study = {"g1", "g2"}
    gene_to_go = {
        "g1": {"GO:0000001"},
        "g2": {"GO:0000001"},
        "g3": {"GO:0000002"},
        "g4": {"GO:0000002"},
    }
    go_to_namespace = {
        "GO:0000001": "biological_process",
        "GO:0000002": "molecular_function",
    }

    one_off = run_ora(
        study_genes=study,
        population_genes=population,
        gene_to_go=gene_to_go,
        go_to_namespace=go_to_namespace,
        namespace_filter="all",
    )

    runner = OraRunner(
        population_genes=population,
        gene_to_go=gene_to_go,
        go_to_namespace=go_to_namespace,
    )
    cached = runner.run_study(study_genes=study, namespace_filter="all")

    assert [r.go_id for r in one_off] == [r.go_id for r in cached]
    assert [r.p_adjusted for r in one_off] == [r.p_adjusted for r in cached]


def test_runner_has_population_cache() -> None:
    population = {"a", "b"}
    gene_to_go = {"a": {"GO:0000001"}, "b": {"GO:0000002"}}
    go_to_namespace = {
        "GO:0000001": "biological_process",
        "GO:0000002": "molecular_function",
    }
    runner = OraRunner(
        population_genes=population,
        gene_to_go=gene_to_go,
        go_to_namespace=go_to_namespace,
    )
    assert runner.go_to_pop_count["GO:0000001"] == 1
    assert runner.go_to_pop_count["GO:0000002"] == 1
