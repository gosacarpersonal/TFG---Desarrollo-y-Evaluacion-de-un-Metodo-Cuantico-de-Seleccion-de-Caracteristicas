# Propuesta operativa de visualizaciones con `viz-definitive`

Fecha: 2026-06-16  
Base revisada: `docs/auditoria/propuesta_visualizaciones_multidimensional_2026-06-16.md`  
Skill aplicada: `.agents/viz-definitive/skills/viz-definitive/SKILL.md`

## Para que sirve este documento

La propuesta multidimensional original funciona bien como inventario maestro. Este documento la convierte en un contrato operativo de figuras: que entra en cuerpo, que va a apendice, que queda como diagnostico y que debe derivarse antes de dibujar.

La regla de cierre es la de la skill:

`pregunta -> forma del dato -> intencion -> metrica derivada -> restriccion cientifica -> familia visual -> composicion -> caveat -> relato -> estetica -> render check -> codigo`

No se deberia programar ninguna figura de cuerpo sin tener completa su ficha.

## Diagnostico general

La propuesta original acierta en lo mas importante: deja de defender una configuracion ganadora aislada y recupera dimensiones que estaban escondidas (`k`, semilla, modelo, split, metrica, beta, oraculo, geometria, ocupacion).

El problema es de jerarquia. Hay demasiadas figuras candidatas a cuerpo. Si se construyen F0-F19 sin criba, la memoria puede parecer un atlas de resultados en vez de una demostracion experimental. La solucion no es hacer mas graficas, sino ordenar el recorrido:

1. confianza en datos/splits;
2. espacio experimental recorrido;
3. comportamiento de selectores;
4. filtrado validation -> test;
5. dependencia de modelo/metrica;
6. evidencia estadistica y coste;
7. mecanismo SHAP/MI;
8. mecanismo QFS interno;
9. comparacion final;
10. scorecard como cierre, no como punto de partida.

## Clasificacion final recomendada

| ID original | Clase `viz-definitive` | Accion | Prioridad | Veredicto |
|---|---:|---|---:|---|
| F0 Cadena de evidencia | memory_candidate | keep/derive | 1 | Necesaria para explicar camino. |
| F1 Cobertura experimental | memory_candidate | keep/derive | 1 | Figura anti-cherry-picking. |
| F2 Espacio-problema | memory_candidate | keep | 1 | Justifica lectura por dataset. |
| F3 Perfil selectores | memory_candidate | keep/derive | 2 | Mapa clasico antes de elegir ganadores. |
| F4 Estabilidad semillas/k | memory_candidate + appendix | derive/split | 2 | Cuerpo resumido; detalle al apendice. |
| F5 Solape metodos | memory_candidate + appendix | derive/split | 2 | Solo si usa tabla inter-metodo real. |
| F6 Senal frente al nulo | appendix -> body if central | derive | 3 | Subir al cuerpo si Madelon sostiene el diagnostico. |
| F7 Embudo validation-test | memory_candidate | derive/replace | 1 | Explica proceso de filtrado. |
| F8 Dependencia del modelo | memory_candidate | keep/derive | 1 | Evita confundir selector con clasificador. |
| F9 Selector x k x dataset | appendix + body extract | split/derive | 3 | Completa es demasiado densa para cuerpo. |
| F10 Coste vs rendimiento | memory_candidate if parsimony claim | derive | 2 | Convertir en frontera de parsimonia. |
| F11 Magnitud y significancia | memory_candidate | keep | 1 | Prueba estadistica del efecto. |
| F12 SHAP vs MI | memory_candidate | derive | 1 | Diagnostico mecanistico fuerte. |
| F13 SHAP beeswarm | appendix or selective body | split | 3 | No debe competir con F12. |
| F14 Barrido QFS beta | memory_candidate | combine with F16 | 1 | Mecanismo QFS interno. |
| F15 QFS vs baseline | memory_candidate | keep | 1 | Comparacion final cuantica. |
| F16 QFS-NA vs oraculo | memory_candidate + appendix | combine/split | 1 | Fusionar con F14 si legible. |
| F17 Geometria Rydberg | appendix | move_to_appendix | 3 | Pedagogica/profundidad, no prueba central. |
| F18 Ocupacion feature x beta | appendix | move_to_appendix | 3 | Profundidad cuantica granular. |
| F19 Scorecard final | memory_candidate | derive | 2 | Cierre, no sustituto de pruebas. |

