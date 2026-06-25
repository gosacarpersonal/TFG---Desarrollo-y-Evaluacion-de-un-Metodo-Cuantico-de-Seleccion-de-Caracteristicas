# Roster detallado de figuras de la memoria

**Fecha:** 2026-06-16
**Base:** [mapa_pregunta_dato_figura_2026-06-16.md](mapa_pregunta_dato_figura_2026-06-16.md) + columnas reales verificadas.
**Convención:** cada figura = **una** pregunta. Origen = tabla(s) + claves de join + columnas. Nivel **P** (cuerpo) / **A** (apéndice).
Notación join: `A ⋈[claves] B`.

---

## BLOQUE A — Planteamiento: ¿qué tipo de problema es cada dataset?

### F1 · Espacio-problema de los 5 datasets · **P**
- **Pregunta:** ¿cómo se reparten dimensión, tamaño y dificultad entre datasets?
- **Origen:** `05/fs_input_dataset_summary` (`dataset, n_train, n_validation, n_test, n_features, n_classes_train, minority_class_train_pct`).
- **Dibuja:** un punto por dataset; x = `n_features` (log), y = `n_train`, tamaño/color = `n_classes_train`, marca = desbalance (`minority_class_train_pct`).
- **Familia:** scatter de espacio-problema con etiquetas.
- **Qué verás:** de un vistazo, que Madelon (500 feat, 2 clases, mucha señal-trampa) y Churn (one-hot, desbalance) y Olive (pocas muestras, multiclase) son problemas *distintos* → justifica leer cada uno por su régimen.

---

## BLOQUE B — Selección clásica: la huella de los selectores

### F2 · Huella de los 12 selectores: coste · estabilidad · redundancia · **P**
- **Pregunta:** ¿qué perfil tiene cada selector más allá del acierto?
- **Origen:** `05/fs_method_profiles` (`method, segundos_medios, jaccard_medio, corr_media_seleccionada`).
- **Dibuja:** un punto por método; x = `jaccard_medio` (estabilidad), y = `corr_media_seleccionada` (redundancia que deja), tamaño = `segundos_medios` (coste, escala log).
- **Familia:** scatter de perfil (3 variables en 1 plano).
- **Qué verás:** quién es estable-barato-poco-redundante vs lo contrario; sitúa a QFS-NA frente a los clásicos como selector tipo-mRMR.

### F3 · ¿Eligen lo mismo los métodos? (solape) · **P** + **A**
- **Pregunta:** ¿qué métodos seleccionan subconjuntos parecidos?
- **Origen:** `05/fs_jaccard_stability` (`dataset, method, k, seed_a, seed_b, jaccard`) agregada por `(dataset, method)`; resumen narrativo en `10_memoria_b2_jaccard_metodos` (`dataset, method, jaccard, rel, red`).
- **Dibuja:** **P** = heatmap de Jaccard medio método×método para 1 dataset representativo; **A** = los 5 datasets (small-multiples).
- **Familia:** matriz de solape con eje común.
- **Qué verás:** familias de métodos que convergen y cuáles divergen; base de "los sustitutos equivalentes".

### F4 · Señal real sobre el nulo (permutación) · **A**
- **Pregunta:** ¿qué variables se separan del azar y cuánto?
- **Origen:** `05/fs_permutation_empirical_pvalues` (`dataset, method, feature, real_score, null_p95, empirical_p_value, above_null_p95, n_permutations`).
- **Dibuja:** strip por dataset; x = `real_score − null_p95` (distancia al nulo, eje compartido), color = `above_null_p95`.
- **Familia:** strip eje-log compartido.
- **Qué verás:** en Madelon la mayoría de variables apenas superan el nulo (I_i≈0.02) → la dificultad no está en la MI univariante.

---

## BLOQUE C — Modelado y mecanismo

