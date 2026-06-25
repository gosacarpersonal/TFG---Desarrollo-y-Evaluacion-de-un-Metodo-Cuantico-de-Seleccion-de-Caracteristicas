from __future__ import annotations

import shutil
import sys
import textwrap
import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import NullFormatter, ScalarFormatter
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.viz_core.config import WarmthConfig
from src.viz_core.editorial_warmth import apply_editorial_axes, save_editorial_figure, set_editorial_rcparams

TABLES = ROOT / "results" / "tables"
OUT = ROOT / "results" / "figures" / "10_memoria"
FIGS = ROOT / "Plantilla_Latex_GCD" / "tfgs" / "figs"

W = WarmthConfig()
BG = W.figure_facecolor
TEXT = W.text_color
MUTED = "#6f6a60"
GRID = W.grid_color
NEUTRAL = W.neutral_color
ACCENT = W.accent_color
SECONDARY = W.secondary_accent
# Paleta de dataset UNIFICADA con superfiguras_memoria.py y fase8 (mismo dataset,
# mismo color en toda la memoria; antes build_memoria usaba tonos distintos).
DATASET_COLORS = {
    "breast_cancer_wisconsin": "#4f81bd",
    "customer_churn": "#d9b382",
    "madelon": "#d95f5f",
    "olive_oil_3class": "#8fb7a8",
    "olive_oil_9class": "#7aa6c2",
}
METHOD_FAMILIES = {
    "variance": "relevancia",
    "f_classif": "relevancia",
    "mutual_info": "relevancia",
    "mutual_correlation": "redundancia",
    "feature_similarity": "redundancia",
    "mrmr_approx": "redundancia",
    "rrfs": "combinado",
    "linear_svm": "embedded",
    "l1_logistic": "embedded",
    "random_forest": "embedded",
    "rfe": "wrapper",
    "boruta": "wrapper",
}
FAMILY_COLORS = {
    "relevancia": "#a9bfd6",
    "redundancia": "#d9b382",
    "combinado": "#c7d59f",
    "wrapper": "#d7a6a1",
    "embedded": "#8fb7a8",
}
LABELS = {
    "breast_cancer_wisconsin": "Breast Cancer",
    "customer_churn": "Customer Churn",
    "madelon": "Madelon",
    "olive_oil_3class": "Olive 3",
    "olive_oil_9class": "Olive 9",
}

FIGURE_FILES = {
    "F1": "f1_banco",
    "F2": "f2_senal_fdr_efecto",
    "F3": "f3_base_confiable",
    "F4": "f4_perfil_selectores",
    "F5": "f5_coste_rendimiento",
    "F6": "f6_shap_variables",
    "F7": "f7_significancia_magnitud",
    "F8": "f8_qfs_alpha_beta",
    "F9": "f9_criterio_vs_optimizador",
    "F10": "f10_qfs_vs_clasico",
    "EV6": "ev6_rendimiento_vs_k",
    "A1": "a1_permutacion_senal_nulo",
    "A2": "a2_leakage",
    "A3": "a3_roster_completo",
    "A4": "a4_shap_concordancia",
    "A5": "a5_panorama_deltas",
    "A6": "a6_handoff_ir",
    "A7": "a7_coste_cuantico",
    "A8": "a8_solape_qfs_clasicos",
    "A9": "a9_macro_f1_auc_binarios",
    "EV5": "ev5_evolucion_adiabatica",
}

SOURCES = {
    "F1": [
        "results/tables/04_split_audit/fase4_resumen_xy.csv",
        "results/tables/04_split_audit/fase4_target_distribucion.csv",
    ],
    "F2": ["results/tables/01_raw_eda/fase1_asociacion_target_resumen.csv"],
    "F3": [
        "results/tables/04_split_audit/fase4_validacion_adversarial.csv",
        "results/tables/04_split_audit/fase4_drift_resumen.csv",
        "results/tables/03_postprocessing_audit/fase3_asociacion_tests.csv",
    ],
    "F4": [
        "results/tables/05_feature_selection/fs_method_profiles.csv",
        "results/tables/05_feature_selection/fs_redundancy_vs_full.csv",
        "results/tables/05_feature_selection/fs_permutation_summary.csv",
        "results/tables/05_feature_selection/fs_all_rankings.csv",
    ],
    "F5": ["results/tables/05_feature_selection/fs_redundancy_vs_full.csv"],
    "F6": [
        "results/tables/06_modeling/modeling_shap_values_summary.csv",
        "results/tables/07_final_comparison/fase7_tabla_maestra.csv",
    ],
    "F7": ["results/tables/07_final_comparison/fase7_tabla_maestra.csv"],
    "F8": [
        "results/tables/08_quantum/qfs_oracle_*.csv",
        "results/tables/08_quantum/qfs_runs_madelon_*.csv",
        "results/tables/08_quantum/qfs_validation_results.csv",
    ],
    "F9": ["results/tables/08_quantum/qfs_quality_control_*.csv", "results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv"],
    "F10": ["results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv", "results/tables/07_final_comparison/fase7_handoff_qfs.csv"],
    "EV6": ["results/tables/08_quantum/ev6_rendimiento_vs_k.csv"],
    "A1": ["results/tables/05_feature_selection/fs_permutation_summary.csv"],
    "A2": ["results/tables/04_split_audit/fase4_leakage_screening.csv"],
    "A3": ["results/tables/05_feature_selection/fs_all_selected_features.csv"],
    "A4": ["results/tables/06_modeling/modeling_shap_values_summary.csv", "results/tables/06_modeling/modeling_shap_values_full_olive_oil_*.csv"],
    "A5": ["results/tables/07_final_comparison/fase7_tabla_maestra.csv"],
    "A6": ["results/tables/05_feature_selection/fs_qfs_handoff_matrices_index.csv"],
    "A7": ["results/tables/08_quantum/qfs_runs_*.csv"],
    "A8": ["results/tables/08_quantum/qfs_selected_all.csv", "results/tables/05_feature_selection/fs_selected_feature_sets.csv"],
    "A9": ["results/tables/08_quantum/qfs_auc_binarios_contexto.csv", "results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv"],
    "EV5": ["QFS_based_on_NA/QFS_Auxiliar_functions.py"],
}


def read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(ROOT / path)


def display_dataset(name: str) -> str:
    return LABELS.get(name, name.replace("_", " ").title())


def method_label(name: str) -> str:
    return name.replace("_", " ")


def wrap_label(label: str, width: int = 18) -> str:
    return "\n".join(textwrap.wrap(str(label), width=width, break_long_words=False))


def finish(fig: plt.Figure, key: str) -> None:
    # Salida limpia: solo el PNG final en figs/ (sin duplicar en 10_memoria).
    FIGS.mkdir(parents=True, exist_ok=True)
    stem = FIGURE_FILES[key]
    save_editorial_figure(fig, FIGS / f"{stem}.png", dpi=300)
    plt.close(fig)


def add_header(fig: plt.Figure, title: str, subtitle: str, y: float = 0.985) -> None:
    fig.text(0.02, y, title, ha="left", va="top", fontsize=15, fontweight="semibold", color=TEXT)
    fig.text(0.02, y - 0.035, subtitle, ha="left", va="top", fontsize=10, color=MUTED)


def panel_label(ax, label: str, title: str) -> None:
    ax.set_title(f"{label}. {title}", loc="left", fontsize=10.5, fontweight="semibold", pad=8, color=TEXT)


def style_all(axes, grid_axis="y") -> None:
    for ax in np.ravel(axes):
        apply_editorial_axes(ax, grid_axis=grid_axis)


