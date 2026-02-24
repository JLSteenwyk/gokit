"""download subcommand."""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import urlretrieve

GO_BASIC_URL = "http://current.geneontology.org/ontology/go-basic.obo"
GOSLIM_GENERIC_URL = "http://current.geneontology.org/ontology/subsets/goslim_generic.obo"


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("download", help="Download common GO ontology OBO files")
    parser.add_argument("--out-dir", default=".", help="Directory where OBO files are downloaded")
    parser.set_defaults(func=run)


def _download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, dst)  # noqa: S310 - explicit trusted endpoint for CLI utility


def run(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    targets = [
        (GO_BASIC_URL, out_dir / "go-basic.obo"),
        (GOSLIM_GENERIC_URL, out_dir / "goslim_generic.obo"),
    ]

    for url, dst in targets:
        print(f"Downloading {url} -> {dst}")
        _download(url, dst)
        print(f"Saved: {dst}")
    return 0
