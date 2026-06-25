# Especificación de figuras de la memoria — versión elevada (composiciones)

> 2026-06-15. Re-planteamiento tras estudiar a fondo `.agents/viz-definitive` (las cinco
> puertas, la taxonomía de 35 familias, el router de figuras combinadas y la capa TFG).
> Supersede la versión anterior. Cambio de filosofía: **dejamos de pensar en gráficos
> sueltos y pasamos a argumentos compuestos** — cada figura de cuerpo es un multipanel o
> una figura por capas donde cada panel/capa tiene un rol no redundante (resultado ·
> mecanismo · coste · incertidumbre · estabilidad · subgrupo). Así colapsamos ~16 gráficos
> aislados en ~10 figuras que narran mucho más.
>
> Cada figura lleva el registro de decisión del skill (compacto): clase TFG · pregunta ·
> familias (de las 35) · composición + por qué no único / por qué no separadas · roles de
> panel · protagonista · título/subtítulo · anotaciones · paleta · caveats · tablas.

## Paleta (editorial warmth, `src/viz_core/config.py`) — estable en TODO el TFG
Fondo `#f7f4ef` · texto `#3b3b3b` · contexto/baseline `#bdbdbd` · énfasis `#d95f5f` ·
secundario `#4f81bd` · datasets {bcw `#a9bfd6`, churn `#d9b382`, madelon `#c7d59f`,
olive_3 `#d7a6a1`, olive_9 `#8fb7a8`} · familias de método {relevancia `#a9bfd6`,
redundancia `#d9b382`, combinado `#c7d59f`, wrapper `#d7a6a1`, embedded `#8fb7a8`}.
Patrón de cabecera: **título = hallazgo**, subtítulo = contexto/métrica/n; gris el
contexto, color solo la evidencia; ≤3 anotaciones. Helpers: `src/viz_core/editorial_warmth.py`.

Principio rector aplicado: *plot the answer, not the column* (métrica derivada antes de
dibujar) y *prefer removing over polishing*. Familias citadas por su número en la
taxonomía de 35.

---

# CUERPO — 10 argumentos compuestos (todos memory_candidate)

## F1 — "Un banco heterogéneo que obliga a elegir bien la métrica"
- **Pregunta central:** ¿es el reto diverso y qué métrica exige?
- **Composición:** multipanel 2 (cross-family). **Por qué no único:** mezcla escala de
  tamaño/dimensión con recomendación de métrica. **Por qué no separadas:** la diversidad
  *justifica* la métrica; es un solo argumento.
  - **Panel A (rol: panorama)** — familia **23 bubble plot**: x=filas (log), y=variables
    (log), tamaño=ratio de desbalance, color=dataset; etiquetas directas.
  - **Panel B (rol: decisión)** — familia **1 barras H** + scorecard: desbalance por
    dataset (ratio mayoría/minoría y nº clases) con una línea de lectura → "por eso
    macro-F1, no exactitud".
- **Protagonista:** madelon (4 filas/var) y olive_9 (9 clases, desbalance).
- **Título:** "Un banco de pruebas que cubre tamaño, dimensión y desbalance".
  **Subtítulo:** "Cinco formulaciones; el desbalance multiclase motiva el uso de macro-F1".
- **Paleta:** colores de dataset; énfasis en los extremos.
- **Caveats:** ejes log etiquetados; el área de burbuja se lee con cautela (anotar valores).
- **Tablas:** `01_raw_eda/` estructura + tabla de desbalance del target. **Plotter:** nuevo.
- **Sustituye:** Q1, Q2.

## F2 — "La señal es real, pero en Madelon casi no es univariante" (signal + FDR + efecto)
- **Pregunta:** ¿la asociación con el target es real tras multiplicidad y de qué magnitud?
- **Composición:** multipanel 2 (combo canónico del skill *signal + FDR + effect size*).
  **Por qué no único:** recuento y magnitud son ejes distintos que no deben confundirse.
  - **Panel A (rol: resultado)** — familia **5 dot/Cleveland**: por dataset, fracción de
    variables que superan FDR 0.05 (anotar k/total).
  - **Panel B (rol: magnitud)** — familia **5 dot** o **20 strip**: efecto absoluto
    mediano y máximo por dataset.