## Cuerpo recomendado despues de la criba

### Bloque 1. Confianza y alcance experimental

#### V0. Cadena de evidencia del TFG

```text
Figure ID: V0
Figure class: memory_candidate
Tier: 2
Question: Que camino verificable sigue la evidencia desde datos crudos hasta conclusion.
Data shape: fases ordenadas, artefactos por fase, verificadores, salidas canonicas.
Analytical intent: trazabilidad/reproducibilidad.
Derived metric needed: conteo de artefactos canonicos por fase y estado verificado/no verificado.
Scientific constraints: no mezclar runs legacy con run canonico; no presentar logs historicos como evidencia principal.
Candidate families: timeline/flow editorial, dot matrix de artefactos, tabla visual.
Rejected families and why: Sankey pesado, porque el volumen del flujo no es la pregunta; infografia decorativa, porque no aporta evidencia.
Composition: multipanel ligero o tabla visual.
Chosen layout: columna de fases + chips de artefactos + marca de verificacion.
Story protagonist: la cadena reproducible, no una metrica.
Title message: La conclusion sale de una cadena de artefactos verificables.
Annotation plan: marcar verificadores obligatorios y handoffs entre fases.
Color/warmth plan: gris para contexto, acento para artefactos canonicos.
Acceptance risks: que parezca diagrama decorativo; evitarlo con rutas/artefactos concretos.
Decision: construir antes de figuras de resultado.
```

#### V1. Mapa de cobertura experimental

```text
Figure ID: V1
Figure class: memory_candidate
Tier: 2
Question: Que combinaciones se recorrieron realmente y donde hay huecos.
Data shape: dataset x dimension experimental; presencia/ausencia o conteo.
Analytical intent: cobertura y anti-cherry-picking.
Derived metric needed: conteos por dataset de selectores, k, modelos, metricas, betas y splits; indicador de validation/test/QFS.
Scientific constraints: distinguir no ejecutado de no aplicable; no colorear como equivalente validation y test.
Candidate families: dot matrix, heatmap discreto, scorecard de cobertura.
Rejected families and why: heatmap continuo, porque sugiere magnitudes donde hay estados; barras apiladas, porque ocultan huecos por dataset.
Composition: single chart.
Chosen layout: dot matrix con columnas agrupadas por fase.
Story protagonist: cobertura real del pipeline.
Title message: El experimento recorre mas de una configuracion por fase y dataset.
Annotation plan: marcar huecos o fases con cobertura parcial.
Color/warmth plan: estados discretos con paleta semanticamente estable.
Acceptance risks: que la matriz sea demasiado ancha; agrupar dimensiones y mandar detalle al apendice.
Decision: construir en cuerpo.
```

#### V2. Auditoria compacta de splits y leakage

```text
Figure ID: V2
Figure class: memory_candidate
Tier: 2
Question: Por que se puede confiar en las particiones antes de comparar modelos.
Data shape: dataset x split x controles.
Analytical intent: control de validez experimental.
Derived metric needed: n_train/n_validation/n_test, balance por split, flags de leakage/drift/duplicados.
Scientific constraints: no ocultar advertencias; no convertir controles binarios en nota textual secundaria.
Candidate families: scorecard compacto, grouped dot matrix, tabla visual.
Rejected families and why: multiples histogramas de clases, porque ocuparian demasiado cuerpo; heatmap continuo si los estados son binarios.
Composition: single chart o panel anexo a V1.
Chosen layout: tabla visual por dataset con tamanos y checks.
Story protagonist: confianza en el split.
Title message: Los resultados se leen sobre particiones auditadas.
Annotation plan: marcar cualquier warning y criterio de estratificacion.
Color/warmth plan: verde/ambar/rojo semantico, con texto para accesibilidad.
Acceptance risks: que parezca burocratica; mantenerla compacta.
Decision: anadir al cuerpo aunque sea como figura-tabla.
```

