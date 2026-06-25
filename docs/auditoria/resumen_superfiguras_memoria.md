# Resumen de superfiguras para la memoria

> 2026-06-16. Matriz de decision para ubicar superfiguras en la memoria,
> indicando numero de subfiguras/paneles, seccion, pregunta cientifica,
> aportacion y motivo de ubicacion. No se aplica ningun maximo artificial de
> paneles: el numero se decide por unidad experimental y funcion narrativa.

## Tabla general

| ID | Superfigura | Nº subfiguras recomendado | Seccion de memoria | Pregunta que responde | Que aporta | Por que va ahi |
|---|---|---:|---|---|---|---|
| SF1 | Recorrido experimental del TFG | 1 panel grande con 9-10 nodos internos | `metodologia.tex` -> `Diseño experimental` | ¿Cual es el camino completo que convierte datos crudos en comparacion clasico--cuantica? | Mapa de lectura: fases clasicas, fase QFS, integracion, diagnostico y cierre | Metodologia debe explicar el contrato experimental antes de mostrar resultados; esta figura orienta al lector |
| SF2 | Banco experimental / regimenes | 4 subfiguras | `resultados.tex` -> `Construcción y auditoría de la base experimental` / `Regímenes del banco como predictores` | ¿Que tipo de problemas son las cinco formulaciones y por que no deben promediarse sin contexto? | Tamaño, dimensionalidad, clases, desbalance, señal y etiqueta de regimen | Abre resultados porque justifica la metrica, la dificultad y la lectura por dataset |
| SF3 | Cadena de validez experimental | 2 subfiguras principales; expansion 5 x 7-9 en apendice | `resultados.tex` -> `Particionado y auditoría de las particiones`; expansion en `apendice.tex` -> `Figuras complementarias de auditoría` | ¿Podemos confiar en datos, preprocesado, splits y tests antes de comparar metodos? | Pantalla de controles: FDR, efecto, drift, leakage, adversarial validation, bootstrap y permutaciones | Debe aparecer antes del rendimiento para blindar que las diferencias no vienen de artefactos |
| SF4 | Espacio clasico de selectores | 4-6 subfiguras | `resultados.tex` -> `Evaluación de los métodos clásicos` / `Caracterización de la selección` | ¿Que cubren los doce selectores y por que son una referencia clasica completa? | Familias, coste, estabilidad, redundancia, señal frente a nulo y seleccion materializada | Va antes del modelado porque define el repertorio de subconjuntos que luego se evalua |
| SF5 | Trayectorias en `k` | 5 subfiguras, una por formulacion | `resultados.tex` -> `Evaluación de los métodos clásicos` / `Modelado y evaluación estadística` | ¿Como evoluciona rendimiento/redundancia al variar el presupuesto de variables? | Relaciona `k`, seleccion, parsimonia, redundancia, rendimiento y referencia QFS puntual | Pertenece al puente entre seleccion y modelado; muestra el procedimiento, no solo el veredicto |
| SF6 | Comparacion final clasico vs QFS | 1 subfigura compacta con 5 filas x 4 enfoques | `resultados.tex` -> `Comparación entre enfoques` | ¿Donde quedan baseline, mejor clasico, QFS-NA y oraculo exacto por dataset? | Marcador final por formulacion con IC/deltas/veredicto | Esta seccion debe cerrar la comparacion externa antes del diagnostico interno |
| SF7 | Tablero QFS: `alpha`, `beta`, MDS y criterio--optimizador | 4-6 subfiguras compactas; expansion 12+ en apendice | `resultados.tex` -> `Evaluación del método cuántico` y `Diagnóstico criterio--optimizador`; expansion en apendice | ¿Que parte del deterioro QFS viene del criterio, del optimizador o de la geometria? | Separa escalera de `alpha`, barrido `beta`, densidades/readout, Hamming/coste, MDS y perdida macro-F1 | Debe dividirse entre mecanismo QFS y diagnostico; es el nucleo explicativo del resultado nulo/deteriorado |
| SF8 | Microdiagnostico SHAP / variables / solape | 6 subfiguras en cuerpo para Madelon+Churn; 15+ si se expande a todos | `resultados.tex` -> `Modelado y evaluación estadística` o `Diagnóstico criterio--optimizador`; expansion en apendice | ¿Las variables seleccionadas por clasicos/QFS coinciden con las que realmente sostienen el modelo? | Conecta SHAP, seleccion clasica, QFS, `I_i`, solape y ausencia/presencia de variables | Va donde se explica por que el modelo funciona o por que QFS falla; Madelon/Churn justifican el diagnostico |
| SF9 | Mapa final de evidencia | 1 matriz grande | `resultados.tex` -> `Consistencia, pruebas y discusión` o cierre de `Comparación entre enfoques` | ¿Que conclusion integrada resiste para cada dataset? | Matriz dataset x evidencia: regimen, clasico, QFS, criterio, optimizador, MDS, consistencia, veredicto | Cierra la memoria de resultados: no introduce datos nuevos, sintetiza la defensa |

