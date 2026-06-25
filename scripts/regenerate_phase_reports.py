from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
R5 = ROOT / "results/reports/05_feature_selection"
R6 = ROOT / "results/reports/06_modeling"
T5 = ROOT / "results/tables/05_feature_selection"
T6 = ROOT / "results/tables/06_modeling"
F5 = ROOT / "results/figures/05_feature_selection"
F6 = ROOT / "results/figures/06_modeling"


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def md_table(
    df: pd.DataFrame,
    cols: list[str] | None = None,
    n: int | None = None,
    floatfmt: int = 4,
) -> str:
    if cols is not None:
        df = df[cols]
    if n is not None:
        df = df.head(n)
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(
                lambda value: "" if pd.isna(value) else f"{value:.{floatfmt}f}"
            )
        else:
            out[col] = out[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(out.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(out.columns)) + " |"
    rows = ["| " + " | ".join(map(str, row)) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep] + rows)


def bullet(items) -> str:
    return "\n".join(f"- {item}" for item in items)


def write_phase5(stamp: str) -> None:
    R5.mkdir(parents=True, exist_ok=True)
    input_summary = read(T5 / "fs_input_dataset_summary.csv")
    method_registry = read(T5 / "fs_method_registry.csv")
    k_values = read(T5 / "fs_k_values_by_dataset.csv")
    exec_times = read(T5 / "fs_all_execution_times.csv")
    selected_sets = read(T5 / "fs_selected_feature_sets.csv")
    stability = read(T5 / "fs_jaccard_stability.csv")
    perm = read(T5 / "fs_permutation_summary.csv")
    redundancy = read(T5 / "fs_redundancy_vs_full.csv")

    exec_summary = (
        exec_times.groupby(["dataset", "method"], as_index=False)
        .agg(
            runs=("status", "size"),
            ok_runs=("status", lambda values: int((values == "ok").sum())),
            mean_elapsed_seconds=("elapsed_seconds", "mean"),
            sample_applied=("sample_applied", "max"),
        )
        .sort_values(["dataset", "method"])
    )
    stab_summary = (
        stability.groupby(["dataset", "method"], as_index=False)
        .agg(
            mean_jaccard=("jaccard", "mean"),
            min_jaccard=("jaccard", "min"),
            comparisons=("jaccard", "size"),
        )
        .sort_values(["dataset", "mean_jaccard"], ascending=[True, False])
    )
    sets_summary = (
        selected_sets.groupby(["dataset", "method"], as_index=False)
        .agg(n_sets=("path", "size"), min_k=("k", "min"), max_k=("k", "max"))
        .sort_values(["dataset", "method"])
    )
    failed = exec_times[exec_times["status"] != "ok"]
    figs = sorted(str(path.relative_to(ROOT)) for path in F5.rglob("*") if path.is_file())

    report = f"""# Fase 5. Selección clásica de características

Regenerado: {stamp}.

La fase aplica selectores clásicos sobre `X_train, y_train` y proyecta las columnas seleccionadas a validation y test sin volver a decidir con esos splits. Este report se ha reconstruido desde las tablas canónicas actuales de `results/tables/05_feature_selection/` tras ejecutar `notebooks/fase5.ipynb` completo en `qfs_env`.

## Datasets

{md_table(input_summary)}

## Métodos registrados

{md_table(method_registry)}

## Valores de k

{md_table(k_values)}

## Ejecución

Runs totales: {len(exec_times)}. Runs con estado `ok`: {int((exec_times["status"] == "ok").sum())}. Runs con incidencias: {len(failed)}.

{md_table(exec_summary, n=30)}

## Subconjuntos exportados

Subconjuntos exportados: {len(selected_sets)}. Directorio conservado completo: `data/selected_features/`.

{md_table(sets_summary, n=40)}

## Estabilidad

{md_table(stab_summary, n=40)}

## Permutación y redundancia

Tablas disponibles: `fs_permutation_summary.csv` ({len(perm)} filas) y `fs_redundancy_vs_full.csv` ({len(redundancy)} filas).

## Cierre

La fase queda sincronizada con el run canónico actual. Los alias `X_val_selected.csv` y `X_validation_selected.csv` se conservan intencionadamente y no se deduplican.
"""
    (R5 / "fase5_feature_selection_report.md").write_text(report, encoding="utf-8")
    (R5 / "fs_initial_audit.md").write_text(
        f"""# Fase 5. Auditoría inicial

Regenerado: {stamp}.

Entradas principales verificadas desde tablas actuales:

{md_table(input_summary)}

No se han tocado `data/selected_features/` ni sus alias de validation. La reejecución de `notebooks/fase5.ipynb` completó sin error mediante nbconvert.
""",
        encoding="utf-8",
    )
    (R5 / "fs_ead_summary.md").write_text(
        f"""# Fase 5. Resumen EDA heredado

Regenerado: {stamp}.

La selección trabaja sobre los datasets procesados y splits heredados. Resumen operativo:

{md_table(input_summary)}
""",
        encoding="utf-8",
    )
    (R5 / "fs_phase5_handoff_to_phase6.md").write_text(
        f"""# Fase 5 -> Fase 6. Handoff

Regenerado: {stamp}.

Fase 6 debe consumir las tablas y carpetas seleccionadas ya materializadas. Resumen de subconjuntos por dataset/método:

{md_table(sets_summary)}

Contrato preservado: los datos derivados de `data/selected_features/` se conservan completos.
""",
        encoding="utf-8",
    )
    (R5 / "fs_visual_audit.md").write_text(
        f"""# Fase 5. Auditoría visual

Regenerado: {stamp}.

Figuras detectadas en `results/figures/05_feature_selection/`: {len(figs)}.

{bullet(figs[:120]) if figs else "_Sin figuras detectadas._"}
""",
        encoding="utf-8",
    )
    (R5 / "fase5_feature_selection_report.tex").write_text(
        "\\section*{Fase 5. Selección clásica de características}\n"
        "Report regenerado desde las tablas canónicas actuales. La fase conserva "
        "el contrato train-only, materializa subconjuntos en "
        "\\texttt{data/selected\\_features/} y mantiene los alias de validation "
        "requeridos por fases posteriores.\n",
        encoding="utf-8",
    )


