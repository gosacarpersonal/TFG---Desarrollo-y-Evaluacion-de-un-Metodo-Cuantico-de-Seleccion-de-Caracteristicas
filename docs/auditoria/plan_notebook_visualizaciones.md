# Blueprint del notebook de visualizaciones — caracterizar POR QUÉ funciona o no QFS

> 2026-06-15. Documento-guion para el **último notebook** (`notebooks/fase10_visualizaciones.ipynb`,
> a crear) que debe reflejar la analítica de toda la memoria. **No es una galería de figuras**: es
> el aparato que *lee* el experimento (no el podio) y caracteriza POR QUÉ QFS funciona o no respecto a
> **dataset · métodos · k · α · β · modelos · métricas · tests estadísticos · todo en conjunto**.
> Escrito para que Codex lo implemente sin ambigüedad. Toda cifra sale de `results/tables/` (rutas
> abajo); ninguna figura inventa datos. Lenguaje visual: matplotlib + `src/viz_core` (exemplars ya
> aceptados: beeswarm SHAP y plano de atribución). Cuatro lentes de "estar bien": **(L1) fidelidad de
> comportamiento** (¿hace lo que la teoría/física predice?), **(L2) posición en el espacio de métodos**,
> **(L3) robustez/consistencia**, **(L4) parsimonia con coherencia**.

---

## PARTE A — Caracterización por dataset (el "por qué" de base, fases 1→3→4)

Cada dataset se barrió *por algo*: estresa un régimen distinto. Esta huella (recaracterizada tras
preprocesado en fase 3 y tras splits en fase 4) es la que **explica** el comportamiento posterior en
k/α/β/modelos y el veredicto de QFS. Fuentes: `01_raw_eda/fase1_sintesis_evidencias.csv`,
`fase1_tamano_efecto_resumen`, `fase1_redundancia_resumen`, `fase1_pca_resumen`,
`fase1_preclasificacion_resumen`; `03_postprocessing_audit/fase3_correlaciones_resumen.csv` (VIF),
`fase3_dimensionalidad_final`, `fase3_shift_distribucional_resumen`, `fase3_target_tests`;
`04_split_audit/fase4_resumen_para_fase5.csv`, `fase4_drift_resumen`, `fase4_leakage_resumen`,
`fase4_validacion_adversarial`, `fase4_pca_varianza`.

| Eje (fuente) | Breast Cancer | Customer Churn | Madelon | Olive 3 | Olive 9 |
|---|---|---|---|---|---|
| filas × vars (p/n) | 569×30 (0.054) | 440 832×10→15 (~0) | 2000×500 (0.25) | 572×8 | 572×8 |
| filas/feature | 18 | 40 075 | **4** | 71 | 71 |
| FDR sobrevive | 27/30 | 10/10 | **13/500** (−25) | — | — (8/8 eff alto) |
| efecto mediano | 0.65 (Cliff) | 0.20 (Cliff) | **0.02** (Cliff) | 0.80 (ε²) | alto (ε²) |
| redundancia (pares \|ρ\|≥.85) | **29** (máx 0.9996) | 0 (máx 0.19) | 12 (máx 0.996) | 2-3 | 2-3 |
| VIF máx / #VIF≥10 (fase 3) | **3806 / 23** | 1.1 / 0 | 1.3 salvo feat_28/48/64≈70-103 / 20 | 326 / 5 | 326 / 5 |
| dim. intrínseca (PCA 80%) | 5 | 6 | **295/500** | 3 | 3 |
| drift: #flag / PSI máx (fase 4) | 25 / 0.50 | 0 / 0.0003 | 41 / 0.18 | 7 / 0.34 | 6 / 0.33 |
| adversarial AUC (≈0.5 ok) | 0.52 | 0.52 | 0.48 | 0.51 | 0.54 |
| leakage (AUC/NMI≥0.99) | 0 | 0 | 0 | 0 | 0 |
| **régimen que estresa** | señal fuerte + **multicolinealidad extrema**, baja dim | **baja redundancia**, n enorme, baseline saturable | **desierto de distractores**, señal en interacciones (MI-ciega) | limpio/separable, redundancia composicional | el más difícil: multiclase n pequeño (86 test) |

