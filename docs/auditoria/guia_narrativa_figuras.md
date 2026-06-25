# Guía narrativa de figuras — el lenguaje de EV4/EV7 para todo el cuerpo

> 2026-06-15. Destila los principios que hacen que EV4 (apertura) y EV7 (cierre) "digan
> algo", para aplicarlos al resto del cuerpo de forma consistente. No es sobre tipos de
> gráfico: es sobre convertir cada figura en un latido de la historia. Pendiente de que el
> autor valide que EV4/EV7 transmiten "esto explica lo que hice y merece la pena".

## La prueba de los 10 segundos (toda figura del cuerpo debe pasarla)
Tapa el título y pregúntate: (1) ¿hay un protagonista (sé dónde mirar primero)?, (2) ¿cuál
es la frase que me llevo?, (3) ¿dónde encaja en el viaje? Si falla 2 de 3, no es de cuerpo.

## Los cuatro principios (el lenguaje común)
1. **Protagonista único + contexto en gris.** Un solo elemento ruidoso; el resto atenuado
   (`#bdbdbd`/alpha bajo). Nada de "todo pesa igual".
2. **El "y esto qué" sobre la figura.** Una anotación (≤2) que afirma el hallazgo, no que
   describe el eje. Título = conclusión; subtítulo = métrica/n/umbral.
3. **Sitio en el viaje.** Cada figura dice de qué acto es y enlaza con la anterior/siguiente
   (anotación-puente). El lector nunca se pregunta "¿dónde estoy?".
4. **Hilo del protagonista (madelon) entre figuras.** Mismo color de resaltado y un arco que
   se sigue: señal escasa (EV4/F2) → la selección es imprescindible (F5) → QFS falla por
   criterio (EV7/F9). Que el lector siga a un personaje.

## El arco del cuerpo (actos, no lista)
- **Apertura — el viaje:** EV4 (embudo del pipeline). "Esto es todo lo que hice."
- **Acto 1 — reto y confianza:** F1 (banco) · F2 (señal real, madelon 13/500) · F3 (base
  fiable). Madelon ya marcado.
- **Acto 2 — la selección caracterizada:** F4 (perfil) · madurez de la selección con k.
- **Acto 3 — el método cuántico por dentro:** EV5 (adiabática) · α/β (EV1/EV2).
- **Acto 4 — el veredicto y su porqué:** EV6 (rendimiento vs k) · EV7 (cierre: criterio vs
  optimizador, madelon/churn). Cierra el arco de madelon.

## Cómo se reescribe cada figura existente (receta de propagación)
Por figura del cuerpo: (a) elegir protagonista; (b) atenuar el resto a gris; (c) escribir la
frase-hallazgo como título y UNA anotación que la señale; (d) añadir el puente narrativo
con la figura vecina; (e) revisar caveats (leyenda directa, sin encodings redundantes,
escalas etiquetadas, IC visibles). Las que tras esto solo repitan una tabla → apéndice.

Mapa rápido protagonista/hallazgo por figura:
- F1 → protagonista: la heterogeneidad; hallazgo: "el desbalance obliga a macro-F1". (O
  fundir en EV4.)
- F2 → madelon (13/500); hallazgo: "la señal de madelon casi no es univariante" (puente a
  EV7).
- F3 → la coherencia; hallazgo: "la base no sesga la comparación".
- F4 → mRMR; hallazgo: "controla redundancia con coste moderado".
- F5 → madelon; hallazgo: "reducir es necesario, no opcional" (puente desde EV4).
- F6 → la variable top de cada modelo; hallazgo: "lo que sostiene el modelo coincide con la
  selección".
- F7 → madelon vs churn; hallazgo: "significancia no es magnitud".
- EV5 → el protocolo; hallazgo: "así explora y sesga QFS".
- EV6 → QFS sobre contexto clásico; hallazgo: "QFS es competitivo en k pequeño".
- EV7 → madelon/churn; hallazgo: "donde falla, sabemos por qué".

## Caveats a respetar al propagar (los que hoy no se cumplen)
- Sin encodings redundantes ni área sin leyenda (F1 burbuja).
- Barra de color que case con los valores (F4-D).
- Familia mixta solo si se rotula (F6 beeswarm+barras).
- Etiquetas directas sin colisión (protagonista a un lado, contexto al otro: ver EV4/EV7).
- Exploratorio→apéndice si solo replica una tabla.

## Estado
Construidos y verificados como prueba de concepto: **EV4** (apertura) y **EV7** (cierre).
Pendiente: validación del autor de que transmiten lo buscado; si sí, propagar esta guía al
resto del cuerpo figura a figura. Relacionado: `diagnostico_figuras_sin_alma.md`,
`banco_preguntas_memoria.md`, `especificacion_figuras_memoria.md`.
