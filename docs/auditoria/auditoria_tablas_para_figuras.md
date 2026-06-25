# Auditoria de tablas para construir figuras

> 2026-06-16. Analisis centrado en las tablas disponibles, no en el diseno de
> figuras. Objetivo: saber que datos existen, con que granularidad, que llaves
> permiten unirlos y que limitaciones hay antes de generar nuevas figuras.

## Resumen ejecutivo

El repositorio contiene **1036 CSVs** en `results/tables/`. No todos son fuentes
primarias utiles para figuras: muchos son resultados por experimento, salidas por
dataset/beta o tablas derivadas. Las fuentes mas importantes son unas 35 tablas
madre repartidas por fases.

Distribucion inspeccionada:

| Bloque | N tablas | Uso principal |
|---|---:|---|
| `01_raw_eda` | 25 | estructura inicial, senal, FDR, efecto, correlacion, PCA |
| `02_preprocessing` | 20 | transformaciones raw -> processed |
| `03_postprocessing_audit` | 25 | conservacion, shift, VIF, asociacion procesada |
| `04_split_audit` | 23 | splits, drift, leakage, validacion adversarial |
| `05_feature_selection` | 529 | rankings, features seleccionadas, estabilidad, permutacion, QFS handoff |
| `06_modeling` | 320 | grid de experimentos, validation/test, bootstrap, SHAP |
| `07_final_comparison` | 7 | comparacion clasica final y handoff hacia QFS |
| `08_quantum` | 84 | validacion QFS, seleccion final, oraculo, runs por beta, control, MDS |
| `10_memoria_*` | 3 | tablas resumidas para figuras de memoria |

La conclusion importante: **hay datos suficientes para figuras muy rigurosas**,
pero hay que construirlas desde tablas madre, no desde PNGs ya existentes.

## 1. Tablas para caracterizar datasets

### Fuentes principales

| Tabla | Filas | Grano | Columnas clave |
|---|---:|---|---|
| `01_raw_eda/fase1_sintesis_evidencias.csv` | 4 | dataset raw | `filas`, `features`, `n_clases`, `ratio_mayoritaria_minoritaria`, `significativas_fdr`, `pares_correlacion_alta`, `componentes_80` |
| `01_raw_eda/fase1_asociacion_target_resumen.csv` | 4 | dataset raw | `variables_contrastadas`, `variables_fdr_005`, `efecto_abs_mediano`, `efecto_abs_maximo` |
| `03_postprocessing_audit/fase3_asociacion_tests.csv` | 4 | dataset processed | `spearman_rankings_raw_processed`, `mi_spearman_raw_processed`, `top_k_overlap_ratio`, `proporcion_fdr_significativas_005` |
| `04_split_audit/fase4_resumen_xy.csv` | 5 | dataset final | `filas`, `features`, `target_clases`, `target_en_X`, `categoricas_en_X` |

### Lectura tecnica

- Fase 1 trabaja con 4 datasets: `olive_oil` aun no esta dividido en 3/9 clases.
- Fase 4 ya trabaja con 5 formulaciones: `olive_oil_3class` y
  `olive_oil_9class`.
- Para figuras finales conviene usar Fase 4 como base dimensional y Fase 1/3
  como evidencia estadistica previa.

### Joins seguros

- `dataset` directo entre tablas de fase 4, 5, 6, 7 y 8.
- Para unir fase 1/3 con fase 4 hay que mapear `olive_oil` a
  `olive_oil_3class` y `olive_oil_9class` si la evidencia aplica a ambas
  formulaciones.

## 2. Tablas para limpieza, drift, leakage y confianza experimental

### Fuentes principales

| Tabla | Filas | Grano | Columnas clave |
|---|---:|---|---|
| `04_split_audit/fase4_validacion_adversarial.csv` | 5 | dataset | `auc_cv`, `auc_fold_std`, `auc_min`, `auc_max` |
| `04_split_audit/fase4_drift_resumen.csv` | 5 | dataset | `variables_con_flag`, `max_psi`, `max_distancia`, `max_drift_score` |
| `04_split_audit/fase4_drift_variables.csv` | 1112 | dataset x comparacion x variable | `statistic`, `p_value`, `distancia`, `psi`, `drift_score`, `drift_flag` |
| `04_split_audit/fase4_leakage_screening.csv` | 556 | dataset x variable | `nombre_sospechoso`, `auc_abs_binaria`, `nmi_con_target`, `unique_ratio` |
| `03_postprocessing_audit/fase3_vif_processed.csv` | 547 | dataset x variable | `vif` |

