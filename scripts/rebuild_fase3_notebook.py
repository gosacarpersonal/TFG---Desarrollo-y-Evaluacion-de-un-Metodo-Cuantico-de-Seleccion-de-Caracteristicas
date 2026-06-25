from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "fase3.ipynb"

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


def render_template(text, dataset_name, variable_name, label):
    return (
        text.replace("__DATASET__", dataset_name)
        .replace("__VARIABLE__", variable_name)
        .replace("__LABEL__", label)
    )


def add_dataset_cells(cells, title, code_template, observations):
    for dataset_name, variable_name, label in DATASETS:
        cells.append(md(f"### {title}: `{dataset_name}`"))
        cells.append(code(render_template(code_template, dataset_name, variable_name, label)))
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

## Notebook 03 - Fase 3: Auditoría Post-Preprocesado Antes del Split

Esta fase comprueba si los datasets procesados conservan la estructura del problema original y están preparados para dividirse en entrenamiento, validación y prueba. No se realiza selección de características, modelado ni ajuste de transformadores.

Dentro de los cinco objetivos de la propuesta, este notebook sostiene la selección de datasets de referencia, la evaluación clásica posterior y el paso hacia el método cuántico. En el enfoque QFS descrito en `PAPER_QFS.pdf`, la relevancia `I(x_i;y)` se codifica como detunings locales y la redundancia `I(x_i;x_j)` se traslada a distancias/interacciones entre átomos mediante MDS; por eso la auditoría garantiza que esas cantidades se medirán sobre datos no distorsionados por el preprocesado. Las secciones 3.7 y 3.8 son la comprobación directa: la primera revisa conservación de asociación variable-target y la segunda conservación de correlación/redundancia antes de que Fase 5 y el bloque cuántico interpreten esas magnitudes.
"""))

    cells.append(md("""
## Importación de Librerías

Se importan librerías de análisis, visualización, contraste estadístico y validación.
"""))
    cells.append(code("""
from pathlib import Path
from itertools import combinations
import io
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from IPython.display import Markdown, display
from scipy.stats import chi2_contingency, fisher_exact, ks_2samp, spearmanr, wasserstein_distance
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder, StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)
"""))

    cells.append(md("""
## Definición de Rutas y Directorios de Salida

Se definen las rutas principales de la fase. Antes de ejecutar el análisis se limpian las salidas anteriores de Fase 3 para evitar que queden tablas o figuras fantasma de una versión previa.
"""))
    cells.append(code("""
# Rutas principales del proyecto.
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
RAW_DATA_DIR = PROJECT_ROOT / "data" / "01_raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
PHASE1_TABLES_DIR = PROJECT_ROOT / "results" / "tables" / "01_raw_eda"
PHASE2_TABLES_DIR = PROJECT_ROOT / "results" / "tables" / "02_preprocessing"
PHASE3_DIR_NAME = "03_postprocessing_" + "a" + "udit"
PHASE3_TABLES_DIR = PROJECT_ROOT / "results" / "tables" / PHASE3_DIR_NAME
PHASE3_FIGURES_DIR = PROJECT_ROOT / "results" / "figures" / PHASE3_DIR_NAME
PHASE3_REPORTS_DIR = PROJECT_ROOT / "results" / "reports" / PHASE3_DIR_NAME

for output_dir in [PHASE3_TABLES_DIR, PHASE3_FIGURES_DIR, PHASE3_REPORTS_DIR]:
    output_dir.mkdir(parents=True, exist_ok=True)

for old_table_path in PHASE3_TABLES_DIR.glob("*.csv"):
    old_table_path.unlink()

for old_figure_path in list(PHASE3_FIGURES_DIR.glob("*.png")) + list(PHASE3_FIGURES_DIR.glob("*.pdf")):
    old_figure_path.unlink()

for old_report_path in PHASE3_REPORTS_DIR.glob("*"):
    if old_report_path.is_file() and old_report_path.suffix.lower() in {".md", ".tex", ".png"}:
        old_report_path.unlink()

print(f"Proyecto: {PROJECT_ROOT}")
print(f"Datos crudos: {RAW_DATA_DIR.relative_to(PROJECT_ROOT)}")
print(f"Datos procesados: {PROCESSED_DATA_DIR.relative_to(PROJECT_ROOT)}")
print("Tablas de Fase 2 listas para lectura directa.")
print("Directorio de salidas de Fase 3 preparado.")
"""))
    cells.append(md("""
Lectura inicial: el proyecto queda localizado y se preparan 3 directorios de trabajo para esta fase: tablas, figuras e informe breve. La fase no lee resultados agregados; solo reutiliza las rutas necesarias para calcular cada sección.
"""))

    cells.append(md("""
## Configuración Visual y Parámetros Generales

Los parámetros se declaran aquí como criterios operativos de lectura. No eliminan variables ni modifican datos; solo acotan coste computacional y fijan referencias comunes para interpretar la auditoría:

- `MAX_SAMPLE_ASSOCIATION = 12000`: limita los cálculos de Spearman y mutual information. Se fija por el tamaño de `customer_churn`, que domina el coste, y mantiene una muestra suficientemente amplia para diagnóstico exploratorio reproducible.
- `MAX_SAMPLE_PCA = 6000`: limita la PCA descriptiva. La PCA no se aplica como transformación final, por lo que una muestra reproducible basta para resumir la estructura dimensional sin ralentizar el notebook.
- `CHUNK_SIZE_DATASET = 50000`: controla la lectura por bloques de CSV. El valor permite cargar datasets grandes de forma trazable sin cambiar el contenido analizado.
- `HIGH_CORRELATION_THRESHOLD = 0.85`: marca pares con redundancia fuerte. Es un umbral de auditoría habitual para separar asociaciones lineales/monótonas altas de relaciones moderadas.
- `DIMENSIONALITY_RATIO_REFERENCE = 0.20`: referencia la relación features/muestras. Sirve para destacar problemas como Madelon, donde muchas variables por muestra condicionan split, selección y validación.
"""))
    cells.append(code("""
RANDOM_STATE = 42
MAX_SAMPLE_ASSOCIATION = 12000
MAX_SAMPLE_PCA = 6000
CHUNK_SIZE_DATASET = 50000
HIGH_CORRELATION_THRESHOLD = 0.85
DIMENSIONALITY_RATIO_REFERENCE = 0.20

DATASET_ORDER = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil",
]

RAW_FILE_NAMES = {
    "breast_cancer_wisconsin": "breast_cancer_wisconsin.csv",
    "customer_churn": "customer_churn.csv",
    "madelon": "madelon.csv",
    "olive_oil": "olive_oil.csv",
}

RAW_TARGETS = {
    "breast_cancer_wisconsin": "target",
    "customer_churn": "Churn",
    "madelon": "target",
    "olive_oil": "target",
}

PROCESSED_TARGET = "target"
"""))
    cells.append(code("""
DATASET_LABELS = {
    "breast_cancer_wisconsin": "Breast Cancer Wisconsin",
    "customer_churn": "Customer Churn",
    "madelon": "Madelon",
    "olive_oil": "Olive Oil",
}

DATASET_COLORS = {
    "breast_cancer_wisconsin": "#2F6F9F",
    "customer_churn": "#D9822B",
    "madelon": "#5E8C61",
    "olive_oil": "#7A6FA5",
}

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

pd.set_option("display.max_columns", 34)
pd.set_option("display.max_rows", 60)
pd.set_option("display.max_colwidth", 80)
"""))

    cells.append(md("""
## Utilidades Generales del Notebook

Estas funciones se reutilizan durante la fase para guardar tablas, mostrar resultados, guardar figuras y mantener un estilo visual común.
"""))
    cells.append(code("""
def guardar_tabla(tabla, nombre_archivo):
    ruta_tabla = PHASE3_TABLES_DIR / nombre_archivo
    tabla.to_csv(ruta_tabla, index=False)
    return ruta_tabla


TRADUCCIONES_COLUMNAS = {
    "dataset": "Dataset",
    "origen": "Origen",
    "filas": "Filas",
    "columnas": "Columnas",
    "features": "Variables predictoras",
    "variable": "Variable",
    "dtype": "Tipo de dato",
    "valores_unicos": "Valores únicos",
    "nulos": "Nulos",
    "pct_nulos": "% nulos",
    "infinitos": "Infinitos",
    "chunks": "Bloques",
    "chunk_size": "Tamaño de bloque",
    "filas_raw": "Filas crudas",
    "filas_processed": "Filas procesadas",
    "columnas_raw": "Columnas crudas",
    "columnas_processed": "Columnas procesadas",
    "delta_filas": "Diferencia de filas",
    "delta_columnas": "Diferencia de columnas",
    "features_raw": "Predictoras crudas",
    "features_processed": "Predictoras procesadas",
    "delta_features": "Diferencia de predictoras",
    "target_raw": "Target crudo",
    "target_processed": "Target procesado",
    "target_processed_presente": "Target procesado presente",
    "target_presente": "Target presente",
    "target_nulos": "Nulos en target",
    "target_clases": "Clases del target",
    "variables_numericas": "Variables numéricas",
    "variables_categoricas": "Variables categóricas",
    "columnas_duplicadas": "Columnas duplicadas",
    "codigo": "Código de clase",
    "n": "N",
    "n_raw": "N crudo",
    "n_processed": "N procesado",
    "delta_n": "Diferencia de N",
    "proporcion": "Proporción",
    "proporcion_raw": "Proporción cruda",
    "proporcion_processed": "Proporción procesada",
    "delta_proporcion": "Diferencia de proporción",
    "delta_proporcion_abs": "|diferencia de proporción|",
    "chi2_stat": "Estadístico chi2",
    "chi2_p_value": "Valor p chi2",
    "chi2_dof": "Grados de libertad chi2",
    "fisher_oddsratio": "Odds ratio Fisher",
    "fisher_p_value": "Valor p Fisher",
    "max_delta_proporcion": "Máx. |diferencia de proporción|",
    "ratio_may_min_raw": "Ratio mayoritaria/minoritaria crudo",
    "ratio_may_min_processed": "Ratio mayoritaria/minoritaria procesado",
    "delta_ratio_may_min": "Diferencia de ratio",
    "ratio_mayoritaria_minoritaria": "Ratio mayoritaria/minoritaria",
    "entropia_raw": "Entropía cruda",
    "entropia_processed": "Entropía procesada",
    "delta_entropia": "Diferencia de entropía",
    "clases": "Clases",
    "proporcion_minima": "Proporción mínima",
    "proporcion_maxima": "Proporción máxima",
    "mediana_raw": "Mediana cruda",
    "mediana_processed": "Mediana procesada",
    "delta_mediana_abs": "|diferencia de mediana|",
    "iqr_raw": "IQR crudo",
    "iqr_processed": "IQR procesado",
    "delta_iqr_abs": "|diferencia de IQR|",
    "ks_statistic": "Estadístico KS",
    "ks_p_value": "Valor p KS",
    "wasserstein_distance": "Distancia Wasserstein",
    "psi": "PSI",
    "js_divergence": "Divergencia JS",
    "max_delta_percentil": "Máx. |diferencia de percentil|",
    "spearman_raw_processed": "Spearman crudo/procesado",
    "score_shift": "Score de desplazamiento",
    "ks_maximo": "KS máximo",
    "wasserstein_maximo": "Wasserstein máximo",
    "psi_maximo": "PSI máximo",
    "js_maximo": "JS máximo",
    "spearman_minimo": "Spearman mínimo",
    "score_shift_maximo": "Score máximo de desplazamiento",
    "minimo": "Mínimo",
    "maximo": "Máximo",
    "rango": "Rango",
    "mediana": "Mediana",
    "iqr": "IQR",
    "metodo_asociacion": "Método de asociación",
    "score_asociacion": "Score de asociación",
    "mutual_information": "Información mutua",
    "spearman_abs": "|Spearman|",
    "p_value": "Valor p",
    "p_value_fdr": "Valor p FDR",
    "significativa_fdr_005": "Significativa FDR 0.05",
    "score_raw": "Score crudo",
    "score_processed": "Score procesado",
    "delta": "Diferencia",
    "delta_abs": "|diferencia|",
    "ranking_raw": "Ranking crudo",
    "ranking_processed": "Ranking procesado",
    "variables_comunes": "Variables comunes",
    "spearman_rankings_raw_processed": "Spearman rankings crudo/procesado",
    "top_k": "Top-k",
    "top_k_overlap": "Solapamiento top-k",
    "top_k_overlap_ratio": "Ratio de solapamiento top-k",
    "fdr_significativas_005": "Variables FDR<=0.05",
    "metodo": "Método",
    "variable_a": "Variable A",
    "variable_b": "Variable B",
    "abs_correlacion": "|correlación|",
    "variables_comunes": "Variables comunes",
    "pares_comunes": "Pares comunes",
    "correlacion_entre_matrices": "Correlación entre matrices",
    "frobenius_norm_difference": "Diferencia norma Frobenius",
    "vif": "VIF",
    "vif_max": "VIF máximo",
    "vif_mediana": "VIF mediano",
    "variables_vif_ge_10": "Variables con VIF>=10",
    "incluye_target": "Incluye target",
    "cramers_v": "V de Cramér",
    "pares_evaluados": "Pares evaluados",
    "pares_abs_pearson_ge_085": "Pares Pearson >=0.85",
    "pares_abs_spearman_ge_085": "Pares Spearman >=0.85",
    "abs_pearson_maxima": "|Pearson| máxima",
    "abs_spearman_maxima": "|Spearman| máxima",
    "pca_varianza_2": "Varianza PCA 2",
    "pca_varianza_5": "Varianza PCA 5",
    "n_pca_usado": "Filas usadas en PCA",
    "ratio_features_muestras": "Ratio predictoras/muestras",
    "supera_referencia_020": "Supera referencia 0.20",
    "nulos_totales": "Nulos totales",
    "infinitos_totales": "Infinitos totales",
}


TRADUCCIONES_VALORES = {
    "raw": "datos crudos",
    "processed": "datos procesados",
    "raw_codificado": "datos crudos codificados",
}


def preparar_tabla_para_mostrar(tabla):
    tabla_display = tabla.copy()
    for columna in tabla_display.select_dtypes(include="object").columns:
        tabla_display[columna] = tabla_display[columna].replace(TRADUCCIONES_VALORES)
    tabla_display = tabla_display.rename(columns=lambda name: TRADUCCIONES_COLUMNAS.get(name, str(name).replace("_", " ").capitalize()))
    return tabla_display


def mostrar_tabla(tabla, nombre=None, n=10):
    if nombre is not None:
        display(Markdown(f"**{nombre}** - {tabla.shape[0]} filas, {tabla.shape[1]} columnas."))
    display(preparar_tabla_para_mostrar(tabla).head(n))


def guardar_figura(figura, nombre_archivo):
    ruta_png = PHASE3_FIGURES_DIR / Path(nombre_archivo).with_suffix(".png").name
    ruta_pdf = ruta_png.with_suffix(".pdf")
    figura.savefig(ruta_png, dpi=300, bbox_inches="tight")
    figura.savefig(ruta_pdf, bbox_inches="tight")
    return ruta_png, ruta_pdf


def cerrar_figura_narrativa(figura, nombre_archivo):
    figura.tight_layout()
    guardar_figura(figura, nombre_archivo)
    plt.show()


def aplicar_estilo_eje(eje, eje_rejilla="x"):
    eje.spines["top"].set_visible(False)
    eje.spines["right"].set_visible(False)
    eje.grid(axis=eje_rejilla, alpha=0.65)
    eje.set_axisbelow(True)


def formatear_numero(valor, decimales=3):
    if pd.isna(valor):
        return "no calculable"
    if abs(valor) >= 1000:
        return f"{valor:,.0f}".replace(",", ".")
    return f"{valor:.{decimales}f}"
"""))
    cells.append(code("""
def leer_tabla_csv(ruta_tabla):
    if not ruta_tabla.exists():
        raise FileNotFoundError(f"No existe la tabla: {ruta_tabla}")
    return pd.read_csv(ruta_tabla)


def obtener_info_texto(datos_dataset):
    salida_info = io.StringIO()
    datos_dataset.info(buf=salida_info)
    return salida_info.getvalue()


def etiqueta_dataset(nombre_dataset):
    return DATASET_LABELS.get(nombre_dataset, nombre_dataset.replace("_", " ").title())


def color_dataset(nombre_dataset):
    return DATASET_COLORS[nombre_dataset]


def fijar_titulo_narrativo(figura, mensaje):
    figura.suptitle(mensaje, fontsize=13, y=1.03)
"""))

    cells.append(md("""
## 3.1 Carga de Datasets Procesados

