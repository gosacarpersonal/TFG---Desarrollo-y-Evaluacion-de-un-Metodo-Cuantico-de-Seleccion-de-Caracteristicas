from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "fase4.ipynb"

DATASETS_OPERATIVOS = [
    ("breast_cancer_wisconsin", "Breast Cancer Wisconsin"),
    ("customer_churn", "Customer Churn"),
    ("madelon", "Madelon"),
    ("olive_oil_3class", "Olive Oil 3 Clases"),
    ("olive_oil_9class", "Olive Oil 9 Clases"),
]


def md(text):
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code(text):
    return nbf.v4.new_code_cell(text.strip() + "\n")


def render_template(text, dataset_name, label):
    return text.replace("__DATASET__", dataset_name).replace("__LABEL__", label)


def add_dataset_cells(cells, title, code_template, observations):
    for dataset_name, label in DATASETS_OPERATIVOS:
        cells.append(md(f"### {title}: `{dataset_name}`"))
        cells.append(code(render_template(code_template, dataset_name, label)))
        if dataset_name in observations:
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

## Notebook 04 - Fase 4: Creación y Auditoría de Splits

Esta fase crea las particiones `train`, `validation` y `test` que utilizarán las fases posteriores. El objetivo no es entrenar modelos finales ni seleccionar variables, sino comprobar que las particiones conservan el problema original sin solapes, pérdidas de clases, drift evidente o señales de leakage.

La fase se plantea como una comprobación de representatividad antes de construir modelos: cada fila debe pertenecer a una única partición, las clases del target deben seguir presentes en los tres subconjuntos y las distribuciones de las variables no deben mostrar cambios que comprometan la comparación posterior entre métodos de selección de características.

Este notebook fija una condición experimental compartida para el contraste final del TFG. Según la propuesta oficial, el objetivo 5 exige comparar el método cuántico frente a los mejores métodos clásicos; por tanto, los mismos splits `train`/`validation`/`test` servirán al brazo clásico y al método QFS sobre átomos neutros. En los trabajos QFS del proyecto, la relevancia se codifica mediante información mutua con el target, la redundancia mediante información mutua entre variables traducida a distancias atómicas vía MDS y el objetivo `Q(x; alfa)` favorece subconjuntos compactos, especialmente en rangos pequeños de características. Por eso el rigor en drift, leakage y validación adversarial no es un trámite: protege la comparación final contra diferencias de particionado que podrían confundirse con una ventaja clásica o cuántica.
"""))

    cells.append(md("""
## Importación de Librerías

Se utilizan herramientas estándar de `pandas`, `scipy`, `scikit-learn` y `matplotlib` para cargar datos, crear particiones estratificadas, contrastar estabilidad estadística y representar los resultados de auditoría.
"""))
    cells.append(code("""
from pathlib import Path
import io
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from IPython.display import Markdown, display
from scipy.stats import chi2_contingency, ks_2samp, wasserstein_distance
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import normalized_mutual_info_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)
"""))

    cells.append(md("""
## Definición de Rutas y Directorios de Salida

Se fijan las rutas de entrada y salida. Al iniciar la fase se limpian las salidas anteriores de Fase 4 para que no queden tablas, figuras o informes de versiones previas.
"""))
    cells.append(code("""
# Rutas principales del proyecto.
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
SPLITS_DIR = PROJECT_ROOT / "data" / "splits"
PHASE3_TABLES_DIR = PROJECT_ROOT / "results" / "tables" / "03_postprocessing_audit"
PHASE4_TABLES_DIR = PROJECT_ROOT / "results" / "tables" / "04_split_audit"
PHASE4_FIGURES_DIR = PROJECT_ROOT / "results" / "figures" / "04_split_audit"
PHASE4_REPORTS_DIR = PROJECT_ROOT / "results" / "reports" / "04_split_audit"

for output_dir in [SPLITS_DIR, PHASE4_TABLES_DIR, PHASE4_FIGURES_DIR, PHASE4_REPORTS_DIR]:
    output_dir.mkdir(parents=True, exist_ok=True)

for old_path in PHASE4_TABLES_DIR.rglob("*.csv"):
    old_path.unlink()

for old_path in PHASE4_FIGURES_DIR.rglob("*"):
    if old_path.suffix.lower() in {".png", ".pdf"}:
        old_path.unlink()

for old_path in PHASE4_FIGURES_DIR.rglob("*.png"):
    old_path.unlink()

for old_path in PHASE4_REPORTS_DIR.rglob("*"):
    if old_path.is_file() and old_path.suffix.lower() in {".md", ".tex", ".png"}:
        old_path.unlink()
"""))
    cells.append(md("""
La inicialización fija las entradas procesadas y prepara los destinos de trabajo de la fase. La limpieza inicial garantiza que las tablas y figuras exportadas al final correspondan a una única ejecución reproducible.
"""))

    cells.append(md("""
## Configuración Visual y Parámetros Generales

El split base es 70/15/15 y se estratifica por target cuando las clases lo permiten. La semilla fija hace reproducible la asignación de filas y facilita que las fases posteriores trabajen siempre con los mismos subconjuntos.

Los parámetros `MAX_SAMPLE_PCA`, `MAX_SAMPLE_ADVERSARIAL` y `MAX_SAMPLE_LEAKAGE` son límites computacionales: reducen el coste de diagnósticos exploratorios cuando un dataset es grande, pero no cambian las particiones guardadas. Los valores se fijan por el mayor coste esperado en `customer_churn` y mantienen miles de observaciones por diagnóstico, suficiente para lectura exploratoria reproducible sin convertir la auditoría en un entrenamiento pesado.

Los umbrales `PSI_REVIEW_THRESHOLD`, `KS_REVIEW_THRESHOLD` y `WASSERSTEIN_REVIEW_THRESHOLD` son criterios de revisión exploratoria, alineados con la auditoría distributiva de Fase 3 para mantener escalas comparables entre fases. No son reglas universales de descarte. `AUC_LEAKAGE_REVIEW_THRESHOLD` y `NMI_LEAKAGE_REVIEW_THRESHOLD` se fijan en 0.99 porque solo interesan proxies casi deterministas del target; valores más bajos se interpretarán con el resto de métricas, no como leakage confirmado.
"""))
    cells.append(code("""
RANDOM_STATE = 2026
TRAIN_PCT = 0.70
VALIDATION_PCT = 0.15
TEST_PCT = 0.15
MAX_SAMPLE_PCA = 6000
MAX_SAMPLE_ADVERSARIAL = 12000
MAX_SAMPLE_LEAKAGE = 12000
MAX_PCA_COMPONENTS = 5

PSI_REVIEW_THRESHOLD = 0.10
KS_REVIEW_THRESHOLD = 0.10
WASSERSTEIN_REVIEW_THRESHOLD = 0.20
AUC_LEAKAGE_REVIEW_THRESHOLD = 0.99
NMI_LEAKAGE_REVIEW_THRESHOLD = 0.99

SPLIT_ORDER = ["train", "validation", "test"]

SOURCE_DATASETS = {
    "breast_cancer_wisconsin": "breast_cancer_wisconsin",
    "customer_churn": "customer_churn",
    "madelon": "madelon",
    "olive_oil_3class": "olive_oil",
    "olive_oil_9class": "olive_oil",
}

TARGET_BY_DATASET = {
    "breast_cancer_wisconsin": "target",
    "customer_churn": "target",
    "madelon": "target",
    "olive_oil_3class": "area",
    "olive_oil_9class": "target",
}

EXCLUDED_BY_DATASET = {
    "breast_cancer_wisconsin": [],
    "customer_churn": [],
    "madelon": [],
    "olive_oil_3class": ["target", "palmitic"],
    "olive_oil_9class": ["area", "palmitic"],
}

DATASET_ORDER = list(SOURCE_DATASETS)
DATASET_LABELS = {
    "breast_cancer_wisconsin": "Breast Cancer Wisconsin",
    "customer_churn": "Customer Churn",
    "madelon": "Madelon",
    "olive_oil_3class": "Olive Oil 3 Clases",
    "olive_oil_9class": "Olive Oil 9 Clases",
}

SPLIT_COLORS = {"train": "#2F6F9F", "validation": "#D9822B", "test": "#5E8C61"}

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

pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 80)
pd.set_option("display.max_colwidth", 90)
"""))

    cells.append(md("""
## Utilidades Generales del Notebook

Las siguientes funciones guardan tablas, muestran salidas, exportan figuras y mantienen un formato visual común. Son utilidades transversales; las funciones analíticas se definen en la sección donde se usan.
"""))
    cells.append(code("""
def guardar_tabla(tabla, nombre_archivo):
    ruta_tabla = PHASE4_TABLES_DIR / nombre_archivo
    tabla.to_csv(ruta_tabla, index=False)
    return ruta_tabla


COLUMNAS_LECTURA = {
    "dataset": "Dataset",
    "fuente": "Fuente",
    "filas": "Filas",
    "columnas": "Columnas",
    "target": "Variable objetivo",
    "target_presente": "Objetivo presente",
    "clases_target": "Clases objetivo",
    "features_potenciales": "Predictoras potenciales",
    "nmi_area_target": "NMI area-target",
    "nmi_palmitic_target": "NMI palmitic-objetivo",
    "max_valores_palmitic_por_clase": "Máximo valores palmitic por clase",
    "variable": "Variable",
    "rol": "Rol",
    "tipo": "Tipo",
    "excluida": "Excluida de X",
    "motivo_exclusion": "Motivo de exclusión",
    "predictoras": "Predictoras",
    "categoricas": "Categóricas",
    "numericas": "Numéricas",
    "target_en_X": "Objetivo dentro de X",
    "variable_excluida": "Variable excluida",
    "nmi_con_target": "NMI con objetivo",
    "auc_univariante": "AUC univariante",
    "split": "Partición",
    "proporcion": "Proporción",
    "estratificado": "Estratificado",
    "random_state": "Semilla",
    "filas_train": "Filas train",
    "filas_validation": "Filas validación",
    "filas_test": "Filas test",
    "original_index": "Índice original",
    "indice_min": "Índice mínimo",
    "indice_max": "Índice máximo",
    "n": "N",
    "x_rows": "Filas X",
    "y_rows": "Filas y",
    "same_index": "Mismo índice",
    "same_columns": "Mismas columnas",
    "index_overlap": "Solape de índice",
    "row_hash_overlap": "Solape de filas",
    "duplicados_X": "Duplicados en X",
    "clase": "Clase",
    "conteo": "Conteo",
    "proporcion_train": "Proporción train",
    "proporcion_validation": "Proporción validación",
    "proporcion_test": "Proporción test",
    "max_delta_proporcion": "Delta máximo de proporción",
    "comparacion": "Comparación",
    "chi2": "Chi-cuadrado",
    "p_value": "p-valor",
    "min_expected": "Esperado mínimo",
    "ks_stat": "Estadístico KS",
    "ks_pvalue": "p-valor KS",
    "wasserstein": "Distancia Wasserstein",
    "psi": "PSI",
    "drift_score": "Puntuación de drift",
    "drift_flag": "Revisión por drift",
    "variables_con_flag": "Variables en revisión",
    "max_psi": "PSI máximo",
    "max_distancia": "Distancia máxima",
    "pc1": "CP1",
    "pc2": "CP2",
    "componente": "Componente",
    "varianza_explicada": "Varianza explicada",
    "varianza_acumulada": "Varianza acumulada",
    "pc1_media": "Media CP1",
    "pc2_media": "Media CP2",
    "variables_numericas": "Variables numéricas",
    "variables_categoricas": "Variables categóricas",
    "nmi_ge_099": "Variables con NMI >= 0,99",
    "nombres_sospechosos": "Nombres sospechosos",
    "muestras_usadas": "Muestras usadas",
    "auc_cv": "AUC medio",
    "auc_fold_std": "Desviación AUC",
    "fold": "Fold",
    "auc": "AUC",
    "index_overlap_total": "Solape total de índice",
    "row_hash_overlap_total": "Solape total de filas",
}