### Lectura tecnica

Estas tablas permiten figuras de garantia metodologica. La granularidad por
variable existe (`drift_variables`, `leakage_screening`, `vif_processed`), y el
resumen por dataset tambien (`drift_resumen`, `validacion_adversarial`).

### Cuidado

- `auc_cv` cercano a 0.5 es bueno en validacion adversarial; no debe tratarse
  como rendimiento predictivo.
- `fase3_vif_processed.csv` solo tiene 4 datasets por el mismo problema de
  `olive_oil` no desdoblado.

## 3. Tablas para seleccion clasica

### Fuentes principales

| Tabla | Filas | Grano | Columnas clave |
|---|---:|---|---|
| `05_feature_selection/fs_method_registry.csv` | 12 | metodo | `method`, `familia`, `usa_target`, `salida`, `criterio_tecnico` |
| `05_feature_selection/fs_method_profiles.csv` | 12 | metodo | `segundos_medios`, `jaccard_medio`, `corr_media_seleccionada` |
| `05_feature_selection/fs_all_rankings.csv` | 116334 | dataset x metodo x seed x k x feature | `family`, `rank`, `score`, `selected`, `elapsed_seconds`, `sample_size`, `status` |
| `05_feature_selection/fs_all_selected_features.csv` | 9267 | dataset x metodo x seed x k x feature seleccionada | igual que rankings, pero `selected=True` |
| `05_feature_selection/fs_selected_feature_sets.csv` | 250 | dataset x metodo x k | `n_features`, `path` |
| `05_feature_selection/fs_jaccard_stability.csv` | 735 | dataset x metodo x k x par de seeds | `seed_a`, `seed_b`, `jaccard` |
| `05_feature_selection/fs_permutation_summary.csv` | 10 | dataset x metodo | `n_features_above_null`, `median_empirical_p_value`, `n_permutations` |
| `05_feature_selection/fs_redundancy_vs_full.csv` | 250 | dataset x metodo x k | `full_mean_abs_corr`, `selected_mean_abs_corr`, `delta_mean_abs_corr`, `selected_high_corr_pairs` |

### Lectura tecnica

Este es el bloque mas potente para figuras de proceso:

- Hay 12 metodos.
- Hay 5 datasets.
- Hay 3 semillas (`13`, `42`, `97`) en rankings/seleccion.
- Hay muchos valores de `k`: `1`, `3`, `4`, `5`, `8`, `10`, `12`, `15`, `19`,
  `20`, `22`, `30`, `50` segun dataset/metodo.
- Hay ranking completo, no solo subset final.

### Joins seguros

- `fs_all_rankings` <-> `fs_method_registry`: `method`.
- `fs_all_selected_features` <-> `fs_jaccard_stability`: `dataset`, `method`, `k`.
- `fs_redundancy_vs_full` <-> `fs_selected_feature_sets`: `dataset`, `method`, `k`.
- `fs_all_selected_features` <-> SHAP/QFS por `dataset`, `feature`, con cuidado
  porque SHAP esta por `feature_set`/modelo y QFS por `selected_features` serializado.

### Limitaciones

- `fs_permutation_summary.csv` solo cubre 2 metodos (`f_classif`,
  `mutual_info`), no los 12.
- `fs_jaccard_stability.csv` tiene 11 metodos, no 12; Boruta puede quedar fuera
  de estabilidad por semillas.

## 4. Tablas de handoff hacia QFS

### Fuentes principales

| Tabla | Filas | Grano | Columnas clave |
|---|---:|---|---|
| `05_feature_selection/fs_qfs_mi_target_vector_long.csv` | 561 | dataset x feature | `I_i` |
| `05_feature_selection/fs_qfs_pairwise_mi_matrix_long.csv` | 561 | dataset x feature, formato ancho | columnas de features + `dataset` |
| `05_feature_selection/fs_qfs_handoff_matrices_index.csv` | indice | dataset/tablas | rutas de matrices |
| `07_final_comparison/fase7_handoff_qfs.csv` | 5 | dataset | `k_referencia`, `mean_I_i`, `max_I_i`, `mean_R_ij_offdiag`, `max_R_ij_offdiag`, rutas MI |

