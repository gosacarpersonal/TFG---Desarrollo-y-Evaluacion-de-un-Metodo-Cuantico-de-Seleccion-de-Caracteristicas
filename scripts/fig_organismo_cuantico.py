#!/usr/bin/env python3
"""Organismo cuántico: mapa de átomos por formulación, color = densidad de Rydberg,
anillo = seleccionado por el corte top-k, etiqueta solo en seleccionados.
Datos verificados: posiciones MDS (positions_json) + densidad por variable
(qfs_runs_<ds>_<beta>.csv). Reglas de legibilidad estrictas (revisión externa)."""
import json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, "results/tables/08_quantum")
OUT = os.path.join(ROOT, "Plantilla_Latex_GCD/tfgs/figs")

BETAS = {  # beta elegido por validacion
    "breast_cancer_wisconsin": 0.1, "customer_churn": 0.9, "madelon": 0.1,
    "olive_oil_3class": 0.0, "olive_oil_9class": 0.2,
}
TITULOS = {
    "breast_cancer_wisconsin": "Breast Cancer W.", "customer_churn": "Customer Churn",
    "madelon": "Madelon (preselec. 20)", "olive_oil_3class": "Olive Oil (3 cl.)",
    "olive_oil_9class": "Olive Oil (9 cl.)",
}

def short(name):
    """Etiqueta corta y legible solo para variables seleccionadas."""
    if name.startswith("feat_"):
        return name.split("_")[1]
    rep = {"subscription_type_": "sub_", "contract_length_": "con_",
           "gender_": "gen_", "support_calls": "sup_calls",
           "payment_delay": "pay_delay", "total_spend": "tot_spend",
           "last_interaction": "last_int", "usage_frequency": "usage_freq",
           "_worst": "·w", "_mean": "·m", "_se": "·se"}
    for k, v in rep.items():
        name = name.replace(k, v)
    return name

def load(ds):
    b = BETAS[ds]
    emb = pd.read_csv(os.path.join(T, "qfs_embedding_error.csv"))
    erow = emb[(emb.dataset == ds) & (np.isclose(emb.beta, b))].iloc[0]
    pj = json.loads(erow["positions_json"])
    # radio de bloqueo: la razon de distancia es 1/sqrt(2) del radio de bloqueo,
    # luego R_b = min_radius / dist_ratio.
    rb = float(erow["min_radius"]) / float(erow["dist_ratio_rydberg"])
    runs = pd.read_csv(os.path.join(T, f"qfs_runs_{ds}_{str(b).replace('.', 'p')}.csv"))
    dens = {c[len("density__"):]: runs.iloc[0][c] for c in runs.columns if c.startswith("density__")}
    ops = pd.read_csv(os.path.join(T, "qfs_operational_summary.csv"))
    sel = set(ops[(ops.dataset == ds) & (np.isclose(ops.beta, b))].iloc[0]["selected_features"].split("|"))
    xs = np.array([d["x"] for d in pj]); ys = np.array([d["y"] for d in pj])
    fs = [d["feature"] for d in pj]
    dv = np.array([dens[f] for f in fs])
    return xs, ys, fs, dv, sel, b, rb

plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans"})
fig, axes = plt.subplots(2, 3, figsize=(11, 7.2))
axes = axes.ravel()
cmap = plt.cm.magma
norm = matplotlib.colors.Normalize(vmin=0, vmax=1)

for ax, ds in zip(axes, BETAS):
    xs, ys, fs, dv, sel, b, rb = load(ds)
    selm = np.array([f in sel for f in fs])
    # Radio de bloqueo de Rydberg (registro estilo disk-graph): discos de radio
    # R_b/2 alrededor de cada atomo; dos discos que se solapan = par bloqueado
    # (no pueden excitarse a la vez), lo que materializa el termino de redundancia.
    for x, y in zip(xs, ys):
        ax.add_patch(Circle((x, y), rb / 2.0, fill=False, ec="0.70",
                            lw=0.6, ls=(0, (3, 3)), alpha=0.30, zorder=1))
    ax.set_aspect("equal", adjustable="datalim")
    # no seleccionados: pequenos, tenues
    ax.scatter(xs[~selm], ys[~selm], c=dv[~selm], cmap=cmap, norm=norm,
               s=70, edgecolors="0.6", linewidths=0.6, alpha=0.85, zorder=2)
    # seleccionados: grandes, anillo negro
    ax.scatter(xs[selm], ys[selm], c=dv[selm], cmap=cmap, norm=norm,
               s=230, edgecolors="black", linewidths=1.6, zorder=3)
    # etiquetas solo seleccionados
    for x, y, f in zip(xs[selm], ys[selm], np.array(fs)[selm]):
        ax.annotate(short(f), (x, y), fontsize=6.2, ha="center", va="center",
                    zorder=5, color="black", xytext=(0, 12),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.12", fc="white",
                              ec="none", alpha=0.7))
    ax.set_title(f"{TITULOS[ds]}   ($\\beta={b:g}$)", fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("0.8")
    ax.margins(0.18)

# panel sobrante: leyenda arriba + colorbar abajo (sin solापes)
lax = axes[5]; lax.axis("off")
handles = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="0.7",
           markeredgecolor="black", markersize=14, markeredgewidth=1.6,
           label="seleccionado (top-$k$)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="0.7",
           markeredgecolor="0.6", markersize=9, label="no seleccionado"),
    Line2D([0], [0], color="0.6", lw=0.9, ls=(0, (3, 3)),
           label="radio de bloqueo (R$_b$/2)"),
]
lax.legend(handles=handles, loc="upper center", frameon=False, fontsize=9.5,
           title="átomo = variable", title_fontsize=10,
           bbox_to_anchor=(0.5, 0.95))

fig.tight_layout(rect=[0, 0, 1, 1])
# colorbar propia en la zona baja del 6o panel
pos = lax.get_position()
cax = fig.add_axes([pos.x0 + 0.01, pos.y0 + 0.04, pos.width * 0.55, 0.025])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
cbar.set_label("densidad de Rydberg media", fontsize=9)
cbar.ax.tick_params(labelsize=8)
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(OUT, f"qfs_organismo_cuantico.{ext}"), dpi=150, bbox_inches="tight")
print("OK ->", os.path.join(OUT, "qfs_organismo_cuantico.{pdf,png}"))
