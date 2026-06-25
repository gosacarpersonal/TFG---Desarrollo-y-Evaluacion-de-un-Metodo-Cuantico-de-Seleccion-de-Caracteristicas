"""Construye una versión narrativa del notebook de Fase 5.

El notebook resultante no recalcula la selección: lee los artefactos ya
producidos por la fase, crea vistas compactas para lectura científica y deja
los CSV completos como fuente trazable.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


NOTEBOOK_PATH = Path("notebooks/fase5.ipynb")
REPORT_DIR = Path("results/reports/05_feature_selection")
AUDIT_PATH = REPORT_DIR / "fase5_reconstruccion_narrativa_audit.md"


def md_cell(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code_cell(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text.strip() + "\n")


SETUP_CODE = r'''
from pathlib import Path
import base64
import html
import os
import sys

import numpy as np
import pandas as pd
from pandas.errors import EmptyDataError
from IPython.display import HTML, Markdown, display

cwd = Path.cwd().resolve()
PROJECT_ROOT = cwd if (cwd / "src").exists() else cwd.parent
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

TABLE_DIR = PROJECT_ROOT / "results/tables/05_feature_selection"
FIGURE_DIR = PROJECT_ROOT / "results/figures/05_feature_selection"
REPORT_DIR = PROJECT_ROOT / "results/reports/05_feature_selection"
SELECTED_DIR = PROJECT_ROOT / "data/selected_features"

pd.set_option("display.max_columns", 12)
pd.set_option("display.width", 140)

TABLAS_REQUERIDAS = [
    "fs_input_dataset_summary.csv",
    "fs_inherited_warnings.csv",
    "fs_train_input_quality.csv",
    "fs_column_alignment_check.csv",
    "fs_method_registry.csv",
    "fs_method_configurations.csv",
    "fs_k_values_by_dataset.csv",
    "fs_sampling_plan.csv",
    "fs_sampling_representativeness.csv",
    "fs_baseline_summary.csv",
    "fs_all_rankings.csv",
    "fs_all_selected_features.csv",
    "fs_all_execution_times.csv",
    "fs_method_profiles.csv",
    "fs_jaccard_stability.csv",
    "fs_kuncheva_stability.csv",
    "fs_permutation_summary.csv",
    "fs_redundancy_vs_full.csv",
    "fs_selected_feature_evidence_map.csv",
    "fs_suspicious_selected_features.csv",
    "fs_figures_selected_for_report.csv",
    "fs_visual_audit.csv",
    "fs_reduced_datasets_log.csv",
    "fs_column_consistency_check.csv",
    "fs_phase6_input_recommendations.csv",
    "fs_phase5_final_checklist.csv",
    "fs_phase5_handoff_to_phase6.csv",
    "fs_phase5_open_issues.csv",
]


def cargar_csv(nombre):
    ruta = TABLE_DIR / nombre
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}")
    try:
        return pd.read_csv(ruta)
    except EmptyDataError:
        return pd.DataFrame()


def _ruta_relativa_si_procede(valor):
    texto = str(valor)
    try:
        ruta = Path(texto)
        if ruta.is_absolute():
            return str(ruta.relative_to(PROJECT_ROOT))
    except Exception:
        pass
    return texto


def _truncar_texto(valor, max_caracteres=82):
    if pd.isna(valor):
        return ""
    texto = _ruta_relativa_si_procede(valor)
    texto = " ".join(str(texto).split())
    return texto if len(texto) <= max_caracteres else texto[: max_caracteres - 1] + "..."


def mostrar_tabla_compacta(tabla, titulo, columnas=None, ordenar_por=None, ascendente=True, max_filas=12, formato=None, max_columnas=8):
    vista = tabla.copy()
    if columnas is not None:
        vista = vista[[col for col in columnas if col in vista.columns]]
    elif len(vista.columns) > max_columnas:
        vista = vista[list(vista.columns[:max_columnas])]
    if ordenar_por is not None and ordenar_por in vista.columns:
        vista = vista.sort_values(ordenar_por, ascending=ascendente)
    if len(vista) > max_filas:
        vista = vista.iloc[:max_filas].copy()
    if formato:
        for columna, funcion in formato.items():
            if columna in vista.columns:
                vista[columna] = vista[columna].map(funcion)
    for columna in vista.select_dtypes(include="object").columns:
        vista[columna] = vista[columna].map(_truncar_texto)
    display(Markdown(f"**{titulo}**  \n{len(tabla)} filas completas en CSV; se muestra una vista compacta de {len(vista)} filas."))
    display(vista)
    return vista


def mostrar_figura(ruta_relativa, titulo=None):
    ruta = PROJECT_ROOT / ruta_relativa
    if not ruta.exists():
        display(Markdown(f"**Figura no encontrada:** `{ruta_relativa}`"))
        return
    if titulo:
        display(Markdown(f"**{titulo}**"))
    mime = "image/svg+xml" if ruta.suffix.lower() == ".svg" else "image/png"
    data = base64.b64encode(ruta.read_bytes()).decode("ascii")
    alt = html.escape(titulo or ruta.name)
    display(HTML(f'<img src="data:{mime};base64,{data}" alt="{alt}" style="width:920px; max-width:100%; height:auto;">'))


def porcentaje(valor):
    if pd.isna(valor):
        return ""
    return f"{100 * valor:.1f}%" if abs(valor) <= 1 else f"{valor:.1f}%"


def numero(valor):
    if pd.isna(valor):
        return ""
    return f"{valor:.3f}"


artefactos = {nombre: cargar_csv(nombre) for nombre in TABLAS_REQUERIDAS}
resumen_artefactos = pd.DataFrame(
    {
        "artefacto": nombre,
        "filas": len(tabla),
        "columnas": len(tabla.columns),
        "ruta": str((TABLE_DIR / nombre).relative_to(PROJECT_ROOT)),
    }
    for nombre, tabla in artefactos.items()
)
'''


DERIVED_CODE = r'''
dataset_summary = artefactos["fs_input_dataset_summary.csv"]
method_registry = artefactos["fs_method_registry.csv"]
method_profiles = artefactos["fs_method_profiles.csv"]
execution_times = artefactos["fs_all_execution_times.csv"]
all_rankings = artefactos["fs_all_rankings.csv"]
jaccard = artefactos["fs_jaccard_stability.csv"]
kuncheva = artefactos["fs_kuncheva_stability.csv"]
permutation = artefactos["fs_permutation_summary.csv"]
redundancy = artefactos["fs_redundancy_vs_full.csv"]
evidence_map = artefactos["fs_selected_feature_evidence_map.csv"]
phase6_recommendations = artefactos["fs_phase6_input_recommendations.csv"]
figures = artefactos["fs_figures_selected_for_report.csv"]
visual_audit = artefactos["fs_visual_audit.csv"]

stability_summary = (
    jaccard.groupby(["dataset", "method"], as_index=False)
    .agg(mean_jaccard=("jaccard", "mean"), min_jaccard=("jaccard", "min"))
)
redundancy_summary = (
    redundancy.groupby(["dataset", "method"], as_index=False)
    .agg(mean_selected_corr=("selected_mean_abs_corr", "mean"), max_selected_corr=("selected_max_abs_corr", "max"))
)
method_dataset_profile = (
    execution_times.groupby(["dataset", "method"], as_index=False)
    .agg(mean_elapsed_seconds=("elapsed_seconds", "mean"), sample_applied=("sample_applied", "max"))
    .merge(stability_summary, on=["dataset", "method"], how="left")
    .merge(redundancy_summary, on=["dataset", "method"], how="left")
)

principal_phase6 = phase6_recommendations[phase6_recommendations["rol_fase6"].eq("principal_para_modelado")].copy()
principal_profile = principal_phase6.merge(
    method_dataset_profile,
    on=["dataset", "method"],
    how="left",
)

selection_frequency = (
    all_rankings[(all_rankings["selected"]) & (all_rankings["seed"].eq(42)) & (all_rankings["status"].eq("ok"))]
    .groupby(["dataset", "feature"], as_index=False)
    .agg(n_methods=("method", "nunique"), best_rank=("rank", "min"))
    .sort_values(["dataset", "n_methods", "best_rank"], ascending=[True, False, True])
)

top_features_by_dataset = (
    selection_frequency[selection_frequency.groupby("dataset").cumcount() < 6]
    .reset_index(drop=True)
)

dataset_method_reading = principal_profile.copy()
mean_jaccard_numeric = pd.to_numeric(dataset_method_reading["mean_jaccard"], errors="coerce").fillna(0)
mean_selected_corr_numeric = pd.to_numeric(dataset_method_reading["mean_selected_corr"], errors="coerce").fillna(0)
dataset_method_reading["lectura"] = np.where(
    mean_jaccard_numeric >= 0.85,
    "estable entre semillas",
    "sensible a semilla o alternativas equivalentes",
)
dataset_method_reading["cautela_redundancia"] = np.where(
    mean_selected_corr_numeric >= 0.5,
    "vigilar redundancia",
    "redundancia contenida",
)
'''


def build_notebook() -> None:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "qfs_env", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }

    cells = [
        md_cell(
            """
            # Fase 5 - Selección clásica de características

            Este notebook reconstruye la lectura científica de la Fase 5 a partir de los artefactos ya ejecutados. No reajusta selectores ni recalcula métricas: interpreta rankings, estabilidad, permutaciones, redundancia, evidencias heredadas y datasets reducidos guardados previamente.

            La regla metodológica se mantiene intacta: cada selector se ajustó con `X_train, y_train`; validation y test solo reciben las columnas ya seleccionadas. Las tablas completas permanecen en `results/tables/05_feature_selection/` y aquí se muestran vistas compactas diseñadas para lectura humana.
            """
        ),
        code_cell(SETUP_CODE),
        md_cell(
            """
            ## Inventario de artefactos usados

            **Pregunta.** ¿La reconstrucción narrativa parte de artefactos existentes y trazables?

            **Criterio.** El notebook lee CSV y figuras ya generados por la fase. Si falta un artefacto requerido, la ejecución se detiene; si existe, se usa como evidencia, no como plantilla decorativa.
            """
        ),
        code_cell(
            """