### Lectura tecnica

Aqui esta el puente real entre lo clasico y QFS:

- `I_i` permite comparar relevancia individual con seleccion clasica y SHAP.
- `R_ij` permite comparar redundancia/estructura con mRMR, RRFS, MDS y criterio
  QUBO.
- `fase7_handoff_qfs.csv` resume por dataset y evita recalcular medias.

### Cuidado

`fs_qfs_pairwise_mi_matrix_long.csv` se llama `long`, pero en realidad esta en
formato ancho: una fila por `dataset`/`feature` y muchas columnas de features.
Para heatmaps o MDS hay que pivotar/filtrar por dataset.

## 5. Tablas para modelado clasico

### Fuentes principales

| Tabla | Filas | Grano | Columnas clave |
|---|---:|---|---|
| `06_modeling/modeling_experiment_grid.csv` | 260 | dataset x feature_set x modelo | `selector`, `k`, `n_features`, `model_name`, `experiment_id` |
| `06_modeling/modeling_validation_results_all.csv` | 260 | experimento validation | `macro_f1`, `balanced_accuracy`, `accuracy`, `auc_roc`, `fit_seconds`, `baseline_macro_f1_same_model`, `delta_macro_f1_vs_same_model_baseline`, `feature_reduction_ratio`, `validation_rank` |
| `06_modeling/modeling_cost_performance.csv` | 260 | experimento validation + test parcial | columnas anteriores + `test_macro_f1`, `test_balanced_accuracy` |
| `06_modeling/modeling_test_confidence_intervals.csv` | 45 | experimento x metrica | `metric`, `estimate`, `ci_low`, `ci_high`, `n_bootstrap` |
| `06_modeling/modeling_pairwise_comparison_tests.csv` | 10 | dataset x comparacion pareada | `difference_macro_f1`, `ci_low`, `ci_high`, `sign_permutation_p_value` |
| `06_modeling/modeling_permutation_test_results.csv` | 15 | experimento | `observed_macro_f1`, `null_mean`, `null_p95`, `p_value`, `n_permutations` |

### Lectura tecnica

Este bloque permite construir:

- curvas/rankings por `k`;
- rendimiento por modelo;
- coste vs rendimiento;
- reduccion de features vs rendimiento;
- bootstrap en test;
- tests pareados;
- permutacion del modelo contra nulo.

### Joins seguros

- `modeling_experiment_grid` <-> `modeling_validation_results_all`:
  `experiment_id`.
- `modeling_validation_results_all` <-> `modeling_test_confidence_intervals`:
  `experiment_id`, `dataset`, `feature_set`, `model_name`.
- `modeling_validation_results_all` <-> `fs_redundancy_vs_full`:
  `dataset`, `selector`/`method`, `k`; hay que normalizar nombre
  `selector` vs `method`.

### Limitaciones

- `modeling_test_confidence_intervals.csv` solo tiene 45 filas: 15
  experimentos x 3 metricas, no los 260 de validation.
- Test completo solo esta para candidatos finales, no para todo el grid.
- AUC solo es interpretable en binarios; no debe mezclarse sin filtro.

## 6. Tablas SHAP

### Fuentes principales

| Tabla | Filas | Grano | Columnas clave |
|---|---:|---|---|
| `06_modeling/modeling_shap_values_summary.csv` | 665 | experimento x feature | `mean_abs_shap`, `rank`, `raw_values_path`, `feature_values_path`, `shap_value_shape`, `output_labels` |
| `06_modeling/modeling_shap_feature_importance.csv` | 561 | dataset x feature | `mean_abs_shap` |
| `06_modeling/modeling_shap_values_full_*.csv` | varios | instancia x feature/clase | valores SHAP crudos |
| `06_modeling/modeling_shap_feature_values_*.csv` | varios | instancia x feature | valores originales de features |

### Lectura tecnica

Hay dos niveles:

1. Resumen (`mean_abs_shap`) para rankings y concordancia con seleccion.
2. Matriz cruda + valores de feature para beeswarm por instancia.

### Joins seguros

- SHAP resumen <-> seleccion clasica: `dataset`, `feature`.
- SHAP resumen <-> QFS `I_i`: `dataset`, `feature`.
- SHAP resumen <-> fase 7: `experiment_id`.

