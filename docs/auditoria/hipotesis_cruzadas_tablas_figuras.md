# Hipotesis cruzadas entre tablas para explicar comportamientos

> 2026-06-16. Matriz de relaciones "no obvias" entre subfiguras/tablas que
> pueden explicar comportamientos experimentales. La idea no es juntar graficas
> por acumulacion, sino detectar puentes: caracteristicas del dataset -> sesgo
> del selector -> rendimiento del modelo -> diagnostico QFS.

## Principio

Una superfigura gana valor cuando conecta evidencias de niveles distintos:

```text
dataset -> selector -> subconjunto -> modelo -> QFS -> diagnostico
```

Muchas relaciones importantes no estan dentro de una sola fase. Aparecen al unir
tablas que, a priori, parecen no tener nada que ver.

## Cruces prioritarios

| ID | Cruce inesperado | Pregunta explicativa | Tablas fuente | Lectura posible |
|---|---|---|---|---|
| H1 | Señal FDR baja + QFS deteriorado | ¿QFS falla donde la señal univariante/pairwise no representa bien el problema? | `01_raw_eda/fase1_asociacion_target_resumen.csv`, `03_postprocessing_audit/fase3_asociacion_tests.csv`, `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | Si Madelon tiene pocas variables FDR y QFS cae, el problema puede estar en el criterio de informacion mutua, no solo en el optimizador |
| H2 | Redundancia alta + metodos redundancia-aware | ¿mRMR/RRFS ganan donde hay mucha correlacion interna? | `01_raw_eda/fase1_redundancia_resumen.csv`, `05_feature_selection/fs_redundancy_vs_full.csv`, `06_modeling/modeling_validation_results_all.csv` | Datasets con correlacion alta deberian favorecer selectores que penalizan redundancia |
| H3 | Drift bajo + deterioro QFS | ¿El fallo QFS no se debe a particiones inestables? | `04_split_audit/fase4_drift_resumen.csv`, `04_split_audit/fase4_validacion_adversarial.csv`, `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | Si drift/adversarial estan controlados y QFS cae, se descarta explicacion por split |
| H4 | Leakage limpio + rendimiento alto | ¿Un rendimiento alto es real o sospechoso? | `04_split_audit/fase4_leakage_screening.csv`, `04_split_audit/fase4_leakage_resumen.csv`, `07_final_comparison/fase7_tabla_maestra.csv` | Si el baseline roza techo pero leakage esta limpio, el resultado se interpreta como señal fuerte, no fuga |
| H5 | VIF/redundancia + SHAP concentrado | ¿El modelo usa pocas variables porque el dataset es redundante? | `03_postprocessing_audit/fase3_vif_processed.csv`, `05_feature_selection/fs_redundancy_vs_full.csv`, `06_modeling/modeling_shap_values_summary.csv` | Un SHAP concentrado en pocas variables puede explicarse por redundancia estructural |
| H6 | Estabilidad Jaccard baja + rendimiento inestable | ¿Un selector falla porque selecciona subconjuntos poco robustos? | `05_feature_selection/fs_jaccard_stability.csv`, `06_modeling/modeling_validation_results_all.csv`, `07_final_comparison/fase7_tabla_maestra.csv` | Bajo Jaccard entre semillas + bajo/variable rendimiento debilita el metodo aunque tenga buena media puntual |
| H7 | Coste alto + ganancia marginal | ¿Wrappers caros aportan lo suficiente? | `05_feature_selection/fs_method_profiles.csv`, `06_modeling/modeling_cost_performance.csv`, `07_final_comparison/fase7_comparacion_final.csv` | Boruta/RFE pueden justificarse solo si su mejora supera coste y no es marginal |
| H8 | Permutacion selector + rendimiento modelo | ¿El selector retiene señal real o ruido que el modelo explota accidentalmente? | `05_feature_selection/fs_permutation_summary.csv`, `06_modeling/modeling_permutation_test_results.csv`, `06_modeling/modeling_validation_results_all.csv` | Si selector no supera nulo pero modelo mejora, hay que sospechar inestabilidad o efecto de modelo |
| H9 | `k` creciente + redundancia creciente + macro-F1 plano | ¿Añadir variables deja de aportar informacion? | `05_feature_selection/fs_redundancy_vs_full.csv`, `06_modeling/modeling_validation_results_all.csv`, `08_quantum/ev6_rendimiento_vs_k.csv` | Si macro-F1 se estabiliza mientras redundancia sube, hay una zona optima de parsimonia |
| H10 | `k` optimo clasico + `alpha` oraculo | ¿El presupuesto elegido por clasicos coincide con el optimo QUBO? | `07_final_comparison/fase7_handoff_qfs.csv`, `08_quantum/qfs_oracle_*.csv`, `08_quantum/qfs_selected_all.csv` | Si `alpha` lleva a cardinalidades similares a `k` clasico, la diferencia no es tamaño sino criterio/subconjunto |
| H11 | `beta` elegido + error MDS | ¿El beta seleccionado coincide con menor error geometrico? | `08_quantum/qfs_selected_all.csv`, `08_quantum/qfs_embedding_error.csv`, `results/tables/10_memoria_b9_embedding_error.csv` | Si beta ganador no minimiza MDS, el rendimiento no esta gobernado solo por geometria |
| H12 | Error MDS alto + fallo optimizador | ¿La geometria explica la distancia QFS-NA vs oraculo? | `08_quantum/qfs_embedding_error.csv`, `08_quantum/qfs_quality_control_*.csv`, `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | Error MDS alto + Hamming/coste alto sugiere fallo operacional/geometrico |
| H13 | Hamming alto + rendimiento bajo | ¿El simulador selecciona un subconjunto distinto al oraculo y eso cuesta macro-F1? | `08_quantum/qfs_quality_control_*.csv`, `08_quantum/qfs_selected_all.csv`, `08_quantum/qfs_model_results.csv` | Hamming alto solo importa si se traduce en caida predictiva |
| H14 | Oraculo bueno + QFS-NA malo | ¿El criterio funciona pero el optimizador falla? | `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv`, `08_quantum/qfs_quality_control_*.csv` | Churn podria entrar aqui si el oraculo recupera baseline pero QFS-NA no |
| H15 | Oraculo malo + QFS-NA parecido | ¿El optimizador no es el problema: falla el criterio? | `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv`, `08_quantum/qfs_quality_control_*.csv`, `05_feature_selection/fs_qfs_mi_target_vector_long.csv` | Madelon podria entrar aqui si QFS-NA se acerca al oraculo pero ambos son malos frente a baseline |
| H16 | QFS vs mRMR/Jaccard + relevancia/redundancia | ¿QFS se parece mas a metodos de relevancia o a metodos redundancia-aware? | `results/tables/10_memoria_b2_jaccard_metodos.csv`, `05_feature_selection/fs_method_registry.csv`, `05_feature_selection/fs_qfs_mi_target_vector_long.csv` | Explica si QFS replica un sesgo clasico concreto o se separa de todos |
| H17 | QFS selecciona variables con alto `I_i` pero bajo SHAP | ¿La informacion mutua individual no predice contribucion del modelo? | `05_feature_selection/fs_qfs_mi_target_vector_long.csv`, `08_quantum/qfs_selected_all.csv`, `06_modeling/modeling_shap_values_summary.csv` | Puente directo entre criterio QFS y utilidad predictiva real |
| H18 | Variables SHAP altas ausentes en QFS | ¿El fallo QFS se debe a perder variables que el modelo necesita? | `06_modeling/modeling_shap_values_summary.csv`, `08_quantum/qfs_selected_all.csv`, `05_feature_selection/fs_all_selected_features.csv` | Muy potente para microdiagnostico de Madelon/Churn |
| H19 | Variables SHAP altas presentes en clasicos y ausentes en QFS | ¿La referencia clasica captura señal que QFS no retiene? | `06_modeling/modeling_shap_values_summary.csv`, `05_feature_selection/fs_all_selected_features.csv`, `08_quantum/qfs_selected_all.csv` | Explica diferencia clasico-QFS a nivel variable |
| H20 | Variables QFS presentes en muchos clasicos pero rendimiento QFS bajo | ¿El problema no es el subconjunto sino el modelo/configuracion QFS? | `08_quantum/qfs_selected_all.csv`, `05_feature_selection/fs_all_selected_features.csv`, `08_quantum/qfs_model_results.csv` | Si QFS selecciona variables consensuadas pero falla, mirar modelo, k o optimizador |
| H21 | Modelos sensibles + selector concreto | ¿Un selector solo funciona con XGBoost/Linear SVM? | `06_modeling/modeling_validation_results_all.csv`, `06_modeling/modeling_experiment_grid.csv`, `07_final_comparison/fase7_tabla_maestra.csv` | Distingue efecto del selector frente a efecto del modelo |
| H22 | AUC binario vs macro-F1 | ¿Un metodo parece bueno por AUC pero no por macro-F1? | `06_modeling/modeling_validation_results_all.csv`, `08_quantum/qfs_auc_binarios_contexto.csv`, `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | Evita conclusiones engañosas en Breast Cancer/Churn |
| H23 | Desbalance + macro-F1 bajo | ¿El fallo viene de clases minoritarias? | `04_split_audit/fase4_target_distribucion.csv`, `06_modeling/modeling_validation_results_all.csv`, `07_final_comparison/fase7_tabla_maestra.csv` | Justifica macro-F1 y ayuda a leer Olive 9 o Churn |
| H24 | Tamaño de test pequeño + IC ancho | ¿No se afirma mejora por falta de potencia? | `04_split_audit/fase4_tamanos_split.csv`, `06_modeling/modeling_test_confidence_intervals.csv`, `07_final_comparison/fase7_comparacion_final.csv` | Muy util para Olive: no confundir ausencia de evidencia con ausencia de efecto |
| H25 | Feature reduction ratio + rendimiento igual | ¿La ganancia principal es parsimonia, no macro-F1? | `06_modeling/modeling_cost_performance.csv`, `07_final_comparison/fase7_comparacion_final.csv` | Defiende seleccion aunque no suba mucho el rendimiento |
| H26 | Tiempo de selector + tiempo de modelo | ¿La seleccion compensa computacionalmente? | `05_feature_selection/fs_all_execution_times.csv`, `05_feature_selection/fs_method_profiles.csv`, `06_modeling/modeling_cost_performance.csv` | Si reducir variables baja fit time, puede justificar metodos aunque macro-F1 empate |
| H27 | Ranking raw->processed conservado + seleccion estable | ¿El preprocesado preserva la señal que luego seleccionan los metodos? | `03_postprocessing_audit/fase3_asociacion_tests.csv`, `05_feature_selection/fs_all_rankings.csv`, `05_feature_selection/fs_jaccard_stability.csv` | Une auditoria de preprocesado con estabilidad de seleccion |
| H28 | PCA/separabilidad + rendimiento baseline | ¿El baseline ya esta cerca del techo por estructura del dataset? | `01_raw_eda/fase1_pca_resumen.csv`, `04_split_audit/fase4_pca_varianza.csv`, `07_final_comparison/fase7_comparacion_final.csv` | Explica por que hay poca mejora posible en datasets faciles |
| H29 | Alta dimension / pocas muestras + wrappers | ¿Wrappers se benefician o sufren en alta dimensionalidad? | `04_split_audit/fase4_resumen_xy.csv`, `05_feature_selection/fs_method_profiles.csv`, `06_modeling/modeling_validation_results_all.csv` | Madelon puede mostrar el coste/riesgo de buscar en 500 variables |
| H30 | Densidad Rydberg por variable + seleccion final | ¿La lectura fisica del simulador se corresponde con las variables elegidas? | `08_quantum/qfs_runs_*_*.csv`, `08_quantum/qfs_selected_all.csv` | Valida que el mapa de densidades no sea decorativo |
| H31 | Densidad Rydberg + SHAP | ¿Las variables con mayor densidad son tambien relevantes para el modelo? | `08_quantum/qfs_runs_*_*.csv`, `06_modeling/modeling_shap_values_summary.csv` | Cruce poco obvio pero muy explicativo: fisica simulada vs explicabilidad predictiva |
| H32 | Densidad Rydberg + `I_i`/`R_ij` | ¿El simulador respeta relevancia y redundancia del QUBO? | `08_quantum/qfs_runs_*_*.csv`, `05_feature_selection/fs_qfs_mi_target_vector_long.csv`, `05_feature_selection/fs_qfs_pairwise_mi_matrix_long.csv` | Mide si el readout fisico se alinea con el criterio matematico |
| H33 | Consistencia por semillas + solape QFS | ¿QFS se acerca a metodos estables o a metodos inestables? | `results/tables/10_memoria_b10_consistencia.csv`, `results/tables/10_memoria_b2_jaccard_metodos.csv` | Si QFS se solapa con metodos estables, su seleccion es mas defendible aunque no gane |
| H34 | Consistencia baja + alto rendimiento puntual | ¿Hay resultados fragiles que no deberian sobredimensionarse? | `results/tables/10_memoria_b10_consistencia.csv`, `07_final_comparison/fase7_tabla_maestra.csv` | Evita vender como robusto un resultado de alta varianza |
| H35 | Variables con leakage sospechoso + SHAP alto | ¿Una variable importante podria ser artefacto? | `04_split_audit/fase4_leakage_screening.csv`, `06_modeling/modeling_shap_values_summary.csv` | Control defensivo: si SHAP alto coincide con sospecha de leakage, hay que discutirlo |
| H36 | Variables con drift + seleccion frecuente | ¿Los selectores eligen variables inestables entre splits? | `04_split_audit/fase4_drift_variables.csv`, `05_feature_selection/fs_all_selected_features.csv` | Si una variable con drift aparece mucho, puede explicar degradacion test |
| H37 | Drift variable + SHAP alto | ¿El modelo depende de variables que cambian entre particiones? | `04_split_audit/fase4_drift_variables.csv`, `06_modeling/modeling_shap_values_summary.csv`, `07_final_comparison/fase7_tabla_maestra.csv` | Explica gap validation-test si existe |
| H38 | Outliers/distribucion + rendimiento de SVM/XGBoost | ¿Un modelo se comporta mejor por la geometria de las variables? | `02_preprocessing/fase2_outliers_iqr.csv`, `01_raw_eda/fase1_distribuciones_numericas.csv`, `06_modeling/modeling_validation_results_all.csv` | Puede explicar diferencias de modelo dentro del mismo selector |
| H39 | Categorical encoding + Churn rendimiento | ¿El comportamiento en Churn se explica por variables categoricas codificadas? | `02_preprocessing/fase2_dimensionalidad_encoding.csv`, `02_preprocessing/fase2_categorias_predictoras.csv`, `06_modeling/modeling_shap_values_summary.csv` | Une preprocesado con interpretabilidad y techo de rendimiento |
| H40 | Olive 3 vs Olive 9 + mismo origen estadistico | ¿La formulacion del target cambia mas que los datos? | `04_split_audit/fase4_formulaciones_olive_oil.csv`, `04_split_audit/fase4_target_distribucion.csv`, `07_final_comparison/fase7_comparacion_final.csv` | Explica diferencias entre Olive 3 y Olive 9 sin atribuirlas a features distintas |

