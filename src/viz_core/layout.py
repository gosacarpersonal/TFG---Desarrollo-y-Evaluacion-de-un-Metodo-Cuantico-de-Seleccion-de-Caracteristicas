from __future__ import annotations

from typing import List

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


def create_layout(layout: str = "1x3", figsize=None, dpi: int = 150):
    if layout == "1x2":
        fig, axes = plt.subplots(1, 2, figsize=figsize or (12, 4.8), dpi=dpi)
        return fig, list(axes)
    if layout == "1x3":
        fig, axes = plt.subplots(1, 3, figsize=figsize or (14, 5), dpi=dpi)
        return fig, list(axes)
    if layout == "2x2":
        fig, axes = plt.subplots(2, 2, figsize=figsize or (12, 8), dpi=dpi)
        return fig, [ax for row in axes for ax in row]
    if layout == "main_side":
        fig = plt.figure(figsize=figsize or (13, 4.8), dpi=dpi)
        gs = GridSpec(1, 2, figure=fig, width_ratios=[2.2, 1.0])
        axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
        return fig, axes
    if layout == "vertical_triptych":
        fig = plt.figure(figsize=figsize or (8.2, 9), dpi=dpi)
        gs = GridSpec(3, 1, figure=fig, hspace=0.28)
        axes = [fig.add_subplot(gs[i, 0]) for i in range(3)]
        return fig, axes
    fig, ax = plt.subplots(figsize=figsize or (8, 5), dpi=dpi)
    return fig, [ax]
