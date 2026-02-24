#!/usr/bin/env python3
"""Fail CI if benchmark metrics violate gate config."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--result", required=True)
    p.add_argument("--config", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))

    min_speedup = float(config.get("min_speedup_x", 1.0))
    min_rows = int(config.get("min_rows", 1))

    speedup = float(result.get("speedup_x", 0.0))
    cold_rows = int(result.get("cold_total_rows", 0))
    warm_rows = int(result.get("warm_total_rows", 0))

    errors: list[str] = []
    if cold_rows != warm_rows:
        errors.append(f"cold_total_rows ({cold_rows}) != warm_total_rows ({warm_rows})")
    if cold_rows < min_rows:
        errors.append(f"cold_total_rows ({cold_rows}) < min_rows ({min_rows})")
    if speedup < min_speedup:
        errors.append(f"speedup_x ({speedup}) < min_speedup_x ({min_speedup})")

    print("Benchmark gate report")
    print(f"  speedup_x      : {speedup}")
    print(f"  cold_total_rows: {cold_rows}")
    print(f"  warm_total_rows: {warm_rows}")
    print(f"  min_speedup_x  : {min_speedup}")
    print(f"  min_rows       : {min_rows}")

    if errors:
        print("\nFAILED:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("\nPASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
