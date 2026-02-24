from __future__ import annotations

from pathlib import Path

import pytest

from gokit.cli.main import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_enrich_emit_plots_single(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")

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
            "--out",
            str(out_prefix),
            "--emit-plots",
            "term-bar,direction-summary",
            "--plot-alpha",
            "1.0",
        ]
    )
    assert rc == 0
    fig_dir = out_prefix.parent / "figures"
    assert (fig_dir / "goea.term_bar.png").exists()
    assert (fig_dir / "goea.direction_summary.png").exists()
