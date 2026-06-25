# Resultados de la Fase 3 - Auditoría Post-Preprocesado

La Fase 3 verifica los datasets procesados antes del split y resume las condiciones medibles que afectan a la partición posterior.

## Hallazgos principales
- El target conserva sus proporciones en todos los datasets: max |delta proporción| = 0.000000.
- Las variables numéricas comparables no muestran desplazamiento distribucional medible: KS máximo = 0.000000, PSI máximo = 0.000000.
- `customer_churn` mantiene 3 categóricas predictoras pendientes; deben codificarse después del split, ajustando el encoder solo con entrenamiento.
- La similitud de matrices crudas/procesadas es completa en las variables comparables: Frobenius máximo = 0.000000.
- La mayor alerta de dimensionalidad es `madelon`, con ratio features/muestras = 0.250.

## Tablas generadas
- `results/tables/03_postprocessing_audit/fase3_asociacion_processed.csv`
- `results/tables/03_postprocessing_audit/fase3_asociacion_shift.csv`
- `results/tables/03_postprocessing_audit/fase3_asociacion_tests.csv`
- `results/tables/03_postprocessing_audit/fase3_carga_datasets.csv`
- `results/tables/03_postprocessing_audit/fase3_carga_datasets_chunks.csv`
- `results/tables/03_postprocessing_audit/fase3_columnas_raw_processed.csv`
- `results/tables/03_postprocessing_audit/fase3_correlaciones_altas.csv`
- `results/tables/03_postprocessing_audit/fase3_correlaciones_matrices.csv`
- `results/tables/03_postprocessing_audit/fase3_correlaciones_resumen.csv`
- `results/tables/03_postprocessing_audit/fase3_cramers_v_categoricas.csv`
- `results/tables/03_postprocessing_audit/fase3_dimensionalidad_final.csv`
- `results/tables/03_postprocessing_audit/fase3_dimensiones_raw_processed.csv`
- `results/tables/03_postprocessing_audit/fase3_estructura_processed.csv`
- `results/tables/03_postprocessing_audit/fase3_nulos_infinitos.csv`
- `results/tables/03_postprocessing_audit/fase3_percentiles_comparables.csv`
- `results/tables/03_postprocessing_audit/fase3_rangos_processed.csv`
- `results/tables/03_postprocessing_audit/fase3_resumen_metricas_split.csv`
- `results/tables/03_postprocessing_audit/fase3_shift_distribucional.csv`
- `results/tables/03_postprocessing_audit/fase3_shift_distribucional_resumen.csv`
- `results/tables/03_postprocessing_audit/fase3_target_distribucion.csv`
- `results/tables/03_postprocessing_audit/fase3_target_resumen.csv`
- `results/tables/03_postprocessing_audit/fase3_target_shift.csv`
- `results/tables/03_postprocessing_audit/fase3_target_tests.csv`
- `results/tables/03_postprocessing_audit/fase3_tipos_processed.csv`
- `results/tables/03_postprocessing_audit/fase3_vif_processed.csv`

## Figuras generadas
- `results/figures/03_postprocessing_audit/fase3_asociacion_breast_cancer_wisconsin.png`
- `results/figures/03_postprocessing_audit/fase3_asociacion_customer_churn.png`
- `results/figures/03_postprocessing_audit/fase3_asociacion_madelon.png`
- `results/figures/03_postprocessing_audit/fase3_asociacion_olive_oil.png`
- `results/figures/03_postprocessing_audit/fase3_asociacion_topk_overlap_qfs.png`
- `results/figures/03_postprocessing_audit/fase3_dimensionalidad_final.png`
- `results/figures/03_postprocessing_audit/fase3_distribucion_conservacion_breast_cancer_wisconsin.png`
- `results/figures/03_postprocessing_audit/fase3_distribucion_conservacion_customer_churn.png`
- `results/figures/03_postprocessing_audit/fase3_distribucion_conservacion_madelon.png`
- `results/figures/03_postprocessing_audit/fase3_distribucion_conservacion_olive_oil.png`
- `results/figures/03_postprocessing_audit/fase3_redundancia_breast_cancer_wisconsin.png`
- `results/figures/03_postprocessing_audit/fase3_redundancia_customer_churn.png`
- `results/figures/03_postprocessing_audit/fase3_redundancia_madelon.png`
- `results/figures/03_postprocessing_audit/fase3_redundancia_olive_oil.png`
- `results/figures/03_postprocessing_audit/fase3_sintesis_metricas_split.png`
- `results/figures/03_postprocessing_audit/fase3_target_conservacion_breast_cancer_wisconsin.png`
- `results/figures/03_postprocessing_audit/fase3_target_conservacion_customer_churn.png`
- `results/figures/03_postprocessing_audit/fase3_target_conservacion_madelon.png`
- `results/figures/03_postprocessing_audit/fase3_target_conservacion_olive_oil.png`
- `results/figures/03_postprocessing_audit/fase3_target_desbalance.png`