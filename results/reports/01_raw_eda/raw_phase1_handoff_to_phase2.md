# Traspaso de Fase 1 a Fase 2

Usar estos resultados para decidir tratamiento de tipos, nulos, constantes, outliers, escalado, codificación, split, controles de leakage y redundancia.

## Decisiones concretas obligatorias

- IDs: excluir o aislar variables con rol `posible_id` según `raw_variable_roles.csv`.
- Baja varianza/dominancia: revisar `raw_low_variance_features.csv` antes de eliminar o conservar variables.
- Codificación: transformar categóricas con ajuste solo en train y categorías desconocidas controladas.
- Escalado: ajustar escaladores solo en train; obligatorio para PCA, distancias y modelos sensibles a escala.
- Outliers: revisar `raw_outlier_summary.csv`; no eliminar automáticamente sin criterio de dominio o robustez.
- Splits: usar particiones estratificadas cuando proceda; especial atención a `olive_oil` por desbalance multiclase.
- Leakage/proxies: revisar `raw_spurious_risk_features.csv` y `raw_proxy_leakage_candidates.csv` antes del modelado.
- Redundancia: controlar pares de `raw_high_correlation_pairs.csv`, especialmente en `breast_cancer_wisconsin`.

## breast_cancer_wisconsin
- Carga correcta: True
- Target identificado: True
- Problemas de calidad: False
- Riesgo dimensionalidad: bajo
- Variables sospechosas: True
- Estado para Fase 2: sí

## customer_churn
- Carga correcta: True
- Target identificado: True
- Problemas de calidad: True
- Riesgo dimensionalidad: bajo
- Variables sospechosas: True
- Estado para Fase 2: sí

## madelon
- Carga correcta: True
- Target identificado: True
- Problemas de calidad: True
- Riesgo dimensionalidad: medio
- Variables sospechosas: True
- Estado para Fase 2: sí

## olive_oil
- Carga correcta: True
- Target identificado: True
- Problemas de calidad: True
- Riesgo dimensionalidad: bajo
- Variables sospechosas: True
- Estado para Fase 2: sí
