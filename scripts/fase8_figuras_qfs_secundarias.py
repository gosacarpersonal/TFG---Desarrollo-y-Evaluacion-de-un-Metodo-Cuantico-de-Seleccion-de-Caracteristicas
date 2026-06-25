"""Regenera las figuras QFS secundarias con datos 1/sqrt(2), en su sitio
(mismos nombres que usa la memoria), estilo de las finalistas.

Borra el ultimo rastro de 0.45 en el PDF. Cada figura se dibuja desde las
tablas canonicas ya regeneradas a 1/sqrt(2).
"""
from __future__ import annotations
import ast, glob, json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
T8 = ROOT / "results" / "tables" / "08_quantum"
T5 = ROOT / "results" / "tables" / "05_feature_selection"
FIGS = ROOT / "Plantilla_Latex_GCD" / "tfgs" / "figs"

DS = ["breast_cancer_wisconsin", "customer_churn", "madelon", "olive_oil_3class", "olive_oil_9class"]
DLAB = {"breast_cancer_wisconsin": "Breast Cancer", "customer_churn": "Customer Churn",
        "madelon": "Madelon", "olive_oil_3class": "Olive Oil 3", "olive_oil_9class": "Olive Oil 9"}
DCOL = {"breast_cancer_wisconsin": "#4f81bd", "customer_churn": "#d9b382", "madelon": "#d95f5f",
        "olive_oil_3class": "#8fb7a8", "olive_oil_9class": "#7aa6c2"}
K_BY = {"olive_oil_3class": 5, "olive_oil_9class": 5, "customer_churn": 10,
        "breast_cancer_wisconsin": 10, "madelon": 10}
BG, TEXT, GRID = "#ffffff", "#333333", "#e6e6e6"
plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 220, "savefig.bbox": "tight",
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "axes.edgecolor": "#c2c2c2",
    "axes.labelcolor": TEXT, "xtick.color": TEXT, "ytick.color": TEXT, "text.color": TEXT,
    "font.size": 9.5, "axes.titlesize": 10.5, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7, "grid.alpha": 0.6,
    "legend.frameon": False})


def title(fig, t, s):
    fig.text(0.015, 0.99, t, fontsize=12.5, fontweight="bold", ha="left", va="top")
    fig.text(0.015, 0.99 - 1.05 / fig.get_size_inches()[1] * 0.5, s,
             fontsize=9, ha="left", va="top", color="#5b5853")


def save(fig, stem):
    fig.savefig(FIGS / f"{stem}.png"); fig.savefig(FIGS / f"{stem}.pdf"); plt.close(fig)
    print("OK", stem)


