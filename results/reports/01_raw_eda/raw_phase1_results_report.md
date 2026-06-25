# Informe de resultados — Fase 1

## 1. Objetivo de la fase

Evaluar estructura, calidad, señal estadística, redundancia, dimensionalidad y riesgos de los datasets crudos antes de aplicar preprocesado, selección de características o modelado.

## 2. Datasets analizados

- `breast_cancer_wisconsin`: 569 filas, 32 columnas, target `target`.
- `customer_churn`: 440832 filas, 12 columnas, target `Churn`.
- `madelon`: 2000 filas, 501 columnas, target `target`.
- `olive_oil`: 572 filas, 12 columnas, target `target`.

## 3. Resumen estructural

- `breast_cancer_wisconsin`: 30 features analíticas, 1 posible(s) identificador(es), ratio features/muestras 0.05272.
- `customer_churn`: 10 features analíticas, 1 posible(s) identificador(es), ratio features/muestras 2.268e-05.
- `madelon`: 500 features analíticas, 0 posible(s) identificador(es), ratio features/muestras 0.25.
- `olive_oil`: 10 features analíticas, 1 posible(s) identificador(es), ratio features/muestras 0.01748.

## 4. Calidad del dato

- `breast_cancer_wisconsin`: 0 columnas con nulos, 0 duplicados, 0 constantes y 0 variables de baja variabilidad/dominancia.
- `customer_churn`: 0 columnas con nulos, 0 duplicados, 0 constantes y 9 variables de baja variabilidad/dominancia.
- `madelon`: 0 columnas con nulos, 0 duplicados, 0 constantes y 24 variables de baja variabilidad/dominancia.
- `olive_oil`: 0 columnas con nulos, 0 duplicados, 0 constantes y 1 variables de baja variabilidad/dominancia.

## 5. Distribución del target

- `breast_cancer_wisconsin`: 2 clases; clase minoritaria n=212; ratio 1.68.
- `customer_churn`: 2 clases; clase minoritaria n=190833; ratio 1.31.
- `madelon`: 2 clases; clase minoritaria n=1000; ratio 1.
- `olive_oil`: 9 clases; clase minoritaria n=25; ratio 8.24.

## 6. Señal variable-target

- `breast_cancer_wisconsin`: 27 variables candidatas univariantes tras FDR y efecto mínimo.
- `customer_churn`: 9 variables candidatas univariantes tras FDR y efecto mínimo.
- `madelon`: 13 variables candidatas univariantes tras FDR y efecto mínimo.
- `olive_oil`: 10 variables candidatas univariantes tras FDR y efecto mínimo.

## 7. Corrección por múltiples comparaciones

- `breast_cancer_wisconsin`: 27 significativas sin corregir frente a 27 tras FDR.
- `customer_churn`: 10 significativas sin corregir frente a 10 tras FDR.
- `madelon`: 38 significativas sin corregir frente a 13 tras FDR.
- `olive_oil`: 10 significativas sin corregir frente a 10 tras FDR.

## 8. Tamaños de efecto

- `breast_cancer_wisconsin`: grande=25, medio=1, muy_pequeño=2, pequeño=2.
- `customer_churn`: grande=4, medio=3, muy_pequeño=1, pequeño=2.
- `madelon`: medio=7, muy_pequeño=459, pequeño=34.
- `olive_oil`: grande=10.

## 9. Redundancia

- `breast_cancer_wisconsin`: 29 pares con |Spearman| >= 0.85.
- `customer_churn`: 0 pares con |Spearman| >= 0.85.
- `madelon`: 12 pares con |Spearman| >= 0.85.
- `olive_oil`: 2 pares con |Spearman| >= 0.85.

## 10. Dimensionalidad y ruido

- `breast_cancer_wisconsin`: riesgo bajo; posible ruido univariante 4 variables.
- `customer_churn`: riesgo bajo; posible ruido univariante 3 variables.
- `madelon`: riesgo medio; posible ruido univariante 493 variables.
- `olive_oil`: riesgo bajo; posible ruido univariante 0 variables.

## 11. Posibles relaciones espurias o leakage

- `breast_cancer_wisconsin`: 1 variables para revisión semántica; no se confirma leakage en esta fase.
- `customer_churn`: 1 variables para revisión semántica; no se confirma leakage en esta fase.
- `madelon`: 25 variables para revisión semántica; no se confirma leakage en esta fase.
- `olive_oil`: 2 variables para revisión semántica; no se confirma leakage en esta fase.

## 12. Preclasificación preliminar