## Cruces por historia narrativa

### 1. "El dataset ya anticipaba el resultado"

Cruces:

- H1: FDR/señal -> QFS deteriorado.
- H2: redundancia -> metodos redundancia-aware.
- H23: desbalance -> macro-F1.
- H24: tamaño test -> IC ancho.
- H28: PCA/separabilidad -> baseline a techo.

**Uso:** explicar por que el comportamiento no aparece de la nada en fase 7/8,
sino que estaba anunciado por la caracterizacion.

### 2. "El selector no falla por azar, falla por su sesgo"

Cruces:

- H6: estabilidad -> rendimiento.
- H7: coste -> ganancia marginal.
- H8: permutacion selector -> permutacion modelo.
- H9: k/redundancia -> rendimiento plano.
- H21: selector x modelo.

**Uso:** pasar de ranking de selectores a explicacion de mecanismos.

### 3. "QFS se parece a algunos clasicos, pero no siempre por buenas razones"

Cruces:

- H10: k clasico -> alpha oraculo.
- H16: solape QFS con metodos clasicos.
- H17: I_i alto pero SHAP bajo.
- H18: SHAP alto ausente en QFS.
- H20: QFS selecciona variables consensuadas pero rinde bajo.

**Uso:** comparar QFS contra clasicos por estructura de seleccion, no solo por
macro-F1.