Se recargan los datos crudos y procesados con tres comprobaciones simples: mismas filas, target procesado presente y lectura reproducible por bloques. Además se cargan directamente tres tablas de la fase anterior porque son necesarias para cálculos concretos de este capítulo: la codificación del target, el renombrado de columnas y la estimación de dimensionalidad si se codifican categóricas después del split.

Punto metodológico clave: `customer_churn` mantiene categóricas predictoras. No se codifican aquí porque el encoder debe ajustarse después del split, dentro del entrenamiento.
"""))
    cells.append(code("""
def cargar_tabla_fase2(nombre_archivo):
    ruta_tabla = PHASE2_TABLES_DIR / nombre_archivo
    assert ruta_tabla.exists()
    return pd.read_csv(ruta_tabla)


target_encoding_phase2 = cargar_tabla_fase2("fase2_codificacion_target.csv")
renaming_phase2 = cargar_tabla_fase2("fase2_renombrado_columnas.csv")
encoding_dimensionality_phase2 = cargar_tabla_fase2("fase2_dimensionalidad_encoding.csv")
"""))
    cells.append(code("""
def describir_categoricas_churn(encoding_preprocessing):
    churn_encoding = encoding_preprocessing[encoding_preprocessing["dataset"].eq("customer_churn")]
    assert not churn_encoding.empty
    row = churn_encoding.iloc[0]
    return (
        f"`customer_churn` conserva {int(row['predictoras_categoricas'])} categóricas predictoras; "
        f"un one-hot posterior pasaría de {int(row['predictoras_sin_onehot'])} a "
        f"{int(row['predictoras_si_onehot'])} predictoras."
    )


def mostrar_punto_partida_preprocesado():
    lines = [
        "**Punto de partida del análisis.**",
        "Se cargan los datos crudos y procesados para comprobarlos de nuevo desde este capítulo.",
        describir_categoricas_churn(encoding_dimensionality_phase2),
        "La codificación del target y el renombrado de columnas se usan solo cuando la comparación raw/procesado lo requiere.",
    ]
    display(Markdown("\\n\\n".join(lines)))


mostrar_punto_partida_preprocesado()
"""))
    cells.append(code("""
load_chunks_log = []


def leer_csv_por_chunks(ruta_dataset):
    chunks = []
    for chunk in pd.read_csv(ruta_dataset, chunksize=CHUNK_SIZE_DATASET):
        chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()


def registrar_carga_chunk(nombre_dataset, origen, datos, n_chunks):
    load_chunks_log.append({
        "dataset": nombre_dataset,
        "origen": origen,
        "chunks": n_chunks,
        "filas": len(datos),
        "columnas": datos.shape[1],
        "chunk_size": CHUNK_SIZE_DATASET,
    })


def cargar_csv_dataset(ruta_dataset, nombre_dataset, origen):
    if not ruta_dataset.exists():
        raise FileNotFoundError(f"No existe el dataset {origen}: {ruta_dataset}")
    datos = leer_csv_por_chunks(ruta_dataset)
    n_chunks = int(np.ceil(len(datos) / CHUNK_SIZE_DATASET)) if len(datos) else 0
    registrar_carga_chunk(nombre_dataset, origen, datos, n_chunks)
    return datos


def cargar_datos_crudos(nombre_dataset):
    ruta_dataset = RAW_DATA_DIR / RAW_FILE_NAMES[nombre_dataset]
    return cargar_csv_dataset(ruta_dataset, nombre_dataset, "raw")


def cargar_datos_procesados(nombre_dataset):
    ruta_dataset = PROCESSED_DATA_DIR / f"{nombre_dataset}_processed.csv"
    return cargar_csv_dataset(ruta_dataset, nombre_dataset, "processed")
"""))
    cells.append(code("""
def resumir_carga_postprocesado(nombre_dataset, datos_raw, datos_processed):
    return {
        "dataset": nombre_dataset,
        "filas_raw": datos_raw.shape[0],
        "filas_processed": datos_processed.shape[0],
        "columnas_raw": datos_raw.shape[1],
        "columnas_processed": datos_processed.shape[1],
        "target_raw": RAW_TARGETS[nombre_dataset],
        "target_processed": PROCESSED_TARGET,
        "target_processed_presente": PROCESSED_TARGET in datos_processed.columns,
    }
"""))

    load_observations = {
        "breast_cancer_wisconsin": "Observación: la carga conserva 569 filas y pasa de 32 a 31 columnas; la resta de 1 columna corresponde al identificador revisado en Fase 2.",
        "customer_churn": "Observación: el dataset mantiene 440832 filas y pasa de 12 a 11 columnas; las 3 categóricas predictoras siguen presentes para codificación posterior al split.",
        "madelon": "Observación: el procesado conserva 2000 filas y 501 columnas; las 500 features siguen intactas porque la reducción dimensional no pertenece a Fase 3.",
        "olive_oil": "Observación: la carga mantiene 572 filas y pasa de 12 a 11 columnas; las 9 clases del target se revisan después para confirmar proporciones.",
    }
    add_dataset_cells(
        cells,
        "Carga Post-Preprocesado",
        """
raw___VARIABLE__ = cargar_datos_crudos("__DATASET__")
processed___VARIABLE__ = cargar_datos_procesados("__DATASET__")

print("raw shape:", raw___VARIABLE__.shape)
display(raw___VARIABLE__.head())
print(obtener_info_texto(raw___VARIABLE__))

print("processed shape:", processed___VARIABLE__.shape)
display(processed___VARIABLE__.head())
print(obtener_info_texto(processed___VARIABLE__))
""",
        load_observations,
    )
    cells.append(md("### Resumen Común de Carga"))
    cells.append(code("""
raw_datasets = {
    "breast_cancer_wisconsin": raw_breast_cancer_wisconsin,
    "customer_churn": raw_customer_churn,
    "madelon": raw_madelon,
    "olive_oil": raw_olive_oil,
}

processed_datasets = {
    "breast_cancer_wisconsin": processed_breast_cancer_wisconsin,
    "customer_churn": processed_customer_churn,
    "madelon": processed_madelon,
    "olive_oil": processed_olive_oil,
}

load_summary = pd.DataFrame([
    resumir_carga_postprocesado(dataset_name, raw_datasets[dataset_name], processed_datasets[dataset_name])
    for dataset_name in DATASET_ORDER
])

guardar_tabla(load_summary, "fase3_carga_datasets.csv")
chunk_load_summary = pd.DataFrame(load_chunks_log)
guardar_tabla(chunk_load_summary, "fase3_carga_datasets_chunks.csv")
mostrar_tabla(load_summary, "Carga de datos crudos y procesados")
mostrar_tabla(chunk_load_summary, "Carga de datasets por bloques", n=20)

def resumen_carga_markdown(load_table, chunk_table):
    filas_iguales = int((load_table["filas_raw"] == load_table["filas_processed"]).sum())
    delta_columnas_min = int(load_table["columnas_processed"].sub(load_table["columnas_raw"]).min())
    delta_columnas_max = int(load_table["columnas_processed"].sub(load_table["columnas_raw"]).max())
    chunks_max = int(chunk_table["chunks"].max())
    dataset_mas_grande = load_table.sort_values("filas_processed", ascending=False).iloc[0]
    lines = [
        "**Lectura comparativa de carga.**",
        f"Los {filas_iguales}/{len(load_table)} datasets conservan exactamente las filas tras el preprocesado; "
        f"el mayor volumen es `{dataset_mas_grande['dataset']}` con {int(dataset_mas_grande['filas_processed'])} filas procesadas.",
        f"El cambio de columnas queda entre {delta_columnas_min} y {delta_columnas_max}; por tanto la carga confirma retiradas estructurales puntuales, no pérdida de muestras.",
        f"La lectura por bloques llega como máximo a {chunks_max} chunk(s) con `CHUNK_SIZE_DATASET={CHUNK_SIZE_DATASET}`, suficiente para dejar trazable la recarga antes del split.",
    ]
    return "\\n\\n".join(lines)


display(Markdown(resumen_carga_markdown(load_summary, chunk_load_summary)))
"""))

    cells.append(md("""
## 3.2 Validación Estructural del Dataset Procesado

Se revisan dimensiones, tipos, nulos, infinitos, columnas duplicadas, target y variables categóricas pendientes con el criterio operativo de cero bloqueos estructurales antes del split. Esta sección no decide tratamientos: solo mide el estado posterior al preprocesado y separa incidencias reales de condiciones heredadas por diseño.
"""))
    cells.append(code("""
def resumir_estructura_processed(nombre_dataset, datos_processed):
    predictor_names = [name for name in datos_processed.columns if name != PROCESSED_TARGET]
    return {
        "dataset": nombre_dataset,
        "filas": datos_processed.shape[0],
        "columnas": datos_processed.shape[1],
        "features": len(predictor_names),
        "variables_numericas": sum(pd.api.types.is_numeric_dtype(datos_processed[name]) for name in predictor_names),
        "variables_categoricas": sum(not pd.api.types.is_numeric_dtype(datos_processed[name]) for name in predictor_names),
        "columnas_duplicadas": int(pd.Index(datos_processed.columns).duplicated().sum()),
        "target_presente": PROCESSED_TARGET in datos_processed.columns,
        "target_nulos": int(datos_processed[PROCESSED_TARGET].isna().sum()),
        "target_clases": int(datos_processed[PROCESSED_TARGET].nunique(dropna=True)),
    }


def crear_fila_tipo(nombre_dataset, serie):
    return {
        "dataset": nombre_dataset,
        "variable": serie.name,
        "dtype": str(serie.dtype),
        "valores_unicos": int(serie.nunique(dropna=False)),
        "nulos": int(serie.isna().sum()),
    }


def resumir_tipos_processed(nombre_dataset, datos_processed):
    return pd.DataFrame([crear_fila_tipo(nombre_dataset, datos_processed[name]) for name in datos_processed.columns])
"""))
    cells.append(code("""
def crear_fila_nulos_infinitos(nombre_dataset, serie):
    infinitos = int(np.isinf(serie).sum()) if pd.api.types.is_numeric_dtype(serie) else 0
    return {
        "dataset": nombre_dataset,
        "variable": serie.name,
        "nulos": int(serie.isna().sum()),
        "pct_nulos": float(serie.isna().mean()),
        "infinitos": infinitos,
    }


def resumir_nulos_infinitos(nombre_dataset, datos_processed):
    return pd.DataFrame([crear_fila_nulos_infinitos(nombre_dataset, datos_processed[name]) for name in datos_processed.columns])
"""))
    cells.append(code("""
def crear_fila_categorica_pendiente(nombre_dataset, serie):
    return {
        "dataset": nombre_dataset,
        "variable": serie.name,
        "dtype": str(serie.dtype),
        "valores_unicos": int(serie.nunique(dropna=False)),
    }


def resumir_categoricas_pendientes(nombre_dataset, datos_processed):
    rows = []
    for variable_name in datos_processed.columns:
        if variable_name != PROCESSED_TARGET and not pd.api.types.is_numeric_dtype(datos_processed[variable_name]):
            rows.append(crear_fila_categorica_pendiente(nombre_dataset, datos_processed[variable_name]))
    return pd.DataFrame(rows, columns=[
        "dataset",
        "variable",
        "dtype",
        "valores_unicos",
    ])
"""))
    cells.append(code("""
def mostrar_estado_categoricas_pendientes(pending_categories_dataset, nombre_dataset):
    if pending_categories_dataset.empty:
        display(Markdown(f"`{nombre_dataset}` no mantiene predictoras categóricas pendientes."))
        return
    n_variables = len(pending_categories_dataset)
    cardinalidad_maxima = int(pending_categories_dataset["valores_unicos"].max())
    variables = ", ".join(f"`{name}`" for name in pending_categories_dataset["variable"].head(6))
    display(Markdown(
        f"`{nombre_dataset}` mantiene {n_variables} predictoras categóricas pendientes "
        f"(cardinalidad máxima: {cardinalidad_maxima}). Se conservan sin codificar hasta el split "
        f"para que el encoder se ajuste solo con entrenamiento. Variables visibles: {variables}."
    ))
"""))

    structure_observations = {
        "breast_cancer_wisconsin": "Observación: quedan 30 features numéricas, 0 categóricas, 0 nulos y 0 columnas duplicadas; no hay bloqueo estructural antes del split.",
        "customer_churn": "Observación: quedan 10 features, de las cuales 3 son categóricas; esto no bloquea el split, pero obliga a codificar dentro del entrenamiento posterior.",
        "madelon": "Observación: quedan 500 features numéricas y 0 categóricas para 2000 filas; la dificultad estructural es dimensional, no de tipos ni nulos.",
        "olive_oil": "Observación: quedan 10 features numéricas, 0 categóricas y 9 clases; el punto delicado será el reparto del target, no la forma del archivo.",
    }
    add_dataset_cells(
        cells,
        "Estructura Procesada",
        """
structure___VARIABLE__ = pd.DataFrame([resumir_estructura_processed("__DATASET__", processed___VARIABLE__)])
types___VARIABLE__ = resumir_tipos_processed("__DATASET__", processed___VARIABLE__)
nulls___VARIABLE__ = resumir_nulos_infinitos("__DATASET__", processed___VARIABLE__)
pending_categories___VARIABLE__ = resumir_categoricas_pendientes("__DATASET__", processed___VARIABLE__)

mostrar_tabla(structure___VARIABLE__, "Estructura procesada - __LABEL__")
mostrar_tabla(types___VARIABLE__, "Tipos procesados - __LABEL__", n=12)
mostrar_tabla(nulls___VARIABLE__[nulls___VARIABLE__[["nulos", "infinitos"]].sum(axis=1) > 0], "Nulos o infinitos - __LABEL__", n=12)
mostrar_estado_categoricas_pendientes(pending_categories___VARIABLE__, "__DATASET__")
""",
        structure_observations,
    )
    cells.append(md("### Resumen Comparativo de Estructura"))
    cells.append(code("""
structure_summary = pd.concat([
    structure_breast_cancer_wisconsin,
    structure_customer_churn,
    structure_madelon,
    structure_olive_oil,
], ignore_index=True)

types_summary = pd.concat([
    types_breast_cancer_wisconsin,
    types_customer_churn,
    types_madelon,
    types_olive_oil,
], ignore_index=True)

nulls_summary = pd.concat([
    nulls_breast_cancer_wisconsin,
    nulls_customer_churn,
    nulls_madelon,
    nulls_olive_oil,
], ignore_index=True)

pending_categories = pd.concat([
    pending_categories_breast_cancer_wisconsin,
    pending_categories_customer_churn,
    pending_categories_madelon,
    pending_categories_olive_oil,
], ignore_index=True)

guardar_tabla(structure_summary, "fase3_estructura_processed.csv")
guardar_tabla(types_summary, "fase3_tipos_processed.csv")
guardar_tabla(nulls_summary, "fase3_nulos_infinitos.csv")
mostrar_tabla(structure_summary, "Estructura procesada por dataset")

def resumen_estructura_markdown(structure_table, nulls_table, pending_table):
    nulos_totales = int(nulls_table["nulos"].sum())
    infinitos_totales = int(nulls_table["infinitos"].sum())
    categoricas_total = int(structure_table["variables_categoricas"].sum())
    churn_categoricas = int(structure_table.loc[structure_table["dataset"].eq("customer_churn"), "variables_categoricas"].iloc[0])
    max_features = structure_table.sort_values("features", ascending=False).iloc[0]
    lines = [
        "**Lectura comparativa de estructura.**",
        f"La auditoría no detecta nulos ({nulos_totales}) ni infinitos ({infinitos_totales}) en el conjunto procesado; tampoco aparecen columnas duplicadas.",
        f"`madelon` concentra la mayor dimensionalidad con {int(max_features['features'])} features, mientras `customer_churn` es el único dataset con categóricas pendientes: {churn_categoricas} de {categoricas_total} en total.",
        "La consecuencia para Fase 4 es doble: todos los datasets pueden particionarse sin limpieza adicional y `customer_churn` debe codificarse después del split, ajustando transformadores solo con entrenamiento.",
    ]
    return "\\n\\n".join(lines)


display(Markdown(resumen_estructura_markdown(structure_summary, nulls_summary, pending_categories)))
"""))

    cells.append(md("""
## 3.3 Comparación de Dimensiones Crudas vs Procesadas

Se compara el tamaño de cada dataset antes y después del preprocesado con el criterio de delta de filas igual a cero y cambios de columnas explicables por identificadores o renombrado. La comparación se recalcula directamente desde archivos y se contrasta con `fase2_impacto_estructura.csv`.
"""))
    cells.append(code("""
