.. _change_log:


Change log
==========

Major changes to gokit are summarized here.

**0.1.3**
Release focused on plotting and documentation polish:

- Plotting dependencies promoted to core package dependencies
- Realistic multi-study example datasets and figure outputs added
- Documentation and README updated with larger generated figure galleries
- Term-bar plots now include a bottom-right direction legend

**0.1.2**
Current release with full feature set including:

- Single-study and batch enrichment analysis
- Semantic similarity comparisons (Jaccard, Resnik, Lin, Wang)
- Auto-plot emission from enrichment runs
- Consolidated markdown report generation
- On-disk OBO cache with SHA256 invalidation
- Run manifest for reproducibility

**0.1.1**
Initial public release with core enrichment functionality:

- Fisher's exact test for overrepresentation analysis
- Multiple testing correction (BH, Bonferroni, Holm)
- Support for id2gos, GAF, GPAD, and gene2go association formats
- Automatic format detection
- Gene ID normalization
- Term propagation through GO hierarchy
- TSV, JSONL, and Parquet output formats
- Plotting support (term-bar, direction-summary, semantic-network)
- Input validation command
- GO ontology download command
