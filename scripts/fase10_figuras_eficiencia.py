"""Figuras de eficiencia y generalizacion (fase 10).

G1/F11  sobreajuste: brecha train-test por bloque y dataset (con semillas).
G2/F12  coste del modelo resultante: ajuste e inferencia, baseline vs seleccion.
G3/F13  coste de SELECCIONAR: clasico vs QFS (ordenes de magnitud); el modelo
        resultante es barato en ambos.

Mismo lenguaje visual que las superfiguras finalistas. Salida PNG+PDF en
results/figures/superfiguras_memoria_finalistas/.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
TAB = ROOT / "results" / "tables"
OUT = ROOT / "results" / "figures" / "superfiguras_memoria_finalistas"
OUT.mkdir(parents=True, exist_ok=True)

DATASETS = ["breast_cancer_wisconsin", "customer_churn", "madelon", "olive_oil_3class", "olive_oil_9class"]
DLAB = {
    "breast_cancer_wisconsin": "Breast Cancer",
    "customer_churn": "Customer Churn",
    "madelon": "Madelon",
    "olive_oil_3class": "Olive Oil 3 clases",
    "olive_oil_9class": "Olive Oil 9 clases",
}
GCOL = {"baseline": "#9e9e9e", "clasico": "#4f81bd", "cuantico": "#d95f5f"}
GLAB = {"baseline": "Todas las variables", "clasico": "Selección clásica", "cuantico": "Selección QFS-NA"}
BG, TEXT, GRID = "#f7f4ef", "#333333", "#ded9d1"

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 220, "savefig.bbox": "tight",
    "figure.facecolor": BG, "axes.facecolor": BG, "axes.edgecolor": "#8b867d",
    "axes.labelcolor": TEXT, "xtick.color": TEXT, "ytick.color": TEXT, "text.color": TEXT,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7, "grid.alpha": 0.7,
    "legend.frameon": False,
})


def add_title(fig, title, subtitle):
    fig.text(0.015, 0.985, title, fontsize=15.5, fontweight="bold", ha="left", va="top")
    fig.text(0.015, 0.945, subtitle, fontsize=10, ha="left", va="top", color="#5b5853")


def finish(ax):
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#b7b0a6")


def save(fig, stem):
    fig.savefig(OUT / f"{stem}.png")
    fig.savefig(OUT / f"{stem}.pdf")
    print(f"guardado: {stem}")


df = pd.read_csv(TAB / "10_eficiencia_generalizacion" / "eficiencia_generalizacion.csv")
# Bloque cuantico = QFS-NA operativo (se excluye el oraculo para la lectura principal).
main = df[df["feature_set"] != "qfs_oracle"].copy()
GRUPOS = ["baseline", "clasico", "cuantico"]


# ----------------------------------------------------------------------------- G1
def figura_g1():
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    fig.subplots_adjust(top=0.80, left=0.17, right=0.97, bottom=0.12)
    offsets = {"baseline": 0.26, "clasico": 0.0, "cuantico": -0.26}
    rng = np.random.default_rng(7)
    for di, ds in enumerate(DATASETS):
        for g in GRUPOS:
            vals = main[(main.dataset == ds) & (main.block == g)]["train_test_gap"].to_numpy()
            if vals.size == 0:
                continue
            y = di + offsets[g] + rng.uniform(-0.05, 0.05, size=vals.size)
            ax.scatter(vals, y, s=14, color=GCOL[g], alpha=0.30, edgecolor="none", zorder=2)
            ax.scatter(vals.mean(), di + offsets[g], s=95, color=GCOL[g], marker="D",
                       edgecolor="white", linewidth=1.1, zorder=4)
    ax.axvline(0, color="#b7b0a6", lw=1, zorder=1)
    ax.set_yticks(range(len(DATASETS)))
    ax.set_yticklabels([DLAB[d] for d in DATASETS])
    ax.set_ylim(-0.6, len(DATASETS) - 0.4)
    ax.invert_yaxis()
    ax.set_xlabel("brecha train − test de macro-F1  (mayor = más sobreajuste)")
    ax.annotate("500 → 19 variables:\nla brecha cae de 0.28 a 0.03",
                xy=(0.275, 2 + 0.26), xytext=(0.30, 0.55),
                fontsize=9, color="#7a3b3b", ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color="#7a3b3b", lw=1.1))
    handles = [Line2D([0], [0], marker="D", color="w", markerfacecolor=GCOL[g],
                      markersize=10, label=GLAB[g]) for g in GRUPOS]
    ax.legend(handles=handles, loc="upper right", fontsize=9.5)
    finish(ax)
    add_title(fig, "La selección recorta el sobreajuste justo donde sobra: alta dimensión",
              "Brecha train−test de macro-F1; cada punto es una semilla×modelo (10×4), el rombo es la media. "
              "Donde no hay sobreajuste (Churn, Olive) no hay nada que recortar.")
    save(fig, "F11_generalizacion_sobreajuste")
    plt.close(fig)


# ----------------------------------------------------------------------------- G2
def figura_g2():
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2))
    fig.subplots_adjust(top=0.80, left=0.13, right=0.975, bottom=0.20, wspace=0.28)
    metry = [("fit_seconds", "A. Coste de ajuste (s, escala log)", axes[0]),
             ("predict_us_per_sample", "B. Coste de inferencia (µs/muestra, log)", axes[1])]
    offsets = {"clasico": 0.16, "cuantico": -0.16}
    for col, titulo, ax in metry:
        for di, ds in enumerate(DATASETS):
            base = main[(main.dataset == ds) & (main.block == "baseline")][col].mean()
            for g in ("clasico", "cuantico"):
                sel = main[(main.dataset == ds) & (main.block == g)][col].mean()
                y = di + offsets[g]
                # flecha baseline -> seleccion: hacia la izquierda = mas barato
                ax.annotate("", xy=(sel, y), xytext=(base, y),
                            arrowprops=dict(arrowstyle="-|>", color=GCOL[g], lw=1.7, alpha=0.85), zorder=3)
                ax.scatter(sel, y, s=70, color=GCOL[g], zorder=4, edgecolor="white", linewidth=1.0)
            ax.scatter(base, di, s=95, color=GCOL["baseline"], zorder=5, edgecolor="white", linewidth=1.1)
        ax.set_xscale("log")
        ax.set_yticks(range(len(DATASETS)))
        ax.set_yticklabels([DLAB[d] for d in DATASETS] if ax is axes[0] else [])
        ax.set_ylim(-0.6, len(DATASETS) - 0.4)
        ax.invert_yaxis()
        ax.set_title(titulo, loc="left")
        finish(ax)
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=GCOL[g], markersize=10, label=GLAB[g])
               for g in GRUPOS]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=9.5, bbox_to_anchor=(0.55, 0.015))
    add_title(fig, "Menos variables abaratan ajuste e inferencia (donde había dimensión que recortar)",
              "Punto gris = todas las variables; la flecha lleva al modelo con selección (izquierda = más barato). "
              "En Customer Churn el one-hot no reduce columnas, así que no abarata.")
    save(fig, "F12_coste_modelo")
    plt.close(fig)


# ----------------------------------------------------------------------------- G3
def figura_g3():
    clas = pd.read_csv(TAB / "05_feature_selection" / "fs_all_execution_times.csv")
    qfs = pd.read_csv(TAB / "08_quantum" / "qfs_operational_summary.csv")
    sel_clas = clas.groupby("dataset")["elapsed_seconds"].sum()
    sel_qfs = qfs.groupby("dataset")["elapsed_seconds"].sum()
    modelo = main[main.block.isin(["clasico", "cuantico"])].groupby("dataset")["fit_seconds"].mean()

    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    fig.subplots_adjust(top=0.80, left=0.17, right=0.96, bottom=0.19)
    for di, ds in enumerate(DATASETS):
        c, q, m = sel_clas[ds], sel_qfs[ds], modelo[ds]
        ax.plot([m, q], [di, di], color="#cfc8bd", lw=1.4, zorder=1)
        ax.scatter(m, di, s=80, color="#9e9e9e", zorder=4, edgecolor="white", linewidth=1.0)
        ax.scatter(c, di, s=95, color="#4f81bd", zorder=4, edgecolor="white", linewidth=1.0)
        ax.scatter(q, di, s=110, color="#d95f5f", zorder=4, edgecolor="white", linewidth=1.0)
        ax.annotate(f"×{q / c:,.0f}".replace(",", "."), xy=(q, di), xytext=(q * 1.35, di),
                    fontsize=9, color="#7a3b3b", va="center")
    ax.set_xscale("log")
    ax.set_yticks(range(len(DATASETS)))
    ax.set_yticklabels([DLAB[d] for d in DATASETS])
    ax.set_ylim(-0.6, len(DATASETS) - 0.4)
    ax.invert_yaxis()
    ax.set_xlabel("segundos (escala log)")
    ax.set_xlim(0.02, 8000)
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#d95f5f", markersize=11, label="Seleccionar con QFS (barrido β)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#4f81bd", markersize=11, label="Seleccionar con métodos clásicos"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#9e9e9e", markersize=11, label="Ajustar el modelo final"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=9.2, bbox_to_anchor=(0.55, 0.01))
    finish(ax)
    add_title(fig, "Seleccionar con QFS cuesta dos órdenes de magnitud más; el modelo, lo mismo (poco)",
              "Coste de ejecutar la selección completa (clásica: 12 métodos×3 semillas; QFS: barrido de β en simulador) "
              "frente al ajuste del modelo final. El factor anota cuánto más cara es la selección QFS.")
    save(fig, "F13_coste_seleccion")
    plt.close(fig)


if __name__ == "__main__":
    figura_g1()
    figura_g2()
    figura_g3()
    print("Listo.")
