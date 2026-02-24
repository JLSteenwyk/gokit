"""Association readers."""

from __future__ import annotations

import re
from pathlib import Path

_GO_RE = re.compile(r"GO:\d{7}")


class UnsupportedAssociationFormatError(ValueError):
    """Raised when association format is not supported yet."""


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


def read_associations(path: Path, assoc_format: str) -> dict[str, set[str]]:
    if assoc_format in {"auto", "id2gos"}:
        return read_id2gos(path)

    raise UnsupportedAssociationFormatError(
        f"Association format '{assoc_format}' is not implemented yet. "
        "Use --assoc-format id2gos for now."
    )