**Lectura clave por dataset (la hipótesis que cada uno pone a prueba sobre QFS):**
- **Madelon** — efecto 0.02, 456 vars sin señal univariante, PCA 295/500, VIF≈1 (el ruido NO es colineal,
  es alta-dim genuina): la relevancia/redundancia por **información mutua de pares es estructuralmente
  ciega** aquí → predice **fallo de CRITERIO** (lo herede quien lo herede, clásico o cuántico).
- **Customer Churn** — redundancia ~0, VIF≈1, baseline→1.0: criterio fácil (poca redundancia que
  controlar) y techo altísimo → margen nulo; cualquier fallo será del **OPTIMIZADOR**, no del criterio.
- **Breast Cancer** — VIF 3806, 29 pares casi perfectos: el caso donde *controlar redundancia* importa
  de verdad → banco natural para ver si QFS se comporta como mRMR.
- **Olive 3 / 9** — espacio diminuto (8 vars): el reto no es escalar sino no degradar; Olive 9 con 86
  filas de test obliga a prudencia (ni mejora ni deterioro afirmables).

→ **Visualización A** (L1, cuerpo): *huella de los 5 regímenes* — small multiples o tabla-gráfico con
p/n, efecto mediano, redundancia (VIF), dim. intrínseca (PCA). Anota qué predice cada régimen para QFS.
Protagonistas Madelon (criterio) y Churn (optimizador). **Esta figura debe ir ANTES del veredicto** para
que el lector lea cada resultado como consecuencia del régimen, no como sorpresa.

---

## PARTE B — Las 9 dimensiones: qué evidencia las responde y qué dicen

### D1 · Dataset → ver PARTE A.

### D2 · Métodos de selección (L2) — *¿qué clase de selector es QFS?*
Fuentes: `05_feature_selection/fs_method_registry.csv` (taxonomía: relevancia/redundancia/comb/wrapper/
embedded + criterio técnico), `fs_qfs_mi_target_vector__*` + `fs_qfs_pairwise_mi_matrix__*` (las MISMAS
I_i,R_ij que consume QFS), `fs_all_rankings.csv`, `08_quantum/qfs_selected_*`.
**Dos vistas (NO solo mRMR — contemplar los 12):**
- **B2a Mapa de coordenadas**: rel_capturada (ΣI_i sel / ΣI_i top-k) vs redundancia interna (media R_ij
  sel), los 12 + QFS, color por familia. Hallazgo ya verificado: QFS es **clase-mRMR en coordenadas** en
  BCW/Madelon/Olive3; en **Churn tiene la redundancia MÁS ALTA** (fuera de su nicho).
- **B2b Solape de subconjunto (Jaccard) de QFS vs los 12**: corrige el sesgo mRMR. Verificado: Olive3
  J=1.00 con mRMR; Madelon máx mRMR pero **0.25** (coincide en coordenada, no en variables → criterio
  no fija); **Churn se parece más a `mutual_correlation`(0.67)/relevancia que a mRMR(0.27)** → el
  optimizador lo desvió de su familia. **Conclusión:** QFS es mRMR-class solo en los casos limpios; donde
  falla, se desvía hacia otra familia, y esa desviación coincide con el tipo de fallo.

### D3 · k (L3) — *¿el comportamiento depende del presupuesto?*
Fuentes: `fs_k_values_by_dataset.csv` (escaleras: BCW 3/5/10/15/20/30; Churn 1/4/5/10/15; Madelon
5/10/15/20; Olive 3/5/8), `fs_redundancy_vs_full.csv` (redundancia interna vs k por método),
`08_quantum/ev6_rendimiento_vs_k.csv` (macro-F1 val vs k: baseline, mRMR, QFS-NA por densidad),
`06_modeling/modeling_cost_performance.csv` (n_features vs macro_f1 vs baseline).
**Lectura:** no quedarse en el k de referencia; mostrar la TRAYECTORIA. El paper dice que QFS brilla en
k pequeño (2–5) y los clásicos lo alcanzan al crecer k → comprobarlo en *nuestros* datos.

### D4 · α (L1) — *¿la teoría se cumple? (Proposición de Mücke)*
Fuentes: `08_quantum/qfs_oracle_*.csv` (mode=alpha_grid: columnas `alpha`, `cardinality`, `q_opt`,
`selected_features`). **B4 escalera-α**: cardinalidad ‖x‖₁ vs α (0→p monótona) sobre el óptimo EXACTO
del QUBO → demuestra que recorrer α *es* recorrer el presupuesto. Caveat: es el QUBO exacto, no el
simulador analógico (que fija α=0.5). Segundo eje: coste q_opt(α).