mostrar_tabla_compacta(
    resumen_artefactos,
    "Artefactos tabulares cargados para la reconstrucción narrativa",
    columnas=["artefacto", "filas", "columnas", "ruta"],
    max_filas=10,
)
            """
        ),
        code_cell(DERIVED_CODE),
        md_cell(
            """
            ## 5.1 Splits y advertencias heredadas

            **Pregunta.** ¿Qué problemas y cautelas entran a la selección clásica desde las fases anteriores?

            **Artefactos usados.** `fs_input_dataset_summary.csv`, `fs_inherited_warnings.csv`, handoff de Fase 4 y splits de `data/splits/`.

            **Criterio metodológico.** Fase 5 solo continúa con datasets aceptados en Fase 4. `olive_oil` se trata como dos problemas distintos (`olive_oil_3class` y `olive_oil_9class`) y no como un dataset ambiguo.
            """
        ),
        code_cell(
            """
mostrar_tabla_compacta(
    dataset_summary,
    "Tamaño y dimensionalidad de los datasets que entran a selección",
    columnas=["dataset", "train_rows", "validation_rows", "test_rows", "raw_features", "processed_features", "classes"],
    max_filas=8,
)

inherited = artefactos["fs_inherited_warnings.csv"]
if len(inherited):
    columnas_warning = [col for col in ["dataset", "tipo", "gravedad", "riesgo", "accion", "evidencia"] if col in inherited.columns]
    mostrar_tabla_compacta(inherited, "Cautelas heredadas relevantes", columnas=columnas_warning, max_filas=12)
