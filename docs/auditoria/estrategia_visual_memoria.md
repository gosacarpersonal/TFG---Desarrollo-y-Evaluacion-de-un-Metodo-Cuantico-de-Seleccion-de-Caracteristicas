# Estrategia visual de la memoria

> 2026-06-15. Decisión narrativa tras la auditoría completa de memoria,
> propuesta, papers, código y artefactos. El problema ya no es falta de
> rigor ni falta de experimentos: es traducir la profundidad computacional
> del TFG en una secuencia visual que declare la tesis real del trabajo.

## Tesis visual

La memoria debe leerse así:

> Se construye una referencia clásica auditada para evaluar QFS de forma
> defendible; el resultado cuántico no es una victoria predictiva general,
> pero sí produce un diagnóstico metodológico fuerte: cuando QFS se deteriora,
> puede separarse si falla el criterio de información mutua o si falla la
> optimización analógica.

Por tanto, las figuras no deben limitarse a mostrar resultados. Deben responder
preguntas de defensa. Cada figura de cuerpo debe funcionar como un argumento:
qué se hizo, por qué era necesario, qué evidencia lo respalda y qué flanco
queda blindado.

## Principios

1. **Figura = pregunta respondida.** Si una figura no responde una pregunta
   que saldría en defensa, va al apéndice o desaparece.
2. **El cuerpo no es un inventario.** El cuerpo debe contener unas diez figuras
   compuestas; el apéndice conserva trazabilidad y detalle.
3. **El resultado nulo se cuenta como hallazgo.** QFS no mejora de forma
   general, pero el trabajo explica por qué. Esa explicación debe ser visual.
4. **El bloque clásico no es preliminar.** Es la condición de posibilidad del
   diagnóstico cuántico; debe verse como una referencia construida, no como
   preparación.
5. **La simulación se blinda, no se esconde.** La relajación geométrica, el
   oráculo exacto y la comparación criterio--optimizador deben mostrarse de
   forma explícita para evitar una lectura ingenua de "el quantum pierde".

## Figuras de cuerpo

### F1. Banco experimental

**Pregunta:** ¿por qué este banco es más exigente que el de referencia?

Debe mostrar tamaño, dimensionalidad, clases y desbalance en una sola lectura.
Su papel es justificar macro-F1 y preparar la idea de regímenes: problemas
pequeños con señal clara, problemas multiclase, problemas de alta dimensión y
Customer Churn como ancla con los papers QFS.

### F2. Señal supervisada

**Pregunta:** ¿dónde hay señal univariante y dónde no?

Debe hacer visible que Madelon casi no tiene señal univariante tras FDR. Esta
figura anticipa el fallo de criterio de QFS: si el criterio depende de
información mutua por pares, Madelon es el contraejemplo natural.

### F3. Base confiable

**Pregunta:** ¿podemos confiar en los datos, el preprocesado y las particiones?

Debe combinar validación adversarial, drift/conservación y leakage. Su función
es blindar el flanco de que los resultados se deben a particiones sucias o
preprocesado contaminado.

### F4. Perfil de selectores clásicos

**Pregunta:** ¿por qué estos doce métodos y qué aporta cada familia?

Debe mostrar redundancia, coste, estabilidad y separación frente al azar. El
punto no es elegir un campeón universal, sino justificar el roster como espejo
de QFS: relevancia, redundancia, combinación, wrappers y embedded.

### F5. Coste dimensional frente a rendimiento

**Pregunta:** ¿qué se gana al seleccionar menos variables?

Debe mostrar macro-F1 frente a número de variables, con baseline y frontera de
subconjuntos compactos. Su papel es convertir "menos variables" en una
propuesta de valor visible, no solo en una tabla.

### F6. Interpretabilidad real

**Pregunta:** ¿qué variables sostienen los modelos seleccionados?

Debe usar SHAP por instancia, no solo barras de importancia media. Esta figura
demuestra que la profundidad de fase 6 no fue ornamental y conecta selección,
señal estadística y contribución al modelo.

### F7. Significancia frente a magnitud

**Pregunta:** ¿cuándo una diferencia es científicamente afirmable?

Debe mostrar baseline frente a mejor clásico con IC y delta pareado. Es la
figura de honestidad estadística: Madelon mejora; Customer Churn es
significativo por tamaño muestral pero no relevante; Olive 9 no permite afirmar
la mejora.

### F8. Mandos de QFS

**Pregunta:** ¿qué hacen alpha y beta?

Debe separar teoría y operación: alpha recorre cardinalidad en el oráculo QUBO;
beta reordena densidades en el simulador neutral-atom. Debe llevar caveat
explícito: el panel de alpha es control exacto clásico del criterio, no salida
del simulador analógico.

### F9. Criterio frente a optimizador

**Pregunta:** cuando QFS se deteriora, ¿qué falla?

Esta es la figura central de la memoria. Debe colocar Madelon y Customer Churn
en dos diagnósticos distintos, usando la misma unidad de lectura que el resto
de resultados: puntos de macro-F1 perdidos frente al baseline.

- Madelon: el optimizador alcanza el criterio, pero el criterio no predice bien.
- Customer Churn: el criterio casi recupera baseline, pero el simulador no llega
  al mínimo de su función.

Sin esta figura, la memoria parece concluir "QFS no gana". Con esta figura,
concluye "QFS queda diagnosticado".

### F10. Comparación final clásico--cuántico

**Pregunta:** ¿dónde queda QFS frente a baseline, mejor clásico y oráculo?

Debe cerrar por dataset con cuatro referencias: baseline, mejor clásico, QFS-NA
y QFS-oráculo. Debe enlazar visualmente con F9 en los deterioros. Esta figura
convierte la comparación final en lectura por regímenes, no en ranking simple.

