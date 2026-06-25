"""Reconstruye notebooks/fase5.ipynb como capítulo incremental."""

from pathlib import Path
import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "fase5.ipynb"


def md(text: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(text.strip())


def code(text: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_code_cell(text.strip())


cells: list[nbformat.NotebookNode] = []

cells.append(
    md(
        """
# Trabajo de Fin de Grado: Desarrollo y Evaluación de un Método Cuántico de Selección de Características

## Notebook 05 - Selección clásica de características

Esta fase construye el bloque clásico que se comparará con QFS. El objetivo no es acumular algoritmos, sino diseñar una comparación atribuible: cada selector representa una pieza de la función cuántica de coste o un referente habitual del campo, siempre ajustado solo con train.

El capítulo se lee de forma incremental. Primero se cargan los cinco problemas y se construye la matriz de variables; después se define el roster de doce métodos, se materializan las matrices de relevancia y redundancia que consume el método cuántico, y finalmente se estudian estabilidad, permutaciones, redundancia interna y figuras.
"""
    )
)

cells.append(
    md(
        """
## 5.1 Preparación del entorno

La primera celda fija el directorio de trabajo, importa `pandas` para la lectura tabular y carga desde `src/fase5_feature_selection.py` funciones de una sola responsabilidad: cargar splits, construir matrices, ejecutar un selector concreto, medir Jaccard, permutar el target y calcular información mutua. El criterio técnico es que cada cálculo aparezca cuando la narración lo necesita.
"""
    )
)
cells.append(
    code(
        """
import os
import sys
from pathlib import Path

import pandas as pd
from IPython.display import Image, Markdown, display

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

import fase5_feature_selection as fs

fs.asegurar_directorios()
fs.configurar_estilo()

pd.set_option("display.max_colwidth", 120)
print(f"Datasets: {len(fs.DATASETS)}")
print(f"Métodos del roster: {len(fs.ROSTER_12)}")
print(f"Semillas de estabilidad: {fs.SEEDS_ESTABILIDAD}")
"""
    )
)
cells.append(
    md(
        """
La ejecución arranca con 5 datasets, 12 métodos y 3 semillas de estabilidad. La selección principal usa la semilla 42, mientras que las semillas 13 y 97 solo entran para medir sensibilidad de los subconjuntos.
"""
    )
)

cells.append(
    md(
        """
## 5.2 Funciones locales de lectura

Estas funciones no alteran resultados: únicamente preparan cabeceras en español, muestran las primeras filas cuando una tabla es larga y abren figuras ya guardadas. El criterio de truncado es explícito: hasta 30 filas se muestran completas; por encima de ese límite se indica cuántas filas se enseñan.
"""
    )
)
cells.append(
    code(
        """
def tabla_es(tabla, columnas=None, max_filas=12, decimales=3):
    vista = tabla.copy()
    if columnas is not None:
        vista = vista.rename(columns=columnas)
    if len(vista) <= 30:
        display(vista.round(decimales))
    else:
        display(Markdown(f"Se muestran las primeras {max_filas} de {len(vista)} filas."))
        display(vista.head(max_filas).round(decimales))


def mostrar_png(ruta, ancho=850):
    display(Image(filename=str(ruta), width=ancho))


def lectura_numero(valor, decimales=3):
    if pd.isna(valor):
        return "no disponible"
    return f"{valor:.{decimales}f}"
"""
    )
)
cells.append(
    md(
        """
Las tres funciones separan presentación y cálculo. En las celdas siguientes, cualquier tabla larga mostrará una cabecera representativa y cualquier figura se leerá desde la ruta creada en la misma sección.
"""
    )
)

cells.append(
    md(
        """
## 5.3 Roster clásico como espejo de QFS

QFS combina dos ingredientes: relevancia `I(x;y)` y redundancia `I(x;x)`, integrados en una optimización global de una función cuadrática. Por eso el roster clásico se organiza como espejo de esa estructura y no como un concurso genérico de selectores.

La relevancia pura queda representada por `f_classif` y `mutual_info`; esta última coincide con la magnitud que QFS codifica como detuning local. La redundancia pura no supervisada se estudia con `mutual_correlation` y `feature_similarity`, siguiendo la guía del tutor sobre MC y FSFS y la literatura de filtros no supervisados revisada por Solorio-Fernández et al. en el paper UFS. La combinación relevancia-redundancia se evalúa con `mrmr_approx` y `rrfs`, que son el análogo clásico más próximo al objetivo de QFS.

Se añaden dos wrappers de referencia: `boruta`, como método all-relevant basado en shadow features y tamaño natural confirmado, y `rfe`, como alternativa minimal-optimal a k fijo. Los métodos embedded (`l1_logistic`, `random_forest`, `linear_svm`) sitúan la selección en el contexto de un modelo. `variance` se conserva como baseline mínimo: aquí se calcula sobre datos estandarizados, siguiendo el protocolo habitual de la selección no supervisada (Solorio-Fernández et al. 2020), lo que produce varianzas casi uniformes; el ranking resultante es, por construcción, un baseline degenerado y su mal comportamiento en el estudio UFS no es sorprendente. Además, `mutual_correlation` y `feature_similarity` figuran en ese mismo estudio entre los filtros UFS con menor rendimiento predictivo: aquí se incluyen como espejo estructural del término de redundancia de QFS, no por competitividad esperada.
"""
    )
)
cells.append(
    code(
        """
registro_metodos = fs.construir_registro_metodos()
fs.guardar_csv(registro_metodos, "fs_method_registry.csv")
tabla_es(
    registro_metodos,
    {
        "method": "Método",
        "familia": "Familia",
        "usa_target": "Usa target",
        "salida": "Salida",
        "criterio_tecnico": "Medida técnica",
    },
    max_filas=20,
)
"""
    )
)
cells.append(
    md(
        """
El roster contiene 12 métodos: 1 baseline mínimo, 2 filtros de relevancia, 2 filtros de redundancia no supervisada, 2 combinaciones relevancia-redundancia, 2 wrappers y 3 embedded. Boruta se interpreta a su tamaño confirmado; los otros 11 métodos producen rankings que se cortan en la escalera de k.
"""
    )
)

cells.append(
    md(
        """
## 5.4 Carga de splits y matrices de variables

Cada dataset se carga desde sus particiones ya fijadas. El preprocesado se ajusta solo con `X_train`: mediana y escalado para variables numéricas, moda y one-hot para categóricas. Validation y test reciben exactamente la transformación aprendida en train, sin decidir columnas ni parámetros.
"""
    )
)
cells.append(
    code(
        """
bundles = {}
resumenes_dataset = []
for dataset in fs.DATASETS:
    bundle = fs.cargar_dataset(dataset)
    bundles[dataset] = bundle
    resumenes_dataset.append(fs.resumen_dataset(bundle))

resumen_datasets = pd.DataFrame(resumenes_dataset)
fs.guardar_csv(resumen_datasets, "fs_input_dataset_summary.csv")
tabla_es(
    resumen_datasets,
    {
        "dataset": "Dataset",
        "n_train": "Filas train",
        "n_validation": "Filas validación",
        "n_test": "Filas test",
        "n_features": "Variables",
        "n_classes_train": "Clases train",
        "minority_class_train_pct": "Clase minoritaria train (%)",
    },
    max_filas=10,
)
"""
    )
)
cells.append(
    md(
        """
La tabla muestra 5 formulaciones operativas. Madelon es el problema más ancho, con 500 variables tras la construcción de la matriz, mientras que Customer Churn concentra el mayor número de filas de entrenamiento y exige muestreo en los métodos costosos.
"""
    )
)

cells.append(
    md(
        """
## 5.5 Presupuesto de k

La escalera de k se deriva del número de variables de cada dataset y combina valores pequeños, raíz cuadrada aproximada, 10% del espacio y cortes habituales hasta 50 variables. El criterio mantiene subconjuntos compactos, porque QFS trabaja de forma natural con presupuestos pequeños en arrays de átomos neutros.
"""
    )
)
cells.append(
    code(
        """
filas_k = []
for dataset, bundle in bundles.items():
    for k in fs.valores_k(bundle.x_train.shape[1]):
        filas_k.append(
            {
                "dataset": dataset,
                "n_features": bundle.x_train.shape[1],
                "k": k,
                "reduction_pct": 100 * (1 - k / bundle.x_train.shape[1]),
            }
        )
k_table = pd.DataFrame(filas_k)
k_por_dataset = {
    dataset: sorted(k_table.loc[k_table["dataset"].eq(dataset), "k"].astype(int).unique())
    for dataset in fs.DATASETS
}
fs.guardar_csv(k_table, "fs_k_values_by_dataset.csv")
fs.guardar_csv(k_table, "fs_dimensionality_reduction_plan.csv")
tabla_es(
    k_table,
    {
        "dataset": "Dataset",
        "n_features": "Variables",
        "k": "k",
        "reduction_pct": "Reducción (%)",
    },
    max_filas=18,
)
"""
    )
)
cells.append(
    md(
        """
La reducción no es homogénea: en datasets pequeños un k de 5 puede ser casi todo el espacio, mientras que en Madelon incluso k=50 conserva solo el 10% de las variables. Por eso las comparaciones posteriores se leen dentro de cada dataset.
"""
    )
)

cells.append(
    md(
        """
## 5.6 Matrices de relevancia y redundancia para QFS

Antes de ejecutar los selectores clásicos, se materializan las dos cantidades que consume el método cuántico: el vector `I_i`, información mutua entre cada variable y el target, y la matriz `R_ij`, información mutua entre pares de variables. La convención sigue la referencia del solver: las variables continuas se discretizan en 5 intervalos uniformes ajustados solo con train, las discretas se conservan como códigos, no se aplica filtro por umbral y no se normaliza en esta fase.
"""
    )
)
cells.append(
    code(
        """
resumen_matrices = []
vectores_mi = []
matrices_mi = []
for dataset, bundle in bundles.items():
    resumen_local, vector_local, matriz_local = fs.materializar_matrices_qfs(bundle)
    resumen_matrices.append(resumen_local)
    vectores_mi.append(vector_local)
    matrices_mi.append(matriz_local.assign(dataset=dataset))

qfs_matrices_index = pd.concat(resumen_matrices, ignore_index=True)
qfs_mi_target_long = pd.concat(vectores_mi, ignore_index=True)
qfs_pairwise_long = pd.concat(matrices_mi, ignore_index=True)
fs.guardar_csv(qfs_matrices_index, "fs_qfs_handoff_matrices_index.csv")
fs.guardar_csv(qfs_mi_target_long, "fs_qfs_mi_target_vector_long.csv")
fs.guardar_csv(qfs_pairwise_long, "fs_qfs_pairwise_mi_matrix_long.csv")
tabla_es(
    qfs_matrices_index[
        [
            "dataset",
            "n_features",
            "mean_I_i",
            "max_I_i",
            "mean_R_ij_offdiag",
            "max_R_ij_offdiag",
            "n_continuous_binned",
            "n_discrete_kept",
            "mi_bins",
        ]
    ],
    {
        "dataset": "Dataset",
        "n_features": "Variables",
        "mean_I_i": "Media I_i",
        "max_I_i": "Máximo I_i",
        "mean_R_ij_offdiag": "Media R_ij",
        "max_R_ij_offdiag": "Máximo R_ij",
        "n_continuous_binned": "Continuas discretizadas",
        "n_discrete_kept": "Discretas conservadas",
        "mi_bins": "Intervalos MI",
    },
    max_filas=10,
)
"""
    )
)
cells.append(
    md(
        """
Las matrices ya muestran una diferencia clave entre problemas: la media de `I_i` resume cuánta señal individual recibe QFS, mientras que la media fuera de diagonal de `R_ij` resume la presión de redundancia. La tabla indica además cuántas variables se discretizan en 5 intervalos y cuántas ya entran como discretas.
"""
    )
)

cells.append(
    md(
        """
## 5.7 Ejecución granular de los doce selectores

Cada método se ejecuta dentro del bucle visible dataset-método-semilla. Boruta se trata como caso especial: produce un conjunto confirmado por dataset y no una escalera de k. RFE, en cambio, se recalcula para cada k porque su objetivo minimal-optimal depende del tamaño solicitado.
"""
    )
)
cells.append(
    code(
        """
rankings_partes = []
tiempos = []
boruta_natural_partes = []

for dataset, bundle in bundles.items():
    for _, metodo_row in registro_metodos.iterrows():
        metodo = metodo_row["method"]
        familia = metodo_row["familia"]
        if metodo == "boruta":
            ranking, log, natural = fs.ejecutar_selector(
                metodo, bundle.x_train, bundle.y_train, None, fs.RANDOM_STATE, dataset, familia
            )
            rankings_partes.append(ranking)
            tiempos.append(log)
            boruta_natural_partes.append(natural)
            continue
        for semilla in fs.SEEDS_ESTABILIDAD:
            if metodo == "rfe":
                k_ref = min(10, max(k_por_dataset[dataset]))
                ranking, log, _ = fs.ejecutar_selector(
                    metodo, bundle.x_train, bundle.y_train, k_ref, semilla, dataset, familia, [k_ref]
                )
                rankings_partes.append(ranking)
                tiempos.append(log)
            else:
                ranking, log, _ = fs.ejecutar_selector(
                    metodo, bundle.x_train, bundle.y_train, max(k_por_dataset[dataset]), semilla, dataset, familia, k_por_dataset[dataset]
                )
                rankings_partes.append(ranking)
                tiempos.append(log)

rankings = pd.concat(rankings_partes, ignore_index=True)
execution_times = pd.DataFrame(tiempos)
boruta_confirmed = pd.concat(boruta_natural_partes, ignore_index=True)

fs.guardar_csv(rankings, "fs_all_rankings.csv")
fs.guardar_csv(rankings[rankings["selected"]], "fs_all_selected_features.csv")
fs.guardar_csv(execution_times, "fs_all_execution_times.csv")
fs.guardar_csv(execution_times, "fs_execution_log.csv", fs.LOG_DIR)
fs.guardar_csv(execution_times[execution_times["status"].ne("ok")], "fs_failed_methods.csv", fs.LOG_DIR)
fs.guardar_csv(boruta_confirmed, "fs_boruta_confirmed_sets.csv")

resumen_ejecucion = (
    rankings[rankings["selected"] & rankings["seed"].eq(fs.RANDOM_STATE)]
    .groupby(["dataset", "method"], as_index=False)
    .agg(n_k=("k", "nunique"), variables_unicas=("feature", "nunique"))
)
tabla_es(
    resumen_ejecucion,
    {
        "dataset": "Dataset",
        "method": "Método",
        "n_k": "Valores de k",
        "variables_unicas": "Variables únicas",
    },
    max_filas=30,
)
"""
    )
)
cells.append(
    md(
        """
La ejecución principal genera una lectura por dataset y método. Boruta aparece con 1 tamaño natural por dataset, mientras que los demás métodos cubren varios k; esa asimetría es metodológica, porque Boruta pregunta qué variables son confirmadas frente a sombras, no cuáles son las primeras k de un ranking.
"""
    )
)

cells.append(
    md(
        """
## 5.8 Tablas granulares por unidad experimental

La selección se guarda con una tabla por dataset, método y k. Además, se construye una vista pivotada método-k para cada dataset, de modo que el espacio completo queda cubierto sin obligar a leer cientos de filas en el cuerpo del notebook.
"""
    )
)
cells.append(
    code(
        """
indice_tablas = fs.guardar_tablas_granulares(rankings, boruta_confirmed)
pivot_seleccion = fs.vista_pivot_seleccion(rankings)
fs.guardar_csv(indice_tablas, "fs_experiment_table_index.csv")
fs.guardar_csv(pivot_seleccion, "fs_experiment_selection_pivot.csv")
tabla_es(
    pivot_seleccion,
    {
        "dataset": "Dataset",
        "method": "Método",
    },
    max_filas=18,
)
"""
    )
)
cells.append(
    md(
        """
La vista pivotada permite comprobar que los 12 métodos están presentes en cada dataset. En las columnas de k se leen directamente los nombres seleccionados; cuando una celda está vacía, el método no produce ese tamaño, como ocurre de forma esperada con Boruta y su único tamaño confirmado.
"""
    )
)

cells.append(
    md(
        """
## 5.9 Lectura por dataset del roster

La siguiente lectura muestra, para cada dataset, la cabecera de la tabla pivotada y el tamaño confirmado de Boruta. El criterio de interpretación es local: no se promedian datasets con dimensionalidades, clases y escalas de señal distintas.
"""
    )
)

lecturas_dataset = {
    "breast_cancer_wisconsin": "En `breast_cancer_wisconsin` se comparan 30 variables procesadas y Boruta fija 1 conjunto natural. La lectura clínica exige distinguir estabilidad de redundancia, porque varios métodos pueden coincidir en variables diagnósticas muy correlacionadas.",
    "customer_churn": "En `customer_churn` el espacio tiene 15 variables y más de 300000 filas de train. La tabla separa métodos rápidos con train completo de métodos muestreados, sin convertir el tamaño muestral en una ventaja narrativa.",
    "madelon": "En `madelon` la tabla resume el caso ancho de 500 variables. La escalera de k es especialmente informativa aquí: k=5 y k=50 representan lecturas muy distintas de señal frente a distractores sintéticos.",
    "olive_oil_3class": "En `olive_oil_3class` solo hay 8 variables, por lo que varios k se acercan al espacio completo. Boruta confirma su tamaño natural y la comparación debe leerse como reducción suave, no como cribado agresivo.",
    "olive_oil_9class": "En `olive_oil_9class` se mantienen las mismas 8 variables que en la formulación de 3 clases, pero cambia la dificultad del target. Por eso la tabla se interpreta junto con estabilidad y redundancia, no solo por nombres seleccionados.",
}

lecturas_figura_roster = {
    "breast_cancer_wisconsin": "En `breast_cancer_wisconsin`, la figura resume 12 métodos y deja visible si Boruta se sitúa por encima o por debajo de los cortes top-k. El contraste aporta una lectura de tamaño que la tabla de variables no muestra de forma inmediata.",
    "customer_churn": "En `customer_churn`, la figura compara 12 decisiones sobre un espacio de 15 variables. El tamaño confirmado de Boruta se interpreta como referencia all-relevant, mientras que los métodos con ranking se leen por cortes de k.",
    "madelon": "En `madelon`, la figura comprime la comparación de 12 métodos sobre 500 variables. La distancia entre el tamaño de Boruta y los cortes pequeños ayuda a leer cuánto cribado exige el problema sintético.",
    "olive_oil_3class": "En `olive_oil_3class`, la figura muestra que 8 variables dejan poco margen para reducciones extremas. Por eso el interés está en qué métodos evitan redundancia, no solo en cuántas columnas retienen.",
    "olive_oil_9class": "En `olive_oil_9class`, los mismos 8 predictores se comparan bajo un target más fino. La figura actúa como control de tamaño antes de interpretar estabilidad y permutaciones.",
}

for dataset in ["breast_cancer_wisconsin", "customer_churn", "madelon", "olive_oil_3class", "olive_oil_9class"]:
    cells.append(md(f"### {dataset}"))
    cells.append(
        code(
            f"""
vista_{dataset} = pivot_seleccion[pivot_seleccion["dataset"].eq("{dataset}")]
boruta_{dataset} = boruta_confirmed[boruta_confirmed["dataset"].eq("{dataset}")]
tabla_es(vista_{dataset}, {{"dataset": "Dataset", "method": "Método"}}, max_filas=20)
tabla_es(
    boruta_{dataset},
    {{"dataset": "Dataset", "method": "Método", "seed": "Semilla", "k_confirmed": "k confirmado", "n_features": "Variables"}},
    max_filas=5,
)
"""
        )
    )
    cells.append(
        md(
            lecturas_dataset[dataset]
        )
    )

cells.append(
    md(
        """
## 5.10 Estabilidad entre semillas

La estabilidad se mide con Jaccard entre subconjuntos obtenidos con semillas diferentes. La métrica se calcula para métodos con ranking; Boruta queda fuera de este contraste porque en esta fase se ha tratado como una decisión confirmatoria única por dataset.
"""
    )
)
cells.append(
    code(
        """
jaccard = fs.calcular_estabilidad(rankings)
fs.guardar_csv(jaccard, "fs_jaccard_stability.csv")
resumen_jaccard = (
    jaccard.groupby(["dataset", "method"], as_index=False)
    .agg(jaccard_medio=("jaccard", "mean"), jaccard_minimo=("jaccard", "min"), comparaciones=("jaccard", "count"))
)
tabla_es(
    resumen_jaccard,
    {
        "dataset": "Dataset",
        "method": "Método",
        "jaccard_medio": "Jaccard medio",
        "jaccard_minimo": "Jaccard mínimo",
        "comparaciones": "Comparaciones",
    },
    max_filas=24,
)
"""
    )
)
cells.append(
    md(
        """
La estabilidad media resume si el selector devuelve prácticamente las mismas variables o si pequeñas variaciones de semilla cambian el subconjunto. Los métodos deterministas tienden a Jaccard 1, mientras que `mutual_info`, modelos embedded y wrappers pueden dispersarse más.
"""
    )
)

cells.append(
    md(
        """
## 5.11 Permutaciones del target

Para los dos métodos de relevancia pura se permuta `y_train` 20 veces y se compara el score real con el percentil 95 del nulo empírico. El mínimo p-valor alcanzable con 20 permutaciones es 1/21, aproximadamente 0,048; mRMR y RRFS se leen después por redundancia porque repetir su paso secuencial en cada permutación multiplicaría el coste sin cambiar la pregunta de relevancia pura.
"""
    )
)
cells.append(
    code(
        """
permutaciones_partes = []
familias = registro_metodos.set_index("method")["familia"].to_dict()
for dataset, bundle in bundles.items():
    k_ref = min(10, max(k_por_dataset[dataset]))
    for metodo in fs.METODOS_PERMUTACION:
        permutaciones_partes.append(
            fs.ejecutar_permutaciones(bundle, metodo, familias[metodo], k_ref, n_permutations=fs.N_PERMUTACIONES)
        )
permutation_pvalues = pd.concat(permutaciones_partes, ignore_index=True)
permutation_summary = (
    permutation_pvalues.groupby(["dataset", "method"], as_index=False)
    .agg(
        n_features_above_null=("above_null_p95", "sum"),
        median_empirical_p_value=("empirical_p_value", "median"),
        n_permutations=("n_permutations", "max"),
    )
)
fs.guardar_csv(permutation_pvalues, "fs_permutation_empirical_pvalues.csv")
fs.guardar_csv(permutation_summary, "fs_permutation_summary.csv")
tabla_es(
    permutation_summary,
    {
        "dataset": "Dataset",
        "method": "Método",
        "n_features_above_null": "Variables sobre p95 nulo",
        "median_empirical_p_value": "p empírico mediano",
        "n_permutations": "Permutaciones",
    },
    max_filas=20,
)
"""
    )
)
cells.append(
    md(
        """
La tabla distingue selección con señal supervisada de selección compatible con azar en 2 métodos y 20 permutaciones por combinación. Una cuenta alta de variables sobre el p95 nulo indica que el ranking real no se explica bien por permutar las etiquetas de train, aunque el p-valor mínimo queda limitado a 0,048.
"""
    )
)

cells.append(
    md(
        """
## 5.12 Redundancia interna de los subconjuntos

La redundancia se resume con la correlación absoluta media de Spearman dentro de cada subconjunto y se compara con el espacio completo de train. Un delta negativo indica que el selector reduce redundancia; un delta positivo indica que concentra variables parecidas.
"""
    )
)
cells.append(
    code(
        """
redundancia = fs.calcular_redundancia_interna(bundles, rankings)
fs.guardar_csv(redundancia, "fs_redundancy_vs_full.csv")
resumen_redundancia = (
    redundancia.groupby(["dataset", "method"], as_index=False)
    .agg(delta_medio=("delta_mean_abs_corr", "mean"), corr_seleccionada=("selected_mean_abs_corr", "mean"))
)
tabla_es(
    resumen_redundancia,
    {
        "dataset": "Dataset",
        "method": "Método",
        "delta_medio": "Delta medio",
        "corr_seleccionada": "Correlación seleccionada",
    },
    max_filas=24,
)
"""
    )
)
cells.append(
    md(
        """
La redundancia interna ofrece una lectura que una tabla de rankings no puede dar: 2 métodos pueden seleccionar variables con scores altos y, aun así, diferir en cuánto solapamiento informativo concentran. Esa es precisamente la dimensión que QFS penaliza con `R_ij`.
"""
    )
)

cells.append(
    md(
        """
## 5.13 Datasets reducidos para la siguiente fase

Con las columnas decididas en train se escriben las matrices reducidas de train, validación y test. La celda no vuelve a ajustar selectores: solo aplica las columnas ya seleccionadas y guarda el índice de conjuntos disponibles.
"""
    )
)
cells.append(
    code(
        """
reduced_sets = fs.guardar_datasets_reducidos(bundles, rankings)
fs.guardar_csv(reduced_sets, "fs_selected_feature_sets.csv")
fs.guardar_csv(reduced_sets, "fs_reduced_datasets_log.csv", fs.LOG_DIR)
tabla_es(
    reduced_sets.groupby(["dataset", "method"], as_index=False).agg(conjuntos=("k", "nunique"), max_variables=("n_features", "max")),
    {
        "dataset": "Dataset",
        "method": "Método",
        "conjuntos": "Conjuntos",
        "max_variables": "Máximo de variables",
    },
    max_filas=24,
)
"""
    )
)
cells.append(
    md(
        """
La salida confirma que los conjuntos reducidos cubren 12 métodos y los tamaños disponibles por dataset. En métodos con ranking hay varios conjuntos; en Boruta hay 1 conjunto porque el tamaño procede del test con variables sombra.
"""
    )
)

cells.append(
    md(
        """
## 5.14 Figuras con decisiones viz-definitive

Se generan cuatro familias de figura: estabilidad Jaccard, contraste por permutación, redundancia interna y comparación del roster por dataset. Además, se guarda un heatmap método-variable por dataset como lectura de coincidencias; si se usa en la memoria, funciona mejor como apoyo visual que como sustituto de las tablas.
"""
    )
)
cells.append(
    code(
        """
figuras = []

ruta_estabilidad = fs.plot_estabilidad(jaccard)
figuras.append({"family_id": "fase5_estabilidad_jaccard", "tier": 2, "question": "¿Qué métodos son estables entre semillas en cada dataset?", "visual_family": "heatmap anotado", "decision": "matriz dataset-método porque la comparación cruzada es el mensaje", "png_path": str(ruta_estabilidad)})
mostrar_png(ruta_estabilidad)
"""
    )
)
cells.append(
    md(
        """
La figura de estabilidad resume 3 semillas por método con ranking. Esta lectura no aparece en el ranking de una sola semilla: necesita comparar subconjuntos repetidos y medir su Jaccard medio entre pares.
"""
    )
)
cells.append(
    code(
        """
ruta_permutaciones = fs.plot_permutaciones(permutation_summary)
figuras.append({"family_id": "fase5_permutaciones_target", "tier": 2, "question": "¿Qué métodos separan variables reales del nulo por permutación?", "visual_family": "heatmap anotado", "decision": "matriz compacta para contar variables sobre p95 nulo", "png_path": str(ruta_permutaciones)})
mostrar_png(ruta_permutaciones)
"""
    )
)
cells.append(
    md(
        """
La figura de permutaciones concentra el contraste real-nulo por dataset y método. Los valores altos señalan rankings supervisados con más variables por encima del percentil 95 nulo; los valores bajos obligan a interpretar el score como débil frente al azar inducido.
"""
    )
)
cells.append(
    code(
        """
ruta_redundancia = fs.plot_redundancia(redundancia)
figuras.append({"family_id": "fase5_redundancia_interna", "tier": 2, "question": "¿La selección reduce o concentra redundancia respecto al espacio completo?", "visual_family": "dot plot con línea cero", "decision": "puntos por dataset para preservar signo y dispersión", "png_path": str(ruta_redundancia)})
mostrar_png(ruta_redundancia)
"""
    )
)
cells.append(
    md(
        """
La línea vertical en 0 separa reducción y concentración de redundancia. Los puntos a la izquierda muestran subconjuntos menos redundantes que el espacio completo; los puntos a la derecha concentran variables más parecidas entre sí.
"""
    )
)

for dataset in ["breast_cancer_wisconsin", "customer_churn", "madelon", "olive_oil_3class", "olive_oil_9class"]:
    cells.append(
        code(
            f"""
ruta_roster_{dataset} = fs.plot_roster_dataset(rankings, "{dataset}")
figuras.append({{"family_id": "fase5_comparacion_roster_dataset", "tier": 0, "question": "¿Cómo cambia el tamaño seleccionado entre métodos para un dataset?", "visual_family": "barras horizontales", "decision": "reusa familia por dataset con escala local", "png_path": str(ruta_roster_{dataset})}})
mostrar_png(ruta_roster_{dataset}, ancho=780)
"""
        )
    )
    cells.append(
        md(
            lecturas_figura_roster[dataset]
        )
    )

cells.append(
    code(
        """
heatmaps = []
for dataset in fs.DATASETS:
    ruta_heatmap = fs.plot_heatmap_metodo_feature(rankings, dataset)
    heatmaps.append({"dataset": dataset, "ruta": str(ruta_heatmap)})
    figuras.append({"family_id": "fase5_heatmap_metodo_variable", "tier": 0, "question": "¿Qué coincidencias aparecen entre métodos y variables?", "visual_family": "heatmap binario", "decision": "apoyo visual para coincidencias top", "png_path": str(ruta_heatmap)})
    mostrar_png(ruta_heatmap, ancho=760)

tabla_es(pd.DataFrame(heatmaps), {"dataset": "Dataset", "ruta": "Figura método-variable"}, max_filas=10)
fs.registrar_decisiones_figuras(figuras)
"""
    )
)
cells.append(
    md(
        """
Los 5 heatmaps método-variable muestran coincidencias entre selectores sin sustituir las tablas granulares. Su papel es visual: destacar qué variables aparecen en varios métodos, mientras el valor exacto de k y el orden de ranking quedan en las tablas guardadas.
"""
    )
)

cells.append(
    md(
        """
## 5.15 Síntesis para la comparación posterior

La fase termina con perfiles por método: coste medio, estabilidad media y redundancia media seleccionada. Estas cifras no deciden por sí solas qué método es mejor; sirven para que la comparación con QFS sea interpretable por ingrediente: relevancia, redundancia, combinación y optimización.
"""
    )
)
cells.append(
    code(
        """
perfil_tiempo = execution_times.groupby("method", as_index=False).agg(segundos_medios=("elapsed_seconds", "mean"))
perfil_estabilidad = jaccard.groupby("method", as_index=False).agg(jaccard_medio=("jaccard", "mean"))
perfil_redundancia = redundancia.groupby("method", as_index=False).agg(corr_media_seleccionada=("selected_mean_abs_corr", "mean"))
method_profiles = (
    perfil_tiempo
    .merge(perfil_estabilidad, on="method", how="left")
    .merge(perfil_redundancia, on="method", how="left")
    .sort_values("method")
)
fs.guardar_csv(method_profiles, "fs_method_profiles.csv")
tabla_es(
    method_profiles,
    {
        "method": "Método",
        "segundos_medios": "Segundos medios",
        "jaccard_medio": "Jaccard medio",
        "corr_media_seleccionada": "Correlación media seleccionada",
    },
    max_filas=20,
)
"""
    )
)
cells.append(
    md(
        """
La síntesis deja 3 ejes de lectura: coste, estabilidad y redundancia. Si QFS mejora a métodos de relevancia pura, el aporte no se atribuye solo a `I_i`; si mejora a métodos de redundancia o mRMR/RRFS, la hipótesis apunta a la combinación global.
"""
    )
)

nb = nbformat.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "qfs_env", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}
NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, NOTEBOOK)
print(f"Notebook reconstruido: {NOTEBOOK}")
