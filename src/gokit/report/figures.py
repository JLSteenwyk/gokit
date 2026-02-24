"""Figure generation helpers for enrichment outputs."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PlotRow:
    go_id: str
    namespace: str
    direction: str
    p_adjusted: float
    study_id: str | None = None


@dataclass
class SemanticEdge:
    study_a: str
    study_b: str
    score: float


def _pick(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        if key in row and row[key] is not None:
            return str(row[key]).strip()
    return ""


def read_enrichment_tsv(path: Path) -> list[PlotRow]:
    rows: list[PlotRow] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for raw in reader:
            go_id = _pick(raw, "GO", "go_id")
            namespace = _pick(raw, "NS", "namespace")
            if not go_id or not namespace:
                continue
            direction = _pick(raw, "direction") or "over"
            p_adj_raw = _pick(raw, "p_adjusted")
            if not p_adj_raw:
                continue
            rows.append(
                PlotRow(
                    go_id=go_id,
                    namespace=namespace,
                    direction=direction,
                    p_adjusted=float(p_adj_raw),
                    study_id=_pick(raw, "study_id") or None,
                )
            )
    return rows


def read_similarity_matrix(path: Path) -> tuple[list[str], dict[tuple[str, str], float]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, [])
        if len(header) < 2 or header[0] != "study_id":
            raise ValueError("Similarity matrix must start with 'study_id' header.")
        ids = [x.strip() for x in header[1:] if x.strip()]
        pairwise: dict[tuple[str, str], float] = {}
        for row in reader:
            if not row:
                continue
            row_id = row[0].strip()
            if not row_id:
                continue
            vals = row[1:]
            for idx, raw in enumerate(vals):
                if idx >= len(ids):
                    break
                col_id = ids[idx]
                try:
                    score = float(raw)
                except ValueError:
                    continue
                pairwise[(row_id, col_id)] = score
        return ids, pairwise


def build_similarity_edges(
    ids: list[str],
    pairwise: dict[tuple[str, str], float],
    *,
    min_similarity: float = 0.2,
    max_edges: int = 100,
) -> list[SemanticEdge]:
    edges: list[SemanticEdge] = []
    for i, a in enumerate(ids):
        for j, b in enumerate(ids):
            if j <= i:
                continue
            score = pairwise.get((a, b), pairwise.get((b, a), 0.0))
            if score >= min_similarity:
                edges.append(SemanticEdge(study_a=a, study_b=b, score=score))
    edges.sort(key=lambda e: (-e.score, e.study_a, e.study_b))
    return edges[: max(1, max_edges)]


def filter_rows(
    rows: list[PlotRow],
    *,
    namespace: str = "all",
    direction: str = "both",
    study_id: str = "",
) -> list[PlotRow]:
    out = rows
    if namespace != "all":
        out = [r for r in out if r.namespace == namespace]
    if direction != "both":
        out = [r for r in out if r.direction == direction]
    if study_id:
        out = [r for r in out if r.study_id == study_id]
    return out


def score_row(row: PlotRow) -> float:
    p = min(max(row.p_adjusted, 1e-300), 1.0)
    return -math.log10(p)


def top_rows(rows: list[PlotRow], top_n: int) -> list[PlotRow]:
    return sorted(rows, key=lambda r: (-score_row(r), r.go_id))[: max(1, top_n)]


def summarize_direction_counts(
    rows: list[PlotRow],
    *,
    alpha: float = 0.05,
) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        if row.p_adjusted > alpha:
            continue
        ns = row.namespace
        direction = row.direction if row.direction in {"over", "under"} else "over"
        bucket = summary.setdefault(ns, {"over": 0, "under": 0})
        bucket[direction] += 1
    return summary


def resolve_output_path(out: Path, image_format: str) -> Path:
    if out.suffix.lower() in {".png", ".svg", ".pdf"}:
        return out
    return out.with_suffix(f".{image_format}")


def _require_matplotlib():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Figure generation requires optional dependency 'matplotlib'. "
            "Install with: pip install 'gokit[plot]'"
        ) from exc
    return plt


def _require_networkx():
    try:
        import networkx as nx
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Semantic network plotting requires optional dependency 'networkx'. "
            "Install with: pip install 'gokit[plot]'"
        ) from exc
    return nx


def _colors() -> dict[str, str]:
    # Prefer curated publication palettes from pypubfigs.
    try:
        from pypubfigs import friendly_pal

        pal = friendly_pal("wong_eight")
        return {
            "bg": "#F6F8F8",
            "panel": "#FFFFFF",
            "grid": "#DCE4E1",
            "text": "#20312D",
            "title": "#0F1B18",
            "label": "#1E2E2A",
            "over": pal[2],   # green-ish
            "under": pal[5],  # orange-red
        }
    except Exception:
        return {
            "bg": "#F6F8F8",
            "panel": "#FFFFFF",
            "grid": "#DCE4E1",
            "text": "#20312D",
            "title": "#0F1B18",
            "label": "#1E2E2A",
            "over": "#0A7A65",
            "under": "#D94841",
        }


def _style_axes(ax, *, title: str, subtitle: str = "") -> None:
    c = _colors()
    fig = ax.figure
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["panel"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", color=c["grid"], linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)
    ax.tick_params(colors=c["text"], labelsize=10)

    if subtitle:
        ax.set_title(
            f"{title}\n{subtitle}",
            loc="left",
            fontsize=15,
            fontweight="bold",
            color=c["title"],
            pad=12,
        )
    else:
        ax.set_title(
            title,
            loc="left",
            fontsize=15,
            fontweight="bold",
            color=c["title"],
            pad=10,
        )


def render_term_bar(
    rows: list[PlotRow],
    *,
    out: Path,
    top_n: int = 20,
    title: str = "",
) -> None:
    chosen = top_rows(rows, top_n)
    if not chosen:
        raise ValueError("No rows available to plot.")

    plt = _require_matplotlib()
    c = _colors()
    labels = [f"{r.go_id} ({r.namespace})" for r in chosen]
    values = [score_row(r) for r in chosen]
    colors = [c["over"] if r.direction == "over" else c["under"] for r in chosen]

    fig_h = max(4.0, min(12.0, 1.8 + 0.35 * len(chosen)))
    fig, ax = plt.subplots(figsize=(10, fig_h))
    y = list(range(len(chosen)))
    ax.barh(y, values, color=colors)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("-log10(p_adjusted)", color=c["text"], fontsize=11, fontweight="bold")
    ax.set_ylabel("GO term", color=c["text"], fontsize=11, fontweight="bold")
    _style_axes(
        ax,
        title=title or "Top GO Signals",
        subtitle="Enriched and purifying terms ranked by adjusted significance",
    )

    # Add value labels for rapid scan in announcement-style visuals.
    for yi, val in enumerate(values):
        ax.text(val + 0.03, yi, f"{val:.2f}", va="center", ha="left", fontsize=9, color=c["label"])
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)


def render_semantic_network(
    ids: list[str],
    pairwise: dict[tuple[str, str], float],
    *,
    out: Path,
    min_similarity: float = 0.2,
    max_edges: int = 100,
    title: str = "",
) -> None:
    if len(ids) < 2:
        raise ValueError("Need at least two studies for semantic network plotting.")

    edges = build_similarity_edges(
        ids,
        pairwise,
        min_similarity=min_similarity,
        max_edges=max_edges,
    )
    if not edges:
        raise ValueError("No semantic edges passed the selected similarity threshold.")

    plt = _require_matplotlib()
    nx = _require_networkx()
    c = _colors()

    graph = nx.Graph()
    graph.add_nodes_from(ids)
    for edge in edges:
        graph.add_edge(edge.study_a, edge.study_b, weight=edge.score)

    pos = nx.spring_layout(graph, weight="weight", seed=13)
    node_sizes: list[float] = []
    for node in graph.nodes:
        weights = [graph[node][nbr]["weight"] for nbr in graph.neighbors(node)]
        mean_w = (sum(weights) / len(weights)) if weights else 0.0
        node_sizes.append(900 + 2400 * mean_w)

    edge_widths = [1.0 + 5.0 * graph[u][v]["weight"] for u, v in graph.edges]
    edge_alpha = [0.25 + 0.6 * graph[u][v]["weight"] for u, v in graph.edges]

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["panel"])
    ax.axis("off")
    _style_axes(
        ax,
        title=title or "Semantic Similarity Network",
        subtitle=f"Edges: similarity >= {min_similarity} (top {max_edges})",
    )
    ax.grid(False)

    for (u, v), w, a in zip(graph.edges, edge_widths, edge_alpha, strict=False):
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=[(u, v)],
            width=w,
            alpha=min(max(a, 0.0), 1.0),
            edge_color=c["over"],
            ax=ax,
        )
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=node_sizes,
        node_color=c["panel"],
        edgecolors=c["under"],
        linewidths=1.8,
        ax=ax,
    )
    nx.draw_networkx_labels(graph, pos, font_size=10, font_color=c["title"], ax=ax)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)


def render_direction_summary(
    rows: list[PlotRow],
    *,
    out: Path,
    alpha: float = 0.05,
    title: str = "",
) -> None:
    summary = summarize_direction_counts(rows, alpha=alpha)
    if not summary:
        raise ValueError("No significant terms found for direction summary.")

    plt = _require_matplotlib()
    c = _colors()
    namespaces = sorted(summary)
    over = [summary[ns]["over"] for ns in namespaces]
    under = [summary[ns]["under"] for ns in namespaces]
    x = list(range(len(namespaces)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    over_bars = ax.bar(
        [i - width / 2 for i in x],
        over,
        width=width,
        label="over",
        color=c["over"],
    )
    under_bars = ax.bar(
        [i + width / 2 for i in x],
        under,
        width=width,
        label="under",
        color=c["under"],
    )
    ax.set_xticks(x)
    ax.set_xticklabels(namespaces)
    ax.set_ylabel(
        f"Significant terms (p_adjusted <= {alpha})",
        color=c["text"],
        fontsize=11,
        fontweight="bold",
    )
    ax.set_xlabel("Namespace", color=c["text"], fontsize=11, fontweight="bold")
    _style_axes(
        ax,
        title=title or "Directional GO Summary",
        subtitle="Significant term counts by namespace and direction",
    )
    ax.legend(frameon=False, loc="upper right", fontsize=10)

    for bar in list(over_bars) + list(under_bars):
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.05,
            f"{int(h)}",
            ha="center",
            va="bottom",
            fontsize=9,
            color=c["label"],
        )
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
