# Roadmap detallado — qué se hace, por qué y QUÉ QUEREMOS DEMOSTRAR

> 2026-06-15. Desarrollo de `roadmap_analisis_qfs_a_memoria.md`. Para cada etapa (y cada instrumento de la
> Etapa 2): **qué se hace · por qué · qué demuestra**. "Qué demuestra" = la afirmación defendible que esa
> etapa deja establecida y que contribuye a la tesis global: *una referencia clásica rigurosa permite no
> solo medir, sino DIAGNOSTICAR y PREDECIR por régimen el comportamiento de QFS; el resultado nulo/deteriorado
> queda rigurosamente atribuido (criterio vs optimizador).*

---

## ETAPA 0 — Estabilizar la base
- **Qué se hace:** commitear el trabajo coherente de Codex como checkpoint limpio; fijar la pila de viz
  (matplotlib+viz_core, salvo decisión contraria); reconciliar los docs de planificación en uno consistente.
- **Por qué:** todo lo que viene se construye encima; sin un punto de partida versionado y reversible,
  cualquier hallazgo posterior es difícil de atribuir o deshacer. Cierra además la incertidumbre de "no sé
  qué tocó Codex".
- **Qué demuestra:** *procedencia y control* — que a partir de aquí cada artefacto (figura, número, texto)
  es trazable desde un estado conocido. No es una afirmación científica; es la condición de posibilidad de
  la reproducibilidad que la memoria promete.

## ETAPA 1 — Cerrar la hipótesis abierta (Churn / embebido)
- **Qué se hace:** *(1a)* recomputar el embebido MDS desde las `R_ij` ya guardadas y medir el **error de
  embebido** por dataset (Churn vs Olive/BCW/Madelon); *(1b, opcional)* ablación acotada a Churn (fases 8–9)
  con label-encoding y/o one-hot `drop_first`.
- **Por qué:** es la única incógnita científica viva. El principio "hipótesis = hipótesis" prohíbe narrar
  el fallo de Churn como geométrico/encoding sin prueba. Y es barato comparado con re-ejecutar nada.
- **Qué demuestra:**
  - Que el deterioro de Churn vive en el **paso de optimización/embebido, no en el criterio** — porque el
    oráculo (sin embebido) recupera ~baseline (0.999) mientras QFS-NA cae a 0.922 con Δcoste +1.32.
  - Si 1a sale como se espera (error de embebido de Churn ≫ resto), demuestra la **frustración geométrica**
    de una matriz de redundancia casi plana.
  - Si se hace 1b, demuestra (o refuta) que el **encoding es causal**: separa "baja redundancia intrínseca"
    de "artefacto one-hot". *Riesgo honesto:* label-encoding deja la matriz aún más plana → podría no mejorar.

## ETAPA 2 — Capa analítica (`notebooks/fase10_visualizaciones.ipynb`)
Cada instrumento demuestra una pieza de la tesis. Todos LEEN artefactos de `results/` (no regeneran).

- **A · Regímenes (VIF, PCA, efecto, drift, adversarial).**
  - *Qué:* huella de los 5 datasets en ejes relevancia y redundancia (VIF), dimensión intrínseca (PCA),
    señal (FDR/efecto), limpieza (drift/adversarial).
  - *Por qué:* sin caracterizar el terreno, el veredicto parece azar.
  - *Qué demuestra:* que los 5 datasets **estresan regímenes distintos** y que el régimen **predice el modo
    de fallo de QFS antes de ejecutarlo** (Madelon→criterio por MI-ciega; Churn→optimizador por redundancia
    ~nula). Convierte el bloque clásico de "contexto" a **teoría predictiva**.
- **B2 · Espacio de métodos (coordenadas + solape Jaccard de los 12).**
  - *Qué:* localizar QFS frente a los 12 selectores (rel. capturada vs redundancia interna; y a qué
    subconjunto se parece).
  - *Por qué:* el espejo de 12 se montó para esto y nunca se leyó; contemplar TODOS, no solo mRMR.
  - *Qué demuestra (L2):* que QFS es **de clase-mRMR en los casos limpios** (Olive3 idéntico) y que **se
    desvía hacia otras familias justo donde falla** (Churn → filtro de redundancia/relevancia, no mRMR;
    Madelon → coincide en coordenada pero 0.25 de solape). La posición en el espacio *coincide* con el modo
    de fallo.
- **B3 · Trayectoria en k.**
  - *Qué:* macro-F1 y redundancia interna vs k (QFS vs contexto clásico y baseline); dim-intrínseca vs
    dim-señal.
  - *Por qué:* el veredicto no puede depender de un único k.
  - *Qué demuestra (L3):* **robustez** — que la conclusión por dataset se sostiene a lo largo del presupuesto;
    y dónde aplica el "QFS brilla en k pequeño" del paper (solo donde hay señal compacta, no en Madelon).
- **B4 · Escalera α (óptimo exacto, Mücke).**
  - *Qué:* cardinalidad ‖x‖₁ y coste vs α sobre el QUBO exacto.
  - *Por qué:* conecta la teoría del marco con la evidencia real.
  - *Qué demuestra (L1):* **fidelidad de comportamiento** — que recorrer α *es* recorrer el presupuesto
    (Proposición de Mücke) en nuestros datos; y que el mecanismo funciona aunque su input `I_i` esté
    degenerado en Madelon (separar "α funciona" de "α recibe relevancias informativas").