## Detalle por superfigura

### SF1 — Recorrido experimental del TFG

**Numero:** 1 panel grande. Internamente puede contener 9-10 nodos: auditoria
raw, preprocesado, auditoria processed, splits, seleccion clasica, modelado,
comparacion clasica, QFS, integracion, diagnostico/sintesis.

**Seccion:** `metodologia.tex`, `Diseño experimental`.

**Pregunta:** ¿cual es el protocolo completo y por que las fases previas no son
preparacion ornamental?

**Aporta:** orden mental. Hace visible que la referencia clasica auditada es la
condicion de posibilidad para diagnosticar QFS.

**Por que ahi:** metodologia debe fijar el camino antes de que resultados
empiecen a desplegar evidencia.

### SF2 — Banco experimental / regimenes

**Numero:** 4 subfiguras.

1. Tamaño muestral frente a dimensionalidad.
2. Desbalance y numero de clases.
3. Señal supervisada/FDR/tamaño de efecto.
4. Regimen sintetico por formulacion.

**Seccion:** `resultados.tex`, `Construcción y auditoría de la base experimental`
y, de forma natural, `Regímenes del banco como predictores`.

**Pregunta:** ¿por que cinco formulaciones producen cinco lecturas
experimentales distintas?

**Aporta:** evita el error de promediar todo. Anticipa que Madelon, Churn,
Breast Cancer y Olive no tensionan el pipeline igual.

**Por que ahi:** es la primera evidencia de resultados; prepara la metrica y la
lectura por regimen.

### SF3 — Cadena de validez experimental

**Numero:** 2 subfiguras en cuerpo:

1. Cadena/pipeline de controles.
2. Matriz `dataset x control`.

Expansion posible: una figura por familia de controles o una matriz completa
5 x 7-9 en apendice.

**Seccion:** `resultados.tex`, `Particionado y auditoría de las particiones`.
La version expandida va en `apendice.tex`, `Figuras complementarias de auditoría`.

**Pregunta:** ¿los resultados posteriores se apoyan en una base limpia y
estadisticamente defendible?

**Aporta:** convierte FDR, efecto, leakage, drift, adversarial validation,
bootstrap y permutaciones en cadena de confianza.

**Por que ahi:** debe aparecer antes de comparar selectores y modelos, porque
legitima los experimentos posteriores.

### SF4 — Espacio clasico de selectores

**Numero:** 4-6 subfiguras. Version de 4:

1. Familias/registro de los 12 selectores.
2. Coste computacional.
3. Estabilidad.
4. Redundancia/señal frente a nulo.

Version de 6 si se separan `redundancia`, `permutacion` y `seleccion
materializada`.

**Seccion:** `resultados.tex`, `Evaluación de los métodos clásicos` ->
`Caracterización de la selección`.

**Pregunta:** ¿la referencia clasica es amplia, diversa y suficientemente fuerte
para comparar QFS?

**Aporta:** demuestra que no se compara QFS contra un baseline pobre. Los doce
selectores cubren relevancia, redundancia, wrappers, embedded y criterios
combinados.

**Por que ahi:** antes de modelar hay que explicar que significan los
subconjuntos que entran al modelo.

### SF5 — Trayectorias en `k`

**Numero:** 5 subfiguras, una por formulacion. Dentro de cada una pueden
coexistir curvas de selectores, baseline, mejor clasico y referencias QFS si
son puntuales.

**Seccion:** `resultados.tex`, `Modelado y evaluación estadística`.

**Pregunta:** ¿que ocurre cuando el presupuesto de variables cambia?

**Aporta:** muestra procedimiento: no solo que un metodo gana, sino como se
madura la seleccion al crecer `k`, cuando aparece redundancia y cuando el
rendimiento se estabiliza o cae.

**Por que ahi:** es el puente natural entre caracterizacion de seleccion y
evaluacion predictiva.

### SF6 — Comparacion final clasico vs QFS

**Numero:** 1 subfigura compacta. Estructura recomendada: 5 filas por dataset y
4 enfoques: baseline, mejor clasico, QFS-NA y QFS-oraculo.

**Seccion:** `resultados.tex`, `Comparación entre enfoques`.

**Pregunta:** ¿QFS iguala, supera o deteriora la referencia clasica auditada?

**Aporta:** marcador final, con deltas/IC/veredicto sin esconder el oraculo
exacto ni el simulador.

**Por que ahi:** esta seccion debe resolver la comparacion externa antes de
entrar a explicar internamente por que ocurre.