def mostrar_tabla(tabla, nombre=None, n=10):
    if nombre is not None:
        display(Markdown(f"**{nombre}** - {tabla.shape[0]} filas, {tabla.shape[1]} columnas."))
    tabla_lectura = tabla.head(n).rename(columns=COLUMNAS_LECTURA)
    display(tabla_lectura)


def guardar_figura(figura, nombre_archivo):
    ruta_png = PHASE4_FIGURES_DIR / nombre_archivo
    ruta_pdf = ruta_png.with_suffix(".pdf")
    figura.savefig(ruta_png, dpi=300, bbox_inches="tight")
    figura.savefig(ruta_pdf, bbox_inches="tight")
    return ruta_png, ruta_pdf


def aplicar_estilo_eje(eje, eje_rejilla="x"):
    eje.spines["top"].set_visible(False)
    eje.spines["right"].set_visible(False)
    eje.grid(axis=eje_rejilla, alpha=0.65)
    eje.set_axisbelow(True)
"""))
    cells.append(code("""
def obtener_info_texto(datos_dataset):
    salida_info = io.StringIO()
    datos_dataset.info(buf=salida_info)
    return salida_info.getvalue()


def etiqueta_dataset(nombre_dataset):
    return DATASET_LABELS.get(nombre_dataset, nombre_dataset.replace("_", " ").title())
"""))

    cells.append(md("""
## 4.1 Carga de Datasets Procesados y Formulaciones Operativas

Se cargan los datasets procesados de Fase 3 y se confirma que las tablas estadísticas previas estén disponibles antes de crear particiones nuevas. `olive_oil` se evalúa en dos formulaciones porque `docs/decisions/fase4_olive_oil_formulations.md` documenta dos tareas supervisadas trazables: `olive_oil_3class`, con `area` como target de 3 clases, y `olive_oil_9class`, con `target` como etiqueta regional de 9 clases. La columna `palmitic` se audita como proxy porque toma un único valor por región; por eso se excluye de ambas formulaciones antes del split. El resultado se lee verificando filas, columnas, clases y variables excluidas, no comparando rendimiento todavía.
"""))
    cells.append(code("""
phase3_table_names = [
    "fase3_resumen_metricas_split.csv",
    "fase3_target_resumen.csv",
    "fase3_dimensionalidad_final.csv",
    "fase3_correlaciones_resumen.csv",
]

for table_name in phase3_table_names:
    table_path = PHASE3_TABLES_DIR / table_name
    assert table_path.exists()
"""))
    cells.append(md("""
Las 4 tablas estadísticas de Fase 3 están disponibles, incluida la dimensionalidad final y el resumen de target. Esa base previa permite crear splits sobre datos ya procesados y auditados, sin reabrir decisiones de limpieza en esta fase.
"""))
    cells.append(code("""
def cargar_dataset_procesado(nombre_fuente):
    ruta_dataset = PROCESSED_DATA_DIR / f"{nombre_fuente}_processed.csv"
    if not ruta_dataset.exists():
        raise FileNotFoundError(f"No existe el dataset procesado: {ruta_dataset}")
    return pd.read_csv(ruta_dataset)


def resumir_carga_operativa(nombre_dataset):
    datos_dataset = datos_operativos[nombre_dataset]
    target_name = TARGET_BY_DATASET[nombre_dataset]
    return {
        "dataset": nombre_dataset,
        "fuente": SOURCE_DATASETS[nombre_dataset],
        "filas": len(datos_dataset),
        "columnas": datos_dataset.shape[1],
        "target": target_name,
        "target_presente": target_name in datos_dataset.columns,
        "clases_target": datos_dataset[target_name].nunique(dropna=True),
        "features_potenciales": datos_dataset.shape[1] - 1,
    }
"""))
    cells.append(code("""
def calcular_nmi_columnas(datos_dataset, variable_a, variable_b):
    return normalized_mutual_info_score(datos_dataset[variable_a].astype(str), datos_dataset[variable_b].astype(str))


def resumir_formulaciones_olive_oil():
    datos_olive = datos_fuente["olive_oil"]
    return pd.DataFrame([crear_fila_formulacion_olive(nombre_dataset, datos_olive) for nombre_dataset in ["olive_oil_3class", "olive_oil_9class"]])


def crear_fila_formulacion_olive(nombre_dataset, datos_olive):
    target_name = TARGET_BY_DATASET[nombre_dataset]
    return {
        "dataset": nombre_dataset,
        "target": target_name,
        "clases_target": datos_olive[target_name].nunique(dropna=True),
        "nmi_area_target": calcular_nmi_columnas(datos_olive, "area", "target"),
        "nmi_palmitic_target": calcular_nmi_columnas(datos_olive, "palmitic", target_name),
        "max_valores_palmitic_por_clase": datos_olive.groupby(target_name)["palmitic"].nunique().max(),
    }
"""))
    cells.append(code("""
datos_fuente = {
    "breast_cancer_wisconsin": cargar_dataset_procesado("breast_cancer_wisconsin"),
    "customer_churn": cargar_dataset_procesado("customer_churn"),
    "madelon": cargar_dataset_procesado("madelon"),
    "olive_oil": cargar_dataset_procesado("olive_oil"),
}

datos_operativos = {
    nombre_dataset: datos_fuente[nombre_fuente].copy()
    for nombre_dataset, nombre_fuente in SOURCE_DATASETS.items()
}

resumen_carga = pd.DataFrame([resumir_carga_operativa(nombre_dataset) for nombre_dataset in DATASET_ORDER])
formulaciones_olive_oil = resumir_formulaciones_olive_oil()

guardar_tabla(resumen_carga, "fase4_carga_datasets.csv")
guardar_tabla(formulaciones_olive_oil, "fase4_formulaciones_olive_oil.csv")
mostrar_tabla(resumen_carga, "Carga de datasets operativos", n=10)
mostrar_tabla(formulaciones_olive_oil, "Métricas de formulaciones Olive Oil", n=10)
"""))
    cells.append(md("""
La carga deja 5 datasets operativos: 569 filas en `breast_cancer_wisconsin`, 440.832 en `customer_churn`, 2.000 en `madelon` y 572 en cada formulación de `olive_oil`. La decisión documentada separa `olive_oil_3class` con 3 clases y `olive_oil_9class` con 9 clases; además, `palmitic` alcanza NMI 1,000 con `target` en la formulación regional, de modo que queda tratado como proxy excluido antes del split.
"""))

    load_observations = {
        "breast_cancer_wisconsin": "La carga muestra 569 filas y 31 columnas, con target binario y 30 variables morfológicas candidatas. Esta escala permite un split test de 86 filas sin perder clases.",
        "customer_churn": "La carga alcanza 440.832 filas y 11 columnas; de las 10 predictoras, 3 son categóricas. Fase 4 las conserva sin codificación global para que el modelado posterior ajuste transformaciones solo con train.",
        "madelon": "La tabla confirma 2.000 filas, 501 columnas y 500 variables numéricas. El target tiene 2 clases equilibradas, de modo que el split estratificado debe mantener exactamente la proporción 50/50.",
        "olive_oil_3class": "`area` se usa como target de 3 clases sobre 572 filas; `target` y `palmitic` quedan fuera de `X`. La exclusión evita que una etiqueta de 9 regiones o su proxy entren en la tarea macro-regional.",
        "olive_oil_9class": "`target` se usa como target de 9 clases sobre las mismas 572 filas; `area` y `palmitic` quedan fuera de `X`. Esta formulación conserva 8 ácidos grasos como predictores auditables.",
    }
    add_dataset_cells(
        cells,
        "Inspección Inicial",
        """
datos___DATASET__ = datos_operativos["__DATASET__"]
print("shape:", datos___DATASET__.shape)
display(datos___DATASET__.head())
print(obtener_info_texto(datos___DATASET__))
""",
        load_observations,
    )

    cells.append(md("""
## 4.2 Separación de Variables Predictoras y Target

Se separan `X` e `y` de forma explícita por dataset operativo. En `olive_oil`, las etiquetas alternativas y `palmitic` se excluyen de `X` antes del split porque contienen información demasiado cercana al target que se quiere predecir.
"""))
    cells.append(code("""
def columnas_no_predictoras(nombre_dataset):
    target_name = TARGET_BY_DATASET[nombre_dataset]
    return [target_name, *EXCLUDED_BY_DATASET[nombre_dataset]]


def separar_variables_xy(nombre_dataset):
    datos_dataset = datos_operativos[nombre_dataset]
    no_predictoras = set(columnas_no_predictoras(nombre_dataset))
    columnas_x = [name for name in datos_dataset.columns if name not in no_predictoras]
    return datos_dataset[columnas_x].copy(), datos_dataset[TARGET_BY_DATASET[nombre_dataset]].copy()


def crear_fila_variable_xy(nombre_dataset, variable_name):
    datos_dataset = datos_operativos[nombre_dataset]
    no_predictoras = set(columnas_no_predictoras(nombre_dataset))
    return {
        "dataset": nombre_dataset,
        "variable": variable_name,
        "dtype": str(datos_dataset[variable_name].dtype),
        "valores_unicos": datos_dataset[variable_name].nunique(dropna=False),
        "nulos": datos_dataset[variable_name].isna().sum(),
        "en_X": variable_name not in no_predictoras,
        "es_target": variable_name == TARGET_BY_DATASET[nombre_dataset],
        "excluida": variable_name in no_predictoras,
    }
"""))
    cells.append(code("""
def resumir_variables_xy(nombre_dataset):
    columnas_dataset = datos_operativos[nombre_dataset].columns
    return pd.DataFrame([crear_fila_variable_xy(nombre_dataset, variable_name) for variable_name in columnas_dataset])


def resumir_xy_dataset(nombre_dataset):
    x_dataset, y_dataset = datasets_xy[nombre_dataset]
    return {
        "dataset": nombre_dataset,
        "filas": len(y_dataset),
        "features": x_dataset.shape[1],
        "target": TARGET_BY_DATASET[nombre_dataset],
        "target_clases": y_dataset.nunique(dropna=True),
        "target_en_X": TARGET_BY_DATASET[nombre_dataset] in x_dataset.columns,
        "categoricas_en_X": sum(not pd.api.types.is_numeric_dtype(x_dataset[name]) for name in x_dataset.columns),
    }
"""))
    cells.append(code("""
def calcular_metrica_variable_excluida(nombre_dataset, variable_name):
    datos_dataset = datos_operativos[nombre_dataset]
    target_name = TARGET_BY_DATASET[nombre_dataset]
    return {
        "dataset": nombre_dataset,
        "variable": variable_name,
        "target": target_name,
        "valores_unicos": datos_dataset[variable_name].nunique(dropna=False),
        "nmi_con_target": calcular_nmi_columnas(datos_dataset, variable_name, target_name),
        "auc_abs_binaria": calcular_auc_binaria(datos_dataset[variable_name], datos_dataset[target_name]),
    }


def calcular_auc_binaria(serie_variable, serie_target):
    if serie_target.nunique(dropna=True) != 2 or serie_variable.nunique(dropna=True) < 2:
        return np.nan
    return calcular_auc_seguro(serie_variable, serie_target)
"""))
    cells.append(code("""
def calcular_auc_seguro(serie_variable, serie_target):
    target_codificado = LabelEncoder().fit_transform(serie_target.astype(str))
    variable_codificada = codificar_serie_para_auc(serie_variable)
    try:
        auc_value = roc_auc_score(target_codificado, variable_codificada)
    except ValueError:
        return np.nan
    return max(float(auc_value), float(1 - auc_value))


def codificar_serie_para_auc(serie_variable):
    if pd.api.types.is_numeric_dtype(serie_variable):
        return pd.to_numeric(serie_variable, errors="coerce").fillna(serie_variable.median())
    return LabelEncoder().fit_transform(serie_variable.astype(str))
"""))
    cells.append(code("""
datasets_xy = {nombre_dataset: separar_variables_xy(nombre_dataset) for nombre_dataset in DATASET_ORDER}

variables_xy = pd.concat([resumir_variables_xy(nombre_dataset) for nombre_dataset in DATASET_ORDER], ignore_index=True)
resumen_xy = pd.DataFrame([resumir_xy_dataset(nombre_dataset) for nombre_dataset in DATASET_ORDER])

