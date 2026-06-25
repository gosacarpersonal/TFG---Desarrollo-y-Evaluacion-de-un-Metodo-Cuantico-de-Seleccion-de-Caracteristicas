# Revisión de la ejecución de Codex (Tier 1–4C)

> 2026-06-14. Revisión independiente de lo ejecutado por Codex, verificando contra el
> código real y los artefactos (no contra el reporte). Todo el trabajo de Codex está en
> working tree, SIN commitear.

## Veredicto general

Trabajo sólido en lo verificable (correctitud + fase cuántica). Saltó tareas editoriales
sin verificador. Los resultados son científicamente coherentes y, de hecho, **el control
de calidad produce el hallazgo más valioso del bloque cuántico**.

## Lo que está BIEN hecho (verificado en código/artefactos)

- **SHAP real (T1.1):** `shap_values_array` ya devuelve la matriz cruda;
  `shap_mean_abs_by_feature` colapsa solo para el ranking; `guardar_shap_crudo` persiste
  la matriz por instancia y por clase; `plot_shap_dataset` produce beeswarm real +
  desglose por clase en olive. Correcto.
- **Tie-break neutral (T1.2):** `SELECTOR_TIE_PRIORITY_BY_DATASET` eliminado.
- **XGBoost (T2.1):** añadido a `MODEL_NAMES` con wrapper `LabelEncodedXGBClassifier` y
  soporte SHAP (`TreeExplainer`). Cuatro modelos en el protocolo.
- **β (T4-A):** `distance_matrix_from_redundancy` añade `β(1+I_i)(1+I_j)` solo cuando
  R_ij≠0 (QFS_D2 eq 14); `β=0` reproduce el original (verificado). De paso corrigió un
  patrón latente del original (cálculo de min/max dentro del bucle → fuera, equivalente)
  y añadió guarda `max==min`.
- **Oráculo Q*(α) + Mücke (T4-A):** `oracle_Q_star` (enumeración ≤20 / Gurobi) y
  `mucke_alpha_for_k` (búsqueda binaria). `verify_fase8_solver.py` pasa de forma
  independiente (5 checks verdes; enumeración rápida).
- **Reglas duras respetadas:** ningún `_OG.py` tocado; capítulos 1-3 y `metodologia.tex`
  intactos; no se movió lógica inline de 1-4 a `src`.
- **Editoriales hechas:** fase 1 (COLUMNAS_PRESENTACION tocado), fase 2 (celda 222→134
  líneas), fase 4 (nota chi² reforzada).

## Lo que SALTÓ o quedó a medias (tareas sin verificador)

- **T3.3 — fase 3 NO tocada:** los heatmaps `fase3_asociacion`×4 y `fase3_redundancia`×4
  que duplican tablas siguen ahí (6 referencias en el generador). Sin hacer.
- **T2.2 paso-2 en fase 5 y 7:** generadores `rebuild_fase5/7` no modificados → el núcleo
  metodológico de esas fases sigue invocándose desde `src` sin verse construir. (Solo
  fase 6 recibió el paso 2.)
- **T2.3 — `UMBRAL_EFECTO_PRACTICO`:** sigue descrito cualitativamente; no se añadió
  justificación explícita del valor.
- **T3.2 parcial:** la celda de fase 2 bajó a 134 líneas, no a ~80.

Ninguno es bloqueante; son los puntos BAJOS/editoriales. Codex priorizó lo verificable.

## Ajustes de Codex revisados (los 4 que reportó)

1. **customer_churn con 15 vars (no 10):** correcto, son 10 crudas + one-hot de 3
   categóricas (gender, subscription_type, contract_length) → 15. Usó la fuente primaria.
   Cabe en la envolvente ≤20, sin pre-selección. OK. (Nota: el plan decía 10; la realidad
   es 15. Actualizar el plan/memoria si se cita el número.)
2. **Desacople de `ahs_utils`:** try/except sobre helpers de visualización opcionales.
   Limpio, no afecta a la lógica del solver. OK.
