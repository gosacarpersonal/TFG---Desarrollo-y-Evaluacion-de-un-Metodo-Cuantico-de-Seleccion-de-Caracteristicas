# Correcciones Codex: QFS MDS verificado y Fase 10

Fecha: 2026-06-15.

Objetivo: alinear la ejecución QFS con el protocolo documentado y regenerar las fases 8, 9 y 10 sin reejecutar el pipeline clásico fases 1-7 ni editar la memoria `.tex`.

## Tabla de desviaciones y correcciones

| Desviación detectada | Evidencia `file:line` | Método documentado | Corrección aplicada | Cambio numérico observado |
|---|---|---|---|---|
| Fase8 usaba una ejecución MDS reducida (`QFS_MDS_RUNS=4`, `QFS_MDS_MAX_ITER=8` en el artefacto auditado), incompatible con el protocolo. | `docs/auditoria/protocolo_revision_fase10.md:92`; `Plantilla_Latex_GCD/tfgs/tex/metodologia.tex:269`; implementación canónica en `QFS_based_on_NA/QFS_Auxiliar_functions.py:88` y `QFS_based_on_NA/QFS_Auxiliar_functions.py:308`. | 100 inicializaciones independientes del MDS y solver con `mds_runs=100`, `mds_max_iter=100`. | `scripts/rebuild_fase8_notebook.py:96-97` fija `QFS_MDS_MAX_ITER = 100` y `QFS_MDS_RUNS = 100`; `scripts/rebuild_fase8_notebook.py:243-244` pasa esos valores a `QFS_NA_Solver`; `scripts/rebuild_fase8_notebook.py:317` guarda `qfs_embedding_error.csv`. Fase8 se reejecutó completa. | `results/tables/08_quantum/qfs_embedding_error.csv`: 55 filas, todas con `mds_runs=100`, `mds_max_iter=100`. Macro-F1 QFS-NA: BCW `0.950231 -> 0.937382`, Churn `0.921700 -> 0.969499`, Madelon `0.633317 -> 0.603223`, Olive3 `1.000000 -> 1.000000`, Olive9 `0.842406 -> 0.842406`. |
| Cada semilla de `n_mds_runs` podía ejecutar varias inicializaciones internas de scikit-learn por el valor por defecto de `MDS.n_init`, haciendo ambiguo el significado de "100 independent MDS runs". | `QFS_based_on_NA/QFS_Auxiliar_functions.py:327-331`. | N ejecuciones independientes deben corresponder a N semillas controladas del protocolo, no a `N * n_init` dependiente de versión. | `QFS_based_on_NA/QFS_Auxiliar_functions.py:331` fija `n_init=1` dentro del bucle de 100 semillas. | El artefacto nuevo queda reproducible como 100 semillas protocolarias. Errores medios por dataset en las 11 betas: BCW `0.229647`, Churn `0.220888`, Madelon `0.250488`, Olive3 `0.138229`, Olive9 `0.145162`. |
| Fase10 B9 recomputaba el embebido con un `NotebookMDS` local y parámetros no canónicos (`n_mds_runs=6`, `max_iter=14`). | Desviación inventariada en `docs/auditoria/protocolo_revision_fase10.md`; corrección actual en `scripts/fase10_visualizaciones_core.py:433` y `scripts/fase10_visualizaciones_core.py:499`. | Fase10 debe leer artefactos de `results/` y no sustituir el solver por una geometría de notebook. | Se eliminó el recomputo: B9 lee `results/tables/08_quantum/qfs_embedding_error.csv`, usa las posiciones guardadas por fase8 y escribe `results/tables/10_memoria_b9_embedding_error.csv`. | B9 canónico seleccionado: BCW beta `0.2`, error `0.231430`, p95 `0.631035`; Churn beta `0.3`, error `0.216884`, p95 `0.545040`; Madelon beta `0.5`, error `0.249641`, p95 `0.604020`; Olive3 beta `0.0`, error `0.124729`, p95 `0.399435`; Olive9 beta `0.4`, error `0.142625`, p95 `0.366250`. |
| B2 podía confundirse con la métrica de correlación absoluta de fase5/memoria. | `scripts/explor_mapa_metodos.py:74`; texto narrativo en fase10. | En el mapa de métodos, redundancia interna debe ser la media de `R_ij` de información mutua del handoff QFS, no correlación absoluta. | Etiqueta y subtítulo actualizados para declarar "redundancia interna (media `R_ij`, MI)". | No cambia selecciones ni métricas; cambia la interpretación de B2 y evita mezclar el espacio QFS con la métrica descriptiva de fase5. |
| Fase10 A/B8 tenía FDR de Olive hardcodeado en el núcleo narrativo. | `scripts/fase10_visualizaciones_core.py:161`; `scripts/fase10_visualizaciones_core.py:184`; `scripts/fase10_visualizaciones_core.py:590`. | Las visualizaciones de fase10 deben leer solo artefactos de `results/`. | Se lee `results/tables/01_raw_eda/fase1_fdr_resumen.csv` y se usa `significativas_fdr`. | No cambia resultados QFS; corrige trazabilidad del régimen del dato. |
| Riesgo de doble normalización de `I_i` y `R_ij`. | Handoff declara "sin normalización min-max" en `results/tables/05_feature_selection/fs_qfs_handoff_matrices_index.csv:2-6`; solver normaliza una vez en `QFS_based_on_NA/QFS_Auxiliar_functions.py:119` y `QFS_based_on_NA/QFS_Auxiliar_functions.py:124`; fase8 pasa `info["I_i"]` y `info["R_ij"]` crudos en `scripts/rebuild_fase8_notebook.py:235-236`. | Fase5 entrega MI cruda; fase8 no debe normalizar de nuevo; `QFS_NA_Solver` aplica `normalize_list/normalize_matrix` una sola vez. | Verificado. No se aplicó cambio funcional. | Control sin cambio numérico: no hay doble normalización en la ruta fase5 -> fase8 -> solver. |

