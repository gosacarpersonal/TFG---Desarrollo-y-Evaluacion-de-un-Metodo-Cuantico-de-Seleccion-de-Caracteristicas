# Asignacion de CSVs a superfiguras

> 2026-06-16. Traduccion operativa de la arquitectura de superfiguras a
> fuentes tabulares reales. Este documento no decide estilo grafico: asigna
> CSVs, llaves, granularidad y tablas intermedias para poder construir figuras
> reproducibles.

## Regla de trabajo

Cada superfigura debe nacer de una tabla intermedia auditable en
`results/tables/10_memoria_*.csv`. Los plotters no deberian repetir joins
complejos ni parseos fragiles; deben leer una tabla ya preparada para la
pregunta.

Salvo que se indique una ruta completa, las rutas CSV de este documento son
relativas a `results/tables/`.

## SF1 — Recorrido experimental del TFG

**Unidad:** fase / bloque metodologico.  
**Funcion tabular:** inventario de artefactos y cobertura.

| Panel | CSVs fuente | Grano | Uso |
|---|---|---|---|
| Recorrido completo | `07_final_comparison/fase7_inventario_artefactos.csv` | artefacto/fase | Evidenciar que hay fases, tablas y figuras generadas |
| Estado de figuras memoria | `scripts/build_memoria_figuras.py` (`FIGURE_FILES`, `SOURCES`) | figura | No es CSV, pero es el manifiesto real de procedencia |
| Cierre de verificacion | `results/logs/*/*verification_report.json` | fase/verificacion | Apoyo si se quiere mostrar checks OK |

**Tabla intermedia recomendada:** `results/tables/10_memoria_recorrido_fuentes.csv`

Columnas:

```text
fase,bloque,artefactos_tabla,artefactos_figura,verificador,estado,fuente_principal
```

**Nota:** aqui no hace falta granularidad experimental; hace falta trazabilidad
de pipeline.

## SF2 — Banco experimental / regimenes

**Unidad:** dataset/formulacion (`D=5`).  
**Funcion tabular:** describir dificultad y regimen antes de comparar metodos.

| Panel | CSVs fuente | Join | Columnas utiles |
|---|---|---|---|
| A. Tamano vs dimensionalidad | `04_split_audit/fase4_resumen_xy.csv` | `dataset` | `filas`, `features`, `target_clases` |
| B. Desbalance/clases | `04_split_audit/fase4_target_distribucion.csv`, `04_split_audit/fase4_resumen_xy.csv` | `dataset` | `clase`, `n`, `proporcion`, `target_clases` |
| C. Senal supervisada previa | `01_raw_eda/fase1_asociacion_target_resumen.csv`, `03_postprocessing_audit/fase3_asociacion_tests.csv` | mapear `olive_oil` -> `olive_oil_3class`/`olive_oil_9class` | `variables_fdr_005`, `efecto_abs_mediano`, `efecto_abs_maximo`, `top_k_overlap_ratio` |
| D. Regimen sintetico | combinar A+B+C | `dataset` | ratios derivados |

**Tabla intermedia recomendada:** `results/tables/10_memoria_dataset_regimen_signal.csv`

Columnas:

```text
dataset,filas,features,target_clases,ratio_mayoritaria_minoritaria,
variables_fdr_005,variables_contrastadas,prop_fdr_005,
efecto_abs_mediano,efecto_abs_maximo,top_k_overlap_ratio,
regimen_dimensional,regimen_senal,regimen_desbalance
```

**Precaucion:** fase 1/3 solo tienen `olive_oil`; duplicar esa evidencia para
las dos formulaciones finales solo si el texto declara que procede del origen
comun.

## SF3 — Cadena de validez experimental

**Unidad:** dataset x control.  
**Funcion tabular:** construir una matriz de garantias metodologicas.

| Control | CSVs fuente | Grano | Columnas utiles |
|---|---|---|---|
| FDR/senal | `01_raw_eda/fase1_fdr_resumen.csv`, `01_raw_eda/fase1_tamano_efecto_resumen.csv` | dataset | `significativas_fdr`, `reduccion_por_correccion`, `efecto_abs_mediano` |
| Preprocesado conservador | `03_postprocessing_audit/fase3_asociacion_tests.csv`, `03_postprocessing_audit/fase3_shift_distribucional_resumen.csv` | dataset | `spearman_rankings_raw_processed`, `mi_spearman_raw_processed`, `score_shift_maximo` |
| Split valido | `04_split_audit/fase4_target_tests.csv`, `04_split_audit/fase4_tamanos_split.csv` | dataset/split | `chi2_p_value`, tamanos por split |
| Drift | `04_split_audit/fase4_drift_resumen.csv` | dataset | `variables_con_flag`, `max_psi`, `max_drift_score` |
| Validacion adversarial | `04_split_audit/fase4_validacion_adversarial.csv` | dataset | `auc_cv`, `auc_fold_std`, `auc_min`, `auc_max` |
| Leakage | `04_split_audit/fase4_leakage_resumen.csv`, `04_split_audit/fase4_leakage_screening.csv` | dataset / dataset x variable | `target_en_X`, `auc_abs_ge_099`, `nmi_ge_099`, `auc_abs_binaria`, `nmi_con_target` |
| Bootstrap/test | `06_modeling/modeling_test_confidence_intervals.csv` | experimento x metrica | `metric`, `estimate`, `ci_low`, `ci_high`, `n_bootstrap` |
| Permutacion | `06_modeling/modeling_permutation_test_results.csv` | experimento | `observed_macro_f1`, `null_p95`, `p_value`, `n_permutations` |

