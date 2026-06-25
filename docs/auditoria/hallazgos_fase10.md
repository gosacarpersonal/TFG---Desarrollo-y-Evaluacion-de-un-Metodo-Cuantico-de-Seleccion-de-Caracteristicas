# Hallazgos fase 10 - visualizaciones QFS

Este documento se genera desde `scripts/fase10_visualizaciones_core.py`. Todas las cifras leen artefactos de `results/`; no se reejecutan fases clasicas ni se edita la memoria.

## Tabla: 10 dimensiones -> hallazgo -> que demuestra -> relacion con la memoria

| Dimension | Instrumento | Hallazgo | Que demuestra | Relacion con la memoria |
|---|---|---|---|---|
| 1 Dataset/regimen | A | El regimen predice el cuello de botella | Transforma contexto en teoria predictiva | 5.1 regimenes del banco |
| 2 Metodos | B2 | QFS es clase mRMR salvo Churn | Atribuye posicion en el espejo de 12 | 5.2 seleccion y posicion en metodos |
| 3 k | B3 | k no arregla Madelon si el criterio no ve senal | Evita podio a k unico | 5.2 trayectoria de seleccion |
| 4 alpha | B4 | Alpha recorre cardinalidad pero Madelon recibe I_i degenerado | Valida Mucke y separa mando/input | 5.3 QUBO exacto |
| 5 beta/geometria | B5/B9 | Beta reordena; geometria de Churn queda refutada como causa | Distingue mando fisico de mecanismo causal | 5.3 fisica y 5.4 discusion |
| 6 Modelos/SHAP | B6/C | Lo que el modelo usa aparece en la seleccion salvo Madelon | Prueba criterio vs modelo | 5.4 diagnostico |
| 7 Metricas | B7 | Macro-F1 primaria; AUC solo binario | No oculta Olive9 | 5.0 protocolo de evaluacion |
| 8 Tests | B8 | La cadena elimina confusores | Autoriza atribucion | Validez estadistica |
| 9 Consistencia | B10 | 3 semillas estables; variacion benigna entre sustitutos | Declara robustez real y limite multi-seed | Nueva subseccion consistencia |
| 10 Sintesis | C | Regimen -> mecanismo -> resultado por dataset | Cierra la tesis no-podio | Cierre de resultados/discusion |

## Instrumentos

### A - Regimenes por dataset

1. **Pregunta + lente.** Que predice el dato antes de ejecutar QFS? Lente: **fidelidad de comportamiento**.
2. **Metrica derivada + artefacto.** VIF de `results/tables/03_postprocessing_audit/fase3_vif_processed.csv`, PCA/FDR/efecto de fase 1, drift y adversarial de `results/tables/04_split_audit/`. Figuras: `results/figures/10_memoria/f10_a_regimenes_dataset.png`.
3. **Que encontre.** BCW: VIF max 3806.1 y 23 variables con VIF>=10, efecto mediano 0.65, PCA80=5. Churn: VIF max 1.1 y 0 VIF>=10, AUC adversarial 0.516, drift 0 flags. Madelon: efecto mediano 0.02, 13/500 FDR, PCA80=295, drift 41 flags. Olive 3/9: 8 variables, VIF max 326.5, PCA80=3, Olive 9 queda limitado por n_test=86.
4. **Que demuestra o desmiente y por que.** Demuestra que los datasets no son cinco carreras equivalentes: BCW exige controlar redundancia, Madelon desmiente que la redundancia explique el fallo, Churn aisla el optimizador y Olive9 obliga a prudencia.
5. **Regimen -> mecanismo -> resultado y memoria.** Este es el arranque de la tesis: regimen medido -> cuello de botella esperado -> lectura del resultado QFS en Resultados y Discusion.

### B2 - Espacio de metodos

