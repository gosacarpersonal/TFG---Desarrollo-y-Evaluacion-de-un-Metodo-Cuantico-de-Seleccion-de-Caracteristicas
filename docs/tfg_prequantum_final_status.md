# Estado final del bloque pre-cuántico (2026-06-11)

Cierre de las Fases 1-7 del TFG "Desarrollo y evaluación de un método cuántico de
selección de características". Detalle de cambios en `docs/tfg_prequantum_worklog.md`.

## Validación final

- **Ejecución limpia completa**: los 7 notebooks (`notebooks/fase1.ipynb` … `fase7.ipynb`)
  ejecutados en orden desde kernel limpio con `jupyter nbconvert --execute` (entorno
  `qfs_env`): 0 errores, 0 celdas sin ejecutar, sin volcados de texto masivos
  (~4,5 min en total).
- **Memoria LaTeX compilada**: `Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf`
  (tectonic; pdflatex del sistema no disponible). 10 referencias bibliográficas
  resueltas; capítulos de introducción, materiales y métodos, resultados y
  discusión, conclusiones y apéndice de reproducibilidad redactados a mano y
  respaldados por artefactos. Páginas clave revisadas visualmente.
- **Coherencia notebooks ↔ memoria**: las cifras citadas en observaciones y en la
  memoria coinciden con los artefactos de la ejecución final (comprobado tras la
  reejecución completa).

## Resultado científico del bloque

| Dataset | Baseline (vars / F1 test) | Mejor selección (método, vars / F1) | Veredicto |
|---|---|---|---|
| breast_cancer_wisconsin | 30 / 0.937 | mRMR k10 / 0.950 | equivalente |
| customer_churn | 10 / 0.991 | mRMR k10 / 0.997 | equivalente (empate práctico) |
| madelon | 500 / 0.613 | f_classif k10 / 0.850 | **mejora significativa** (+0.237, IC [0.18,0.30], p=0.021) |
| olive_oil_3class | 8 / 1.000 | random_forest k5 / 1.000 | equivalente |
| olive_oil_9class | 8 / 0.839 | mutual_info k5 / 0.855 | equivalente (n_test=86) |

Los 15 candidatos superan el test de permutación de etiquetas (p=0.002). Referencia
operativa para la fase cuántica en `results/tables/07_final_comparison/fase7_handoff_qfs.csv`.

## Estructura entregada

- `notebooks/fase1-7.ipynb`: narrativos, ejecutados, con tests/métricas explicados
  e interpretados por dataset, parámetros justificados y Olive Oil separado en
  `olive_oil_3class` / `olive_oil_9class` desde la Fase 2.3 en adelante.
- `src/`: `fase5_feature_selection.py` (etapas), `phase6_modeling/pipeline.py`,
  `fase7_evidencia.py`, `viz_core/`.
- `scripts/rebuild_fase{1..7}_notebook.py`: generadores de los notebooks (fuente de verdad).
- `results/`: tablas, figuras, informes y logs por fase (todo regenerado en la
  ejecución final); `data/splits` y `data/selected_features` con las 5 formulaciones.
- `Plantilla_Latex_GCD/tfgs/`: memoria pre-cuántica compilable (`tectonic ejemplo-memoria.tex`).

## Correcciones de fondo aplicadas en esta sesión

1. Fase 5 y Fase 6 referenciaban tablas de fases anteriores que ya no existían → recableadas.
2. El cruce selección-EDA emparejaba por primer token del nombre (cobertura sin sentido) → prefijo más largo.
3. El k de referencia de Olive Oil era 8 = espacio completo (selección trivial) → 5.
4. **El baseline de Fase 6 entrenaba con `original_index` como predictora** → excluida.
5. Los pipelines sobrescribían .tex dentro de la plantilla → desacoplado.
6. `tfg.cls`: opción `[pdftex]` eliminada (autodetección de driver).

## Limpieza realizada

Eliminados: `prompts_raw/` (duplicado de `promtps_raw/`), `notebooks/results/`
(árbol vacío extraviado), `__pycache__`/checkpoints, intermedios LaTeX, 6 .tex
autogenerados huérfanos de la plantilla, 9 módulos `src/` muertos de generaciones
anteriores y los informes de auditoría de sesiones antiguas con cifras obsoletas
(`results/reports/01_raw_eda/` completo y restos en 02 y 05).

## Pendiente / fuera de alcance de este bloque

- Fase cuántica (QFS sobre `QFS_based_on_NA/`) y su comparación contra el handoff.
- El resumen de la memoria contiene un `TODO_EVIDENCIA` para incorporar los
  resultados cuánticos cuando existan.
- `pdflatex` nativo no está instalado en el sistema; la memoria compila con
  `tectonic` (instalado en `qfs_env`). El `.cls` es compatible con ambos.
- Limitaciones metodológicas declaradas en memoria y notebooks: partición única
  (sin CV anidada), hiperparámetros fijos, test pequeño en Olive Oil, resoluciones
  de contrastes acotadas por coste.
