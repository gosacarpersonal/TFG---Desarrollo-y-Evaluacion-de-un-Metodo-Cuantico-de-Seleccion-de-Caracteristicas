# Auditoría visual de figuras de la memoria — 2026-06-21

Revisión figura a figura **viendo el render real** (no infiriendo), sobre las
figuras efectivamente compiladas en `ejemplo-memoria.tex`. Objetivo: separar
percepción ("son lamentables") de defecto concreto y accionable.

## Veredicto global

La calidad **no es uniforme y no es mala en bloque**. Es bimodal:

- **Cuerpo (serie `F##.pdf`): de aceptable a excelente.** Varias figuras se
  rediseñaron desde borradores flojos (la serie minúscula `f#.png` es el
  borrador viejo, no lo compilado). F09 y `qfs_organismo_cuantico` son de
  nivel sobresaliente para un TFG.
- **Apéndice (series `a#`, `ev#`, `f10_b#`): aquí viven los defectos reales.**

El problema de fondo **no es estética difusa**: es **un antipatrón recurrente y
nombrable** + fallos de pulido puntuales. Eso es bueno: es corregible de forma
sistemática.

## Antipatrón principal: heatmap aplicado a datos casi-constantes / casi-vacíos / de 2 filas

Un heatmap solo comunica si hay **variación 2D que leer por color**. Cuando la
matriz es casi uniforme, está medio vacía, o tiene 2 filas estiradas a todo el
ancho, el resultado parece roto y desperdicia tinta. Casos:

| Figura | Dónde | Problema | Arreglo propuesto |
|---|---|---|---|
| `a1_permutacion_senal_nulo` | Apéndice | Heatmap de **2 filas** (f_classif, mutual_info) × 5 datasets estirado a página completa; color casi uniforme | Tabla compacta o barras agrupadas |
| `a3_roster_completo` | Apéndice | Heatmap casi constante por columna (249/105/456/48/48 repetido); el color no aporta info salvo boruta/rfe | Tabla, o barras destacando solo boruta/rfe |
| `a5_panorama_deltas` | Apéndice | Heatmap **mayoritariamente vacío** (la mayoría de celdas en blanco) | Dot plot de deltas por dataset |
| `f4`→`F04` panel D (viejo) | — | Ya corregido en el finalista: pasó de heatmap 2 filas a dot plot de 12 métodos | (resuelto, sirve de patrón a replicar) |

> **Patrón a replicar:** F04 ya demuestra el arreglo correcto (heatmap roto →
> dot plot). Aplicar el mismo criterio a a1/a3/a5.

## Antipatrón secundario: small-multiples ilegibles

| Figura | Problema | Arreglo |
|---|---|---|
| `ev6_rendimiento_vs_k` | 5 paneles en tira muy ancha y baja; fuentes diminutas; escalas Y dispares (Olive3 0.990–1.000 vs Madelon 0.53–0.56) que impiden comparar | Subir altura, normalizar/anotar escalas, fuente mayor |

## Fallos de pulido en figuras por lo demás buenas

| Figura | Defecto | Severidad |
|---|---|---|
| `F04_perfil_selectores` | Etiquetas Y de dos palabras ("f classif", "mutual info") se parten y **colisionan con la fila vecina** en los 4 paneles | Media |
| `F09_atribucion...` | En el origen, "Olive 3" y "Breast Cancer" se **solapan** ("Oliv eBCancer") | Baja |

## Figuras confirmadas BIEN (no tocar)

- `F01`, `F02`, `F03` (banda verde de referencia), `F07`, `F08` (rediseñada 4→2 paneles)
- `F06` (SHAP beeswarm, aceptable)
- **`F09`** — plano de atribución por cuadrantes con anotaciones dirigidas: excelente
- **`qfs_organismo_cuantico`** — embebido atómico MDS con colormap de densidad Rydberg: excelente
- `ev5_evolucion_adiabatica` (metodología), `a6_handoff_ir`, `a7_coste_cuantico`

## Inventario completado (resto de figuras)

- `f10_a_regimenes_dataset`: 4 paneles de barras; aceptable, pero cobertura de
  datasets **inconsistente entre paneles** (VIF/PCA solo muestran 3 de 5).
- `f10_b10_consistencia`: dot plot de los 12 selectores; **bien**, campo completo.
- `a2_leakage`: scatter limpio; **bien**.
- `a4_shap_concordancia`: heatmap **bien aplicado** (variación 2D real por clase).
- `ev7_cierre_narrativo`: slope chart baseline→QFS→oráculo; bueno, **pero duplica
  el mensaje de F10 y F09** (ver redundancia abajo).
- `ev8_scorecard_evidencia`: scorecard dataset × cadena de evidencia; **excelente
  síntesis**.
- `f10_b5_beta_geometria`, `f10_b9_atomos_mds_error`, `ev4`: pendientes menores,
  no críticas para el hallazgo central.

---

# HALLAZGO CENTRAL: el campo de comparación está colapsado

