# Plan de limpieza del directorio del TFG

**Fecha de auditoría:** 2026-06-16
**Estado:** PLAN — nada ejecutado. Auditoría solo-lectura verificada de forma independiente.
**Alcance:** todo el directorio, con foco en el output generado por los notebooks de fases 1–9.

> Regla de oro de este plan: **la verdad de "qué es canónico" la dicta lo que el código/LaTeX consume de verdad**, no las fechas ni los nombres. Cada ítem marcado lleva su estado de verificación. Donde pone "NO TOCAR" es porque hay una referencia viva comprobada.

---

## 0. Fotografía del directorio

- Tamaño total: **4,6 G** · ~8.800 rutas (sin `.git`).
- Pesos: `data/` 2,5 G · `.git/` 874 M · `results/` 715 M · `.agents/` 473 M · `docs/` 61 M · `notebooks/` 27 M.
- Git: 126 modificados, 108 sin trackear, 7.030 ficheros trackeados (de ellos **3.690 = 52 % en `.agents/`**).

### Anclas de ejecución canónica (mtime de los notebooks)
- Fases 1–7: **2026-06-14**
- Fases 8–9: **2026-06-15**
- Figuras de memoria (`superfiguras_memoria.ipynb`): **2026-06-16**

Cualquier output anterior a la fecha de su fase es candidato a resto de un run previo.

---

## 1. Conjunto canónico — INTOCABLE ("sí o sí")

Esto es lo que la memoria y el pipeline consumen de verdad. No entra en ninguna fase de borrado.

| Capa | Ruta | Por qué |
|---|---|---|
| Datos fuente | `data/01_raw/` | Origen, no regenerable. |
| Datos procesados | `data/processed/` (06-14) | Run canónico. |
| Splits | `data/splits/` (06-14) | Run canónico. |
| Selección | `data/selected_features/` (06-14, 1.260f) | Run único y limpio de fase 5. |
| Tablas | `results/tables/01_…06_` (06-14), `08_quantum/` (06-15) | Run canónico. |
| Figuras memoria | las **36** de `\includegraphics` en `Plantilla_Latex_GCD/tfgs/figs/` | Lo que compila el PDF. |
| Código | `src/`, `scripts/`, `QFS_based_on_NA/` | Fuente. |
| Notebooks | `notebooks/fase1-9.ipynb`, `notebooks/superfiguras_memoria.ipynb` | Fuente reproducible. |
| Memoria | `Plantilla_Latex_GCD/` (`.tex` + 36 figs + logos) | Entregable. |

**Trampas verificadas — NO TOCAR aunque "parezcan" duplicados/viejos:**
- `data/selected_features/**/X_val_selected.csv` — **alias intencionado** de `X_validation_selected.csv`. `src/fase5_feature_selection.py:758-759` escribe ambos; `src/fase5_notebook_readings.py:462` **verifica que exista**. Deduplicar rompe la verificación de fase 5. (≈311 M de "duplicación" que NO es eliminable sin tocar código.)
- `results/tables/07_final_comparison/fase7_comparacion_final.csv` (pre-QFS, 06-14) — lo **lee `fase9.ipynb:2559`** como baseline clásico. Input vivo, no superado.

---

## 2. Hallazgos verificados (output de fases 1–9)

| # | Artefacto | Fecha | Peso | Referencias en código | Veredicto |
|---|---|---|---|---|---|
| H1 | `results/logs/05_feature_selection/previous_tables_20260613_112241/` | 06-12/13 | 46 M / 420f | `verify_fase5_notebook.py` (baseline regresión, opcional) | Archivar |
| H2 | `results/reports/05_feature_selection/` + `…/06_modeling/` | **06-12** | ~340 K / 18f | Memoria NO los cita; narrativa **pre-XGBoost** | Regenerar o archivar |
| H3 | `results/tables/07_final_comparison/fase7_validacion_completitud.csv` · `fase7_inventario_artefactos.csv` | **06-12** | <2 K | **Cero referencias** | Borrable |
| H4 | `results/logs/06_modeling_shap_reference/…hardcoded_tiebreak_backup.csv` | 06-13 | <20 K | **Cero referencias** | Borrable |
| H5 | `results/predictions/06_modeling/test_predictions.csv` + `…_xgboost.csv` | 06-14 | ~39 M | trackeadas en git, regenerables (fase 6) | A `.gitignore` |
| H6 | `results/figures/11_recorrido_skill/` (R1–R36) | 06-16 | 5,5 M | **Cero referencias** (notebook borrado) | Archivar |
| H7 | 31 figs en `figs/` no incluidas por LaTeX (`ev7/ev8`, `fase*/fs_*` viejas, `rec_*`, `f10_b3/b6/b7`…) | 06-13→16 | ~10 M | no en `\includegraphics` | Archivar |
| H8 | `results/figures/12_superfiguras/` (F01–F15) | 06-16 | 3,4 M | genera el notebook actual, **no** en LaTeX | DECISIÓN (ver §5) |
| H9 | `.agents/*.zip` (×3) + carpetas descomprimidas | — | 170 M zips, tracked | tooling, no entregable | §6 destructivo |
| H10 | `notebooks/recorrido_memoria.{ipynb,html}` en histórico git | — | ~43 M en pack | borrados del árbol | §6 destructivo |
| H11 | predicciones gitignored en disco (`validation_predictions.csv`, `*_qfs.csv`) | 06-14/15 | 508 M | regenerables | Opcional (disco) |