### D5 · β (L1) — *el segundo mando y el flanco geométrico*
Fuentes: `08_quantum/qfs_runs_<ds>_0p0…1p0.csv` (densidades Rydberg por β; columnas `density__*`),
`qfs_quality_control_*.csv` (Hamming y Δcoste por β), `qfs_operational_summary.csv`
(`dist_ratio_rydberg`, β elegido). **Hallazgo:** β elegido y dist_ratio por dataset — BCW 0.45, Churn
**0.35**, Madelon **0.35**, Olive 0.45 (todos relajados desde el 1/√2≈0.707 del paper; Churn/Madelon los
más relajados). **B5**: mapa β × variable (densidad) + cómo β mueve la F1 de validación; conecta con D8
(átomos).

### D6 · Modelos (L3) — *el valor de la selección no es absoluto*
Fuentes: `06_modeling/modeling_cost_performance.csv` (columnas `model_name`, `macro_f1`,
`baseline_macro_f1_same_model`, `delta_macro_f1_vs_same_model_baseline` — 4 modelos: logística, SVM
lineal, random forest, XGBoost), `modeling_validation_results_all.csv`, `modeling_test_results_candidates`.
**Hallazgo a visualizar:** la ganancia de selección en Madelon **se desploma +0.28→+0.094 al pasar de
lineales/bosque a XGBoost** (XGBoost absorbe distractores). **B6**: delta-vs-baseline por (selector ×
modelo) → la interacción selección×modelo, hoy nota a pie.

### D7 · Métricas (L4/contexto) — *por qué macro-F1 y qué cambia con AUC*
Fuentes: `08_quantum/qfs_auc_binarios_contexto.csv` (macro-F1 vs AUC-ROC en binarios: baseline/QFS-NA/
oráculo), `modeling_cost_performance` (`macro_f1`, `balanced_accuracy`, `auc_roc`). **Lectura:** macro-F1
como primaria porque hay multiclase/desbalance (Olive 9, ratio 8.24) donde el AUC binario del paper no
aplica; AUC solo como puente con las cifras publicadas. **B7** (apéndice): macro-F1 vs AUC en los 2
binarios.

### D8 · Tests estadísticos (L1/transversal) — *la cadena de confusores descartados*
Fuentes por fase: FDR + tamaño de efecto (`fase1_fdr_resumen`, `fase1_tamano_efecto_resumen`); shift de
preprocesado nulo (`fase3_shift_distribucional_resumen` todo 0, `fase3_target_tests` p=1.0); splits
(`fase4_validacion_adversarial` AUC≈0.5, `fase4_drift_resumen`, `fase4_leakage_resumen`); permutación de
selección (`fs_permutation_summary`, p≈0.048); bootstrap + sign-permutation + label-permutation
(`06_modeling/modeling_pairwise_comparison_tests`, `modeling_permutation_test_results`); control del
óptimo exacto (`qfs_quality_control_*`). **B8**: la cadena como secuencia de "qué eliminamos para que la
comparación sea limpia" (FDR→efecto→shift→adversarial→drift→leakage→permutación→bootstrap→óptimo exacto),
no como adornos sueltos.

### D9 · Átomos / configuración física (L1) — *el cuerpo del método (Fig. 2 del paper), ausente*
Recompute (no hay posiciones guardadas) llamando al solver:
`QFS_based_on_NA/QFS_Auxiliar_functions.arrange_atoms_robust_MDS(R_b, normalize_list(I_i),
normalize_matrix(R_ij), dist_ratio_rydberg, beta=β_elegido)`, con `C=862690·2π·1e6`,
`R_b=(C/Δ_local_max)^{1/6}` (Δ_local_max=30e6), semilla fija; I_i,R_ij del handoff (Olive 8, Churn 15
directos; BCW/Madelon sobre las 20 preseleccionadas — `qfs_preselection_summary.csv`). **B9** por dataset:
posiciones, radio de bloqueo R_b, tamaño/color=relevancia (detuning), aristas=pares redundantes dentro de
bloqueo, y **error de embebido** (`calculate_error_matrix`). **Aquí debe verse** por qué Churn rompe
(dist_ratio 0.35 → mayor distorsión) y por qué Madelon no es un problema de hardware (embebido válido,
falla el criterio).

