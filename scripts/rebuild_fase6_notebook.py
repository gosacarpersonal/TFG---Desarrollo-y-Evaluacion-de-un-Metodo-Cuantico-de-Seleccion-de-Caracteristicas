"""Reconstruye notebooks/fase6.ipynb como capítulo incremental anti-meta."""

from pathlib import Path
import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "fase6.ipynb"


def md(text: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(text.strip())


def code(text: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_code_cell(text.strip())


cells: list[nbformat.NotebookNode] = []

cells.append(md("""
# Trabajo de Fin de Grado: Desarrollo y Evaluación de un Método Cuántico de Selección de Características

## Notebook 06 - Modelado clásico y evaluación estadística

Esta fase evalúa si los subconjuntos clásicos de Fase 5 conservan o mejoran el rendimiento predictivo frente a usar todas las variables. El capítulo mantiene una regla estricta: validation selecciona candidatos y test se consulta una sola vez, cuando la decisión ya está cerrada.

La parrilla se amplía al roster completo de 12 métodos. Para cada dataset se evalúan 13 conjuntos de variables: `all_features` y un subconjunto por método; Boruta entra con su tamaño confirmado y el resto entra al k de referencia. La fase usa cuatro modelos fijos, incluido XGBoost como ancla directa con PAPER_QFS, y no recalcula información mutua ni reabre la selección de características.
"""))

cells.append(md("""
## 6.1 Preparación del entorno

La primera celda fija la raíz del proyecto e importa funciones de grano fino desde `src/phase6_modeling`: carga de splits, construcción de parrilla, entrenamiento de un experimento, evaluación de test, bootstrap, contrastes, permutaciones, SHAP lineal y figuras. Cada función devuelve un resultado concreto y se llama en la sección donde se interpreta.
"""))
cells.append(code("""
import os
import sys
from pathlib import Path

import pandas as pd
from IPython.display import Image, Markdown, display

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from phase6_modeling import pipeline as p6

paths = p6.phase6_paths(PROJECT_ROOT)
p6.limpiar_salidas_fase6(paths)
p6.configurar_estilo()

print(f"Datasets: {len(p6.DATASETS)}")
print(f"Modelos: {len(p6.MODEL_NAMES)}")
print(f"Bootstrap: {p6.N_BOOTSTRAP}")
print(f"Permutaciones de etiquetas: {p6.N_LABEL_PERMUTATIONS}")
print(f"Máximo de filas explicadas por SHAP: {p6.SHAP_MAX_EXPLAIN_ROWS}")
"""))
cells.append(md("""
La fase arranca con 5 datasets, 4 modelos, 400 remuestreos bootstrap y 500 permutaciones de etiquetas. Esos valores se mantienen fijos en todo el capítulo para que validation, test e incertidumbre compartan el mismo protocolo. SHAP explica como máximo 1200 filas de validation por candidato mediante una muestra determinista; las métricas y contrastes siguen usando todas las predicciones disponibles.
"""))

cells.append(md("""
## 6.2 Funciones locales de presentación

Estas funciones solo controlan cómo se muestra la evidencia: cabeceras en español, truncado explícito y apertura de PNG guardados. No calculan métricas ni modifican predicciones; el cálculo queda en las funciones importadas desde `src`.
"""))
cells.append(code("""
def tabla_es(tabla, columnas=None, max_filas=12, decimales=3):
    vista = tabla.copy()
    if columnas:
        vista = vista.rename(columns=columnas)
    if len(vista) <= 30:
        display(vista.round(decimales))
    else:
        display(Markdown(f"Se muestran las primeras {max_filas} de {len(vista)} filas."))
        display(vista.head(max_filas).round(decimales))


def mostrar_png(ruta, ancho=850):
    display(Image(filename=str(ruta), width=ancho))
"""))
cells.append(md("""
Las salidas extensas se recortan solo en pantalla. Las tablas completas se guardan en `results/tables/06_modeling/` y las predicciones por fila quedan en `results/predictions/06_modeling/`.
"""))

cells.append(md("""
## 6.3 Protocolo de modelado

El protocolo extiende el paper QFS: allí se comparan subconjuntos con XGBoost y AUC; aquí se usan 4 modelos clásicos con hiperparámetros fijos y Macro-F1 como métrica primaria. XGBoost entra como ancla de comparabilidad con el paper, mientras AUC-ROC se registra solo como contexto en los datasets binarios. Macro-F1 es más adecuada para los casos multiclase y desbalanceados porque cada clase contribuye al promedio, mientras que la exactitud balanceada se reserva como desempate.

Los modelos son regresión logística balanceada (`max_iter=2500`), SVM lineal balanceado (`max_iter=5000`), random forest balanceado (`80` árboles, profundidad máxima `12`, `min_samples_leaf=2`, `max_samples=0.25`) y XGBoost (`200` árboles, profundidad `5`, `learning_rate=0.1`, `subsample=0.8`, `colsample_bytree=0.8`). No se ajustan hiperparámetros en test.
"""))
cells.append(code("""
modelos = pd.DataFrame(
    [
        {"model_name": "logistic_regression", "max_iter": 2500, "class_weight": "balanced"},
        {"model_name": "linear_svm", "max_iter": 5000, "class_weight": "balanced"},
        {"model_name": "random_forest", "n_estimators": 80, "max_depth": 12},
        {"model_name": "xgboost", "n_estimators": 200, "max_depth": 5, "learning_rate": 0.1},
    ]
)
tabla_es(modelos, {"model_name": "Modelo", "max_iter": "Iteraciones", "class_weight": "Pesos", "n_estimators": "Árboles", "max_depth": "Profundidad", "learning_rate": "Learning rate"}, max_filas=5)
"""))
cells.append(md("""
La tabla muestra 4 modelos y sus hiperparámetros fijos. La elección evita que la comparación entre selectores se confunda con una búsqueda de modelo; todos los subconjuntos reciben el mismo bloque de clasificadores.
"""))

cells.append(md("""
## 6.4 Carga de datos y parrilla del roster

Se cargan los splits de Fase 4 y los conjuntos de Fase 5. La parrilla de cada dataset contiene 13 conjuntos: `all_features`, Boruta con su tamaño confirmado y los otros 11 métodos al k de referencia (`10` en datasets grandes y `5` en olive). Boruta no se recorta a k porque su salida es un conjunto confirmado por shadow features.
"""))
cells.append(code("""
split_summary = p6.resumen_splits(paths)
feature_sets = p6.cargar_conjuntos_fase5(paths)
grid = p6.construir_parrilla(paths, feature_sets)

p6.guardar_csv(split_summary, paths.tables / "modeling_input_split_sizes.csv")
p6.guardar_csv(feature_sets, paths.tables / "modeling_feature_sets_from_fase5.csv")
p6.guardar_csv(grid, paths.tables / "modeling_experiment_grid.csv")

tabla_es(split_summary, {"dataset": "Dataset", "train_rows": "Filas train", "validation_rows": "Filas validación", "test_rows": "Filas test", "raw_features": "Variables crudas", "train_classes": "Clases train"}, max_filas=10)
"""))
cells.append(md("""
Se cargan 5 datasets con train, validación y test separados. Customer Churn aporta 308582 filas de train y 66125 de test, mientras que Madelon concentra el mayor número de variables crudas con 500 predictores.
"""))

cells.append(code("""
grid_summary = (
    grid.groupby("dataset", as_index=False)
    .agg(feature_sets=("feature_set", "nunique"), models=("model_name", "nunique"), experiments=("experiment_id", "nunique"))
)
tabla_es(grid_summary, {"dataset": "Dataset", "feature_sets": "Conjuntos", "models": "Modelos", "experiments": "Experimentos"}, max_filas=10)
"""))
cells.append(md("""
Cada dataset queda con 13 conjuntos, 4 modelos y 52 experimentos de validation. En total se entrenan 260 combinaciones antes de fijar los candidatos de test; 240 corresponden a subconjuntos clásicos y 20 a baselines `all_features`.
"""))

cells.append(md("""
## 6.5 Entrenamiento en validation

Cada fila de la parrilla se entrena en train y se evalúa en validation. Se guardan métricas por experimento, tablas granulares por dataset-conjunto-modelo y predicciones por fila; estas predicciones permiten calcular bootstrap, contrastes y reutilización posterior sin reentrenar.
"""))
cells.append(code("""
validation_rows = []
validation_predictions_parts = []
trained_models = {}

for row in grid.itertuples(index=False):
    result, predictions, estimator = p6.entrenar_experimento_validation(paths, row)
    validation_rows.append(result)
    validation_predictions_parts.append(predictions)
    trained_models[row.experiment_id] = estimator

validation_results = p6.enriquecer_validation(pd.DataFrame(validation_rows))
validation_predictions = pd.concat(validation_predictions_parts, ignore_index=True)

p6.guardar_csv(validation_results, paths.tables / "modeling_validation_results_all.csv")
p6.guardar_csv(validation_predictions, paths.predictions / "validation_predictions.csv")

validation_dir = paths.tables / "experiments_validation"
for row in validation_results.itertuples(index=False):
    name = f"validation__{row.dataset}__{row.feature_set}__{row.model_name}.csv"
    p6.guardar_csv(pd.DataFrame([row._asdict()]), validation_dir / name)

tabla_es(
    validation_results.groupby("dataset", as_index=False).agg(experimentos=("experiment_id", "nunique"), mejor_macro_f1=("macro_f1", "max"), peor_macro_f1=("macro_f1", "min")),
    {"dataset": "Dataset", "experimentos": "Experimentos", "mejor_macro_f1": "Mejor Macro-F1", "peor_macro_f1": "Peor Macro-F1"},
    max_filas=10,
)
"""))
cells.append(md("""
Validation evalúa 260 experimentos y conserva predicciones por fila para todos ellos. El rango entre mejor y peor Macro-F1 por dataset muestra cuánto depende el rendimiento de combinar selector y modelo.
"""))

cells.append(md("""
## 6.6 Lectura de validation por dataset

La tabla de cada dataset muestra la parrilla completa ordenada por Macro-F1. Esta lectura local evita promediar problemas de naturaleza distinta y permite ver si la reducción dimensional mejora al baseline del mismo modelo.
"""))
validation_notes = {
    "breast_cancer_wisconsin": "En `breast_cancer_wisconsin` se ordenan 52 combinaciones de validation. La primera posición marca el candidato local más fuerte, y la lectura compara si reducir desde 30 variables conserva Macro-F1 frente al baseline.",
    "customer_churn": "En `customer_churn` aparecen 52 combinaciones de validation sobre el problema con más filas. La tabla permite comprobar si los subconjuntos de 10 o 12 variables mantienen el rendimiento del conjunto completo.",
    "madelon": "En `madelon` se revisan 52 combinaciones de validation con 500 variables de partida. El interés principal es ver qué métodos reducen dimensionalidad sin perder la señal útil del problema artificial.",
    "olive_oil_3class": "En `olive_oil_3class` la parrilla conserva 52 combinaciones de validation, aunque el espacio original tiene solo 8 variables. La comparación se centra en si k=5 basta para retener la separación entre 3 clases.",
    "olive_oil_9class": "En `olive_oil_9class` se muestran 52 combinaciones de validation con 9 clases y 8 variables crudas. La lectura mira la caída asociada a pasar de todas las variables a subconjuntos de 5.",
}
for dataset in ["breast_cancer_wisconsin", "customer_churn", "madelon", "olive_oil_3class", "olive_oil_9class"]:
    cells.append(md(f"### {dataset}"))
    cells.append(code(f"""
local = validation_results[validation_results["dataset"].eq("{dataset}")].sort_values("validation_rank")
tabla_es(
    local[["validation_rank", "feature_set", "model_name", "macro_f1", "balanced_accuracy", "delta_macro_f1_vs_same_model_baseline", "n_features_used"]],
    {{"validation_rank": "Posición", "feature_set": "Conjunto", "model_name": "Modelo", "macro_f1": "Macro-F1", "balanced_accuracy": "Exactitud balanceada", "delta_macro_f1_vs_same_model_baseline": "Delta Macro-F1", "n_features_used": "Variables"}},
    max_filas=52,
)
"""))
    cells.append(md(validation_notes[dataset]))

cells.append(md("""
## 6.7 Candidatos cerrados para test

Los candidatos se fijan con validation: el mejor baseline y los dos mejores subconjuntos distintos por dataset. Los empates se resuelven con una regla neutral y determinista: Macro-F1, exactitud balanceada, reducción dimensional, nombre alfabético del selector, conjunto y tiempo. Así test responde una pregunta cerrada y no funciona como segunda validación.
"""))
cells.append(code("""
candidates = p6.seleccionar_candidatos_test(validation_results)
p6.guardar_csv(candidates, paths.tables / "modeling_test_candidates_from_validation.csv")
tabla_es(
    candidates[["dataset", "candidate_label", "feature_set", "model_name", "macro_f1", "balanced_accuracy", "n_features_used"]],
    {"dataset": "Dataset", "candidate_label": "Etiqueta", "feature_set": "Conjunto", "model_name": "Modelo", "macro_f1": "Macro-F1 validación", "balanced_accuracy": "Exactitud balanceada", "n_features_used": "Variables"},
    max_filas=20,
)
"""))
cells.append(md("""
Quedan 15 candidatos cerrados: 3 por dataset. Esta decisión preserva el anclaje experimental porque ningún resultado de test interviene en la selección.
"""))

cells.append(md("""
## 6.8 Evaluación única en test

Los modelos ya entrenados se aplican al split de test solo para los candidatos cerrados. También se guardan predicciones por fila y una tabla granular por dataset-conjunto-modelo.
"""))
cells.append(code("""
test_rows = []
test_predictions_parts = []
for candidate in candidates.itertuples(index=False):
    result, predictions = p6.evaluar_candidato_test(paths, candidate, trained_models[candidate.experiment_id])
    test_rows.append(result)
    test_predictions_parts.append(predictions)

test_results = pd.DataFrame(test_rows)
test_predictions = pd.concat(test_predictions_parts, ignore_index=True)

p6.guardar_csv(test_results, paths.tables / "modeling_test_results_candidates.csv")
p6.guardar_csv(test_predictions, paths.predictions / "test_predictions.csv")
for model_name, model_predictions in test_predictions.groupby("model_name", sort=False):
    p6.guardar_csv(model_predictions, paths.predictions / f"test_predictions_{model_name}.csv")

test_dir = paths.tables / "experiments_test"
for row in test_results.itertuples(index=False):
    name = f"test__{row.dataset}__{row.feature_set}__{row.model_name}.csv"
    p6.guardar_csv(pd.DataFrame([row._asdict()]), test_dir / name)

tabla_es(
    test_results[["dataset", "candidate_label", "feature_set", "model_name", "validation_macro_f1", "test_macro_f1", "test_balanced_accuracy", "n_features_used"]],
    {"dataset": "Dataset", "candidate_label": "Etiqueta", "feature_set": "Conjunto", "model_name": "Modelo", "validation_macro_f1": "Macro-F1 validación", "test_macro_f1": "Macro-F1 test", "test_balanced_accuracy": "Exactitud balanceada test", "n_features_used": "Variables"},
    max_filas=20,
)
"""))
cells.append(md("""
Test se consulta para 15 candidatos y genera predicciones por fila. La comparación entre Macro-F1 de validation y test permite detectar estabilidad o caída de rendimiento sin reabrir la elección del candidato.
"""))

cells.append(md("""
## 6.9 Intervalos bootstrap

Los intervalos de confianza se calculan sobre predicciones ya guardadas, sin reentrenar. Se usan 400 remuestreos por experimento y se reportan Macro-F1, exactitud balanceada y exactitud para separar rendimiento puntual de incertidumbre muestral.
"""))
cells.append(code("""
validation_intervals = p6.bootstrap_intervalos(validation_predictions, split="validation")
test_intervals = p6.bootstrap_intervalos(test_predictions, split="test")
p6.guardar_csv(validation_intervals, paths.tables / "modeling_validation_confidence_intervals.csv")
p6.guardar_csv(test_intervals, paths.tables / "modeling_test_confidence_intervals.csv")

macro_test = test_intervals[test_intervals["metric"].eq("macro_f1")]
tabla_es(
    macro_test[["dataset", "feature_set", "model_name", "estimate", "ci_low", "ci_high", "n_bootstrap"]],
    {"dataset": "Dataset", "feature_set": "Conjunto", "model_name": "Modelo", "estimate": "Macro-F1", "ci_low": "IC bajo", "ci_high": "IC alto", "n_bootstrap": "Remuestreos"},
    max_filas=20,
)
"""))
cells.append(md("""
Los 15 intervalos de Macro-F1 en test se estiman con 400 remuestreos. Los intervalos amplios señalan resultados que deben interpretarse con cautela, especialmente en datasets con test pequeño o muchas clases.
"""))

cells.append(md("""
## 6.10 Comparaciones pareadas y permutación de etiquetas

Cada subconjunto final se compara contra el baseline del mismo dataset usando las mismas filas de test. La diferencia de Macro-F1 se acompaña de IC bootstrap y de una permutación de signos sobre aciertos por fila; además, cada candidato se contrasta contra una nula de 500 permutaciones de etiquetas.
"""))
cells.append(code("""
paired = p6.comparaciones_pareadas(test_predictions, test_results)
label_perm = p6.permutacion_etiquetas(test_predictions)
p6.guardar_csv(paired, paths.tables / "modeling_pairwise_comparison_tests.csv")
p6.guardar_csv(label_perm, paths.tables / "modeling_permutation_test_results.csv")

tabla_es(
    paired[["dataset", "candidate_experiment_id", "difference_macro_f1", "ci_low", "ci_high", "sign_permutation_p_value", "n_sign_permutations"]],
    {"dataset": "Dataset", "candidate_experiment_id": "Candidato", "difference_macro_f1": "Diferencia Macro-F1", "ci_low": "IC bajo", "ci_high": "IC alto", "sign_permutation_p_value": "p signos", "n_sign_permutations": "Permutaciones"},
    max_filas=15,
)
"""))
cells.append(md("""
Las comparaciones pareadas producen 10 contrastes candidato-baseline, dos por dataset. El signo de la diferencia indica si el subconjunto supera al baseline en las mismas filas de test.
"""))

cells.append(code("""
tabla_es(
    label_perm[["dataset", "feature_set", "model_name", "observed_macro_f1", "null_mean", "null_p95", "p_value", "n_permutations"]],
    {"dataset": "Dataset", "feature_set": "Conjunto", "model_name": "Modelo", "observed_macro_f1": "Macro-F1 observado", "null_mean": "Media nula", "null_p95": "p95 nulo", "p_value": "p valor", "n_permutations": "Permutaciones"},
    max_filas=20,
)
"""))
cells.append(md("""
La permutación de etiquetas evalúa 15 candidatos con 500 permutaciones cada uno. Un Macro-F1 observado por encima del p95 nulo indica que la predicción no se explica bien por azar de etiquetas bajo el candidato fijado.
"""))

cells.append(md("""
## 6.11 SHAP por familia de modelo

La explicación se calcula para los candidatos finales con la librería `shap`: `TreeExplainer` en random forest y XGBoost, y `LinearExplainer` en regresión logística o SVM lineal. El fondo del explicador se toma de train, las variables son las mismas que recibe el modelo tras el preprocesado y se persiste la matriz SHAP cruda con signo por instancia. Para mantener el capítulo ejecutable, SHAP usa una muestra determinista de validation cuando el split es grande; la media de valores absolutos se usa solo como resumen tabular y en los datasets olive se conserva además la dimensión de clase para interpretar qué variables empujan hacia cada variedad.
"""))
cells.append(code("""
shap_parts = []
for candidate in candidates.itertuples(index=False):
    shap_parts.append(p6.shap_candidato(paths, candidate, trained_models[candidate.experiment_id]))
shap_values = pd.concat(shap_parts, ignore_index=True)
p6.guardar_csv(shap_values, paths.tables / "modeling_shap_values_summary.csv")

shap_top = shap_values.groupby(["dataset", "feature"], as_index=False)["mean_abs_shap"].mean().sort_values(["dataset", "mean_abs_shap"], ascending=[True, False])
p6.guardar_csv(shap_top, paths.tables / "modeling_shap_feature_importance.csv")
raw_shap_files = sorted(paths.tables.glob("modeling_shap_values_full_*.csv"))
tabla_es(
    shap_top.groupby("dataset").head(5),
    {"dataset": "Dataset", "feature": "Variable", "mean_abs_shap": "Media |SHAP|"},
    max_filas=25,
)
print(f"Matrices SHAP crudas guardadas: {len(raw_shap_files)}")
"""))
cells.append(md("""
La tabla muestra las 5 variables con mayor contribución absoluta media por dataset, pero la evidencia interpretativa completa queda en las matrices crudas `modeling_shap_values_full_*`. En esas matrices el signo y la dispersión por fila permiten leer dirección del efecto, y en olive la dimensión de clase separa los empujes hacia cada variedad.
"""))

cells.append(md("""
## 6.12 Coste-rendimiento y figuras

Las figuras se construyen con decisiones viz-definitive de Tier 2: intervalos de test, SHAP por dataset y coste-rendimiento. Cada figura se guarda como PNG a 300 dpi y PDF vectorial, y se muestra antes de la lectura.
"""))
cells.append(code("""
cost = p6.coste_rendimiento(validation_results, test_results)
p6.guardar_csv(cost, paths.tables / "modeling_cost_performance.csv")

figure_rows = []
for dataset in p6.DATASETS:
    path_ic = p6.plot_baseline_vs_methods(paths, dataset, test_results, test_intervals)
    path_cost = p6.plot_coste_rendimiento(paths, dataset, cost)
    shap_paths = p6.plot_shap_dataset(paths, dataset, shap_values)
    figure_rows.extend([
        {"dataset": dataset, "family": "baseline_vs_methods_ic", "path": str(path_ic.relative_to(PROJECT_ROOT))},
        {"dataset": dataset, "family": "cost_performance", "path": str(path_cost.relative_to(PROJECT_ROOT))},
    ])
    for path_shap in shap_paths:
        figure_rows.append({"dataset": dataset, "family": "shap_summary", "path": str(path_shap.relative_to(PROJECT_ROOT))})
p6.guardar_csv(pd.DataFrame(figure_rows), paths.tables / "modeling_figures_index.csv")
p6.registrar_decisiones_figuras(paths)

for row in figure_rows:
    mostrar_png(PROJECT_ROOT / row["path"], ancho=780)
"""))
cells.append(md("""
Se muestran las figuras de intervalos, coste-rendimiento y SHAP. En los datasets olive aparecen beeswarms adicionales por clase, de modo que el resumen global no mezcla direcciones de efecto incompatibles.
"""))

cells.append(md("""
## 6.13 Cierre científico de Fase 6

La fase deja cerrada la referencia clásica: 260 experimentos de validation, 15 candidatos test, predicciones por fila, intervalos bootstrap, comparaciones pareadas, permutaciones de etiquetas y explicación SHAP. La comparación con QFS puede hacerse después sin reentrenar estos modelos.
"""))
cells.append(code("""
summary = pd.DataFrame(
    [
        {"Magnitud": "Experimentos validation", "Valor": validation_results["experiment_id"].nunique()},
        {"Magnitud": "Candidatos test", "Valor": test_results["experiment_id"].nunique()},
        {"Magnitud": "Predicciones validation", "Valor": len(validation_predictions)},
        {"Magnitud": "Predicciones test", "Valor": len(test_predictions)},
        {"Magnitud": "Figuras PNG", "Valor": len(list(paths.figures.rglob("*.png")))},
        {"Magnitud": "Figuras PDF", "Valor": len(list(paths.figures.rglob("*.pdf")))},
    ]
)
p6.guardar_csv(summary, paths.tables / "modeling_phase6_summary.csv")
tabla_es(summary, max_filas=10)
"""))
cells.append(md("""
El cierre confirma 260 experimentos de validation y 15 candidatos test. Las predicciones guardadas por fila son la base para comparar la fase clásica con QFS sin volver a entrenar modelos ni consultar test de nuevo.
"""))

nb = nbformat.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "qfs_env", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}
NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, NOTEBOOK)
print(f"Notebook reconstruido: {NOTEBOOK}")