def J(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if (a | b) else 0.0


sel = pd.read_csv(T8 / "qfs_selected_all.csv")
def qfs_feats(ds, cfg="qfs_na"):
    r = sel[(sel.dataset == ds) & (sel.configuration == cfg)]
    return [f for f in str(r.iloc[0].selected_features).split("|") if f] if len(r) else []

fs = pd.read_csv(T5 / "fs_all_selected_features.csv")
def classic_feats(ds, method, k, seed=42):
    s = fs[(fs.dataset == ds) & (fs.method == method) & (fs.k == k) & (fs.seed == seed) & (fs.selected == True)]
    return s.feature.tolist()

METHODS12 = ["variance", "f_classif", "mutual_info", "mutual_correlation", "feature_similarity",
             "mrmr_approx", "rrfs", "l1_logistic", "random_forest", "linear_svm", "rfe", "boruta"]


# ---------------------------------------------------------------- f10_b9 atomos+error
def fig_atomos():
    # Rediseno: las nubes MDS no tienen estructura interpretable (y se confunden
    # con la fig 4.10). La pregunta es "¿la geometria explica el deterioro?": la
    # metrica que la responde es el ERROR de embebido por dataset.
    emb = pd.read_csv(T8 / "qfs_embedding_error.csv")
    rows = []
    for ds in DS:
        b = sel[(sel.dataset == ds) & (sel.configuration == "qfs_na")].iloc[0].beta
        row = emb[(emb.dataset == ds) & (np.isclose(emb.beta, b))].iloc[0]
        rows.append((ds, float(row.embedding_error_mean)))
    d = pd.DataFrame(rows, columns=["dataset", "err"]).sort_values("err").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    fig.subplots_adjust(top=0.78, bottom=0.13, left=0.16, right=0.95)
    focus = {"customer_churn", "breast_cancer_wisconsin"}
    colors = [DCOL[x] if x in focus else "#c8c0b7" for x in d.dataset]
    y = np.arange(len(d))
    ax.barh(y, d.err, color=colors, edgecolor="#333", linewidth=0.5, zorder=3)
    for i, v in enumerate(d.err):
        ax.text(v + d.err.max() * 0.02, i, f"{v:.3f}", va="center", fontsize=9, color=TEXT)
    ax.set_yticks(y, [DLAB[x] for x in d.dataset])
    ax.set_xlabel("error medio de embebido MDS  (menor = mejor geometría)")
    ax.set_xlim(0, d.err.max() * 1.18)
    ax.grid(axis="x", alpha=0.5)
    title(fig, "La geometría del embebido no explica el deterioro de Customer Churn",
          "Error medio de embebido (MDS) por dataset, en la configuración elegida. Customer Churn (se deteriora) y Breast Cancer (no) tienen un error casi idéntico.")
    save(fig, "f10_b9_atomos_mds_error")


# ---------------------------------------------------------------- f10_b2 jaccard 12
def fig_jaccard12():
    M = np.zeros((len(DS), len(METHODS12)))
    for i, ds in enumerate(DS):
        q = qfs_feats(ds); k = K_BY[ds]
        for j, m in enumerate(METHODS12):
            cf = classic_feats(ds, m, k)
            M[i, j] = J(q, cf) if cf else np.nan
    fig, ax = plt.subplots(figsize=(11, 3.6))
    fig.subplots_adjust(top=0.74, bottom=0.22, left=0.12, right=1.0)
    im = ax.imshow(M, cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(METHODS12))); ax.set_xticklabels(METHODS12, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(DS))); ax.set_yticklabels([DLAB[d] for d in DS])
    ax.grid(False)
    for i in range(len(DS)):
        for j in range(len(METHODS12)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if M[i, j] > 0.55 else "#333333")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01, label="Jaccard")
    title(fig, "¿A qué familia clásica se parece la selección de QFS-NA?",
          "Solape de variables (Jaccard) entre el subconjunto QFS-NA y cada selector clásico, al presupuesto de referencia.")
    save(fig, "f10_b2_jaccard_12_metodos")


# ---------------------------------------------------------------- explor_mapa (espejo plano)
def fig_mapa():
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    fig.subplots_adjust(top=0.80, bottom=0.12, left=0.1, right=0.97)
    for ds in DS:
        q = qfs_feats(ds); k = K_BY[ds]
        jq = {m: J(q, classic_feats(ds, m, k)) for m in ["mrmr_approx", "mutual_correlation", "f_classif"] if classic_feats(ds, m, k)}
        # x: parecido a mRMR (combinado), y: parecido a correlación (redundancia)
        ax.scatter(jq.get("mrmr_approx", 0), jq.get("mutual_correlation", 0), s=160,
                   color=DCOL[ds], edgecolor="white", linewidth=1.2, zorder=3, label=DLAB[ds])
    ax.plot([0, 1], [0, 1], color="#b7b0a6", lw=1, ls="--", zorder=1)
    ax.set_xlabel("solape con mRMR (compromiso combinado)")
    ax.set_ylabel("solape con correlación mutua (redundancia)")
    ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper left", fontsize=9)
    title(fig, "QFS-NA vive en el nicho relevancia-redundancia de los selectores clásicos",
          "Cada dataset según cuánto se parece el subconjunto QFS-NA a mRMR y a la correlación mutua (Jaccard).")
    save(fig, "explor_mapa_metodos")


