from dataclasses import dataclass
from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fase1_agent_utils import (
    benjamini_hochberg,
    categorical_features,
    classify_columns,
    cliffs_delta,
    cramers_v,
    ensure_dir,
    get_feature_columns,
    infer_target_column,
    is_identifier_column,
    markdown_report_to_latex,
    numeric_features,
    robust_outlier_rate,
    safe_read_table,
    save_current_figure,
    save_table,
    write_latex_report_from_markdown,
)


# ---------------------- #
# PALETA EDITORIAL (TFG) #
# ---------------------- #
from viz_core.editorial_warmth import (
    EditorialPalette,
    set_editorial_rcparams,
    apply_editorial_axes,
    add_editorial_text,
)

TFG_PALETTE = EditorialPalette(
    background="#FAF7F2",
    panel="#FAF7F2",
    grid="#E6DED2",
    text="#2D2A26",
    spine="#E6DED2",
    muted_text="#6F6A60",
    primary="#2F6F9F",
    secondary="#8FB3C9",
    accent="#D9822B",
    positive="#5E8C61",
    negative="#B85C5C",
    neutral="#B8B0A3",
    categorical=(
        "#2F6F9F",
        "#D9822B",
        "#5E8C61",
        "#B85C5C",
        "#8FB3C9",
        "#B8B0A3",
    )
)

PALETA = {
    "fondo": TFG_PALETTE.background,
    "panel": TFG_PALETTE.panel,
    "texto": TFG_PALETTE.text,
    "muted": TFG_PALETTE.muted_text,
    "rejilla": TFG_PALETTE.grid,
    "azul": TFG_PALETTE.primary,
    "azul_suave": TFG_PALETTE.secondary,
    "naranja": TFG_PALETTE.accent,
    "verde": TFG_PALETTE.positive,
    "rojo": TFG_PALETTE.negative,
    "gris": TFG_PALETTE.neutral,
    "morado": "#7A6FA5",
}

ORDEN_DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil",
]

CORR_THRESHOLD = 0.85
DOMINANT_MODE_THRESHOLD = 0.98
LOW_UNIQUE_RATIO = 0.01
MAX_VIS_ROWS = 5000
MAX_HEATMAP_FEATURES = 60
RANDOM_STATE = 42


@dataclass
class Phase1Context:
    project_root: Path
    raw_data_dir: Path
    src_dir: Path
    tables_dir: Path
    figures_dir: Path
    reports_dir: Path
    dataset_config: dict
    raw_datasets: dict
    sampled_datasets: dict
    tables: dict
    figure_paths: list


def crear_contexto_fase1(project_root=None):
    root = Path.cwd() if project_root is None else Path(project_root)
    if root.name == "notebooks":
        root = root.parent
    raw_data_dir = root / "data" / "01_raw"
    src_dir = root / "src"
    tables_dir = root / "results" / "tables" / "01_raw_eda"
    figures_dir = root / "results" / "figures" / "01_raw_eda"
    reports_dir = root / "results" / "reports" / "01_raw_eda"
    for path in [src_dir, tables_dir, figures_dir, reports_dir]:
        ensure_dir(path)
    dataset_config = {
        "breast_cancer_wisconsin": {"path": raw_data_dir / "breast_cancer_wisconsin.csv", "target": "target"},
        "customer_churn": {"path": raw_data_dir / "customer_churn.csv", "target": "Churn"},
        "madelon": {"path": raw_data_dir / "madelon.csv", "target": "target"},
        "olive_oil": {"path": raw_data_dir / "olive_oil.csv", "target": "target"},
    }
    configurar_estilo_editorial()
    return Phase1Context(root, raw_data_dir, src_dir, tables_dir, figures_dir, reports_dir, dataset_config, {}, {}, {}, [])


def configurar_estilo_editorial():
    set_editorial_rcparams(TFG_PALETTE)


def registrar_tabla(contexto, nombre_archivo, tabla):
    contexto.tables[nombre_archivo] = tabla
    save_table(tabla, contexto.tables_dir / nombre_archivo)
    return tabla


def registrar_figura(contexto, ruta_relativa):
    ruta = contexto.figures_dir / ruta_relativa
    save_current_figure(ruta, dpi=180)
    contexto.figure_paths.append(ruta)
    return ruta


def preparar_ejes(axis, grid_axis="x"):
    axis.set_facecolor(TFG_PALETTE.panel)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(TFG_PALETTE.spine)
    axis.spines["bottom"].set_color(TFG_PALETTE.spine)
    if grid_axis:
        axis.grid(axis=grid_axis, color=TFG_PALETTE.grid, alpha=0.65, linewidth=0.6)
    axis.set_axisbelow(True)


def etiqueta_barras_horizontales(axis, valores, formato="{:.0f}", desplazamiento=0.01):
    maximo = max([float(v) for v in valores if pd.notna(v)] + [1.0])
    for indice, valor in enumerate(valores):
        if pd.isna(valor):
            continue
        axis.text(float(valor) + maximo * desplazamiento, indice, formato.format(valor), va="center", color=TFG_PALETTE.muted_text, fontsize=8)


def formato_entero_es(valor):
    return f"{int(valor):,}".replace(",", ".")


def ordenar_datasets(tabla):
    orden = {nombre: posicion for posicion, nombre in enumerate(ORDEN_DATASETS)}
    return tabla.assign(_orden=tabla["dataset"].map(orden).fillna(99)).sort_values("_orden").drop(columns="_orden")


def etiqueta_dataset(nombre):
    etiquetas = {
        "breast_cancer_wisconsin": "breast\ncancer\nwisconsin",
        "customer_churn": "customer\nchurn",
        "madelon": "madelon",
        "olive_oil": "olive\noil",
    }
    return etiquetas.get(nombre, str(nombre).replace("_", "\n"))


def correlaciones_spearman_pares(datos, columnas):
    corr = datos[columnas].corr(method="spearman")
    filas = []
    for pos_a, variable_a in enumerate(columnas):
        for variable_b in columnas[pos_a + 1:]:
            valor = corr.loc[variable_a, variable_b]
            filas.append({
                "variable_a": variable_a,
                "variable_b": variable_b,
                "spearman": valor,
                "abs_spearman": abs(valor),
                "par": f"{variable_a} / {variable_b}",
            })
    return pd.DataFrame(filas)


def color_severidad(valor):
    return {
        0: TFG_PALETTE.positive,
        1: TFG_PALETTE.accent,
        2: TFG_PALETTE.negative,
    }.get(int(valor), TFG_PALETTE.neutral)


def heatmap_spearman_triangular(axis, matriz_correlacion, columnas, mostrar_etiquetas=True):
    mascara_superior = np.triu(np.ones_like(matriz_correlacion, dtype=bool), k=1)
    matriz_visible = matriz_correlacion.mask(mascara_superior)
    image = axis.imshow(matriz_visible, vmin=-1, vmax=1, cmap="RdBu_r", aspect="auto")
    axis.set_xticks(range(len(columnas)))
    axis.set_yticks(range(len(columnas)))
    if mostrar_etiquetas:
        axis.set_xticklabels(columnas, rotation=90, fontsize=7)
        axis.set_yticklabels(columnas, fontsize=7)
    else:
        axis.set_xticklabels([])
        axis.set_yticklabels([])
    return image


def cargar_datasets_crudos(contexto):
    datasets = {}
    load_rows, columns_rows, issue_rows = [], [], []
    for name, cfg in contexto.dataset_config.items():
        path = Path(cfg["path"])
        try:
            if not path.exists():
                raise FileNotFoundError(f"No existe el archivo: {path}")
            datos = safe_read_table(path)
            target = infer_target_column(datos, cfg.get("target"))
            datasets[name] = {"df": datos, "target": target, "path": path}
            load_rows.append({
                "dataset": name,
                "archivo": str(path),
                "filas": len(datos),
                "columnas": datos.shape[1],
                "target_detectado": target,
                "carga_correcta": True,
                "incidencias": "" if target else "Target no identificado",
            })
            for variable in datos.columns:
                columns_rows.append({"dataset": name, "variable": variable, "dtype": str(datos[variable].dtype)})
            if target is None:
                issue_rows.append({"dataset": name, "tipo": "target", "detalle": "No se ha identificado target"})
            for variable in [col for col in datos.columns if str(col).startswith("Unnamed") or str(col).strip() == ""]:
                issue_rows.append({"dataset": name, "tipo": "columna_sin_nombre", "detalle": variable})
        except Exception as error:
            load_rows.append({
                "dataset": name,
                "archivo": str(path),
                "filas": np.nan,
                "columnas": np.nan,
                "target_detectado": None,
                "carga_correcta": False,
                "incidencias": str(error),
            })
            issue_rows.append({"dataset": name, "tipo": "error_carga", "detalle": str(error)})
    contexto.raw_datasets = datasets
    registrar_tabla(contexto, "raw_load_summary.csv", pd.DataFrame(load_rows))
    registrar_tabla(contexto, "raw_columns_summary.csv", pd.DataFrame(columns_rows))
    registrar_tabla(contexto, "raw_initial_issues.csv", pd.DataFrame(issue_rows))
    return contexto.tables["raw_load_summary.csv"]


def auditar_estructura(contexto):
    structure_rows, role_tables, dtype_rows = [], [], []
    for dataset, objeto in contexto.raw_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        roles = classify_columns(datos, target)
        roles.insert(0, "dataset", dataset)
        role_tables.append(roles)
        features = get_feature_columns(datos, target)
        structure_rows.append({
            "dataset": dataset,
            "filas": len(datos),
            "columnas_totales": datos.shape[1],
            "features": len(features),
            "target": target,
            "numéricas": int(roles["role"].isin(["numérica", "binaria_numérica"]).sum()),
            "categóricas": int(roles["role"].isin(["categórica", "binaria_categórica"]).sum()),
            "binarias": int(roles["role"].str.contains("binaria").sum()),
            "posibles_ids": int((roles["role"] == "posible_id").sum()),
            "ratio_features_muestras": len(features) / len(datos) if len(datos) else np.nan,
        })
        for dtype, count in datos.dtypes.astype(str).value_counts().items():
            dtype_rows.append({"dataset": dataset, "dtype": dtype, "n_columnas": int(count)})
    registrar_tabla(contexto, "raw_structure_summary.csv", pd.DataFrame(structure_rows))
    roles = pd.concat(role_tables, ignore_index=True) if role_tables else pd.DataFrame()
    registrar_tabla(contexto, "raw_variable_roles.csv", roles)
    registrar_tabla(contexto, "raw_dtype_summary.csv", pd.DataFrame(dtype_rows))
    return contexto.tables["raw_structure_summary.csv"]


def auditar_calidad(contexto):
    missing_rows, duplicate_rows, constant_rows, lowvar_rows, quality_rows = [], [], [], [], []
    for dataset, objeto in contexto.raw_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        duplicados = int(datos.duplicated().sum())
        duplicate_rows.append({"dataset": dataset, "duplicados": duplicados, "duplicados_pct": duplicados / len(datos) if len(datos) else np.nan})
        n_missing_cols = n_constant = n_lowvar = 0
        for variable in datos.columns:
            serie = datos[variable]
            missing = int(serie.isna().sum())
            if missing > 0:
                n_missing_cols += 1
            missing_rows.append({"dataset": dataset, "variable": variable, "missing": missing, "missing_pct": float(serie.isna().mean())})
            if variable == target:
                continue
            n_unique = serie.nunique(dropna=True)
            if n_unique <= 1:
                n_constant += 1
                constant_rows.append({"dataset": dataset, "variable": variable, "n_unique": int(n_unique)})
            mode_pct = serie.value_counts(dropna=True, normalize=True).iloc[0] if serie.notna().any() else np.nan
            unique_ratio = n_unique / len(serie) if len(serie) else np.nan
            if mode_pct >= DOMINANT_MODE_THRESHOLD or unique_ratio <= LOW_UNIQUE_RATIO:
                n_lowvar += 1
                lowvar_rows.append({
                    "dataset": dataset,
                    "variable": variable,
                    "n_unique": int(n_unique),
                    "unique_ratio": unique_ratio,
                    "mode_pct": mode_pct,
                })
        quality_rows.append({
            "dataset": dataset,
            "n_missing_cols": n_missing_cols,
            "total_missing": int(datos.isna().sum().sum()),
            "duplicados": duplicados,
            "constantes": n_constant,
            "baja_varianza_o_dominancia": n_lowvar,
        })
    registrar_tabla(contexto, "raw_missing_values.csv", pd.DataFrame(missing_rows))
    registrar_tabla(contexto, "raw_duplicates_summary.csv", pd.DataFrame(duplicate_rows))
    registrar_tabla(contexto, "raw_constant_features.csv", pd.DataFrame(constant_rows))
    registrar_tabla(contexto, "raw_low_variance_features.csv", pd.DataFrame(lowvar_rows))
    registrar_tabla(contexto, "raw_quality_summary.csv", pd.DataFrame(quality_rows))
    return contexto.tables["raw_quality_summary.csv"]


