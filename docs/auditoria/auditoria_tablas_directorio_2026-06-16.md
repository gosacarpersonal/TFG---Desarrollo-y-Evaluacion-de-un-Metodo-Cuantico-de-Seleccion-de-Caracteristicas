# Auditoría de tablas del directorio

Fecha: 2026-06-16.

## Alcance

Se inventariaron ficheros `.csv`, `.tsv` y `.xlsx` en todo el repositorio, excluyendo `.git`. La auditoría separa el núcleo del TFG (`data/`, `results/`, `QFS_based_on_NA/`) de `.agents/`, porque `.agents/` contiene assets de skills y no resultados científicos del trabajo.

Artefactos generados:

- `docs/auditoria/inventario_tablas_2026-06-16.csv`: inventario fila a fila.
- `docs/auditoria/inventario_tablas_familias_2026-06-16.csv`: resumen por fase/familia.
- `docs/auditoria/auditoria_tablas_directorio_2026-06-16.md`: este informe.

## Resumen ejecutivo

- Tablas totales detectadas: 3153.
- Tablas del núcleo TFG, sin `.agents` ni salidas de esta auditoría: 2785.
- Tablas en `.agents`: 366.
- Tablas con referencia directa por ruta: 164.
- Tablas mencionadas por nombre: 386.
- Tablas consumidas por convención/patrón: 1027.
- Artefactos de fase sin referencia directa detectada: 855.
- Sin uso detectado automático: 355.

La lectura importante: muchas tablas no aparecen citadas una a una porque son consumidas por patrón de carpeta. El caso más claro es `data/selected_features/`, donde Fase 6 consume matrices por dataset/selector/k/split, no por referencias literales a cada CSV.

## Resumen por fase/zona

| phase | files | size_mb | used_or_convention | no_direct_ref | question |
| --- | --- | --- | --- | --- | --- |
| 01_raw_eda | 25 | 8.4 | 25 | 0 | Datos crudos: estructura, señales iniciales y riesgos. |
| 02_preprocessing | 20 | 0.2 | 20 | 0 | Preprocesado: transformaciones y datasets procesados. |
| 03_postprocessing_audit | 25 | 0.4 | 25 | 0 | Auditoría postprocesado: leakage, drift, duplicados, coherencia. |
| 04_split_audit | 23 | 12.8 | 23 | 0 | Splits: índices, balance y reproducibilidad train/validation/test. |
| 05_feature_selection | 529 | 35.9 | 19 | 510 | Selección clásica: variables, estabilidad, coste y redundancia. |
| 06_modeling | 320 | 9.1 | 45 | 275 | Modelado: métricas, candidatos, intervalos, contrastes e interpretación. |
| 07_final_comparison | 5 | 0.0 | 5 | 0 | Síntesis clásica final y handoff hacia QFS. |
| 08_quantum | 84 | 1.1 | 14 | 70 | QFS: runs, selección, calidad, oráculos y comparación contra baseline. |
| 10_memoria | 3 | 0.0 | 3 | 0 | Memoria: tablas de síntesis para figuras/narrativa. |
| data_processed | 4 | 23.4 | 4 | 0 | Datos procesados listos para análisis. |
| data_raw | 9 | 59.0 | 9 | 0 | Fuente original de datos. |
| data_selected_features | 1260 | 2375.0 | 1260 | 0 | Matrices resultantes de selectores por dataset/k/split. |
| data_splits | 30 | 29.2 | 30 | 0 | Filas/columnas de cada split reproducible. |
| legacy_qfs | 9 | 0.1 | 3 | 6 | Resultados históricos o auxiliares del QFS heredado. |
| legacy_qfs_data | 2 | 1.6 | 2 | 0 | Datasets heredados del código QFS auxiliar. |
| logs | 11 | 0.1 | 9 | 2 | Logs tabulares de ejecución/verificación. |
| predictions | 6 | 539.4 | 6 | 0 | Predicciones por fila para verificación y fases posteriores. |
| previous_run_logs | 420 | 44.6 | 73 | 347 | Tablas archivadas de runs anteriores. |

## Top tablas por tamaño en el núcleo TFG

| path | phase | family | role | size_mb | rows_counted | n_columns |
| --- | --- | --- | --- | --- | --- | --- |
| results/predictions/06_modeling/validation_predictions.csv | predictions | predictions | usada_directamente_por_ruta | 382.669 |  | 9 |
| results/predictions/08_quantum/validation_predictions_qfs.csv | predictions | predictions | usada_directamente_por_ruta | 61.225 | 533456 | 10 |
| results/predictions/08_quantum/test_predictions_qfs.csv | predictions | predictions | usada_directamente_por_ruta | 58.175 | 533464 | 10 |
| data/selected_features/customer_churn/f_classif/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/feature_similarity/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/l1_logistic/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/linear_svm/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/mrmr_approx/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/mutual_correlation/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/mutual_info/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/random_forest/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/rrfs/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/variance/k_15/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 49.733 | 308582 | 15 |
| data/selected_features/customer_churn/boruta/k_12/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 46.202 | 308582 | 12 |
| data/selected_features/customer_churn/mrmr_approx/k_10/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 43.847 | 308582 | 10 |
| data/selected_features/customer_churn/feature_similarity/k_10/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 43.847 | 308582 | 10 |
| data/selected_features/customer_churn/l1_logistic/k_10/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 43.847 | 308582 | 10 |
| data/selected_features/customer_churn/variance/k_10/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 43.847 | 308582 | 10 |
| data/selected_features/customer_churn/f_classif/k_10/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 34.682 | 308582 | 10 |
| data/selected_features/customer_churn/mutual_info/k_10/X_train_selected.csv | data_selected_features | selected_feature_matrices | usada_directamente_por_ruta | 34.682 | 308582 | 10 |

