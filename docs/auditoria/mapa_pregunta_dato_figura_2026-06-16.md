# Mapa pregunta → dato → figura

**Fecha:** 2026-06-16
**Fuente de verdad:** `docs/auditoria/inventario_tablas_2026-06-16.csv` (auditoría de tablas de Codex).
**Propósito:** convertir el inventario de tablas en la *especificación* del rediseño visual. Cada figura nace de una pregunta, con su tabla y su grano ya fijados, **antes** de elegir la forma. Antídoto contra los "volcados".

Regla operativa (flujo viz-definitive): `pregunta narrativa → tabla(s) del inventario → grano → familia visual candidata → nivel`. La familia visual es candidata, no dogma: se confirma con la regla del router, no se fuerza el dato a un molde (nada de "5 datasets ⇒ 5 paneles").

Niveles: **P** principal (cuerpo, ≤1 idea/figura) · **A** apéndice (densidad defendible) · **N** notebook (exploración íntegra).

---

## Parte 1 — Cobertura: dónde hay dato rico y dónde falta figura

Cruce de las familias del inventario con la espina narrativa (régimen → criterio/optimizador → mecanismo → resultado QFS → consistencia).

| Acto narrativo | Dato disponible (familias) | Riqueza | Estado figura |
|---|---|---|---|
| Regímenes-predictor por dataset | `01_raw_eda`, `04_split_audit`, `fs_input_dataset_summary` | media | débil |
| Perfil de selectores (criterio↔optimizador) | `05`: `fs_method_profiles`, `fs_jaccard_stability`, `fs_permutation_*`, `fs_boruta_confirmed_sets` | **alta** | a rehacer |
| Significancia y magnitud | `06`: `modeling_pairwise_comparison_tests`, `modeling_*_confidence_intervals`, `modeling_permutation_test_results` | alta | débil |
| Mecanismo (microdiagnóstico) | `06/shap`: 32 tablas (`modeling_shap_feature_importance`, `_values_summary`, per-config) | **muy alta** | infrautilizado |
| Coste vs rendimiento | `06`: `modeling_cost_performance`, `fs_all_execution_times` | media | a rehacer |
| Readout QFS α/β | `08`: `qfs_runs_<ds>_<beta>` (11β × 5 ds), `qfs_phase8_summary` | **muy alta** | infrautilizado |
| QFS calidad / oráculo | `08`: `qfs_quality_control_*`, `qfs_oracle_*` (×5 ds) | alta | infrautilizado |
| QFS vs clásico | `08`: `comparacion_qfs_*`, `contrastes_pareados_qfs`, `qfs_auc_binarios_contexto` | alta | a rehacer |
| Embedding / coste cuántico | `08`: `qfs_embedding_error`, `qfs_operational_summary` | media | parcial |
| Consistencia entre semillas | `05` jaccard + `10_memoria_b2/b10` | media | parcial |

**Huecos de mayor retorno** (dato sobrante, figura inexistente o pobre):
1. **Barrido β completo** (`qfs_runs_*_*`, 55 tablas) — hoy sin figura que lo muestre íntegro.
2. **SHAP** (32 tablas) — solo se usa beeswarm aislado; falta el cruce SHAP↔I_i (discordancia criterio).
3. **Contrastes pareados + intervalos** — la significancia estadística no tiene figura clara.

**Solapes / a retirar** (la regla "1 figura = 1 pregunta"): varias figuras actuales repiten el mismo readout (p. ej. múltiples vistas de Δ rendimiento). El roster definitivo debe colapsar estas a una por pregunta.

---

## Parte 2 — Índice maestro pregunta → dato → figura

### Acto 1 · Régimen: ¿qué tipo de problema es cada dataset?
- **P1.** *¿Cómo se reparten señal, dimensión y dificultad entre los 5 datasets?*
  Datos: `fs_input_dataset_summary`, `01_raw_eda/*`, `04_split_audit` (balance).
  Familia: tabla-gráfica / scatter de espacio-problema (dim vs señal vs n). Nivel **P**.

### Acto 2 · Criterio vs optimizador: ¿por qué QFS gana o pierde?
- **P2.** *¿Qué huella deja cada selector (estabilidad, coste, redundancia)?*
  Datos: `fs_method_profiles` (`segundos_medios`, `jaccard_medio`, `corr_media_seleccionada`).
  Familia: small-multiples por eje, identidad intra-dataset (criterio del router). Nivel **P**.
- **P3.** *¿Coinciden los selectores en qué variables eligen?*
  Datos: `fs_jaccard_stability`, `fs_qfs_pairwise_mi_matrix_long`.
  Familia: matriz/heatmap de solape con eje común. Nivel **P** (resumen) + **A** (12 métodos).
