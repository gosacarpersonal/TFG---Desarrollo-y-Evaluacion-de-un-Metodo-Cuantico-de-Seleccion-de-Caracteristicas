from pathlib import Path
import shutil

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "fase1.ipynb"

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
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "qfs_env", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }

    cells = []

    cells.append(md("""
# Trabajo de Fin de Grado: Desarrollo y Evaluación de un Método Cuántico de Selección de Características

## Notebook 01 - Fase 1: Análisis Exploratorio de los Datos Crudos

Esta fase inspecciona los datasets originales antes de tomar decisiones de preprocesado, selección de características o modelado. El recorrido se plantea como una exploración progresiva: primero se comprueba la lectura de cada archivo, después se caracteriza cada dataset por separado y, solo al final de cada sección, se construye una comparación conjunta cuando aporta lectura.

El encaje con la propuesta del TFG es directo: esta fase documenta la selección de datasets de referencia del objetivo 2, prepara la comparación clásica de los objetivos 1 y 3 y deja una base reproducible para que el método cuántico de selección de características pueda evaluarse contra un brazo clásico bien caracterizado. La lectura se orienta además al paso posterior hacia QFS: las asociaciones variable-target anticipan la relevancia que después se codificará como información mutua, y las redundancias entre variables anticipan las interacciones que QFS trasladará a distancias entre átomos.
"""))

    cells.append(md("""
## Importación de Librerías

Se importan las librerías que se utilizarán durante el análisis exploratorio y la generación de evidencias reproducibles.
"""))
    cells.append(code("""
from pathlib import Path
import io
import shutil
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from IPython.display import Markdown, display as ipy_display
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)
"""))

    cells.append(md("""
## Preparación del Entorno de Trabajo

Se localizan los datos crudos y se preparan las carpetas donde se conservarán las tablas y figuras de esta fase. Si alguna carpeta esencial no existiera, la ejecución se detendría sin producir una lectura parcial.
"""))
    cells.append(code("""
# Rutas principales del proyecto.
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA_DIR = PROJECT_ROOT / "data" / "01_raw"
TABLES_DIR = PROJECT_ROOT / "results" / "tables" / "01_raw_eda"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures" / "01_raw_eda"
REPORTS_DIR = PROJECT_ROOT / "results" / "reports" / "01_raw_eda"

for output_dir in [TABLES_DIR, FIGURES_DIR, REPORTS_DIR]:
    output_dir.mkdir(parents=True, exist_ok=True)

for old_table_path in TABLES_DIR.glob("*.csv"):
    old_table_path.unlink()

for old_figure_path in FIGURES_DIR.rglob("*.png"):
    old_figure_path.unlink()

for old_figure_path in FIGURES_DIR.rglob("*.pdf"):
    old_figure_path.unlink()

for old_child in FIGURES_DIR.iterdir():
    if old_child.is_dir() and not any(old_child.iterdir()):
        old_child.rmdir()

for old_report_path in REPORTS_DIR.glob("*"):
    if old_report_path.is_file():
        old_report_path.unlink()

assert DATA_DIR.exists()
assert TABLES_DIR.exists()
assert FIGURES_DIR.exists()
assert REPORTS_DIR.exists()
"""))
    cells.append(md("""
El entorno queda preparado para leer los datos crudos y conservar las tablas y figuras que sustentan la fase. La comprobación es silenciosa si las carpetas existen; así el capítulo empieza por el objeto de estudio y no por detalles de ejecución.
"""))

    cells.append(md("""
## Configuración Visual y Parámetros Generales

La configuración visual se mantiene sobria para facilitar la lectura en notebook y en memoria. El límite de muestra visual se usa únicamente para representar datasets grandes; los cálculos estadísticos se realizan sobre los datos completos salvo que se indique lo contrario.
"""))
    cells.append(code("""
# Parámetros generales del análisis.
RANDOM_STATE = 42
MAX_FILAS_MUESTRA_VISUAL = 5000

PALETA_DATASETS = {
    "breast_cancer_wisconsin": "#2F6F9F",
    "customer_churn": "#D9822B",
    "madelon": "#5E8C61",
    "olive_oil": "#7A6FA5",
}

ORDEN_DATASETS = list(PALETA_DATASETS)

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

pd.set_option("display.max_columns", 28)
pd.set_option("display.max_rows", 50)
pd.set_option("display.width", 160)
"""))

    cells.append(md("""
## Utilidades Generales del Notebook

Estas funciones son pequeñas y tienen una responsabilidad concreta: guardar tablas, guardar figuras y aplicar un estilo visual común. Se definen aquí porque se reutilizan en varias secciones.
"""))
    cells.append(code("""
def guardar_tabla(tabla, nombre_archivo):
    ruta_tabla = TABLES_DIR / nombre_archivo
    tabla.to_csv(ruta_tabla, index=False)
    return ruta_tabla


def guardar_figura(figura, nombre_archivo):
    ruta_figura = FIGURES_DIR / nombre_archivo
    ruta_figura.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(ruta_figura, dpi=300, bbox_inches="tight")
    ruta_pdf = ruta_figura.with_suffix(".pdf")
    figura.savefig(ruta_pdf, bbox_inches="tight")
    return ruta_figura


def aplicar_estilo_eje(eje, eje_rejilla="x"):
    eje.spines["top"].set_visible(False)
    eje.spines["right"].set_visible(False)
    eje.grid(axis=eje_rejilla, alpha=0.65)
    eje.set_axisbelow(True)


def mostrar_ruta_relativa(ruta):
    print("Figura guardada en formatos PNG y PDF.")


COLUMNAS_PRESENTACION_ESPECIFICAS = {
    "features": "variables predictoras",
    "target_presente": "target presente",
    "ratio_features_muestras": "variables / filas",
    "filas_por_feature": "filas por variable",
    "ratio_valores_unicos": "valores únicos / filas",
    "variables_moda_dominante_98": "variables con moda dominante al 98%",
    "n": "observaciones",
    "ratio_mayoritaria_minoritaria": "ratio mayoritaria / minoritaria",
    "p_valor": "p-valor",
    "p_valor_fdr": "p-valor FDR",
    "abs_tamano_efecto": "|tamaño de efecto|",
    "efecto_abs_mediano": "|efecto| mediano",
    "efecto_abs_maximo": "|efecto| máximo",
    "variable_a": "variable A",
    "variable_b": "variable B",
    "spearman": "Spearman",
    "abs_spearman": "|Spearman|",
    "correlacion_abs_maxima": "|correlación| máxima",
    "componentes_80": "componentes para 80%",
    "componentes_90": "componentes para 90%",
    "categoria_exploratoria": "categoría exploratoria",
}


def nombre_columna_presentacion(columna):
    if columna is None:
        return None
    if columna in COLUMNAS_PRESENTACION_ESPECIFICAS:
        return COLUMNAS_PRESENTACION_ESPECIFICAS[columna]
    return str(columna).replace("_", " ")

VALORES_PRESENTACION = {
    "breast_cancer_wisconsin": "Breast Cancer Wisconsin",
    "customer_churn": "Customer Churn",
    "madelon": "Madelon",
    "olive_oil": "Olive Oil",
    "muestra_estratificada_visual": "muestra estratificada visual",
    "completo": "completo",
    "revisar_riesgo": "revisar por cautela",
    "revisar_por_cautela": "revisar por cautela",
    "redundancia_alta": "redundancia alta",
    "senal_fuerte": "señal fuerte",
    "senal_moderada": "señal moderada",
    "sin_senal_univariante": "sin señal univariante",
    "mann_whitney_u": "Mann-Whitney U",
    "kruskal_wallis": "Kruskal-Wallis",
    "chi2": "chi-cuadrado",
    "cramers_v": "V de Cramér",
    "cliffs_delta": "delta de Cliff",
    "epsilon_squared": "epsilon cuadrado",
    "dagostino_k2": "D'Agostino K²",
    "shapiro_wilk": "Shapiro-Wilk",
    "muestra_insuficiente": "muestra insuficiente",
    True: "sí",
    False: "no",
}


def preparar_tabla_presentacion(tabla):
    tabla_presentada = tabla.copy()
    for columna in tabla_presentada.columns:
        if tabla_presentada[columna].dtype == "object" or tabla_presentada[columna].dtype == "bool":
            tabla_presentada[columna] = tabla_presentada[columna].map(
                lambda valor: VALORES_PRESENTACION.get(valor, valor)
            )
    if isinstance(tabla_presentada.index, pd.MultiIndex):
        tabla_presentada.index = pd.MultiIndex.from_tuples(
            tuple(VALORES_PRESENTACION.get(valor, valor) for valor in indice)
            for indice in tabla_presentada.index
        )
    else:
        tabla_presentada.index = tabla_presentada.index.map(lambda valor: VALORES_PRESENTACION.get(valor, valor))
    tabla_presentada = tabla_presentada.rename(
        columns=lambda columna: nombre_columna_presentacion(VALORES_PRESENTACION.get(columna, columna))
    )
    tabla_presentada.index.name = nombre_columna_presentacion(tabla.index.name)
    tabla_presentada.columns.name = nombre_columna_presentacion(tabla.columns.name)
    return tabla_presentada


def display(obj=None, *args, **kwargs):
    if isinstance(obj, pd.DataFrame):
        return ipy_display(preparar_tabla_presentacion(obj), *args, **kwargs)
    if obj.__class__.__name__ == "Styler":
        return ipy_display(preparar_tabla_presentacion(obj.data).style, *args, **kwargs)
    return ipy_display(obj, *args, **kwargs)
"""))

    cells.append(md("""
## 1.1 Comprobación y Carga Inicial de los Datasets

Se comprueba la existencia de los archivos y se carga cada dataset de manera individual. La selección del banco responde al objetivo 2 de la propuesta, que exige diversidad en número de muestras, número de variables y tipo de variables: se combinan datasets clínicos, sintéticos, químicos y de negocio. Frente a los tres datasets binarios de 14-19 features usados en el paper QFS, aquí se amplía deliberadamente el reto con `olive_oil` multiclase, `madelon` con 500 variables y solo 20 informativas por construcción, y `customer_churn` con 440.832 filas; esta variedad permite leer desde el inicio qué casos tensionan relevancia, redundancia, dimensionalidad y escala muestral.
"""))
    cells.append(code("""
# Datos y targets esperados para esta fase.
rutas_datasets = {
    "breast_cancer_wisconsin": DATA_DIR / "breast_cancer_wisconsin.csv",
    "customer_churn": DATA_DIR / "customer_churn.csv",
    "madelon": DATA_DIR / "madelon.csv",
    "olive_oil": DATA_DIR / "olive_oil.csv",
}

targets_esperados = {
    "breast_cancer_wisconsin": "target",
    "customer_churn": "Churn",
    "madelon": "target",
    "olive_oil": "target",
}

for ruta_dataset in rutas_datasets.values():
    assert ruta_dataset.exists()
"""))
    cells.append(md("""
Los 4 datasets esperados existen antes de la carga. La validación permite continuar con lectura tabular homogénea mediante `pandas.read_csv`.
"""))
    cells.append(code("""
def cargar_dataset(ruta_dataset):
    if not ruta_dataset.exists():
        raise FileNotFoundError(f"No se encuentra el archivo: {ruta_dataset}")
    return pd.read_csv(ruta_dataset)


def obtener_info_texto(datos_dataset):
    salida_info = io.StringIO()
    datos_dataset.info(buf=salida_info)
    return salida_info.getvalue()


def mostrar_inspeccion_inicial(datos_dataset):
    print(f"dimensiones: {datos_dataset.shape}")
    display(datos_dataset.head())
    print(obtener_info_texto(datos_dataset))
"""))

    load_observations = {
        "breast_cancer_wisconsin": "La lectura muestra 569 filas y 32 columnas. El target `target` está presente y aparece una columna `id`, por lo que más adelante se revisa como posible identificador antes de modelar.",
        "customer_churn": "La lectura muestra 440.832 filas y 12 columnas. Es el dataset con mayor volumen muestral y combina variables numéricas, categóricas y el identificador `CustomerID`.",
        "madelon": "La lectura muestra 2.000 filas y 501 columnas. La estructura ya anticipa un problema de dimensionalidad: 500 columnas predictoras y un target binario.",
        "olive_oil": "La lectura muestra 572 filas y 12 columnas. Incluye `id`, un target textual multiclase y variables numéricas asociadas a composición de ácidos grasos.",
    }
    add_dataset_cells(
        cells,
        "Carga Inicial",
        """
{variable_name} = cargar_dataset(rutas_datasets["{dataset_name}"])
mostrar_inspeccion_inicial({variable_name})
""",
        load_observations,
    )

    cells.append(md("""
### Registro Común de Datasets Cargados

Una vez inspeccionados individualmente, los datasets se agrupan en un diccionario para reutilizarlos en las secciones siguientes sin repetir rutas ni nombres de variables.
"""))
    cells.append(code("""
datasets = {
    "breast_cancer_wisconsin": breast_cancer_wisconsin,
    "customer_churn": customer_churn,
    "madelon": madelon,
    "olive_oil": olive_oil,
}

resumen_carga = pd.DataFrame([
    {
        "dataset": nombre_dataset,
        "archivo": rutas_datasets[nombre_dataset].name,
        "filas": len(datos_dataset),
        "columnas": datos_dataset.shape[1],
        "target": targets_esperados[nombre_dataset],
        "target_presente": targets_esperados[nombre_dataset] in datos_dataset.columns,
    }
    for nombre_dataset, datos_dataset in datasets.items()
])

guardar_tabla(resumen_carga, "fase1_carga_inicial.csv")
display(resumen_carga)
"""))
    cells.append(md("""
El registro de carga confirma 4 datasets con target presente. La escala va de 569 filas en `breast_cancer_wisconsin` a 440.832 en `customer_churn`, y la anchura va de 12 columnas en `customer_churn` y `olive_oil` a 501 en `madelon`; por eso las secciones siguientes comparan calidad, target, asociación y redundancia sin asumir un único perfil de datos.
"""))

    cells.append(md("""
## 1.2 Inspección Estructural Básica

La inspección estructural cuantifica filas, columnas predictoras, tipos de variables y posibles identificadores. También se calcula la fracción `features / filas`; se informa como diagnóstico de presión dimensional, no como umbral de aceptación o rechazo.
"""))
    cells.append(code("""
def obtener_columnas_predictoras(datos_dataset, target):
    return [variable for variable in datos_dataset.columns if variable != target]


def nombre_sugiere_identificador(variable):
    nombre_variable = str(variable).lower()
    return nombre_variable in {"id", "customerid", "customer_id"} or nombre_variable.endswith("_id")


def columna_es_unica(serie):
    return serie.nunique(dropna=True) == len(serie)


def es_posible_identificador(datos_dataset, variable):
    return nombre_sugiere_identificador(variable) and columna_es_unica(datos_dataset[variable])


def listar_posibles_identificadores(datos_dataset, target):
    columnas_predictoras = obtener_columnas_predictoras(datos_dataset, target)
    return [variable for variable in columnas_predictoras if es_posible_identificador(datos_dataset, variable)]
"""))
    cells.append(code("""
def contar_columnas_numericas(datos_dataset, columnas_predictoras):
    return len(datos_dataset[columnas_predictoras].select_dtypes(include=np.number).columns)


def crear_resumen_estructura_basico(nombre_dataset, datos_dataset, target, columnas_predictoras):
    return {
        "dataset": nombre_dataset,
        "filas": len(datos_dataset),
        "columnas_totales": datos_dataset.shape[1],
        "features": len(columnas_predictoras),
        "target": target,
    }


def calcular_ratio_features_muestras(datos_dataset, target):
    return len(obtener_columnas_predictoras(datos_dataset, target)) / len(datos_dataset)


def resumir_estructura_dataset(nombre_dataset, datos_dataset, target):
    columnas_predictoras = obtener_columnas_predictoras(datos_dataset, target)
    posibles_identificadores = listar_posibles_identificadores(datos_dataset, target)
    columnas_numericas = contar_columnas_numericas(datos_dataset, columnas_predictoras)
    resumen = crear_resumen_estructura_basico(nombre_dataset, datos_dataset, target, columnas_predictoras)
    resumen["variables_numericas"] = columnas_numericas
    resumen["variables_categoricas"] = len(columnas_predictoras) - columnas_numericas
    resumen["posibles_identificadores"] = len(posibles_identificadores)
    resumen["nombres_posibles_identificadores"] = ", ".join(map(str, posibles_identificadores))
    resumen["ratio_features_muestras"] = calcular_ratio_features_muestras(datos_dataset, target)
    return resumen
"""))

    structure_obs = {
        "breast_cancer_wisconsin": "`breast_cancer_wisconsin` tiene 31 variables predictoras para 569 filas. La columna `id` queda marcada como identificador potencial y no debe tratarse como señal clínica.",
        "customer_churn": "`customer_churn` tiene 10 variables predictoras para 440.832 filas. `CustomerID` queda marcado como 1 identificador potencial; la cautela estructural no es dimensional sino semántica y de codificación.",
        "madelon": "`madelon` tiene 500 variables predictoras para 2.000 filas. Su ratio `features / filas` es el mayor de la fase y justifica prestar atención a dimensionalidad y ruido.",
        "olive_oil": "`olive_oil` tiene 11 variables predictoras para 572 filas. La columna `id` queda marcada como identificador potencial, mientras que el resto de variables se mantiene para análisis exploratorio.",
    }
    add_dataset_cells(
        cells,
        "Estructura",
        """
estructura_{variable_name} = pd.DataFrame([
    resumir_estructura_dataset("{dataset_name}", {variable_name}, targets_esperados["{dataset_name}"])
])
display(estructura_{variable_name}.style.format({{"ratio_features_muestras": "{{:.5f}}"}}))
""",
        structure_obs,
    )

    cells.append(md("""
### Comparación de Presión Dimensional

La comparación visual responde una pregunta concreta: cuántas filas hay por cada variable predictora. Esta formulación es más legible que representar solo la fracción `features / filas`, porque evita que valores muy pequeños parezcan exactamente cero.
"""))
    cells.append(code("""
estructura_datasets = pd.concat([
    estructura_breast_cancer_wisconsin,
    estructura_customer_churn,
    estructura_madelon,
    estructura_olive_oil,
], ignore_index=True)
estructura_datasets["filas_por_feature"] = estructura_datasets["filas"] / estructura_datasets["features"]

guardar_tabla(estructura_datasets, "fase1_estructura_datasets.csv")
display(estructura_datasets.style.format({
    "ratio_features_muestras": "{:.5f}",
    "filas_por_feature": "{:.1f}",
}))
"""))
    cells.append(md("""
La tabla estructural resume 31 features en `breast_cancer_wisconsin`, 11 en `olive_oil`, 10 en `customer_churn` y 500 en `madelon`. La presión dimensional queda cuantificada por filas por feature: 18,4 en `breast_cancer_wisconsin`, 57.200,0 en `customer_churn`, 4,0 en `madelon` y 52,0 en `olive_oil`; la figura siguiente convierte esa diferencia de órdenes de magnitud en lectura visual.
"""))
    cells.append(code("""
figura, eje = plt.subplots(figsize=(9, 4.8))
datos_grafico = estructura_datasets.set_index("dataset").loc[ORDEN_DATASETS].reset_index()
sns.scatterplot(
    datos_grafico,
    y="dataset",
    x="filas_por_feature",
    hue="dataset",
    palette=PALETA_DATASETS,
    s=140,
    legend=False,
    ax=eje,
)
eje.set_xscale("log")
eje.set_title("Madelon soporta la mayor presión dimensional")
eje.set_xlabel("filas / feature (escala logarítmica)")
eje.set_ylabel("")
aplicar_estilo_eje(eje)
for _, fila in datos_grafico.iterrows():
    eje.text(fila["filas_por_feature"] * 1.08, fila["dataset"], f'{fila["filas_por_feature"]:.1f}', va="center")
ruta_figura = guardar_figura(figura, "01_02_estructura_filas_por_feature.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
"""))
    cells.append(md("""
La figura confirma que `madelon` es el dataset con menos filas por variable predictora, mientras que `customer_churn` dispone de muchas observaciones por cada feature. Por tanto, la Fase 2 deberá tratar la dimensionalidad de `madelon` con especial cuidado.
"""))

    cells.append(md("""
## 1.3 Calidad del Dato Crudo

La calidad se revisa por dataset. Se separan nulos, duplicados, constantes, baja cardinalidad relativa y dominancia de moda para evitar nombres opacos como `baja_varianza_o_dominancia`. El umbral de moda dominante del 98% se usa solo como alerta exploratoria de variables casi constantes.
"""))
    cells.append(code("""
UMBRAL_CARDINALIDAD_RELATIVA_BAJA = 0.01
UMBRAL_MODA_DOMINANTE = 0.98
"""))
    cells.append(code("""
def contar_nulos_totales(datos_dataset):
    return int(datos_dataset.isna().sum().sum())


def contar_filas_duplicadas(datos_dataset):
    return int(datos_dataset.duplicated().sum())


def calcular_ratio_valores_unicos(serie):
    return serie.nunique(dropna=True) / len(serie)


def calcular_frecuencia_moda(serie):
    return float(serie.value_counts(dropna=False, normalize=True).iloc[0])
"""))
    cells.append(code("""
def resumir_calidad_variable(nombre_dataset, variable, serie):
    valores_unicos = int(serie.nunique(dropna=True))
    ratio_unicos = calcular_ratio_valores_unicos(serie)
    frecuencia_moda = calcular_frecuencia_moda(serie)
    return {
        "dataset": nombre_dataset,
        "variable": variable,
        "nulos": int(serie.isna().sum()),
        "valores_unicos": valores_unicos,
        "ratio_valores_unicos": ratio_unicos,
        "frecuencia_moda": frecuencia_moda,
        "constante": valores_unicos <= 1,
        "baja_cardinalidad_relativa": ratio_unicos <= UMBRAL_CARDINALIDAD_RELATIVA_BAJA,
        "moda_dominante": frecuencia_moda >= UMBRAL_MODA_DOMINANTE,
    }


def resumir_calidad_variables(nombre_dataset, datos_dataset, target):
    columnas_predictoras = obtener_columnas_predictoras(datos_dataset, target)
    return pd.DataFrame([
        resumir_calidad_variable(nombre_dataset, variable, datos_dataset[variable])
        for variable in columnas_predictoras
    ])
"""))
    cells.append(code("""
def resumir_calidad_dataset(nombre_dataset, datos_dataset, calidad_variables):
    return {
        "dataset": nombre_dataset,
        "nulos_totales": contar_nulos_totales(datos_dataset),
        "filas_duplicadas": contar_filas_duplicadas(datos_dataset),
        "variables_constantes": int(calidad_variables["constante"].sum()),
        "variables_baja_cardinalidad_relativa": int(calidad_variables["baja_cardinalidad_relativa"].sum()),
        "variables_moda_dominante_98": int(calidad_variables["moda_dominante"].sum()),
    }


def seleccionar_variables_calidad(calidad_variables):
    mascara_revision = (
        calidad_variables["constante"]
        | calidad_variables["baja_cardinalidad_relativa"]
        | calidad_variables["moda_dominante"]
    )
    return calidad_variables[mascara_revision].sort_values("frecuencia_moda", ascending=False)
"""))

    quality_obs = {
        "breast_cancer_wisconsin": "No se observan nulos, duplicados, constantes ni variables marcadas por baja cardinalidad o moda dominante: las 5 alertas agregadas quedan en 0. En esta sección no aparece señal que justifique limpieza automática.",
        "customer_churn": "No se observan nulos ni duplicados. Aparecen 9 variables con baja cardinalidad relativa; esto no implica error, porque varias variables son categóricas o discretas.",
        "madelon": "No se observan nulos ni duplicados. Aparecen 24 variables de baja cardinalidad relativa dentro de una matriz de 500 features, por lo que conviene revisarlas antes de selección formal.",
        "olive_oil": "No se observan nulos ni duplicados. La variable `Area` es la única de 11 predictoras que aparece por baja cardinalidad relativa; no se elimina aquí porque puede ser semánticamente relevante y debe analizarse frente al target.",
    }
    add_dataset_cells(
        cells,
        "Calidad",
        """
calidad_variables_{variable_name} = resumir_calidad_variables(
    "{dataset_name}",
    {variable_name},
    targets_esperados["{dataset_name}"],
)
calidad_{variable_name} = pd.DataFrame([
    resumir_calidad_dataset("{dataset_name}", {variable_name}, calidad_variables_{variable_name})
])
variables_calidad_revision_{variable_name} = seleccionar_variables_calidad(calidad_variables_{variable_name})

display(calidad_{variable_name})
if variables_calidad_revision_{variable_name}.empty:
    display(Markdown("No hay variables marcadas para revisión por estas reglas."))
else:
    display(variables_calidad_revision_{variable_name}.style.format({{
        "ratio_valores_unicos": "{{:.4f}}",
        "frecuencia_moda": "{{:.2%}}",
    }}))
""",
        quality_obs,
    )

    cells.append(md("""
### Resumen Comparativo de Calidad

La comparación se construye después de revisar cada dataset por separado. No se genera una figura si la tabla responde mejor la pregunta de calidad.
"""))
    cells.append(code("""
calidad_datasets = pd.concat([
    calidad_breast_cancer_wisconsin,
    calidad_customer_churn,
    calidad_madelon,
    calidad_olive_oil,
], ignore_index=True)

calidad_variables = pd.concat([
    calidad_variables_breast_cancer_wisconsin,
    calidad_variables_customer_churn,
    calidad_variables_madelon,
    calidad_variables_olive_oil,
], ignore_index=True)

guardar_tabla(calidad_datasets, "fase1_calidad_datasets.csv")
guardar_tabla(calidad_variables, "fase1_calidad_variables.csv")
display(calidad_datasets)
"""))
    cells.append(md("""
El resumen comparativo no detecta nulos, duplicados ni variables constantes en ninguno de los 4 datasets. Las alertas se concentran en baja cardinalidad relativa: 9 variables en `customer_churn`, 24 en `madelon`, 1 en `olive_oil` y 0 en `breast_cancer_wisconsin`; como no hay modas dominantes al 98%, la siguiente pregunta no es limpieza por defecto, sino cómo esas variables se relacionan con el target.
"""))

    cells.append(md("""
## 1.4 Análisis del Target

El target se analiza por dataset porque su distribución condiciona particiones, métricas y lectura de resultados. No se usa un umbral universal de desbalance: se informa la proporción de clases y el ratio entre clase mayoritaria y minoritaria.
"""))
    cells.append(code("""
def calcular_distribucion_target(nombre_dataset, datos_dataset, target):
    conteos = datos_dataset[target].value_counts(dropna=False)
    proporciones = datos_dataset[target].value_counts(dropna=False, normalize=True)
    return pd.DataFrame({
        "dataset": nombre_dataset,
        "target": target,
        "clase": conteos.index.astype(str),
        "n": conteos.values,
        "proporcion": proporciones.values,
    })


def resumir_balance_target(distribucion_target):
    clase_mayor = distribucion_target.sort_values("n", ascending=False).iloc[0]
    clase_menor = distribucion_target.sort_values("n", ascending=True).iloc[0]
    hay_empate = clase_mayor["n"] == clase_menor["n"]
    return {
        "dataset": distribucion_target["dataset"].iloc[0],
        "target": distribucion_target["target"].iloc[0],
        "n_clases": len(distribucion_target),
        "clase_mayoritaria": "empate" if hay_empate else clase_mayor["clase"],
        "clase_minoritaria": "empate" if hay_empate else clase_menor["clase"],
        "ratio_mayoritaria_minoritaria": clase_mayor["n"] / clase_menor["n"],
    }
"""))
    cells.append(code("""
def anotar_barras_target(eje, distribucion_target):
    for contenedor in eje.containers:
        etiquetas = [f"{proporcion:.1%}" for proporcion in distribucion_target["proporcion"]]
        eje.bar_label(contenedor, labels=etiquetas, padding=3, fontsize=9)


def graficar_target_dataset(distribucion_target):
    nombre_dataset = distribucion_target["dataset"].iloc[0]
    datos_grafico = distribucion_target.sort_values("proporcion", ascending=True)
    alto_figura = max(3.2, 0.42 * len(datos_grafico) + 1.8)
    figura, eje = plt.subplots(figsize=(8.5, alto_figura))
    sns.barplot(datos_grafico, y="clase", x="proporcion", color=PALETA_DATASETS[nombre_dataset], ax=eje)
    eje.set_title(f"Distribución del target en {nombre_dataset}")
    eje.set_xlabel("proporción")
    eje.set_ylabel("")
    eje.xaxis.set_major_formatter(lambda valor, posicion: f"{valor:.0%}")
    aplicar_estilo_eje(eje)
    anotar_barras_target(eje, datos_grafico)
    figura.tight_layout()
    return figura


def graficar_desbalance_comparado(target_resumen):
    datos_grafico = target_resumen.set_index("dataset").loc[ORDEN_DATASETS].reset_index()
    datos_grafico = datos_grafico.sort_values("ratio_mayoritaria_minoritaria")
    figura, eje = plt.subplots(figsize=(9, 4.8))
    colores = [
        PALETA_DATASETS[dataset] if dataset == datos_grafico.iloc[-1]["dataset"] else "#B8B0A3"
        for dataset in datos_grafico["dataset"]
    ]
    eje.barh(datos_grafico["dataset"], datos_grafico["ratio_mayoritaria_minoritaria"], color=colores)
    eje.axvline(1, color="#6F6A60", linewidth=1.1, linestyle="--")
    eje.set_title("Olive Oil concentra el mayor desbalance del target")
    eje.set_xlabel("ratio clase mayoritaria / minoritaria")
    eje.set_ylabel("")
    aplicar_estilo_eje(eje)
    caso_extremo = datos_grafico.iloc[-1]
    eje.annotate(
        f'{caso_extremo["ratio_mayoritaria_minoritaria"]:.2f}:1',
        xy=(caso_extremo["ratio_mayoritaria_minoritaria"], caso_extremo["dataset"]),
        xytext=(caso_extremo["ratio_mayoritaria_minoritaria"] * 0.78, caso_extremo["dataset"]),
        va="center",
        ha="right",
        arrowprops={"arrowstyle": "->", "color": "#6F6A60", "lw": 1},
    )
    for _, fila in datos_grafico.iloc[:-1].iterrows():
        eje.text(fila["ratio_mayoritaria_minoritaria"] + 0.08, fila["dataset"], f'{fila["ratio_mayoritaria_minoritaria"]:.2f}:1', va="center")
    figura.tight_layout()
    return figura
"""))

    target_obs = {
        "breast_cancer_wisconsin": "El target es binario y la clase `B` es mayoritaria. El ratio mayoritaria/minoritaria es 1,684, por lo que en modelado conviene no depender solo de accuracy.",
        "customer_churn": "El target es binario y `1.0` es la clase mayoritaria. El tamaño muestral es grande, así que pequeñas diferencias pueden resultar estadísticamente significativas.",
        "madelon": "El target está perfectamente balanceado: las dos clases tienen 1.000 observaciones. El reto principal no es el desbalance, sino la dimensionalidad y el ruido.",
        "olive_oil": "El target tiene 9 clases y `South-Apulia` domina frente a clases pequeñas como `North-Apulia`, con ratio 8,240. Las fases posteriores deberán preservar clases minoritarias.",
    }
    add_dataset_cells(
        cells,
        "Target",
        """
target_distribucion_{variable_name} = calcular_distribucion_target(
    "{dataset_name}",
    {variable_name},
    targets_esperados["{dataset_name}"],
)
target_resumen_{variable_name} = pd.DataFrame([resumir_balance_target(target_distribucion_{variable_name})])

display(target_resumen_{variable_name}.style.format({{"ratio_mayoritaria_minoritaria": "{{:.3f}}"}}))
display(target_distribucion_{variable_name}.style.format({{"proporcion": "{{:.2%}}"}}))
""",
        target_obs,
    )

    cells.append(md("""
### Resumen Comparativo del Target

Después de revisar cada distribución, se conserva una tabla conjunta para consultar número de clases y ratio de balance.
"""))
    cells.append(code("""
target_distribucion = pd.concat([
    target_distribucion_breast_cancer_wisconsin,
    target_distribucion_customer_churn,
    target_distribucion_madelon,
    target_distribucion_olive_oil,
], ignore_index=True)

target_resumen = pd.concat([
    target_resumen_breast_cancer_wisconsin,
    target_resumen_customer_churn,
    target_resumen_madelon,
    target_resumen_olive_oil,
], ignore_index=True)

guardar_tabla(target_distribucion, "fase1_target_distribucion.csv")
guardar_tabla(target_resumen, "fase1_target_resumen.csv")
display(target_resumen.style.format({"ratio_mayoritaria_minoritaria": "{:.3f}"}))

figura = graficar_desbalance_comparado(target_resumen)
ruta_figura = guardar_figura(figura, "01_04_target_desbalance_comparado.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
"""))
    cells.append(md("""
La comparación resume los cuatro targets sin repetir las tablas de distribución. `madelon` queda exactamente balanceado con ratio 1,000; `customer_churn` alcanza 1,310; `breast_cancer_wisconsin` sube a 1,684; y `olive_oil` es el caso extremo con 9 clases y ratio 8,240 entre `South-Apulia` y `North-Apulia`. Esta lectura deja abierta la necesidad de estratificación, que se comprobará al construir particiones en fases posteriores.
"""))

    cells.append(md("""
## 1.5 Muestreo Visual

El muestreo visual solo se aplica cuando una figura sería difícil de leer por tamaño muestral. No sustituye los cálculos estadísticos sobre datos completos. Si se muestrea, se comprueba la distribución del target completo frente a la muestra.
"""))
    cells.append(code("""
def necesita_muestra_visual(datos_dataset):
    return len(datos_dataset) > MAX_FILAS_MUESTRA_VISUAL


def calcular_fraccion_muestreo(datos_dataset):
    return MAX_FILAS_MUESTRA_VISUAL / len(datos_dataset)


def crear_muestra_estratificada(datos_dataset, target):
    fraccion = calcular_fraccion_muestreo(datos_dataset)
    return (
        datos_dataset
        .groupby(target, group_keys=False, dropna=False)
        .sample(frac=fraccion, random_state=RANDOM_STATE)
        .sample(frac=1, random_state=RANDOM_STATE)
        .reset_index(drop=True)
    )


def crear_muestra_visual_dataset(datos_dataset, target):
    if necesita_muestra_visual(datos_dataset):
        return crear_muestra_estratificada(datos_dataset, target), "muestra_estratificada_visual"
    return datos_dataset.copy(), "completo"
"""))
    cells.append(code("""
def comparar_target_completo_muestra(nombre_dataset, datos_dataset, muestra_visual, target):
    completo = datos_dataset[target].value_counts(normalize=True, dropna=False)
    muestra = muestra_visual[target].value_counts(normalize=True, dropna=False)
    return pd.DataFrame([
        {
            "dataset": nombre_dataset,
            "clase": str(clase),
            "proporcion_completa": completo.loc[clase],
            "proporcion_muestra_visual": muestra.get(clase, np.nan),
            "diferencia_absoluta": abs(completo.loc[clase] - muestra.get(clase, np.nan)),
        }
        for clase in completo.index
    ])


def resumir_muestra_visual(nombre_dataset, datos_dataset, muestra_visual, tipo_muestra):
    return pd.DataFrame([{
        "dataset": nombre_dataset,
        "filas_originales": len(datos_dataset),
        "filas_muestra_visual": len(muestra_visual),
        "tipo_muestra": tipo_muestra,
    }])
"""))

    sampling_obs = {
        "breast_cancer_wisconsin": "El dataset conserva sus 569 filas porque queda por debajo del límite visual de 5.000. Las visualizaciones pueden usar el conjunto completo.",
        "customer_churn": "Se crea una muestra visual estratificada de 5.000 filas. La comparación del target permite comprobar que la muestra conserva prácticamente las proporciones originales.",
        "madelon": "`madelon` mantiene sus 2.000 filas completas. El problema principal es dimensional, no de volumen muestral para visualización.",
        "olive_oil": "`olive_oil` conserva 572 filas. Dado su target de 9 clases, mantener todas las observaciones evita perder clases minoritarias en diagnósticos visuales.",
    }
    add_dataset_cells(
        cells,
        "Muestreo Visual",
        """
muestra_visual_{variable_name}, tipo_muestra_{variable_name} = crear_muestra_visual_dataset(
    {variable_name},
    targets_esperados["{dataset_name}"],
)
muestreo_{variable_name} = resumir_muestra_visual(
    "{dataset_name}",
    {variable_name},
    muestra_visual_{variable_name},
    tipo_muestra_{variable_name},
)
target_muestra_{variable_name} = comparar_target_completo_muestra(
    "{dataset_name}",
    {variable_name},
    muestra_visual_{variable_name},
    targets_esperados["{dataset_name}"],
)

display(muestreo_{variable_name})
display(target_muestra_{variable_name}.style.format({{
    "proporcion_completa": "{{:.3%}}",
    "proporcion_muestra_visual": "{{:.3%}}",
    "diferencia_absoluta": "{{:.4%}}",
}}))
""",
        sampling_obs,
    )
    cells.append(code("""
muestras_visuales = {
    "breast_cancer_wisconsin": muestra_visual_breast_cancer_wisconsin,
    "customer_churn": muestra_visual_customer_churn,
    "madelon": muestra_visual_madelon,
    "olive_oil": muestra_visual_olive_oil,
}

muestreo_resumen = pd.concat([
    muestreo_breast_cancer_wisconsin,
    muestreo_customer_churn,
    muestreo_madelon,
    muestreo_olive_oil,
], ignore_index=True)
muestreo_target = pd.concat([
    target_muestra_breast_cancer_wisconsin,
    target_muestra_customer_churn,
    target_muestra_madelon,
    target_muestra_olive_oil,
], ignore_index=True)

guardar_tabla(muestreo_resumen, "fase1_muestreo_visual_resumen.csv")
guardar_tabla(muestreo_target, "fase1_muestreo_visual_target.csv")
display(muestreo_resumen)
"""))
    cells.append(md("""
El cierre de muestreo deja 3 datasets completos y 1 dataset reducido solo para visualización. `customer_churn` pasa de 440.832 a 5.000 filas visuales mediante muestreo estratificado; `breast_cancer_wisconsin`, `madelon` y `olive_oil` conservan 569, 2.000 y 572 filas respectivamente. Los cálculos estadísticos posteriores siguen usando datos completos salvo que se indique muestra visual.
"""))

    cells.append(md("""
## 1.6 Análisis Univariante de Variables Numéricas

El análisis univariante busca asimetría, colas pesadas y outliers estadísticos. La técnica combina estadísticos descriptivos, skewness, kurtosis y tasa de outliers por criterio IQR 1,5; se calcula una tabla completa por dataset y se visualizan variables seleccionadas por señal empírica, no una única variable arbitraria.
"""))
    cells.append(code("""
def obtener_columnas_numericas_predictoras(datos_dataset, target):
    columnas_predictoras = obtener_columnas_predictoras(datos_dataset, target)
    identificadores = set(listar_posibles_identificadores(datos_dataset, target))
    return [
        variable for variable in datos_dataset[columnas_predictoras].select_dtypes(include=np.number).columns
        if variable not in identificadores
    ]


def calcular_tasa_outliers_iqr(serie):
    serie_limpia = serie.dropna()
    q1, q3 = serie_limpia.quantile([0.25, 0.75])
    rango_intercuartilico = q3 - q1
    if rango_intercuartilico == 0:
        return 0.0
    limite_inferior = q1 - 1.5 * rango_intercuartilico
    limite_superior = q3 + 1.5 * rango_intercuartilico
    return float(((serie_limpia < limite_inferior) | (serie_limpia > limite_superior)).mean())
"""))
    cells.append(code("""
def resumir_variable_numerica(nombre_dataset, variable, serie):
    return {
        "dataset": nombre_dataset,
        "variable": variable,
        "media": serie.mean(),
        "desviacion": serie.std(),
        "minimo": serie.min(),
        "mediana": serie.median(),
        "maximo": serie.max(),
        "skewness": serie.skew(),
        "kurtosis": serie.kurtosis(),
        "outlier_rate_iqr": calcular_tasa_outliers_iqr(serie),
        "missing_pct": serie.isna().mean(),
    }


def resumir_distribuciones_dataset(nombre_dataset, datos_dataset, target):
    columnas_numericas = obtener_columnas_numericas_predictoras(datos_dataset, target)
    return pd.DataFrame([
        resumir_variable_numerica(nombre_dataset, variable, datos_dataset[variable])
        for variable in columnas_numericas
    ])
"""))
    cells.append(code("""
def seleccionar_variables_univariantes(distribuciones_dataset, max_variables=4):
    variables_outliers = distribuciones_dataset.nlargest(max_variables, "outlier_rate_iqr")["variable"]
    variables_asimetria = (
        distribuciones_dataset
        .assign(skew_abs=lambda tabla: tabla["skewness"].abs())
        .nlargest(max_variables, "skew_abs")["variable"]
    )
    variables = pd.concat([variables_outliers, variables_asimetria]).drop_duplicates()
    return variables.head(max_variables).tolist()


def graficar_distribuciones_univariantes(nombre_dataset, datos_visual, variables_foco):
    numero_variables = len(variables_foco)
    figura, ejes = plt.subplots(1, numero_variables, figsize=(4.3 * numero_variables, 3.8))
    ejes = np.atleast_1d(ejes)
    for eje, variable in zip(ejes, variables_foco):
        sns.histplot(datos_visual[variable].dropna(), bins="auto", kde=True, color=PALETA_DATASETS[nombre_dataset], ax=eje)
        eje.set_title(variable)
        eje.set_xlabel("")
        aplicar_estilo_eje(eje, "y")
    figura.suptitle(f"Las colas y asimetrías se concentran en variables concretas de {nombre_dataset}", y=1.05)
    figura.tight_layout()
    return figura
"""))

    univariate_obs = {
        "breast_cancer_wisconsin": "La tabla muestra 30 variables numéricas y outlier rate máximo 11,42%, sobre todo en variables de error (`*_se`). Esto orienta a usar métodos robustos, no a eliminar observaciones automáticamente.",
        "customer_churn": "Las 7 variables numéricas son discretas o de rango acotado. La tasa de outliers IQR es 0,00% en esta revisión, por lo que el foco posterior será codificación e interpretación práctica.",
        "madelon": "Aunque hay 500 variables, las tasas medias de outliers son bajas. La revisión por ranking evita inspeccionar manualmente todas las columnas.",
        "olive_oil": "Las 10 variables numéricas presentan asimetría absoluta media 0,512 y outlier rate máximo 8,92%. Se conserva la lectura como diagnóstico previo al preprocesado.",
    }
    add_dataset_cells(
        cells,
        "Univariante Numérico",
        """
distribuciones_{variable_name} = resumir_distribuciones_dataset(
    "{dataset_name}",
    {variable_name},
    targets_esperados["{dataset_name}"],
)
variables_univariantes_{variable_name} = seleccionar_variables_univariantes(distribuciones_{variable_name})

display(
    distribuciones_{variable_name}
    .assign(skew_abs=lambda tabla: tabla["skewness"].abs())
    .sort_values(["outlier_rate_iqr", "skew_abs"], ascending=False)
    .head(10)
    .style.format({{
        "skewness": "{{:.3f}}",
        "kurtosis": "{{:.3f}}",
        "outlier_rate_iqr": "{{:.2%}}",
        "missing_pct": "{{:.2%}}",
    }})
)

figura = graficar_distribuciones_univariantes(
    "{dataset_name}",
    muestras_visuales["{dataset_name}"],
    variables_univariantes_{variable_name},
)
ruta_figura = guardar_figura(figura, "01_06_univariante_{dataset_name}.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
""",
        univariate_obs,
    )
    cells.append(code("""
distribuciones_numericas = pd.concat([
    distribuciones_breast_cancer_wisconsin,
    distribuciones_customer_churn,
    distribuciones_madelon,
    distribuciones_olive_oil,
], ignore_index=True)

resumen_univariante_dataset = (
    distribuciones_numericas
    .groupby("dataset")
    .agg(
        variables_numericas=("variable", "count"),
        outlier_rate_media=("outlier_rate_iqr", "mean"),
        outlier_rate_maxima=("outlier_rate_iqr", "max"),
        skew_abs_media=("skewness", lambda serie: serie.abs().mean()),
        skew_abs_maxima=("skewness", lambda serie: serie.abs().max()),
    )
    .reset_index()
)

guardar_tabla(distribuciones_numericas, "fase1_distribuciones_numericas.csv")
guardar_tabla(resumen_univariante_dataset, "fase1_univariante_resumen_dataset.csv")
display(resumen_univariante_dataset.style.format({
    "outlier_rate_media": "{:.2%}",
    "outlier_rate_maxima": "{:.2%}",
    "skew_abs_media": "{:.3f}",
    "skew_abs_maxima": "{:.3f}",
}))
"""))
    cells.append(md("""
El cierre univariante compara 547 variables numéricas en total. `madelon` aporta 500 variables y tiene outlier rate medio 0,90%, pero su máximo llega a 14,30%; `breast_cancer_wisconsin` concentra más asimetría, con skew absoluto medio 1,740 y máximo 5,447; `customer_churn` no muestra outliers IQR en sus 7 numéricas; y `olive_oil` queda en un punto intermedio con outlier rate máximo 8,92%. La siguiente sección comprueba si esas formas de distribución justifican abandonar supuestos paramétricos.
"""))

    cells.append(md("""
## 1.7 Normalidad Exploratoria

La normalidad se revisa como diagnóstico. El criterio técnico usa D'Agostino K² para variables con al menos 20 observaciones y Shapiro-Wilk para muestras menores; el resultado se acompaña con Q-Q plots de variables seleccionadas por menor p-valor para leer desviaciones de forma, no para imponer gaussianidad.
"""))
    cells.append(code("""
ALFA_NORMALIDAD = 0.05
"""))
    cells.append(code("""
def elegir_test_normalidad(serie):
    return "shapiro_wilk" if len(serie.dropna()) < 20 else "dagostino_k2"


def ejecutar_test_normalidad(serie):
    serie_limpia = serie.dropna()
    if len(serie_limpia) < 8:
        return np.nan, np.nan, "muestra_insuficiente"
    if elegir_test_normalidad(serie_limpia) == "shapiro_wilk":
        estadistico, p_valor = stats.shapiro(serie_limpia)
        return estadistico, p_valor, "shapiro_wilk"
    estadistico, p_valor = stats.normaltest(serie_limpia)
    return estadistico, p_valor, "dagostino_k2"


def resumir_normalidad_variable(nombre_dataset, variable, serie):
    estadistico, p_valor, test = ejecutar_test_normalidad(serie)
    return {
        "dataset": nombre_dataset,
        "variable": variable,
        "test": test,
        "estadistico": estadistico,
        "p_valor": p_valor,
        "rechaza_normalidad": bool(pd.notna(p_valor) and p_valor < ALFA_NORMALIDAD),
        "n_usado": int(serie.dropna().shape[0]),
    }
"""))
    cells.append(code("""
def resumir_normalidad_dataset(nombre_dataset, datos_visual, target):
    columnas_numericas = obtener_columnas_numericas_predictoras(datos_visual, target)
    return pd.DataFrame([
        resumir_normalidad_variable(nombre_dataset, variable, datos_visual[variable])
        for variable in columnas_numericas
    ])


def seleccionar_variables_qq(normalidad_dataset, max_variables=3):
    return normalidad_dataset.sort_values("p_valor").head(max_variables)["variable"].tolist()


def graficar_qq_dataset(nombre_dataset, datos_visual, variables_qq):
    figura, ejes = plt.subplots(1, len(variables_qq), figsize=(4.5 * len(variables_qq), 4))
    ejes = np.atleast_1d(ejes)
    for eje, variable in zip(ejes, variables_qq):
        stats.probplot(datos_visual[variable].dropna(), dist="norm", plot=eje)
        eje.get_lines()[0].set_markerfacecolor(PALETA_DATASETS[nombre_dataset])
        eje.get_lines()[0].set_markeredgecolor(PALETA_DATASETS[nombre_dataset])
        eje.get_lines()[0].set_markersize(3)
        eje.get_lines()[1].set_color("#2D2A26")
        eje.set_title(f"{variable}: desviación frente a normal")
        eje.grid(alpha=0.55)
    figura.suptitle(f"Los Q-Q plots muestran por qué la normalidad es solo un diagnóstico en {nombre_dataset}", y=1.05)
    figura.tight_layout()
    return figura
"""))

    normality_obs = {
        "breast_cancer_wisconsin": "Las 30 variables testadas rechazan normalidad al 100,0%, y las seleccionadas muestran desviaciones claras respecto a la recta normal coherentes con las asimetrías de 1.6.",
        "customer_churn": "El rechazo de normalidad alcanza el 100,0%, pero debe leerse con prudencia: varias variables son discretas y la muestra visual sigue teniendo 5.000 filas.",
        "madelon": "Solo el 22,8% de las 500 variables rechaza normalidad. Aun así, el diagnóstico principal de `madelon` sigue siendo la dimensionalidad.",
        "olive_oil": "Las 10 variables testadas rechazan normalidad al 100,0% y muestran patrones discretos o desviaciones visuales. Esto respalda el uso de pruebas no paramétricas en asociación.",
    }
    add_dataset_cells(
        cells,
        "Normalidad",
        """
normalidad_{variable_name} = resumir_normalidad_dataset(
    "{dataset_name}",
    muestras_visuales["{dataset_name}"],
    targets_esperados["{dataset_name}"],
)
variables_qq_{variable_name} = seleccionar_variables_qq(normalidad_{variable_name})
resumen_normalidad_{variable_name} = pd.DataFrame([{{
    "dataset": "{dataset_name}",
    "variables_testadas": len(normalidad_{variable_name}),
    "pct_rechaza_normalidad": normalidad_{variable_name}["rechaza_normalidad"].mean(),
    "n_minimo_usado": normalidad_{variable_name}["n_usado"].min(),
    "n_maximo_usado": normalidad_{variable_name}["n_usado"].max(),
}}])

display(resumen_normalidad_{variable_name}.style.format({{"pct_rechaza_normalidad": "{{:.1%}}"}}))
display(normalidad_{variable_name}.sort_values("p_valor").head(10).style.format({{
    "estadistico": "{{:.3f}}",
    "p_valor": "{{:.2e}}",
}}))

figura = graficar_qq_dataset("{dataset_name}", muestras_visuales["{dataset_name}"], variables_qq_{variable_name})
ruta_figura = guardar_figura(figura, "01_07_normalidad_{dataset_name}.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
""",
        normality_obs,
    )
    cells.append(code("""
normalidad_variables = pd.concat([
    normalidad_breast_cancer_wisconsin,
    normalidad_customer_churn,
    normalidad_madelon,
    normalidad_olive_oil,
], ignore_index=True)
normalidad_resumen = pd.concat([
    resumen_normalidad_breast_cancer_wisconsin,
    resumen_normalidad_customer_churn,
    resumen_normalidad_madelon,
    resumen_normalidad_olive_oil,
], ignore_index=True)

guardar_tabla(normalidad_variables, "fase1_normalidad_variables.csv")
guardar_tabla(normalidad_resumen, "fase1_normalidad_resumen.csv")
display(normalidad_resumen.style.format({"pct_rechaza_normalidad": "{:.1%}"}))
"""))
    cells.append(md("""
El resumen de normalidad muestra rechazo en el 100,0% de las variables de `breast_cancer_wisconsin`, `customer_churn` y `olive_oil`, mientras que `madelon` rechaza en el 22,8% de sus 500 variables. La muestra usada va de 569 filas en `breast_cancer_wisconsin` a 5.000 filas visuales en `customer_churn`, por lo que la lectura práctica es clara: las asociaciones de la sección siguiente deben apoyarse en pruebas no paramétricas y no en normalidad gaussiana.
"""))

    cells.append(md("""
## 1.8 Asociación Exploratoria Variable-Target

La asociación se calcula con pruebas distintas según el tipo de variable y target. Las funciones se introducen por bloques para que el lector vea qué se aplica y por qué. Esta sección es el precursor clásico del término de relevancia del método QFS: en el paper, la relevancia de cada variable se expresa como información mutua `I(x_i; y)` y se codifica en detunings locales dentro del objetivo `Q(x; alpha)`. Aquí todavía no se estima esa MI final, pero sí se identifica qué variables muestran relación univariante con el target y cómo debe leerse esa señal antes de selección.
"""))
    cells.append(code("""
ALFA_ASOCIACION = 0.05
"""))
    cells.append(md("""
### Mann-Whitney U y Delta de Cliff

Se usan para variables numéricas frente a target binario. Mann-Whitney evalúa diferencias de distribución entre dos grupos y delta de Cliff resume la magnitud de la separación.
"""))
    cells.append(code("""
def separar_grupos_por_target(datos_dataset, variable, target):
    clases = list(pd.Series(datos_dataset[target]).dropna().unique())
    return [datos_dataset.loc[datos_dataset[target] == clase, variable].dropna() for clase in clases]


def calcular_delta_cliff_desde_u(estadistico_u, grupo_a, grupo_b):
    return (2 * estadistico_u / (len(grupo_a) * len(grupo_b))) - 1


def contrastar_numerica_binaria(datos_dataset, variable, target):
    grupo_a, grupo_b = separar_grupos_por_target(datos_dataset, variable, target)
    estadistico_u, p_valor = stats.mannwhitneyu(grupo_a, grupo_b, alternative="two-sided")
    efecto = calcular_delta_cliff_desde_u(estadistico_u, grupo_a, grupo_b)
    return "mann_whitney_u", estadistico_u, p_valor, "cliffs_delta", efecto
"""))
    cells.append(md("""
### Kruskal-Wallis y Epsilon Cuadrado

Se usan para variables numéricas frente a targets con más de dos clases. Kruskal-Wallis compara grupos sin asumir normalidad y epsilon cuadrado aproxima magnitud de efecto.
"""))
    cells.append(code("""
def calcular_epsilon_cuadrado(estadistico_h, numero_observaciones, numero_grupos):
    if numero_observaciones <= numero_grupos:
        return np.nan
    return (estadistico_h - numero_grupos + 1) / (numero_observaciones - numero_grupos)


def contrastar_numerica_multiclase(datos_dataset, variable, target):
    grupos = separar_grupos_por_target(datos_dataset, variable, target)
    estadistico_h, p_valor = stats.kruskal(*grupos)
    numero_observaciones = sum(len(grupo) for grupo in grupos)
    efecto = calcular_epsilon_cuadrado(estadistico_h, numero_observaciones, len(grupos))
    return "kruskal_wallis", estadistico_h, p_valor, "epsilon_squared", efecto
"""))
    cells.append(md("""
### Chi-Cuadrado y V de Cramér

Se usan para variables categóricas frente al target. Chi-cuadrado contrasta independencia y V de Cramér resume la fuerza de asociación entre categorías.
"""))
    cells.append(code("""
def calcular_cramers_v(tabla_contingencia):
    chi2 = stats.chi2_contingency(tabla_contingencia, correction=False)[0]
    numero_observaciones = tabla_contingencia.to_numpy().sum()
    filas, columnas = tabla_contingencia.shape
    return np.sqrt((chi2 / numero_observaciones) / max(1, min(columnas - 1, filas - 1)))


def contrastar_categorica(datos_dataset, variable, target):
    tabla_contingencia = pd.crosstab(datos_dataset[variable], datos_dataset[target])
    estadistico, p_valor, _, _ = stats.chi2_contingency(tabla_contingencia)
    efecto = calcular_cramers_v(tabla_contingencia)
    return "chi2", estadistico, p_valor, "cramers_v", efecto
"""))
    cells.append(md("""
### Corrección FDR de Benjamini-Hochberg

FDR significa *False Discovery Rate*. La corrección de Benjamini-Hochberg reduce la sobreinterpretación de p-valores cuando se prueban muchas variables en el mismo dataset.
"""))
    cells.append(code("""
def corregir_p_valores_bh(p_valores):
    p_valores = np.asarray(p_valores, dtype=float)
    resultado = np.full(p_valores.shape, np.nan)
    mascara = ~np.isnan(p_valores)
    valores_validos = p_valores[mascara]
    if len(valores_validos) == 0:
        return resultado
    orden = np.argsort(valores_validos)
    valores_ordenados = valores_validos[orden]
    factores = len(valores_ordenados) / np.arange(1, len(valores_ordenados) + 1)
    ajustados = np.minimum.accumulate((valores_ordenados * factores)[::-1])[::-1]
    valores_ajustados = np.empty_like(ajustados)
    valores_ajustados[orden] = np.clip(ajustados, 0, 1)
    resultado[mascara] = valores_ajustados
    return resultado
"""))
    cells.append(code("""
def target_es_binario(datos_dataset, target):
    return datos_dataset[target].nunique(dropna=True) == 2


def contrastar_variable_con_target(datos_dataset, variable, target):
    if pd.api.types.is_numeric_dtype(datos_dataset[variable]):
        if target_es_binario(datos_dataset, target):
            return contrastar_numerica_binaria(datos_dataset, variable, target)
        return contrastar_numerica_multiclase(datos_dataset, variable, target)
    return contrastar_categorica(datos_dataset, variable, target)


def construir_fila_asociacion(nombre_dataset, datos_dataset, variable, target):
    test, estadistico, p_valor, nombre_efecto, efecto = contrastar_variable_con_target(datos_dataset, variable, target)
    return {
        "dataset": nombre_dataset,
        "variable": variable,
        "test": test,
        "estadistico": estadistico,
        "p_valor": p_valor,
        "nombre_tamano_efecto": nombre_efecto,
        "tamano_efecto": efecto,
    }


def aplicar_fdr_y_magnitud(asociaciones_dataset):
    asociaciones_dataset["p_valor_fdr"] = corregir_p_valores_bh(asociaciones_dataset["p_valor"].to_numpy())
    asociaciones_dataset["abs_tamano_efecto"] = asociaciones_dataset["tamano_efecto"].abs()
    return asociaciones_dataset


def calcular_asociaciones_dataset(nombre_dataset, datos_dataset, target):
    variables_excluidas = set(listar_posibles_identificadores(datos_dataset, target))
    variables_validas = [variable for variable in obtener_columnas_predictoras(datos_dataset, target) if variable not in variables_excluidas]
    asociaciones_dataset = pd.DataFrame([
        construir_fila_asociacion(nombre_dataset, datos_dataset, variable, target)
        for variable in variables_validas
    ])
    return aplicar_fdr_y_magnitud(asociaciones_dataset)
"""))
    cells.append(code("""
def preparar_top_significancia(asociaciones_dataset, max_variables=12):
    return asociaciones_dataset.nsmallest(max_variables, "p_valor_fdr").copy()


def calcular_menos_log10_fdr(asociaciones_dataset):
    return -np.log10(asociaciones_dataset["p_valor_fdr"].clip(lower=1e-300))


def graficar_top_significancia(nombre_dataset, asociaciones_dataset):
    datos_grafico = preparar_top_significancia(asociaciones_dataset)
    datos_grafico["menos_log10_fdr"] = calcular_menos_log10_fdr(datos_grafico).clip(upper=50)
    datos_grafico = datos_grafico.sort_values("menos_log10_fdr")
    figura, eje = plt.subplots(figsize=(9, max(4.2, 0.38 * len(datos_grafico) + 1.6)))
    eje.barh(datos_grafico["variable"], datos_grafico["menos_log10_fdr"], color=PALETA_DATASETS[nombre_dataset])
    eje.axvline(-np.log10(ALFA_ASOCIACION), color="#B85C5C", linestyle="--", linewidth=1)
    eje.set_title(f"La relevancia exploratoria se concentra en el top FDR de {nombre_dataset}")
    eje.set_xlabel("-log10(FDR), capado en 50")
    eje.set_ylabel("")
    aplicar_estilo_eje(eje)
    eje.text(-np.log10(ALFA_ASOCIACION) + 0.3, eje.get_ylim()[0] + 0.4, "FDR=0,05", color="#B85C5C", fontsize=9)
    figura.tight_layout()
    return figura
"""))

    association_obs = {
        "breast_cancer_wisconsin": "La asociación univariante es fuerte: 27 de 30 variables quedan con FDR < 0,05. La lectura sigue siendo exploratoria porque muchas variables pueden estar correlacionadas entre sí.",
        "customer_churn": "Las 10 variables contrastadas son significativas tras FDR, pero el tamaño muestral de 440.832 filas exige mirar también la magnitud del efecto.",
        "madelon": "Aparecen señales univariantes, pero son escasas frente a 500 variables. Esta sección ya anticipa que la selección de características será crítica.",
        "olive_oil": "Las 10 variables numéricas muestran asociación fuerte con el target de 9 clases. Algunas señales pueden actuar como proxies de región y se revisan en la sección de cautelas.",
    }
    add_dataset_cells(
        cells,
        "Asociación Variable-Target",
        """
asociacion_{variable_name} = calcular_asociaciones_dataset(
    "{dataset_name}",
    {variable_name},
    targets_esperados["{dataset_name}"],
)

display(
    asociacion_{variable_name}
    .sort_values("p_valor_fdr", ascending=True)
    .head(12)
    .style.format({{
        "p_valor": "{{:.2e}}",
        "p_valor_fdr": "{{:.2e}}",
        "tamano_efecto": "{{:.4f}}",
        "abs_tamano_efecto": "{{:.4f}}",
    }})
)

figura = graficar_top_significancia("{dataset_name}", asociacion_{variable_name})
ruta_figura = guardar_figura(figura, "01_08_asociacion_{dataset_name}.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
""",
        association_obs,
    )
    cells.append(code("""
asociacion_target = pd.concat([
    asociacion_breast_cancer_wisconsin,
    asociacion_customer_churn,
    asociacion_madelon,
    asociacion_olive_oil,
], ignore_index=True)
resumen_asociacion_target = (
    asociacion_target
    .groupby("dataset")
    .agg(
        variables_contrastadas=("variable", "count"),
        variables_fdr_005=("p_valor_fdr", lambda serie: int((serie < ALFA_ASOCIACION).sum())),
        efecto_abs_mediano=("abs_tamano_efecto", "median"),
        efecto_abs_maximo=("abs_tamano_efecto", "max"),
    )
    .reset_index()
)
guardar_tabla(asociacion_target, "fase1_asociacion_target.csv")
guardar_tabla(resumen_asociacion_target, "fase1_asociacion_target_resumen.csv")
display(resumen_asociacion_target.style.format({
    "efecto_abs_mediano": "{:.4f}",
    "efecto_abs_maximo": "{:.4f}",
}))
"""))
    cells.append(md("""
La vista conjunta separa cantidad de señal y magnitud. `breast_cancer_wisconsin` conserva 27 de 30 variables con FDR < 0,05 y efecto máximo 0,9509; `customer_churn` marca 10 de 10, aunque su efecto mediano mezcla numéricas y categóricas; `madelon` solo mantiene 13 de 500 pese a contrastar muchas variables; y `olive_oil` conserva 10 de 10 con efecto máximo 1,0000. Esta tabla deja preparada la lectura de FDR y magnitud sin convertir todavía la asociación en selección final.
"""))

    cells.append(md("""
## 1.9 Significancia Corregida Por Múltiples Contrastes

Se revisa, dataset por dataset, cuántas variables son significativas antes y después de FDR. La técnica aplicada es Benjamini-Hochberg con alfa 0,05, y el objetivo es detectar señales que podrían ser falsos positivos exploratorios.
"""))
    cells.append(code("""
ALFA_FDR = 0.05


def resumir_fdr_dataset(asociaciones_dataset):
    return pd.DataFrame([{
        "dataset": asociaciones_dataset["dataset"].iloc[0],
        "variables_contrastadas": len(asociaciones_dataset),
        "significativas_sin_corregir": int((asociaciones_dataset["p_valor"] < ALFA_FDR).sum()),
        "significativas_fdr": int((asociaciones_dataset["p_valor_fdr"] < ALFA_FDR).sum()),
    }]).assign(
        reduccion_por_correccion=lambda tabla: tabla["significativas_sin_corregir"] - tabla["significativas_fdr"]
    )


def seleccionar_variables_perdidas_por_fdr(asociaciones_dataset):
    mascara = (asociaciones_dataset["p_valor"] < ALFA_FDR) & (asociaciones_dataset["p_valor_fdr"] >= ALFA_FDR)
    return asociaciones_dataset[mascara].sort_values("p_valor")
"""))

    fdr_obs = {
        "breast_cancer_wisconsin": "La corrección FDR no reduce el número de variables significativas: se mantienen 27 de 30. La cautela principal no es el falso positivo aislado, sino la redundancia entre variables.",
        "customer_churn": "La corrección FDR tampoco reduce el número de variables significativas: permanecen 10 de 10. Por el tamaño muestral, la magnitud del efecto sigue siendo imprescindible.",
        "madelon": "La corrección FDR reduce las variables significativas de 38 a 13. Esto confirma que parte de la señal sin corregir puede ser ruido exploratorio.",
        "olive_oil": "Las variables contrastadas sobreviven a FDR. Dado que el target es multiclase y algunas señales son muy fuertes, se revisan posibles proxies en 1.13.",
    }
    add_dataset_cells(
        cells,
        "FDR",
        """
fdr_{variable_name} = resumir_fdr_dataset(asociacion_{variable_name})
perdidas_fdr_{variable_name} = seleccionar_variables_perdidas_por_fdr(asociacion_{variable_name})

display(fdr_{variable_name})
if perdidas_fdr_{variable_name}.empty:
    display(Markdown("No hay variables que pierdan significancia tras FDR."))
else:
    display(perdidas_fdr_{variable_name}.style.format({{
        "p_valor": "{{:.2e}}",
        "p_valor_fdr": "{{:.2e}}",
        "tamano_efecto": "{{:.4f}}",
    }}))
""",
        fdr_obs,
    )
    cells.append(code("""
resumen_fdr = pd.concat([
    fdr_breast_cancer_wisconsin,
    fdr_customer_churn,
    fdr_madelon,
    fdr_olive_oil,
], ignore_index=True)

guardar_tabla(resumen_fdr, "fase1_fdr_resumen.csv")
display(resumen_fdr)
"""))
    cells.append(md("""
La corrección por múltiples contrastes apenas cambia los datasets con señal fuerte: `breast_cancer_wisconsin` mantiene 27 variables significativas, `customer_churn` mantiene 10 y `olive_oil` mantiene 10. El contraste decisivo aparece en `madelon`, donde las variables significativas bajan de 38 a 13 y la reducción por corrección es 25; por tanto, este dataset será el banco más exigente para separar relevancia de ruido.
"""))

    cells.append(md("""
## 1.10 Magnitud del Efecto

La magnitud del efecto se interpreta por métrica. `cliffs_delta`, `epsilon_squared` y `cramers_v` no significan exactamente lo mismo; por eso se revisan por dataset y junto a la prueba aplicada. Su papel metodológico enlaza con la relevancia `I(x_i; y)` de QFS: antes de construir el término de detuning local del objetivo `Q(x; alpha)`, conviene distinguir señales estadísticamente detectables de efectos con tamaño práctico suficiente.
"""))
    cells.append(code("""
def resumir_tamano_efecto_dataset(asociaciones_dataset):
    return (
        asociaciones_dataset
        .groupby("nombre_tamano_efecto")
        .agg(
            variables=("variable", "count"),
            efecto_abs_mediano=("abs_tamano_efecto", "median"),
            efecto_abs_maximo=("abs_tamano_efecto", "max"),
        )
        .reset_index()
    )


def graficar_tamano_efecto_dataset(nombre_dataset, asociaciones_dataset):
    datos_grafico = asociaciones_dataset.nlargest(12, "abs_tamano_efecto").sort_values("abs_tamano_efecto")
    figura, eje = plt.subplots(figsize=(9, max(4.2, 0.38 * len(datos_grafico) + 1.6)))
    eje.hlines(datos_grafico["variable"], 0, datos_grafico["abs_tamano_efecto"], color="#B8B0A3", linewidth=2)
    eje.scatter(datos_grafico["abs_tamano_efecto"], datos_grafico["variable"], color=PALETA_DATASETS[nombre_dataset], s=70)
    eje.set_title(f"La magnitud práctica ordena las señales de {nombre_dataset}")
    eje.set_xlabel("|tamaño de efecto|")
    eje.set_ylabel("")
    aplicar_estilo_eje(eje)
    figura.tight_layout()
    return figura
"""))
    effect_obs = {
        "breast_cancer_wisconsin": "Los mayores tamaños de efecto corresponden a variables diagnósticas numéricas, con Cliff máximo 0,9509. Esto no equivale a independencia entre variables, que se revisa en redundancia.",
        "customer_churn": "La significancia estadística convive con efectos de distinta magnitud: Cliff mediano 0,2285 y V de Cramér mediano 0,1754. La tabla separa relevancia práctica de tamaño muestral.",
        "madelon": "Los tamaños de efecto son más moderados que en otros datasets: Cliff mediano 0,0195 y máximo 0,2621. Esto es coherente con un problema diseñado para contener ruido y señal dispersa.",
        "olive_oil": "La magnitud del efecto es alta frente al target multiclase, con epsilon squared mediano 0,7972 y máximo 1,0000. Esta fuerza requiere revisión semántica para evitar proxies directos.",
    }
    add_dataset_cells(
        cells,
        "Magnitud del Efecto",
        """
efecto_resumen_{variable_name} = resumir_tamano_efecto_dataset(asociacion_{variable_name})
display(efecto_resumen_{variable_name}.style.format({{
    "efecto_abs_mediano": "{{:.4f}}",
    "efecto_abs_maximo": "{{:.4f}}",
}}))

figura = graficar_tamano_efecto_dataset("{dataset_name}", asociacion_{variable_name})
ruta_figura = guardar_figura(figura, "01_10_efecto_{dataset_name}.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
""",
        effect_obs,
    )
    cells.append(code("""
resumen_efecto = pd.concat([
    efecto_resumen_breast_cancer_wisconsin.assign(dataset="breast_cancer_wisconsin"),
    efecto_resumen_customer_churn.assign(dataset="customer_churn"),
    efecto_resumen_madelon.assign(dataset="madelon"),
    efecto_resumen_olive_oil.assign(dataset="olive_oil"),
], ignore_index=True)
guardar_tabla(resumen_efecto, "fase1_tamano_efecto_resumen.csv")
display(resumen_efecto.style.format({
    "efecto_abs_mediano": "{:.4f}",
    "efecto_abs_maximo": "{:.4f}",
}))
"""))
    cells.append(md("""
El resumen de efecto muestra perfiles muy distintos. `olive_oil` alcanza epsilon squared mediano 0,7972 y máximo 1,0000; `breast_cancer_wisconsin` tiene Cliff mediano 0,6541 y máximo 0,9509; `customer_churn` combina Cliff mediano 0,2285 con V de Cramér mediano 0,1754; y `madelon` queda mucho más bajo, con Cliff mediano 0,0195 y máximo 0,2621. La pregunta que queda abierta es si las variables de mayor efecto son independientes o redundantes.
"""))

    cells.append(md("""
## 1.11 Redundancia y Correlación Entre Variables

La redundancia se revisa con Spearman porque mide asociación monótona sin exigir normalidad. El umbral `|rho| >= 0.85` se usa como alerta exploratoria de correlación fuerte, no como regla automática de eliminación. En el paper QFS, las secciones II-IV formulan la redundancia por pares como `R_ij` y la embeben en distancias atómicas mediante MDS para que el bloqueo de Rydberg penalice excitaciones redundantes; esta sección prepara ese mismo razonamiento desde resultados clásicos.
"""))
    cells.append(code("""
UMBRAL_CORRELACION_ALTA = 0.85
"""))
    cells.append(code("""
def calcular_matriz_spearman(datos_dataset, target):
    columnas_numericas = obtener_columnas_numericas_predictoras(datos_dataset, target)
    return datos_dataset[columnas_numericas].corr(method="spearman")


def convertir_matriz_correlacion_a_pares(nombre_dataset, matriz_correlacion):
    filas_resultado = []
    columnas = matriz_correlacion.columns
    for posicion, variable_a in enumerate(columnas):
        for variable_b in columnas[posicion + 1:]:
            correlacion = matriz_correlacion.loc[variable_a, variable_b]
            filas_resultado.append({
                "dataset": nombre_dataset,
                "variable_a": variable_a,
                "variable_b": variable_b,
                "spearman": correlacion,
                "abs_spearman": abs(correlacion),
            })
    return pd.DataFrame(filas_resultado)


def resumir_redundancia_dataset(pares_correlacion):
    return pd.DataFrame([{
        "dataset": pares_correlacion["dataset"].iloc[0],
        "pares_evaluados": len(pares_correlacion),
        "pares_correlacion_alta": int((pares_correlacion["abs_spearman"] >= UMBRAL_CORRELACION_ALTA).sum()),
        "correlacion_abs_maxima": pares_correlacion["abs_spearman"].max(),
    }])
"""))
    cells.append(code("""
def seleccionar_variables_heatmap(pares_correlacion, max_pares=8):
    pares_top = pares_correlacion.nlargest(max_pares, "abs_spearman")
    variables = pd.unique(pares_top[["variable_a", "variable_b"]].to_numpy().ravel())
    return variables.tolist()


def dibujar_ranking_correlaciones(eje, pares_top):
    etiquetas = pares_top["variable_a"] + " / " + pares_top["variable_b"]
    colores = ["#B8B0A3" if valor < UMBRAL_CORRELACION_ALTA else "#B85C5C" for valor in pares_top["abs_spearman"]]
    eje.barh(etiquetas, pares_top["abs_spearman"], color=colores)
    eje.axvline(UMBRAL_CORRELACION_ALTA, color="#6F6A60", linestyle="--", linewidth=1)
    eje.set_xlabel("|Spearman|")
    eje.set_ylabel("")
    aplicar_estilo_eje(eje)


def graficar_redundancia_dataset(nombre_dataset, matriz_correlacion, pares_correlacion):
    variables_heatmap = seleccionar_variables_heatmap(pares_correlacion)
    pares_top = pares_correlacion.nlargest(8, "abs_spearman").sort_values("abs_spearman")
    figura, ejes = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1.05, 1.25]})
    sns.heatmap(
        matriz_correlacion.loc[variables_heatmap, variables_heatmap],
        vmin=-1,
        vmax=1,
        center=0,
        cmap="vlag",
        ax=ejes[0],
        cbar_kws={"label": "Spearman"},
    )
    ejes[0].set_title("Submatriz de variables implicadas")
    ejes[0].tick_params(axis="x", labelrotation=90, labelsize=8)
    ejes[0].tick_params(axis="y", labelsize=8)
    dibujar_ranking_correlaciones(ejes[1], pares_top)
    ejes[1].set_title("Pares más redundantes")
    ejes[1].text(UMBRAL_CORRELACION_ALTA + 0.01, ejes[1].get_ylim()[0] + 0.4, "|rho|=0,85", color="#6F6A60", fontsize=9)
    n_pares_altos = int((pares_correlacion["abs_spearman"] >= UMBRAL_CORRELACION_ALTA).sum())
    figura.suptitle(f"{nombre_dataset} presenta {n_pares_altos} pares por encima de |rho|=0,85", y=1.03)
    figura.tight_layout()
    return figura
"""))
    redundancy_obs = {
        "breast_cancer_wisconsin": "Se observan 29 pares con `|Spearman| >= 0,85` y correlación máxima 1,000 entre variables de la misma familia diagnóstica. Este dataset necesitará control de redundancia.",
        "customer_churn": "No aparecen pares por encima de `|Spearman| >= 0.85`. La redundancia lineal/monótona no parece la principal cautela en este dataset.",
        "madelon": "Aparecen 12 pares con `|Spearman| >= 0,85` dentro de una matriz de 124.750 pares. El problema sigue siendo tanto dimensional como de señal dispersa.",
        "olive_oil": "Aparecen 2 pares altamente correlacionados entre 45 pares de variables de composición. La redundancia debe considerarse antes de selección de características.",
    }
    add_dataset_cells(
        cells,
        "Redundancia",
        """
matriz_spearman_{variable_name} = calcular_matriz_spearman(
    muestras_visuales["{dataset_name}"],
    targets_esperados["{dataset_name}"],
)
pares_spearman_{variable_name} = convertir_matriz_correlacion_a_pares(
    "{dataset_name}",
    matriz_spearman_{variable_name},
)
redundancia_{variable_name} = resumir_redundancia_dataset(pares_spearman_{variable_name})

display(redundancia_{variable_name}.style.format({{"correlacion_abs_maxima": "{{:.3f}}"}}))
display(pares_spearman_{variable_name}.nlargest(10, "abs_spearman").style.format({{
    "spearman": "{{:.3f}}",
    "abs_spearman": "{{:.3f}}",
}}))

figura = graficar_redundancia_dataset("{dataset_name}", matriz_spearman_{variable_name}, pares_spearman_{variable_name})
ruta_figura = guardar_figura(figura, "01_11_redundancia_{dataset_name}.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
""",
        redundancy_obs,
    )
    cells.append(code("""
correlaciones_pares = pd.concat([
    pares_spearman_breast_cancer_wisconsin,
    pares_spearman_customer_churn,
    pares_spearman_madelon,
    pares_spearman_olive_oil,
], ignore_index=True)
resumen_redundancia = pd.concat([
    redundancia_breast_cancer_wisconsin,
    redundancia_customer_churn,
    redundancia_madelon,
    redundancia_olive_oil,
], ignore_index=True)

guardar_tabla(correlaciones_pares, "fase1_correlaciones_spearman_pares.csv")
guardar_tabla(resumen_redundancia, "fase1_redundancia_resumen.csv")
display(resumen_redundancia.style.format({"correlacion_abs_maxima": "{:.3f}"}))
"""))
    cells.append(md("""
La comparación de redundancia evalúa 435 pares en `breast_cancer_wisconsin`, 21 en `customer_churn`, 124.750 en `madelon` y 45 en `olive_oil`. Superan `|rho| >= 0,85` un total de 29 pares en `breast_cancer_wisconsin`, 12 en `madelon`, 2 en `olive_oil` y 0 en `customer_churn`; las correlaciones máximas son 1,000, 0,996, 0,916 y 0,191 respectivamente. Esta lectura enlaza directamente con el término `R_ij` que QFS convertirá en proximidad atómica.
"""))

    cells.append(md("""
## 1.12 Dimensionalidad y PCA Exploratorio

PCA se usa aquí como diagnóstico previo a la selección de características. La pregunta no es si PCA predice bien, sino si la varianza numérica parece concentrarse en pocas componentes o si permanece muy distribuida.
"""))
    cells.append(code("""
UMBRALES_VARIANZA_PCA = [0.80, 0.90]
"""))
    cells.append(code("""
def preparar_matriz_pca(datos_dataset, target):
    columnas_numericas = obtener_columnas_numericas_predictoras(datos_dataset, target)
    matriz_numerica = datos_dataset[columnas_numericas].dropna()
    matriz_escalada = StandardScaler().fit_transform(matriz_numerica)
    return matriz_escalada, columnas_numericas


def calcular_pca_dataset(nombre_dataset, datos_dataset, target):
    matriz_escalada, columnas_numericas = preparar_matriz_pca(datos_dataset, target)
    pca = PCA(random_state=RANDOM_STATE)
    pca.fit(matriz_escalada)
    return pd.DataFrame({
        "dataset": nombre_dataset,
        "componente": np.arange(1, len(pca.explained_variance_ratio_) + 1),
        "varianza_explicada": pca.explained_variance_ratio_,
        "varianza_acumulada": np.cumsum(pca.explained_variance_ratio_),
        "n_variables_pca": len(columnas_numericas),
        "n_filas_pca": matriz_escalada.shape[0],
    })
"""))
    cells.append(code("""
def componentes_para_umbral(pca_dataset, umbral):
    supera_umbral = pca_dataset[pca_dataset["varianza_acumulada"] >= umbral]
    return int(supera_umbral["componente"].iloc[0]) if not supera_umbral.empty else np.nan


def resumir_pca_dataset(pca_dataset):
    return pd.DataFrame([{
        "dataset": pca_dataset["dataset"].iloc[0],
        "componentes_80": componentes_para_umbral(pca_dataset, 0.80),
        "componentes_90": componentes_para_umbral(pca_dataset, 0.90),
        "n_variables_pca": int(pca_dataset["n_variables_pca"].iloc[0]),
        "n_filas_pca": int(pca_dataset["n_filas_pca"].iloc[0]),
    }])


def graficar_pca_dataset(nombre_dataset, pca_dataset):
    figura, eje = plt.subplots(figsize=(8.5, 4.6))
    eje.plot(pca_dataset["componente"], pca_dataset["varianza_acumulada"], marker="o", markersize=3, color=PALETA_DATASETS[nombre_dataset])
    eje.axhline(0.80, color="#B85C5C", linestyle="--", linewidth=1, label="80%")
    eje.axhline(0.90, color="#6F6A60", linestyle=":", linewidth=1, label="90%")
    componentes_80 = componentes_para_umbral(pca_dataset, 0.80)
    eje.set_title(f"{nombre_dataset} alcanza el 80% de varianza en {componentes_80} componentes")
    eje.set_xlabel("componente principal")
    eje.set_ylabel("varianza acumulada")
    eje.set_ylim(0, 1.02)
    eje.legend(frameon=False)
    aplicar_estilo_eje(eje, "both")
    figura.tight_layout()
    return figura
"""))
    pca_obs = {
        "breast_cancer_wisconsin": "Pocas componentes explican gran parte de la varianza: 5 alcanzan el 80% y 7 el 90%, coherente con la redundancia entre variables diagnósticas.",
        "customer_churn": "La varianza se concentra en pocas componentes: 6 alcanzan el 80% y 7 el 90% entre 7 variables numéricas. Este diagnóstico usa la muestra visual por coste de representación.",
        "madelon": "Se necesitan muchas componentes para alcanzar 80% y 90% de varianza. Esto confirma que no hay una compresión simple de la estructura numérica.",
        "olive_oil": "La varianza se concentra en 3 componentes para el 80% y 5 para el 90%, lo que encaja con correlaciones entre variables de composición.",
    }
    add_dataset_cells(
        cells,
        "PCA Exploratorio",
        """
pca_{variable_name} = calcular_pca_dataset(
    "{dataset_name}",
    muestras_visuales["{dataset_name}"],
    targets_esperados["{dataset_name}"],
)
pca_resumen_{variable_name} = resumir_pca_dataset(pca_{variable_name})

display(pca_resumen_{variable_name})
figura = graficar_pca_dataset("{dataset_name}", pca_{variable_name})
ruta_figura = guardar_figura(figura, "01_12_pca_{dataset_name}.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
""",
        pca_obs,
    )
    cells.append(code("""
pca_resultados = pd.concat([
    pca_breast_cancer_wisconsin,
    pca_customer_churn,
    pca_madelon,
    pca_olive_oil,
], ignore_index=True)
pca_resumen = pd.concat([
    pca_resumen_breast_cancer_wisconsin,
    pca_resumen_customer_churn,
    pca_resumen_madelon,
    pca_resumen_olive_oil,
], ignore_index=True)

guardar_tabla(pca_resultados, "fase1_pca_varianza.csv")
guardar_tabla(pca_resumen, "fase1_pca_resumen.csv")
display(pca_resumen)
"""))
    cells.append(md("""
PCA resume la presión geométrica de cada dataset. `breast_cancer_wisconsin` alcanza el 80% de varianza con 5 componentes y el 90% con 7; `olive_oil` necesita 3 y 5; `customer_churn` necesita 6 y 7 entre sus 7 numéricas; y `madelon` requiere 295 y 369 de 500 componentes. La lectura es consistente con el resto del EDA: `madelon` no ofrece una compresión lineal sencilla y debe tratarse como testbed de alta dimensionalidad.
"""))

    cells.append(md("""
## 1.13 Señales Espurias, Proxies y Variables a Revisar

Una asociación espuria es una señal que puede desaparecer tras controlar múltiples contrastes. El criterio técnico marca tres reglas: significancia solo antes de FDR, efecto significativo pero mínimo y efecto casi perfecto; un proxy representa indirectamente información cercana al target, y una fuga potencial indica información no disponible en un escenario real de predicción. En esta fase solo se señalan variables que conviene revisar antes de modelar.
"""))
    cells.append(code("""
UMBRAL_EFECTO_MINIMO = 0.05
UMBRAL_EFECTO_CASI_PERFECTO = 0.95
"""))
    cells.append(code("""
def cumple_significativa_solo_sin_fdr(fila):
    return fila["p_valor"] < ALFA_FDR and fila["p_valor_fdr"] >= ALFA_FDR


def cumple_significativa_con_efecto_minimo(fila):
    return fila["p_valor_fdr"] < ALFA_FDR and fila["abs_tamano_efecto"] <= UMBRAL_EFECTO_MINIMO


def cumple_efecto_casi_perfecto(fila):
    return fila["abs_tamano_efecto"] >= UMBRAL_EFECTO_CASI_PERFECTO


def marcar_reglas_revision(tabla):
    tabla_marcada = tabla.copy()
    tabla_marcada["solo_significativa_sin_fdr"] = tabla_marcada.apply(cumple_significativa_solo_sin_fdr, axis=1)
    tabla_marcada["significativa_efecto_minimo"] = tabla_marcada.apply(cumple_significativa_con_efecto_minimo, axis=1)
    tabla_marcada["efecto_casi_perfecto"] = tabla_marcada.apply(cumple_efecto_casi_perfecto, axis=1)
    return tabla_marcada
"""))
    cells.append(code("""
def detectar_variables_revision_dataset(asociaciones_dataset):
    variables_marcadas = marcar_reglas_revision(asociaciones_dataset)
    columnas_reglas = ["solo_significativa_sin_fdr", "significativa_efecto_minimo", "efecto_casi_perfecto"]
    return variables_marcadas[variables_marcadas[columnas_reglas].any(axis=1)].copy()


def resumir_variables_revision_dataset(variables_revision_dataset, nombre_dataset):
    columnas_reglas = ["solo_significativa_sin_fdr", "significativa_efecto_minimo", "efecto_casi_perfecto"]
    if variables_revision_dataset.empty:
        return pd.DataFrame([{**{"dataset": nombre_dataset, "variables_a_revisar": 0}, **{columna: 0 for columna in columnas_reglas}}])
    return pd.DataFrame([{
        "dataset": nombre_dataset,
        "variables_a_revisar": len(variables_revision_dataset),
        **{columna: int(variables_revision_dataset[columna].sum()) for columna in columnas_reglas},
    }])
"""))
    revision_obs = {
        "breast_cancer_wisconsin": "Aparece 1 variable con efecto casi perfecto. Esto no confirma fuga de información, pero sí obliga a revisar semántica y redundancia antes de modelar.",
        "customer_churn": "Aparece 1 señal significativa con efecto mínimo. Este caso ilustra por qué no basta con mirar p-valores en datasets grandes.",
        "madelon": "Predominan 25 variables que eran significativas sin corrección y dejan de serlo tras FDR. Esto encaja con falsos positivos exploratorios.",
        "olive_oil": "Aparecen 2 variables con efecto casi perfecto frente al target multiclase. La revisión semántica es obligatoria para evitar proxies directos de región.",
    }
    add_dataset_cells(
        cells,
        "Variables a Revisar",
        """
revision_{variable_name} = detectar_variables_revision_dataset(asociacion_{variable_name})
revision_resumen_{variable_name} = resumir_variables_revision_dataset(revision_{variable_name}, "{dataset_name}")

display(revision_resumen_{variable_name})
if revision_{variable_name}.empty:
    display(Markdown("No se marcan variables para revisión con estas reglas exploratorias."))
else:
    display(revision_{variable_name}.sort_values("abs_tamano_efecto", ascending=False).style.format({{
        "p_valor": "{{:.2e}}",
        "p_valor_fdr": "{{:.2e}}",
        "tamano_efecto": "{{:.4f}}",
        "abs_tamano_efecto": "{{:.4f}}",
    }}))
""",
        revision_obs,
    )
    cells.append(code("""
variables_revision = pd.concat([
    revision_breast_cancer_wisconsin,
    revision_customer_churn,
    revision_madelon,
    revision_olive_oil,
], ignore_index=True)
resumen_revision = pd.concat([
    revision_resumen_breast_cancer_wisconsin,
    revision_resumen_customer_churn,
    revision_resumen_madelon,
    revision_resumen_olive_oil,
], ignore_index=True)

guardar_tabla(variables_revision, "fase1_variables_revision_riesgos.csv")
guardar_tabla(resumen_revision, "fase1_riesgos_resumen.csv")
display(resumen_revision)
"""))
    cells.append(md("""
El resumen marca 1 variable en `breast_cancer_wisconsin`, 1 en `customer_churn`, 25 en `madelon` y 2 en `olive_oil`. Los motivos también cambian: `madelon` acumula 25 variables que solo eran significativas antes de FDR, `customer_churn` aporta 1 señal significativa con efecto mínimo y los otros dos datasets concentran efectos casi perfectos. Esta sección no elimina variables, pero fija qué señales deberán revisarse antes de modelar.
"""))

    cells.append(md("""
## 1.14 Preclasificación Exploratoria de Variables

La preclasificación resume la lectura disponible por dataset mediante reglas explícitas sobre FDR, tamaño de efecto, redundancia `|rho| >= 0,85` y variables a revisar. No es selección final: solo organiza señales fuertes, señales moderadas, redundancia alta, cautelas de revisión y ausencia de señal univariante.
"""))
    cells.append(code("""
def crear_conjunto_variables_redundantes(pares_correlacion):
    pares_altos = pares_correlacion[pares_correlacion["abs_spearman"] >= UMBRAL_CORRELACION_ALTA]
    variables = set()
    for _, fila in pares_altos.iterrows():
        variables.add((fila["dataset"], fila["variable_a"]))
        variables.add((fila["dataset"], fila["variable_b"]))
    return variables


def crear_conjunto_variables_revision(variables_revision_dataset):
    return set(zip(variables_revision_dataset["dataset"], variables_revision_dataset["variable"]))


def clasificar_variable_exploratoria(fila, variables_redundantes, variables_a_revisar):
    clave_variable = (fila["dataset"], fila["variable"])
    if clave_variable in variables_a_revisar:
        return "revisar_riesgo"
    if clave_variable in variables_redundantes:
        return "redundancia_alta"
    if fila["p_valor_fdr"] < ALFA_FDR and fila["abs_tamano_efecto"] >= 0.30:
        return "senal_fuerte"
    if fila["p_valor_fdr"] < ALFA_FDR:
        return "senal_moderada"
    return "sin_senal_univariante"
"""))
    cells.append(code("""
def preclasificar_dataset(asociaciones_dataset, pares_correlacion, variables_revision_dataset):
    variables_redundantes = crear_conjunto_variables_redundantes(pares_correlacion)
    variables_a_revisar = crear_conjunto_variables_revision(variables_revision_dataset)
    preclasificacion = asociaciones_dataset.copy()
    preclasificacion["categoria_exploratoria"] = preclasificacion.apply(
        clasificar_variable_exploratoria,
        axis=1,
        variables_redundantes=variables_redundantes,
        variables_a_revisar=variables_a_revisar,
    )
    return preclasificacion


def resumir_preclasificacion(preclasificacion_dataset):
    return (
        preclasificacion_dataset
        .groupby(["dataset", "categoria_exploratoria"])
        .size()
        .rename("n_variables")
        .reset_index()
    )


def graficar_preclasificacion_dataset(nombre_dataset, resumen_dataset):
    figura, eje = plt.subplots(figsize=(8, 3.4))
    datos_grafico = resumen_dataset.assign(
        categoria_presentada=lambda tabla: tabla["categoria_exploratoria"].map(VALORES_PRESENTACION)
    )
    sns.barplot(datos_grafico, y="categoria_presentada", x="n_variables", color=PALETA_DATASETS[nombre_dataset], ax=eje)
    eje.set_title(f"La lectura inicial reparte las variables de {nombre_dataset} por categoría")
    eje.set_xlabel("número de variables")
    eje.set_ylabel("")
    aplicar_estilo_eje(eje)
    figura.tight_layout()
    return figura
"""))
    preclass_obs = {
        "breast_cancer_wisconsin": "La preclasificación concentra variables en redundancia alta y señal fuerte. La Fase 2 deberá evitar seleccionar varias variables equivalentes.",
        "customer_churn": "La preclasificación muestra señal en las 10 variables contrastadas, pero con 1 variable marcada para revisar por efecto mínimo.",
        "madelon": "La mayoría de variables queda sin señal univariante: 456 de 500. Las pocas señales y redundancias detectadas deben validarse con métodos robustos.",
        "olive_oil": "La preclasificación mezcla 6 señales fuertes, 2 variables redundantes y 2 variables de revisión. La cautela semántica debe tratarse antes de modelar.",
    }
    add_dataset_cells(
        cells,
        "Preclasificación",
        """
preclasificacion_{variable_name} = preclasificar_dataset(
    asociacion_{variable_name},
    pares_spearman_{variable_name},
    revision_{variable_name},
)
preclasificacion_resumen_{variable_name} = resumir_preclasificacion(preclasificacion_{variable_name})

display(preclasificacion_resumen_{variable_name})
figura = graficar_preclasificacion_dataset("{dataset_name}", preclasificacion_resumen_{variable_name})
ruta_figura = guardar_figura(figura, "01_14_preclasificacion_{dataset_name}.png")
plt.show()
mostrar_ruta_relativa(ruta_figura)
""",
        preclass_obs,
    )
    cells.append(code("""
preclasificacion_variables = pd.concat([
    preclasificacion_breast_cancer_wisconsin,
    preclasificacion_customer_churn,
    preclasificacion_madelon,
    preclasificacion_olive_oil,
], ignore_index=True)
preclasificacion_resumen = pd.concat([
    preclasificacion_resumen_breast_cancer_wisconsin,
    preclasificacion_resumen_customer_churn,
    preclasificacion_resumen_madelon,
    preclasificacion_resumen_olive_oil,
], ignore_index=True)

guardar_tabla(preclasificacion_variables, "fase1_preclasificacion_variables.csv")
guardar_tabla(preclasificacion_resumen, "fase1_preclasificacion_resumen.csv")
display(preclasificacion_resumen.pivot_table(
    index="dataset",
    columns="categoria_exploratoria",
    values="n_variables",
    fill_value=0,
))
"""))
    cells.append(md("""
La tabla dinámica de preclasificación deja visible todo el espacio resumido. `madelon` concentra 456 variables sin señal univariante, 25 de revisión y 18 con redundancia alta; `breast_cancer_wisconsin` reparte 18 variables en redundancia alta, 6 en señal fuerte y 3 sin señal; `customer_churn` tiene 4 señales fuertes, 5 moderadas y 1 revisión; y `olive_oil` combina 6 señales fuertes, 2 redundantes y 2 de revisión. Esta síntesis organiza la entrada a Fase 2 sin decidir aún qué variables se seleccionarán.
"""))

    cells.append(md("""
## 1.15 Síntesis Exploratoria

La síntesis reúne las métricas principales calculadas en las secciones anteriores: estructura, calidad, target, FDR, redundancia y PCA. El criterio de lectura es comparativo, porque el objetivo es cerrar la fase con un perfil de dificultad y utilidad para cada banco de datos.
"""))
    cells.append(code("""
sintesis_evidencias = (
    estructura_datasets[["dataset", "filas", "features", "ratio_features_muestras", "filas_por_feature", "posibles_identificadores"]]
    .merge(calidad_datasets[["dataset", "nulos_totales", "filas_duplicadas", "variables_constantes", "variables_baja_cardinalidad_relativa"]], on="dataset")
    .merge(target_resumen[["dataset", "n_clases", "ratio_mayoritaria_minoritaria"]], on="dataset")
    .merge(resumen_fdr[["dataset", "significativas_fdr", "reduccion_por_correccion"]], on="dataset")
    .merge(resumen_redundancia[["dataset", "pares_correlacion_alta", "correlacion_abs_maxima"]], on="dataset")
    .merge(pca_resumen[["dataset", "componentes_80", "componentes_90"]], on="dataset")
)

guardar_tabla(sintesis_evidencias, "fase1_sintesis_evidencias.csv")
display(sintesis_evidencias.style.format({
    "ratio_features_muestras": "{:.5f}",
    "filas_por_feature": "{:.1f}",
    "ratio_mayoritaria_minoritaria": "{:.3f}",
    "correlacion_abs_maxima": "{:.3f}",
}))
"""))
    cells.append(md("""
La síntesis conjunta condensa 4 perfiles de dificultad. `madelon` combina 500 features, 4,0 filas por feature, 13 variables FDR y 12 pares redundantes; `customer_churn` combina 440.832 filas, 10 features y 0 pares redundantes altos; `breast_cancer_wisconsin` acumula 29 pares `|rho| >= 0,85`; y `olive_oil` añade 9 clases con ratio 8,240. Las lecturas por dataset desglosan estas implicaciones antes del cierre.
"""))
    synthesis_obs = {
        "breast_cancer_wisconsin": "La síntesis de `breast_cancer_wisconsin` combina señal fuerte con redundancia alta. Para la Fase 2, la cautela principal es seleccionar variables repetidas o incluir identificadores.",
        "customer_churn": "La síntesis de `customer_churn` muestra 440.832 filas, 10 features y 10 variables FDR. La lectura posterior debe priorizar magnitud de efecto y codificación correcta.",
        "madelon": "La síntesis de `madelon` confirma 500 features, 4,0 filas por feature y reducción FDR de 38 a 13. Necesita selección robusta frente a ruido.",
        "olive_oil": "La síntesis de `olive_oil` muestra 9 clases, ratio 8,240, 10 variables FDR y 2 variables de revisión semántica por posible proxy.",
    }
    for dataset_name, _, label in DATASETS:
        cells.append(md(f"### Síntesis: `{dataset_name}`"))
        cells.append(code(f"""
display(sintesis_evidencias[sintesis_evidencias["dataset"] == "{dataset_name}"].style.format({{
    "ratio_features_muestras": "{{:.5f}}",
    "filas_por_feature": "{{:.1f}}",
    "ratio_mayoritaria_minoritaria": "{{:.3f}}",
    "correlacion_abs_maxima": "{{:.3f}}",
}}))
"""))
        cells.append(md(synthesis_obs[dataset_name]))

    cells.append(md("""
### Resumen Para Memoria

Se guarda un resumen breve de Fase 1 con los resultados principales. El informe no sustituye a las tablas: resume las implicaciones metodológicas que sí pertenecen a esta fase exploratoria.
"""))
    cells.append(code("""
summary_lines = [
    "# Resultados de la Fase 1 - Análisis exploratorio crudo",
    "",
    "La Fase 1 carga los datasets crudos, caracteriza estructura, calidad, target, asociaciones exploratorias, FDR, redundancia y dimensionalidad.",
    "",
    "## Hallazgos principales",
]

for _, row in sintesis_evidencias.iterrows():
    revision_row = resumen_revision[resumen_revision["dataset"].eq(row["dataset"])]
    n_review = int(revision_row["variables_a_revisar"].iloc[0]) if not revision_row.empty else 0
    summary_lines.append(
        f"- `{row['dataset']}`: {int(row['filas'])} filas, {int(row['features'])} features, "
        f"ratio features/muestras={row['ratio_features_muestras']:.5f}, "
        f"FDR significativas={int(row['significativas_fdr'])}, "
        f"pares Spearman >=0.85={int(row['pares_correlacion_alta'])}, "
        f"variables para revisión={n_review}."
    )

summary_lines.extend([
    "",
    "## Implicaciones para fases posteriores",
    "- Fase 2 debe limitarse a preprocesado estructural: identificadores, nombres y target.",
    "- Fase 3 debe comprobar que el preprocesado conserva target, distribuciones y señal exploratoria.",
    "- Fase 4 debe estratificar y vigilar fugas de información y desplazamientos de distribución, especialmente en Olive Oil y variables con efecto casi perfecto.",
    "- Fase 5 debe separar señal, ruido y redundancia; `madelon` es el caso crítico para selección robusta.",
    "",
    "## Tablas generadas",
])

for table_path in sorted(TABLES_DIR.glob("fase1_*.csv")):
    summary_lines.append(f"- `{table_path.relative_to(PROJECT_ROOT)}`")

summary_lines.extend(["", "## Figuras generadas"])
for figure_path in sorted(FIGURES_DIR.rglob("*.png")):
    summary_lines.append(f"- `{figure_path.relative_to(PROJECT_ROOT)}`")

summary_path = REPORTS_DIR / "fase1_resumen_para_memoria.md"
summary_path.write_text("\\n".join(summary_lines), encoding="utf-8")
print("Resumen para memoria guardado.")
"""))
    cells.append(md("""
El resumen para memoria queda guardado y no añade resultados nuevos. Su función es condensar las conclusiones principales de esta fase exploratoria para la redacción final.
"""))

    cells.append(md("""
## 1.16 Conclusiones y Consideraciones Para la Fase 2

La Fase 1 permite afirmar lo siguiente desde resultados exploratorios y criterios reproducibles de calidad, target, FDR, redundancia y PCA: los cuatro datasets se cargan correctamente, no se observan nulos ni duplicados, los targets presentan comportamientos distintos y la relación entre variables y target varía mucho entre datasets.

`breast_cancer_wisconsin` exige controlar identificadores y redundancia. `customer_churn` exige no confundir significancia con relevancia práctica. `madelon` exige métodos de selección capaces de manejar dimensionalidad y ruido. `olive_oil` exige estratificación multiclase, métricas adecuadas y revisión semántica de variables con efecto casi perfecto.

Lo que todavía no se puede concluir con el criterio técnico de Fase 1 es rendimiento predictivo, causalidad, fuga de información confirmada o conjunto final de variables. Esas decisiones corresponden a fases posteriores con preprocesado, particiones, selección de características y validación.
"""))

    nb["cells"] = cells
    return nb


if __name__ == "__main__":
    notebook = build_notebook()
    nbf.write(notebook, NOTEBOOK_PATH)
    print(f"Notebook reconstruido: {NOTEBOOK_PATH}")
