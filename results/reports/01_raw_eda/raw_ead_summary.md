# Resumen EAD preliminar — Fase 1

Este documento resume la evidencia generada por el notebook de Fase 1. Las conclusiones son exploratorias y no sustituyen el preprocesado ni la selección formal de características de fases posteriores.

## breast_cancer_wisconsin

- Estructura: 569 filas y 30 features analíticas; target `target`.
- Calidad: 0 columnas con nulos, 0 filas duplicadas y 0 variables constantes.
- Target: 2 clases; ratio mayoritaria/minoritaria 1.68.
- Señal univariante: 26 variables con efecto medio/grande tras FDR.
- Redundancia: 29 pares con correlación alta según el umbral de la sección 1.11.
- Dimensionalidad: riesgo bajo; posible ruido univariante 4 variables.
- Riesgos: 1 variables marcadas para revisión; no se confirma leakage en esta fase.

## customer_churn

- Estructura: 440832 filas y 10 features analíticas; target `Churn`.
- Calidad: 0 columnas con nulos, 0 filas duplicadas y 0 variables constantes.
- Target: 2 clases; ratio mayoritaria/minoritaria 1.31.
- Señal univariante: 7 variables con efecto medio/grande tras FDR.
- Redundancia: 0 pares con correlación alta según el umbral de la sección 1.11.
- Dimensionalidad: riesgo bajo; posible ruido univariante 3 variables.
- Riesgos: 1 variables marcadas para revisión; no se confirma leakage en esta fase.

## madelon

- Estructura: 2000 filas y 500 features analíticas; target `target`.
- Calidad: 0 columnas con nulos, 0 filas duplicadas y 0 variables constantes.
- Target: 2 clases; ratio mayoritaria/minoritaria 1.
- Señal univariante: 7 variables con efecto medio/grande tras FDR.
- Redundancia: 12 pares con correlación alta según el umbral de la sección 1.11.
- Dimensionalidad: riesgo medio; posible ruido univariante 493 variables.
- Riesgos: 25 variables marcadas para revisión; no se confirma leakage en esta fase.

## olive_oil

- Estructura: 572 filas y 10 features analíticas; target `target`.
- Calidad: 0 columnas con nulos, 0 filas duplicadas y 0 variables constantes.
- Target: 9 clases; ratio mayoritaria/minoritaria 8.24.
- Señal univariante: 10 variables con efecto medio/grande tras FDR.
- Redundancia: 2 pares con correlación alta según el umbral de la sección 1.11.
- Dimensionalidad: riesgo bajo; posible ruido univariante 0 variables.
- Riesgos: 2 variables marcadas para revisión; no se confirma leakage en esta fase.

## Figuras candidatas para memoria

- `results/figures/01_raw_eda/01_02_estructura/raw_structure_summary.png`: Escala muestral, dimensionalidad inicial y ratio variables/muestras.
- `results/figures/01_raw_eda/01_03_calidad/raw_quality_issues_summary.png`: Incidencias accionables de calidad del dato crudo sin heatmap vacío.
- `results/figures/01_raw_eda/01_04_target/raw_target_distribution_panel.png`: Distribución de clases, con lectura separada para binarios y olive_oil multiclase.
- `results/figures/01_raw_eda/01_09_fdr/raw_fdr_before_after.png`: Efecto de la corrección por múltiples comparaciones, especialmente en madelon.
- `results/figures/01_raw_eda/01_11_redundancia/raw_high_corr_pairs_by_dataset.png`: Redundancia potencial por correlación alta y prioridad de control en Fase 2.
- `results/figures/01_raw_eda/01_15_ead/raw_dataset_profile_heatmap.png`: Matriz de severidad EAD trazada desde raw_dataset_profiles.csv.

## Tablas clave

- `raw_load_summary.csv`
- `raw_structure_summary.csv`
- `raw_quality_summary.csv`
- `raw_target_distribution.csv`
- `raw_feature_target_tests.csv`
- `raw_fdr_corrected_tests.csv`
- `raw_effect_sizes.csv`
- `raw_high_correlation_pairs.csv`
- `raw_feature_preclassification.csv`
- `raw_phase1_checklist.csv`