def analizar_target(contexto):
    target_rows, balance_rows, metric_rows = [], [], []
    for dataset, objeto in contexto.raw_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        if target is None or target not in datos.columns:
            balance_rows.append({"dataset": dataset, "target": target, "estado": "sin_target"})
            continue
        counts = datos[target].value_counts(dropna=False)
        total = counts.sum()
        for clase, cantidad in counts.items():
            target_rows.append({"dataset": dataset, "target": target, "clase": str(clase), "n": int(cantidad), "pct": float(cantidad / total)})
        ratio = float(counts.max() / counts.min()) if counts.min() > 0 else np.inf
        balance_rows.append({
            "dataset": dataset,
            "target": target,
            "estado": "ok",
            "n_clases": int(counts.size),
            "clase_minoritaria_n": int(counts.min()),
            "ratio_mayoritaria_minoritaria": ratio,
        })
        metric_rows.append({
            "dataset": dataset,
            "recomendacion_metricas": "balanced_accuracy, macro_f1, recall por clase" if ratio >= 1.5 else "accuracy + macro_f1 + matriz de confusión",
            "split_recomendado": "estratificado" if counts.min() >= 2 else "revisar clase mínima",
        })
    registrar_tabla(contexto, "raw_target_distribution.csv", pd.DataFrame(target_rows))
    registrar_tabla(contexto, "raw_target_balance_summary.csv", pd.DataFrame(balance_rows))
    registrar_tabla(contexto, "raw_metric_recommendations.csv", pd.DataFrame(metric_rows))
    return contexto.tables["raw_target_balance_summary.csv"]


def crear_muestras_visuales(contexto):
    sampled_datasets, sampling_rows, sample_target_rows = {}, [], []
    for dataset, objeto in contexto.raw_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        usa_muestra = len(datos) > MAX_VIS_ROWS
        if usa_muestra and target is not None and target in datos.columns:
            fracciones = datos[target].value_counts(normalize=True, dropna=False)
            partes = []
            for clase, proporcion in fracciones.items():
                grupo = datos[datos[target].eq(clase)]
                n_grupo = max(1, int(MAX_VIS_ROWS * proporcion))
                partes.append(grupo.sample(min(len(grupo), n_grupo), random_state=RANDOM_STATE))
            muestra = pd.concat(partes, ignore_index=False)
            if len(muestra) > MAX_VIS_ROWS:
                muestra = muestra.sample(MAX_VIS_ROWS, random_state=RANDOM_STATE)
            tipo_muestreo = "estratificado_aproximado"
        elif usa_muestra:
            muestra = datos.sample(MAX_VIS_ROWS, random_state=RANDOM_STATE)
            tipo_muestreo = "aleatorio_simple"
        else:
            muestra = datos.copy()
            tipo_muestreo = "sin_muestreo"
        sampled_datasets[dataset] = {"df": muestra, "target": target, "sampled": usa_muestra}
        sampling_rows.append({
            "dataset": dataset,
            "usa_muestra": usa_muestra,
            "n_completo": len(datos),
            "n_muestra": len(muestra),
            "tipo_muestreo": tipo_muestreo,
        })
        if target is not None and target in datos.columns:
            completo = datos[target].value_counts(normalize=True, dropna=False)
            muestra_pct = muestra[target].value_counts(normalize=True, dropna=False)
            for clase in sorted(set(completo.index).union(set(muestra_pct.index)), key=lambda item: str(item)):
                sample_target_rows.append({
                    "dataset": dataset,
                    "clase": str(clase),
                    "pct_completo": float(completo.get(clase, 0)),
                    "pct_muestra": float(muestra_pct.get(clase, 0)),
                    "dif_abs": abs(float(completo.get(clase, 0) - muestra_pct.get(clase, 0))),
                })
    contexto.sampled_datasets = sampled_datasets
    registrar_tabla(contexto, "raw_sampling_strategy.csv", pd.DataFrame(sampling_rows))
    registrar_tabla(contexto, "raw_sample_vs_full_target.csv", pd.DataFrame(sample_target_rows))
    return contexto.tables["raw_sampling_strategy.csv"]


def analizar_univariante(contexto):
    numeric_rows, shape_rows, outlier_rows = [], [], []
    for dataset, objeto in contexto.raw_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        for variable in numeric_features(datos, target):
            valores = pd.to_numeric(datos[variable], errors="coerce")
            desc = valores.describe(percentiles=[0.25, 0.5, 0.75]).to_dict()
            outlier_rate = robust_outlier_rate(valores)
            numeric_rows.append({
                "dataset": dataset,
                "variable": variable,
                "count": desc.get("count"),
                "mean": desc.get("mean"),
                "std": desc.get("std"),
                "min": desc.get("min"),
                "q25": desc.get("25%"),
                "median": desc.get("50%"),
                "q75": desc.get("75%"),
                "max": desc.get("max"),
            })
            shape_rows.append({
                "dataset": dataset,
                "variable": variable,
                "skewness": float(valores.skew(skipna=True)),
                "kurtosis": float(valores.kurt(skipna=True)),
                "outlier_rate_iqr": outlier_rate,
                "missing_pct": float(valores.isna().mean()),
            })
            outlier_rows.append({"dataset": dataset, "variable": variable, "outlier_rate_iqr": outlier_rate})
    distribution = pd.DataFrame(shape_rows)
    registrar_tabla(contexto, "raw_numeric_descriptive_stats.csv", pd.DataFrame(numeric_rows))
    registrar_tabla(contexto, "raw_distribution_shape.csv", distribution)
    registrar_tabla(contexto, "raw_outlier_summary.csv", pd.DataFrame(outlier_rows))
    resumen = distribution.groupby("dataset").agg(
        outlier_rate_media=("outlier_rate_iqr", "mean"),
        skew_abs_media=("skewness", lambda serie: np.nanmean(np.abs(serie))),
        variables_numéricas=("variable", "count"),
    ).reset_index() if not distribution.empty else pd.DataFrame()
    registrar_tabla(contexto, "raw_univariate_dataset_summary.csv", resumen)
    return distribution


def analizar_normalidad(contexto):
    normality_rows = []
    try:
        from scipy.stats import normaltest, shapiro
        scipy_ok = True
    except Exception:
        scipy_ok = False
    for dataset, objeto in contexto.sampled_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        for variable in numeric_features(datos, target):
            valores = pd.to_numeric(datos[variable], errors="coerce").dropna()
            if not scipy_ok or len(valores) < 8:
                normality_rows.append({"dataset": dataset, "variable": variable, "test": "no_ejecutado", "p_value": np.nan, "rechaza_0_05": np.nan, "n": len(valores)})
                continue
            muestra = valores.sample(min(len(valores), 5000), random_state=RANDOM_STATE) if len(valores) > 5000 else valores
            stat, p_value = normaltest(muestra) if len(muestra) >= 20 else shapiro(muestra)
            normality_rows.append({
                "dataset": dataset,
                "variable": variable,
                "test": "dagostino_k2" if len(muestra) >= 20 else "shapiro",
                "p_value": float(p_value),
                "rechaza_0_05": bool(p_value < 0.05),
                "n": len(valores),
            })
    tests = pd.DataFrame(normality_rows)
    summary = tests.groupby("dataset").agg(
        variables_testadas=("variable", "count"),
        pct_rechaza_normalidad=("rechaza_0_05", "mean"),
    ).reset_index() if not tests.empty else pd.DataFrame()
    registrar_tabla(contexto, "raw_normality_tests.csv", tests)
    registrar_tabla(contexto, "raw_normality_summary.csv", summary)
    return summary


def analizar_asociacion_target(contexto):
    assoc_rows, mi_rows = [], []
    try:
        from scipy.stats import chi2_contingency, kruskal, mannwhitneyu
        scipy_ok = True
    except Exception:
        scipy_ok = False
    try:
        from sklearn.feature_selection import mutual_info_classif
        from sklearn.preprocessing import OrdinalEncoder
        sklearn_ok = True
    except Exception:
        sklearn_ok = False
    for dataset, objeto in contexto.raw_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        if target is None or target not in datos.columns:
            continue
        target_values = datos[target]
        clases = target_values.dropna().unique()
        if len(clases) < 2:
            continue
        features = get_feature_columns(datos, target)
        for variable in features:
            assoc_rows.append(_calcular_asociacion_variable(datos, target_values, clases, variable, dataset, target, scipy_ok))
        if sklearn_ok and features:
            mi_rows.extend(_calcular_informacion_mutua(datos, target_values, features, dataset, mutual_info_classif, OrdinalEncoder))
    tests = pd.DataFrame(assoc_rows)
    if not tests.empty:
        for column, default_value in {
            "effect_size_name": "no_calculado",
            "effect_size": np.nan,
            "p_value": np.nan,
        }.items():
            if column not in tests.columns:
                tests[column] = default_value
            else:
                tests[column] = tests[column].fillna(default_value) if column == "effect_size_name" else tests[column]
        tests["p_value_fdr"] = tests.groupby("dataset")["p_value"].transform(benjamini_hochberg)
    effects = tests[["dataset", "variable", "effect_size", "effect_size_name", "p_value", "p_value_fdr"]].copy() if not tests.empty else pd.DataFrame()
    mi_scores = pd.DataFrame(mi_rows)
    candidates = tests[(tests["p_value_fdr"] < 0.05) & (tests["effect_size"].abs() > 0.05)].copy() if not tests.empty else pd.DataFrame()
    registrar_tabla(contexto, "raw_feature_target_tests.csv", tests)
    registrar_tabla(contexto, "raw_feature_target_effect_sizes.csv", effects)
    registrar_tabla(contexto, "raw_feature_target_mi_scores.csv", mi_scores)
    registrar_tabla(contexto, "raw_mutual_information_scores.csv", mi_scores.copy())
    registrar_tabla(contexto, "raw_candidate_features_univariate.csv", candidates)
    return tests


def _calcular_asociacion_variable(datos, target_values, clases, variable, dataset, target, scipy_ok):
    serie = datos[variable]
    row = {"dataset": dataset, "variable": variable, "target": target, "n": int(serie.notna().sum())}
    try:
        if scipy_ok:
            from scipy.stats import chi2_contingency, kruskal, mannwhitneyu
        if pd.api.types.is_numeric_dtype(serie):
            row["variable_type"] = "numérica"
            grupos = [pd.to_numeric(serie[target_values == clase], errors="coerce").dropna() for clase in clases]
            if scipy_ok and len(clases) == 2:
                stat, p_value = mannwhitneyu(grupos[0], grupos[1], alternative="two-sided")
                effect = cliffs_delta(grupos[0], grupos[1])
                test, effect_name = "mann_whitney_u", "cliffs_delta"
            elif scipy_ok:
                stat, p_value = kruskal(*grupos)
                n_total, n_clases = sum(len(grupo) for grupo in grupos), len(grupos)
                effect = max(0, (stat - n_clases + 1) / (n_total - n_clases)) if n_total > n_clases else np.nan
                test, effect_name = "kruskal_wallis", "epsilon_squared"
            else:
                stat = p_value = effect = np.nan
                test, effect_name = "no_scipy", "no_calculado"
        else:
            row["variable_type"] = "categórica"
            tabla = pd.crosstab(serie.fillna("__MISSING__"), target_values.fillna("__MISSING__"))
            if scipy_ok:
                stat, p_value, _, _ = chi2_contingency(tabla)
                effect = cramers_v(tabla)
                test, effect_name = "chi2", "cramers_v"
            else:
                stat = p_value = effect = np.nan
                test, effect_name = "no_scipy", "no_calculado"
        row.update({"test": test, "statistic": float(stat) if pd.notna(stat) else np.nan, "p_value": float(p_value) if pd.notna(p_value) else np.nan, "effect_size": effect, "effect_size_name": effect_name})
    except Exception as error:
        row.update({"test": "error", "p_value": np.nan, "effect_size": np.nan, "error": str(error)})
    return row


def _calcular_informacion_mutua(datos, target_values, features, dataset, mutual_info_classif, OrdinalEncoder):
    try:
        matriz = datos[features].copy()
        for variable in features:
            if pd.api.types.is_numeric_dtype(matriz[variable]):
                matriz[variable] = pd.to_numeric(matriz[variable], errors="coerce").fillna(matriz[variable].median())
            else:
                matriz[variable] = matriz[variable].astype("object").fillna("__MISSING__")
                matriz[[variable]] = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1).fit_transform(matriz[[variable]])
        target_encoded = OrdinalEncoder().fit_transform(target_values.astype("object").fillna("__MISSING__").to_frame()).ravel()
        scores = mutual_info_classif(matriz, target_encoded, discrete_features="auto", random_state=RANDOM_STATE)
        return [{"dataset": dataset, "variable": variable, "mutual_information": float(score)} for variable, score in zip(features, scores)]
    except Exception as error:
        return [{"dataset": dataset, "variable": "__ERROR__", "mutual_information": np.nan, "error": str(error)}]


def analizar_fdr_y_efectos(contexto):
    tests = contexto.tables["raw_feature_target_tests.csv"]
    corrected = tests.copy()
    summary = corrected.groupby("dataset").agg(
        variables_testeadas=("variable", "count"),
        significativas_sin_corregir=("p_value", lambda serie: int((serie < 0.05).sum())),
        significativas_fdr=("p_value_fdr", lambda serie: int((serie < 0.05).sum())),
    ).reset_index() if not corrected.empty else pd.DataFrame()
    if not summary.empty:
        summary["reduccion"] = summary["significativas_sin_corregir"] - summary["significativas_fdr"]
    effects = contexto.tables["raw_feature_target_effect_sizes.csv"].copy()
    if not effects.empty:
        effects["magnitud_exploratoria"] = effects["effect_size"].apply(clasificar_magnitud_efecto)
        strong = effects[(effects["p_value_fdr"] < 0.05) & (effects["magnitud_exploratoria"].isin(["medio", "grande"]))].copy()
        interpretation = effects.groupby(["dataset", "magnitud_exploratoria"]).size().reset_index(name="n_variables")
    else:
        strong, interpretation = pd.DataFrame(), pd.DataFrame()
    registrar_tabla(contexto, "raw_fdr_corrected_tests.csv", corrected)
    registrar_tabla(contexto, "raw_fdr_summary.csv", summary)
    registrar_tabla(contexto, "raw_effect_sizes.csv", effects)
    registrar_tabla(contexto, "raw_effect_size_interpretation.csv", interpretation)
    registrar_tabla(contexto, "raw_strong_effect_features.csv", strong)
    return summary


