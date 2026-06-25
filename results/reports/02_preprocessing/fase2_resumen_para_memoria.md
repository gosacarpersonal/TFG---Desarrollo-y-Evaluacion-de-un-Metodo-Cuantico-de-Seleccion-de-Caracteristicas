# Resultados de la Fase 2 - Preprocesado Estructural

La Fase 2 aplica únicamente transformaciones estructurales verificables: renombrado, exclusión de identificadores, codificación del target y guardado de datasets procesados.

No se imputan nulos, no se eliminan outliers, no se eliminan variables por baja cardinalidad y no se ajustan encoders ni escaladores globales.

Los umbrales de cardinalidad/dominancia/correlación se documentan como alertas heurísticas, con referencias a caret, scikit-learn y la ficha UCI/PDF de Madelon cuando procede.

Tablas principales:
- `results/tables/02_preprocessing/fase2_cardinalidad_dominancia.csv`
- `results/tables/02_preprocessing/fase2_carga_datasets.csv`
- `results/tables/02_preprocessing/fase2_categorias_predictoras.csv`
- `results/tables/02_preprocessing/fase2_codificacion_target.csv`
- `results/tables/02_preprocessing/fase2_codigos_especiales.csv`
- `results/tables/02_preprocessing/fase2_correlation_shift.csv`
- `results/tables/02_preprocessing/fase2_dimensionalidad_encoding.csv`
- `results/tables/02_preprocessing/fase2_distribution_shift.csv`
- `results/tables/02_preprocessing/fase2_duplicados.csv`
- `results/tables/02_preprocessing/fase2_identificadores_detectados.csv`
- `results/tables/02_preprocessing/fase2_impacto_estructura.csv`
- `results/tables/02_preprocessing/fase2_nulos_variables.csv`
- `results/tables/02_preprocessing/fase2_outliers_iqr.csv`
- `results/tables/02_preprocessing/fase2_rangos_numericos.csv`
- `results/tables/02_preprocessing/fase2_recarga_datasets.csv`
- `results/tables/02_preprocessing/fase2_renombrado_columnas.csv`
- `results/tables/02_preprocessing/fase2_separacion_xy.csv`
- `results/tables/02_preprocessing/fase2_target_shift.csv`
- `results/tables/02_preprocessing/fase2_tipos_columnas.csv`
- `results/tables/02_preprocessing/fase2_transformaciones_estructurales.csv`

Figuras:
- `results/figures/02_preprocessing/fase2_categorica_customer_churn_contract_length.pdf`
- `results/figures/02_preprocessing/fase2_categorica_customer_churn_contract_length.png`
- `results/figures/02_preprocessing/fase2_categorica_customer_churn_gender.pdf`
- `results/figures/02_preprocessing/fase2_categorica_customer_churn_gender.png`
- `results/figures/02_preprocessing/fase2_categorica_customer_churn_subscription_type.pdf`
- `results/figures/02_preprocessing/fase2_categorica_customer_churn_subscription_type.png`
- `results/figures/02_preprocessing/fase2_distribuciones_numericas_breast_cancer_wisconsin.pdf`
- `results/figures/02_preprocessing/fase2_distribuciones_numericas_breast_cancer_wisconsin.png`
- `results/figures/02_preprocessing/fase2_distribuciones_numericas_customer_churn.pdf`
- `results/figures/02_preprocessing/fase2_distribuciones_numericas_customer_churn.png`
- `results/figures/02_preprocessing/fase2_distribuciones_numericas_madelon.pdf`
- `results/figures/02_preprocessing/fase2_distribuciones_numericas_madelon.png`
- `results/figures/02_preprocessing/fase2_distribuciones_numericas_olive_oil.pdf`
- `results/figures/02_preprocessing/fase2_distribuciones_numericas_olive_oil.png`
- `results/figures/02_preprocessing/fase2_impacto_preprocesado_control.pdf`
- `results/figures/02_preprocessing/fase2_impacto_preprocesado_control.png`
- `results/figures/02_preprocessing/fase2_outliers_iqr_breast_cancer_wisconsin.pdf`
- `results/figures/02_preprocessing/fase2_outliers_iqr_breast_cancer_wisconsin.png`
- `results/figures/02_preprocessing/fase2_outliers_iqr_customer_churn.pdf`
- `results/figures/02_preprocessing/fase2_outliers_iqr_customer_churn.png`
- `results/figures/02_preprocessing/fase2_outliers_iqr_madelon.pdf`
- `results/figures/02_preprocessing/fase2_outliers_iqr_madelon.png`
- `results/figures/02_preprocessing/fase2_outliers_iqr_olive_oil.pdf`
- `results/figures/02_preprocessing/fase2_outliers_iqr_olive_oil.png`
- `results/figures/02_preprocessing/fase2_outliers_iqr_resumen_completo.pdf`
- `results/figures/02_preprocessing/fase2_outliers_iqr_resumen_completo.png`
- `results/figures/02_preprocessing/fase2_outliers_iqr_resumen_zoom.pdf`
- `results/figures/02_preprocessing/fase2_outliers_iqr_resumen_zoom.png`

Datasets procesados:
- `data/processed/breast_cancer_wisconsin_processed.csv`
- `data/processed/customer_churn_processed.csv`
- `data/processed/madelon_processed.csv`
- `data/processed/olive_oil_processed.csv`