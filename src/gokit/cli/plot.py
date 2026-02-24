"""plot subcommand."""

from __future__ import annotations

import argparse
from pathlib import Path

from gokit.cli.common import require_existing_file
from gokit.report.figures import (
    build_similarity_edges,
    filter_rows,
    read_enrichment_tsv,
    read_similarity_matrix,
    render_direction_summary,
    render_semantic_network,
    render_term_bar,
    resolve_output_path,
)


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("plot", help="Generate figures from enrichment TSV outputs")
    parser.add_argument("--input", required=True, help="Input enrichment TSV path")
    parser.add_argument("--out", required=True, help="Output figure path or prefix")
    parser.add_argument("--format", default="png", choices=["png", "svg", "pdf"])
    parser.add_argument(
        "--kind",
        default="term-bar",
        choices=["term-bar", "direction-summary", "semantic-network"],
    )
    parser.add_argument("--top-n", type=int, default=20, help="Top terms to plot for term-bar")
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance threshold for summary plots",
    )
    parser.add_argument("--namespace", default="all", choices=["BP", "MF", "CC", "all"])
    parser.add_argument("--direction", default="both", choices=["over", "under", "both"])
    parser.add_argument("--study-id", default="", help="Optional study ID filter for batch tables")
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.2,
        help="Minimum edge weight for semantic-network plots",
    )
    parser.add_argument(
        "--max-edges",
        type=int,
        default=100,
        help="Maximum number of edges to draw in semantic-network plots",
    )
    parser.add_argument("--title", default="", help="Optional custom figure title")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    input_path = require_existing_file(args.input, "input")
    out_path = resolve_output_path(Path(args.out), args.format)

    try:
        if args.kind == "semantic-network":
            ids, pairwise = read_similarity_matrix(input_path)
            has_edges = build_similarity_edges(
                ids,
                pairwise,
                min_similarity=args.min_similarity,
                max_edges=args.max_edges,
            )
            if len(has_edges) == 0:
                print("No semantic edges remain after applying similarity filters.")
                return 1
            render_semantic_network(
                ids,
                pairwise,
                out=out_path,
                min_similarity=args.min_similarity,
                max_edges=args.max_edges,
                title=args.title,
            )
        else:
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
            if args.kind == "term-bar":
                render_term_bar(rows, out=out_path, top_n=args.top_n, title=args.title)
            else:
                render_direction_summary(rows, out=out_path, alpha=args.alpha, title=args.title)
    except (RuntimeError, ValueError) as exc:
        print(str(exc))
        return 1

    print(f"Figure written: {out_path}")
    return 0
