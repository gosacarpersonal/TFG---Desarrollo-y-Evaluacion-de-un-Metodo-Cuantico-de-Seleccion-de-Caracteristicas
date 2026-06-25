"""O1 — El organismo de la selección (prueba del lenguaje tipo-WaPo).

Una sola rejilla densa: filas = 12 selectores (por familia), columnas = variables (ordenadas
por consenso), celda = frecuencia de selección a lo largo de toda la escalera de k y las
semillas. De lejos se ve el patrón (consenso vs páramo de distractores); de cerca, cada
celda es "este método elige esta variable con esta frecuencia". Datos reales: fs_all_rankings.
"""
from __future__ import annotations

import shutil
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bmf", ROOT / "scripts" / "build_memoria_figuras.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
BG, TEXT, MUTED, NEUTRAL, ACCENT, SECONDARY = b.BG, b.TEXT, b.MUTED, b.NEUTRAL, b.ACCENT, b.SECONDARY
OUT, FIGS = b.OUT, b.FIGS
FAM = b.METHOD_FAMILIES
FAMC = b.FAMILY_COLORS

ORDEN_FAMILIA = ["relevancia", "redundancia", "combinado", "wrapper", "embedded"]


def build(dataset: str = "madelon") -> None:
    b.set_editorial_rcparams()
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "savefig.dpi": 300})
    df = pd.read_csv(ROOT / "results/tables/05_feature_selection/fs_all_rankings.csv")
    df = df[df.dataset == dataset].copy()
    df["selected"] = df["selected"].astype(str).str.lower().isin(["true", "1", "1.0"])
    freq = df.groupby(["method", "feature"])["selected"].mean().unstack("feature")
    # orden de filas por familia; orden de columnas por consenso (frecuencia media)
    metodos = sorted(freq.index, key=lambda m: (ORDEN_FAMILIA.index(FAM.get(m, "embedded")), m))
    freq = freq.loc[metodos]
    col_order = freq.mean(axis=0).sort_values(ascending=False).index
    freq_full = freq[col_order]
    n_total = freq_full.shape[1]
    n_consenso = int((freq_full.mean(axis=0) > 0.3).sum())
    # Zoom a las variables consensuadas: con 500 columnas la señal (~16 vars) se
    # aplasta y el resto es ruido. Mostramos el bloque legible y declaramos el corte.
    topn = min(40, n_total)
    freq = freq_full.iloc[:, :topn]
    M = freq.to_numpy()

    fig = plt.figure(figsize=(13.0, 6.4), facecolor=BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[0.02, 1.0], wspace=0.015, left=0.17, right=0.95, top=0.82, bottom=0.22)
    axfam = fig.add_subplot(gs[0]); ax = fig.add_subplot(gs[1])

    cmap = LinearSegmentedColormap.from_list("sel", [BG, "#dce7f0", "#7aa6c2", "#2f5a8a"])
    im = ax.imshow(M, aspect="auto", cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
    ax.set_yticks(range(len(metodos)), [b.method_label(m) for m in metodos], fontsize=9)
    ax.set_xticks([])
    if n_total > topn:
        xlab = f"las {topn} variables más consensuadas de {n_total}  →   las ~{n_total - n_consenso} restantes son páramo (frecuencia ≈ 0)"
    else:
        xlab = f"{n_total} variables, ordenadas por consenso de selección  →"
    ax.set_xlabel(xlab, fontsize=9.8)
    for s in ax.spines.values():
        s.set_visible(False)
    # linea que separa el nucleo de consenso del resto
    if 0 < n_consenso < topn:
        ax.axvline(n_consenso - 0.5, color=ACCENT, lw=1.6, ls="--", zorder=4)
        ax.text(n_consenso + 0.3, 1.4, f"← ~{n_consenso} variables de consenso",
                fontsize=9, color=TEXT, fontweight="semibold", va="center")

    # tira de color de familia a la izquierda
    axfam.set_xlim(0, 1); axfam.set_ylim(len(metodos) - 0.5, -0.5); axfam.axis("off")
    for i, m in enumerate(metodos):
        axfam.add_patch(plt.Rectangle((0, i - 0.5), 1, 1, color=FAMC[FAM.get(m, "embedded")], alpha=0.85))

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015)
    cbar.set_label("Frecuencia de selección\n(sobre k y semillas)", fontsize=8.5)
    cbar.ax.tick_params(labelsize=8, colors=MUTED)

    handles = [plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=FAMC[f], markersize=9, label=f) for f in ORDEN_FAMILIA]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=5, frameon=False, fontsize=8.4,
              handletextpad=0.3, columnspacing=1.4, title="Familia de método (franja izquierda)", title_fontsize=8.4)

    fig.suptitle(f"Doce selectores convergen en ~{n_consenso} variables de {n_total}: el consenso emerge solo",
                 x=0.04, ha="left", fontsize=15, fontweight="semibold", color=TEXT, y=0.955)
    fig.text(0.04, 0.885, f"{b.display_dataset(dataset)} · cada celda = con qué frecuencia un método elige una variable (sobre la escalera de k y tres semillas)",
             ha="left", fontsize=9.4, color=MUTED)

    OUT.mkdir(parents=True, exist_ok=True); FIGS.mkdir(parents=True, exist_ok=True)
    stem = "o1_organismo_seleccion"
    png = OUT / f"{stem}.png"; pdf = OUT / f"{stem}.pdf"
    fig.savefig(png, facecolor=BG); fig.savefig(pdf, facecolor=BG)
    shutil.copy2(png, FIGS / png.name)
    plt.close(fig)
    print("O1 built:", png, "| shape:", M.shape)


if __name__ == "__main__":
    build()
