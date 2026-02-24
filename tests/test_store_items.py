from __future__ import annotations

from gokit.core.enrichment import run_ora


def _dataset():
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
    return study, population, gene_to_go, go_to_namespace


def test_store_items_default_off() -> None:
    study, population, gene_to_go, go_to_namespace = _dataset()
    rows = run_ora(
        study_genes=study,
        population_genes=population,
        gene_to_go=gene_to_go,
        go_to_namespace=go_to_namespace,
        namespace_filter="all",
    )
    assert rows
    assert rows[0].study_items is None
    assert rows[0].pop_items is None


def test_store_items_always_on() -> None:
    study, population, gene_to_go, go_to_namespace = _dataset()
    rows = run_ora(
        study_genes=study,
        population_genes=population,
        gene_to_go=gene_to_go,
        go_to_namespace=go_to_namespace,
        namespace_filter="all",
        store_items=True,
    )
    assert rows
    assert rows[0].study_items is not None
    assert rows[0].pop_items is not None