## Cómo leer la columna `role`

- `usada_directamente_por_ruta`: algún script/notebook/doc/tex contiene la ruta exacta.
- `mencionada_por_nombre`: aparece el nombre del archivo, pero no la ruta completa; puede ser uso real o mención documental.
- `entrada_de_pipeline_por_convencion`: dataset de entrada esperado por estructura de carpetas.
- `consumida_por_patron_directorio_fase6`: matrices de `data/selected_features/` consumidas por patrón; no deben deduplicarse ni borrarse por falta de referencia literal.
- `salida_regenerable_o_consumida_por_fases_posteriores`: predicciones por fila; algunas están ignoradas en git pero siguen siendo necesarias/regenerables.
- `artefacto_de_fase_no_referenciado_directamente`: tabla de resultados disponible para auditoría/reporte, aunque ningún archivo la cite literalmente.
- `sin_uso_detectado`: no se infirió uso ni por ruta, ni por nombre, ni por convención conocida.
- `auxiliar_agents_fuera_nucleo_tfg`: CSV de `.agents`; fuera del análisis científico principal.

## De dónde salen y qué preguntan

### `data/01_raw/`

Datos fuente externos. Responden qué información original entra al proyecto. No se consideran outputs limpiables.

### `data/processed/`

Salidas de preprocesado. Responden cómo queda cada dataset tras normalización, limpieza y codificación.

### `data/splits/`

Salidas de Fase 4. Responden qué filas quedan en train, validation y test, y permiten reproducir los splits.

### `data/selected_features/`

Salidas de Fase 5. Responden qué matriz resulta al aplicar cada selector y cada k a train/validation/test. Se consumen por patrón de directorio en Fase 6. Los pares `X_val_selected.csv` y `X_validation_selected.csv` son alias intencionados.

### `results/tables/01_raw_eda/` a `results/tables/04_split_audit/`

Tablas de auditoría de datos, preprocesado, postprocesado y particionado. Responden a calidad, leakage, drift, consistencia y trazabilidad antes del modelado.

### `results/tables/05_feature_selection/`

Tablas de ranking, estabilidad, redundancia, permutación, handoff y granularidad de selectores. Responden qué variables se eligen, con qué robustez y bajo qué coste.

### `results/tables/06_modeling/`

Tablas de validation/test, candidatos, intervalos, contrastes, coste y SHAP. Responden qué modelos/subconjuntos rinden mejor y cómo se interpretan. Incluyen XGBoost en la parrilla actual.

### `results/tables/07_final_comparison/`

Síntesis final clásica y handoff hacia QFS. Importante: `fase7_comparacion_final.csv` se conserva porque lo lee Fase 9 como baseline clásico.

### `results/tables/08_quantum/`

Resultados QFS: runs por beta/configuración, selección de variables, calidad, oráculos, comparaciones contra baseline y validación. Responden si QFS aporta o no frente a alternativas clásicas.

### `results/tables/10_*`

Tablas auxiliares de memoria/figuras narrativas. Responden preguntas de síntesis visual, consistencia y atribución para la memoria.

### `results/predictions/`

Predicciones por fila. Son pesadas y regenerables, pero útiles para verificación, Fase 9 y comparación por instancia.

### `QFS_based_on_NA/Results/`

Resultados históricos o auxiliares del código QFS heredado. Conviene tratarlos como referencia/legacy, no como run canónico salvo que un notebook actual los cite.

### `.agents/`

Contiene CSVs de assets/ejemplos de skills. No forman parte del pipeline TFG.

## Hallazgos prácticos

1. El grueso de tablas no está en `results/tables`, sino en `data/selected_features/` y predicciones. Eso no implica basura: muchas son entradas derivadas para modelado.
2. Las tablas más claramente vivas por uso directo son las citadas en scripts/notebooks de fases posteriores: splits, resultados de modelado, comparación final clásica y predicciones.
3. Las tablas de `results/tables/05_feature_selection/granular/` y muchos CSV de `experiments_validation/` no suelen citarse individualmente; son trazabilidad granular.
4. `.agents/` aporta ruido para una auditoría científica. Puede excluirse de informes TFG salvo que se auditen skills.
5. `results/predictions/06_modeling/test_predictions*.csv` están ignoradas/desindexadas pero siguen presentes y son regenerables.

## Limitaciones

- La detección de uso literal busca rutas/nombres en código, notebooks, docs y LaTeX. No ejecuta análisis dinámico de paths construidos con variables.
- Las tablas muy grandes no siempre tienen conteo exacto de filas para evitar una pasada costosa sobre gigabytes; sí se extrae cabecera cuando es legible.
- `artefacto_de_fase_no_referenciado_directamente` no significa borrable: significa que no hay referencia literal detectada. En resultados científicos puede ser trazabilidad útil.

## Recomendación para limpieza futura

Para decidir limpieza futura, filtrar `inventario_tablas_2026-06-16.csv` por:

1. `role == sin_uso_detectado` y `root != .agents`.
2. `role == artefacto_de_fase_no_referenciado_directamente`, revisando fase/familia.
3. `size_mb` descendente.
4. No tocar `data/selected_features/` salvo decisión explícita de reproducibilidad.
