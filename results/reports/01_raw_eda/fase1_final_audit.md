# Auditoría crítica final — Fase 1

## Checks superados
- **Cifras del informe Markdown trazadas a CSV:** superado. Evidencia: 54 líneas derivadas de CSV verificadas; faltantes: 0.
- **LaTeX coherente con Markdown:** superado. Evidencia: La copia de results y Plantilla_Latex_GCD/tfgs/tex/resultados_fase1.tex son idénticas y contienen cifras clave; símbolos relacionales convertidos a comandos LaTeX.
- **Notebook, CSV e informes sin contradicciones numéricas detectadas:** superado. Evidencia: Comparación automática contra tablas fuente principales.
- **Figuras guardadas mostradas en notebook:** superado. Evidencia: 36 salidas image/png en notebook y 36 PNG guardados.
- **Figuras no vacías:** superado. Evidencia: PNG con variación de píxel y tamaño razonable; sospechosas: 0.
- **Sospechosas con motivo explícito:** superado. Evidencia: 29 filas en raw_spurious_risk_features.csv con columna motivos completa.
- **Customer Churn no sobreinterpretado:** superado. Evidencia: Informe añade cautela por tamaño muestral y lectura con tamaños de efecto.
- **Madelon interpretado como ruido/alta dimensionalidad con señal residual:** superado. Evidencia: 493 posibles ruidos univariantes y 7 señales fuertes exploratorias.
- **Olive Oil marcado como multiclase desbalanceado:** superado. Evidencia: 9 clases, minoritaria n=25, ratio 8.24.
- **Breast Cancer marcado como señal fuerte y redundancia alta:** superado. Evidencia: 26 señales fuertes exploratorias y 29 pares con Spearman alto.
- **LaTeX integrable en plantilla:** superado. Evidencia: Motor LaTeX local: no disponible; copia en tex/resultados_fase1.tex y entornos balanceados.
- **Fase 2 recibe decisiones concretas:** superado. Evidencia: IDs, Baja varianza, Codificación, Escalado, Outliers, Splits, Leakage, Redundancia.

## Incidencias abiertas
- No quedan incidencias bloqueantes tras los cambios aplicados.

## Incidencias encontradas durante la auditoría
- El traspaso inicial a Fase 2 no enumeraba de forma explícita todas las decisiones solicitadas: IDs, baja varianza, codificación, escalado, outliers, splits, leakage y redundancia.
- El informe inicial podía reforzar la cautela sobre `customer_churn`, porque el tamaño muestral puede hacer significativos efectos pequeños.
- No hay motor LaTeX (`pdflatex`, `lualatex` o `xelatex`) disponible en este entorno; por tanto se verificó integración sintáctica y copia a la carpeta de plantilla, no compilación PDF local.

## Cambios aplicados
- Se actualizó `notebooks/fase1.ipynb` para regenerar el informe con una sección de matices interpretativos por dataset.
- Se actualizó el handoff `raw_phase1_handoff_to_phase2.md` con decisiones concretas para Fase 2.
- Se ajustó la conversión LaTeX en `src/fase1_agent_utils.py` para evitar símbolos Unicode relacionales problemáticos.
- Se regeneraron `raw_phase1_results_report.md`, `raw_phase1_results_report.tex` y `Plantilla_Latex_GCD/tfgs/tex/resultados_fase1.tex` ejecutando el notebook completo en `qfs_env`.

## Trazabilidad de cifras
- Las cifras del informe Markdown se contrastaron contra estas tablas: `raw_candidate_features_univariate.csv`, `raw_dataset_profiles.csv`, `raw_dataset_signal_summary.csv`, `raw_dimensionality_summary.csv`, `raw_effect_size_interpretation.csv`, `raw_fdr_summary.csv`, `raw_figures_selected_for_report.csv`, `raw_load_summary.csv`, `raw_quality_summary.csv`, `raw_redundancy_summary.csv`, `raw_spurious_risk_features.csv`, `raw_structure_summary.csv`, `raw_target_balance_summary.csv`.
- Las variables sospechosas se trazan a `raw_spurious_risk_features.csv`; los candidatos de proxy/leakage fuerte se trazan además a `raw_proxy_leakage_candidates.csv`.
- Las figuras candidatas para memoria se trazan a `raw_figures_selected_for_report.csv` y existen en `results/figures/01_raw_eda/`.

## Puntos que deben vigilarse en Fase 2
- **IDs:** excluir o aislar columnas `posible_id` antes de cualquier ajuste.
- **Baja varianza/dominancia:** revisar `raw_low_variance_features.csv`; no eliminar sin comprobar impacto por dataset.
- **Codificación:** ajustar codificadores solo con train y controlar categorías no vistas.
- **Escalado:** ajustar escaladores solo con train; especialmente importante para PCA, distancias y métodos sensibles a escala.
- **Outliers:** revisar `raw_outlier_summary.csv` y preferir tratamientos robustos antes que borrado automático.
- **Splits:** usar estratificación; `olive_oil` requiere especial cuidado por multiclase y desbalance.
- **Leakage/proxies:** revisar semánticamente `raw_spurious_risk_features.csv` y `raw_proxy_leakage_candidates.csv` antes de modelar.
- **Redundancia:** controlar `raw_high_correlation_pairs.csv`, especialmente en `breast_cancer_wisconsin`.
- **Customer Churn:** interpretar p-values junto con tamaños de efecto por el gran tamaño muestral.
- **Madelon:** tratar como dataset de alta dimensionalidad y ruido, preservando la posibilidad de señal real.

## Resultado de la auditoría
La Fase 1 queda auditada y apta para alimentar Fase 2, con las cautelas metodológicas anteriores.
