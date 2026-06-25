# Instrucciones para Codex — ejecución del TFG QFS por tiers

> Guion único para que Codex ejecute los prompts del directorio `docs/auditoria/` en
> orden, con verificaciones intermedias. Fuente primaria de verdad: el código real
> (`src/`, `scripts/`, `QFS_based_on_NA/`), los papers de `docs/papers/` y la propuesta
> de `docs/propuesta/`. **Los `.md` de `docs/decisions/`, `docs/tfg_prequantum_*.md` y
> los worklog son secundarios** (generados por IA): no tratar como autoridad; verificar
> siempre contra fuente primaria.

## Reglas de oro (no negociables)

1. **Estructura canónica:** todo cambio respeta `docs/auditoria/estructura_notebooks.md`
   (markdown sección → funciones visibles inline → por dataset → narrativa por dataset
   → síntesis). NO mover funciones inline de 1-4 a `src`. NO hacer cuadernos delgados.
2. **Fuente primaria:** anclar cada decisión en código (`QFS_based_on_NA/`) o papers
   (`docs/papers/`). Si un `.md` contradice una fuente primaria, prevalece la primaria.
3. **Coherencia código↔notebook↔memoria:** el cuaderno y la memoria deben describir lo
   que el código hace, no lo que parece. Verificar con tests/lectura, no con suposición.
4. **Verificar antes de pasar de tier:** cada tier tiene su check; no avanzar si falla.
5. **No `--no-verify`, no `git push --force`, no destruir trabajo en progreso.**
6. **Reportar diffs y outputs de los verify** al cierre de cada tier.

## Orden de ejecución (cascada)

### Tier 1 — Correctitud crítica (bloque clásico)

Ejecuta en este orden. Una sola sesión por tarea, con verificación al final.

1. **T1.1 — Fase 6 SHAP real.** Lee `docs/auditoria/prompt_fase6.md` (punto 1: SHAP).
   Reescribe en `src/phase6_modeling/pipeline.py` (a) `shap_values_array` para que
   PERSISTA la matriz cruda en lugar de colapsarla a media|SHAP|; (b)
   `shap_candidato` para guardar la matriz por candidato; (c) `plot_shap_dataset` para
   usar `shap.summary_plot` (beeswarm) por modelo-dataset, con desglose por clase en
   `olive_oil_3class` y `olive_oil_9class`. Mantén el barplot de media|SHAP| solo como
   complemento si lo deseas.
2. **T1.2 — Fase 6 tie-break neutral.** Misma fase. Elimina
   `SELECTOR_TIE_PRIORITY_BY_DATASET` (líneas 53-63) y sustituye por desempate
   alfabético sobre `selector` en `seleccionar_candidatos_test:389`. Documenta el
   cambio en el cuaderno.
3. **T1.3 — Fase 5 regenerar.** Solo regeneración. Ejecuta
   `python scripts/rebuild_fase5_notebook.py` (el script ya está corregido para
   `variance` y MC/FSFS). Pasa `scripts/verify_fase5_notebook.py`.

**Verificación Tier 1 (todo lo siguiente debe pasar):**
- `python scripts/verify_fase5_notebook.py` → OK.
- `python scripts/verify_fase6_notebook.py` → OK (tras re-ejecución SHAP).
- `ls results/figures/06_modeling/shap_summary_*.png` muestra figuras y al inspeccionar
  un PNG se ve un BEESWARM, no un barplot.
- `results/tables/06_modeling/modeling_shap_values_full_*.csv` (matriz cruda) existe.
- `git diff src/phase6_modeling/pipeline.py` no contiene
  `SELECTOR_TIE_PRIORITY_BY_DATASET`.

### Tier 3 — Editorial 1-4 (en paralelo con Tier 2, no se pisan)

Bajo coste. Puede hacerse en cualquier momento tras Tier 1.

4. **T3.1 — Fase 1.** `docs/auditoria/prompt_fase1.md`. Edita
   `scripts/rebuild_fase1_notebook.py`: minimiza `COLUMNAS_PRESENTACION` y
   retira/transforma `01_08_asociacion`×4 y `01_11_redundancia`×4. Regenera.
5. **T3.2 — Fase 2.** `docs/auditoria/prompt_fase2.md`. Trocea la celda de 222 líneas
   (sección 2.9) dentro del cuaderno. Regenera.
6. **T3.3 — Fase 3.** `docs/auditoria/prompt_fase3.md`. Retira/transforma
   `fase3_asociacion`×4 y `fase3_redundancia`×4. Regenera.
7. **T3.4 — Fase 4.** `docs/auditoria/prompt_fase4.md`. Refuerza la nota sobre el χ²
   entre splits estratificados. Regenera.

**Verificación Tier 3:**
- `python scripts/verify_fase{1,2,3,4}_notebook.py` → todos OK.
- Conteo `find results/figures/0{1,3}_* -name "*asociacion*" | wc -l` muestra que
  los heatmaps redundantes se han retirado o convertido.

### Tier 2 — Ancla con paper QFS + estructura paso 2

Una sola re-ejecución de fase 6 (la más cara). Asegúrate de tener cerrado Tier 1 antes.