def figure_f1() -> None:
    df = read_csv("results/tables/04_split_audit/fase4_resumen_xy.csv").copy()
    target = read_csv("results/tables/04_split_audit/fase4_target_distribucion.csv")
    ratios = (
        target.groupby(["dataset", "clase"], as_index=False)["n"].sum()
        .groupby("dataset")["n"]
        .agg(lambda s: s.max() / s.min())
        .rename("ratio_mayoritaria_minoritaria")
        .reset_index()
    )
    df = df.merge(ratios, on="dataset", how="left")
    df = df[df["dataset"].isin(DATASET_COLORS)]
    df["n_clases"] = df["target_clases"]
    fig = plt.figure(figsize=(11.2, 5.8), facecolor=BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.28, 1], left=0.08, right=0.96, top=0.78, bottom=0.18, wspace=0.36)
    ax = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    sizes = 180 + 360 * (df["ratio_mayoritaria_minoritaria"] / df["ratio_mayoritaria_minoritaria"].max())
    ax.scatter(df["filas"], df["features"], s=sizes, c=df["dataset"].map(DATASET_COLORS), edgecolor=TEXT, linewidth=0.6, alpha=0.88)
    label_offsets = {
        "olive_oil_3class": (8, -16),
        "olive_oil_9class": (8, 8),
        "customer_churn": (-78, 6),
        "madelon": (8, 6),
        "breast_cancer_wisconsin": (8, 6),
    }
    for _, r in df.iterrows():
        ax.annotate(
            display_dataset(r.dataset),
            (r.filas, r.features),
            xytext=label_offsets.get(r.dataset, (6, 5)),
            textcoords="offset points",
            fontsize=8.6,
            color=TEXT,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Filas (escala log)")
    ax.set_ylabel("Variables predictoras (escala log)")
    panel_label(ax, "A", "Escala y dimensionalidad")
    d = df.sort_values("ratio_mayoritaria_minoritaria")
    colors = [DATASET_COLORS[x] for x in d.dataset]
    ax2.barh([display_dataset(x) for x in d.dataset], d["ratio_mayoritaria_minoritaria"], color=colors, edgecolor="none")
    for i, r in enumerate(d.itertuples()):
        ax2.text(r.ratio_mayoritaria_minoritaria + 0.05, i, f"{r.n_clases:.0f} clases", va="center", fontsize=8.5, color=MUTED)
    ax2.set_xlabel("Ratio clase mayoritaria/minoritaria")
    panel_label(ax2, "B", "Desbalance y métrica")
    ax2.text(0.02, -0.22, "Lectura: el banco exige macro-F1 para no ocultar clases minoritarias.", transform=ax2.transAxes, fontsize=9.2, color=TEXT)
    style_all([ax, ax2])
    add_header(fig, "Un banco de pruebas que cubre tamaño, dimensión y desbalance", "Cinco formulaciones; el desbalance multiclase motiva el uso de macro-F1")
    finish(fig, "F1")


def figure_f2() -> None:
    df = read_csv("results/tables/01_raw_eda/fase1_asociacion_target_resumen.csv")
    df["frac"] = df.variables_fdr_005 / df.variables_contrastadas
    df = df.sort_values("frac")
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.6), facecolor=BG, gridspec_kw={"left": 0.1, "right": 0.97, "top": 0.78, "bottom": 0.19, "wspace": 0.34})
    y = np.arange(len(df))
    colors = [ACCENT if x == "madelon" else NEUTRAL for x in df.dataset]
    axes[0].hlines(y, 0, df.frac, color=colors, lw=2)
    axes[0].scatter(df.frac, y, s=72, color=colors, zorder=3)
    for i, r in enumerate(df.itertuples()):
        axes[0].text(r.frac + 0.03, i, f"{int(r.variables_fdr_005)}/{int(r.variables_contrastadas)}", va="center", fontsize=8.8)
    axes[0].set_yticks(y, [display_dataset(x) for x in df.dataset])
    axes[0].set_xlim(0, 1.12)
    axes[0].set_xlabel("Fracción de variables con FDR < 0.05")
    panel_label(axes[0], "A", "Señal tras multiplicidad")
    width = 0.34
    axes[1].barh(y - width / 2, df.efecto_abs_mediano, height=width, color=colors, alpha=0.85, label="Mediano")
    axes[1].barh(y + width / 2, df.efecto_abs_maximo, height=width, color=SECONDARY, alpha=0.65, label="Máximo")
    axes[1].set_yticks(y, [display_dataset(x) for x in df.dataset])
    axes[1].set_xlabel("Tamaño de efecto absoluto")
    axes[1].legend(loc="lower right", frameon=False)
    panel_label(axes[1], "B", "Magnitud de la asociación")
    style_all(axes)
    axes[1].annotate("Madelon: señal escasa y débil", xy=(df[df.dataset == "madelon"].efecto_abs_mediano.iloc[0], list(df.dataset).index("madelon")), xytext=(0.28, 0.7), textcoords="data", arrowprops={"arrowstyle": "->", "color": ACCENT}, fontsize=9, color=TEXT)
    add_header(fig, "La señal supervisada es real, pero en Madelon apenas es univariante", "Variables que superan FDR 0.05 y tamaño de efecto, por dataset")
    finish(fig, "F2")


def figure_f3() -> None:
    auc = read_csv("results/tables/04_split_audit/fase4_validacion_adversarial.csv")
    drift = read_csv("results/tables/04_split_audit/fase4_drift_resumen.csv")
    assoc = read_csv("results/tables/03_postprocessing_audit/fase3_asociacion_tests.csv")
    order = auc.dataset.tolist()
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5.3), facecolor=BG, gridspec_kw={"left": 0.07, "right": 0.98, "top": 0.76, "bottom": 0.2, "wspace": 0.36})
    y = np.arange(len(order))
    colors = [DATASET_COLORS[x] for x in order]
    axes[0].axvspan(0.45, 0.55, color=SECONDARY, alpha=0.18)
    axes[0].axvline(0.5, color=MUTED, ls="--", lw=1)
    axes[0].errorbar(auc.auc_cv, y, xerr=auc.auc_fold_std, fmt="o", color=TEXT, ecolor=NEUTRAL, capsize=3, ms=5)
    axes[0].scatter(auc.auc_cv, y, s=64, c=colors, zorder=3)
    axes[0].set_yticks(y, [display_dataset(x) for x in order])
    axes[0].set_xlabel("AUC adversarial (0.5 = intercambiable)")
    axes[0].set_xlim(0.35, 0.68)
    panel_label(axes[0], "A", "Particiones intercambiables")
    d = drift.set_index("dataset").loc[order].reset_index()
    axes[1].barh(y, d.max_drift_score, color=colors, alpha=0.78)
    axes[1].axvline(0.25, color=MUTED, ls="--", lw=1)
    for i, r in enumerate(d.itertuples()):
        axes[1].text(r.max_drift_score + 0.015, i, f"{int(r.variables_con_flag)} flags", va="center", fontsize=8.5)
    axes[1].set_yticks(y, [display_dataset(x) for x in order])
    axes[1].set_xlabel("Máximo score drift (PSI/KS/W)")
    panel_label(axes[1], "B", "Drift acotado")
    assoc_expanded = assoc.copy()
    olive = assoc_expanded[assoc_expanded["dataset"] == "olive_oil"]
    if not olive.empty:
        assoc_expanded = pd.concat(
            [
                assoc_expanded[assoc_expanded["dataset"] != "olive_oil"],
                olive.assign(dataset="olive_oil_3class"),
                olive.assign(dataset="olive_oil_9class"),
            ],
            ignore_index=True,
        )
    a = assoc_expanded.set_index("dataset").reindex(order).reset_index()
    axes[2].hlines(y, 0.95, a.spearman_rankings_raw_processed, color=colors, lw=2)
    axes[2].scatter(a.spearman_rankings_raw_processed, y, s=64, c=colors, zorder=3)
    axes[2].set_yticks(y, [display_dataset(x) for x in order])
    axes[2].set_xlim(0.94, 1.005)
    axes[2].set_xlabel("Spearman ranking MI raw -> processed")
    panel_label(axes[2], "C", "Preprocesado fiel")
    style_all(axes)
    add_header(fig, "Particiones intercambiables, drift acotado y preprocesado fiel", "AUC adversarial ≈ 0.5, drift bajo umbral y rankings de MI conservados")
    finish(fig, "F3")


def figure_f4() -> None:
    prof = read_csv("results/tables/05_feature_selection/fs_method_profiles.csv").copy()
    red = read_csv("results/tables/05_feature_selection/fs_redundancy_vs_full.csv")
    perm = read_csv("results/tables/05_feature_selection/fs_permutation_summary.csv")
    prof["family"] = prof.method.map(METHOD_FAMILIES)
    redm = red.groupby("method", as_index=False)["delta_mean_abs_corr"].mean()
    prof = prof.merge(redm, on="method", how="left")
    order = prof.sort_values("delta_mean_abs_corr").method.tolist()
    y = np.arange(len(order))
    fig = plt.figure(figsize=(13.3, 8.3), facecolor=BG)
    gs = fig.add_gridspec(2, 2, left=0.12, right=0.97, top=0.82, bottom=0.13, wspace=0.35, hspace=0.48)
    axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
    p = prof.set_index("method").loc[order].reset_index()
    colors = [FAMILY_COLORS[x] for x in p.family]
    axes[0].axvline(0, color=MUTED, lw=1)
    axes[0].hlines(y, 0, p.delta_mean_abs_corr, color=colors, lw=2)
    axes[0].scatter(p.delta_mean_abs_corr, y, s=48, c=colors, zorder=3)
    axes[0].set_yticks(y, [method_label(x) for x in order])
    axes[0].set_xlabel("Delta correlación absoluta media")
    panel_label(axes[0], "A", "Redundancia interna")
    axes[1].barh(y, p.segundos_medios, color=colors)
    axes[1].set_xscale("log")
    axes[1].set_yticks(y, [method_label(x) for x in order])
    axes[1].set_xlabel("Segundos medios por ejecución (log)")
    panel_label(axes[1], "B", "Coste de ajuste")
    j = p.jaccard_medio.fillna(1.0)
    axes[2].hlines(y, 0, j, color=colors, lw=2)
    axes[2].scatter(j, y, s=48, c=colors, zorder=3)
    axes[2].set_xlim(0.68, 1.03)
    axes[2].set_yticks(y, [method_label(x) for x in order])
    axes[2].set_xlabel("Jaccard medio entre semillas")
    panel_label(axes[2], "C", "Estabilidad")
    pivot = perm.pivot_table(index="method", columns="dataset", values="n_features_above_null", aggfunc="mean")
    im = axes[3].imshow(pivot.fillna(0), aspect="auto", cmap=LinearSegmentedColormap.from_list("warm_seq", [BG, "#d9b382", ACCENT]), vmin=0)
    axes[3].set_yticks(range(len(pivot.index)), [method_label(x) for x in pivot.index])
    axes[3].set_xticks(range(len(pivot.columns)), [display_dataset(x) for x in pivot.columns], rotation=35, ha="right")
    panel_label(axes[3], "D", "Variables sobre nulo p95")
    for i in range(pivot.shape[0]):
        for jcol in range(pivot.shape[1]):
            val = pivot.iloc[i, jcol]
            if pd.notna(val):
                axes[3].text(jcol, i, f"{val:.0f}", ha="center", va="center", fontsize=7.5, color=TEXT)
    axes[3].set_xlabel("Contraste disponible para filtros de relevancia")
    cbar = fig.colorbar(im, ax=axes[3], fraction=0.046, pad=0.02)
    cbar.ax.tick_params(labelsize=8, colors=MUTED)
    style_all(axes[:3])
    apply_editorial_axes(axes[3], show_grid=False)
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=c, label=f, markersize=7) for f, c in FAMILY_COLORS.items()]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.97, 0.91), ncol=5, frameon=False, title="Familia")
    add_header(fig, "mRMR controla la redundancia con coste moderado; los wrappers la pagan en tiempo", "Perfil de los doce selectores: redundancia, coste, estabilidad y separación del azar", y=0.965)
    finish(fig, "F4")


