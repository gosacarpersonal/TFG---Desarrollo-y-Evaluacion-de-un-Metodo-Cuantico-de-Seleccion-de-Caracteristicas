"""Scorecard de evidencia — tercer sabor narrativo.

Hipótesis: lo que transmite "todo lo que he hecho y merece la pena" no es una figura de un
solo mensaje, sino ver de un vistazo la CADENA de evidencia verificada por dataset. Lee
valores reales; donde un dato proviene de olive combinado (FDR de fase 1) se documenta.
"""
from __future__ import annotations

import shutil
import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bmf", ROOT / "scripts" / "build_memoria_figuras.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
BG, TEXT, MUTED, NEUTRAL, ACCENT, SECONDARY = b.BG, b.TEXT, b.MUTED, b.NEUTRAL, b.ACCENT, b.SECONDARY
OUT, FIGS = b.OUT, b.FIGS

OK = "#7fa37a"      # verde apagado: garantía cumplida
WARN = "#d9a441"    # ámbar: cautela / a techo
BAD = "#c75c54"     # rojo: atención / fallo

DATASETS = ["breast_cancer_wisconsin", "customer_churn", "madelon", "olive_oil_3class", "olive_oil_9class"]
COLS = ["Señal real\n(FDR)", "Particiones\n(adversarial)", "Estabilidad\n(Jaccard)",
        "Selección\nvs baseline", "Veredicto\nQFS"]
# (texto, color) por celda; valores reales verificados
CELLS = {
    "breast_cancer_wisconsin": [("27/30", OK), ("0.52", OK), ("0.98", OK), ("=  (+0.01)", OK), ("iguala", OK)],
    "customer_churn":          [("10/10", OK), ("0.52", OK), ("0.96", OK), ("≈ techo", WARN), ("opt. falla", BAD)],
    "madelon":                 [("13/500", BAD), ("0.48", OK), ("0.98", OK), ("+0.094 ✔", OK), ("crit. falla", BAD)],
    "olive_oil_3class":        [("10/10*", OK), ("0.51", OK), ("1.00", OK), ("=  (1.000)", OK), ("iguala", OK)],
    "olive_oil_9class":        [("10/10*", OK), ("0.54", OK), ("0.99", OK), ("=  (n=86)", WARN), ("iguala", OK)],
}


def build() -> None:
    b.set_editorial_rcparams()
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "savefig.dpi": 300})
    fig, ax = plt.subplots(figsize=(12.2, 5.9), facecolor=BG)
    nC, nR = len(COLS), len(DATASETS)
    ax.set_xlim(0, nC + 1.6); ax.set_ylim(0, nR + 2.2); ax.axis("off"); ax.invert_yaxis()
    # cabeceras de columna
    for j, c in enumerate(COLS):
        ax.text(1.6 + j + 0.5, 0.45, c, ha="center", va="center", fontsize=9, color=TEXT, fontweight="semibold")
    # filas
    for i, ds in enumerate(DATASETS):
        prot = ds in ("madelon", "customer_churn")
        ax.text(1.5, 1.2 + i + 0.5, b.display_dataset(ds), ha="right", va="center",
                fontsize=9.4, color=TEXT, fontweight="semibold" if prot else "normal")
        for j, (txt, col) in enumerate(CELLS[ds]):
            x, y = 1.6 + j, 1.2 + i
            ax.add_patch(FancyBboxPatch((x + 0.06, y + 0.08), 0.88, 0.84,
                         boxstyle="round,pad=0.0,rounding_size=0.06", linewidth=0, facecolor=col, alpha=0.85))
            ax.text(x + 0.5, y + 0.5, txt, ha="center", va="center", fontsize=8.6,
                    color="#ffffff" if col in (BAD,) else TEXT, fontweight="semibold")
    # leyenda semántica (debajo de la tabla, sin solapar la última fila)
    yleg = nR + 1.55
    for k, (lab, col) in enumerate([("garantía", OK), ("cautela", WARN), ("atención", BAD)]):
        ax.add_patch(FancyBboxPatch((1.6 + k * 1.9, yleg), 0.3, 0.34, boxstyle="round,pad=0,rounding_size=0.05",
                     linewidth=0, facecolor=col, alpha=0.85))
        ax.text(1.98 + k * 1.9, yleg + 0.17, lab, va="center", fontsize=8.6, color=MUTED)
    ax.text(1.6, yleg + 0.85, "* FDR de Olive sobre la formulación combinada de fase 1", ha="left", va="center", fontsize=7.4, color=MUTED)
    fig.suptitle("Cada dataset atraviesa la misma cadena de evidencia verificada",
                 x=0.07, ha="left", fontsize=15, fontweight="semibold", color=TEXT, y=0.95)
    fig.text(0.07, 0.885, "De la señal cruda al veredicto cuántico; el color resume el estado de cada garantía por dataset",
             ha="left", fontsize=9.8, color=MUTED)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.80, bottom=0.04)

    OUT.mkdir(parents=True, exist_ok=True); FIGS.mkdir(parents=True, exist_ok=True)
    png = OUT / "ev8_scorecard_evidencia.png"; pdf = OUT / "ev8_scorecard_evidencia.pdf"
    fig.savefig(png, facecolor=BG); fig.savefig(pdf, facecolor=BG)
    shutil.copy2(png, FIGS / png.name)
    plt.close(fig)
    print("EV8 built:", png)


if __name__ == "__main__":
    build()
