"""Study/population gene list readers."""

from __future__ import annotations

from pathlib import Path


def read_gene_set(path: Path) -> set[str]:
    genes: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            genes.add(line)
    return genes


def read_study_manifest(path: Path) -> list[tuple[str, Path]]:
    """Read study manifest lines as either:
    - <study_name>\\t<study_path>
    - <study_path>
    """
    rows: list[tuple[str, Path]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                name = parts[0].strip()
                study_path = Path(parts[1].strip())
            else:
                study_path = Path(parts[0].strip())
                name = study_path.stem
            if not name:
                name = study_path.stem
            rows.append((name, study_path))
    return rows