#### V3. Espacio-problema de los datasets

```text
Figure ID: V3
Figure class: memory_candidate
Tier: 2
Question: Que regimen representa cada dataset.
Data shape: 5 datasets con p, n, clases y desbalance.
Analytical intent: comparacion estructural.
Derived metric needed: ratio p/n, desbalance o proporcion de clase minoritaria; escala log para p/n si procede.
Scientific constraints: declarar escala log; etiquetar datasets; no usar area sin escala clara.
Candidate families: scatter/bubble, dot plot comparativo, small table.
Rejected families and why: barras separadas por metrica, porque impiden ver regimen conjunto; radar chart, por distorsion perceptiva.
Composition: single chart.
Chosen layout: scatter p vs n con color desbalance y tamano clases.
Story protagonist: datasets no equivalentes.
Title message: Los cinco datasets viven en regimenes experimentales distintos.
Annotation plan: destacar Madelon y Churn si son extremos.
Color/warmth plan: color continuo solo para desbalance; etiquetas directas.
Acceptance risks: sobreinterpretar distancias en escala log.
Decision: construir.
```

### Bloque 2. Seleccion clasica antes del modelado

#### V4. Perfil operacional de selectores

```text
Figure ID: V4
Figure class: memory_candidate
Tier: 2
Question: Que comportamiento tienen los selectores antes de mirar rendimiento final.
Data shape: metodo x estabilidad x redundancia x coste.
Analytical intent: relacion coste-estabilidad-redundancia.
Derived metric needed: estabilidad media, redundancia media y tiempo medio por metodo desde tablas canonicas.
Scientific constraints: `fs_jaccard_stability.csv` es estabilidad intra-metodo entre semillas; no usarlo como solape inter-metodo.
Candidate families: scatter/bubble, Cleveland dot plot de 3 metricas, multipanel de rankings.
Rejected families and why: bubble si el tamano dificulta comparar coste; radar chart por falsa precision y mala comparacion.
Composition: single chart o multipanel 1x3 si el scatter queda ambiguo.
Chosen layout: preferir 1x3 dot plot ordenado por familia si el bubble no es legible.
Story protagonist: QFS/mRMR-like frente a selectores puramente predictivos o filtrados.
Title message: Los selectores difieren en coste, estabilidad y redundancia antes de competir en F1.
Annotation plan: resaltar familias de criterio.
Color/warmth plan: color por familia de selector estable en toda la memoria.
Acceptance risks: coste muy sesgado; usar escala log si se declara.
Decision: construir como cuerpo.
```

#### V5. Estabilidad frente a semilla y k

```text
Figure ID: V5
Figure class: memory_candidate + appendix
Tier: 2
Question: Que selectores sobreviven a cambios de semilla y cardinalidad.
Data shape: dataset x metodo x k x pares de semillas x Jaccard.
Analytical intent: robustez/instabilidad.
Derived metric needed: mediana e IQR de Jaccard por dataset/metodo/k; opcional tasa de Jaccard bajo umbral.
Scientific constraints: mostrar variabilidad, no solo media; indicar numero de pares de semillas.
Candidate families: heatmap resumido, dot+interval, small multiples.
Rejected families and why: ridge por dataset si impide leer metodos; full heatmap 5 datasets en cuerpo si reduce legibilidad.
Composition: cuerpo reducido + apendice completo.
Chosen layout: cuerpo con dot+interval por metodo y dataset agregado; apendice con heatmaps dataset x metodo x k.
Story protagonist: selectores robustos vs fragiles.
Title message: La estabilidad no es uniforme: algunos selectores cambian con semilla/k.
Annotation plan: linea o banda de estabilidad aceptable si se define.
Color/warmth plan: acento para fragilidad; contexto en gris.
Acceptance risks: agregacion excesiva; conservar detalle en apendice.
Decision: derive/split.
```

