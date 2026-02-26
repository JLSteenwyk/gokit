.. _faq:


FAQ
===

**What type of enrichment analysis does gokit perform?**

gokit performs overrepresentation analysis (ORA) using Fisher's exact test.
It tests whether GO terms are significantly enriched (overrepresented)
or depleted (underrepresented) in a study gene set compared to a
background population.

|

**What association file formats does gokit support?**

gokit supports four association file formats: id2gos (simple gene-to-GO
mapping), GAF (Gene Association File format 2.x), GPAD (Gene Product
Association Data format 1.x/2.x), and NCBI gene2go format. By default,
gokit automatically detects the format.

|

**What multiple testing correction methods are available?**

gokit supports the following correction methods: Benjamini-Hochberg FDR
(``fdr_bh``, default), Benjamini-Yekutieli FDR (``fdr_by``),
Bonferroni (``bonferroni``), Holm (``holm``), and no correction (``none``).

|

**What semantic similarity metrics are supported?**

gokit supports Jaccard index, Resnik similarity (based on information
content of the most informative common ancestor), Lin similarity, and
Wang similarity for comparing GO term sets across studies.

|

**Does gokit have any dependencies?**

gokit is designed with zero core dependencies for maximum portability.
Optional extras include ``pyarrow`` for Parquet output (``pip install gokit[io]``)
and ``matplotlib``/``networkx`` for plotting (``pip install gokit[plot]``).

|

**How do I download the Gene Ontology files?**

Use the ``gokit download`` command to download ``go-basic.obo`` and
``goslim_generic.obo`` into the current directory. Alternatively,
download them manually from http://current.geneontology.org/ontology/.

|

**I am having trouble installing gokit, what should I do?**

Please install gokit using a virtual environment as directed in the installation instructions.
If you are still running into issues after installing in a virtual environment, please
open an issue on `GitHub <https://github.com/JLSteenwyk/gokit/issues>`_.

^^^^^