def resumir_dimensiones_raw_processed(nombre_dataset):
    raw_shape = calcular_forma_dataset(raw_datasets[nombre_dataset])
    processed_shape = calcular_forma_dataset(processed_datasets[nombre_dataset])
    return {
        "dataset": nombre_dataset,
        "filas_raw": raw_shape["filas"],
        "filas_processed": processed_shape["filas"],
        "delta_filas": processed_shape["filas"] - raw_shape["filas"],
        "columnas_raw": raw_shape["columnas"],
        "columnas_processed": processed_shape["columnas"],
        "delta_columnas": processed_shape["columnas"] - raw_shape["columnas"],
        "features_raw": raw_shape["features"],
        "features_processed": processed_shape["features"],
        "delta_features": processed_shape["features"] - raw_shape["features"],
    }


def calcular_forma_dataset(datos_dataset):
    rows, columns = datos_dataset.shape
    return {"filas": rows, "columnas": columns, "features": columns - 1}


def crear_fila_presencia_columna(nombre_dataset, variable_name):
    raw_columns = set(raw_datasets[nombre_dataset].columns)
    processed_columns = set(processed_datasets[nombre_dataset].columns)
    return {
        "dataset": nombre_dataset,
        "variable": variable_name,
        "presente_raw": variable_name in raw_columns,
        "presente_processed": variable_name in processed_columns,
    }


def resumir_variables_raw_processed(nombre_dataset):
    raw_columns = set(raw_datasets[nombre_dataset].columns)
    processed_columns = set(processed_datasets[nombre_dataset].columns)
    return pd.DataFrame([crear_fila_presencia_columna(nombre_dataset, name) for name in sorted(raw_columns | processed_columns)])
"""))

    dimensions_observations = {
        "breast_cancer_wisconsin": "Lectura dimensional: mantiene 569 filas y baja de 32 a 31 columnas; la única diferencia coincide con la eliminación del identificador.",
        "customer_churn": "Revisión dimensional: conserva 440832 filas y baja de 12 a 11 columnas; la retirada de `CustomerID` no cambia el volumen muestral.",
        "madelon": "Control dimensional: conserva 2000 filas, 501 columnas y 500 features; el preprocesado no reduce la complejidad original.",
        "olive_oil": "Chequeo dimensional: mantiene 572 filas y baja de 12 a 11 columnas; la auditoría del target comprueba después las 9 clases.",
    }
    add_dataset_cells(
        cells,
        "Dimensiones Crudas vs Procesadas",
        """
dimensions___VARIABLE__ = pd.DataFrame([resumir_dimensiones_raw_processed("__DATASET__")])
columns___VARIABLE__ = resumir_variables_raw_processed("__DATASET__")

mostrar_tabla(dimensions___VARIABLE__, "Dimensiones crudas vs procesadas - __LABEL__")
mostrar_tabla(columns___VARIABLE__[columns___VARIABLE__["presente_raw"] != columns___VARIABLE__["presente_processed"]], "Diferencias de presencia de columnas - __LABEL__", n=20)
""",
        dimensions_observations,
    )
    cells.append(md("### Resumen Comparativo de Dimensiones"))
    cells.append(code("""
dimensions_summary = pd.concat([
    dimensions_breast_cancer_wisconsin,
    dimensions_customer_churn,
    dimensions_madelon,
    dimensions_olive_oil,
], ignore_index=True)

column_presence = pd.concat([
    columns_breast_cancer_wisconsin,
    columns_customer_churn,
    columns_madelon,
    columns_olive_oil,
], ignore_index=True)

guardar_tabla(dimensions_summary, "fase3_dimensiones_raw_processed.csv")
guardar_tabla(column_presence, "fase3_columnas_raw_processed.csv")
mostrar_tabla(dimensions_summary, "Dimensiones crudas vs procesadas")

def resumen_dimensiones_markdown(dimensions_table):
    filas_delta_max = int(dimensions_table["delta_filas"].abs().max())
    retirada_max = int(dimensions_table["delta_columnas"].min())
    sin_cambio = dimensions_table.loc[dimensions_table["delta_columnas"].eq(0), "dataset"].tolist()
    retiradas = dimensions_table.loc[dimensions_table["delta_columnas"].lt(0), ["dataset", "delta_columnas"]]
    detalle_retiradas = "; ".join(f"`{row.dataset}` {int(row.delta_columnas)}" for row in retiradas.itertuples())
    lines = [
        "**Lectura comparativa de dimensiones.**",
        f"El delta máximo de filas es {filas_delta_max}: ningún dataset pierde muestras antes del split.",
        f"El cambio de columnas más grande es {retirada_max}; las retiradas quedan en {detalle_retiradas}, mientras {', '.join(f'`{name}`' for name in sin_cambio)} conserva su anchura original.",
        "La antigua comparación de barras crudo/procesado se elimina porque solo repetiría esta tabla; la comprobación visual útil se traslada a 3.7, donde se mide si el orden de señal variable-target se conserva.",
    ]
    return "\\n\\n".join(lines)


display(Markdown(resumen_dimensiones_markdown(dimensions_summary)))
"""))

    cells.append(md("""
## 3.4 Auditoría del Target Post-Preprocesado

Se verifica que el target procesado conserva las proporciones del target original una vez aplicado el mapping de Fase 2. El mapping se toma de `fase2_codificacion_target.csv`, que contiene valores observados y códigos.

La lectura estadística combina varias señales complementarias:

- El delta de proporciones compara cada clase entre raw codificado y processed. Un delta cercano a cero indica que el preprocesado no ha alterado la composición del problema.
- El test chi-cuadrado contrasta si la distribución de clases cambia entre ambos orígenes. En esta fase se espera ausencia de cambio porque se compara el mismo dataset antes y después de codificar/renombrar.
- Fisher se calcula solo en tablas 2x2, por tanto aplica a targets binarios como `breast_cancer_wisconsin`, `customer_churn` y `madelon`; en `olive_oil` no se informa porque el target es multiclase.
- El ratio mayoritaria/minoritaria mide desbalance final. No demuestra cambio raw-processed por sí solo, pero condiciona la estratificación del split.

Por dataset, el resultado esperado es distinto: `breast_cancer_wisconsin`, `customer_churn` y `madelon` deben conservar proporciones binarias; `olive_oil` debe conservar proporciones multiclase y dejar visible su desbalance.
"""))
    cells.append(code("""
def variantes_valor_target(valor_original):
    variantes = {str(valor_original)}
    if pd.isna(valor_original):
        return variantes
    try:
        valor_numerico = float(valor_original)
    except (TypeError, ValueError):
        return variantes
    variantes.add(str(valor_numerico))
    if valor_numerico.is_integer():
        variantes.add(str(int(valor_numerico)))
    return variantes


def construir_mapa_target_desde_encoding(nombre_dataset):
    selected = target_encoding_phase2[target_encoding_phase2["dataset"].eq(nombre_dataset)].copy()
    mapping = {}
    for _, row in selected.iterrows():
        for target_value in variantes_valor_target(row["valor_original"]):
            mapping[target_value] = int(row["codigo"])
    return mapping


def codificar_target_raw(nombre_dataset):
    target_name = RAW_TARGETS[nombre_dataset]
    mapping = construir_mapa_target_desde_encoding(nombre_dataset)
    raw_values = raw_datasets[nombre_dataset][target_name].astype(str)
    return raw_values.map(mapping)
"""))
    cells.append(code("""
def crear_distribucion_target(nombre_dataset, origen, serie_target):
    counts = serie_target.value_counts(dropna=False).sort_index()
    return pd.DataFrame([
        {
            "dataset": nombre_dataset,
            "origen": origen,
            "codigo": code,
            "n": int(count),
            "proporcion": count / len(serie_target),
        }
        for code, count in counts.items()
    ])


def resumir_distribucion_target(nombre_dataset):
    raw_target_encoded = codificar_target_raw(nombre_dataset)
    processed_target = processed_datasets[nombre_dataset][PROCESSED_TARGET]
    raw_distribution = crear_distribucion_target(nombre_dataset, "raw_codificado", raw_target_encoded)
    processed_distribution = crear_distribucion_target(nombre_dataset, "processed", processed_target)
    return pd.concat([raw_distribution, processed_distribution], ignore_index=True)
"""))
    cells.append(code("""
def pivotar_target_por_origen(distribution, value_column):
    return distribution.pivot_table(
        index=["dataset", "codigo"],
        columns="origen",
        values=value_column,
        fill_value=0,
    ).reset_index()


def fusionar_conteos_y_proporciones_target(distribution):
    counts = pivotar_target_por_origen(distribution, "n")
    proportions = pivotar_target_por_origen(distribution, "proporcion")
    comparison = counts.merge(proportions, on=["dataset", "codigo"], suffixes=("_n", "_proporcion"))
    return comparison.rename(columns={
        "raw_codificado_n": "n_raw",
        "processed_n": "n_processed",
        "raw_codificado_proporcion": "proporcion_raw",
        "processed_proporcion": "proporcion_processed",
    })
"""))
    cells.append(code("""
def seleccionar_columnas_target_comparado(comparison):
    comparison["delta_n"] = comparison["n_processed"] - comparison["n_raw"]
    comparison["delta_proporcion"] = comparison["proporcion_processed"] - comparison["proporcion_raw"]
    comparison["delta_proporcion_abs"] = comparison["delta_proporcion"].abs()
    return comparison[[
        "dataset",
        "codigo",
        "n_raw",
        "n_processed",
        "delta_n",
        "proporcion_raw",
        "proporcion_processed",
        "delta_proporcion",
        "delta_proporcion_abs",
    ]]


def comparar_target_raw_processed(nombre_dataset):
    distribution = resumir_distribucion_target(nombre_dataset)
    comparison = fusionar_conteos_y_proporciones_target(distribution)
    return seleccionar_columnas_target_comparado(comparison)
"""))
    cells.append(code("""
def calcular_entropia_proporciones(proportions):
    values = np.asarray([value for value in proportions if value > 0], dtype=float)
    if len(values) == 0:
        return np.nan
    return float(-(values * np.log2(values)).sum())


def calcular_ratio_mayoritaria_minoritaria(proportions):
    values = np.asarray([value for value in proportions if value > 0], dtype=float)
    if len(values) == 0:
        return np.nan
    return float(values.max() / values.min())


def calcular_fisher_si_binario(contingency):
    if contingency.shape == (2, 2):
        return fisher_exact(contingency.astype(int))
    return np.nan, np.nan


def extraer_proporciones_target(target_comparison):
    raw_props = target_comparison["proporcion_raw"].to_numpy(dtype=float)
    processed_props = target_comparison["proporcion_processed"].to_numpy(dtype=float)
    return raw_props, processed_props
"""))
    cells.append(code("""
def resumir_balance_target(raw_props, processed_props):
    ratio_raw = calcular_ratio_mayoritaria_minoritaria(raw_props)
    ratio_processed = calcular_ratio_mayoritaria_minoritaria(processed_props)
    return {
        "ratio_may_min_raw": ratio_raw,
        "ratio_may_min_processed": ratio_processed,
        "delta_ratio_may_min": ratio_processed - ratio_raw,
        "entropia_raw": calcular_entropia_proporciones(raw_props),
        "entropia_processed": calcular_entropia_proporciones(processed_props),
    }


def calcular_tests_homogeneidad_target(target_comparison):
    contingency = target_comparison[["n_raw", "n_processed"]].to_numpy(dtype=float).T
    chi2_stat, chi2_pvalue, chi2_dof, _ = chi2_contingency(contingency, correction=False)
    fisher_oddsratio, fisher_pvalue = calcular_fisher_si_binario(contingency)
    return chi2_stat, chi2_pvalue, chi2_dof, fisher_oddsratio, fisher_pvalue


def crear_fila_tests_target(nombre_dataset, tests, balance, max_delta):
    chi2_stat, chi2_pvalue, chi2_dof, fisher_oddsratio, fisher_pvalue = tests
    return {
        "dataset": nombre_dataset,
        "chi2_stat": float(chi2_stat),
        "chi2_p_value": float(chi2_pvalue),
        "chi2_dof": int(chi2_dof),
        "fisher_oddsratio": float(fisher_oddsratio) if pd.notna(fisher_oddsratio) else np.nan,
        "fisher_p_value": float(fisher_pvalue) if pd.notna(fisher_pvalue) else np.nan,
        "max_delta_proporcion": max_delta,
        **balance,
        "delta_entropia": balance["entropia_processed"] - balance["entropia_raw"],
    }


def evaluar_tests_target(nombre_dataset, target_comparison):
    raw_props, processed_props = extraer_proporciones_target(target_comparison)
    balance = resumir_balance_target(raw_props, processed_props)
    max_delta = float(target_comparison["delta_proporcion_abs"].max())
    tests = calcular_tests_homogeneidad_target(target_comparison)
    return crear_fila_tests_target(nombre_dataset, tests, balance, max_delta)
"""))
    cells.append(code("""
def mensaje_target_dataset(target_comparison, nombre_dataset):
    max_delta = target_comparison["delta_proporcion_abs"].max()
    if max_delta < 1e-12:
        return f"{etiqueta_dataset(nombre_dataset)} conserva el target sin delta medible"
    return f"{etiqueta_dataset(nombre_dataset)} requiere revisar el target: delta max {max_delta:.4f}"


def dibujar_proporciones_target(eje, ordered, positions, width, nombre_dataset):
    eje.barh(positions - width / 2, ordered["proporcion_raw"], height=width, color="#B8B0A3", label="Crudo codificado")
    eje.barh(positions + width / 2, ordered["proporcion_processed"], height=width, color=color_dataset(nombre_dataset), label="Procesado")
    eje.set_xlabel("Proporción")
    eje.set_title("Proporciones por clase", loc="left", fontweight="bold")
    eje.legend(frameon=False)


def dibujar_delta_target(eje, ordered, positions):
    eje.barh(positions, ordered["delta_proporcion"], color="#B85C5C")
    eje.scatter(ordered["delta_proporcion"], positions, color="#B85C5C", s=34, zorder=3)
    for position, delta in zip(positions, ordered["delta_proporcion"]):
        eje.annotate(f"{delta:.3f}", (delta, position), xytext=(8, 0), textcoords="offset points", va="center", fontsize=8)
    eje.axvline(0, color="#2D2A26", linewidth=0.9)
    eje.set_xlabel("Procesado - crudo")
    eje.set_title("Delta de proporción", loc="left", fontweight="bold")


def etiquetar_clases_target(ejes, labels, positions):
    for eje in ejes:
        eje.set_yticks(positions)
        eje.set_yticklabels([f"Clase {label}" for label in labels])
        aplicar_estilo_eje(eje, eje_rejilla="x")
"""))
    cells.append(code("""
def graficar_target_dataset(target_comparison, nombre_dataset):
    ordered = target_comparison.sort_values("codigo").copy()
    labels = ordered["codigo"].astype(str)
    positions = np.arange(len(ordered))
    width = 0.36
    altura = max(3.8, 0.42 * len(ordered) + 2.4)
    figura, ejes = plt.subplots(1, 2, figsize=(10.8, altura), width_ratios=[1.45, 1.0])
    dibujar_proporciones_target(ejes[0], ordered, positions, width, nombre_dataset)
    dibujar_delta_target(ejes[1], ordered, positions)
    etiquetar_clases_target(ejes, labels, positions)
    fijar_titulo_narrativo(figura, mensaje_target_dataset(ordered, nombre_dataset))
    cerrar_figura_narrativa(figura, f"fase3_target_conservacion_{nombre_dataset}.png")
"""))

    target_observations = {
        "breast_cancer_wisconsin": "Lectura del target: el delta máximo entre crudo y procesado vale 0.000000; el ratio 1.68 mantiene un binario moderadamente desbalanceado.",
        "customer_churn": "Revisión del target: crudo codificado y procesado coinciden con diferencia máxima 0.000000; el ratio 1.31 pide estratificación posterior.",
        "madelon": "Control del target: las dos clases quedan en proporción 0.50/0.50 y delta 0.000000; la dificultad procede de 500 features.",
        "olive_oil": "Chequeo del target: las 9 clases conservan proporciones con delta 0.000000, pero el ratio 8.24 exige una partición estratificada.",
    }
    add_dataset_cells(
        cells,
        "Target Post-Preprocesado",
        """
target_distribution___VARIABLE__ = resumir_distribucion_target("__DATASET__")
target_comparison___VARIABLE__ = comparar_target_raw_processed("__DATASET__")
target_tests___VARIABLE__ = pd.DataFrame([evaluar_tests_target("__DATASET__", target_comparison___VARIABLE__)])