def figure_f5() -> None:
    traj = read_csv("results/tables/05_feature_selection/fs_redundancy_vs_full.csv")
    datasets = list(DATASET_COLORS)
    fig, axes = plt.subplots(2, 3, figsize=(13.2, 7.2), facecolor=BG, gridspec_kw={"left": 0.07, "right": 0.97, "top": 0.82, "bottom": 0.12, "wspace": 0.3, "hspace": 0.42})
    axes = axes.ravel()
    BORUTA = "#5a8f7b"  # verde: el wrapper de referencia que se quiere batir
    for ax, ds in zip(axes, datasets):
        d = traj[traj.dataset == ds]
        for selector, s in d.groupby("method"):
            s = s.sort_values("k")
            if selector == "mrmr_approx":
                ax.plot(s.k, s.delta_mean_abs_corr, color=ACCENT, lw=2.4, marker="o", ms=4, zorder=4, label="mRMR")
            elif selector == "boruta":
                # Boruta se resalta como trayectoria, no como cuadrado aislado.
                ax.plot(s.k, s.delta_mean_abs_corr, color=BORUTA, lw=2.4, marker="o", ms=4,
                        zorder=5, label="Boruta")
            else:
                ax.plot(s.k, s.delta_mean_abs_corr, color=NEUTRAL, lw=1.0, alpha=0.32, zorder=1)
        ax.axhline(0, color=SECONDARY, ls="--", lw=1.1, label="Redundancia del espacio completo")
        ks = sorted(d.k.dropna().unique())
        if len(ks) > 6:
            ks = ks[:: max(1, len(ks) // 6)]
        ax.set_xticks(ks)
        ax.set_title(display_dataset(ds), loc="left", fontsize=10.5, fontweight="semibold")
        ax.set_xlabel("Tamaño del subconjunto k")
        ax.set_ylabel("Delta correlación media")
        apply_editorial_axes(ax)
    axes[-1].axis("off")
    handles = [
        Line2D([0], [0], color=ACCENT, lw=2.4, marker="o", label="mRMR (protagonista)"),
        Line2D([0], [0], color=BORUTA, lw=2.4, marker="o", label="Boruta (referencia a batir)"),
        Line2D([0], [0], color=NEUTRAL, lw=1.2, alpha=0.55, label="Otros selectores"),
        Line2D([0], [0], color=SECONDARY, lw=1.1, ls="--", label="Espacio completo"),
    ]
    fig.legend(handles=handles, frameon=False, ncol=4, loc="upper right", bbox_to_anchor=(0.985, 0.91))
    add_header(fig, "La selección madura al crecer k; mRMR evita concentrar redundancia", "Delta de correlación interna frente a k; en gris el contexto clásico, mRMR y Boruta (la referencia a batir) destacados")
    finish(fig, "F5")


def shap_panel(ax, dataset: str, feature_set: str, model: str, top_n: int = 8) -> None:
    summary = read_csv("results/tables/06_modeling/modeling_shap_values_summary.csv")
    rows = summary[(summary.dataset == dataset) & (summary.feature_set == feature_set) & (summary.model_name == model)].sort_values("rank").head(top_n)
    raw = pd.read_csv(ROOT / rows.raw_values_path.iloc[0])
    vals = pd.read_csv(ROOT / rows.feature_values_path.iloc[0])
    features = rows.feature.tolist()[::-1]
    rng = np.random.default_rng(2)
    for i, feat in enumerate(features):
        x = raw[feat].to_numpy()
        v = vals[feat].to_numpy()
        norm = (v - np.nanmin(v)) / (np.nanmax(v) - np.nanmin(v) + 1e-12)
        y = i + rng.normal(0, 0.07, size=len(x))
        ax.scatter(x, y, c=norm, cmap=LinearSegmentedColormap.from_list("shap", [SECONDARY, ACCENT]), s=13, alpha=0.72, linewidth=0)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_yticks(range(len(features)), [wrap_label(f, 18) for f in features])
    ax.set_xlabel("Valor SHAP")
    ax.set_title(display_dataset(dataset), loc="left", fontsize=10.5, fontweight="semibold")
    apply_editorial_axes(ax, grid_axis="x")


def shap_importance_panel(ax, dataset: str, feature_set: str, model: str, top_n: int = 6) -> None:
    summary = read_csv("results/tables/06_modeling/modeling_shap_values_summary.csv")
    rows = (
        summary[(summary.dataset == dataset) & (summary.feature_set == feature_set) & (summary.model_name == model)]
        .sort_values("rank")
        .head(top_n)
        .iloc[::-1]
    )
    color = DATASET_COLORS.get(dataset, ACCENT)
    ax.barh(range(len(rows)), rows.mean_abs_shap, color=color, alpha=0.86)
    ax.set_yticks(range(len(rows)), [wrap_label(f, 16) for f in rows.feature])
    ax.set_xlabel("|SHAP| medio")
    ax.set_title(display_dataset(dataset), loc="left", fontsize=10.2, fontweight="semibold")
    apply_editorial_axes(ax)


def figure_f6() -> None:
    best = read_csv("results/tables/07_final_comparison/fase7_tabla_maestra.csv")
    best = best.sort_values("validation_macro_f1").groupby("dataset").tail(1).set_index("dataset")
    fig, axes = plt.subplots(2, 3, figsize=(13.4, 7.4), facecolor=BG, gridspec_kw={"left": 0.12, "right": 0.97, "top": 0.82, "bottom": 0.12, "wspace": 0.45, "hspace": 0.48})
    axes = axes.ravel()
    binarios = {"breast_cancer_wisconsin", "customer_churn", "madelon"}
    for ax, ds in zip(axes, DATASET_COLORS):
        row = best.loc[ds]
        if ds in binarios:
            shap_panel(ax, ds, row.feature_set, row.model_name)
        else:
            shap_importance_panel(ax, ds, row.feature_set, row.model_name)
    axes[-1].axis("off")
    add_header(fig, "Las variables que sostienen cada modelo coinciden con la selección", "Beeswarm SHAP por instancia en los binarios; |SHAP| medio en Olive multiclase (beeswarm por clase en apéndice)")
    finish(fig, "F6")


def figure_f7() -> None:
    df = read_csv("results/tables/07_final_comparison/fase7_tabla_maestra.csv")
    bases = df[df.candidate_label == "baseline_mejor_en_validation"].set_index("dataset")
    best = df[df.candidate_label != "baseline_mejor_en_validation"].sort_values("validation_macro_f1").groupby("dataset").tail(1).set_index("dataset")
    order = list(DATASET_COLORS)
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.8), facecolor=BG, gridspec_kw={"left": 0.1, "right": 0.97, "top": 0.78, "bottom": 0.18, "wspace": 0.34})
    y = np.arange(len(order))
    axes[0].errorbar(bases.loc[order].test_macro_f1, y - 0.13, xerr=[bases.loc[order].test_macro_f1 - bases.loc[order].test_macro_f1_ci_low, bases.loc[order].test_macro_f1_ci_high - bases.loc[order].test_macro_f1], fmt="o", color=NEUTRAL, ecolor=NEUTRAL, capsize=3, label="Baseline")
    axes[0].errorbar(best.loc[order].test_macro_f1, y + 0.13, xerr=[best.loc[order].test_macro_f1 - best.loc[order].test_macro_f1_ci_low, best.loc[order].test_macro_f1_ci_high - best.loc[order].test_macro_f1], fmt="o", color=SECONDARY, ecolor=SECONDARY, capsize=3, label="Selección")
    axes[0].set_yticks(y, [display_dataset(x) for x in order])
    axes[0].set_xlabel("Macro-F1 test con IC 95%")
    if axes[0].get_legend():
        axes[0].get_legend().remove()
    panel_label(axes[0], "A", "Resultado en test")
    delta = best.loc[order]
    colors = [ACCENT if x == "madelon" else NEUTRAL for x in order]
    axes[1].axvline(0, color=MUTED, lw=1)
    axes[1].axvline(0.01, color=ACCENT, ls="--", lw=1)
    axes[1].errorbar(delta.difference_candidate_minus_baseline, y, xerr=[delta.difference_candidate_minus_baseline - delta.ci_low, delta.ci_high - delta.difference_candidate_minus_baseline], fmt="none", ecolor=NEUTRAL, capsize=3)
    axes[1].scatter(delta.difference_candidate_minus_baseline, y, s=58, c=colors, zorder=3)
    axes[1].set_yticks(y, [display_dataset(x) for x in order])
    axes[1].set_xlabel("Delta selección - baseline")
    panel_label(axes[1], "B", "Magnitud práctica")
    style_all(axes)
    add_header(fig, "La selección iguala al baseline; solo Madelon mejora de forma relevante", "Macro-F1 en test e IC bootstrap 95%; gris = baseline, azul = selección; umbral práctico 0.01")
    finish(fig, "F7")


