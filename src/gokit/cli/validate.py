"""validate subcommand."""

from __future__ import annotations

import argparse

from gokit.cli.common import require_existing_file


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("validate", help="Validate enrichment inputs")
    parser.add_argument("--study", required=True)
    parser.add_argument("--population", required=True)
    parser.add_argument("--assoc", required=True)
    parser.add_argument("--obo", default="go-basic.obo")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    checks = [
        ("study", args.study),
        ("population", args.population),
        ("association", args.assoc),
        ("obo", args.obo),
    ]

    failed = False
    for label, raw_path in checks:
        try:
            checked = require_existing_file(raw_path, label)
            print(f"OK   {label:<10} {checked}")
        except (FileNotFoundError, ValueError) as exc:
            print(f"FAIL {label:<10} {exc}")
            failed = True

    return 1 if failed else 0