- **Protagonista:** madelon (13/500, efecto 0.02) resaltado en rojo en ambos paneles →
  *anticipa* el límite de criterio de QFS (anotación puente).
- **Título:** "La señal supervisada es real, pero en Madelon apenas es univariante".
  **Subtítulo:** "Variables que superan FDR 0.05 y tamaño de efecto, por dataset".
- **Paleta:** datasets; madelon `#d95f5f`; resto contexto.
- **Caveats:** separar recuento de magnitud; FDR Benjamini-Hochberg.
- **Tablas:** `fase1_asociacion_target_resumen.csv` (`variables_fdr_005`,
  `variables_contrastadas`, `efecto_abs_mediano`, `efecto_abs_maximo`). **Plotter:** nuevo.
- **Sustituye:** Q3.

## F3 — "Se puede confiar en la base" (representatividad + drift + conservación)
- **Pregunta:** ¿datos, particiones y preprocesado son fiables antes de comparar?
- **Composición:** multipanel 3 (combo *data quality + affected variables + next action*;
  tres-panel roles A/B/C). **Por qué no separadas:** las tres son la misma afirmación
  "la base no sesga".
  - **Panel A (rol: resultado)** — familia **5 dot + banda**: AUC adversarial por dataset
    con banda 0.45–0.55 y línea 0.5 (particiones intercambiables).
  - **Panel B (rol: mecanismo/cautela)** — familia **2 barras agrupadas + umbral**: max
    PSI/KS/Wasserstein por dataset con líneas de umbral; anotar nº de flags.
  - **Panel C (rol: validación)** — familia **10 slopegraph** o **5 dot**: Spearman de
    rankings MI raw→processed por dataset (~1.0).
- **Protagonista:** la coherencia transversal (todos compatibles con base limpia).
- **Título:** "Particiones intercambiables, drift acotado y preprocesado fiel".
  **Subtítulo:** "AUC adversarial ≈ 0.5, PSI/KS bajo umbral y rankings de MI conservados".
- **Paleta:** datasets; bandas/umbrales en contexto; rojo solo si algo violara umbral.
- **Caveats:** AUC≈0.5 es lo bueno (contraintuitivo, anotarlo); drift = cautela, no defecto.
- **Tablas:** `fase4_validacion_adversarial.csv`, `fase4_drift_resumen.csv`,
  `fase3_asociacion_tests.csv`. **Plotter:** nuevo (3 paneles, reusa lógica adversarial).
- **Sustituye:** Q5, Q6, Q4 (sube Q4 al cuerpo dentro de esta figura; leakage Q7 → apéndice).

## F4 — "Los doce selectores: redundancia, coste, estabilidad y señal" (four-panel insignia)
- **Pregunta:** ¿qué selector es preferible y por qué? (patrón canónico del skill,
  ampliado a 4 paneles por decisión del autor).
- **Composición:** multipanel 4 en rejilla 2×2 (roles A=diferenciador, B=coste,
  C=estabilidad, D=señal vs azar). **Por qué no único:** una conclusión solo-de-rendimiento
  engañaría; parsimonia, estabilidad y separación del nulo cambian la lectura. **Por qué 4
  y no 3:** la separación frente al azar es una garantía independiente que cierra el perfil.
  - **Panel A (rol: diferenciador)** — familia **5 dot/lollipop base 0**: delta de
    redundancia interna por método (mRMR único ≤0).
  - **Panel B (rol: coste)** — familia **1 barras H (log)**: tiempo medio por método,
    color por familia (filtros 0.007s … Boruta 2.5s).
  - **Panel C (rol: estabilidad)** — familia **5 dot**: Jaccard medio por método.
  - **Panel D (rol: señal vs azar)** — familia **28 heatmap** compacto (método×dataset) o
    **5 dot**: variables sobre el p95 nulo por método, confirmando que la selección no es
    ruido.
- **Orden compartido** de métodos en los cuatro paneles; color por familia consistente;
  una sola leyenda de familia para toda la figura (no repetir por panel).
