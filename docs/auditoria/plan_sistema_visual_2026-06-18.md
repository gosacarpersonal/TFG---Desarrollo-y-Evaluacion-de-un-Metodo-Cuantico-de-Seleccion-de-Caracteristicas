# Plan maestro del sistema visual de la memoria — 2026-06-18

Encargo: reset inteligente de las figuras (revisión externa). No borrar a ciegas:
**poner todas las figuras en cuarentena, leer la memoria como si no existieran, y
reconstruir solo las imprescindibles, desde la pregunta científica y no desde el
artefacto de notebook ya generado.** Coherente con el contrato previo del autor
(figura = instrumento; `rediseno_figuras_memoria_2026-06-16.md`).

Nota: la revisión externa mira una versión **anterior** al último commit. Ya
están hechos: organismo cuántico creado, heatmaps de solape movidos al apéndice,
figura de cadena de tests eliminada (es `tab:cadena-tests`), diagramas TikZ del
marco. Este plan parte del **estado actual real** (inventario abajo).

---

## 1. Principio rector (canon visual)
- **Una figura = una pregunta principal.** Si responde tres, son tres figuras o
  ninguna.
- **≤ 2 paneles** salvo excepción justificada (los *small-multiples* de 5
  formulaciones cuentan como una pregunta si comparten leyenda/escala).
- **Títulos cortos**, sin subtítulo-titular de notebook; **captions de 1–2
  líneas** (la metodología va al texto).
- **Tipografía legible a tamaño PDF**, paleta y escala comunes, sin leyendas
  redundantes; **comparación directa** antes que *dashboard*.
- **Cuerpo = las 5 preguntas del tribunal; todo lo demás al apéndice.**

Las cinco preguntas que el cuerpo debe contestar visualmente:
1. ¿Qué **régimen** tiene cada dataset?
2. ¿Qué muestran las **referencias clásicas** (y cuál es el espejo de QFS)?
3. ¿Cómo **funciona QFS** sobre el banco?
4. ¿Qué **resultado** da frente al baseline y al óptimo exacto?
5. ¿El fallo viene del **criterio o del optimizador**?

---

## 2. Sistema objetivo: 6 figuras de cuerpo (+2 conceptuales del marco)

| # | Figura de cuerpo | Pregunta | Origen | Estado |
|---|---|---|---|---|
| M1 | Evolución adiabática (TikZ) | fundamento | ya hecha | KEEP |
| M2 | Bloqueo de Rydberg (TikZ) | fundamento | ya hecha | KEEP |
| R1 | **Régimen del banco** | (1) | fusiona F01+F02+f10\_a | REDISEÑAR (nueva, 1 sola) |
| R2 | **Perfil/espejo clásico** | (2) | F04 (+idea o1) | REDISEÑAR |
| R3 | **Organismo cuántico** | (3) | qfs\_organismo\_cuantico | KEEP (ya en canon) |
| R4 | **Comparación final** | (4) | F10 | REDISEÑAR (limpiar) |
| R5 | **Atribución criterio–optimizador** | (5) | F09 | REDISEÑAR (nuclear) |
| R6 | **SHAP: variables que sostienen los modelos** | (2/4) | F06 | **CUERPO** (decisión del autor) — revisar legibilidad/canon |

Resultado: de **18 figuras en resultados a 6** (R1–R6). El resto, al apéndice o
fuera.

**Decisiones fijadas por el autor (2026-06-18):**
- **SHAP → cuerpo** (R6 se queda; 6 figuras de cuerpo en Resultados + 2 TikZ del marco).
- **Alcance → rediseño completo con generadores nuevos** para R1, R2, R4, R5
  (R3 ya hecho; R6/SHAP se revisa y se reescribe su generador si su forma actual
  no cumple el canon — requiere la matriz SHAP de `modeling_shap_values_summary`).

---

## 3. Auditoría figura por figura (estado actual → decisión)

**Marco / metodología**
- `fig:adiabatica-esquema` (TikZ) → **KEEP**.
- `fig:rydberg-esquema` (TikZ) → **KEEP**.
- `ev5_evolucion_adiabatica` (perfiles Ω/Δ/detuning) → **MOVER A APÉNDICE** o
  fundir como panel pequeño en M1; hoy es un plot de notebook suelto.

**Resultados — régimen (hay 3 solapadas, deben ser 1):**
- `F01_banco_regimenes` (tamaño/dim/desbalance/FDR) → **MERGE → R1**.
- `F02_senal_fdr_efecto` (FDR + efecto) → **MERGE → R1** (su contenido vive ya en
  `tab:senal`).
- `f10_a_regimenes_dataset` (efecto/VIF/PCA/AUC adv.) → **MERGE → R1** (su
  contenido vive ya en `tab:regimenes`).
- `F03_base_confiable` (AUC adv. + drift + rankings) → **MOVER A APÉNDICE** (es
  auditoría; `tab:particiones` ya da el veredicto).

