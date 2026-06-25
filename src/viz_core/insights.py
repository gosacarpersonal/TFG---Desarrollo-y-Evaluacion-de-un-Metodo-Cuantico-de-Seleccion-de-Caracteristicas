from __future__ import annotations

from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd

from .config import InsightConfig


def categorical_top_insight(data: pd.DataFrame, category: str, value: str, mode: str = "mean") -> str:
    agg = data.groupby(category)[value].agg(mode).sort_values(ascending=False)
    top = agg.index[0]
    second = agg.index[1] if len(agg) > 1 else top
    diff = agg.iloc[0] - agg.iloc[1] if len(agg) > 1 else 0
    return f"{top} presenta el valor medio más alto y supera a {second} en {diff:.1f} unidades."


def time_event_insights(series_df: pd.DataFrame, x: str, y: str, event_points: Optional[Sequence] = None) -> list[dict]:
    insights = []
    if event_points:
        for point in event_points:
            label = point.get("label", "Punto relevante")
            x_value = point["x"]
            row = series_df.loc[series_df[x] == x_value]
            if not row.empty:
                insights.append({"x": row.iloc[0][x], "y": row.iloc[0][y], "label": label})
    else:
        idx = series_df[y].idxmin()
        row = series_df.loc[idx]
        insights.append({"x": row[x], "y": row[y], "label": "Mínimo local / incidente"})
    return insights


def concise_title_from_insight(prefix: str, insight: str) -> str:
    return f"{prefix}: {insight}"