#### V6. Solape real entre metodos

```text
Figure ID: V6
Figure class: memory_candidate + appendix
Tier: 2
Question: Distintos metodos eligen lo mismo o exploran regiones diferentes.
Data shape: dataset x metodo A x metodo B x k, Jaccard inter-metodo.
Analytical intent: estructura de similitud entre selectores.
Derived metric needed: Jaccard inter-metodo real por dataset/k; promedio solo si k queda documentado.
Scientific constraints: no usar estabilidad entre semillas como sustituto; declarar k o agregacion.
Candidate families: correlation/overlap heatmap, clustermap, top pairs lollipop.
Rejected families and why: red/network si no mejora sobre matriz; heatmap completo en cuerpo si los labels no caben.
Composition: cuerpo con un dataset representativo o matriz resumida; apendice con 5 datasets.
Chosen layout: heatmap ordenado por familias con etiquetas legibles.
Story protagonist: familias de selectores que convergen o divergen.
Title message: El solape entre metodos revela redundancia metodologica y diversidad real.
Annotation plan: marcar bloque QFS/mRMR/MI si aparece.
Color/warmth plan: escala secuencial perceptiva con limites 0-1.
Acceptance risks: tabla inter-metodo ausente; si falta, construir derivado desde selected features antes.
Decision: construir solo con fuente inter-metodo valida.
```

#### V7. Senal frente al nulo

```text
Figure ID: V7
Figure class: appendix -> memory_candidate if central
Tier: 2
Question: La seleccion detecta senal por encima de permutacion.
Data shape: dataset x metodo/feature x p-valor empirico o distancia al nulo.
Analytical intent: significancia empirica y control del azar.
Derived metric needed: p-FDR o proporcion de features que superan umbral por dataset/metodo.
Scientific constraints: distinguir p crudo de FDR; no afirmar ausencia de senal si el test solo mira MI marginal.
Candidate families: ECDF, strip/rug + umbral, dot plot de proporciones.
Rejected families and why: histograma por dataset si bins dominan la lectura; volcano si no hay efecto comparable.
Composition: single chart o small multiples.
Chosen layout: ECDF/strip compacto con linea FDR.
Story protagonist: datasets donde MI marginal queda plana frente al nulo.
Title message: La senal marginal no aparece con la misma fuerza en todos los datasets.
Annotation plan: destacar Madelon si sostiene el argumento de criterio.
Color/warmth plan: dataset como facet; umbral en linea sobria.
Acceptance risks: venderlo como prueba total del problema; caveat visible.
Decision: apendice por defecto; cuerpo si enlaza directamente con V11.
```

### Bloque 3. Modelado y filtrado

#### V8. Embudo validation -> test

```text
Figure ID: V8
Figure class: memory_candidate
Tier: 2
Question: Como se redujo el espacio de candidatos sin usar test para elegir.
Data shape: candidatos en validation, candidatos cerrados, resultados en test.
Analytical intent: proceso experimental y riesgo de selection bias.
Derived metric needed: rank_validation, selected_for_test, delta_test_vs_validation, cambio de ranking.
Scientific constraints: test solo como evaluacion final; separar claramente validation de test.
Candidate families: slopegraph/rank-change, dot flow, compact funnel table.
Rejected families and why: Sankey salvo que haya muchos estados con volumen real; barras de top-N porque ocultan cambios de ranking.
Composition: multipanel ligero si incluye conteo + rank-change.
Chosen layout: dot/slope por dataset desde validation rank a test result, con conteo de candidatos evaluados.
Story protagonist: la decision de candidatura antes del test.
Title message: Los candidatos finales salen de validation y solo despues se contrastan en test.
Annotation plan: marcar cambios de ranking fuertes.
Color/warmth plan: acento para candidatos finales; resto gris.
Acceptance risks: demasiadas lineas; limitar a top-N y declarar criterio.
Decision: construir antes de scorecard.
```