1. **Pregunta + lente.** Que clase de selector es QFS cuando usa las mismas I_i y R_ij del handoff? Lente: **posicion-en-metodos**.
2. **Metrica derivada + artefacto.** Coordenadas relevancia/redundancia de `scripts/explor_mapa_metodos.py` y Jaccard QFS-vs-12 desde `fs_all_rankings.csv` + `comparacion_qfs_configuraciones_vs_baseline.csv`; aqui `redundancia interna` significa media de `R_ij` (informacion mutua del handoff QFS), distinta de la correlacion absoluta `selected_mean_abs_corr` usada en fase5/memoria. Tabla derivada `results/tables/10_memoria_b2_jaccard_metodos.csv`. Figuras: `results/figures/10_memoria/explor_mapa_metodos.png`, `results/figures/10_memoria/f10_b2_jaccard_12_metodos.png`.
3. **Que encontre.** Maximos Jaccard: Breast Cancer=f_classif (0.54), Customer Churn=mutual_correlation (0.67), Madelon=mrmr_approx (0.25), Olive 3=mrmr_approx (1.00), Olive 9=f_classif (0.67). Churn: mutual_correlation=0.67 frente a mRMR=0.43; Madelon mRMR=0.25. En variables, Churn QFS-NA retiene el bloque completo `subscription_type_*` y deja fuera `payment_delay`, `tenure` y `last_interaction`, que el oraculo si recupera.
4. **Que demuestra o desmiente y por que.** Demuestra que QFS cae en la familia mRMR solo cuando el regimen lo permite; en Churn se sale del nicho mRMR y ese desplazamiento coincide con el deficit leve de optimizador.
5. **Regimen -> mecanismo -> resultado y memoria.** Mapea a Resultados/seleccion y a la subseccion de diagnostico criterio-optimizador: no es podio, es ubicacion mecanistica de QFS frente a la referencia clasica.

### B3 - Trayectoria en k

1. **Pregunta + lente.** El comportamiento de QFS depende del presupuesto k o se mantiene como patron? Lente: **robustez**.
2. **Metrica derivada + artefacto.** `results/tables/08_quantum/ev6_rendimiento_vs_k.csv` para macro-F1 y `results/tables/05_feature_selection/fs_redundancy_vs_full.csv` para redundancia interna. Figuras: `results/figures/10_memoria/f10_b3_trayectoria_k.png`.
3. **Que encontre.** Breast Cancer QFS 0.913-0.950, mRMR 0.924-0.963; Customer Churn QFS 0.769-0.991, mRMR 0.769-0.994; Madelon QFS 0.526-0.557, mRMR 0.527-0.566; Olive 3 QFS 1.000-1.000, mRMR 0.989-1.000; Olive 9 QFS 0.857-0.918, mRMR 0.834-0.913. Baseline RF cubre 0.527-0.992. Orden α Churn: α=0.3:support_calls|contract_length_Monthly; α=0.5:support_calls|payment_delay|total_spend|contract_length_Monthly; α=0.7:age|tenure|support_calls|payment_delay|total_spend|gender_Male|contract_length_Monthly; α=0.9:age|tenure|usage_frequency|support_calls|payment_delay|total_spend|last_interaction|gender_Male|subscription_type_Basic|contract_length_Monthly. Madelon: α=0.1:k=1; α=0.6:k=1; α=0.9:k=4; α=1.0:k=20.
4. **Que demuestra o desmiente y por que.** Demuestra robustez local y orden de merito: en Churn el optimo exacto mete continuas informativas antes que grupos dummy completos; en Madelon la escalera es plana hasta α alto, asi que cambiar k no arregla un criterio que no ve senal.
5. **Regimen -> mecanismo -> resultado y memoria.** Ancla el capitulo de seleccion: k es un mando del proceso y se lee junto al orden α, no como una fila aislada.

### B4 - Escalera alpha

