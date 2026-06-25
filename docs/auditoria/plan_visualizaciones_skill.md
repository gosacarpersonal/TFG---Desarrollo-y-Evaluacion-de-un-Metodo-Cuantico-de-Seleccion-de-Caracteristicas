# Replanteamiento de visualizaciones con la skill viz-definitive (NO generar aún)

> 2026-06-16. Corrección de fondo: la FORMA (tamaño, nº de paneles, eje) se DERIVA de
> pregunta→forma-de-datos→intención→métrica→familia→composición (router de la skill, pasos 1–10);
> NO se elige un molde de figura y se mete el dato dentro. El error repetido fue "5 datasets ⇒ 5
> paneles": preset, no derivación. Aquí cada figura cita **familia (nº de `family-taxonomy-35.md`)**,
> **caveat (fichero de `references/`)** y **criterio** (router/complexity-ladder/combined-figure-router).
> Regla transversal: una sola figura por pregunta; protagonista + contexto en gris; título=hallazgo;
> probar a tamaño de PDF (combined-figure-router "mandatory render rule").

Notación: F#=familia de la taxonomía-35. Nivel=complexity-ladder (0 tabla … 4 diagnóstico denso).

## Acto 1 — Régimen del dato (caracterización)

**V1 · ¿Los 5 datasets cubren regímenes distintos?**
- Datos: categoría(dataset)+varios numéricos (filas, p, p/n, desbalance, nº clases). Intención: *summarise profile*.
- Métrica derivada: p/n, ratio de desbalance, nº clases (no crudos). Constraint: escalas en órdenes de magnitud → log.
- Familia: **F5 dot/Cleveland** (comparación precisa multi-métrica), nivel 1. Composición: **single axes** (o scorecard nivel 0).
- Caveat: `area-vs-radius-scaling.md` → **NO bubble** (área incomparable, que es lo que tienta con filas×vars×desbalance); `log-scales.md`; `dangerous-charts.md`.
- Forma derivada: NO burbujas; dot plot/scorecard. Protagonista: Madelon (p/n=0.25) y desbalance Olive9.

**V2 · ¿Dónde la redundancia es estructura que el criterio puede explotar? (VIF)** [EXEMPLAR hecho]
- Datos: numérico(VIF) por variable, agrupado por dataset. Intención: *compare distributions / comparabilidad cross-dataset*.
- Familia: **F20 strip/beeswarm** (observaciones crudas por grupo), nivel 1. Composición: **single axes, eje log COMPARTIDO** (no small multiples, porque la comparabilidad entre datasets ES la pregunta).
- Caveat: `log-scales.md` (VIF en log), `overplotting.md` (jitter), `categorical-ordering.md` (ordenar datasets por colinealidad).
- Forma derivada: 1 eje, NO 5 paneles. Protagonista: BCW (familia tamaño, máx 3806); anotación de nº vars≥10.

**V3 · ¿Cuál es la dimensión intrínseca de cada dataset? (PCA)**
- Datos: orden(componente)+métrica(varianza acumulada) por dataset. Intención: *show change*; respuesta=componentes@80%.
- Familia: **F8 línea** (curva de varianza acumulada), nivel 1. Composición: **overlay en 1 eje** (el CONTRASTE entre curvas —Madelon casi diagonal vs resto empinadas— es el mensaje → overlay, no small multiples).
- Caveat: `spaghetti-plots.md` (solo 5 líneas + resaltar protagonista), línea de umbral 80%.
- Forma derivada: 1 eje con 5 líneas, Madelon resaltada; anotación "295/500 comp".

**V4 · ¿La señal univariante sobrevive a FDR y con qué efecto?**
- Datos: categoría(dataset)+conteo(vars FDR/total)+numérico(efecto mediano). Intención: *compare* (recuento) + *magnitud*.
- Familia: **F4 lollipop** (fracción FDR), nivel 1; magnitud de efecto como segundo encoding. Composición: **layered o 2-panel** (separar recuento de magnitud, combined-figure-router Type B: "signal + FDR + effect").
- Caveat: `grouped-barplots.md` (evitar barras agrupadas), separar significancia de magnitud. Protagonista: Madelon (13/500, efecto 0.02).