- `breast_cancer_wisconsin`: candidata_fuerte=25, candidata_moderada=1, pendiente_multivariante=1, posible_ruido_univariante=2, sospechosa=1.
- `customer_churn`: candidata_fuerte=7, candidata_moderada=2, sospechosa=1.
- `madelon`: candidata_fuerte=7, pendiente_multivariante=3, posible_ruido_univariante=453, redundante_o_correlacionada=12, sospechosa=25.
- `olive_oil`: candidata_fuerte=8, sospechosa=2.

## 13. Figuras más importantes

- `results/figures/01_raw_eda/01_02_estructura/raw_structure_summary.png`: Escala muestral, dimensionalidad inicial y ratio variables/muestras.
- `results/figures/01_raw_eda/01_03_calidad/raw_quality_issues_summary.png`: Incidencias accionables de calidad del dato crudo sin heatmap vacío.
- `results/figures/01_raw_eda/01_04_target/raw_target_distribution_panel.png`: Distribución de clases, con lectura separada para binarios y olive_oil multiclase.
- `results/figures/01_raw_eda/01_09_fdr/raw_fdr_before_after.png`: Efecto de la corrección por múltiples comparaciones, especialmente en madelon.
- `results/figures/01_raw_eda/01_11_redundancia/raw_high_corr_pairs_by_dataset.png`: Redundancia potencial por correlación alta y prioridad de control en Fase 2.
- `results/figures/01_raw_eda/01_15_ead/raw_dataset_profile_heatmap.png`: Matriz de severidad EAD trazada desde raw_dataset_profiles.csv.

## 14. Tablas más importantes

`raw_structure_summary.csv`, `raw_quality_summary.csv`, `raw_target_distribution.csv`, `raw_feature_target_tests.csv`, `raw_fdr_corrected_tests.csv`, `raw_effect_sizes.csv`, `raw_high_correlation_pairs.csv`, `raw_feature_preclassification.csv`.

## 15. Conclusiones por dataset

- `breast_cancer_wisconsin`: pasa a fases posteriores con riesgo dimensional bajo, 26 señales fuertes exploratorias y 1 riesgos a revisar.
- `customer_churn`: pasa a fases posteriores con riesgo dimensional bajo, 7 señales fuertes exploratorias y 1 riesgos a revisar.
- `madelon`: pasa a fases posteriores con riesgo dimensional medio, 7 señales fuertes exploratorias y 25 riesgos a revisar.
- `olive_oil`: pasa a fases posteriores con riesgo dimensional bajo, 10 señales fuertes exploratorias y 2 riesgos a revisar.

## 15.1 Matices de interpretación

- `customer_churn`: por su tamaño muestral, la significación estadística debe leerse junto al tamaño de efecto; no se interpreta como evidencia fuerte por p-value aislado.
- `madelon`: el patrón sugiere alta dimensionalidad y mucho ruido univariante, pero no ausencia total de señal; hay variables con señal exploratoria tras FDR.
- `olive_oil`: queda marcado como problema multiclase con desbalance relevante; la evaluación posterior debe priorizar métricas macro o balanceadas.
- `breast_cancer_wisconsin`: muestra señal univariante fuerte, pero también redundancia alta; la Fase 2 debe controlar variables correlacionadas antes de selección formal.

## 16. Implicaciones para la Fase 2

La Fase 2 debe usar explícitamente los artefactos de esta fase para tomar, como mínimo, las siguientes decisiones:
- IDs: excluir o aislar columnas con rol `posible_id` antes de entrenar o seleccionar variables.
- Baja varianza/dominancia: revisar `raw_low_variance_features.csv` y decidir eliminación, recodificación o conservación justificada.
- Codificación: codificar variables categóricas sin introducir información del target ni mezclar ajuste entre train y test.
- Escalado: ajustar escaladores solo con train, especialmente para PCA, métodos basados en distancia y modelos sensibles a escala.
- Outliers: revisar `raw_outlier_summary.csv` y decidir tratamiento robusto sin eliminar observaciones de forma automática.
- Splits: mantener particiones estratificadas cuando proceda, con especial cuidado en `olive_oil` por su target multiclase desbalanceado.
- Leakage/proxies: auditar semánticamente `raw_spurious_risk_features.csv` y `raw_proxy_leakage_candidates.csv` antes de modelar.
- Redundancia: usar `raw_high_correlation_pairs.csv` para controlar bloques correlacionados, especialmente en `breast_cancer_wisconsin`.

## 17. Incidencias y decisiones metodológicas

No se inventan datos ni targets. Se excluyen identificadores de los análisis de asociación y correlación. Las visualizaciones vacías se omiten, especialmente mapas de nulos cuando no hay nulos.