def figure_f8() -> None:
    oracle = []
    for p in (TABLES / "08_quantum").glob("qfs_oracle_*.csv"):
        oracle.append(pd.read_csv(p))
    oracle = pd.concat(oracle, ignore_index=True)
    alpha = oracle[oracle["mode"] == "alpha_grid"].copy()
    runs = []
    for p in sorted((TABLES / "08_quantum").glob("qfs_runs_madelon_*.csv")):
        d = pd.read_csv(p)
        runs.append(d.iloc[[0]])
    runs = pd.concat(runs, ignore_index=True)
    density_cols = [c for c in runs.columns if c.startswith("density__")]
    mat = runs.sort_values("beta")[density_cols].to_numpy().T
    valid = read_csv("results/tables/08_quantum/qfs_validation_results.csv")
    fig = plt.figure(figsize=(13.2, 8.0), facecolor=BG)
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.25], left=0.08, right=0.98, top=0.82, bottom=0.12, wspace=0.3, hspace=0.45)
    ax = fig.add_subplot(gs[0, 0])
    axq = fig.add_subplot(gs[1, 0])
    axv = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, 1])
    for ds, d in alpha.groupby("dataset"):
        ax.step(d.alpha, d.cardinality, where="post", color=DATASET_COLORS.get(ds, NEUTRAL), lw=2, label=display_dataset(ds))
    ax.set_xlabel("alpha del QUBO exacto")
    ax.set_ylabel("Cardinalidad del óptimo")
    panel_label(ax, "A", "alpha recorre presupuestos")
    for ds, d in alpha.groupby("dataset"):
        axq.plot(d.alpha, d.q_opt, color=DATASET_COLORS.get(ds, NEUTRAL), lw=1.8)
    axq.axhline(0, color=MUTED, lw=0.8)
    axq.set_xlabel("alpha del QUBO exacto")
    axq.set_ylabel("Coste óptimo Q*")
    panel_label(axq, "B", "coste del oráculo")
    for ds, d in valid.groupby("dataset"):
        d = d.sort_values("beta")
        is_focus = ds in ("madelon", "customer_churn")
        axv.plot(
            d.beta,
            d.validation_macro_f1,
            color=DATASET_COLORS.get(ds, NEUTRAL) if is_focus else NEUTRAL,
            lw=2.3 if is_focus else 1.0,
            alpha=0.95 if is_focus else 0.35,
            marker="o" if is_focus else None,
            ms=3.5,
            label=display_dataset(ds) if is_focus else None,
        )
    axv.set_xlabel("beta")
    axv.set_ylabel("Macro-F1 validación QFS-NA")
    axv.legend(frameon=False, loc="lower right", fontsize=8)
    panel_label(axv, "C", "beta sí mueve rendimiento")
    im = ax2.imshow(mat, aspect="auto", cmap=LinearSegmentedColormap.from_list("qfs", [BG, "#d9b382", ACCENT]))
    ax2.set_xticks(range(len(runs)), [f"{b:.1f}" for b in runs.sort_values("beta").beta], rotation=0)
    ax2.set_yticks(range(len(density_cols)), [c.replace("density__", "") for c in density_cols], fontsize=7)
    ax2.set_xlabel("beta")
    panel_label(ax2, "D", "beta reordena Madelon")
    fig.colorbar(im, ax=ax2, fraction=0.035, pad=0.02, label="Densidad")
    style_all([ax, axq, axv])
    apply_editorial_axes(ax2, show_grid=False)
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    add_header(fig, "alpha fija el tamaño; beta cambia la selección y el rendimiento", "Oráculo QUBO exacto para alpha; validación QFS-NA y densidad de Rydberg para beta")
    finish(fig, "F8")


def figure_f9() -> None:
    comp = read_csv("results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv")
    qualities = []
    for p in (TABLES / "08_quantum").glob("qfs_quality_control_*.csv"):
        d = pd.read_csv(p)
        qualities.append(d.loc[d["beta"].sub(0.5).abs().idxmin()])
    qc = pd.DataFrame(qualities)
    qfs = comp[comp.configuration == "qfs_na"][["dataset", "qfs_test_macro_f1", "baseline_test_macro_f1"]]
    oracle = comp[comp.configuration == "qfs_oracle_mucke"][["dataset", "qfs_test_macro_f1"]].rename(columns={"qfs_test_macro_f1": "oracle_macro_f1"})
    df = qc.merge(qfs, on="dataset").merge(oracle, on="dataset", how="left")
    df["criterio_deficit"] = df["baseline_test_macro_f1"] - df["oracle_macro_f1"]
    fig = plt.figure(figsize=(12.2, 5.8), facecolor=BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], left=0.09, right=0.97, top=0.78, bottom=0.18, wspace=0.34)
    ax = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax.axvline(0, color=MUTED, lw=1)
    ax.axhline(0.02, color=MUTED, lw=1, ls="--")
    offsets = {
        "madelon": (10, 10),
        "customer_churn": (10, 6),
        "breast_cancer_wisconsin": (10, 6),
        "olive_oil_3class": (10, 6),
        "olive_oil_9class": (10, 6),
    }
    for _, r in df.iterrows():
        ax.scatter(r.delta_cost_alpha05, r.criterio_deficit, s=92, color=DATASET_COLORS[r.dataset], edgecolor=TEXT, lw=0.6)
        ax.annotate(display_dataset(r.dataset), (r.delta_cost_alpha05, r.criterio_deficit), xytext=offsets.get(r.dataset, (6, 5)), textcoords="offset points", fontsize=8.8)
    ax.text(0.02, 0.80, "Falla criterio", transform=ax.transAxes, fontsize=9, color=ACCENT, fontweight="semibold")
    ax.text(0.62, 0.12, "Falla optimizador", transform=ax.transAxes, fontsize=9, color=ACCENT, fontweight="semibold")
    ax.set_xlabel("Delta coste QFS-NA - óptimo exacto")
    ax.set_ylabel("Déficit macro-F1 del óptimo exacto")
    ax.margins(x=0.08, y=0.18)
    panel_label(ax, "A", "Diagnóstico por cuadrantes")
    d = df.sort_values("delta_cost_alpha05")
    y = np.arange(len(d))
    ax2.axvline(0, color=MUTED, lw=1)
    ax2.hlines(y - 0.13, 0, d.delta_cost_alpha05, color=SECONDARY, lw=2, label="Delta coste")
    ax2.scatter(d.delta_cost_alpha05, y - 0.13, color=SECONDARY, s=48)
    ax2.hlines(y + 0.13, 0, d.hamming_distance / max(d.hamming_distance.max(), 1), color=NEUTRAL, lw=2, label="Hamming (normalizado)")
    ax2.scatter(d.hamming_distance / max(d.hamming_distance.max(), 1), y + 0.13, color=NEUTRAL, s=48)
    ax2.set_yticks(y, [display_dataset(x) for x in d.dataset])
    ax2.set_xlabel("Delta coste (azul) y Hamming normalizado (gris)")
    ax2.legend(frameon=False, loc="lower right")
    panel_label(ax2, "B", "Evidencia del coste")
    style_all([ax, ax2])
    add_header(fig, "Madelon agota el criterio; Customer Churn agota al optimizador", "Calidad de la optimización (Delta coste) frente a calidad del criterio (déficit del óptimo exacto)")
    finish(fig, "F9")


def figure_f10() -> None:
    q = read_csv("results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv")
    hand = read_csv("results/tables/07_final_comparison/fase7_handoff_qfs.csv").set_index("dataset")
    order = list(DATASET_COLORS)
    fig, ax = plt.subplots(figsize=(12.4, 6), facecolor=BG)
    y = np.arange(len(order))
    offsets = [-0.24, -0.08, 0.08, 0.24]
    series = [
        ("Baseline", [hand.loc[d, "baseline_test_macro_f1"] for d in order], NEUTRAL, None),
        ("Mejor clásico", [hand.loc[d, "seleccion_test_macro_f1"] for d in order], SECONDARY, None),
        ("QFS-NA", [q[(q.dataset == d) & (q.configuration == "qfs_na")].qfs_test_macro_f1.iloc[0] for d in order], ACCENT, "qfs_na"),
        ("QFS-oráculo", [q[(q.dataset == d) & (q.configuration == "qfs_oracle_mucke")].qfs_test_macro_f1.iloc[0] for d in order], "#d9b382", "qfs_oracle_mucke"),
    ]
    for off, (name, vals, color, cfg) in zip(offsets, series):
        if cfg:
            lows, highs = [], []
            for ds, val in zip(order, vals):
                row = q[(q.dataset == ds) & (q.configuration == cfg)].iloc[0]
                base = row.baseline_test_macro_f1
                lo = base + row.delta_ci_low
                hi = base + row.delta_ci_high
                lows.append(max(0, val - lo))
                highs.append(max(0, hi - val))
            ax.errorbar(vals, y + off, xerr=[lows, highs], fmt="none", ecolor=color, alpha=0.45, capsize=2, lw=1)
        ax.scatter(vals, y + off, s=62, color=color, label=name, edgecolor=TEXT, lw=0.4, zorder=3)
    ax.set_yticks(y, [display_dataset(x) for x in order])
    ax.set_xlabel("Macro-F1 test")
    ax.set_xlim(0.55, 1.02)
    ax.legend(frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.22))
    apply_editorial_axes(ax)
    add_header(fig, "El método cuántico iguala con señal clara y se deteriora donde falla criterio u optimizador", "Macro-F1 en test por dataset; barras = IC bootstrap del delta frente a baseline")
    finish(fig, "F10")


