from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass
class WarmthConfig:
    """Controls visual warmth and overall softness of the figure."""

    enabled: bool = True
    figure_facecolor: str = "#ffffff"
    axes_facecolor: str = "#ffffff"
    grid_color: str = "#e6e6e6"
    spine_color: str = "#c2c2c2"
    text_color: str = "#3b3b3b"
    neutral_color: str = "#bdbdbd"
    accent_color: str = "#d95f5f"
    secondary_accent: str = "#4f81bd"
    categorical_palette: Sequence[str] = field(
        default_factory=lambda: ["#a9bfd6", "#d9b382", "#c7d59f", "#d7a6a1", "#8fb7a8"]
    )
    alpha_main: float = 0.9
    alpha_secondary: float = 0.55
    grid_alpha: float = 0.9
    line_width: float = 2.0
    title_weight: str = "semibold"
    title_size: int = 15
    subtitle_size: int = 10
    label_size: int = 11
    tick_size: int = 9
    annotation_size: int = 10
    use_despine: bool = True
    show_soft_grid: bool = True
    marker_size: int = 28
    jitter: float = 0.09


@dataclass
class InsightConfig:
    """Narrative annotation controls."""

    enabled: bool = True
    highlight_color: str = "#d95f5f"
    context_color: str = "#bdbdbd"
    arrow_color: str = "#d95f5f"
    text_weight: str = "semibold"
    annotation_size: int = 11
    sentence_case_title: bool = True


@dataclass
class VizConfig:
    """Shared top-level configuration."""

    notebook: bool = True
    figsize: Optional[tuple] = None
    dpi: int = 150
    warmth: WarmthConfig = field(default_factory=WarmthConfig)
    insight: InsightConfig = field(default_factory=InsightConfig)
    style_name: str = "closed_skill"