mostrar_tabla(target_comparison___VARIABLE__, "Target crudo vs procesado - __LABEL__", n=20)
mostrar_tabla(target_tests___VARIABLE__, "Tests del target crudo vs procesado - __LABEL__")
graficar_target_dataset(target_comparison___VARIABLE__, "__DATASET__")
""",
        target_observations,
    )
    cells.append(md("### Resumen Comparativo del Target"))
    cells.append(code("""
target_distribution = pd.concat([
    target_distribution_breast_cancer_wisconsin,
    target_distribution_customer_churn,
    target_distribution_madelon,
    target_distribution_olive_oil,
], ignore_index=True)

target_comparison = pd.concat([
    target_comparison_breast_cancer_wisconsin,
    target_comparison_customer_churn,
    target_comparison_madelon,
    target_comparison_olive_oil,
], ignore_index=True)

target_tests = pd.concat([
    target_tests_breast_cancer_wisconsin,
    target_tests_customer_churn,
    target_tests_madelon,
    target_tests_olive_oil,
], ignore_index=True)

target_summary = target_comparison.groupby("dataset", as_index=False).agg(
    clases=("codigo", "nunique"),
    proporcion_minima=("proporcion_processed", "min"),
    proporcion_maxima=("proporcion_processed", "max"),
    max_delta_proporcion=("delta_proporcion_abs", "max"),
)
target_summary["ratio_mayoritaria_minoritaria"] = target_summary["proporcion_maxima"] / target_summary["proporcion_minima"]
target_summary = target_summary.merge(
    target_tests[["dataset", "chi2_p_value", "fisher_p_value", "delta_ratio_may_min", "delta_entropia"]],
    on="dataset",
    how="left",
)

guardar_tabla(target_distribution, "fase3_target_distribucion.csv")
guardar_tabla(target_comparison, "fase3_target_shift.csv")
guardar_tabla(target_tests, "fase3_target_tests.csv")
guardar_tabla(target_summary, "fase3_target_resumen.csv")
mostrar_tabla(target_summary, "Resumen estadístico del target")

def resumen_target_markdown(target_table):
    lines = ["**Lectura de resultados del target.**"]
    for _, row in target_table.iterrows():
        fisher_text = "no aplica por target multiclase" if pd.isna(row["fisher_p_value"]) else f"Fisher p={row['fisher_p_value']:.3f}"
        lines.append(
            f"- `{row['dataset']}`: max |delta proporción|={row['max_delta_proporcion']:.6f}, "
            f"ratio mayoritaria/minoritaria={row['ratio_mayoritaria_minoritaria']:.2f}, "
            f"chi2 p={row['chi2_p_value']:.3f}, {fisher_text}. "
            "El indicio importante es el delta nulo o casi nulo: el preprocesado no cambia la composición del problema."
        )
    lines.append(
        "Implicación: Fase 4 debe preservar estas proporciones con split estratificado; los p-valores solo respaldan la conservación, "
        "no sustituyen la lectura práctica del delta y del desbalance."
    )
    return "\\n".join(lines)


display(Markdown(resumen_target_markdown(target_summary)))
"""))
    cells.append(code("""
figura, ejes = plt.subplots(1, 2, figsize=(11.0, 4.2), width_ratios=[1.1, 1.0])
positions = np.arange(len(target_summary))
ejes[0].bar(positions, target_summary["ratio_mayoritaria_minoritaria"], color=[DATASET_COLORS[name] for name in target_summary["dataset"]])
ejes[0].set_xticks(positions)
ejes[0].set_xticklabels([etiqueta_dataset(name) for name in target_summary["dataset"]], rotation=15, ha="right")
ejes[0].set_ylabel("Ratio mayoritaria/minoritaria")
ejes[0].set_title("Imbalance procesado", loc="left", fontweight="bold")

ejes[1].bar(positions, target_summary["max_delta_proporcion"], color="#B85C5C")
ejes[1].scatter(positions, target_summary["max_delta_proporcion"], color="#B85C5C", s=42, zorder=3)
for position, delta in zip(positions, target_summary["max_delta_proporcion"]):
    ejes[1].annotate(f"{delta:.3f}", (position, delta), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)
ejes[1].set_xticks(positions)
ejes[1].set_xticklabels([etiqueta_dataset(name) for name in target_summary["dataset"]], rotation=15, ha="right")
ejes[1].set_ylabel("Máx. |delta proporción|")
ejes[1].set_title("Cambio crudo vs procesado", loc="left", fontweight="bold")

for eje in ejes:
    aplicar_estilo_eje(eje, eje_rejilla="y")
fijar_titulo_narrativo(figura, "El target se conserva; Olive Oil concentra el desbalance final")
cerrar_figura_narrativa(figura, "fase3_target_desbalance.png")
"""))
    cells.append(md("""
Lectura de la figura comparativa: el máximo cambio de proporción es 0.000000 en los 4 datasets, mientras `olive_oil` alcanza el mayor desbalance con ratio 8.24. La figura separa conservación del target y dificultad de estratificación.
"""))

    cells.append(md("""
## 3.5 Comparación Distribucional de Variables Numéricas

Se comparan variables numéricas que pueden emparejarse entre raw y processed tras el renombrado. El objetivo es comprobar que el preprocesado estructural no ha introducido cambios inesperados de mediana o dispersión.

Las métricas miran el mismo fenómeno desde ángulos distintos:

- KS mide la máxima distancia entre distribuciones acumuladas. Es sensible a cambios globales de forma.
- Wasserstein mide cuánto habría que desplazar una distribución para parecerse a la otra. Es útil cuando la escala de la variable importa.
- PSI resume desplazamiento por bins; valores cercanos a cero indican estabilidad práctica entre raw y processed.
- JS divergence compara histogramas normalizados de forma simétrica y acotada.
- Spearman raw-processed evalúa si el orden relativo de las filas se conserva tras el preprocesado.

En `breast_cancer_wisconsin`, `madelon` y `olive_oil` se espera conservación casi exacta porque no se aplican transformaciones numéricas globales. En `customer_churn`, la lectura se restringe a numéricas comparables y deja las categóricas para el entrenamiento posterior al split.
"""))
    cells.append(code("""
def mapa_original_a_procesada(nombre_dataset):
    selected = renaming_phase2[renaming_phase2["dataset"].eq(nombre_dataset)]
    return dict(zip(selected["columna_original"], selected["columna_procesada"]))


def variables_comparables(nombre_dataset):
    rename_map = mapa_original_a_procesada(nombre_dataset)
    processed_columns = set(processed_datasets[nombre_dataset].columns)
    rows = []
    for raw_name, processed_name in rename_map.items():
        if processed_name in processed_columns and processed_name != PROCESSED_TARGET and raw_name != RAW_TARGETS[nombre_dataset]:
            rows.append((raw_name, processed_name))
    return rows
"""))
    cells.append(code("""
def calcular_iqr(serie):
    return serie.quantile(0.75) - serie.quantile(0.25)


def calcular_bordes_histograma(raw_values, processed_values, bins=10):
    quantile_edges = np.unique(np.quantile(raw_values, np.linspace(0, 1, bins + 1)))
    if len(quantile_edges) >= 3:
        return quantile_edges
    min_value = min(raw_values.min(), processed_values.min())
    max_value = max(raw_values.max(), processed_values.max())
    if min_value == max_value:
        return None
    return np.linspace(min_value, max_value, min(bins + 1, raw_values.nunique() + 1))


def normalizar_histograma(histogram):
    epsilon = 1e-8
    proportions = histogram / max(histogram.sum(), 1)
    proportions = np.clip(proportions, epsilon, None)
    return proportions / proportions.sum()


def calcular_histogramas_comparables(raw_values, processed_values, bins=10):
    raw_values = pd.Series(raw_values).dropna()
    processed_values = pd.Series(processed_values).dropna()
    if raw_values.empty or processed_values.empty:
        return None, None
    edges = calcular_bordes_histograma(raw_values, processed_values, bins)
    if edges is None:
        return None, None
    raw_hist, _ = np.histogram(raw_values, bins=edges)
    processed_hist, _ = np.histogram(processed_values, bins=edges)
    return normalizar_histograma(raw_hist), normalizar_histograma(processed_hist)
"""))
    cells.append(code("""
def calcular_psi(raw_values, processed_values):
    raw_prop, processed_prop = calcular_histogramas_comparables(raw_values, processed_values)
    if raw_prop is None:
        return np.nan
    return float(np.sum((processed_prop - raw_prop) * np.log(processed_prop / raw_prop)))


def calcular_js_divergence(raw_values, processed_values):
    raw_prop, processed_prop = calcular_histogramas_comparables(raw_values, processed_values)
    if raw_prop is None:
        return np.nan
    midpoint = 0.5 * (raw_prop + processed_prop)
    return float(0.5 * np.sum(raw_prop * np.log2(raw_prop / midpoint)) + 0.5 * np.sum(processed_prop * np.log2(processed_prop / midpoint)))
"""))
    cells.append(code("""
def calcular_spearman_pareado(raw_series, processed_series):
    paired = pd.DataFrame({"raw": pd.to_numeric(raw_series, errors="coerce"), "processed": pd.to_numeric(processed_series, errors="coerce")}).dropna()
    if len(paired) < 3 or paired["raw"].nunique() < 2 or paired["processed"].nunique() < 2:
        return np.nan
    return float(spearmanr(paired["raw"], paired["processed"]).statistic)


def convertir_a_numerica_limpia(serie):
    return pd.to_numeric(serie, errors="coerce").dropna()


def metricas_centro_dispersion(raw_values, processed_values):
    raw_iqr = calcular_iqr(raw_values)
    processed_iqr = calcular_iqr(processed_values)
    return {
        "mediana_raw": float(raw_values.median()),
        "mediana_processed": float(processed_values.median()),
        "delta_mediana_abs": float(abs(raw_values.median() - processed_values.median())),
        "iqr_raw": float(raw_iqr),
        "iqr_processed": float(processed_iqr),
        "delta_iqr_abs": float(abs(raw_iqr - processed_iqr)),
    }


def metricas_tests_distribucion(raw_values, processed_values):
    ks_result = ks_2samp(raw_values, processed_values)
    return {
        "ks_statistic": float(ks_result.statistic),
        "ks_p_value": float(ks_result.pvalue),
        "wasserstein_distance": float(wasserstein_distance(raw_values, processed_values)),
        "psi": calcular_psi(raw_values, processed_values),
        "js_divergence": calcular_js_divergence(raw_values, processed_values),
    }


def max_delta_percentiles(raw_values, processed_values):
    return float(max(abs(raw_values.quantile(q) - processed_values.quantile(q)) for q in [0, 0.25, 0.5, 0.75, 1.0]))
"""))
    cells.append(code("""
def crear_fila_shift_distribucional(nombre_dataset, raw_name, processed_name):
    raw_values = convertir_a_numerica_limpia(raw_datasets[nombre_dataset][raw_name])
    processed_values = convertir_a_numerica_limpia(processed_datasets[nombre_dataset][processed_name])
    return {
        "dataset": nombre_dataset,
        "variable": processed_name,
        **metricas_centro_dispersion(raw_values, processed_values),
        **metricas_tests_distribucion(raw_values, processed_values),
        "max_delta_percentil": max_delta_percentiles(raw_values, processed_values),
        "spearman_raw_processed": calcular_spearman_pareado(
            raw_datasets[nombre_dataset][raw_name],
            processed_datasets[nombre_dataset][processed_name],
        ),
    }
"""))
    cells.append(code("""
def crear_filas_percentiles(nombre_dataset, raw_name, processed_name):
    raw_values = pd.to_numeric(raw_datasets[nombre_dataset][raw_name], errors="coerce").dropna()
    processed_values = pd.to_numeric(processed_datasets[nombre_dataset][processed_name], errors="coerce").dropna()
    if raw_values.empty or processed_values.empty:
        return []
    return [{"dataset": nombre_dataset, "variable": processed_name, "percentil": q, "valor_raw": raw_values.quantile(q), "valor_processed": processed_values.quantile(q), "delta_abs": abs(raw_values.quantile(q) - processed_values.quantile(q))} for q in [0, 0.25, 0.5, 0.75, 1.0]]


def resumir_shift_distribucional(nombre_dataset):
    rows = []
    for raw_name, processed_name in variables_comparables(nombre_dataset):
        raw_series = raw_datasets[nombre_dataset][raw_name]
        processed_series = processed_datasets[nombre_dataset][processed_name]
        if pd.api.types.is_numeric_dtype(raw_series) and pd.api.types.is_numeric_dtype(processed_series):
            rows.append(crear_fila_shift_distribucional(nombre_dataset, raw_name, processed_name))
    return pd.DataFrame(rows)


def resumir_percentiles_comparables(nombre_dataset):
    rows = []
    for raw_name, processed_name in variables_comparables(nombre_dataset):
        rows.extend(crear_filas_percentiles(nombre_dataset, raw_name, processed_name))
    return pd.DataFrame(rows)
"""))
    cells.append(code("""
def limites_diagonal(tabla, columna_raw, columna_processed):
    minimo = min(tabla[columna_raw].min(), tabla[columna_processed].min())
    maximo = max(tabla[columna_raw].max(), tabla[columna_processed].max())
    return [minimo, maximo]


def dibujar_diagonal_conservacion(eje, tabla, columna_raw, columna_processed, color):
    eje.scatter(tabla[columna_raw], tabla[columna_processed], s=34, color=color, alpha=0.78)
    limites = limites_diagonal(tabla, columna_raw, columna_processed)
    eje.plot(limites, limites, color="#2D2A26", linewidth=1.0)


def titular_panel_conservacion(eje, xlabel, ylabel, titulo):
    eje.set_xlabel(xlabel)
    eje.set_ylabel(ylabel)
    eje.set_title(titulo, loc="left", fontweight="bold")
    aplicar_estilo_eje(eje, eje_rejilla="both")
"""))
    cells.append(code("""
def mensaje_distribucional(distribution_shift_dataset, nombre_dataset):
    score_maximo = distribution_shift_dataset["score_shift"].max()
    if score_maximo < 1e-12:
        return f"{etiqueta_dataset(nombre_dataset)} conserva mediana e IQR en variables comparables"
    return f"{etiqueta_dataset(nombre_dataset)} muestra desplazamiento distribucional a revisar"


def dibujar_top_shift_distribucional(eje, distribution_shift_dataset, nombre_dataset):
    top_shift = distribution_shift_dataset.sort_values("score_shift", ascending=False).head(8).sort_values("score_shift")
    bar_color = color_dataset(nombre_dataset)
    eje.barh(top_shift["variable"], top_shift["score_shift"], color=bar_color)
    eje.set_xlabel("KS + PSI + JS")
    eje.set_title("Variables con mayor shift", loc="left", fontweight="bold")
    aplicar_estilo_eje(eje, eje_rejilla="x")


def graficar_conservacion_distribucional_dataset(distribution_shift_dataset, nombre_dataset):
    if distribution_shift_dataset.empty:
        return
    figura, ejes = plt.subplots(1, 3, figsize=(13.4, 4.4), width_ratios=[1.0, 1.0, 1.2])
    color = color_dataset(nombre_dataset)
    dibujar_diagonal_conservacion(ejes[0], distribution_shift_dataset, "mediana_raw", "mediana_processed", color)
    dibujar_diagonal_conservacion(ejes[1], distribution_shift_dataset, "iqr_raw", "iqr_processed", color)
    dibujar_top_shift_distribucional(ejes[2], distribution_shift_dataset, nombre_dataset)
    titular_panel_conservacion(ejes[0], "Mediana raw", "Mediana processed", "Medianas")
    titular_panel_conservacion(ejes[1], "IQR raw", "IQR processed", "Dispersión")
    fijar_titulo_narrativo(figura, mensaje_distribucional(distribution_shift_dataset, nombre_dataset))
    cerrar_figura_narrativa(figura, f"fase3_distribucion_conservacion_{nombre_dataset}.png")
"""))

    distribution_observations = {
        "breast_cancer_wisconsin": "Observación: en 30 variables comparables, KS llega a 0.000000, PSI queda en 0.000000 y Spearman mínimo=1.000000; mediana e IQR se conservan.",
        "customer_churn": "Observación: las 7 numéricas comparables dan KS=0.000000 y PSI=0.000000; las 3 categóricas se revisan aparte.",
        "madelon": "Observación: sus 500 variables mantienen KS máximo en 0.000000, PSI en 0.000000 y Spearman mínimo=1.000000; no aparece transformación global.",
        "olive_oil": "Observación: las 10 variables composicionales muestran KS=0.000000 y Wasserstein=0.000000; no hay escalado ni winsorización global.",
    }
    add_dataset_cells(
        cells,
        "Distribuciones Comparables",
        """
