from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import seaborn as sns

from .config import WarmthConfig


def get_palette(n: int = 3, warmth: Optional[WarmthConfig] = None) -> Sequence[str]:
    warmth = warmth or WarmthConfig()
    base = list(warmth.categorical_palette)
    if n <= len(base):
        return base[:n]
    extra = sns.color_palette("pastel", n - len(base)).as_hex()
    return base + list(extra)


def apply_theme(ax=None, warmth: Optional[WarmthConfig] = None):
    warmth = warmth or WarmthConfig()
    if ax is None:
        ax = plt.gca()
    fig = ax.figure
    fig.patch.set_facecolor(warmth.figure_facecolor)
    ax.set_facecolor(warmth.axes_facecolor)
    ax.tick_params(colors=warmth.text_color, labelsize=warmth.tick_size)
    ax.xaxis.label.set_color(warmth.text_color)
    ax.yaxis.label.set_color(warmth.text_color)
    for spine in ax.spines.values():
        spine.set_color(warmth.spine_color)
    if warmth.show_soft_grid:
        ax.grid(True, axis="y", color=warmth.grid_color, alpha=warmth.grid_alpha, linestyle="--", linewidth=0.9)
        ax.grid(False, axis="x")
    else:
        ax.grid(False)
    if warmth.use_despine:
        sns.despine(ax=ax)
    return ax


def set_titles(ax, title: Optional[str] = None, subtitle: Optional[str] = None, warmth: Optional[WarmthConfig] = None):
    warmth = warmth or WarmthConfig()
    if title:
        ax.text(
            0.0,
            1.075,
            title,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=warmth.title_size,
            fontweight=warmth.title_weight,
            color=warmth.text_color,
        )
    if subtitle:
        ax.text(
            0.0,
            1.03,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=warmth.subtitle_size,
            color=warmth.text_color,
        )
    return ax
