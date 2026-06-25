# Plan de reequilibrio cuántico ↔ clásico — 2026-06-18

**Decisión del autor:** aplicar *ambas* palancas (degradar detalle clásico al
apéndice + expandir el cuántico) y **aprobar este plan antes de ejecutar**.

**Diagnóstico medido (capítulo de Resultados, palabras de cuerpo):**
clásico 3 299 (64 %) · cuántico+comparativa 1 365 (27 %) · discusión 480 (9 %).
La subsección más larga de la memoria es *Modelado clásico* (989); *Evaluación
del método cuántico* tiene 424. El objeto del TFG es minoría en su capítulo.

**Objetivo (centro de gravedad, no porcentaje):** que el capítulo de Resultados
tenga su centro de gravedad en QFS y la comparativa. El ~50 % es un **termómetro
de control, no una meta**: si el capítulo respira cuántico con menos, perfecto;
no se infla texto para "llegar al número". El cuántico crece con **mecanismo que
hoy falta**, no con relleno. (Recuentos por subsección verificados con conteo
sobre los `.tex`.)

**Segundo eje (revisión externa de presentación):** la memoria "parece a ratos
outputs de notebook pegados en LaTeX". Se añade un eje de **capa visual**
(sección G) independiente del contenido.

**PRINCIPIO RECTOR (ajuste del autor) — cuerpo ligero, apéndice defendible:**
en el cuerpo solo van **tablas/figuras de veredicto** (pocas columnas, lectura
inmediata). Toda evidencia densa pero valiosa —clásica *o* cuántica— va al
apéndice y **se referencia inline** en el punto exacto donde se afirma algo
("…como detalla la Tabla~A.x / Figura~A.y"). Así cada afirmación queda
defendible sin colar tablas y figuras todo el rato. Esta regla **generaliza** la
palanca A: no es "degradar lo clásico", es "el cuerpo argumenta, el apéndice
prueba".

---

## A. Degradar el detalle clásico al apéndice (mantener veredictos)

Regla: en el cuerpo se queda el *régimen* y el *veredicto*; la mecánica
reproducible baja al apéndice. Nada se borra.

| Sección | Ahora | Acción | Queda en cuerpo (~) | Va al apéndice |
|---|---|---|---|---|
| §5.1.1–5.1.3 (audit datos) | 584 | Condensar prosa; tablas `postproc`/`particiones` → apéndice | 350 | Tablas postproc + particiones + detalle de drift |
| §5.1.4 Regímenes | 468 | **Mantener** (es el puente que predice el cuántico) + `tab:regimenes` | 468 | — |
| §5.2.1 Caracterización selección | 573 | Mantener veredicto + `tab:perfil`; mover figura "organismo" y detalle de permutación | 300 | Discusión de permutación/organismo |
| §5.2.2 Modelado clásico | 989 | Mantener `tab:comparacion`, veredicto, Madelon y el puente de variables; `tab:candidatos` → apéndice; recortar discusión XGBoost | 500 | `tab:candidatos`, detalle de la parrilla |
| §5.2.3 Comparación final | 236 | Mantener (cierre breve) | 200 | — |
| §5.2.4 Espejo de QFS | 347 | **Mover a §5.4** (es cuántico-comparativo, hoy mal ubicado) | → cuántico | — |

**Reducción del clásico en cuerpo:** ~3 299 → ~1 800.

---

## B. Expandir el cuántico (lo que falta)

### B1. Marco §2.3 Computación adiabática (196 → ~300, tope)
Añadir lo justo para entender el **protocolo QFS**: gap mínimo, condición
adiabática frente al tiempo de evolución y el *driving* de dos pasos conectado
con Ω, Δ global y detuning local. **[Condición del revisor]** *No* convertir el
marco en una clase de física: el objetivo es el protocolo, no demostrar la
computación adiabática. *No* tocar §2.4 (Rydberg ya está dimensionado).

### B2. NUEVA subsección §5.3.0 "El mecanismo de QFS sobre el banco" (~600 + figura)
**[AJUSTE del autor: las CINCO formulaciones, no una.]** La pieza que **hoy no
existe**: cómo funciona el método de verdad. Se explica la cadena genérica una
vez —grafo $I_i$/$R_{ij}$ → posiciones de los átomos (MDS) → densidad de Rydberg
por átomo → corte top-$k$ → subconjunto— y se lee sobre las cinco.
- **Figura nueva = "organismo cuántico"** (small-multiples, 5 paneles, uno por
  formulación, al β elegido). Datos verificados disponibles para las cinco:
  posiciones por átomo en `qfs_embedding_error.positions_json`
  (`{feature,x,y}`) y **densidad de Rydberg por variable** en
  `qfs_runs_<ds>_<beta>.csv` (columnas `density__<var>`). Cada panel: átomos en
  su posición MDS, color = densidad de Rydberg, contorno = seleccionado por el
  corte top-$k$, tamaño = relevancia $I_i$. Es el equivalente cuántico del
  "organismo" clásico de Madelon y de la figura de regímenes.
