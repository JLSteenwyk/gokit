"""enrich subcommand."""

from __future__ import annotations

import argparse
from pathlib import Path

from gokit.cache.obo_cache import default_cache_dir, load_or_build_obo_cache
from gokit.cli.common import parse_csv_list, require_existing_file
from gokit.core.enrichment import EnrichmentResult, OraRunner
from gokit.core.manifest import build_input_files, default_manifest, write_manifest
from gokit.core.propagation import propagate_gene_to_go
from gokit.core.semantic import StudyTermSet, pairwise_semantic_similarity
from gokit.io.assoc import read_associations
from gokit.io.study import read_gene_set, read_study_manifest
from gokit.report.writers import (
    write_combined_jsonl,
    write_grouped_summary_batch,
    write_grouped_summary_single,
    write_combined_tsv,
    write_jsonl,
    write_similarity_matrix,
    write_similarity_top_pairs,
    write_tsv,
)
from gokit.report.parquet_writer import write_combined_parquet, write_results_parquet


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("enrich", help="Run GO enrichment analysis")
    parser.add_argument("--study", default="", help="Study gene list file")
    parser.add_argument(
        "--studies",
        default="",
        help="Batch manifest with lines as '<study_name>\\t<study_path>' or '<study_path>'",
    )
    parser.add_argument("--population", required=True, help="Population gene list file")
    parser.add_argument("--assoc", required=True, help="Association file")
    parser.add_argument("--assoc-format", default="auto", choices=["auto", "gaf", "gpad", "gene2go", "id2gos"])
    parser.add_argument("--obo", required=True, help="Ontology OBO file")
    parser.add_argument("--namespace", default="all", choices=["BP", "MF", "CC", "all"])
    parser.add_argument("--method", default="fdr_bh")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--fdr-resamples", type=int, default=0)
    parser.add_argument("--relationships", default="", help="Comma-separated relationships")
    parser.add_argument("--cache-dir", default=str(default_cache_dir()), help="Cache directory")
    parser.add_argument(
        "--no-propagate-counts",
        action="store_true",
        help="Do not propagate associations to ancestor GO terms",
    )
    parser.add_argument("--store-items", default="auto", choices=["auto", "always", "never"])
    parser.add_argument("--out", required=True, help="Output prefix path")
    parser.add_argument("--out-formats", default="tsv,jsonl", help="Comma-separated output formats")
    parser.add_argument(
        "--compare-semantic",
        action="store_true",
        help="In batch mode, compute ontology-aware pairwise similarity between enriched term sets",
    )
    parser.add_argument(
        "--semantic-metric",
        default="jaccard",
        choices=["jaccard", "resnik", "lin", "wang"],
        help="Semantic metric for --compare-semantic",
    )
    parser.add_argument(
        "--semantic-top-k",
        type=int,
        default=5,
        help="Top contributing GO term pairs to emit per study pair",
    )
    parser.add_argument("--manifest", default="", help="Optional manifest output path")
    parser.add_argument("--dry-run", action="store_true", help="Validate and emit manifest only")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    if bool(args.study) == bool(args.studies):
        raise ValueError("Provide exactly one of --study or --studies")

    study_path = require_existing_file(args.study, "study") if args.study else None
    studies_manifest = require_existing_file(args.studies, "studies") if args.studies else None
    population = require_existing_file(args.population, "population")
    assoc = require_existing_file(args.assoc, "association")
    obo = require_existing_file(args.obo, "obo")

    relationships = parse_csv_list(args.relationships)
    out_formats = parse_csv_list(args.out_formats)
    out_prefix = Path(args.out)

    manifest_path = Path(args.manifest) if args.manifest else out_prefix.with_suffix(".manifest.json")
    named_inputs: list[tuple[str, Path]] = [
        ("population", population),
        ("association", assoc),
        ("obo", obo),
    ]
    if study_path:
        named_inputs.append(("study", study_path))
    if studies_manifest:
        named_inputs.append(("studies", studies_manifest))
    input_files = build_input_files(named_inputs)

    if args.dry_run:
        notes = "Dry-run validation completed."
        results = []
        combined_rows: list[tuple[str, EnrichmentResult]] = []
        pairwise: dict[tuple[str, str], float] = {}
        top_pairs: dict[tuple[str, str], list[tuple[str, str, float]]] = {}
        study_ids: list[str] = []
    else:
        pop_genes = read_gene_set(population)
        gene_to_go = read_associations(assoc, args.assoc_format)
        obo_cached = load_or_build_obo_cache(obo, Path(args.cache_dir))
        obo_meta = obo_cached.meta

        if not args.no_propagate_counts:
            gene_to_go = propagate_gene_to_go(gene_to_go, obo_cached.go_to_ancestors)

        runner = OraRunner(
            population_genes=pop_genes,
            gene_to_go=gene_to_go,
            go_to_namespace=obo_cached.go_to_namespace,
        )

        results = []
        combined_rows: list[tuple[str, EnrichmentResult]] = []
        pairwise: dict[tuple[str, str], float] = {}
        top_pairs: dict[tuple[str, str], list[tuple[str, str, float]]] = {}
        study_ids: list[str] = []

        if study_path:
            study_genes = read_gene_set(study_path)
            results = runner.run_study(
                study_genes=study_genes,
                namespace_filter=args.namespace,
                store_items=(args.store_items == "always"),
            )
            combined_rows = [("study", r) for r in results]
            study_ids = ["study"]
        else:
            studies = read_study_manifest(studies_manifest)
            termsets: list[StudyTermSet] = []
            for study_id, file_path in studies:
                path = require_existing_file(str(file_path), f"study({study_id})")
                study_genes = read_gene_set(path)
                rows = runner.run_study(
                    study_genes=study_genes,
                    namespace_filter=args.namespace,
                    store_items=(args.store_items == "always"),
                )
                combined_rows.extend((study_id, row) for row in rows)
                termsets.append(StudyTermSet(study_id=study_id, go_ids={r.go_id for r in rows}))
                study_ids.append(study_id)
            results = [row for _, row in combined_rows]
            if args.compare_semantic:
                pairwise, top_pairs = pairwise_semantic_similarity(
                    termsets,
                    obo_cached.go_to_ancestors,
                    metric=args.semantic_metric,
                    go_to_pop_count=runner.go_to_pop_count,
                    pop_n=len(runner.population_genes),
                    go_to_parents=obo_cached.go_to_parents,
                    top_k=args.semantic_top_k,
                )

        notes = (
            f"Computed {len(results)} enriched GO rows; "
            f"obo_format={obo_meta.format_version or 'na'}; "
            f"obo_data={obo_meta.data_version or 'na'}; "
            f"cache_hit={obo_cached.cache_hit}; "
            f"propagate={not args.no_propagate_counts}; "
            f"batch={bool(args.studies)}; "
            f"semantic_compared={bool(pairwise)}; "
            f"semantic_metric={args.semantic_metric if args.compare_semantic else 'na'}."
        )

    manifest = default_manifest(
        command="gokit enrich",
        seed=args.seed,
        alpha=args.alpha,
        method=args.method,
        namespace=args.namespace,
        relationships=relationships,
        out_formats=out_formats,
        input_files=input_files,
        notes=notes,
    )
    write_manifest(manifest_path, manifest)

    if not args.dry_run:
        if args.study:
            if "tsv" in out_formats:
                write_tsv(out_prefix.with_suffix(".tsv"), results)
                write_grouped_summary_single(out_prefix.with_suffix(".summary.tsv"), results, args.alpha)
            if "jsonl" in out_formats:
                write_jsonl(out_prefix.with_suffix(".jsonl"), results)
            if "parquet" in out_formats:
                try:
                    write_results_parquet(out_prefix.with_suffix(".parquet"), results)
                except RuntimeError as exc:
                    print(str(exc))
                    return 1
        else:
            out_dir = out_prefix
            studies_dir = out_dir / "studies"
            for study_id in study_ids:
                rows = [row for sid, row in combined_rows if sid == study_id]
                if "tsv" in out_formats:
                    write_tsv(studies_dir / f"{study_id}.tsv", rows)
                    write_grouped_summary_single(
                        studies_dir / f"{study_id}.summary.tsv",
                        rows,
                        args.alpha,
                    )
                if "jsonl" in out_formats:
                    write_jsonl(studies_dir / f"{study_id}.jsonl", rows)
                if "parquet" in out_formats:
                    try:
                        write_results_parquet(studies_dir / f"{study_id}.parquet", rows)
                    except RuntimeError as exc:
                        print(str(exc))
                        return 1
            if "tsv" in out_formats:
                write_combined_tsv(out_dir / "all_studies.tsv", combined_rows)
                write_grouped_summary_batch(out_dir / "grouped_summary.tsv", combined_rows, args.alpha)
            if "jsonl" in out_formats:
                write_combined_jsonl(out_dir / "all_studies.jsonl", combined_rows)
            if "parquet" in out_formats:
                try:
                    write_combined_parquet(out_dir / "all_studies.parquet", combined_rows)
                except RuntimeError as exc:
                    print(str(exc))
                    return 1
            if args.compare_semantic and pairwise:
                write_similarity_matrix(out_dir / "semantic_similarity.tsv", study_ids, pairwise)
                write_similarity_top_pairs(
                    out_dir / "semantic_top_pairs.tsv",
                    top_pairs,
                    study_ids,
                )

    print(f"Manifest written: {manifest_path}")
    if args.dry_run:
        print("Dry-run complete.")
    else:
        print(f"Enrichment complete: {len(results)} rows.")
    return 0
