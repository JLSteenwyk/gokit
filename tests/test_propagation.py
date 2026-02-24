from __future__ import annotations

from gokit.core.propagation import propagate_gene_to_go


def test_propagate_gene_to_go_adds_ancestors() -> None:
    gene_to_go = {"g1": {"GO:0000002"}}
    go_to_ancestors = {"GO:0000002": {"GO:0000001"}}

    out = propagate_gene_to_go(gene_to_go, go_to_ancestors)
    assert out["g1"] == {"GO:0000002", "GO:0000001"}
