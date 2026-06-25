"""Funciones de la Fase 7: comparación final del bloque clásico y mapa de evidencia.

La fase no entrena ni recalcula métricas: integra los artefactos de las fases 1-6,
valida su completitud, construye la tabla maestra de experimentos, resume la
comparación final en test y prepara el handoff a la fase cuántica (QFS).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

RANDOM_STATE = 42
DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]
# Margen de equivalencia práctica para macro-F1: una diferencia significativa por
# debajo de este umbral se declara empate práctico (significancia != relevancia).
# REVISAR: umbral declarado de 0.01 (un punto de macro-F1); ajustable.
UMBRAL_EFECTO_PRACTICO = 0.01
TABLE_DIR = Path("results/tables/07_final_comparison")
FIGURE_DIR = Path("results/figures/07_final_comparison")
REPORT_DIR = Path("results/reports/07_final_comparison")
NARRATIVE_TABLE_COLUMNS = {
    "veredicto",
    "candidate_reason",
}

ARTEFACTOS_REQUERIDOS = {
    "fase1_sintesis": "results/tables/01_raw_eda/fase1_sintesis_evidencias.csv",
    "fase3_metricas_split": "results/tables/03_postprocessing_audit/fase3_resumen_metricas_split.csv",
    "fase4_resumen": "results/tables/04_split_audit/fase4_resumen_para_fase5.csv",
    "fase5_jaccard": "results/tables/05_feature_selection/fs_jaccard_stability.csv",
    "fase5_redundancia": "results/tables/05_feature_selection/fs_redundancy_vs_full.csv",
    "fase5_permutacion": "results/tables/05_feature_selection/fs_permutation_summary.csv",
    "fase6_validacion": "results/tables/06_modeling/modeling_validation_results_all.csv",
    "fase6_test": "results/tables/06_modeling/modeling_test_results_candidates.csv",
    "fase6_intervalos_test": "results/tables/06_modeling/modeling_test_confidence_intervals.csv",
    "fase6_comparaciones": "results/tables/06_modeling/modeling_pairwise_comparison_tests.csv",
    "fase6_permutacion": "results/tables/06_modeling/modeling_permutation_test_results.csv",
    "fase6_coste": "results/tables/06_modeling/modeling_cost_performance.csv",
    "fase5_qfs_matrices_index": "results/tables/05_feature_selection/fs_qfs_handoff_matrices_index.csv",
}


def asegurar_directorios() -> None:
    for path in [TABLE_DIR, FIGURE_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def guardar_tabla(tabla: pd.DataFrame, nombre: str) -> Path:
    ruta = TABLE_DIR / nombre
    columnas_narrativas = [col for col in tabla.columns if col in NARRATIVE_TABLE_COLUMNS]
    tabla.drop(columns=columnas_narrativas, errors="ignore").to_csv(ruta, index=False)
    return ruta


def configurar_estilo() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.facecolor": "#F8F5EF",
            "axes.facecolor": "#F8F5EF",
            "axes.edgecolor": "#CFC7BA",
            "font.size": 10,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.labelcolor": "#2F2F2F",
            "xtick.color": "#2F2F2F",
            "ytick.color": "#2F2F2F",
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        }
    )


def guardar_figura(fig: plt.Figure, nombre: str) -> Path:
    ruta = FIGURE_DIR / nombre
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=300)
    fig.savefig(ruta.with_suffix(".pdf"))
    plt.close(fig)
    return ruta


def suavizar_ejes(eje: plt.Axes) -> None:
    """Aplica el acabado editorial común sin alterar datos ni escalas."""
    eje.spines["top"].set_visible(False)
    eje.spines["right"].set_visible(False)
    eje.spines["left"].set_color("#CFC7BA")
    eje.spines["bottom"].set_color("#CFC7BA")
    eje.grid(axis="x", color="#E5DED2", linewidth=0.8)
    eje.grid(axis="y", color="#EDE7DC", linewidth=0.6)


def inventariar_artefactos() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Carga los artefactos requeridos de fases anteriores y registra su estado."""
    artefactos: dict[str, pd.DataFrame] = {}
    filas = []
    for clave, ruta_texto in ARTEFACTOS_REQUERIDOS.items():
        ruta = Path(ruta_texto)
        existe = ruta.exists()
        tabla = pd.read_csv(ruta) if existe else pd.DataFrame()
        artefactos[clave] = tabla
        filas.append(
            {
                "artefacto": clave,
                "ruta": ruta_texto,
                "existe": existe,
                "filas": len(tabla),
                "estado": "ok" if existe and not tabla.empty else "falta",
            }
        )
    return artefactos, pd.DataFrame(filas)


