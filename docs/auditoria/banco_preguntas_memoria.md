# Banco de preguntas de la memoria → composición visual → tabla de origen

> 2026-06-14. Banco definitivo y enriquecido (supersede a
> `preguntas_y_visualizaciones_memoria.md`). Integra las cinco dimensiones opacadas
> (validación previa, velocidad, interpretabilidad, comportamiento por método α/β/MI,
> métricas) además del eje de rendimiento. Cada pregunta sigue la ruta de
> `.agents/viz-definitive`: pregunta → intención → familia/composición → tabla+columnas →
> caveat. Marcas: **★ hueco** (falta en memoria) · **✓ ya en memoria** · *(apéndice)*.
> Regla: una figura solo si responde una pregunta; mejor quitar que pulir.

Toda cifra sale de una tabla real bajo `results/`. Ninguna figura inventa datos.

---

## Bloque 0 — El banco de pruebas: ¿es un reto diverso?

- **Q1. ¿Cubren los datasets regímenes distintos (tamaño, dimensión, desbalance, clases)?**
  *situar el reto en un mapa* · burbujas: filas (x, log) × variables (y, log), tamaño =
  desbalance, color = nº clases · `01_raw_eda/` estructura + `fase1_*desbalance*` ·
  caveat: ejes log, anotar madelon (4 filas/var) y churn (44k). **★** (hoy solo barra de
  filas/variable).
- **Q2. ¿Cuánta presión dimensional tiene cada problema?** *riesgo dimensional* · barras
  filas/variable · `01_02_estructura_filas_por_feature` · **✓**.

## Bloque 1 — La base es fiable (los "mini-boosts de confianza")

- **Q3. ¿La señal univariante es real tras corregir multiplicidad?** *cerrar "¿es azar?"*
  · barras apiladas vars-FDR/total por dataset, con efecto mediano anotado; madelon
  resaltado (13/500, efecto 0.02) · `fase1_asociacion_target_resumen.csv`
  (`variables_fdr_005`, `variables_contrastadas`, `efecto_abs_mediano`) · caveat: separar
  recuento de magnitud. **★** (cuerpo — prepara el fallo de criterio de QFS).
- **Q4. ¿El preprocesado conservó la estructura de relevancia?** *cerrar "¿favoreció a
  algún método?"* · dumbbell Spearman raw→processed por dataset (todos ~1.0) ·
  `fase3_asociacion_tests.csv` (`spearman_rankings_raw_processed`, `delta_mi_medio`) ·
  **★** *(apéndice)*.
- **Q5. ¿Son representativas las particiones?** *cerrar "¿el split sesga?"* · barras AUC
  adversarial con banda de referencia en 0.5 (0.476–0.535) · `fase4_validacion_adversarial.csv`
  (`auc_cv`, `auc_fold_std`) · caveat: mostrar la banda, no solo la barra. **✓** (mejorar
  con la banda 0.5).
- **Q6. ¿Hay drift entre train y test?** *representatividad numérica* · small multiples
  por dataset de KS/Wasserstein/PSI con líneas de umbral · `fase4_drift_*` (`max_psi`,
  `variables_con_flag`) · caveat: marcar umbrales (PSI 0.10) y nº de flags. **★** (cuerpo;
  el texto ya cita PSI 0.50 sin figura).
- **Q7. ¿Hay leakage (proxy determinista)?** *cerrar "¿fuga?"* · scatter AUC univariante ×
  NMI por variable con líneas en 0.99 · `fase4_leakage_screening.csv` · **★** *(apéndice)*.

## Bloque 2 — Por qué la base clásica es robusta (caracterización de la selección)

- **Q8. ¿Cómo se comportan los 12 selectores y cómo se agrupan por familia?** *taxonomía
  operativa, el resultado nuclear de fase 5* · figura compuesta: panel A roster por
  dataset (qué selecciona cada método), panel B perfil método coloreado por familia
  (coste × redundancia, tamaño = estabilidad) · `fs_all_rankings.csv`,
  `fs_method_profiles.csv` (`segundos_medios`, `jaccard_medio`, `corr_media_seleccionada`)
  · **★** (cuerpo).
