# Prompt — Notebook espejo de la memoria (figuras y tablas del TFG)

Construye `notebooks/memoria_visual.ipynb` y su generador
`scripts/rebuild_memoria_visual_notebook.py`. Respeta la estructura canónica
(`docs/auditoria/estructura_notebooks.md`) y la guía de estilo
(`docs/estilo_redaccion_tfg.md`).

## Propósito y principio rector

Un único notebook que **reproduce, en un solo sitio, todas las figuras y tablas que
aparecen en la memoria final del TFG**, en el mismo orden en que aparecen en ella. Sirve
para (a) repasar de un vistazo todo el contenido visual/tabular de la memoria y (b)
refrescar de forma reproducible los artefactos que la memoria consume.

Principios:
- **No recomputa el pipeline.** Lee los artefactos ya generados en `results/` (CSVs y, donde
  haga falta, reusa las funciones de plot de `src/`). Es un notebook de consolidación, no
  de cálculo. Debe ejecutarse en segundos, no en horas.
- **Fuente única de las figuras de la memoria.** Cada figura se regenera llamando a la
  misma función de plot que la produjo en su fase (importada de `src/`) o, si esa función
  no es invocable de forma aislada, copiando el PNG existente; y se escribe en
  `Plantilla_Latex_GCD/tfgs/figs/` con el nombre EXACTO que la memoria referencia.
- **Coherencia LaTeX↔datos.** Para cada tabla hardcodeada en los `.tex`, el notebook
  carga el CSV de origen, muestra el DataFrame y verifica que las cifras clave coinciden
  con las del `.tex` (chequeo explícito que falla si hay deriva).
- **Espejo del orden de la memoria:** una sección por capítulo/sección de la memoria,
  con el mismo encabezado, la caption real como markdown y la figura/tabla debajo.

## Inventario exacto a reproducir (verificado 2026-06-14)

### Figuras (8) — nombre en `figs/` → artefacto origen → fase/plotter

| Figura (figs/) | Artefacto / origen | Capítulo memoria |
|---|---|---|
| `01_02_estructura_filas_por_feature.png` | `results/figures/01_raw_eda/01_02_estructura_filas_por_feature.png` (fase 1) | 5.1 Auditoría base |
| `fase4_validacion_adversarial_auc.png` | `results/figures/04_split_audit/...` (fase 4) | 5.1 Auditoría base |
| `fs_stability_jaccard_heatmap.png` | `results/figures/05_feature_selection/stability/...` (fase 5) | 5.2 Clásica |
| `fs_permutation_above_null_heatmap.png` | `results/figures/05_feature_selection/permutation/...` (fase 5) | 5.2 Clásica |
| `fs_redundancy_delta.png` | `results/figures/05_feature_selection/redundancy/...` (fase 5) | 5.2 Clásica |
| `fase7_test_baseline_vs_seleccion.png` | `results/figures/07_final_comparison/...` (fase 7) | 5.2 Clásica |
| `fase7_estabilidad_vs_rendimiento.png` | `results/figures/07_final_comparison/...` (fase 7) | 5.2 Clásica |
| `qfs_beta_map_madelon.png` | `results/figures/08_quantum/qfs_beta_map_madelon.png` (fase 8) | 5.3 Cuántica |

Para cada una: preferir regenerarla llamando a su función de plot en `src/` sobre el CSV
de origen (mejor: garantiza estilo consistente y figura idéntica a la validada); si no es
invocable de forma aislada, copiar el PNG. En ambos casos, escribir en `figs/` con el
nombre exacto de la tabla.

### Tablas (4) — caption/label en memoria → CSV de origen → verificación

| Tabla (label) | Capítulo | CSV de origen | Cifras clave a verificar |
|---|---|---|---|
| `tab:datasets` | 4 Métodos | derivar de `data/splits/*` o de la tabla de fase 1 | filas/variables/clases por dataset |
| `tab:comparacion` | 5.2 Clásica | `results/tables/07_final_comparison/fase7_comparacion_final_con_qfs.csv` (filas clásicas) | baseline/mejor/delta/veredicto por dataset; madelon $+0.094$ |
| `tab:qfs-control` | 5.3 Cuántica | `results/tables/08_quantum/qfs_quality_control_{madelon,customer_churn}.csv` | Hamming y $\Delta$coste (madelon $-0.010$, churn $+1.323$) |
| `tab:qfs-comparacion` | 5.3 Cuántica | `results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv` | QFS-NA/oráculo/baseline por dataset; deterioros churn y madelon |

## Estructura del notebook (espejo de la memoria)

1. **Markdown intro** + celda de setup: rutas, helper `mostrar_figura(nombre)` (que copia/
   regenera a `figs/` y muestra inline), helper `mostrar_tabla(df)`, helper
   `emitir_latex(df)` para volcar el cuerpo de la tabla LaTeX, y un helper
   `verificar(valor_csv, valor_tex, nombre, tol)` que asegura coherencia.
2. **Sección "Cap. 4 — Conjuntos de datos"**: regenera `tab:datasets` desde los splits
   reales y verifica filas/variables/clases. Una frase por dataset.
3. **Sección "Cap. 5.1 — Auditoría de la base experimental"**: figuras `01_02_*` y
   `fase4_validacion_adversarial_auc`, cada una con su caption real y una lectura breve.
4. **Sección "Cap. 5.2 — Evaluación de los métodos clásicos"**: `tab:comparacion`
   (DataFrame + LaTeX + verificación), figura `fase7_test_baseline_vs_seleccion`, los tres
   heatmaps `fs_*` y `fase7_estabilidad_vs_rendimiento`.
5. **Sección "Cap. 5.3 — Evaluación del método cuántico y comparación"**:
   `qfs_beta_map_madelon`, `tab:qfs-control` y `tab:qfs-comparacion` (DataFrames + LaTeX +
   verificación), con la lectura criterio-vs-optimizador.
6. **Sección final "Coherencia memoria↔datos"**: un resumen de todas las verificaciones
   (todas deben pasar), de modo que ejecutar el notebook confirme que las cifras de los
   `.tex` siguen cuadrando con los artefactos. Si alguna falla, el notebook lo señala.

## Reglas

- NO recomputar fases 1-9 ni reentrenar nada. Solo leer `results/` y `data/splits/`.
- NO inventar cifras: toda tabla sale de un CSV; toda figura de un artefacto o su plotter.
- Las figuras se escriben en `figs/` con el nombre EXACTO que la memoria referencia, de
  modo que ejecutar este notebook deje la memoria lista para compilar.
- Mantener la estructura canónica (markdown sección → función visible → salida → lectura).
- Voz impersonal en los markdown, según la guía de estilo.

## Verificación

`scripts/verify_memoria_visual_notebook.py`: comprueba que (1) el notebook ejecuta de
principio a fin sin errores; (2) tras ejecutarlo, las 8 figuras existen en `figs/` con el
nombre correcto; (3) las verificaciones de coherencia LaTeX↔datos pasan todas; (4) no se
referencia ninguna figura/tabla que la memoria no use (y viceversa: cobertura completa de
las 8 figuras + 4 tablas).

## Nota de mantenimiento

Si en el futuro se añaden o quitan figuras/tablas de la memoria, este notebook y su
verificador son el único sitio que hay que actualizar para mantener el espejo. Conviene
referenciar este notebook en el README como "regenerador de artefactos de la memoria".