#### V9. Dependencia del modelo

```text
Figure ID: V9
Figure class: memory_candidate
Tier: 2
Question: Cuanto cambia la lectura al cambiar el clasificador.
Data shape: dataset x modelo x selector/k/candidato x metrica.
Analytical intent: sensibilidad al modelo.
Derived metric needed: mejor delta frente a baseline del mismo modelo por dataset/modelo; opcional dispersion entre modelos.
Scientific constraints: comparar siempre contra baseline del mismo modelo; no mezclar validation y test.
Candidate families: dot matrix, slopegraph, heatmap discreto/continuo.
Rejected families and why: heatmap de todas las configuraciones si se vuelve mural; lineas spaghetti por selector.
Composition: single chart con dataset x modelo; apendice para selector/k completo.
Chosen layout: dot matrix de deltas por dataset/modelo con simbolo de mejora/empate/perdida.
Story protagonist: variabilidad atribuible al modelo.
Title message: Parte del resultado depende del clasificador, no solo del selector.
Annotation plan: marcar datasets con conclusion sensible al modelo.
Color/warmth plan: escala divergente centrada en 0.
Acceptance risks: ocultar selector ganador; incluir nota de agregacion.
Decision: cuerpo prioritario.
```

#### V10. Frontera coste-rendimiento

```text
Figure ID: V10
Figure class: memory_candidate if parsimony claim
Tier: 2
Question: Cuanta reduccion de variables se logra sin perder rendimiento.
Data shape: dataset x selector x k/modelo con reduccion, F1, tiempo.
Analytical intent: trade-off/parsimony.
Derived metric needed: delta macro-F1 vs baseline mismo modelo; feature_reduction_ratio; frontera de Pareto por dataset.
Scientific constraints: no mezclar coste temporal y reduccion de variables como si fueran igual; baseline explicito.
Candidate families: scatter with Pareto frontier, connected scatter, dot plot of best parsimonious candidates.
Rejected families and why: nube completa sin frontera; bubble con fit_seconds si dificulta lectura.
Composition: small multiples por dataset o single chart con top frontera.
Chosen layout: scatter reducido a candidatos de frontera + linea delta=0.
Story protagonist: configuraciones que reducen mucho sin perder F1.
Title message: La seleccion permite reducir variables, pero la frontera cambia por dataset.
Annotation plan: etiquetar mejores puntos parsimoniosos.
Color/warmth plan: selector por color estable; frontera con trazo destacado.
Acceptance risks: demasiados puntos; filtrar solo por criterio analitico documentado.
Decision: cuerpo si el texto defiende parsimonia; si no, apendice.
```

#### V11. Magnitud e incertidumbre de las mejoras

```text
Figure ID: V11
Figure class: memory_candidate
Tier: 2
Question: Las mejoras frente a baseline son grandes y estadisticamente sostenibles.
Data shape: dataset/candidato con delta, CI, p-valores y n de remuestreo/permutacion.
Analytical intent: inferencia/uncertainty.
Derived metric needed: delta macro-F1 con IC bootstrap y p-FDR; veredicto por intervalo y p.
Scientific constraints: mostrar 0 como referencia; no confundir p crudo y FDR; indicar n_bootstrap/n_permutations.
Candidate families: forest plot, lollipop with intervals, slopegraph baseline-candidate.
Rejected families and why: barras con error si dificultan comparar contra cero; ranking sin IC.
Composition: single chart.
Chosen layout: forest plot horizontal.
Story protagonist: deltas cuyo IC cruza o no cruza cero.
Title message: No toda mejora numerica es una mejora fiable.
Annotation plan: linea cero; etiquetas de p-FDR o veredicto.
Color/warmth plan: divergente: mejora fiable, empate, deterioro.
Acceptance risks: demasiados candidatos; limitar a candidatos cerrados.
Decision: construir.
```

