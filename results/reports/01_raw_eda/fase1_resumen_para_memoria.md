# Resultados de la Fase 1 - Análisis exploratorio crudo

La Fase 1 carga los datasets crudos, caracteriza estructura, calidad, target, asociaciones exploratorias, FDR, redundancia y dimensionalidad.

## Hallazgos principales
- `breast_cancer_wisconsin`: 569 filas, 31 features, ratio features/muestras=0.05448, FDR significativas=27, pares Spearman >=0.85=29, variables para revisión=1.
- `customer_churn`: 440832 filas, 11 features, ratio features/muestras=0.00002, FDR significativas=10, pares Spearman >=0.85=0, variables para revisión=1.
- `madelon`: 2000 filas, 500 features, ratio features/muestras=0.25000, FDR significativas=13, pares Spearman >=0.85=12, variables para revisión=25.
- `olive_oil`: 572 filas, 11 features, ratio features/muestras=0.01923, FDR significativas=10, pares Spearman >=0.85=2, variables para revisión=2.

## Implicaciones para fases posteriores
- Fase 2 debe limitarse a preprocesado estructural: identificadores, nombres y target.
- Fase 3 debe comprobar que el preprocesado conserva target, distribuciones y señal exploratoria.
- Fase 4 debe estratificar y vigilar fugas de información y desplazamientos de distribución, especialmente en Olive Oil y variables con efecto casi perfecto.
- Fase 5 debe separar señal, ruido y redundancia; `madelon` es el caso crítico para selección robusta.

## Tablas generadas
- `results/tables/01_raw_eda/fase1_asociacion_target.csv`
- `results/tables/01_raw_eda/fase1_asociacion_target_resumen.csv`
- `results/tables/01_raw_eda/fase1_calidad_datasets.csv`
- `results/tables/01_raw_eda/fase1_calidad_variables.csv`
- `results/tables/01_raw_eda/fase1_carga_inicial.csv`
- `results/tables/01_raw_eda/fase1_correlaciones_spearman_pares.csv`
- `results/tables/01_raw_eda/fase1_distribuciones_numericas.csv`
- `results/tables/01_raw_eda/fase1_estructura_datasets.csv`
- `results/tables/01_raw_eda/fase1_fdr_resumen.csv`
- `results/tables/01_raw_eda/fase1_muestreo_visual_resumen.csv`
- `results/tables/01_raw_eda/fase1_muestreo_visual_target.csv`
- `results/tables/01_raw_eda/fase1_normalidad_resumen.csv`
- `results/tables/01_raw_eda/fase1_normalidad_variables.csv`
- `results/tables/01_raw_eda/fase1_pca_resumen.csv`
- `results/tables/01_raw_eda/fase1_pca_varianza.csv`
- `results/tables/01_raw_eda/fase1_preclasificacion_resumen.csv`
- `results/tables/01_raw_eda/fase1_preclasificacion_variables.csv`
- `results/tables/01_raw_eda/fase1_redundancia_resumen.csv`
- `results/tables/01_raw_eda/fase1_riesgos_resumen.csv`
- `results/tables/01_raw_eda/fase1_sintesis_evidencias.csv`
- `results/tables/01_raw_eda/fase1_tamano_efecto_resumen.csv`
- `results/tables/01_raw_eda/fase1_target_distribucion.csv`
- `results/tables/01_raw_eda/fase1_target_resumen.csv`
- `results/tables/01_raw_eda/fase1_univariante_resumen_dataset.csv`
- `results/tables/01_raw_eda/fase1_variables_revision_riesgos.csv`

## Figuras generadas
- `results/figures/01_raw_eda/01_02_estructura_filas_por_feature.png`
- `results/figures/01_raw_eda/01_04_target_desbalance_comparado.png`
- `results/figures/01_raw_eda/01_06_univariante_breast_cancer_wisconsin.png`
- `results/figures/01_raw_eda/01_06_univariante_customer_churn.png`
- `results/figures/01_raw_eda/01_06_univariante_madelon.png`
- `results/figures/01_raw_eda/01_06_univariante_olive_oil.png`
- `results/figures/01_raw_eda/01_07_normalidad_breast_cancer_wisconsin.png`
- `results/figures/01_raw_eda/01_07_normalidad_customer_churn.png`
- `results/figures/01_raw_eda/01_07_normalidad_madelon.png`
- `results/figures/01_raw_eda/01_07_normalidad_olive_oil.png`
- `results/figures/01_raw_eda/01_08_asociacion_breast_cancer_wisconsin.png`
- `results/figures/01_raw_eda/01_08_asociacion_customer_churn.png`
- `results/figures/01_raw_eda/01_08_asociacion_madelon.png`
- `results/figures/01_raw_eda/01_08_asociacion_olive_oil.png`
- `results/figures/01_raw_eda/01_10_efecto_breast_cancer_wisconsin.png`
- `results/figures/01_raw_eda/01_10_efecto_customer_churn.png`
- `results/figures/01_raw_eda/01_10_efecto_madelon.png`
- `results/figures/01_raw_eda/01_10_efecto_olive_oil.png`
- `results/figures/01_raw_eda/01_11_redundancia_breast_cancer_wisconsin.png`
- `results/figures/01_raw_eda/01_11_redundancia_customer_churn.png`
- `results/figures/01_raw_eda/01_11_redundancia_madelon.png`
- `results/figures/01_raw_eda/01_11_redundancia_olive_oil.png`
- `results/figures/01_raw_eda/01_12_pca_breast_cancer_wisconsin.png`
- `results/figures/01_raw_eda/01_12_pca_customer_churn.png`
- `results/figures/01_raw_eda/01_12_pca_madelon.png`
- `results/figures/01_raw_eda/01_12_pca_olive_oil.png`
- `results/figures/01_raw_eda/01_14_preclasificacion_breast_cancer_wisconsin.png`
- `results/figures/01_raw_eda/01_14_preclasificacion_customer_churn.png`
- `results/figures/01_raw_eda/01_14_preclasificacion_madelon.png`
- `results/figures/01_raw_eda/01_14_preclasificacion_olive_oil.png`