- **B5 · β y geometría.**
  - *Qué:* mapa β × densidad de Rydberg + F1 de validación; `dist_ratio` por dataset.
  - *Por qué:* β es el segundo mando real y el flanco geométrico debe verse, no esconderse.
  - *Qué demuestra (L1):* que β **reordena de verdad** la selección y que la **geometría se relajó**
    (dist_ratio 0.45/0.35 vs 0.707 del paper) — el flanco de defensa, declarado.
- **B9 · Configuración de átomos (Fig. 2 del paper, ausente hoy).**
  - *Qué:* posiciones MDS, radio de bloqueo, detuning=relevancia, aristas redundantes, error de embebido,
    por dataset y β (sale de la Etapa 1a).
  - *Por qué:* es el cuerpo físico del método; sin él, "átomos neutros" es solo una palabra.
  - *Qué demuestra (L1):* que el método **es físicamente realizable** y, sobre todo, **dónde se rompe**
    (Churn) y dónde no (Madelon embebe bien → su fallo no es geométrico). Hace tangible el diagnóstico.
- **B6 · Dependencia del modelo.**
  - *Qué:* delta de selección por (selector × modelo); el desplome de Madelon +0.28→+0.094 con XGBoost.
  - *Por qué:* "seleccionar ayuda" no es absoluto.
  - *Qué demuestra (L3):* que **el valor de la selección es condicional al modelo** (XGBoost absorbe los 295
    dims de ruido de Madelon), no una propiedad fija — matiz que el podio oculta.
- **B7 · Métricas.**
  - *Qué:* macro-F1 vs balanced-acc vs AUC (binarios); desbalance de Olive9.
  - *Por qué:* justificar la métrica y el puente con el paper.
  - *Qué demuestra (L4/honestidad):* que **macro-F1 no esconde nada** (el AUC binario del paper no aplica a
    multiclase/desbalance) y que la inconclusión de Olive9 es honestidad de n=86, no una derrota oculta.
- **B8 · Cadena de tests estadísticos.**
  - *Qué:* FDR→efecto→shift→adversarial→drift→leakage→permutación→bootstrap→óptimo exacto.
  - *Por qué:* los tests son lo que permite ATRIBUIR en vez de adivinar.
  - *Qué demuestra (L1):* que cada veredicto (deterioro, equivalencia, mejora) **sobrevive a los confusores**
    — no es ruido, fuga, ni artefacto de partición. Es la licencia para hacer afirmaciones causales.
- **C · Síntesis.**
  - *Qué:* beeswarm SHAP por dataset (L4) + plano de atribución (clímax).
  - *Qué demuestra:* el **diagnóstico integrado** — deterioro = criterio + optimizador, en macro-F1, los 5
    datasets; y que las variables que sostienen el modelo coinciden con las que la selección retuvo (L4).

**Qué demuestra la Etapa 2 en conjunto:** la teoría completa **régimen → mecanismo → resultado** sobre las 9
dimensiones y las 4 lentes — el aparato analítico que la memoria solo tiene que narrar.

## ETAPA 3 — Curar (cuerpo / apéndice / solo-notebook)
- **Qué se hace:** clasificar cada figura por la prueba de los 10s y "¿responde una pregunta de defensa?".
- **Por qué:** una memoria es una argumentación, no un atlas; el exceso de figuras diluye la tesis.
- **Qué demuestra:** *disciplina comunicativa* — que el cuerpo es mínimo y suficiente; cada figura del
  cuerpo defiende una afirmación, el resto da trazabilidad en apéndice/notebook. (Claim de comunicación, no
  de ciencia.)

## ETAPA 4 — Reescribir la memoria
- **Qué se hace:** integrar régimen→mecanismo→resultado en Introducción (tesis desde el inicio), Métodos
  (espejo de 12 como coordenadas; VIF/PCA como ejes), Resultados (régimen ANTES del veredicto; clímax =
  atribución), Discusión/Conclusiones (régimen-predictor, descomposición relevancia/redundancia, one-hot como
  causa candidata + future-work).
- **Por qué:** el análisis solo vale si aterriza en el entregable; pasar de "veredicto" a "explicación".
- **Qué demuestra:** la **tesis central ante el tribunal** — que el TFG no reporta "QFS empata/pierde", sino
  que construye una referencia que **predice y atribuye** el comportamiento de QFS por régimen, distinguiéndose
  del paper (que no caracteriza régimen) y blindando los flancos (simulación, geometría, encoding).

## ETAPA 5 — Verificar y cerrar
- **Qué se hace:** re-ejecutar los 9+1 notebooks desde núcleo limpio; verificar cada cifra contra su
  artefacto; compilar LaTeX; pase de consistencia; commit final.
- **Por qué:** la reproducibilidad es una afirmación que hay que sostener, no asumir.
- **Qué demuestra:** que **toda cifra de la memoria es reproducible y trazable** desde código limpio — la
  garantía que promete el apéndice de reproducibilidad.

---

## La cadena de demostraciones, de un vistazo
E0 procedencia → E1 *el fallo de Churn es del optimizador/embebido* → E2 *el régimen predice y el aparato
diagnostica las 9 dimensiones* → E3 disciplina → E4 *la tesis: referencia clásica que predice y atribuye
QFS* → E5 reproducibilidad. Cada eslabón es una afirmación defendible; juntos son la memoria.