## Resultados regenerados

Ejecuciones completadas sin error desde el entorno `qfs_env`:

- `notebooks/fase8.ipynb`: reejecutado completo con MDS verificado 100/100.
- `scripts/verify_fase8_ejecucion.py`: `OVERALL: PASS`.
- `scripts/verify_fase8_solver.py`: checks A-E `true`.
- `notebooks/fase9.ipynb`: reejecutado completo sobre fase8 nueva.
- `scripts/verify_fase9_evaluacion.py`: `OVERALL: PASS`.
- `scripts/build_diagnostico_atribucion.py`: regeneró `results/figures/10_memoria/diag_atribucion_qfs.png`.
- `scripts/fase10_visualizaciones_core.py` y `notebooks/fase10_visualizaciones.ipynb`: ejecutados sin error; regeneraron `docs/auditoria/hallazgos_fase10.md`.

Artefactos nuevos o actualizados:

- `results/tables/08_quantum/qfs_embedding_error.csv`
- `results/tables/10_memoria_b9_embedding_error.csv`
- `results/tables/08_quantum/qfs_operational_summary.csv`
- `results/tables/08_quantum/qfs_selected_all.csv`
- `results/tables/08_quantum/qfs_quality_control_*.csv`
- `results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv`
- `results/figures/10_memoria/*.png`
- copia PNG en `Plantilla_Latex_GCD/tfgs/figs/`

## Diagnóstico tras corrección