1. **Pregunta + lente.** Se cumple la lectura de Mucke: aumentar alpha recorre cardinalidad? Lente: **fidelidad**.
2. **Metrica derivada + artefacto.** `results/tables/08_quantum/qfs_oracle_*.csv`, filas `mode=alpha_grid`: cardinalidad y `q_opt` del QUBO exacto. Figuras: `results/figures/10_memoria/f10_b4_escalera_alpha.png`.
3. **Que encontre.** A alpha=0.5 las cardinalidades son BCW=1, Churn=4, Madelon=1, Olive3=2, Olive9=2; a alpha=1.0 suben a {'breast_cancer_wisconsin': 20, 'customer_churn': 15, 'madelon': 20, 'olive_oil_3class': 8, 'olive_oil_9class': 8}. En Madelon las mejores I_i son feat_241=0.026, feat_475=0.023, feat_338=0.020: una escala casi plana.
4. **Que demuestra o desmiente y por que.** Demuestra que el mecanismo matematico funciona; lo que falla en Madelon no es alpha sino el input: una relevancia MI de pares casi sin informacion util.
5. **Regimen -> mecanismo -> resultado y memoria.** Mapea al marco QUBO y a Resultados: teoria del criterio separada de su entrada, regimen -> relevancias utiles o degeneradas -> resultado.

### B5 - beta y geometria

1. **Pregunta + lente.** Que mueve beta y que flanco geometrico deja visible? Lente: **fidelidad**.
2. **Metrica derivada + artefacto.** `qfs_runs_<dataset>_<beta>.csv` para densidades; `qfs_operational_summary.csv` y `qfs_selected_all.csv` para beta elegido y dist_ratio. Figuras: `results/figures/10_memoria/f10_b5_beta_geometria.png`.
3. **Que encontre.** Betas elegidos/dist_ratio: Breast Cancer beta=0.20, dist_ratio=0.45, Customer Churn beta=0.30, dist_ratio=0.45, Madelon beta=0.50, dist_ratio=0.45, Olive 3 beta=0.00, dist_ratio=0.45, Olive 9 beta=0.40, dist_ratio=0.45.
4. **Que demuestra o desmiente y por que.** Demuestra que beta no es hiperparametro cosmetico: cambia el patron de densidades. Con el re-run canonico todos los beta elegidos aceptan dist_ratio=0.45; por tanto la relajacion geometrica ya no explica Churn.
5. **Regimen -> mecanismo -> resultado y memoria.** Mapea al metodo fisico y prepara B9: beta reordena densidades, pero el mecanismo causal se decide con el error de embebido canonico.

### B9 - Atomos y error de embebido

1. **Pregunta + lente.** La hipotesis one-hot/geometria de Churn se confirma o se refuta al medir el error MDS? Lente: **fidelidad**.
2. **Metrica derivada + artefacto.** `results/tables/08_quantum/qfs_embedding_error.csv`, guardado durante fase8 desde el embebido MDS real de `QFS_NA_Solver` con `mds_runs=100` y `mds_max_iter=100`; tabla de lectura para memoria `results/tables/10_memoria_b9_embedding_error.csv`. Figuras: `results/figures/10_memoria/f10_b9_atomos_mds_error.png`.
3. **Que encontre.** Errores medios de embebido: Breast Cancer=0.231, Customer Churn=0.217, Madelon=0.250, Olive 3=0.125, Olive 9=0.143. Churn rank por error alto=3/5; Δcoste a beta elegido: Churn=+0.622, Madelon=-0.059.
4. **Que demuestra o desmiente y por que.** Refuta la cadena one-hot -> MDS frustrado -> fallo: Churn embebe mejor que Madelon y BCW, aunque sigue teniendo un deficit leve de optimizador. One-hot queda como hipotesis/rasgo de seleccion, no como causa demostrada. Madelon queda separado: gran fallo de criterio aunque el coste NA no explica el deterioro principal.
5. **Regimen -> mecanismo -> resultado y memoria.** Mapea a la discusion de optimizador: regimen -> geometria medida -> resultado. La memoria debe decir Churn=optimizador leve sin geometria, no fallo simetrico con Madelon.

