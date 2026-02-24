"""Shared CLI helpers."""

from __future__ import annotations

from pathlib import Path


def parse_csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def require_existing_file(path: str, label: str) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{label} not found: {p}")
    if not p.is_file():
        raise FileNotFoundError(f"{label} is not a file: {p}")
    if p.stat().st_size == 0:
        raise ValueError(f"{label} is empty: {p}")
    return p


def write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