# ---------------------------------------------------------------- ev6 rendimiento vs k
def fig_ev6():
    ev = pd.read_csv(T8 / "ev6_rendimiento_vs_k.csv")
    fsets = {fsv: c for fsv, c in zip(sorted(ev.feature_set.unique()),
             ["#9e9e9e", "#4f81bd", "#d95f5f", "#8fb7a8"])}
    fig, axes = plt.subplots(1, 5, figsize=(13, 3.7), sharey=False)
    fig.subplots_adjust(top=0.74, bottom=0.16, left=0.05, right=0.99, wspace=0.3)
    for ax, ds in zip(axes, DS):
        sub = ev[ev.dataset == ds]
        for fsv in sub.feature_set.unique():
            s = sub[sub.feature_set == fsv].sort_values("k")
            ax.plot(s.k, s.validation_macro_f1, marker="o", ms=3, lw=1.5,
                    color=fsets.get(fsv, "#777"), label=fsv)
        ax.set_title(DLAB[ds], fontsize=9); ax.set_xlabel("k")
    axes[0].set_ylabel("macro-F1 val")
    axes[-1].legend(fontsize=7, loc="lower right")
    title(fig, "El rendimiento se estabiliza con pocos atributos: el presupuesto k elegido es robusto",
          "Macro-F1 de validación frente al tamaño del subconjunto para baseline, mRMR y QFS-NA.")
    save(fig, "ev6_rendimiento_vs_k")


# ---------------------------------------------------------------- f10_b5 densidad vs beta
def fig_densidad_beta():
    # Mas grande y legible (2x3): la version 1x5 quedaba diminuta.
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.6))
    fig.subplots_adjust(top=0.86, bottom=0.09, left=0.07, right=0.97, wspace=0.26, hspace=0.34)
    axes = axes.ravel()
    for ax, ds in zip(axes, DS):
        rows = []
        for f in sorted(glob.glob(str(T8 / f"qfs_runs_{ds}_*.csv"))):
            d = pd.read_csv(f); beta = d.beta.iloc[0]
            dens = d[[c for c in d.columns if c.startswith("density__")]].iloc[0].to_numpy(float)
            k = K_BY[ds]; top = np.sort(dens)[::-1][:k].mean(); rest = np.sort(dens)[::-1][k:].mean() if len(dens) > k else 0
            rows.append((beta, top, rest))
        r = pd.DataFrame(rows, columns=["beta", "top", "rest"]).sort_values("beta")
        ax.plot(r.beta, r.top, marker="o", ms=6, lw=2.2, color=DCOL[ds], label="seleccionadas (top-k)")
        ax.plot(r.beta, r.rest, marker="o", ms=5, lw=1.8, color="#b7b0a6", label="resto")
        ax.fill_between(r.beta, r.rest, r.top, color=DCOL[ds], alpha=0.10)
        ax.set_title(DLAB[ds], fontsize=11); ax.set_xlabel(r"$\beta$")
        ax.set_ylabel("densidad Rydberg media")
    axes[5].axis("off")
    axes[0].legend(fontsize=9, loc="best")
    title(fig, r"$\beta$ reordena las densidades de Rydberg, pero no explica el deterioro",
          r"Densidad media de las variables seleccionadas (top-k) frente al resto, al variar $\beta$, por dataset. La banda mide la separación entre ambas.")
    save(fig, "f10_b5_beta_geometria")