### B6 - Dependencia del modelo

1. **Pregunta + lente.** La utilidad de la seleccion es una propiedad del selector o de la pareja selector-modelo? Lente: **robustez**.
2. **Metrica derivada + artefacto.** `results/tables/06_modeling/modeling_cost_performance.csv` para el plano selector-modelo; `results/logs/06_modeling_shap_reference/modeling_test_results_candidates_before_xgboost_reference_update.csv` y `results/tables/06_modeling/modeling_test_results_candidates.csv` para el delta Madelon en test. Figuras: `results/figures/10_memoria/f10_b6_modelo_delta.png`.
3. **Que encontre.** En Madelon, Boruta/top-1 frente a baseline pasa de +0.280 con Random Forest (0.893-0.613) a +0.094 con XGBoost (0.907-0.813).
4. **Que demuestra o desmiente y por que.** Demuestra que XGBoost absorbe distractores mejor que los modelos lineales/bosque; por eso el fallo de criterio de Madelon se matiza por modelo, no desaparece.
5. **Regimen -> mecanismo -> resultado y memoria.** La memoria puede defender que seleccion no es un podio universal: regimen de ruido + modelo determinan el valor de seleccionar.

### B7 - Metricas

1. **Pregunta + lente.** Macro-F1 esconde algo que AUC-ROC veria en los binarios? Lente: **parsimonia-coherencia**.
2. **Metrica derivada + artefacto.** `results/tables/08_quantum/qfs_auc_binarios_contexto.csv` y macro-F1 de `comparacion_qfs_configuraciones_vs_baseline.csv`. Figuras: `results/figures/10_memoria/f10_b7_macro_f1_auc.png`.
3. **Que encontre.** BCW: AUC baseline=0.976, QFS=0.953; Churn: baseline=1.000, QFS=0.983. Olive9 no entra en AUC binario y n_test=86.
4. **Que demuestra o desmiente y por que.** Demuestra que macro-F1 es la metrica correcta para comparar todos los regimenes; AUC solo sirve como puente con el paper en binarios.
5. **Regimen -> mecanismo -> resultado y memoria.** Liga metrica con regimen: Olive9 es inconcluso por multiclase/desbalance, no porque se oculte una mejora por AUC.

### B8 - Cadena de tests

1. **Pregunta + lente.** Que confusores quedan descartados antes de atribuir un deterioro? Lente: **fidelidad**.
2. **Metrica derivada + artefacto.** `fase1_fdr_resumen`, `fase3_shift_distribucional_resumen`, `fase4_validacion_adversarial`, `fase4_leakage_resumen`, `fs_permutation_empirical_pvalues`, `modeling_pairwise_comparison_tests`, `modeling_permutation_test_results`, `qfs_quality_control_*`. Figuras: `results/figures/10_memoria/f10_b8_cadena_tests.png`.
3. **Que encontre.** FDR Madelon conserva 13/500; shift fase3 max=0.0; adversarial AUC rango=0.476-0.535; label-permutation p minimo=0.0020; bootstrap/sign-permutation usa 400 bootstraps y 2000 permutaciones.
4. **Que demuestra o desmiente y por que.** Demuestra que la comparacion no descansa en fuga, split adversarial o azar de etiquetas; por eso se puede atribuir Madelon a criterio y Churn a optimizador.
5. **Regimen -> mecanismo -> resultado y memoria.** Da la licencia metodologica de la tesis: referencia clasica rigurosa no solo mide, tambien permite atribuir.

### B10 - Consistencia

