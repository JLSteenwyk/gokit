from __future__ import annotations

import json
from pathlib import Path

from gokit.cli.main import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_enrich_outputs_rows(tmp_path: Path) -> None:
    study = tmp_path / "study.txt"
    population = tmp_path / "population.txt"
    assoc = tmp_path / "assoc.txt"
    obo = tmp_path / "go-basic.obo"

    _write(study, "gene1\ngene2\n")
    _write(population, "gene1\ngene2\ngene3\ngene4\n")
    _write(
        assoc,
        "\n".join(
            [
                "gene1 GO:0000001",
                "gene2 GO:0000001",
                "gene3 GO:0000002",
                "gene4 GO:0000002",
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
                "namespace: molecular_function",
                "",
            ]
        ),
    )

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
            "--namespace",
            "all",
            "--out",
            str(out_prefix),
            "--out-formats",
            "tsv,jsonl",
        ]
    )

    assert rc == 0
    tsv = out_prefix.with_suffix(".tsv")
    assert tsv.exists()
    lines = tsv.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 2
    assert lines[0].startswith("GO\tNS\tdirection\t")
    body = "\n".join(lines[1:])
    assert "\tover\t" in body
    assert "\tunder\t" in body


def test_enrich_method_flag_changes_adjustment(tmp_path: Path) -> None:
    study = tmp_path / "study.txt"
    population = tmp_path / "population.txt"
    assoc = tmp_path / "assoc.txt"
    obo = tmp_path / "go-basic.obo"

    _write(study, "gene1\ngene2\n")
    _write(population, "gene1\ngene2\ngene3\ngene4\n")
    _write(
        assoc,
        "\n".join(
            [
                "gene1 GO:0000001",
                "gene2 GO:0000001",
                "gene3 GO:0000002",
                "gene4 GO:0000002",
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
                "",
                "[Term]",
                "id: GO:0000001",
                "namespace: biological_process",
                "",
                "[Term]",
                "id: GO:0000002",
                "namespace: biological_process",
                "",
                "[Term]",
                "id: GO:0000003",
                "namespace: molecular_function",
                "",
            ]
        ),
    )

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
            "--method",
            "bonferroni",
            "--out",
            str(out_prefix),
            "--out-formats",
            "jsonl",
        ]
    )
    assert rc == 0
    rows = [json.loads(line) for line in out_prefix.with_suffix(".jsonl").read_text(encoding="utf-8").splitlines()]
    assert rows
    assert any(abs(r["p_adjusted"] - 0.5) < 1e-12 for r in rows)
