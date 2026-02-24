from __future__ import annotations

from pathlib import Path

from gokit.cli.main import main
from gokit.core.idnorm import infer_id_mode, normalize_assoc_keys, normalize_gene_set


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_idnorm_infer_prefers_int_when_overlap_better() -> None:
    pop = {"00101", "00102", "00103"}
    assoc = {"101", "102", "999"}
    assert infer_id_mode(pop, assoc) == "int"


def test_idnorm_normalize_assoc_merges_on_int_mode() -> None:
    assoc = {
        "00101": {"GO:0000001"},
        "101": {"GO:0000002"},
    }
    out = normalize_assoc_keys(assoc, "int")
    assert out["101"] == {"GO:0000001", "GO:0000002"}


def test_enrich_with_gene2go_and_auto_id_type(tmp_path: Path) -> None:
    study = tmp_path / "study.txt"
    population = tmp_path / "population.txt"
    gene2go = tmp_path / "gene2go"
    obo = tmp_path / "go-basic.obo"

    _write(study, "00101\n00102\n")
    _write(population, "00101\n00102\n00103\n")
    _write(
        gene2go,
        "\n".join(
            [
                "#tax_id\tGeneID\tGO_ID\tEvidence\tQualifier\tGO_term\tPubMed\tCategory",
                "9606\t101\tGO:0000001\tIEA\t\tterm\t1\tProcess",
                "9606\t102\tGO:0000001\tIEA\t\tterm\t1\tProcess",
                "9606\t103\tGO:0000002\tIEA\t\tterm\t1\tFunction",
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
                "namespace: molecular_function",
                "",
            ]
        ),
    )

    out = tmp_path / "out" / "goea"
    rc = main(
        [
            "enrich",
            "--study",
            str(study),
            "--population",
            str(population),
            "--assoc",
            str(gene2go),
            "--assoc-format",
            "gene2go",
            "--id-type",
            "auto",
            "--obo",
            str(obo),
            "--out",
            str(out),
            "--out-formats",
            "tsv",
        ]
    )
    assert rc == 0
    tsv = out.with_suffix(".tsv").read_text(encoding="utf-8")
    assert "GO:0000001" in tsv


def test_enrich_with_gene2go_str_id_type_can_drop_overlap(tmp_path: Path) -> None:
    study = tmp_path / "study.txt"
    population = tmp_path / "population.txt"
    gene2go = tmp_path / "gene2go"
    obo = tmp_path / "go-basic.obo"

    _write(study, "00101\n00102\n")
    _write(population, "00101\n00102\n00103\n")
    _write(
        gene2go,
        "\n".join(
            [
                "#tax_id\tGeneID\tGO_ID\tEvidence\tQualifier\tGO_term\tPubMed\tCategory",
                "9606\t101\tGO:0000001\tIEA\t\tterm\t1\tProcess",
                "9606\t102\tGO:0000001\tIEA\t\tterm\t1\tProcess",
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
            ]
        ),
    )

    out = tmp_path / "out" / "goea"
    rc = main(
        [
            "enrich",
            "--study",
            str(study),
            "--population",
            str(population),
            "--assoc",
            str(gene2go),
            "--assoc-format",
            "gene2go",
            "--id-type",
            "str",
            "--obo",
            str(obo),
            "--out",
            str(out),
            "--out-formats",
            "tsv",
        ]
    )
    assert rc == 0
    lines = out.with_suffix(".tsv").read_text(encoding="utf-8").strip().splitlines()
    # Header only expected because IDs do not match without int normalization.
    assert len(lines) == 1