1. **Pregunta + lente.** La conclusion depende de semillas o solo bailan sustitutos equivalentes? Lente: **robustez**.
2. **Metrica derivada + artefacto.** `results/tables/05_feature_selection/fs_jaccard_stability.csv` para 3 semillas de seleccion; `modeling_pairwise_comparison_tests.csv` y `modeling_permutation_test_results.csv` para bootstrap/permutacion; `qfs_embedding_error.csv` para QFS con 100 MDS. Tabla derivada `results/tables/10_memoria_b10_consistencia.csv`. Figuras: `results/figures/10_memoria/f10_b10_consistencia.png`.
3. **Que encontre.** Filtros/MI deterministas tienen Jaccard minimo 1.00; random_forest baja a Madelon=0.88 y Olive9=0.78; Churn mRMR=0.88. La resolucion nula es seleccion 1/21≈0.048 y label-permutation 0.002; modelado usa 400 bootstraps y 2000 sign-perms.
4. **Que demuestra o desmiente y por que.** Demuestra robustez heterogenea: la seleccion estable no discrimina por si sola; donde hay variacion, suele cambiar el representante de informacion equivalente (feat_28/48, dummies Basic/Standard, palmitoleic/stearic). La consistencia fuerte de modelado/QFS multi-seed queda como decision futura, no como afirmacion inventada.
5. **Regimen -> mecanismo -> resultado y memoria.** Mapea a una subseccion nueva de memoria `Consistencia y robustez`: convierte semillas/permutaciones/bootstrap en evidencia con proposito y limite declarado.

### C - Sintesis integrada

1. **Pregunta + lente.** Cuando QFS falla, se puede separar criterio de optimizador y cerrar el relato entero? Lente: **fidelidad / posicion-en-metodos / robustez / parsimonia-coherencia**.
2. **Metrica derivada + artefacto.** `scripts/build_f6_shap_beeswarm.py` para SHAP y `scripts/build_diagnostico_atribucion.py` sobre `comparacion_qfs_configuraciones_vs_baseline.csv` para descomposicion macro-F1. Figuras: `results/figures/10_memoria/f6_shap_beeswarm_bcw.png`, `results/figures/10_memoria/diag_atribucion_qfs.png`.
3. **Que encontre.** Madelon: fallo criterio=+0.170, optimizador=+0.040, total=+0.210; QFS-NA macro-F1=0.603. Churn: criterio=+0.001, optimizador=+0.030, total=+0.030; QFS-NA macro-F1=0.969. SHAP top: Breast Cancer: texture_worst/radius_worst/area_worst; Customer Churn: support_calls/age/total_spend; Madelon: feat_241/feat_336/feat_105; Olive 3: other/linolenic/linoleic; Olive 9: linolenic/linoleic/other.
4. **Que demuestra o desmiente y por que.** Demuestra la tesis central y descarta la simetria falsa: Madelon es un fallo grande de criterio; Churn es un deficit leve de optimizador sin causa geometrica demostrada; BCW/Olive3 no fallan; Olive9 queda inconcluso.
5. **Regimen -> mecanismo -> resultado y memoria.** Es el climax de Resultados/Discusion: regimen -> mecanismo -> resultado, con SHAP como coherencia variable-level y plano de atribucion como cierre.


## Resumen de 10 lineas
1. Se construyo fase 10 como orquestador narrativo y nucleo reutilizable.
2. Todas las visualizaciones leen `results/` y copian figuras a la plantilla LaTeX.
3. A muestra que cada dataset estresa un regimen distinto.
4. B2 ubica QFS frente a los 12 selectores, no solo frente a mRMR.
5. B3-B5 separan los mandos k, alpha y beta.
6. B9 recompone el embebido atomico y mide error MDS por dataset.
7. B6-B7 muestran que modelo y metrica cambian la lectura del valor de seleccionar.
8. B8 ordena los tests como cadena de confusores descartados.
9. B10 anade consistencia: 3 semillas en seleccion, resampling en modelado y 100 MDS en QFS.
10. C confirma la tesis canonica: Madelon criterio grande; Churn optimizador leve sin geometria; Olive9 inconcluso.
