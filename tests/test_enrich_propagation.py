from __future__ import annotations

import json
from pathlib import Path

from gokit.cli.main import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path]:
    study = tmp_path / "study.txt"
    population = tmp_path / "population.txt"
    assoc = tmp_path / "assoc.txt"
    obo = tmp_path / "go-basic.obo"
    cache_dir = tmp_path / "cache"

    _write(study, "gene1\ngene2\n")
    _write(population, "gene1\ngene2\ngene3\ngene4\n")
    _write(
        assoc,
        "\n".join(
            [
                "gene1 GO:0000002",
                "gene2 GO:0000002",
                "gene3 GO:0000003",
                "gene4 GO:0000003",
            ]
        )
        + "\n",
    )
    _write(
        obo,
        "\n".join(
            [
                "format-version: 1.2",
                "data-version: test-release",
                "",
                "[Term]",
                "id: GO:0000001",
                "namespace: biological_process",
                "",
                "[Term]",
                "id: GO:0000002",
                "namespace: biological_process",
                "is_a: GO:0000001 ! parent",
                "",
                "[Term]",
                "id: GO:0000003",
                "namespace: molecular_function",
                "",
            ]
        ),
    )
    return study, population, assoc, obo, cache_dir


def test_enrich_uses_propagation_by_default(tmp_path: Path) -> None:
    study, population, assoc, obo, cache_dir = _fixture(tmp_path)
    out_prefix = tmp_path / "out" / "goea"

    rc = main(
        [
            "enrich",
            "--study",
            str(study),
            "--population",
            str(population),
            "--assoc",
            str(assoc),
            "--assoc-format",
            "id2gos",
            "--obo",
            str(obo),
            "--cache-dir",
            str(cache_dir),
            "--out",
            str(out_prefix),
            "--out-formats",
            "jsonl",
        ]
    )
    assert rc == 0

    rows = [
        json.loads(line)
        for line in out_prefix.with_suffix(".jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    go_ids = {r["go_id"] for r in rows}
    assert "GO:0000001" in go_ids


def test_enrich_can_disable_propagation(tmp_path: Path) -> None:
    study, population, assoc, obo, cache_dir = _fixture(tmp_path)
    out_prefix = tmp_path / "out2" / "goea"

    rc = main(
        [
            "enrich",
            "--study",
            str(study),
            "--population",
            str(population),
            "--assoc",
            str(assoc),
            "--assoc-format",
            "id2gos",
            "--obo",
            str(obo),
            "--cache-dir",
            str(cache_dir),
            "--no-propagate-counts",
            "--out",
            str(out_prefix),
            "--out-formats",
            "jsonl",
        ]
    )
    assert rc == 0

    rows = [
        json.loads(line)
        for line in out_prefix.with_suffix(".jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    go_ids = {r["go_id"] for r in rows}
    assert "GO:0000001" not in go_ids