Este es el problema más grave, por encima de cualquier defecto estético. Lo
detonó la observación de que "no sirve mostrar métricas buenísimas si no se
comparan contra **todos** los competidores, no solo contra el segundo mejor".

## El patrón, confirmado en TODO el inventario

**Ninguna figura compara el rendimiento final de QFS (macro-F1) contra la
distribución de los 12 selectores clásicos.** Todas las comparaciones de
*rendimiento* colapsan el campo a una de estas tres referencias:

- `baseline` (todas las variables)
- `mejor clásico` (un único ganador, los otros 11 desaparecen)
- `oráculo` (óptimo exacto del QUBO)

Evidencia por figura:

| Figura | Qué compara | Competidores mostrados |
|---|---|---|
| `F10` / `ev7` | macro-F1 final | baseline, **mejor** clásico, QFS, oráculo |
| `F09` | atribución criterio/optim. | baseline, QFS, oráculo |
| `a9` | F1 vs AUC | baseline, QFS, oráculo |
| `ev8` (scorecard) | "Selección vs **baseline**" | solo baseline |
| `tab:candidatos` (apénd.) | test | mejor baseline + **2** mejores subconj. |

## Las vistas que SÍ usan los 12 selectores nunca son de rendimiento

El campo completo (12 métodos) solo aparece en ejes **secundarios**:

| Figura | Eje (los 12 métodos, pero NO rendimiento) |
|---|---|
| `f10_b2` | solape Jaccard |
| `explor_mapa`, `a8` | similitud a mRMR/correlación/Boruta |
| `F04` | redundancia, coste, estabilidad |
| `f10_b10` | estabilidad entre semillas |
| `o1`, `f5` | consenso / redundancia vs k |

## Por qué esto es un problema de defendibilidad (no estético)

Cuando afirmas "QFS empata al mejor clásico", el lector **no puede situar a QFS
en el campo**: ¿está en la mediana de los 12, en el cuartil superior, o solo
gana a un ganador puntualmente flojo? Falta la figura que un tribunal pediría:
**macro-F1 de QFS contra la nube/caja de los 12 selectores clásicos, por
dataset** (box/strip plot con QFS resaltado). Y la figura que más se acercaba a
ese papel —`a5_panorama_deltas`, deltas de todos los selectores— es justo una de
las **rotas** (heatmap medio vacío). El defecto visual y el defecto de
comparación son, en ese caso, el mismo agujero.

## Defectos adicionales detectados al completar el inventario

- **`a8`**: la leyenda incluye "Boruta" pero **no hay ninguna barra de Boruta
  visible** (dato ausente/cero sin anotar) → figura aparentemente rota.
- **`a9`**: colisión de etiquetas ("Customer"/"Breast" superpuestas).
- **Redundancia narrativa**: `F10`, `F09` y `ev7` cuentan esencialmente la misma
  historia baseline→QFS→oráculo con tres formatos distintos. Conviene decidir
  cuál es la canónica del cuerpo y degradar las otras o diferenciarlas.

---

---

# EL COLAPSO ES SISTEMÁTICO EN TODOS LOS EJES (verificado en `results/tables/`)

El problema no se limita a los 12 selectores: la memoria colapsa al ganador en
**cada eje del diseño experimental**. La rejilla completa existe y está intacta;
solo que casi nada de ella es visible. Cuantificación:

| Eje | Granularidad real en `results/tables/` | Lo que se muestra en la memoria |
|---|---|---|
| Validación (rejilla completa) | **260 filas** en `modeling_validation_results_all.csv` (dataset × selector × k × modelo, con macro-F1, bal-acc, acc, AUC, delta, rank) | **15 filas** (`modeling_test_results_candidates`, `tab:candidatos`) → ~94 % invisible |
| Selectores | 12 (`fs_all_rankings`, `fs_all_selected_features`) | "mejor clásico" (1) |
| Modelos | 4 (LogReg, SVM, RF, XGB) por config | el modelo ganador de cada config |
| Presupuestos k | barrido por dataset (`fs_k_values_by_dataset`) | k de referencia |
| β (QFS) | **11 valores** 0.0→1.0 × 5 datasets (`qfs_runs_*`, 55 ficheros; `qfs_validation_results` = 60 filas) | β elegido por dataset (1 punto) |
| α (QFS) | barrido exacto completo (`qfs_oracle_*`) | punto-oráculo |
| Métricas | 4 (macro-F1, bal-acc, accuracy, AUC-ROC) | casi siempre solo macro-F1 |
| Distribución por β (shots) | ~266 filas/β de bitstrings y densidades (`qfs_runs_madelon_0p5`) | nada (solo el seleccionado) |
| Tests pareados | `modeling_pairwise_comparison_tests` | 10 filas (solo los candidatos ganadores) |

**Síntesis del colapso: 260 experimentos de validación → 15 mostrados.** Cada
"260 experimentos" del trabajo está representado por su ganador, no por su
distribución. Esto es exactamente lo que hace que el lector no pueda juzgar si
QFS es competitivo en el campo o solo contra un ganador puntual — y se repite
para modelos, β, α, k y métricas.

