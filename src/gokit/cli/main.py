"""Main CLI entrypoint."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from gokit.cli import benchmark, cache, download, enrich, explain, plot, validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gokit", description="GO enrichment toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enrich.register_parser(subparsers)
    validate.register_parser(subparsers)
    benchmark.register_parser(subparsers)
    cache.register_parser(subparsers)
    explain.register_parser(subparsers)
    plot.register_parser(subparsers)
    download.register_parser(subparsers)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