else:
    display(Markdown("No hay advertencias heredadas registradas en `fs_inherited_warnings.csv`."))
            """
        ),
        md_cell(
            """
            **Lectura.** `customer_churn` exige atención por codificación ajustada solo con train; `madelon` llega con alta dimensionalidad; `breast_cancer_wisconsin` y las dos formulaciones de Olive Oil arrastran cautelas de drift o redundancia. Estas advertencias no bloquean la fase, pero condicionan cómo interpretar estabilidad, redundancia y utilidad para Fase 6.
            """
        ),
        md_cell(
            """
            ## 5.2 Protocolo y familias de métodos

            **Pregunta.** ¿Qué pregunta responde cada familia de selección y qué limitación introduce?

            **Criterio metodológico.** Se comparan filtros, filtros supervisados, relevancia-redundancia, regularización y métodos embedded. Ninguno usa validation/test para decidir columnas.
            """
        ),
        code_cell(
            """
familias = method_registry.copy()
familias["lectura_metodológica"] = familias["family"].map(
    {
        "filtros": "ordena variables por una propiedad simple; es barato, pero no usa el target",
        "filtros supervisados": "mide asociación marginal con el target; puede ignorar interacciones y redundancia",
        "relevancia-redundancia": "busca señal evitando variables repetidas; depende de la aproximación mRMR usada",
        "regularizacion": "favorece subconjuntos parsimoniosos mediante penalización; sensible a escalado y correlación",
        "embedded": "usa un modelo para estimar importancia; puede ser estable o costoso según dataset",
    }
)
mostrar_tabla_compacta(
    familias,
    "Familias, contrato train-only y limitaciones principales",
    columnas=["method", "family", "uses_target", "has_randomness", "requires_sample_when_large", "expected_cost", "fit_scope", "lectura_metodológica"],
    max_filas=10,
)
            """
        ),
        md_cell(
            """
            **Decisión.** La comparación no busca declarar un selector universalmente mejor. Busca una base clásica defendible para contrastar en Fase 6: métodos baratos para referencia, métodos supervisados para señal marginal, métodos multivariantes para redundancia y métodos embedded para importancias dependientes de modelo.
            """
        ),
        md_cell(
            """
            ## 5.3 Preparación de matrices y contrato train-only

            **Pregunta.** ¿Las matrices que reciben los selectores cumplen el contrato de no fuga?

            **Artefactos usados.** `fs_train_input_quality.csv`, `fs_column_alignment_check.csv`, `fs_suspicious_selected_features.csv`.

            **Criterio metodológico.** El preprocesado que afecta a variables predictoras se ajusta en train y se aplica a validation/test. Las columnas prohibidas no entran en X.
            """
        ),
        code_cell(
            """