| Dataset | Régimen | Baseline macro-F1 | Oracle Mücke macro-F1 | QFS-NA macro-F1 | Pérdida criterio | Pérdida optimizador | Coste NA - oracle a α=0.5 | Error embebido B9 | Lectura |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Breast Cancer Wisconsin | baja dimensión, señal robusta | `0.937382` | `0.937382` | `0.937382` | `0.000000` | `0.000000` | `-1.269918` | `0.231430` | Equivalente; la corrección elimina la mejora espuria anterior, pero conserva equivalencia. |
| Customer Churn | mixto con one-hot y redundancia estructurada | `0.999815` | `0.999138` | `0.969499` | `0.000677` | `0.029638` | `+0.622080` | `0.216884` | Sigue siendo fallo de optimizador, aunque mucho menos extremo que con MDS 4/8. La hipótesis one-hot no se afirma como causa única: el error de embebido no es anómalamente alto frente a BCW/Madelon. |
| Madelon | alta dimensión con señal sintética dispersa | `0.813034` | `0.643298` | `0.603223` | `0.169737` | `0.040075` | `-0.059045` | `0.249641` | Sigue siendo fallo de criterio: incluso el óptimo exacto bajo el criterio QFS queda lejos del baseline. El coste NA no explica el deterioro principal. |
| Olive Oil 3-class | baja dimensión, señal fuerte | `1.000000` | `1.000000` | `1.000000` | `0.000000` | `0.000000` | `-0.164796` | `0.124729` | Equivalente; régimen favorable y geometría con menor error. |
| Olive Oil 9-class | n pequeño/desbalanceado | `0.838732` | `0.905955` | `0.842406` | `-0.067223` | `0.063549` | `+0.902885` | `0.142625` | Inconcluso por n=86: oracle mejora, NA queda equivalente al baseline. |

## Cambios relevantes frente al artefacto MDS 4/8

| Dataset/configuración | Macro-F1 QFS antes | Macro-F1 QFS ahora | Δ del cambio | Veredicto ahora |
|---|---:|---:|---:|---|
| BCW QFS-NA | `0.950231` | `0.937382` | `-0.012850` | equivalente |
| BCW oracle | `0.937382` | `0.937382` | `0.000000` | equivalente |
| Churn QFS-NA | `0.921700` | `0.969499` | `+0.047799` | deterioro |
| Churn oracle | `0.999138` | `0.999138` | `0.000000` | deterioro leve |
| Madelon QFS-NA | `0.633317` | `0.603223` | `-0.030094` | deterioro |
| Madelon oracle | `0.643298` | `0.643298` | `0.000000` | deterioro |
| Olive3 QFS-NA | `1.000000` | `1.000000` | `0.000000` | equivalente |
| Olive9 QFS-NA | `0.842406` | `0.842406` | `0.000000` | equivalente |

La corrección cambia magnitudes, no el veredicto central. Churn deja de parecer un fallo extremo de geometría/optimizador y pasa a un deterioro menor pero todavía atribuible principalmente al optimizador. Madelon queda más claramente como fallo del criterio: el oracle exacto también deteriora de forma grande respecto al baseline.

## Resumen en 10 líneas

1. Se corrigió fase8 para ejecutar QFS con MDS verificado `100 x 100`.
2. Se fijó `MDS(n_init=1)` para que 100 semillas signifiquen 100 inicializaciones independientes.
3. Se guardó el embebido real del solver en `qfs_embedding_error.csv`.
4. Se eliminó de fase10 B9 el MDS local no canónico y ahora lee el artefacto de fase8.
5. Se corrigió B2 para declarar redundancia interna como media `R_ij` de MI.
6. Se sustituyó el FDR hardcodeado por lectura desde `fase1_fdr_resumen`.
7. Se verificó que no hay doble normalización entre fase5 y fase8.
8. Fase8, fase9 y fase10 se ejecutaron completas sin errores y con verificadores en PASS.
9. El diagnóstico se mantiene: Madelon es fallo de criterio; Churn es fallo de optimizador; BCW y Olive3 son equivalentes; Olive9 sigue inconcluso.
10. Queda abierto solo interpretar en memoria el mecanismo fino de Churn: la causa one-hot sigue siendo hipótesis, no conclusión cerrada.