## Material disponible para las figuras/tablas de "campo completo"

Todo lo necesario ya está calculado (no hay que reentrenar nada):

- **Campo de rendimiento**: `modeling_validation_results_all.csv` (260) y
  `modeling_test_results_candidates.csv` → box/strip de los 12 selectores × 4
  modelos por dataset, con QFS y oráculo superpuestos.
- **Sensibilidad a β**: `qfs_validation_results.csv` (60) → curva macro-F1 vs β
  por dataset (no un punto).
- **Sensibilidad a α**: `qfs_oracle_*` → frente de cardinalidad/criterio completo.
- **Robustez a modelo**: las 4 columnas de modelo de la rejilla → ya parcialmente
  en `tab:ap-qfs-modelos`, ampliable al campo clásico.
- **Coherencia entre métricas**: 4 métricas en la misma rejilla.

---

## Conclusión accionable (actualizada)

Por orden de impacto en la defensa:

1. **[CRÍTICO] Figura del campo de rendimiento completo**: macro-F1 de QFS-NA
   frente a los 12 selectores clásicos × 4 modelos por dataset (box/strip con QFS
   y oráculo resaltados). Es la comparación que hoy no existe y la que sostiene
   la tesis. Fuente: `modeling_validation_results_all.csv`.
2. **[CRÍTICO] Mostrar la distribución, no el punto, en los demás ejes**:
   - macro-F1 **vs β** por dataset (curva, no punto) — `qfs_validation_results`.
   - criterio/cardinalidad **vs α** completo — `qfs_oracle_*`.
   - robustez **vs modelo** ampliada al campo clásico, no solo QFS.
   - coherencia entre las **4 métricas** en la misma rejilla.
3. **Reconstruir `a5_panorama_deltas`** como dot plot de deltas de **todos** los
   selectores (resuelve heatmap roto + comparación incompleta a la vez).
4. **Arreglar `a8`** (Boruta invisible) o reemplazarlo por solape contra los 12.
5. Reconvertir heatmaps mal aplicados `a1`, `a3` a tabla/dot plot (patrón F04).
6. Rehacer legibilidad de `ev6`; pulir colisiones de etiquetas `F04`, `F09`, `a9`.
7. Decidir la figura canónica entre `F10`/`F09`/`ev7` y resolver la redundancia.
8. **Capa de trazabilidad**: el cuerpo muestra el campo completo (puntos 1–2); el
   apéndice/anexo digital conserva la rejilla de 260 + barridos para auditar
   cualquier punto. Así los 260 experimentos quedan reflejados sin saturar.

---

# PASE DE VALENCIA COMPLETO — 2026-06-22

Criterio aplicado y verificado visualmente por mí a **todas** las figuras de la
memoria: bug → chart correcto → **ancla de valencia** → pie explicativo →
verificación visual. Veredicto por figura:

## Reconstruidas con ancla
- `a8` solape vs mRMR/Boruta → dot plot + **banda de azar**.
- `a5` panorama deltas → dot plot **anclado en 0** (verde mejora / rojo empeora).
- `a1` señal vs nulo → ratio real/nulo **anclado en 1×**.
- `a3` roster → **consenso** por variable (distractores en rojo).
- `f10_b2` Jaccard vs 12 → color = **Jaccard − azar** (exceso sobre azar).
- `F05` campo de validación (nueva) → baseline + QFS/óptimo resaltados.

## Verificadas: pasan (ancla/anotación/descriptiva justificada)
- Cuerpo: `F01` (composición, contexto), `F02` (banda azar + anotación Madelon),
  `F03` (banda verde de referencia), `F04` (perfil 12), `F06` (SHAP, descriptiva),
  `F07` (significancia/CI), `F08` (α/β), `F09` (**cuadrantes criterio/optimizador
  = valencia explícita**), `F10` (baseline/mejor/QFS/óptimo), `qfs_organismo`
  (registro MDS), `ev5` (anotación "cambio de paso").
- Apéndice: `a2` (umbral 0.99), `a4` (heatmap SHAP bien aplicado), `a6` (anotación
  Madelon flat), `a7` (coste, caveat), `a9` (limpia), `ev6` (baseline anchor),
  `f5` (línea "espacio completo" en 0), `f10_b5` (título dirigido + selected/resto),
  `f10_b9` (MDS + error), `f10_b10` (estabilidad), `f10_a` (regímenes), `o1`
  (consenso anotado), `ev8` (scorecard garantía/cautela/atención).

## Eliminada
- `explor_mapa` (QFS vs mRMR/mutua): **redundante** con `f10_b2` (que ya cubre
  esas celdas y con ancla de azar) y sin ancla propia → movida a `/basura`,
  referencias redirigidas a `f10_b2`.

Salida limpia (solo `figs/`), sin recrear `10_memoria`. Memoria compila (exit=0).