def figure_ev6() -> None:
    df = read_csv("results/tables/08_quantum/ev6_rendimiento_vs_k.csv")
    labels = {
        "baseline_rf": "Baseline RF",
        "mrmr_approx": "mRMR",
        "qfs_na_top_density": "QFS-NA",
    }
    colors = {
        "baseline_rf": NEUTRAL,
        "mrmr_approx": SECONDARY,
        "qfs_na_top_density": ACCENT,
    }
    linestyles = {"baseline_rf": "--", "mrmr_approx": "-", "qfs_na_top_density": "-"}
    fig = plt.figure(figsize=(14.2, 8.4), facecolor=BG)
    gs = fig.add_gridspec(2, 3, left=0.06, right=0.98, bottom=0.10, top=0.80, wspace=0.34, hspace=0.52)
    axes = [fig.add_subplot(gs[i // 3, i % 3]) for i in range(6)]
    for ax, ds in zip(axes, DATASET_COLORS):
        local = df[df.dataset.eq(ds)]
        for feature_set in ["baseline_rf", "mrmr_approx", "qfs_na_top_density"]:
            g = local[local.feature_set.eq(feature_set)].sort_values("k")
            ax.plot(
                g.k,
                g.validation_macro_f1,
                marker="o",
                lw=2.4 if feature_set != "baseline_rf" else 1.6,
                ms=6.5,
                color=colors[feature_set],
                ls=linestyles[feature_set],
                alpha=0.95 if feature_set != "baseline_rf" else 0.75,
                label=labels[feature_set],
            )
        ax.set_title(display_dataset(ds), loc="left", fontsize=11, fontweight="semibold")
        ax.set_xlabel("Tamaño del subconjunto k")
        ax.set_ylabel("Macro-F1 validación")
        # Eje Y completo 0-1 (skill y-axis-baseline: comparacion de magnitud absoluta).
        ax.set_xticks(sorted(local.k.unique()))
        ax.set_ylim(0, 1.02)
        apply_editorial_axes(ax)
    axes[-1].axis("off")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, frameon=False, loc="upper right", bbox_to_anchor=(0.96, 0.88), ncol=3)
    add_header(fig, "La curva de rendimiento muestra dónde QFS aguanta y dónde se separa", "Re-modelado dirigido: baseline, mRMR y QFS-NA top densidad con random forest de Fase 6")
    finish(fig, "EV6")


def figure_a1() -> None:
    # Reconstruida: el summary solo tenia 2 metodos con valor constante (heatmap
    # plano). Aqui, por variable, cuanto supera la puntuacion real al nulo p95
    # (cociente; ancla en 1 = nulo). Muestra el margen de senal, no un conteo.
    df = read_csv("results/tables/05_feature_selection/fs_features_above_null.csv").copy()
    df["ratio"] = df.real_score / df.null_p95.replace(0, np.nan)
    df = df.dropna(subset=["ratio"])
    labels = {"f_classif": "F de ANOVA", "mutual_info": "Información mutua"}
    cmap = {"f_classif": SECONDARY, "mutual_info": ACCENT}
    order = (
        df.groupby("dataset")["ratio"]
        .median()
        .sort_values()
        .index
        .tolist()
    )
    rng = np.random.default_rng(44)
    fig, axes = plt.subplots(len(order), 1, figsize=(8.4, 7.6))
    add_header(
        fig,
        "Cuánto supera la señal real al azar, variable a variable",
        "Cociente puntuación real / percentil 95 del nulo (20 permutaciones), por variable. La línea en 1 es el nulo: a su derecha, señal real.",
    )
    for ax, ds in zip(np.ravel(axes), order):
        s = df[df.dataset == ds]
        ax.axvline(1.0, color=MUTED, lw=1.1, zorder=1)
        for met in labels:
            m = s[s.method == met]
            if m.empty:
                continue
            yj = rng.uniform(-0.16, 0.16, len(m))
            ax.scatter(m.ratio, yj, s=32, color=cmap[met], alpha=0.7,
                       edgecolor="white", linewidth=0.4, zorder=3)
        ax.set_xscale("log")
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_title(display_dataset(ds), loc="left", fontsize=10,
                     fontweight="semibold", pad=3)
        med = float(s["ratio"].median())
        ax.text(med, 0.36, f"mediana {med:.1f}x", ha="center", va="center", fontsize=8, color=MUTED)
        apply_editorial_axes(ax, show_grid=False)
    np.ravel(axes)[-1].set_xlabel("Puntuación real / nulo p95  (escala log; 1 = nulo)")
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=cmap[k],
                      markeredgecolor="white", markersize=8, label=labels[k]) for k in labels]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False,
               fontsize=8.5, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.05, right=0.97, top=0.90, bottom=0.10, hspace=0.55)
    out = FIGS / "a1_permutacion_senal_nulo.png"
    save_editorial_figure(fig, out, dpi=300)
    plt.close(fig)
    print(f"built a1 -> {out}")


def figure_a2() -> None:
    df = read_csv("results/tables/04_split_audit/fase4_leakage_screening.csv")
    top = df.sort_values("auc_abs_binaria", ascending=False).groupby("dataset").head(60)
    fig, ax = plt.subplots(figsize=(8.8, 6.1), facecolor=BG)
    for ds, d in top.groupby("dataset"):
        ax.scatter(d.auc_abs_binaria, d.nmi_con_target, s=18, color=DATASET_COLORS.get(ds, NEUTRAL), alpha=0.55, label=display_dataset(ds))
    ax.axvline(0.99, color=ACCENT, ls="--", lw=1)
    ax.axhline(0.99, color=ACCENT, ls="--", lw=1)
    ax.set_xlabel("AUC univariante absoluto")
    ax.set_ylabel("NMI con target")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    apply_editorial_axes(ax)
    add_header(fig, "La pantalla de leakage no activa el umbral duro", "Variables con mayor AUC/NMI; líneas = 0.99")
    finish(fig, "A2")


def figure_a3() -> None:
    # Reconstruida (2): la version anterior mostraba la DISTRIBUCION de consenso
    # pero no EN QUE selectores coinciden. Ahora: matriz de co-seleccion, Jaccard
    # medio entre cada par de selectores (promedio de los 5 datasets en su
    # presupuesto de referencia). Bloques calidos = familias que eligen lo mismo.
    fs = read_csv("results/tables/05_feature_selection/fs_all_selected_features.csv")
    methods = ["variance", "f_classif", "mutual_info",
               "mutual_correlation", "feature_similarity", "mrmr_approx",
               "rrfs",
               "l1_logistic", "random_forest", "linear_svm",
               "rfe", "boruta"]
    fam_breaks = [3, 6, 7, 10]  # separadores entre familias
    kref = {"olive_oil_3class": 5, "olive_oil_9class": 5}
    datasets = list(DATASET_COLORS)
    acc = np.zeros((len(methods), len(methods)))
    cnt = np.zeros((len(methods), len(methods)))
    for ds in datasets:
        sub = fs[fs.dataset == ds]
        if sub.empty:
            continue
        sets: dict = {}
        for mi, met in enumerate(methods):
            m = sub[(sub.method == met) & (sub.selected == 1)]
            if m.empty:
                continue
            seeds = list(m.seed.unique())
            seed = 42 if 42 in seeds else sorted(seeds)[0]
            m = m[m.seed == seed]
            ks = sorted(m.k.unique())
            kb = min(ks, key=lambda k: abs(int(k) - kref.get(ds, 10)))
            sets[mi] = set(m[m.k == kb].feature.astype(str))
        for a in sets:
            for b in sets:
                uni = len(sets[a] | sets[b])
                if uni > 0:
                    acc[a, b] += len(sets[a] & sets[b]) / uni
                    cnt[a, b] += 1
    M = np.divide(acc, cnt, out=np.full_like(acc, np.nan), where=cnt > 0)
    # Matriz simetrica -> mascara triangular (skill heatmaps): solo el triangulo
    # inferior, celdas mas grandes y legibles.
    n = len(methods)
    Mtri = M.copy()
    for i in range(n):
        for j in range(n):
            if j > i:
                Mtri[i, j] = np.nan
    fig, ax = plt.subplots(figsize=(11.6, 10.2), facecolor=BG)
    cmap = LinearSegmentedColormap.from_list("cons", [BG, "#d9b382", ACCENT])
    cmap.set_bad(BG)
    im = ax.imshow(np.ma.masked_invalid(Mtri), cmap=cmap, vmin=0, vmax=1)
    for i in range(n):
        for j in range(n):
            if j <= i and not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center",
                        fontsize=8.4, color=TEXT if M[i, j] < 0.62 else BG)
    # Separadores de familia en forma de L, acotados al triángulo (no cruzan el vacío).
    for b in fam_breaks:
        ax.plot([-0.5, b - 0.5], [b - 0.5, b - 0.5], color=MUTED, lw=1.0, zorder=6)
        ax.plot([b - 0.5, b - 0.5], [b - 0.5, n - 0.5], color=MUTED, lw=1.0, zorder=6)
    ax.set_xticks(range(n), [method_label(m) for m in methods], rotation=40, ha="right", fontsize=9.5)
    ax.set_yticks(range(n), [method_label(m) for m in methods], fontsize=9.5)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(n - 0.5, -0.5)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cb.set_label("Jaccard medio entre selectores")
    apply_editorial_axes(ax, show_grid=False)
    add_header(
        fig,
        "¿Qué selectores coinciden en las mismas variables?",
        "Solape de Jaccard medio entre cada par de selectores (promedio de los 5 datasets en su presupuesto de referencia). Más cálido = eligen casi las mismas variables; las líneas separan familias (relevancia, redundancia, combinado, embedded, wrapper).",
    )
    fig.subplots_adjust(left=0.16, right=0.99, top=0.86, bottom=0.16)
    out = FIGS / "a3_roster_completo.png"
    save_editorial_figure(fig, out, dpi=300)
    plt.close(fig)
    print(f"built a3 -> {out}")


