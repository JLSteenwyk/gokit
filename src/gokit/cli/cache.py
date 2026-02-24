"""cache subcommand."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from gokit.cache.obo_cache import load_or_build_obo_cache


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("cache", help="Manage gokit cache")
    parser.add_argument("action", choices=["status", "build", "clear"])
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "gokit"))
    parser.add_argument("--obo", default="", help="OBO file to register during build")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    cache_dir = Path(args.cache_dir)

    if args.action == "status":
        if not cache_dir.exists():
            print(f"Cache directory does not exist: {cache_dir}")
            return 0
        files = [p for p in cache_dir.rglob("*") if p.is_file()]
        print(f"Cache directory: {cache_dir}")
        print(f"Cached files: {len(files)}")
        obo_files = [p for p in files if p.suffix == ".json" and p.parent.name == "obo"]
        print(f"OBO cache entries: {len(obo_files)}")
        return 0

    if args.action == "build":
        cache_dir.mkdir(parents=True, exist_ok=True)
        if args.obo:
            obo = Path(args.obo)
            if not obo.exists():
                print(f"OBO file not found: {obo}")
                return 1
            cached = load_or_build_obo_cache(obo, cache_dir)
            print(f"OBO cache ready: {cached.cache_path} (hit={cached.cache_hit})")
        else:
            stamp = cache_dir / "CACHE_READY"
            stamp.write_text("gokit cache scaffold\n", encoding="utf-8")
            print(f"Cache initialized: {cache_dir}")
        return 0

    if args.action == "clear":
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            print(f"Cache cleared: {cache_dir}")
        else:
            print(f"Cache directory does not exist: {cache_dir}")
        return 0

    return 1