def clasificar_magnitud_efecto(value):
    if pd.isna(value):
        return "no_calculado"
    magnitude = abs(value)
    if magnitude < 0.05:
        return "muy_pequeño"
    if magnitude < 0.147:
        return "pequeño"
    if magnitude < 0.33:
        return "medio"
    return "grande"


def analizar_redundancia(contexto):
    corr_rows, high_rows, red_rows = [], [], []
    for dataset, objeto in contexto.raw_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        columnas = numeric_features(datos, target)
        if len(columnas) < 2:
            red_rows.append({"dataset": dataset, "n_numeric_features": len(columnas), "high_corr_pairs": 0, "corr_threshold": CORR_THRESHOLD})
            continue
        corr = datos[columnas].corr(method="spearman").abs()
        high_count = 0
        for pos, variable_a in enumerate(columnas):
            for variable_b in columnas[pos + 1:]:
                value = corr.loc[variable_a, variable_b]
                corr_rows.append({"dataset": dataset, "variable_a": variable_a, "variable_b": variable_b, "spearman_abs": float(value)})
                if pd.notna(value) and value >= CORR_THRESHOLD:
                    high_count += 1
                    high_rows.append({"dataset": dataset, "variable_a": variable_a, "variable_b": variable_b, "spearman_abs": float(value)})
        red_rows.append({"dataset": dataset, "n_numeric_features": len(columnas), "high_corr_pairs": high_count, "corr_threshold": CORR_THRESHOLD})
    registrar_tabla(contexto, "raw_correlation_matrix_long.csv", pd.DataFrame(corr_rows))
    registrar_tabla(contexto, "raw_high_correlation_pairs.csv", pd.DataFrame(high_rows))
    registrar_tabla(contexto, "raw_redundancy_summary.csv", pd.DataFrame(red_rows))
    return contexto.tables["raw_redundancy_summary.csv"]


def analizar_dimensionalidad_y_pca(contexto):
    strong = contexto.tables["raw_strong_effect_features.csv"]
    structure = contexto.tables["raw_structure_summary.csv"]
    strong_counts = strong.groupby("dataset").size().rename("variables_efecto_fuerte").reset_index() if not strong.empty else pd.DataFrame(columns=["dataset", "variables_efecto_fuerte"])
    base = structure.merge(strong_counts, on="dataset", how="left")
    base["variables_efecto_fuerte"] = base["variables_efecto_fuerte"].fillna(0).astype(int)
    base["riesgo_dimensionalidad"] = np.select(
        [base["ratio_features_muestras"] >= 1, base["ratio_features_muestras"] >= 0.1],
        ["alto", "medio"],
        default="bajo",
    )
    base["posible_ruido_univariante"] = base["features"] - base["variables_efecto_fuerte"]
    dimensionality = base[["dataset", "filas", "features", "ratio_features_muestras", "variables_efecto_fuerte", "posible_ruido_univariante", "riesgo_dimensionalidad"]]
    registrar_tabla(contexto, "raw_dimensionality_summary.csv", dimensionality)
    registrar_tabla(contexto, "raw_noise_risk_summary.csv", dimensionality.copy())
    registrar_tabla(contexto, "raw_pca_variance_summary.csv", calcular_pca_resumen(contexto))
    return dimensionality


def calcular_pca_resumen(contexto):
    rows = []
    try:
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
    except Exception:
        return pd.DataFrame(rows)
    for dataset, objeto in contexto.sampled_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        columnas = numeric_features(datos, target)
        if len(columnas) < 2 or len(datos) < 3:
            continue
        matriz = datos[columnas].apply(pd.to_numeric, errors="coerce")
        matriz = matriz.fillna(matriz.median(numeric_only=True))
        matriz = matriz.loc[:, matriz.std(numeric_only=True) > 0]
        if matriz.shape[1] < 2:
            continue
        escalada = StandardScaler().fit_transform(matriz)
        n_components = min(10, escalada.shape[1], escalada.shape[0])
        pca = PCA(n_components=n_components, random_state=RANDOM_STATE)
        pca.fit_transform(escalada)
        acumulada = np.cumsum(pca.explained_variance_ratio_)
        for component, (ratio, cumulative) in enumerate(zip(pca.explained_variance_ratio_, acumulada), 1):
            rows.append({"dataset": dataset, "component": component, "explained_variance_ratio": float(ratio), "cumulative": float(cumulative)})
    return pd.DataFrame(rows)


def detectar_riesgos_espurios(contexto):
    rows = []
    tests = contexto.tables["raw_feature_target_tests.csv"]
    for _, result in tests.iterrows():
        motivos = []
        p_value = result.get("p_value", np.nan)
        p_fdr = result.get("p_value_fdr", np.nan)
        effect = result.get("effect_size", np.nan)
        if pd.notna(p_value) and p_value < 0.05 and (pd.isna(p_fdr) or p_fdr >= 0.05):
            motivos.append("significativa_sin_fdr_no_con_fdr")
        if pd.notna(p_fdr) and p_fdr < 0.05 and pd.notna(effect) and abs(effect) < 0.05:
            motivos.append("fdr_significativo_efecto_minimo")
        if pd.notna(effect) and abs(effect) > 0.95:
            motivos.append("efecto_casi_perfecto_revisar_proxy_leakage")
        if motivos:
            rows.append({
                "dataset": result["dataset"],
                "variable": result["variable"],
                "motivos": ";".join(motivos),
                "p_value": p_value,
                "p_value_fdr": p_fdr,
                "effect_size": effect,
                "riesgo": "revisar",
            })
    risks = pd.DataFrame(rows)
    proxy = risks[risks["motivos"].str.contains("proxy|leakage", na=False)].copy() if not risks.empty else pd.DataFrame()
    registrar_tabla(contexto, "raw_spurious_risk_features.csv", risks)
    registrar_tabla(contexto, "raw_proxy_leakage_candidates.csv", proxy)
    registrar_tabla(contexto, "raw_univariate_signal_quality.csv", tests.copy())
    return risks


def preclasificar_variables(contexto):
    rows = []
    high_corr = contexto.tables["raw_high_correlation_pairs.csv"]
    risks_table = contexto.tables["raw_spurious_risk_features.csv"]
    tests = contexto.tables["raw_feature_target_tests.csv"]
    for dataset, objeto in contexto.raw_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        high = set()
        if not high_corr.empty:
            subset_high = high_corr[high_corr["dataset"] == dataset]
            high.update(subset_high["variable_a"].tolist())
            high.update(subset_high["variable_b"].tolist())
        risks = set(risks_table[risks_table["dataset"] == dataset]["variable"].tolist()) if not risks_table.empty else set()
        assoc = tests[tests["dataset"] == dataset].set_index("variable") if not tests.empty else pd.DataFrame()
        for variable in get_feature_columns(datos, target):
            categoria, p_fdr, effect = "pendiente_multivariante", np.nan, np.nan
            if not assoc.empty and variable in assoc.index:
                result = assoc.loc[variable]
                result = result.iloc[0] if isinstance(result, pd.DataFrame) else result
                p_fdr = result.get("p_value_fdr", np.nan)
                effect = result.get("effect_size", np.nan)
                if pd.notna(p_fdr) and p_fdr < 0.05 and pd.notna(effect) and abs(effect) >= 0.147:
                    categoria = "candidata_fuerte"
                elif pd.notna(p_fdr) and p_fdr < 0.05:
                    categoria = "candidata_moderada"
                elif pd.notna(effect) and abs(effect) < 0.05:
                    categoria = "posible_ruido_univariante"
            if variable in high and categoria not in ["candidata_fuerte", "sospechosa"]:
                categoria = "redundante_o_correlacionada"
            if variable in risks:
                categoria = "sospechosa"
            rows.append({
                "dataset": dataset,
                "variable": variable,
                "p_value_fdr": p_fdr,
                "effect_size": effect,
                "es_redundante": variable in high,
                "es_sospechosa": variable in risks,
                "categoria_preliminar": categoria,
            })
    preclassification = pd.DataFrame(rows)
    summary = preclassification.groupby(["dataset", "categoria_preliminar"]).size().reset_index(name="n_variables") if not preclassification.empty else pd.DataFrame()
    registrar_tabla(contexto, "raw_feature_preclassification.csv", preclassification)
    registrar_tabla(contexto, "raw_feature_evidence_map.csv", preclassification.copy())
    registrar_tabla(contexto, "raw_dataset_signal_summary.csv", summary)
    return summary


def construir_perfiles_dataset(contexto):
    profile = contexto.tables["raw_structure_summary.csv"].copy()
    candidates = [
        contexto.tables["raw_quality_summary.csv"],
        contexto.tables["raw_target_balance_summary.csv"][["dataset", "n_clases", "ratio_mayoritaria_minoritaria"]],
        contexto.tables["raw_redundancy_summary.csv"][["dataset", "high_corr_pairs"]],
        contexto.tables["raw_dimensionality_summary.csv"][["dataset", "riesgo_dimensionalidad", "variables_efecto_fuerte", "posible_ruido_univariante"]],
    ]
    for right in candidates:
        if not right.empty:
            profile = profile.merge(right, on="dataset", how="left")
    risks = contexto.tables["raw_spurious_risk_features.csv"]
    if not risks.empty:
        profile = profile.merge(risks.groupby("dataset").size().rename("variables_sospechosas").reset_index(), on="dataset", how="left")
    else:
        profile["variables_sospechosas"] = 0
    profile["variables_sospechosas"] = profile["variables_sospechosas"].fillna(0).astype(int)
    registrar_tabla(contexto, "raw_dataset_profiles.csv", profile)
    return profile


def ejecutar_analisis_fase1(contexto):
    cargar_datasets_crudos(contexto)
    auditar_estructura(contexto)
    auditar_calidad(contexto)
    analizar_target(contexto)
    crear_muestras_visuales(contexto)
    analizar_univariante(contexto)
    analizar_normalidad(contexto)
    analizar_asociacion_target(contexto)
    analizar_fdr_y_efectos(contexto)
    analizar_redundancia(contexto)
    analizar_dimensionalidad_y_pca(contexto)
    detectar_riesgos_espurios(contexto)
    preclasificar_variables(contexto)
    construir_perfiles_dataset(contexto)
    return contexto


def generar_todas_las_figuras(contexto, mostrar=True):
    contexto.figure_paths = []
    plot_carga(contexto, mostrar)
    plot_estructura(contexto, mostrar)
    plot_calidad(contexto, mostrar)
    plot_target(contexto, mostrar)
    plot_muestreo(contexto, mostrar)
    plot_univariante(contexto, mostrar)
    plot_normalidad(contexto, mostrar)
    plot_asociacion(contexto, mostrar)
    plot_fdr_y_efectos(contexto, mostrar)
    plot_redundancia(contexto, mostrar)
    plot_dimensionalidad(contexto, mostrar)
    plot_pca(contexto, mostrar)
    plot_riesgos(contexto, mostrar)
    plot_preclasificacion(contexto, mostrar)
    plot_perfil_ead(contexto, mostrar)
    return contexto.figure_paths


def cerrar_figura(mostrar):
    if mostrar:
        plt.show()
    else:
        plt.close()


def plot_carga(contexto, mostrar=True):
    data = ordenar_datasets(contexto.tables["raw_load_summary.csv"])
    data = data[data["carga_correcta"].eq(True)]
    if data.empty:
        return None
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    
    y = np.arange(len(data))
    
    axes[0].barh(y, data["filas"], height=0.55, color=TFG_PALETTE.primary)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(data["dataset"], fontsize=9)
    axes[0].set_xscale("log")
    axes[0].set_xlabel("Número de muestras (escala log)")
    
    axes[1].barh(y, data["columnas"], height=0.55, color=TFG_PALETTE.secondary)
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Número de features (escala log)")
    
    etiqueta_barras_horizontales(axes[0], data["filas"], "{:.0f}", 0.03)
    etiqueta_barras_horizontales(axes[1], data["columnas"], "{:.0f}", 0.03)

    add_editorial_text(axes[0], "Muestras leídas por dataset", "Escala logarítmica para comparar tamaños muy distintos", palette=TFG_PALETTE)
    add_editorial_text(axes[1], "Columnas leídas por dataset", "La figura valida escala inicial, no calidad analítica", palette=TFG_PALETTE)
    
    for ax in axes:
        apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
        
    fig.suptitle("Carga y escala inicial de datasets", y=1.08, fontsize=14, fontweight="semibold", color=TFG_PALETTE.text)
    
    registrar_figura(contexto, Path("01_01_carga") / "raw_load_rows_columns.png")
    cerrar_figura(mostrar)