def corregir_multiplicidad(p_valores: pd.Series) -> pd.DataFrame:
    """Corrige por comparaciones múltiples la familia de contrastes pareados.

    Aplica Benjamini-Hochberg (FDR, step-up) y Holm (family-wise, step-down)
    sobre los p-valores no nulos, dejando NaN donde no hay contraste (baseline).
    """
    fdr = pd.Series(np.nan, index=p_valores.index, dtype=float)
    holm = pd.Series(np.nan, index=p_valores.index, dtype=float)
    validos = p_valores.dropna()
    n = len(validos)
    if n == 0:
        return pd.DataFrame({"paired_pvalue_fdr": fdr, "paired_pvalue_holm": holm})
    orden = validos.sort_values()
    p = orden.to_numpy(dtype=float)
    rangos = np.arange(1, n + 1)
    # Benjamini-Hochberg: p * n / rango, monotonía step-up desde el mayor
    bh = np.minimum.accumulate((p * n / rangos)[::-1])[::-1]
    bh = np.clip(bh, 0.0, 1.0)
    # Holm: p * (n - i), monotonía step-down (acumulado máximo)
    hl = np.maximum.accumulate(p * (n - np.arange(n)))
    hl = np.clip(hl, 0.0, 1.0)
    fdr.loc[orden.index] = bh
    holm.loc[orden.index] = hl
    return pd.DataFrame({"paired_pvalue_fdr": fdr, "paired_pvalue_holm": holm})