- **Protagonista:** mRMR (baja redundancia, coste moderado) frente a Boruta (caro, fiable).
- **Título:** "mRMR controla la redundancia con coste moderado; los wrappers la pagan en
  tiempo". **Subtítulo:** "Perfil de los doce selectores: redundancia, coste, estabilidad y
  separación del azar".
- **Paleta:** 5 colores de familia; mRMR/Boruta anotados.
- **Caveats:** tiempo = ajuste, no inferencia; escala log; perfil promedia datasets.
- **Tablas:** `fs_method_profiles.csv` (`segundos_medios`, `jaccard_medio`,
  `corr_media_seleccionada`), `fs_redundancy_*`. **Plotter:** nuevo (compose_panels).
- **Sustituye:** Q8, Q9, Q10, Q11, Q12. (La selección por método y el roster completo → apéndice.)

## F5 — "Menos variables, igual o mejor rendimiento" (coste–rendimiento, small multiples)
- **Pregunta:** ¿la reducción dimensional mantiene/mejora el rendimiento?
- **Composición:** small multiples (familia **22 scatter** + capa de línea + frontera) por
  dataset, escalas compartidas por eje y. **Por qué small multiples:** la identidad por
  dataset importa; no se promedian regímenes.
  - Cada panel: x=nº variables (log), y=macro-F1; puntos=(selector,modelo); línea
    horizontal=baseline del mismo modelo; frontera de Pareto resaltada; anotar k de
    referencia.
- **Protagonista:** la frontera (subconjuntos compactos que igualan/superan baseline);
  madelon como caso donde la reducción es necesaria.
- **Título:** "La selección recupera o mejora el rendimiento con una fracción de las
  variables". **Subtítulo:** "Macro-F1 frente al número de variables; línea = baseline del
  mismo modelo".
- **Paleta:** puntos `#bdbdbd`; frontera `#d95f5f`; baseline `#4f81bd` discontinuo.
- **Caveats:** un panel por dataset; x log; no promediar.
- **Tablas:** `06_modeling/modeling_cost_performance.csv` (`n_features`, `macro_f1`,
  `baseline_macro_f1_same_model`, `model_name`). **Plotter:** nuevo. **Sustituye:** Q13.

## F6 — "Qué variables sostienen el modelo" (SHAP beeswarm)
- **Pregunta:** ¿qué variables explican cada modelo y en qué dirección?
- **Composición:** small multiples de **20 beeswarm** (2 en cuerpo: bcw y madelon; olive
  por clase → apéndice). Capa única por panel (el beeswarm ya es denso).
- **Protagonista:** las 2-3 variables top y su dirección; en madelon, que las variables
  útiles NO son las de mayor MI univariante (enlaza con F2 y con el fallo de QFS).
- **Título:** "Las variables que sostienen el modelo coinciden con la selección".
  **Subtítulo:** "Valores SHAP por instancia del mejor candidato; color = valor de la
  variable".
- **Paleta:** divergente `#4f81bd`→`#d95f5f` (re-tematizar el colormap SHAP al sistema).
- **Caveats:** SHAP explica el modelo, no causalidad; por instancia, no media.
- **Tablas:** `06_modeling/modeling_shap_values_full_*.csv` + `*feature_values_*`.
  **Plotter:** ya generado → copiar/re-tematizar. **Sustituye:** Q14.

## F7 — "Igualar no es mejorar: significancia frente a magnitud" (resultado + lectura honesta)
- **Pregunta:** ¿la selección mejora al baseline y cómo debe leerse?
- **Composición:** multipanel 2 (combo *aggregate result + uncertainty*; A resultado, B
  matiz). **Por qué no único:** el veredicto y su matiz (umbral práctico) son dos lecturas.
  - **Panel A (rol: resultado)** — familia **5 dot + IC**: baseline vs mejor selección en
    test con IC bootstrap por dataset.
  - **Panel B (rol: incertidumbre/lectura)** — familia **5 dot/dumbbell**: delta pareado
    con IC y línea de umbral de efecto práctico (0.01); churn protagonista.
- **Protagonista:** madelon (única mejora significativa) y churn (significativo pero por
  debajo del umbral).
