# Roadmap: del análisis al cierre de la memoria con el análisis "perfecto" de QFS

> 2026-06-15. Camino desde el estado actual hasta una memoria terminada que caracterice POR QUÉ
> funciona o no QFS respecto a **dataset · métodos · k · α · β · modelos · métricas · tests · todo en
> conjunto**. Para cada etapa: *qué crear, qué ejecutar (y qué NO), qué va a la memoria (y qué NO), y la
> puerta de decisión del autor*. Complementa: `plan_notebook_visualizaciones.md` (el guion de figuras),
> `sintesis_hallazgos_vs_qfs.md` (los hallazgos), `plan_figuras_narrativo.md` (la espina del cuerpo).

## Principios rectores (las reglas que ya hemos aprendido)
1. **Proceso, no podio.** Analizar el experimento (regímenes, mandos, tests), no el mejor resultado.
2. **Analizar antes de narrar.** Calcular → mirar → figura → solo entonces texto de memoria.
3. **Plasmar siempre.** Nada vive solo en la cabeza ni en el chat; va a un notebook o a la memoria.
4. **Hipótesis = hipótesis** hasta probarla (p. ej. one-hot/Churn). No sobreafirmar.
5. **No todo va a la memoria.** El análisis completo de 9 dimensiones vive en el notebook; la memoria
   recibe la espina + el clímax + apoyos. Curar es parte del trabajo.
6. **Ejecutar lo mínimo necesario.** Re-render de figuras y el notebook (leen artefactos existentes) sí;
   re-ejecutar TODO el pipeline NO, salvo el cierre de reproducibilidad final.
7. **Puntos de reevaluación.** Cada etapa de análisis puede destapar algo; hay gates explícitos para parar
   y replanear en vez de seguir en piloto automático.
8. **Espina conceptual:** régimen (fases 1–4) → mecanismo (criterio-relevancia / criterio-redundancia /
   optimizador-embebido) → resultado (fases 8–9). Toda figura y todo párrafo cuelga de ahí.

---

## ETAPA 0 — Estabilizar la base (antes de construir nada más)
- **Crear:** nada. **Ejecutar:** nada de análisis.
- **Acción:** decidir el trabajo no commiteado de Codex (commit como checkpoint limpio vs revisar/revertir)
  y la herramienta de viz (matplotlib+viz_core vs plotnine). Commitear lo coherente da una base estable y
  reversible y cierra la ansiedad de "no sé qué tocó Codex".
- **Memoria:** no toca todavía.
- **GATE 0 (autor):** ¿commiteo el baseline?  ¿matplotlib o plotnine?  → sin esto, todo lo demás se
  construye sobre arena.

## ETAPA 1 — Cerrar las hipótesis abiertas (verificar antes de narrar)
La única incógnita científica viva es el fallo de Churn (¿geometría/encoding o baja redundancia intrínseca?).
- **1a — Recompute de átomos (D9), BARATO:** recomputar el embebido MDS desde las `R_ij` existentes y medir
  **error de embebido** Churn vs Olive/BCW/Madelon. *Ejecutar:* sí, pero solo el MDS (no QFS). *Crear:* la
  figura de átomos por dataset (era B9 del blueprint). Confirma o refuta la "frustración geométrica".
- **1b — Ablación TARGETED de Churn (opcional, solo si 1a no zanja):** fases 8–9 solo de Churn con variante
  label-encoding y/o one-hot `drop_first`. *Ejecutar:* sí, acotado a Churn. Resuelve la causa raíz.
- **Lo que NO se hace:** re-ejecutar el bloque clásico ni los otros 4 datasets.
- **Memoria:** el resultado entra como *explicación del fallo de optimizador en Churn* + limitación/future-work
  (sensibilidad de QFS al preprocesado en baja redundancia).
- **GATE 1 (autor):** tras 1a, ¿basta para narrar la hipótesis como "candidata verificada en geometría", o
  quieres la certeza de 1b?

## ETAPA 2 — Construir la capa analítica = notebook `fase10_visualizaciones.ipynb`
El grueso de "qué crear". Instrumento a instrumento, **anclado en el régimen**, siguiendo el blueprint.
- **Crear:** el notebook + sus figuras: A regímenes (con VIF/PCA), B2 espacio-métodos (coords + Jaccard de
  los 12), B3 trayectoria-k, B4 escalera-α (Mücke), B5 β+geometría, B9 átomos (de la Etapa 1a), B6 modelos,
  B7 métricas, B8 cadena-tests, C síntesis (beeswarm por dataset + plano de atribución).
- **Ejecutar:** sí, pero todo **lee artefactos de `results/`** ya existentes (salvo el MDS de 1a). No
  regenera resultados.