### F5 · Significancia y magnitud: ¿la mejora es real? · **P**
- **Pregunta:** ¿el mejor candidato bate al baseline con significancia?
- **Origen:** `06/modeling_pairwise_comparison_tests` (`dataset, baseline_experiment_id, candidate_experiment_id, difference_macro_f1, ci_low, ci_high, sign_permutation_p_value`) ⋈[`candidate_experiment_id = experiment_id`] `06/modeling_test_results_candidates` (para etiqueta `selector, model_name, k`).
- **Dibuja:** forest plot por dataset; punto = `difference_macro_f1`, barra = [`ci_low, ci_high`], marca de significancia por `sign_permutation_p_value`.
- **Familia:** forest plot / Δ con IC.
- **Qué verás:** dónde el intervalo cruza 0 (no significativo) y dónde no → separa mejora sustantiva de ruido.

### F6 · Coste vs rendimiento: ¿cuánto cuesta reducir? · **P**
- **Pregunta:** ¿qué se gana/pierde al recortar variables?
- **Origen:** `06/modeling_cost_performance` (`dataset, selector, k, feature_reduction_ratio, delta_macro_f1_vs_same_model_baseline, fit_seconds, ...`).
- **Dibuja:** x = `feature_reduction_ratio`, y = `delta_macro_f1_vs_same_model_baseline`, por dataset; línea de "sin cambio" en y=0.
- **Familia:** scatter coste-beneficio.
- **Qué verás:** que se puede tirar el 90 % de features sin perder F1 (o ganando) en varios datasets → el argumento de eficiencia.

### F7 · ⭐ Discordancia SHAP ↔ MI: el corazón del diagnóstico · **P**
- **Pregunta:** ¿lo que el modelo usa coincide con lo que la MI rankea?
- **Origen:** `06/modeling_shap_feature_importance` (`dataset, feature, mean_abs_shap`) ⋈[`dataset, feature`] `05/fs_qfs_mi_target_vector_long` (`dataset, feature, I_i`).
- **Dibuja:** scatter por dataset; x = `I_i` (lo que ve la MI), y = `mean_abs_shap` (lo que usa el modelo); resalta el cuadrante alto-SHAP/baja-MI.
- **Familia:** scatter de discordancia con cuadrantes.
- **Qué verás:** en Madelon, variables como `feat_336/105/153` con SHAP alto pero MI plana → **prueba visual de que el fallo es de criterio** (la MI no las ve), no del optimizador.

### F8 · SHAP beeswarm del dataset clave · **P** (+ resto en **A**)
- **Pregunta:** ¿cómo se reparte el efecto por instancia y signo?
- **Origen:** `06/shap/modeling_shap_values_full_*` (valores por instancia) del dataset elegido; resto a apéndice.
- **Dibuja:** beeswarm SHAP estándar, top features.
- **Familia:** beeswarm.
- **Qué verás:** dirección y dispersión del efecto de cada variable; complementa F7 con el "cómo".

---

## BLOQUE D — QFS (cuántico)

### F9 · Escalera α/β: QFS al barrer β · **P** (síntesis) + **A** (paisaje)
- **Pregunta:** ¿cómo cambian cardinalidad y rendimiento al mover β?
- **Origen:** `08/qfs_phase8_summary` o `08/qfs_selected_all` (`dataset, alpha, beta, k, n_features, validation_macro_f1`); densidad de ocupación en `08/qfs_operational_summary` (`dataset, beta, k, mean_density_selected, mean_density_unselected`).
- **Dibuja:** **P** = línea por dataset, x = `beta`, y = `validation_macro_f1` con `n_features` anotado; **A** = paisaje completo con los 11 β × 5 datasets desde `08/qfs_runs_<ds>_<beta>` (55 tablas).
- **Familia:** línea de cardinalidad/rendimiento.
- **Qué verás:** cómo β regula la presión de selección; *caveat embebido: α/β son del oráculo, no del simulador adiabático.*

### F10 · QFS vs baseline clásico: ¿aporta? · **P**
- **Pregunta:** ¿bate QFS al clásico y con qué significancia?
- **Origen:** `08/comparacion_qfs_vs_baseline` (`dataset, delta_test_macro_f1, delta_ci_low, delta_ci_high, p_valor_pareado_fdr, veredicto`). Autocontenida.
- **Dibuja:** Δ con IC por dataset, color/etiqueta = `veredicto`, marca FDR.
- **Familia:** Δ con IC / slopegraph baseline→QFS.
- **Qué verás:** dónde QFS empata, gana o pierde, ya con corrección por comparaciones múltiples.

