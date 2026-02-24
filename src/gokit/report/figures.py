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
    over_bars = ax.bar([i - width / 2 for i in x], over, width=width, label="over", color=c["over"])
    under_bars = ax.bar([i + width / 2 for i in x], under, width=width, label="under", color=c["under"])
    ax.set_xticks(x)
    ax.set_xticklabels(namespaces)
    ax.set_ylabel(f"Significant terms (p_adjusted <= {alpha})", color=c["text"], fontsize=11, fontweight="bold")
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