- **Título:** "La selección iguala al baseline; solo Madelon mejora de forma relevante".
  **Subtítulo:** "Macro-F1 en test e IC bootstrap 95%; umbral de efecto práctico 0.01".
- **Paleta:** baseline `#bdbdbd`, selección `#4f81bd`, mejora `#d95f5f`; umbral discontinuo.
- **Caveats:** IC visibles; churn a techo (anotar). **Tablas:**
  `fase7_test_baseline_vs_seleccion` + `fase7_tabla_maestra.csv`. **Plotter:** reutilizar A,
  nuevo B. **Sustituye:** Q16, Q17.

## F8 — "Los dos mandos de QFS: α fija el tamaño, β reordena" (teoría + mecanismo)
- **Pregunta:** ¿cómo controlan α y β la selección cuántica?
- **Composición:** multipanel 2 (A teoría, B operativo). **Por qué no separadas:** son los
  dos grados de libertad del mismo método.
  - **Panel A (rol: teoría→práctica)** — familia **10/8 escalera (step line)**: α (x) vs
    cardinalidad del óptimo exacto (y) por dataset; marcar el α del k de referencia.
  - **Panel B (rol: mecanismo)** — familia **28 heatmap**: densidad de Rydberg por
    variable × β (madelon).
- **Protagonista:** la monotonía α↔k (Proposición 1) y cómo β reordena.
- **Título:** "α recorre la escalera de presupuestos; β reordena las candidatas".
  **Subtítulo:** "Óptimo exacto del QUBO frente a α (izq.) y densidad de Rydberg frente a β
  (der., Madelon)".
- **Paleta:** datasets en A; secuencial cálida en B.
- **Caveats fuertes:** Panel A es el QUBO EXACTO (oráculo), no el simulador (que fija α).
- **Tablas:** `08_quantum/qfs_oracle_*.csv` (`alpha`, `cardinality`),
  `qfs_runs_madelon_*.csv` (`density__*`, `beta`). **Plotter:** A nuevo, B reutilizar.
- **Sustituye:** Q19, Q20.

## F9 — "Dos fracasos distintos: criterio frente a optimizador" (el hallazgo central)
- **Pregunta:** cuando QFS se deteriora, ¿falla el criterio o el optimizador?
- **Composición final:** plano de atribución en una sola unidad de lectura: puntos de
  macro-F1 perdidos frente al baseline. **Por qué no multipanel:** el control de coste y
  Hamming ya queda en la tabla inmediatamente anterior; la figura debe ser el clímax
  predictivo, no otra tabla visual. La descomposición que se dibuja es:
  `deterioro = (baseline - oráculo exacto) + (oráculo exacto - QFS-NA)`.
  - **Eje X (rol: optimizador)** — fallo del optimizador: F1 del óptimo exacto menos F1
    de QFS-NA.
  - **Eje Y (rol: criterio)** — fallo del criterio: F1 del baseline menos F1 del óptimo
    exacto.
  - **Regiones/anotaciones** — Madelon aparece limitado por el criterio; Customer Churn
    por la optimización analógica simulada. El resto queda como contexto gris.
- **Protagonista:** madelon (criterio) y churn (optimizador), anotados.
- **Título:** "Cuando QFS falla, el control frente al óptimo exacto dice por qué".
  **Subtítulo:** "El deterioro frente al baseline se descompone en fallo de criterio y
  fallo de optimizador, ambos en puntos de macro-F1".
- **Paleta:** criterio cálido, optimizador frío, contexto gris; no usar colores de dataset
  para evitar que el lector lea ranking por problema en lugar de atribución.
- **Caveats:** el oráculo exacto es control clásico del criterio QUBO; QFS-NA es simulación
  analógica, no hardware. La evidencia de coste/Hamming permanece en
  `tab:qfs-control`.
- **Tablas:** `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv`. **Plotter:**
  `scripts/build_diagnostico_atribucion.py`. **Archivo cuerpo:**
  `diag_atribucion_qfs.png`.
- **Sustituye:** Q21. (Es la aportación metodológica; va destacada.)