quality = artefactos["fs_train_input_quality.csv"]
alignment = artefactos["fs_column_alignment_check.csv"]
suspicious = artefactos["fs_suspicious_selected_features.csv"]
mostrar_tabla_compacta(quality, "Calidad de entrada por dataset", max_filas=8)
mostrar_tabla_compacta(alignment, "Alineación train/validation/test y ausencia de target en X", max_filas=8)
display(Markdown(f"**Variables sospechosas seleccionadas:** {len(suspicious)} registros."))
            """
        ),
        md_cell(
            """
            **Interpretación.** La evidencia apunta a matrices alineadas y sin selección de columnas sospechosas. La ausencia de sospechosas no garantiza ausencia absoluta de proxies semánticos; por eso el riesgo residual se mantiene documentado para modelado.
            """
        ),
        md_cell(
            """
            ## 5.4 Configuración real de métodos

            **Pregunta.** ¿Qué métodos se ejecutan completos y cuáles requieren control de coste?

            **Criterio metodológico.** Los métodos baratos se ejecutan sobre train completo. En datasets grandes, los métodos costosos pueden usar muestra estratificada documentada; sus tiempos no se comparan como si fueran ejecución completa.
            """
        ),
        code_cell(
            """
config = artefactos["fs_method_configurations.csv"]
config_resumen = config.pivot_table(index="dataset", columns="decision", values="method", aggfunc="count", fill_value=0).reset_index()
mostrar_tabla_compacta(config_resumen, "Plan de ejecución por dataset", max_filas=8)
mostrar_tabla_compacta(
    method_dataset_profile,
    "Coste, muestreo y estabilidad por dataset-método",
    columnas=["dataset", "method", "mean_elapsed_seconds", "sample_applied", "mean_jaccard", "mean_selected_corr"],
    ordenar_por="mean_elapsed_seconds",
    ascendente=False,
    max_filas=12,
    formato={"mean_elapsed_seconds": numero, "mean_jaccard": numero, "mean_selected_corr": numero},
)
            """
        ),
        md_cell(
            """
            **Decisión.** La salida de métodos fallidos se conserva como evidencia negativa. En la ejecución actual no hay métodos fallidos ni warnings de método, por lo que la comparación puede apoyarse en todos los selectores registrados.
            """
        ),
        md_cell(
            """
            ## 5.5 Valores de k

            **Pregunta.** ¿Las reducciones de dimensionalidad son razonables para cada dataset?

            **Criterio metodológico.** Los valores de k se acotan por número de variables disponibles: no se exige el mismo k a Olive Oil que a Madelon. La figura se muestra aquí porque explica el diseño experimental, no al final como galería.
            """
        ),
        code_cell(
            """
k_values = artefactos["fs_k_values_by_dataset.csv"]
k_compacto = (
    k_values.groupby("dataset", as_index=False)
    .agg(n_features=("n_features", "max"), k_values=("k", lambda serie: ", ".join(map(str, sorted(serie.unique())))), max_reduction_pct=("reduction_pct", "max"))
)
mostrar_tabla_compacta(k_compacto, "Valores de k por dataset", max_filas=8, formato={"max_reduction_pct": lambda valor: f"{valor:.1f}%"})
mostrar_figura("results/figures/05_feature_selection/protocol/fs_k_reduction_plan.png", "Plan de k y reducción dimensional")
            """
        ),
        md_cell(
            """
            **Implicación para Fase 6.** Los subconjuntos con k pequeño permiten comparar modelos bajo reducción agresiva; los k cercanos a la dimensionalidad original sirven como control de sensibilidad.
            """
        ),
        md_cell(
            """
            ## 5.6 Muestreo para coste computacional

            **Pregunta.** ¿El control de coste altera de forma visible la distribución del target?

            **Criterio metodológico.** El muestreo solo se usa para métodos costosos y se registra. La representatividad se evalúa con diferencia máxima de proporciones del target.
            """
        ),
        code_cell(
            """
sampling = artefactos["fs_sampling_plan.csv"].merge(artefactos["fs_sampling_representativeness.csv"], on="dataset", how="left")
mostrar_tabla_compacta(
    sampling,
    "Muestreo y representatividad por dataset",
    columnas=["dataset", "sample_applied", "sample_size", "train_size", "max_abs_target_prop_diff", "justification"],
    max_filas=8,
    formato={"max_abs_target_prop_diff": porcentaje},
)
            """
        ),
        md_cell(
            """
            **Interpretación.** `customer_churn` es el único dataset con muestra estratificada por tamaño. La diferencia máxima de proporciones registrada es muy baja, pero los tiempos de sus métodos muestreados deben leerse como tiempos sobre muestra, no sobre train completo.
            """
        ),
        md_cell(
            """
            ## 5.7 y 5.8 Selección baseline y selección clásica completa

            **Pregunta.** ¿Qué métodos producen señal recurrente y qué variables aparecen repetidamente por dataset?

            **Criterio metodológico.** La baseline rápida se interpreta como referencia mínima. La selección completa incorpora métodos con distintas hipótesis para evitar que una sola familia dicte la narrativa.
            """
        ),
        code_cell(
            """