variables_excluidas_rows = []
for nombre_dataset in DATASET_ORDER:
    for variable_name in EXCLUDED_BY_DATASET[nombre_dataset]:
        variables_excluidas_rows.append(calcular_metrica_variable_excluida(nombre_dataset, variable_name))

variables_excluidas_metricas = pd.DataFrame(variables_excluidas_rows)

guardar_tabla(variables_xy, "fase4_variables_xy.csv")
guardar_tabla(resumen_xy, "fase4_resumen_xy.csv")
guardar_tabla(variables_excluidas_metricas, "fase4_variables_excluidas_metricas.csv")
mostrar_tabla(resumen_xy, "Resumen X/y por dataset", n=10)
mostrar_tabla(variables_xy.sort_values(["dataset", "excluida", "variable"], ascending=[True, False, True]), "Relación global de variables X/y", n=30)
mostrar_tabla(variables_excluidas_metricas, "Métricas de variables excluidas en Olive Oil", n=10)
"""))
    cells.append(md("""
La separación global produce 30 predictoras en `breast_cancer_wisconsin`, 10 en `customer_churn`, 500 en `madelon` y 8 en cada formulación de `olive_oil`; en los 5 casos `target_en_X` queda en `False`. La relación `variables_xy` permite reconstruir qué columnas entran en `X` y cuáles se excluyen, mientras que las métricas de Olive Oil cuantifican el riesgo: `palmitic` tiene NMI 1,000 con `target` en `olive_oil_9class` y la etiqueta alternativa `area` tiene NMI 0,665 con la región de 9 clases.
"""))

    xy_observations = {
        "breast_cancer_wisconsin": "La separación deja `target_en_X=False` y conserva 30 predictoras. No hay variables categóricas, así que el riesgo principal no es codificación sino representatividad de las clases.",
        "customer_churn": "La separación deja 10 predictoras y 3 categóricas en `X`. Esas 3 columnas se mantienen crudas para que Fase 6 las codifique dentro del entrenamiento ajustado con train.",
        "madelon": "La separación conserva 500 predictoras numéricas y 2 clases. La dimensionalidad no se reduce aquí, porque la selección debe ocurrir después sobre los mismos splits auditados.",
        "olive_oil_3class": "La separación retiene 8 predictoras y excluye 2 columnas no predictoras. `target` y `palmitic` quedan fuera para que la tarea de 3 clases no vea información regional directa.",
        "olive_oil_9class": "La separación retiene 8 predictoras y excluye `area` junto con `palmitic`. La NMI 1,000 entre `palmitic` y `target` justifica que esa variable no llegue a selección.",
    }
    add_dataset_cells(
        cells,
        "Variables Predictoras y Target",
        """
variables_xy___DATASET__ = variables_xy[variables_xy["dataset"].eq("__DATASET__")]
resumen_xy___DATASET__ = resumen_xy[resumen_xy["dataset"].eq("__DATASET__")]

mostrar_tabla(resumen_xy___DATASET__, "Resumen X/y - __LABEL__", n=5)
mostrar_tabla(variables_xy___DATASET__.sort_values(["excluida", "variable"], ascending=[False, True]), "Variables X/y - __LABEL__", n=15)
""",
        xy_observations,
    )

    cells.append(md("""
## 4.3 Creación de Splits Train, Validation y Test

Se aplica un split 70/15/15 con estratificación por target. La semilla se fija para reproducibilidad y los índices originales se conservan para auditar solapes.
"""))
    cells.append(code("""
def admite_estratificacion(serie_target):
    return serie_target.value_counts(dropna=False).min() >= 4


def crear_splits_dataset(nombre_dataset):
    x_dataset, y_dataset = datasets_xy[nombre_dataset]
    stratify_main = y_dataset if admite_estratificacion(y_dataset) else None
    x_train, x_temp, y_train, y_temp = train_test_split(
        x_dataset, y_dataset, train_size=TRAIN_PCT, random_state=RANDOM_STATE, stratify=stratify_main
    )
    stratify_temp = y_temp if stratify_main is not None else None
    x_val, x_test, y_val, y_test = train_test_split(
        x_temp, y_temp, test_size=0.5, random_state=RANDOM_STATE + 1, stratify=stratify_temp
    )
    return {"train": (x_train, y_train), "validation": (x_val, y_val), "test": (x_test, y_test)}
"""))
    cells.append(code("""
def resumir_protocolo_dataset(nombre_dataset):
    y_dataset = datasets_xy[nombre_dataset][1]
    return {
        "dataset": nombre_dataset,
        "train_pct": TRAIN_PCT,
        "validation_pct": VALIDATION_PCT,
        "test_pct": TEST_PCT,
        "stratify": admite_estratificacion(y_dataset),
        "random_state": RANDOM_STATE,
        "min_clase": int(y_dataset.value_counts(dropna=False).min()),
    }


def crear_filas_tamanos(nombre_dataset):
    rows = []
    for split_name, split_data in splits_dataset[nombre_dataset].items():
        rows.append(crear_fila_tamano(nombre_dataset, split_name, split_data))
    return rows
"""))
    cells.append(code("""
def crear_fila_tamano(nombre_dataset, split_name, split_data):
    expected_pct = {"train": TRAIN_PCT, "validation": VALIDATION_PCT, "test": TEST_PCT}[split_name]
    observed_pct = len(split_data[1]) / len(datasets_xy[nombre_dataset][1])
    return {
        "dataset": nombre_dataset,
        "split": split_name,
        "filas": len(split_data[1]),
        "proporcion": observed_pct,
        "proporcion_esperada": expected_pct,
        "delta_abs": abs(observed_pct - expected_pct),
    }
"""))
    cells.append(code("""
def guardar_splits_dataset(nombre_dataset):
    dataset_dir = SPLITS_DIR / nombre_dataset
    dataset_dir.mkdir(parents=True, exist_ok=True)
    for split_name, (x_split, y_split) in splits_dataset[nombre_dataset].items():
        x_split.to_csv(dataset_dir / f"X_{split_name}.csv", index=True, index_label="original_index")
        y_split.to_frame("target").to_csv(dataset_dir / f"y_{split_name}.csv", index=True, index_label="original_index")


def crear_filas_indices(nombre_dataset):
    rows = []
    for split_name, (x_split, _) in splits_dataset[nombre_dataset].items():
        rows.extend({"dataset": nombre_dataset, "split": split_name, "original_index": index} for index in x_split.index)
    return rows
"""))
    cells.append(code("""
splits_dataset = {nombre_dataset: crear_splits_dataset(nombre_dataset) for nombre_dataset in DATASET_ORDER}

for nombre_dataset in DATASET_ORDER:
    guardar_splits_dataset(nombre_dataset)

protocolo_split = pd.DataFrame([resumir_protocolo_dataset(nombre_dataset) for nombre_dataset in DATASET_ORDER])
tamanos_split = pd.DataFrame([row for nombre_dataset in DATASET_ORDER for row in crear_filas_tamanos(nombre_dataset)])
indices_split = pd.DataFrame([row for nombre_dataset in DATASET_ORDER for row in crear_filas_indices(nombre_dataset)])

guardar_tabla(protocolo_split, "fase4_protocolo_split.csv")
guardar_tabla(tamanos_split, "fase4_tamanos_split.csv")
guardar_tabla(indices_split, "fase4_indices_split.csv")
mostrar_tabla(protocolo_split, "Protocolo aplicado por dataset", n=10)
mostrar_tabla(tamanos_split, "Tamaños de split", n=15)
"""))
    cells.append(md("""
El protocolo confirma el mismo reparto 70/15/15 en los 5 datasets, con estratificación por target y semilla 2026. En tamaños absolutos, `customer_churn` domina la fase con 308.582 filas de train, mientras que las dos formulaciones de `olive_oil` conservan 400/86/86 observaciones.
"""))
    cells.append(code("""
figura, eje = plt.subplots(figsize=(9.4, 4.8))
pivot_tamanos = tamanos_split.pivot(index="dataset", columns="split", values="proporcion").loc[DATASET_ORDER, SPLIT_ORDER]
left_values = np.zeros(len(pivot_tamanos))
for split_name in SPLIT_ORDER:
    eje.barh([etiqueta_dataset(name) for name in pivot_tamanos.index], pivot_tamanos[split_name], left=left_values, color=SPLIT_COLORS[split_name], label=split_name.title())
    left_values += pivot_tamanos[split_name].to_numpy()
eje.set_xlim(0, 1)
eje.set_xlabel("Proporción del dataset")
eje.set_title("Los Splits Conservan el Protocolo 70/15/15", loc="left", fontweight="bold")
eje.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.28))
aplicar_estilo_eje(eje, eje_rejilla="x")
guardar_figura(figura, "fase4_tamanos_split.png")
plt.show()
"""))
    cells.append(md("""
La figura global confirma que las proporciones observadas siguen el protocolo 70/15/15 con desviaciones máximas pequeñas: 0,00114 en `breast_cancer_wisconsin`, 0,0000009 en `customer_churn` y 0,000699 en cada formulación de `olive_oil`; `madelon` queda exactamente en 0,700/0,150/0,150. Esta estabilidad de tamaño abre la comprobación más estricta por dataset: índices conservados, estratificación y ausencia de solapes.
"""))

    split_observations = {
        "breast_cancer_wisconsin": "El reparto queda en 398 filas train, 85 validation y 86 test. La mayor desviación frente al 70/15/15 es 0,00114, causada solo por redondeo entero.",
        "customer_churn": "El reparto queda en 308.582 filas train y 66.125 en cada partición de validación y test. La desviación máxima frente al protocolo es menor que 0,000001.",
        "madelon": "El split produce 1.400 filas train, 300 validation y 300 test. Las proporciones son exactamente 0,700, 0,150 y 0,150.",
        "olive_oil_3class": "El reparto queda en 400 filas train, 86 validation y 86 test. La estratificación es necesaria porque las 3 macro-regiones no tienen el mismo tamaño.",
        "olive_oil_9class": "El reparto también queda en 400/86/86. La auditoría del target comprueba después que las 9 clases regionales sigan presentes en las tres particiones.",
    }
    add_dataset_cells(
        cells,
        "Tamaños de Split",
        """
tamanos___DATASET__ = tamanos_split[tamanos_split["dataset"].eq("__DATASET__")]
indices___DATASET__ = indices_split[indices_split["dataset"].eq("__DATASET__")]

mostrar_tabla(tamanos___DATASET__, "Tamaños - __LABEL__", n=10)
mostrar_tabla(indices___DATASET__.groupby("split", as_index=False).agg(indice_min=("original_index", "min"), indice_max=("original_index", "max"), n=("original_index", "count")), "Rango de índices conservados - __LABEL__", n=10)
""",
        split_observations,
    )

    cells.append(md("""
## 4.4 Recarga, Duplicados y Solapes Entre Particiones

Se recargan las particiones guardadas y se comprueba que `X` e `y` mantienen longitud, columnas e índices. Después se auditan solapes de índices y de filas idénticas entre splits.
"""))
    cells.append(code("""
def recargar_split(nombre_dataset, split_name):
    dataset_dir = SPLITS_DIR / nombre_dataset
    x_split = pd.read_csv(dataset_dir / f"X_{split_name}.csv", index_col="original_index")
    y_split = pd.read_csv(dataset_dir / f"y_{split_name}.csv", index_col="original_index")["target"]
    return x_split, y_split


def comprobar_recarga_split(nombre_dataset, split_name):
    x_guardado, y_guardado = splits_dataset[nombre_dataset][split_name]
    x_recargado, y_recargado = recargar_split(nombre_dataset, split_name)
    return {
        "dataset": nombre_dataset,
        "split": split_name,
        "filas_X": len(x_recargado),
        "filas_y": len(y_recargado),
        "columnas_X": x_recargado.shape[1],
        "len_X_eq_y": len(x_recargado) == len(y_recargado),
        "columnas_ok": list(x_recargado.columns) == list(x_guardado.columns),
        "indice_ok": list(x_recargado.index) == list(x_guardado.index),
    }
"""))
    cells.append(code("""
def hash_filas(datos_split):
    return pd.util.hash_pandas_object(datos_split, index=False)


