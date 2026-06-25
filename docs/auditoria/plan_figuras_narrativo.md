# Programa de figuras dirigido por la tesis (espina narrativa)

> 2026-06-15. Consolida `banco_preguntas_memoria.md` (las 26 preguntas) + `guia_narrativa_figuras.md`
> (el lenguaje EV4/EV7) + la revisión crítica integral. **Diferencia clave frente al banco:** el
> banco ordena por *tapar huecos de cobertura*; este programa ordena por una **espina narrativa**
> que declara la tesis real y blinda los flancos de defensa. Una figura solo entra si es un latido
> de esa historia. Lenguaje obligatorio: organismo denso, protagonista único + contexto gris,
> anotación "y esto qué", sitio en el viaje (ver `guia_narrativa_figuras.md`).

## La tesis que las figuras deben sostener (lo que la revisión sacó)

El titular cuántico NO es una victoria; es un **resultado nulo/deteriorado rigurosamente
atribuido**. La aportación es el **diagnóstico criterio↔optimizador** habilitado por la referencia
clásica y el óptimo exacto. Las figuras deben:
1. **Declarar esa tesis desde el principio** (no dejar que el deterioro sorprenda al lector).
2. **Hacer visible la profundidad** computada (170 selecciones, 260 modelados, SHAP por instancia,
   densidades Rydberg, barridos β/α) — hoy comprimida en ~18 figuras, varias de solo-media.
3. **Blindar los dos flancos de defensa:** es *simulación* clásica (no hardware) y la *geometría se
   relajó* (1/√2→0.45/0.35/0.25), causa sospechada del fallo del optimizador en Churn.

Protagonista que cose el arco: **Madelon** (señal escasa → selección imprescindible → QFS falla por
*criterio*) y **Churn** como contrapunto (QFS falla por *optimizador*). Mismo color en todas.

## El arco (4 actos) — qué responde cada figura

**Apertura — "esto es todo lo que hice y por qué importa".**
- EV4 recorrido del TFG (embudo del pipeline). ✓ insertado en metodología con
  tesis explícita: las fases 1--7 construyen la referencia y las fases 8--9
  diagnostican QFS.

**Acto 1 — el reto y la confianza (la base no sesga).**
- F1 banco: heterogeneidad → obliga a macro-F1. ✓ (ya narrativa).
- **F2 señal real**: Madelon 13/500, efecto 0.02 → *planta el hilo*: "su señal apenas es
  univariante" (puente directo a la tesis). ✓ (ya narrativa; mantener).
- F3 base fiable: AUC adversarial ~0.5, drift bajo, rankings MI conservados. ✓ (mostrar banda 0.5).

**Acto 2 — la selección caracterizada (profundidad clásica).**
- **O1 organismo de selección** (12 métodos × variables, frecuencia): consenso vs páramo de
  distractores. ✓ insertado en cuerpo como puente entre perfil clásico y fallo posterior
  del criterio QFS en Madelon.
- F4 perfil de selectores (coste×redundancia, familia, estabilidad): mRMR controla redundancia. ✓
- F5 redundancia vs k: reducir es necesario, no opcional (Madelon). ✓
- **F6 → beeswarm SHAP por instancia** (REEMPLAZO): lo que sostiene el modelo coincide con lo que
  la selección retuvo, con dispersión y dirección. ★ **construido (demostrador BCW)**; falta
  propagar a Madelon (donde el criterio falla) y desglose por clase en Olive.

**Acto 3 — el método cuántico por dentro (no solo el resultado).**
- EV5 protocolo adiabático: así explora y sesga QFS. ✓ *Añadir rótulo "simulación analógica".*
- F8 α/β: α recorre la cardinalidad del óptimo exacto (Mücke), β modula densidad Rydberg. ✓
- **A6/handoff I_i,R_ij**: QFS consume las mismas cantidades que los clásicos (trazabilidad). ✓ apéndice.

**Acto 4 — el veredicto y SU PORQUÉ (la tesis, clímax).**
- **F9 atribución QFS** (macro-F1 descompuesta): Madelon pierde por criterio
  (`baseline - oráculo`), Churn por optimizador simulado (`oráculo - QFS-NA`). ✓ — *la
  figura central; coste/Hamming queda como tabla de control y la figura cuenta el porqué
  predictivo.*
- F10 / EV6 QFS vs clásico por k e IC: dónde iguala, dónde se deteriora. ✓
- EV7 cierre narrativo (scorecard): cierra el arco Madelon/Churn. ✓

## Acción por figura (reconciliación con el set actual)

| Figura | Estado | Acción |
|---|---|---|
| F1, F2, F3, F4, O1, F5, F8, F10, EV5, EV6, EV7 | existen, narrativas | **keep/restyle** (aplicar receta guía; rótulos de caveat) |
| EV4 | generador corregido e insertado | **keep** como mapa de lectura de las nueve fases |
| F9 atribución QFS | insertada | **keep como clímax** (`diag_atribucion_qfs`; no volver a la F9 Δcoste/Hamming salvo como apoyo) |
| **F6** | solo media \|SHAP\|, 2/5 datasets | **replace → beeswarm** (hecho BCW; faltan Madelon + Olive por clase) |
| F3 panel olive vacío, F6 viejo | flojos | retirar forma vieja al validar el reemplazo |
| A1–A9 | apéndice | keep; A4 SHAP trivial → derivar del beeswarm |
| EV8 scorecard | duplica EV7 | evaluar fusión o descartar |

## Orden de construcción (mayor retorno primero)
1. **F6 beeswarm** (gravísimo hueco de profundidad) — BCW ✓ · Madelon · Olive por clase. ← en curso
2. **F9** mantener la atribución en macro-F1 como clímax; reforzar caveat de simulación/geometría en texto cercano.
3. **O1** confirmado en cuerpo (profundidad de la selección de un vistazo).
4. Rótulos de "simulación analógica" en EV5/F8/F10 (flanco hardware).
5. Apertura EV4: media frase de tesis. ✓ insertado
6. Apéndice: A6 handoff, A2 leakage, A8 solape QFS↔clásicos.

## Demostrador construido este turno
- `scripts/build_f6_shap_beeswarm.py` → `f6_shap_beeswarm_bcw.png` (85 instancias, top 12/22,
  color = valor de variable). Prueba de que el lenguaje organismo + "profundidad visible" se
  propaga al cuerpo. Pendiente validación del autor antes de propagar a los demás datasets/figuras.
