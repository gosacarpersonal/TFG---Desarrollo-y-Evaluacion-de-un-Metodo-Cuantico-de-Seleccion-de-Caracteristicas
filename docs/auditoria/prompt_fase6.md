# Prompt de arreglo — Fase 6

Lógica en `src/phase6_modeling/pipeline.py`; notebook generado por
`scripts/rebuild_fase6_notebook.py` (`notebooks/fase6.ipynb`). Respeta
`docs/estilo_redaccion_tfg.md` y `docs/auditoria/estructura_notebooks.md`. Regenera y
valida con `scripts/verify_fase6_notebook.py`.

Arregla estos fallos verificados:

1. **[CRÍTICO] SHAP desperdiciado.** `shap_candidato` (`pipeline.py:568`) calcula el
   objeto SHAP completo (signo, por instancia, por clase), pero `shap_values_array`
   (`:554-565`) lo colapsa a media|SHAP| (`np.mean(np.abs(values), axis=(0,2))`, `:560`)
   antes de guardar nada, y `plot_shap_dataset` (`:633-641`) es un `sns.barplot`, no un
   beeswarm —pese a que el fichero se llama `shap_summary_*`. Arréglalo:
   - **Persistir la matriz SHAP cruda** (valores con signo por instancia y, en
     multiclase, por clase) por candidato, no solo el ranking media|SHAP|.
   - **Dibujar un beeswarm real** con `shap.summary_plot(explanation, ...)` por
     modelo-dataset, conservando el nombre `shap_summary_*` (que ahora sí lo será).
   - En `olive_oil_3class` y `olive_oil_9class`, **desglose por clase** (las clases
     importan para interpretar la dirección del efecto).
   - Mantén el barplot de media|SHAP| si quieres, pero como complemento, no como único
     gráfico.
   - Añade en el cuaderno la lectura: qué variable empuja hacia qué clase y con qué
     dispersión por instancia.

2. **[MEDIO — defensibilidad] Tie-break hardcodeado por dataset.**
   `SELECTOR_TIE_PRIORITY_BY_DATASET` (`:53-63`) fija prioridades de desempate solo para
   `breast_cancer_wisconsin` y `olive_oil_3class`, sin justificación. Aunque solo rompe
   empates exactos (`:396-399`), es una elección post-hoc no defendible. Sustitúyela por
   un desempate **neutral y determinista** (p. ej. orden alfabético del selector) o
   justifica cada prioridad explícitamente en el texto. Reejecuta y comprueba que la
   selección de candidatos a test no cambia de forma que invalide conclusiones.

3. **[MEDIO — estructura, paso 2] Mostrar la creación del núcleo.** El cuaderno YA narra
   por dataset (§6.6) y por figura (§6.12) — eso NO se toca. Falta el paso 2: el protocolo
   que constituye el aporte (cálculo SHAP, bootstrap, permutaciones pareadas y de
   etiquetas) se invoca con `p6.*` sin verse construir. Sube al cuaderno la creación
   visible de al menos el cálculo SHAP (el del punto 1) y del contraste estadístico,
   dejando en `src` solo el plumbing. Acepta que el cuaderno se alargue. Ver
   `estructura_notebooks.md`.

4. **[DECISIÓN APROBADA — añadir XGBoost al protocolo].** Las decisiones del usuario
   (2026-06-14) y la memoria actualizada (`metodologia.tex`) fijan el protocolo en
   **cuatro** modelos: logistic_regression + linear_svm + random_forest + xgboost, todos
   con hiperparámetros fijos y pesos balanceados. Añade `"xgboost"` a `MODEL_NAMES`
   (`src/phase6_modeling/pipeline.py:52`) y configura el clasificador con
   `XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.1, subsample=0.8,
   colsample_bytree=0.8, tree_method="hist", random_state=RANDOM_STATE)` (valores
   defendibles y coherentes con el orden de magnitud de la grilla de PAPER_QFS §VII; no
   se realiza búsqueda, como dicta el protocolo). La métrica primaria sigue siendo
   macro-F1; añade `auc_roc` como métrica secundaria que solo se calcula en los datasets
   binarios (`breast_cancer_wisconsin`, `customer_churn`) y se registra como contexto
   frente al paper. Coste: ~25 % más experimentos en validation (4 modelos × 12
   selectores × 5 datasets = 240 experimentos).

Criterio de aceptación: existen beeswarms reales por modelo-dataset (y por clase en
olive); la matriz SHAP cruda se persiste; el desempate es neutral o justificado; el
cálculo SHAP y el contraste se ven construir en el cuaderno; ancla de comparabilidad con
los papers (XGBoost+AUC+Boruta) presente o su ausencia justificada;
`verify_fase6_notebook.py` pasa.