- Prosa **proporcional**: los casos con historia (Churn = el optimizador gasta
  cupo en dummies; Madelon = densidades sobre distractores) se leen con detalle;
  los limpios (Olive 3, BCW) en una o dos frases.
- **[Condición del revisor — legibilidad estricta]** riesgo real de "potente
  pero ilegible". Reglas: **no** codificar cuatro canales a la vez; lo esencial
  es color = densidad de Rydberg y marcador = seleccionado. El tamaño = $I_i$
  solo si no satura (si no, fuera). **Etiquetas solo para variables
  seleccionadas**, leyenda común a los cinco paneles, caption corto. **Fallback:**
  si los 5 paneles no quedan legibles, partir en dos figuras o reducir canales.
  Esta figura **es el cuello de botella**: se construye y se juzga ANTES de
  escribir el texto que la describe (ver orden de ejecución).

### B3. §5.3 Evaluación del método cuántico (424 → ~750)
Se integra con B2: tras el mapa de mecanismo, el resultado **por dataset** (qué
seleccionó QFS-NA, qué densidades, efecto real de β en el *readout*), leído
formulación a formulación como el bloque clásico. Apoyo: el organismo cuántico
(B2) sustituye o limpia las figuras `qfs_beta_map_*`/`fase9_resumen_*` actuales
si resultan poco legibles.

### B4. §5.4 Comparación entre enfoques (552 + 347 reubicado → ~1 100)
- Absorber aquí §5.2.4 (espejo de QFS), que es comparativo.
- **Comparar en las 4 coordenadas, no solo macro-F1:** añadir la redundancia
  interna y la compacidad del subconjunto QFS-NA frente a mRMR/Boruta (datos ya
  disponibles), no solo el F1.
- **NUEVA tabla (resumen, en cuerpo):** robustez del veredicto de QFS-NA por
  dataset — mejor modelo, rango de macro-F1 entre los 4 modelos y si la
  conclusión cambia o no. **[Condición del revisor]** la rejilla completa de los
  4 modelos × dataset va al **apéndice**, no al cuerpo (evitar otra tabla grande
  de resultados). Desde `qfs_model_results.csv`.
- **NUEVA tabla:** subconjunto QFS-NA vs mRMR vs oráculo por dataset (Jaccard +
  nombres de variables seleccionadas), consolidando lo que hoy está disperso en
  prosa. Compacta → puede ir en cuerpo; la versión extensa, al apéndice.

### B5. §5.5 Diagnóstico criterio–optimizador (389 → ~600)
Extender el análisis variable a variable **solo donde aporte diagnóstico**
**[condición del revisor]**: detalle en Churn (cupo en dummies) y Madelon
(criterio sobre feat\_xxx); lectura corta en Breast Cancer y Olive Oil. Conecta
la densidad de Rydberg de cada átomo con la atribución. Apoya en `tab:atribucion`
(ya creada) + las densidades.

**Aumento del cuántico en cuerpo:** ~1 365 → ~3 350.

---

## C. Efecto neto estimado (Resultados)

| Bloque | Antes | Después |
|---|---|---|
| Clásico (cuerpo) | 3 299 (64 %) | ~1 800 (~34 %) |
| Cuántico + comparativa | 1 365 (27 %) | ~3 450 (~54 %) |
| Discusión/consistencia | 480 (9 %) | ~700 (~13 %) |

Se cumple el objetivo: **el cuántico pasa a mayoría en su capítulo**, sin perder
la referencia clásica (sigue íntegra, repartida entre cuerpo condensado y
apéndice).

---

## D. Lo que NO se toca
- La tesis y el relato régimen→mecanismo→resultado (se refuerzan, no cambian).
- Los números canónicos (todo sale de los CSV ya verificados).
- El estado del arte (su parte cuántica ya está bien dimensionada: 606 vs 232).
- El bloque clásico desaparece del cuerpo solo en su *detalle mecánico*; sus
  veredictos y el régimen siguen en Resultados.

## E. Riesgos y mitigación
- **Crecimiento del apéndice:** aceptable (es su función); se mantiene el índice
  de trazabilidad.
- **Figura nueva de mecanismo:** se construye con matplotlib desde datos reales
  (posiciones + densidades), ejecución estricta, formato PDF, caption corto.
- **Coherencia de referencias:** al mover §5.2.4 y tablas, revisar todos los
  `\ref` (compilación detecta los rotos).

## G. Capa visual y presentación (eje nuevo)

Diagnóstico de la revisión externa: tablas apretadas (Cuadro 5.2), tablas
"CSV en papel" (Cuadro A.1 de trazabilidad), captions demasiado largos con
metodología dentro (Cuadro 5.7), figuras pensadas para pantalla y no para PDF
(Figura 5.19, cadena de tests, horizontal y con letra diminuta), y sobrecarga
de evidencia en el cuerpo. Acciones:

