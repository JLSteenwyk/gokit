from __future__ import annotations

from pathlib import Path

from gokit.cli.main import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _common_obo(path: Path) -> None:
    _write(
        path,
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


def test_enrich_with_gaf_gpad_gene2go(tmp_path: Path) -> None:
    pop = tmp_path / "population.txt"
    study = tmp_path / "study.txt"
    obo = tmp_path / "go-basic.obo"
    _write(pop, "A\nB\nC\nD\n101\n102\n")
    _write(study, "A\nB\n101\n")
    _common_obo(obo)

    gaf = tmp_path / "mini.gaf"
    _write(
        gaf,
        "\n".join(
            [
                "!gaf-version: 2.2",
                "UniProtKB\tA\tGENEA\t\tGO:0000001\tPMID:1\tIDA\t\tF\tName\t\tprotein\ttaxon:9606\t20240101\tUniProt",
                "UniProtKB\tB\tGENEB\t\tGO:0000001\tPMID:2\tIDA\t\tF\tName\t\tprotein\ttaxon:9606\t20240101\tUniProt",
                "UniProtKB\tC\tGENEC\t\tGO:0000002\tPMID:3\tIDA\t\tF\tName\t\tprotein\ttaxon:9606\t20240101\tUniProt",
            ]
        )
        + "\n",
    )

    gpad = tmp_path / "mini.gpad"
    _write(
        gpad,
        "\n".join(
            [
                "!gpa-version: 2.0",
                "UniProtKB\tA\t\tGO:0000001\tPMID:1\tECO:0000000\t\t\t20240101\tUniProt",
                "UniProtKB\tB\t\tGO:0000001\tPMID:2\tECO:0000000\t\t\t20240101\tUniProt",
                "UniProtKB\tD\t\tGO:0000002\tPMID:3\tECO:0000000\t\t\t20240101\tUniProt",
            ]
        )
        + "\n",
    )

    gene2go = tmp_path / "gene2go"
    _write(
        gene2go,
        "\n".join(
            [
                "#tax_id\tGeneID\tGO_ID\tEvidence\tQualifier\tGO_term\tPubMed\tCategory",
                "9606\t101\tGO:0000001\tIEA\t\tterm\t1\tProcess",
                "9606\t102\tGO:0000002\tIEA\t\tterm\t1\tFunction",
            ]
        )
        + "\n",
    )

    for fmt, assoc in [("gaf", gaf), ("gpad", gpad), ("gene2go", gene2go)]:
        out = tmp_path / f"out_{fmt}" / "goea"
        rc = main(
            [
                "enrich",
                "--study",
                str(study),
                "--population",
                str(pop),
                "--assoc",
                str(assoc),
                "--assoc-format",
                fmt,
                "--obo",
                str(obo),
                "--out",
                str(out),
                "--out-formats",
                "tsv",
            ]
        )
        assert rc == 0
        text = out.with_suffix(".tsv").read_text(encoding="utf-8")
        assert "GO\tNS\t" in text
