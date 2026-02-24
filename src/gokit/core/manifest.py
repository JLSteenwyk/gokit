"""Run manifest helpers."""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from gokit import __version__


@dataclass
class InputFile:
    label: str
    path: str
    sha256: str
    size_bytes: int


@dataclass
class RunManifest:
    schema_version: str
    command: str
    created_at_utc: str
    gokit_version: str
    python_version: str
    platform: str
    seed: int | None
    alpha: float
    method: str
    namespace: str
    relationships: list[str]
    out_formats: list[str]
    inputs: list[InputFile]
    notes: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def build_input_files(named_paths: Iterable[tuple[str, Path]]) -> list[InputFile]:
    records: list[InputFile] = []
    for label, path in named_paths:
        records.append(
            InputFile(
                label=label,
                path=str(path),
                sha256=sha256_file(path),
                size_bytes=path.stat().st_size,
            )
        )
    return records


def write_manifest(path: Path, manifest: RunManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(manifest)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def runtime_platform() -> str:
    return f"{platform.system()} {platform.release()}"


def runtime_python() -> str:
    return platform.python_version()


def default_manifest(
    *,
    command: str,
    seed: int | None,
    alpha: float,
    method: str,
    namespace: str,
    relationships: list[str],
    out_formats: list[str],
    input_files: list[InputFile],
    notes: str,
) -> RunManifest:
    return RunManifest(
        schema_version="1",
        command=command,
        created_at_utc=now_utc_iso(),
        gokit_version=__version__,
        python_version=runtime_python(),
        platform=runtime_platform(),
        seed=seed,
        alpha=alpha,
        method=method,
        namespace=namespace,
        relationships=relationships,
        out_formats=out_formats,
        inputs=input_files,
        notes=notes,
    )