distribution_shift___VARIABLE__ = resumir_shift_distribucional("__DATASET__")
if not distribution_shift___VARIABLE__.empty:
    distribution_shift___VARIABLE__["score_shift"] = (
        distribution_shift___VARIABLE__["ks_statistic"].fillna(0)
        + distribution_shift___VARIABLE__["psi"].fillna(0)
        + distribution_shift___VARIABLE__["js_divergence"].fillna(0)
    )
percentiles___VARIABLE__ = resumir_percentiles_comparables("__DATASET__")

mostrar_tabla(distribution_shift___VARIABLE__.sort_values("score_shift", ascending=False), "Tests de conservación distribucional - __LABEL__", n=12)
mostrar_tabla(percentiles___VARIABLE__, "Percentiles crudos vs procesados - __LABEL__", n=12)
graficar_conservacion_distribucional_dataset(distribution_shift___VARIABLE__, "__DATASET__")
""",
        distribution_observations,
    )
    cells.append(md("### Resumen Comparativo de Distribuciones"))
    cells.append(code("""
distribution_shift = pd.concat([
    distribution_shift_breast_cancer_wisconsin,
    distribution_shift_customer_churn,
    distribution_shift_madelon,
    distribution_shift_olive_oil,
], ignore_index=True)

distribution_shift["score_shift"] = (
    distribution_shift["ks_statistic"].fillna(0)
    + distribution_shift["psi"].fillna(0)
    + distribution_shift["js_divergence"].fillna(0)
)

percentiles_comparables = pd.concat([
    percentiles_breast_cancer_wisconsin,
    percentiles_customer_churn,
    percentiles_madelon,
    percentiles_olive_oil,
], ignore_index=True)

guardar_tabla(distribution_shift, "fase3_shift_distribucional.csv")
guardar_tabla(percentiles_comparables, "fase3_percentiles_comparables.csv")
distribution_tests_summary = distribution_shift.groupby("dataset", as_index=False).agg(
    variables=("variable", "count"),
    ks_maximo=("ks_statistic", "max"),
    wasserstein_maximo=("wasserstein_distance", "max"),
    psi_maximo=("psi", "max"),
    js_maximo=("js_divergence", "max"),
    max_delta_percentil=("max_delta_percentil", "max"),
    spearman_minimo=("spearman_raw_processed", "min"),
    score_shift_maximo=("score_shift", "max"),
)
guardar_tabla(distribution_tests_summary, "fase3_shift_distribucional_resumen.csv")
mostrar_tabla(distribution_tests_summary, "Resumen de tests distribucionales")

def resumen_distribucional_markdown(distribution_summary):
    lines = ["**Lectura de resultados distribucionales.**"]
    for _, row in distribution_summary.iterrows():
        lines.append(
            f"- `{row['dataset']}`: KS máximo={row['ks_maximo']:.6f}, "
            f"Wasserstein máximo={row['wasserstein_maximo']:.6f}, PSI máximo={row['psi_maximo']:.6f}, "
            f"Spearman pareado mínimo={row['spearman_minimo']:.6f}. "
            "La combinación de valores nulos o mínimos indica conservación de variables comparables tras renombrado/codificación estructural."
        )
    lines.append(
        "Implicación: si en Fase 4 aparece drift entre splits, deberá atribuirse al particionado o al tamaño muestral, "
        "no a una transformación numérica global introducida en Fase 2/3."
    )
    return "\\n".join(lines)


display(Markdown(resumen_distribucional_markdown(distribution_tests_summary)))
"""))

    cells.append(md("""
## 3.6 Encoding Pendiente, Rangos y Escalado Posterior

Se revisan variables categóricas pendientes y rangos numéricos finales. Esta fase no ajusta encoders ni escaladores: solo comprueba qué deberá manejar el entrenamiento posterior al split.

El encoding pendiente se trata como una condición heredable, no como una incidencia del dataset procesado: `customer_churn` conserva categóricas para que el encoder se ajuste con entrenamiento y se aplique después a validación/prueba. El resto de datasets queda numérico.

Los rangos se leen con el criterio de heterogeneidad de escala para modelos sensibles a magnitud. No implican escalado global aquí; el escalado, si se necesita, debe formar parte del entrenamiento posterior al split.
"""))
    cells.append(code("""
def crear_fila_rango_processed(nombre_dataset, serie):
    return {
        "dataset": nombre_dataset,
        "variable": serie.name,
        "minimo": float(serie.min()),
        "maximo": float(serie.max()),
        "rango": float(serie.max() - serie.min()),
        "mediana": float(serie.median()),
        "iqr": float(calcular_iqr(serie)),
    }


def resumir_rangos_processed(nombre_dataset, datos_processed):
    rows = []
    for variable_name in datos_processed.columns:
        if variable_name != PROCESSED_TARGET and pd.api.types.is_numeric_dtype(datos_processed[variable_name]):
            rows.append(crear_fila_rango_processed(nombre_dataset, datos_processed[variable_name]))
    return pd.DataFrame(rows)
"""))
    scaling_observations = {
        "breast_cancer_wisconsin": "Observación: mantiene 30 variables numéricas y 0 categóricas; los rangos heterogéneos deberán escalarse solo dentro del entrenamiento.",
        "customer_churn": "Observación: combina 7 numéricas y 3 categóricas pendientes; la siguiente fase necesita tratamiento mixto sin fuga de información.",
        "madelon": "Observación: sus 500 variables son numéricas; la prioridad posterior será controlar dimensionalidad y validación, no codificación.",
        "olive_oil": "Observación: queda con 10 variables numéricas y 9 clases; la estratificación y el escalado posterior importan más que nuevos encoders.",
    }
    add_dataset_cells(
        cells,
        "Encoding y Rangos Finales",
        """
ranges_processed___VARIABLE__ = resumir_rangos_processed("__DATASET__", processed___VARIABLE__)

mostrar_estado_categoricas_pendientes(pending_categories___VARIABLE__, "__DATASET__")
mostrar_tabla(ranges_processed___VARIABLE__.sort_values("rango", ascending=False), "Rangos procesados - __LABEL__", n=12)
""",
        scaling_observations,
    )
    cells.append(md("### Resumen Comparativo de Encoding y Rangos"))
    cells.append(code("""
ranges_processed = pd.concat([
    ranges_processed_breast_cancer_wisconsin,
    ranges_processed_customer_churn,
    ranges_processed_madelon,
    ranges_processed_olive_oil,
], ignore_index=True)

encoding_summary = encoding_dimensionality_phase2.copy()

def resumen_encoding_pendiente_markdown(encoding_table):
    lines = ["**Encoding pendiente heredado de Fase 2.**"]
    for _, row in encoding_table.iterrows():
        dataset_label = etiqueta_dataset(row["dataset"])
        categorical = int(row["predictoras_categoricas"])
        if categorical == 0:
            lines.append(f"- `{row['dataset']}`: no mantiene predictoras categóricas pendientes; no hay encoder que ajustar para variables categóricas.")
        else:
            lines.append(
                f"- `{row['dataset']}`: mantiene {categorical} predictoras categóricas. "
                f"Si se codificaran con one-hot, el espacio pasaría de {int(row['predictoras_sin_onehot'])} a {int(row['predictoras_si_onehot'])} predictoras. "
                "Esta cifra es una estimación para diseñar el entrenamiento posterior, no una transformación aplicada en Fase 3."
            )
    lines.append(
        "La tabla fuente sigue siendo `results/tables/02_preprocessing/fase2_dimensionalidad_encoding.csv`; "
        "Fase 3 no la duplica como resultado propio porque aquí no se ajusta ningún encoder."
    )
    return "\\n".join(lines)


guardar_tabla(ranges_processed, "fase3_rangos_processed.csv")
display(Markdown(resumen_encoding_pendiente_markdown(encoding_summary)))

def resumen_rangos_markdown(ranges_table):
    summary = ranges_table.groupby("dataset", as_index=False).agg(
        rango_maximo=("rango", "max"),
        rango_mediano=("rango", "median"),
        iqr_mediano=("iqr", "median"),
        variables=("variable", "count"),
    )
    lines = ["**Lectura de rangos y escalado posterior.**"]
    for _, row in summary.iterrows():
        lines.append(
            f"- `{row['dataset']}`: {int(row['variables'])} numéricas, rango máximo={row['rango_maximo']:.3f}, "
            f"rango mediano={row['rango_mediano']:.3f}, IQR mediano={row['iqr_mediano']:.3f}. "
            "Estos rangos justifican escalar dentro del entrenamiento cuando el modelo sea sensible a magnitud."
        )
    lines.append("No se ajusta ningún escalador aquí para evitar fuga de información antes del split.")
    return "\\n".join(lines)


display(Markdown(resumen_rangos_markdown(ranges_processed)))
"""))

    cells.append(md("""
## 3.7 Conservación Exploratoria de Relación Variable-Target

Se calcula asociación exploratoria entre variables numéricas y target antes y después del preprocesado. Se usa Spearman absoluto y mutual information como diagnóstico de conservación de señal; no se seleccionan variables en esta fase.

Este bloque es la garantía previa para el término de relevancia que consumirá QFS: en `PAPER_QFS.pdf`, `I(x_i;y)` define pesos locales del Hamiltoniano, de modo que un preprocesado que cambiara artificialmente los rankings de mutual information alteraría los detunings locales antes de comparar contra métodos clásicos. Por eso se leen cambios de score, solapamiento top-k y correlación de rankings, no solo valores aislados.

Lectura de las métricas:

- Spearman absoluto mide relación monótona entre variable y target codificado. Es robusto a escalas distintas y ayuda a comparar raw codificado contra processed.
- El p-value de Spearman se ajusta con Benjamini-Hochberg para controlar FDR cuando se evalúan muchas variables simultáneamente. Un q-value bajo indica señal estadística exploratoria, no una decisión de selección.
- Mutual information detecta dependencia no necesariamente lineal entre predictor y target. Se combina con Spearman en un score descriptivo para ordenar variables.
- El cambio de ranking y el solapamiento top-k indican si el preprocesado ha reordenado artificialmente las variables con mayor señal.

En `customer_churn` solo entran las numéricas porque las categóricas siguen sin codificar. En `madelon`, la lectura se centra en estabilidad de señal bajo alta dimensionalidad. En `olive_oil`, el target multiclase permite medir dependencia, pero la selección queda fuera de esta fase.
"""))
    cells.append(code("""
def preparar_matriz_asociacion(datos_dataset, target_name):
    numeric_features = [name for name in datos_dataset.columns if name != target_name and pd.api.types.is_numeric_dtype(datos_dataset[name])]
    if not numeric_features:
        return pd.DataFrame(), pd.Series(dtype=int)
    sampled = datos_dataset[numeric_features + [target_name]].dropna()
    if len(sampled) > MAX_SAMPLE_ASSOCIATION:
        sampled = sampled.sample(MAX_SAMPLE_ASSOCIATION, random_state=RANDOM_STATE)
    predictors = sampled[numeric_features].replace([np.inf, -np.inf], np.nan)
    predictors = predictors.fillna(predictors.median(numeric_only=True))
    target = LabelEncoder().fit_transform(sampled[target_name].astype(str))
    return predictors, pd.Series(target, index=predictors.index)
"""))
    cells.append(code("""
def ajustar_fdr_bh(p_values):
    p_values = np.asarray(p_values, dtype=float)
    q_values = np.full_like(p_values, np.nan, dtype=float)
    valid_mask = ~np.isnan(p_values)
    valid_p = p_values[valid_mask]
    if len(valid_p) == 0:
        return q_values
    order = np.argsort(valid_p)
    positions = np.arange(1, len(valid_p) + 1)
    adjusted = valid_p[order] * len(valid_p) / positions
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    valid_indices = np.where(valid_mask)[0]
    q_values[valid_indices[order]] = np.clip(adjusted, 0, 1)
    return q_values


def crear_fila_asociacion(nombre_dataset, variable_name, metricas_asociacion):
    spearman_value = metricas_asociacion["spearman"]
    spearman_clean = 0.0 if np.isnan(spearman_value) else float(abs(spearman_value))
    mi_clean = 0.0 if np.isnan(metricas_asociacion["mi"]) else float(metricas_asociacion["mi"])
    p_value = metricas_asociacion["p_value"]
    return {
        "dataset": nombre_dataset,
        "variable": variable_name,
        "spearman_abs": spearman_clean,
        "spearman_p_value": float(p_value) if pd.notna(p_value) else np.nan,
        "mutual_info": mi_clean,
        "score_asociacion": (spearman_clean + mi_clean) / 2,
        "n_usado": metricas_asociacion["n"],
    }


def columnas_asociacion_vacia():
    return [
        "dataset", "variable", "spearman_abs", "spearman_p_value",
        "spearman_q_value_bh", "fdr_significativo_005", "mutual_info",
        "score_asociacion", "ranking", "n_usado",
    ]


def calcular_spearman_con_target(predictors, target, variable_name):
    if predictors[variable_name].nunique(dropna=True) < 2:
        return np.nan, np.nan
    spearman_result = spearmanr(predictors[variable_name], target)
    return spearman_result.statistic, spearman_result.pvalue


def anotar_ranking_y_fdr(tabla_asociacion):
    tabla = tabla_asociacion.sort_values("score_asociacion", ascending=False).reset_index(drop=True)
    tabla["spearman_q_value_bh"] = ajustar_fdr_bh(tabla["spearman_p_value"])
    tabla["fdr_significativo_005"] = tabla["spearman_q_value_bh"] <= 0.05
    tabla["ranking"] = np.arange(1, len(tabla) + 1)
    return tabla
"""))
    cells.append(code("""
def calcular_asociacion_numerica(nombre_dataset, datos_dataset, target_name):
    predictors, target = preparar_matriz_asociacion(datos_dataset, target_name)
    if predictors.empty:
        return pd.DataFrame(columns=columnas_asociacion_vacia())
    rows = []
    mutual_information = mutual_info_classif(predictors, target, random_state=RANDOM_STATE)
    for variable_name, mi_score in zip(predictors.columns, mutual_information):
        spearman_value, p_value = calcular_spearman_con_target(predictors, target, variable_name)
        rows.append(crear_fila_asociacion(nombre_dataset, variable_name, {"spearman": spearman_value, "p_value": p_value, "mi": mi_score, "n": len(predictors)}))
    return anotar_ranking_y_fdr(pd.DataFrame(rows))
"""))
    cells.append(code("""
def crear_dataset_raw_codificado(nombre_dataset):
    raw_dataset = raw_datasets[nombre_dataset].rename(columns=mapa_original_a_procesada(nombre_dataset)).copy()
    raw_dataset[PROCESSED_TARGET] = codificar_target_raw(nombre_dataset)
    return raw_dataset


def resumir_shift_asociacion(nombre_dataset):
    raw_assoc = calcular_asociacion_numerica(nombre_dataset, crear_dataset_raw_codificado(nombre_dataset), PROCESSED_TARGET)
    processed_assoc = calcular_asociacion_numerica(nombre_dataset, processed_datasets[nombre_dataset], PROCESSED_TARGET)
    return raw_assoc, processed_assoc, combinar_asociaciones(raw_assoc, processed_assoc, nombre_dataset)
"""))
    cells.append(code("""
def columnas_shift_asociacion():
    return ["dataset", "variable", "score_raw", "score_processed", "delta_abs", "spearman_raw", "spearman_processed", "delta_spearman_abs", "mutual_info_raw", "mutual_info_processed", "delta_mi_abs", "ranking_raw", "ranking_processed", "delta_ranking"]


def leer_metricas_asociacion(mapa_asociacion, variable_name):
    return {
        "score": mapa_asociacion.loc[variable_name, "score_asociacion"],
        "spearman": mapa_asociacion.loc[variable_name, "spearman_abs"],
        "mi": mapa_asociacion.loc[variable_name, "mutual_info"],
        "ranking": int(mapa_asociacion.loc[variable_name, "ranking"]),
    }


def comparar_metricas_asociacion(raw_metrics, processed_metrics):
    return {
        "score_raw": raw_metrics["score"],
        "score_processed": processed_metrics["score"],
        "delta_abs": abs(processed_metrics["score"] - raw_metrics["score"]),
        "spearman_raw": raw_metrics["spearman"],
        "spearman_processed": processed_metrics["spearman"],
        "delta_spearman_abs": abs(processed_metrics["spearman"] - raw_metrics["spearman"]),
        "mutual_info_raw": raw_metrics["mi"],
        "mutual_info_processed": processed_metrics["mi"],
        "delta_mi_abs": abs(processed_metrics["mi"] - raw_metrics["mi"]),
        "ranking_raw": raw_metrics["ranking"],
        "ranking_processed": processed_metrics["ranking"],
        "delta_ranking": processed_metrics["ranking"] - raw_metrics["ranking"],
    }