def plot_estructura(contexto, mostrar=True):
    data = ordenar_datasets(contexto.tables["raw_structure_summary.csv"])
    
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    
    axes[0].scatter(data["filas"], data["features"], s=150, color=TFG_PALETTE.primary, 
                    edgecolor=TFG_PALETTE.background, linewidth=1.5, alpha=0.9)
    for _, row in data.iterrows():
        axes[0].annotate(row["dataset"], (row["filas"], row["features"]), 
                         xytext=(7, 7), textcoords="offset points", fontsize=9, 
                         color=TFG_PALETTE.text, fontweight="semibold")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("Número de muestras (filas)")
    axes[0].set_ylabel("Número de variables (columnas)")
    add_editorial_text(axes[0], "Escala estructural de datasets", 
                       "Madelon es alta dimensión; Customer Churn es gran volumen", palette=TFG_PALETTE)
    apply_editorial_axes(axes[0], palette=TFG_PALETTE, grid_axis="both", show_grid=True)
    
    colors = [TFG_PALETTE.negative if r >= 0.1 else TFG_PALETTE.secondary for r in data["ratio_features_muestras"]]
    axes[1].barh(data["dataset"], data["ratio_features_muestras"], color=colors, height=0.55)
    axes[1].axvline(0.1, color=TFG_PALETTE.accent, linestyle="--", linewidth=1.2, label="Umbral de riesgo medio (0.1)")
    axes[1].set_xlabel("Ratio variables / muestras")
    axes[1].legend(loc="lower right", frameon=False)
    add_editorial_text(axes[1], "Riesgo dimensional inicial", 
                       "Madelon supera críticamente el umbral seguro", palette=TFG_PALETTE)
    apply_editorial_axes(axes[1], palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    
    etiqueta_barras_horizontales(axes[1], data["ratio_features_muestras"], "{:.3f}", 0.02)
    
    fig.suptitle("Auditoría estructural de los datasets", y=1.08, fontsize=14, fontweight="semibold", color=TFG_PALETTE.text)
    
    registrar_figura(contexto, Path("01_02_estructura") / "raw_structure_summary.png")
    cerrar_figura(mostrar)


def plot_calidad(contexto, mostrar=True):
    data = ordenar_datasets(contexto.tables["raw_quality_summary.csv"])
    
    fig, ax = plt.subplots(figsize=(9, 4))
    y = np.arange(len(data))
    
    ax.hlines(y, 0, data["baja_varianza_o_dominancia"], color=TFG_PALETTE.spine, linewidth=1.8, zorder=1)
    ax.scatter(data["baja_varianza_o_dominancia"], y, color=TFG_PALETTE.primary, s=120, zorder=2, edgecolor=TFG_PALETTE.background)
    
    ax.set_yticks(y)
    ax.set_yticklabels(data["dataset"], fontsize=9)
    ax.set_xlabel("Número de variables con baja variabilidad o dominancia (umbral 98%)")
    
    for idx, val in enumerate(data["baja_varianza_o_dominancia"]):
        ax.text(val + 0.5, idx, f"{val} vars", va="center", ha="left", fontsize=9, fontweight="semibold", color=TFG_PALETTE.text)
        
    add_editorial_text(ax, "Calidad del dato crudo: dominancia y baja variabilidad", 
                       "Nota: Nulos, duplicados y constantes son cero en todos los datasets", palette=TFG_PALETTE)
    apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    
    ax.set_xlim(0, max(data["baja_varianza_o_dominancia"]) + 3)
    
    registrar_figura(contexto, Path("01_03_calidad") / "raw_quality_issues_summary.png")
    cerrar_figura(mostrar)


def plot_target(contexto, mostrar=True):
    target = contexto.tables["raw_target_distribution.csv"]
    
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw={"width_ratios": [1, 1.2]})
    
    bin_datasets = ["madelon", "customer_churn", "breast_cancer_wisconsin"]
    y_bin = np.arange(len(bin_datasets))
    
    for idx, dname in enumerate(bin_datasets):
        d_data = target[target["dataset"] == dname].sort_values("clase")
        if len(d_data) == 2:
            c0_name, c0_n, c0_pct = d_data.iloc[0]["clase"], d_data.iloc[0]["n"], d_data.iloc[0]["pct"]
            c1_name, c1_n, c1_pct = d_data.iloc[1]["clase"], d_data.iloc[1]["n"], d_data.iloc[1]["pct"]
            
            axes[0].barh(idx, c0_pct, height=0.45, color=TFG_PALETTE.secondary, label=str(c0_name) if idx == 0 else "")
            axes[0].barh(idx, c1_pct, left=c0_pct, height=0.45, color=TFG_PALETTE.primary, label=str(c1_name) if idx == 0 else "")
            
            axes[0].text(c0_pct / 2, idx, f"{c0_name}\n({c0_pct:.1%})", va="center", ha="center", color="#FFFFFF", fontsize=8, fontweight="bold")
            axes[0].text(c0_pct + c1_pct / 2, idx, f"{c1_name}\n({c1_pct:.1%})", va="center", ha="center", color="#FFFFFF", fontsize=8, fontweight="bold")
            
    axes[0].set_yticks(y_bin)
    axes[0].set_yticklabels(bin_datasets, fontsize=9)
    axes[0].set_xlim(0, 1.0)
    axes[0].set_xlabel("Proporción relativa")
    add_editorial_text(axes[0], "Datasets binarios", "Distribuciones de clases equilibradas o moderadas", palette=TFG_PALETTE)
    apply_editorial_axes(axes[0], palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    
    olive_data = target[target["dataset"] == "olive_oil"].sort_values("n")
    y_olive = np.arange(len(olive_data))
    
    colors_olive = [TFG_PALETTE.secondary if n < 50 else TFG_PALETTE.primary for n in olive_data["n"]]
    axes[1].barh(y_olive, olive_data["n"], color=colors_olive, height=0.55)
    axes[1].set_yticks(y_olive)
    axes[1].set_yticklabels(olive_data["clase"], fontsize=9)
    axes[1].set_xlabel("Número de observaciones")
    
    max_n = olive_data["n"].max()
    for idx, (_, row) in enumerate(olive_data.iterrows()):
        axes[1].text(row["n"] + max_n * 0.02, idx, f"{row['n']} ({row['pct']:.1%})", va="center", ha="left", fontsize=8, color=TFG_PALETTE.text)
        
    add_editorial_text(axes[1], "Dataset multiclase: olive_oil", "Desbalance relevante y cardinalidad de clases (9 categorías)", palette=TFG_PALETTE)
    apply_editorial_axes(axes[1], palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    axes[1].set_xlim(0, max_n * 1.25)
    
    fig.suptitle("Distribución de clases de la variable target", y=1.08, fontsize=14, fontweight="semibold", color=TFG_PALETTE.text)
    registrar_figura(contexto, Path("01_04_target") / "raw_target_distribution_panel.png")
    cerrar_figura(mostrar)
    
    balance = ordenar_datasets(contexto.tables["raw_target_balance_summary.csv"])
    balance = balance[balance["estado"].eq("ok")]
    fig, axis = plt.subplots(figsize=(8.5, 4))
    
    colors = [TFG_PALETTE.negative if val >= 1.5 else TFG_PALETTE.primary for val in balance["ratio_mayoritaria_minoritaria"]]
    axis.barh(balance["dataset"], balance["ratio_mayoritaria_minoritaria"], color=colors, height=0.5)
    
    axis.axvline(1.5, color=TFG_PALETTE.accent, linestyle="--", linewidth=1.2, label="Umbral de alerta de desbalance (1.5)")
    axis.set_xlabel("Ratio clase mayoritaria / minoritaria")
    add_editorial_text(axis, "Ratio de desbalance del target", "olive_oil exige tratamiento especial en validación y métricas", palette=TFG_PALETTE)
    apply_editorial_axes(axis, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    axis.legend(loc="lower right", frameon=False)
    
    etiqueta_barras_horizontales(axis, balance["ratio_mayoritaria_minoritaria"], "{:.2f}", 0.015)
    
    y_pos_olive = list(balance["dataset"]).index("olive_oil")
    axis.text(8.24 - 0.5, y_pos_olive, "Crítico", color="#FFFFFF", fontsize=8, fontweight="bold", va="center", ha="right")
    
    registrar_figura(contexto, Path("01_04_target") / "raw_target_balance_ratio.png")
    cerrar_figura(mostrar)


def plot_muestreo(contexto, mostrar=True):
    strategy = contexto.tables["raw_sampling_strategy.csv"]
    sample_names = strategy[strategy["usa_muestra"].eq(True)]["dataset"].tolist()
    for dataset in sample_names:
        data = contexto.tables["raw_sample_vs_full_target.csv"]
        data = data[data["dataset"].eq(dataset)].sort_values("clase")
        if data.empty:
            continue
            
        fig, ax = plt.subplots(figsize=(9, 3.5))
        
        c0_row = data.iloc[0]
        c1_row = data.iloc[1]
        
        ax.barh(1, c0_row["pct_completo"], height=0.4, color=TFG_PALETTE.secondary, label=f"Clase {c0_row['clase']}")
        ax.barh(1, c1_row["pct_completo"], left=c0_row["pct_completo"], height=0.4, color=TFG_PALETTE.primary, label=f"Clase {c1_row['clase']}")
        
        ax.barh(0, c0_row["pct_muestra"], height=0.4, color=TFG_PALETTE.secondary)
        ax.barh(0, c1_row["pct_muestra"], left=c0_row["pct_muestra"], height=0.4, color=TFG_PALETTE.primary)
        
        ax.set_yticks([1, 0])
        strategy_row = strategy[strategy["dataset"].eq(dataset)].iloc[0]
        n_completo = int(strategy_row["n_completo"])
        n_muestra = int(strategy_row["n_muestra"])
        ax.set_yticklabels([f"Datos completos\n(n={formato_entero_es(n_completo)})", f"Muestra visual\n(n={formato_entero_es(n_muestra)})"], fontsize=9)
        ax.set_xlim(0, 1.0)
        ax.set_xlabel("Proporción relativa")
        
        ax.text(c0_row["pct_completo"]/2, 1, f"{c0_row['pct_completo']:.2%}", va="center", ha="center", color="#FFFFFF", fontsize=9, fontweight="bold")
        ax.text(c0_row["pct_completo"] + c1_row["pct_completo"]/2, 1, f"{c1_row['pct_completo']:.2%}", va="center", ha="center", color="#FFFFFF", fontsize=9, fontweight="bold")
        
        ax.text(c0_row["pct_muestra"]/2, 0, f"{c0_row['pct_muestra']:.2%}", va="center", ha="center", color="#FFFFFF", fontsize=9, fontweight="bold")
        ax.text(c0_row["pct_muestra"] + c1_row["pct_muestra"]/2, 0, f"{c1_row['pct_muestra']:.2%}", va="center", ha="center", color="#FFFFFF", fontsize=9, fontweight="bold")
        
        max_dif = data["dif_abs"].max()
        ax.text(0.5, -0.5, f"Diferencia máxima entre proporciones: {max_dif:.6f} puntos porcentuales", 
                ha="center", va="top", fontsize=9, color=TFG_PALETTE.muted_text, fontstyle="italic")
        
        add_editorial_text(ax, f"Validación de Muestreo: {dataset}", 
                           "El muestreo estratificado aproximado preserva prácticamente las proporciones del target", palette=TFG_PALETTE)
        apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
        ax.legend(loc="lower right", frameon=False)
        
        registrar_figura(contexto, Path("01_05_muestreo") / f"{dataset}_target_full_vs_sample.png")
        cerrar_figura(mostrar)


def plot_univariante(contexto, mostrar=True):
    import matplotlib.gridspec as gridspec
    shape = contexto.tables["raw_distribution_shape.csv"]
    
    for dataset, objeto in contexto.sampled_datasets.items():
        data_shape = shape[shape["dataset"].eq(dataset)]
        if data_shape.empty:
            continue
            
        top_outliers = data_shape.sort_values("outlier_rate_iqr", ascending=False).head(8)
        if top_outliers.empty:
            continue
            
        top_var = top_outliers.iloc[0]["variable"]
        top_rate = top_outliers.iloc[0]["outlier_rate_iqr"]
        
        fig = plt.figure(figsize=(12.5, 4.8))
        gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1.2], height_ratios=[1.2, 0.4], hspace=0.3, wspace=0.25)
        
        ax_left = fig.add_subplot(gs[:, 0])
        ax_right_hist = fig.add_subplot(gs[0, 1])
        ax_right_box = fig.add_subplot(gs[1, 1], sharex=ax_right_hist)
        
        top_outliers_sorted = top_outliers.sort_values("outlier_rate_iqr")
        ax_left.barh(top_outliers_sorted["variable"], top_outliers_sorted["outlier_rate_iqr"], 
                     color=TFG_PALETTE.secondary, height=0.55)
        
        y_pos_top = len(top_outliers_sorted) - 1
        ax_left.patches[y_pos_top].set_facecolor(TFG_PALETTE.primary)
        
        ax_left.set_xlabel("Tasa de outliers IQR")
        add_editorial_text(ax_left, "Ranking de outliers por variable", 
                           "Variables con mayor presencia de valores atípicos", palette=TFG_PALETTE)
        apply_editorial_axes(ax_left, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
        etiqueta_barras_horizontales(ax_left, top_outliers_sorted["outlier_rate_iqr"], "{:.1%}", 0.02)
        
        values = pd.to_numeric(objeto["df"][top_var], errors="coerce").dropna()
        
        ax_right_hist.hist(values, bins=32, color=TFG_PALETTE.primary, alpha=0.75, edgecolor=TFG_PALETTE.background, density=True)
        if len(values) > 1:
            try:
                from scipy.stats import gaussian_kde
                kde = gaussian_kde(values)
                x_grid = np.linspace(values.min(), values.max(), 200)
                ax_right_hist.plot(x_grid, kde(x_grid), color=TFG_PALETTE.accent, linewidth=1.8, label="Densidad KDE")
            except Exception:
                pass
                
        ax_right_hist.set_ylabel("Densidad")
        add_editorial_text(ax_right_hist, f"Distribución de: {top_var}", 
                           f"Variable con mayor tasa de outliers ({top_rate:.1%})", palette=TFG_PALETTE)
        apply_editorial_axes(ax_right_hist, palette=TFG_PALETTE, grid_axis="y", show_grid=True)
        plt.setp(ax_right_hist.get_xticklabels(), visible=False)
        
        ax_right_box.boxplot(values, vert=False, patch_artist=True, 
                             boxprops={"facecolor": TFG_PALETTE.secondary, "color": TFG_PALETTE.primary, "linewidth": 1.2}, 
                             medianprops={"color": TFG_PALETTE.accent, "linewidth": 2},
                             flierprops={"marker": "o", "markerfacecolor": TFG_PALETTE.negative, "markersize": 3, "markeredgecolor": "none", "alpha": 0.5})
        
        ax_right_box.set_xlabel("Valor de la variable")
        ax_right_box.set_yticks([])
        apply_editorial_axes(ax_right_box, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
        
        fig.suptitle(f"Análisis univariante y outliers — {dataset}", y=1.08, fontsize=14, fontweight="semibold", color=TFG_PALETTE.text)
        
        registrar_figura(contexto, Path("01_06_univariante") / f"{dataset}_selected_numeric_distributions.png")
        cerrar_figura(mostrar)


def plot_normalidad(contexto, mostrar=True):
    data = ordenar_datasets(contexto.tables["raw_normality_summary.csv"])
    if data.empty or data["pct_rechaza_normalidad"].isna().all():
        return None
        
    fig, ax = plt.subplots(figsize=(9, 4.2))
    y = np.arange(len(data))
    
    sizes = 80 + data["variables_testadas"] * 2.5
    ax.scatter(data["pct_rechaza_normalidad"], y, s=sizes, color=TFG_PALETTE.primary, 
               edgecolor=TFG_PALETTE.background, linewidth=1.5, alpha=0.95, label="Test de normalidad (p < 0.05)")
    
    ax.set_yticks(y)
    ax.set_yticklabels(data["dataset"], fontsize=9)
    ax.set_xlim(-0.05, 1.1)
    ax.set_xlabel("Proporción de variables que rechazan normalidad")
    
    for idx, row in data.iterrows():
        y_pos = list(data["dataset"]).index(row["dataset"])
        ax.text(row["pct_rechaza_normalidad"] - 0.03 if row["pct_rechaza_normalidad"] > 0.5 else row["pct_rechaza_normalidad"] + 0.03, 
                y_pos, f"Evaluadas: {int(row['variables_testadas'])} ({row['pct_rechaza_normalidad']:.1%})", 
                va="center", ha="right" if row["pct_rechaza_normalidad"] > 0.5 else "left", fontsize=8.5, fontweight="semibold", color=TFG_PALETTE.text)
        
    add_editorial_text(ax, "Test de normalidad exploratorio", 
                       "La cautela metodológica se documenta en el notebook; la figura solo resume proporciones", palette=TFG_PALETTE)
    apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    
    registrar_figura(contexto, Path("01_07_normalidad") / "raw_normality_rejection_by_dataset.png")
    cerrar_figura(mostrar)


def plot_asociacion(contexto, mostrar=True):
    tests = contexto.tables["raw_feature_target_tests.csv"]
    for dataset in [name for name in ORDEN_DATASETS if name in set(tests["dataset"])]:
        data = tests[tests["dataset"].eq(dataset)].dropna(subset=["p_value_fdr", "effect_size"]).copy()
        if data.empty:
            continue
            
        data["neg_log10_fdr"] = -np.log10(data["p_value_fdr"].clip(lower=1e-300))
        data["abs_effect"] = data["effect_size"].abs()
        
        if dataset == "olive_oil":
            fig, ax = plt.subplots(figsize=(9, 4.5))
            top_sorted = data.sort_values("abs_effect", ascending=False).head(15).sort_values("abs_effect")
            
            colors = [TFG_PALETTE.negative if val >= 0.999 else TFG_PALETTE.primary for val in top_sorted["abs_effect"]]
            ax.barh(top_sorted["variable"], top_sorted["abs_effect"], color=colors, height=0.55)
            ax.set_xlabel("Tamaño de efecto (Epsilon cuadrado)")
            add_editorial_text(ax, f"Ranking de asociación variable-target: {dataset}", 
                               "Dos variables alcanzan efecto 1.0 y requieren revisión semántica", palette=TFG_PALETTE)
            apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
            etiqueta_barras_horizontales(ax, top_sorted["abs_effect"], "{:.3f}", 0.015)
            
            ax.text(1.0 - 0.03, len(top_sorted)-1, "Posible leakage / proxy perfecto", color="#FFFFFF", 
                    fontsize=8, fontweight="bold", va="center", ha="right")
            
            fig.suptitle(f"Asociación variable-target — {dataset}", y=1.08, fontsize=14, fontweight="semibold", color=TFG_PALETTE.text)
            registrar_figura(contexto, Path("01_08_asociacion_target") / f"{dataset}_volcano_ranking.png")
            cerrar_figura(mostrar)
            continue
            
        fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8), gridspec_kw={"width_ratios": [1.2, 1]})
        
        focus_sig = (data["p_value_fdr"] < 0.05) & (data["abs_effect"] >= 0.1)
        axes[0].scatter(data.loc[~focus_sig, "effect_size"], data.loc[~focus_sig, "neg_log10_fdr"], 
                        color=TFG_PALETTE.neutral, alpha=0.35, s=30, label="Sin significancia/efecto")
        axes[0].scatter(data.loc[focus_sig, "effect_size"], data.loc[focus_sig, "neg_log10_fdr"], 
                        color=TFG_PALETTE.primary, alpha=0.85, s=40, label="Significativo + Efecto relevante")
        
        axes[0].axhline(-np.log10(0.05), linestyle="--", linewidth=1, color=TFG_PALETTE.accent)
        axes[0].set_xlabel("Tamaño de efecto (delta de Cliff / correlación)")
        axes[0].set_ylabel("-log10(FDR)")
        
        add_editorial_text(axes[0], "Gráfico volcano", "Asociación corregida por FDR frente a magnitud del efecto", palette=TFG_PALETTE)
        apply_editorial_axes(axes[0], palette=TFG_PALETTE, grid_axis="both", show_grid=True)
        
        top_3 = data.sort_values("abs_effect", ascending=False).head(3)
        for _, row in top_3.iterrows():
            axes[0].annotate(row["variable"], (row["effect_size"], row["neg_log10_fdr"]), 
                             xytext=(8, 8), textcoords="offset points", fontsize=8.5, fontweight="bold",
                             color=TFG_PALETTE.text, arrowprops=dict(arrowstyle="->", color=TFG_PALETTE.accent, lw=0.8))
            
        top_10 = data.sort_values("abs_effect", ascending=False).head(10).sort_values("abs_effect")
        axes[1].barh(top_10["variable"], top_10["abs_effect"], color=TFG_PALETTE.secondary, height=0.55)
        
        for idx in range(len(top_10) - 3, len(top_10)):
            axes[1].patches[idx].set_facecolor(TFG_PALETTE.primary)
            
        axes[1].set_xlabel("|Tamaño de efecto|")
        add_editorial_text(axes[1], "Ranking de variables", "Top 10 variables con mayor tamaño de efecto", palette=TFG_PALETTE)
        apply_editorial_axes(axes[1], palette=TFG_PALETTE, grid_axis="x", show_grid=True)
        etiqueta_barras_horizontales(axes[1], top_10["abs_effect"], "{:.3f}", 0.015)
        
        fig.suptitle(f"Asociación variable-target — {dataset}", y=1.08, fontsize=14, fontweight="semibold", color=TFG_PALETTE.text)
        registrar_figura(contexto, Path("01_08_asociacion_target") / f"{dataset}_volcano_ranking.png")
        cerrar_figura(mostrar)


def plot_fdr_y_efectos(contexto, mostrar=True):
    fdr = ordenar_datasets(contexto.tables["raw_fdr_summary.csv"])
    
    fig, axis = plt.subplots(figsize=(9, 4.4))
    y = np.arange(len(fdr))
    width = 0.35
    
    axis.barh(y - width / 2, fdr["significativas_sin_corregir"], height=width, 
              color=TFG_PALETTE.secondary, label="Sin corregir (p < 0.05)")
    axis.barh(y + width / 2, fdr["significativas_fdr"], height=width, 
              color=TFG_PALETTE.primary, label="Tras FDR (Benjamini-Hochberg)")
    
    axis.set_yticks(y)
    axis.set_yticklabels(fdr["dataset"], fontsize=9)
    axis.set_xlabel("Variables significativas")
    
    for idx, row in enumerate(fdr.itertuples()):
        axis.text(row.significativas_sin_corregir + 5, idx - width/2, f"{int(row.significativas_sin_corregir)}", 
                  va="center", ha="left", fontsize=8.5, color=TFG_PALETTE.muted_text)
        axis.text(row.significativas_fdr + 5, idx + width/2, f"{int(row.significativas_fdr)}", 
                  va="center", ha="left", fontsize=8.5, color=TFG_PALETTE.text, fontweight="bold")
        
    madelon_idx = list(fdr["dataset"]).index("madelon")
    axis.annotate("Madelon pierde un 65.8%\nde señales espurias\n(38 -> 13)", 
                  xy=(13, madelon_idx + width/2), 
                  xytext=(60, madelon_idx - 0.2),
                  arrowprops=dict(arrowstyle="->", color=TFG_PALETTE.accent, lw=1.2),
                  fontsize=9, fontweight="semibold", color=TFG_PALETTE.text,
                  bbox=dict(boxstyle="round,pad=0.3", fc="#FFF8F0", ec=TFG_PALETTE.accent, alpha=0.9))
                  
    add_editorial_text(axis, "Impacto de la corrección FDR", 
                       "La corrección por tasa de falsos descubrimientos reduce la señal de ruido en madelon", palette=TFG_PALETTE)
    apply_editorial_axes(axis, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    axis.legend(loc="lower right", frameon=False)
    
    registrar_figura(contexto, Path("01_09_fdr") / "raw_fdr_before_after.png")
    cerrar_figura(mostrar)
    
    effects = contexto.tables["raw_effect_sizes.csv"]
    for dataset in [name for name in ORDEN_DATASETS if name in set(effects["dataset"])]:
        data = effects[effects["dataset"].eq(dataset)].dropna(subset=["effect_size"]).copy()
        data["abs_effect"] = data["effect_size"].abs()
        
        top = data.sort_values("abs_effect", ascending=False).head(10).sort_values("abs_effect")
        
        fig, axis = plt.subplots(figsize=(9, 4.2))
        
        axis.hlines(top["variable"], 0, top["abs_effect"], color=TFG_PALETTE.spine, linewidth=1.5)
        axis.scatter(top["abs_effect"], top["variable"], color=TFG_PALETTE.primary, s=80, edgecolor=TFG_PALETTE.background, zorder=3)
        axis.scatter(top.iloc[-1]["abs_effect"], top.iloc[-1]["variable"], color=TFG_PALETTE.accent, s=100, edgecolor=TFG_PALETTE.background, zorder=4)
        
        axis.set_xlabel("|Tamaño de efecto|")
        metric_name = top.iloc[0]["effect_size_name"] if "effect_size_name" in top.columns else "Efecto"
        
        add_editorial_text(axis, f"Tamaños de efecto principales ({metric_name})", 
                           f"Top 10 variables con mayor magnitud de asociación — {dataset}", palette=TFG_PALETTE)
        apply_editorial_axes(axis, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
        
        for idx, (_, row) in enumerate(top.iterrows()):
            axis.text(row["abs_effect"] + 0.01, idx, f"{row['abs_effect']:.3f}", va="center", ha="left", fontsize=8, color=TFG_PALETTE.muted_text)
            
        registrar_figura(contexto, Path("01_10_tamanos_efecto") / f"{dataset}_effect_size_lollipop.png")
        cerrar_figura(mostrar)


def plot_redundancia(contexto, mostrar=True):
    high_corr = contexto.tables["raw_high_correlation_pairs.csv"]
    
    for dataset, objeto in contexto.sampled_datasets.items():
        datos, target = objeto["df"], objeto["target"]
        columnas = numeric_features(datos, target)
        
        if len(columnas) < 2:
            continue
            
        if dataset == "customer_churn":
            pares = correlaciones_spearman_pares(datos, columnas).sort_values("abs_spearman", ascending=False).head(8)
            pares = pares.sort_values("abs_spearman")
            fig, ax = plt.subplots(figsize=(8.8, 4.2))
            ax.hlines(pares["par"], 0, pares["abs_spearman"], color=TFG_PALETTE.spine, linewidth=1.5)
            ax.scatter(pares["abs_spearman"], pares["par"], color=TFG_PALETTE.primary, s=80, edgecolor=TFG_PALETTE.background, zorder=3)
            ax.axvline(CORR_THRESHOLD, color=TFG_PALETTE.accent, linestyle="--", linewidth=1.2, label=f"Umbral {CORR_THRESHOLD}")
            ax.set_xlim(0, max(CORR_THRESHOLD * 1.08, pares["abs_spearman"].max() * 1.15))
            ax.set_xlabel("|Spearman|")
            for pos, row in enumerate(pares.itertuples()):
                ax.text(row.abs_spearman + 0.015, pos, f"{row.abs_spearman:.2f}", va="center", ha="left", fontsize=8.5, color=TFG_PALETTE.muted_text)
            add_editorial_text(ax, "Correlaciones máximas sin superar el umbral — customer_churn",
                               "Top pares por |Spearman|; no se detecta redundancia alta", palette=TFG_PALETTE)
            apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
            ax.legend(loc="lower right", frameon=False)
            registrar_figura(contexto, Path("01_11_redundancia") / f"{dataset}_spearman_heatmap.png")
            cerrar_figura(mostrar)
            continue
            
        elif dataset == "madelon":
            madelon_pairs = high_corr[high_corr["dataset"] == "madelon"]
            vars_involved = list(set(madelon_pairs["variable_a"].tolist() + madelon_pairs["variable_b"].tolist()))
            
            if len(vars_involved) >= 2:
                corr = datos[vars_involved].corr(method="spearman")
                fig, ax = plt.subplots(figsize=(8, 7.5))
                image = heatmap_spearman_triangular(ax, corr, vars_involved, mostrar_etiquetas=True)
                                
                colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
                colorbar.set_label("Coeficiente de Spearman", color=TFG_PALETTE.text)
                colorbar.ax.tick_params(colors=TFG_PALETTE.muted_text)
                
                add_editorial_text(ax, f"Redundancia en {dataset} (vista reducida)", 
                                   "Mapa de calor de variables con correlaciones altas (|Spearman| >= 0.85)", palette=TFG_PALETTE)
                apply_editorial_axes(ax, palette=TFG_PALETTE, show_grid=False)
                registrar_figura(contexto, Path("01_11_redundancia") / f"{dataset}_spearman_heatmap.png")
                cerrar_figura(mostrar)
            else:
                fig, ax = plt.subplots(figsize=(7, 4))
                ax.text(0.5, 0.5, "Correlaciones altas por debajo del umbral", ha="center", va="center")
                ax.set_axis_off()
                registrar_figura(contexto, Path("01_11_redundancia") / f"{dataset}_spearman_heatmap.png")
                cerrar_figura(mostrar)
            continue
            
        else:
            pairs_dataset = high_corr[high_corr["dataset"].eq(dataset)]
            if dataset == "breast_cancer_wisconsin" and not pairs_dataset.empty:
                counts = pd.concat([pairs_dataset["variable_a"], pairs_dataset["variable_b"]]).value_counts()
                columnas = counts.head(18).index.tolist()
            if len(columnas) > MAX_HEATMAP_FEATURES:
                columnas = datos[columnas].var(numeric_only=True).sort_values(ascending=False).head(MAX_HEATMAP_FEATURES).index.tolist()
            corr = datos[columnas].corr(method="spearman")
            
            side = max(6.5, min(10, 0.28 * len(columnas) + 4))
            fig, ax = plt.subplots(figsize=(side, side))
            image = heatmap_spearman_triangular(ax, corr, columnas, mostrar_etiquetas=True)
            
            colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
            colorbar.set_label("Coeficiente de Spearman", color=TFG_PALETTE.text)
            colorbar.ax.tick_params(colors=TFG_PALETTE.muted_text)
            
            subtitle = "Variables más implicadas en pares de alta correlación" if dataset == "breast_cancer_wisconsin" else "Matriz completa de variables numéricas del dataset"
            add_editorial_text(ax, f"Correlación de Spearman — {dataset}", subtitle, palette=TFG_PALETTE)
            apply_editorial_axes(ax, palette=TFG_PALETTE, show_grid=False)
            registrar_figura(contexto, Path("01_11_redundancia") / f"{dataset}_spearman_heatmap.png")
            cerrar_figura(mostrar)
            
    summary = ordenar_datasets(contexto.tables["raw_redundancy_summary.csv"])
    fig, axis = plt.subplots(figsize=(8.5, 4))
    
    colors = [TFG_PALETTE.accent if val > 0 else TFG_PALETTE.secondary for val in summary["high_corr_pairs"]]
    axis.barh(summary["dataset"], summary["high_corr_pairs"], color=colors, height=0.5)
    
    axis.set_xlabel("Número de pares de variables")
    axis.set_xlim(0, max(summary["high_corr_pairs"].max() * 1.12, 1))
    add_editorial_text(axis, "Frecuencia de redundancia potencial", 
                       f"Pares con correlación |Spearman| >= {CORR_THRESHOLD}", palette=TFG_PALETTE)
    apply_editorial_axes(axis, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    
    etiqueta_barras_horizontales(axis, summary["high_corr_pairs"], "{:.0f}", 0.02)
    
    bc_idx = list(summary["dataset"]).index("breast_cancer_wisconsin")
    axis.annotate("29 pares redundantes:\nRequiere control formal en Fase 2", 
                  xy=(29, bc_idx), xytext=(20, bc_idx + 0.48),
                  arrowprops=dict(arrowstyle="->", color=TFG_PALETTE.accent, lw=1.2),
                  fontsize=8.5, fontweight="semibold", color=TFG_PALETTE.text,
                  bbox=dict(boxstyle="round,pad=0.25", fc="#FFFBF5", ec=TFG_PALETTE.accent, alpha=0.9))
                  
    registrar_figura(contexto, Path("01_11_redundancia") / "raw_high_corr_pairs_by_dataset.png")
    cerrar_figura(mostrar)


def plot_dimensionalidad(contexto, mostrar=True):
    data = ordenar_datasets(contexto.tables["raw_dimensionality_summary.csv"])
    y = np.arange(len(data))
    color_map = {"bajo": TFG_PALETTE.positive, "medio": TFG_PALETTE.accent, "alto": TFG_PALETTE.negative}
    colors = [color_map.get(risk, TFG_PALETTE.neutral) for risk in data["riesgo_dimensionalidad"]]
    sizes = 120 + np.sqrt(data["features"]) * 42
    
    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    ax.scatter(data["ratio_features_muestras"], y, s=sizes, color=colors, edgecolor=TFG_PALETTE.background, linewidth=1.5, zorder=3)
    ax.axvline(0.1, color=TFG_PALETTE.accent, linestyle="--", linewidth=1.2, label="Umbral riesgo medio (0.1)")
    ax.set_xscale("log")
    ax.set_xlim(max(data["ratio_features_muestras"].min() / 3, 1e-6), data["ratio_features_muestras"].max() * 2.4)
    ax.set_yticks(y)
    ax.set_yticklabels([etiqueta_dataset(name) for name in data["dataset"]], fontsize=9)
    ax.set_xlabel("Ratio variables / muestras (escala log)")
    
    for pos, row in enumerate(data.itertuples()):
        etiqueta = f"{row.features} vars · riesgo {row.riesgo_dimensionalidad}"
        if row.dataset == "breast_cancer_wisconsin":
            ax.text(row.ratio_features_muestras * 0.82, pos + 0.16, etiqueta, va="bottom", ha="right", fontsize=8.5, color=TFG_PALETTE.text, fontweight="semibold")
        else:
            ax.text(row.ratio_features_muestras * 1.12, pos, etiqueta, va="center", ha="left", fontsize=8.5, color=TFG_PALETTE.text, fontweight="semibold")
    
    add_editorial_text(ax, "Riesgo dimensional: madelon queda separado del resto",
                       "El tamaño del punto representa número de variables; la línea marca el umbral exploratorio", palette=TFG_PALETTE)
    apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    
    registrar_figura(contexto, Path("01_12_dimensionalidad") / "raw_dimensionality_summary.png")
    cerrar_figura(mostrar)


def plot_pca(contexto, mostrar=True):
    pca = contexto.tables["raw_pca_variance_summary.csv"]
    for dataset in [name for name in ORDEN_DATASETS if name in set(pca["dataset"])]:
        data = pca[pca["dataset"].eq(dataset)]
        
        fig, axis = plt.subplots(figsize=(7.5, 4.2))
        
        axis.plot(data["component"], data["cumulative"], marker="o", color=TFG_PALETTE.primary, 
                  linewidth=2.2, markersize=6, label="Varianza acumulada")
        
        axis.axhline(0.8, color=TFG_PALETTE.accent, linestyle="--", linewidth=1.2, label="Umbral 80%")
        
        axis.set_ylim(0, 1.05)
        axis.set_xlabel("Componente Principal")
        axis.set_ylabel("Varianza explicada acumulada")
        
        over_80 = data[data["cumulative"] >= 0.8]
        if not over_80.empty:
            k_comp = over_80.iloc[0]["component"]
            k_var = over_80.iloc[0]["cumulative"]
            axis.scatter(k_comp, k_var, color=TFG_PALETTE.accent, s=120, zorder=5, edgecolor=TFG_PALETTE.background)
            axis.annotate(f"K={k_comp} comp.\n({k_var:.1%})", 
                          xy=(k_comp, k_var), 
                          xytext=(k_comp + 0.5, k_var - 0.15),
                          arrowprops=dict(arrowstyle="->", color=TFG_PALETTE.accent, lw=1),
                          fontsize=8.5, fontweight="semibold", color=TFG_PALETTE.text)
        
        if dataset == "madelon":
            axis.text(6, 0.4, "Crecimiento lineal lento:\nSugerencia de alta presencia de ruido\no señal distribuida de forma débil.", 
                      color=TFG_PALETTE.negative, fontsize=8.5, fontstyle="italic",
                      bbox=dict(boxstyle="round,pad=0.3", fc="#FFF0F0", ec=TFG_PALETTE.negative, alpha=0.8, linewidth=0.5))
                      
        add_editorial_text(axis, f"PCA exploratorio: {dataset}", 
                           "Análisis de varianza explicada acumulada por componentes principales", palette=TFG_PALETTE)
        apply_editorial_axes(axis, palette=TFG_PALETTE, grid_axis="both", show_grid=True)
        axis.legend(loc="lower right", frameon=False)
        
        registrar_figura(contexto, Path("01_12_dimensionalidad") / f"{dataset}_pca_scree.png")
        cerrar_figura(mostrar)


def plot_riesgos(contexto, mostrar=True):
    risks = contexto.tables["raw_spurious_risk_features.csv"]
    if risks.empty:
        return None
        
    for dataset in [name for name in ORDEN_DATASETS if name in set(risks["dataset"])]:
        df_dataset_risks = risks[risks["dataset"] == dataset].copy()
        df_dataset_risks["abs_effect"] = df_dataset_risks["effect_size"].abs()
        df_dataset_risks["tipo_alerta"] = np.where(
            df_dataset_risks["motivos"].str.contains("proxy|leakage", case=False, na=False),
            "proxy/leakage potencial",
            "discrepancia FDR-efecto",
        )
        top = df_dataset_risks.sort_values("abs_effect", ascending=False).head(14).sort_values("abs_effect")
        colors = [TFG_PALETTE.negative if tipo == "proxy/leakage potencial" else TFG_PALETTE.accent for tipo in top["tipo_alerta"]]
        
        fig_height = max(3.8, 0.34 * len(top) + 2.0)
        fig, ax = plt.subplots(figsize=(9.2, fig_height))
        ax.hlines(top["variable"], 0, top["abs_effect"], color=TFG_PALETTE.spine, linewidth=1.5, zorder=1)
        ax.scatter(top["abs_effect"], top["variable"], color=colors, s=90, edgecolor=TFG_PALETTE.background, zorder=3)
        ax.set_xlim(0, max(top["abs_effect"].max() * 1.18, 0.12))
        ax.set_xlabel("|Tamaño de efecto|")
        
        for pos, row in enumerate(top.itertuples()):
            ax.text(row.abs_effect + max(top["abs_effect"].max() * 0.025, 0.006), pos, f"{row.abs_effect:.3f}", va="center", ha="left", fontsize=8.5, color=TFG_PALETTE.muted_text)
        
        from matplotlib.lines import Line2D
        handles_by_tipo = {
            "proxy/leakage potencial": Line2D([0], [0], marker="o", color="none", markerfacecolor=TFG_PALETTE.negative, markeredgecolor=TFG_PALETTE.background, markersize=8, label="Proxy/leakage potencial"),
            "discrepancia FDR-efecto": Line2D([0], [0], marker="o", color="none", markerfacecolor=TFG_PALETTE.accent, markeredgecolor=TFG_PALETTE.background, markersize=8, label="Discrepancia FDR-efecto"),
        }
        legend_handles = [handles_by_tipo[tipo] for tipo in top["tipo_alerta"].drop_duplicates()]
        if len(legend_handles) > 1:
            ax.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, -0.24), ncol=len(legend_handles), frameon=False)
        
        muestra_texto = f"Se muestran {len(top)} de {len(df_dataset_risks)} variables marcadas" if len(df_dataset_risks) > len(top) else f"{len(df_dataset_risks)} variables marcadas"
        add_editorial_text(ax, f"Variables a revisar semánticamente — {dataset}",
                           f"Ranking por magnitud de efecto; {muestra_texto}", palette=TFG_PALETTE)
        apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="x", show_grid=True)
        
        registrar_figura(contexto, Path("01_13_espurias") / f"{dataset}_spurious_risk_volcano.png")
        cerrar_figura(mostrar)


def plot_preclasificacion(contexto, mostrar=True):
    summary = contexto.tables["raw_dataset_signal_summary.csv"]
    if summary.empty:
        return None
        
    pivot = summary.pivot(index="dataset", columns="categoria_preliminar", values="n_variables").fillna(0)
    pivot = ordenar_datasets(pivot.reset_index()).set_index("dataset")
    
    colors = {
        "candidata_fuerte": TFG_PALETTE.primary,
        "candidata_moderada": TFG_PALETTE.secondary,
        "pendiente_multivariante": "#7A6FA5",
        "posible_ruido_univariante": "#D8C8A5",
        "redundante_o_correlacionada": TFG_PALETTE.accent,
        "sospechosa": TFG_PALETTE.negative
    }
    
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    y = np.arange(len(pivot))
    
    left_abs = np.zeros(len(pivot))
    categories = [c for c in colors if c in pivot.columns]
    
    for cat in categories:
        vals = pivot[cat].to_numpy()
        axes[0].barh(y, vals, left=left_abs, label=cat.replace("_", " ").capitalize(), color=colors[cat], height=0.55)
        left_abs += vals
        
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(pivot.index, fontsize=9)
    axes[0].set_xscale("log")
    axes[0].set_xlabel("Número de variables (escala log)")
    add_editorial_text(axes[0], "Composición Absoluta", "Escala de variables por categoría (escala logarítmica)", palette=TFG_PALETTE)
    apply_editorial_axes(axes[0], palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    
    pivot_rel = pivot.div(pivot.sum(axis=1), axis=0)
    left_rel = np.zeros(len(pivot))
    
    for cat in categories:
        vals = pivot_rel[cat].to_numpy()
        axes[1].barh(y, vals, left=left_rel, color=colors[cat], height=0.55)
        
        for idx, val in enumerate(vals):
            if val >= 0.08:
                axes[1].text(left_rel[idx] + val/2, idx, f"{val:.0%}", va="center", ha="center", 
                             color="#FFFFFF", fontsize=8, fontweight="bold")
        left_rel += vals
        
    axes[1].set_yticks(y)
    axes[1].set_yticklabels([])
    axes[1].set_xlim(0, 1.0)
    axes[1].set_xlabel("Proporción relativa")
    add_editorial_text(axes[1], "Composición Relativa", "Porcentaje de variables por categoría (100% stacked)", palette=TFG_PALETTE)
    apply_editorial_axes(axes[1], palette=TFG_PALETTE, grid_axis="x", show_grid=True)
    
    axes[0].legend(loc="lower left", frameon=False, bbox_to_anchor=(0.0, -0.32), ncol=3, fontsize=8.5)
    
    fig.suptitle("Preclasificación Exploratoria de Variables", y=1.08, fontsize=15, fontweight="semibold", color=TFG_PALETTE.text)
    
    registrar_figura(contexto, Path("01_14_preclasificacion") / "raw_feature_preclassification_stacked.png")
    cerrar_figura(mostrar)


def plot_perfil_ead(contexto, mostrar=True):
    profiles = ordenar_datasets(contexto.tables["raw_dataset_profiles.csv"])

    indicadores = [
        ("Dimensión", "riesgo_dimensionalidad"),
        ("Calidad", "baja_varianza_o_dominancia"),
        ("Target", "ratio_mayoritaria_minoritaria"),
        ("Redundancia", "high_corr_pairs"),
        ("Señal útil", "variables_efecto_fuerte"),
        ("Riesgos", "variables_sospechosas"),
    ]

    filas = []
    for row in profiles.itertuples():
        severidad_dimension = 1 if row.riesgo_dimensionalidad == "medio" else 2 if row.riesgo_dimensionalidad == "alto" else 0
        severidad_calidad = 2 if row.baja_varianza_o_dominancia >= 20 else 1 if row.baja_varianza_o_dominancia > 0 else 0
        severidad_target = 2 if row.ratio_mayoritaria_minoritaria >= 3 else 1 if row.ratio_mayoritaria_minoritaria >= 1.5 else 0
        severidad_redundancia = 2 if row.high_corr_pairs >= 20 else 1 if row.high_corr_pairs > 0 else 0
        severidad_senal = 0 if row.variables_efecto_fuerte >= 10 else 1 if row.variables_efecto_fuerte > 0 else 2
        severidad_riesgos = 2 if row.variables_sospechosas >= 2 else 1 if row.variables_sospechosas > 0 else 0
        valores = {
            "Dimensión": (severidad_dimension, f"{row.ratio_features_muestras:.3g}"),
            "Calidad": (severidad_calidad, f"{int(row.baja_varianza_o_dominancia)} vars"),
            "Target": (severidad_target, f"{row.ratio_mayoritaria_minoritaria:.2g}"),
            "Redundancia": (severidad_redundancia, f"{int(row.high_corr_pairs)} pares"),
            "Señal útil": (severidad_senal, f"{int(row.variables_efecto_fuerte)} vars"),
            "Riesgos": (severidad_riesgos, f"{int(row.variables_sospechosas)} vars"),
        }
        for indicador, _ in indicadores:
            severidad, etiqueta = valores[indicador]
            filas.append({
                "dataset": row.dataset,
                "indicador": indicador,
                "severidad": severidad,
                "etiqueta": etiqueta,
            })

    perfil = pd.DataFrame(filas)
    x_map = {name: pos for pos, (name, _) in enumerate(indicadores)}
    y_map = {name: pos for pos, name in enumerate(profiles["dataset"])}
    perfil["x"] = perfil["indicador"].map(x_map)
    perfil["y"] = perfil["dataset"].map(y_map)
    perfil["size"] = 220 + perfil["severidad"] * 190
    perfil["color"] = perfil["severidad"].map(color_severidad)

    fig, ax = plt.subplots(figsize=(10.5, 4.9))
    ax.scatter(perfil["x"], perfil["y"], s=perfil["size"], c=perfil["color"],
               edgecolor=TFG_PALETTE.background, linewidth=1.5, zorder=3)
    for row in perfil.itertuples():
        ax.text(row.x, row.y, row.etiqueta, ha="center", va="center", fontsize=7.5,
                color="#FFFFFF" if row.severidad == 2 else TFG_PALETTE.text, fontweight="semibold")

    ax.set_xticks(range(len(indicadores)))
    ax.set_xticklabels([name for name, _ in indicadores], fontsize=9)
    ax.set_yticks(range(len(profiles)))
    ax.set_yticklabels([etiqueta_dataset(name) for name in profiles["dataset"]], fontsize=9, fontweight="semibold")
    ax.set_xlim(-0.6, len(indicadores) - 0.4)
    ax.set_ylim(len(profiles) - 0.5, -0.5)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(True, axis="both", color=TFG_PALETTE.grid, linewidth=0.6, alpha=0.75)
    ax.set_axisbelow(True)

    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=TFG_PALETTE.positive, markeredgecolor=TFG_PALETTE.background, markersize=9, label="Bajo / favorable"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=TFG_PALETTE.accent, markeredgecolor=TFG_PALETTE.background, markersize=11, label="Vigilar"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=TFG_PALETTE.negative, markeredgecolor=TFG_PALETTE.background, markersize=13, label="Alto / revisar"),
    ]
    ax.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, -0.28), ncol=3, frameon=False)

    add_editorial_text(ax, "Perfil EAD por severidad relativa",
                       "Puntos mayores y rojos indican más atención requerida; señal útil se interpreta en sentido favorable", palette=TFG_PALETTE)
    apply_editorial_axes(ax, palette=TFG_PALETTE, grid_axis="both", show_grid=True, remove_spines=True)
    
    registrar_figura(contexto, Path("01_15_ead") / "raw_dataset_profile_heatmap.png")
    cerrar_figura(mostrar)


