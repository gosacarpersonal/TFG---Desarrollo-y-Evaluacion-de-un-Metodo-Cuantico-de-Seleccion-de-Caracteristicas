from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class EditorialPalette:
    """Coherent colours inspired by the benchmark HTML gallery and adapted for reports."""

    background: str = "#FFFFFF"
    panel: str = "#FFFFFF"
    text: str = "#2F2F2F"
    muted_text: str = "#6F6A60"
    grid: str = "#E6E6E6"
    spine: str = "#C2C2C2"
    primary: str = "#2F6F9F"
    secondary: str = "#8FB3C9"
    accent: str = "#D9822B"
    positive: str = "#5E8C61"
    negative: str = "#B85C5C"
    neutral: str = "#B8B0A3"
    categorical: Sequence[str] = field(
        default_factory=lambda: (
            "#2F6F9F",
            "#D9822B",
            "#5E8C61",
            "#B85C5C",
            "#8FB3C9",
            "#B8B0A3",
        )
    )


DARK_BENCHMARK_PALETTE = EditorialPalette(
    background="#0B0F19",
    panel="#161E31",
    text="#F3F4F6",
    muted_text="#9CA3AF",
    grid="#2A3448",
    spine="#334155",
    primary="#6366F1",
    secondary="#3B82F6",
    accent="#8B5CF6",
    positive="#10B981",
    negative="#EF4444",
    neutral="#64748B",
    categorical=("#6366F1", "#3B82F6", "#8B5CF6", "#10B981", "#EF4444", "#94A3B8"),
)

WARM_REPORT_PALETTE = EditorialPalette()


def set_editorial_rcparams(palette: EditorialPalette = WARM_REPORT_PALETTE) -> None:
    """Apply global Matplotlib defaults for calm, warm, report-ready figures."""

    plt.rcParams.update(
        {
            "figure.facecolor": palette.background,
            "axes.facecolor": palette.panel,
            "savefig.facecolor": palette.background,
            "axes.edgecolor": palette.spine,
            "axes.labelcolor": palette.text,
            "text.color": palette.text,
            "xtick.color": palette.muted_text,
            "ytick.color": palette.muted_text,
            "grid.color": palette.grid,
            "grid.linestyle": "-",
            "grid.linewidth": 0.6,
            "axes.grid": False,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlelocation": "left",
            "axes.prop_cycle": plt.cycler(color=list(palette.categorical)),
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.titleweight": "semibold",
            "axes.labelsize": 10,
            "legend.frameon": False,
            "figure.dpi": 150,
            "savefig.dpi": 180,
        }
    )


def apply_editorial_axes(
    ax,
    palette: EditorialPalette = WARM_REPORT_PALETTE,
    *,
    grid_axis: str = "y",
    show_grid: bool = True,
    remove_spines: bool = True,
):
    """Apply the mandatory benchmark-inspired warmth layer to one axes."""

    fig = ax.figure
    fig.patch.set_facecolor(palette.background)
    ax.set_facecolor(palette.panel)
    ax.tick_params(colors=palette.muted_text, labelsize=9)
    ax.xaxis.label.set_color(palette.text)
    ax.yaxis.label.set_color(palette.text)
    ax.title.set_color(palette.text)

    if remove_spines:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(palette.spine)
        ax.spines[side].set_linewidth(0.8)

    if show_grid:
        ax.grid(True, axis=grid_axis, color=palette.grid, linewidth=0.6, alpha=0.8)
    else:
        ax.grid(False)
    ax.set_axisbelow(True)
    return ax


def add_editorial_text(
    ax,
    title: str,
    subtitle: Optional[str] = None,
    *,
    palette: EditorialPalette = WARM_REPORT_PALETTE,
    title_size: int = 15,
    subtitle_size: int = 10,
):
    """Add a title/subtitle hierarchy above the plot without cramping the axes."""

    ax.set_title("")
    ax.text(
        0,
        1.10 if subtitle else 1.06,
        title,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=title_size,
        fontweight="semibold",
        color=palette.text,
    )
    if subtitle:
        ax.text(
            0,
            1.045,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=subtitle_size,
            color=palette.muted_text,
        )
    return ax


def de_emphasise_artists(artists: Iterable, *, alpha: float = 0.35, linewidth: Optional[float] = None) -> None:
    """Reduce salience of context marks so the focus can be highlighted honestly."""

    for artist in artists:
        if hasattr(artist, "set_alpha"):
            artist.set_alpha(alpha)
        if linewidth is not None and hasattr(artist, "set_linewidth"):
            artist.set_linewidth(linewidth)


def annotate_focus(
    ax,
    x,
    y,
    text: str,
    *,
    palette: EditorialPalette = WARM_REPORT_PALETTE,
    xytext=(18, 18),
):
    """Add one restrained callout for the analytical focus."""

    return ax.annotate(
        text,
        xy=(x, y),
        xytext=xytext,
        textcoords="offset points",
        color=palette.text,
        fontsize=10,
        fontweight="semibold",
        arrowprops={"arrowstyle": "->", "color": palette.accent, "lw": 1.2},
        bbox={"boxstyle": "round,pad=0.28", "fc": palette.background, "ec": palette.spine, "lw": 0.8, "alpha": 0.95},
    )


def save_editorial_figure(fig, path: str | Path, *, dpi: int = 180) -> Path:
    """Save a figure with report-safe padding and warm background."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.18)
    return path


def editorial_acceptance_block(
    *,
    surface: str,
    main_accent: str,
    context_deemphasis: str,
    text_hierarchy: str,
    scientific_honesty: str,
    export: str,
) -> str:
    """Return the mandatory textual acceptance block for notebook/report notes."""

    return (
        "Editorial warmth pass:\n"
        f"- Surface: {surface}\n"
        f"- Main accent: {main_accent}\n"
        f"- Context de-emphasis: {context_deemphasis}\n"
        "- Grid/spines: soft grid, top/right spines removed unless analytically required.\n"
        f"- Text hierarchy: {text_hierarchy}\n"
        f"- Export/readability: {export}\n"
        f"- Scientific honesty: {scientific_honesty}"
    )