### Limitaciones

- SHAP detallado no esta para los 260 experimentos, sino para 15 candidatos
  finales aproximadamente.
- Para multiclase, hay que respetar `output_labels`/forma de matriz; no colapsar
  sin declararlo.

## 7. Tablas de comparacion clasica final

### Fuentes principales

| Tabla | Filas | Grano | Columnas clave |
|---|---:|---|---|
| `07_final_comparison/fase7_tabla_maestra.csv` | 15 | dataset x candidato final | `validation_macro_f1`, `test_macro_f1`, `test_macro_f1_ci_low`, `test_macro_f1_ci_high`, `difference_candidate_minus_baseline`, `paired_correctness_permutation_pvalue`, `paired_pvalue_fdr` |
| `07_final_comparison/fase7_comparacion_final.csv` | 5 | dataset | `baseline_test_macro_f1`, `seleccion_test_macro_f1`, `delta_test_macro_f1`, `delta_ci_low`, `delta_ci_high`, `p_valor_pareado_fdr` |
| `07_final_comparison/fase7_handoff_qfs.csv` | 5 | dataset | referencia clasica + resumen `I_i/R_ij` |

### Lectura tecnica

Estas son las tablas que deben cerrar el bloque clasico. Tienen la granularidad
correcta para veredicto, pero no sustituyen al grid de fase 6. Si una figura
necesita mostrar procedimiento, debe volver a `modeling_validation_results_all`
o `modeling_cost_performance`.

## 8. Tablas QFS

### Fuentes principales

