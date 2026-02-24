from __future__ import annotations

from pathlib import Path

from gokit.cli.main import main


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_golden_single_outputs(tmp_path: Path) -> None:
    root = Path("tests/golden/single")
    inp = root / "input"
    exp = root / "expected"

    out_prefix = tmp_path / "single" / "goea"
    cache_dir = tmp_path / "cache_single"

    rc = main(
        [
            "enrich",
            "--study",
            str(inp / "study.txt"),
            "--population",
            str(inp / "population.txt"),
            "--assoc",
            str(inp / "assoc.txt"),
            "--assoc-format",
            "id2gos",
            "--obo",
            str(inp / "go-basic.obo"),
            "--cache-dir",
            str(cache_dir),
            "--out",
            str(out_prefix),
            "--out-formats",
            "tsv,jsonl",
        ]
    )
    assert rc == 0

    assert _read(out_prefix.with_suffix(".tsv")) == _read(exp / "goea.tsv")
    assert _read(out_prefix.with_suffix(".jsonl")) == _read(exp / "goea.jsonl")
    assert _read(out_prefix.with_suffix(".summary.tsv")) == _read(exp / "goea.summary.tsv")


def test_golden_batch_outputs(tmp_path: Path) -> None:
    root = Path("tests/golden/batch")
    inp = root / "input"
    exp = root / "expected"

    out_dir = tmp_path / "batch_out"
    cache_dir = tmp_path / "cache_batch"

    rc = main(
        [
            "enrich",
            "--studies",
            str(inp / "studies.tsv"),
            "--population",
            str(inp / "population.txt"),
            "--assoc",
            str(inp / "assoc.txt"),
            "--assoc-format",
            "id2gos",
            "--obo",
            str(inp / "go-basic.obo"),
            "--cache-dir",
            str(cache_dir),
            "--out",
            str(out_dir),
            "--out-formats",
            "tsv,jsonl",
            "--compare-semantic",
            "--semantic-metric",
            "jaccard",
            "--semantic-top-k",
            "5",
        ]
    )
    assert rc == 0

    checks = [
        (out_dir / "all_studies.tsv", exp / "all_studies.tsv"),
        (out_dir / "all_studies.jsonl", exp / "all_studies.jsonl"),
        (out_dir / "grouped_summary.tsv", exp / "grouped_summary.tsv"),
        (out_dir / "semantic_similarity.tsv", exp / "semantic_similarity.tsv"),
        (out_dir / "semantic_top_pairs.tsv", exp / "semantic_top_pairs.tsv"),
        (out_dir / "studies" / "study_a.tsv", exp / "studies" / "study_a.tsv"),
        (out_dir / "studies" / "study_a.jsonl", exp / "studies" / "study_a.jsonl"),
        (out_dir / "studies" / "study_a.summary.tsv", exp / "studies" / "study_a.summary.tsv"),
        (out_dir / "studies" / "study_b.tsv", exp / "studies" / "study_b.tsv"),
        (out_dir / "studies" / "study_b.jsonl", exp / "studies" / "study_b.jsonl"),
        (out_dir / "studies" / "study_b.summary.tsv", exp / "studies" / "study_b.summary.tsv"),
    ]

    for got, expected in checks:
        assert _read(got) == _read(expected)