def figure_a4() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.8), facecolor=BG, gridspec_kw={"left": 0.11, "right": 0.97, "top": 0.78, "bottom": 0.22, "wspace": 0.28})
    for ax, ds, feature_set, model in [
        (axes[0], "olive_oil_3class", "all_features", "linear_svm"),
        (axes[1], "olive_oil_9class", "l1_logistic_k5", "xgboost"),
    ]:
        summary = read_csv("results/tables/06_modeling/modeling_shap_values_summary.csv")
        rows = summary[(summary.dataset == ds) & (summary.feature_set == feature_set) & (summary.model_name == model)].sort_values("rank").head(6)
        raw = pd.read_csv(ROOT / rows.raw_values_path.iloc[0])
        labels = [str(x) for x in str(rows.output_labels.dropna().iloc[0]).split("|")] if rows.output_labels.notna().any() else []
        features = rows.feature.tolist()
        matrix = []
        for label in labels:
            vals = []
            for feat in features:
                col = f"{feat}__class_{label}"
                vals.append(raw[col].abs().mean() if col in raw.columns else np.nan)
            matrix.append(vals)
        mat = np.array(matrix)
        im = ax.imshow(mat, aspect="auto", cmap=LinearSegmentedColormap.from_list("shap_heat", [BG, "#d9b382", ACCENT]))
        ax.set_xticks(range(len(features)), [wrap_label(f, 12) for f in features], rotation=35, ha="right")
        ax.set_yticks(range(len(labels)), [f"Clase {x}" for x in labels])
        ax.set_title(display_dataset(ds), loc="left", fontsize=10.5, fontweight="semibold")
        apply_editorial_axes(ax, show_grid=False)
    fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02, label="|SHAP| medio")
    add_header(fig, "SHAP por clase revela qué variables sostienen cada región de Olive Oil", "Importancia media absoluta por clase para las variables principales")
    finish(fig, "A4")


def figure_a5() -> None:
    # Reconstruida: heatmap medio vacio (sobre tabla maestra colapsada) ->
    # dot plot de deltas de los 12 selectores por dataset, anclado en 0
    # (valencia: a la derecha mejora el baseline; a la izquierda lo empeora).
    from matplotlib.patches import Patch
    cp = read_csv("results/tables/06_modeling/modeling_cost_performance.csv")
    col = "delta_macro_f1_vs_same_model_baseline"
    cp = cp[(cp.selector != "all_features")].dropna(subset=[col])
    best = cp.loc[cp.groupby(["dataset", "selector"])[col].idxmax()].reset_index(drop=True)
    order = list(DATASET_COLORS)
    pos, neg = "#5a8f7b", ACCENT
    rng = np.random.default_rng(44)
    fig, axes = plt.subplots(len(order), 1, figsize=(8.4, 7.8))
    add_header(
        fig,
        "Cuánto mejora cada selector al baseline, por dataset",
        "Mejor Δ de macro-F1 (validación) de cada selector frente a usar todas las variables. La línea en 0 es el baseline.",
    )
    for ax, ds in zip(np.ravel(axes), order):
        s = best[best.dataset == ds].reset_index(drop=True)
        yj = rng.uniform(-0.16, 0.16, len(s))
        ax.axvline(0, color=MUTED, lw=1.1, zorder=1)
        cols = [pos if v >= 0 else neg for v in s[col]]
        ax.scatter(s[col], yj, s=48, c=cols, edgecolor="white", linewidth=0.6, zorder=3)
        ib, iw = int(s[col].values.argmax()), int(s[col].values.argmin())
        for i, up in [(ib, True), (iw, False)]:
            r = s.iloc[i]
            ax.annotate(method_label(r.selector), (r[col], yj[i]), fontsize=7.0,
                        color=TEXT, xytext=(0, 11 if up else -11),
                        textcoords="offset points", ha="center",
                        va="bottom" if up else "top")
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_title(display_dataset(ds), loc="left", fontsize=10,
                     fontweight="semibold", pad=3)
        apply_editorial_axes(ax, grid_axis="x")
    np.ravel(axes)[-1].set_xlabel("Δ macro-F1 frente al baseline (validación)")
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=pos,
               markeredgecolor="white", markersize=8, label="Mejora el baseline"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=neg,
               markeredgecolor="white", markersize=8, label="Empeora el baseline"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False,
               fontsize=8.5, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.05, right=0.97, top=0.90, bottom=0.10, hspace=0.55)
    out = FIGS / "a5_panorama_deltas.png"
    save_editorial_figure(fig, out, dpi=300)
    plt.close(fig)
    print(f"built a5 -> {out}")


def figure_a6() -> None:
    df = read_csv("results/tables/05_feature_selection/fs_qfs_handoff_matrices_index.csv").set_index("dataset").reindex(DATASET_COLORS)
    df = df.sort_values("mean_I_i", ascending=True)
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 5.4), facecolor=BG, gridspec_kw={"left": 0.1, "right": 0.97, "top": 0.77, "bottom": 0.18, "wspace": 0.34})
    axes[0].barh([display_dataset(x) for x in df.index], df.mean_I_i, color=[DATASET_COLORS[x] for x in df.index])
    for yi, val in enumerate(df.mean_I_i):
        axes[0].text(val + df.mean_I_i.max() * 0.025, yi, f"{val:.3f}", va="center", fontsize=8, color=MUTED)
    axes[0].set_xlim(0, df.mean_I_i.max() * 1.16)
    axes[0].set_xlabel(r"Media $I_i$ (relevancia con el target)")
    panel_label(axes[0], "A", "Relevancia target")
    axes[1].barh([display_dataset(x) for x in df.index], df.mean_R_ij_offdiag, color=[DATASET_COLORS[x] for x in df.index])
    for yi, val in enumerate(df.mean_R_ij_offdiag):
        axes[1].text(val + df.mean_R_ij_offdiag.max() * 0.025, yi, f"{val:.3f}", va="center", fontsize=8, color=MUTED)
    axes[1].set_xlim(0, df.mean_R_ij_offdiag.max() * 1.16)
    axes[1].set_xlabel(r"Media $R_{ij}$ (redundancia pareada)")
    panel_label(axes[1], "B", "Redundancia pareada")
    style_all(axes)
    if "madelon" in list(df.index):
        ym = list(df.index).index("madelon")
        axes[0].annotate("Madelon: relevancia casi plana;\nQFS apenas recibe señal que ordenar",
                         xy=(float(df.mean_I_i.loc["madelon"]), ym),
                         xytext=(float(df.mean_I_i.max()) * 0.35, ym),
                         fontsize=7.5, color=ACCENT, va="center", ha="left",
                         arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.0))
    add_header(fig, "Lo que recibe QFS: relevancia y redundancia por dataset", "Vector $I_i$ y matriz $R_{ij}$ calculados en fase 5 y reutilizados por la fase cuántica; en Madelon ambos son casi nulos")
    finish(fig, "A6")


def figure_a7() -> None:
    # Metrica derivada (skill: derived-metrics + log-scales): no plotear segundos
    # crudos en log (las barras se igualan), sino coste ABSOLUTO lineal con base
    # en 0 (A) y el MULTIPLO frente a Boruta, la referencia a batir (B).
    rows = []
    for p in (TABLES / "08_quantum").glob("qfs_runs_*.csv"):
        d = pd.read_csv(p).iloc[0]
        rows.append({"dataset": d.dataset, "elapsed_seconds": d.elapsed_seconds})
    df = pd.DataFrame(rows)
    agg = df.groupby("dataset")["elapsed_seconds"].mean().reindex(DATASET_COLORS).dropna()
    prof = read_csv("results/tables/05_feature_selection/fs_method_profiles.csv").set_index("method")["segundos_medios"]
    boruta = float(prof.get("boruta"))
    order = list(agg.sort_values().index)
    agg = agg.loc[order]
    mult = agg / boruta
    colors = [DATASET_COLORS.get(x, NEUTRAL) for x in order]
    y = np.arange(len(order))
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.6), facecolor=BG,
                             gridspec_kw={"left": 0.12, "right": 0.97, "top": 0.78, "bottom": 0.16, "wspace": 0.46})
    axes[0].barh(y, agg.values, color=colors, zorder=3)
    for i, v in enumerate(agg.values):
        axes[0].text(v + agg.max() * 0.02, i, f"{v:,.0f} s", va="center", fontsize=9, color=TEXT)
    axes[0].set_yticks(y, [display_dataset(x) for x in order])
    axes[0].set_xlabel("Segundos por barrido de β (simulador)")
    axes[0].set_xlim(0, agg.max() * 1.2)
    panel_label(axes[0], "A", "Coste absoluto del simulador")
    axes[1].barh(y, mult.values, color=colors, zorder=3)
    axes[1].axvline(1, color="#5a8f7b", lw=1.6, ls="--", zorder=4)
    for i, v in enumerate(mult.values):
        axes[1].text(v + mult.max() * 0.02, i, f"{v:,.0f}×", va="center", fontsize=9, color=TEXT)
    axes[1].set_yticks(y, [display_dataset(x) for x in order])
    axes[1].set_xlabel("Veces el coste de selección de Boruta  (línea verde = 1×, 6,5 s)")
    axes[1].set_xlim(0, mult.max() * 1.2)
    panel_label(axes[1], "B", "Coste relativo a la referencia a batir")
    style_all(axes, grid_axis="x")
    add_header(
        fig,
        f"Simular QFS cuesta entre {round(mult.min())}× y {round(mult.max())}× lo que cuesta Boruta",
        "Tiempo por barrido de β del simulador analógico: coste absoluto en segundos (A) y múltiplo del coste de selección de Boruta, la referencia a batir (B). Caveat: simulación clásica en CPU, no hardware cuántico.",
    )
    finish(fig, "A7")


