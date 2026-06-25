# Rediseño del sistema visual de la memoria — contrato

> 2026-06-16. Tras auditar las 15 figuras `F01–F15` como si fueran figuras de un
> PDF de memoria (no como salidas de notebook con zoom). Veredicto: **no son
> mejorables con retoques; hay que rediseñar desde la pregunta científica y desde
> el formato final.** El defecto raíz no es estético: **son volcados de tablas, no
> instrumentos de razonamiento.** Una figura del TFG debe encadenar
> evidencia → mecanismo → conclusión y leerse a ancho de página.

## 0. La cadena que las figuras deben hacer visible

```
régimen del dato
  → validez experimental
  → comportamiento clásico (12 selectores, referencia)
  → transformación QFS:  I_i / R_ij  →  geometría (MDS)  →  readout (átomos)
  → top-k seleccionado
  → modelo
  → SHAP (qué usa el modelo)
  → diagnóstico criterio / optimizador / geometría
  → veredicto por dataset
```

Cada figura principal debe ser **un eslabón** (o una transición entre eslabones),
no un collage de subplots bajo un título común.

## 1. Contrato de formato (PDF, no notebook)

- **Anchos reales:** `\textwidth` ≈ 16 cm (figura ancha) o `0.48\textwidth` (media).
  Nada de figuras 23×5 in: a ancho de página los ticks quedan microscópicos.
- **Aspecto sano:** preferir 4:3, 3:2, cuadrado o **vertical** para figuras densas.
  Prohibido el "panel-strip" 1×5 con texto en el eje.
- **Máx 3 paneles en una fila.** Más de 3 → rejilla 2×3 / 3×2 / vertical, o
  seleccionar casos críticos en vez de pintar los 5 datasets.
- **Fuente legible al tamaño final:** ticks/labels ≥ ~7–8 pt *a tamaño de imprenta*
  (⇒ dimensionar la figura en pulgadas y `fontsize` en consecuencia, no al revés).
- **Cada figura es legible sin zoom** o se rediseña/parte.

## 2. Gramática visual fija (una sola, para todo el documento)

- **Color = dataset** SOLO cuando el dataset es la unidad principal de la figura.
  Paleta fija (Okabe-Ito): BCW azul, Churn naranja, Madelon morado, Olive3 verde
  claro, Olive9 verde oscuro.
- **Enfoque (baseline / mejor clásico / QFS-NA / QFS-oráculo) = forma + posición
  fija**, idéntica en toda la memoria (p.ej. ○ baseline, ■ clásico, ▲ QFS-NA,
  ◆ oráculo). Nunca recodificar.
- **Incertidumbre/significancia = opacidad, contorno o barra de error**, no color.
- **Gris = contexto** (lo que no es el mensaje).
- **Color saturado fuerte = SOLO el mecanismo que esa figura explica.** Una figura,
  un acento.
- **Anotación interpretativa obligatoria:** cada panel lleva el "so what" escrito
  en la propia figura (1 frase dirigida a la conclusión), no solo ejes.
- Mínimo grid, sin bordes negros por defecto, títulos cortos, aire útil.

## 3. Auditoría figura a figura

| Fig | Veredicto | Motivo (PDF + razonamiento) | Destino |
|---|---|---|---|
| F01 embudo | **Redicseñar** | el área de "nº de tablas/fase" no es ciencia (debug). Salvar solo el *funnel* de reducción de variables (p→clásico→QFS) como mensaje de compresión | principal (compacta) |
| F02 regímenes | **Rediseñar** | 3 paneles sueltos. Colapsar a UN mapa de dificultad (señal × dimensionalidad) anotado con qué tensiona cada dataset | principal; coord. paralelas → apéndice |
| F03 validez | **Rediseñar/degradar** | demasiado. Principal = una "puerta de confianza" compacta (adversarial≈0.5 + permutación obs≫nulo). El resto a apéndice | principal mínima + apéndice |
| F04 selectores | **Rediseñar** | 3 paneles. Principal = un mapa del espacio de selectores con la envolvente de referencia | principal; resto apéndice |
| F05 trayectorias k | **Rediseñar** | 1×5 ultra-ancho, ilegible en PDF. Rejilla vertical/casos críticos; un mensaje (redundancia sube / rendimiento satura) | principal (rediseño) + apéndice |
| F06 marcador final | **Mantener** | dumbbell = instrumento real. Aplicar gramática + anotar significancia | principal |
| F07 tablero QFS | **Rediseñar** | 4 gráficos independientes pegados. Falta la flecha α→β→optimizador→MDS. Convertir en secuencia guiada o repartir | principal (secuencia) |
| F08 SHAP/I_i/solape | **Rediseñar** | barras sueltas; no conecta variable a variable. → **matriz variable × evidencia** (SHAP, I_i, QFS-NA, oráculo, clásicos, veredicto) hecha visual, con codificación acierto/fallo/ausencia-crítica | principal |
| F09 plano diagnóstico | **Mantener** | es la figura-tesis. Pulir gramática y anotación | principal |
| F10 beeswarm | **Mantener→apéndice** | bien como granularidad; principal solo protagonista, más grande | apéndice |
| F11 matrices MI | **Mantener→apéndice** | buena estructura; principal = integrarla en la figura de transformación QFS | apéndice + integrada |
| F12 escalera α | **Mantener→apéndice/integrar** | fold en la cadena de mecanismo QFS | apéndice/integrada |
| F13 paisaje optimizador | **Rediseñar a fondo** | la más importante y la más pobre: solo densidad media + histograma. Debe **abrir la caja negra del readout** (ver §5) | principal (clave) |
| F14 geometría MDS | **Mantener→integrar** | integrar en la cadena Ii/Rij→geometría→readout | apéndice/integrada |
| F15 panorama 260 exp | **Degradar** | nube microscópica no va en principal. Rediseñar como densidad/resumen por modelo×dataset | notebook/apéndice |

