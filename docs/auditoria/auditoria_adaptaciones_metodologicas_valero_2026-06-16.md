# Auditoría de adaptaciones metodológicas defendibles

Fecha: 2026-06-16.

Objetivo: revisar decisiones del TFG que podrían parecer arbitrarias si no se
definen antes de usarse, siguiendo el patrón de la revisión de Valero: objetivo
claro, datos claros, métricas claras, experimentos reproducibles y cautelas
metodológicas explícitas.

## Criterio de revisión

Una decisión se considera defendida si cumple tres condiciones:

1. se declara en metodología antes de aparecer en resultados;
2. se distingue si procede del paper, del protocolo clásico o de una adaptación
   operativa propia;
3. se audita con artefactos trazables y no se usa como explicación causal sin
   evidencia.

## Casos revisados

| Decisión | Riesgo tipo Valero | Estado tras revisión | Evidencia principal |
|---|---|---|---|
| Relajación geométrica de QFS-NA (`1/sqrt(2)` a `0.45/0.35/0.25`) | Que parezca un ajuste ad hoc para que el método funcione. | Reforzado. Metodología declara la razón de factibilidad, la lista predeclarada y que el valor no se optimiza en test. Resultados explican que todas las configuraciones finales aceptan `0.45` y que la geometría se contrasta con error MDS. | `metodologia.tex`, sección QFS; `resultados.tex`, evaluación QFS; `results/tables/08_quantum/qfs_embedding_error.csv`. |
| Término `beta` en la distancia atómica | Que se presente como reproducción literal del paper si es una variante operativa. | Reforzado. Se separa el mapeo base `R_ij^{-1/6}` del término añadido `beta(1+I_i)(1+I_j)` y se define `beta` como grado experimental, no nueva magnitud física. | `metodologia.tex`, ecuación `eq:qfs-distancia-beta`; `qfs_runs_*`; figura F8. |
| `alpha` del oráculo frente a QFS-NA operativo | Confundir el óptimo exacto clásico con salida del simulador analógico. | Reforzado. El contrato aclara que QFS-NA fija `alpha=0.5` y elige `beta` por validación con `random_forest` como evaluador fijo; el recorrido de `alpha` pertenece al oráculo exacto. | `metodologia.tex`, contrato de evaluación; `resultados.tex`, F8/F9. |
| Codificación `one-hot` de Customer Churn | Que parezca inconsistencia frente al paper o causa no probada del deterioro. | Ya estaba defendido y se mantiene. Se declara como divergencia frente a `label encoding`, se explica que transforma 10 predictoras crudas en 15 columnas QFS y se descarta como causa geométrica demostrada mediante error MDS. | `metodologia.tex`, datos y envolvente QFS; `resultados.tex`, regímenes y MDS; `conclusiones.tex`. |
| Preselección híbrida en Breast Cancer y Madelon | Que parezca que QFS no opera sobre el problema completo. | Defendido. Se explica como consecuencia de la envolvente de simulación; se ajusta solo con entrenamiento usando `mrmr_approx_k20`; se declara parte del método híbrido. | `metodologia.tex`, contrato QFS; `resultados.tex`, evaluación QFS; `qfs_preselection_summary.csv`. |
| Macro-F1 como métrica primaria frente a AUC del paper | Que se acuse de cambiar métrica para favorecer resultados. | Defendido. La memoria justifica macro-F1 por banco multiclase/desbalanceado y conserva AUC-ROC solo como contexto en binarios. | `metodologia.tex`, protocolo de modelado; `resultados.tex`, lectura AUC-contexto; apéndice. |
| Inclusión de XGBoost | Que parezca introducir un modelo para cambiar el baseline. | Defendido. Se explica como puente con el paper QFS y como baseline fuerte en alta dimensionalidad; resultados muestran cómo reduce la mejora clásica de Madelon sin eliminarla. | `metodologia.tex`, modelos; `resultados.tex`, modelado clásico; `conclusiones.tex`. |
| Umbral práctico de `0.01` macro-F1 | Que el veredicto no esté definido matemáticamente antes de resultados. | Defendido. La regla exige delta positivo, IC que excluya cero, p ajustado y efecto práctico mínimo. | `resultados.tex`, tabla clásica; `metodologia.tex`, evaluación estadística. |
| Robustez y semillas | Que se afirme robustez no ejecutada. | Defendido y reforzado. La memoria distingue estabilidad de selección, bootstrap/permutaciones de modelado y QFS con 100 inicializaciones MDS; no afirma multi-semilla completo de fase 8-9. | `resultados.tex`, consistencia; `conclusiones.tex`, limitaciones. |
| Boruta con tamaño natural frente a presupuesto `k` fijo | Que parezca comparación desigual. | Defendido. Se explica que Boruta confirma variables relevantes sin `k` prefijado; el resto de selectores sí se evalúa por escalera de presupuestos. | `metodologia.tex`, métodos clásicos; `resultados.tex`, comparación clásica. |
| `variance` como selector mínimo | Que el notebook diga "varianza cruda" aunque el método se calcula después del escalado. | Corregido. La narrativa ya decía que se calcula sobre datos estandarizados; se actualizó el registro técnico y el notebook ejecutado a "varianza tras escalado". | `src/fase5_feature_selection.py`; `notebooks/fase5.ipynb`; `scripts/rebuild_fase5_notebook.py`. |
| Lenguaje de Fase 8 sobre MDS | Que "MDS canónico" sugiera reproducción literal del paper o invisibilice la relajación geométrica. | Corregido. El notebook y su script generador hablan de MDS verificado del solver y de adaptación operativa trazada. | `scripts/rebuild_fase8_notebook.py`; `notebooks/fase8.ipynb`; `qfs_embedding_error.csv`. |

## Cambios aplicados en esta revisión

- Se reescribió la codificación física de QFS para separar el mapeo base del
  paper y la variante operativa con `beta`.
- Se añadió una explicación explícita de la relajación geométrica: motivo,
  lista predeclarada, valor final `0.45R_b` y uso como condición de factibilidad,
  no como optimización en test.
- Se corrigió el contrato de evaluación: `beta` se elige por validación en
  QFS-NA usando `random_forest` como evaluador fijo; `alpha` se recorre en el
  oráculo exacto.
- Se sustituyeron expresiones potencialmente ambiguas como "canónico" por
  "verificado" o "ejecución final trazada" cuando podían confundirse con una
  reproducción literal del paper.
- Se corrigió la etiqueta técnica de `variance`, que aparecía como "varianza
  cruda" aunque el pipeline usa los datos transformados por el preprocesador.
- Se reforzaron conclusiones para declarar que QFS conserva el núcleo del
  método de referencia, pero incorpora adaptaciones operativas trazadas.

## Lectura final

La memoria ya no debe vender la fase QFS como una reproducción literal del
paper. La defensa correcta es:

> Se implementa el núcleo QFS de relevancia-redundancia y embebido atómico, se
> compara contra un oráculo exacto del QUBO y se evalúa una variante operativa
> trazada del simulador neutral-atom. Las adaptaciones necesarias para el banco
> propio se declaran antes de resultados y se auditan con artefactos.
