# Fase 5. Selección clásica de características

Regenerado: 2026-06-16 10:31:31.

La fase aplica selectores clásicos sobre `X_train, y_train` y proyecta las columnas seleccionadas a validation y test sin volver a decidir con esos splits. Este report se ha reconstruido desde las tablas canónicas actuales de `results/tables/05_feature_selection/` tras ejecutar `notebooks/fase5.ipynb` completo en `qfs_env`.

## Datasets

| dataset | n_train | n_validation | n_test | n_features | n_classes_train | minority_class_train_pct |
| --- | --- | --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | 398 | 85 | 86 | 30 | 2 | 37.1859 |
| customer_churn | 308582 | 66125 | 66125 | 15 | 2 | 43.2893 |
| madelon | 1400 | 300 | 300 | 500 | 2 | 50.0000 |
| olive_oil_3class | 400 | 86 | 86 | 8 | 3 | 17.0000 |
| olive_oil_9class | 400 | 86 | 86 | 8 | 9 | 4.5000 |

## Métodos registrados

| method | familia | usa_target | salida | criterio_tecnico |
| --- | --- | --- | --- | --- |
| variance | base mínima | False | ranking | varianza tras escalado |
| f_classif | relevancia pura | True | ranking | F univariante |
| mutual_info | relevancia pura | True | ranking | I(x;y) |
| mutual_correlation | redundancia pura | False | ranking | Pearson medio |
| feature_similarity | redundancia pura | False | ranking | clusters varianza-covarianza |
| mrmr_approx | relevancia-redundancia | True | ranking | MI menos correlación |
| rrfs | relevancia-redundancia | True | ranking | Fisher con poda de similitud |
| boruta | wrapper all-relevant | True | conjunto natural | shadow features |
| rfe | wrapper minimal-optimal | True | ranking | eliminación recursiva |
| l1_logistic | embedded | True | ranking | coeficientes L1 |
| random_forest | embedded | True | ranking | importancia de bosque |
| linear_svm | embedded | True | ranking | margen lineal |

## Valores de k

| dataset | n_features | k | reduction_pct |
| --- | --- | --- | --- |
| breast_cancer_wisconsin | 30 | 3 | 90.0000 |
| breast_cancer_wisconsin | 30 | 5 | 83.3333 |
| breast_cancer_wisconsin | 30 | 10 | 66.6667 |
| breast_cancer_wisconsin | 30 | 15 | 50.0000 |
| breast_cancer_wisconsin | 30 | 20 | 33.3333 |
| breast_cancer_wisconsin | 30 | 30 | 0.0000 |
| customer_churn | 15 | 1 | 93.3333 |
| customer_churn | 15 | 4 | 73.3333 |
| customer_churn | 15 | 5 | 66.6667 |
| customer_churn | 15 | 10 | 33.3333 |
| customer_churn | 15 | 15 | 0.0000 |
| madelon | 500 | 5 | 99.0000 |
| madelon | 500 | 10 | 98.0000 |
| madelon | 500 | 15 | 97.0000 |
| madelon | 500 | 20 | 96.0000 |
| madelon | 500 | 22 | 95.6000 |
| madelon | 500 | 30 | 94.0000 |
| madelon | 500 | 50 | 90.0000 |
| olive_oil_3class | 8 | 3 | 62.5000 |
| olive_oil_3class | 8 | 5 | 37.5000 |
| olive_oil_3class | 8 | 8 | 0.0000 |
| olive_oil_9class | 8 | 3 | 62.5000 |
| olive_oil_9class | 8 | 5 | 37.5000 |
| olive_oil_9class | 8 | 8 | 0.0000 |

## Ejecución

Runs totales: 170. Runs con estado `ok`: 170. Runs con incidencias: 0.