## F10 — "QFS frente a la mejor referencia clásica" (cierre, enlazado a F9)
- **Pregunta:** ¿iguala/supera QFS a los mejores clásicos y por qué no donde no?
- **Composición:** small multiples / dumbbell por dataset (familia **5 dot + IC** o **10
  slope**). 4 marcadores: baseline · mejor clásico · QFS-NA · QFS-oráculo, con IC; veredicto
  anotado; flecha a F9 donde hay deterioro.
- **Protagonista:** el contraste por régimen (equivalente en señal clara; deterioro en
  madelon/churn con causa distinta).
- **Título:** "El método cuántico iguala en los problemas con señal clara y se deteriora
  donde el criterio o el optimizador fallan". **Subtítulo:** "Macro-F1 en test por dataset
  con IC bootstrap 95%; NA = simulador, oráculo = óptimo exacto".
- **Paleta:** baseline `#bdbdbd`, clásico `#4f81bd`, QFS-NA `#d95f5f`, oráculo `#d9b382`.
- **Caveats:** IC; el oráculo casi iguala en churn (señala optimizador).
- **Tablas:** `08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` (NA y oráculo)
  + `07_final_comparison/fase7_handoff_qfs.csv` para la mejor referencia clásica.
  **Plotter:** `scripts/build_memoria_figuras.py` (`figure_f10`).
- **Sustituye:** Q24.

---

# APÉNDICE (figuras de apoyo, Tier 1)

- **A1 — Permutación señal vs nulo, detalle por dataset** (heatmap método×dataset
  completo). `fase5` permutación. (El resumen ya está en F4-D; aquí el detalle.)
- **A2 — Leakage** (scatter AUC×NMI por variable, líneas 0.99). `fase4_leakage_screening`. (Q7.)
- **A3 — Roster completo y selección por variable** (heatmaps método×variable, 5 datasets).
  `fs_all_rankings` / `*_method_feature_heatmap`. (parte de Q8.)
- **A4 — Concordancia SHAP↔selección↔fase 1** + **SHAP por clase (olive)**.
  `modeling_shap_*`. (Q15 + resto de Q14.)
- **A5 — Panorama de deltas** (heatmap selector×dataset, divergente en 0).
  `fase7_panorama_validacion_delta`. (Q18.)
- **A6 — Handoff I/R** (heatmap R_ij + barras I_i por dataset). handoff. (Q22.)
- **A7 — Coste de la vía cuántica simulada** (barras tiempo, caveat fuerte de simulación).
  `qfs_runs_*`. (Q23.)
- **A8 — Solape QFS vs clásicos** (matriz binaria / UpSet). `qfs_selected_*`. (Q25.)
- **A9 — Macro-F1 vs AUC en binarios** (barras agrupadas). `qfs_auc_binarios_contexto`. (Q26.)

---

## Resumen del salto (antes → ahora)
- Antes: ~16 figuras de cuerpo, casi todas gráfico único.
- Ahora: **10 argumentos compuestos** de cuerpo (multipanel/layered/small-multiples), cada
  uno con roles de panel no redundantes, + 9 de apéndice. Menos figuras, más narrativa.
- Combinaciones nuevas que el skill habilita y aprovechamos: F2 (señal+FDR+efecto),
  F3 (representatividad+drift+conservación), F4 (rendimiento+coste+estabilidad, el
  three-panel insignia), F7 (resultado+lectura honesta), F8 (α teoría + β mecanismo),
  F9 (diagnóstico+evidencia del criterio-vs-optimizador), F10 (cierre enlazado a F9).

## Plotters
- Reutilizan: parte de F3 (adversarial), F7-A (baseline vs selección), F8-B (β map), A1, A5.
- Copiar/re-tematizar: F6 (SHAP beeswarm).
- Nuevos (compose_panels + editorial_warmth): F1, F2, F3, F4, F5, F7-B, F8-A, F9, F10 + apéndice.

## Decisiones para el usuario
1. ¿Validas el salto a 10 figuras compuestas de cuerpo (en vez de ~16 sueltas)?
2. ¿Alguna composición que prefieras separar o fusionar distinto? (p. ej. ¿F4 a 4 paneles
   añadiendo permutación, o se queda en 3?)
3. ¿Algún caveat que quieras reforzar (sobre todo F8/F9: "oráculo = clásico exacto, no
   cuántico")?
