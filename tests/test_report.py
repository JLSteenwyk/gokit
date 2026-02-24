from __future__ import annotations

import json
from pathlib import Path

from gokit.cli.main import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_report_generates_markdown_from_tsv_and_manifest(tmp_path: Path) -> None:
    run_prefix = tmp_path / "run" / "goea"
    tsv = run_prefix.with_suffix(".tsv")
    manifest = Path(str(run_prefix) + ".manifest.json")
    _write(
        tsv,
        "\n".join(
            [
                "GO\tNS\tdirection\tstudy_count\tstudy_n\tpop_count\tpop_n\tp_uncorrected\tp_adjusted",
                "GO:0001\tBP\tover\t5\t10\t10\t100\t0.001\t0.01",
                "GO:0002\tMF\tunder\t1\t10\t20\t100\t0.02\t0.2",
                "",
            ]
        ),
    )
    manifest.write_text(
        json.dumps(
            {
                "command": "gokit enrich",
                "created_at_utc": "2026-02-24T00:00:00+00:00",
                "method": "fdr_bh",
                "alpha": 0.05,
                "namespace": "all",
            }
        ),
        encoding="utf-8",
    )

    rc = main(["report", "--run", str(run_prefix)])
    assert rc == 0
    out = Path(str(run_prefix) + ".report.md")
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "GOKIT Run Report" in text
    assert "GO:0001" in text