# ---------------------------------------------------------------- f10_b10 consistencia
def fig_consistencia():
    # Dos paneles: Jaccard (sin corregir) vs Kuncheva (corregido por azar).
    # El segundo revela que mRMR e informacion mutua son menos estables de lo
    # que el Jaccard sugiere -> cierra la grieta viz<->texto.
    from matplotlib.colors import LinearSegmentedColormap

    def matriz(path, col, methods):
        d = pd.read_csv(path)
        g = d.groupby(["dataset", "method"])[col].mean().reset_index()
        M = np.full((len(DS), len(methods)), np.nan)
        for i, ds in enumerate(DS):
            sub = g[g.dataset == ds].set_index("method")
            for j, m in enumerate(methods):
                if m in sub.index:
                    M[i, j] = sub.loc[m, col]
        return M

    methods = sorted(pd.read_csv(T5 / "fs_jaccard_stability.csv").method.unique())
    Mj = matriz(T5 / "fs_jaccard_stability.csv", "jaccard", methods)
    Mk = matriz(T5 / "fs_kuncheva_stability.csv", "kuncheva", methods)
    cmap = LinearSegmentedColormap.from_list("stab", ["#d95f5f", "#efe4cf", "#4f81bd"])
    cmap.set_bad("#e9e9e9")

    fig, axes = plt.subplots(2, 1, figsize=(12.8, 8.6))
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.13, right=0.91, hspace=0.58)
    for ax, M, lab in [(axes[0], Mj, "A. Jaccard (sin corregir)"),
                       (axes[1], Mk, "B. Kuncheva (corregido por azar)")]:
        im = ax.imshow(np.ma.masked_invalid(M), cmap=cmap, vmin=0.4, vmax=1.0, aspect="auto")
        for i in range(len(DS)):
            for j in range(len(methods)):
                if not np.isnan(M[i, j]):
                    ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=7.3,
                            color="white" if (M[i, j] < 0.58 or M[i, j] > 0.9) else "#333333")
        ax.set_xticks(range(len(methods)), [m.replace("_", " ") for m in methods], rotation=45, ha="right", fontsize=7.8)
        ax.set_yticks(range(len(DS)), [DLAB[d] for d in DS])
        ax.set_title(lab, fontsize=10.5, loc="left", fontweight="bold")
        ax.grid(False)
    cb = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.018)
    cb.set_label("estabilidad entre semillas\n(1 = idéntica; frío = inestable)")
    title(fig, "El Jaccard sobreestima la estabilidad de mRMR e información mutua",
          "A: solape Jaccard sin corregir. B: índice de Kuncheva, que descuenta el solape esperable por azar. Esos dos criterios se enfrían en B (su coincidencia entre semillas es en parte azar, sobre todo en conjuntos pequeños); los filtros deterministas (gris en B) tienen solape trivial.")
    save(fig, "f10_b10_consistencia")


# ---------------------------------------------------------------- a8 solape qfs vs mrmr/boruta
def fig_solape_a8():
    fig, ax = plt.subplots(figsize=(8.5, 4.0))
    fig.subplots_adjust(top=0.78, bottom=0.14, left=0.12, right=0.97)
    x = np.arange(len(DS)); w = 0.35
    jm = [J(qfs_feats(d), classic_feats(d, "mrmr_approx", K_BY[d])) for d in DS]
    jb = [J(qfs_feats(d), classic_feats(d, "boruta", K_BY[d]) or classic_feats(d, "boruta", K_BY[d])) for d in DS]
    ax.bar(x - w/2, jm, w, color="#4f81bd", label="mRMR")
    ax.bar(x + w/2, jb, w, color="#d7a6a1", label="Boruta")
    ax.set_xticks(x); ax.set_xticklabels([DLAB[d] for d in DS], fontsize=8)
    ax.set_ylabel("Jaccard con QFS-NA"); ax.set_ylim(0, 1.05); ax.legend(fontsize=9)
    title(fig, "Solape de QFS-NA con las referencias clásicas mRMR y Boruta",
          "Jaccard entre el subconjunto QFS-NA y los de mRMR y Boruta, al presupuesto de referencia.")
    save(fig, "a8_solape_qfs_clasicos")


