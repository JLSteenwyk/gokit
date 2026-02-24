"""Core enrichment engine for ORA."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from gokit.core.stats import bh_adjust, fisher_right_tail


@dataclass
class EnrichmentResult:
    go_id: str
    namespace: str
    study_count: int
    study_n: int
    pop_count: int
    pop_n: int
    p_uncorrected: float
    p_adjusted: float
    study_items: set[str] | None = None
    pop_items: set[str] | None = None


_NS_MAP = {
    "biological_process": "BP",
    "molecular_function": "MF",
    "cellular_component": "CC",
}


def _canonical_ns(ns: str | None) -> str:
    if ns is None:
        return "NA"
    return _NS_MAP.get(ns, ns)


class OraRunner:
    """Reusable ORA runner that caches population term counts."""

    def __init__(
        self,
        *,
        population_genes: set[str],
        gene_to_go: dict[str, set[str]],
        go_to_namespace: dict[str, str],
    ) -> None:
        self.population_genes = set(population_genes)
        self.gene_to_go = gene_to_go
        self.go_to_namespace = go_to_namespace
        self.go_to_pop_count = self._build_go_to_pop_count()

    def _build_go_to_pop_count(self) -> dict[str, int]:
        go_to_pop_genes: dict[str, set[str]] = defaultdict(set)
        for gene in self.population_genes:
            for goid in self.gene_to_go.get(gene, set()):
                go_to_pop_genes[goid].add(gene)
        return {goid: len(genes) for goid, genes in go_to_pop_genes.items()}

    def run_study(
        self, *, study_genes: set[str], namespace_filter: str, store_items: bool = False
    ) -> list[EnrichmentResult]:
        study = set(study_genes).intersection(self.population_genes)
        go_to_study_count: dict[str, int] = defaultdict(int)
        go_to_study_items: dict[str, set[str]] = defaultdict(set)
        go_to_pop_items: dict[str, set[str]] | None = defaultdict(set) if store_items else None

        if store_items and go_to_pop_items is not None:
            for gene in self.population_genes:
                for goid in self.gene_to_go.get(gene, set()):
                    go_to_pop_items[goid].add(gene)

        for gene in study:
            for goid in self.gene_to_go.get(gene, set()):
                go_to_study_count[goid] += 1
                if store_items:
                    go_to_study_items[goid].add(gene)

        rows: list[tuple[str, str, int, int, int, int, float]] = []
        pvals: list[float] = []

        for goid, study_count in go_to_study_count.items():
            if study_count <= 0:
                continue
            pop_count = self.go_to_pop_count.get(goid, 0)
            if pop_count <= 0:
                continue

            ns = _canonical_ns(self.go_to_namespace.get(goid))
            if namespace_filter != "all" and ns != namespace_filter:
                continue

            p_unc = fisher_right_tail(
                pop_n=len(self.population_genes),
                pop_count=pop_count,
                study_n=len(study),
                study_count=study_count,
            )
            rows.append(
                (
                    goid,
                    ns,
                    study_count,
                    len(study),
                    pop_count,
                    len(self.population_genes),
                    p_unc,
                )
            )
            pvals.append(p_unc)

        padj = bh_adjust(pvals)
        results: list[EnrichmentResult] = []
        for idx, row in enumerate(rows):
            goid, ns, st_cnt, st_n, pop_cnt, pop_n, p_unc = row
            results.append(
                EnrichmentResult(
                    go_id=goid,
                    namespace=ns,
                    study_count=st_cnt,
                    study_n=st_n,
                    pop_count=pop_cnt,
                    pop_n=pop_n,
                    p_uncorrected=p_unc,
                    p_adjusted=padj[idx],
                    study_items=(go_to_study_items.get(goid, set()) if store_items else None),
                    pop_items=(go_to_pop_items.get(goid, set()) if store_items and go_to_pop_items else None),
                )
            )
        results.sort(key=lambda r: (r.p_adjusted, r.p_uncorrected, r.go_id))
        return results


def run_ora(
    *,
    study_genes: set[str],
    population_genes: set[str],
    gene_to_go: dict[str, set[str]],
    go_to_namespace: dict[str, str],
    namespace_filter: str,
    store_items: bool = False,
) -> list[EnrichmentResult]:
    """Convenience wrapper for one-off runs."""
    runner = OraRunner(
        population_genes=population_genes,
        gene_to_go=gene_to_go,
        go_to_namespace=go_to_namespace,
    )
    return runner.run_study(
        study_genes=study_genes, namespace_filter=namespace_filter, store_items=store_items
    )