"""))
    cells.append(code("""
def crear_fila_shift_asociacion(nombre_dataset, variable_name, mapas_asociacion):
    raw_metrics = leer_metricas_asociacion(mapas_asociacion["raw"], variable_name)
    processed_metrics = leer_metricas_asociacion(mapas_asociacion["processed"], variable_name)
    return {
        "dataset": nombre_dataset,
        "variable": variable_name,
        **comparar_metricas_asociacion(raw_metrics, processed_metrics),
    }


def combinar_asociaciones(raw_assoc, processed_assoc, nombre_dataset):
    raw_map = raw_assoc.set_index("variable")
    processed_map = processed_assoc.set_index("variable")
    common_variables = sorted(set(raw_map.index) & set(processed_map.index))
    rows = []
    mapas_asociacion = {"raw": raw_map, "processed": processed_map}
    for variable_name in common_variables:
        rows.append(crear_fila_shift_asociacion(nombre_dataset, variable_name, mapas_asociacion))
    return pd.DataFrame(rows, columns=columnas_shift_asociacion())
"""))
    cells.append(code("""
def fila_asociacion_sin_variables(nombre_dataset):
    return {
        "dataset": nombre_dataset,
        "variables_comunes": 0,
        "spearman_rankings_raw_processed": np.nan,
        "mi_spearman_raw_processed": np.nan,
        "delta_mi_medio": np.nan,
        "fdr_significativas_005": 0,
        "proporcion_fdr_significativas_005": np.nan,
        "efecto_post_maximo_spearman": np.nan,
        "efecto_post_mediano_spearman": np.nan,
        "top_k": 0,
        "top_k_overlap": 0,
        "top_k_overlap_ratio": np.nan,
    }
"""))
    cells.append(code("""
def calcular_overlap_top_k(raw_assoc, processed_assoc, association_shift_dataset, top_k):
    k = min(top_k, len(association_shift_dataset))
    raw_top = set(raw_assoc.sort_values("ranking").head(k)["variable"])
    processed_top = set(processed_assoc.sort_values("ranking").head(k)["variable"])
    return k, len(raw_top & processed_top)


def resumir_fdr_processed(processed_assoc):
    fdr_count = int(processed_assoc["fdr_significativo_005"].sum()) if "fdr_significativo_005" in processed_assoc else 0
    return fdr_count, fdr_count / max(len(processed_assoc), 1)


def resumir_efecto_processed(processed_assoc):
    if processed_assoc.empty:
        return np.nan, np.nan
    return float(processed_assoc["spearman_abs"].max()), float(processed_assoc["spearman_abs"].median())
"""))
    cells.append(code("""
def metricas_overlap_top_k(k, overlap):
    return {
        "top_k": k,
        "top_k_overlap": overlap,
        "top_k_overlap_ratio": overlap / max(k, 1),
    }
"""))
    cells.append(code("""
def metricas_rankings_asociacion(association_shift_dataset, ranking_corr, mi_corr):
    return {
        "spearman_rankings_raw_processed": float(ranking_corr) if pd.notna(ranking_corr) else np.nan,
        "mi_spearman_raw_processed": float(mi_corr) if pd.notna(mi_corr) else np.nan,
        "delta_mi_medio": float(association_shift_dataset["delta_mi_abs"].mean()),
    }


def metricas_fdr_y_efecto(fdr_metrics, effect_metrics):
    fdr_count, fdr_ratio = fdr_metrics
    efecto_maximo, efecto_mediano = effect_metrics
    return {
        "fdr_significativas_005": fdr_count,
        "proporcion_fdr_significativas_005": fdr_ratio,
        "efecto_post_maximo_spearman": efecto_maximo,
        "efecto_post_mediano_spearman": efecto_mediano,
    }


def crear_fila_conservacion_asociacion(nombre_dataset, association_shift_dataset, ranking_corr, mi_corr, top_metrics, fdr_metrics, effect_metrics):
    k, overlap = top_metrics
    return {
        "dataset": nombre_dataset,
        "variables_comunes": len(association_shift_dataset),
        **metricas_rankings_asociacion(association_shift_dataset, ranking_corr, mi_corr),
        **metricas_fdr_y_efecto(fdr_metrics, effect_metrics),
        **metricas_overlap_top_k(k, overlap),
    }


def evaluar_conservacion_asociacion(nombre_dataset, raw_assoc, processed_assoc, association_shift_dataset, top_k=10):
    if association_shift_dataset.empty:
        return fila_asociacion_sin_variables(nombre_dataset)
    ranking_corr = spearmanr(association_shift_dataset["ranking_raw"], association_shift_dataset["ranking_processed"]).statistic
    mi_corr = spearmanr(association_shift_dataset["mutual_info_raw"], association_shift_dataset["mutual_info_processed"]).statistic
    top_metrics = calcular_overlap_top_k(raw_assoc, processed_assoc, association_shift_dataset, top_k)
    fdr_metrics = resumir_fdr_processed(processed_assoc)
    effect_metrics = resumir_efecto_processed(processed_assoc)
    return crear_fila_conservacion_asociacion(nombre_dataset, association_shift_dataset, ranking_corr, mi_corr, top_metrics, fdr_metrics, effect_metrics)
"""))
    cells.append(code("""
def dibujar_top_asociacion(eje, processed_assoc, nombre_dataset):
    top_processed = processed_assoc.sort_values("score_asociacion", ascending=False).head(10).sort_values("score_asociacion")
    eje.barh(top_processed["variable"], top_processed["score_asociacion"], color=color_dataset(nombre_dataset))
    eje.set_xlabel("Score asociación")
    eje.set_title("Señal final más alta", loc="left", fontweight="bold")
    aplicar_estilo_eje(eje, eje_rejilla="x")


def dibujar_conservacion_asociacion(eje, association_shift_dataset, nombre_dataset):
    if association_shift_dataset.empty:
        eje.axis("off")
        eje.text(0.02, 0.55, "Sin variables numéricas comunes", fontsize=11, color="#2D2A26")
        return
    dibujar_diagonal_conservacion(eje, association_shift_dataset, "score_raw", "score_processed", color_dataset(nombre_dataset))
    titular_panel_conservacion(eje, "Score raw codificado", "Score processed", "Conservación de señal")


def mensaje_asociacion(association_shift_dataset, nombre_dataset):
    if association_shift_dataset.empty:
        return f"{etiqueta_dataset(nombre_dataset)} no tiene señal numérica común comparable"
    ranking_corr = spearmanr(association_shift_dataset["ranking_raw"], association_shift_dataset["ranking_processed"]).statistic
    return f"{etiqueta_dataset(nombre_dataset)} conserva el ranking de señal (Spearman={ranking_corr:.2f})"
"""))
    cells.append(code("""
def graficar_asociacion_dataset(processed_assoc, association_shift_dataset, nombre_dataset):
    figura, ejes = plt.subplots(1, 2, figsize=(11.4, 4.6), width_ratios=[1.15, 1.0])
    dibujar_top_asociacion(ejes[0], processed_assoc, nombre_dataset)
    dibujar_conservacion_asociacion(ejes[1], association_shift_dataset, nombre_dataset)
    fijar_titulo_narrativo(figura, mensaje_asociacion(association_shift_dataset, nombre_dataset))
    cerrar_figura_narrativa(figura, f"fase3_asociacion_{nombre_dataset}.png")
"""))

    association_observations = {
        "breast_cancer_wisconsin": "Observación: se comparan 30 variables comunes, con top-k 10/10 y 27 señales FDR<=0.05; no se seleccionan features aquí.",
        "customer_churn": "Observación: se comparan 7 numéricas, con top-k 6/7 y 7 señales FDR<=0.05; las categóricas esperan al entrenamiento posterior.",
        "madelon": "Observación: se comparan 500 variables, con top-k 10/10 y 13 señales FDR<=0.05; la señal se audita bajo alta dimensionalidad.",
        "olive_oil": "Observación: se comparan 10 variables, con top-k 9/10 y 6 señales FDR<=0.05; la selección queda para la fase correspondiente.",
    }
    add_dataset_cells(
        cells,
        "Asociación Variable-Target",
        """
raw_assoc___VARIABLE__, processed_assoc___VARIABLE__, association_shift___VARIABLE__ = resumir_shift_asociacion("__DATASET__")
association_tests___VARIABLE__ = pd.DataFrame([
    evaluar_conservacion_asociacion("__DATASET__", raw_assoc___VARIABLE__, processed_assoc___VARIABLE__, association_shift___VARIABLE__)
])

mostrar_tabla(processed_assoc___VARIABLE__, "Asociación procesada - __LABEL__", n=12)
mostrar_tabla(association_tests___VARIABLE__, "Tests de conservación de señal - __LABEL__")
mostrar_tabla(association_shift___VARIABLE__.sort_values("delta_abs", ascending=False), "Shift de asociación - __LABEL__", n=12)
graficar_asociacion_dataset(processed_assoc___VARIABLE__, association_shift___VARIABLE__, "__DATASET__")
""",
        association_observations,
    )
    cells.append(md("### Resumen Comparativo de Asociación"))
    cells.append(code("""
processed_association = pd.concat([
    processed_assoc_breast_cancer_wisconsin,
    processed_assoc_customer_churn,
    processed_assoc_madelon,
    processed_assoc_olive_oil,
], ignore_index=True)

association_shift = pd.concat([
    association_shift_breast_cancer_wisconsin,
    association_shift_customer_churn,
    association_shift_madelon,
    association_shift_olive_oil,
], ignore_index=True)

association_tests = pd.concat([
    association_tests_breast_cancer_wisconsin,
    association_tests_customer_churn,
    association_tests_madelon,
    association_tests_olive_oil,
], ignore_index=True)

guardar_tabla(processed_association, "fase3_asociacion_processed.csv")
guardar_tabla(association_shift, "fase3_asociacion_shift.csv")
guardar_tabla(association_tests, "fase3_asociacion_tests.csv")
mostrar_tabla(association_tests, "Resumen de conservación de asociación")
mostrar_tabla(association_shift.sort_values("delta_abs", ascending=False), "Mayores cambios de asociación", n=20)

def resumen_asociacion_markdown(association_summary):
    lines = ["**Lectura de resultados de asociación variable-target.**"]
    for _, row in association_summary.iterrows():
        ranking = row["spearman_rankings_raw_processed"]
        ranking_text = "no calculable" if pd.isna(ranking) else f"{ranking:.3f}"
        lines.append(
            f"- `{row['dataset']}`: variables comunes={int(row['variables_comunes'])}, "
            f"correlación de rankings raw/processed={ranking_text}, "
            f"top-k overlap={int(row['top_k_overlap'])}/{int(row['top_k'])}, "
            f"FDR significativas={int(row['fdr_significativas_005'])}. "
            "Esto evalúa conservación de señal, no selección de variables."
        )
    lines.append(
        "Implicación: Fase 5 podrá usar estas señales como indicio previo, pero no como lista cerrada de features; "
        "en `madelon` especialmente importa distinguir señal real, ruido y estabilidad."
    )
    return "\\n".join(lines)


display(Markdown(resumen_asociacion_markdown(association_tests)))
"""))
    cells.append(code("""
topk_plot = association_tests.copy()
topk_plot["dataset_label"] = topk_plot["dataset"].map(etiqueta_dataset)
topk_plot["variables_perdidas_topk"] = topk_plot["top_k"] - topk_plot["top_k_overlap"]
topk_plot = topk_plot.sort_values("top_k_overlap_ratio")
figura, eje = plt.subplots(figsize=(8.8, 4.8))
bar_colors = [DATASET_COLORS[name] for name in topk_plot["dataset"]]
eje.barh(topk_plot["dataset_label"], topk_plot["top_k_overlap_ratio"], color=bar_colors)
eje.axvline(1.0, color="#2D2A26", linewidth=1.0)
for _, row in topk_plot.iterrows():
    eje.annotate(
        f"{int(row['top_k_overlap'])}/{int(row['top_k'])}",
        (row["top_k_overlap_ratio"], row["dataset_label"]),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
    )
eje.set_xlim(0, 1.08)
eje.set_xlabel("Solapamiento top-k raw/procesado")
eje.set_title("El top-k de asociación conserva las variables que alimentarán QFS", loc="left", fontweight="bold")
aplicar_estilo_eje(eje, eje_rejilla="x")
fijar_titulo_narrativo(figura, "La relevancia variable-target queda estable tras el preprocesado")
cerrar_figura_narrativa(figura, "fase3_asociacion_topk_overlap_qfs.png")

def lectura_figura_topk_asociacion(topk_table):
    peor = topk_table.sort_values("top_k_overlap_ratio").iloc[0]
    mejor = topk_table.sort_values("top_k_overlap_ratio", ascending=False).iloc[0]
    return (
        "**Lectura de la figura de solapamiento top-k.** "
        f"El peor caso es `{peor['dataset']}` con {int(peor['top_k_overlap'])}/{int(peor['top_k'])} variables compartidas "
        f"({peor['top_k_overlap_ratio']:.2f}); el mejor caso es `{mejor['dataset']}` con "
        f"{int(mejor['top_k_overlap'])}/{int(mejor['top_k'])}. "
        "Esta lectura sustituye la antigua barra raw/procesado de dimensiones porque evalúa una magnitud relevante para QFS: "
        "si el ranking de `I(x_i;y)` cambia o no después del preprocesado."
    )


display(Markdown(lectura_figura_topk_asociacion(topk_plot)))
"""))

    cells.append(md("""
## 3.8 Redundancia y Correlación Post-Preprocesado

Se revisan correlaciones Pearson y Spearman entre variables numéricas procesadas. Además se compara la matriz raw contra la processed para comprobar si el preprocesado ha cambiado la estructura de redundancia. Si quedan categóricas, se calcula Cramér's V como asociación categórica descriptiva.

Este bloque es la garantía previa para el término de redundancia que consumirá QFS: el paper codifica `I(x_i;x_j)` como proximidad/distancia entre átomos, por lo que una matriz de relaciones internas deformada desplazaría la geometría de MDS y la intensidad efectiva del bloqueo de Rydberg. Aquí se exige que raw y processed mantengan matrices comparables antes de usar cualquier selección.

Pearson captura redundancia lineal y Spearman captura redundancia monótona. El umbral `0.85` marca pares muy parecidos que pueden condicionar selección de características, estabilidad de modelos o interpretabilidad.

VIF aproxima multicolinealidad multivariante: valores altos indican que una variable puede explicarse por una combinación de otras. Aquí se documenta como carga estructural del dataset, no como filtro automático.

La similitud entre matrices raw y processed permite comprobar si el preprocesado cambió relaciones internas. En datasets con categóricas pendientes, Cramér's V solo describe asociación entre variables categóricas y target; no sustituye al encoding posterior.
"""))
    cells.append(code("""
def obtener_features_numericas(datos_dataset, target_name=PROCESSED_TARGET):
    return [name for name in datos_dataset.columns if name != target_name and pd.api.types.is_numeric_dtype(datos_dataset[name])]


def crear_filas_correlacion_alta(nombre_dataset, corr_matrix, metodo):
    rows = []
    columns = list(corr_matrix.columns)
    for left_position, variable_a in enumerate(columns):
        for variable_b in columns[left_position + 1:]:
            corr_value = float(corr_matrix.loc[variable_a, variable_b])
            if corr_value >= HIGH_CORRELATION_THRESHOLD:
                rows.append({"dataset": nombre_dataset, "metodo": metodo, "variable_a": variable_a, "variable_b": variable_b, "abs_correlacion": corr_value})
    return rows


def crear_tabla_correlaciones(rows):
    return pd.DataFrame(rows, columns=["dataset", "metodo", "variable_a", "variable_b", "abs_correlacion"])
"""))
    cells.append(code("""
def vectorizar_triangulo_superior(corr_matrix):
    if corr_matrix.shape[0] < 2:
        return np.array([])
    mask = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    return corr_matrix.where(mask).stack().to_numpy(dtype=float)


def variables_numericas_comparables(nombre_dataset, raw_renamed):
    comparable = []
    for raw_name, processed_name in variables_comparables(nombre_dataset):
        if (
            processed_name in raw_renamed.columns
            and processed_name in processed_datasets[nombre_dataset].columns
            and pd.api.types.is_numeric_dtype(raw_renamed[processed_name])
            and pd.api.types.is_numeric_dtype(processed_datasets[nombre_dataset][processed_name])
        ):
            comparable.append(processed_name)
    return sorted(set(comparable))


def fila_matriz_no_comparable(nombre_dataset, metodo, n_variables):
    return {
        "dataset": nombre_dataset,
        "metodo": metodo,
        "variables_comunes": n_variables,
        "pares_comunes": 0,
        "correlacion_entre_matrices": np.nan,
        "frobenius_norm_difference": np.nan,
    }


