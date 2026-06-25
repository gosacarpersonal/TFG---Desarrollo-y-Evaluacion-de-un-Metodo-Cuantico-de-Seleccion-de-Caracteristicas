# Auditoría de tablas y CSV de todo el TFG — 2026-06-21

Mismo método que la auditoría visual ([auditoria_visual_figuras_2026-06-21.md](auditoria_visual_figuras_2026-06-21.md)):
inventario real, qué entra a la memoria, calidad/redundancia y la lente de
colapso. Verificado sobre `results/tables/` (1107 CSV).

## Inventario por fase

| Fase | CSV | Composición dominante |
|---|---|---|
| 01 raw EDA | 25 | tablas-resultado de auditoría exploratoria |
| 02 preprocessing | 22 | auditoría de invarianza |
| 03 postproc audit | 27 | correlaciones, asociación, drift |
| 04 split audit | 24 | adversarial, leakage, drift de particiones |
| 05 feature selection | **584** | mayoría: **árbol granular** (5 datasets × 12 métodos × k) + ~90 tablas-resultado |
| 06 modeling | **327** | **260 experimentos** (1 CSV/experimento) + 15 test + 33 SHAP + ~19 resumen |
| 07 final comparison | 7 | tablas de cierre (varias solapadas) |
| 08 quantum | 86 | **55 `qfs_runs`** (β) + 5 oráculo + 5 QC + ~21 |
| 10 efic./general. | 2 | — |
| **TOTAL** | **1107** | |

## Clasificación funcional (los 1107 no son 1107 "resultados")

Tres familias muy distintas, hoy mezcladas sin distinción:

1. **Tablas-resultado** (pequeño subconjunto, ~80–100): lo que se cita o se
   citaría. Resúmenes, rankings, comparaciones, perfiles.
2. **Volcados granulares** (la mayoría): 260 `experiments_validation/*`, 15 test,
   55 `qfs_runs_*`, 33 SHAP, árbol `05/granular/<dataset>/<método>/k_*.csv`. Son
   la **base defendible** — un fichero por experimento/condición.
3. **Andamiaje / procedencia** (~95 `log` + checks + `index` + `schema` +
   `plan` + `protocol`): metadatos de pipeline. **No son resultados** y casi
   nunca deben citarse.

> Implicación: "260 experimentos" hoy no es navegable porque no hay manifiesto
> que separe estas tres familias.

## EL MISMO COLAPSO, ahora en las tablas

La rejilla completa de rendimiento existe pero **ninguna tabla la muestra**, ni
en cuerpo ni en apéndice:

| Tabla mostrada | Filas | Qué hace |
|---|---|---|
| `tab:comparacion` (cuerpo) | 5 | baseline vs **"mejor selección"** (1 de 12); los otros 11 desaparecen |
| `tab:candidatos` (apénd.) | ≤15 | mejor baseline + **2** mejores subconjuntos |
| `fase7_tabla_maestra.csv` | **15** | pese al nombre "maestra", ya está colapsada a candidatos |
| `tab:comparacion` pareada | 10 | solo los candidatos ganadores |

La verdadera matriz completa es **`modeling_validation_results_all.csv` (260
filas)** — dataset × selector × k × modelo, con **las 4 métricas** (macro-F1,
balanced-acc, accuracy, AUC-ROC), delta vs baseline y rank. **No se cita ni se
resume en ninguna parte.** Mismo caso para β (`qfs_runs_*`, 55 ficheros) y α
(`qfs_oracle_*`).

## Redundancia y problemas de calidad detectados

- **Cuatro tablas de comparación solapadas** sin canónica clara:
  `comparacion_qfs_vs_baseline` (5) · `comparacion_qfs_configuraciones_vs_baseline`
  (10) · `fase7_comparacion_final` (5) · `fase7_comparacion_final_con_qfs` (15).
- **Datos duplicados en dos formas**: los 260 experimentos están a la vez
  fragmentados (260 ficheros de 1 fila) y agregados (`..._results_all.csv`).
  Útil para acceso, pero hay que documentar cuál es la fuente canónica.
- **Naming engañoso**: `fase7_tabla_maestra` no es la tabla maestra (la maestra
  real es la rejilla de 260).
- **Granularidad rica pero invisible**: cada experimento guarda 4 métricas; la
  memoria solo expone macro-F1. Las otras 3 (balanced-acc, accuracy, AUC) están
  calculadas y sin usar.

## Lo bueno (no tocar)

- La cobertura es **exhaustiva y trazable**: existe el dato para defender
  cualquier afirmación. El problema es de *exposición y organización*, no de
  falta de datos.
- Las tablas de auditoría del apéndice (`tab:senal`, `tab:postproc`,
  `tab:particiones`, `tab:perfil`) son resúmenes fieles y bien construidos.
- La tabla de trazabilidad `tab:ap-indice-trazabilidad` ya esboza el manifiesto
  que falta — hay que completarla, no inventarla.

## Conclusión accionable (tablas)

Paralela a la de figuras. Por impacto:

1. **[CRÍTICO] Tabla del campo completo**: resumen de la rejilla de 260 — por
   dataset, distribución de macro-F1 de los 12 selectores × 4 modelos (mín/
   mediana/máx o cuartiles), con QFS y oráculo situados. Hoy no existe.
2. **Exponer las 4 métricas**, no solo macro-F1, al menos en apéndice.
3. **Resolver la redundancia** de las 4 tablas de comparación: elegir canónica.
4. **Manifiesto de material suplementario**: clasificar los 1107 en
   resultado / granular / andamiaje, con la fuente canónica de cada cifra.
   Ese es el vehículo para reflejar los 260 experimentos sin saturar el PDF.
5. Renombrar/aclarar `fase7_tabla_maestra` y documentar fuente canónica de la
   rejilla (`modeling_validation_results_all.csv`).

## Pendiente (no inspeccionado en detalle aún)

Contenido fino de fases 01–04 (tablas de EDA/preproc/split), árbol granular de
05 (consistencia entre `k_*.csv`), y los 5 `qfs_oracle_*` y 5 `qfs_quality_control_*`.
