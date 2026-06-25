# Registro de limpieza 2026-06-16

## Borrado

- `results/tables/07_final_comparison/fase7_validacion_completitud.csv`
- `results/tables/07_final_comparison/fase7_inventario_artefactos.csv`
- `results/logs/06_modeling_shap_reference/modeling_test_results_candidates_before_shap.hardcoded_tiebreak_backup.csv`

Nota: la ruta pedida como `results/logs/06_modeling_shap_reference/hardcoded_tiebreak_backup.csv` no existía con ese nombre exacto. La ruta presente en el árbol era `modeling_test_results_candidates_before_shap.hardcoded_tiebreak_backup.csv`, y se archivó como backup hardcoded obsoleto de la misma familia.

## Regenerado

- Reejecutado `notebooks/fase5.ipynb` completo con `conda run -n qfs_env python -m nbconvert --to notebook --execute --inplace notebooks/fase5.ipynb`.
- Reejecutado `notebooks/fase6.ipynb` completo con `conda run -n qfs_env python -m nbconvert --to notebook --execute --inplace notebooks/fase6.ipynb`.
- Regenerados reports de `results/reports/05_feature_selection/` y `results/reports/06_modeling/` desde tablas canónicas actuales mediante `scripts/regenerate_phase_reports.py` porque los notebooks actuales no recreaban esas carpetas.
- Los reports de fase 6 incluyen XGBoost. Madelon queda reportado con `boruta_confirmed_19 / xgboost / macro-F1 0.9067` como mejor candidato observado en test, no con el resumen antiguo `random_forest` ~0.766.

## Movido / archivado

Destino de archivo: `docs/auditoria/_archivo_limpieza_2026-06-16/`.

- Movida carpeta completa `results/figures/11_recorrido_skill/` a `docs/auditoria/_archivo_limpieza_2026-06-16/results/figures/11_recorrido_skill/`.
- Archivos en `11_recorrido_skill`: 38.
- Movidas imágenes no referenciadas desde `Plantilla_Latex_GCD/tfgs/figs/`: 28.
- Comprobación posterior de LaTeX: 34 `\includegraphics`, 31 bases únicas, 0 figuras faltantes.
- No se movieron logos ni imágenes referenciadas por los `.tex`.
- No se movió `results/figures/10_memoria/` ni `results/figures/12_superfiguras/`.

## Gitignore / predicciones

- Añadidas a `.gitignore`:
  - `/results/predictions/06_modeling/test_predictions.csv`
  - `/results/predictions/06_modeling/test_predictions_xgboost.csv`
- Ejecutado `git rm --cached` sobre ambas rutas.
- Los dos CSV siguen presentes en disco:
  - `results/predictions/06_modeling/test_predictions.csv`
  - `results/predictions/06_modeling/test_predictions_xgboost.csv`

## Compilación LaTeX

`latexmk` existe dentro de `qfs_env`, pero falla porque la instalación TeX Live del entorno no tiene `pdflatex.fmt` y `fmtutil-sys` tampoco puede generarlo por ausencia de `mktexlsr.pl`.

Compilación cerrada correctamente con Tectonic:

```text
conda run -n qfs_env tectonic -X compile ejemplo-memoria.tex
note: Writing `ejemplo-memoria.pdf` (7.35 MiB)
```

Salida relevante: hubo warnings tipográficos `Overfull \hbox` / `Underfull \vbox`, pero no errores de compilación ni figuras faltantes. PDF generado: `Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf` (`7.4M`, 2026-06-16 10:44).

Verificación posterior: todas las figuras referenciadas por `\includegraphics` existen tras el archivo (`refs=34`, `unique=31`, `missing=0`).

## Verificaciones

### `conda run -n qfs_env python scripts/verify_fase5_notebook.py`

```json
{
  "checks": {
    "a_outputs_have_observation": true,
    "b_no_repeated_long_phrases": true,
    "c_numeric_observations_ge_70pct": true,
    "d_section_intros_ok": true,
    "e_figures_saved_match_displayed": true,
    "f_execution_clean": true,
    "g_no_big_bang": true,
    "h_no_internal_audit_visible": true,
    "i_no_forbidden_visible_tables": true,
    "j_src_import_present": true,
    "k_no_pipeline_vocabulary": true,
    "l_unaffected_methods_identical": true,
    "m_roster_and_boruta_ok": true
  },
  "report": "results/logs/05_feature_selection/fase5_verification_report.json"
}
```

### `conda run -n qfs_env python scripts/verify_fase6_notebook.py`

```json
{
  "checks": {
    "a_outputs_have_observation": true,
    "b_no_repeated_long_phrases": true,
    "c_numeric_observations_ge_70pct": true,
    "d_section_intros_ok": true,
    "e_figures_saved_match_displayed": true,
    "f_execution_clean": true,
    "g_no_big_bang": true,
    "h_no_internal_audit_visible": true,
    "i_no_forbidden_visible_tables": true,
    "j_src_import_present": true,
    "k_no_pipeline_vocabulary": true,
    "l_grid_baseline_plus_12": true,
    "m_boruta_confirmed_sizes": true,
    "n_predictions_by_row": true,
    "o_stable_model_config": true,
    "p_shap_real_library_used": true,
    "q_shap_values_for_all_candidates": true,
    "r_test_candidates_deterministic": true
  },
  "report": "results/logs/06_modeling/fase6_verification_report.json"
}
```

## Estado final resumido

- Hay cambios sin commit previos y nuevos; no se ha hecho commit.
- `data/selected_features/` no se ha tocado.
- `.agents/` no se ha tocado salvo que ya existían cambios previos no relacionados.
- No se ha reescrito historial de git.
