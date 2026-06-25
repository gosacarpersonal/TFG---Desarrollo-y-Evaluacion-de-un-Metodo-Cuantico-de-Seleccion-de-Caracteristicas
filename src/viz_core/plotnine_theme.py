from __future__ import annotations

from pathlib import Path

try:
    from plotnine import element_blank, element_line, element_text, theme, theme_minimal
except ModuleNotFoundError as exc:  # pragma: no cover - optional plotting backend
    raise ModuleNotFoundError(
        "plotnine is required for src.viz_core.plotnine_theme. "
        "Install plotnine>=0.15.7."
    ) from exc

from .config import WarmthConfig


def theme_tfg(width: float = 11.5, height: float = 6.2, dpi: int = 300, base_size: int = 12):
    """Return the warm report theme used by plotnine prototypes."""

    w = WarmthConfig()
    return theme_minimal(base_size=base_size) + theme(
        figure_size=(width, height),
        dpi=dpi,
        plot_background=element_blank(),
        panel_background=element_blank(),
        panel_grid_major_y=element_line(color=w.grid_color, size=0.55, alpha=w.grid_alpha),
        panel_grid_major_x=element_line(color=w.grid_color, size=0.45, alpha=0.75),
        panel_grid_minor=element_blank(),
        axis_text=element_text(color="#6f6a60"),
        axis_title_x=element_text(color=w.text_color, size=base_size),
        axis_title_y=element_blank(),
        plot_title=element_text(color=w.text_color, size=base_size + 4, weight="bold"),
        plot_subtitle=element_text(color="#6f6a60", size=base_size),
        legend_position="bottom",
        legend_title=element_blank(),
        legend_text=element_text(color=w.text_color, size=base_size - 1),
    )


def save_plotnine(plot, path: str | Path, width: float = 11.5, height: float = 6.2, dpi: int = 300) -> Path:
    """Save a plotnine object with consistent dimensions and quiet logging."""

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plot.save(out, width=width, height=height, dpi=dpi, verbose=False)
    return out