baseline = artefactos["fs_baseline_summary.csv"]
mostrar_tabla_compacta(
    baseline,
    "Resumen de baseline rápida",
    columnas=["dataset", "method", "mean_elapsed_seconds", "n_selected_rows"],
    ordenar_por="dataset",
    max_filas=15,
    formato={"mean_elapsed_seconds": numero},
)
mostrar_tabla_compacta(
    top_features_by_dataset,
    "Variables más recurrentes por dataset en selección completa",
    columnas=["dataset", "feature", "n_methods", "best_rank"],
    max_filas=20,
)
            """
        ),
        md_cell(
            """
            **Lectura por dataset.** En Breast Cancer predominan variables morfológicas correlacionadas; en `customer_churn` aparecen variables operativas de uso, soporte y contrato; en Madelon la selección debe leerse con cautela por alta dimensionalidad y ruido; en Olive Oil las variables químicas son pocas y tienden a repetirse entre métodos, por lo que la comparación relevante se desplaza hacia estabilidad y formulación del target.
            """
        ),
        code_cell(
            """
for dataset in dataset_summary["dataset"]:
    ruta = f"results/figures/05_feature_selection/top_features/{dataset}_top_selected_features.png"
    mostrar_figura(ruta, f"Variables recurrentes en {dataset}")
            """
        ),
        md_cell(
            """
            ## 5.9 Guardado tidy de rankings, subconjuntos y tiempos

            **Pregunta.** ¿Los resultados son trazables sin convertir el notebook en un inventario gigante?

            **Criterio metodológico.** El detalle completo permanece en CSV largos (`fs_all_rankings.csv`, `fs_all_selected_features.csv`, `fs_all_execution_times.csv`). El notebook solo muestra perfiles que ayudan a interpretar.
            """
        ),
        code_cell(
            """
trazabilidad = pd.DataFrame(
    [
        {"artefacto": "fs_all_rankings.csv", "filas": len(artefactos["fs_all_rankings.csv"]), "uso": "ranking largo por dataset, método, seed, k y variable"},
        {"artefacto": "fs_all_selected_features.csv", "filas": len(artefactos["fs_all_selected_features.csv"]), "uso": "subconjuntos seleccionados en formato trazable"},
        {"artefacto": "fs_all_execution_times.csv", "filas": len(artefactos["fs_all_execution_times.csv"]), "uso": "tiempos, muestra y estado por ejecución"},
        {"artefacto": "fs_phase6_input_recommendations.csv", "filas": len(phase6_recommendations), "uso": "entradas principales y auxiliares para Fase 6"},
    ]
)
mostrar_tabla_compacta(trazabilidad, "Artefactos largos preservados fuera del notebook", max_filas=8)
            """
        ),
        md_cell(
            """
            **Decisión.** No se muestran tablas largas de rankings en el notebook porque inducen lectura mecánica y duplican CSV. La evidencia completa queda guardada y recargable.
            """
        ),
        md_cell(
            """
            ## 5.10 Estabilidad por semillas

            **Pregunta.** ¿La selección depende de la semilla?

            **Criterio metodológico.** Jaccard mide solapamiento de subconjuntos; Kuncheva corrige el solapamiento esperado por azar. Baja estabilidad no descarta utilidad: puede indicar variables redundantes o soluciones alternativas.
            """
        ),
        code_cell(
            """
stability_dataset = (
    method_dataset_profile.groupby("dataset", as_index=False)
    .agg(mean_jaccard=("mean_jaccard", "mean"), min_jaccard=("mean_jaccard", "min"))
)
mostrar_tabla_compacta(stability_dataset, "Estabilidad media por dataset", max_filas=8, formato={"mean_jaccard": numero, "min_jaccard": numero})
mostrar_tabla_compacta(
    method_dataset_profile,
    "Métodos menos estables que conviene vigilar",
    columnas=["dataset", "method", "mean_jaccard", "mean_selected_corr"],
    ordenar_por="mean_jaccard",
    max_filas=12,
    formato={"mean_jaccard": numero, "mean_selected_corr": numero},
)
            """
        ),
        md_cell(
            """
            **Implicación para Fase 6.** Los métodos estables son candidatos naturales para la parrilla inicial. Los métodos menos estables pueden mantenerse como sensibilidad si el rendimiento de validación compensa esa incertidumbre.
            """
        ),
        md_cell(
            """
            ## 5.11 Permutaciones del target

            **Pregunta.** ¿Los scores reales superan una referencia nula simple?

            **Criterio metodológico.** Se compara el score real con una distribución nula generada permutando `y_train`. Con 20 permutaciones, la evidencia es aproximada y sirve como diagnóstico, no como prueba definitiva.
            """
        ),
        code_cell(
            """
