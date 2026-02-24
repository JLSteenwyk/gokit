from __future__ import annotations

from pathlib import Path

from gokit.report.figures import (
    filter_rows,
    read_enrichment_tsv,
    resolve_output_path,
    summarize_direction_counts,
    top_rows,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_read_and_filter_rows(tmp_path: Path) -> None:
    tsv = tmp_path / "all_studies.tsv"
    _write(
        tsv,
        "\n".join(
            [
                "study_id\tGO\tNS\tdirection\tstudy_count\tstudy_n\tpop_count\tpop_n\tp_uncorrected\tp_adjusted",
                "study_a\tGO:0001\tBP\tover\t5\t10\t10\t100\t0.001\t0.01",
                "study_a\tGO:0002\tBP\tunder\t1\t10\t20\t100\t0.002\t0.02",
                "study_b\tGO:0003\tMF\tover\t3\t10\t30\t100\t0.01\t0.1",
                "",
            ]
        ),
    )

    rows = read_enrichment_tsv(tsv)
    assert len(rows) == 3
    bp_over = filter_rows(rows, namespace="BP", direction="over", study_id="study_a")
    assert len(bp_over) == 1
    assert bp_over[0].go_id == "GO:0001"


def test_summary_and_top_rows(tmp_path: Path) -> None:
    tsv = tmp_path / "goea.tsv"
    _write(
        tsv,
        "\n".join(
            [
                "GO\tNS\tdirection\tstudy_count\tstudy_n\tpop_count\tpop_n\tp_uncorrected\tp_adjusted",
                "GO:0001\tBP\tover\t5\t10\t10\t100\t0.001\t0.01",
                "GO:0002\tBP\tunder\t1\t10\t20\t100\t0.002\t0.02",
                "GO:0003\tMF\tover\t3\t10\t30\t100\t0.01\t0.1",
                "",
            ]
        ),
    )
    rows = read_enrichment_tsv(tsv)

    summary = summarize_direction_counts(rows, alpha=0.05)
    assert summary["BP"]["over"] == 1
    assert summary["BP"]["under"] == 1
    assert "MF" not in summary

    top = top_rows(rows, 2)
    assert len(top) == 2
    assert top[0].go_id == "GO:0001"


def test_resolve_output_path() -> None:
    assert resolve_output_path(Path("out/figure"), "png").as_posix().endswith("figure.png")
    assert resolve_output_path(Path("out/figure.svg"), "png").as_posix().endswith("figure.svg")