def generar_informes_fase1(contexto):
    figures_selected = _guardar_figuras_candidatas(contexto)
    _guardar_resumen_ead(contexto, figures_selected)
    report_text = construir_informe_resultados(contexto, figures_selected)
    report_path = contexto.reports_dir / "raw_phase1_results_report.md"
    report_path.write_text(report_text, encoding="utf-8")
    latex_path = contexto.reports_dir / "raw_phase1_results_report.tex"
    template_path = contexto.project_root / "Plantilla_Latex_GCD" / "tfgs" / "tex" / "resultados_fase1.tex"
    ensure_dir(template_path.parent)
    write_latex_report_from_markdown(report_text, latex_path, title="Resultados de la Fase 1")
    write_latex_report_from_markdown(report_text, template_path, title="Resultados de la Fase 1")
    return report_path


def _guardar_figuras_candidatas(contexto):
    figure_candidates = [
        {"dataset": "global", "figura": "raw_structure_summary.png", "motivo": "Escala muestral, dimensionalidad inicial y ratio variables/muestras", "ruta": str((contexto.figures_dir / "01_02_estructura" / "raw_structure_summary.png").relative_to(contexto.project_root))},
        {"dataset": "global", "figura": "raw_quality_issues_summary.png", "motivo": "Incidencias accionables de calidad del dato crudo sin heatmap vacío", "ruta": str((contexto.figures_dir / "01_03_calidad" / "raw_quality_issues_summary.png").relative_to(contexto.project_root))},
        {"dataset": "global", "figura": "raw_target_distribution_panel.png", "motivo": "Distribución de clases, con lectura separada para binarios y olive_oil multiclase", "ruta": str((contexto.figures_dir / "01_04_target" / "raw_target_distribution_panel.png").relative_to(contexto.project_root))},
        {"dataset": "global", "figura": "raw_fdr_before_after.png", "motivo": "Efecto de la corrección por múltiples comparaciones, especialmente en madelon", "ruta": str((contexto.figures_dir / "01_09_fdr" / "raw_fdr_before_after.png").relative_to(contexto.project_root))},
        {"dataset": "global", "figura": "raw_high_corr_pairs_by_dataset.png", "motivo": "Redundancia potencial por correlación alta y prioridad de control en Fase 2", "ruta": str((contexto.figures_dir / "01_11_redundancia" / "raw_high_corr_pairs_by_dataset.png").relative_to(contexto.project_root))},
        {"dataset": "global", "figura": "raw_dataset_profile_heatmap.png", "motivo": "Matriz de severidad EAD trazada desde raw_dataset_profiles.csv", "ruta": str((contexto.figures_dir / "01_15_ead" / "raw_dataset_profile_heatmap.png").relative_to(contexto.project_root))},
    ]
    selected = pd.DataFrame([row for row in figure_candidates if (contexto.project_root / row["ruta"]).exists()])
    registrar_tabla(contexto, "raw_figures_selected_for_report.csv", selected)
    return selected


