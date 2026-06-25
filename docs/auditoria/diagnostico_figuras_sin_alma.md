# Por qué las figuras "no dicen nada" — diagnóstico

> 2026-06-15. El autor: técnicamente correctas, funcionales, pero "no me dicen nada", no
> transmiten "esto explica todo lo que he hecho en el TFG y merece la pena". El problema NO
> es el tipo de gráfico ni la paleta. Es **narrativa**: tenemos una galería de respuestas,
> no una historia.

## La causa raíz: galería de respuestas, no historia

Cada figura responde UNA pregunta bien y por separado. Pero un TFG que **desarrolla y
evalúa un método** a lo largo de 7+ fases necesita que las figuras se sientan como un
**recorrido**, no como un panel de resultados intercambiable con el de cualquier paper.
Seis razones concretas de por qué se sienten huecas:

### 1. No hay espina dorsal: falta la figura del VIAJE
Ninguna figura muestra el recorrido completo: crudo → auditado → particionado → seleccionado
→ modelado → cuántico → veredicto. Lo planeamos (EV4, el embudo dimensional 500→20→k) y
**no se llegó a construir**. Es, probablemente, la causa principal de "no me explican todo
lo que he hecho": no existe la figura que abarca el TFG entero.

### 2. Son resultados sin tensión ni consecuencia
La mayoría describe un inventario ("hay 5 datasets", "estas variables superan FDR") en vez
de plantear una tensión y resolverla. Las dos que SÍ "dicen algo" —F7 (significancia≠magnitud)
y F9 (criterio vs optimizador)— son justo las que tienen un *punchline*. El resto enuncia,
no argumenta.

### 3. No hay un protagonista que se siga entre figuras
Madelon es el protagonista natural (señal escasa → la selección es imprescindible → QFS
falla por criterio → el caso más rico del TFG). Pero su arco está repartido por F2, F5, F7,
F9 y EV6 **sin hilo visual**. El lector nunca "sigue a un personaje". Las historias se
recuerdan cuando sigues a alguien.

### 4. El proceso sigue infrarrepresentado
Hablamos de endpoints→trayectorias, pero solo EV5 y EV6 son trayectorias. La evolución que
identificamos (α, β, madurez de la selección con k, el embudo) **casi no se construyó**
(EV1-EV4 quedaron fuera). La idea de "el proceso pesa tanto como el resultado" apenas
aterrizó en las figuras reales.

### 5. Falta el "y esto qué" ENCIMA de la figura
El skill pide título=hallazgo + una anotación que señale el insight + atenuar el contexto.
Muchas figuras tienen título-hallazgo pero **ningún elemento que destaque**: todo pesa
visualmente lo mismo, así que nada resalta y la lectura se diluye. Una figura que "dice
algo" tiene UN elemento ruidoso y el resto en gris.

### 6. No conectan con el TRABAJO intelectual detrás
El valor del TFG está en el rigor y en las decisiones (la separación olive 3/9, el handoff,
"construimos un oráculo exacto para separar dos fracasos"). Las figuras muestran métricas,
no las decisiones que las hacen valiosas. Solo F9 visualiza una idea metodológica; el resto
podría ser de cualquier benchmark.

## Caveats técnicos que además no se cumplen (el autor los intuye)

- **F1-A:** el tamaño de burbuja codifica desbalance pero **sin leyenda de tamaño** y
  **redundante** con el panel B → encoding de área no informativo; Olive 3/9 se solapan
  (mismos 572×8) con etiquetas montadas.
- **F4-D:** la barra de color no casa con los valores anotados (escala descuadrada).
- **F6:** ahora mezcla beeswarm (binarios) + barras (olive) en una figura → familia mixta
  (honesto, pero el skill lo marca; conviene un rótulo que lo explique).
- **Transversal:** varias figuras son **exploratorias presentadas como explicativas** (si
  solo reproducen una tabla, sobran o deben añadir la dimensión que la tabla no da). Leyendas
  que podrían ser etiquetas directas; contexto que no se atenúa.

## El arreglo NO es "más figuras": es convertir galería en relato

Cuatro movimientos, en orden de impacto:

1. **Construir la espina (el viaje).** El embudo/recorrido del TFG (EV4) como figura de
   apertura de Resultados: una sola imagen donde se vea TODO el pipeline y dónde encaja
   cada fase. Es la que dará la sensación de "esto explica todo lo que hice".
2. **Hilar un protagonista.** Madelon (o el que prefieras) como hilo rojo: mismo color de
   resaltado y una anotación que lo siga figura a figura (señal escasa → selección
   imprescindible → QFS falla por criterio). Que el lector siga un personaje.
3. **Poner el "y esto qué" en cada figura del cuerpo.** Un protagonista ruidoso + UNA
   anotación que diga el hallazgo + el resto en gris. Pasar de "enseñar datos" a "afirmar
   algo".
4. **Aterrizar el proceso.** Construir de verdad las trayectorias que faltan (α, β, madurez
   de la selección con k) donde aporten el "cómo se llegó", no solo el "qué salió".
   Degradar a apéndice (o eliminar) las que solo inventarían una tabla.

## Reencuadre del cuerpo como SECUENCIA (propuesta)

Pensar el cuerpo como actos, no como lista:
- **Apertura — el viaje:** EV4 (embudo del pipeline) → "esto es todo lo que hice".
- **Acto 1 — el reto y la confianza:** F1 (banco) + F2 (señal real) + F3 (base fiable), con
  madelon ya marcado como protagonista.
- **Acto 2 — la selección, caracterizada:** F4 (perfil) + trayectoria de madurez con k.
- **Acto 3 — el método cuántico por dentro:** EV5 (adiabática) + α/β (EV1/EV2).
- **Acto 4 — el veredicto y su porqué:** EV6 + F10 + F9 (criterio vs optimizador), cerrando
  el arco de madelon.

Cada figura hereda del acto anterior y prepara el siguiente (anotación-puente), de modo que
el conjunto se lea como una historia con principio, nudo y desenlace.

## Lo que necesito de ti para ejecutarlo
1. ¿Te resuena el diagnóstico (galería→historia) como la causa de "no me dicen nada"?
2. ¿Protagonista = madelon, u otro hilo (p. ej. "la compacidad" o "redundancia")?
3. ¿Empezamos por la **figura del viaje (EV4)** como prueba de concepto del nuevo enfoque,
   la miramos juntos, y si transmite lo que buscas, propagamos el estilo al resto?
