"""F6 (reescritura como organismo) — Beeswarm SHAP por instancia.

El F6 actual reduce SHAP a una barra de media |SHAP| (y solo en 2/5 datasets): tira la
dimensión más rica que se computó, la dispersion y la DIRECCION del efecto por instancia.
Este beeswarm la recupera: cada punto es una validacion real; su posicion x es la
contribucion SHAP a la prediccion y su color, el valor (estandarizado) de la variable.
De lejos se ve que variable manda; de cerca, como un valor alto/bajo empuja la decision.

Datos reales (sin transformar): modeling_shap_values_full_* (SHAP por instancia) y
modeling_shap_feature_values_* (valor de la variable por instancia), fase 6.
Caso del cuerpo: breast_cancer_wisconsin, subconjunto confirmado por Boruta (22 vars),
linear_svm — el candidato elegido por validacion en la Tabla 5.1.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bmf", ROOT / "scripts" / "build_memoria_figuras.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
BG, TEXT, MUTED, NEUTRAL, ACCENT, SECONDARY = b.BG, b.TEXT, b.MUTED, b.NEUTRAL, b.ACCENT, b.SECONDARY
OUT, FIGS = b.OUT, b.FIGS

DATASET = "breast_cancer_wisconsin"
FEATSET = "boruta_confirmed_22"
MODEL = "linear_svm"
TOP_N = 12


def _beeswarm_offsets(x: np.ndarray, n_bins: int = 28, max_spread: float = 0.42) -> np.ndarray:
    """Asigna un desplazamiento vertical por densidad local (pseudo-beeswarm honesto)."""
    y = np.zeros_like(x, dtype=float)
    if len(x) == 0:
        return y
    edges = np.linspace(np.min(x), np.max(x) + 1e-9, n_bins + 1)
    idx = np.clip(np.digitize(x, edges) - 1, 0, n_bins - 1)
    for bbin in np.unique(idx):
        members = np.where(idx == bbin)[0]
        c = len(members)
        if c == 1:
            y[members] = 0.0
            continue
        # repartir simetricamente alrededor de 0, escalado por densidad relativa
        spread = max_spread * min(1.0, c / 8.0)
        y[members] = np.linspace(-spread, spread, c)
    return y


def build() -> None:
    b.set_editorial_rcparams()
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "savefig.dpi": 300})

    shap = pd.read_csv(ROOT / f"results/tables/06_modeling/modeling_shap_values_full_{DATASET}__{FEATSET}__{MODEL}.csv")
    fval = pd.read_csv(ROOT / f"results/tables/06_modeling/modeling_shap_feature_values_{DATASET}__{FEATSET}__{MODEL}.csv")
    feats = [c for c in shap.columns if c != "row_position"]

    order = (
        pd.Series({f: shap[f].abs().mean() for f in feats})
        .sort_values(ascending=False)
        .index.tolist()
    )
    top = order[:TOP_N]
    n_inst = len(shap)

    fig = plt.figure(figsize=(11.6, 7.2), facecolor=BG)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.255, right=0.9, top=0.80, bottom=0.115)

    cmap = LinearSegmentedColormap.from_list("fval", ["#5b7fa6", "#cdd3d8", SECONDARY])
    norm = Normalize(vmin=-2.2, vmax=2.2)  # valores estandarizados (z), recortados para color

    ax.axvline(0.0, color=MUTED, lw=1.0, alpha=0.6, zorder=1)
    for row, feat in enumerate(reversed(top)):  # el mas importante arriba
        sv = shap[feat].to_numpy()
        vv = np.clip(fval[feat].to_numpy(), -2.2, 2.2)
        off = _beeswarm_offsets(sv)
        ax.scatter(sv, np.full_like(sv, row) + off, c=vv, cmap=cmap, norm=norm,
                   s=15, alpha=0.82, linewidths=0, zorder=3)

    ax.set_yticks(range(len(top)), [b.method_label(f) for f in reversed(top)], fontsize=9.3)
    ax.set_ylim(-0.7, len(top) - 0.3)
    ax.set_xlabel("Contribucion SHAP a la prediccion  (← clase benigna   ·   maligna →)", fontsize=10)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=b.GRID, lw=0.6, alpha=0.5)
    ax.set_axisbelow(True)

    # protagonista: la variable top
    prot = top[0]
    ax.annotate(
        f"{b.method_label(prot)}: la que mas\npesa; valores altos empujan\na maligno",
        xy=(shap[prot].quantile(0.92), len(top) - 1), xytext=(0.62, 0.74),
        textcoords="axes fraction", fontsize=9, color=TEXT, fontweight="semibold",
        arrowprops={"arrowstyle": "->", "color": ACCENT, "lw": 1.3}, ha="left",
    )

    # colorbar del valor de la variable
    sm = ScalarMappable(norm=norm, cmap=cmap); sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.022, pad=0.02)
    cbar.set_label("valor de la variable\n(bajo → alto, z)", fontsize=8.6)
    cbar.ax.tick_params(labelsize=8, colors=MUTED)
    cbar.outline.set_visible(False)

    fig.text(0.255, 0.945, "Las variables que la seleccion retuvo son las que sostienen el modelo",
             fontsize=14.5, color=TEXT, fontweight="bold", ha="left")
    fig.text(0.255, 0.905,
             f"SHAP por instancia · Breast Cancer · subconjunto Boruta ({FEATSET.split('_')[-1]} vars) · SVM lineal · "
             f"n={n_inst} validacion · top {TOP_N} de {len(feats)}",
             fontsize=9.6, color=MUTED, ha="left")
    fig.text(0.255, 0.04,
             "Cada punto es una muestra de validacion. SHAP explica el modelo, no causalidad.",
             fontsize=8.8, color=MUTED, ha="left")

    OUT.mkdir(parents=True, exist_ok=True); FIGS.mkdir(parents=True, exist_ok=True)
    png = OUT / "f6_shap_beeswarm_bcw.png"
    fig.savefig(png, dpi=300, facecolor=BG)
    import shutil
    shutil.copy(png, FIGS / "f6_shap_beeswarm_bcw.png")
    plt.close(fig)
    print(f"OK -> {png}  ({n_inst} instancias, top {TOP_N})")


if __name__ == "__main__":
    build()
