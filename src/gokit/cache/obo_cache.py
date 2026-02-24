"""On-disk OBO cache and ancestor closure utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from gokit.core.manifest import sha256_file
from gokit.io.obo import OboMeta, read_obo_graph


@dataclass
class OboCached:
    go_to_namespace: dict[str, str]
    go_to_parents: dict[str, set[str]]
    go_to_ancestors: dict[str, set[str]]
    meta: OboMeta
    cache_hit: bool
    cache_path: Path


def default_cache_dir() -> Path:
    return Path.home() / ".cache" / "gokit"


def _cache_file_for(obo_path: Path, cache_dir: Path) -> Path:
    key = sha256_file(obo_path)
    return cache_dir / "obo" / f"{key}.json"


def _compute_ancestors(go_to_parents: dict[str, set[str]]) -> dict[str, set[str]]:
    memo: dict[str, set[str]] = {}

    def dfs(goid: str) -> set[str]:
        if goid in memo:
            return memo[goid]
        parents = go_to_parents.get(goid, set())
        closure: set[str] = set(parents)
        for parent in parents:
            closure.update(dfs(parent))
        memo[goid] = closure
        return closure

    for goid in go_to_parents:
        dfs(goid)
    return memo


def _serialize_setmap(data: dict[str, set[str]]) -> dict[str, list[str]]:
    return {k: sorted(v) for k, v in data.items()}


def _deserialize_setmap(data: dict[str, list[str]]) -> dict[str, set[str]]:
    return {k: set(v) for k, v in data.items()}


def load_or_build_obo_cache(obo_path: Path, cache_dir: Path | None = None) -> OboCached:
    base = cache_dir or default_cache_dir()
    base.mkdir(parents=True, exist_ok=True)
    cache_path = _cache_file_for(obo_path, base)

    if cache_path.exists():
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        return OboCached(
            go_to_namespace=payload["go_to_namespace"],
            go_to_parents=_deserialize_setmap(payload["go_to_parents"]),
            go_to_ancestors=_deserialize_setmap(payload["go_to_ancestors"]),
            meta=OboMeta(
                format_version=payload.get("format_version"),
                data_version=payload.get("data_version"),
            ),
            cache_hit=True,
            cache_path=cache_path,
        )

    go_to_namespace, go_to_parents, meta = read_obo_graph(obo_path)
    go_to_ancestors = _compute_ancestors(go_to_parents)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "obo_path": str(obo_path),
        "obo_sha256": sha256_file(obo_path),
        "format_version": meta.format_version,
        "data_version": meta.data_version,
        "go_to_namespace": go_to_namespace,
        "go_to_parents": _serialize_setmap(go_to_parents),
        "go_to_ancestors": _serialize_setmap(go_to_ancestors),
    }
    cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return OboCached(
        go_to_namespace=go_to_namespace,
        go_to_parents=go_to_parents,
        go_to_ancestors=go_to_ancestors,
        meta=meta,
        cache_hit=False,
        cache_path=cache_path,
    )