# ---------------------------------------------------------------- a9 macro-f1 vs auc binarios
def fig_auc_a9():
    auc = pd.read_csv(T8 / "qfs_auc_binarios_contexto.csv")
    cmp = pd.read_csv(T8 / "comparacion_qfs_configuraciones_vs_baseline.csv")
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    fig.subplots_adjust(top=0.80, bottom=0.12, left=0.12, right=0.97)
    BIN = ["breast_cancer_wisconsin", "customer_churn"]
    marks = {"baseline": ("o", "#9e9e9e"), "qfs_na": ("D", "#d95f5f"), "qfs_oracle_mucke": ("s", "#d9b382")}
    for ds in BIN:
        for fuente, (mk, col) in marks.items():
            a = auc[(auc.dataset == ds) & (auc.fuente.str.contains(fuente.replace("_mucke", "")))]
            if not len(a):
                continue
            aucv = a.auc_roc.max()
            cfg = "qfs_na" if fuente == "qfs_na" else ("qfs_oracle_mucke" if "oracle" in fuente else None)
            if cfg:
                f1 = cmp[(cmp.dataset == ds) & (cmp.configuration == cfg)].qfs_test_macro_f1.iloc[0]
            else:
                f1 = cmp[(cmp.dataset == ds) & (cmp.configuration == "qfs_na")].baseline_test_macro_f1.iloc[0]
            ax.scatter(f1, aucv, marker=mk, s=120, color=col, edgecolor="white", linewidth=1, zorder=3)
            ax.annotate(DLAB[ds].split()[0], (f1, aucv), fontsize=7, xytext=(4, 4), textcoords="offset points")
    from matplotlib.lines import Line2D
    h = [Line2D([0], [0], marker=m, color="w", markerfacecolor=c, markersize=10, label=l)
         for l, (m, c) in zip(["baseline", "QFS-NA", "QFS-oráculo"], marks.values())]
    ax.legend(handles=h, fontsize=9, loc="lower right")
    ax.set_xlabel("macro-F1 test"); ax.set_ylabel("AUC-ROC")
    title(fig, "Macro-F1 frente a AUC-ROC en los problemas binarios",
          "Coherencia entre macro-F1 y AUC para baseline, QFS-NA y QFS-oráculo en Breast Cancer y Customer Churn.")
    save(fig, "a9_macro_f1_auc_binarios")


# ---------------------------------------------------------------- f10_b4 escalera alpha
def fig_escalera_alpha():
    # Generador reescrito (el original se perdio): escalera de alpha del optimo
    # exacto, con el punto de operacion (estrella) como conclusion visual.
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0))
    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.07, right=0.97, wspace=0.22)
    for ds in DS:
        oracle = pd.read_csv(T8 / f"qfs_oracle_{ds}.csv")
        grid = oracle[oracle["mode"] == "alpha_grid"].sort_values("alpha")
        axes[0].plot(grid.alpha, grid.cardinality, marker="o", ms=3, lw=1.8, color=DCOL[ds], label=DLAB[ds])
        axes[1].plot(grid.alpha, grid.q_opt, marker="o", ms=3, lw=1.8, color=DCOL[ds])
        op = oracle[oracle["mode"] != "alpha_grid"]
        if not op.empty:
            o = op.iloc[0]
            # Punto de operacion: circulo grande con borde oscuro (sin estrellas).
            axes[0].scatter(o.alpha, o.cardinality, s=150, color=DCOL[ds], edgecolor="#222", linewidth=2.0, zorder=6)
            axes[1].scatter(o.alpha, o.q_opt, s=150, color=DCOL[ds], edgecolor="#222", linewidth=2.0, zorder=6)
    axes[0].set_xlabel(r"$\alpha$"); axes[0].set_ylabel("nº de variables del óptimo")
    axes[0].set_title("A. α fija el tamaño del subconjunto", loc="left")
    axes[1].set_xlabel(r"$\alpha$"); axes[1].set_ylabel("coste óptimo Q*")
    axes[1].set_title("B. coste del óptimo exacto", loc="left")
    axes[0].legend(fontsize=8, loc="upper left")
    title(fig, "La escalera de α: subir el presupuesto añade variables a coste decreciente",
          "Cardinalidad y coste del óptimo exacto del QUBO al recorrer α; el punto con borde marca el α de operación de cada dataset.")
    save(fig, "f10_b4_escalera_alpha")


if __name__ == "__main__":
    for fn in [fig_atomos, fig_escalera_alpha, fig_densidad_beta, fig_consistencia]:
        try:
            fn()
        except Exception as e:
            print("FALLO", fn.__name__, "->", repr(e))
    print("listo")
