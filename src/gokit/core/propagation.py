"""Association propagation helpers."""

from __future__ import annotations


def propagate_gene_to_go(
    gene_to_go: dict[str, set[str]],
    go_to_ancestors: dict[str, set[str]],
) -> dict[str, set[str]]:
    propagated: dict[str, set[str]] = {}
    for gene, goids in gene_to_go.items():
        out = set(goids)
        for goid in goids:
            out.update(go_to_ancestors.get(goid, set()))
        propagated[gene] = out
    return propagated