def _guardar_resumen_ead(contexto, figures_selected):
    profiles = contexto.tables["raw_dataset_profiles.csv"]
    lines = ["# Resumen EAD preliminar — Fase 1", "", "Este documento resume la evidencia generada por el notebook de Fase 1. Las conclusiones son exploratorias y no sustituyen el preprocesado ni la selección formal de características de fases posteriores.", ""]
    for _, row in profiles.iterrows():
        n_clases = int(row.get("n_clases", 0)) if pd.notna(row.get("n_clases", np.nan)) else "NA"
        ratio = row.get("ratio_mayoritaria_minoritaria", np.nan)
        ratio_text = f"{ratio:.3g}" if pd.notna(ratio) else "NA"
        lines += [
            f"## {row['dataset']}", "",
            f"- Estructura: {int(row.get('filas', 0))} filas y {int(row.get('features', 0))} features analíticas; target `{row.get('target', 'NA')}`.",
            f"- Calidad: {int(row.get('n_missing_cols', 0))} columnas con nulos, {int(row.get('duplicados', 0))} filas duplicadas y {int(row.get('constantes', 0))} variables constantes.",
            f"- Target: {n_clases} clases; ratio mayoritaria/minoritaria {ratio_text}.",
            f"- Señal univariante: {int(row.get('variables_efecto_fuerte', 0))} variables con efecto medio/grande tras FDR.",
            f"- Redundancia: {int(row.get('high_corr_pairs', 0))} pares con correlación alta según el umbral de la sección 1.11.",
            f"- Dimensionalidad: riesgo {row.get('riesgo_dimensionalidad', 'NA')}; posible ruido univariante {int(row.get('posible_ruido_univariante', 0))} variables.",
            f"- Riesgos: {int(row.get('variables_sospechosas', 0))} variables marcadas para revisión; no se confirma leakage en esta fase.",
            "",
        ]
    lines += ["## Figuras candidatas para memoria", ""]
    if figures_selected.empty:
        lines.append("No se seleccionan figuras porque no se han generado archivos válidos.")
    else:
        for _, row in figures_selected.iterrows():
            lines.append(f"- `{row['ruta']}`: {row['motivo']}.")
    lines += ["", "## Tablas clave", "", "- `raw_load_summary.csv`", "- `raw_structure_summary.csv`", "- `raw_quality_summary.csv`", "- `raw_target_distribution.csv`", "- `raw_feature_target_tests.csv`", "- `raw_fdr_corrected_tests.csv`", "- `raw_effect_sizes.csv`", "- `raw_high_correlation_pairs.csv`", "- `raw_feature_preclassification.csv`", "- `raw_phase1_checklist.csv`"]
    (contexto.reports_dir / "raw_ead_summary.md").write_text("\n".join(lines), encoding="utf-8")