**Tabla intermedia recomendada:** `results/tables/10_memoria_cadena_validez.csv`

Columnas:

```text
dataset,control,valor,umbral,estado,detalle,tabla_fuente
```

**Precaucion:** esta tabla debe guardar estados interpretables (`ok`,
`cautela`, `no_aplica`), pero tambien el valor numerico original.

## SF4 — Espacio clasico de selectores

**Unidad:** metodo clasico (`M=12`) y, cuando proceda, dataset x metodo.

| Panel | CSVs fuente | Join | Columnas utiles |
|---|---|---|---|
| A. Familias/registro | `05_feature_selection/fs_method_registry.csv` | `method` | `familia`, `usa_target`, `salida`, `criterio_tecnico` |
| B. Perfil global | `05_feature_selection/fs_method_profiles.csv` | `method` | `segundos_medios`, `jaccard_medio`, `corr_media_seleccionada` |
| C. Estabilidad por dataset/k | `05_feature_selection/fs_jaccard_stability.csv` | `dataset,method,k` | `seed_a`, `seed_b`, `jaccard` |
| D. Redundancia por dataset/k | `05_feature_selection/fs_redundancy_vs_full.csv` | `dataset,method,k` | `selected_mean_abs_corr`, `delta_mean_abs_corr`, `selected_high_corr_pairs` |
| E. Separacion frente a nulo | `05_feature_selection/fs_permutation_summary.csv` | `dataset,method` | `n_features_above_null`, `median_empirical_p_value`, `n_permutations` |
| F. Seleccion materializada | `05_feature_selection/fs_all_selected_features.csv` | `dataset,method,k,feature` | `seed`, `rank`, `score`, `elapsed_seconds` |

**Tabla intermedia recomendada:** `results/tables/10_memoria_selector_profile.csv`

Columnas:

```text
dataset,method,familia,k,segundos_medios,jaccard_medio_global,
jaccard_dataset_k,selected_mean_abs_corr,delta_mean_abs_corr,
selected_high_corr_pairs,n_features_above_null,median_empirical_p_value,
n_features_selected,n_seeds,status
```

**Precauciones:**

- `fs_permutation_summary.csv` solo cubre `f_classif` y `mutual_info`.
- Boruta puede no aparecer en `fs_jaccard_stability.csv`.
- Para un panel global, promediar por dataset/k debe hacerse explicitamente y
  conservar tambien la tabla granular.

## SF5 — Trayectorias en k

**Unidad:** dataset x metodo/selector x `k`; rendimiento por modelo.

| Panel | CSVs fuente | Join | Columnas utiles |
|---|---|---|---|
| Redundancia vs `k` | `05_feature_selection/fs_redundancy_vs_full.csv` | `dataset,method,k` | `selected_mean_abs_corr`, `delta_mean_abs_corr`, `n_selected_features` |
| Rendimiento validation vs `k` | `06_modeling/modeling_validation_results_all.csv` | normalizar `selector` -> `method`; `dataset,k` | `model_name`, `macro_f1`, `baseline_macro_f1_same_model`, `delta_macro_f1_vs_same_model_baseline`, `validation_rank` |
| Coste/parsimonia | `06_modeling/modeling_cost_performance.csv` | `experiment_id` o `dataset,feature_set,model_name` | `fit_seconds`, `feature_reduction_ratio`, `n_features_used` |
| QFS como referencia puntual | `08_quantum/qfs_validation_results.csv`, `08_quantum/qfs_selected_all.csv` | `dataset,k` | `configuration`, `alpha`, `beta`, `validation_macro_f1` |

**Tabla intermedia recomendada:** `results/tables/10_memoria_k_path.csv`

Columnas:

```text
dataset,method,feature_set,k,model_name,n_features,macro_f1,
baseline_macro_f1_same_model,delta_macro_f1_vs_same_model_baseline,
selected_mean_abs_corr,delta_mean_abs_corr,feature_reduction_ratio,
fit_seconds,source,configuration,alpha,beta
```