mostrar_tabla_compacta(
    permutation,
    "Resumen de variables por encima del p95 nulo",
    columnas=["dataset", "method", "n_features_above_null", "median_empirical_p_value", "n_permutations"],
    max_filas=12,
    formato={"median_empirical_p_value": numero},
)
mostrar_figura("results/figures/05_feature_selection/permutation/fs_permutation_above_null_heatmap.png", "Permutaciones: score real frente a nulo")
            """
        ),
        md_cell(
            """
            **Interpretación.** Breast Cancer, Churn y Olive Oil muestran más variables por encima del nulo que Madelon en varios métodos. En Madelon la señal existe, pero se reparte en un espacio de 500 variables y debe validarse con modelos posteriores.
            """
        ),
        md_cell(
            """
            ## 5.12 Redundancia interna de subconjuntos

            **Pregunta.** ¿La selección reduce información repetida o conserva bloques redundantes?

            **Criterio metodológico.** Se compara correlación media/máxima de subconjuntos contra el conjunto completo. La redundancia no es siempre mala, pero puede inflar interpretaciones de importancia.
            """
        ),
        code_cell(
            """
redundancy_principal = principal_phase6.merge(
    redundancy,
    on=["dataset", "method", "k"],
    how="left",
)
mostrar_tabla_compacta(
    redundancy_principal,
    "Redundancia en subconjuntos principales para Fase 6",
    columnas=["dataset", "method", "k", "selected_mean_abs_corr", "selected_max_abs_corr", "selected_high_corr_pairs", "full_high_corr_pairs"],
    ordenar_por="selected_mean_abs_corr",
    ascendente=False,
    max_filas=20,
    formato={"selected_mean_abs_corr": numero, "selected_max_abs_corr": numero},
)
            """
        ),
        md_cell(
            """
            **Riesgo residual.** Si un subconjunto tiene alta correlación interna, Fase 6 debe valorar si el rendimiento justifica esa redundancia o si conviene preferir métodos de relevancia-redundancia.
            """
        ),
        md_cell(
            """
            ## 5.13 Cruce con EDA y señales sospechosas

            **Pregunta.** ¿La selección contradice o complementa la evidencia estadística previa?

            **Criterio metodológico.** Una variable sin señal univariante previa puede ser útil multivariadamente; por tanto, el cruce con EDA informa riesgos, no borra variables automáticamente.
            """
        ),
        code_cell(
            """
evidence = evidence_map.copy()
coverage_dataset = evidence.groupby("dataset", as_index=False).agg(mean_evidence_coverage=("evidence_coverage", "mean"), max_evidence_coverage=("evidence_coverage", "max"))
mostrar_tabla_compacta(coverage_dataset, "Cobertura media de evidencia previa por dataset", max_filas=8, formato={"mean_evidence_coverage": porcentaje, "max_evidence_coverage": porcentaje})
display(Markdown(f"**Variables sospechosas seleccionadas:** {len(artefactos['fs_suspicious_selected_features.csv'])}."))
            """
        ),
        md_cell(
            """
            **Interpretación.** El cruce con EDA no encuentra variables sospechosas seleccionadas. La baja cobertura de evidencia previa en algunos subconjuntos se interpreta con cautela: puede reflejar señal multivariante o limitaciones del mapeo entre nombres transformados y evidencia de fases tempranas.
            """
        ),
        md_cell(
            """
            ## 5.14 Datasets reducidos para Fase 6

            **Pregunta.** ¿Qué debe consumir Fase 6 y qué queda como material auxiliar?

            **Criterio metodológico.** Los directorios `principal_para_modelado` forman una parrilla inicial compacta. El resto de subconjuntos se conserva para sensibilidad, ablación o apéndice; no se reajustan selectores en Fase 6.
            """
        ),
        code_cell(
            """
mostrar_tabla_compacta(
    principal_profile,
    "Subconjuntos principales recomendados para Fase 6",
    columnas=["dataset", "method", "k", "path", "mean_jaccard", "mean_selected_corr", "riesgo_residual"],
    max_filas=25,
    formato={"mean_jaccard": numero, "mean_selected_corr": numero},
)
consistency = artefactos["fs_column_consistency_check.csv"]
consistency_summary = consistency.groupby("dataset", as_index=False).agg(all_columns_exist=("all_columns_exist", "all"), same_order=("same_order_train_validation_test", "all"), no_extra_columns=("no_extra_columns", "all"))
mostrar_tabla_compacta(consistency_summary, "Consistencia de columnas en datasets reducidos", max_filas=8)
            """
        ),
        md_cell(
            """
            **Decisión.** Fase 6 debe partir de `fs_phase6_input_recommendations.csv`: cuatro métodos principales por dataset para una primera comparación, manteniendo todos los artefactos auxiliares disponibles sin mezclarlos con la parrilla principal.
            """
        ),
        md_cell(
            """
            ## 5.15 Comparación narrativa y visual

            **Pregunta.** ¿Qué métodos parecen más útiles por dataset antes de modelar?

            **Criterio metodológico.** La utilidad se lee como equilibrio entre coste, estabilidad, redundancia y evidencia nula, no como rendimiento predictivo final. El rendimiento se decide en Fase 6.
            """
        ),
        code_cell(
            """