**Patrón de fondo:** el re-run canónico del 06-14 regeneró **tablas y datos** pero **no los reports** → los restos viejos se concentran en `reports/` y en el snapshot `previous_*`.

---

## 3. Plan por fases (orden recomendado: A → F)

Cada fase indica reversibilidad. **Antes de cualquier borrado:** commit limpio del estado actual (hay 126 modificados + 108 untracked sin commitear).

### Fase A — Restos sin referencias (alta confianza, reversible)
Verificado: cero referencias en código/notebooks/LaTeX.
```
results/tables/07_final_comparison/fase7_validacion_completitud.csv   # H3
results/tables/07_final_comparison/fase7_inventario_artefactos.csv    # H3
results/logs/06_modeling_shap_reference/*hardcoded_tiebreak_backup.csv # H4
```
Acción: mover a `docs/auditoria/_archivo_limpieza_2026-06-16/` (no `rm` directo). Ganancia: trivial en peso, alta en claridad.

### Fase B — Reports stale 06-12 (DECISIÓN, no solo borrar)
`results/reports/05_feature_selection/` y `results/reports/06_modeling/` (pre-XGBoost).
- Verificado: la memoria **no** los referencia ni arrastra sus cifras (0.766/0.85 ausentes en `tex/`).
- Riesgo: bajo para la memoria; alto si alguien los reabre creyéndolos vigentes.
- **Decisión del autor:** (a) **regenerar** desde `fase5.ipynb`/`fase6.ipynb` actuales si se quieren reports vivos, o (b) archivarlos como histórico.

### Fase C — Snapshot de regresión `previous_tables` (archivar tras cerrar fase 5)
`results/logs/05_feature_selection/previous_tables_20260613_112241/` (46 M, H1).
- Lo usa `verify_fase5_notebook.py` como baseline de regresión (degrada si falta, no rompe).
- Acción: conservar mientras se re-ejecute/valide fase 5; después mover a archivo. **No borrar mientras haya re-runs pendientes.**

### Fase D — Política `.gitignore` de predicciones regenerables (repo −39 M)
`test_predictions.csv` + `test_predictions_xgboost.csv` (H5) están trackeadas con criterio incoherente respecto a sus hermanas ya ignoradas.
```
git rm --cached results/predictions/06_modeling/test_predictions.csv \
                results/predictions/06_modeling/test_predictions_xgboost.csv
# añadir ambas a .gitignore (junto al resto de predictions)
```
Reversible (los CSV siguen en disco; regenerables vía fase 6).

### Fase E — Capa visual: generaciones superadas (archivar, no borrar)
- `results/figures/11_recorrido_skill/` (H6) — huérfana, mover a archivo.
- Las 31 figs no usadas de `figs/` (H7) — mover a `Plantilla_Latex_GCD/tfgs/figs/_descartadas/` hasta cerrar la memoria (no romper `\includegraphics`).

### Fase F — Salud del repositorio (DESTRUCTIVO — requiere OK explícito)
El `.git` de 874 M se explica casi entero por binarios no-fuente:
- `.agents/*.zip` (170 M, H9) — además duplican carpetas descomprimidas al lado.
- `recorrido_memoria.*` en histórico (~43 M, H10).
- Sacar `.agents/` del árbol + `.gitignore` es seguro/reversible. **Recuperar el espacio del `.git` exige `git filter-repo`** → reescribe hashes de commits. Hablarlo y confirmarlo antes. Resultado esperado: repo de ~874 M → <100 M.

---

## 4. Datos derivados pesados (`data/selected_features`, 2,4 G)

Run único 06-14, regenerable vía `src/fase5_feature_selection.py`. **1.260 ficheros trackeados** en git.
Decisión de retención (no urgente, no destructiva de resultados):
- Conservar todo (estado actual), o
- Conservar solo los `k` y datasets que entran en la memoria + un manifest, o
- Regenerar bajo demanda y sacar del repo.
Recordatorio: el alias `X_val`/`X_validation` (§1) **no** es deduplicable sin tocar código.

---

## 5. Decisión abierta bloqueante (figuras)

El notebook actual produce `F01–F15` (`12_superfiguras/`, H8), pero el LaTeX sigue incluyendo la familia `f1…f10`/`a*`/`ev*`. O bien (a) la memoria usa deliberadamente la familia antigua y `F01-F15` es trabajo nuevo sin cablear, o (b) `F01-F15` debe sustituirlas y el LaTeX está desactualizado. **Hasta resolver esto, `12_superfiguras/` no se toca.**

---

## 6. Resumen de ganancias

| Fase | Acción | Disco | Repo (.git) | Riesgo |
|---|---|---|---|---|
| A | borrar restos sin refs | ~0 | ~0 | nulo |
| B | regenerar/archivar reports | ~0 | ~0 | bajo (decisión) |
| C | archivar `previous_tables` | 46 M | — | bajo (tras fase 5) |
| D | gitignore predicciones | 0 | −39 M | nulo (reversible) |
| E | archivar figs superadas | ~15 M | — | nulo |
| F | purgar `.agents`/histórico | 213 M | **−~770 M** | ALTO (reescribe historia) |
| D-datos | política selected_features | hasta 1,5 G | hasta −1,5 G | medio (decisión) |

**Prioridad real:** no es el peso. Es **(B)** cerrar la ambigüedad de los reports pre-XGBoost y **(§5)** decidir la generación de figuras definitiva, porque son los dos puntos donde una versión vieja podría colarse en el entregable.
