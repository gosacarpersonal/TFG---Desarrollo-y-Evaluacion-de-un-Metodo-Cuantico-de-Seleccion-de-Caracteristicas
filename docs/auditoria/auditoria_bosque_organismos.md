# Auditoría del bosque: de galería de gráficos a ORGANISMOS

> 2026-06-15. Reencuadre tras la referencia del autor (WaPo, *Job Gains and Losses*). El
> objetivo real no es "10 figuras correctas", sino **pocas piezas-organismo**: imágenes
> densísimas que contienen TODO el trabajo de una dimensión a la vez y se leen de un
> vistazo. Forest first; luego afinamos a las hojas. Sin rigidez con el número.

## Qué hace "perfecta" a la figura de referencia (las cualidades a replicar)
1. **Densidad sin ruido:** cientos/miles de celdas, una por dato; nada saturado. La unidad
   es la CELDA, no el punto. (Small-multiple llevado al extremo.)
2. **El proceso es el eje:** X = tiempo/orden; la historia está en la FORMA del conjunto
   (bloque rojo de la recesión → marea verde de la recuperación). El "cómo se llegó".
3. **Doble lectura gestalt + detalle:** de lejos, el patrón; de cerca, cada celda es un
   dato concreto con su valor. Sirve al que ojea y al que escudriña.
4. **Color = magnitud con significado** (divergente, consistente) → crea el "cuadro".
5. **Narrativa encima del dato:** banda de contexto (recesión), una anotación de foco,
   título-tema. Contexto y foco conviven sin pelearse.

→ "Explica todo lo que hice y merece la pena" = **ver mucho trabajo, vivo y legible, en una
sola pieza.** Mis figuras fallaban por lo contrario: pocas, planas, de un solo mensaje.

## El bosque del TFG como 4-5 ORGANISMOS (no 21 gráficos)

Cada organismo absorbe una dimensión entera del trabajo; alrededor, pocas "hojas" de foco.

- **O1 — El organismo de la SELECCIÓN** (la joya; dato `fs_all_rankings`, 116k filas).
  Rejilla por dataset: filas = 12 selectores (agrupados por familia), columnas = variables
  (ordenadas por consenso), celda = frecuencia/rango de selección a lo largo de k y
  semillas. De lejos: qué variables son consenso (columnas oscuras), qué familias se
  parecen, los 480 distractores de Madelon como un páramo claro. De cerca: cada celda es
  "este método elige esta variable a este k". TODO el roster en una imagen viva.

- **O2 — El organismo de la AUDITORÍA / cadena de evidencia** (`fase1_asociacion` 550 +
  `fase4_drift_variables` 1112 + leakage). Rejilla: filas = variables, columnas = controles
  (efecto, FDR, normalidad, drift KS/W/PSI por split, leakage AUC/NMI, conservación),
  celda = estado/valor. Una imagen = TODO el rigor, variable a variable. El "health check"
  del dato a lo largo del pipeline.

- **O3 — El organismo del MODELADO** (`modeling_validation_results` + cost_performance).
  Rejilla: filas = (selector × modelo), columnas = k, celda = macro-F1 (o Δ vs baseline),
  small multiples por dataset. Se ve el espacio entero de modelado y dónde aparece la
  mejora (el verde) frente al baseline.

- **O4 — El organismo CUÁNTICO** (`qfs_runs_*` densidades + `qfs_oracle`). Rejilla: filas =
  variables, columnas = β (y/o α), celda = densidad de Rydberg. Ya medio existe (β-map);
  elevarlo a los 5 datasets y cruzarlo con el óptimo exacto. La "película" de cómo QFS
  reordena el espacio al barrer sus mandos.

- **O5 — El organismo SHAP / interpretabilidad** (`modeling_shap_values_full`). Por
  candidato: instancias × variables, celda = valor SHAP (el beeswarm es una proyección de
  esto; la rejilla por clase en olive es otra). Qué sostiene cada modelo, sin colapsar.

Y un puñado de **HOJAS** de foco (las que ya "decían algo": F7 significancia, F9/EV7
criterio-vs-optimizador, EV4 recorrido como portada). No 21 piezas: ~5 organismos + ~4-6
hojas.

## Principios de construcción (heredados de la referencia)
- Unidad = celda; densidad alta deliberada; orden con significado (clustering/consenso).
- Color divergente semántico y CONSISTENTE entre todos los organismos.
- Doble escala de lectura: legible la silueta a tamaño página, y el detalle al ampliar.
- Una banda de contexto + una anotación de foco por organismo (no más).
- El proceso/orden en un eje siempre que exista (k, β, α, fases, instancias).

## Plan
1. **Bosque (ahora):** validar el reencuadre a organismos y construir **O1** (el de la
   selección) como prueba de que nuestros datos dan una pieza tipo-WaPo viva.
2. **Hojas (después):** afinar O1 (orden de columnas, color, anotación), luego O2-O5, y
   conservar las pocas hojas de foco. El número final sale de la historia, no de una cuota.

## Decisión para el autor
¿Vamos con O1 (organismo de la selección) como primera pieza-prueba del nuevo lenguaje, la
miramos, y si transmite el "joder, cuánto hay aquí y qué bien se ve", propagamos el patrón
a O2-O5?