### Bloque 4. Mecanismo interpretativo

#### V12. Discordancia SHAP vs MI

```text
Figure ID: V12
Figure class: memory_candidate
Tier: 2
Question: Donde divergen relevancia marginal y utilidad predictiva model-dependent.
Data shape: dataset x feature con MI y mean_abs_SHAP.
Analytical intent: relacion/discordancia.
Derived metric needed: rank_MI y rank_SHAP por dataset; discordancia de ranks o z-scores, porque MI y SHAP no comparten escala.
Scientific constraints: SHAP depende del modelo/candidato; MI marginal no captura interacciones; join exacto por dataset+feature.
Candidate families: scatter with quadrants, hexbin if dense, lollipop top discordant features.
Rejected families and why: scatter con escalas crudas si induce comparacion falsa; barras top SHAP sin MI.
Composition: small multiples por dataset o scatter + top-discordance side panel.
Chosen layout: facet por dataset con ranks normalizados; anotar outliers.
Story protagonist: features con SHAP alto y MI bajo o viceversa.
Title message: La utilidad predictiva no siempre coincide con la relevancia marginal.
Annotation plan: cuadrantes, top discrepancias, caveat de modelo.
Color/warmth plan: punto gris general; acento para features seleccionadas o discordantes.
Acceptance risks: overplotting; usar alpha/hexbin o top labels.
Decision: construir como diagnostico estrella, despues de V9/V11.
```

#### V13. Beeswarm SHAP representativo

```text
Figure ID: V13
Figure class: appendix or selective memory_candidate
Tier: 2
Question: Como impactan variables concretas sobre instancias reales.
Data shape: instancia x feature con SHAP y valor de feature.
Analytical intent: interpretabilidad local/global.
Derived metric needed: top features por mean_abs_SHAP del candidato seleccionado.
Scientific constraints: no comparar datasets en un beeswarm; declarar modelo/candidato/dataset.
Candidate families: beeswarm/strip, violin+points, top-feature dot summary.
Rejected families and why: beeswarm de todos los datasets en cuerpo; saturacion de labels.
Composition: single chart por dataset; todos al apendice.
Chosen layout: Madelon o dataset clave solo si aporta lectura que V12 no da.
Story protagonist: distribucion de impactos de features clave.
Title message: Las variables discordantes tienen impacto heterogeneo por instancia.
Annotation plan: conectar con features destacadas en V12.
Color/warmth plan: paleta SHAP estandar si ya se usa; evitar leyenda redundante.
Acceptance risks: figura familiar pero redundante; remover del cuerpo si solo adorna V12.
Decision: apendice por defecto.
```

### Bloque 5. QFS como sistema parametrico

#### V14. Mapa operativo QFS: beta + control contra oraculo

```text
Figure ID: V14
Figure class: memory_candidate
Tier: 2
Question: Como cambia QFS por beta y que parte corresponde al criterio/optimizador.
Data shape: dataset x beta/configuracion con rendimiento, cardinalidad, Hamming y delta coste.
Analytical intent: comportamiento interno + control tecnico.
Derived metric needed: zona operativa por beta; validation_macro_f1, n_features/k, hamming_mean/min, delta_cost_mean/min.
Scientific constraints: separar QFS simulado/QFS-NA/oraculo; no vender beta optimo sin mostrar sensibilidad.
Candidate families: multipanel line chart, dot matrix by beta, small multiples.
Rejected families and why: cuatro curvas superpuestas con doble eje; heatmap completo si oculta tendencia.
Composition: multipanel Type B.
Chosen layout: 2x2 maximo: rendimiento, cardinalidad, Hamming, delta coste; o 2 paneles en cuerpo y resto apendice.
Story protagonist: beta como control de seleccion y calidad.
Title message: QFS se entiende como paisaje parametrico, no como un unico punto.
Annotation plan: marcar beta elegido y zona estable/inestable.
Color/warmth plan: dataset por linea si son pocas; si no, facet por dataset.
Acceptance risks: demasiadas lineas; dividir si la legenda crece.
Decision: fusionar F14+F16 si render es legible; F16 completo al apendice.
```