### F11 · Control de calidad QFS: QFS-NA vs oráculo · **P**/**A**
- **Pregunta:** ¿el solver alcanza lo que el oráculo dice óptimo?
- **Origen:** `08/qfs_quality_control_<dataset>` ×5 concatenadas (`dataset, beta, k, hamming_distance, delta_cost_alpha05, qfs_na_features, oracle_features`).
- **Dibuja:** por dataset, `hamming_distance` (QFS-NA vs oráculo) y `delta_cost_alpha05` vs β.
- **Familia:** strip/línea de discrepancia.
- **Qué verás:** la lectura criterio↔optimizador por vía cuántica independiente: dónde falla el *criterio* (Madelon) vs el *optimizador* (Churn, Hamming pequeño pero deterioro leve). *Caveat: deterioro Churn 0.03 NO geométrico.*

### F12 · 🏁 Tablero de cierre: marcador final por dataset · **P** (clímax)
- **Pregunta:** ¿cuál es el veredicto global baseline vs selección vs QFS?
- **Origen:** `07/fase7_comparacion_final_con_qfs` (`dataset, baseline_test_macro_f1, seleccion_test_macro_f1, qfs_test_macro_f1, delta_test_macro_f1, p_valor_pareado_fdr, veredicto`). Autocontenida.
- **Dibuja:** scorecard: 3 columnas (baseline / mejor clásico / QFS) × 5 datasets, con Δ, p-FDR y veredicto.
- **Familia:** scorecard de evidencia.
- **Qué verás:** la conclusión del TFG de un golpe: régimen → quién gana y si la diferencia es real.

---

## BLOQUE E — Profundidad (apéndice/notebook): hacer visible la escala

| ID | Pregunta | Origen | Familia | Nivel |
|---|---|---|---|---|
| **A-grid** | trayectoria de selección de las 12 técnicas × k | `05/granular/<ds>/<sel>/k_*` (500) o `fs_all_selected_features` filtrado | rejilla método×k | A/N |
| **A-config** | paisaje de rendimiento por configuración | `06/modeling_cost_performance` (todas las filas) o `experiments_validation/test` (275) | small-multiples modelo×subconjunto | A/N |
| **A-beta** | paisaje β íntegro + densidad de ocupación | `08/qfs_runs_<ds>_<beta>` (55) `density__feat_*` | heatmap ocupación × β | A |
| **A-embed** | coste/error de embedding cuántico | `08/qfs_embedding_error` (`embedding_error_mean/p95, dist_ratio_rydberg`) | barras/strip | A |
| **A-consist** | qué baila entre semillas y qué se mantiene | `10_memoria_b2_jaccard_metodos` + `10_memoria_b10_consistencia` | jaccard + sustitutos | A |
| **A-control** | validez: leakage, drift, splits | `03_postprocessing_audit/*`, `04_split_audit/*` | panel de validez | A |
| **A-auc** | contexto AUC en binarios | `08/qfs_auc_binarios_contexto` (`dataset, fuente, model_name, auc_roc`) | barras agrupadas | A |

---

## Resumen del roster
- **Cuerpo (P):** F1–F12 (12 figuras), una pregunta cada una, cubren régimen → selección → mecanismo → QFS → cierre.
- **Apéndice (A):** F3/F4/F8 extendidas + A-grid/config/beta/embed/consist/control/auc.
- **Joins reales clave:** F5 (`pairwise ⋈ candidates`), F7 (`shap ⋈ MI`); el resto son autocontenidas o concatenación por dataset.
- **Caveats de obligado respeto:** α/β=oráculo (F9), deterioro Churn no geométrico (F11), one-hot Churn no monótono.

## Pendiente de decisión del autor
1. Dataset "clave" para F8 en el cuerpo (candidato: Madelon, por ser el caso criterio).
2. Si F11 va a cuerpo o apéndice (es potente pero técnico).
3. Confirmar que el orden F1→F12 calza con el índice de capítulos de la memoria.
