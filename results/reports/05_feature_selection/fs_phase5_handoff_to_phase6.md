# Fase 5 -> Fase 6. Handoff

Regenerado: 2026-06-16 10:31:31.

Fase 6 debe consumir las tablas y carpetas seleccionadas ya materializadas. Resumen de subconjuntos por dataset/método:

| dataset | method | n_sets | min_k | max_k |
| --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | boruta | 1 | 22 | 22 |
| breast_cancer_wisconsin | f_classif | 6 | 3 | 30 |
| breast_cancer_wisconsin | feature_similarity | 6 | 3 | 30 |
| breast_cancer_wisconsin | l1_logistic | 6 | 3 | 30 |
| breast_cancer_wisconsin | linear_svm | 6 | 3 | 30 |
| breast_cancer_wisconsin | mrmr_approx | 6 | 3 | 30 |
| breast_cancer_wisconsin | mutual_correlation | 6 | 3 | 30 |
| breast_cancer_wisconsin | mutual_info | 6 | 3 | 30 |
| breast_cancer_wisconsin | random_forest | 6 | 3 | 30 |
| breast_cancer_wisconsin | rfe | 1 | 10 | 10 |
| breast_cancer_wisconsin | rrfs | 6 | 3 | 30 |
| breast_cancer_wisconsin | variance | 6 | 3 | 30 |
| customer_churn | boruta | 1 | 12 | 12 |
| customer_churn | f_classif | 5 | 1 | 15 |
| customer_churn | feature_similarity | 5 | 1 | 15 |
| customer_churn | l1_logistic | 5 | 1 | 15 |
| customer_churn | linear_svm | 5 | 1 | 15 |
| customer_churn | mrmr_approx | 5 | 1 | 15 |
| customer_churn | mutual_correlation | 5 | 1 | 15 |
| customer_churn | mutual_info | 5 | 1 | 15 |
| customer_churn | random_forest | 5 | 1 | 15 |
| customer_churn | rfe | 1 | 10 | 10 |
| customer_churn | rrfs | 5 | 1 | 15 |
| customer_churn | variance | 5 | 1 | 15 |
| madelon | boruta | 1 | 19 | 19 |
| madelon | f_classif | 7 | 5 | 50 |
| madelon | feature_similarity | 7 | 5 | 50 |
| madelon | l1_logistic | 7 | 5 | 50 |
| madelon | linear_svm | 7 | 5 | 50 |
| madelon | mrmr_approx | 7 | 5 | 50 |
| madelon | mutual_correlation | 7 | 5 | 50 |
| madelon | mutual_info | 7 | 5 | 50 |
| madelon | random_forest | 7 | 5 | 50 |
| madelon | rfe | 1 | 10 | 10 |
| madelon | rrfs | 7 | 5 | 50 |
| madelon | variance | 7 | 5 | 50 |
| olive_oil_3class | boruta | 1 | 8 | 8 |
| olive_oil_3class | f_classif | 3 | 3 | 8 |
| olive_oil_3class | feature_similarity | 3 | 3 | 8 |
| olive_oil_3class | l1_logistic | 3 | 3 | 8 |
| olive_oil_3class | linear_svm | 3 | 3 | 8 |
| olive_oil_3class | mrmr_approx | 3 | 3 | 8 |
| olive_oil_3class | mutual_correlation | 3 | 3 | 8 |
| olive_oil_3class | mutual_info | 3 | 3 | 8 |
| olive_oil_3class | random_forest | 3 | 3 | 8 |
| olive_oil_3class | rfe | 1 | 8 | 8 |
| olive_oil_3class | rrfs | 3 | 3 | 8 |
| olive_oil_3class | variance | 3 | 3 | 8 |
| olive_oil_9class | boruta | 1 | 8 | 8 |
| olive_oil_9class | f_classif | 3 | 3 | 8 |
| olive_oil_9class | feature_similarity | 3 | 3 | 8 |
| olive_oil_9class | l1_logistic | 3 | 3 | 8 |
| olive_oil_9class | linear_svm | 3 | 3 | 8 |
| olive_oil_9class | mrmr_approx | 3 | 3 | 8 |
| olive_oil_9class | mutual_correlation | 3 | 3 | 8 |
| olive_oil_9class | mutual_info | 3 | 3 | 8 |
| olive_oil_9class | random_forest | 3 | 3 | 8 |
| olive_oil_9class | rfe | 1 | 8 | 8 |
| olive_oil_9class | rrfs | 3 | 3 | 8 |
| olive_oil_9class | variance | 3 | 3 | 8 |

Contrato preservado: los datos derivados de `data/selected_features/` se conservan completos.
