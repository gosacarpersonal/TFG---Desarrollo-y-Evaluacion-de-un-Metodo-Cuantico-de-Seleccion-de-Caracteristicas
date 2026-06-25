from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks" / "fase9.ipynb"
TABLE8 = ROOT / "results" / "tables" / "08_quantum"
FIG8 = ROOT / "results" / "figures" / "08_quantum"
TABLE7 = ROOT / "results" / "tables" / "07_final_comparison"
PRED8 = ROOT / "results" / "predictions" / "08_quantum"
DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]
MODELS = ["logistic_regression", "linear_svm", "random_forest", "xgboost"]
VERDICTOS = {"mejora_significativa", "empate_practico", "equivalente", "deterioro"}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def is_missing(value: str | None) -> bool:
    return value is None or value == "" or value.lower() == "nan"


def main() -> int:
    report: dict[str, object] = {"notebook_exists": NB.exists()}

    results_path = TABLE8 / "qfs_model_results.csv"
    contrasts_path = TABLE8 / "contrastes_pareados_qfs.csv"
    op_path = TABLE8 / "comparacion_qfs_vs_baseline.csv"
    cfg_path = TABLE8 / "comparacion_qfs_configuraciones_vs_baseline.csv"
    ext_path = TABLE7 / "fase7_comparacion_final_con_qfs.csv"
    pred_test_path = PRED8 / "test_predictions_qfs.csv"
    pred_val_path = PRED8 / "validation_predictions_qfs.csv"

    for name, path in [
        ("model_results_exists", results_path),
        ("contrasts_exists", contrasts_path),
        ("operative_comparison_exists", op_path),
        ("config_comparison_exists", cfg_path),
        ("extended_fase7_exists", ext_path),
        ("test_predictions_exists", pred_test_path),
        ("validation_predictions_exists", pred_val_path),
    ]:
        report[name] = path.exists()

    if results_path.exists():
        results = read_csv_rows(results_path)
        report["qfs_results_40_rows"] = len(results) == 5 * 2 * 4
        grouped: dict[tuple[str, str], set[str]] = {}
        for row in results:
            grouped.setdefault((row["dataset"], row["configuration"]), set()).add(row["model_name"])
        report["qfs_results_models_complete"] = bool(grouped) and all(models == set(MODELS) for models in grouped.values())
        metric_cols = ["validation_macro_f1", "test_macro_f1", "test_balanced_accuracy"]
        report["qfs_results_no_missing_metrics"] = not any(is_missing(row.get(col)) for row in results for col in metric_cols)

    if contrasts_path.exists():
        contrasts = read_csv_rows(contrasts_path)
        needed = {
            "ci_low",
            "ci_high",
            "sign_permutation_p_value",
            "p_value_fdr",
            "p_value_holm",
            "label_permutation_p_value",
        }
        report["contrasts_40_rows"] = len(contrasts) == 5 * 2 * 4
        columns = set(contrasts[0].keys()) if contrasts else set()
        report["contrasts_columns_present"] = needed.issubset(columns)
        report["contrasts_no_missing_stats"] = (
            not any(is_missing(row.get(col)) for row in contrasts for col in needed)
            if needed.issubset(columns)
            else False
        )

    if op_path.exists():
        op = read_csv_rows(op_path)
        report["operative_5_rows"] = len(op) == 5 and sorted(row["dataset"] for row in op) == sorted(DATASETS)
        report["operative_all_qfs_na"] = {row["configuration"] for row in op} == {"qfs_na"}
        report["operative_verdicts_valid"] = {row["veredicto"] for row in op}.issubset(VERDICTOS)

    if cfg_path.exists():
        cfg = read_csv_rows(cfg_path)
        cfg_grouped: dict[str, list[dict[str, str]]] = {}
        for row in cfg:
            cfg_grouped.setdefault(row["dataset"], []).append(row)
        report["config_two_per_dataset"] = len(cfg_grouped) == 5 and all(len(rows) == 2 for rows in cfg_grouped.values())
        report["config_has_oracle_and_na"] = bool(cfg_grouped) and all(
            {"qfs_na", "qfs_oracle_mucke"}.issubset({row["configuration"] for row in rows})
            for rows in cfg_grouped.values()
        )

    if ext_path.exists():
        ext = read_csv_rows(ext_path)
        report["extended_contains_fase9_qfs"] = "fase9_qfs" in {row.get("fuente", "") for row in ext}

    figures = [FIG8 / f"fase9_resumen_evidencia_{dataset}.png" for dataset in DATASETS]
    report["all_evidence_figures_exist"] = all(path.exists() for path in figures)

    bool_checks = {k: v for k, v in report.items() if isinstance(v, bool)}
    overall = all(bool_checks.values())
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("OVERALL:", "PASS" if overall else "FAIL")
    (ROOT / "results" / "logs" / "08_quantum").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "logs" / "08_quantum" / "fase9_evaluacion_verification_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