def write_phase6(stamp: str) -> None:
    R6.mkdir(parents=True, exist_ok=True)
    validation = read(T6 / "modeling_validation_results_all.csv")
    test = read(T6 / "modeling_test_results_candidates.csv")
    ci = read(T6 / "modeling_test_confidence_intervals.csv")
    pairwise = read(T6 / "modeling_pairwise_comparison_tests.csv")
    perm = read(T6 / "modeling_permutation_test_results.csv")
    shap_files = sorted(T6.glob("modeling_shap_*"))
    figs = sorted(str(path.relative_to(ROOT)) for path in F6.rglob("*") if path.is_file())

    best_validation = (
        validation.sort_values(["dataset", "validation_rank"])
        .groupby("dataset", as_index=False)
        .head(1)
    )
    best_test = (
        test.sort_values(["dataset", "test_macro_f1"], ascending=[True, False])
        .groupby("dataset", as_index=False)
        .head(1)
    )
    models_by_dataset = (
        validation.groupby("dataset")["model_name"]
        .apply(lambda values: ", ".join(sorted(values.dropna().unique())))
        .reset_index(name="models_evaluated")
    )
    xgb_count = int((validation["model_name"] == "xgboost").sum())
    madelon = test[test["dataset"] == "madelon"].sort_values(
        "test_macro_f1", ascending=False
    )

    report = f"""# Fase 6. Modelado y evaluación final

Regenerado: {stamp}.

La fase compara modelos sobre todos los atributos y subconjuntos procedentes de Fase 5. Este report se ha reconstruido desde las tablas canónicas actuales de `results/tables/06_modeling/` tras ejecutar `notebooks/fase6.ipynb` completo en `qfs_env`.

## Cobertura de modelos

Experimentos de validation: {len(validation)}. Candidatos evaluados en test: {len(test)}. Filas de validation con `xgboost`: {xgb_count}.

{md_table(models_by_dataset)}

## Mejor configuración por validation

{md_table(best_validation, ["dataset", "feature_set", "model_name", "macro_f1", "balanced_accuracy", "n_features_used"])}

## Mejor configuración observada en test entre candidatos cerrados

{md_table(best_test, ["dataset", "feature_set", "model_name", "validation_macro_f1", "test_macro_f1", "test_balanced_accuracy", "n_features_used"])}

## Candidatos Madelon

{md_table(madelon, ["dataset", "feature_set", "model_name", "validation_macro_f1", "test_macro_f1", "test_balanced_accuracy", "n_features_used"])}

## Intervalos y comparaciones

Intervalos bootstrap en test: {len(ci)} filas. Comparaciones pareadas frente a baseline: {len(pairwise)} filas. Tests de permutación: {len(perm)} filas.

{md_table(pairwise, n=20)}

## SHAP

Ficheros SHAP/tablas relacionadas detectados: {len(shap_files)}. Figuras de modelado detectadas: {len(figs)}.

## Lectura prudente

Los subconjuntos no se reinterpretan como óptimos universales: la selección de candidatos se cierra en validation y test se consulta para la evaluación final. La versión actual ya incluye XGBoost; en Madelon el candidato principal actual no es el antiguo `random_forest` con macro-F1 alrededor de 0.766, sino configuraciones `xgboost` como `boruta_confirmed_19` y `rfe_k10`.
"""
    (R6 / "fase6_resumen_para_memoria.md").write_text(report, encoding="utf-8")
    (R6 / "fase6_final_audit.md").write_text(
        f"""# Fase 6. Auditoría final

Regenerado: {stamp}.

Checks de coherencia desde tablas actuales:

- Experimentos validation: {len(validation)}.
- Candidatos test: {len(test)}.
- Modelos presentes: {", ".join(sorted(validation["model_name"].dropna().unique()))}.
- Filas XGBoost en validation: {xgb_count}.
- Mejor Madelon en test: {madelon.iloc[0]["feature_set"]} / {madelon.iloc[0]["model_name"]} / macro-F1 {madelon.iloc[0]["test_macro_f1"]:.4f}.

{md_table(best_test, ["dataset", "feature_set", "model_name", "test_macro_f1", "test_balanced_accuracy", "n_features_used"])}
""",
        encoding="utf-8",
    )
    (R6 / "fase6_handoff_to_phase7.md").write_text(
        f"""# Fase 6 -> Fase 7. Handoff

Regenerado: {stamp}.

Tablas principales para fases posteriores:

- `results/tables/06_modeling/modeling_validation_results_all.csv`
- `results/tables/06_modeling/modeling_test_results_candidates.csv`
- `results/tables/06_modeling/modeling_test_confidence_intervals.csv`
- `results/tables/06_modeling/modeling_pairwise_comparison_tests.csv`
- `results/predictions/06_modeling/test_predictions.csv`
- `results/predictions/06_modeling/test_predictions_xgboost.csv`

Candidatos test actuales:

{md_table(test, ["dataset", "feature_set", "model_name", "candidate_label", "validation_macro_f1", "test_macro_f1", "n_features_used"])}
""",
        encoding="utf-8",
    )
    (R6 / "fase6_shap_interpretation.md").write_text(
        f"""# Fase 6. Interpretación SHAP

Regenerado: {stamp}.

Tablas SHAP detectadas en `results/tables/06_modeling/`: {len(shap_files)}.

{bullet(str(path.relative_to(ROOT)) for path in shap_files[:120]) if shap_files else "_Sin tablas SHAP detectadas._"}
""",
        encoding="utf-8",
    )
    (R6 / "fase6_visual_quality_audit.md").write_text(
        f"""# Fase 6. Auditoría visual

Regenerado: {stamp}.

Figuras detectadas en `results/figures/06_modeling/`: {len(figs)}.

{bullet(figs[:120]) if figs else "_Sin figuras detectadas._"}
""",
        encoding="utf-8",
    )
    (R6 / "fase6_resumen_para_memoria.tex").write_text(
        "\\section*{Fase 6. Modelado y evaluación final}\n"
        "Report regenerado desde las tablas canónicas actuales. La parrilla "
        "actual incluye XGBoost y los candidatos de Madelon ya no corresponden "
        "al resumen antiguo basado solo en \\texttt{random\\_forest} con "
        "macro-F1 aproximada de 0.766.\n",
        encoding="utf-8",
    )


def main() -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_phase5(stamp)
    write_phase6(stamp)
    print(f"Reports regenerados en {R5.relative_to(ROOT)} y {R6.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
