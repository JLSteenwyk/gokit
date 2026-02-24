from __future__ import annotations

import json
from pathlib import Path

from gokit.cli.main import main


def test_benchmark_writes_json(tmp_path: Path) -> None:
    out = tmp_path / "bench.json"
    rc = main(
        [
            "benchmark",
            "--iterations",
            "2",
            "--population-size",
            "300",
            "--study-size",
            "40",
            "--go-terms",
            "120",
            "--out",
            str(out),
        ]
    )
    assert rc == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "cold_elapsed_seconds" in payload
    assert "warm_elapsed_seconds" in payload
    assert payload["cold_total_rows"] >= 0
    assert payload["warm_total_rows"] >= 0