**Precaucion:** QFS no recorre todos los `k`; normalmente entra como punto o
linea de referencia en el `k` final, no como trayectoria completa comparable a
los 12 selectores.

## SF6 — Comparacion final clasico vs QFS

**Unidad:** dataset x enfoque final.

| Enfoque | CSVs fuente | Join | Columnas utiles |
|---|---|---|---|
| Baseline y mejor clasico | `07_final_comparison/fase7_comparacion_final.csv` | `dataset` | `baseline_test_macro_f1`, `seleccion_test_macro_f1`, `delta_test_macro_f1`, `delta_ci_low`, `delta_ci_high` |
| Candidatos clasicos completos | `07_final_comparison/fase7_tabla_maestra.csv` | `dataset,experiment_id` | `feature_set`, `model_name`, `test_macro_f1`, `test_macro_f1_ci_low`, `test_macro_f1_ci_high` |
| QFS-NA y oraculo | `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | `dataset,configuration` | `qfs_test_macro_f1`, `delta_test_macro_f1`, `delta_ci_low`, `delta_ci_high`, `veredicto` |
| Modelos QFS si se requiere | `08_quantum/qfs_model_results.csv` | `dataset,configuration` | `model_name`, `test_macro_f1`, `validation_macro_f1` |

**Tabla intermedia recomendada:** `results/tables/10_memoria_comparacion_final_long.csv`

Columnas:

```text
dataset,approach,configuration,model_name,n_features,test_macro_f1,
ci_low,ci_high,delta_vs_baseline,p_value_fdr,veredicto,source_table
```

**Precaucion:** `qfs_model_results.csv` tiene varios modelos por configuracion;
si se usa, hay que decidir si se muestra el mejor modelo QFS o el modelo elegido
por protocolo. La tabla `comparacion_qfs_configuraciones_vs_baseline.csv` ya
parece contener la comparacion final.

## SF7 — Tablero QFS: alpha, beta, MDS y criterio-optimizador

**Unidad:** dataset x parametro/configuracion.

| Panel | CSVs fuente | Join | Columnas utiles |
|---|---|---|---|
| Alpha / oraculo exacto | `08_quantum/qfs_oracle_*.csv` | `dataset,alpha` | `mode`, `k_target`, `cardinality`, `q_opt`, `selected_features`, `elapsed_seconds` |
| Beta / validation | `08_quantum/qfs_validation_results.csv` | `dataset,beta,configuration` | `alpha`, `beta`, `k`, `validation_macro_f1`, `selected_features` |
| Beta / runs y densidades | `08_quantum/qfs_runs_*_*.csv` | `dataset,beta`; derretir `density__*` | `cost_f`, `count`, `bitstring`, `selected_features`, `density__*` |
| Control optimizador | `08_quantum/qfs_quality_control_*.csv` | `dataset,beta,k` | `hamming_distance`, `q_na_alpha05`, `q_oracle_alpha05`, `delta_cost_alpha05` |
| MDS/geometria | `08_quantum/qfs_embedding_error.csv` | `dataset,beta` | `embedding_error_mean`, `embedding_error_p95`, `target_distance_mean`, `mds_distance_mean`, `positions_json` |
| Diagnostico rendimiento | `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | `dataset,configuration` | `baseline_test_macro_f1`, `qfs_test_macro_f1`, `delta_test_macro_f1`, `veredicto` |

**Tabla intermedia recomendada:** `results/tables/10_memoria_qfs_diagnosis.csv`

Columnas:

```text
dataset,configuration,alpha,beta,k,baseline_test_macro_f1,
qfs_test_macro_f1,delta_test_macro_f1,oracle_test_macro_f1,
criterio_loss,optimizer_loss,hamming_distance,delta_cost_alpha05,
embedding_error_mean,embedding_error_p95,veredicto
```

**Tabla intermedia adicional:** `results/tables/10_memoria_qfs_beta_density_long.csv`

Columnas:

```text
dataset,beta,feature,density,cost_f,count,selected_in_best_bitstring
```

**Precauciones:**

- No asumir que `qfs_validation_results.csv` es una malla rectangular
  `alpha x beta`; filtrar por `configuration`.
- `qfs_runs_*` tiene columnas `density__feature` distintas por dataset.
- `positions_json` exige parseo JSON si se quieren coordenadas MDS.

## SF8 — Microdiagnostico SHAP / variables / solape

**Unidad:** dataset x feature, con capas de seleccion, SHAP, QFS e informacion
mutua.

