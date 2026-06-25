# Revision critica de la propuesta visual con criterio `viz-definitive`

Fecha: 2026-06-16  
Documento revisado: `docs/auditoria/propuesta_visualizaciones_multidimensional_2026-06-16.md`  
Criterio aplicado: ruta `viz-definitive` para figuras no triviales de memoria.

## Veredicto corto

La propuesta mejora claramente el roster inicial porque deja de mirar solo el resultado final y recupera dimensiones que estaban escondidas: `k`, semilla, modelo, split validation/test, beta, ocupacion cuantica, geometria y control contra oraculo.

Pero mi juicio critico es este: **todavia hay demasiadas figuras candidatas a cuerpo**. La propuesta es buena como inventario maestro, no como guion final de memoria. Si se suben F0-F19 casi tal cual, la memoria corre el riesgo de parecer un catalogo de resultados en vez de una demostracion experimental. Falta una criba mas dura:

- Que entra porque explica el camino.
- Que entra porque sostiene una conclusion.
- Que se va al apendice porque documenta profundidad.
- Que se queda solo como diagnostico interno.

La regla que aplicaria es: **el cuerpo no debe demostrar que se han probado muchas cosas; debe demostrar por que cada decision experimental era necesaria**.

## Riesgos detectados

### 1. Hay peligro de ir demasiado directo al marcador final

El scorecard final, QFS vs baseline y SHAP vs MI son potentes, pero si aparecen sin una preparacion metodologica fuerte pueden sonar a "miramos el ganador y luego explicamos". Para evitarlo, el cuerpo debe hacer visible el camino:

1. Que los datasets no son intercambiables.
2. Que la seleccion clasica no es un bloque unico, sino un espacio de comportamientos.
3. Que `k`, semilla y modelo cambian la lectura.
4. Que validation y test no cumplen el mismo papel.
5. Que la comparacion QFS solo tiene sentido despues de fijar un baseline clasico y un criterio.

La propuesta ya incluye piezas para esto, pero algunas estan marcadas como figuras de cuerpo sin que su pregunta este aun lo bastante afilada.

### 2. Muchas figuras mezclan "evidencia" con "exploracion"

Ejemplos:

- F9 rendimiento selector x k x dataset puede ser central, pero tambien puede convertirse en una pared de puntos si no se reduce a una pregunta concreta.
- F14 barrido beta y F16 control QFS-oraculo comparten eje narrativo; separarlas puede duplicar la historia cuantica.
- F17 geometria Rydberg y F18 ocupacion feature x beta son valiosas, pero no necesariamente conclusivas para el cuerpo.

Segun `viz-definitive`, una figura de memoria debe tener un mensaje, denominador, metrica y caveat. Varias figuras actuales aun son "mapas de todo lo que existe".

### 3. Falta explicitar metricas derivadas antes de dibujar

La propuesta lista columnas y tablas, pero varias figuras necesitan una metrica intermedia defendible:

- F4 estabilidad: no basta con Jaccard bruto; conviene resumir por mediana/IQR por selector, dataset y k, y reservar la matriz completa al apendice.
- F7 embudo validation-test: debe definir `delta_test_vs_validation`, retencion de ranking o cambio de rank.
- F8 dependencia del modelo: debe separar efecto del selector, efecto del modelo y posible interaccion.
- F12 SHAP vs MI: debe definir una discordancia comparable, por ejemplo rank normalizado o z-score por dataset, porque MI y SHAP no tienen escala comun.
- F14/F16 QFS: debe definir "zona operativa" o frontera beta, no solo trazar todas las curvas.
- F19 scorecard: cada celda debe tener un criterio reproducible, no un veredicto manual.

Sin esas metricas, la visualizacion puede parecer mas precisa de lo que realmente es.

### 4. Faltan caveats visibles

Hay tres caveats que deberian aparecer en titulos, subtitulos o notas, no escondidos en texto:

- SHAP depende del modelo entrenado; no es una verdad universal de la variable.
- MI univariante puede fallar en interacciones; esto es precisamente parte del diagnostico, no una sorpresa posterior.
- QFS simulado / QFS-NA / oraculo exacto no son el mismo objeto experimental; la figura debe separar criterio, optimizador y ejecucion cuantica simulada.

### 5. El apendice debe tener arquitectura, no ser un vertedero

La propuesta de apendice es rica, pero debe organizarse por funcion:

- Trazabilidad de datos y particiones.
- Barridos clasicos completos.
- Interpretabilidad completa.
- Barridos cuanticos completos.
- Controles negativos / leakage / drift / estabilidad.

Si no, el apendice se convierte en "todo lo que no cupo".

## Criba recomendada

### Cuerpo de memoria: figuras que si defenderia