def construir_tabla_maestra(artefactos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une validación, test y contrastes de la Fase 6 en una tabla por experimento candidato."""
    test = artefactos["fase6_test"].copy()
    # Esquema de Fase 6: difference_macro_f1 y sign_permutation_p_value; se
    # renombran a los nombres internos canónicos que usa el resto de la fase.
    comparaciones = artefactos["fase6_comparaciones"][
        ["candidate_experiment_id", "difference_macro_f1", "ci_low", "ci_high", "sign_permutation_p_value"]
    ].rename(columns={
        "candidate_experiment_id": "experiment_id",
        "difference_macro_f1": "difference_candidate_minus_baseline",
        "sign_permutation_p_value": "paired_correctness_permutation_pvalue",
    })
    permutacion = artefactos["fase6_permutacion"][["experiment_id", "p_value"]].rename(
        columns={"p_value": "label_permutation_p_value"}
    )
    intervalos = artefactos["fase6_intervalos_test"]
    if "split" in intervalos.columns:
        intervalos = intervalos[intervalos["split"].eq("test")]
    intervalos_macro = intervalos[intervalos["metric"].eq("macro_f1")][
        ["experiment_id", "ci_low", "ci_high"]
    ].rename(columns={"ci_low": "test_macro_f1_ci_low", "ci_high": "test_macro_f1_ci_high"})

    maestra = (
        test.merge(intervalos_macro, on="experiment_id", how="left")
        .merge(comparaciones, on="experiment_id", how="left")
        .merge(permutacion, on="experiment_id", how="left")
    )
    maestra = maestra.sort_values(["dataset", "test_macro_f1"], ascending=[True, False]).reset_index(drop=True)
    # Corrección por multiplicidad sobre la familia de contrastes pareados
    # candidato-vs-baseline (todos los candidatos seleccionados de los 5 datasets).
    correccion = corregir_multiplicidad(maestra["paired_correctness_permutation_pvalue"])
    maestra = pd.concat([maestra, correccion], axis=1)
    return maestra


def validar_completitud(artefactos: dict[str, pd.DataFrame], maestra: pd.DataFrame) -> pd.DataFrame:
    """Comprueba que cada dataset llega a la comparación final con baseline, candidatos y contrastes."""
    filas = []
    for dataset in DATASETS:
        candidatos = maestra[maestra["dataset"].eq(dataset)]
        baseline = candidatos[candidatos["feature_set"].eq("all_features")]
        seleccionados = candidatos[~candidatos["feature_set"].eq("all_features")]
        validacion = artefactos["fase6_validacion"]
        n_experimentos_validacion = int(validacion["dataset"].eq(dataset).sum())
        filas.append(
            {
                "dataset": dataset,
                "candidatos_test": len(candidatos),
                "tiene_baseline": not baseline.empty,
                "n_seleccionados": len(seleccionados),
                "experimentos_validacion": n_experimentos_validacion,
                "contrastes_pareados_completos": bool(seleccionados["difference_candidate_minus_baseline"].notna().all()),
                "permutacion_completa": bool(candidatos["label_permutation_p_value"].notna().all()),
                "estado": "ok"
                if (not baseline.empty and len(seleccionados) >= 1 and n_experimentos_validacion >= 15)
                else "incompleto",
            }
        )
    return pd.DataFrame(filas)


def resumen_comparacion_final(maestra: pd.DataFrame) -> pd.DataFrame:
    """Resume por dataset el baseline frente al mejor subconjunto seleccionado en test."""
    filas = []
    for dataset in DATASETS:
        candidatos = maestra[maestra["dataset"].eq(dataset)]
        baseline = candidatos[candidatos["feature_set"].eq("all_features")].iloc[0]
        mejor = candidatos[~candidatos["feature_set"].eq("all_features")].sort_values(
            "test_macro_f1", ascending=False
        ).iloc[0]
        delta = mejor["test_macro_f1"] - baseline["test_macro_f1"]
        ci_low = mejor["ci_low"]
        ci_high = mejor["ci_high"]
        p_crudo = mejor["paired_correctness_permutation_pvalue"]
        p_fdr = mejor["paired_pvalue_fdr"]
        p_holm = mejor["paired_pvalue_holm"]
        # El veredicto usa el p-valor corregido por multiplicidad (FDR), coherente
        # con la corrección por comparaciones múltiples aplicada en el EDA, Y un
        # umbral de efecto práctico (UMBRAL_EFECTO_PRACTICO): una diferencia
        # estadísticamente significativa pero de magnitud despreciable se declara
        # empate práctico, en línea con la sección de validación estadística
        # (significancia distinta de relevancia). Constante revisable.
        p_decision = p_fdr if pd.notna(p_fdr) else p_crudo
        significativa = (p_decision < 0.05) and (ci_low > 0)
        if delta > UMBRAL_EFECTO_PRACTICO and significativa:
            veredicto = "mejora_significativa"
        elif significativa and 0 < delta <= UMBRAL_EFECTO_PRACTICO:
            veredicto = "empate_practico"
        elif delta < 0 and (p_decision < 0.05) and ci_high < 0:
            veredicto = "deterioro"
        else:
            veredicto = "equivalente_dentro_del_ruido"
        filas.append(
            {
                "dataset": dataset,
                "baseline_features": int(baseline["n_features_used"]),
                "baseline_test_macro_f1": baseline["test_macro_f1"],
                "mejor_feature_set": mejor["feature_set"],
                "mejor_modelo": mejor["model_name"],
                "seleccion_features": int(mejor["n_features_used"]),
                "seleccion_test_macro_f1": mejor["test_macro_f1"],
                "delta_test_macro_f1": delta,
                "delta_ci_low": ci_low,
                "delta_ci_high": ci_high,
                "p_valor_pareado_crudo": p_crudo,
                "p_valor_pareado_fdr": p_fdr,
                "p_valor_pareado_holm": p_holm,
                "veredicto": veredicto,
            }
        )
    return pd.DataFrame(filas)


def sintesis_seleccion_clasica(artefactos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Cruza estabilidad y redundancia (Fase 5) con el delta de validación (Fase 6) por dataset y método."""
    jaccard = (
        artefactos["fase5_jaccard"].groupby(["dataset", "method"], as_index=False)
        .agg(jaccard_medio=("jaccard", "mean"))
    )
    redundancia = artefactos["fase5_redundancia"]
    redundancia = (
        redundancia.assign(delta_redundancia=redundancia["selected_mean_abs_corr"] - redundancia["full_mean_abs_corr"])
        .groupby(["dataset", "method"], as_index=False)
        .agg(delta_redundancia=("delta_redundancia", "mean"))
    )
    validacion = artefactos["fase6_validacion"]
    seleccionados = validacion[~validacion["feature_set"].eq("all_features")].copy()
    seleccionados["method"] = seleccionados["selector"]
    rendimiento = (
        seleccionados.groupby(["dataset", "method"], as_index=False)
        .agg(mejor_delta_validacion=("delta_macro_f1_vs_same_model_baseline", "max"))
    )
    return (
        rendimiento.merge(jaccard, on=["dataset", "method"], how="left")
        .merge(redundancia, on=["dataset", "method"], how="left")
        .sort_values(["dataset", "mejor_delta_validacion"], ascending=[True, False])
        .reset_index(drop=True)
    )


def preparar_handoff_qfs(maestra: pd.DataFrame, resumen: pd.DataFrame, artefactos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Construye la referencia operativa que la fase cuántica debe igualar o superar por dataset."""
    # Presupuesto de variables de referencia por dataset (ver
    # docs/decisions/roster_clasico_espejo.md): mayor k<=10 con reducción real en
    # los conjuntos grandes y 5 en las dos formulaciones de Olive Oil.
    K_REFERENCIA = {
        "breast_cancer_wisconsin": 10,
        "customer_churn": 10,
        "madelon": 10,
        "olive_oil_3class": 5,
        "olive_oil_9class": 5,
    }
    k_referencia = pd.DataFrame(
        [{"dataset": d, "k_referencia": k} for d, k in K_REFERENCIA.items()]
    )
    permutacion_f5 = (
        artefactos["fase5_permutacion"].groupby("dataset", as_index=False)
        .agg(mediana_p_permutacion_seleccion=("median_empirical_p_value", "median"))
    )
    handoff = resumen.merge(k_referencia, on="dataset").merge(permutacion_f5, on="dataset")
    indice_matrices = artefactos["fase5_qfs_matrices_index"][
        ["dataset", "mi_target_vector_table", "pairwise_mi_matrix_table", "mean_I_i", "max_I_i", "mean_R_ij_offdiag", "max_R_ij_offdiag"]
    ]
    handoff = handoff.merge(indice_matrices, on="dataset", how="left")
    columnas = [
        "dataset",
        "k_referencia",
        "baseline_test_macro_f1",
        "seleccion_test_macro_f1",
        "mejor_feature_set",
        "mediana_p_permutacion_seleccion",
        "mi_target_vector_table",
        "pairwise_mi_matrix_table",
        "mean_I_i",
        "max_I_i",
        "mean_R_ij_offdiag",
        "max_R_ij_offdiag",
    ]
    return handoff[columnas]


def plot_comparacion_test(maestra: pd.DataFrame) -> Path:
    """Macro-F1 en test con IC bootstrap: baseline frente a candidatos seleccionados, por dataset."""
    datos = maestra.copy()
    datos["config"] = np.where(datos["feature_set"].eq("all_features"), "baseline (todas)", "selección")
    fig, ejes = plt.subplots(1, len(DATASETS), figsize=(16, 5.0), sharey=False)
    for eje, dataset in zip(ejes, DATASETS):
        grupo = datos[datos["dataset"].eq(dataset)].sort_values("test_macro_f1")
        posiciones = np.arange(len(grupo))
        colores = ["#8B867C" if c == "baseline (todas)" else "#2F6F9F" for c in grupo["config"]]
        eje.errorbar(
            grupo["test_macro_f1"],
            posiciones,
            xerr=[
                grupo["test_macro_f1"] - grupo["test_macro_f1_ci_low"],
                grupo["test_macro_f1_ci_high"] - grupo["test_macro_f1"],
            ],
            fmt="none",
            ecolor="#b0aca3",
            capsize=3,
        )
        eje.scatter(grupo["test_macro_f1"], posiciones, c=colores, s=55, zorder=3)
        etiquetas = [
            f"{fila.feature_set}\n({fila.model_name}, {fila.n_features_used} vars)"
            for fila in grupo.itertuples()
        ]
        eje.set_yticks(posiciones)
        eje.set_yticklabels(etiquetas, fontsize=7)
        eje.set_title(dataset, fontsize=9)
        eje.set_xlabel("Macro-F1 en test")
        suavizar_ejes(eje)
        if dataset == "madelon":
            mejor = grupo.loc[grupo["feature_set"].ne("all_features")].sort_values("test_macro_f1", ascending=False).iloc[0]
            delta_m = float(mejor["difference_candidate_minus_baseline"])
            ci_lo_m = float(mejor["ci_low"])
            ci_hi_m = float(mejor["ci_high"])
            eje.annotate(
                f"+{delta_m:.3f} F1\nIC [{ci_lo_m:.2f}, {ci_hi_m:.2f}]",
                xy=(mejor["test_macro_f1"], int(np.where(grupo.index == mejor.name)[0][0])),
                xytext=(0.69, 1.7),
                textcoords="data",
                arrowprops={"arrowstyle": "->", "color": "#B85C5C", "lw": 1.1},
                color="#B85C5C",
                fontsize=8,
                ha="left",
            )
    fig.suptitle(
        "Madelon es el único salto significativo; el resto comprime variables sin perder macro-F1",
        x=0.03,
        y=1.02,
        ha="left",
        fontweight="bold",
        color="#2F2F2F",
    )
    fig.text(0.03, 0.955, "Puntos con intervalo bootstrap 95%; gris = baseline con todas las variables, azul = subconjunto seleccionado.", color="#6F6A60")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return guardar_figura(fig, "fase7_test_baseline_vs_seleccion.png")


def plot_panorama_validacion(artefactos: dict[str, pd.DataFrame]) -> Path:
    """Mapa de calor del mejor delta de macro-F1 en validación por dataset y selector."""
    validacion = artefactos["fase6_validacion"]
    seleccionados = validacion[~validacion["feature_set"].eq("all_features")]
    tabla = (
        seleccionados.groupby(["dataset", "selector"])["delta_macro_f1_vs_same_model_baseline"]
        .max()
        .unstack()
    )
    fig, eje = plt.subplots(figsize=(9.8, 4.8))
    sns.heatmap(
        tabla,
        annot=True,
        fmt="+.3f",
        cmap=sns.diverging_palette(15, 145, s=65, l=55, as_cmap=True),
        center=0,
        linewidths=0.5,
        linecolor="#F8F5EF",
        ax=eje,
        cbar_kws={"label": "mejor delta macro-F1"},
    )
    eje.set_title("La mejora de validación se concentra en madelon y no en un selector universal")
    eje.set_xlabel("")
    eje.set_ylabel("")
    fila_madelon = int(np.where(tabla.index == "madelon")[0][0])
    eje.add_patch(plt.Rectangle((0, fila_madelon), tabla.shape[1], 1, fill=False, edgecolor="#B85C5C", lw=1.5))
    mad = tabla.loc["madelon"].dropna()
    fig.text(
        0.12,
        0.02,
        f"Fila resaltada: madelon concentra las mejoras de validación (+{mad.min():.3f} a +{mad.max():.3f}), por eso pasa a ser el banco principal para QFS compacto.",
        color="#B85C5C",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    return guardar_figura(fig, "fase7_panorama_validacion_delta.png")


PALETA_DATASETS = {
    "breast_cancer_wisconsin": "#2F6F9F",
    "customer_churn": "#5E8C61",
    "madelon": "#B85C5C",
    "olive_oil_3class": "#D9822B",
    "olive_oil_9class": "#6F6A60",
}


def plot_perfil_seleccion(sintesis: pd.DataFrame) -> Path:
    """Dos lecturas del perfil de selección: la estabilidad es uniforme y el
    diferenciador real entre métodos es el control de redundancia."""
    fig, (eje_a, eje_b) = plt.subplots(1, 2, figsize=(13.5, 5.4), width_ratios=[1.0, 1.25])

    # Panel A: estabilidad media por método (con el estimador de MI determinista
    # la selección es estable en casi todos; ya no hay régimen inestable).
    estab = (
        sintesis.dropna(subset=["jaccard_medio"])
        .groupby("method", as_index=False)
        .agg(jaccard_medio=("jaccard_medio", "mean"))
        .sort_values("jaccard_medio")
    )
    colores_a = ["#B85C5C" if v < 0.95 else "#9FB3C8" for v in estab["jaccard_medio"]]
    eje_a.barh(estab["method"], estab["jaccard_medio"], color=colores_a)
    eje_a.axvline(1.0, color="#8B867C", linewidth=1, linestyle=":", alpha=0.7)
    eje_a.set_xlim(0, 1.05)
    eje_a.set_xlabel("Estabilidad entre semillas (Jaccard medio)")
    eje_a.set_title("La selección es estable en todos los métodos", fontsize=10)
    eje_a.tick_params(axis="y", labelsize=8)
    suavizar_ejes(eje_a)

    # Panel B: control de redundancia frente a mejora de rendimiento. El cuadrante
    # deseable es arriba-izquierda (reduce redundancia y mejora macro-F1).
    datos = sintesis.dropna(subset=["delta_redundancia", "mejor_delta_validacion"])
    for ds, grupo in datos.groupby("dataset"):
        eje_b.scatter(
            grupo["delta_redundancia"], grupo["mejor_delta_validacion"],
            color=PALETA_DATASETS.get(ds, "#6F6A60"), s=90, alpha=0.85, label=ds, zorder=3,
        )
    eje_b.axvline(0, color="#8B867C", linewidth=1, linestyle="--")
    eje_b.axhline(0, color="#8B867C", linewidth=1, linestyle="--")
    mrmr = datos[(datos["method"].eq("mrmr_approx")) & (datos["dataset"].eq("madelon"))]
    if not mrmr.empty:
        r = mrmr.iloc[0]
        eje_b.annotate(
            "mRMR: único que reduce\nredundancia en madelon",
            xy=(float(r["delta_redundancia"]), float(r["mejor_delta_validacion"])),
            xytext=(float(r["delta_redundancia"]) + 0.02, float(r["mejor_delta_validacion"]) + 0.12),
            arrowprops={"arrowstyle": "->", "color": "#B85C5C", "lw": 1.1},
            color="#B85C5C", fontsize=8.5,
        )
    eje_b.set_xlabel("Cambio de redundancia interna (negativo = más diverso)")
    eje_b.set_ylabel("Mejor delta de macro-F1 en validación")
    eje_b.set_title("El control de redundancia distingue a los métodos", fontsize=10)
    eje_b.legend(fontsize=7.5, loc="upper right")
    suavizar_ejes(eje_b)

    fig.suptitle(
        "Con el estimador de MI determinista la selección es estable; el diferenciador es la redundancia",
        x=0.02, y=1.02, ha="left", fontweight="bold", color="#2F2F2F",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    return guardar_figura(fig, "fase7_estabilidad_vs_rendimiento.png")


def plot_mini_resumen_dataset(dataset: str, comparacion_final: pd.DataFrame, sintesis: pd.DataFrame) -> Path:
    """Ficha visual por dataset basada en la comparación final y la síntesis de selectores."""
    fila = comparacion_final[comparacion_final["dataset"].eq(dataset)].iloc[0]
    sintesis_ds = sintesis[sintesis["dataset"].eq(dataset)].copy()
    mejor_estabilidad = sintesis_ds["jaccard_medio"].max()
    mejor_delta_valid = sintesis_ds["mejor_delta_validacion"].max()

    fig, ejes = plt.subplots(1, 2, figsize=(8.8, 3.2), gridspec_kw={"width_ratios": [1, 1.35]})
    valores = pd.DataFrame(
        {
            "configuracion": [
                f"baseline\n{int(fila['baseline_features'])} vars",
                f"selección\n{int(fila['seleccion_features'])} vars",
            ],
            "macro_f1": [fila["baseline_test_macro_f1"], fila["seleccion_test_macro_f1"]],
        }
    )
    colores = ["#8B867C", "#2F6F9F"]
    ejes[0].barh(valores["configuracion"], valores["macro_f1"], color=colores, height=0.42)
    ejes[0].set_xlim(max(0, valores["macro_f1"].min() - 0.08), min(1.02, valores["macro_f1"].max() + 0.08))
    ejes[0].set_xlabel("Macro-F1 en test")
    ejes[0].set_title("Test final")
    for y, valor in enumerate(valores["macro_f1"]):
        ejes[0].text(valor + 0.006, y, f"{valor:.3f}", va="center", fontsize=9, color="#2F2F2F")
    suavizar_ejes(ejes[0])

    sns.scatterplot(
        data=sintesis_ds,
        x="jaccard_medio",
        y="mejor_delta_validacion",
        hue="method",
        s=80,
        ax=ejes[1],
        legend=False,
        palette="colorblind",
    )
    ejes[1].axhline(0, color="#8B867C", linewidth=1, linestyle="--")
    ejes[1].axvline(0.7, color="#8B867C", linewidth=1, linestyle=":", alpha=0.8)
    ejes[1].set_xlim(-0.02, 1.02)
    ejes[1].set_xlabel("Jaccard medio")
    ejes[1].set_ylabel("Mejor delta validación")
    ejes[1].set_title("Perfil de selectores")
    suavizar_ejes(ejes[1])

    titulo_veredicto = fila["veredicto"].replace("_", " ")
    fig.suptitle(
        f"{dataset}: delta test {fila['delta_test_macro_f1']:+.3f} y veredicto {titulo_veredicto}",
        x=0.03,
        y=1.03,
        ha="left",
        fontweight="bold",
        color="#2F2F2F",
    )
    fig.text(
        0.03,
        0.92,
        f"IC delta [{fila['delta_ci_low']:.2f}, {fila['delta_ci_high']:.2f}], p pareado (FDR)={fila['p_valor_pareado_fdr']:.3f}; "
        f"mejor Jaccard={mejor_estabilidad:.2f}, mejor delta validación={mejor_delta_valid:+.3f}.",
        color="#6F6A60",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.86])
    nombre = f"fase7_mini_resumen_evidencia__{dataset}.png"
    return guardar_figura(fig, nombre)