## 4. Arquitectura nueva por niveles

**Principal (memoria, ~7–8 figuras, cada una un eslabón):**
1. **Mapa de dificultad del banco** (señal × dimensionalidad, anotado). [de F02]
2. **Puerta de confianza** (validez en 1 vista compacta). [de F03]
3. **Referencia clásica** (espacio de selectores + envolvente de rendimiento alcanzable). [F04+F05]
4. **Transformación QFS** — cadena para el dataset protagonista: I_i/R_ij → MDS → readout → selección. [integra F11/F12/F14]
5. **Apertura del readout cuántico** (la caja negra; ver §5). [rediseño de F13]
6. **Matriz variable × evidencia** (SHAP/I_i/QFS/clásicos → acierto/fallo). [de F08]
7. **Plano criterio–optimizador**. [F09]
8. **Veredicto por dataset** (síntesis visual, slopegraph anotado). [de F06/F09]

**Apéndice (granularidad por dataset):** beeswarm 5×, matrices MI 5×, escalera α
5×, geometría MDS 5×, trayectorias k completas.

**Notebook (auditoría exhaustiva):** panorama de experimentos, controles completos,
todos los β, todos los α. **Con ejecución estricta** (§6).

## 5. Figura clave — apertura del readout QFS (deja de ser caja negra)

Una figura con **una sola pregunta**: *¿qué hace realmente el readout analógico y
sigue la relevancia del problema?* Orden lógico de paneles (dataset protagonista,
resto a apéndice). Fuentes: `qfs_runs_*`, `qfs_oracle_*`, `qfs_quality_control_*`,
`fs_qfs_mi_target_vector_long`, SHAP.

1. **Bitstrings dominantes** (frecuencia de las soluciones top) — qué subconjuntos
   emergen.
2. **Distribución de cardinalidades activadas** — ¿respeta el presupuesto k?
3. **Energía/coste frente al óptimo del oráculo** — brecha del optimizador.
4. **Concentración/entropía del readout** — ¿colapsa a una solución o se dispersa?
5. **Coactivación entre átomos** (matriz) — qué variables se encienden juntas.
6. **Estabilidad del top-k frente a β** — robustez del readout.
7. **Densidad de Rydberg vs I_i vs SHAP vs selección clásica** (scatter) — ¿el átomo
   excitado coincide con lo relevante/lo que usa el modelo/lo que eligen los clásicos?

El panel 7 es el que cierra el argumento: conecta el mecanismo cuántico con
relevancia, modelo y referencia clásica.

## 6. Integridad de ingeniería (obligatorio)

- **Fuera los `try/except` amplios + `traceback.print_exc()`** que dejan el notebook
  "ejecutado" con figuras ausentes.
- **Celda-guardia al inicio:** `assert` de que existen `results/tables/` y los CSV
  clave; si faltan, **fallar ruidosamente** (no continuar).
- Modo estricto: un fallo de figura **detiene** la ejecución. "Ejecutado" debe
  significar "todas las figuras construidas con datos reales".
- Verificación post-ejecución: nº de figuras esperadas == nº de PNG escritas, y
  todas con `mtime` de esta ejecución.

## 7. Qué NO repetir

- "Hay 5 datasets ⇒ 5 paneles" sin preguntar si son legibles/comparables/necesarios.
- Tratar QFS-NA como caja negra.
- Meterlo todo "porque el dato existe": separar principal / apéndice / notebook.
- Confundir "muchos datos" con "una lectura".
