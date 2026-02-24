from __future__ import annotations

from pathlib import Path

from gokit.cli.main import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_batch_mode_and_semantic_output(tmp_path: Path) -> None:
    pop = tmp_path / "population.txt"
    assoc = tmp_path / "assoc.txt"
    obo = tmp_path / "go-basic.obo"

    s1 = tmp_path / "s1.txt"
    s2 = tmp_path / "s2.txt"
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
                "data-version: batch-test",
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

    _write(s1, "gene1\ngene2\n")
    _write(s2, "gene3\ngene4\n")
    _write(studies, f"study_a\t{s1}\nstudy_b\t{s2}\n")

    out_dir = tmp_path / "out"
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
            str(out_dir),
            "--out-formats",
            "tsv,jsonl",
            "--compare-semantic",
            "--semantic-metric",
            "resnik",
        ]
    )

    assert rc == 0
    assert (out_dir / "studies" / "study_a.tsv").exists()
    assert (out_dir / "studies" / "study_b.tsv").exists()
    assert (out_dir / "all_studies.tsv").exists()
    assert (out_dir / "all_studies.jsonl").exists()
    assert (out_dir / "semantic_similarity.tsv").exists()
    assert (out_dir / "semantic_top_pairs.tsv").exists()

    matrix = (out_dir / "semantic_similarity.tsv").read_text(encoding="utf-8")
    assert "study_a" in matrix
    assert "study_b" in matrix