**V5 · ¿La base no sesga la comparación? (adversarial)**
- Datos: categoría(dataset)+métrica(AUC adversarial ± fold-std). Intención: *show uncertainty vs referencia 0.5*.
- Familia: **F5 dot plot con barras de error**, nivel 1; banda de referencia en 0.5. Composición: single axes.
- Caveat: `error-bars.md` (mostrar la banda/IC), `y-axis-baseline.md` → **NO barras desde 0** (la referencia es 0.5, no 0). Protagonista: la banda (todos ≈0.5 = sin sesgo).

## Acto 2 — Selección clásica y posición de QFS

**V6 · ¿Cómo se agrupan los 12 selectores? (perfil)**
- Datos: categoría(método)+numéricos (coste, redundancia interna, estabilidad). Intención: *summarise profile*.
- Familia: **F22 scatter** (redundancia x, coste y), color=familia, etiqueta directa; nivel 2. Estabilidad como anotación, NO como área.
- Caveat: `area-vs-radius-scaling.md` (no dimensionar por estabilidad), `uninformative-color.md` (color=familia, semántico), `overplotting.md`. Protagonista: mRMR (mínima redundancia).

**V7 · ¿Dónde cae QFS entre los 12? (espacio de métodos)**
- Datos: alta-dim → 2 coords (relevancia capturada, redundancia interna R_ij) por método+QFS. Intención: *show position/relationship*.
- Familia: **F22 scatter**, QFS protagonista (estrella), 12 en gris/color-familia. Composición: **small multiples por dataset** (F3 composición): aquí SÍ small multiples, criterio del combined-figure-router = "identity of the comparison matters more than overlay" (cada dataset tiene variables/escala distintas). NO es preset: es que la comparación es intra-dataset.
- Caveat: `multipanel-grammar.md` (encoding compartido, una leyenda), `cross-chart-consistency.md` (misma definición de coords que la memoria). Protagonista: QFS; anotación Churn (fuera del nicho mRMR).

**V8 · ¿A qué método se parece el subconjunto de QFS? (Jaccard QFS vs 12)**
- Datos: por dataset, Jaccard(QFS, método) → ranking. Intención: *rank*.
- Familia: **F4 lollipop / F5 dot** ordenado por Jaccard; NO heatmap (por `heatmaps.md`: el RANKING por dataset es el mensaje, no el patrón matricial; heatmap "weaker for exact values"). Composición: small multiples de lollipops o el dataset protagonista (Churn).
- Caveat: `categorical-ordering.md` (ordenar por Jaccard), `heatmaps.md` (motivo de descartarlo). Protagonista: el método más cercano + mRMR resaltado.

**V9 · Mecanismo de Churn por variable (qué suelta/coge QFS)**
- Datos: categoría(variable)+relevancia(I_i)+estado de selección {ambos / solo-NA / solo-oráculo}. Intención: *diagnose/compare*.
- Familia: **F4 lollipop** de I_i por variable (ordenado), marcador con color de estado (3 estados). Nivel 1, single axes.
- Caveat: `categorical-ordering.md`, `color-choices.md` (3 estados semánticos, colorblind-safe). Protagonista: payment_delay/tenure/last_interaction (soltadas por QFS, en el óptimo) y los grupos one-hot sobre-elegidos. Forma: lollipop, NO matriz.

## Acto 3 — Mandos del método (k, α, β)

**V10 · Trayectoria en k (macro-F1 vs k)**
- Datos: orden(k)+métrica por método por dataset. Intención: *show change/compare*.
- Familia: **F8 línea**; composición **small multiples por dataset** (criterio: rangos de k y escalas difieren → identidad por dataset; combined-figure-router). 3 líneas (baseline/mRMR/QFS), QFS protagonista.
- Caveat: `spaghetti-plots.md` (3 líneas, resaltar QFS), `ordered-x-connect-dots.md` (x ordenado). 

**V11 · Escalera α (Mücke + degeneración de Madelon)**
- Datos: orden(α)+cardinalidad ‖x‖ del óptimo exacto por dataset. Intención: *show change/fidelity*.
- Métrica derivada: cardinalidad vs α (NO el heatmap variable×α de Codex, que `heatmaps.md` desaconseja para esta lectura). Familia: **F8 línea** overlay 5 datasets, single axes; el contraste (Madelon plana-y-salto vs resto gradual) es el mensaje → overlay.
- Caveat: `spaghetti-plots.md`, `ordered-x-connect-dots.md`. Protagonista: Madelon (colapso). El detalle variable×α, si se quiere, a apéndice como F28 heatmap.