### G1. Infraestructura de tablas
- Adoptar **`booktabs`** (`\toprule/\midrule/\bottomrule`, sin `\hline`) y
  **`tabularx`** (columna `X` que reparte ancho y permite salto de línea), más
  `array`/`ragged2e` para cabeceras. `siunitx` (opcional) para alinear decimales.
- **Prohibido** `\resizebox{\textwidth}{!}{...}` como solución general (encoge la
  letra; deja tablas "correctas pero feas"). Si una tabla no cabe legible, se
  parte o se va al apéndice.

### G2. Política de captions (1–2 líneas)
El pie dice **qué es** la tabla/figura; la explicación metodológica (AUC,
multiclase, one-hot, convenciones) se mueve al **texto** antes o después, no al
caption. Reescribir los pies largos: `tab:candidatos`, `tab:qfs-control`,
`tab:atribucion`, `tab:cadena-tests`, `tab:postproc`.

### G3. Colocación de cada tabla (cuerpo = veredicto; resto → apéndice + ref inline)
| Tabla | Destino | Motivo |
|---|---|---|
| `tab:comparacion` (5.1 clásica) | **Cuerpo** | veredicto |
| `tab:qfs-comparacion` (QFS vs baseline) | **Cuerpo** | veredicto |
| `tab:atribucion` (criterio/optimizador) | **Cuerpo** | tesis central |
| `tab:qfs-control` (Hamming/Δcoste) | **Cuerpo** (compacta) | veredicto cuántico |
| `tab:regimenes` | **Cuerpo** (simplificada) | puente al cuántico |
| `tab:senal`, `tab:postproc`, `tab:particiones` | **Apéndice** | auditoría densa |
| `tab:perfil` (12 selectores) | **Apéndice** | densa; en cuerpo solo el veredicto |
| `tab:candidatos` (15×7) | **Apéndice** | densa |
| `tab:embedding` | **Apéndice** | apoyo |
| `tab:cadena-tests` | **Apéndice** | mapa de referencia |
| `tab:ap-indice-trazabilidad` (A.1) | **Apéndice**, rediseñada | partir/limpiar: rutas en `\texttt` cortas, una columna de "qué prueba" |

Cada tabla movida se **cita inline** donde se afirma lo que prueba.

### G4. Figuras
- **Figura 5.19 (cadena de tests, `f10_b8`): eliminar.** Su contenido ya está en
  `tab:cadena-tests` (tabla legible). Es el caso exacto que la revisión pedía
  "convertir en tabla/esquema de bloques".
- Revisar las figuras horizontales con texto pequeño (`f10_b*`, `explor_*`): o se
  rehacen a ancho de página legible, o pasan al apéndice referenciadas.
- La figura nueva del organismo cuántico (B2) se diseña ya para PDF (vertical/
  cuadrada, 5 paneles, fuente legible, caption corto).

### G5. Aligerar el cuerpo
Tras G3–G4, el capítulo 5 debe tener **jerarquía visual**: por sección, 1 tabla
de veredicto y, como mucho, 1 figura; el detalle, en el apéndice citado. Objetivo
visual: que ninguna página sea un volcado de evidencia.

---

## F. Orden de ejecución (revisado — figura-primero como puerta de de-risking)

**[Condición del revisor: prioridad absoluta a §5.3.0 y a la limpieza visual;
primero la figura; si no funciona, no se expande el texto que depende de ella.]**

0. **GATE — Construir la figura del organismo cuántico** (script Python desde
   `positions_json` + `density__<var>`), renderizar y **juzgar legibilidad**
   (yo + autor) con las reglas estrictas de B2. **Si no funciona, parar aquí** y
   replantear (partir/reducir canales) antes de escribir nada de texto nuevo.
1. **Infraestructura visual** (G1): `booktabs`/`tabularx`/`array`; convertir las
   tablas existentes (sin tocar datos) y verificar compilación.
2. Marco §2.3 (acotado, ver B1).
3. Escribir §5.3.0 (mecanismo, ya con la figura validada) + expandir §5.3.
4. Expandir §5.4 (con §5.2.4 absorbida, 4 coordenadas, tabla-resumen por modelo)
   y §5.5 (proporcional).
5. Degradar/condensar el clásico (§5.1.x, §5.2.1, §5.2.2).
6. **Reubicar tablas/figuras densas al apéndice (G3–G4) con referencias inline**,
   recortar captions (G2), rediseñar la tabla A.1 y **eliminar la Figura 5.19**.
7. Recompilar (tectonic), verificar refs y centro de gravedad, **revisar el PDF
   página a página** (sin tablas al límite ni páginas cargadas), push, reporte.