| Tabla | Filas | Grano | Columnas clave |
|---|---:|---|---|
| `08_quantum/qfs_validation_results.csv` | 60 | dataset x configuracion x alpha/beta | `configuration`, `alpha`, `beta`, `k`, `selected_features`, `validation_macro_f1` |
| `08_quantum/qfs_selected_all.csv` | 10 | dataset x configuracion final | igual que anterior, solo seleccion final |
| `08_quantum/qfs_model_results.csv` | 40 | dataset x configuracion x modelo | `model_name`, `test_macro_f1`, `validation_macro_f1`, `test_auc_roc` |
| `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | 10 | dataset x configuracion | `baseline_test_macro_f1`, `qfs_test_macro_f1`, `delta_test_macro_f1`, `delta_ci_low`, `delta_ci_high`, `veredicto` |
| `08_quantum/qfs_quality_control_*.csv` | 11 por dataset | dataset x beta | `hamming_distance`, `q_na_alpha05`, `q_oracle_alpha05`, `delta_cost_alpha05` |
| `08_quantum/qfs_oracle_*.csv` | 12 por dataset | dataset x alpha | `cardinality`, `q_opt`, `selected_features` |
| `08_quantum/qfs_embedding_error.csv` | 55 | dataset x beta | `embedding_error_mean`, `embedding_error_p95`, `target_distance_mean`, `mds_distance_mean`, `positions_json` |
| `08_quantum/qfs_runs_*_*.csv` | variable | dataset x beta x bitstring/result | `cost_f`, `count`, `bitstring`, `selected_features`, `density__*` |

### Lectura tecnica

Este bloque permite separar:

- seleccion por alpha/beta;
- rendimiento validation/test;
- comparacion contra baseline;
- control oraculo vs QFS-NA;
- densidades por variable;
- error MDS/embebido;
- frecuencia de bitstrings y coste.

### Joins seguros

- `qfs_selected_all` <-> `comparacion_qfs_configuraciones_vs_baseline`:
  `dataset`, `configuration`.
- `qfs_model_results` <-> `comparacion_qfs_configuraciones_vs_baseline`:
  `dataset`, `configuration`, con cuidado porque `qfs_model_results` tiene 4
  modelos por configuracion y comparacion ya parece elegir modelo final.
- `qfs_quality_control_*` <-> `qfs_validation_results`: `dataset`, `beta`, `k`.
- `qfs_oracle_*` <-> `qfs_selected_all`: `dataset`, `alpha`, `configuration`
  filtrando `qfs_oracle_mucke`.
- `qfs_embedding_error` <-> `qfs_selected_all`: `dataset`, `beta`.

### Limitaciones

- `qfs_validation_results.csv` tiene 60 filas: no es grid completo
  `alpha x beta` para ambas configuraciones. Parece: QFS-NA barre beta con alpha
  fijo/operativo y oraculo aporta puntos alpha. Hay que leer `configuration`
  antes de asumir una malla rectangular.
- `qfs_runs_*` tiene columnas `density__*` distintas por dataset; para una tabla
  unificada hay que derretir columnas `density__` a formato largo.
- `positions_json` en `qfs_embedding_error.csv` permite reconstruir coordenadas,
  pero exige parseo JSON.

## 9. Tablas de memoria derivadas

| Tabla | Filas | Grano | Uso |
|---|---:|---|---|
| `results/tables/10_memoria_b2_jaccard_metodos.csv` | 60 | dataset x metodo | solape QFS-clasicos + relevancia/redundancia |
| `results/tables/10_memoria_b10_consistencia.csv` | 53 | dataset x metodo x k | consistencia Jaccard resumida |
| `results/tables/10_memoria_b9_embedding_error.csv` | 5 | dataset | error MDS para configuracion seleccionada |

Estas tablas son utiles para figuras finales, pero son derivadas. Si hay una
contradiccion, prevalecen las fuentes de fase 5/8.

## 10. Llaves canonicas para construir datasets de figura

| Entidad | Llaves |
|---|---|
| Dataset final | `dataset` |
| Feature | `dataset`, `feature` |
| Selector clasico | `dataset`, `method`, `k`, `seed`, `feature` |
| Set clasico materializado | `dataset`, `method`, `k` |
| Experimento de modelo | `experiment_id` |
| Resultado validation | `dataset`, `feature_set`, `model_name`, `experiment_id` |
| Resultado test final | `dataset`, `feature_set`, `model_name`, `experiment_id` |
| QFS validation | `dataset`, `configuration`, `alpha`, `beta`, `k` |
| QFS final | `dataset`, `configuration` |
| Oraculo QFS | `dataset`, `alpha` |
| Control QFS | `dataset`, `beta`, `k` |
| MDS/QFS geometry | `dataset`, `beta` |

## 11. Huecos y precauciones antes de graficar

1. **Olive raw vs Olive 3/9:** fases 1--3 tienen `olive_oil`; fases 4--8 tienen
   `olive_oil_3class` y `olive_oil_9class`.
2. **No todo tiene test:** los 260 experimentos son validation; test/IC estan
   para candidatos finales.
3. **No todo tiene SHAP crudo:** SHAP detallado existe para candidatos finales,
   no para todo el grid.
4. **Permutaciones no cubren todos los selectores:** `fs_permutation_summary`
   solo cubre `f_classif` y `mutual_info`.
5. **QFS no es una malla rectangular simple:** no asumir `alpha x beta` completo
   sin filtrar `configuration`.
6. **Columnas serializadas:** `selected_features`, `positions_json` y rutas de
   SHAP requieren parseo, no split ingenuo si contienen caracteres especiales.
7. **Nombres selector/metodo:** fase 5 usa `method`; fase 6 usa `selector` y
   `feature_set`. Hay que normalizar.
8. **Metricas binarias/multiclase:** `auc_roc` no debe mezclarse con datasets
   multiclase sin declarar el filtro o el criterio.

## 12. Recomendacion de trabajo

Antes de crear o modificar figuras, construir datasets intermedios limpios en
`results/tables/10_memoria_*` o similar, uno por pregunta:

| Pregunta de datos | Tablas fuente | Dataset intermedio recomendado |
|---|---|---|
| Regimen de dataset final + senal previa | fase 4 + fase 1/3 | `10_memoria_dataset_regimen_signal.csv` |
| Perfil selector completo | registry + profiles + stability + redundancy | `10_memoria_selector_profile.csv` |
| Trayectoria `k` seleccion/rendimiento | redundancy + validation results | `10_memoria_k_path.csv` |
| Concordancia seleccion-SHAP-QFS | selected features + SHAP + QFS selected + `I_i` | `10_memoria_feature_concordance.csv` |
| Diagnostico QFS | comparacion QFS + quality control + selected all | `10_memoria_qfs_diagnosis.csv` |
| Geometria QFS | embedding error + selected all + qfs runs | `10_memoria_qfs_geometry.csv` |

Asi las figuras dejan de depender de joins repetidos dentro del plotter y pasan
a tener una fuente tabular auditable.