def medir_solape_splits(nombre_dataset, split_a, split_b):
    x_a = splits_dataset[nombre_dataset][split_a][0]
    x_b = splits_dataset[nombre_dataset][split_b][0]
    return {
        "dataset": nombre_dataset,
        "split_a": split_a,
        "split_b": split_b,
        "index_overlap": len(set(x_a.index) & set(x_b.index)),
        "row_hash_overlap": len(set(hash_filas(x_a)) & set(hash_filas(x_b))),
    }
"""))
    cells.append(code("""
def contar_duplicados_internos(nombre_dataset, split_name):
    x_split = splits_dataset[nombre_dataset][split_name][0]
    return {
        "dataset": nombre_dataset,
        "split": split_name,
        "duplicados_X": int(x_split.duplicated().sum()),
    }


def combinaciones_split():
    return [("train", "validation"), ("train", "test"), ("validation", "test")]
"""))
    cells.append(code("""
recarga_splits = pd.DataFrame([
    comprobar_recarga_split(nombre_dataset, split_name)
    for nombre_dataset in DATASET_ORDER
    for split_name in SPLIT_ORDER
])

solapes_split = pd.DataFrame([
    medir_solape_splits(nombre_dataset, split_a, split_b)
    for nombre_dataset in DATASET_ORDER
    for split_a, split_b in combinaciones_split()
])

duplicados_internos = pd.DataFrame([
    contar_duplicados_internos(nombre_dataset, split_name)
    for nombre_dataset in DATASET_ORDER
    for split_name in SPLIT_ORDER
])

guardar_tabla(recarga_splits, "fase4_recarga_splits.csv")
guardar_tabla(solapes_split, "fase4_solapes_splits.csv")
guardar_tabla(duplicados_internos, "fase4_duplicados_internos.csv")
mostrar_tabla(recarga_splits, "Comprobación de recarga", n=15)
mostrar_tabla(solapes_split, "Solapes entre splits", n=15)
mostrar_tabla(duplicados_internos, "Duplicados internos por split", n=15)
"""))
    cells.append(md("""
La recarga global valida 15 pares `X/y` con igualdad de filas, columnas e índices en todas las particiones. Los 15 pares de splits tienen `index_overlap=0` y `row_hash_overlap=0`, y los 15 splits presentan `duplicados_X=0`; por tanto, las salidas guardadas reproducen exactamente la asignación creada en memoria antes de auditar distribuciones.
"""))

    overlap_observations = {
        "breast_cancer_wisconsin": "Los 3 splits recargan con `len_X_eq_y=True`, `columnas_ok=True` e `indice_ok=True`. Los 3 pares de particiones tienen 0 solapes de índice y 0 solapes de hash.",
        "customer_churn": "La comprobación cubre 440.832 índices repartidos en 3 pares `X/y`. Incluso con 308.582 filas en train, los solapes de índice y de hash quedan en 0.",
        "madelon": "Los 3 splits conservan 500 columnas tras recarga. Los pares train-validation, train-test y validation-test tienen `index_overlap=0`.",
        "olive_oil_3class": "Los 400, 86 y 86 registros recargan con 8 columnas predictoras y sin duplicados internos. En un dataset pequeño, este 0 de solapes es una condición crítica.",
        "olive_oil_9class": "La formulación multiclase comparte origen con `olive_oil_3class`, pero dentro de sus 3 particiones hay 0 solapes de índice y 0 filas duplicadas.",
    }
    add_dataset_cells(
        cells,
        "Integridad de Splits",
        """
recarga___DATASET__ = recarga_splits[recarga_splits["dataset"].eq("__DATASET__")]
solapes___DATASET__ = solapes_split[solapes_split["dataset"].eq("__DATASET__")]
duplicados___DATASET__ = duplicados_internos[duplicados_internos["dataset"].eq("__DATASET__")]

mostrar_tabla(recarga___DATASET__, "Recarga - __LABEL__", n=10)
mostrar_tabla(solapes___DATASET__, "Solapes - __LABEL__", n=10)
mostrar_tabla(duplicados___DATASET__, "Duplicados internos - __LABEL__", n=10)
""",
        overlap_observations,
    )

    cells.append(md("""
## 4.5 Conservación del Target Entre Splits

Se comparan las proporciones de clase entre `train`, `validation` y `test` para comprobar que ninguna partición cambia el problema de clasificación. Como los splits se construyen con estratificación cuando las clases lo permiten, el contraste chi-cuadrado no se interpreta como una prueba de hipótesis informativa e independiente: funciona como control de coherencia del estratificado y como alarma si una clase desaparece o queda con frecuencia esperada demasiado baja. Su `p_value` se lee junto con el tamaño muestral, porque en datasets grandes puede detectar diferencias muy pequeñas.

La lectura combina tres evidencias: proporciones por clase, mayor delta frente a train y recuento esperado mínimo del chi-cuadrado. Una clase ausente o un delta grande sería más preocupante que un p-valor aislado. Esta sección no decide modelos; solo verifica que la selección posterior trabajará sobre el mismo problema de clasificación en train, validation y test.

La columna `max_delta_proporcion` mide, para cada clase, la diferencia entre la mayor y la menor proporción observada entre splits. Es una medida práctica del tamaño del cambio. `min_expected_count` muestra la celda esperada más pequeña del contraste chi-cuadrado; si es baja, la aproximación del test es menos estable. `clases_ausentes` cuenta celdas con frecuencia cero en la tabla split-clase; una clase ausente en `validation` o `test` sería una limitación directa para evaluar modelos sobre esa clase.
"""))
    cells.append(code("""
def crear_distribucion_target(nombre_dataset):
    rows = []
    clases_dataset = clases_target_dataset(nombre_dataset)
    for split_name, (_, y_split) in splits_dataset[nombre_dataset].items():
        rows.extend(crear_filas_target_split(nombre_dataset, split_name, y_split, clases_dataset))
    return pd.DataFrame(rows)


def clases_target_dataset(nombre_dataset):
    clases = set()
    for _, y_split in splits_dataset[nombre_dataset].values():
        clases.update(y_split.dropna().unique())
    return sorted(clases, key=lambda value: str(value))


def crear_filas_target_split(nombre_dataset, split_name, y_split, clases_dataset):
    counts = y_split.value_counts(dropna=False).reindex(clases_dataset, fill_value=0)
    return [
        {"dataset": nombre_dataset, "split": split_name, "clase": class_value, "n": int(count), "proporcion": count / len(y_split)}
        for class_value, count in counts.items()
    ]
"""))
    cells.append(code("""
def calcular_diferencias_target(nombre_dataset):
    distribution = distribucion_target[distribucion_target["dataset"].eq(nombre_dataset)]
    rows = []
    for class_value, group in distribution.groupby("clase"):
        rows.append(crear_fila_diferencia_target(nombre_dataset, class_value, group))
    return pd.DataFrame(rows)


def crear_fila_diferencia_target(nombre_dataset, class_value, group):
    return {
        "dataset": nombre_dataset,
        "clase": class_value,
        "min_proporcion": group["proporcion"].min(),
        "max_proporcion": group["proporcion"].max(),
        "max_delta_proporcion": group["proporcion"].max() - group["proporcion"].min(),
    }
"""))
    cells.append(code("""
def crear_tabla_contingencia_target(nombre_dataset):
    rows = []
    for split_name, (_, y_split) in splits_dataset[nombre_dataset].items():
        rows.extend({"split": split_name, "clase": class_value} for class_value in y_split)
    return pd.crosstab(pd.DataFrame(rows)["split"], pd.DataFrame(rows)["clase"])


def probar_homogeneidad_target(nombre_dataset):
    contingency = crear_tabla_contingencia_target(nombre_dataset)
    statistic, p_value, _, expected = chi2_contingency(contingency)
    return {
        "dataset": nombre_dataset,
        "chi2_statistic": float(statistic),
        "chi2_p_value": float(p_value),
        "min_expected_count": float(expected.min()),
        "clases_ausentes": int((contingency == 0).sum().sum()),
    }
"""))
    cells.append(code("""
def resumen_target_plot(nombre_dataset):
    test_row = tests_target[tests_target["dataset"].eq(nombre_dataset)].iloc[0]
    max_delta = diferencias_target[diferencias_target["dataset"].eq(nombre_dataset)]["max_delta_proporcion"].max()
    return {
        "max_delta": max_delta,
        "min_expected": test_row["min_expected_count"],
        "clases_ausentes": int(test_row["clases_ausentes"]),
    }


def graficar_target_dataset(nombre_dataset):
    subset = distribucion_target[distribucion_target["dataset"].eq(nombre_dataset)]
    pivot = subset.pivot(index="clase", columns="split", values="proporcion").fillna(0)
    delta_train = pivot[SPLIT_ORDER].subtract(pivot["train"], axis=0).abs()[["validation", "test"]].max(axis=1)
    top_delta = delta_train.sort_values(ascending=False).head(12).sort_values()
    metricas = resumen_target_plot(nombre_dataset)
    figura, ejes = plt.subplots(1, 2, figsize=(12.0, 4.8), gridspec_kw={"width_ratios": [1.45, 1]})
    pivot[SPLIT_ORDER].plot(kind="bar", ax=ejes[0], color=[SPLIT_COLORS[name] for name in SPLIT_ORDER], width=0.78)
    ejes[0].set_ylabel("Proporción")
    ejes[0].set_xlabel("Clase")
    ejes[0].set_title("Proporciones por clase", loc="left", fontweight="bold")
    ejes[0].legend(frameon=False, ncol=3, title="")
    ejes[1].barh(top_delta.index.astype(str), top_delta.values, color="#7A8F5A")
    ejes[1].set_xlabel("Mayor delta frente a train")
    ejes[1].set_title("Clases más sensibles", loc="left", fontweight="bold")
    ejes[1].text(
        0.98,
        0.05,
        f"max delta={metricas['max_delta']:.3f}\\nmin esperado={metricas['min_expected']:.1f}\\nclases ausentes={metricas['clases_ausentes']}",
        transform=ejes[1].transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        bbox={"facecolor": "#FAF7F2", "edgecolor": "#D8D0C4", "boxstyle": "round,pad=0.35"},
    )
    for eje in ejes:
        aplicar_estilo_eje(eje, eje_rejilla="y" if eje is ejes[0] else "x")
    figura.suptitle(f"{etiqueta_dataset(nombre_dataset)}: Representatividad del Target", fontsize=13, y=1.03)
    figura.tight_layout()
    guardar_figura(figura, f"fase4_target_{nombre_dataset}.png")
    plt.show()
"""))
    cells.append(code("""
distribucion_target = pd.concat([crear_distribucion_target(nombre_dataset) for nombre_dataset in DATASET_ORDER], ignore_index=True)
diferencias_target = pd.concat([calcular_diferencias_target(nombre_dataset) for nombre_dataset in DATASET_ORDER], ignore_index=True)
tests_target = pd.DataFrame([probar_homogeneidad_target(nombre_dataset) for nombre_dataset in DATASET_ORDER])

guardar_tabla(distribucion_target, "fase4_target_distribucion.csv")
guardar_tabla(diferencias_target, "fase4_target_diferencias.csv")
guardar_tabla(tests_target, "fase4_target_tests.csv")
mostrar_tabla(tests_target, "Contrastes de homogeneidad del target", n=10)
mostrar_tabla(diferencias_target.sort_values("max_delta_proporcion", ascending=False), "Mayores diferencias de proporción", n=15)
"""))
    cells.append(md("""
La lectura global del target no muestra pérdidas de clase: `clases_ausentes=0` en los 5 datasets. El mayor delta de proporción es 0,0116 y aparece en varias clases de `olive_oil`, mientras que `madelon` queda en 0,0000 y `customer_churn` en 0,00000079; los p-valores chi-cuadrado permanecen entre 0,9968 y 1,0000, con mínimo esperado de 3,76 en `olive_oil_9class`, que será la formulación más sensible por tamaño de clase.
"""))

    target_observations = {
        "breast_cancer_wisconsin": "El máximo delta de proporción es 0.0046 y no hay clases ausentes; el split conserva el desbalance binario original sin cambiar el problema.",
        "customer_churn": "El máximo delta es menor que 1e-6. Con 440.832 filas, la conclusión práctica es conservación completa del target, no solo p-valor alto.",
        "madelon": "La estratificación deja exactamente 50/50 en las tres particiones. La dificultad posterior no procede del target, sino de la relación 500 features / 2.000 filas.",
        "olive_oil_3class": "El máximo delta queda en 0.0116 y todas las macro-regiones aparecen en train, validation y test. La formulación de 3 clases es representativa.",
        "olive_oil_9class": "Todas las clases están presentes, pero el recuento esperado mínimo es 3.76. El split es válido, aunque la evaluación posterior tendrá intervalos amplios por clases minoritarias.",
    }
    add_dataset_cells(
        cells,
        "Target Entre Splits",
        """