#### V15. QFS frente a baseline clasico

```text
Figure ID: V15
Figure class: memory_candidate
Tier: 2
Question: QFS mejora, empata o empeora frente al baseline clasico en test.
Data shape: dataset/configuracion con baseline, qfs, delta, CI, p-FDR/Holm/permutation, veredicto.
Analytical intent: comparacion final con incertidumbre.
Derived metric needed: delta_test_macro_f1 y veredicto reproducible por CI + p-FDR.
Scientific constraints: no elegir configuracion por test; mostrar IC y p; comparar contra baseline declarado.
Candidate families: forest plot, slopegraph baseline->QFS, bullet chart.
Rejected families and why: barras lado a lado sin delta/IC; scorecard solo iconico sin magnitud.
Composition: single chart.
Chosen layout: forest plot horizontal con cero y veredicto.
Story protagonist: delta QFS-baseline por dataset.
Title message: QFS no aporta lo mismo en todos los datasets.
Annotation plan: veredicto y p-FDR junto a cada fila.
Color/warmth plan: divergente centrada en cero.
Acceptance risks: confundir baseline clasico con mejor clasico; etiqueta explicita.
Decision: construir aparte de V14.
```

#### V16. Geometria y ocupacion cuantica

```text
Figure ID: V16
Figure class: appendix
Tier: 2
Question: Que sustrato fisico/ocupacional hay detras de los runs QFS.
Data shape: posiciones atomos x dataset/beta; density/selection feature x beta.
Analytical intent: profundidad y trazabilidad cuantica.
Derived metric needed: embedding_error_mean/p95; ocupacion o frecuencia por feature/beta.
Scientific constraints: no usar geometria como explicacion causal si el resultado no lo prueba; declarar MDS/error.
Candidate families: scatter atomos, heatmap feature x beta, small multiples.
Rejected families and why: 3D; mapas fisicos decorativos sin error.
Composition: apendice con dos familias separadas.
Chosen layout: scatter de geometria + heatmap de ocupacion por dataset.
Story protagonist: sensibilidad fisica/ocupacional.
Title message: El apendice muestra el sustrato cuantico que el cuerpo resume.
Annotation plan: marcar embedding error alto y beta elegido.
Color/warmth plan: color por seleccion/densidad con escala clara.
Acceptance risks: parecer prueba central; ubicar como trazabilidad.
Decision: mover F17/F18 al apendice.
```

### Bloque 6. Sintesis

#### V17. Scorecard final reproducible

```text
Figure ID: V17
Figure class: memory_candidate
Tier: 2
Question: Cual es la conclusion comprimida despues de recorrer todo el pipeline.
Data shape: dataset x criterios con estados y metricas de soporte.
Analytical intent: sintesis.
Derived metric needed: reglas por celda: rendimiento, incertidumbre, coste, robustez, interpretabilidad, QFS vs baseline.
Scientific constraints: no usar iconos/veredictos manuales sin regla; mostrar empates e incertidumbre.
Candidate families: scorecard, bullet table, grouped dot matrix.
Rejected families and why: heatmap generico porque mezcla conceptos; ranking unico porque borra trade-offs.
Composition: single chart.
Chosen layout: scorecard por dataset con columnas agrupadas.
Story protagonist: conclusion por dataset con caveats.
Title message: La conclusion final es heterogenea por dataset y criterio.
Annotation plan: notas breves para celdas con caveat.
Color/warmth plan: semantico y textual: gana/empata/pierde/advertencia.
Acceptance risks: convertirlo en sustituto de la evidencia; ubicar al final y citar figuras soporte.
Decision: construir al final, no primero.
```

## Apendice estructurado