def construir_informe_resultados(contexto, figures_selected):
    load = contexto.tables["raw_load_summary.csv"]
    structure = contexto.tables["raw_structure_summary.csv"]
    quality = contexto.tables["raw_quality_summary.csv"]
    target = contexto.tables["raw_target_balance_summary.csv"]
    candidates = contexto.tables["raw_candidate_features_univariate.csv"]
    fdr = contexto.tables["raw_fdr_summary.csv"]
    effects = contexto.tables["raw_effect_size_interpretation.csv"]
    redundancy = contexto.tables["raw_redundancy_summary.csv"]
    dimensionality = contexto.tables["raw_dimensionality_summary.csv"]
    risks = contexto.tables["raw_spurious_risk_features.csv"]
    signal = contexto.tables["raw_dataset_signal_summary.csv"]
    profiles = contexto.tables["raw_dataset_profiles.csv"]
    lines = ["# Informe de resultados — Fase 1", "", "## 1. Objetivo de la fase", "", "Evaluar estructura, calidad, señal estadística, redundancia, dimensionalidad y riesgos de los datasets crudos antes de aplicar preprocesado, selección de características o modelado.", "", "## 2. Datasets analizados", ""]
    for _, row in load.iterrows():
        lines.append(f"- `{row['dataset']}`: {int(row['filas'])} filas, {int(row['columnas'])} columnas, target `{row['target_detectado']}`.")
    lines += ["", "## 3. Resumen estructural", ""]
    for _, row in structure.iterrows():
        lines.append(f"- `{row['dataset']}`: {int(row['features'])} features analíticas, {int(row['posibles_ids'])} posible(s) identificador(es), ratio features/muestras {row['ratio_features_muestras']:.4g}.")
    lines += ["", "## 4. Calidad del dato", ""]
    for _, row in quality.iterrows():
        lines.append(f"- `{row['dataset']}`: {int(row['n_missing_cols'])} columnas con nulos, {int(row['duplicados'])} duplicados, {int(row['constantes'])} constantes y {int(row['baja_varianza_o_dominancia'])} variables de baja variabilidad/dominancia.")
    lines += ["", "## 5. Distribución del target", ""]
    for _, row in target.iterrows():
        ratio_text = f"{row.get('ratio_mayoritaria_minoritaria', np.nan):.3g}" if pd.notna(row.get("ratio_mayoritaria_minoritaria", np.nan)) else "NA"
        lines.append(f"- `{row['dataset']}`: {int(row.get('n_clases', 0))} clases; clase minoritaria n={int(row.get('clase_minoritaria_n', 0))}; ratio {ratio_text}.")
    lines += ["", "## 6. Señal variable-target", ""]
    if candidates.empty:
        lines.append("No se identifican candidatas univariantes bajo los criterios exploratorios definidos.")
    else:
        for _, row in candidates.groupby("dataset").size().reset_index(name="n_candidatas").iterrows():
            lines.append(f"- `{row['dataset']}`: {int(row['n_candidatas'])} variables candidatas univariantes tras FDR y efecto mínimo.")
    lines += ["", "## 7. Corrección por múltiples comparaciones", ""]
    for _, row in fdr.iterrows():
        lines.append(f"- `{row['dataset']}`: {int(row['significativas_sin_corregir'])} significativas sin corregir frente a {int(row['significativas_fdr'])} tras FDR.")
    lines += ["", "## 8. Tamaños de efecto", ""]
    for dataset, group in effects.groupby("dataset"):
        parts = [f"{row['magnitud_exploratoria']}={int(row['n_variables'])}" for _, row in group.iterrows()]
        lines.append(f"- `{dataset}`: " + ", ".join(parts) + ".")
    lines += ["", "## 9. Redundancia", ""]
    for _, row in redundancy.iterrows():
        lines.append(f"- `{row['dataset']}`: {int(row['high_corr_pairs'])} pares con |Spearman| >= {row.get('corr_threshold', CORR_THRESHOLD)}.")
    lines += ["", "## 10. Dimensionalidad y ruido", ""]
    for _, row in dimensionality.iterrows():
        lines.append(f"- `{row['dataset']}`: riesgo {row['riesgo_dimensionalidad']}; posible ruido univariante {int(row['posible_ruido_univariante'])} variables.")
    lines += ["", "## 11. Posibles relaciones espurias o leakage", ""]
    for _, row in risks.groupby("dataset").size().reset_index(name="n_riesgos").iterrows():
        lines.append(f"- `{row['dataset']}`: {int(row['n_riesgos'])} variables para revisión semántica; no se confirma leakage en esta fase.")
    lines += ["", "## 12. Preclasificación preliminar", ""]
    for dataset, group in signal.groupby("dataset"):
        parts = [f"{row['categoria_preliminar']}={int(row['n_variables'])}" for _, row in group.iterrows()]
        lines.append(f"- `{dataset}`: " + ", ".join(parts) + ".")
    lines += ["", "## 13. Figuras más importantes", ""]
    for _, row in figures_selected.iterrows():
        lines.append(f"- `{row['ruta']}`: {row['motivo']}.")
    lines += ["", "## 14. Tablas más importantes", "", "`raw_structure_summary.csv`, `raw_quality_summary.csv`, `raw_target_distribution.csv`, `raw_feature_target_tests.csv`, `raw_fdr_corrected_tests.csv`, `raw_effect_sizes.csv`, `raw_high_correlation_pairs.csv`, `raw_feature_preclassification.csv`.", "", "## 15. Conclusiones por dataset", ""]
    for _, row in profiles.iterrows():
        lines.append(f"- `{row['dataset']}`: pasa a fases posteriores con riesgo dimensional {row.get('riesgo_dimensionalidad', 'NA')}, {int(row.get('variables_efecto_fuerte', 0))} señales fuertes exploratorias y {int(row.get('variables_sospechosas', 0))} riesgos a revisar.")
    lines += ["", "## 15.1 Matices de interpretación", ""]
    lines += [
        "- `customer_churn`: por su tamaño muestral, la significación estadística debe leerse junto al tamaño de efecto; no se interpreta como evidencia fuerte por p-value aislado.",
        "- `madelon`: el patrón sugiere alta dimensionalidad y mucho ruido univariante, pero no ausencia total de señal; hay variables con señal exploratoria tras FDR.",
        "- `olive_oil`: queda marcado como problema multiclase con desbalance relevante; la evaluación posterior debe priorizar métricas macro o balanceadas.",
        "- `breast_cancer_wisconsin`: muestra señal univariante fuerte, pero también redundancia alta; la Fase 2 debe controlar variables correlacionadas antes de selección formal.",
    ]
    lines += ["", "## 16. Implicaciones para la Fase 2", ""]
    lines += [
        "La Fase 2 debe usar explícitamente los artefactos de esta fase para tomar, como mínimo, las siguientes decisiones:",
        "- IDs: excluir o aislar columnas con rol `posible_id` antes de entrenar o seleccionar variables.",
        "- Baja varianza/dominancia: revisar `raw_low_variance_features.csv` y decidir eliminación, recodificación o conservación justificada.",
        "- Codificación: codificar variables categóricas sin introducir información del target ni mezclar ajuste entre train y test.",
        "- Escalado: ajustar escaladores solo con train, especialmente para PCA, métodos basados en distancia y modelos sensibles a escala.",
        "- Outliers: revisar `raw_outlier_summary.csv` y decidir tratamiento robusto sin eliminar observaciones de forma automática.",
        "- Splits: mantener particiones estratificadas cuando proceda, con especial cuidado en `olive_oil` por su target multiclase desbalanceado.",
        "- Leakage/proxies: auditar semánticamente `raw_spurious_risk_features.csv` y `raw_proxy_leakage_candidates.csv` antes de modelar.",
        "- Redundancia: usar `raw_high_correlation_pairs.csv` para controlar bloques correlacionados, especialmente en `breast_cancer_wisconsin`.",
    ]
    lines += ["", "## 17. Incidencias y decisiones metodológicas", "", "No se inventan datos ni targets. Se excluyen identificadores de los análisis de asociación y correlación. Las visualizaciones vacías se omiten, especialmente mapas de nulos cuando no hay nulos."]
    return "\n".join(lines)