target_distribucion___DATASET__ = distribucion_target[distribucion_target["dataset"].eq("__DATASET__")]
target_diferencias___DATASET__ = diferencias_target[diferencias_target["dataset"].eq("__DATASET__")]
target_tests___DATASET__ = tests_target[tests_target["dataset"].eq("__DATASET__")]

mostrar_tabla(target_distribucion___DATASET__, "Distribución target - __LABEL__", n=30)
mostrar_tabla(target_diferencias___DATASET__.sort_values("max_delta_proporcion", ascending=False), "Diferencias target - __LABEL__", n=12)
mostrar_tabla(target_tests___DATASET__, "Test target - __LABEL__", n=5)
graficar_target_dataset("__DATASET__")
""",
        target_observations,
    )

    cells.append(md("""
## 4.6 Drift Univariante de Variables Entre Splits

Se compara `train` frente a `validation` y `test` para detectar cambios de distribución que puedan afectar la evaluación posterior. En variables numéricas, KS mide la mayor distancia entre distribuciones acumuladas y capta cambios de forma o localización; Wasserstein estima cuánto habría que desplazar la masa de una distribución para parecerse a la otra y se estandariza por la desviación típica de `train`; PSI resume cambios por intervalos y facilita una lectura de estabilidad poblacional.

En variables categóricas, el chi-cuadrado contrasta si las frecuencias por categoría cambian entre particiones. La distancia de proporciones resume el tamaño práctico de ese cambio y el PSI categórico conserva la misma lógica de estabilidad que en variables numéricas. Se combinan contrastes y tamaños de efecto porque los p-values dependen del tamaño muestral; aquí el objetivo es localizar señales de revisión, no seleccionar ni descartar variables.

La figura por dataset no dibuja solo el score agregado: separa la métrica que dispara cada alerta. Así se distingue si una variable cambia por forma acumulada (KS), por desplazamiento de escala (Wasserstein/distancia) o por redistribución por intervalos (PSI). Esta distinción importa porque en la selección posterior una alerta de drift es una cautela de representatividad, no una instrucción automática de eliminar variables.
"""))
    cells.append(code("""
def calcular_psi_categorico(base, comparacion):
    base_prop = base.astype(str).value_counts(normalize=True)
    comp_prop = comparacion.astype(str).value_counts(normalize=True)
    categorias = sorted(set(base_prop.index) | set(comp_prop.index))
    return sumar_psi([base_prop.get(cat, 0) for cat in categorias], [comp_prop.get(cat, 0) for cat in categorias])


def sumar_psi(base_values, comp_values):
    epsilon = 1e-6
    total = 0.0
    for base_value, comp_value in zip(base_values, comp_values):
        base_safe = max(base_value, epsilon)
        comp_safe = max(comp_value, epsilon)
        total += (comp_safe - base_safe) * np.log(comp_safe / base_safe)
    return float(total)
"""))
    cells.append(code("""
def calcular_psi_numerico(base, comparacion):
    base_clean = pd.to_numeric(base, errors="coerce").dropna()
    comp_clean = pd.to_numeric(comparacion, errors="coerce").dropna()
    if base_clean.nunique() < 2 or comp_clean.empty:
        return np.nan
    cortes = np.unique(np.quantile(base_clean, np.linspace(0, 1, 11)))
    if len(cortes) < 3:
        return np.nan
    base_bins = pd.cut(base_clean, bins=cortes, include_lowest=True)
    comp_bins = pd.cut(comp_clean, bins=cortes, include_lowest=True)
    return calcular_psi_categorico(base_bins, comp_bins)
"""))
    cells.append(code("""
def calcular_drift_numerico(paquete_drift):
    base_clean = pd.to_numeric(paquete_drift["base"], errors="coerce").dropna()
    comp_clean = pd.to_numeric(paquete_drift["comparacion_serie"], errors="coerce").dropna()
    statistic, p_value = ks_2samp(base_clean, comp_clean)
    std_base = base_clean.std(ddof=0) or 1.0
    wasserstein_std = wasserstein_distance(base_clean, comp_clean) / std_base
    psi_value = calcular_psi_numerico(base_clean, comp_clean)
    metricas = crear_metricas_drift(paquete_drift, {"tipo": "numerica", "statistic": statistic, "p_value": p_value, "distancia": wasserstein_std, "psi": psi_value})
    return crear_fila_drift(metricas)
"""))
    cells.append(code("""
def calcular_drift_categorico(paquete_drift):
    base = paquete_drift["base"]
    comparacion = paquete_drift["comparacion_serie"]
    contingency = pd.crosstab(pd.Series(["base"] * len(base) + ["comparacion"] * len(comparacion)), pd.concat([base, comparacion]).astype(str))
    statistic, p_value, _, _ = chi2_contingency(contingency)
    distancia = calcular_distancia_proporciones(base, comparacion)
    psi_value = calcular_psi_categorico(base, comparacion)
    metricas = crear_metricas_drift(paquete_drift, {"tipo": "categorica", "statistic": statistic, "p_value": p_value, "distancia": distancia, "psi": psi_value})
    return crear_fila_drift(metricas)


def calcular_distancia_proporciones(base, comparacion):
    base_prop = base.astype(str).value_counts(normalize=True)
    comp_prop = comparacion.astype(str).value_counts(normalize=True)
    categorias = sorted(set(base_prop.index) | set(comp_prop.index))
    return 0.5 * sum(abs(base_prop.get(cat, 0) - comp_prop.get(cat, 0)) for cat in categorias)
"""))
    cells.append(code("""
def crear_metricas_drift(paquete_drift, medidas_drift):
    return {**paquete_drift, **medidas_drift}


def crear_fila_drift(metricas_drift):
    score = calcular_score_drift(metricas_drift)
    return {
        "dataset": metricas_drift["dataset"],
        "comparacion": metricas_drift["comparacion"],
        "variable": metricas_drift["variable"],
        "tipo": metricas_drift["tipo"],
        "statistic": float(metricas_drift["statistic"]),
        "p_value": float(metricas_drift["p_value"]),
        "distancia": float(metricas_drift["distancia"]),
        "psi": float(metricas_drift["psi"]) if not np.isnan(metricas_drift["psi"]) else np.nan,
        "drift_score": float(score),
        "drift_flag": bool(evaluar_flag_drift(metricas_drift)),
    }
"""))
    cells.append(code("""
def calcular_score_drift(metricas_drift):
    psi_value = metricas_drift["psi"] if not np.isnan(metricas_drift["psi"]) else 0
    if metricas_drift["tipo"] == "categorica":
        return np.nanmax([abs(metricas_drift["distancia"]), psi_value])
    return np.nanmax([abs(metricas_drift["statistic"]), abs(metricas_drift["distancia"]), psi_value])


def evaluar_flag_drift(metricas_drift):
    psi_value = metricas_drift["psi"] if not np.isnan(metricas_drift["psi"]) else 0
    if metricas_drift["tipo"] == "categorica":
        return psi_value >= PSI_REVIEW_THRESHOLD or abs(metricas_drift["distancia"]) >= KS_REVIEW_THRESHOLD
    return abs(metricas_drift["statistic"]) >= KS_REVIEW_THRESHOLD or abs(metricas_drift["distancia"]) >= WASSERSTEIN_REVIEW_THRESHOLD or psi_value >= PSI_REVIEW_THRESHOLD
"""))
    cells.append(code("""
def calcular_drift_dataset(nombre_dataset):
    rows = []
    train_x = splits_dataset[nombre_dataset]["train"][0]
    for comparison_name in ["validation", "test"]:
        compare_x = splits_dataset[nombre_dataset][comparison_name][0]
        paquete_comparacion = {"dataset": nombre_dataset, "comparacion": comparison_name, "train_x": train_x, "compare_x": compare_x}
        rows.extend(calcular_drift_comparacion(paquete_comparacion))
    return pd.DataFrame(rows)


def calcular_drift_comparacion(paquete_comparacion):
    rows = []
    for variable_name in paquete_comparacion["train_x"].columns:
        rows.append(calcular_drift_variable(crear_paquete_drift(paquete_comparacion, variable_name)))
    return rows
"""))
    cells.append(code("""
def crear_paquete_drift(paquete_comparacion, variable_name):
    return {
        "dataset": paquete_comparacion["dataset"],
        "comparacion": paquete_comparacion["comparacion"],
        "variable": variable_name,
        "base": paquete_comparacion["train_x"][variable_name],
        "comparacion_serie": paquete_comparacion["compare_x"][variable_name],
    }


def calcular_drift_variable(paquete_drift):
    if pd.api.types.is_numeric_dtype(paquete_drift["base"]):
        return calcular_drift_numerico(paquete_drift)
    return calcular_drift_categorico(paquete_drift)


def resumir_drift_dataset(nombre_dataset, drift_dataset):
    return {
        "dataset": nombre_dataset,
        "tests": len(drift_dataset),
        "variables_con_flag": drift_dataset.loc[drift_dataset["drift_flag"], "variable"].nunique(),
        "max_psi": drift_dataset["psi"].max(),
        "max_distancia": drift_dataset["distancia"].max(),
        "max_drift_score": drift_dataset["drift_score"].max(),
    }
"""))
    cells.append(code("""
def resumir_drift_comparaciones(nombre_dataset):
    subset = drift_variables[drift_variables["dataset"].eq(nombre_dataset)]
    resumen = (
        subset.groupby("comparacion", as_index=False)
        .agg(
            pruebas=("variable", "count"),
            variables_con_flag=("drift_flag", "sum"),
            max_drift_score=("drift_score", "max"),
            mediana_drift_score=("drift_score", "median"),
        )
    )
    resumen["comparacion"] = pd.Categorical(resumen["comparacion"], categories=["validation", "test"], ordered=True)
    return resumen.sort_values("comparacion")


def preparar_top_drift(nombre_dataset, n_variables=10):
    subset = drift_variables[drift_variables["dataset"].eq(nombre_dataset)]
    return (
        subset.groupby("variable", as_index=False)
        .agg(drift_score=("drift_score", "max"), drift_flag=("drift_flag", "max"))
        .sort_values("drift_score", ascending=False)
        .head(n_variables)
        .sort_values("drift_score")
    )


def preparar_metricas_top_drift(nombre_dataset, top_variables):
    subset = drift_variables[
        drift_variables["dataset"].eq(nombre_dataset)
        & drift_variables["variable"].isin(top_variables["variable"])
    ].copy()
    subset["ks"] = np.where(subset["tipo"].eq("numerica"), subset["statistic"].abs(), np.nan)
    subset["distancia_abs"] = subset["distancia"].abs()
    metricas = (
        subset.groupby("variable", as_index=False)
        .agg(
            ks=("ks", "max"),
            distancia=("distancia_abs", "max"),
            psi=("psi", "max"),
            drift_score=("drift_score", "max"),
            drift_flag=("drift_flag", "max"),
        )
        .fillna(0)
    )
    orden = top_variables["variable"].tolist()
    metricas["variable"] = pd.Categorical(metricas["variable"], categories=orden, ordered=True)
    return metricas.sort_values("variable")


def titulo_drift_dataset(nombre_dataset):
    resumen = drift_resumen[drift_resumen["dataset"].eq(nombre_dataset)].iloc[0]
    variables_flag = int(resumen["variables_con_flag"])
    if variables_flag == 0:
        return f"{etiqueta_dataset(nombre_dataset)}: sin drift operativo frente a train"
    return f"{etiqueta_dataset(nombre_dataset)}: {variables_flag} variables requieren revisión"