- **Q9. ¿Es estable la selección entre semillas?** *fiabilidad* · heatmap Jaccard ·
  `fs_jaccard_stability.csv` · **✓**.
- **Q10. ¿Qué métodos controlan la redundancia?** *diferenciador clave* · dumbbell/dot
  delta redundancia base 0 (mRMR único ≤0) · `fs_redundancy_delta` · **✓**.
- **Q11. ¿La señal supera al azar?** *honestidad* · heatmap real vs nulo · permutación ·
  **✓**.
- **Q12. ¿Cuánto cuesta cada método (velocidad)?** *coste, dimensión ausente* · barras
  horizontales tiempo medio por método en escala log, coloreadas por familia (filtros
  0.007s … Boruta 2.5s) · `fs_method_profiles.csv`/`fs_all_execution_times.csv` · caveat:
  escala log etiquetada; es tiempo de ajuste, no de inferencia. **★** (cuerpo).
- **Q13. ¿La reducción dimensional mantiene o mejora el rendimiento?** *propuesta de valor
  central del TFG* · scatter coste (nº variables, x) × macro-F1 (y) con línea de baseline,
  small multiples por dataset · `06_modeling/modeling_cost_performance.csv` (`n_features`,
  `macro_f1`, `baseline_macro_f1_same_model`) · **★** (cuerpo).

## Bloque 3 — Interpretabilidad (¿qué sostiene cada modelo?)

- **Q14. ¿Qué variables sostienen cada modelo y en qué dirección?** *explicabilidad — el
  hueco más grave* · beeswarm SHAP por modelo-dataset (1-2 en cuerpo: bcw y madelon; por
  clase en olive) · `06_modeling/modeling_shap_values_full_*.csv` + `*feature_values_*` ·
  caveat: SHAP explica el modelo, no causalidad; muestra dispersión por instancia. **★**
  (cuerpo + resto *(apéndice)*).
- **Q15. ¿Coinciden SHAP, selección y asociación de fase 1?** *cierre del círculo
  relevancia↔selección↔modelo* · concordancia top-k (dumbbell o solape) ·
  `modeling_shap_feature_importance.csv` + selección + `fase1_asociacion` · **★**
  *(apéndice)*.

## Bloque 4 — El veredicto clásico

- **Q16. ¿La selección iguala/mejora al baseline por dataset?** *veredicto* · baseline vs
  selección con IC bootstrap en test · `fase7_test_baseline_vs_seleccion` · **✓**.
- **Q17. ¿Significancia vs magnitud?** *prudencia (churn a techo)* · deltas pareados con
  línea de umbral de efecto práctico (0.01) · `fase7_tabla_maestra.csv` · **★** (cuerpo,
  refuerza la tabla).
- **Q18. ¿Dónde ayuda cada selector (panorama)?** *visión de conjunto* · heatmap delta
  validación selector × dataset · `fase7_panorama_validacion_delta` (existe) · **★**
  *(apéndice)*.

## Bloque 5 — El método cuántico: comportamiento, no solo resultado

- **Q19. ¿Recorre α la escalera de presupuestos (Proposición 1 de Mücke)?** *teoría→práctica
  del control de cardinalidad* · escalera α (x) × cardinalidad ‖x‖₁ (y) del óptimo exacto
  · `08_quantum/qfs_oracle_*.csv` (`alpha`, `cardinality`, `k_target`) · caveat: es el
  QUBO exacto, no el simulador analógico (que fija α). **★** (cuerpo — conecta marco
  teórico con evidencia).
- **Q20. ¿Cómo modula β la selección?** *segundo grado de libertad* · mapa β × variable
  (densidad Rydberg) · `08_quantum/qfs_runs_*.csv` (`density__*`, `beta`) · **✓** (madelon;
  añadir olive_9 donde el oráculo ayuda).
- **Q21. ¿Optimiza bien el simulador su propio criterio? (criterio vs optimizador)** *la
  aportación metodológica central* · figura de dos lecturas: Hamming y Δcoste por dataset,
  separando madelon (Δcoste≈0 → criterio) de churn (Δcoste +1.32 → optimizador) ·
  `08_quantum/qfs_quality_control_*.csv` (`hamming_distance`, `delta_cost_alpha05`) ·
  **★** (cuerpo).