mostrar_tabla_compacta(
    dataset_method_reading,
    "Lectura de métodos principales por dataset",
    columnas=["dataset", "method", "k", "mean_jaccard", "mean_selected_corr", "lectura", "cautela_redundancia"],
    max_filas=25,
    formato={"mean_jaccard": numero, "mean_selected_corr": numero},
)
mostrar_figura("results/figures/05_feature_selection/summary/fs_method_profiles_summary.png", "Perfil global de métodos: coste, estabilidad y redundancia")
for dataset in dataset_summary["dataset"]:
    ruta = f"results/figures/05_feature_selection/method_feature_heatmaps/{dataset}_method_feature_heatmap.png"
    mostrar_figura(ruta, f"Coincidencia método-variable en {dataset}")
mostrar_figura("results/figures/05_feature_selection/visual_review_sheet/fs_visual_review_sheet.png", "Lámina de revisión visual de candidatas para memoria")
            """
        ),
        md_cell(
            """
            **Lectura prudente.** `f_classif` y `mutual_info` son referencias fuertes por coste y señal marginal; `mrmr_approx` aporta control de redundancia con menor estabilidad; `random_forest` añade una lectura embedded útil, pero dependiente de modelo; `variance` queda como baseline no supervisada y no debe interpretarse como evidencia de relación con el target.
            """
        ),
        md_cell(
            """
            ## 5.16 Cierre, checklist y handoff

            **Pregunta.** ¿La fase queda lista para modelado sin perder cautelas?

            **Criterio metodológico.** El cierre no elige modelos. Entrega subconjuntos, riesgos y una parrilla compacta para que Fase 6 evalúe rendimiento sin contaminar validation/test.
            """
        ),
        code_cell(
            """
mostrar_tabla_compacta(artefactos["fs_phase5_final_checklist.csv"], "Checklist final de Fase 5", max_filas=20)
mostrar_tabla_compacta(artefactos["fs_phase5_handoff_to_phase6.csv"], "Handoff resumido a Fase 6", max_filas=8)
mostrar_tabla_compacta(artefactos["fs_phase5_open_issues.csv"], "Incidencias y cautelas abiertas", max_filas=8)
            """
        ),
        md_cell(
            """
            **Implicación final.** La Fase 5 queda como baseline clásica trazable. Fase 6 debe evaluar si la estabilidad y la reducción dimensional observadas se traducen en rendimiento robusto, manteniendo separadas las dos formulaciones de Olive Oil y tratando `customer_churn` con su cautela de codificación train-only.
            """
        ),
    ]

    nb["cells"] = cells
    NOTEBOOK_PATH.write_text(nbf.writes(nb), encoding="utf-8")


def write_reconstruction_audit() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(
        """
# Auditoría de reconstrucción narrativa - Fase 5

## Secciones corregidas

- Se sustituyó el patrón repetitivo `Objetivo/Evidencia/Decisión/Revisión` por preguntas científicas específicas en 5.1-5.16.
- Se movieron las figuras a las secciones donde explican el diseño o la interpretación: k en 5.5, permutaciones en 5.11, variables recurrentes en 5.7-5.8 y síntesis visual en 5.15.
- Se separaron explícitamente evidencia, interpretación, decisión e implicación para Fase 6 en texto narrativo.

## Tablas resumidas

- Se reemplazó la exposición directa de CSV largos por vistas compactas derivadas en memoria.
- El detalle completo se preserva en `results/tables/05_feature_selection/`.
- Las vistas principales son: dimensionalidad por dataset, familias de métodos, plan de ejecución, k por dataset, muestreo, variables recurrentes, estabilidad, permutaciones, redundancia y recomendaciones para Fase 6.

## `.head()` eliminados o justificados

- El notebook reconstruido no usa `.head()` como evidencia principal.
- Las vistas compactas usan una función explícita `mostrar_tabla_compacta`, que informa cuántas filas existen en el CSV completo y cuántas se muestran.

## Figuras recolocadas/rediseñadas

- No se rediseñaron métricas ni figuras guardadas para no alterar resultados.
- Se recolocaron figuras existentes en el argumento narrativo.
- La lámina de revisión visual se conserva como síntesis, y los heatmaps densos permanecen como apéndice auditado.

## Criterios metodológicos explicitados