**Resultados — clásico:**
- `F04_perfil_selectores` → **REDISEÑAR → R2** (espejo de QFS: redundancia vs
  estabilidad vs coste, mRMR destacado).
- `o1_organismo_seleccion` (organismo Madelon) → **CONVERTIR en panel de R2** o
  **MOVER A APÉNDICE** (idea buena, ejecución comprimida).
- `f5_coste_rendimiento` (redundancia vs k) → **MOVER A APÉNDICE**.
- `F07_significancia_magnitud` (deltas pareados) → **MOVER A APÉNDICE**
  (`tab:comparacion` ya da el veredicto en cuerpo).
- `F06_shap_beeswarm` → **R6** si se mantiene en cuerpo; si no, apéndice.

**Resultados — cuántico:**
- `qfs_organismo_cuantico` → **KEEP → R3**.
- `F08_mandos_qfs_alpha_beta` (α y β juntos = dos mecanismos) → **PARTIR**: α al
  apéndice (control), β al apéndice; el cuerpo solo necesita la conclusión, ya en
  `tab:qfs-control`/texto. **MOVER A APÉNDICE**.
- `F09_atribucion_criterio_optimizador` → **REDISEÑAR → R5** (limpio, 2 ejes).
- `F10_comparacion_final` → **REDISEÑAR → R4**.
- `ev6_rendimiento_vs_k` → **MOVER A APÉNDICE**.
- `f10_b4_escalera_alpha` → **MOVER A APÉNDICE**.
- `f10_b5_beta_geometria` → **MOVER A APÉNDICE**.
- `f10_b9_atomos_mds_error` (embebido MDS) → **DELETE** del cuerpo: el organismo
  cuántico (R3) ya muestra posiciones y `tab:embedding` da el error. Si se quiere,
  un panel de error dentro de R3.
- `f10_b10_consistencia` → **MOVER A APÉNDICE**.

**Apéndice (a1–a9, mapa, jaccard):** se quedan como evidencia de defensa,
referenciadas inline. Revisar solo legibilidad, sin rediseño profundo.

---

## 4. Las 5 figuras nuevas/rediseñadas (qué cuentan y de qué datos salen)

- **R1 Régimen del banco** — *small-multiples* por formulación con los ejes que
  predicen a QFS: señal (FDR/efecto), redundancia (VIF/pares), dimensión (PCA),
  balance. Una rejilla limpia, no tres dashboards. Datos:
  `fase1_*`, `fase3_correlaciones_resumen`, `fase4_*` (ya usados en las tablas).
- **R2 Perfil/espejo clásico** — plano redundancia interna × coste, tamaño =
  estabilidad, con `mrmr_approx` y QFS destacados como espejo. Datos:
  `fs_method_profiles`.
- **R3 Organismo cuántico** — hecho (`scripts/fig_organismo_cuantico.py`).
- **R4 Comparación final** — barras por dataset: baseline / mejor clásico /
  QFS-NA / oráculo, con IC. Datos: `comparacion_qfs_configuraciones_vs_baseline`,
  `modeling_test_results_candidates`.
- **R5 Atribución criterio–optimizador** — plano Δcriterio (vertical) × Δoptimizador
  (horizontal), un punto por dataset; Madelon y Churn en cuadrantes opuestos.
  Datos: `tab:atribucion` (ya derivada).

Todas se construyen con generadores matplotlib reproducibles en `scripts/`,
mismo canon (paleta, fuente, tamaño), salida PDF + PNG a `figs/`.

---

## 5. Riesgos y límites
- Las F01–F10 son PDFs de notebook/Codex sin generador local fiable: rediseñar =
  **escribir generadores nuevos** (como se hizo con el organismo cuántico), no
  editar el PDF. Es el grueso del trabajo.
- No tocar los números (todo de CSV verificados).
- Mantener referencias inline; al borrar/mover figuras, revisar todos los `\ref`
  (la compilación detecta rotos).

## 6. Orden de ejecución propuesto
1. **R5 atribución** y **R4 comparación final** (nucleares, datos ya derivados,
   bajo riesgo) — generadores + sustituir F09/F10.
2. **R1 régimen** (fusiona 3 figuras en 1) — el mayor recorte.
3. **R2 perfil/espejo** clásico.
4. Decisión sobre **R6 SHAP** (cuerpo vs apéndice).
5. Mover al apéndice F03, f5, F07, F08, ev6, f10\_b4/b5/b9/b10 con refs inline;
   borrar del cuerpo lo redundante.
6. Recompilar (tectonic), revisar PDF página a página (≤ ~8 figuras de cuerpo,
   sin dashboards), push, reporte.

## 7. Decisiones (estado)
- **R6 SHAP** → cuerpo. *(fijado)*
- **Alcance** → rediseño completo con generadores nuevos. *(fijado)*
- **o1 organismo clásico de Madelon**: pendiente — ¿panel dentro de R2 o apéndice?
  (propuesta por defecto: panel/idea integrada en R2; el PNG suelto, al apéndice).