## Figuras de apéndice

El apéndice debe conservar las figuras que dan trazabilidad sin cargar el
cuerpo:

- Permutaciones completas método x dataset.
- Leakage por variable.
- Roster completo método x variable.
- SHAP adicional por dataset y por clase.
- Handoff `I_i` / `R_ij`.
- Coste de simulación QFS.
- Solape entre QFS, mRMR y Boruta.
- Macro-F1 frente a AUC en binarios.

Estas figuras no son secundarias por importancia, sino por función: responden a
preguntas de detalle cuando el lector ya ha aceptado la tesis principal.

## Reordenación narrativa sugerida

La sección de resultados debería seguir el orden de las figuras, no el orden
histórico de los notebooks:

1. **Banco y confianza:** F1, F2, F3.
2. **Referencia clásica:** F4, F5, F6, F7.
3. **Método cuántico y diagnóstico:** F8, F9, F10.

Así el lector no siente nueve fases acumuladas, sino tres actos:

1. Se construye un banco fiable.
2. Se obtiene una referencia clásica exigente.
3. Se evalúa QFS y se diagnostican sus límites.

## Qué corregir antes de generar o insertar figuras

1. Actualizar resumen/abstract/resum: deben incluir el resultado cuántico y el
   diagnóstico criterio--optimizador; eliminar marcadores pendientes y cifras
   antiguas de Madelon.
2. Sustituir restos de "siete fases" por el relato correcto: siete fases
   clásicas más fase 8 QFS y fase 9 integración, o directamente nueve fases.
3. Blindar el lenguaje de simulación: QFS-NA es simulador analógico local; el
   oráculo es control exacto clásico del QUBO, no método cuántico.
4. Aclarar variables crudas frente a codificadas en Customer Churn para evitar
   inconsistencias aparentes entre 10 y 15 variables.
5. Decidir si las figuras actuales ya cumplen cada pregunta o si deben
   regenerarse con una composición más argumental.

## Prioridad de ejecución

1. F9 y F10 primero: son el corazón de la nueva tesis.
2. F1-F3 después: blindan la base y preparan los regímenes.
3. F4-F7: convierten la profundidad clásica en evidencia visible.
4. Apéndice: solo cuando el cuerpo ya cuente la historia.

## Estado actual verificado

La comprobación del árbol actual muestra que la arquitectura visual ya está
muy avanzada: las figuras F1--F5 y F7--F10 existen en
`Plantilla_Latex_GCD/tfgs/figs/` y están referenciadas en
`resultados.tex`. También existe `ev6_rendimiento_vs_k.png` y está
insertada como apoyo a la lectura de la escalera de `k`.

El hueco principal no es de existencia de figuras, sino de ajuste entre figura
y tesis:

| Figura | Existe | Insertada | Estado narrativo |
|---|---:|---:|---|
| F1 banco | sí | sí | adecuada como apertura, revisar que el texto la use para justificar regímenes y métrica |
| F2 señal FDR/efecto | sí | sí | clave para anticipar Madelon; debe enlazarse explícitamente con F9 |
| F3 base confiable | sí | sí | adecuada para blindar leakage/drift; evitar que parezca mero control técnico |
| F4 perfil selectores | sí | sí | importante para que el roster sea visible; debe leerse como espejo de QFS |
| O1 organismo de selección | sí | sí | sube la profundidad clásica al cuerpo: doce selectores frente a las 500 variables de Madelon |
| F5 redundancia frente a k | sí | sí | no responde coste-rendimiento; se conserva como maduración/redundancia y `ev6_rendimiento_vs_k` cubre rendimiento frente a k |
| F6 SHAP | sí | sí | contiene beeswarm por instancia para los binarios y Madelon; las barras quedan solo para Olive multiclase, con detalle por clase en apéndice |
| F7 significancia/magnitud | sí | sí | correcta; debe sostener la honestidad de veredictos |
| F8 alpha/beta | sí | sí | correcta si el caption mantiene el caveat de oráculo exacto |
| F9 atribución QFS | sí | sí | figura central; `diag_atribucion_qfs` descompone el deterioro en criterio frente a optimizador |
| F10 QFS vs clásico | sí | sí | cierre natural; debe enlazar con F9 y no leerse como ranking simple |

Figuras de apoyo ya disponibles pero no insertadas en el cuerpo:
`ev7_cierre_narrativo`, `ev8_scorecard_evidencia` y el conjunto A1--A9 del
apéndice. `ev4_recorrido_tfg` ya se regeneró con un generador Pillow, está
insertada en metodología y funciona como mapa de lectura de las nueve fases.
No deben subirse más figuras al cuerpo salvo que sustituyan texto, porque el
riesgo ahora es saturación.

## Próximo trabajo recomendado

1. **Reescribir captions y párrafos de transición**, empezando por F8--F10,
   para que el lector entienda que el hallazgo central es diagnóstico.
2. **Mantener F6 con caption correcto**: ya muestra beeswarm por instancia para
   Breast Cancer, Customer Churn y Madelon; las barras de Olive deben leerse como
   resumen multiclase y el detalle por clase queda en apéndice.
3. **Renombrar mentalmente F5**: el archivo actual muestra redundancia frente a
   `k`, no rendimiento frente al número de variables. Se conserva para explicar
   maduración/redundancia y se apoya con `ev6_rendimiento_vs_k` para la pregunta
   de rendimiento.
4. **Actualizar resumen e introducción antes de tocar más figuras**: las figuras
   pueden ser buenas, pero si el resumen aún dice que la fase cuántica está
   pendiente, la narrativa visual queda descuadrada.