def graficar_drift_dataset(nombre_dataset):
    top_variables = preparar_top_drift(nombre_dataset)
    metricas_top = preparar_metricas_top_drift(nombre_dataset, top_variables)
    resumen_comparaciones = resumir_drift_comparaciones(nombre_dataset)
    colores_top = np.where(top_variables["drift_flag"], "#B85C5C", "#2F6F9F")
    figura, ejes = plt.subplots(1, 3, figsize=(15.0, 5.4), gridspec_kw={"width_ratios": [1.15, 1.45, 0.85]})
    ejes[0].barh(top_variables["variable"], top_variables["drift_score"], color=colores_top)
    ejes[0].axvline(PSI_REVIEW_THRESHOLD, color="#6F6A60", linestyle="--", linewidth=1.1)
    ejes[0].text(PSI_REVIEW_THRESHOLD, 0.02, "PSI/KS 0,10", transform=ejes[0].get_xaxis_transform(), ha="left", va="bottom", fontsize=8, color="#6F6A60")
    ejes[0].set_xlabel("Máximo score observado")
    ejes[0].set_title("Variables que más cambian", loc="left", fontweight="bold")

    posiciones = np.arange(len(metricas_top))
    offsets = [-0.24, 0.0, 0.24]
    for offset, (columna, etiqueta, color) in zip(offsets, [
        ("ks", "KS", "#2F6F9F"),
        ("distancia", "Distancia", "#D9822B"),
        ("psi", "PSI", "#7A6FA5"),
    ]):
        valores = metricas_top[columna].to_numpy()
        ejes[1].barh(posiciones + offset, valores, height=0.21, color=color, alpha=0.82, label=etiqueta)
    ejes[1].axvline(PSI_REVIEW_THRESHOLD, color="#6F6A60", linestyle="--", linewidth=1.0)
    ejes[1].axvline(WASSERSTEIN_REVIEW_THRESHOLD, color="#6F6A60", linestyle=":", linewidth=1.0)
    ejes[1].set_yticks(posiciones)
    ejes[1].set_yticklabels(metricas_top["variable"].astype(str))
    ejes[1].set_xlabel("Valor máximo por métrica")
    ejes[1].set_title("Métrica que dispara la revisión", loc="left", fontweight="bold")
    ejes[1].legend(frameon=False, fontsize=8)
    n_flags_top = int(metricas_top["drift_flag"].sum())
    ejes[1].text(
        0.98,
        0.04,
        f"{n_flags_top} variables top en revisión\\numbrales: KS/PSI=0,10; W=0,20",
        transform=ejes[1].transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        bbox={"facecolor": "#FAF7F2", "edgecolor": "#D8D0C4", "boxstyle": "round,pad=0.30"},
    )

    ejes[2].bar(resumen_comparaciones["comparacion"], resumen_comparaciones["variables_con_flag"], color="#D9822B", width=0.58)
    limite_y = max(1, resumen_comparaciones["variables_con_flag"].max() * 1.22)
    for _, row in resumen_comparaciones.iterrows():
        label_y = row["variables_con_flag"] + limite_y * 0.03
        ejes[2].text(row["comparacion"], label_y, f"max={row['max_drift_score']:.2f}", ha="center", va="bottom", fontsize=9)
    ejes[2].set_ylim(0, limite_y)
    ejes[2].set_ylabel("Variables con señal")
    ejes[2].set_title("Dónde se concentra", loc="left", fontweight="bold")
    for eje in ejes:
        aplicar_estilo_eje(eje, eje_rejilla="x" if eje is not ejes[2] else "y")
    figura.suptitle(titulo_drift_dataset(nombre_dataset), fontsize=13, y=1.03)
    figura.tight_layout()
    guardar_figura(figura, f"fase4_drift_{nombre_dataset}.png")
    plt.show()
"""))
    cells.append(code("""
drift_por_dataset = {nombre_dataset: calcular_drift_dataset(nombre_dataset) for nombre_dataset in DATASET_ORDER}
drift_variables = pd.concat(drift_por_dataset.values(), ignore_index=True)
drift_resumen = pd.DataFrame([resumir_drift_dataset(nombre_dataset, drift_por_dataset[nombre_dataset]) for nombre_dataset in DATASET_ORDER])

guardar_tabla(drift_variables, "fase4_drift_variables.csv")
guardar_tabla(drift_resumen, "fase4_drift_resumen.csv")
mostrar_tabla(drift_resumen, "Resumen de drift univariante", n=10)
mostrar_tabla(drift_variables.sort_values("drift_score", ascending=False), "Variables con mayor drift", n=20)
"""))
    cells.append(md("""
El resumen global de drift separa un caso estable y cuatro casos con revisión. `customer_churn` no activa señales de revisión y su máximo score es 0,0131; en cambio, `breast_cancer_wisconsin` marca 25 variables, `madelon` 41, `olive_oil_3class` 7 y `olive_oil_9class` 6. El umbral operativo de PSI es 0,10, KS 0,10 y Wasserstein estandarizado 0,20; por eso las figuras siguientes anotan el umbral y muestran qué métrica explica cada alerta antes de interpretar cada dataset.
"""))

    drift_observations = {
        "breast_cancer_wisconsin": "Aparecen 25 variables con señal de revisión y el máximo PSI llega a 0,500. No invalida el split: el AUC adversarial medio es 0,522, pero la selección posterior debe leer estas variables como sensibilidad del particionado.",
        "customer_churn": "No aparece ninguna variable con señal de revisión: máximo PSI 0,0003 y máxima distancia 0,013. Es el split más estable de la fase y pasa a selección sin cautelas distributivas relevantes.",
        "madelon": "Hay 41 variables con señal de revisión entre 500 y un máximo drift_score de 0,235. En proporción es una alerta acotada, coherente con alta dimensionalidad, y debe cruzarse con estabilidad de selección posterior.",
        "olive_oil_3class": "Siete de ocho variables muestran señal de revisión, con PSI máximo 0,339 y distancia máxima 0,210. La señal obliga a intervalos prudentes en Fase 6, no a rehacer el split.",
        "olive_oil_9class": "Seis de ocho variables muestran señal de revisión, con PSI máximo 0,329 y distancia máxima 0,163. El test de 86 filas y las 9 clases hacen necesaria una lectura por clase en modelado.",
    }
    add_dataset_cells(
        cells,
        "Drift Univariante",
        """
drift___DATASET__ = drift_variables[drift_variables["dataset"].eq("__DATASET__")]
drift_resumen___DATASET__ = drift_resumen[drift_resumen["dataset"].eq("__DATASET__")]
drift_comparaciones___DATASET__ = resumir_drift_comparaciones("__DATASET__")

mostrar_tabla(drift_resumen___DATASET__, "Resumen drift - __LABEL__", n=5)
mostrar_tabla(drift_comparaciones___DATASET__, "Drift por comparación - __LABEL__", n=5)
mostrar_tabla(drift___DATASET__.sort_values("drift_score", ascending=False), "Top drift - __LABEL__", n=15)
graficar_drift_dataset("__DATASET__")
""",
        drift_observations,
    )

    cells.append(md("""
## 4.7 Representatividad Multivariante con PCA Exploratorio

PCA se usa como diagnóstico visual de mezcla entre splits. No se aplica como transformación para las fases posteriores. Cada figura combina PC1-PC2 con la varianza explicada de los primeros componentes para no sobreinterpretar una proyección con poca varianza.
"""))
    cells.append(code("""
def crear_onehot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def columnas_por_tipo(datos_x):
    numericas = [name for name in datos_x.columns if pd.api.types.is_numeric_dtype(datos_x[name])]
    categoricas = [name for name in datos_x.columns if name not in numericas]
    return numericas, categoricas
"""))
    cells.append(code("""
def crear_preprocesador_modelado(datos_x):
    numericas, categoricas = columnas_por_tipo(datos_x)
    transformers = []
    if numericas:
        transformers.append(("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numericas))
    if categoricas:
        transformers.append(("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", crear_onehot_encoder())]), categoricas))
    return ColumnTransformer(transformers)


def matriz_preprocesada(datos_x):
    preprocessor = crear_preprocesador_modelado(datos_x)
    matriz = preprocessor.fit_transform(datos_x)
    return matriz.toarray() if hasattr(matriz, "toarray") else np.asarray(matriz)
"""))
    cells.append(code("""
def datos_pca_dataset(nombre_dataset):
    combined_x = unir_x_splits(nombre_dataset)
    sampled_x = muestrear_filas(combined_x, MAX_SAMPLE_PCA)
    matriz = matriz_preprocesada(sampled_x.drop(columns=["split"], errors="ignore"))
    pca = PCA(n_components=min(MAX_PCA_COMPONENTS, matriz.shape[1]), random_state=RANDOM_STATE)
    coords = pca.fit_transform(matriz)
    resultado_pca = {"dataset": nombre_dataset, "sampled_x": sampled_x, "coords": coords, "pca": pca}
    return crear_tablas_pca(resultado_pca)


def unir_x_splits(nombre_dataset):
    frames = []
    for split_name, (x_split, _) in splits_dataset[nombre_dataset].items():
        frames.append(x_split.assign(split=split_name))
    return pd.concat(frames, ignore_index=False)
"""))
    cells.append(code("""