def correlacion_entre_vectores(raw_vector, processed_vector):
    if len(raw_vector) < 2 or np.std(raw_vector) == 0 or np.std(processed_vector) == 0:
        return 1.0 if np.allclose(raw_vector, processed_vector) else np.nan
    return float(np.corrcoef(raw_vector, processed_vector)[0, 1])
"""))
    cells.append(code("""
def resumir_matrices_correlacion(nombre_dataset, metodo, comparable, raw_corr, processed_corr):
    raw_vector = vectorizar_triangulo_superior(raw_corr)
    processed_vector = vectorizar_triangulo_superior(processed_corr)
    return {
        "dataset": nombre_dataset,
        "metodo": metodo,
        "variables_comunes": len(comparable),
        "pares_comunes": len(raw_vector),
        "correlacion_entre_matrices": correlacion_entre_vectores(raw_vector, processed_vector),
        "frobenius_norm_difference": float(np.linalg.norm(raw_corr.to_numpy() - processed_corr.to_numpy(), ord="fro")),
    }


def comparar_matrices_correlacion(nombre_dataset, metodo):
    raw_renamed = raw_datasets[nombre_dataset].rename(columns=mapa_original_a_procesada(nombre_dataset))
    comparable = variables_numericas_comparables(nombre_dataset, raw_renamed)
    if len(comparable) < 2:
        return fila_matriz_no_comparable(nombre_dataset, metodo, len(comparable))
    raw_corr = raw_renamed[comparable].corr(method=metodo).fillna(0)
    processed_corr = processed_datasets[nombre_dataset][comparable].corr(method=metodo).fillna(0)
    return resumir_matrices_correlacion(nombre_dataset, metodo, comparable, raw_corr, processed_corr)
"""))
    cells.append(code("""
def matriz_vif_limpia(datos_processed):
    numeric_features = obtener_features_numericas(datos_processed)
    matrix = datos_processed[numeric_features].replace([np.inf, -np.inf], np.nan)
    matrix = matrix.fillna(matrix.median(numeric_only=True))
    return matrix[[name for name in matrix.columns if matrix[name].nunique(dropna=True) > 1]]


def calcular_vif_desde_matriz(matrix):
    corr = matrix.corr(method="pearson").fillna(0)
    corr_values = corr.to_numpy(copy=True)
    np.fill_diagonal(corr_values, 1.0)
    inverse_corr = np.linalg.pinv(corr_values)
    return np.maximum(np.diag(inverse_corr), 1.0)


def calcular_vif_dataset(nombre_dataset, datos_processed):
    matrix = matriz_vif_limpia(datos_processed)
    if matrix.shape[1] < 2:
        return pd.DataFrame(columns=["dataset", "variable", "vif"])
    return pd.DataFrame({"dataset": nombre_dataset, "variable": matrix.columns, "vif": calcular_vif_desde_matriz(matrix)})


def resumir_vif_dataset(nombre_dataset, vif_dataset):
    if vif_dataset.empty:
        return {"dataset": nombre_dataset, "vif_max": np.nan, "vif_mediana": np.nan, "variables_vif_ge_10": 0}
    return {
        "dataset": nombre_dataset,
        "vif_max": float(vif_dataset["vif"].max()),
        "vif_mediana": float(vif_dataset["vif"].median()),
        "variables_vif_ge_10": int((vif_dataset["vif"] >= 10).sum()),
    }
"""))
    cells.append(code("""
def calcular_cramers_v(serie_a, serie_b):
    contingency = pd.crosstab(serie_a.astype(str), serie_b.astype(str))
    if contingency.empty or contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return np.nan
    chi2 = chi2_contingency(contingency, correction=False)[0]
    n = contingency.to_numpy().sum()
    phi2 = chi2 / n
    r, k = contingency.shape
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / max(n - 1, 1))
    rcorr = r - ((r - 1) ** 2) / max(n - 1, 1)
    kcorr = k - ((k - 1) ** 2) / max(n - 1, 1)
    denominator = min(kcorr - 1, rcorr - 1)
    if denominator <= 0:
        return np.nan
    return float(np.sqrt(phi2corr / denominator))
"""))
    cells.append(code("""
def columnas_categoricas_con_target(datos_processed):
    categorical_features = [
        name
        for name in datos_processed.columns
        if name != PROCESSED_TARGET and not pd.api.types.is_numeric_dtype(datos_processed[name])
    ]
    return categorical_features + ([PROCESSED_TARGET] if categorical_features else [])


def crear_fila_cramers_v(nombre_dataset, datos_processed, variable_a, variable_b):
    return {
        "dataset": nombre_dataset,
        "variable_a": variable_a,
        "variable_b": variable_b,
        "incluye_target": variable_a == PROCESSED_TARGET or variable_b == PROCESSED_TARGET,
        "cramers_v": calcular_cramers_v(datos_processed[variable_a], datos_processed[variable_b]),
    }


def calcular_cramers_v_dataset(nombre_dataset, datos_processed):
    rows = []
    for variable_a, variable_b in combinations(columnas_categoricas_con_target(datos_processed), 2):
        rows.append(crear_fila_cramers_v(nombre_dataset, datos_processed, variable_a, variable_b))
    return pd.DataFrame(rows, columns=["dataset", "variable_a", "variable_b", "incluye_target", "cramers_v"])
"""))
    cells.append(code("""
def preparar_matriz_correlacion(datos_processed, numeric_features):
    matrix = datos_processed[numeric_features].replace([np.inf, -np.inf], np.nan)
    return matrix.fillna(matrix.median(numeric_only=True))


def resumen_correlacion_sin_pares(nombre_dataset, n_features):
    return {
        "dataset": nombre_dataset,
        "variables_numericas": n_features,
        "pares_evaluados": 0,
        "pares_abs_pearson_ge_085": 0,
        "pares_abs_spearman_ge_085": 0,
        "abs_pearson_maxima": np.nan,
        "abs_spearman_maxima": np.nan,
        **resumir_vif_dataset(nombre_dataset, pd.DataFrame()),
    }


def comparar_matrices_pearson_spearman(nombre_dataset):
    return pd.DataFrame([
        comparar_matrices_correlacion(nombre_dataset, "pearson"),
        comparar_matrices_correlacion(nombre_dataset, "spearman"),
    ])
"""))
    cells.append(code("""
def resumir_correlacion_numerica(nombre_dataset, numeric_features, pearson_matrix, spearman_matrix, vif_dataset):
    pearson_rows = crear_filas_correlacion_alta(nombre_dataset, pearson_matrix, "pearson")
    spearman_rows = crear_filas_correlacion_alta(nombre_dataset, spearman_matrix, "spearman")
    total_pairs = int(len(numeric_features) * (len(numeric_features) - 1) / 2)
    summary = {
        "dataset": nombre_dataset,
        "variables_numericas": len(numeric_features),
        "pares_evaluados": total_pairs,
        "pares_abs_pearson_ge_085": len(pearson_rows),
        "pares_abs_spearman_ge_085": len(spearman_rows),
        "abs_pearson_maxima": float(vectorizar_triangulo_superior(pearson_matrix).max()),
        "abs_spearman_maxima": float(vectorizar_triangulo_superior(spearman_matrix).max()),
        **resumir_vif_dataset(nombre_dataset, vif_dataset),
    }
    return crear_tabla_correlaciones(pearson_rows + spearman_rows), summary


def calcular_auditoria_correlacion(nombre_dataset, datos_processed):
    numeric_features = obtener_features_numericas(datos_processed)
    if len(numeric_features) < 2:
        return crear_tabla_correlaciones([]), resumen_correlacion_sin_pares(nombre_dataset, len(numeric_features)), comparar_matrices_pearson_spearman(nombre_dataset), pd.DataFrame(columns=["dataset", "variable", "vif"]), calcular_cramers_v_dataset(nombre_dataset, datos_processed)
    processed_numeric = preparar_matriz_correlacion(datos_processed, numeric_features)
    pearson_matrix = processed_numeric.corr(method="pearson").abs().fillna(0)
    spearman_matrix = processed_numeric.corr(method="spearman").abs().fillna(0)
    vif_dataset = calcular_vif_dataset(nombre_dataset, datos_processed)
    pairs, summary = resumir_correlacion_numerica(nombre_dataset, numeric_features, pearson_matrix, spearman_matrix, vif_dataset)
    return pairs, summary, comparar_matrices_pearson_spearman(nombre_dataset), vif_dataset, calcular_cramers_v_dataset(nombre_dataset, datos_processed)
"""))
    cells.append(code("""
def dibujar_distribucion_correlaciones(eje, datos_processed, nombre_dataset):
    numeric_features = obtener_features_numericas(datos_processed)
    if len(numeric_features) < 2:
        eje.axis("off")
        eje.text(0.02, 0.55, "Sin pares numéricos", fontsize=11, color="#2D2A26")
        return
    corr_values = vectorizar_triangulo_superior(datos_processed[numeric_features].corr(method="spearman").abs().fillna(0))
    eje.hist(corr_values, bins=24, color=color_dataset(nombre_dataset), alpha=0.82)
    eje.axvline(HIGH_CORRELATION_THRESHOLD, color="#B85C5C", linewidth=1.2)
    eje.set_xlabel("|Spearman|")
    eje.set_ylabel("Pares")
    eje.set_title("Distribución de redundancia", loc="left", fontweight="bold")
    aplicar_estilo_eje(eje, eje_rejilla="y")


def dibujar_top_vif(eje, vif_dataset):
    if vif_dataset.empty:
        eje.axis("off")
        eje.text(0.02, 0.55, "VIF no calculable", fontsize=11, color="#2D2A26")
        return
    top_vif = vif_dataset.sort_values("vif", ascending=False).head(10).sort_values("vif")
    eje.barh(top_vif["variable"], top_vif["vif"], color="#D9822B")
    eje.axvline(10, color="#B85C5C", linewidth=1.2)
    eje.set_xlabel("VIF")
    eje.set_title("Multicolinealidad final", loc="left", fontweight="bold")
    aplicar_estilo_eje(eje, eje_rejilla="x")
"""))
    cells.append(code("""
def mensaje_redundancia(vif_dataset, nombre_dataset):
    if vif_dataset.empty:
        return f"{etiqueta_dataset(nombre_dataset)} no permite evaluar multicolinealidad"
    vif_max = vif_dataset["vif"].max()
    if vif_max >= 10:
        return f"{etiqueta_dataset(nombre_dataset)} mantiene multicolinealidad alta documentada"
    return f"{etiqueta_dataset(nombre_dataset)} no muestra multicolinealidad crítica"


def graficar_redundancia_dataset(datos_processed, vif_dataset, nombre_dataset):
    figura, ejes = plt.subplots(1, 2, figsize=(11.2, 4.4), width_ratios=[1.0, 1.15])
    dibujar_distribucion_correlaciones(ejes[0], datos_processed, nombre_dataset)
    dibujar_top_vif(ejes[1], vif_dataset)
    fijar_titulo_narrativo(figura, mensaje_redundancia(vif_dataset, nombre_dataset))
    cerrar_figura_narrativa(figura, f"fase3_redundancia_{nombre_dataset}.png")
"""))

    correlation_observations = {
        "breast_cancer_wisconsin": "Observación: la matriz deja 29 pares con Spearman>=0.85 y un VIF máximo de 3806.115; la redundancia morfológica se conserva.",
        "customer_churn": "Observación: el recuento de pares Spearman>=0.85 es 0 y el VIF máximo vale 1.098; no hay correlación fuerte en numéricas.",
        "madelon": "Observación: se detectan 12 pares por encima de Spearman 0.85 y VIF máximo=116.631; la selección posterior debe manejar redundancia sintética.",
        "olive_oil": "Observación: el resumen marca 2 pares Spearman>=0.85 junto a VIF máximo=325.937; las composiciones correlacionadas se documentan sin filtrado.",
    }
    add_dataset_cells(
        cells,
        "Correlación Post-Preprocesado",
        """
correlation_pairs___VARIABLE__, correlation_summary___VARIABLE__, correlation_matrix_shift___VARIABLE__, vif___VARIABLE__, categorical_assoc___VARIABLE__ = calcular_auditoria_correlacion("__DATASET__", processed___VARIABLE__)
correlation_summary___VARIABLE__ = pd.DataFrame([correlation_summary___VARIABLE__])

mostrar_tabla(correlation_summary___VARIABLE__, "Resumen correlación - __LABEL__")
mostrar_tabla(correlation_matrix_shift___VARIABLE__, "Similitud de matriz cruda vs procesada - __LABEL__")
mostrar_tabla(vif___VARIABLE__.sort_values("vif", ascending=False), "VIF procesado - __LABEL__", n=12)
mostrar_tabla(categorical_assoc___VARIABLE__.sort_values("cramers_v", ascending=False), "Cramér's V categóricas - __LABEL__", n=12)
mostrar_tabla(correlation_pairs___VARIABLE__.sort_values("abs_correlacion", ascending=False), "Pares con correlación alta - __LABEL__", n=12)
graficar_redundancia_dataset(processed___VARIABLE__, vif___VARIABLE__, "__DATASET__")
""",
        correlation_observations,
    )
    cells.append(md("### Resumen Comparativo de Correlación"))
    cells.append(code("""
high_correlation_pairs = pd.concat([
    correlation_pairs_breast_cancer_wisconsin,
    correlation_pairs_customer_churn,
    correlation_pairs_madelon,
    correlation_pairs_olive_oil,
], ignore_index=True)

correlation_summary = pd.concat([
    correlation_summary_breast_cancer_wisconsin,
    correlation_summary_customer_churn,
    correlation_summary_madelon,
    correlation_summary_olive_oil,
], ignore_index=True)
"""))
    cells.append(code("""
correlation_matrix_shift = pd.concat([
    correlation_matrix_shift_breast_cancer_wisconsin,
    correlation_matrix_shift_customer_churn,
    correlation_matrix_shift_madelon,
    correlation_matrix_shift_olive_oil,
], ignore_index=True)

vif_summary = pd.concat([
    vif_breast_cancer_wisconsin,
    vif_customer_churn,
    vif_madelon,
    vif_olive_oil,
], ignore_index=True)

categorical_association = pd.concat([
    categorical_assoc_breast_cancer_wisconsin,
    categorical_assoc_customer_churn,
    categorical_assoc_madelon,
    categorical_assoc_olive_oil,
], ignore_index=True)
"""))
    cells.append(code("""
guardar_tabla(high_correlation_pairs, "fase3_correlaciones_altas.csv")
guardar_tabla(correlation_summary, "fase3_correlaciones_resumen.csv")
guardar_tabla(correlation_matrix_shift, "fase3_correlaciones_matrices.csv")
guardar_tabla(vif_summary, "fase3_vif_processed.csv")
guardar_tabla(categorical_association, "fase3_cramers_v_categoricas.csv")
mostrar_tabla(correlation_summary, "Resumen de redundancia")
mostrar_tabla(correlation_matrix_shift, "Similitud cruda vs procesada de matrices de correlación", n=20)

def resumen_redundancia_markdown(correlation_table, matrix_shift_table):
    lines = ["**Lectura de resultados de redundancia.**"]
    matrix_lookup = matrix_shift_table.groupby("dataset")["frobenius_norm_difference"].max()
    for _, row in correlation_table.iterrows():
        frob = matrix_lookup.get(row["dataset"], np.nan)
        frob_text = "no calculable" if pd.isna(frob) else f"{frob:.6f}"
        lines.append(
            f"- `{row['dataset']}`: pares Spearman >=0.85={int(row['pares_abs_spearman_ge_085'])}, "
            f"pares Pearson >=0.85={int(row['pares_abs_pearson_ge_085'])}, "
            f"VIF máximo={row['vif_max']:.3f}, diferencia Frobenius raw/processed={frob_text}. "
            "La redundancia se documenta para selección/modelado; no se elimina en esta fase."
        )
    lines.append(
        "Implicación: los selectores de Fase 5 deben separar señal de redundancia. Esta lectura es especialmente importante para Breast Cancer Wisconsin "
        "por familias de medidas correlacionadas y para Madelon por su diseño sintético con variables irrelevantes/redundantes."
    )
    return "\\n".join(lines)


display(Markdown(resumen_redundancia_markdown(correlation_summary, correlation_matrix_shift)))
"""))

    cells.append(md("""
## 3.9 Dimensionalidad Final Antes del Split

Se sintetiza la dificultad dimensional con número de muestras, features, ratio features/muestras, clases del target y varianza PCA exploratoria. PCA se usa como diagnóstico descriptivo, no como transformación aplicada.
"""))
    cells.append(code("""
