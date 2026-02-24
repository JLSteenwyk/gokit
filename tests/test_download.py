from __future__ import annotations

from pathlib import Path

from gokit.cli import download
from gokit.cli.main import main


def test_download_writes_expected_files(tmp_path: Path, monkeypatch) -> None:
    def fake_urlretrieve(url: str, dst: Path):
        Path(dst).write_text(f"downloaded from {url}\n", encoding="utf-8")
        return str(dst), None

    monkeypatch.setattr(download, "urlretrieve", fake_urlretrieve)

    rc = main(["download", "--out-dir", str(tmp_path)])
    assert rc == 0
    assert (tmp_path / "go-basic.obo").exists()
    assert (tmp_path / "goslim_generic.obo").exists()
