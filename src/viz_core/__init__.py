from .config import VizConfig, WarmthConfig, InsightConfig
from .theme import apply_theme, get_palette, set_titles
from .insights import categorical_top_insight, time_event_insights, concise_title_from_insight
from .layout import create_layout

__all__ = [
    "VizConfig",
    "WarmthConfig",
    "InsightConfig",
    "apply_theme",
    "get_palette",
    "set_titles",
    "categorical_top_insight",
    "time_event_insights",
    "concise_title_from_insight",
    "create_layout",
]

from .editorial_warmth import (
    EditorialPalette,
    WARM_REPORT_PALETTE,
    DARK_BENCHMARK_PALETTE,
    set_editorial_rcparams,
    apply_editorial_axes,
    add_editorial_text,
    de_emphasise_artists,
    annotate_focus,
    save_editorial_figure,
    editorial_acceptance_block,
)