| ID propuesta | Decision | Motivo | Ajuste recomendado |
|---|---|---|---|
| F0 Cadena de evidencia | **Cuerpo** | Explica el camino experimental y evita salto al resultado final. | Hacerla metodologica, no decorativa: artefactos, decisiones y salidas verificables. |
| F1 Mapa de cobertura experimental | **Cuerpo** | Da trazabilidad y escala del trabajo. | Usar matriz/dot matrix, no infografia. Mostrar huecos si existen. |
| F2 Espacio-problema | **Cuerpo** | Justifica que los datasets no se comparan como clones. | Scatter simple con etiquetas y caveat de escala log. |
| F3 Perfil global de selectores | **Cuerpo** | Presenta el mapa clasico antes de elegir ganadores. | Dot/scatter con coste, estabilidad y redundancia; evitar sobrecodificar. |
| F4 Estabilidad frente a semillas y k | **Cuerpo reducido + apendice completo** | Es camino experimental real, no resultado final. | En cuerpo: resumen robusto; en apendice: matriz completa. |
| F5 Solape entre metodos | **Cuerpo si se resume bien** | Explica familias de selectores y redundancia metodologica. | Una matriz representativa o clustermap resumido; full 5 datasets al apendice. |
| F6 Senal frente al nulo | **Cuerpo o apendice segun capitulo** | Es clave para no sobreinterpretar MI. | Si Madelon es central al argumento, subir una version compacta al cuerpo. |
| F7 Embudo validation-test | **Cuerpo** | Es una pieza que faltaba: muestra el proceso de seleccion, no solo el ganador. | Mejor dot/slope/rank-change que Sankey si hay pocos estados. |
| F8 Dependencia del modelo | **Cuerpo** | Evita atribuir al selector lo que puede ser del clasificador. | Dot matrix o slopegraph por modelo; explicitar metrica y split. |
| F10 Coste vs rendimiento | **Cuerpo si sostiene parsimonia** | Defiende reduccion de variables sin perder rendimiento. | Usar frontera/parsimony plot, no nube completa indiscriminada. |
| F11 Magnitud y significancia | **Cuerpo** | Es la prueba estadistica del efecto. | Forest plot con IC, p-FDR y n/bootstrap visible. |
| F12 SHAP vs MI | **Cuerpo** | Es el diagnostico mecanistico mas fuerte. | Usar ranks/z-scores por dataset; anotar outliers; caveat SHAP-modelo. |
| F14 + F16 QFS beta/control | **Cuerpo fusionado si cabe** | Juntas cuentan criterio, beta y calidad contra oraculo. | Figura multipanel 2x2 solo si cada panel cumple un rol; si no, F16 al apendice. |
| F15 QFS vs baseline clasico | **Cuerpo** | Es comparacion final cuantica con incertidumbre. | Forest/slope con IC y veredicto estadistico. |
| F19 Scorecard final | **Cuerpo, cierre** | Sintetiza sin reemplazar las pruebas. | Scorecard con criterios reproducibles y notas de incertidumbre. |

Esto deja unas **13-14 figuras de cuerpo**, pero varias son pequenas o metodologicas. Si hay que recortar, recortaria antes F5, F6 o F10 que F7/F8/F11/F12/F15.

### Apendice: figuras valiosas pero no necesariamente de cuerpo

| ID propuesta | Decision | Motivo |
|---|---|---|
| F9 Rendimiento selector x k x dataset | **Apendice + extracto en cuerpo** | Completo es demasiado ancho; en cuerpo conviene una sintesis por frontera o top-N. |
| F13 SHAP beeswarm representativo | **Apendice o cuerpo muy selectivo** | Visualmente util, pero no debe competir con F12 si F12 ya explica la discordancia. |
| F17 Geometria atomos Rydberg | **Apendice recomendado** | Enseña sustrato fisico, pero no parece explicar por si sola el deterioro/mejora. |
| F18 Ocupacion feature x beta | **Apendice fuerte** | Gran profundidad cuantica; demasiado granular para argumento principal. |
| A1-A12 | **Apendice estructurado** | Mantener, pero agrupadas por funcion experimental. |

### Diagnostico interno o candidatos a degradar

| Figura | Riesgo | Decision |
|---|---|---|
| Cualquier heatmap completo de cientos de features | Ilegible en PDF; parece exhaustivo pero comunica poco. | Apendice, top-k, o resumen estadistico. |
| Cualquier figura con todos los modelos, datasets, k y selectores a la vez | Sobrecarga perceptiva. | Dividir por pregunta o resumir con metrica derivada. |
| Diagramas de flujo tipo Sankey si solo hay 3-4 estados | Dan mucho peso visual a una decision simple. | Usar slope/rank/dot flow. |
| Scorecard sin reglas de puntuacion | Parece editorial en vez de cientifico. | Definir reglas antes. |

