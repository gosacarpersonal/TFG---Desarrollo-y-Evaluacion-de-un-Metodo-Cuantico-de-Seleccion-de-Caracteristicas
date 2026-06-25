# Auditoría de reconstrucción narrativa — Fase 1

Fecha de validación: 2026-06-06.

## Alcance

Se reconstruyó `notebooks/fase1.ipynb` como notebook narrativo y auditable, preservando los cálculos, CSV, rutas de artefactos y conclusiones científicas existentes. La intervención se centró en presentación, explicación metodológica, selección de evidencia visible y legibilidad visual.

## Cambios aplicados

- Introducción reescrita como fase científica del TFG: qué analiza Fase 1, qué no decide, qué artefactos genera y cómo alimenta Fase 2.
- Eliminado el bloque `0. Decisiones visuales`.
- Sustituido el patrón repetitivo `Objetivo / Decisión visual` por texto de sección con pregunta, criterio, evidencia, interpretación y traspaso.
- Añadido `src/fase1_narrative_helpers.py` para vistas compactas, observaciones por dataset, tablas de handoff y resúmenes de auditoría.
- Eliminado el uso de `.head()` y `.tail()` como evidencia visible en el notebook.
- Manteniendo el notebook como orquestador: los cálculos principales siguen en `src/fase1_refined_workflow.py`; las nuevas funciones solo preparan vistas narrativas.

## Secciones reconstruidas

- 1.1 Carga: tabla compacta con archivo abreviado, filas, columnas, target, carga e incidencias; explicación de escala log y límite de interpretación.
- 1.2 Estructura: explicación de `ratio_features_muestras`, umbrales exploratorios internos y observación por dataset.
- 1.3 Calidad: foco en incidencias reales de baja variabilidad/dominancia; nulos, duplicados y constantes se dejan como control tabular.
- 1.4 Target: tabla sin `estado`, con clase minoritaria/mayoritaria, tamaños y ratio; lectura por dataset para splits y métricas.
- 1.5 Muestreo visual: tratado como caso específico de `customer_churn`; aclarado que no altera cálculos ni CSV completos.
- 1.6 Univariante: explicación de skewness, kurtosis, outlier IQR y selección de variables; ranking por dataset.
- 1.7 Normalidad: explicitados test, condiciones y cautelas; la advertencia metodológica se movió del gráfico al Markdown.
- 1.8 Asociación: explicitados test por tipo de variable, FDR, tamaño de efecto e información mutua; top por efecto y FDR por dataset.
- 1.9-1.10 FDR/efectos: fusionadas narrativamente como significancia corregida y magnitud de efecto.
- 1.11 Correlación: justificado `|Spearman| >= 0.85`; heatmaps triangulares y rankings cuando comunican mejor.
- 1.12 PCA: separado riesgo dimensional de diagnóstico PCA; añadido componente para 80% de varianza en vista compacta.
- 1.13 Riesgos: explicitados motivos de sospecha y recordatorio de que sospechosa no significa eliminar.
- 1.14 Preclasificación: reforzada como mapa exploratorio, no selección final; observación por dataset.
- 1.15 EAD: tabla compacta de perfil, decisión para Fase 2 y cautela; figuras candidatas para memoria visibles.
- 1.16 Handoff: checklist compacto y tabla tema/evidencia/decisión/riesgo residual.
- 1.17 Auditoría: resumen por tipo de artefacto; detalle completo preservado en CSV.

## Figuras rediseñadas o ajustadas

- `raw_load_rows_columns.png`: retiradas etiquetas internas de “dominio muestral/dimensional”; añadidas etiquetas numéricas y justificación de escala log.
- `raw_normality_rejection_by_dataset.png`: eliminado bloque de texto largo dentro de la figura; la cautela queda en Markdown.
- Heatmaps de Spearman: convertidos a vista triangular sin anotaciones numéricas densas.
- Se mantiene el enfoque de rankings para variables sospechosas y efectos principales cuando una tabla/ranking comunica mejor que un volcano completo.

No se eliminaron físicamente PNG existentes para preservar rutas y compatibilidad con informes. Se eliminaron o sustituyeron en la presentación del notebook tablas gigantes, `tail(12)`, `.head()` arbitrarios y el plan visual global.

## Tablas visibles resumidas

El notebook muestra vistas compactas de:

- carga;
- estructura;
- calidad;
- target;
- muestreo visual;
- resumen univariante;
- normalidad;
- top de asociación por efecto y FDR;
- resumen FDR y magnitud de efecto;
- redundancia;
- dimensionalidad y PCA;
- riesgos;
- preclasificación;
- perfil EAD;
- checklist y handoff;
- resumen de artefactos.

Los CSV completos se preservan en `results/tables/01_raw_eda`.

## CSV preservados

Verificados CSV clave:

- `raw_load_summary.csv`: 4 filas.
- `raw_structure_summary.csv`: 4 filas.
- `raw_missing_values.csv`: 557 filas.
- `raw_numeric_descriptive_stats.csv`: 547 filas.
- `raw_distribution_shape.csv`: 547 filas.
- `raw_feature_target_tests.csv`: 550 filas.
- `raw_fdr_corrected_tests.csv`: 550 filas.
- `raw_effect_sizes.csv`: 550 filas.
- `raw_high_correlation_pairs.csv`: 43 filas.
- `raw_spurious_risk_features.csv`: 29 filas.
- `raw_feature_preclassification.csv`: 550 filas.
- `raw_dataset_profiles.csv`: 4 filas.

## Conclusiones científicas preservadas

Se mantienen las conclusiones principales:

- `breast_cancer_wisconsin`: señal univariante fuerte y redundancia alta que debe controlarse.
- `customer_churn`: tamaño muestral grande; significancia debe leerse con tamaño de efecto.
- `madelon`: alta dimensionalidad, ruido univariante y señal residual tras FDR.
- `olive_oil`: problema multiclase desbalanceado con señal fuerte y revisión semántica pendiente.

No se añadieron conclusiones de rendimiento predictivo, causalidad, leakage confirmado ni selección final.

## Validación ejecutada

- Notebook ejecutado completo con `/home/gosacar/miniconda3/envs/qfs_env/bin/python -m jupyter nbconvert --to notebook --execute notebooks/fase1.ipynb --inplace`.
- `py_compile` correcto para:
  - `src/fase1_refined_workflow.py`;
  - `src/fase1_agent_utils.py`;
  - `src/fase1_narrative_helpers.py`.
- Figuras PNG en `results/figures/01_raw_eda`: 36.
- Figuras vacías detectadas: 0.
- Figuras visualmente en blanco detectadas: 0.
- Notebook sin errores de ejecución.
- Notebook sin `.head()` ni `.tail()` en código fuente.
- Sin salidas de texto plano gigantes detectadas.
- Lámina de revisión visual generada en `results/reports/01_raw_eda/_visual_review/fase1_reconstruccion_review_sheet.jpg`.
- Informes Markdown/LaTeX de Fase 1 actualizados por `generar_informes_fase1(contexto)`.

## Incidencias

- La especificación pedía `prompts_raw/reconstrucción_fase1.txt`, pero en disco existe `promtps_raw/reconstrucción_fase1.txt`. Se usó esa ruta real sin renombrarla.
- No se generó un PDF independiente del notebook; la revisión de legibilidad se hizo sobre figuras PNG y lámina visual para prevenir clipping/solapamientos en exportación.