---

## PARTE C — Síntesis "todo en conjunto" (D9-bis, el clímax, L1–L4)

La integración es la tesis: para cada dataset, **régimen (A) → comportamiento en los mandos (B) →
veredicto**, con el plano de atribución como cierre.

- **Madelon** = fallo de **criterio**: régimen (efecto 0.02, PCA 295/500, MI-ciega) → α ordena casi al
  azar, QFS≈mRMR en coordenada pero 0.25 de solape, átomos embeben bien (Δcoste≈0), oráculo *también*
  cae a 0.643 → el límite es la formulación, no el hardware.
- **Customer Churn** = fallo de **optimizador**: régimen (redundancia ~0, baseline 1.0, dist_ratio 0.35)
  → oráculo recupera ~baseline (criterio bien) pero QFS-NA cae a 0.922, expulsado de su nicho mRMR
  (solape 0.27, redundancia más alta) y Δcoste +1.32 → el límite es la dinámica analógica/geometría.
- **BCW / Olive 3** = sin fallo atribuible: QFS iguala con menos variables, ≈mRMR.
- **Olive 9** = inconcluso por n: oráculo 0.906 pero 86 filas de test → prudencia.

**Figura clímax** = plano de atribución (`diag_atribucion_qfs`, ya construido): deterioro =
fallo_criterio (baseline−oráculo) + fallo_optimizador (oráculo−QFS-NA), en macro-F1, los 5 datasets.

---

## PARTE D — Estructura del notebook (celdas) para Codex

`notebooks/fase10_visualizaciones.ipynb` — orquestador narrativo (núcleo reutilizable en `scripts/`/`src/`,
celdas que ejecutan-muestran-interpretan, como el patrón de fases 1–4):

0. **Intro**: propósito (analizar el proceso, no el podio), las 4 lentes, fuentes.
1. **§A Regímenes** → Visualización A (huella de los 5 datasets). Markdown: qué predice cada régimen.
2. **§D2 Espacio de métodos** → B2a (coordenadas) + B2b (solape Jaccard de los 12). Markdown: QFS=clase-mRMR salvo donde falla.
3. **§D3 Trayectoria en k** → B3 (macro-F1 y redundancia vs k; QFS vs contexto clásico + baseline).
4. **§D4 Escalera α** → B4 (cardinalidad y coste vs α, óptimo exacto = Mücke).
5. **§D5 β y geometría** → B5 (densidad Rydberg vs β + dist_ratio por dataset).
6. **§D9 Átomos** → B9 (recompute MDS por dataset; bloqueo, detuning, error). El bloque más nuevo.
7. **§D6 Modelos** → B6 (delta selección × modelo; el desplome de Madelon con XGBoost).
8. **§D7 Métricas** → B7 (macro-F1 vs AUC, binarios) [apéndice].
9. **§D8 Cadena de tests** → B8 (confusores descartados, transversal).
10. **§C Síntesis** → beeswarm SHAP por dataset (L4) + plano de atribución (clímax). Markdown: el "por qué" integrado.

**Reparto memoria:** cuerpo = A, B2, B3, B4, B9, atribución, beeswarm; apéndice = B5, B6, B7, B8 detalle.
Cada figura del cuerpo debe pasar la prueba de los 10s y responder una pregunta de defensa.

---

## Hallazgos ya verificados (no recomputar, sí construir)
- Mapa de métodos: `scripts/explor_mapa_metodos.py` (coords) + solape Jaccard (ver arriba).
- Atribución: `scripts/build_diagnostico_atribucion.py` → `diag_atribucion_qfs.png` (decomposición macro-F1).
- Beeswarm SHAP: `scripts/build_f6_shap_beeswarm.py` (BCW; propagar a Madelon + Olive por clase).
- dist_ratio por dataset (BCW .45 / Churn .35 / Madelon .35 / Olive .45) y β elegido: `qfs_operational_summary.csv`.
- Entorno: `/home/gosacar/miniconda3/envs/qfs_env/bin/python`. NO ejecutar hasta validación; este doc es el guion.
