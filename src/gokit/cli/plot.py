"""plot subcommand."""

from __future__ import annotations

import argparse
from pathlib import Path

from gokit.cli.common import require_existing_file
from gokit.report.figures import (
    filter_rows,
    read_enrichment_tsv,
    render_direction_summary,
    render_term_bar,
    resolve_output_path,
)


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("plot", help="Generate figures from enrichment TSV outputs")
    parser.add_argument("--input", required=True, help="Input enrichment TSV path")
    parser.add_argument("--out", required=True, help="Output figure path or prefix")
    parser.add_argument("--format", default="png", choices=["png", "svg", "pdf"])
    parser.add_argument("--kind", default="term-bar", choices=["term-bar", "direction-summary"])
    parser.add_argument("--top-n", type=int, default=20, help="Top terms to plot for term-bar")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance threshold for summary plots")
    parser.add_argument("--namespace", default="all", choices=["BP", "MF", "CC", "all"])
    parser.add_argument("--direction", default="both", choices=["over", "under", "both"])
    parser.add_argument("--study-id", default="", help="Optional study ID filter for batch tables")
    parser.add_argument("--title", default="", help="Optional custom figure title")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    input_path = require_existing_file(args.input, "input")
    out_path = resolve_output_path(Path(args.out), args.format)

    rows = read_enrichment_tsv(input_path)
    rows = filter_rows(
        rows,
        namespace=args.namespace,
        direction=args.direction,
        study_id=args.study_id,
    )
    if not rows:
        print("No rows remain after applying plot filters.")
        return 1

    try:
        if args.kind == "term-bar":
            render_term_bar(rows, out=out_path, top_n=args.top_n, title=args.title)
        else:
            render_direction_summary(rows, out=out_path, alpha=args.alpha, title=args.title)
    except (RuntimeError, ValueError) as exc:
        print(str(exc))
        return 1

    print(f"Figure written: {out_path}")
    return 0
