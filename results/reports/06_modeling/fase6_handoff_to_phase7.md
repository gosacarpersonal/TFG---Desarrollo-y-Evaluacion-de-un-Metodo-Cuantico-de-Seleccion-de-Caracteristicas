# Fase 6 -> Fase 7. Handoff

Regenerado: 2026-06-16 10:31:31.

Tablas principales para fases posteriores:

- `results/tables/06_modeling/modeling_validation_results_all.csv`
- `results/tables/06_modeling/modeling_test_results_candidates.csv`
- `results/tables/06_modeling/modeling_test_confidence_intervals.csv`
- `results/tables/06_modeling/modeling_pairwise_comparison_tests.csv`
- `results/predictions/06_modeling/test_predictions.csv`
- `results/predictions/06_modeling/test_predictions_xgboost.csv`

Candidatos test actuales:

| dataset | feature_set | model_name | candidate_label | validation_macro_f1 | test_macro_f1 | n_features_used |
| --- | --- | --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | all_features | linear_svm | baseline_mejor_en_validation | 0.9749 | 0.9374 | 30 |
| breast_cancer_wisconsin | boruta_confirmed_22 | linear_svm | subconjunto_top_1_validation | 0.9874 | 0.9502 | 22 |
| breast_cancer_wisconsin | linear_svm_k10 | xgboost | subconjunto_top_2_validation | 0.9749 | 0.9496 | 10 |
| customer_churn | all_features | xgboost | baseline_mejor_en_validation | 0.9999 | 0.9998 | 10 |
| customer_churn | l1_logistic_k10 | xgboost | subconjunto_top_1_validation | 0.9992 | 0.9991 | 10 |
| customer_churn | mrmr_approx_k10 | xgboost | subconjunto_top_2_validation | 0.9992 | 0.9991 | 10 |
| madelon | all_features | xgboost | baseline_mejor_en_validation | 0.7433 | 0.8130 | 500 |
| madelon | boruta_confirmed_19 | xgboost | subconjunto_top_1_validation | 0.8565 | 0.9067 | 19 |
| madelon | rfe_k10 | xgboost | subconjunto_top_2_validation | 0.8499 | 0.9000 | 10 |
| olive_oil_3class | all_features | linear_svm | baseline_mejor_en_validation | 1.0000 | 1.0000 | 8 |
| olive_oil_3class | f_classif_k5 | linear_svm | subconjunto_top_1_validation | 1.0000 | 1.0000 | 5 |
| olive_oil_3class | l1_logistic_k5 | linear_svm | subconjunto_top_2_validation | 1.0000 | 1.0000 | 5 |
| olive_oil_9class | all_features | linear_svm | baseline_mejor_en_validation | 0.9434 | 0.8387 | 8 |
| olive_oil_9class | l1_logistic_k5 | xgboost | subconjunto_top_1_validation | 0.9552 | 0.9543 | 5 |
| olive_oil_9class | boruta_confirmed_8 | linear_svm | subconjunto_top_2_validation | 0.9434 | 0.8387 | 8 |
