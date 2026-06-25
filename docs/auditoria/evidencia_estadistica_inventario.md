# Inventario de evidencia estadística previa (los "mini-boosts de confianza")

> 2026-06-14. Catálogo de los tests y validaciones de las fases 1-4 (y 5-6) que la memoria
> está opacando y que dan solidez a la base clásica. Cada uno responde a una objeción
> potencial ANTES de la comparación cuántica, de modo que el veredicto QFS se apoya en
> terreno auditado. Todos con cifra real localizada en su tabla.

## Por qué importa (la idea que articuló el usuario)

El TFG no va de datasets, ni de tests, ni de modelos. Pero una base clásica sólida y
auditada es lo que permite explicar el comportamiento cuántico con criterio y evidencia:
cada test previo cierra una pregunta del tipo "¿y cómo sé que...?" antes de que aparezca
QFS. Cuando QFS se deteriora en madelon, el lector ya sabe (por el FDR previo) que madelon
casi no tiene señal univariante: la base explica el resultado cuántico.

## Catálogo (qué prueba, cifra real, tabla, objeción que cierra)

### Fase 1 — el dato crudo tiene señal real
- **Señal supervisada sobrevive a multiplicidad.** bcw 27/30, churn 10/10, olive 10/10,
  **madelon 13/500** variables superan FDR 0.05. `fase1_asociacion_target_resumen.csv`.
  → cierra "¿la asociación no es azar de contrastes múltiples?". Y el 13/500 de madelon
  (efecto mediano 0.02) es la antesala del fallo de criterio de QFS.
- **No normalidad ⇒ no-paramétrico justificado.** % que rechaza normalidad alto (bcw
  100%). `fase1_normalidad_resumen.csv`. → cierra "¿por qué Mann-Whitney/Kruskal y no t?".
- **Magnitud del efecto, no solo significancia.** Cliff's δ / ε² / Cramér's V por
  variable. `fase1_tamano_efecto_resumen.csv`. → cierra "¿significativo = relevante?".
- **Redundancia ya presente en crudo.** Spearman por pares, VIF. `fase1_redundancia_*`,
  `fase1_correlaciones_spearman_pares.csv`. → antesala del término R_ij de QFS.

### Fase 3 — el preprocesado no distorsionó nada
- **Estructura de relevancia conservada casi perfecta.** Spearman de rankings raw vs
  processed: bcw 0.9996, churn 1.0, madelon 1.0, olive 0.988; ΔMI medio ~0.
  `fase3_asociacion_tests.csv`. → cierra "¿el preprocesado favoreció a algún método?".
- **Target intacto.** chi² p=1.0, Fisher p=1.0, Δentropía 0. `fase3_target_tests.csv`.
- **Redundancia conservada.** VIF y Cramér's V processed. `fase3_vif_processed.csv`,
  `fase3_cramers_v_categoricas.csv`.

### Fase 4 — las particiones son representativas y sin fuga
- **Particiones indistinguibles (sin sesgo de split).** Adversarial AUC ≈ 0.5 en los
  cinco: bcw 0.522, churn 0.516, madelon 0.476, olive3 0.513, olive9 0.535.
  `fase4_validacion_adversarial.csv`. → cierra "¿el split favorece al test?".
- **Sin proxy determinista del target (leakage).** AUC univariante y NMI por variable, con
  umbral 0.99. `fase4_leakage_screening.csv`. → cierra "¿hay fuga de información?".
- **Drift bajo control.** KS/Wasserstein/PSI por variable; max PSI por dataset (bcw 0.50).
  `fase4_drift_resumen.csv`, `fase4_drift_variables.csv`. → cierra "¿train y test miden lo
  mismo?".
- **Conservación de clases por split.** chi² de proporciones. `fase4_target_tests.csv`.

### Fase 5-6 — la selección y el modelado son fiables (ya parcialmente en memoria)
- Estabilidad Jaccard/Kuncheva (`fs_jaccard_stability.csv`), permutación del target
  (`fs_*permutation*`), redundancia interna (`fs_redundancy_*`).
- Bootstrap, permutación pareada y de etiquetas, FDR/Holm (`06_modeling/`).
- **Velocidad por método** (`fs_all_execution_times.csv`, `fit_seconds`) — opacada.
- **Perfil por método** coste/estabilidad/redundancia (`fs_method_profiles.csv`) — opacado.
- **SHAP** matrices crudas + beeswarm — opacado.

## Las cinco dimensiones que la memoria opaca (resumen unificado)

1. **Evidencia de validación previa** (este documento): señal real (FDR), no-normalidad,
   conservación del preprocesado, representatividad de splits, leakage, drift.
2. **Velocidad / coste computacional** (fase 5-6).
3. **Interpretabilidad / SHAP** (fase 6).
4. **Comportamiento por método** (relevancia/redundancia/combinado; alineación α/β/MI).
5. **Comportamiento de métricas** (macro-F1 vs balanced vs AUC).

Las cinco, juntas, convierten la memoria de "reporte de modelos" en "cadena de evidencia
auditada que culmina en un veredicto cuántico defendible".

## Uso

Este inventario alimenta el banco de preguntas (a construir tras la discusión con el
usuario): cada ítem aquí es una pregunta candidata con su tabla de origen ya localizada.
Relacionado con `preguntas_y_visualizaciones_memoria.md` y `cobertura_visual_memoria.md`.