def muestrear_filas(datos_x, max_rows):
    if len(datos_x) <= max_rows:
        return datos_x.copy()
    muestras = []
    for split_name, parte_split in datos_x.groupby("split", sort=False):
        n_muestra = min(len(parte_split), max_rows // 3)
        muestra = parte_split.sample(n_muestra, random_state=RANDOM_STATE).copy()
        muestra["split"] = split_name
        muestras.append(muestra)
    return pd.concat(muestras, ignore_index=False)


def crear_tablas_pca(resultado_pca):
    coordenadas = pd.DataFrame({
        "dataset": resultado_pca["dataset"],
        "split": resultado_pca["sampled_x"]["split"].to_numpy(),
        "pc1": resultado_pca["coords"][:, 0],
        "pc2": resultado_pca["coords"][:, 1],
    })
    varianza = pd.DataFrame(crear_filas_varianza_pca(resultado_pca["dataset"], resultado_pca["pca"]))
    return coordenadas, varianza
"""))
    cells.append(code("""
def crear_filas_varianza_pca(nombre_dataset, pca):
    cumulative = np.cumsum(pca.explained_variance_ratio_)
    return [
        {
            "dataset": nombre_dataset,
            "component": component_index + 1,
            "explained_variance_ratio": float(value),
            "cumulative_explained_variance": float(cumulative[component_index]),
        }
        for component_index, value in enumerate(pca.explained_variance_ratio_)
    ]
"""))
    cells.append(code("""
def graficar_pca_dataset(nombre_dataset):
    coords = pca_coordenadas[pca_coordenadas["dataset"].eq(nombre_dataset)]
    variance = pca_varianza[pca_varianza["dataset"].eq(nombre_dataset)]
    figura, ejes = plt.subplots(1, 2, figsize=(11.2, 4.8), gridspec_kw={"width_ratios": [1.35, 1]})
    for split_name in SPLIT_ORDER:
        subset = coords[coords["split"].eq(split_name)]
        ejes[0].scatter(subset["pc1"], subset["pc2"], s=14, alpha=0.42, color=SPLIT_COLORS[split_name], label=split_name.title())
        ejes[0].scatter(subset["pc1"].mean(), subset["pc2"].mean(), s=90, color=SPLIT_COLORS[split_name], edgecolor="#2D2A26", linewidth=0.8)
    ejes[1].bar(variance["component"], variance["explained_variance_ratio"], color="#2F6F9F")
    cumulative_pc2 = variance.loc[variance["component"].le(2), "explained_variance_ratio"].sum()
    ejes[0].text(
        0.02,
        0.03,
        f"PC1+PC2 explican {cumulative_pc2:.1%}\\ncentros marcados con borde",
        transform=ejes[0].transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        bbox={"facecolor": "#FAF7F2", "edgecolor": "#D8D0C4", "boxstyle": "round,pad=0.35"},
    )
    ejes[1].axhline(0.10, color="#6F6A60", linestyle="--", linewidth=1.0)
    ejes[1].text(variance["component"].max(), 0.105, "10% por componente", ha="right", va="bottom", fontsize=8, color="#6F6A60")
    formatear_figura_pca(ejes, nombre_dataset)
    guardar_figura(figura, f"fase4_pca_{nombre_dataset}.png")
    plt.show()
"""))
    cells.append(code("""
def formatear_figura_pca(ejes, nombre_dataset):
    ejes[0].set_title("PC1-PC2 por split", loc="left", fontweight="bold")
    ejes[0].set_xlabel("PC1")
    ejes[0].set_ylabel("PC2")
    ejes[0].legend(frameon=False)
    ejes[1].set_title("Varianza explicada", loc="left", fontweight="bold")
    ejes[1].set_xlabel("Componente")
    ejes[1].set_ylabel("Ratio")
    for eje in ejes:
        aplicar_estilo_eje(eje, eje_rejilla="both")
    ejes[0].figure.suptitle(f"{etiqueta_dataset(nombre_dataset)}: PCA comprueba mezcla entre splits", fontsize=13, y=1.04)
"""))
    cells.append(code("""
pca_resultados = {nombre_dataset: datos_pca_dataset(nombre_dataset) for nombre_dataset in DATASET_ORDER}
pca_coordenadas = pd.concat([pca_resultados[nombre_dataset][0] for nombre_dataset in DATASET_ORDER], ignore_index=True)
pca_varianza = pd.concat([pca_resultados[nombre_dataset][1] for nombre_dataset in DATASET_ORDER], ignore_index=True)

guardar_tabla(pca_coordenadas, "fase4_pca_coordenadas.csv")
guardar_tabla(pca_varianza, "fase4_pca_varianza.csv")
mostrar_tabla(pca_varianza, "Varianza explicada por PCA", n=25)
"""))
    cells.append(md("""
La PCA global muestra cuánto puede leerse de la proyección PC1-PC2: `olive_oil` acumula 68,6% en dos componentes, `breast_cancer_wisconsin` 63,2%, `customer_churn` 28,7% y `madelon` solo 2,3%. Por tanto, una buena mezcla visual en `madelon` no puede tomarse como prueba fuerte de representatividad multivariante, mientras que en `olive_oil` y `breast_cancer_wisconsin` la proyección resume una parte sustancial de la variabilidad.
"""))

    pca_observations = {
        "breast_cancer_wisconsin": "PC1 explica 44,3% y PC2 añade 19,0%, con 63,2% acumulado. La mezcla visual se puede leer con más confianza que en `madelon`, aunque no resume el 100% del espacio.",
        "customer_churn": "La PCA usa una muestra visual de 6.000 filas frente a 440.832 totales. PC1-PC2 acumulan 28,7%, suficiente para detectar separaciones gruesas pero no para descartar cambios sutiles.",
        "madelon": "PC1-PC2 acumulan solo 2,3% de la varianza. Aunque los splits parezcan mezclados, la proyección pierde casi todo el espacio de 500 variables.",
        "olive_oil_3class": "PC1-PC2 acumulan 68,6% de la varianza tras excluir proxies. La figura permite revisar si train, validation o test quedan separados por composición química.",
        "olive_oil_9class": "La varianza PC1-PC2 también acumula 68,6%, porque usa las mismas 8 variables químicas. La proyección diagnostica representatividad, no separabilidad garantizada de 9 clases.",
    }
    add_dataset_cells(
        cells,
        "PCA Exploratorio",
        """
pca_varianza___DATASET__ = pca_varianza[pca_varianza["dataset"].eq("__DATASET__")]
pca_coordenadas___DATASET__ = pca_coordenadas[pca_coordenadas["dataset"].eq("__DATASET__")]

mostrar_tabla(pca_varianza___DATASET__, "Varianza PCA - __LABEL__", n=10)
mostrar_tabla(pca_coordenadas___DATASET__.groupby("split", as_index=False).agg(n=("pc1", "count"), pc1_media=("pc1", "mean"), pc2_media=("pc2", "mean")), "Resumen coordenadas PCA - __LABEL__", n=10)
graficar_pca_dataset("__DATASET__")
""",
        pca_observations,
    )

    cells.append(md("""
## 4.8 Auditoría de Leakage y Proxies Después del Split

Se comprueba que el target no esté en `X`, se buscan nombres sospechosos y se calcula asociación univariante extrema. En variables binarias se usa AUC absoluto; en todos los targets se usa NMI como señal de dependencia casi perfecta.
"""))
    cells.append(code("""
def discretizar_para_nmi(serie_variable):
    if not pd.api.types.is_numeric_dtype(serie_variable):
        return serie_variable.astype(str)
    try:
        return pd.qcut(serie_variable.rank(method="first"), q=min(10, serie_variable.nunique()), duplicates="drop").astype(str)
    except ValueError:
        return serie_variable.astype(str)


def calcular_nmi_variable(serie_variable, serie_target):
    variable_discreta = discretizar_para_nmi(serie_variable)
    return normalized_mutual_info_score(serie_target.astype(str), variable_discreta.astype(str))


def obtener_muestra_leakage(nombre_dataset):
    x_dataset, y_dataset = datasets_xy[nombre_dataset]
    if len(y_dataset) <= MAX_SAMPLE_LEAKAGE:
        return x_dataset, y_dataset
    sampled_index = y_dataset.sample(MAX_SAMPLE_LEAKAGE, random_state=RANDOM_STATE).index
    return x_dataset.loc[sampled_index], y_dataset.loc[sampled_index]
"""))
    cells.append(code("""
def evaluar_leakage_variable(nombre_dataset, variable_name):
    x_dataset, y_dataset = muestras_leakage[nombre_dataset]
    serie_variable = x_dataset[variable_name]
    return {
        "dataset": nombre_dataset,
        "variable": variable_name,
        "nombre_sospechoso": detectar_nombre_sospechoso(nombre_dataset, variable_name),
        "auc_abs_binaria": calcular_auc_binaria(serie_variable, y_dataset),
        "nmi_con_target": calcular_nmi_variable(serie_variable, y_dataset),
        "unique_ratio": serie_variable.nunique(dropna=False) / len(serie_variable),
    }


def detectar_nombre_sospechoso(nombre_dataset, variable_name):
    tokens = [TARGET_BY_DATASET[nombre_dataset], "target", "label", "class", "clase"]
    return any(token.lower() in variable_name.lower() for token in tokens)
"""))
    cells.append(code("""
def resumir_leakage_dataset(nombre_dataset):
    screening = leakage_screening[leakage_screening["dataset"].eq(nombre_dataset)]
    x_dataset = datasets_xy[nombre_dataset][0]
    return {
        "dataset": nombre_dataset,
        "target_en_X": TARGET_BY_DATASET[nombre_dataset] in x_dataset.columns,
        "n_muestras_usadas": len(muestras_leakage[nombre_dataset][1]),
        "nombres_sospechosos": int(screening["nombre_sospechoso"].sum()),
        "auc_abs_ge_099": int((screening["auc_abs_binaria"] >= AUC_LEAKAGE_REVIEW_THRESHOLD).sum()),
        "nmi_ge_099": int((screening["nmi_con_target"] >= NMI_LEAKAGE_REVIEW_THRESHOLD).sum()),
        "categoricas_en_X": int(resumen_xy.loc[resumen_xy["dataset"].eq(nombre_dataset), "categoricas_en_X"].iloc[0]),
    }
"""))
    cells.append(code("""
muestras_leakage = {nombre_dataset: obtener_muestra_leakage(nombre_dataset) for nombre_dataset in DATASET_ORDER}

leakage_screening = pd.DataFrame([
    evaluar_leakage_variable(nombre_dataset, variable_name)
    for nombre_dataset in DATASET_ORDER
    for variable_name in datasets_xy[nombre_dataset][0].columns
])

leakage_resumen = pd.DataFrame([resumir_leakage_dataset(nombre_dataset) for nombre_dataset in DATASET_ORDER])

guardar_tabla(leakage_screening, "fase4_leakage_screening.csv")
guardar_tabla(leakage_resumen, "fase4_leakage_resumen.csv")
mostrar_tabla(leakage_resumen, "Resumen leakage/proxy", n=10)
mostrar_tabla(leakage_screening.sort_values("nmi_con_target", ascending=False), "Variables con mayor NMI con target", n=20)
"""))
    cells.append(md("""
La pantalla global de leakage no detecta proxies extremos en las variables que permanecen en `X`: los 5 datasets tienen `target_en_X=False`, 0 nombres sospechosos y 0 variables con NMI >= 0,99. La cautela relevante queda documentada fuera de `X`, porque `palmitic` alcanza NMI 1,000 con `target` en `olive_oil_9class` y por eso fue excluida antes del split.
"""))

    leakage_observations = {
        "breast_cancer_wisconsin": "El resumen marca `target_en_X=False`, 0 nombres sospechosos, 0 variables con AUC >= 0,99 y 0 con NMI >= 0,99. Las asociaciones predictivas no se interpretan como leakage si no codifican el target por diseño.",
        "customer_churn": "El screening usa 12.000 muestras y mantiene 3 categóricas en `X`; aun así, hay 0 nombres sospechosos y 0 variables con NMI >= 0,99. La codificación queda para el modelado posterior.",
        "madelon": "La revisión cubre 2.000 muestras y 500 variables, con 0 nombres sospechosos y 0 proxies extremos. La selección real se aplaza a la etapa posterior.",
        "olive_oil_3class": "`palmitic` no aparece en `X`; el resumen deja 0 variables con NMI >= 0,99 entre las 8 predictoras. La métrica excluida explica por qué no debe entrar en la formulación.",
        "olive_oil_9class": "La exclusión de `area` y `palmitic` deja 8 predictoras y 0 proxies NMI >= 0,99. La tabla de excluidas conserva la evidencia del proxy perfecto sin contaminar `X`.",
    }
    add_dataset_cells(
        cells,
        "Leakage y Proxies",
        """
leakage___DATASET__ = leakage_screening[leakage_screening["dataset"].eq("__DATASET__")]
leakage_resumen___DATASET__ = leakage_resumen[leakage_resumen["dataset"].eq("__DATASET__")]

mostrar_tabla(leakage_resumen___DATASET__, "Resumen leakage - __LABEL__", n=5)
mostrar_tabla(leakage___DATASET__.sort_values("nmi_con_target", ascending=False), "Screening leakage - __LABEL__", n=15)
""",
        leakage_observations,
    )

    cells.append(md("""
## 4.9 Validación Adversarial Train vs Test

La validación adversarial intenta distinguir filas de `train` frente a filas de `test`. Un AUC cercano a 0.5 sugiere particiones difíciles de distinguir; valores altos indican posible cambio de distribución que debe leerse junto con drift y PCA.
"""))
    cells.append(code("""
def preparar_adversarial_dataset(nombre_dataset):
    train_x = splits_dataset[nombre_dataset]["train"][0].assign(origen_split=0)
    test_x = splits_dataset[nombre_dataset]["test"][0].assign(origen_split=1)
    combined = pd.concat([train_x, test_x], ignore_index=True)
    sampled = muestrear_adversarial(combined)
    y_adv = sampled.pop("origen_split")
    return sampled, y_adv


def muestrear_adversarial(datos_adversarial):
    if len(datos_adversarial) <= MAX_SAMPLE_ADVERSARIAL:
        return datos_adversarial.copy()
    muestras = []
    for origen_split, parte_origen in datos_adversarial.groupby("origen_split", sort=False):
        muestra = parte_origen.sample(MAX_SAMPLE_ADVERSARIAL // 2, random_state=RANDOM_STATE).copy()
        muestra["origen_split"] = origen_split
        muestras.append(muestra)
    return pd.concat(muestras, ignore_index=True)
"""))
    cells.append(code("""
def crear_pipeline_adversarial(datos_x):
    preprocessor = crear_preprocesador_modelado(datos_x)
    model = LogisticRegression(max_iter=600, solver="liblinear", random_state=RANDOM_STATE)
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def evaluar_adversarial_dataset(nombre_dataset):
    x_adv, y_adv = preparar_adversarial_dataset(nombre_dataset)
    pipeline = crear_pipeline_adversarial(x_adv)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_val_score(pipeline, x_adv, y_adv, cv=cv, scoring="roc_auc")
    metricas = {"dataset": nombre_dataset, "scores": scores, "filas": len(x_adv), "features": x_adv.shape[1]}
    return crear_resultado_adversarial(metricas)
"""))
    cells.append(code("""
def crear_resultado_adversarial(metricas_adversarial):
    scores = metricas_adversarial["scores"]
    return {
        "dataset": metricas_adversarial["dataset"],
        "auc_cv": float(np.mean(scores)),
        "auc_fold_std": float(np.std(scores, ddof=1)),
        "auc_min": float(np.min(scores)),
        "auc_max": float(np.max(scores)),
        "n_muestras_usadas": metricas_adversarial["filas"],
        "features_usadas": metricas_adversarial["features"],
    }


def crear_filas_folds_adversarial(nombre_dataset, scores):
    return [{"dataset": nombre_dataset, "fold": fold + 1, "auc": score} for fold, score in enumerate(scores)]
"""))
    cells.append(code("""
def evaluar_folds_adversarial_dataset(nombre_dataset):
    x_adv, y_adv = preparar_adversarial_dataset(nombre_dataset)
    pipeline = crear_pipeline_adversarial(x_adv)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_val_score(pipeline, x_adv, y_adv, cv=cv, scoring="roc_auc")
    return crear_filas_folds_adversarial(nombre_dataset, scores)
"""))
    cells.append(code("""
adversarial_resultados = pd.DataFrame([evaluar_adversarial_dataset(nombre_dataset) for nombre_dataset in DATASET_ORDER])
adversarial_folds = pd.DataFrame([row for nombre_dataset in DATASET_ORDER for row in evaluar_folds_adversarial_dataset(nombre_dataset)])

guardar_tabla(adversarial_resultados, "fase4_validacion_adversarial.csv")
guardar_tabla(adversarial_folds, "fase4_validacion_adversarial_folds.csv")
mostrar_tabla(adversarial_resultados, "Validación adversarial train vs test", n=10)
mostrar_tabla(adversarial_folds, "AUC por fold", n=25)
"""))
    cells.append(md("""
La validación adversarial queda cerca de la banda de azar en los 5 datasets: los AUC medios van de 0,500 en `madelon` a 0,535 en `olive_oil_9class`. Esa lectura refuerza que las diferencias entre train y test no forman una separación fácil para un clasificador auxiliar.
"""))
    cells.append(code("""
figura, eje = plt.subplots(figsize=(8.8, 4.8))
ordered_adv = adversarial_resultados.sort_values("auc_cv")
eje.axvspan(0.45, 0.55, color="#5E8C61", alpha=0.12, label="Banda azar 0,45-0,55")
eje.errorbar(ordered_adv["auc_cv"], [etiqueta_dataset(name) for name in ordered_adv["dataset"]], xerr=ordered_adv["auc_fold_std"], fmt="o", color="#2F6F9F", ecolor="#B8B0A3", capsize=4)
eje.axvline(0.5, color="#5E8C61", linestyle="--", linewidth=1.2, label="AUC 0,50")
eje.set_xlim(0.40, max(0.75, ordered_adv["auc_cv"].max() + 0.05))
eje.set_xlabel("AUC adversarial")
eje.set_title("Train y test permanecen cerca del azar adversarial", loc="left", fontweight="bold")
eje.text(
    0.545,
    -0.45,
    "azar práctico",
    ha="right",
    va="center",
    fontsize=9,
    color="#5E8C61",
)
eje.legend(frameon=False)
aplicar_estilo_eje(eje, eje_rejilla="x")
guardar_figura(figura, "fase4_validacion_adversarial_auc.png")
plt.show()
"""))
    cells.append(md("""
La validación adversarial queda dentro de una banda compatible con azar práctico: los AUC medios van de 0,476 en `madelon` a 0,535 en `olive_oil_9class`, con línea de referencia en 0,500 y desviaciones por fold entre 0,0126 y 0,0778. Ningún dataset se acerca a un AUC alto de separación train-test; el siguiente desglose confirma si esa media oculta folds extremos o tamaños de muestra insuficientes.
"""))

    adversarial_observations = {
        "breast_cancer_wisconsin": "El AUC adversarial medio es 0,522 con desviación 0,0778 en 484 muestras. La variabilidad por fold es visible, pero la media permanece dentro de la banda de azar práctico.",
        "customer_churn": "El AUC adversarial medio es 0,516 con desviación 0,0126 usando 12.000 muestras balanceadas por origen. El tamaño grande no revela separación train-test relevante.",
        "madelon": "El AUC adversarial medio es 0,476 con desviación 0,0536 en 1.700 muestras. La alta dimensionalidad no produce una separación sistemática de train y test.",
        "olive_oil_3class": "El AUC adversarial medio es 0,513 con desviación 0,0588 en 486 muestras. El tamaño reducido explica que los folds oscilen más que en `customer_churn`.",
        "olive_oil_9class": "El AUC adversarial medio es 0,535 con desviación 0,0592 en 486 muestras. La validación no mide rendimiento de clasificación; solo pregunta si train y test se distinguen.",
    }
    add_dataset_cells(
        cells,
        "Validación Adversarial",
        """
adversarial___DATASET__ = adversarial_resultados[adversarial_resultados["dataset"].eq("__DATASET__")]
adversarial_folds___DATASET__ = adversarial_folds[adversarial_folds["dataset"].eq("__DATASET__")]

mostrar_tabla(adversarial___DATASET__, "Resultado adversarial - __LABEL__", n=5)
mostrar_tabla(adversarial_folds___DATASET__, "Folds adversariales - __LABEL__", n=10)
""",
        adversarial_observations,
    )

    cells.append(md("""
## 4.10 Síntesis de la Auditoría de Particiones

Se reúne una tabla final con métricas observadas para cada dataset operativo y se aplica un criterio de lectura común: estabilidad del target, número de variables con drift, AUC adversarial frente a la banda de azar y proxies NMI >= 0,99. La síntesis no recalcula resultados; condensa las auditorías anteriores para dejar explícitas las garantías y cautelas que acompañan a la selección de características posterior.
"""))
    cells.append(code("""
target_delta_resumen = diferencias_target.groupby("dataset", as_index=False).agg(max_delta_target=("max_delta_proporcion", "max"))
overlap_resumen = solapes_split.groupby("dataset", as_index=False).agg(index_overlap_total=("index_overlap", "sum"), row_hash_overlap_total=("row_hash_overlap", "sum"))
size_wide = tamanos_split.pivot(index="dataset", columns="split", values="filas").reset_index()
size_wide = size_wide.rename(columns={"train": "filas_train", "validation": "filas_validation", "test": "filas_test"})
leakage_metricas = leakage_resumen.drop(columns=["target_en_X", "categoricas_en_X"])

resumen_fase5 = (
    resumen_xy.merge(size_wide, on="dataset", how="left")
    .merge(target_delta_resumen, on="dataset", how="left")
    .merge(drift_resumen[["dataset", "variables_con_flag", "max_psi", "max_distancia"]], on="dataset", how="left")
    .merge(leakage_metricas, on="dataset", how="left")
    .merge(adversarial_resultados[["dataset", "auc_cv", "auc_fold_std"]], on="dataset", how="left")
    .merge(overlap_resumen, on="dataset", how="left")
)

guardar_tabla(resumen_fase5, "fase4_resumen_para_fase5.csv")
mostrar_tabla(resumen_fase5, "Síntesis métrica de la auditoría", n=10)
"""))
    cells.append(md("""
La síntesis confirma una base común para la selección posterior: los 5 datasets tienen solape total de índice igual a 0, `nmi_ge_099=0` en las variables de `X` y AUC adversarial compatible con particiones no separables de forma trivial. La única cautela persistente es distributiva, concentrada en 25 variables de `breast_cancer_wisconsin` y 41 de `madelon`.
"""))
    cells.append(code("""
figura, ejes = plt.subplots(2, 2, figsize=(12.0, 8.0))
ejes = ejes.ravel()
labels = resumen_fase5["dataset"].map(etiqueta_dataset)

ejes[0].barh(labels, resumen_fase5["max_delta_target"], color="#2F6F9F")
ejes[0].set_title("El target queda estable")
ejes[0].set_xlabel("Delta máximo de proporción")

ejes[1].barh(labels, resumen_fase5["variables_con_flag"], color="#D9822B")
ejes[1].set_title("El drift concentra las cautelas")
ejes[1].set_xlabel("Variables en revisión")

ejes[2].barh(labels, resumen_fase5["auc_cv"], color="#5E8C61")
ejes[2].axvspan(0.45, 0.55, color="#5E8C61", alpha=0.12)
ejes[2].axvline(0.5, color="#6F6A60", linestyle="--", linewidth=1)
ejes[2].set_title("Train-test se acerca al azar")
ejes[2].set_xlabel("AUC adversarial")

ejes[3].barh(labels, resumen_fase5["nmi_ge_099"], color="#B85C5C")
ejes[3].set_title("No quedan proxies NMI >= 0,99")
ejes[3].set_xlabel("Variables en X")
ejes[3].set_xlim(0, max(1, resumen_fase5["nmi_ge_099"].max() + 1))

for eje in ejes:
    aplicar_estilo_eje(eje, eje_rejilla="x")

figura.suptitle("Particiones sin solapes ni proxies extremos", fontsize=14, y=1.02)
figura.tight_layout()
guardar_figura(figura, "fase4_resumen_metricas_split.png")
plt.show()
"""))
    cells.append(md("""
El panel comparativo resume la condición final de las particiones: todos los datasets tienen solape total de índices igual a 0 y `nmi_ge_099=0` en las variables que permanecen en `X`. La mayor cautela no procede de leakage, sino de drift: 25 variables marcadas en `breast_cancer_wisconsin`, 41 en `madelon`, 7 en `olive_oil_3class` y 6 en `olive_oil_9class`; `customer_churn` combina 0 señales de revisión, delta de target casi nulo y AUC adversarial 0,516.
"""))
    cells.append(md("""
## 4.11 Conclusiones de la Auditoría

La Fase 4 deja creados y auditados los splits de cinco datasets operativos. Los puntos que deben permanecer visibles al pasar a selección de características son:

- `customer_churn` conserva variables categóricas en `X`; su codificación debe ajustarse dentro del entrenamiento posterior.
- `madelon` mantiene una dimensionalidad alta, por lo que la selección de características debe evaluar estabilidad y no solo ranking.
- `olive_oil_3class` y `olive_oil_9class` son formulaciones distintas; no deben mezclarse de nuevo como un único dataset.
- `palmitic` queda fuera de las formulaciones de `olive_oil` porque presenta asociación casi perfecta con `target`.
- Las métricas de drift, PCA y validación adversarial son diagnósticos de representatividad del split; no sustituyen la evaluación de modelos posterior.
"""))
    cells.append(code("""
summary_lines = [
    "# Resultados de la Fase 4 - Creación y Auditoría de Splits",
    "",
    "La Fase 4 crea particiones train/validation/test y audita su estabilidad antes de selección de características.",
    "",
    "## Datasets operativos",
]

for nombre_dataset in DATASET_ORDER:
    summary_lines.append(f"- `{nombre_dataset}`")

summary_lines.extend([
    "",
    "## Conclusión",
    "Las particiones quedan fijadas con solapes nulos, targets conservados y sin proxies extremos dentro de X.",
])

summary_path = PHASE4_REPORTS_DIR / "fase4_resumen_para_memoria.md"
summary_path.write_text("\\n".join(summary_lines), encoding="utf-8")
"""))
    cells.append(md("""
La síntesis escrita conserva la conclusión académica de la fase: las particiones quedan fijadas con solapes nulos, targets conservados y sin proxies extremos dentro de `X`. Con ello queda garantizada una base común para comparar la selección clásica y la selección cuántica sin confundir el efecto del método con diferencias de particionado.
"""))

    notebook["cells"] = cells
    return notebook


if __name__ == "__main__":
    notebook = build_notebook()
    nbf.write(notebook, NOTEBOOK_PATH)
    print(f"Notebook rebuilt: {NOTEBOOK_PATH.relative_to(ROOT)}")
