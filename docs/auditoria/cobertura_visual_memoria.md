# Auditoría de cobertura visual de la memoria

> 2026-06-14. Cruce entre lo que la memoria explica/muestra y todo lo que los notebooks
> produjeron, para detectar visualizaciones (o evidencia) que se están dejando fuera y
> que, de no incluirse, dejan el TFG menos cerrado. Verificado contra `results/` y los
> `.tex`.

## Cifras de partida

- Artefactos producidos: **140 figuras PNG** y **1030 tablas CSV** (la mayoría de tablas
  son granulares por experimento: fase 5 = 529, fase 6 = 320; no son material de memoria).
- La memoria usa hoy **8 figuras + 4 tablas**. El resto de figuras no se muestra ni se
  cita.

El objetivo de esta auditoría NO es meter las 140 figuras —eso sería ruido—, sino
identificar las pocas cuya ausencia deja un hueco argumental.

## Q1 — Qué explica la memoria (mapa por capítulo)

| Cap. | Contenido | Estado |
|---|---|---|
| 1 Introducción | Motivación, 5 objetivos, estructura | Cerrado |
| 2 Marco teórico | FS, QUBO, α↔k, adiabática, Rydberg, validación estadística | Cerrado |
| 3 Estado del arte | Métodos clásicos, optimización cuántica, Rydberg, QFS | Cerrado |
| 4 Métodos | Datasets, roster de 12, grafo I/R, método cuántico (α, β, oráculo), diseño de 7 fases, protocolo (4 modelos, macro-F1, contrastes) | Cerrado |
| 5 Resultados | 5.1 auditoría base, 5.2 clásica, 5.3 cuántica, comparación, discusión | Reescrito; faltan figuras (ver Q4) |
| 6 Conclusiones | 6 conclusiones + limitaciones + trabajo futuro | Reescrito |
| Apéndice | Reproducibilidad | **Desactualizado** (ver "Hallazgos no-figura") |

## Q2/Q3 — Qué se hizo y qué visualizaciones se pueden extraer de cada notebook

Familias de figura por fase (deduplicadas por dataset). Clasificación: **USADA** /
**HUECO** (debería entrar) / *exploratoria* (dejar fuera o apéndice).

### Fase 1 — EDA (30 figuras, 1 usada)
- `01_02_estructura_filas_por_feature` — **USADA**.
- `01_04_target_desbalance_comparado` — **HUECO (alto)**: la memoria justifica macro-F1
  por "multiclase y desbalanceado", pero el desbalance nunca se muestra.
- `univariante`, `normalidad`, `efecto`, `asociacion`, `redundancia`, `pca`,
  `preclasificacion` (×4 c/u) — *exploratorias*; a lo sumo apéndice.

### Fase 2 — Preprocesado (14 figuras, 0 usadas)
- `fase2_impacto_preprocesado_control` — *apéndice* (respalda "preprocesado conservador").
- `distribuciones_numericas`, `outliers_iqr`, `categorica` — *exploratorias*.

### Fase 3 — Auditoría post-preprocesado (20 figuras, 0 usadas)
- `fase3_distribucion_conservacion` / `target_conservacion` — *apéndice*: la memoria
  **afirma** que el preprocesado no alteró distribuciones/target, pero no lo muestra.
- `fase3_dimensionalidad_final`, `sintesis_metricas_split`,
  `asociacion_topk_overlap_qfs` — *apéndice/niche*.
- `asociacion`, `redundancia` (×4) — *exploratorias*.

### Fase 4 — Auditoría de splits (18 figuras, 1 usada)
- `fase4_validacion_adversarial_auc` — **USADA**.
- `fase4_drift` (×5) — **HUECO (alto)**: el texto de resultados cita cifras de drift
  (KS/Wasserstein/PSI, "PSI máximo de 0.50", alertas marcadas) que salen de una figura
  que NO se muestra.
- `fase4_target` (×5), `fase4_pca` (×5) — *apéndice* (conservación de target y
  representatividad multivariante).
- `tamanos_split`, `resumen_metricas_split` — *contexto menor*.

### Fase 5 — Selección (13 figuras, 3 usadas)
- `fs_stability_jaccard_heatmap`, `fs_permutation_above_null_heatmap`,
  `fs_redundancy_delta` — **USADAS**.
- `roster_comparison` (×5) — **HUECO (alto)**: es la comparación de los 12 selectores por
  dataset, el resultado nuclear de la fase 5 ("espejo de QFS"). El lector lee que hay 12
  métodos espejo pero nunca los ve comparados.
- `method_feature_heatmap` (×5) — *apéndice* (qué variables elige cada método).

### Fase 6 — Modelado (27 figuras, 0 usadas)
- `shap_summary` (×5 + por clase) — **HUECO (el más grave)**: la memoria dice que se
  calcula SHAP "para comprobar qué variables sostienen cada subconjunto"; se invirtió
  esfuerzo en arreglar los beeswarm reales; y NINGUNO aparece. Evidencia de
  interpretabilidad prometida y no mostrada.
