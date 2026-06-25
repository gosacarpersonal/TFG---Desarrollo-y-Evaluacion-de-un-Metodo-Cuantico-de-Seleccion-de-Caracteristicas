"""Cierre narrativo — el desenlace que cierra el arco abierto por EV4.

Segundo ejemplo del enfoque historia: no "QFS vs baseline" a secas, sino "dónde QFS iguala
y, donde falla, POR QUÉ" (criterio vs optimizador), con madelon y churn como protagonistas
y los problemas con señal clara en gris. Lee números reales.
"""
from __future__ import annotations

import shutil
import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bmf", ROOT / "scripts" / "build_memoria_figuras.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
BG, TEXT, MUTED, NEUTRAL, ACCENT, SECONDARY = b.BG, b.TEXT, b.MUTED, b.NEUTRAL, b.ACCENT, b.SECONDARY
OUT, FIGS = b.OUT, b.FIGS

OPT = "#d9883f"  # naranja cálido para "falla el optimizador"

# (dataset, baseline, qfs_na, oracle, veredicto, nota)
DATA = [
    ("olive_oil_3class", 1.000, 1.000, 1.000, "eq", None),
    ("breast_cancer_wisconsin", 0.937, 0.950, 0.937, "eq", None),
    ("olive_oil_9class", 0.839, 0.842, 0.906, "eq", None),
    ("customer_churn", 1.000, 0.922, 0.999, "opt",
     "El criterio vale (el óptimo exacto casi iguala\nal baseline) pero el optimizador analógico\nno converge → fallo de la implementación"),
    ("madelon", 0.813, 0.633, 0.643, "crit",
     "QFS optimiza bien su criterio, pero el criterio\nfalla: la información mutua no ve las\ninteracciones que hacen útil a cada variable"),
]
COLOR = {"eq": NEUTRAL, "opt": OPT, "crit": ACCENT}
ETIQ = {"eq": "Iguala (menos variables)", "opt": "Falla el optimizador", "crit": "Falla el criterio"}


def build() -> None:
    b.set_editorial_rcparams()
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "savefig.dpi": 300})
    fig, ax = plt.subplots(figsize=(12.4, 6.6), facecolor=BG)
    ys = list(range(len(DATA)))
    for y, (ds, base, na, ora, verd, nota) in zip(ys, DATA):
        c = COLOR[verd]
        prot = verd in ("opt", "crit")
        # camino baseline -> QFS-NA (la historia es el cambio)
        ax.plot([base, na], [y, y], "-", color=c, lw=2.8 if prot else 1.6, alpha=0.9 if prot else 0.45, zorder=2)
        ax.scatter([base], [y], s=70, facecolor=BG, edgecolor=MUTED, linewidth=1.6, zorder=3)
        ax.scatter([na], [y], s=95 if prot else 60, color=c, zorder=4, alpha=1.0 if prot else 0.6)
        # oráculo como referencia tenue (dónde el criterio exacto recupera)
        if abs(ora - na) > 0.01:
            ax.scatter([ora], [y], s=46, facecolor="none", edgecolor=c, linewidth=1.4, zorder=3)
        ax.annotate(b.display_dataset(ds), (min(base, na), y), xytext=(-10, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=9, color=TEXT if prot else MUTED,
                    fontweight="semibold" if prot else "normal")
    # anotaciones del porqué (solo protagonistas), en zonas vacías y sin solaparse
    ax.annotate(DATA[4][5], (0.633, 4), xytext=(0.70, 3.55), textcoords="data", fontsize=8.6, color=ACCENT,
                va="top", arrowprops={"arrowstyle": "->", "color": ACCENT})
    ax.annotate(DATA[3][5], (0.922, 3), xytext=(0.575, 1.7), textcoords="data", fontsize=8.6, color=OPT,
                va="top", arrowprops={"arrowstyle": "->", "color": OPT})
    # leyenda manual de marcadores
    ax.scatter([], [], s=70, facecolor=BG, edgecolor=MUTED, linewidth=1.6, label="Baseline (todas las variables)")
    ax.scatter([], [], s=90, color=NEUTRAL, label="QFS-NA (simulador)")
    ax.scatter([], [], s=46, facecolor="none", edgecolor=TEXT, linewidth=1.4, label="Óptimo exacto (oráculo)")
    ax.legend(loc="lower left", frameon=False, fontsize=8.4)
    ax.set_yticks([]); ax.set_ylim(-0.6, len(DATA) - 0.4)
    ax.set_xlim(0.55, 1.03)
    ax.set_xlabel("Macro-F1 en test")
    b.apply_editorial_axes(ax, grid_axis="x")
    fig.suptitle("QFS iguala donde hay señal clara; donde no, sabemos exactamente por qué",
                 x=0.09, ha="left", fontsize=15, fontweight="semibold", color=TEXT, y=0.96)
    fig.text(0.09, 0.90, "Baseline → subconjunto QFS por dataset; el óptimo exacto separa fallo de criterio (Madelon) de fallo de optimizador (Churn)",
             ha="left", fontsize=9.6, color=MUTED)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.84, bottom=0.12)

    OUT.mkdir(parents=True, exist_ok=True); FIGS.mkdir(parents=True, exist_ok=True)
    png = OUT / "ev7_cierre_narrativo.png"; pdf = OUT / "ev7_cierre_narrativo.pdf"
    fig.savefig(png, facecolor=BG); fig.savefig(pdf, facecolor=BG)
    shutil.copy2(png, FIGS / png.name)
    plt.close(fig)
    print("EV7 built:", png)


if __name__ == "__main__":
    build()
