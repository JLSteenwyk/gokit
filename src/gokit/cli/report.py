"""report subcommand."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "report",
        help="Build a consolidated markdown report for a gokit run",
    )
    parser.add_argument("--run", required=True, help="Run directory, output prefix, or TSV file")
    parser.add_argument(
        "--out",
        default="",
        help="Report markdown path (default: <run>/run_report.md)",
    )
    parser.add_argument("--top-n", type=int, default=10, help="Top terms to include")
    parser.set_defaults(func=run)


def _find_manifest(run_path: Path) -> Path | None:
    if (
        run_path.is_file()
        and run_path.suffix == ".json"
        and run_path.name.endswith(".manifest.json")
    ):
        return run_path
    if run_path.exists():
        candidate = Path(str(run_path) + ".manifest.json")
        if candidate.exists():
            return candidate
    if run_path.is_dir():
        local = sorted(run_path.glob("*.manifest.json"))
        if local:
            return local[0]
    return None


def _find_primary_tsv(run_path: Path) -> Path:
    if run_path.is_file() and run_path.suffix == ".tsv":
        return run_path
    candidate = Path(str(run_path) + ".tsv")
    if candidate.exists():
        return candidate
    if run_path.is_dir():
        batch = run_path / "all_studies.tsv"
        if batch.exists():
            return batch
        single = sorted(run_path.glob("*.tsv"))
        for p in single:
            if not p.name.endswith(".summary.tsv"):
                return p
    raise FileNotFoundError("Could not locate a primary enrichment TSV for report generation.")


def _read_tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _sort_rows(rows: list[dict[str, str]], top_n: int) -> list[dict[str, str]]:
    def _padj(row: dict[str, str]) -> float:
        raw = row.get("p_adjusted", "1")
        try:
            return float(raw)
        except ValueError:
            return 1.0

    return sorted(
        rows,
        key=lambda r: (_padj(r), r.get("GO", r.get("go_id", ""))),
    )[: max(1, top_n)]


def _default_out(run_path: Path) -> Path:
    if run_path.is_dir():
        return run_path / "run_report.md"
    if run_path.suffix == ".tsv":
        return run_path.with_suffix(".report.md")
    return Path(str(run_path) + ".report.md")


def run(args: argparse.Namespace) -> int:
    run_path = Path(args.run)
    # Accept either existing directories/files or output prefixes.
    out_path = Path(args.out) if args.out else _default_out(run_path)
    manifest_path = _find_manifest(run_path)
    try:
        tsv_path = _find_primary_tsv(run_path)
    except FileNotFoundError:
        print(f"Run path does not exist or no TSV found for report input: {run_path}")
        return 1

    rows = _read_tsv_rows(tsv_path)
    top = _sort_rows(rows, args.top_n)

    manifest = {}
    if manifest_path:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    lines: list[str] = []
    lines.append("# GOKIT Run Report")
    lines.append("")
    lines.append(f"- Primary table: `{tsv_path}`")
    lines.append(f"- Total rows: `{len(rows)}`")
    if manifest_path:
        lines.append(f"- Manifest: `{manifest_path}`")
    lines.append("")

    if manifest:
        lines.append("## Run Metadata")
        lines.append("")
        lines.append(f"- Command: `{manifest.get('command', 'na')}`")
        lines.append(f"- Created (UTC): `{manifest.get('created_at_utc', 'na')}`")
        lines.append(f"- Method: `{manifest.get('method', 'na')}`")
        lines.append(f"- Alpha: `{manifest.get('alpha', 'na')}`")
        lines.append(f"- Namespace: `{manifest.get('namespace', 'na')}`")
        lines.append("")

    lines.append("## Top Terms")
    lines.append("")
    if not top:
        lines.append("No rows found.")
    else:
        is_batch = "study_id" in top[0]
        if is_batch:
            lines.append("| study_id | GO | NS | direction | p_adjusted |")
            lines.append("|---|---|---|---:|---:|")
            for row in top:
                lines.append(
                    f"| {row.get('study_id','')} | {row.get('GO','')} | {row.get('NS','')} | "
                    f"{row.get('direction','')} | {row.get('p_adjusted','')} |"
                )
        else:
            lines.append("| GO | NS | direction | p_adjusted |")
            lines.append("|---|---|---|---:|")
            for row in top:
                lines.append(
                    f"| {row.get('GO','')} | {row.get('NS','')} | "
                    f"{row.get('direction','')} | {row.get('p_adjusted','')} |"
                )
    lines.append("")

    if run_path.is_dir():
        lines.append("## Output Files")
        lines.append("")
        for p in sorted(run_path.rglob("*")):
            if p.is_file():
                lines.append(f"- `{p.relative_to(run_path)}`")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report written: {out_path}")
    return 0
