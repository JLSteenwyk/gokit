from __future__ import annotations

from pathlib import Path

from gokit.io.assoc import read_associations


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_read_gaf(tmp_path: Path) -> None:
    gaf = tmp_path / "mini.gaf"
    _write(
        gaf,
        "\n".join(
            [
                "!gaf-version: 2.2",
                "UniProtKB\tP12345\tGENE1\t\tGO:0000001\tPMID:1\tIDA\t\tF\tName\t\tprotein\ttaxon:9606\t20240101\tUniProt",
                "UniProtKB\tP99999\tGENE2\t\tGO:0000002\tPMID:2\tIDA\t\tF\tName\t\tprotein\ttaxon:9606\t20240101\tUniProt",
            ]
        )
        + "\n",
    )
    assoc = read_associations(gaf, "gaf")
    assert assoc["P12345"] == {"GO:0000001"}
    assert assoc["P99999"] == {"GO:0000002"}


def test_read_gpad(tmp_path: Path) -> None:
    gpad = tmp_path / "mini.gpad"
    _write(
        gpad,
        "\n".join(
            [
                "!gpa-version: 2.0",
                "UniProtKB\tP12345\t\tGO:0000001\tPMID:1\tECO:0000000\t\t\t20240101\tUniProt",
                "UniProtKB\tP99999\t\tGO:0000002\tPMID:2\tECO:0000000\t\t\t20240101\tUniProt",
            ]
        )
        + "\n",
    )
    assoc = read_associations(gpad, "gpad")
    assert assoc["P12345"] == {"GO:0000001"}
    assert assoc["P99999"] == {"GO:0000002"}


def test_read_gene2go(tmp_path: Path) -> None:
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
    assoc = read_associations(gene2go, "gene2go")
    assert assoc["101"] == {"GO:0000001"}
    assert assoc["102"] == {"GO:0000002"}


def test_auto_detection(tmp_path: Path) -> None:
    gene2go = tmp_path / "gene2go"
    _write(
        gene2go,
        "#tax_id\tGeneID\tGO_ID\n9606\t101\tGO:0000001\n",
    )
    assoc = read_associations(gene2go, "auto")
    assert assoc["101"] == {"GO:0000001"}
