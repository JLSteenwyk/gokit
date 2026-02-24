from __future__ import annotations

from pathlib import Path

from gokit.cli.main import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    pop = tmp_path / "population.txt"
    assoc = tmp_path / "assoc.txt"
    obo = tmp_path / "go-basic.obo"
    studies = tmp_path / "studies.tsv"

    _write(pop, "gene1\ngene2\ngene3\ngene4\n")
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
                "is_a: GO:0000001 ! parent",
                "",
            ]
        ),
    )
    _write(tmp_path / "study_a.txt", "gene1\ngene2\n")
    _write(tmp_path / "study_b.txt", "gene3\ngene4\n")
    _write(studies, f"study_a\t{tmp_path / 'study_a.txt'}\nstudy_b\t{tmp_path / 'study_b.txt'}\n")
    return pop, assoc, obo, studies


def test_semantic_namespace_filter_applied(tmp_path: Path) -> None:
    pop, assoc, obo, studies = _fixture(tmp_path)
    out = tmp_path / "out"

    rc = main(
        [
            "enrich",
            "--studies",
            str(studies),
            "--population",
            str(pop),
            "--assoc",
            str(assoc),
            "--assoc-format",
            "id2gos",
            "--obo",
            str(obo),
            "--out",
            str(out),
            "--out-formats",
            "tsv",
            "--compare-semantic",
            "--semantic-metric",
            "jaccard",
            "--semantic-namespace",
            "BP",
        ]
    )
    assert rc == 0
    pair_summary = (out / "semantic_pair_summary.tsv").read_text(encoding="utf-8")
    assert "study_a" in pair_summary
    assert "study_b" in pair_summary


def test_semantic_min_padjsig_filter_can_zero_terms(tmp_path: Path) -> None:
    pop, assoc, obo, studies = _fixture(tmp_path)
    out = tmp_path / "out2"

    rc = main(
        [
            "enrich",
            "--studies",
            str(studies),
            "--population",
            str(pop),
            "--assoc",
            str(assoc),
            "--assoc-format",
            "id2gos",
            "--obo",
            str(obo),
            "--out",
            str(out),
            "--out-formats",
            "tsv",
            "--compare-semantic",
            "--semantic-metric",
            "jaccard",
            "--semantic-min-padjsig",
            "1e-12",
        ]
    )
    assert rc == 0
    rows = (out / "semantic_pair_summary.tsv").read_text(encoding="utf-8").strip().splitlines()
    assert len(rows) >= 2
    # with strict threshold, raw term counts should be 0 for cross-study row
    cross = [r for r in rows[1:] if r.startswith("study_a\tstudy_b")][0]
    cols = cross.split("\t")
    assert cols[2] == "0"  # raw_a_terms
    assert cols[3] == "0"  # raw_b_terms
