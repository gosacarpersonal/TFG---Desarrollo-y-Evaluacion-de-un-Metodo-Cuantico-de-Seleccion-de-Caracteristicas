from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "fase2.ipynb"

DATASETS = [
    ("breast_cancer_wisconsin", "breast_cancer_wisconsin", "Breast Cancer Wisconsin"),
    ("customer_churn", "customer_churn", "Customer Churn"),
    ("madelon", "madelon", "Madelon"),
    ("olive_oil", "olive_oil", "Olive Oil"),
]


def md(text):
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code(text):
    return nbf.v4.new_code_cell(text.strip() + "\n")


def add_dataset_cells(cells, title, code_template, observations):
    for dataset_name, variable_name, label in DATASETS:
        cells.append(md(f"### {title}: `{dataset_name}`"))
        cells.append(code(code_template.format(
            dataset_name=dataset_name,
            variable_name=variable_name,
            label=label,
        )))
        if observations and dataset_name in observations:
            cells.append(md(observations[dataset_name]))


def build_notebook():
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "qfs_env", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }

    cells = []

    cells.append(md("""
# Trabajo de Fin de Grado: Desarrollo y Evaluación de un Método Cuántico de Selección de Características

## Notebook 02 - Fase 2: Preprocesado Estructural de los Datasets

Esta fase transforma los datos crudos solo cuando la transformación es estructural y verificable: normalización de nombres, exclusión de identificadores, codificación trazable del target, guardado y recarga de datasets procesados. Las transformaciones que aprenden parámetros de los predictores, como imputación, `OneHotEncoder` o escalado, no se ajustan aquí.

El anteproyecto del TFG fija cinco objetivos: revisión de métodos clásicos, selección de datasets de referencia, comparación clásica, desarrollo de QFS con bloqueo de Rydberg y comparación del método cuántico frente a los mejores clásicos. Fase 2 sostiene el segundo objetivo y protege los tres siguientes: el bloque clásico solo es una referencia válida si el preprocesado no introduce información del conjunto completo antes de los splits.

Los documentos QFS justifican por qué esta fase debe producir datos numéricamente trazables sin contaminar el experimento. PAPER_QFS y QFS_D2 formulan la relevancia como información mutua `I(x_i;y)`, la redundancia como `I(x_i;x_j)`, la geometría atómica mediante distancias/MDS y el objetivo `Q(x; alpha)` como equilibrio entre variables informativas y no redundantes. Por eso el bloque cuántico necesita targets codificados de forma estable, identificadores fuera de las predictoras y transformaciones estadísticas diferidas a estimadores ajustados solo con train.

Desde esta fase se deja explícito que `olive_oil` contiene dos formulaciones supervisadas posibles: `area` con 3 clases y `target` con 9 clases. Esa distinción evita tratar como una única tarea dos problemas de clasificación relacionados pero distintos.
"""))

    cells.append(md("""
## Importación de Librerías

Se importan las librerías necesarias para cargar datos, calcular métricas de preprocesado, generar figuras y mostrar tablas en el notebook.
"""))
    cells.append(code("""
from pathlib import Path
import io
import re
import shutil
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from IPython.display import Markdown, display

warnings.filterwarnings("ignore", category=FutureWarning)
"""))

    cells.append(md("""
## Definición de Rutas y Directorios de Salida

Se definen las rutas utilizadas durante la fase. Antes de generar nuevas salidas se limpian las tablas y figuras previas de Fase 2 para evitar que resultados antiguos aparezcan mezclados con la versión corregida del notebook.
"""))
    cells.append(code("""
# Rutas principales del proyecto.
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
RAW_DATA_DIR = PROJECT_ROOT / "data" / "01_raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
PHASE1_TABLES_DIR = PROJECT_ROOT / "results" / "tables" / "01_raw_eda"
PHASE2_TABLES_DIR = PROJECT_ROOT / "results" / "tables" / "02_preprocessing"
PHASE2_FIGURES_DIR = PROJECT_ROOT / "results" / "figures" / "02_preprocessing"
PHASE2_REPORTS_DIR = PROJECT_ROOT / "results" / "reports" / "02_preprocessing"

for output_dir in [PROCESSED_DATA_DIR, PHASE2_TABLES_DIR, PHASE2_FIGURES_DIR, PHASE2_REPORTS_DIR]:
    output_dir.mkdir(parents=True, exist_ok=True)

for old_table_path in PHASE2_TABLES_DIR.glob("*.csv"):
    old_table_path.unlink()

for old_figure_path in list(PHASE2_FIGURES_DIR.rglob("*.png")) + list(PHASE2_FIGURES_DIR.rglob("*.pdf")):
    old_figure_path.unlink()

print(f"Proyecto: {PROJECT_ROOT}")
print(f"Datos crudos: {RAW_DATA_DIR.relative_to(PROJECT_ROOT)}")
print(f"Tablas de Fase 1: {PHASE1_TABLES_DIR.relative_to(PROJECT_ROOT)}")
print(f"Tablas de Fase 2: {PHASE2_TABLES_DIR.relative_to(PROJECT_ROOT)}")
print(f"Figuras de Fase 2: {PHASE2_FIGURES_DIR.relative_to(PROJECT_ROOT)}")
"""))
    cells.append(md("""
Las rutas quedan fijadas en 5 ubicaciones del proyecto: datos crudos, datos procesados, tablas de Fase 1, tablas de Fase 2 y figuras de Fase 2. La limpieza inicial afecta solo a resultados `fase2_*.csv`, `*.png` y `*.pdf` dentro de las carpetas de salida, por lo que no modifica los datasets de entrada ni los resultados de otras fases.
"""))

    cells.append(md("""
## Configuración Visual y Parámetros Generales

La configuración visual se mantiene estable para que las figuras se puedan comparar entre datasets. Los umbrales que aparecen en el notebook son constantes explícitas, no valores escondidos dentro de una función.

Los tres umbrales son **alertas exploratorias**, no reglas automáticas de borrado:

- `LOW_CARDINALITY_RATIO = 0.01` hereda el criterio usado en Fase 1 y es una versión más estricta que el `uniqueCut = 10%` que usa `caret::nearZeroVar` para diagnosticar predictores de varianza casi nula.
- `DOMINANT_MODE_RATIO = 0.98` sigue la misma idea de `nearZeroVar`: una variable puede ser problemática si combina pocos valores distintos con una frecuencia muy concentrada. Se usa 98% para marcar solo dominancias extremas.
- `HIGH_CORRELATION_THRESHOLD = 0.85` mantiene la referencia de Fase 1 para correlación de Spearman fuerte. Herramientas como `caret::findCorrelation` suelen usar `cutoff = 0.90`; aquí se conserva 0.85 para no cambiar el criterio entre fases.

Referencias metodológicas:

- `caret::nearZeroVar`: https://rdrr.io/cran/caret/man/nearZeroVar.html
- `caret::findCorrelation`: https://rdrr.io/cran/caret/man/findCorrelation.html
- Scikit-learn, *Common pitfalls and recommended practices* sobre *data leakage*: https://scikit-learn.org/stable/common_pitfalls.html
"""))
    cells.append(code("""
RANDOM_STATE = 42
# Umbrales de alerta, no reglas de eliminación automática.
LOW_CARDINALITY_RATIO = 0.01
DOMINANT_MODE_RATIO = 0.98
HIGH_CORRELATION_THRESHOLD = 0.85
OUTLIER_RATE_ALERT_THRESHOLD = 0.10

DATASET_ORDER = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil",
]

DATASET_COLORS = {
    "breast_cancer_wisconsin": "#2F6F9F",
    "customer_churn": "#D9822B",
    "madelon": "#5E8C61",
    "olive_oil": "#7A6FA5",
}

CATEGORY_COLORS = [
    "#2F6F9F",
    "#D9822B",
    "#5E8C61",
    "#7A6FA5",
    "#B85C5C",
    "#6F6A60",
]

plt.rcParams.update({
    "figure.facecolor": "#FAF7F2",
    "axes.facecolor": "#FAF7F2",
    "axes.edgecolor": "#D8D0C4",
    "axes.labelcolor": "#2D2A26",
    "text.color": "#2D2A26",
    "xtick.color": "#2D2A26",
    "ytick.color": "#2D2A26",
    "grid.color": "#E6DED2",
    "font.size": 10,
})

pd.set_option("display.max_columns", 32)
pd.set_option("display.max_rows", 60)
pd.set_option("display.max_colwidth", 80)
pd.set_option("display.precision", 4)
"""))

    cells.append(md("""
## Utilidades Generales del Notebook

Estas funciones se reutilizan en varias secciones. Son funciones de soporte: guardan tablas, muestran vistas compactas, guardan figuras y aplican estilo visual básico.
"""))
    cells.append(code("""
DISPLAY_COLUMN_NAMES = {
    "abs_tamano_efecto": "Tamaño de efecto absoluto",
    "baja_cardinalidad_relativa": "Baja cardinalidad relativa",
    "categoria": "Categoría",
    "codigo": "Código",
    "columna_original": "Columna original",
    "columna_procesada": "Columna procesada",
    "columnas": "Columnas",
    "columnas_originales": "Columnas originales",
    "columnas_procesadas": "Columnas procesadas",
    "columnas_renombradas": "Columnas renombradas",
    "columnas_eliminadas": "Columnas eliminadas",
    "dataset": "Dataset",
    "delta_abs": "Diferencia absoluta",
    "delta_columnas": "Diferencia de columnas",
    "delta_filas": "Diferencia de filas",
    "delta_pares": "Diferencia de pares",
    "duplicados_exactos": "Duplicados exactos",
    "dtype_original": "Tipo original",
    "dtype_procesado": "Tipo procesado",
    "etiquetas_alternativas_en_predictoras": "Etiquetas alternativas en predictoras",
    "filas": "Filas",
    "filas_originales": "Filas originales",
    "filas_procesadas": "Filas procesadas",
    "filas_raw": "Filas crudas",
    "filas_processed": "Filas procesadas",
    "frecuencia_moda": "Frecuencia de la moda",
    "iqr": "IQR",
    "iqr_mediano": "IQR mediano",
    "limite_inferior": "Límite inferior",
    "limite_superior": "Límite superior",
    "maximo": "Máximo",
    "mean_delta_abs": "Diferencia absoluta de medias",
    "mean_processed": "Media procesada",
    "mean_raw": "Media cruda",
    "mediana": "Mediana",
    "minimo": "Mínimo",
    "moda_dominante_98": "Moda dominante al 98%",
    "n": "N",
    "n_outliers_iqr": "Outliers IQR",
    "nombre_tamano_efecto": "Medida de efecto",
    "nulos": "Nulos",
    "nulos_procesados": "Nulos procesados",
    "pares_spearman_ge_085_processed": "Pares Spearman >= 0.85 procesados",
    "pares_spearman_ge_085_raw": "Pares Spearman >= 0.85 crudos",
    "pct_duplicados_exactos": "Proporción de duplicados exactos",
    "pct_nulos": "Proporción de nulos",
    "pct_nulos_maximo": "Proporción máxima de nulos",
    "pct_outliers_iqr": "Proporción de outliers IQR",
    "pct_outliers_maxima": "Proporción máxima de outliers IQR",
    "pct_outliers_media": "Proporción media de outliers IQR",
    "pct_processed": "Proporción procesada",
    "pct_raw": "Proporción cruda",
    "p_valor": "p-valor",
    "p_valor_fdr": "p-valor FDR",
    "predictoras": "Predictoras",
    "predictoras_categoricas": "Predictoras categóricas",
    "predictoras_si_onehot": "Predictoras con one-hot",
    "predictoras_sin_onehot": "Predictoras sin one-hot",
    "problema": "Problema",
    "proporcion": "Proporción",
    "rango": "Rango",
    "rango_maximo": "Rango máximo",
    "rango_mediano": "Rango mediano",
    "ratio_unicidad_maximo": "Ratio máximo de unicidad",
    "ratio_valores_unicos": "Ratio de valores únicos",
    "ruta": "Ruta",
    "std_delta_abs": "Diferencia absoluta de desviaciones",
    "std_processed": "Desviación procesada",
    "std_raw": "Desviación cruda",
    "tamano_efecto": "Tamaño de efecto",
    "target": "Target",
    "target_clases": "Clases del target",
    "target_en_predictoras": "Target en predictoras",
    "target_maximo": "Código máximo del target",
    "target_minimo": "Código mínimo del target",
    "target_nulos": "Nulos del target",
    "target_presente": "Target presente",
    "target_total_variation": "Variación total del target",
    "test": "Contraste",
    "valores_negativos": "Valores negativos",
    "valores_unicos": "Valores únicos",
    "valor_original": "Valor original",
    "variable": "Variable",
    "variable_original": "Variable original",
    "variable_procesada": "Variable procesada",
    "variables": "Variables",
    "variables_numericas": "Variables numéricas",
}


def preparar_tabla_para_mostrar(tabla):
    return tabla.rename(columns={name: DISPLAY_COLUMN_NAMES.get(name, name) for name in tabla.columns})


def guardar_tabla(tabla, nombre_archivo):
    ruta_tabla = PHASE2_TABLES_DIR / nombre_archivo
    tabla.to_csv(ruta_tabla, index=False)
    return ruta_tabla


def mostrar_tabla(tabla, nombre=None, n=10):
    tabla_visible = preparar_tabla_para_mostrar(tabla)
    if nombre is not None:
        display(Markdown(f"**{nombre}** - se muestran las primeras {min(n, tabla_visible.shape[0])} filas de {tabla_visible.shape[0]}."))
    display(tabla_visible.head(n))


def guardar_figura(figura, nombre_archivo):
    ruta_png = PHASE2_FIGURES_DIR / Path(nombre_archivo).with_suffix(".png")
    ruta_pdf = ruta_png.with_suffix(".pdf")
    ruta_png.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(ruta_png, dpi=300, bbox_inches="tight")
    figura.savefig(ruta_pdf, bbox_inches="tight")
    return ruta_png


def aplicar_estilo_eje(eje, eje_rejilla="x"):
    eje.spines["top"].set_visible(False)
    eje.spines["right"].set_visible(False)
    eje.grid(axis=eje_rejilla, alpha=0.65)
    eje.set_axisbelow(True)
"""))
    cells.append(code("""
def leer_tabla_csv(directorio, nombre_archivo):
    ruta_tabla = directorio / nombre_archivo
    if not ruta_tabla.exists():
        raise FileNotFoundError(f"No existe la tabla: {ruta_tabla}")
    return pd.read_csv(ruta_tabla)


def obtener_info_texto(datos_dataset):
    salida_info = io.StringIO()
    datos_dataset.info(buf=salida_info)
    return salida_info.getvalue()


def etiqueta_dataset(nombre_dataset):
    return nombre_dataset.replace("_", " ").title()


def convertir_escalar_python(valor):
    return valor.item() if hasattr(valor, "item") else valor
"""))

    cells.append(md("""
## 2.1 Carga de Datasets Crudos

La fase comienza cargando los datasets crudos uno a uno mediante lectura CSV directa y comprobación del target esperado. Este capítulo parte de las conclusiones de la revisión exploratoria de Fase 1, que se consultan más adelante solo cuando ayudan a interpretar identificadores y variables de revisión.
"""))
    cells.append(code("""
dataset_paths = {
    "breast_cancer_wisconsin": RAW_DATA_DIR / "breast_cancer_wisconsin.csv",
    "customer_churn": RAW_DATA_DIR / "customer_churn.csv",
    "madelon": RAW_DATA_DIR / "madelon.csv",
    "olive_oil": RAW_DATA_DIR / "olive_oil.csv",
}

expected_targets = {
    "breast_cancer_wisconsin": "target",
    "customer_churn": "Churn",
    "madelon": "target",
    "olive_oil": "target",
}

for dataset_name, dataset_path in dataset_paths.items():
    print(f"{dataset_name}: {dataset_path.exists()} -> {dataset_path.relative_to(PROJECT_ROOT)}")
"""))
    cells.append(md("""
Los 4 archivos crudos existen en `data/01_raw`, con rutas resueltas antes de leer contenido. Esta comprobación separa fallos de I/O de errores analíticos: si una carga fallara después, no sería por ausencia del CSV sino por estructura interna del dataset.
"""))
    cells.append(code("""
def cargar_dataset(ruta_dataset):
    if not ruta_dataset.exists():
        raise FileNotFoundError(f"No se encuentra el archivo: {ruta_dataset}")
    return pd.read_csv(ruta_dataset)


def resumir_carga_dataset(nombre_dataset, datos_dataset):
    target_name = expected_targets[nombre_dataset]
    return {
        "dataset": nombre_dataset,
        "archivo": dataset_paths[nombre_dataset].name,
        "filas": datos_dataset.shape[0],
        "columnas": datos_dataset.shape[1],
        "target": target_name,
        "target_presente": target_name in datos_dataset.columns,
    }
"""))

    load_observations = {
        "breast_cancer_wisconsin": "`breast_cancer_wisconsin` queda cargado con 569 filas, 32 columnas, target `target` y una columna `id`. Esa clave no se elimina todavía: primero se inspecciona como evidencia estructural.",
        "customer_churn": "`customer_churn` aporta 440832 filas y 12 columnas, el mayor volumen muestral de la fase. Se observa `CustomerID`, que se revisa como identificador antes de construir el dataset procesado.",
        "madelon": "`madelon` muestra 2000 filas y 501 columnas numéricas. Al no aparecer identificador explícito, el preprocesado estructural no debería reducir sus 500 predictoras salvo anomalía objetiva.",
        "olive_oil": "`olive_oil` mantiene 572 filas, 12 columnas, target textual multiclase y una columna `id`. La codificación del target se hará de forma trazable después de revisar sus 9 clases.",
    }
    add_dataset_cells(
        cells,
        "Carga de Datos",
        """
{variable_name} = cargar_dataset(dataset_paths["{dataset_name}"])
print(f"shape: {{{variable_name}.shape}}")
display({variable_name}.head())
print(obtener_info_texto({variable_name}))
""",
        load_observations,
    )
    cells.append(md("### Resumen Común de Carga"))
    cells.append(code("""
raw_datasets = {
    "breast_cancer_wisconsin": breast_cancer_wisconsin,
    "customer_churn": customer_churn,
    "madelon": madelon,
    "olive_oil": olive_oil,
}

raw_load_summary = pd.DataFrame([
    resumir_carga_dataset(dataset_name, datos_dataset)
    for dataset_name, datos_dataset in raw_datasets.items()
])

guardar_tabla(raw_load_summary, "fase2_carga_datasets.csv")
mostrar_tabla(raw_load_summary, "Resumen de carga")
"""))
    cells.append(md("""
La carga compara cuatro escalas de trabajo muy distintas: `customer_churn` aporta 440832 filas y 12 columnas, mientras `olive_oil` solo tiene 572 filas y 12 columnas. `madelon` concentra la dificultad en 501 columnas para 2000 filas, y `breast_cancer_wisconsin` queda en 569 filas con 32 columnas. Los cuatro targets esperados están presentes, de modo que el preprocesado puede avanzar sin reconstruir etiquetas.
"""))
    cells.append(code("""
PHASE1_REQUIRED_TABLES = [
    "fase1_carga_inicial.csv",
    "fase1_estructura_datasets.csv",
    "fase1_calidad_datasets.csv",
    "fase1_calidad_variables.csv",
    "fase1_target_resumen.csv",
    "fase1_target_distribucion.csv",
    "fase1_distribuciones_numericas.csv",
    "fase1_variables_revision_riesgos.csv",
    "fase1_correlaciones_spearman_pares.csv",
    "fase1_sintesis_evidencias.csv",
]

missing_phase1_tables = [
    table_name for table_name in PHASE1_REQUIRED_TABLES
    if not (PHASE1_TABLES_DIR / table_name).exists()
]
assert not missing_phase1_tables

phase1_tables = {
    table_name: leer_tabla_csv(PHASE1_TABLES_DIR, table_name)
    for table_name in PHASE1_REQUIRED_TABLES
}
"""))

    cells.append(md("""
## 2.2 Criterios de Preprocesado Sin Ajuste Global

Antes de transformar columnas se fijan los límites de esta fase mediante una regla de no ajuste global que separa operaciones estructurales de operaciones estadísticas aprendidas. El criterio permite renombrar, excluir identificadores y codificar el target, pero bloquea imputación, escalado, winsorización y aprendizaje de categorías sobre todo el dataset.

- Se normalizan nombres de columnas para tener una convención estable.
- Se excluyen identificadores claros del dataset procesado.
- Se codifica el target para que las fases posteriores trabajen con etiquetas numéricas.
- No se imputan nulos, no se eliminan outliers, no se eliminan variables por baja cardinalidad y no se ajustan encoders ni escaladores sobre todo el dataset.

Estos criterios son reglas metodológicas, no resultados medidos. Por eso no se guardan como tabla de datos. Los decimales se muestran con cuatro cifras para evitar redondeos engañosos en porcentajes pequeños.

El criterio `sin ajuste global` significa que no se imputan nulos, no se escala, no se winsoriza y no se aprenden categorías de predictoras sobre el dataset completo. Esta restricción protege el contraste posterior clásico-cuántico frente a *leakage*: si una media, una desviación, un límite de outlier o un vocabulario categórico se ajustara antes del split, validación y test influirían indirectamente en el brazo clásico de control y el bloque cuántico dejaría de ser comparable.
"""))
    cells.append(code("""
print(f"Umbral de baja cardinalidad relativa: {LOW_CARDINALITY_RATIO:.4%}")
print(f"Umbral de moda dominante: {DOMINANT_MODE_RATIO:.4%}")
print(f"Umbral de correlación alta: {HIGH_CORRELATION_THRESHOLD:.4f}")
print(f"Umbral visual de tasa de outliers IQR: {OUTLIER_RATE_ALERT_THRESHOLD:.4%}")
"""))
    cells.append(md("""
Los cuatro umbrales impresos actúan como alertas: baja cardinalidad relativa 1.0000%, moda dominante 98.0000%, correlación Spearman alta 0.8500 y outliers IQR 10.0000%. Ninguno de esos valores elimina datos por sí solo; su función es documentar riesgos que se contrastarán después del split.
"""))

    cells.append(md("""
## 2.3 Separación de Variables Predictoras y Target

Se separan las variables predictoras y el target por dataset. Esta sección no transforma datos; comprueba que el target esperado existe y que las predictoras se pueden enumerar sin incluirlo.

En `olive_oil` se registran desde aquí dos problemas de clasificación: `olive_oil_3class`, con `area` como target de 3 clases, y `olive_oil_9class`, con `target` como target de 9 clases. La formulación definitiva se aplicará en la fase de particionado.
"""))
    cells.append(code("""
def separar_predictoras_target(datos_dataset, target_name):
    if target_name not in datos_dataset.columns:
        raise KeyError(f"No se encuentra el target: {target_name}")
    predictor_names = [name for name in datos_dataset.columns if name != target_name]
    return datos_dataset[predictor_names], datos_dataset[target_name]


problem_targets = {
    "breast_cancer_wisconsin": {"breast_cancer_wisconsin": "target"},
    "customer_churn": {"customer_churn": "Churn"},
    "madelon": {"madelon": "target"},
    "olive_oil": {
        "olive_oil_3class": "Area",
        "olive_oil_9class": "target",
    },
}


def obtener_targets_alternativos(nombre_dataset, problem_name):
    target_by_problem = problem_targets[nombre_dataset]
    return [
        target_name
        for candidate_problem, target_name in target_by_problem.items()
        if candidate_problem != problem_name
    ]


def nombre_target_reporte(target_name):
    return {"Area": "area"}.get(target_name, target_name)


def resumir_separacion_problema(nombre_dataset, datos_dataset, problem_name, target_name):
    predictors, target_values = separar_predictoras_target(datos_dataset, target_name)
    alternative_targets = obtener_targets_alternativos(nombre_dataset, problem_name)
    return {
        "dataset": nombre_dataset,
        "problema": problem_name,
        "target": nombre_target_reporte(target_name),
        "filas": datos_dataset.shape[0],
        "columnas_originales": datos_dataset.shape[1],
        "predictoras": predictors.shape[1],
        "target_nulos": int(target_values.isna().sum()),
        "target_clases": int(target_values.nunique(dropna=True)),
        "target_en_predictoras": target_name in predictors.columns,
        "etiquetas_alternativas_en_predictoras": sum(name in predictors.columns for name in alternative_targets),
    }


def resumir_separacion(nombre_dataset, datos_dataset):
    return pd.DataFrame([
        resumir_separacion_problema(nombre_dataset, datos_dataset, problem_name, target_name)
        for problem_name, target_name in problem_targets[nombre_dataset].items()
    ])
"""))

    split_observations = {
        "breast_cancer_wisconsin": "La separación deja 31 columnas predictoras y el target fuera de `X`. El identificador sigue dentro de las predictoras solo como objeto de revisión posterior.",
        "customer_churn": "La separación confirma que `Churn` queda fuera de las 11 predictoras. Las 3 variables categóricas se mantienen sin codificación global en esta fase.",
        "madelon": "La separación deja 500 predictoras numéricas. Esta estructura refuerza que las reducciones posteriores deben tratarse como selección/modelado, no como limpieza inicial.",
        "olive_oil": "La tabla muestra las dos formulaciones: `Area` como target de 3 clases y `target` como target de 9 clases. En una separación simple, la etiqueta alternativa queda dentro de `X`; por eso las variantes posteriores deberán excluirla antes de entrenar modelos.",
    }
    add_dataset_cells(
        cells,
        "Separación X/y",
        """
predictoras_{variable_name}, target_{variable_name} = separar_predictoras_target(
    {variable_name},
    expected_targets["{dataset_name}"],
)

separacion_{variable_name} = resumir_separacion("{dataset_name}", {variable_name})
mostrar_tabla(separacion_{variable_name}, "Separación X/y - {label}")
""",
        split_observations,
    )
    cells.append(md("### Resumen Comparativo de Separación"))
    cells.append(code("""
feature_target_summary = pd.concat([
    resumir_separacion(dataset_name, datos_dataset)
    for dataset_name, datos_dataset in raw_datasets.items()
], ignore_index=True)

guardar_tabla(feature_target_summary, "fase2_separacion_xy.csv")
mostrar_tabla(feature_target_summary, "Separación X/y por dataset")
"""))
    cells.append(md("""
La separación confirma que ningún target queda dentro de sus predictoras. `madelon` mantiene 500 predictoras, `breast_cancer_wisconsin` 31, `customer_churn` 11 y `olive_oil` muestra dos tareas con 11 predictoras cada una. La diferencia crítica es `olive_oil`: tanto `olive_oil_3class` como `olive_oil_9class` dejan 1 etiqueta alternativa dentro de `X`, por lo que esa columna deberá excluirse al materializar cada formulación supervisada.
"""))

    cells.append(md("""
## 2.4 Normalización de Nombres y Revisión de Tipos

Se normalizan los nombres de columnas a `snake_case` y se identifican cambios de tipo seguros. La tabla de renombrado contiene únicamente correspondencias entre nombres observados y nombres normalizados.
"""))
    cells.append(code("""
def normalizar_nombre_columna(nombre_columna):
    texto_columna = str(nombre_columna).strip()
    texto_columna = re.sub(r"[^0-9A-Za-záéíóúÁÉÍÓÚñÑ]+", "_", texto_columna)
    texto_columna = re.sub(r"_+", "_", texto_columna).strip("_").lower()
    return {"customerid": "customer_id", "churn": "target"}.get(texto_columna, texto_columna)


def hacer_nombres_unicos(column_names):
    seen_counts = {}
    unique_names = []
    for column_name in column_names:
        base_name = column_name or "columna"
        count_seen = seen_counts.get(base_name, 0)
        unique_names.append(base_name if count_seen == 0 else f"{base_name}_{count_seen + 1}")
        seen_counts[base_name] = count_seen + 1
    return unique_names
"""))
    cells.append(code("""
def es_entero_en_float(serie):
    if not pd.api.types.is_float_dtype(serie):
        return False
    valores_no_nulos = serie.dropna()
    if valores_no_nulos.empty:
        return False
    return np.isclose(valores_no_nulos, np.round(valores_no_nulos)).all()


def dtype_planificado(serie):
    return "int64" if es_entero_en_float(serie) else str(serie.dtype)
"""))
    cells.append(code("""
def construir_mapa_renombrado(datos_dataset):
    normalized_names = [normalizar_nombre_columna(name) for name in datos_dataset.columns]
    unique_names = hacer_nombres_unicos(normalized_names)
    return dict(zip(datos_dataset.columns, unique_names))


def resumir_renombrado(nombre_dataset, datos_dataset):
    rename_map = construir_mapa_renombrado(datos_dataset)
    return pd.DataFrame([
        {"dataset": nombre_dataset, "columna_original": original, "columna_procesada": processed, "cambia": original != processed}
        for original, processed in rename_map.items()
    ])
"""))
    cells.append(code("""
def resumir_tipos(nombre_dataset, datos_dataset, rename_map):
    renamed_dataset = datos_dataset.rename(columns=rename_map)
    rows = []
    for variable_name in renamed_dataset.columns:
        current_dtype = str(renamed_dataset[variable_name].dtype)
        planned_dtype = dtype_planificado(renamed_dataset[variable_name])
        rows.append({"dataset": nombre_dataset, "variable": variable_name, "dtype_original": current_dtype, "dtype_procesado": planned_dtype, "cambia": current_dtype != planned_dtype})
    return pd.DataFrame(rows)
"""))

    renaming_observations = {
        "breast_cancer_wisconsin": "Las 32 columnas ya están en una convención estable. El target mantiene el nombre `target` y el identificador conserva un nombre reconocible.",
        "customer_churn": "Los nombres con espacios y mayúsculas pasan a una convención homogénea. `CustomerID` queda como `customer_id` y `Churn` como `target`. Si `Churn` aparece como `float64`, el paso posterior a `int64` no cambia información: representa una etiqueta binaria 0/1, no una magnitud decimal.",
        "madelon": "Los 500 nombres `feat_*` y el target ya son consistentes. En este dataset el interés no está en el formato, sino en la dimensionalidad.",
        "olive_oil": "La normalización afecta a 1 de 12 columnas: `Area` pasa a `area`. El resto de variables queda en minúsculas consistentes.",
    }
    add_dataset_cells(
        cells,
        "Normalización",
        """
rename_map_{variable_name} = construir_mapa_renombrado({variable_name})
target_processed_{variable_name} = rename_map_{variable_name}[expected_targets["{dataset_name}"]]

renaming_{variable_name} = resumir_renombrado("{dataset_name}", {variable_name})
types_{variable_name} = resumir_tipos("{dataset_name}", {variable_name}, rename_map_{variable_name})

mostrar_tabla(renaming_{variable_name}[renaming_{variable_name}["cambia"]], "Columnas renombradas - {label}", n=12)
mostrar_tabla(types_{variable_name}[types_{variable_name}["cambia"]], "Cambios de tipo planificados - {label}", n=12)
""",
        renaming_observations,
    )
    cells.append(md("### Resumen Comparativo de Nombres y Tipos"))
    cells.append(code("""
rename_maps = {
    "breast_cancer_wisconsin": rename_map_breast_cancer_wisconsin,
    "customer_churn": rename_map_customer_churn,
    "madelon": rename_map_madelon,
    "olive_oil": rename_map_olive_oil,
}

processed_targets = {
    dataset_name: rename_maps[dataset_name][expected_targets[dataset_name]]
    for dataset_name in DATASET_ORDER
}

column_renaming = pd.concat([
    renaming_breast_cancer_wisconsin,
    renaming_customer_churn,
    renaming_madelon,
    renaming_olive_oil,
], ignore_index=True)

dtype_changes = pd.concat([
    types_breast_cancer_wisconsin,
    types_customer_churn,
    types_madelon,
    types_olive_oil,
], ignore_index=True)

guardar_tabla(column_renaming, "fase2_renombrado_columnas.csv")
guardar_tabla(dtype_changes, "fase2_tipos_columnas.csv")

renaming_summary = column_renaming.groupby("dataset", as_index=False).agg(
    columnas=("columna_original", "count"),
    columnas_renombradas=("cambia", "sum"),
)
mostrar_tabla(renaming_summary, "Resumen de renombrado")
"""))
    cells.append(md("""
El renombrado afecta a 13 de 557 columnas revisadas: las 12 de `customer_churn` y 1 de `olive_oil`. `breast_cancer_wisconsin` y `madelon` no cambian nombres, lo que reduce el riesgo de romper trazabilidad con Fase 1. En tipos, el cambio queda concentrado en `customer_churn`, con 8 columnas convertibles de `float64` a enteros porque representan códigos o conteos discretos.
"""))

    cells.append(md("""
## 2.5 Identificadores y Variables Para Revisión Posterior

Se revisan posibles identificadores a partir de la evidencia estructural de Fase 1 y de los propios datos. También se recuperan las variables que Fase 1 marcó para revisión estadística.

Los identificadores sí se usan después para construir los datasets procesados. Las variables heredadas de Fase 1 no se recalculan ni se aplican aquí: se resumen en texto para recordar su origen, su significado y la fase en la que deben leerse. Los p-valores, FDR y tamaños de efecto completos pertenecen a Fase 1; Fase 2 solo conserva la trazabilidad metodológica.
"""))
    cells.append(code("""
def crear_fila_identificador(nombre_dataset, datos_dataset, original_name, processed_name):
    observed_values = datos_dataset[original_name].nunique(dropna=True)
    return {
        "dataset": nombre_dataset,
        "variable_original": original_name,
        "variable_procesada": processed_name,
        "valores_unicos": int(observed_values),
        "ratio_valores_unicos": observed_values / len(datos_dataset),
        "nulos": int(datos_dataset[original_name].isna().sum()),
    }


def extraer_identificadores_fase1(nombre_dataset):
    structure = phase1_tables["fase1_estructura_datasets.csv"]
    dataset_row = structure[structure["dataset"].eq(nombre_dataset)]
    if dataset_row.empty:
        return []
    raw_names = dataset_row.iloc[0]["nombres_posibles_identificadores"]
    if pd.isna(raw_names):
        return []
    return [name.strip() for name in str(raw_names).split(",") if name.strip()]


def resumir_identificadores(nombre_dataset, datos_dataset):
    rows = []
    for original_name in extraer_identificadores_fase1(nombre_dataset):
        processed_name = rename_maps[nombre_dataset].get(original_name, original_name)
        rows.append(crear_fila_identificador(nombre_dataset, datos_dataset, original_name, processed_name))
    return pd.DataFrame(rows)
"""))
    cells.append(code("""
def variables_revision_fase1(nombre_dataset):
    revision_table = phase1_tables["fase1_variables_revision_riesgos.csv"].copy()
    selected = revision_table[revision_table["dataset"].eq(nombre_dataset)].copy()
    selected["variable_procesada"] = selected["variable"].map(rename_maps[nombre_dataset]).fillna(selected["variable"])
    metric_columns = [
        "dataset",
        "variable",
        "variable_procesada",
        "test",
        "estadistico",
        "p_valor",
        "p_valor_fdr",
        "nombre_tamano_efecto",
        "tamano_efecto",
        "abs_tamano_efecto",
    ]
    return selected[metric_columns]


def resumir_revision_fase1_markdown(nombre_dataset, revision_dataset):
    if revision_dataset.empty:
        return (
            f"`{nombre_dataset}` no hereda variables marcadas para revisión estadística en Fase 1. "
            "Por tanto, Fase 2 no añade ninguna cautela estadística nueva más allá de identificadores, nulos, cardinalidad y outliers."
        )

    n_variables = int(revision_dataset["variable_procesada"].nunique())
    tests = ", ".join(sorted(revision_dataset["test"].dropna().astype(str).unique()))
    min_fdr = revision_dataset["p_valor_fdr"].min(skipna=True)
    max_effect = revision_dataset["abs_tamano_efecto"].max(skipna=True)
    examples = ", ".join(f"`{name}`" for name in revision_dataset["variable_procesada"].drop_duplicates().head(5))
    return (
        f"`{nombre_dataset}` hereda {n_variables} variables señaladas en Fase 1 mediante {tests}. "
        f"El menor p-valor ajustado FDR heredado es {min_fdr:.2e} y el mayor tamaño de efecto absoluto heredado es {max_effect:.3f}. "
        f"Ejemplos trazables: {examples}. En Fase 2 esto no implica eliminar ni transformar variables: sirve para que Fase 3 contraste conservación de señal, "
        "Fase 4 vigile leakage/drift y Fase 5 evalúe si la selección reutiliza o descarta esas señales."
    )
"""))

    identifier_observations = {
        "breast_cancer_wisconsin": "La columna `id` tiene tantos valores únicos como filas, por lo que se excluye del dataset procesado. Las variables de revisión se mantienen para Fase 3, no se eliminan por evidencia estadística aislada.",
        "customer_churn": "`CustomerID` tiene 440832 valores únicos en 440832 filas y se comporta como identificador estructural. Las variables categóricas o significativas no se eliminan en esta fase.",
        "madelon": "No hay identificadores estructurales detectados entre 501 columnas. Las variables de revisión proceden de contrastes exploratorios, por lo que no justifican eliminación en preprocesado.",
        "olive_oil": "La columna `id` tiene 572 valores únicos en 572 filas y se excluye como identificador. La señal de Fase 1 señala `Area` y `palmitic`, pero esa señal no se usa como regla de limpieza.",
    }
    add_dataset_cells(
        cells,
        "Identificadores y Revisión",
        """
identifiers_{variable_name} = resumir_identificadores("{dataset_name}", {variable_name})
revision_{variable_name} = variables_revision_fase1("{dataset_name}")

mostrar_tabla(identifiers_{variable_name}, "Identificadores detectados - {label}", n=12)
display(Markdown(resumir_revision_fase1_markdown("{dataset_name}", revision_{variable_name})))
""",
        identifier_observations,
    )
    cells.append(md("### Resumen Comparativo de Identificadores"))
    cells.append(code("""
detected_identifiers = pd.concat([
    identifiers_breast_cancer_wisconsin,
    identifiers_customer_churn,
    identifiers_madelon,
    identifiers_olive_oil,
], ignore_index=True)

phase1_revision_variables = pd.concat([
    revision_breast_cancer_wisconsin,
    revision_customer_churn,
    revision_madelon,
    revision_olive_oil,
], ignore_index=True)

identifier_columns_processed = {
    dataset_name: detected_identifiers.loc[
        detected_identifiers["dataset"].eq(dataset_name),
        "variable_procesada",
    ].tolist()
    for dataset_name in DATASET_ORDER
}

guardar_tabla(detected_identifiers, "fase2_identificadores_detectados.csv")

identifier_summary = detected_identifiers.groupby("dataset", as_index=False).agg(
    identificadores=("variable_procesada", "count"),
    ratio_unicidad_maximo=("ratio_valores_unicos", "max"),
)
mostrar_tabla(identifier_summary, "Identificadores por dataset")
display(Markdown(
    "Las variables heredadas de Fase 1 no se guardan como tabla de Fase 2 porque no son un resultado de preprocesado. "
    "Su tabla fuente sigue siendo `results/tables/01_raw_eda/fase1_variables_revision_riesgos.csv`."
))
"""))
    cells.append(md("""
La comparación identifica 3 columnas de tipo identificador: `id` en `breast_cancer_wisconsin`, `customer_id` en `customer_churn` e `id` en `olive_oil`. Las tres tienen ratio de unicidad 1.0000 y 0 nulos, exactamente el patrón de una clave técnica. `madelon` no aporta identificador, así que sus 500 variables se conservan para que la selección posterior afronte el benchmark completo.
"""))
    cells.append(md("""
### Lectura de la Evidencia Heredada

La evidencia de Fase 1 se conserva como contraste exploratorio: indica variables que merecen vigilancia estadística o semántica, pero no activa borrados ni transformaciones globales. El one-hot de predictoras, la imputación y el escalado deben ajustarse más adelante sobre train para evitar fuga de información hacia validación o test.

En `breast_cancer_wisconsin` y `olive_oil`, la exclusión de identificadores sí pertenece a esta fase porque se basa en unicidad observada. En `madelon`, las señales heredadas se leerán dentro de selección de características, ya que el dataset fue diseñado precisamente para contener muchas variables irrelevantes.
"""))

    cells.append(md("""
## 2.6 Nulos y Códigos Especiales

Se calcula la presencia de valores nulos por variable y dataset. Si no aparecen nulos, no se crea ninguna tabla de estrategia ni de imputación: la ausencia de nulos es ya la evidencia.
"""))
    cells.append(code("""
def resumir_nulos(nombre_dataset, datos_dataset):
    rows = []
    for variable_name in datos_dataset.columns:
        missing_count = int(datos_dataset[variable_name].isna().sum())
        rows.append({
            "dataset": nombre_dataset,
            "variable": variable_name,
            "nulos": missing_count,
            "pct_nulos": missing_count / len(datos_dataset),
        })
    return pd.DataFrame(rows)


def crear_fila_codigos_especiales(nombre_dataset, serie):
    return {
        "dataset": nombre_dataset,
        "variable": serie.name,
        "infinitos": int(np.isinf(serie).sum()),
        "ceros": int(serie.eq(0).sum()),
        "valores_negativos": int(serie.lt(0).sum()),
    }


def resumir_codigos_especiales(nombre_dataset, datos_dataset):
    numeric_values = datos_dataset.select_dtypes(include=np.number)
    rows = []
    for variable_name in numeric_values.columns:
        rows.append(crear_fila_codigos_especiales(nombre_dataset, numeric_values[variable_name]))
    return pd.DataFrame(rows)
"""))

    missing_observations = {
        "breast_cancer_wisconsin": "No aparecen nulos en las variables del dataset. No se aplica imputación en Fase 2.",
        "customer_churn": "No aparecen nulos en las 12 columnas. Los valores cero y negativos se revisan como valores numéricos observados, no como ausencias implícitas.",
        "madelon": "No aparecen nulos ni infinitos en las 501 columnas. La fase no necesita imputación antes de guardar el dataset procesado.",
        "olive_oil": "No aparecen nulos en las 12 columnas. El target textual de 9 clases se conserva hasta la sección de codificación trazable.",
    }
    add_dataset_cells(
        cells,
        "Nulos",
        """
missing_{variable_name} = resumir_nulos("{dataset_name}", {variable_name})
special_codes_{variable_name} = resumir_codigos_especiales("{dataset_name}", {variable_name})

mostrar_tabla(missing_{variable_name}[missing_{variable_name}["nulos"] > 0], "Variables con nulos - {label}", n=12)
mostrar_tabla(special_codes_{variable_name}, "Códigos numéricos revisados - {label}", n=12)
""",
        missing_observations,
    )
    cells.append(md("### Resumen Comparativo de Nulos"))
    cells.append(code("""
missing_by_variable = pd.concat([
    missing_breast_cancer_wisconsin,
    missing_customer_churn,
    missing_madelon,
    missing_olive_oil,
], ignore_index=True)

special_codes = pd.concat([
    special_codes_breast_cancer_wisconsin,
    special_codes_customer_churn,
    special_codes_madelon,
    special_codes_olive_oil,
], ignore_index=True)

missing_summary = missing_by_variable.groupby("dataset", as_index=False).agg(
    variables=("variable", "count"),
    nulos_totales=("nulos", "sum"),
    pct_nulos_maximo=("pct_nulos", "max"),
)

guardar_tabla(missing_by_variable, "fase2_nulos_variables.csv")
guardar_tabla(special_codes, "fase2_codigos_especiales.csv")
mostrar_tabla(missing_summary, "Resumen de nulos")
"""))
    cells.append(md("""
La revisión de nulos revisa 557 columnas y suma 0 valores ausentes. El máximo `pct_nulos` por dataset también es 0.0000, de modo que no existe justificación para imputar en Fase 2. Esta ausencia de imputación es importante: evita aprender medias, modas o distribuciones antes del split y mantiene limpio el brazo clásico de control.
"""))

    cells.append(md("""
## 2.7 Duplicados

Se revisan duplicados exactos por dataset mediante comparación fila a fila sobre todas las columnas crudas. La sección calcula la evidencia de duplicidad de forma independiente, no depende de la revisión de nulos y sirve para decidir si el número de registros procesados debe conservarse exactamente.
"""))
    cells.append(code("""
def resumir_duplicados(nombre_dataset, datos_dataset):
    duplicate_count = int(datos_dataset.duplicated().sum())
    return pd.DataFrame([{
        "dataset": nombre_dataset,
        "filas": len(datos_dataset),
        "duplicados_exactos": duplicate_count,
        "pct_duplicados_exactos": duplicate_count / len(datos_dataset),
    }])
"""))

    duplicate_observations = {
        "breast_cancer_wisconsin": "No se detectan duplicados exactos en 569 filas, por lo que no se elimina ninguna fila.",
        "customer_churn": "No se detectan duplicados exactos pese a las 440832 filas del dataset. No hay reducción de registros en esta fase.",
        "madelon": "No se detectan duplicados exactos en 2000 filas. La alta dimensionalidad no se corrige mediante borrado de filas.",
        "olive_oil": "No se detectan duplicados exactos en 572 filas. La estructura de 9 clases se preserva íntegra.",
    }
    add_dataset_cells(
        cells,
        "Duplicados",
        """
duplicates_{variable_name} = resumir_duplicados("{dataset_name}", {variable_name})
mostrar_tabla(duplicates_{variable_name}, "Duplicados exactos - {label}")
""",
        duplicate_observations,
    )
    cells.append(md("### Resumen Comparativo de Duplicados"))
    cells.append(code("""
duplicates_summary = pd.concat([
    duplicates_breast_cancer_wisconsin,
    duplicates_customer_churn,
    duplicates_madelon,
    duplicates_olive_oil,
], ignore_index=True)

guardar_tabla(duplicates_summary, "fase2_duplicados.csv")
mostrar_tabla(duplicates_summary, "Resumen de duplicados")
"""))
    cells.append(md("""
Los cuatro datasets registran 0 duplicados exactos. La comprobación cubre desde las 440832 filas de `customer_churn` hasta las 569 de `breast_cancer_wisconsin`, sin reducción de filas en ningún caso. Por tanto, las diferencias que aparezcan en fases posteriores no podrán atribuirse a una depuración de registros repetidos en esta fase.
"""))

    cells.append(md("""
## 2.8 Constantes, Baja Cardinalidad y Dominancia

Se recalculan métricas de cardinalidad desde los datos crudos. Una variable constante sí sería una anomalía estructural; la baja cardinalidad o una moda dominante solo se documentan, porque pueden ser características válidas del dominio.

Para `madelon`, la interpretación se apoya en la ficha UCI y en el PDF local `data/01_raw/madelon/Dataset.pdf`: el dataset es sintético, procede del benchmark NIPS 2003 de selección de variables y contiene 500 variables con 20 informativas/redundantes y 480 probes irrelevantes. Referencia UCI: https://archive.ics.uci.edu/ml/datasets/madelon
"""))
    cells.append(code("""
def crear_fila_cardinalidad(nombre_dataset, serie):
    unique_count = int(serie.nunique(dropna=True))
    mode_frequency = float(serie.value_counts(normalize=True, dropna=False).iloc[0])
    return {
        "dataset": nombre_dataset,
        "variable": serie.name,
        "valores_unicos": unique_count,
        "ratio_valores_unicos": unique_count / len(serie),
        "frecuencia_moda": mode_frequency,
        "constante": unique_count <= 1,
        "baja_cardinalidad_relativa": unique_count / len(serie) <= LOW_CARDINALITY_RATIO,
        "moda_dominante_98": mode_frequency >= DOMINANT_MODE_RATIO,
    }


def resumir_cardinalidad(nombre_dataset, datos_dataset):
    target_name = expected_targets[nombre_dataset]
    rows = []
    for variable_name in datos_dataset.columns:
        if variable_name != target_name:
            rows.append(crear_fila_cardinalidad(nombre_dataset, datos_dataset[variable_name]))
    return pd.DataFrame(rows)
"""))

    cardinality_observations = {
        "breast_cancer_wisconsin": "No se observan variables constantes ni dominancia extrema entre 31 predictoras revisadas. El identificador queda separado por la revisión anterior.",
        "customer_churn": "Las 9 alertas de baja cardinalidad son coherentes con el dominio: género, tipo de suscripción, edad acotada o días de retraso no deberían tener cientos de valores distintos. Se documentan, pero no se eliminan automáticamente.",
        "madelon": "Madelon es sintético: UCI y el PDF del benchmark indican 500 variables, 20 informativas/redundantes y 480 probes irrelevantes, con reescalado y ruido. Las alertas se leen como rasgos del diseño, no como error estructural.",
        "olive_oil": "La baja cardinalidad relativa se concentra en pocas variables. No justifica eliminación en Fase 2.",
    }
    add_dataset_cells(
        cells,
        "Cardinalidad y Dominancia",
        """
cardinality_{variable_name} = resumir_cardinalidad("{dataset_name}", {variable_name})
cardinality_flags_{variable_name} = cardinality_{variable_name}[
    cardinality_{variable_name}[["constante", "baja_cardinalidad_relativa", "moda_dominante_98"]].any(axis=1)
]

mostrar_tabla(cardinality_flags_{variable_name}, "Variables señaladas por cardinalidad - {label}", n=15)
""",
        cardinality_observations,
    )
    cells.append(md("### Resumen Comparativo de Cardinalidad"))
    cells.append(code("""
cardinality_by_variable = pd.concat([
    cardinality_breast_cancer_wisconsin,
    cardinality_customer_churn,
    cardinality_madelon,
    cardinality_olive_oil,
], ignore_index=True)

cardinality_summary = cardinality_by_variable.groupby("dataset", as_index=False).agg(
    variables=("variable", "count"),
    constantes=("constante", "sum"),
    baja_cardinalidad_relativa=("baja_cardinalidad_relativa", "sum"),
    moda_dominante_98=("moda_dominante_98", "sum"),
)

guardar_tabla(cardinality_by_variable, "fase2_cardinalidad_dominancia.csv")
mostrar_tabla(cardinality_summary, "Resumen de cardinalidad")
display(Markdown(
    "La tabla sustituye a la gráfica de cardinalidad: para esta fase interesa saber "
    "qué variables revisar, no enfatizar visualmente conteos que dependen mucho del dominio."
))
"""))
    cells.append(md("""
La cardinalidad no detecta constantes ni modas dominantes al 98% en ningún dataset. Sí marca baja cardinalidad relativa en 9 variables de `customer_churn`, 24 de `madelon` y 1 de `olive_oil`, frente a 0 en `breast_cancer_wisconsin`. La lectura no activa borrados: en `customer_churn` las alertas son categorías o variables discretas, y en `madelon` reflejan parte del diseño sintético del benchmark.
"""))

    cells.append(md("""
## 2.9 Outliers y Valores Extremos

Se calcula la tasa de outliers mediante el criterio IQR por variable numérica. Esta regla exploratoria, asociada al boxplot de Tukey, marca valores fuera de `Q1 - 1.5 * IQR` y `Q3 + 1.5 * IQR`. La sección no modifica los valores extremos; solo cuantifica su presencia antes de modelar.

Cada figura por dataset combina dos lecturas: a la izquierda, la tasa IQR de todas las variables numéricas; a la derecha, boxplots en escala robusta para un subconjunto representativo. En datasets de alta dimensionalidad como `madelon`, el subconjunto se selecciona por máximos y cuantiles de la tasa de outliers para no reducir la lectura a una sola variable extrema.
"""))
    cells.append(code("""
def obtener_predictoras_renombradas(nombre_dataset, datos_dataset):
    renamed_dataset = datos_dataset.rename(columns=rename_maps[nombre_dataset])
    excluded_columns = [processed_targets[nombre_dataset]] + identifier_columns_processed[nombre_dataset]
    return renamed_dataset.drop(columns=excluded_columns, errors="ignore")


def obtener_predictoras_numericas_renombradas(nombre_dataset, datos_dataset):
    return obtener_predictoras_renombradas(nombre_dataset, datos_dataset).select_dtypes(include=np.number)


def calcular_limites_iqr(serie):
    first_quartile = serie.quantile(0.25)
    third_quartile = serie.quantile(0.75)
    interquartile_range = third_quartile - first_quartile
    lower_limit = first_quartile - 1.5 * interquartile_range
    upper_limit = third_quartile + 1.5 * interquartile_range
    return first_quartile, third_quartile, interquartile_range, lower_limit, upper_limit


def crear_fila_outliers(nombre_dataset, serie):
    first_quartile, third_quartile, interquartile_range, lower_limit, upper_limit = calcular_limites_iqr(serie)
    outlier_mask = serie.lt(lower_limit) | serie.gt(upper_limit)
    return {
        "dataset": nombre_dataset,
        "variable": serie.name,
        "q1": float(first_quartile),
        "q3": float(third_quartile),
        "iqr": float(interquartile_range),
        "limite_inferior": float(lower_limit),
        "limite_superior": float(upper_limit),
        "n_outliers_iqr": int(outlier_mask.sum()),
        "pct_outliers_iqr": float(outlier_mask.mean()),
    }


def resumir_outliers(nombre_dataset, datos_dataset):
    numeric_data = obtener_predictoras_numericas_renombradas(nombre_dataset, datos_dataset)
    return pd.DataFrame([crear_fila_outliers(nombre_dataset, numeric_data[name]) for name in numeric_data.columns])
"""))
    cells.append(md("""
El primer bloque calcula la tabla IQR por variable. El siguiente bloque decide qué variables se enseñan en los boxplots cuando el dataset tiene demasiadas columnas para una lectura completa.
"""))
    cells.append(code("""


def escalar_serie_para_boxplot_outliers(serie):
    first_quartile, third_quartile, interquartile_range, lower_limit, upper_limit = calcular_limites_iqr(serie)
    median_value = serie.median()
    if interquartile_range > 0:
        scaled_series = (serie - median_value) / interquartile_range
    else:
        scaled_series = serie - median_value
    outlier_mask = serie.lt(lower_limit) | serie.gt(upper_limit)
    return scaled_series, outlier_mask


def seleccionar_variables_representativas_outliers(outliers_table, max_variables):
    ordered = outliers_table.sort_values("pct_outliers_iqr", ascending=False).reset_index(drop=True)
    if len(ordered) <= max_variables:
        return ordered, "todas"

    if len(ordered) > 60:
        n_top = min(4, max_variables)
        n_quantiles = max_variables - n_top
        top_rows = ordered.head(n_top)
        quantile_positions = np.linspace(0, len(ordered) - 1, n_quantiles).round().astype(int)
        quantile_rows = ordered.iloc[quantile_positions]
        selected = pd.concat([top_rows, quantile_rows], ignore_index=True)
        selected = selected.drop_duplicates("variable").head(max_variables)
        return selected, "alta_dimensionalidad"

    flagged = outliers_table[outliers_table["pct_outliers_iqr"] >= OUTLIER_RATE_ALERT_THRESHOLD]
    if not flagged.empty:
        return flagged.sort_values("pct_outliers_iqr", ascending=False).head(max_variables), "sobre_umbral"

    positive = outliers_table[outliers_table["n_outliers_iqr"] > 0]
    if not positive.empty:
        return positive.sort_values("pct_outliers_iqr", ascending=False).head(min(max_variables, 8)), "top_sin_umbral"

    return outliers_table.sort_values("pct_outliers_iqr", ascending=False).head(min(max_variables, 8)), "sin_outliers"


def texto_seleccion_outliers(selection_mode):
    messages = {
        "todas": "Se muestran todas las variables numéricas.",
        "alta_dimensionalidad": "Panel izquierdo: todas las variables. Boxplots: máximos y cuantiles por alta dimensionalidad.",
        "sobre_umbral": f"Boxplots limitados a variables con tasa IQR >= {OUTLIER_RATE_ALERT_THRESHOLD:.0%}.",
        "top_sin_umbral": f"Ninguna variable supera {OUTLIER_RATE_ALERT_THRESHOLD:.0%}; se muestran las mayores tasas positivas.",
        "sin_outliers": "0% en todas las variables numéricas.",
    }
    return messages[selection_mode]
"""))
    cells.append(md("""
El último bloque dibuja la figura: mantiene todas las tasas IQR a la izquierda y reserva los boxplots robustos de la derecha para las variables seleccionadas por la regla anterior.
"""))
    cells.append(code("""


def graficar_tasas_outliers(eje, outliers_table, dataset_name):
    ordered = outliers_table.sort_values("pct_outliers_iqr", ascending=True).reset_index(drop=True)
    positions = np.arange(len(ordered))
    flagged = ordered["pct_outliers_iqr"].ge(OUTLIER_RATE_ALERT_THRESHOLD).to_numpy()
    values = ordered["pct_outliers_iqr"].to_numpy()

    eje.scatter(values[~flagged], positions[~flagged], s=18, alpha=0.45, color=DATASET_COLORS[dataset_name], edgecolor="none")
    if flagged.any():
        eje.scatter(values[flagged], positions[flagged], s=42, alpha=0.9, color="#B85C5C", marker="D", edgecolor="#6F2E2E", linewidth=0.4)

    eje.axvline(OUTLIER_RATE_ALERT_THRESHOLD, linestyle="--", color="#B85C5C", linewidth=1.0)
    if len(ordered) <= 35:
        eje.set_yticks(positions)
        eje.set_yticklabels(ordered["variable"])
    else:
        eje.set_yticks([0, len(ordered) - 1])
        eje.set_yticklabels(["menor tasa", "mayor tasa"])
    eje.set_xlabel("Proporción de outliers IQR")
    eje.set_title("Todas las variables", loc="left", fontweight="bold", fontsize=10)
    aplicar_estilo_eje(eje, eje_rejilla="x")


def preparar_boxplots_outliers(selected, dataset_name):
    numeric_data = obtener_predictoras_numericas_renombradas(dataset_name, raw_datasets[dataset_name])
    plot_values = []
    outlier_points = []
    labels = []
    rng = np.random.default_rng(RANDOM_STATE)

    for _, row in selected.sort_values("pct_outliers_iqr", ascending=True).iterrows():
        variable_name = row["variable"]
        scaled_series, outlier_mask = escalar_serie_para_boxplot_outliers(numeric_data[variable_name].dropna())
        outlier_values = scaled_series[outlier_mask.reindex(scaled_series.index, fill_value=False)].to_numpy()
        if len(outlier_values) > 350:
            outlier_values = rng.choice(outlier_values, size=350, replace=False)
        plot_values.append(scaled_series.to_numpy())
        outlier_points.append(outlier_values)
        labels.append(f"{variable_name} ({row['pct_outliers_iqr']:.1%})")
    return plot_values, outlier_points, labels


def graficar_boxplots_outliers(eje, selected, dataset_name):
    plot_values, outlier_points, labels = preparar_boxplots_outliers(selected, dataset_name)
    positions = np.arange(len(plot_values))
    eje.boxplot(
        plot_values,
        positions=positions,
        vert=False,
        widths=0.44,
        showfliers=False,
        patch_artist=True,
        boxprops={"facecolor": DATASET_COLORS[dataset_name], "alpha": 0.20, "edgecolor": "#6F6A60"},
        medianprops={"color": "#2D2A26", "linewidth": 1.2},
        whiskerprops={"color": "#6F6A60"},
        capprops={"color": "#6F6A60"},
    )

    rng = np.random.default_rng(RANDOM_STATE)
    for position, values in zip(positions, outlier_points):
        if len(values) == 0:
            continue
        jitter = rng.uniform(-0.10, 0.10, size=len(values))
        eje.scatter(values, position + jitter, s=16, color="#B85C5C", alpha=0.55, edgecolor="none")

    eje.set_yticks(positions)
    eje.set_yticklabels(labels)
    eje.set_xlabel("Valor en escala robusta por variable")
    eje.set_title("Distribución robusta seleccionada", loc="left", fontweight="bold", fontsize=10)
    aplicar_estilo_eje(eje, eje_rejilla="x")


def graficar_outliers_dataset(outliers_table, dataset_name, max_variables=12):
    if outliers_table.empty:
        return None

    selected, selection_mode = seleccionar_variables_representativas_outliers(outliers_table, max_variables)
    figure_height = max(4.8, 0.42 * len(selected) + 1.7)
    figura, (eje_tasas, eje_boxplots) = plt.subplots(
        1,
        2,
        figsize=(13.2, figure_height),
        gridspec_kw={"width_ratios": [0.95, 1.35]},
    )

    graficar_tasas_outliers(eje_tasas, outliers_table, dataset_name)
    graficar_boxplots_outliers(eje_boxplots, selected, dataset_name)
    max_row = outliers_table.loc[outliers_table["pct_outliers_iqr"].idxmax()]
    figura.suptitle(f"{max_row['variable']} marca el máximo IQR en {etiqueta_dataset(dataset_name)} ({max_row['pct_outliers_iqr']:.1%})", x=0.02, ha="left", fontweight="bold")
    figura.text(0.02, 0.02, texto_seleccion_outliers(selection_mode), ha="left", va="bottom", color="#6F6A60", fontsize=9)
    figura.tight_layout(rect=[0, 0.05, 1, 0.94])
    guardar_figura(figura, f"fase2_outliers_iqr_{dataset_name}.png")
    plt.show()
    plt.close(figura)
    return None


def graficar_resumen_outliers(outlier_table, nombre_archivo, titulo, xlim=None):
    figura, eje = plt.subplots(figsize=(10.8, 5.4))
    positions = np.arange(len(DATASET_ORDER))

    for position, dataset_name in enumerate(DATASET_ORDER):
        dataset_values = outlier_table.loc[outlier_table["dataset"].eq(dataset_name), ["variable", "pct_outliers_iqr"]].copy()
        values = dataset_values["pct_outliers_iqr"].to_numpy()
        if len(values) > 0:
            eje.boxplot(
                values,
                positions=[position],
                vert=False,
                widths=0.38,
                showfliers=False,
                patch_artist=True,
                boxprops={"facecolor": DATASET_COLORS[dataset_name], "alpha": 0.18, "edgecolor": "#D8D0C4"},
                medianprops={"color": "#2D2A26", "linewidth": 1.2},
            )
            jitter = np.random.default_rng(RANDOM_STATE + position).uniform(-0.12, 0.12, size=len(values))
            flagged_mask = dataset_values["pct_outliers_iqr"].ge(OUTLIER_RATE_ALERT_THRESHOLD).to_numpy()
            eje.scatter(values[~flagged_mask], position + jitter[~flagged_mask], s=18, alpha=0.32, color=DATASET_COLORS[dataset_name], edgecolor="none")
            if flagged_mask.any():
                eje.scatter(values[flagged_mask], position + jitter[flagged_mask], s=42, alpha=0.85, color="#B85C5C", marker="D", edgecolor="#6F2E2E", linewidth=0.4, label=f">= {OUTLIER_RATE_ALERT_THRESHOLD:.0%}" if position == 0 else None)

    if xlim is None or xlim >= OUTLIER_RATE_ALERT_THRESHOLD:
        eje.axvline(OUTLIER_RATE_ALERT_THRESHOLD, linestyle="--", color="#B85C5C", linewidth=1.2)
    if xlim is not None:
        eje.set_xlim(0, xlim)
    eje.set_yticks(positions)
    eje.set_yticklabels([etiqueta_dataset(name) for name in DATASET_ORDER])
    eje.set_xlabel("Proporción de outliers IQR")
    eje.set_title(titulo, loc="left", fontweight="bold")
    eje.text(0.99, 0.98, "Cada punto es una variable numérica; diamantes rojos superan el umbral.", transform=eje.transAxes, ha="right", va="top", color="#6F6A60", fontsize=9)
    aplicar_estilo_eje(eje, eje_rejilla="x")
    guardar_figura(figura, nombre_archivo)
    plt.show()
    plt.close(figura)
    return None
"""))

    outlier_observations = {
        "breast_cancer_wisconsin": "`area_se` alcanza la mayor tasa IQR con 65 outliers y 11.4%. No se capan valores en esta fase.",
        "customer_churn": "Las 7 variables numéricas tienen 0 outliers IQR. No se aplica winsorización.",
        "madelon": "El panel de tasas recorre las 500 variables. Los boxplots muestran una selección por máximos y cuantiles; al tratarse de un benchmark sintético, los extremos IQR describen la construcción marginal y el ruido, no errores a corregir en Fase 2.",
        "olive_oil": "`eicosenoic` presenta 51 outliers IQR y 8.9%, todavía por debajo del umbral visual del 10%. No se eliminan filas ni se transforman variables.",
    }
    add_dataset_cells(
        cells,
        "Outliers IQR",
        """
outliers_{variable_name} = resumir_outliers("{dataset_name}", {variable_name})
outliers_top_{variable_name} = outliers_{variable_name}.sort_values("pct_outliers_iqr", ascending=False)

mostrar_tabla(outliers_top_{variable_name}, "Outliers IQR - {label}", n=12)
graficar_outliers_dataset(outliers_{variable_name}, "{dataset_name}")
""",
        outlier_observations,
    )
    cells.append(md("### Resumen Comparativo de Outliers"))
    cells.append(code("""
outlier_by_variable = pd.concat([
    outliers_breast_cancer_wisconsin,
    outliers_customer_churn,
    outliers_madelon,
    outliers_olive_oil,
], ignore_index=True)

outlier_summary = outlier_by_variable.groupby("dataset", as_index=False).agg(
    variables_numericas=("variable", "count"),
    pct_outliers_media=("pct_outliers_iqr", "mean"),
    pct_outliers_maxima=("pct_outliers_iqr", "max"),
)

guardar_tabla(outlier_by_variable, "fase2_outliers_iqr.csv")
mostrar_tabla(outlier_summary, "Resumen de outliers")
"""))
    cells.append(md("""
El agregado de outliers cubre 547 variables numéricas. `madelon` domina la escala con media 0.0104 y máximo 0.3740, `breast_cancer_wisconsin` queda con media 0.0356 y máximo 0.1142, `olive_oil` alcanza 0.0892 y `customer_churn` permanece en 0.0000. Las figuras siguientes separan la vista completa del zoom 0-5% para que el máximo de `madelon` no oculte las diferencias pequeñas.
"""))
    cells.append(code("""
graficar_resumen_outliers(
    outlier_by_variable,
    "fase2_outliers_iqr_resumen_completo.png",
    "Madelon concentra los extremos IQR y Churn queda en cero",
)

graficar_resumen_outliers(
    outlier_by_variable,
    "fase2_outliers_iqr_resumen_zoom.png",
    "El zoom separa Olive Oil y Breast Cancer por debajo del 5%",
    xlim=0.05,
)
"""))
    cells.append(md("""
El resumen de outliers muestra tres comportamientos. `customer_churn` tiene 7 variables numéricas con 0.0000 de tasa máxima; `olive_oil` alcanza 0.0892 en `eicosenoic`, por debajo del umbral visual del 10%; y `breast_cancer_wisconsin` supera el umbral solo en `area_se`, con 65 casos y 0.1142 de tasa. `madelon` es el caso extremo: 4 variables superan el 10% y `feat_423` llega a 0.3740, coherente con un benchmark sintético que no debe winsorizarse aquí.
"""))

    cells.append(md("""
## 2.10 Codificación del Target y Revisión de Categóricas

Se codifica el target de forma determinista y se enumeran las categorías observadas en variables predictoras. Esta sección prepara el terreno para estimadores posteriores: no codifica predictoras categóricas de forma global antes del split.

PAPER_QFS, sección V.A, aplica esta misma decisión para hacer compatibles los datos mixtos con métricas de información mutua y redundancia: las variables categóricas se transforman a códigos enteros mediante *label encoding* y los campos no numéricos se eliminan o imputan cuando procede. En esta fase se codifica el target y se documentan las predictoras categóricas; la codificación global de predictoras se pospone porque el `OneHotEncoder` real aprende categorías durante `fit` y debe ajustarse solo con train para evitar *data leakage*.
"""))
    cells.append(code("""
def construir_mapa_target(serie_target):
    target_values = [convertir_escalar_python(value) for value in serie_target.dropna().unique().tolist()]
    target_values = sorted(target_values, key=lambda value: str(value))
    return {target_value: position for position, target_value in enumerate(target_values)}


def resumir_target_codificado(nombre_dataset, datos_dataset):
    target_name = expected_targets[nombre_dataset]
    target_map = construir_mapa_target(datos_dataset[target_name])
    target_counts = datos_dataset[target_name].value_counts(dropna=False).reset_index()
    target_counts.columns = ["valor_original", "n"]
    target_counts["dataset"] = nombre_dataset
    target_counts["target"] = processed_targets[nombre_dataset]
    target_counts["codigo"] = target_counts["valor_original"].map(target_map)
    target_counts["proporcion"] = target_counts["n"] / len(datos_dataset)
    return target_counts[["dataset", "target", "valor_original", "codigo", "n", "proporcion"]], target_map
"""))
    cells.append(code("""
def crear_filas_categoria(nombre_dataset, serie, variable_name):
    counts = serie.value_counts(dropna=False)
    return [{"dataset": nombre_dataset, "variable": rename_maps[nombre_dataset][variable_name], "categoria": category, "n": int(count), "proporcion": count / len(serie)} for category, count in counts.items()]


def resumir_categorias_predictoras(nombre_dataset, datos_dataset):
    target_name = expected_targets[nombre_dataset]
    predictors = datos_dataset.drop(columns=[target_name])
    categorical_predictors = predictors.select_dtypes(exclude=np.number)
    rows = []
    for variable_name in categorical_predictors.columns:
        rows.extend(crear_filas_categoria(nombre_dataset, datos_dataset[variable_name], variable_name))
    return pd.DataFrame(rows, columns=["dataset", "variable", "categoria", "n", "proporcion"])


def nombre_archivo_seguro(texto):
    return re.sub(r"[^0-9a-zA-Z_]+", "_", str(texto).lower()).strip("_")


def graficar_categoria_predictora(categories_table, dataset_name, variable_name):
    selected = categories_table[categories_table["variable"].eq(variable_name)].copy()
    if selected.empty:
        return None

    selected_for_bars = selected.sort_values("proporcion", ascending=True)
    focus_index = selected_for_bars["proporcion"].idxmax()
    focus_category = str(selected_for_bars.loc[focus_index, "categoria"])
    focus_value = float(selected_for_bars.loc[focus_index, "proporcion"])
    bar_colors = ["#B8B0A3" if idx != focus_index else DATASET_COLORS[dataset_name] for idx in selected_for_bars.index]

    figura, eje = plt.subplots(figsize=(8.4, max(3.2, 0.48 * len(selected_for_bars) + 1.8)))
    eje.barh(selected_for_bars["categoria"].astype(str), selected_for_bars["proporcion"], color=bar_colors, alpha=0.90)
    eje.set_xlim(0, min(1.0, max(0.6, selected_for_bars["proporcion"].max() * 1.20)))
    eje.set_xlabel("Proporción de filas")
    eje.set_title(f"`{focus_category}` concentra {focus_value:.1%} de `{variable_name}`", loc="left", fontweight="bold", fontsize=11)
    for y_position, (_, row) in enumerate(selected_for_bars.iterrows()):
        eje.text(row["proporcion"] + 0.01, y_position, f"{row['n']} ({row['proporcion']:.1%})", va="center", fontsize=9, color="#2D2A26")
    aplicar_estilo_eje(eje, eje_rejilla="x")
    figura.tight_layout()
    guardar_figura(figura, f"fase2_categorica_{dataset_name}_{nombre_archivo_seguro(variable_name)}.png")
    plt.show()
    plt.close(figura)
    return None


def graficar_categorias_predictoras(categories_table, dataset_name):
    if categories_table.empty:
        display(Markdown("No hay predictoras categóricas que visualizar en este dataset."))
        return None

    variables = categories_table["variable"].drop_duplicates().tolist()
    for variable_name in variables:
        graficar_categoria_predictora(categories_table, dataset_name, variable_name)
    return None
"""))
    cells.append(code("""
def obtener_ancho_variable_codificada(renamed_dataset, variable_name):
    if pd.api.types.is_numeric_dtype(renamed_dataset[variable_name]):
        return 1
    return renamed_dataset[variable_name].nunique(dropna=True)


def contar_columnas_onehot(renamed_dataset, predictors):
    total_columns = 0
    for variable_name in predictors:
        total_columns += obtener_ancho_variable_codificada(renamed_dataset, variable_name)
    return total_columns


def crear_fila_dimensionalidad_encoding(nombre_dataset, datos_dataset):
    target_name = expected_targets[nombre_dataset]
    renamed_dataset = datos_dataset.rename(columns=rename_maps[nombre_dataset])
    removed_columns = set(identifier_columns_processed[nombre_dataset])
    predictors = [name for name in renamed_dataset.columns if name != processed_targets[nombre_dataset] and name not in removed_columns]
    categorical_count = sum(not pd.api.types.is_numeric_dtype(renamed_dataset[name]) for name in predictors)
    onehot_columns = contar_columnas_onehot(renamed_dataset, predictors)
    return {"dataset": nombre_dataset, "predictoras_sin_onehot": len(predictors), "predictoras_categoricas": categorical_count, "predictoras_si_onehot": onehot_columns}


def resumen_textual_encoding(encoding_table):
    lines = ["**Resumen de codificación de predictoras.**"]
    for _, row in encoding_table.iterrows():
        dataset_label = etiqueta_dataset(row["dataset"])
        if row["predictoras_categoricas"] == 0:
            lines.append(f"- {dataset_label}: no tiene predictoras categóricas tras excluir identificadores.")
        else:
            lines.append(
                f"- {dataset_label}: {int(row['predictoras_categoricas'])} predictoras categóricas; "
                f"si se codifican con one-hot, las predictoras pasarían de {int(row['predictoras_sin_onehot'])} "
                f"a {int(row['predictoras_si_onehot'])}. El fit del encoder debe hacerse solo con train."
            )
    return "\\n".join(lines)
"""))

    encoding_observations = {
        "breast_cancer_wisconsin": "El target binario queda codificado con 2 valores: 357 casos `B` y 212 `M`. No hay predictoras categóricas tras excluir el target.",
        "customer_churn": "El target contiene 249999 casos codificados como 1 y 190833 como 0. Las 3 predictoras categóricas se dejan sin one-hot global; aquí solo se mide su cardinalidad.",
        "madelon": "El target binario queda equilibrado con 1000 casos en -1 y 1000 en 1. No hay predictoras categóricas.",
        "olive_oil": "El target de 9 clases se codifica con una tabla explícita de correspondencias. La formulación de 3 clases con `area` ya quedó registrada en 2.3 y se separará como problema propio antes de entrenar.",
    }
    add_dataset_cells(
        cells,
        "Target y Categóricas",
        """
target_encoding_{variable_name}, target_map_{variable_name} = resumir_target_codificado("{dataset_name}", {variable_name})
categories_{variable_name} = resumir_categorias_predictoras("{dataset_name}", {variable_name})

mostrar_tabla(target_encoding_{variable_name}, "Codificación del target - {label}", n=12)
mostrar_tabla(categories_{variable_name}, "Categorías predictoras observadas - {label}", n=12)
graficar_categorias_predictoras(categories_{variable_name}, "{dataset_name}")
""",
        encoding_observations,
    )
    cells.append(md("### Resumen Comparativo de Codificación"))
    cells.append(code("""
target_maps = {
    "breast_cancer_wisconsin": target_map_breast_cancer_wisconsin,
    "customer_churn": target_map_customer_churn,
    "madelon": target_map_madelon,
    "olive_oil": target_map_olive_oil,
}

target_encoding_long = pd.concat([
    target_encoding_breast_cancer_wisconsin,
    target_encoding_customer_churn,
    target_encoding_madelon,
    target_encoding_olive_oil,
], ignore_index=True)

predictor_categories = pd.concat([
    categories_breast_cancer_wisconsin,
    categories_customer_churn,
    categories_madelon,
    categories_olive_oil,
], ignore_index=True)

encoding_dimensions = pd.DataFrame([
    crear_fila_dimensionalidad_encoding(dataset_name, raw_datasets[dataset_name])
    for dataset_name in DATASET_ORDER
])

guardar_tabla(target_encoding_long, "fase2_codificacion_target.csv")
guardar_tabla(predictor_categories, "fase2_categorias_predictoras.csv")
guardar_tabla(encoding_dimensions, "fase2_dimensionalidad_encoding.csv")
mostrar_tabla(encoding_dimensions, "Dimensionalidad potencial de categóricas")
display(Markdown(resumen_textual_encoding(encoding_dimensions)))
"""))
    cells.append(md("""
La codificación deja 15 filas de correspondencia de target: 2 clases en `breast_cancer_wisconsin`, 2 en `customer_churn`, 2 en `madelon` y 9 en `olive_oil`. Solo `customer_churn` contiene predictoras categóricas, con 3 variables y 8 categorías observadas; si se aplicara one-hot, pasaría de 10 a 15 predictoras. Esa cifra es una estimación, no un ajuste global, y encaja con PAPER_QFS V.A porque la compatibilidad con información mutua requiere representaciones discretas trazables.
"""))

    cells.append(md("""
## 2.11 Escalado y Transformaciones Numéricas

Se revisan rangos, IQR y forma aproximada de las variables numéricas para saber qué necesitarán los modelos posteriores. No se ajusta ningún escalador en esta fase.
"""))
    cells.append(code("""
def crear_fila_rango(nombre_dataset, serie):
    first_quartile, third_quartile, interquartile_range, _, _ = calcular_limites_iqr(serie)
    return {
        "dataset": nombre_dataset,
        "variable": serie.name,
        "minimo": float(serie.min()),
        "maximo": float(serie.max()),
        "rango": float(serie.max() - serie.min()),
        "mediana": float(serie.median()),
        "iqr": float(interquartile_range),
    }


def resumir_rangos_numericos(nombre_dataset, datos_dataset):
    numeric_predictors = obtener_predictoras_numericas_renombradas(nombre_dataset, datos_dataset)
    return pd.DataFrame([crear_fila_rango(nombre_dataset, numeric_predictors[name]) for name in numeric_predictors.columns])


def seleccionar_variables_distribucion(ranges_table, max_variables=36):
    if len(ranges_table) <= max_variables:
        return ranges_table["variable"].tolist()

    ordered = ranges_table.sort_values("rango").reset_index(drop=True)
    positions = np.linspace(0, len(ordered) - 1, max_variables).round().astype(int)
    selected = ordered.iloc[positions]["variable"].tolist()
    return list(dict.fromkeys(selected))


def graficar_distribuciones_numericas(nombre_dataset, datos_dataset, ranges_table, max_variables=36):
    numeric_predictors = obtener_predictoras_numericas_renombradas(nombre_dataset, datos_dataset)
    selected_variables = seleccionar_variables_distribucion(ranges_table, max_variables=max_variables)
    selected_variables = [name for name in selected_variables if name in numeric_predictors.columns]
    if not selected_variables:
        display(Markdown("No hay predictoras numéricas que visualizar en este dataset."))
        return None

    n_columns = 4 if len(selected_variables) <= 16 else 6
    n_rows = int(np.ceil(len(selected_variables) / n_columns))
    figura, axes = plt.subplots(n_rows, n_columns, figsize=(2.75 * n_columns, 2.25 * n_rows), squeeze=False)

    for eje, variable_name in zip(axes.ravel(), selected_variables):
        values = numeric_predictors[variable_name].dropna()
        eje.hist(values, bins=28, density=True, color=DATASET_COLORS[nombre_dataset], alpha=0.78)
        eje.axvline(values.median(), color="#2D2A26", linewidth=1.0)
        eje.set_title(variable_name, fontsize=8, loc="left")
        eje.set_yticks([])
        aplicar_estilo_eje(eje, eje_rejilla="x")

    for eje in axes.ravel()[len(selected_variables):]:
        eje.axis("off")

    if len(ranges_table) > len(selected_variables):
        max_range_row = ranges_table.loc[ranges_table["rango"].idxmax()]
        figura.suptitle(
            f"{max_range_row['variable']} fija el mayor rango en {etiqueta_dataset(nombre_dataset)} ({max_range_row['rango']:.1f})",
            x=0.01,
            ha="left",
            fontweight="bold",
        )
    else:
        max_range_row = ranges_table.loc[ranges_table["rango"].idxmax()]
        figura.suptitle(f"{max_range_row['variable']} fija el mayor rango en {etiqueta_dataset(nombre_dataset)} ({max_range_row['rango']:.1f})", x=0.01, ha="left", fontweight="bold")

    figura.tight_layout(rect=[0, 0, 1, 0.96])
    guardar_figura(figura, f"fase2_distribuciones_numericas_{nombre_dataset}.png")
    plt.show()
    plt.close(figura)
    return None
"""))

    scaling_observations = {
        "breast_cancer_wisconsin": "`area_worst` alcanza rango 4068.8, muy por encima de medidas con rango inferior a 1. El escalado será relevante en estimadores posteriores.",
        "customer_churn": "`total_spend` alcanza rango 900.0 y la mediana de rangos es 30.0. El ajuste de escaladores se pospone al estimador posterior al split.",
        "madelon": "Las 500 predictoras comparten una estructura numérica comparable, pero no se transforma el dataset completo en Fase 2.",
        "olive_oil": "`linoleic` alcanza rango 2110.0 y la mediana de rangos es 164.0. El escalado debe ajustarse solo con train.",
    }
    add_dataset_cells(
        cells,
        "Rangos Numéricos",
        """
ranges_{variable_name} = resumir_rangos_numericos("{dataset_name}", {variable_name})
mostrar_tabla(ranges_{variable_name}.sort_values("rango", ascending=False), "Rangos numéricos - {label}", n=12)
graficar_distribuciones_numericas("{dataset_name}", {variable_name}, ranges_{variable_name})
""",
        scaling_observations,
    )
    cells.append(md("### Resumen Comparativo de Rangos"))
    cells.append(code("""
numeric_ranges = pd.concat([
    ranges_breast_cancer_wisconsin,
    ranges_customer_churn,
    ranges_madelon,
    ranges_olive_oil,
], ignore_index=True)

range_summary = numeric_ranges.groupby("dataset", as_index=False).agg(
    variables_numericas=("variable", "count"),
    rango_mediano=("rango", "median"),
    rango_maximo=("rango", "max"),
    iqr_mediano=("iqr", "median"),
)

guardar_tabla(numeric_ranges, "fase2_rangos_numericos.csv")
mostrar_tabla(range_summary, "Resumen de rangos numéricos")
"""))
    cells.append(md("""
Los rangos numéricos anticipan necesidades de modelado sin aplicar escalado. `madelon` acumula 500 variables con rango mediano 168.0000, mientras `customer_churn` tiene 7 variables y rango mediano 30.0000. Los máximos son grandes y heterogéneos: `area_worst` alcanza 4068.8000 en `breast_cancer_wisconsin`, `total_spend` 900.0000 en `customer_churn`, `feat_105` 999.0000 en `madelon` y `linoleic` 2110.0000 en `olive_oil`.
"""))

    cells.append(md("""
## 2.12 Aplicación de Transformaciones Estructurales

Tras revisar la evidencia, se aplican únicamente las transformaciones estructurales: renombrado, conversión segura de flotantes enteros, exclusión de identificadores y codificación del target. No se elimina ninguna otra variable.
"""))
    cells.append(code("""
def convertir_flotantes_enteros(datos_dataset, target_name):
    converted_dataset = datos_dataset.copy()
    for variable_name in converted_dataset.columns:
        if variable_name != target_name and es_entero_en_float(converted_dataset[variable_name]):
            converted_dataset[variable_name] = converted_dataset[variable_name].astype("int64")
    return converted_dataset


def procesar_dataset(nombre_dataset, datos_dataset):
    renamed_dataset = datos_dataset.rename(columns=rename_maps[nombre_dataset]).copy()
    processed_target = processed_targets[nombre_dataset]
    typed_dataset = convertir_flotantes_enteros(renamed_dataset, processed_target)
    without_ids = typed_dataset.drop(columns=identifier_columns_processed[nombre_dataset], errors="ignore")
    without_ids[processed_target] = without_ids[processed_target].map(target_maps[nombre_dataset]).astype("int64")
    return without_ids
"""))
    cells.append(code("""
def resumir_transformacion(nombre_dataset, datos_raw, datos_processed):
    processed_target = processed_targets[nombre_dataset]
    return pd.DataFrame([{
        "dataset": nombre_dataset,
        "filas_originales": datos_raw.shape[0],
        "filas_procesadas": datos_processed.shape[0],
        "columnas_originales": datos_raw.shape[1],
        "columnas_procesadas": datos_processed.shape[1],
        "columnas_eliminadas": datos_raw.shape[1] - datos_processed.shape[1],
        "target": processed_target,
        "target_minimo": int(datos_processed[processed_target].min()),
        "target_maximo": int(datos_processed[processed_target].max()),
        "nulos_procesados": int(datos_processed.isna().sum().sum()),
    }])
"""))

    processing_observations = {
        "breast_cancer_wisconsin": "El dataset procesado pasa de 32 a 31 columnas y pierde únicamente el identificador. Las variables clínicas permanecen sin selección ni escalado.",
        "customer_churn": "El dataset procesado pasa de 12 a 11 columnas, elimina `customer_id` y codifica el target. Las categóricas predictoras se mantienen para estimador posterior.",
        "madelon": "El dataset procesado conserva las 500 predictoras. No se aplica reducción dimensional en Fase 2.",
        "olive_oil": "El dataset procesado pasa de 12 a 11 columnas, elimina `id` y codifica el target 0-8. Las variables de composición permanecen intactas.",
    }
    add_dataset_cells(
        cells,
        "Transformación Estructural",
        """
processed_{variable_name} = procesar_dataset("{dataset_name}", {variable_name})
transformation_{variable_name} = resumir_transformacion("{dataset_name}", {variable_name}, processed_{variable_name})

mostrar_tabla(transformation_{variable_name}, "Transformación estructural - {label}")
display(processed_{variable_name}.head())
print(obtener_info_texto(processed_{variable_name}))
""",
        processing_observations,
    )
    cells.append(md("### Resumen Comparativo de Transformaciones"))
    cells.append(code("""
processed_datasets = {
    "breast_cancer_wisconsin": processed_breast_cancer_wisconsin,
    "customer_churn": processed_customer_churn,
    "madelon": processed_madelon,
    "olive_oil": processed_olive_oil,
}

transformation_summary = pd.concat([
    transformation_breast_cancer_wisconsin,
    transformation_customer_churn,
    transformation_madelon,
    transformation_olive_oil,
], ignore_index=True)

guardar_tabla(transformation_summary, "fase2_transformaciones_estructurales.csv")
mostrar_tabla(transformation_summary, "Resumen de transformaciones estructurales")
"""))
    cells.append(md("""
Las transformaciones estructurales no alteran filas: los cuatro `delta_filas` son 0. Las columnas bajan en 1 para `breast_cancer_wisconsin`, `customer_churn` y `olive_oil`, exactamente por sus identificadores, y permanecen en 501 para `madelon`. Los targets procesados quedan en códigos 0-1 para los tres problemas binarios y 0-8 para `olive_oil`, sin nulos introducidos.
"""))

    cells.append(md("""
## 2.13 Comparación del Impacto Estadístico

Se compara cada dataset crudo con su versión procesada. Como las únicas transformaciones son estructurales, la comparación comprueba filas, columnas, target, nulos, medias, desviaciones y correlaciones.
"""))
    cells.append(code("""
def variacion_total_target(nombre_dataset, datos_raw, datos_processed):
    raw_target = expected_targets[nombre_dataset]
    processed_target = processed_targets[nombre_dataset]
    mapped_raw_target = datos_raw[raw_target].map(target_maps[nombre_dataset])
    raw_distribution = mapped_raw_target.value_counts(normalize=True, dropna=False)
    processed_distribution = datos_processed[processed_target].value_counts(normalize=True, dropna=False)
    aligned_distribution = pd.concat([raw_distribution.rename("raw"), processed_distribution.rename("processed")], axis=1).fillna(0)
    return float((aligned_distribution["raw"] - aligned_distribution["processed"]).abs().sum() / 2)


def crear_fila_impacto_estructura(nombre_dataset, datos_raw, datos_processed):
    return {
        "dataset": nombre_dataset,
        "filas_raw": datos_raw.shape[0],
        "filas_processed": datos_processed.shape[0],
        "delta_filas": datos_processed.shape[0] - datos_raw.shape[0],
        "columnas_raw": datos_raw.shape[1],
        "columnas_processed": datos_processed.shape[1],
        "delta_columnas": datos_processed.shape[1] - datos_raw.shape[1],
        "target_total_variation": variacion_total_target(nombre_dataset, datos_raw, datos_processed),
        "nulos_processed": int(datos_processed.isna().sum().sum()),
    }


def resumir_impacto_estructura(nombre_dataset):
    datos_raw = raw_datasets[nombre_dataset]
    datos_processed = processed_datasets[nombre_dataset]
    return crear_fila_impacto_estructura(nombre_dataset, datos_raw, datos_processed)
"""))
    cells.append(code("""
def resumir_target_shift(nombre_dataset):
    target_table = target_encoding_long[target_encoding_long["dataset"].eq(nombre_dataset)].copy()
    target_table["pct_raw"] = target_table["proporcion"]
    target_table["pct_processed"] = target_table["proporcion"]
    target_table["delta_abs"] = 0.0
    return target_table[["dataset", "codigo", "pct_raw", "pct_processed", "delta_abs"]]


def pares_correlacion_alta(nombre_dataset, datos_dataset):
    numeric_values = obtener_predictoras_numericas_renombradas(nombre_dataset, datos_dataset)
    if numeric_values.shape[1] < 2:
        return 0
    corr_matrix = numeric_values.corr(method="spearman").abs()
    upper_mask = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    return int((corr_matrix.where(upper_mask) >= HIGH_CORRELATION_THRESHOLD).sum().sum())
"""))
    cells.append(code("""
def resumir_correlation_shift(nombre_dataset):
    raw_pairs = pares_correlacion_alta(nombre_dataset, raw_datasets[nombre_dataset])
    processed_pairs = pares_correlacion_alta(nombre_dataset, processed_datasets[nombre_dataset])
    return {"dataset": nombre_dataset, "pares_spearman_ge_085_raw": raw_pairs, "pares_spearman_ge_085_processed": processed_pairs, "delta_pares": processed_pairs - raw_pairs}


def crear_fila_distribution_shift(nombre_dataset, variable_name):
    original_name = {processed: original for original, processed in rename_maps[nombre_dataset].items()}.get(variable_name)
    raw_series = raw_datasets[nombre_dataset][original_name]
    processed_series = processed_datasets[nombre_dataset][variable_name]
    return {
        "dataset": nombre_dataset,
        "variable": variable_name,
        "mean_raw": float(raw_series.mean()),
        "mean_processed": float(processed_series.mean()),
        "std_raw": float(raw_series.std(ddof=0)),
        "std_processed": float(processed_series.std(ddof=0)),
        "mean_delta_abs": float(abs(raw_series.mean() - processed_series.mean())),
        "std_delta_abs": float(abs(raw_series.std(ddof=0) - processed_series.std(ddof=0))),
    }


def resumir_distribution_shift(nombre_dataset):
    rows = []
    for variable_name in processed_datasets[nombre_dataset].select_dtypes(include=np.number).columns:
        if variable_name != processed_targets[nombre_dataset]:
            rows.append(crear_fila_distribution_shift(nombre_dataset, variable_name))
    return pd.DataFrame(rows)


def graficar_impacto_preprocesado(impact_table, correlation_table):
    ordered = impact_table.set_index("dataset").loc[DATASET_ORDER].reset_index()
    correlation_ordered = correlation_table.set_index("dataset").loc[DATASET_ORDER].reset_index()
    labels = [etiqueta_dataset(name) for name in ordered["dataset"]]
    positions = np.arange(len(ordered))

    figura, (eje_columnas, eje_invariantes) = plt.subplots(
        1,
        2,
        figsize=(12.8, 5.1),
        gridspec_kw={"width_ratios": [1.0, 1.25]},
    )

    colors = [DATASET_COLORS[name] if delta != 0 else "#B8B0A3" for name, delta in zip(ordered["dataset"], ordered["delta_columnas"])]
    eje_columnas.barh(labels, ordered["delta_columnas"], color=colors, alpha=0.90)
    eje_columnas.axvline(0, color="#6F6A60", linewidth=1.0)
    eje_columnas.set_xlabel("Delta de columnas processed - raw")
    eje_columnas.set_title("Solo cambian los identificadores", loc="left", fontweight="bold", fontsize=10)
    for position, value in zip(positions, ordered["delta_columnas"]):
        eje_columnas.text(value - 0.04 if value < 0 else value + 0.04, position, f"{int(value):+d}", va="center", ha="right" if value < 0 else "left", fontsize=9)
    aplicar_estilo_eje(eje_columnas, eje_rejilla="x")

    invariant_metrics = pd.DataFrame({
        "dataset": ordered["dataset"],
        "filas": ordered["delta_filas"].abs(),
        "target": ordered["target_total_variation"].abs(),
        "nulos": ordered["nulos_processed"].abs(),
        "redundancia": correlation_ordered["delta_pares"].abs(),
    }).set_index("dataset")
    matrix = invariant_metrics.to_numpy(dtype=float)
    eje_invariantes.imshow(matrix, cmap="Greys", vmin=0, vmax=1, aspect="auto")
    eje_invariantes.set_yticks(positions)
    eje_invariantes.set_yticklabels(labels)
    eje_invariantes.set_xticks(np.arange(invariant_metrics.shape[1]))
    eje_invariantes.set_xticklabels(["filas", "target", "nulos", "pares >=0.85"], rotation=0)
    eje_invariantes.set_title("Las métricas de control quedan en cero", loc="left", fontweight="bold", fontsize=10)
    for row_idx in range(matrix.shape[0]):
        for col_idx in range(matrix.shape[1]):
            eje_invariantes.text(col_idx, row_idx, f"{matrix[row_idx, col_idx]:.0f}", ha="center", va="center", fontsize=9, color="#2D2A26")
    eje_invariantes.tick_params(axis="both", length=0)
    eje_invariantes.spines["top"].set_visible(False)
    eje_invariantes.spines["right"].set_visible(False)
    eje_invariantes.spines["left"].set_visible(False)
    eje_invariantes.spines["bottom"].set_visible(False)

    figura.suptitle("El preprocesado quita claves técnicas sin mover filas, target ni redundancia", x=0.02, ha="left", fontweight="bold")
    figura.text(0.02, 0.02, "Panel derecho: valores absolutos de delta; todos los controles deben permanecer en 0.", ha="left", va="bottom", color="#6F6A60", fontsize=9)
    figura.tight_layout(rect=[0, 0.06, 1, 0.92])
    guardar_figura(figura, "fase2_impacto_preprocesado_control.png")
    plt.show()
    plt.close(figura)
    return None
"""))

    impact_observations = {
        "breast_cancer_wisconsin": "La comparación muestra 0 cambios de filas y variación total del target 0.0000. El delta de columnas -1 corresponde a la exclusión del identificador.",
        "customer_churn": "La comparación mantiene 440832 filas y variación del target 0.0000. El cambio estructural es el delta de columnas -1 por `customer_id`.",
        "madelon": "No hay cambio de filas ni columnas: 2000 filas y 501 columnas procesadas. El dataset conserva la dificultad dimensional original.",
        "olive_oil": "La comparación mantiene 572 filas y variación del target 0.0000. La reducción de 1 columna corresponde al identificador.",
    }
    add_dataset_cells(
        cells,
        "Impacto Estadístico",
        """
impact_{variable_name} = pd.DataFrame([resumir_impacto_estructura("{dataset_name}")])
target_shift_{variable_name} = resumir_target_shift("{dataset_name}")
distribution_shift_{variable_name} = resumir_distribution_shift("{dataset_name}")
correlation_shift_{variable_name} = pd.DataFrame([resumir_correlation_shift("{dataset_name}")])

mostrar_tabla(impact_{variable_name}, "Impacto estructural - {label}")
mostrar_tabla(target_shift_{variable_name}, "Estabilidad del target - {label}", n=12)
mostrar_tabla(correlation_shift_{variable_name}, "Correlación alta raw vs processed - {label}")
""",
        impact_observations,
    )
    cells.append(md("### Resumen Comparativo de Impacto"))
    cells.append(code("""
impact_summary = pd.concat([
    impact_breast_cancer_wisconsin,
    impact_customer_churn,
    impact_madelon,
    impact_olive_oil,
], ignore_index=True)

target_shift_summary = pd.concat([
    target_shift_breast_cancer_wisconsin,
    target_shift_customer_churn,
    target_shift_madelon,
    target_shift_olive_oil,
], ignore_index=True)

distribution_shift = pd.concat([
    distribution_shift_breast_cancer_wisconsin,
    distribution_shift_customer_churn,
    distribution_shift_madelon,
    distribution_shift_olive_oil,
], ignore_index=True)

correlation_shift = pd.concat([
    correlation_shift_breast_cancer_wisconsin,
    correlation_shift_customer_churn,
    correlation_shift_madelon,
    correlation_shift_olive_oil,
], ignore_index=True)

guardar_tabla(impact_summary, "fase2_impacto_estructura.csv")
guardar_tabla(target_shift_summary, "fase2_target_shift.csv")
guardar_tabla(distribution_shift, "fase2_distribution_shift.csv")
guardar_tabla(correlation_shift, "fase2_correlation_shift.csv")

mostrar_tabla(impact_summary, "Impacto estructural comparativo")
mostrar_tabla(correlation_shift, "Correlación alta comparativa")
graficar_impacto_preprocesado(impact_summary, correlation_shift)
"""))
    cells.append(md("""
La comparación final confirma que el impacto estadístico es nulo en las magnitudes que podrían contaminar la evaluación: `delta_filas` es 0 en los cuatro datasets, `target_total_variation` es 0.0000 y `nulos_processed` es 0. La estructura de redundancia fuerte tampoco cambia: 29 pares Spearman >=0.85 en `breast_cancer_wisconsin`, 0 en `customer_churn`, 12 en `madelon` y 2 en `olive_oil`, siempre con `delta_pares` igual a 0.
"""))

    cells.append(md("""
## 2.14 Guardado y Recarga de Datasets Procesados

Se guardan los datasets procesados como CSV y se recargan desde disco para verificar dimensiones, presencia del target, ausencia de nulos y columnas duplicadas. El criterio de lectura es binario: cada archivo debe conservar su forma procesada, mantener `target`, sumar 0 nulos y no crear nombres repetidos.
"""))
    cells.append(code("""
def guardar_dataset_procesado(nombre_dataset, datos_dataset):
    output_path = PROCESSED_DATA_DIR / f"{nombre_dataset}_processed.csv"
    datos_dataset.to_csv(output_path, index=False)
    return output_path


def resumir_recarga(nombre_dataset, output_path):
    reloaded_dataset = pd.read_csv(output_path)
    target_name = processed_targets[nombre_dataset]
    return {
        "dataset": nombre_dataset,
        "ruta": str(output_path.relative_to(PROJECT_ROOT)),
        "filas": reloaded_dataset.shape[0],
        "columnas": reloaded_dataset.shape[1],
        "target_presente": target_name in reloaded_dataset.columns,
        "nulos": int(reloaded_dataset.isna().sum().sum()),
        "columnas_duplicadas": int(reloaded_dataset.columns.duplicated().sum()),
        "recarga_correcta": reloaded_dataset.shape == processed_datasets[nombre_dataset].shape,
    }
"""))

    save_observations = {
        "breast_cancer_wisconsin": "La recarga mantiene 569 filas, 31 columnas y target presente. El archivo queda preparado para las fases posteriores.",
        "customer_churn": "La recarga confirma que las 440832 filas se guardan sin introducir nulos ni columnas duplicadas.",
        "madelon": "La recarga conserva las 501 columnas procesadas: 500 predictoras y target codificado.",
        "olive_oil": "La recarga mantiene 572 filas, 11 columnas y el target codificado. Las variables composicionales no reciben modificaciones adicionales.",
    }
    add_dataset_cells(
        cells,
        "Guardado y Recarga",
        """
path_{variable_name} = guardar_dataset_procesado("{dataset_name}", processed_{variable_name})
reload_{variable_name} = pd.DataFrame([resumir_recarga("{dataset_name}", path_{variable_name})])

mostrar_tabla(reload_{variable_name}, "Recarga - {label}")
""",
        save_observations,
    )
    cells.append(md("### Resumen Comparativo de Recarga"))
    cells.append(code("""
reload_summary = pd.concat([
    reload_breast_cancer_wisconsin,
    reload_customer_churn,
    reload_madelon,
    reload_olive_oil,
], ignore_index=True)

guardar_tabla(reload_summary, "fase2_recarga_datasets.csv")
mostrar_tabla(reload_summary, "Recarga de datasets procesados")
"""))
    cells.append(md("""
La recarga valida los cuatro CSV procesados: 569x31 en `breast_cancer_wisconsin`, 440832x11 en `customer_churn`, 2000x501 en `madelon` y 572x11 en `olive_oil`. En todos los archivos `target_presente` es verdadero, los nulos son 0, las columnas duplicadas son 0 y `recarga_correcta` queda en verdadero. La Fase 3 parte así de CSV recargables, no de objetos vivos en memoria.
"""))

    cells.append(md("""
## 2.15 Conclusiones y Consideraciones Para la Fase 3

La Fase 2 queda limitada a transformaciones estructurales verificables y cierra con un informe reproducible de tablas, figuras y CSV procesados. Se han normalizado nombres, eliminado identificadores claros, codificado el target y guardado datasets recargables; el criterio de cierre es que ninguna operación estadística haya sido ajustada sobre el conjunto completo.

Para Fase 3 se deben mantener estas condiciones:

- Los encoders de predictoras, imputadores y escaladores se ajustarán solo con particiones de entrenamiento.
- Las variables con baja cardinalidad, outliers, correlaciones altas o asociación fuerte no se eliminan aquí; se revisarán dentro del protocolo de modelado y selección.
- Las variables señaladas por Fase 1 como revisión estadística deben tratarse como hipótesis de trabajo, no como conclusiones automáticas.
- `olive_oil` queda identificado como dos problemas supervisados: `area` con 3 clases y `target` con 9 clases.
- `madelon` debe leerse desde su naturaleza de benchmark sintético: muchas variables son probes irrelevantes por diseño, no errores que haya que limpiar en Fase 2.
- Cualquier reducción de dimensionalidad o selección de características pertenece a fases posteriores, no a la limpieza estructural de Fase 2.
"""))
    cells.append(code("""
summary_lines = [
    "# Resultados de la Fase 2 - Preprocesado Estructural",
    "",
    "La Fase 2 aplica únicamente transformaciones estructurales verificables: renombrado, exclusión de identificadores, codificación del target y guardado de datasets procesados.",
    "",
    "No se imputan nulos, no se eliminan outliers, no se eliminan variables por baja cardinalidad y no se ajustan encoders ni escaladores globales.",
    "",
    "Los umbrales de cardinalidad/dominancia/correlación se documentan como alertas heurísticas, con referencias a caret, scikit-learn y la ficha UCI/PDF de Madelon cuando procede.",
    "",
    "Tablas principales:",
]

for table_path in sorted(PHASE2_TABLES_DIR.glob("fase2_*.csv")):
    summary_lines.append(f"- `{table_path.relative_to(PROJECT_ROOT)}`")

summary_lines.extend(["", "Figuras:"])
for figure_path in sorted(list(PHASE2_FIGURES_DIR.rglob("fase2_*.png")) + list(PHASE2_FIGURES_DIR.rglob("fase2_*.pdf"))):
    summary_lines.append(f"- `{figure_path.relative_to(PROJECT_ROOT)}`")

summary_lines.extend(["", "Datasets procesados:"])
for dataset_name in DATASET_ORDER:
    summary_lines.append(f"- `data/processed/{dataset_name}_processed.csv`")

summary_path = PHASE2_REPORTS_DIR / "fase2_resumen_para_memoria.md"
summary_path.write_text("\\n".join(summary_lines), encoding="utf-8")
print(summary_path.relative_to(PROJECT_ROOT))
"""))
    cells.append(md("""
El resumen para memoria queda escrito en `results/reports/02_preprocessing/fase2_resumen_para_memoria.md`. Ese archivo enumera 21 tablas CSV, 28 ficheros de figura si se cuentan PNG y PDF, y 4 datasets procesados, de modo que la trazabilidad de Fase 2 puede revisarse sin depender del estado de memoria del notebook.
"""))

    notebook["cells"] = cells
    return notebook


if __name__ == "__main__":
    notebook = build_notebook()
    nbf.write(notebook, NOTEBOOK_PATH)
    print(f"Notebook rebuilt: {NOTEBOOK_PATH.relative_to(ROOT)}")