- **Q22. ¿Consume QFS las mismas cantidades que los clásicos (I_i, R_ij)?** *trazabilidad
  del handoff* · heatmap R_ij + barras I_i por dataset · handoff
  (`fs_qfs_handoff_matrices_index.csv` → matrices) · **★** *(apéndice)*.
- **Q23. ¿Cuánto cuesta QFS frente a los clásicos?** *coste de la vía cuántica (simulada)*
  · barras tiempo simulación por dataset junto al rango clásico · `qfs_runs_*`
  (`elapsed_seconds`) + `fs_method_profiles` · caveat fuerte: es tiempo de SIMULACIÓN
  analógica, no de hardware; etiquetarlo así. **★** *(apéndice; con caveat)*.

## Bloque 6 — La comparación clásico↔cuántico (cierre)

- **Q24. ¿QFS iguala/supera a los mejores clásicos?** *el veredicto cuántico, hoy solo
  tabla* · figura compuesta por dataset: baseline / mejor-clásico / QFS-NA / QFS-oráculo
  con IC, dumbbell o barras · `08_quantum/comparacion_qfs_vs_baseline.csv` · caveat:
  marcar veredicto (equivalente/deterioro). **★** (cuerpo — paraleliza la figura clásica).
- **Q25. ¿Qué variables elige QFS frente a Boruta/mRMR?** *atribución del comportamiento* ·
  matriz de solape (UpSet o heatmap binario) · `qfs_selected_*` + selección clásica ·
  **★** *(apéndice)*.
- **Q26. ¿Cómo se comportan las métricas (macro-F1 vs AUC en binarios)?** *justificar la
  elección de métrica y el puente con el paper* · barras agrupadas macro-F1/AUC en los dos
  binarios · `08_quantum/qfs_auc_binarios_contexto.csv` + test results · **★** *(apéndice)*.

---

## Conjunto objetivo (propuesta de reparto)

**Cuerpo de resultados (~14-16 figuras):** Q1, Q2✓, Q3, Q5✓, Q6, Q8, Q9✓, Q10✓, Q11✓,
Q12, Q13, Q14, Q16✓, Q17, Q19, Q20✓, Q21, Q24. (8 ya integradas + ~10 cierra-huecos.)

**Apéndice de figuras de apoyo:** Q4, Q7, Q15, Q18, Q22, Q23, Q25, Q26.

**Fuera (ruido):** univariante/normalidad/pca/preclasificación de fase 1, outliers/
categóricas de fase 2, asociación/redundancia heatmaps que duplican tablas, intervalos de
test por dataset de fase 6 (redundantes con Q16).

## Estado de implementación por figura

- **Reutilizan plotter existente** (regenerar a `figs/`): Q2, Q5, Q9, Q10, Q11, Q16, Q20.
- **Plotter nuevo necesario** (no existe figura, sí la tabla): Q1, Q3, Q6, Q8, Q12, Q13,
  Q14 (beeswarm ya generado en fase 6, copiar), Q17, Q19, Q21, Q24, y los de apéndice.
- Construir cada figura nueva con la ruta `viz-definitive` Tier 2 (cuerpo) / Tier 1
  (apéndice).

## Mapa pregunta → sección de la memoria

- Bloque 0-1 → §5.1 (base experimental).
- Bloque 2-3 → §5.2 (clásica) + interpretabilidad.
- Bloque 4 → §5.2 cierre.
- Bloque 5-6 → §5.3 (cuántica y comparación).

## Decisiones que requieren al usuario

1. Validar el reparto cuerpo/apéndice (¿subir o bajar alguna? p. ej. ¿Q23 velocidad QFS al
   cuerpo pese al caveat de "simulación"? ¿Q19 escalera α al cuerpo o apéndice?).
2. ¿Confirmamos ~14-16 figuras de cuerpo, o se prefiere un cuerpo más esbelto (~10) con más
   material en apéndice?
3. Tras validar: orden de construcción (sugerido: primero los huecos ALTOS del cuerpo —
   Q14 SHAP, Q24 comparación QFS, Q8 roster, Q6 drift, Q13 coste-rendimiento, Q21
   criterio-vs-optimizador, Q3 FDR— y luego apéndice).
