# Prompt de arreglo — Fase 8c (evaluación QFS + integración con Fase 7)

Construye `notebooks/fase9.ipynb` (o extiende `notebooks/fase7.ipynb` con una sección
8/9 — decide según limpieza de la estructura, prefiero un cuaderno nuevo `fase8b` o
`fase9`). Respeta `docs/auditoria/estructura_notebooks.md`.

Requisito previo: Fase 8a + 8b completadas. Fase 6 ya ejecutada con XGBoost incluido
(Tier 2). Predicciones por fila de fase 6 archivadas
(`results/tables/06_modeling/validation_predictions_*.csv`, `test_predictions_*.csv`).

## Sección 9.1 — Carga de configuraciones QFS y materialización de subconjuntos

Para cada dataset y para cada configuración seleccionada por fase 8b
(operativo `(α=0.5, β*)` + oráculo `α*` por k), construir los conjuntos
`X_train_qfs / X_validation_qfs / X_test_qfs` a partir de los splits de fase 4 y los
bitstrings guardados. Verificar que el número de variables coincide con el k objetivo.

## Sección 9.2 — Entrenamiento bajo el protocolo idéntico de Fase 6

Para cada `(dataset, configuración QFS)`, entrenar los **mismos cuatro modelos** que
fase 6 (logistic_regression, linear_svm, random_forest, xgboost) con los mismos
hiperparámetros fijos y pesos balanceados. NO hacer búsqueda. Reusar el código de
fase 6 (`src/phase6_modeling/pipeline.py`) sin duplicar lógica.

Calcular sobre validation y test:
- macro-F1 (primaria), balanced_accuracy (desempate).
- En binarios (`breast_cancer_wisconsin`, `customer_churn`): AUC-ROC como métrica de
  contexto frente al paper.
- Predicciones por fila archivadas con el mismo esquema que fase 6.

## Sección 9.3 — Comparación pareada QFS ↔ baseline de Fase 6

Para cada `(dataset, configuración QFS, modelo)`, comparar contra el baseline
correspondiente de fase 6 (mismo dataset y modelo, todas las features) reutilizando las
predicciones por fila archivadas. NO reentrenar baselines.

Aplicar el mismo protocolo estadístico de fase 6:
- Bootstrap 400 sobre la diferencia de macro-F1 → IC 95 %.
- Permutación de signos pareada sobre aciertos por fila (2 000) → p-valor.
- Permutación de etiquetas (500) sobre la configuración QFS → p-valor adicional.
- Corrección de multiplicidad FDR Benjamini–Hochberg y Holm sobre la familia de
  contrastes finales (un QFS por dataset).

## Sección 9.4 — Integración con la tabla maestra de Fase 7

Extender `results/tables/07_final_comparison/comparacion_final.csv` (o equivalente)
añadiendo una fila por dataset con la mejor configuración QFS (operativo) y otra con la
configuración oráculo. Mantener la regla de veredicto de fase 7:

- `mejora_significativa` si: delta positivo Y IC pareado excluye 0 Y p-FDR < 0.05 Y
  delta ≥ `UMBRAL_EFECTO_PRACTICO`.
- `empate_practico` si: estadísticamente significativo pero delta < umbral práctico.
- `equivalente` si: IC pareado incluye 0.
- `deterioro` si: delta negativo y p-FDR < 0.05.

## Sección 9.5 — Lectura por dataset (estructura canónica)

Replicar el patrón de fase 7 (`### Evidencia: <dataset>`) con una ficha por dataset que
incluya:
- Baseline de fase 6, mejor selección clásica de fase 6, QFS operativo, QFS oráculo.
- Métricas (macro-F1, balanced_accuracy, AUC si binario) e IC.
- Veredicto y lectura en prosa que conecte fases 1–7 con el resultado QFS.

## Sección 9.6 — Comparación con cifras publicadas

En los dos binarios del banco, presentar el AUC-ROC observado para QFS junto al de
fase 6 con XGBoost y comparar **cualitativamente** con las tablas de PAPER_QFS y
QFS_D2. Recordar la nota de `metodologia.tex` sobre el protocolo no reproducido al pie
de la letra (datasets ampliados, modelos extra), de modo que la comparación se lee como
contexto, no como reproducción.

## Sección 9.7 — Limitaciones específicas de la fase cuántica

Declarar honestamente:
- Simulación analógica (no hardware real); coherente con la implementación de
  referencia~`\cite{orquin2026}`.
- Pre-selección híbrida en bcw y madelon: declarado, decisión justificada en `8.1`.
- β implementado siguiendo QFS_D2 eq 14, pero el barrido cubre 11 valores discretos.
- Oráculo `Q*(α)` factible por enumeración hasta 20 variables; en datasets mayores
  (post pre-selección sigue siendo ≤20) el control de calidad es completo.

## Artefactos

- `results/tables/08_quantum/comparacion_qfs_vs_baseline.csv` (un veredicto por
  dataset, formato compatible con fase 7).
- `results/tables/08_quantum/contrastes_pareados_qfs.csv` (IC + p crudo + p-FDR + p-Holm
  + p-label-perm).
- `results/figures/08_quantum/fase9_resumen_evidencia_{dataset}.png` (figura por
  dataset).
- Actualización de `results/tables/07_final_comparison/comparacion_final.csv` con las
  filas QFS añadidas.

## Verificación

`scripts/verify_fase9_evaluacion.py`: comprobar que cada dataset tiene baseline +
clásico + QFS_operativo + QFS_oráculo, que los IC y p-valores están todos calculados,
y que la regla de veredicto se ha aplicado.

## Cierre

Tras esta fase, el TFG queda listo para reescribir `Plantilla_Latex_GCD/tfgs/tex/resultados.tex`
y `conclusiones.tex` con las cifras QFS reales. No tocar `metodologia.tex` ni los
capítulos 1–3 (cerrados y anclados en fuentes primarias).
