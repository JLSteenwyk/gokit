from __future__ import annotations

from pathlib import Path

from gokit.cache.obo_cache import load_or_build_obo_cache


def _obo_text(version: str) -> str:
    return "\n".join(
        [
            "format-version: 1.2",
            f"data-version: {version}",
            "",
            "[Term]",
            "id: GO:0000001",
            "namespace: biological_process",
            "",
            "[Term]",
            "id: GO:0000002",
            "namespace: molecular_function",
            "is_a: GO:0000001 ! parent",
            "",
        ]
    )


def test_obo_cache_hit_and_ancestors(tmp_path: Path) -> None:
    obo = tmp_path / "go.obo"
    obo.write_text(_obo_text("v1"), encoding="utf-8")

    first = load_or_build_obo_cache(obo, tmp_path / "cache")
    second = load_or_build_obo_cache(obo, tmp_path / "cache")

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert "GO:0000001" in first.go_to_ancestors["GO:0000002"]


def test_obo_cache_invalidation_by_content(tmp_path: Path) -> None:
    obo = tmp_path / "go.obo"
    cache_dir = tmp_path / "cache"

    obo.write_text(_obo_text("v1"), encoding="utf-8")
    first = load_or_build_obo_cache(obo, cache_dir)

    obo.write_text(_obo_text("v2"), encoding="utf-8")
    second = load_or_build_obo_cache(obo, cache_dir)

    assert second.cache_hit is False
    assert first.cache_path != second.cache_path
