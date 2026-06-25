# src Directory Summary

## Purpose
Lógica reutilizable del bloque pre-cuántico. Los notebooks de las fases 5, 6 y 7
orquestan estos módulos; las fases 1-4 son autocontenidas en sus notebooks
(generados por `scripts/rebuild_fase*_notebook.py`).

## File Map
* `fase5_feature_selection.py`: Fase 5 por etapas (`cargar_bundles`, `etapa_*`,
  `guardar_artefactos`, `run_phase5`): selectores clásicos train-only, estabilidad
  Jaccard/Kuncheva, permutaciones del target, redundancia, cruce con EDA,
  datasets reducidos y handoff a Fase 6.
* `phase6_modeling/pipeline.py`: Fase 6 (`run_phase6` y funciones por sección):
  auditoría de entradas, parrilla experimental, validación, candidatos, test con
  bootstrap, contrastes pareados y de permutación, importancias e informes.
* `fase7_evidencia.py`: Fase 7: inventario de artefactos 1-6, tabla maestra,
  validación de completitud, comparación final con veredicto, síntesis
  estabilidad-redundancia-rendimiento, handoff QFS y figuras de cierre.
* `viz_core/`: capa visual Editorial Warmth (referenciada por las skills de
  visualización).

## Key Dependencies
* pandas, numpy, scipy, scikit-learn, matplotlib, seaborn (entorno conda `qfs_env`).
