# Preguntas de la memoria y visualizaciones que las responden

> 2026-06-14. Invierte el flujo: primero QUÉ debe demostrar/responder la memoria, luego
> QUÉ composición visual lo responde y DE QUÉ TABLA sale. Metodología: la ruta obligatoria
> del skill `.agents/viz-definitive` (`pregunta → forma del dato → intención → métrica
> derivada → restricción científica → familia → composición → caveat → render`). Principio:
> una figura solo entra si responde una pregunta; mejor quitar que pulir de más.

---

## Parte 1 — Auditoría: ¿está la memoria escrita para un humano o para un agente?

Igual que pasó con los notebooks (de "para IA" a "para humano"), la memoria arrastra dos
problemas, ambos confirmados con medición sobre los `.tex`.

### 1.1 Escritura para-agente (tells a depurar)

Menciones a rutas/ficheros/internals que un lector de la memoria NO necesita:
`apendice.tex` 25, `metodologia.tex` 22, `resultados.tex` 15. Patrones:
- Nombres de CSV y rutas `results/...` dentro del cuerpo ("se materializa en
  `fs_qfs_handoff_*.csv`", "una tabla por experimento en `experiments_validation`").
- Lenguaje de directorio ("subdirectorios numerados", "núcleo limpio", `nbconvert`).
- Marcadores de tarea para agente: este problema estaba presente en versiones
  previas (`PENDIENTE_RESULTADOS`), pero ya fue retirado de `resultados.tex`.
- Explicar el andamiaje (qué contiene cada carpeta) en lugar de la ciencia.

**Criterio de arreglo:** la trazabilidad a artefactos es legítima, pero va en el apéndice
de reproducibilidad de forma compacta, no salpicada por resultados/metodología. El cuerpo
habla de evidencia y decisiones, no de nombres de fichero. Un lector que solo tiene el PDF
debe entenderlo todo sin ver el repositorio.

### 1.2 Opacidad: la memoria reducía 9 fases a "resultados de modelos"

Cobertura medida en `resultados.tex` (nº de menciones):

| Dimensión | ¿Cubierta? | Dato disponible (no usado) |
|---|---|---|
| Rendimiento (macro-F1) y redundancia | Sí (19/12) | — |
| Estabilidad (Jaccard/Kuncheva) | Sí (12/4) | — |
| **Velocidad / coste computacional** | **No (0)** | `fs_all_execution_times.csv`, `fit_seconds` (fase 6) |
| **Interpretabilidad / SHAP** | **No (0)** | matrices SHAP crudas + beeswarm (fase 6) |
| **Comportamiento por método** (relevancia vs redundancia vs combinado; alineación con α/β/MI) | **No (f_classif/mutual_info = 0)** | `fs_method_profiles.csv`, `fs_all_rankings.csv`, handoff `I_i`/`R_ij` |
| Comportamiento de métricas | Parcial (solo macro-F1) | AUC contexto, balanced accuracy, por clase |

Las fases 1-9 se hicieron de principio a fin, con tests, tiempos, estabilidad,
permutaciones, redundancia, interpretabilidad, handoff diseñado, ejecución QFS y
control frente al óptimo exacto. La memoria debía contar algo más que el final
(modelos): debía explicar *por qué* la base clásica es robusta y *cómo* se
comporta QFS más allá del macro-F1. Cerrar esto fue el objetivo de la Parte 2.

---

## Parte 2 — Preguntas → composición visual → tabla de origen

Agrupadas por lo que el TFG debe demostrar. Cada entrada: **Pregunta** · *intención* ·
**familia/composición** · `tabla de origen` · caveat. (★ = hueco actual; ✓ = ya en memoria.)

### A. ¿Es fiable y diversa la base experimental? (fases 1-4)

- **A1. ¿Cubren los datasets regímenes distintos (tamaño, dimensión, desbalance)?**
  *situar el banco* · small multiples o burbuja (filas × variables, color = desbalance,
  forma = nº clases) · `results/tables/01_raw_eda/` (estructura + desbalance) · ★ hoy solo
  se muestra estructura de filas; falta la lectura conjunta y el desbalance.
- **A2. ¿El preprocesado conservó la señal?** *antes/después* · dumbbell o slope por
  dataset (asociación/redundancia raw vs processed) · `03_postprocessing_audit/*conservacion*`
  · ★ afirmado, no mostrado → apéndice.
- **A3. ¿Son representativas las particiones (sin drift ni leakage)?** *control* · small
  multiples de drift (KS/Wasserstein/PSI) + AUC adversarial · `04_split_audit/` · drift ★
  (texto cita cifras sin figura); adversarial ✓.

### B. ¿Por qué la base clásica es robusta y ayuda tanto? (fases 5-7)

- **B1. ¿Cómo se comportan los 12 métodos y cómo se agrupan por ingrediente?**
  *taxonomía operativa* · figura compuesta: roster por dataset + perfil método (coste,
  estabilidad, redundancia) coloreado por familia (relevancia/redundancia/combinado/
  wrapper/embedded) · `fs_all_rankings.csv`, `fs_method_profiles.csv` · ★ el resultado
  nuclear de fase 5 no se muestra.
- **B2. ¿Es estable la selección entre semillas?** *fiabilidad* · heatmap Jaccard ·
  `fs_jaccard_stability.csv` · ✓.
- **B3. ¿Qué métodos controlan la redundancia?** *diferenciador* · dot/dumbbell delta
  redundancia con base 0 · `fs_redundancy_delta` · ✓.
- **B4. ¿La señal supera al azar?** *honestidad* · heatmap real vs nulo · permutación · ✓.
- **B5. ¿Cuánto cuesta cada método (velocidad)?** *coste* · barras horizontales de tiempo
  por método (escala log si procede), o tiempo vs estabilidad · `fs_all_execution_times.csv`
  · ★ dimensión velocidad ausente.
- **B6. ¿La reducción mantiene o mejora el rendimiento por dimensión?** *propuesta de
  valor* · scatter coste(nº vars) vs macro-F1, con frontera · `06_modeling/...cost...` ·
  ★ visualiza el argumento central; no está.
- **B7. ¿Qué variables sostienen cada modelo (interpretabilidad)?** *explicabilidad* ·
  F6 muestra SHAP por instancia en Breast Cancer, Customer Churn y Madelon, y barras de
  importancia media para Olive; queda como mejora opcional sustituir/acompañar con beeswarm
  editorial completo · matrices SHAP crudas · ✓ mostrado, con margen de elevación visual.

### C. ¿Cómo se comporta QFS y cómo se compara? (fases 8-9)

- **C1. ¿QFS iguala/supera a los mejores clásicos?** *veredicto* · figura de comparación
  QFS-NA/oráculo/baseline/mejor-clásico por dataset (dumbbell o barras con IC) ·
  `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` · ✓ figura insertada como
  F10; debe leerse junto a F9, no como ranking simple.
- **C2. ¿Optimiza bien el simulador su propio criterio? (criterio vs optimizador)** *el
  hallazgo central* · plano de atribución del deterioro en macro-F1, separando madelon
  (criterio falla) de churn (optimizador falla); Hamming + Δcoste quedan como tabla de
  control · `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` · ✓ figura central
  insertada como `diag_atribucion_qfs.png`.
- **C3. ¿Cómo modula β la selección?** *grado de libertad* · mapa β×variable (densidad
  Rydberg) · `qfs_runs_*_*.csv` · ✓ (solo madelon; añadir olive_9 donde el oráculo ayuda).
- **C4. ¿Consume QFS las mismas cantidades que los clásicos (I_i, R_ij)?** *trazabilidad
  del handoff* · heatmap R_ij + barras I_i por dataset · handoff `fs_qfs_handoff_*` · ★
  refuerza "misma entrada, distinta optimización".
- **C5. ¿Coincide la selección de QFS con la de los clásicos?** *atribución* · matriz de
  solape (UpSet/heatmap) variables QFS vs Boruta/mRMR · `qfs_selected_*` + selección
  clásica · ★ ayuda a leer por qué gana/pierde.

### D. Transversal — disciplina estadística y métricas

- **D1. ¿Significancia vs magnitud?** *prudencia* · ya cubierto en tablas (churn); una
  nota visual de IC pareados podría reforzarlo · `fase7_tabla_maestra` · opcional.
- **D2. ¿Cómo se comportan las métricas (macro-F1 vs balanced acc vs AUC en binarios)?**
  *elección de métrica* · pequeña tabla/figura comparando métricas en los binarios ·
  `qfs_auc_binarios_contexto.csv` + test results · ★ justifica visualmente la elección.

---

## Síntesis: el salto de cobertura

La memoria pasa de contar **rendimiento + redundancia + estabilidad** a contar la historia
completa de la base clásica y de QFS: **velocidad, interpretabilidad, comportamiento por
método (α/β/MI), métricas y el diagnóstico criterio-vs-optimizador**. Eso responde a "por
qué la base clásica es tan robusta" y "qué hace QFS realmente", no solo "quién gana en
macro-F1".

Conjunto objetivo de figuras (orden de prioridad): B7 SHAP, C1 comparación QFS, B1 roster,
A3 drift, B6 coste-rendimiento, B5 velocidad, C2 criterio-vs-optimizador, A1 banco,
C4 handoff. El resto (A2, C3 extra, C5, D) a apéndice o según espacio.

## Decisiones que requieren al usuario (antes de construir)

1. **Validar/editar el conjunto de preguntas** (A1-D2): ¿alguna sobra o falta?
2. ¿Qué preguntas se responden en el **cuerpo** y cuáles en **apéndice**?
3. ¿Reescribimos primero el cuerpo de resultados para que cada figura responda a su
   pregunta (de-opacando 1-7 y quitando los tells para-agente), y después construimos el
   notebook espejo apuntando a ese conjunto final?

## Notas de implementación

- Construir cada figura con la ruta de `viz-definitive` (Tier 2 para las de cuerpo).
- Reusar plotters de `src/` donde existan; crear nuevos solo para los huecos (velocidad,
  coste-rendimiento, comparación QFS, criterio-vs-optimizador, handoff, solape).
- Toda figura sale de una tabla real; ninguna cifra se inventa (regla del skill).
