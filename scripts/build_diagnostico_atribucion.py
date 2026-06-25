"""Plano de atribucion del deterioro de QFS — la tesis del TFG hecha imagen.

Idea (derivada del problema, no de una plantilla): cuando QFS-NA empeora frente al baseline,
ese deterioro se DESCOMPONE en dos faltas independientes, ambas en las mismas unidades de
macro-F1 y por tanto comparables entre datasets:

    deterioro_total = (F1_baseline - F1_oraculo)  +  (F1_oraculo - F1_QFS_NA)
                       \_______ criterio _______/    \______ optimizador ______/

- Criterio: ¿el OPTIMO EXACTO del QUBO (oraculo, misma cardinalidad k) predice bien? Si no,
  la formulacion por informacion mutua es el limite (no el hardware).
- Optimizador: ¿la dinamica analogica ALCANZA ese optimo? Si no, el limite es la optimizacion.

Cada dataset es un punto en el plano (optimizador →, criterio ↑). Madelon y Churn caen en
cuadrantes OPUESTOS: la misma imagen prueba que los dos deterioros tienen causas distintas.
Datos reales: comparacion_qfs_configuraciones_vs_baseline.csv (fase 9). Sin transformar.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bmf", ROOT / "scripts" / "build_memoria_figuras.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
BG, TEXT, MUTED, NEUTRAL, ACCENT, SECONDARY, GRID = b.BG, b.TEXT, b.MUTED, b.NEUTRAL, b.ACCENT, b.SECONDARY, b.GRID
OUT, FIGS, LABELS = b.OUT, b.FIGS, b.LABELS

CRIT_COLOR = "#b5651d"   # criterio (calido) — protagonista Madelon
OPT_COLOR = "#3d6b8e"    # optimizador (frio) — protagonista Churn


def build() -> None:
    b.set_editorial_rcparams()
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "savefig.dpi": 300})

    comp = pd.read_csv(ROOT / "results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv")
    rows = []
    for d in LABELS:
        na = comp[(comp.dataset == d) & (comp.configuration == "qfs_na")].iloc[0]
        orc = comp[(comp.dataset == d) & (comp.configuration == "qfs_oracle_mucke")].iloc[0]
        base = float(na.baseline_test_macro_f1)
        f_orac = float(orc.qfs_test_macro_f1)
        f_na = float(na.qfs_test_macro_f1)
        rows.append(dict(dataset=d, base=base, oracle=f_orac, na=f_na,
                         criterio=base - f_orac, optimizador=f_orac - f_na, total=base - f_na))
    t = pd.DataFrame(rows)

    fig = plt.figure(figsize=(10.6, 7.4), facecolor=BG)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.115, right=0.965, top=0.80, bottom=0.115)

    xmin, xmax = -0.03, 0.10
    ymin, ymax = -0.10, 0.20
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)

    # regiones de fallo (muy tenues)
    ax.axhspan(0.02, ymax, xmin=0, xmax=1, color=CRIT_COLOR, alpha=0.045, zorder=0)
    ax.axvspan(0.02, xmax, ymin=0, ymax=1, color=OPT_COLOR, alpha=0.05, zorder=0)
    ax.axhline(0, color=MUTED, lw=0.9, alpha=0.6, zorder=1)
    ax.axvline(0, color=MUTED, lw=0.9, alpha=0.6, zorder=1)

    # etiquetas de region (en las esquinas, lejos de los puntos)
    ax.text(-0.028, 0.196, "limitado por el CRITERIO", color=CRIT_COLOR, fontsize=10.5,
            fontweight="bold", va="top", ha="left")
    ax.text(-0.028, 0.179, "el óptimo exacto ya predice mal:\nla información mutua no ve las\ninteracciones de orden superior",
            color=CRIT_COLOR, fontsize=8.3, va="top", ha="left", alpha=0.9)
    ax.text(xmax - 0.002, -0.088, "limitado por el OPTIMIZADOR", color=OPT_COLOR, fontsize=10.5,
            fontweight="bold", va="bottom", ha="right")
    ax.text(xmax - 0.002, -0.072, "la dinámica analógica no alcanza el\nmínimo de su propia función de coste",
            color=OPT_COLOR, fontsize=8.3, va="bottom", ha="right", alpha=0.9)
    ax.text(-0.028, -0.05, "QFS iguala o mejora\n(sin fallo atribuible)", color=MUTED,
            fontsize=8.4, va="center", ha="left", style="italic")

    prot = {"madelon": CRIT_COLOR, "customer_churn": OPT_COLOR}
    label_off = {  # desplazamientos a medida para evitar colisiones
        "madelon": (10, 4), "customer_churn": (10, 2),
        "breast_cancer_wisconsin": (2, 11), "olive_oil_3class": (6, -14),
        "olive_oil_9class": (-12, 10),
    }
    for r in t.itertuples():
        is_prot = r.dataset in prot
        c = prot.get(r.dataset, NEUTRAL)
        ax.scatter(r.optimizador, r.criterio, s=240 if is_prot else 120,
                   color=c, alpha=0.95 if is_prot else 0.55, zorder=4,
                   edgecolors=BG, linewidths=1.5)
        ha = "right" if r.dataset == "olive_oil_9class" else "left"
        ax.annotate(LABELS[r.dataset], (r.optimizador, r.criterio),
                    xytext=label_off[r.dataset], textcoords="offset points", ha=ha,
                    fontsize=10.5 if is_prot else 8.8,
                    color=TEXT if is_prot else MUTED,
                    fontweight="bold" if is_prot else "normal", zorder=5)

    # anotaciones de la descomposicion en los dos protagonistas
    md = t[t.dataset == "madelon"].iloc[0]
    ax.annotate(f"deterioro {md.total*100:.0f} pts  =  {md.criterio*100:.0f} criterio  +  {md.optimizador*100:.0f} optimizador",
                xy=(md.optimizador + 0.002, md.criterio), xytext=(0.026, 0.139),
                textcoords="data", fontsize=8.8, color=CRIT_COLOR, ha="left", fontweight="semibold",
                arrowprops={"arrowstyle": "->", "color": CRIT_COLOR, "lw": 1.2})
    ch = t[t.dataset == "customer_churn"].iloc[0]
    ax.annotate(f"deterioro {ch.total*100:.0f} pts  =  {ch.criterio*100:.0f} criterio  +  {ch.optimizador*100:.0f} optimizador",
                xy=(ch.optimizador, ch.criterio + 0.004), xytext=(0.034, 0.052),
                textcoords="data", fontsize=8.8, color=OPT_COLOR, ha="left", fontweight="semibold",
                arrowprops={"arrowstyle": "->", "color": OPT_COLOR, "lw": 1.2})

    ax.set_xlabel("Fallo del OPTIMIZADOR  →   (F1 del óptimo exacto − F1 de QFS-NA, puntos de macro-F1)", fontsize=9.8)
    ax.set_ylabel("Fallo del CRITERIO  →   (F1 del baseline − F1 del óptimo exacto)", fontsize=9.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.set_xticks(np.arange(-0.02, 0.11, 0.02)); ax.set_yticks(np.arange(-0.10, 0.21, 0.05))

    fig.text(0.115, 0.945, "Cuando QFS falla, el control frente al óptimo exacto dice POR QUÉ",
             fontsize=15, color=TEXT, fontweight="bold", ha="left")
    fig.text(0.115, 0.905,
             "El deterioro frente al baseline se descompone, en puntos de macro-F1, en fallo de criterio (la formulación)\n"
             "y fallo de optimizador (la dinámica analógica). Madelon y Churn: misma magnitud de daño, causas opuestas.",
             fontsize=9.3, color=MUTED, ha="left")

    OUT.mkdir(parents=True, exist_ok=True); FIGS.mkdir(parents=True, exist_ok=True)
    png = OUT / "diag_atribucion_qfs.png"
    fig.savefig(png, dpi=300, facecolor=BG)
    import shutil
    shutil.copy(png, FIGS / "diag_atribucion_qfs.png")
    plt.close(fig)
    print(t.to_string(index=False))
    print(f"\nOK -> {png}")


if __name__ == "__main__":
    build()