def figure_a8() -> None:
    # Reconstruida desde CSV canonico (fs_all_selected_features): el origen del
    # bug "Boruta invisible" era leer una ruta data/.../boruta/k_* inexistente
    # (Boruta no recorre k). Dot plot pareado en lugar de heatmap 5x2.
    q = read_csv("results/tables/08_quantum/qfs_selected_all.csv")
    fs = read_csv("results/tables/05_feature_selection/fs_all_selected_features.csv")
    refs = {"mrmr_approx": "mRMR", "boruta": "Boruta"}
    SEED = 42
    pool = fs.groupby("dataset").feature.nunique().to_dict()  # universo N por dataset
    rows = []
    for ds in DATASET_COLORS:
        qrow = q[(q.dataset == ds) & (q.configuration == "qfs_na")]
        if qrow.empty:
            continue
        qset = set(str(qrow.iloc[0].selected_features).split("|"))
        sub = fs[fs.dataset == ds]
        for method, label in refs.items():
            msub = sub[(sub.method == method) & (sub.selected == 1)]
            if msub.empty:
                continue
            seeds = list(msub.seed.unique())
            seed = SEED if SEED in seeds else sorted(seeds)[0]
            msub = msub[msub.seed == seed]
            ks = sorted(msub.k.unique())
            kbest = min(ks, key=lambda k: abs(int(k) - len(qset)))
            feats = set(msub[msub.k == kbest].feature.astype(str))
            a, b, N = len(qset), len(feats), pool.get(ds, 1)
            ei = a * b / N                       # interseccion esperada (azar)
            chance = ei / (a + b - ei) if (a + b - ei) > 0 else 0.0
            rows.append({"dataset": ds, "label": label,
                         "jaccard": len(qset & feats) / len(qset | feats),
                         "inter": len(qset & feats), "k": int(kbest),
                         "chance": chance})
    d = pd.DataFrame(rows)

    from matplotlib.patches import Patch
    colors = {"mRMR": ACCENT, "Boruta": SECONDARY}
    fig, ax = plt.subplots(figsize=(8.4, 4.7))
    add_header(
        fig,
        "El parecido de QFS-NA con sus referencias, frente al azar",
        "Solape de Jaccard con mRMR/Boruta; la banda gris es el solape esperable por azar (a su derecha, parecido real).",
    )
    order = list(DATASET_COLORS)
    for y, ds in enumerate(order):
        s = d[d.dataset == ds]
        if s.empty:
            continue
        chance = float(s.chance.max())
        ax.add_patch(plt.Rectangle((0, y - 0.34), chance, 0.68, color=NEUTRAL,
                                   alpha=0.25, lw=0, zorder=0))
        if len(s) == 2:
            ax.plot(list(s.jaccard), [y, y], color=GRID, lw=2.0, zorder=1)
        for r in s.itertuples():
            ax.scatter(r.jaccard, y, s=92, color=colors[r.label],
                       edgecolor="white", linewidth=0.8, zorder=3)
            ax.annotate(f"{r.jaccard:.2f}", (r.jaccard, y),
                        xytext=(0, 10 if r.label == "Boruta" else -10),
                        textcoords="offset points", ha="center",
                        va="bottom" if r.label == "Boruta" else "top",
                        fontsize=7.5, color=MUTED)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([display_dataset(ds) for ds in order])
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.invert_yaxis()
    ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("Solape de Jaccard con el subconjunto QFS-NA")
    apply_editorial_axes(ax, grid_axis="x")
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=colors[k],
                      markeredgecolor="white", markersize=9, label=k) for k in colors]
    handles.append(Patch(facecolor=NEUTRAL, alpha=0.25, label="Azar (solape esperado)"))
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=9, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.17, right=0.96, top=0.83, bottom=0.17)
    out = FIGS / "a8_solape_qfs_clasicos.png"
    save_editorial_figure(fig, out, dpi=300)
    plt.close(fig)
    print(f"built a8 -> {out}  | valores:\n{d[['dataset','label','jaccard','inter','k']].to_string(index=False)}")


def figure_a9() -> None:
    auc = read_csv("results/tables/08_quantum/qfs_auc_binarios_contexto.csv")
    comp = read_csv("results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv")
    rows = []
    source_map = {"baseline_fase6": "baseline", "qfs_na": "qfs_na", "qfs_oracle_mucke": "qfs_oracle_mucke"}
    source_labels = {"baseline_fase6": "Baseline", "qfs_na": "QFS-NA", "qfs_oracle_mucke": "QFS-oráculo"}
    for _, r in auc.iterrows():
        cfg = source_map.get(r.fuente)
        if cfg == "baseline":
            macro = comp[comp.dataset == r.dataset].baseline_test_macro_f1.iloc[0]
        else:
            macro = comp[(comp.dataset == r.dataset) & (comp.configuration == cfg)].qfs_test_macro_f1.iloc[0]
        rows.append({"dataset": r.dataset, "fuente": r.fuente, "macro_f1": macro, "auc_roc": r.auc_roc})
    d = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8.8, 5.6), facecolor=BG)
    markers = {"baseline_fase6": "o", "qfs_na": "s", "qfs_oracle_mucke": "^"}
    for ds, g in d.groupby("dataset"):
        g = g.sort_values("macro_f1")
        ax.plot(g.macro_f1, g.auc_roc, color=DATASET_COLORS.get(ds, NEUTRAL), lw=1.0, alpha=0.45)
        for _, r in g.iterrows():
            ax.scatter(
                r.macro_f1,
                r.auc_roc,
                s=82,
                marker=markers[r.fuente],
                color=DATASET_COLORS.get(ds, NEUTRAL),
                edgecolor=TEXT,
                lw=0.55,
                zorder=3,
            )
    ax.set_xlabel("Macro-F1 test")
    ax.set_ylabel("AUC-ROC test")
    ax.set_xlim(0.91, 1.006)
    ax.set_ylim(0.952, 1.004)
    dataset_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=DATASET_COLORS[ds], markeredgecolor=TEXT, markersize=7, label=display_dataset(ds))
        for ds in sorted(d.dataset.unique())
    ]
    source_handles = [
        Line2D([0], [0], marker=markers[src], color=TEXT, markerfacecolor=BG, markeredgecolor=TEXT, lw=0, markersize=7, label=label)
        for src, label in source_labels.items()
    ]
    ax.legend(handles=dataset_handles + source_handles, frameon=False, fontsize=8, loc="lower right", ncol=2)
    apply_editorial_axes(ax)
    add_header(fig, "Macro-F1 y AUC cuentan la misma cautela en binarios", "Contexto binario para baseline, QFS-NA y QFS-oráculo")
    finish(fig, "A9")


def figure_ev5() -> None:
    spec = importlib.util.spec_from_file_location("qfs_aux", ROOT / "QFS_based_on_NA" / "QFS_Auxiliar_functions.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    t_max = 4e-6
    t = np.linspace(0, t_max, 300)
    omega_max = 15e6
    delta_max = 30e6
    delta_local_max = 30e6
    omega = np.array([module.Omega_global(x, t_max, omega_max) for x in t]) / 1e6
    delta = np.array([module.Delta_2step(x, t_max, delta_max) for x in t]) / 1e6
    local = np.array([module.Delta_local_2step(x, t_max, delta_local_max) for x in t]) / 1e6
    x_us = t * 1e6
    fig, ax = plt.subplots(figsize=(9.6, 5.4), facecolor=BG)
    ax.plot(x_us, omega, color=SECONDARY, lw=2.2, label="Omega(t)")
    ax.plot(x_us, delta, color=ACCENT, lw=2.0, label="Delta global(t)")
    ax.plot(x_us, local, color="#d9b382", lw=2.0, label="Delta local(t)")
    ax.axvline(x_us.max() / 2, color=MUTED, ls="--", lw=1)
    ax.text(x_us.max() / 2 + 0.05, min(delta) * 0.88, "cambio de paso", fontsize=8.5, color=MUTED)
    ax.set_xlabel("Tiempo (microsegundos)")
    ax.set_ylabel("Amplitud / detuning (MHz)")
    ax.legend(frameon=False, loc="lower right")
    apply_editorial_axes(ax)
    add_header(fig, "La dinámica adiabática separa preparación global y sesgo local", "Protocolos deterministas Omega(t), Delta_global(t) y Delta_local(t) del solver QFS")
    finish(fig, "EV5")


def heatmap_figure(pivot: pd.DataFrame, key: str, title: str, subtitle: str, cbar_label: str, diverging: bool = False) -> None:
    pivot = pivot.copy()
    fig, ax = plt.subplots(figsize=(max(8.5, pivot.shape[1] * 1.55), max(5.2, pivot.shape[0] * 0.34 + 2.2)), facecolor=BG)
    cmap = LinearSegmentedColormap.from_list("div", [SECONDARY, BG, ACCENT]) if diverging else LinearSegmentedColormap.from_list("seq", [BG, "#d9b382", ACCENT])
    vmax = np.nanmax(np.abs(pivot.to_numpy())) if diverging else np.nanmax(pivot.to_numpy())
    vmin = -vmax if diverging else 0
    im = ax.imshow(pivot.fillna(0), aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(pivot.columns)), [display_dataset(x) for x in pivot.columns], rotation=35, ha="right")
    ax.set_yticks(range(len(pivot.index)), [method_label(x) for x in pivot.index])
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.iloc[i, j]
            if pd.notna(val):
                ax.text(j, i, f"{val:.2f}" if abs(val) < 1 else f"{val:.0f}", ha="center", va="center", fontsize=7.5, color=TEXT)
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label(cbar_label)
    apply_editorial_axes(ax, show_grid=False)
    add_header(fig, title, subtitle)
    finish(fig, key)


