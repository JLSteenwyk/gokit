"""explain subcommand."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("explain", help="Explain a GO result row")
    parser.add_argument("--go-id", default="", help="GO ID to explain")
    parser.add_argument("--result-json", default="", help="JSON file containing one result object")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    if args.result_json:
        p = Path(args.result_json)
        if not p.exists():
            print(f"Result file not found: {p}")
            return 1
        payload = json.loads(p.read_text(encoding="utf-8"))
        print("Result explanation scaffold:")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.go_id:
        print(f"Explanation scaffold for {args.go_id}:")
        print("- statistical trace: pending engine implementation")
        print("- ancestor path trace: pending engine implementation")
        return 0

    print("Provide either --go-id or --result-json")
    return 1
