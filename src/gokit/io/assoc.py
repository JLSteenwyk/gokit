"""Association readers."""

from __future__ import annotations

import re
from pathlib import Path

_GO_RE = re.compile(r"GO:\d{7}")


class UnsupportedAssociationFormatError(ValueError):
    """Raised when association format is not supported yet."""


def _detect_assoc_format(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".gaf"):
        return "gaf"
    if name.endswith(".gpad"):
        return "gpad"
    if "gene2go" in name:
        return "gene2go"

    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("!gaf-version"):
                return "gaf"
            if line.startswith("!gpa-version") or line.startswith("!gpad-version"):
                return "gpad"
            if line.startswith("#") and "tax_id" in line and "go_id" in line.lower():
                return "gene2go"
            parts = line.split("\t")
            if len(parts) > 4 and parts[0].isdigit() and _GO_RE.match(parts[2]):
                return "gene2go"
            if _GO_RE.search(line):
                return "id2gos"
    return "id2gos"


def _extract_goids(tokens: list[str]) -> set[str]:
    goids: set[str] = set()
    for token in tokens:
        for match in _GO_RE.findall(token):
            goids.add(match)
    return goids


def read_id2gos(path: Path) -> dict[str, set[str]]:
    assoc: dict[str, set[str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            gene = parts[0]
            goids = _extract_goids(parts[1:])
            if not goids:
                continue
            assoc.setdefault(gene, set()).update(goids)
    return assoc


def read_gaf(path: Path) -> dict[str, set[str]]:
    """Read GAF 2.x format using DB Object ID as gene key."""
    assoc: dict[str, set[str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip() or raw.startswith("!"):
                continue
            parts = raw.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            gene = parts[1].strip()
            goid = parts[4].strip()
            if not gene or not _GO_RE.fullmatch(goid):
                continue
            assoc.setdefault(gene, set()).add(goid)
    return assoc


def read_gpad(path: Path) -> dict[str, set[str]]:
    """Read GPAD 1.x/2.x format using DB Object ID as gene key."""
    assoc: dict[str, set[str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip() or raw.startswith("!"):
                continue
            parts = raw.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            gene = parts[1].strip()
            goid = parts[3].strip()
            if not gene or not _GO_RE.fullmatch(goid):
                continue
            assoc.setdefault(gene, set()).add(goid)
    return assoc


def read_gene2go(path: Path) -> dict[str, set[str]]:
    """Read NCBI gene2go format using GeneID as gene key."""
    assoc: dict[str, set[str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            gene = parts[1].strip()
            goid = parts[2].strip()
            if not gene or not _GO_RE.fullmatch(goid):
                continue
            assoc.setdefault(gene, set()).add(goid)
    return assoc


def read_associations(path: Path, assoc_format: str) -> dict[str, set[str]]:
    fmt = _detect_assoc_format(path) if assoc_format == "auto" else assoc_format

    if fmt == "id2gos":
        return read_id2gos(path)
    if fmt == "gaf":
        return read_gaf(path)
    if fmt == "gpad":
        return read_gpad(path)
    if fmt == "gene2go":
        return read_gene2go(path)

    raise UnsupportedAssociationFormatError(
        f"Association format '{assoc_format}' is not implemented."
    )