### 4. "Criterio, optimizador y geometria se pueden separar"

Cruces:

- H11: beta elegido -> error MDS.
- H12: MDS alto -> fallo optimizador.
- H13: Hamming alto -> rendimiento bajo.
- H14: oraculo bueno + QFS-NA malo.
- H15: oraculo malo + QFS-NA parecido.
- H32: densidad Rydberg -> I_i/R_ij.

**Uso:** sostener la tesis central de diagnostico criterio--optimizador.

### 5. "La explicabilidad comprueba si la historia predictiva tiene sentido"

Cruces:

- H5: redundancia/VIF -> SHAP concentrado.
- H17: I_i vs SHAP.
- H18/H19: SHAP alto ausente/presente en QFS/clasicos.
- H31: densidad Rydberg vs SHAP.
- H35/H37: leakage/drift vs SHAP.

**Uso:** bajar del rendimiento agregado a variables concretas.

## Priorizacion

Si hay que elegir pocas relaciones para llevar al cuerpo de la memoria:

| Prioridad | Cruce | Motivo |
|---:|---|---|
| 1 | H1 + H15 | Explica Madelon como fallo de criterio |
| 2 | H12 + H14 | Explica Churn como fallo de optimizador/geometria |
| 3 | H9 | Conecta `k`, redundancia y rendimiento; cuenta procedimiento |
| 4 | H17/H18 | Une QFS con SHAP y utilidad real de variables |
| 5 | H6 | Evita que la seleccion clasica sea solo ranking; introduce robustez |
| 6 | H24 | Da honestidad estadistica a Olive/test pequeño |
| 7 | H16/H33 | Situa QFS dentro del ecosistema clasico |
| 8 | H35/H37 | Blindaje defensivo: variables importantes no deben ser leakage/drift |

## Tablas intermedias que conviene crear

Estas hipotesis no deberian calcularse dentro de cada plotter. Conviene
materializarlas:

| Tabla propuesta | Hipotesis que alimenta |
|---|---|
| `10_memoria_dataset_method_outcomes.csv` | H1, H2, H21, H23, H24, H28, H29, H40 |
| `10_memoria_selector_robustness_outcomes.csv` | H6, H7, H8, H9, H26, H27, H34 |
| `10_memoria_qfs_classic_overlap_diagnosis.csv` | H10, H16, H20, H33 |
| `10_memoria_qfs_internal_diagnosis.csv` | H11, H12, H13, H14, H15, H30, H32 |
| `10_memoria_feature_level_explanation.csv` | H5, H17, H18, H19, H31, H35, H36, H37, H39 |

## Regla de lectura

Cada cruce debe acabar en una frase falsable:

```text
En dataset D, metodo M se comporta asi porque la evidencia A muestra X y la
evidencia B muestra Y.
```

Si no se puede escribir esa frase sin forzarla, el cruce no debe ir al cuerpo:
puede quedarse como auditoria o apendice.
