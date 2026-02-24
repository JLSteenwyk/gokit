"""OBO parser for GO term namespaces and parent relationships."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OboMeta:
    format_version: str | None
    data_version: str | None


def read_obo_graph(path: Path) -> tuple[dict[str, str], dict[str, set[str]], OboMeta]:
    go_to_namespace: dict[str, str] = {}
    go_to_parents: dict[str, set[str]] = {}
    format_version: str | None = None
    data_version: str | None = None

    current_go: str | None = None
    current_ns: str | None = None
    current_parents: set[str] = set()
    in_term = False

    def finalize_term() -> None:
        nonlocal current_go, current_ns, current_parents
        if current_go:
            if current_ns:
                go_to_namespace[current_go] = current_ns
            go_to_parents[current_go] = set(current_parents)

    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                if in_term:
                    finalize_term()
                current_go = None
                current_ns = None
                current_parents = set()
                in_term = False
                continue

            if line.startswith("format-version:"):
                format_version = line.split(":", 1)[1].strip()
                continue
            if line.startswith("data-version:"):
                data_version = line.split(":", 1)[1].strip()
                continue

            if line == "[Term]":
                if in_term:
                    finalize_term()
                current_go = None
                current_ns = None
                current_parents = set()
                in_term = True
                continue

            if not in_term:
                continue

            if line.startswith("id: GO:"):
                current_go = line.split(": ", 1)[1].strip()
            elif line.startswith("namespace:"):
                current_ns = line.split(": ", 1)[1].strip()
            elif line.startswith("is_a: GO:"):
                current_parents.add(line.split()[1])

    if in_term:
        finalize_term()

    return go_to_namespace, go_to_parents, OboMeta(
        format_version=format_version, data_version=data_version
    )


def read_obo_namespace_map(path: Path) -> tuple[dict[str, str], OboMeta]:
    go_to_namespace, _, meta = read_obo_graph(path)
    return go_to_namespace, meta
