"""Figuras conceptuales del marco teórico (cap. 2).

Genera dos PDF vectoriales con estética limpia (fondo blanco), para apoyar
las secciones de fundamentos cuánticos (#13) y de formulación combinatoria
(#12). No usa datos: son esquemas pedagógicos.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "Plantilla_Latex_GCD" / "tfgs" / "figs"

BG = "#ffffff"
TEXT = "#333333"
MUTED = "#6f6a60"
ACCENT = "#4f81bd"
RED = "#d95f5f"
GRID = "#d7d0c7"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "savefig.bbox": "tight", "font.size": 10.5, "text.color": TEXT,
    "axes.edgecolor": "#c2c2c2", "axes.labelcolor": TEXT,
})


class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, _ = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs3d)


def bloch_sphere(ax) -> None:
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 20)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, color=GRID, linewidth=0.5, rstride=2, cstride=2, alpha=0.7)
    # ejes
    for a, b, c in [(1.3, 0, 0), (0, 1.3, 0), (0, 0, 1.35)]:
        ax.plot([0, a], [0, b], [0, c], color=MUTED, lw=0.9)
        ax.plot([0, -a], [0, -b], [0, -c], color=MUTED, lw=0.6, alpha=0.5)
    # estado de superposicion
    th, ph = np.pi / 3, np.pi / 4
    sx, sy, sz = np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)
    ax.add_artist(Arrow3D([0, sx], [0, sy], [0, sz], mutation_scale=16, lw=2.4, color=ACCENT, arrowstyle="-|>"))
    ax.text(0, 0, 1.55, r"$|0\rangle$", color=TEXT, fontsize=12, ha="center")
    ax.text(0, 0, -1.7, r"$|1\rangle$", color=TEXT, fontsize=12, ha="center")
    ax.text(sx + 0.15, sy, sz + 0.18, r"$\alpha|0\rangle+\beta|1\rangle$", color=ACCENT, fontsize=10.5, fontweight="bold")
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1)
    ax.set_box_aspect((1, 1, 1)); ax.axis("off")
    ax.view_init(elev=18, azim=30)
    ax.set_title("A. Cúbit y superposición", loc="center", fontsize=11, fontweight="semibold", pad=-2)


def entanglement(ax) -> None:
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    for cx, lab in [(0.28, "A"), (0.72, "B")]:
        circ = plt.Circle((cx, 0.58), 0.13, fill=False, edgecolor=MUTED, lw=1.4)
        ax.add_patch(circ)
        ax.text(cx, 0.58, lab, ha="center", va="center", fontsize=12, color=TEXT, fontweight="bold")
    # enlace ondulado
    xx = np.linspace(0.41, 0.59, 100)
    ax.plot(xx, 0.58 + 0.03 * np.sin((xx - 0.41) / 0.18 * 4 * np.pi), color=RED, lw=2)
    ax.annotate("estado conjunto\nno factorizable", xy=(0.5, 0.62), xytext=(0.5, 0.92),
                ha="center", va="top", fontsize=9, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1))
    ax.text(0.5, 0.30, "Al medir A queda fijada\nla medida de B:\ncorrelación sin análogo clásico",
            ha="center", va="top", fontsize=9, color=MUTED)
    ax.set_title("B. Entrelazamiento", loc="center", fontsize=11, fontweight="semibold", pad=-2)


def hamiltonian_levels(ax) -> None:
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    levels = [(0.22, "$E_0$  (estado fundamental)", ACCENT, "fundamental"),
              (0.55, "$E_1$", MUTED, ""), (0.72, "$E_2$", MUTED, ""), (0.85, r"$\vdots$", MUTED, "")]
    for y, lab, col, _ in levels:
        if lab == r"$\vdots$":
            ax.text(0.5, y, lab, ha="center", fontsize=12, color=col)
            continue
        ax.plot([0.25, 0.75], [y, y], color=col, lw=3 if col == ACCENT else 1.8)
        ax.text(0.80, y, lab, va="center", fontsize=10, color=TEXT if col == ACCENT else MUTED)
    ax.annotate("", xy=(0.18, 0.55), xytext=(0.18, 0.22),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.2))
    ax.text(0.13, 0.385, "gap", rotation=90, va="center", ha="center", fontsize=9, color=MUTED)
    ax.text(0.5, 0.06, "El hamiltoniano $H$ fija las energías;\nsu autovector de menor energía es la solución",
            ha="center", va="bottom", fontsize=9, color=MUTED)
    ax.set_title("C. Hamiltoniano y niveles de energía", loc="center", fontsize=11, fontweight="semibold", pad=-2)


def figura_cubit() -> None:
    fig = plt.figure(figsize=(13.0, 4.3), facecolor=BG)
    ax1 = fig.add_subplot(1, 3, 1, projection="3d")
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)
    bloch_sphere(ax1); entanglement(ax2); hamiltonian_levels(ax3)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02, wspace=0.05)
    out = FIGS / "mt_cubit_bloch.pdf"
    fig.savefig(out); plt.close(fig)
    print("built", out)


def figura_escalera_alpha() -> None:
    # Esquema (no datos): al recorrer alpha de 0 a 1, el optimo del QUBO
    # describe una escalera discreta de presupuestos k, con tramos planos y saltos.
    fig, ax = plt.subplots(figsize=(8.2, 4.6), facecolor=BG)
    alphas = np.array([0, 0.18, 0.18, 0.37, 0.37, 0.55, 0.55, 0.72, 0.72, 0.9, 0.9, 1.0])
    ks = np.array([1, 1, 3, 3, 4, 4, 7, 7, 8, 8, 11, 11])
    ax.step(alphas, ks, where="post", color=ACCENT, lw=2.6)
    # marca un presupuesto de referencia k* y el salto que lo omite
    ax.axhline(5, color=RED, ls="--", lw=1.3)
    ax.text(1.005, 5, r"$k^{\star}$ de referencia", color=RED, va="center", fontsize=9.5)
    ax.annotate("la escalera salta $k^{\\star}$:\nel óptimo exacto se resuelve\nentonces con $\\sum_i x_i=k^{\\star}$",
                xy=(0.46, 4), xytext=(0.05, 8.4), fontsize=9, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
    ax.set_xlabel(r"$\alpha$  (peso relevancia $\leftrightarrow$ redundancia)")
    ax.set_ylabel(r"cardinalidad del óptimo  $k=\sum_i x_i$")
    ax.set_xlim(0, 1.0); ax.set_ylim(0, 12)
    ax.set_title("La trayectoria de $\\alpha$ es una escalera discreta de presupuestos",
                 loc="left", fontsize=11.5, fontweight="semibold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.6, alpha=0.6)
    fig.subplots_adjust(left=0.11, right=0.82, top=0.9, bottom=0.13)
    out = FIGS / "mt_escalera_alpha.pdf"
    fig.savefig(out); plt.close(fig)
    print("built", out)


if __name__ == "__main__":
    figura_cubit()
    figura_escalera_alpha()
    print("listo")