3. **`dist_ratio` 0.45/0.35/0.25 en vez de 1/√2 (`QFS_DIST_RATIOS`):** NO es un atajo
   no-cuántico. Es la fracción del radio de bloqueo para el MDS; el `1/√2` del paper no
   encontraba geometría embebible y se prueban ratios menores, guardando el usado por CSV
   y lanzando error si ninguno funciona. **ES una divergencia del paper que hay que
   declarar** en resultados, y puede estar relacionada con el fallo del optimizador en
   churn (ver abajo).
4. **Baseline test de fase 6:** el artefacto real solo guarda el baseline final por
   dataset; la comparación QFS usa ese baseline archivado sin reentrenar. Correcto.

## Resultados QFS — coherentes y con un hallazgo clave

| Dataset | baseline | QFS-NA | QFS-oráculo | veredicto |
|---|---|---|---|---|
| breast_cancer_wisconsin | 0.937 | 0.950 (+0.013) | 0.937 (0) | equivalente |
| customer_churn | 0.9998 | 0.922 (−0.078) | 0.9991 (−0.001) | deterioro |
| madelon | 0.813 | 0.633 (−0.180) | 0.643 (−0.170) | deterioro |
| olive_oil_3class | 1.000 | 1.000 | 1.000 | equivalente |
| olive_oil_9class | 0.839 | 0.842 | 0.906 | equivalente |

**Hallazgo más valioso (control de calidad oráculo vs analógico):**

- **madelon:** `Δcoste ≈ −0.01` (el simulador casi alcanza el óptimo del QUBO), pero
  ambos (NA y oráculo) rinden ~0.63 → **el criterio MI falla**. Es la limitación esperada:
  la información mutua es ciega a las interacciones XOR de madelon. Hallazgo fuerte y
  defendible (QFS hereda la ceguera de la MI a las interacciones de orden superior).
- **customer_churn:** `Δcoste = +1.32` (NA=1.17 vs óptimo=−0.15), Hamming 8/10 → **el
  optimizador analógico falló**; el oráculo, que sí optimiza, casi iguala el baseline
  (0.999). El deterioro −0.078 es de la implementación analógica, no del criterio.

Esta **distinción criterio-vs-optimizador** es justo lo que el control de calidad se
diseñó para revelar (`metodologia.tex` sec:contrato). Es el mejor resultado del bloque
cuántico y debe ser el eje de la discusión.

## Consecuencia importante de añadir XGBoost (afecta a la narrativa)

Con XGBoost como baseline, el resultado estrella del bloque clásico **cambia de magnitud**:
- madelon: baseline pasó de 0.613 (modelos lineales/RF) a **0.813** (XGBoost maneja mejor
  la alta dimensión). La mejora por selección encoge de **+0.280 a +0.094**.
- Versiones previas de `conclusiones.tex` y `resultados.tex` afirmaban "+0.280
  en madelon". Esa cifra debe quedar reemplazada por la lectura XGBoost-aware:
  la mejora sigue siendo significativa, pero menor y dependiente del modelo.

## Cosas a declarar en la memoria al escribir resultados

1. La divergencia `dist_ratio` (0.45–0.25 vs 1/√2 del paper) y su posible efecto en el
   fallo del optimizador analógico en churn.
2. El baseline near-perfect de customer_churn (0.9998): a techo, la comparación es poco
   informativa (cualquier selección parece deterioro). Caveat explícito.
3. La distinción criterio-vs-optimizador (madelon vs churn) como hallazgo central.
4. Las cifras XGBoost-aware (madelon +0.094, no +0.280).

## Housekeeping pendiente

- Nada commiteado: todo en working tree.
- `__pycache__/` sin gitignorar (varios `.pyc` untracked). Añadir a `.gitignore`.
- `ejemplo-memoria.pdf` regenerado pero ningún `.tex` modificado → recompilación; OK.

## Recomendación de cierre

1. Completar lo saltado solo si aporta: T3.3 (fase 3 heatmaps) y T2.2 paso-2 en 5/7 son
   editoriales; valen para la entrega pero no afectan a la ciencia. T2.3 (umbral) sí
   conviene justificarlo.
2. Reescribir `resultados.tex` y `conclusiones.tex` con: cifras XGBoost-aware, el hallazgo
   criterio-vs-optimizador, y los caveats (dist_ratio, churn a techo).
3. `.gitignore` para `__pycache__`, y commitear por bloques (correctitud / fase cuántica /
   editorial).