**V12 · β reordena densidades de Rydberg**
- Datos: matriz(variable × β) de densidad, por dataset. Intención: *show pattern/change*.
- Familia: **F28 heatmap** (matriz con estructura real, ver patrón de reordenación) — heatmap SÍ es correcto aquí (a diferencia del roster). Solo el dataset protagonista (no 5; `heatmaps.md`: evitar matrices enormes). Paleta secuencial, colorbar etiquetado.
- Caveat: `heatmaps.md` (1 matriz legible, paleta secuencial). Protagonista: la variable que más se mueve con β.

## Acto 4 — Átomos, modelos, métricas, consistencia, diagnóstico

**V13 · Configuración atómica + refutación geométrica**
- Datos: posiciones 2D + relevancia + radio de bloqueo (layout); y error de embebido por dataset (refutación). Intención: *show structure* + *compare*.
- Familia: layout = **F22 scatter** (aspect equal, tamaño=relevancia, aristas=redundantes en bloqueo) para 1 dataset ilustrativo; refutación = **F5 dot plot** del error de embebido (Churn vs resto). Composición: combined Type B (mecanismo + caveat).
- Caveat: `aspect-ratio.md` (geometría física, aspecto igual), `error-bars.md`. Protagonista de la refutación: Churn (0.217) NO es el peor → descarta geometría.

**V14 · SHAP beeswarm por dataset** [estándar = beeswarm BCW ya hecho]
- Datos: SHAP por instancia × valor de variable. Intención: *distribution + relationship (ML diagnostic)*.
- Familia: **F20 beeswarm**; una figura por dataset (NO 5 apretadas en una). Caveat: `overplotting.md` (jitter/densidad), color=valor de variable. Protagonista: variable top. Olive: por clase.

**V15 · Dependencia del modelo (Madelon +0.28→+0.094)**
- Datos: 2 puntos (RF, XGBoost) de delta-selección por dataset. Intención: *show change (before/after)*.
- Familia: **F10 slopegraph** (dos puntos, etiquetar inicio/fin) — elegante para RF→XGBoost. Protagonista: Madelon (colapso de la ganancia).
- Caveat: `slopegraph`/`categorical-ordering`. Forma: slopegraph, NO barras agrupadas.

**V16 · Consistencia (qué baila entre semillas)**
- Datos: Jaccard entre 3 semillas por método/dataset + variables que cambian. Intención: *show stability*.
- Familia: **F5 dot plot** de Jaccard (mayoría 1.0; RF más bajo); anotar los sustitutos que bailan. Single axes.
- Caveat: `error-bars.md` si hay rango; no sobre-encodear. Protagonista: los <1.0 (feat_28↔48, dummies, palmitoleic↔stearic) = inestabilidad benigna.

**V17 · Camino metodológico (4→100) + diagnóstico criterio↔optimizador**
- Corrección 4→100: **F10 slopegraph** (macro-F1 4-run→100-run por dataset; Churn 0.922→0.969). 
- Atribución [hecho `diag_atribucion`]: **F22 scatter** (plano fallo-criterio × fallo-optimizador), protagonistas Madelon/Churn en cuadrantes distintos. Composición: combined Type B (corrección + plano).
- Caveat: `cross-chart-consistency.md` (cifras canónicas), `y-axis-baseline.md`.

## Lo que se DESCARTA (when-to-remove + heatmaps)
- El **roster 12×variables** como heatmap gigante (Codex): `heatmaps.md` ("avoid annotating large matrices; text becomes texture") + etiquetas ilegibles → se sustituye por V7 (espacio de métodos) + V8 (Jaccard) + V9 (mecanismo Churn), que SÍ extraen el insight.
- Cualquier panel vacío o de escala incomparable (la VIF de 5 paneles) → V2 single-axis.
- Bubble charts por área (V1) → dot/Cleveland.

## Regla de aceptación (por figura, antes de dar por buena)
Responde 1 pregunta · familia justificada vs ≥1 alternativa · forma DERIVADA (no preset) · caveat honrado · protagonista+anotación-hallazgo · legible a tamaño PDF · cifras canónicas.