| Capa | CSVs fuente | Join | Columnas utiles |
|---|---|---|---|
| SHAP resumen | `06_modeling/modeling_shap_values_summary.csv`, `06_modeling/modeling_shap_feature_importance.csv` | `dataset,feature`; o `experiment_id` para candidato concreto | `mean_abs_shap`, `rank`, `raw_values_path`, `feature_values_path`, `output_labels` |
| SHAP crudo | `06_modeling/modeling_shap_values_full_*.csv`, `06_modeling/modeling_shap_feature_values_*.csv` | rutas desde `modeling_shap_values_summary.csv` | matriz por instancia |
| Seleccion clasica | `05_feature_selection/fs_all_selected_features.csv` | `dataset,feature`; filtrar `method,k,seed` | `method`, `k`, `seed`, `rank`, `score` |
| Feature sets clasicos | `05_feature_selection/fs_selected_feature_sets.csv` | `dataset,method,k` | rutas de subsets |
| QFS seleccion final | `08_quantum/qfs_selected_all.csv` | parsear `selected_features` por `dataset,configuration` | `configuration`, `alpha`, `beta`, `selected_features` |
| Relevancia QFS | `05_feature_selection/fs_qfs_mi_target_vector_long.csv` | `dataset,feature` | `I_i` |
| Redundancia QFS | `05_feature_selection/fs_qfs_pairwise_mi_matrix_long.csv` | filtrar dataset y features | `R_ij` en formato ancho |
| Solape derivado | `10_memoria_b2_jaccard_metodos.csv` | `dataset,method` | `jaccard`, `rel`, `red` |

**Tabla intermedia recomendada:** `results/tables/10_memoria_feature_concordance.csv`

Columnas:

```text
dataset,feature,mean_abs_shap,shap_rank,I_i,qfs_na_selected,
qfs_oracle_selected,n_classic_methods_selected,classic_methods_selected,
best_classic_selected,selected_by_mrmr,selected_by_boruta,
selected_by_best_model_feature_set,feature_rank_best_selector
```

**Precauciones:**

- `selected_features` esta serializado: parsear con `ast.literal_eval` si tiene
  formato de lista Python o con parser robusto segun el contenido real.
- SHAP crudo existe para candidatos finales, no para los 260 experimentos.
- Para Olive multiclase, respetar `output_labels`; no colapsar por comodidad sin
  crear una columna `aggregation`.

## SF9 — Mapa final de evidencia

**Unidad:** dataset x dimension de evidencia.

| Dimension | CSVs fuente | Columnas utiles |
|---|---|---|
| Regimen | `10_memoria_dataset_regimen_signal.csv` | regimenes derivados |
| Validez | `10_memoria_cadena_validez.csv` | estado por control |
| Clasico | `07_final_comparison/fase7_comparacion_final.csv` | baseline, seleccion, delta, p |
| QFS | `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | QFS-NA, oraculo, delta, veredicto |
| Diagnostico | `10_memoria_qfs_diagnosis.csv` | `criterio_loss`, `optimizer_loss`, Hamming, MDS |
| Consistencia | `10_memoria_b10_consistencia.csv`, `05_feature_selection/fs_jaccard_stability.csv` | `jaccard` |
| Solape | `10_memoria_b2_jaccard_metodos.csv` | `jaccard`, `rel`, `red` |

**Tabla intermedia recomendada:** `results/tables/10_memoria_evidence_map.csv`

Columnas:

```text
dataset,dimension,value_numeric,value_label,status,source_table,
supports_claim,caveat
```

**Precaucion:** esta tabla es derivada y editorial, pero debe conservar
`source_table` y `supports_claim` para que cada celda sea trazable.

## Orden recomendado para crear tablas intermedias

1. `10_memoria_dataset_regimen_signal.csv`
2. `10_memoria_cadena_validez.csv`
3. `10_memoria_selector_profile.csv`
4. `10_memoria_k_path.csv`
5. `10_memoria_comparacion_final_long.csv`
6. `10_memoria_qfs_diagnosis.csv`
7. `10_memoria_qfs_beta_density_long.csv`
8. `10_memoria_feature_concordance.csv`
9. `10_memoria_evidence_map.csv`

## Minimo viable

Si hay poco tiempo, priorizar solo cinco tablas:

| Tabla | Por que |
|---|---|
| `10_memoria_dataset_regimen_signal.csv` | une las cinco formulaciones con la dificultad real |
| `10_memoria_selector_profile.csv` | convierte los doce selectores en referencia defendible |
| `10_memoria_k_path.csv` | conecta seleccion, `k`, redundancia y rendimiento |
| `10_memoria_qfs_diagnosis.csv` | sostiene el diagnostico criterio--optimizador |
| `10_memoria_feature_concordance.csv` | conecta SHAP, seleccion clasica, QFS e `I_i` |

Estas cinco tablas permitirian construir casi todas las figuras importantes sin
volver a improvisar joins dentro de cada script.