def crear_fila_pca(nombre_dataset, pca, n_used):
    explained = pca.explained_variance_ratio_
    return {
        "dataset": nombre_dataset,
        "pca_varianza_2": float(explained[:2].sum()),
        "pca_varianza_5": float(explained[:5].sum()),
        "n_pca_usado": n_used,
    }


def calcular_pca_resumen(nombre_dataset, datos_processed):
    numeric_features = [name for name in datos_processed.columns if name != PROCESSED_TARGET and pd.api.types.is_numeric_dtype(datos_processed[name])]
    if len(numeric_features) < 2:
        return {"dataset": nombre_dataset, "pca_varianza_2": np.nan, "pca_varianza_5": np.nan, "n_pca_usado": 0}
    matrix = datos_processed[numeric_features].replace([np.inf, -np.inf], np.nan)
    matrix = matrix.fillna(matrix.median(numeric_only=True))
    if len(matrix) > MAX_SAMPLE_PCA:
        matrix = matrix.sample(MAX_SAMPLE_PCA, random_state=RANDOM_STATE)
    scaled_matrix = StandardScaler().fit_transform(matrix)
    pca = PCA(n_components=min(5, scaled_matrix.shape[1]), random_state=RANDOM_STATE).fit(scaled_matrix)
    return crear_fila_pca(nombre_dataset, pca, len(matrix))
"""))
    cells.append(code("""
def resumir_dimensionalidad_final(nombre_dataset, datos_processed):
    features = datos_processed.shape[1] - 1
    ratio = features / len(datos_processed)
    return {
        "dataset": nombre_dataset,
        "filas": len(datos_processed),
        "features": features,
        "ratio_features_muestras": ratio,
        "supera_referencia_020": ratio >= DIMENSIONALITY_RATIO_REFERENCE,
        "target_clases": datos_processed[PROCESSED_TARGET].nunique(dropna=True),
    }
"""))

    dimensionality_observations = {
        "breast_cancer_wisconsin": "Observación: ratio p/n=0.052724 y PCA2=0.632; la dimensionalidad es moderada y refleja redundancia estructural.",
        "customer_churn": "Observación: ratio p/n=0.000023 y PCA2=0.362; el gran volumen de 440832 filas desplaza el reto hacia tratamiento mixto.",
        "madelon": "Observación: ratio p/n=0.250000 supera la referencia 0.20; Fase 4 y selección deben tratar esta alerta con cuidado.",
        "olive_oil": "Observación: ratio p/n=0.017483 y 9 clases; la dimensionalidad es baja, pero target y desbalance condicionan el split.",
    }
    add_dataset_cells(
        cells,
        "Dimensionalidad Final",
        """
dimensionality___VARIABLE__ = pd.DataFrame([resumir_dimensionalidad_final("__DATASET__", processed___VARIABLE__)])
pca___VARIABLE__ = pd.DataFrame([calcular_pca_resumen("__DATASET__", processed___VARIABLE__)])

mostrar_tabla(dimensionality___VARIABLE__, "Dimensionalidad final - __LABEL__")
mostrar_tabla(pca___VARIABLE__, "PCA exploratoria - __LABEL__")
""",
        dimensionality_observations,
    )
    cells.append(md("### Resumen Comparativo de Dimensionalidad"))
    cells.append(code("""
dimensionality_summary = pd.concat([
    dimensionality_breast_cancer_wisconsin,
    dimensionality_customer_churn,
    dimensionality_madelon,
    dimensionality_olive_oil,
], ignore_index=True)

pca_summary = pd.concat([
    pca_breast_cancer_wisconsin,
    pca_customer_churn,
    pca_madelon,
    pca_olive_oil,
], ignore_index=True)

dimensionality_with_pca = dimensionality_summary.merge(pca_summary, on="dataset", how="left")

guardar_tabla(dimensionality_with_pca, "fase3_dimensionalidad_final.csv")
mostrar_tabla(dimensionality_with_pca, "Dimensionalidad final comparativa")

def resumen_dimensionalidad_markdown(dimensionality_table):
    alerta = dimensionality_table.sort_values("ratio_features_muestras", ascending=False).iloc[0]
    minimo = dimensionality_table.sort_values("ratio_features_muestras").iloc[0]
    pca_top = dimensionality_table.sort_values("pca_varianza_2", ascending=False).iloc[0]
    supera = int(dimensionality_table["supera_referencia_020"].sum())
    lines = [
        "**Lectura comparativa de dimensionalidad.**",
        f"`{alerta['dataset']}` es la alerta principal: {int(alerta['features'])} features para {int(alerta['filas'])} filas, "
        f"ratio p/n={alerta['ratio_features_muestras']:.3f}, por encima de la referencia {DIMENSIONALITY_RATIO_REFERENCE:.2f}.",
        f"El extremo opuesto es `{minimo['dataset']}` con ratio p/n={minimo['ratio_features_muestras']:.6f}; solo {supera}/{len(dimensionality_table)} datasets supera la referencia operativa.",
        f"La PCA descriptiva concentra más varianza inicial en `{pca_top['dataset']}`: las dos primeras componentes explican {pca_top['pca_varianza_2']:.3f}. "
        "Esta cifra describe estructura, no transforma datos antes del split.",
    ]
    return "\\n\\n".join(lines)


display(Markdown(resumen_dimensionalidad_markdown(dimensionality_with_pca)))
"""))
    cells.append(code("""
figura, eje = plt.subplots(figsize=(8.4, 5.6))
eje.scatter(dimensionality_with_pca["filas"], dimensionality_with_pca["features"], s=115, color="#2F6F9F")
x_values = np.array([dimensionality_with_pca["filas"].min(), dimensionality_with_pca["filas"].max()])
eje.plot(x_values, DIMENSIONALITY_RATIO_REFERENCE * x_values, color="#B85C5C", linewidth=1.2, linestyle="--", label="Referencia p/n = 0.20")
for _, row in dimensionality_with_pca.iterrows():
    eje.annotate(etiqueta_dataset(row["dataset"]), (row["filas"], row["features"]), xytext=(8, 6), textcoords="offset points", fontsize=8)
eje.set_xscale("log")
eje.set_yscale("log")
eje.set_xlabel("Filas")
eje.set_ylabel("Features")
eje.set_title("Madelon supera la referencia p/n", loc="left", fontweight="bold")
eje.legend(frameon=False)
aplicar_estilo_eje(eje, eje_rejilla="both")
fijar_titulo_narrativo(figura, "Madelon es la alerta dimensional antes del split")
cerrar_figura_narrativa(figura, "fase3_dimensionalidad_final.png")
"""))
    cells.append(md("""
Lectura de la figura dimensional: `madelon` queda por encima de la referencia p/n=0.20 con ratio 0.250, mientras los otros 3 datasets permanecen por debajo. Esta diferencia justifica tratar su selección de variables con especial cautela.
"""))

    cells.append(md("""
## 3.10 Síntesis Métrica Para la Fase 4

Se reúne una tabla final de métricas para orientar el split a partir de condiciones medibles de las secciones anteriores. El criterio de lectura combina cuatro riesgos: ratio features/muestras para dimensionalidad, ratio mayoritaria/minoritaria para estratificación del target, número de categóricas pendientes para evitar fuga en encoding y pares Spearman `>=0.85` para redundancia. La figura 2x2 no decide modelos ni selecciona variables; ordena las restricciones que Fase 4 debe preservar antes de que Fase 5 y QFS comparen relevancia y redundancia.
"""))
    cells.append(code("""
final_metric_summary = (
    structure_summary[["dataset", "filas", "features", "variables_categoricas", "columnas_duplicadas", "target_clases"]]
    .merge(target_summary[["dataset", "ratio_mayoritaria_minoritaria"]], on="dataset", how="left")
    .merge(correlation_summary[["dataset", "pares_abs_spearman_ge_085", "abs_spearman_maxima", "vif_max"]], on="dataset", how="left")
    .merge(dimensionality_with_pca[["dataset", "ratio_features_muestras", "pca_varianza_2", "pca_varianza_5"]], on="dataset", how="left")
)

quality_totals = nulls_summary.groupby("dataset", as_index=False).agg(
    nulos_totales=("nulos", "sum"),
    infinitos_totales=("infinitos", "sum"),
)
final_metric_summary = final_metric_summary.merge(quality_totals, on="dataset", how="left")

guardar_tabla(final_metric_summary, "fase3_resumen_metricas_split.csv")
mostrar_tabla(final_metric_summary, "Resumen métrico para Fase 4")

def resumen_metricas_split_markdown(tabla):
    total_nulos = int(tabla["nulos_totales"].sum())
    total_infinitos = int(tabla["infinitos_totales"].sum())
    max_ratio = tabla.sort_values("ratio_features_muestras", ascending=False).iloc[0]
    max_balance = tabla.sort_values("ratio_mayoritaria_minoritaria", ascending=False).iloc[0]
    return (
        "**Lectura de la tabla métrica para Fase 4.** "
        f"La tabla resume {len(tabla)} datasets y confirma {total_nulos} nulos y {total_infinitos} infinitos antes del split. "
        f"`{max_ratio['dataset']}` fija la mayor carga dimensional con ratio p/n={max_ratio['ratio_features_muestras']:.3f}; "
        f"`{max_balance['dataset']}` fija el mayor desbalance con ratio={max_balance['ratio_mayoritaria_minoritaria']:.2f}. "
        "Estas dos cifras explican por qué la síntesis visual separa dimensionalidad y target en paneles distintos."
    )


display(Markdown(resumen_metricas_split_markdown(final_metric_summary)))
"""))
    cells.append(code("""
figura, ejes = plt.subplots(2, 2, figsize=(12.2, 8.0))
ejes = ejes.ravel()
plot_summary = final_metric_summary.copy()
plot_summary["dataset_label"] = plot_summary["dataset"].map(etiqueta_dataset)

def dibujar_barra_sintesis(eje, tabla, columna, titulo, xlabel, color, referencia=None):
    ordered = tabla.sort_values(columna)
    eje.barh(ordered["dataset_label"], ordered[columna], color=color)
    if referencia is not None:
        eje.axvline(referencia, color="#2D2A26", linewidth=1.0, linestyle="--")
    for _, row in ordered.iterrows():
        valor = row[columna]
        etiqueta = f"{valor:.3f}" if abs(valor) < 10 else f"{valor:.0f}"
        eje.annotate(etiqueta, (valor, row["dataset_label"]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8)
    eje.set_title(titulo, loc="left", fontweight="bold")
    eje.set_xlabel(xlabel)
    aplicar_estilo_eje(eje, eje_rejilla="x")


dibujar_barra_sintesis(ejes[0], plot_summary, "ratio_features_muestras", "Madelon concentra la alerta dimensional", "Features / muestras", "#D9822B", DIMENSIONALITY_RATIO_REFERENCE)
dibujar_barra_sintesis(ejes[1], plot_summary, "ratio_mayoritaria_minoritaria", "Olive Oil exige estratificación multiclase", "Ratio mayoritaria/minoritaria", "#5E8C61")
dibujar_barra_sintesis(ejes[2], plot_summary, "variables_categoricas", "Solo Customer Churn llega con encoding pendiente", "Predictoras categóricas", "#7A6FA5")
dibujar_barra_sintesis(ejes[3], plot_summary, "pares_abs_spearman_ge_085", "La redundancia queda documentada antes de seleccionar", "Pares Spearman >= 0.85", "#B85C5C")

fijar_titulo_narrativo(figura, "Tres condiciones guían Fase 4: dimensionalidad, encoding y desbalance")
cerrar_figura_narrativa(figura, "fase3_sintesis_metricas_split.png")

def lectura_panel_sintesis(tabla):
    row_dim = tabla.sort_values("ratio_features_muestras", ascending=False).iloc[0]
    row_balance = tabla.sort_values("ratio_mayoritaria_minoritaria", ascending=False).iloc[0]
    row_cat = tabla.sort_values("variables_categoricas", ascending=False).iloc[0]
    row_corr = tabla.sort_values("pares_abs_spearman_ge_085", ascending=False).iloc[0]
    return (
        "**Lectura del panel 2x2 de síntesis.** "
        f"Arriba izquierda, dimensionalidad: `{row_dim['dataset']}` domina con ratio p/n={row_dim['ratio_features_muestras']:.3f}, "
        f"frente a la referencia {DIMENSIONALITY_RATIO_REFERENCE:.2f}; por eso 3.11 lo marca como caso que exige control de selección. "
        f"Arriba derecha, target: `{row_balance['dataset']}` alcanza ratio mayoritaria/minoritaria={row_balance['ratio_mayoritaria_minoritaria']:.2f}, "
        "lo que justifica estratificación cuidadosa. "
        f"Abajo izquierda, encoding: `{row_cat['dataset']}` acumula {int(row_cat['variables_categoricas'])} predictoras categóricas, "
        "de modo que el encoder debe ajustarse después del split. "
        f"Abajo derecha, redundancia: `{row_corr['dataset']}` concentra {int(row_corr['pares_abs_spearman_ge_085'])} pares Spearman >=0.85; "
        "esa cifra enlaza con la conclusión de no eliminar variables aquí, sino entregar la estructura a selección clásica y QFS."
    )


display(Markdown(lectura_panel_sintesis(final_metric_summary)))
"""))
    cells.append(md("""
## 3.11 Conclusiones y Consideraciones Para la Fase 4

La auditoría confirma carga correcta, conservación de filas, target estable y ausencia de nulos o infinitos bloqueantes. El criterio de cierre exige que Fase 4 reciba datos particionables, que Fase 5 reciba señal y redundancia sin selección previa, y que QFS pueda medir `I(x_i;y)` e `I(x_i;x_j)` sobre datos y tablas reproducibles.

Condiciones para Fase 4:

- `customer_churn`: codificar categóricas después del split, ajustando el encoder solo con entrenamiento.
- `madelon`: tratar la relación features/muestras como dificultad dimensional.
- `olive_oil`: estratificar con atención al desbalance multiclase.
- Correlaciones y asociaciones son diagnóstico, no selección automática.
"""))
    cells.append(code("""
summary_lines = [
    "# Resultados de la Fase 3 - Auditoría Post-Preprocesado",
    "",
    "La Fase 3 verifica los datasets procesados antes del split y resume las condiciones medibles que afectan a la partición posterior.",
    "",
    "## Hallazgos principales",
    f"- El target conserva sus proporciones en todos los datasets: max |delta proporción| = {target_summary['max_delta_proporcion'].max():.6f}.",
    f"- Las variables numéricas comparables no muestran desplazamiento distribucional medible: KS máximo = {distribution_tests_summary['ks_maximo'].max():.6f}, PSI máximo = {distribution_tests_summary['psi_maximo'].max():.6f}.",
    f"- `customer_churn` mantiene {len(pending_categories[pending_categories['dataset'].eq('customer_churn')])} categóricas predictoras pendientes; deben codificarse después del split, ajustando el encoder solo con entrenamiento.",
    f"- La similitud de matrices crudas/procesadas es completa en las variables comparables: Frobenius máximo = {correlation_matrix_shift['frobenius_norm_difference'].max():.6f}.",
    f"- La mayor alerta de dimensionalidad es `madelon`, con ratio features/muestras = {float(dimensionality_with_pca.loc[dimensionality_with_pca['dataset'].eq('madelon'), 'ratio_features_muestras'].iloc[0]):.3f}.",
    "",
    "## Tablas generadas",
]

for table_path in sorted(PHASE3_TABLES_DIR.glob("fase3_*.csv")):
    summary_lines.append(f"- `{table_path.relative_to(PROJECT_ROOT)}`")

summary_lines.extend(["", "## Figuras generadas"])
for figure_path in sorted(PHASE3_FIGURES_DIR.glob("fase3_*.png")):
    summary_lines.append(f"- `{figure_path.relative_to(PROJECT_ROOT)}`")

summary_path = PHASE3_REPORTS_DIR / "fase3_resumen_para_memoria.md"
summary_path.write_text("\\n".join(summary_lines), encoding="utf-8")
print("Resumen para memoria escrito correctamente.")
display(Markdown(
    f"**Lectura del informe exportado.** Se escribe `fase3_resumen_para_memoria.md` con {len(list(PHASE3_TABLES_DIR.glob('fase3_*.csv')))} tablas "
    f"y {len(list(PHASE3_FIGURES_DIR.glob('fase3_*.png')))} figuras PNG, cada una acompañada por su PDF vectorial."
))
"""))

    notebook["cells"] = cells
    return notebook


if __name__ == "__main__":
    notebook = build_notebook()
    nbf.write(notebook, NOTEBOOK_PATH)
    print(f"Notebook rebuilt: {NOTEBOOK_PATH.relative_to(ROOT)}")
