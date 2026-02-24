"""Shorthand CLI aliases for gokit subcommands."""

from __future__ import annotations

from collections.abc import Sequence

from gokit.cli.main import main


def _run_with(subcommand: str, argv: Sequence[str] | None = None) -> int:
    args = [subcommand]
    if argv is not None:
        args.extend(argv)
    return main(args)


def enrich_main(argv: Sequence[str] | None = None) -> int:
    return _run_with("enrich", argv)


def validate_main(argv: Sequence[str] | None = None) -> int:
    return _run_with("validate", argv)


def benchmark_main(argv: Sequence[str] | None = None) -> int:
    return _run_with("benchmark", argv)


def cache_main(argv: Sequence[str] | None = None) -> int:
    return _run_with("cache", argv)


def explain_main(argv: Sequence[str] | None = None) -> int:
    return _run_with("explain", argv)


def plot_main(argv: Sequence[str] | None = None) -> int:
    return _run_with("plot", argv)


def download_main(argv: Sequence[str] | None = None) -> int:
    return _run_with("download", argv)
