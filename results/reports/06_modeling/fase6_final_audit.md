# Fase 6. Auditoría final

Regenerado: 2026-06-16 10:31:31.

Checks de coherencia desde tablas actuales:

- Experimentos validation: 260.
- Candidatos test: 15.
- Modelos presentes: linear_svm, logistic_regression, random_forest, xgboost.
- Filas XGBoost en validation: 65.
- Mejor Madelon en test: boruta_confirmed_19 / xgboost / macro-F1 0.9067.

| dataset | feature_set | model_name | test_macro_f1 | test_balanced_accuracy | n_features_used |
| --- | --- | --- | --- | --- | --- |
| breast_cancer_wisconsin | boruta_confirmed_22 | linear_svm | 0.9502 | 0.9502 | 22 |
| customer_churn | all_features | xgboost | 0.9998 | 0.9998 | 10 |
| madelon | boruta_confirmed_19 | xgboost | 0.9067 | 0.9067 | 19 |
| olive_oil_3class | all_features | linear_svm | 1.0000 | 1.0000 | 8 |
| olive_oil_9class | l1_logistic_k5 | xgboost | 0.9543 | 0.9583 | 5 |