def generar_checklist_y_handoff(contexto):
    rows = []
    quality = contexto.tables["raw_quality_summary.csv"]
    dimensionality = contexto.tables["raw_dimensionality_summary.csv"]
    risks = contexto.tables["raw_spurious_risk_features.csv"]
    for dataset in contexto.dataset_config:
        loaded = dataset in contexto.raw_datasets
        target = contexto.raw_datasets[dataset]["target"] if loaded else None
        quality_row = quality[quality["dataset"].eq(dataset)]
        dim_row = dimensionality[dimensionality["dataset"].eq(dataset)]
        risk_rows = risks[risks["dataset"].eq(dataset)] if not risks.empty else pd.DataFrame()
        rows.append({
            "dataset": dataset,
            "carga_correcta": loaded,
            "target_identificado": target is not None,
            "problemas_calidad": bool(quality_row[["n_missing_cols", "duplicados", "constantes", "baja_varianza_o_dominancia"]].sum(axis=1).iloc[0] > 0) if not quality_row.empty else np.nan,
            "fdr_calculado": not contexto.tables["raw_fdr_summary.csv"].empty,
            "tamanos_efecto_calculados": not contexto.tables["raw_effect_sizes.csv"].empty,
            "redundancia_calculada": not contexto.tables["raw_redundancy_summary.csv"].empty,
            "hay_variables_sospechosas": not risk_rows.empty,
            "riesgo_dimensionalidad": dim_row["riesgo_dimensionalidad"].iloc[0] if not dim_row.empty else np.nan,
            "pasa_a_fase2": "sí" if loaded and target is not None else "revisar antes de Fase 2",
        })
    checklist = pd.DataFrame(rows)
    registrar_tabla(contexto, "raw_phase1_checklist.csv", checklist)
    _guardar_handoff(contexto, checklist)
    return checklist


def _guardar_handoff(contexto, checklist):
    lines = [
        "# Traspaso de Fase 1 a Fase 2", "",
        "Usar estos resultados para decidir tratamiento de tipos, nulos, constantes, outliers, escalado, codificación, split, controles de leakage y redundancia.", "",
        "## Decisiones concretas obligatorias", "",
        "- IDs: excluir o aislar variables con rol `posible_id` según `raw_variable_roles.csv`.",
        "- Baja varianza/dominancia: revisar `raw_low_variance_features.csv` antes de eliminar o conservar variables.",
        "- Codificación: transformar categóricas con ajuste solo en train y categorías desconocidas controladas.",
        "- Escalado: ajustar escaladores solo en train; obligatorio para PCA, distancias y modelos sensibles a escala.",
        "- Outliers: revisar `raw_outlier_summary.csv`; no eliminar automáticamente sin criterio de dominio o robustez.",
        "- Splits: usar particiones estratificadas cuando proceda; especial atención a `olive_oil` por desbalance multiclase.",
        "- Leakage/proxies: revisar `raw_spurious_risk_features.csv` y `raw_proxy_leakage_candidates.csv` antes del modelado.",
        "- Redundancia: controlar pares de `raw_high_correlation_pairs.csv`, especialmente en `breast_cancer_wisconsin`.",
        "",
    ]
    for _, row in checklist.iterrows():
        lines += [
            f"## {row['dataset']}",
            f"- Carga correcta: {row['carga_correcta']}",
            f"- Target identificado: {row['target_identificado']}",
            f"- Problemas de calidad: {row['problemas_calidad']}",
            f"- Riesgo dimensionalidad: {row['riesgo_dimensionalidad']}",
            f"- Variables sospechosas: {row['hay_variables_sospechosas']}",
            f"- Estado para Fase 2: {row['pasa_a_fase2']}",
            "",
        ]
    (contexto.reports_dir / "raw_phase1_handoff_to_phase2.md").write_text("\n".join(lines), encoding="utf-8")


def generar_revision_critica(contexto):
    expected_tables = [
        "raw_load_summary.csv", "raw_structure_summary.csv", "raw_missing_values.csv", "raw_duplicates_summary.csv",
        "raw_target_distribution.csv", "raw_numeric_descriptive_stats.csv", "raw_distribution_shape.csv",
        "raw_feature_target_tests.csv", "raw_fdr_corrected_tests.csv", "raw_effect_sizes.csv",
        "raw_mutual_information_scores.csv", "raw_high_correlation_pairs.csv", "raw_dimensionality_summary.csv",
        "raw_spurious_risk_features.csv", "raw_feature_preclassification.csv", "raw_dataset_profiles.csv",
    ]
    rows = [{"tipo": "tabla", "artefacto": name, "existe": (contexto.tables_dir / name).exists(), "ruta": str((contexto.tables_dir / name).relative_to(contexto.project_root))} for name in expected_tables]
    figure_files = sorted(contexto.figures_dir.glob("**/*.png"))
    rows.extend({"tipo": "figura", "artefacto": path.name, "existe": path.exists(), "ruta": str(path.relative_to(contexto.project_root))} for path in figure_files)
    audit = pd.DataFrame(rows)
    registrar_tabla(contexto, "raw_phase1_artifact_audit.csv", audit)
    tables_present = int(audit[audit["tipo"].eq("tabla")]["existe"].sum())
    lines = [
        "# Revisión crítica — Fase 1", "",
        "## Estructura narrativa", "",
        "El notebook refinado mantiene la secuencia faseada y delega cálculo, figuras e informes en funciones reutilizables de `/src`.", "",
        "## Auditoría visual", "",
        "Las figuras se han sustituido por versiones editoriales con superficie cálida, colores consistentes, etiquetas más legibles y el mismo propósito analítico.", "",
        "## Límites", "",
        "La fase sigue siendo preliminar: no confirma leakage, no decide selección final y no valida rendimiento predictivo.", "",
        f"Artefactos auditados: {len(audit)}. Figuras PNG guardadas: {len(figure_files)}. Tablas esperadas presentes: {tables_present}/{len(expected_tables)}.",
    ]
    (contexto.reports_dir / "raw_phase1_critical_review.md").write_text("\n".join(lines), encoding="utf-8")
    return audit