def bar_figure(series: pd.Series, key: str, title: str, subtitle: str, xlabel: str) -> None:
    series = series.dropna()
    fig, ax = plt.subplots(figsize=(8.8, 5.4), facecolor=BG)
    colors = [DATASET_COLORS.get(x, NEUTRAL) for x in series.index]
    ax.barh([display_dataset(x) for x in series.index], series.values, color=colors)
    ax.set_xlabel(xlabel)
    apply_editorial_axes(ax)
    add_header(fig, title, subtitle)
    finish(fig, key)


FIGURE_BUILDERS = {
    "F1": figure_f1,
    "F2": figure_f2,
    "F3": figure_f3,
    "F4": figure_f4,
    "F5": figure_f5,
    "F6": figure_f6,
    "F7": figure_f7,
    "F8": figure_f8,
    "F9": figure_f9,
    "F10": figure_f10,
    "EV6": figure_ev6,
    "A1": figure_a1,
    "A2": figure_a2,
    "A3": figure_a3,
    "A4": figure_a4,
    "A5": figure_a5,
    "A6": figure_a6,
    "A7": figure_a7,
    "A8": figure_a8,
    "A9": figure_a9,
    "EV5": figure_ev5,
}


def figure_campo_validacion() -> None:
    """Pieza central: dónde cae QFS en el campo completo de los 12 selectores.

    Lee los CSV canónicos directamente (rejilla de 260 en validación, no la
    tabla maestra colapsada) y guarda solo el PDF final en figs/.
    """
    grid = read_csv("results/tables/06_modeling/modeling_validation_results_all.csv")
    # QFS evaluado con el MISMO protocolo de modelado que los clasicos (4 modelos),
    # no la validacion interna de fase 8: comparacion apples-to-apples en el eje.
    qfs = read_csv("results/tables/08_quantum/qfs_model_results.csv")

    datasets = ["breast_cancer_wisconsin", "customer_churn", "madelon",
                "olive_oil_3class", "olive_oil_9class"]
    model_abbr = {"logistic_regression": "LR", "linear_svm": "SVM",
                  "random_forest": "RF", "xgboost": "XGB"}

    fig, axes = plt.subplots(len(datasets), 1, figsize=(8.6, 9.4))
    add_header(
        fig,
        "QFS frente al campo completo de los doce selectores",
        "Macro-F1 de validación; cada punto es un selector con su mejor modelo.",
    )

    for ax, ds in zip(np.ravel(axes), datasets):
        g = grid[grid.dataset == ds]
        sel = g[g.selector != "all_features"]
        best = sel.loc[sel.groupby("selector").macro_f1.idxmax()].reset_index(drop=True)
        baseline_val = g[g.selector == "all_features"].macro_f1.max()

        q = qfs[qfs.dataset == ds]
        qfs_na_val = q[q.configuration == "qfs_na"].validation_macro_f1.max()
        oracle_val = q[q.configuration == "qfs_oracle_mucke"].validation_macro_f1.max()

        rng = np.random.default_rng(44)
        yj = rng.uniform(-0.13, 0.13, len(best))
        ax.scatter(best.macro_f1, yj, s=40, color=NEUTRAL, alpha=0.85,
                   edgecolor="white", linewidth=0.6, zorder=3)

        ax.axvline(baseline_val, color=MUTED, ls="--", lw=1.0, zorder=2)

        imax = int(best.macro_f1.values.argmax())
        top = best.iloc[imax]
        ax.annotate(f"{method_label(top.selector)} ({model_abbr.get(top.model_name, '')})",
                    (top.macro_f1, yj[imax]), fontsize=7.0, color=TEXT,
                    xytext=(0, 11), textcoords="offset points", ha="center")

        ax.scatter([qfs_na_val], [0.0], marker="D", s=66, color=ACCENT,
                   edgecolor="white", linewidth=0.8, zorder=5)
        ax.scatter([oracle_val], [0.0], marker="^", s=72, color=SECONDARY,
                   edgecolor="white", linewidth=0.8, zorder=5)

        ax.set_ylim(-0.62, 0.62)
        ax.set_yticks([])
        ax.set_title(display_dataset(ds), loc="left", fontsize=10,
                     fontweight="semibold", color=TEXT, pad=4)
        apply_editorial_axes(ax, grid_axis="x")

    np.ravel(axes)[-1].set_xlabel("Macro-F1 de validación")
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=NEUTRAL,
               markeredgecolor="white", markersize=8,
               label="Selector clásico (mejor modelo)"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=ACCENT,
               markeredgecolor="white", markersize=9, label="QFS-NA (mejor modelo)"),
        Line2D([0], [0], marker="^", color="none", markerfacecolor=SECONDARY,
               markeredgecolor="white", markersize=9, label="Óptimo exacto (QUBO)"),
        Line2D([0], [0], color=MUTED, ls="--", lw=1.1,
               label="Baseline (todas las variables)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False,
               fontsize=8.5, bbox_to_anchor=(0.5, 0.005))
    fig.subplots_adjust(left=0.05, right=0.97, top=0.90, bottom=0.12, hspace=0.6)

    FIGS.mkdir(parents=True, exist_ok=True)
    out = FIGS / "F05_campo_validacion_selectores.pdf"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.18, facecolor=BG)
    plt.close(fig)
    print(f"built campo_validacion -> {out}")


def figure_f10_b2() -> None:
    # Reconstruida (generador estaba en /basura): Jaccard QFS-NA vs los 12
    # selectores, pero el COLOR es Jaccard - azar (excess), asi el lector ve si
    # el parecido es real (verde) o trivial (rojo). Arregla celdas vacias.
    q = read_csv("results/tables/08_quantum/qfs_selected_all.csv")
    fs = read_csv("results/tables/05_feature_selection/fs_all_selected_features.csv")
    methods = ["variance", "f_classif", "mutual_info", "mutual_correlation",
               "feature_similarity", "mrmr_approx", "rrfs", "l1_logistic",
               "random_forest", "linear_svm", "rfe", "boruta"]
    pool = fs.groupby("dataset").feature.nunique().to_dict()
    order = list(DATASET_COLORS)
    jac = np.full((len(order), len(methods)), np.nan)
    exc = np.full((len(order), len(methods)), np.nan)
    for i, ds in enumerate(order):
        qrow = q[(q.dataset == ds) & (q.configuration == "qfs_na")]
        if qrow.empty:
            continue
        qset = set(str(qrow.iloc[0].selected_features).split("|"))
        sub = fs[fs.dataset == ds]
        N = pool.get(ds, 1)
        for j, met in enumerate(methods):
            msub = sub[(sub.method == met) & (sub.selected == 1)]
            if msub.empty:
                continue
            seeds = list(msub.seed.unique())
            seed = 42 if 42 in seeds else sorted(seeds)[0]
            msub = msub[msub.seed == seed]
            ks = sorted(msub.k.unique())
            kb = min(ks, key=lambda k: abs(int(k) - len(qset)))
            feats = set(msub[msub.k == kb].feature.astype(str))
            a, b = len(qset), len(feats)
            jc = len(qset & feats) / len(qset | feats)
            ei = a * b / N
            ch = ei / (a + b - ei) if (a + b - ei) > 0 else 0.0
            jac[i, j] = jc
            exc[i, j] = jc - ch
    fig, ax = plt.subplots(figsize=(11.0, 4.6))
    vmax = float(np.nanmax(np.abs(exc))) or 1.0
    cmap = LinearSegmentedColormap.from_list("div", [ACCENT, "#efe9df", "#5a8f7b"])
    im = ax.imshow(exc, aspect="auto", cmap=cmap, vmin=-vmax, vmax=vmax)
    for i in range(len(order)):
        for j in range(len(methods)):
            if not np.isnan(jac[i, j]):
                ax.text(j, i, f"{jac[i, j]:.2f}", ha="center", va="center",
                        fontsize=6.5, color=TEXT)
    # Conclusion visual: recuadrar, por dataset, el selector con MAYOR parecido
    # real (excess sobre azar) -> el lector ve de un vistazo a quien se parece QFS.
    from matplotlib.patches import Rectangle as _Rect
    for i in range(len(order)):
        row = exc[i]
        if np.all(np.isnan(row)):
            continue
        jbest = int(np.nanargmax(row))
        if row[jbest] > 0:
            ax.add_patch(_Rect((jbest - 0.5, i - 0.5), 1, 1, fill=False,
                               edgecolor=TEXT, lw=1.8, zorder=5))
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels([method_label(m) for m in methods], rotation=40, ha="right", fontsize=8)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([display_dataset(d) for d in order])
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cb.set_label("Jaccard − azar")
    apply_editorial_axes(ax, show_grid=False)
    add_header(
        fig,
        "¿A qué familia clásica se parece QFS-NA, más allá del azar?",
        "Número = Jaccard QFS↔selector; color = Jaccard menos el solape por azar (verde: más que azar; rojo: igual o menos). El recuadro marca, por dataset, el selector al que QFS-NA más se parece.",
    )
    fig.subplots_adjust(left=0.13, right=0.99, top=0.80, bottom=0.22)
    out = FIGS / "f10_b2_jaccard_12_metodos.png"
    save_editorial_figure(fig, out, dpi=300)
    plt.close(fig)
    print(f"built f10_b2 -> {out}")


def main() -> None:
    set_editorial_rcparams()
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "savefig.facecolor": BG,
            "text.color": TEXT,
            "axes.labelcolor": TEXT,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "font.size": 9.5,
            "savefig.dpi": 300,
        }
    )
    order = ["F9", "F4", "F2", "F3", "F5", "F6", "F7", "F8", "F10", "EV6", "F1", "EV5", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"]
    for key in order:
        FIGURE_BUILDERS[key]()
        print(f"built {key}: {FIGURE_FILES[key]}.png/.pdf")


if __name__ == "__main__":
    main()
