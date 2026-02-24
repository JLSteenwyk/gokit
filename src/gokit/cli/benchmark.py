"""benchmark subcommand."""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

from gokit.core.enrichment import OraRunner, run_ora


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("benchmark", help="Run local gokit benchmark suite")
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--population-size", type=int, default=5000)
    parser.add_argument("--study-size", type=int, default=300)
    parser.add_argument("--go-terms", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--out", default="", help="Optional JSON output path")
    parser.set_defaults(func=run)


def _build_synthetic_dataset(
    *, seed: int, population_size: int, study_size: int, go_terms: int
) -> tuple[set[str], set[str], dict[str, set[str]], dict[str, str]]:
    rng = random.Random(seed)
    population = {f"gene{i}" for i in range(population_size)}
    study = set(rng.sample(sorted(population), min(study_size, len(population))))

    ns_values = ["biological_process", "molecular_function", "cellular_component"]
    go_ids = [f"GO:{i:07d}" for i in range(1, go_terms + 1)]
    go_to_namespace = {goid: ns_values[i % 3] for i, goid in enumerate(go_ids)}

    gene_to_go: dict[str, set[str]] = {}
    for gene in population:
        n = rng.randint(1, 6)
        gene_to_go[gene] = set(rng.sample(go_ids, n))

    return study, population, gene_to_go, go_to_namespace


def run(args: argparse.Namespace) -> int:
    study, population, gene_to_go, go_to_namespace = _build_synthetic_dataset(
        seed=args.seed,
        population_size=args.population_size,
        study_size=args.study_size,
        go_terms=args.go_terms,
    )

    tic_cold = time.perf_counter()
    cold_rows = 0
    for _ in range(args.iterations):
        rows = run_ora(
            study_genes=study,
            population_genes=population,
            gene_to_go=gene_to_go,
            go_to_namespace=go_to_namespace,
            namespace_filter="all",
        )
        cold_rows += len(rows)
    toc_cold = time.perf_counter()

    runner = OraRunner(
        population_genes=population,
        gene_to_go=gene_to_go,
        go_to_namespace=go_to_namespace,
    )
    tic_warm = time.perf_counter()
    warm_rows = 0
    for _ in range(args.iterations):
        rows = runner.run_study(study_genes=study, namespace_filter="all")
        warm_rows += len(rows)
    toc_warm = time.perf_counter()

    cold_seconds = toc_cold - tic_cold
    warm_seconds = toc_warm - tic_warm
    speedup = (cold_seconds / warm_seconds) if warm_seconds > 0 else 0.0

    result = {
        "iterations": args.iterations,
        "population_size": args.population_size,
        "study_size": args.study_size,
        "go_terms": args.go_terms,
        "cold_elapsed_seconds": round(cold_seconds, 6),
        "warm_elapsed_seconds": round(warm_seconds, 6),
        "speedup_x": round(speedup, 3),
        "cold_total_rows": cold_rows,
        "warm_total_rows": warm_rows,
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Benchmark written: {out}")
    return 0
