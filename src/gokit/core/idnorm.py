"""Gene ID normalization helpers."""

from __future__ import annotations

import re

_INT_RE = re.compile(r"^[+-]?\d+$")


def normalize_one(gene_id: str, mode: str) -> str | None:
    gid = gene_id.strip()
    if mode == "str":
        return gid
    if mode == "int":
        if not _INT_RE.fullmatch(gid):
            return None
        return str(int(gid))
    raise ValueError(f"Unsupported id normalization mode: {mode}")


def normalize_gene_set(genes: set[str], mode: str) -> set[str]:
    out: set[str] = set()
    for gid in genes:
        n = normalize_one(gid, mode)
        if n is not None:
            out.add(n)
    return out


def normalize_assoc_keys(assoc: dict[str, set[str]], mode: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for gid, gos in assoc.items():
        n = normalize_one(gid, mode)
        if n is None:
            continue
        out.setdefault(n, set()).update(gos)
    return out


def infer_id_mode(population_genes: set[str], assoc_keys: set[str]) -> str:
    pop_str = set(population_genes)
    assoc_str = set(assoc_keys)
    overlap_str = len(pop_str.intersection(assoc_str))

    pop_int = normalize_gene_set(population_genes, "int")
    assoc_int = normalize_gene_set(assoc_keys, "int")
    overlap_int = len(pop_int.intersection(assoc_int))

    if overlap_int > overlap_str:
        return "int"
    return "str"