- **Reusar:** `explor_mapa_metodos.py`, `build_diagnostico_atribucion.py`, `build_f6_shap_beeswarm.py`.
- **Memoria:** todavía no; primero ver qué dice cada instrumento (analizar-antes-de-narrar).
- **GATE 2 (autor):** revisar cada instrumento a medida que sale; ¿alguno destapa algo que cambie la
  narrativa? (checkpoint de reevaluación, principio 7).

## ETAPA 3 — Curar: qué entra en la memoria y qué se queda en el notebook
- **Crear:** una tabla de reparto (cuerpo / apéndice / solo-notebook) por figura, aplicando la prueba de los
  10s y "¿responde una pregunta de defensa?".
- **Ejecutar:** nada.
- **Memoria (criterio):** *cuerpo* = espina (regímenes, espacio-métodos, k, α, átomos, atribución, beeswarm);
  *apéndice* = β, modelos, métricas, detalle de tests, handoff; *solo-notebook* = exploratorios y trazas.
  **No todo va a la memoria.**
- **GATE 3 (autor):** validar el reparto antes de tocar el LaTeX.

## ETAPA 4 — Reescribir la memoria (proceso, no podio)
- **Crear/editar:** integrar la **teoría régimen→mecanismo→resultado**. Cambios por capítulo:
  - *Métodos:* declarar el espejo de 12 como sistema de coordenadas relevancia/redundancia; VIF/PCA como
    ejes de caracterización.
  - *Resultados:* poner la huella de regímenes ANTES del veredicto; leer cada dimensión como lectura del
    régimen; clímax = atribución; el espacio-métodos con los 12 (no solo mRMR).
  - *Discusión/Conclusiones:* regimen-como-predictor; descomposición relevancia/redundancia; one-hot como
    causa candidata del fallo de Churn (limitación honesta + future-work).
  - *Introducción:* anunciar la tesis (resultado nulo/deteriorado rigurosamente atribuido) desde el inicio.
- **Ejecutar:** nada (solo escribir LaTeX y referenciar figuras ya generadas).
- **Memoria:** esta ES la etapa de memoria.
- **GATE 4 (autor):** revisar redacción contra la guía de estilo (`docs/estilo_redaccion_tfg.md`).

## ETAPA 5 — Verificar y cerrar (reproducibilidad)
- **Ejecutar:** AQUÍ sí, todo de principio a fin — los 9 notebooks + el fase10 desde núcleo limpio, para
  garantizar reproducibilidad; verificar cada cifra citada contra su artefacto; compilar LaTeX; pase final
  de consistencia (números, captions, referencias).
- **Crear:** nada nuevo; checklist de verificación.
- **Memoria:** congelar. Commit final.
- **GATE 5 (autor):** visto bueno final.

---

## Mapa: dónde se resuelve cada una de las 9 dimensiones
| Dimensión | Instrumento / dónde | Lente | ¿Memoria? |
|---|---|---|---|
| Dataset | Etapa 2-A regímenes (VIF/PCA/efecto) | L1 | Cuerpo (antes del veredicto) |
| Métodos de selección | 2-B2 (coords + Jaccard 12), leído vía VIF | L2 | Cuerpo |
| k | 2-B3 (trayectoria; dim-intrínseca vs dim-señal) | L3 | Cuerpo |
| α | 2-B4 (escalera Mücke, óptimo exacto) | L1 | Cuerpo (compacta) |
| β | 2-B5 + 1a átomos (geometría, dist_ratio) | L1 | Cuerpo (átomos) / apéndice (β-map) |
| Modelos | 2-B6 (delta selección×modelo; Madelon XGB) | L3 | Apéndice (+ nota en cuerpo) |
| Métricas | 2-B7 (macro-F1 vs AUC; desbalance Olive9) | L4 | Apéndice |
| Tests estadísticos | 2-B8 (cadena de confusores) | L1 | Cuerpo (compacto) / apéndice |
| Todo en conjunto | 2-C + Etapa 4 (régimen→mecanismo→resultado) | L1–L4 | Cuerpo (clímax + discusión) |

## Decisiones que dependen de ti (gates)
- **G0:** commit del baseline de Codex (sí/revisar) · herramienta viz (matplotlib/plotnine).
- **G1:** tras el recompute de átomos, ¿hace falta la ablación de Churn (1b) o basta con 1a?
- **G2:** revisión instrumento-a-instrumento del notebook (checkpoint de hallazgos emergentes).
- **G3:** reparto cuerpo/apéndice/notebook.
- **G4:** redacción final.

## Riesgos / lo que puede cambiar el plan
- Que el recompute de átomos (1a) refute la hipótesis del embebido → entonces el fallo de Churn se narra solo
  como "baja redundancia intrínseca + relajación de geometría", sin la historia one-hot.
- Que un instrumento de la Etapa 2 destape un hallazgo nuevo (probable, principio 7) → re-curar y posiblemente
  re-narrar; por eso Etapa 3–4 van DESPUÉS de ver todos los instrumentos.
- Alcance: la memoria no debe convertirse en un atlas de 30 figuras; el filtro es "pregunta de defensa".