- `validation_cost_performance` (×5) — **HUECO (medio)**: coste (nº variables) frente a
  rendimiento; visualiza directamente la propuesta de valor de subconjuntos compactos,
  eje central del TFG.
- `test_macro_f1_confidence_intervals` (×5) — *redundante* con la figura consolidada de
  fase 7; dejar fuera.

### Fase 7 — Comparación final (8 figuras, 2 usadas)
- `fase7_test_baseline_vs_seleccion`, `fase7_estabilidad_vs_rendimiento` — **USADAS**.
- `fase7_panorama_validacion_delta` — **HUECO (medio)**: mapa de delta por
  selector×dataset; el "panorama" de qué métodos ayudan y dónde.
- `fase7_mini_resumen_evidencia` (×5) — *apéndice* (fichas por dataset).

### Fase 8/9 — Cuántica (10 figuras fuente; 3 figuras narrativas usadas en cuerpo)
- `qfs_beta_map_madelon` — **USADA**.
- `fase9_resumen_evidencia` (×5) — **DISPONIBLE COMO SOPORTE**: verificado por
  `scripts/verify_fase9_evaluacion.py`; la asimetría cuerpo clásico/cuerpo cuántico queda
  cubierta por F10 (`f10_qfs_vs_clasico.png`) y por la F9 diagnóstica
  (`diag_atribucion_qfs.png`).
- `qfs_beta_map` (otros 4) — *representativos*; quizá añadir olive_9 (donde el oráculo
  ayuda).

## Q4 — Qué visualizaciones DEBERÍAN componer la memoria

### Mantener (8 actuales)
Las 8 ya integradas son correctas y se quedan.

### Añadir para cerrar huecos (recomendado)

| Figura a añadir | Fase | Severidad | Ubicación sugerida |
|---|---|---|---|
| Beeswarm SHAP (1-2 representativos) | 6 | **ALTA** | 5.2/5.3 resultados |
| Comparación/evidencia QFS por dataset | 9 | **ALTA** | 5.3 resultados |
| Roster de 12 selectores (1-2 datasets) | 5 | **ALTA** | 5.2 resultados |
| Drift de splits (1 representativo) | 4 | **ALTA** | 5.1 resultados |
| Desbalance del target | 1 | MEDIA-ALTA | 5.1 resultados |
| Coste vs rendimiento (1 representativo) | 6 | MEDIA | 5.2 resultados |
| Panorama delta selector×dataset | 7 | MEDIA | 5.2 resultados |

→ Memoria objetivo: **~13-15 figuras** (las 8 actuales + 5-7 cierra-huecos), no 8.

### Llevar a apéndice (apoyo, sin bloquear el cuerpo)

Conservación post-preprocesado (fase 3), target/pca por split (fase 4), impacto del
preprocesado (fase 2), method-feature heatmaps y resto de roster (fase 5), beeswarm SHAP
del resto de datasets (fase 6), β-maps y fichas de evidencia restantes (fase 8/9).

### Dejar fuera (ruido exploratorio)

Univariante/normalidad/efecto/pca/preclasificacion de fase 1, outliers/categóricas de
fase 2, asociación/redundancia heatmaps que duplican tablas, intervalos de test por
dataset de fase 6 (redundantes con fase 7).

## Hallazgos NO-figura (también dejan el TFG menos cerrado)

1. **Apéndice desactualizado** (`apendice.tex`): revisar que ya no diga "195
   experimentos", "siete cuadernos" ni marco "pre-cuántico"; la memoria actual
   trabaja con 260 experimentos y 9 fases.
2. **Marcadores antiguos de resultados**: el `PENDIENTE_RESULTADOS` de
   `resultados.tex` ya fue retirado; mantener la búsqueda en la checklist para
   evitar que reaparezcan marcadores similares.
3. La sección 5.2 cita estabilidad/permutación/redundancia con cifras concretas: verificar
   que todas esas cifras siguen cuadrando tras la reejecución con 12 métodos + XGBoost.

## Implicación para el notebook espejo de la memoria

El plan de `prompt_memoria_visual.md` debe actualizarse: su inventario objetivo NO son las
8 figuras actuales, sino el **conjunto final tras esta auditoría** (8 + las cierra-huecos
aprobadas). El notebook genera ese conjunto a `figs/` y verifica coherencia, de modo que
"repasar la memoria en visualizaciones" cubra un TFG ya cerrado.

## Decisiones que requieren al usuario

1. ¿Qué cierra-huecos de severidad ALTA/MEDIA se suben al cuerpo de resultados y cuáles a
   apéndice? (recomendación: las 4 ALTAS al cuerpo; desbalance, coste-rendimiento y
   panorama al cuerpo si no recargan; el resto a apéndice.)
2. ¿Se crea un apéndice de figuras de apoyo o se mantiene el apéndice solo de
   reproducibilidad (actualizado)?