## Figuras que faltan o estan poco explicitas

### M1. Auditoria de particiones y leakage

No basta con que exista en apendice A11. Deberia haber al menos una figura o tabla breve en cuerpo, probablemente cerca de F1/F2, que diga:

- splits usados;
- tamanos train/validation/test;
- criterio de estratificacion;
- controles de leakage/drift;
- datasets con advertencias.

Puede ser una tabla visual compacta, no necesariamente una grafica grande. Sin esto, el lector ve muchas metricas pero no ve aun la confianza en la particion experimental.

### M2. De seleccion bruta a candidatos modelados

F7 va en esta direccion, pero la pregunta debe ser mas concreta: **como se pasa de cientos de configuraciones clasicas a las candidatas finales**. No es solo validation-test; es el proceso de filtrado:

- selector;
- k;
- modelo;
- split;
- criterio de desempate;
- coste o parsimonia.

Esta figura es importante porque explica camino, no resultado.

### M3. Estabilidad de la conclusion, no solo estabilidad del selector

F4 mide estabilidad de seleccion. Pero falta una pieza mas cercana a la tesis:

- la conclusion cambia si uso macro-F1, balanced accuracy o AUC?
- cambia si miro otro modelo?
- cambia si penalizo coste?

Parte esta en A9 y F8, pero conviene que el cuerpo tenga una mini-figura o columna en F19 que diga si la conclusion es robusta a metricas alternativas.

### M4. Criterio QFS separado de optimizador QFS

El texto debe evitar que el lector piense que "QFS falla/acierta" como una caja unica. La visualizacion debe separar:

- criterio QUBO/MI/redundancia;
- embedding/geometria;
- optimizador/sampling QFS-NA;
- evaluacion downstream con modelo clasico.

F14-F16 pueden hacerlo, pero solo si se disenan como una cadena causal. Si son curvas sueltas por beta, se pierde esa separacion.

## Ruta final recomendada para no ir directo al final

1. **Confianza experimental:** F0 + F1 + auditoria compacta de splits/leakage.
2. **Por que cada dataset se interpreta por separado:** F2.
3. **Mapa clasico antes de elegir:** F3 + F4/F5 resumidas.
4. **Como se filtran candidatos:** F7.
5. **Robustez frente al modelo y metrica:** F8 + nota/mini-panel de metricas alternativas.
6. **Prueba estadistica y coste:** F10/F11.
7. **Mecanismo del fallo/acierto:** F12, con F13 solo si aporta lectura individual.
8. **QFS como criterio + optimizador + beta:** F14/F16 fusionada o secuencial.
9. **Comparacion final:** F15.
10. **Cierre sintesis:** F19.

Con esta ruta, el scorecard final no aparece como salto, sino como consecuencia.

## Decision sobre las figuras cuanticas F14/F16/F15

Mi recomendacion: **fusionar F14 y F16, no fusionar F15**.

- F14 y F16 comparten beta y explican el comportamiento interno de QFS. Una figura multipanel puede contar: rendimiento, cardinalidad, Hamming contra oraculo y delta de coste.
- F15 debe quedarse aparte porque responde otra pregunta: no "como se comporta QFS por dentro", sino "que aporta frente al baseline".

Si la figura fusionada queda cargada, dejaria en cuerpo solo dos paneles:

- beta vs rendimiento/cardinalidad;
- beta vs discrepancia con oraculo.

Y mandaria el resto al apendice.

## Decision sobre las figuras nuevas del roster anterior

- **Geometria de atomos Rydberg:** apendice, salvo que el capitulo cuantico necesite una figura pedagogica. No parece una prueba central del resultado.
- **Dependencia del modelo:** cuerpo. Esta es mas importante de lo que parecia: protege la memoria de una critica seria, que es confundir selector con clasificador.

## Criterio de construccion antes de programar

Antes de generar cada figura de cuerpo, haria una ficha minima:

```yaml
id:
pregunta:
clase: memory_candidate | appendix | diagnostic_internal | remove
tabla_origen:
joins:
metrica_derivada:
familia_elegida:
familia_rechazada:
unidad_de_facet:
denominador:
caveat_visible:
criterio_de_exito:
```

Si una figura no puede rellenar esa ficha, no deberia construirse aun.

## Conclusion

No creo que falten mas resultados; creo que falta **jerarquia**. El material esta. La mejora no es crear mas figuras, sino convertir el inventario en una narracion experimental:

- primero confianza;
- luego mapa de decisiones;
- despues pruebas;
- despues mecanismo;
- finalmente comparacion.

Mi recomendacion operativa es no empezar por F12 ni por F19. Empezaria por **F0/F1/F7/F8**, porque son las que obligan a explicar el camino. Despues construiria F11/F12/F15/F19, que son las figuras de conclusion.