### SF7 — Tablero QFS: `alpha`, `beta`, MDS y criterio--optimizador

**Numero:** 4-6 subfiguras en cuerpo:

1. Escalera de `alpha` del oraculo exacto.
2. Barrido de `beta` en validacion o densidad.
3. Control Hamming/coste frente al oraculo.
4. Error MDS/geometria.
5. Plano criterio--optimizador.
6. Mini resultado QFS vs oraculo/baseline para casos protagonistas.

Expansion: 12 o mas subfiguras en apendice si se hacen 5 paneles de `alpha`, 5
de `beta`, MDS y diagnostico separado.

**Seccion:** repartida entre `Evaluación del método cuántico` y
`Diagnóstico criterio--optimizador`.

**Pregunta:** cuando QFS se deteriora, ¿falla el criterio, el optimizador
analogico simulado o la geometria/embebido?

**Aporta:** la tesis metodologica central. Separa mecanismo (`alpha`, `beta`,
MDS) de atribucion del fallo (criterio vs optimizador).

**Por que ahi:** primero se debe explicar como opera QFS; despues, en la seccion
de diagnostico, se atribuye el deterioro.

### SF8 — Microdiagnostico SHAP / variables / solape

**Numero:** 6 subfiguras en cuerpo si se centra en Madelon y Customer Churn:

1. Solape/seleccion Madelon.
2. SHAP Madelon.
3. Ranking `I_i`/posicion QFS Madelon.
4. Solape/seleccion Churn.
5. SHAP Churn.
6. Ranking `I_i`/posicion QFS Churn.

Expansion completa: 15 o mas subfiguras para 5 formulaciones x 3 capas, mas
desgloses multiclase de Olive.

**Seccion:** si se usa para explicar modelos, `Modelado y evaluación
estadística`; si se usa para explicar fallo QFS, `Diagnóstico
criterio--optimizador`. La expansion completa debe ir al apendice.

**Pregunta:** ¿las variables que seleccionan los metodos coinciden con las que
el modelo usa realmente?

**Aporta:** baja el veredicto macro a nivel variable. En Madelon puede sostener
el fallo de criterio; en Churn puede mostrar si QFS pierde por seleccion
operativa aunque el criterio sea recuperable.

**Por que ahi:** es una figura de explicabilidad causal-operativa; no debe
abrir resultados, sino intervenir cuando ya se sabe que hay una diferencia que
explicar.

### SF9 — Mapa final de evidencia

**Numero:** 1 matriz grande. Internamente puede tener 5 filas x 6-8 columnas:
regimen, validez, mejor clasico, QFS-NA, oraculo, criterio, optimizador, MDS,
consistencia, veredicto.

**Seccion:** `resultados.tex`, `Consistencia, pruebas y discusión`. Tambien
puede cerrar `Comparación entre enfoques` si se quiere que sea el ultimo
elemento antes de conclusiones.

**Pregunta:** ¿que conclusion integrada queda por dataset despues de todo el
recorrido?

**Aporta:** sintesis defensiva. No sustituye las figuras anteriores; recoge su
veredicto y caveats en una matriz trazable.

**Por que ahi:** solo tiene sentido al final, cuando el lector ya ha visto la
evidencia granular.

## Recuento recomendado

| ID | Cuerpo | Expansion apendice |
|---|---:|---:|
| SF1 | 1 | 1 |
| SF2 | 4 | 5+ si se hacen fichas por dataset |
| SF3 | 2 | 5-9 o matriz completa de controles |
| SF4 | 4-6 | 12+ si se desagrega por metodo/dataset |
| SF5 | 5 | 5 o mas si se separan modelos |
| SF6 | 1 | 5 si se separa por dataset |
| SF7 | 4-6 | 12+ |
| SF8 | 6 | 15+ |
| SF9 | 1 | 1 |

**Total cuerpo orientativo:** entre 28 y 32 paneles repartidos en 9
superfiguras. Es razonable para este TFG si cada superfigura tiene una pregunta
clara y una tabla fuente auditable.

## Orden narrativo recomendado

1. SF1 en metodologia: mapa del protocolo.
2. SF2 en apertura de resultados: banco/regimenes.
3. SF3 antes de rendimiento: validez experimental.
4. SF4 antes de modelado: referencia clasica.
5. SF5 durante modelado: recorrido en `k`.
6. SF8 donde haga falta explicar variables: modelos o diagnostico.
7. SF6 al abrir comparacion clasico--QFS.
8. SF7 como nucleo de QFS y diagnostico.
9. SF9 al cierre: evidencia integrada.

## Criterio final

Una superfigura entra en cuerpo si responde una pregunta que cambia la lectura
de la memoria. Entra en apendice si conserva trazabilidad, reproduce detalle o
permite auditar una afirmacion ya defendida en cuerpo.