- Contrato train-only.
- Separación de `olive_oil_3class` y `olive_oil_9class`.
- Interpretación de familias de métodos.
- Justificación de k, muestreo, semillas, estabilidad, permutaciones y redundancia.
- Distinción entre `principal_para_modelado` y `auxiliar_exploratorio` en Fase 6.

## Conclusiones preservadas

- No se cambiaron métricas, rankings, datasets reducidos ni rutas de artefactos.
- La interpretación sigue siendo prudente: la utilidad predictiva final queda para Fase 6.

## Artefactos preservados

- CSV completos en `results/tables/05_feature_selection/`.
- Figuras en `results/figures/05_feature_selection/`.
- Datasets reducidos en `data/selected_features/`.
- Informes Markdown/LaTeX y handoff existentes.

## Incidencias abiertas

- El notebook depende de artefactos previos: si se borran CSV o figuras, se detiene con error explícito.
- La auditoría visual final debe revisarse también en el PDF/visor humano de la memoria.
- Fase 6 debe validar rendimiento; Fase 5 no declara un selector óptimo.

## Limpieza final de presentación

- Se eliminaron rutas absolutas de tablas visibles y se sustituyeron por rutas relativas cuando la ruta aporta trazabilidad.
- Se limitaron las vistas compactas a ocho columnas por defecto para reducir roturas en PDF.
- Se truncaron textos largos en columnas narrativas o de ruta sin modificar los CSV completos.
- Se evitó una construcción de pandas sensible a avisos futuros y se mantuvo la misma lectura agregada.
- Las 14 figuras auditadas se muestran en el notebook con tamaño fijo legible, ancho responsive y texto alternativo; los ficheros originales no se modificaron.
- La comprobación final de presentación exporta HTML/PDF desde el notebook ejecutado para revisar warnings, tablas, rutas visibles y legibilidad.
- Esta pasada no cambió métricas, rankings, datasets reducidos, rutas de artefactos guardados ni conclusiones científicas.
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_report_addendum() -> None:
    md_path = REPORT_DIR / "fase5_feature_selection_report.md"
    tex_path = REPORT_DIR / "fase5_feature_selection_report.tex"
    md_marker = "## Reconstrucción narrativa del notebook"
    md_addendum = """
## Reconstrucción narrativa del notebook

El notebook de Fase 5 se reorganizó como lectura científica de los artefactos ya ejecutados. La reconstrucción no cambia métricas, rankings, datasets reducidos ni rutas; evita usar `.head()` como evidencia principal y muestra vistas compactas derivadas en memoria.

La interpretación queda organizada por pregunta: contrato train-only, familias de métodos, valores de k, muestreo, selección completa, estabilidad, permutaciones, redundancia, cruce con EDA y entrega a Fase 6. Las figuras se muestran junto a la decisión que apoyan y los heatmaps densos quedan como apéndice auditado.

Para Fase 6, la tabla `fs_phase6_input_recommendations.csv` distingue los subconjuntos `principal_para_modelado` de los `auxiliar_exploratorio`; todos conservan el riesgo residual de validar rendimiento sin reajustar selectores.
""".strip()
    if md_path.exists():
        md_text = md_path.read_text(encoding="utf-8")
        if md_marker not in md_text:
            md_path.write_text(md_text.rstrip() + "\n\n" + md_addendum + "\n", encoding="utf-8")
    tex_marker = r"\subsection{Reconstrucción narrativa del notebook}"
    tex_addendum = r"""
\subsection{Reconstrucción narrativa del notebook}

El notebook de Fase 5 se reorganizó como lectura científica de los artefactos ya ejecutados. La reconstrucción no cambia métricas, rankings, datasets reducidos ni rutas; evita usar \texttt{.head()} como evidencia principal y muestra vistas compactas derivadas en memoria.

La interpretación queda organizada por pregunta: contrato train-only, familias de métodos, valores de k, muestreo, selección completa, estabilidad, permutaciones, redundancia, cruce con EDA y entrega a Fase 6. Las figuras se muestran junto a la decisión que apoyan y los heatmaps densos quedan como apéndice auditado.

Para Fase 6, la tabla \texttt{fs\_phase6\_input\_recommendations.csv} distingue los subconjuntos \texttt{principal\_para\_modelado} de los \texttt{auxiliar\_exploratorio}; todos conservan el riesgo residual de validar rendimiento sin reajustar selectores.
""".strip()
    if tex_path.exists():
        tex_text = tex_path.read_text(encoding="utf-8")
        if tex_marker not in tex_text:
            tex_path.write_text(tex_text.rstrip() + "\n\n" + tex_addendum + "\n", encoding="utf-8")
        plantilla = Path("Plantilla_Latex_GCD/tfgs/tex/resultados_fase5.tex")
        if plantilla.parent.exists():
            plantilla.write_text(tex_path.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    build_notebook()
    write_reconstruction_audit()
    write_report_addendum()