| dataset | method | runs | ok_runs | mean_elapsed_seconds | sample_applied |
| --- | --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | boruta | 1 | 1 | 10.2843 | False |
| breast_cancer_wisconsin | f_classif | 3 | 3 | 0.0005 | False |
| breast_cancer_wisconsin | feature_similarity | 3 | 3 | 0.0007 | False |
| breast_cancer_wisconsin | l1_logistic | 3 | 3 | 0.1317 | False |
| breast_cancer_wisconsin | linear_svm | 3 | 3 | 0.0046 | False |
| breast_cancer_wisconsin | mrmr_approx | 3 | 3 | 0.0288 | False |
| breast_cancer_wisconsin | mutual_correlation | 3 | 3 | 0.0007 | False |
| breast_cancer_wisconsin | mutual_info | 3 | 3 | 0.0281 | False |
| breast_cancer_wisconsin | random_forest | 3 | 3 | 0.5596 | False |
| breast_cancer_wisconsin | rfe | 3 | 3 | 2.0706 | False |
| breast_cancer_wisconsin | rrfs | 3 | 3 | 0.0286 | False |
| breast_cancer_wisconsin | variance | 3 | 3 | 0.0002 | False |
| customer_churn | boruta | 1 | 1 | 6.6082 | True |
| customer_churn | f_classif | 3 | 3 | 0.0283 | False |
| customer_churn | feature_similarity | 3 | 3 | 0.1768 | False |
| customer_churn | l1_logistic | 3 | 3 | 0.0234 | True |
| customer_churn | linear_svm | 3 | 3 | 0.0031 | True |
| customer_churn | mrmr_approx | 3 | 3 | 0.0160 | True |
| customer_churn | mutual_correlation | 3 | 3 | 0.1495 | False |
| customer_churn | mutual_info | 3 | 3 | 0.0137 | True |
| customer_churn | random_forest | 3 | 3 | 0.8086 | True |
| customer_churn | rfe | 3 | 3 | 1.2235 | True |
| customer_churn | rrfs | 3 | 3 | 0.0151 | True |
| customer_churn | variance | 3 | 3 | 0.0319 | False |
| madelon | boruta | 1 | 1 | 11.7931 | False |
| madelon | f_classif | 3 | 3 | 0.0025 | False |
| madelon | feature_similarity | 3 | 3 | 0.3503 | False |
| madelon | l1_logistic | 3 | 3 | 0.7406 | False |
| madelon | linear_svm | 3 | 3 | 0.0359 | False |
| madelon | mrmr_approx | 3 | 3 | 1.2617 | False |

## Subconjuntos exportados

Subconjuntos exportados: 250. Directorio conservado completo: `data/selected_features/`.

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

## Estabilidad

| dataset | method | mean_jaccard | min_jaccard | comparisons |
| --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | f_classif | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | feature_similarity | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | l1_logistic | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | linear_svm | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | mrmr_approx | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | mutual_correlation | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | mutual_info | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | rfe | 1.0000 | 1.0000 | 3 |
| breast_cancer_wisconsin | rrfs | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | variance | 1.0000 | 1.0000 | 18 |
| breast_cancer_wisconsin | random_forest | 0.8404 | 0.5000 | 18 |
| customer_churn | f_classif | 1.0000 | 1.0000 | 15 |
| customer_churn | feature_similarity | 1.0000 | 1.0000 | 15 |
| customer_churn | mutual_correlation | 1.0000 | 1.0000 | 15 |
| customer_churn | random_forest | 1.0000 | 1.0000 | 15 |
| customer_churn | rfe | 1.0000 | 1.0000 | 3 |
| customer_churn | variance | 1.0000 | 1.0000 | 15 |
| customer_churn | l1_logistic | 0.9636 | 0.8182 | 15 |
| customer_churn | linear_svm | 0.9556 | 0.6667 | 15 |
| customer_churn | mutual_info | 0.9467 | 0.6000 | 15 |
| customer_churn | rrfs | 0.9467 | 0.6000 | 15 |
| customer_churn | mrmr_approx | 0.7618 | 0.3333 | 15 |
| madelon | f_classif | 1.0000 | 1.0000 | 21 |
| madelon | feature_similarity | 1.0000 | 1.0000 | 21 |
| madelon | l1_logistic | 1.0000 | 1.0000 | 21 |
| madelon | linear_svm | 1.0000 | 1.0000 | 21 |
| madelon | mrmr_approx | 1.0000 | 1.0000 | 21 |
| madelon | mutual_correlation | 1.0000 | 1.0000 | 21 |
| madelon | mutual_info | 1.0000 | 1.0000 | 21 |
| madelon | rfe | 1.0000 | 1.0000 | 3 |
| madelon | rrfs | 1.0000 | 1.0000 | 21 |
| madelon | variance | 1.0000 | 1.0000 | 21 |
| madelon | random_forest | 0.7782 | 0.3889 | 21 |
| olive_oil_3class | f_classif | 1.0000 | 1.0000 | 9 |
| olive_oil_3class | feature_similarity | 1.0000 | 1.0000 | 9 |
| olive_oil_3class | l1_logistic | 1.0000 | 1.0000 | 9 |
| olive_oil_3class | linear_svm | 1.0000 | 1.0000 | 9 |
| olive_oil_3class | mrmr_approx | 1.0000 | 1.0000 | 9 |
| olive_oil_3class | mutual_correlation | 1.0000 | 1.0000 | 9 |
| olive_oil_3class | mutual_info | 1.0000 | 1.0000 | 9 |

## Permutación y redundancia

Tablas disponibles: `fs_permutation_summary.csv` (10 filas) y `fs_redundancy_vs_full.csv` (250 filas).

## Cierre

La fase queda sincronizada con el run canónico actual. Los alias `X_val_selected.csv` y `X_validation_selected.csv` se conservan intencionadamente y no se deduplican.