8. **T2.1 — Fase 6 añadir XGBoost.** `docs/auditoria/prompt_fase6.md` punto 4. Añade
   `"xgboost"` a `MODEL_NAMES` (`pipeline.py:52`) y configura `XGBClassifier` con los
   hiperparámetros indicados. Añade AUC-ROC como métrica secundaria SOLO en binarios.
   Re-ejecuta fase 6 completa (~25 % más experimentos, 240 en validation).
9. **T2.2 — Paso 2 estructura.** Sube al cuaderno de fase 5 la creación visible de los
   selectores espejo de QFS (relevancia I(x;y), redundancia I(x;x), mrmr/rrfs). En fase
   6, sube la creación visible del cálculo SHAP (post T1.1) y de los contrastes. En
   fase 7, muestra la regla de decisión del veredicto.
10. **T2.3 — Fase 7 umbral.** Verifica/justifica `UMBRAL_EFECTO_PRACTICO`. Regenera.

**Verificación Tier 2:**
- `python scripts/verify_fase{5,6,7}_notebook.py` → todos OK.
- `results/tables/06_modeling/validation_results.csv` tiene 4 × 12 × 5 = 240 filas o
  equivalente (3 modelos antiguos + xgboost) en validation.
- `results/tables/06_modeling/test_predictions_*.csv` para xgboost están presentes.
- En binarios, hay columna `auc_roc` en las tablas de resultados; en multiclase, no.
- Los cuadernos de 5, 6 y 7 muestran inline las funciones núcleo (no solo `fs.*`,
  `p6.*`, `f7.*`).

### Checkpoint antes de fase cuántica

Antes de arrancar Tier 4, comprueba todo lo siguiente. Si algo no se cumple, vuelve
atrás y arréglalo:

- [ ] Las 7 fases regeneradas pasan su `verify_faseN_notebook.py`.
- [ ] Las cifras de `results/tables/07_final_comparison/comparacion_final.csv` siguen
      cuadrando con el veredicto narrativo de fase 7 (ahora con XGBoost).
- [ ] Las matrices `Iᵢ` y `Rᵢⱼ` de fase 5 están en disco, **sin normalizar** y con
      5 bins uniforme (`grep -l "normalization_note" results/tables/05_*`).
- [ ] La memoria LaTeX compila sin errores
      (`cd Plantilla_Latex_GCD/tfgs && conda run -n qfs_env tectonic ejemplo-memoria.tex`).
- [ ] El bibliografía contiene `chen2016` (XGBoost), `mucke2023` y `orquin2026`.
- [ ] No hay diferencias semánticas pendientes entre `metodologia.tex` y el código
      (cualquier afirmación verificable apunta a lo que el código realmente hace).

### Tier 4 — Fase cuántica (cuando el checkpoint pasa)

11. **T4-A — Solver: β + oráculo.** `docs/auditoria/prompt_fase8a_solver.md`.
    Implementa β en `QFS_Auxiliar_functions.py` (sin tocar `*_OG.py`) y el oráculo
    `Q*(α)` exacto + recorrido vía Algorithm 1 de Mücke. Pasa
    `scripts/verify_fase8_solver.py`.
12. **T4-B — Ejecución QFS.** `docs/auditoria/prompt_fase8b_ejecucion.md`. Construye
    `notebooks/fase8.ipynb` con pre-selección híbrida (bcw 30→20, madelon 500→20),
    barrido β∈{0,0.1,…,1.0}, oráculo α-recorrido, selección de (α,β) por validation.
    Pasa `scripts/verify_fase8_ejecucion.py`.
13. **T4-C — Evaluación + integración con fase 7.**
    `docs/auditoria/prompt_fase8c_evaluacion.md`. Construye `notebooks/fase9.ipynb`,
    evalúa QFS con el protocolo idéntico de fase 6, comparación pareada vs baselines,
    extensión de la tabla maestra de fase 7. Pasa `scripts/verify_fase9_evaluacion.py`.

**Verificación Tier 4:**
- `results/tables/08_quantum/comparacion_qfs_vs_baseline.csv` tiene 5 filas (una por
  dataset), con veredicto bajo la misma regla de fase 7.
- `results/figures/08_quantum/qfs_beta_map_*.png` existe para los 5 datasets.
- Control de calidad: para cada dataset existe el reporte de Hamming + Δcoste entre
  QFS-NA y oráculo.

## Cierre del TFG (post Tier 4)

Reescribir `Plantilla_Latex_GCD/tfgs/tex/resultados.tex` y `conclusiones.tex` con las
cifras QFS reales. **No tocar** `introduccion.tex`, `marco_teorico.tex`, `estado_arte.tex`
ni `metodologia.tex` salvo correcciones puntuales (esos capítulos ya están cerrados y
anclados en fuentes primarias).

## Recuperación ante fallos

- Si un `verify_*` falla, lee el error con cuidado, contrasta con el código y arregla.
  No suprimas el verify ni añadas `# noqa`. La causa raíz suele estar en una
  contradicción real entre lo escrito y lo ejecutado.
- Si el SHAP da error de memoria al persistir la matriz cruda, guarda en formato
  compacto (`.npz`) por candidato, no en CSV.
- Si Gurobi no está disponible para el oráculo, usa la enumeración exhaustiva (cabe
  en ≤20 vars) y declara el límite en el cuaderno.
- En cualquier duda metodológica, **fuente primaria > .md secundario > intuición**.