- **A1.** *¿Qué variables superan el nulo por permutación y cuánto?*
  Datos: `fs_permutation_empirical_pvalues`, `fs_permutation_summary`. Familia: strip eje-log compartido. Nivel **A**.

### Acto 3 · Mecanismo: ¿qué hace el modelo por dentro?
- **P4.** *¿Qué variables mueven la predicción y coinciden con lo que la MI rankea?*
  Datos: `modeling_shap_feature_importance` + `fs_qfs_mi_target_vector_long`.
  Familia: **cruce SHAP↔I_i** (scatter discordancia) — corazón del diagnóstico Madelon=criterio. Nivel **P**.
- **P5.** *¿Cómo se distribuye el efecto por instancia?* Datos: `modeling_shap_values_summary` (+ per-config). Familia: beeswarm. Nivel **P** (1 dataset clave) + **A** (resto).
- **A2.** *Mecanismo Churn:* qué suelta/conserva QFS. Datos: `modeling_shap_feature_importance` (churn) + `qfs_selected_all`. Familia: waterfall/deterioro. Nivel **A**. *(Caveat: deterioro 0.03 NO geométrico; no insinuar geometría.)*

### Acto 4 · Resultado QFS: ¿aporta frente a lo clásico?
- **P6.** *¿Cómo se comporta QFS al barrer β?*
  Datos: `qfs_runs_<ds>_0p0…1p0` (55 tablas) + `qfs_phase8_summary`.
  Familia: línea de cardinalidad/rendimiento vs β (escalera). Nivel **P** (síntesis) + **A** (paisaje completo). *(Caveat: α/β son del oráculo, no del simulador adiabático.)*
- **P7.** *¿Gana QFS al baseline clásico y es significativo?*
  Datos: `comparacion_qfs_vs_baseline`, `contrastes_pareados_qfs`, `qfs_auc_binarios_contexto`.
  Familia: slopegraph / Δ con IC. Nivel **P**.
- **P8.** *Tablero de cierre:* marcador final por dataset. Datos: `qfs_operational_summary` + `fase7_comparacion_final_con_qfs`. Familia: scorecard. Nivel **P** (clímax).

### Acto 5 · Consistencia y validez
- **A3.** *¿Qué baila entre semillas y qué se mantiene?* Datos: `10_memoria_b2_jaccard`, `10_memoria_b10_consistencia`. Familia: jaccard + sustitutos. Nivel **A**.
- **A4.** *Coste/embedding cuántico.* Datos: `qfs_embedding_error`, `qfs_operational_summary`. Familia: barras/strip. Nivel **A**.
- **A5.** *Controles (leakage, drift, splits).* Datos: `03_postprocessing_audit/*`, `04_split_audit/*`. Familia: panel de validez. Nivel **A**.

---

## Parte 3 — Profundidad: las 855 tablas no referenciadas como material visual

El inventario marca 855 tablas como "artefacto de fase sin referencia directa". **No son basura: son la profundidad computacional que hoy no se ve.** Asignación deliberada al nivel que las hace defendibles sin saturar el cuerpo:

| Familia granular | Nº | Qué encierra | Figura de profundidad | Nivel |
|---|---|---|---|---|
| `05/granular/<ds>/<sel>/k_*` | 500 | ranking por selector × k | rejilla 12-selectores × k (trayectoria densa real) | **A/N** |
| `06/experiments_validation` + `experiments_test` | 275 | métricas por configuración | paisaje por configuración (modelo × subconjunto) | **A/N** |
| `08/qfs_runs_<ds>_<beta>` | 55 | runs por β | paisaje α/β íntegro (apoya P6) | **A** |
| `06/shap` per-config | 32 | SHAP por config | apoyo a P4/P5 en apéndice | **A** |

Principio: el cuerpo cuenta **una** pregunta por figura; el apéndice/notebook exhibe la **densidad** que respalda que el experimento fue grande. Esto cierra la tensión registrada de "profundidad infracontada visualmente".

---

## Qué NO entra como figura (es input, no material)
- `data/selected_features/` (1260, 2.4 GB) — entradas de fase 6; su *contenido* solo aflora vía SHAP/per-instance.
- `predictions` (539 MB) — solo si se hace análisis de error por instancia.
- `previous_run_logs` (420), `.agents` (366), `legacy_qfs` — fuera del material de figura.

---

## Cómo se usa este mapa
1. Cada figura del rediseño se abre citando su fila aquí (pregunta + tabla + grano + nivel).
2. Si una figura no tiene fila → o falta la pregunta, o falta el dato (revisar inventario antes de dibujar).
3. Los caveats embebidos (one-hot Churn, α=oráculo, deterioro no geométrico) son de obligado respeto al componer.
4. Construcción: Claude monta las figuras (matplotlib), no se delega; el grano manda sobre el nº de paneles.