| Grupo | Figuras | Funcion |
|---|---|---|
| A. Trazabilidad de datos | V1 detalle, V2 detalle, A11 | splits, leakage, drift, duplicados, balance. |
| B. Barridos clasicos | F4 completo, F5 completo, F9 completo, A1-A4 | selector, k, semilla, redundancia, rankings. |
| C. Significancia e interpretabilidad | F6 completo, F13 todos los datasets, A5-A7 | nulos, SHAP completo, MI pairwise. |
| D. Robustez de modelado | A8-A9 | modelos y metricas alternativas. |
| E. QFS completo | F14/F16 detalle, F17, F18, A10 | betas, configuraciones, oraculo, geometria, ocupacion. |
| F. Historico/regenerabilidad | A12 | logs y runs anteriores sin mezclarlos con run canonico. |

## Reglas de metrica derivada antes de plotear

Estas derivaciones son obligatorias antes de programar:

| Figura | Metrica derivada necesaria |
|---|---|
| V1 | conteos por fase/dimension y estado validation/test/QFS. |
| V2 | n por split, balance por split, flags de auditoria. |
| V4 | estabilidad/coste/redundancia canonicas con nombres de columnas actuales. |
| V5 | mediana e IQR de Jaccard por dataset/metodo/k. |
| V6 | Jaccard inter-metodo real; no intra-semilla. |
| V7 | p-FDR o proporcion sobre umbral por dataset/metodo. |
| V8 | rank_validation, selected_for_test, delta_test_vs_validation, rank_change. |
| V9 | delta por modelo contra baseline del mismo modelo. |
| V10 | frontera de Pareto por dataset con reduccion y delta F1. |
| V11 | veredicto por CI + p-FDR. |
| V12 | ranks/z-scores por dataset y discordancia SHAP-MI. |
| V14 | zona beta operativa; Hamming/delta coste contra oraculo. |
| V15 | delta QFS-baseline con IC y p-FDR. |
| V17 | reglas reproducibles por celda del scorecard. |

## Familias visuales prohibidas o degradadas

- No usar dual y-axis para rendimiento/cardinalidad QFS; separar paneles.
- No usar 3D para geometria Rydberg.
- No usar radar para perfiles de selectores.
- No usar scorecard de iconos sin reglas.
- No usar heatmaps gigantes en cuerpo si los labels no son legibles en PDF.
- No usar Sankey salvo que el volumen del flujo sea realmente la pregunta.
- No usar barras sin cero cuando codifican magnitud.

## Orden de construccion recomendado

1. V1 cobertura experimental.
2. V2 auditoria compacta de splits/leakage.
3. V8 embudo validation-test.
4. V9 dependencia del modelo.
5. V11 magnitud e incertidumbre.
6. V12 SHAP vs MI.
7. V14 mapa operativo QFS.
8. V15 QFS vs baseline.
9. V17 scorecard final.
10. V4/V5/V6/V7/V10 y apendices.

La razon es deliberada: primero se blindan el camino y las amenazas de interpretacion; despues se construyen las figuras de conclusion.

## Checklist de aceptacion para cada figura de cuerpo

Antes de aceptar una figura:

- responde una sola pregunta necesaria;
- declara tabla(s) origen y joins;
- usa metrica derivada si la pregunta lo requiere;
- conserva denominadores, n, incertidumbre o umbrales relevantes;
- tiene caveat visible si la conclusion es parcial;
- compara al menos dos familias visuales si es Tier 2;
- evita figuras prohibidas salvo justificacion documentada;
- es legible a tamano PDF;
- no duplica una tabla sin aportar forma, incertidumbre, mecanismo o comparacion;
- guarda artefacto reproducible y, si va a LaTeX, existe en `Plantilla_Latex_GCD/tfgs/figs/`.

## Veredicto operativo

La propuesta multidimensional no necesita mas amplitud; necesita disciplina. El cuerpo deberia quedar como una narracion experimental, no como un catalogo. El apendice debe cargar la exhaustividad. Y el scorecard final solo debe aparecer cuando el lector ya haya visto el camino que lo justifica.

