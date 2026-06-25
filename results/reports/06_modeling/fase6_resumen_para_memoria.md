# Fase 6. Modelado y evaluación final

Regenerado: 2026-06-16 10:31:31.

La fase compara modelos sobre todos los atributos y subconjuntos procedentes de Fase 5. Este report se ha reconstruido desde las tablas canónicas actuales de `results/tables/06_modeling/` tras ejecutar `notebooks/fase6.ipynb` completo en `qfs_env`.

## Cobertura de modelos

Experimentos de validation: 260. Candidatos evaluados en test: 15. Filas de validation con `xgboost`: 65.

| dataset | models_evaluated |
| --- | --- |
| breast_cancer_wisconsin | linear_svm, logistic_regression, random_forest, xgboost |
| customer_churn | linear_svm, logistic_regression, random_forest, xgboost |
| madelon | linear_svm, logistic_regression, random_forest, xgboost |
| olive_oil_3class | linear_svm, logistic_regression, random_forest, xgboost |
| olive_oil_9class | linear_svm, logistic_regression, random_forest, xgboost |

## Mejor configuración por validation

| dataset | feature_set | model_name | macro_f1 | balanced_accuracy | n_features_used |
| --- | --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | boruta_confirmed_22 | linear_svm | 0.9874 | 0.9844 | 22 |
| customer_churn | all_features | xgboost | 0.9999 | 0.9999 | 10 |
| madelon | boruta_confirmed_19 | xgboost | 0.8565 | 0.8567 | 19 |
| olive_oil_3class | random_forest_k5 | linear_svm | 1.0000 | 1.0000 | 5 |
| olive_oil_9class | l1_logistic_k5 | xgboost | 0.9552 | 0.9528 | 5 |

## Mejor configuración observada en test entre candidatos cerrados

| dataset | feature_set | model_name | validation_macro_f1 | test_macro_f1 | test_balanced_accuracy | n_features_used |
| --- | --- | --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | boruta_confirmed_22 | linear_svm | 0.9874 | 0.9502 | 0.9502 | 22 |
| customer_churn | all_features | xgboost | 0.9999 | 0.9998 | 0.9998 | 10 |
| madelon | boruta_confirmed_19 | xgboost | 0.8565 | 0.9067 | 0.9067 | 19 |
| olive_oil_3class | all_features | linear_svm | 1.0000 | 1.0000 | 1.0000 | 8 |
| olive_oil_9class | l1_logistic_k5 | xgboost | 0.9552 | 0.9543 | 0.9583 | 5 |

## Candidatos Madelon

| dataset | feature_set | model_name | validation_macro_f1 | test_macro_f1 | test_balanced_accuracy | n_features_used |
| --- | --- | --- | --- | --- | --- | --- |
| madelon | boruta_confirmed_19 | xgboost | 0.8565 | 0.9067 | 0.9067 | 19 |
| madelon | rfe_k10 | xgboost | 0.8499 | 0.9000 | 0.9000 | 10 |
| madelon | all_features | xgboost | 0.7433 | 0.8130 | 0.8133 | 500 |

## Intervalos y comparaciones

Intervalos bootstrap en test: 45 filas. Comparaciones pareadas frente a baseline: 10 filas. Tests de permutación: 15 filas.

| dataset | baseline_experiment_id | candidate_experiment_id | difference_macro_f1 | ci_low | ci_high | sign_permutation_p_value | n_bootstrap | n_sign_permutations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | breast_cancer_wisconsin__all_features__linear_svm | breast_cancer_wisconsin__boruta_confirmed_22__linear_svm | 0.0128 | 0.0000 | 0.0391 | 1.0000 | 400 | 2000 |
| breast_cancer_wisconsin | breast_cancer_wisconsin__all_features__linear_svm | breast_cancer_wisconsin__linear_svm_k10__xgboost | 0.0122 | -0.0466 | 0.0579 | 1.0000 | 400 | 2000 |
| customer_churn | customer_churn__all_features__xgboost | customer_churn__l1_logistic_k10__xgboost | -0.0007 | -0.0009 | -0.0005 | 0.0005 | 400 | 2000 |
| customer_churn | customer_churn__all_features__xgboost | customer_churn__mrmr_approx_k10__xgboost | -0.0007 | -0.0009 | -0.0005 | 0.0005 | 400 | 2000 |
| madelon | madelon__all_features__xgboost | madelon__boruta_confirmed_19__xgboost | 0.0936 | 0.0533 | 0.1401 | 0.0005 | 400 | 2000 |
| madelon | madelon__all_features__xgboost | madelon__rfe_k10__xgboost | 0.0869 | 0.0440 | 0.1370 | 0.0005 | 400 | 2000 |
| olive_oil_3class | olive_oil_3class__all_features__linear_svm | olive_oil_3class__f_classif_k5__linear_svm | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 400 | 2000 |
| olive_oil_3class | olive_oil_3class__all_features__linear_svm | olive_oil_3class__l1_logistic_k5__linear_svm | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 400 | 2000 |
| olive_oil_9class | olive_oil_9class__all_features__linear_svm | olive_oil_9class__l1_logistic_k5__xgboost | 0.1155 | -0.0037 | 0.2405 | 0.3548 | 400 | 2000 |
| olive_oil_9class | olive_oil_9class__all_features__linear_svm | olive_oil_9class__boruta_confirmed_8__linear_svm | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 400 | 2000 |

## SHAP

Ficheros SHAP/tablas relacionadas detectados: 32. Figuras de modelado detectadas: 54.

## Lectura prudente

Los subconjuntos no se reinterpretan como óptimos universales: la selección de candidatos se cierra en validation y test se consulta para la evaluación final. La versión actual ya incluye XGBoost; en Madelon el candidato principal actual no es el antiguo `random_forest` con macro-F1 alrededor de 0.766, sino configuraciones `xgboost` como `boruta_confirmed_19` y `rfe_k10`.
