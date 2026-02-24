from __future__ import annotations

import json
from pathlib import Path

from gokit.cli.main import build_parser, main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_parser_has_expected_commands() -> None:
    parser = build_parser()
    help_text = parser.format_help()
    for cmd in ["enrich", "validate", "benchmark", "cache", "explain", "plot", "download", "report"]:
        assert cmd in help_text


def test_validate_fails_on_missing_inputs(tmp_path: Path) -> None:
    rc = main(
        [
            "validate",
            "--study",
            str(tmp_path / "missing_study.txt"),
            "--population",
            str(tmp_path / "missing_population.txt"),
            "--assoc",
            str(tmp_path / "missing_assoc.txt"),
            "--obo",
            str(tmp_path / "missing.obo"),
        ]
    )
    assert rc == 1


def test_enrich_writes_manifest(tmp_path: Path) -> None:
    study = tmp_path / "study.txt"
    population = tmp_path / "population.txt"
    assoc = tmp_path / "assoc.txt"
    obo = tmp_path / "go-basic.obo"

    _write(study, "gene1\ngene2\n")
    _write(population, "gene1\ngene2\ngene3\n")
    _write(assoc, "gene1\tGO:0008150\n")
    _write(obo, "format-version: 1.2\n")

    out_prefix = tmp_path / "results" / "goea"
    rc = main(
        [
            "enrich",
            "--study",
            str(study),
            "--population",
            str(population),
            "--assoc",
            str(assoc),
            "--obo",
            str(obo),
            "--out",
            str(out_prefix),
            "--out-formats",
            "tsv,jsonl",
        ]
    )

    assert rc == 0
    manifest_path = out_prefix.with_suffix(".manifest.json")
    assert manifest_path.exists()

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1"
    assert payload["command"] == "gokit enrich"
    assert len(payload["inputs"]) == 4
