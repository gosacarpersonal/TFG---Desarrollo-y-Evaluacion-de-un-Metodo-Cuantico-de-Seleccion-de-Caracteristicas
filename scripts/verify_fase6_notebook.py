from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "fase6.ipynb"
TABLE_DIR = ROOT / "results" / "tables" / "06_modeling"
FIGURE_DIR = ROOT / "results" / "figures" / "06_modeling"
PRED_DIR = ROOT / "results" / "predictions" / "06_modeling"
LOG_DIR = ROOT / "results" / "logs" / "06_modeling"
REPORT_PATH = LOG_DIR / "fase6_verification_report.json"
SHAP_REFERENCE = ROOT / "results" / "logs" / "06_modeling_shap_reference" / "modeling_test_results_candidates_before_shap.csv"

DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]
ROSTER_12 = {
    "variance",
    "f_classif",
    "mutual_info",
    "mutual_correlation",
    "feature_similarity",
    "mrmr_approx",
    "rrfs",
    "boruta",
    "rfe",
    "l1_logistic",
    "random_forest",
    "linear_svm",
}
BORUTA_K = {
    "breast_cancer_wisconsin": 22,
    "customer_churn": 12,
    "madelon": 19,
    "olive_oil_3class": 8,
    "olive_oil_9class": 8,
}

PIPELINE_WORDS = ["artefacto", "artefactos", "handoff", "fuente de verdad", "pipeline", "filas en el artefacto"]
INTERNAL_WORDS = ["nbformat", "checklist", "inventario", "auto-auditoría", "auto-auditoria", "completitud"]
TABLE_FORBIDDEN = ["criterio", "evidence", "reason", "risk", "mitigation", "status", "check", "cumple", "estado", "ok", "schema", "warnings"]
BIG_BANG = [r"\brun_phase6\s*\(", r"\bforce\s*=\s*True\b", r"\bresultados\s*\[", r"\betapa_[A-Za-z0-9_]*\s*\("]


def cell_source(cell) -> str:
    return cell.get("source", "") or ""


def output_text(cell) -> str:
    chunks = []
    for output in cell.get("outputs", []):
        if output.get("output_type") == "stream":
            chunks.append(output.get("text", ""))
        if output.get("output_type") == "error":
            chunks.extend(output.get("traceback", []))
        for key, value in output.get("data", {}).items():
            if key.startswith("image/"):
                continue
            if isinstance(value, str):
                chunks.append(value)
            elif isinstance(value, list):
                chunks.append("".join(map(str, value)))
    return "\n".join(chunks)


def has_visible_output(cell) -> bool:
    if cell.get("cell_type") != "code":
        return False
    for output in cell.get("outputs", []):
        if output.get("output_type") == "error":
            return True
        if output.get("output_type") == "stream" and output.get("text", "").strip():
            return True
        if any(key in output.get("data", {}) for key in ["text/plain", "text/html", "image/png", "image/jpeg"]):
            return True
    return False


def is_observation(cell) -> bool:
    if cell.get("cell_type") != "markdown":
        return False
    text = re.sub(r"\s+", " ", cell_source(cell).strip())
    return bool(text) and not text.startswith("#")


def observations(cells) -> list[str]:
    rows = []
    for i, cell in enumerate(cells[:-1]):
        if has_visible_output(cell) and is_observation(cells[i + 1]):
            rows.append(re.sub(r"\s+", " ", cell_source(cells[i + 1]).strip()))
    return rows


def outputs_without_observation(cells) -> list[int]:
    return [i + 1 for i, cell in enumerate(cells[:-1]) if has_visible_output(cell) and not is_observation(cells[i + 1])]


def repeated_phrases(obs: list[str]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for text in obs:
        words = re.findall(r"[\wÁÉÍÓÚÜÑáéíóúüñ`_.=-]+", text.lower())
        seen = set()
        for size in range(7, min(13, len(words)) + 1):
            for start in range(0, len(words) - size + 1):
                seen.add(" ".join(words[start : start + size]))
        counts.update(seen)
    return {k: v for k, v in counts.items() if v >= 3}


def cites_number(text: str) -> bool:
    return bool(re.search(r"(?<![\w])[-+]?\d+(?:[.,]\d+)?", text))


def section_intros(cells) -> list[dict[str, object]]:
    technical = re.compile(r"train|validation|test|Macro-F1|bootstrap|permut|SHAP|Boruta|parrilla|modelo|candidato|predic", re.I)
    rows = []
    for cell in cells:
        if cell.get("cell_type") != "markdown":
            continue
        text = cell_source(cell).strip()
        match = re.match(r"^## (6\.\d+) ", text)
        if not match:
            continue
        intro = text.split("\n\n", 1)[1] if "\n\n" in text else ""
        wc = len(re.findall(r"\w+", intro))
        rows.append({"section": match.group(1), "word_count": wc, "mentions_method": bool(technical.search(intro)), "ok": wc > 25 and bool(technical.search(intro))})
    return rows


def figure_checks(cells) -> dict[str, object]:
    pngs = {p.relative_to(ROOT).as_posix() for p in FIGURE_DIR.rglob("*.png")}
    pdfs = {p.relative_to(ROOT).with_suffix(".png").as_posix() for p in FIGURE_DIR.rglob("*.pdf")}
    shown = sum(1 for c in cells for o in c.get("outputs", []) if "image/png" in o.get("data", {}))
    return {
        "saved_png": len(pngs),
        "saved_pdf": len(pdfs),
        "displayed_images": shown,
        "png_without_pdf": sorted(pngs - pdfs),
        "pdf_without_png": sorted(pdfs - pngs),
        "ok": len(pngs) == len(pdfs) == shown and not (pngs - pdfs) and not (pdfs - pngs),
    }


def visible_text(cells) -> dict[str, list[str]]:
    markdown = "\n".join(cell_source(c) for c in cells if c.get("cell_type") == "markdown").lower()
    outputs = "\n".join(output_text(c) for c in cells if c.get("cell_type") == "code").lower()
    visible = markdown + "\n" + outputs
    return {
        "pipeline_words": [w for w in PIPELINE_WORDS if w in visible],
        "internal_words": [w for w in INTERNAL_WORDS if w in visible],
        "table_words": [w for w in TABLE_FORBIDDEN if re.search(rf"\b{re.escape(w)}\b", outputs)],
    }


def source_checks(cells) -> dict[str, object]:
    source = "\n".join(cell_source(c) for c in cells)
    return {"big_bang_hits": [p for p in BIG_BANG if re.search(p, source)], "src_import": "from phase6_modeling import pipeline as p6" in source}


def grid_checks() -> dict[str, object]:
    grid = pd.read_csv(TABLE_DIR / "modeling_experiment_grid.csv")
    per_dataset = grid.groupby("dataset").agg(feature_sets=("feature_set", "nunique"), experiments=("experiment_id", "nunique")).reset_index()
    boruta = grid[grid["selector"].eq("boruta")][["dataset", "k", "n_features"]].drop_duplicates()
    boruta_ok = all(int(boruta.loc[boruta["dataset"].eq(ds), "k"].iloc[0]) == k for ds, k in BORUTA_K.items())
    selectors = set(grid.loc[grid["selector"].ne("all_features"), "selector"].unique())
    return {
        "per_dataset": per_dataset.to_dict(orient="records"),
        "all_13_sets": bool((per_dataset["feature_sets"].eq(13) & per_dataset["experiments"].eq(52)).all()),
        "selectors": sorted(selectors),
        "roster_ok": selectors == ROSTER_12,
        "boruta_ok": boruta_ok,
    }


def prediction_checks() -> dict[str, object]:
    validation = pd.read_csv(PRED_DIR / "validation_predictions.csv")
    test = pd.read_csv(PRED_DIR / "test_predictions.csv")
    required = {"experiment_id", "dataset", "feature_set", "model_name", "split", "row_position", "y_true", "y_pred", "correct"}
    return {
        "validation_rows": len(validation),
        "test_rows": len(test),
        "validation_columns_ok": required.issubset(validation.columns),
        "test_columns_ok": required.issubset(test.columns),
        "validation_experiments": validation["experiment_id"].nunique(),
        "test_experiments": test["experiment_id"].nunique(),
        "ok": required.issubset(validation.columns) and required.issubset(test.columns) and validation["experiment_id"].nunique() == 260 and test["experiment_id"].nunique() == 15,
    }


def stable_config_checks() -> dict[str, object]:
    grid = pd.read_csv(TABLE_DIR / "modeling_experiment_grid.csv")
    validation = pd.read_csv(TABLE_DIR / "modeling_validation_results_all.csv")
    return {
        "models": sorted(grid["model_name"].unique()),
        "baseline_rows": int(grid["feature_set"].eq("all_features").sum()),
        "validation_rows": len(validation),
        "ok": sorted(grid["model_name"].unique()) == ["linear_svm", "logistic_regression", "random_forest", "xgboost"] and int(grid["feature_set"].eq("all_features").sum()) == 20,
    }


def shap_real_checks() -> dict[str, object]:
    source = (ROOT / "src" / "phase6_modeling" / "pipeline.py").read_text(encoding="utf-8")
    return {
        "import_shap": "import shap" in source,
        "tree_explainer": "shap.TreeExplainer" in source,
        "linear_explainer": "shap.LinearExplainer" in source,
        "old_function_absent": "shap_lineal_candidato" not in source,
        "surrogate_absent": "surrogate" not in source.lower(),
        "ok": "import shap" in source
        and "shap.TreeExplainer" in source
        and "shap.LinearExplainer" in source
        and "shap_lineal_candidato" not in source
        and "surrogate" not in source.lower(),
    }


def shap_coverage_checks() -> dict[str, object]:
    shap_values = pd.read_csv(TABLE_DIR / "modeling_shap_values_summary.csv")
    candidates = pd.read_csv(TABLE_DIR / "modeling_test_results_candidates.csv")
    explained = set(shap_values["experiment_id"].unique())
    expected = set(candidates["experiment_id"].unique())
    rf_expected = set(candidates.loc[candidates["model_name"].eq("random_forest"), "experiment_id"].unique())
    rf_explained = set(shap_values.loc[shap_values["model_name"].eq("random_forest"), "experiment_id"].unique())
    required = {"experiment_id", "dataset", "feature_set", "model_name", "feature", "mean_abs_shap", "rank", "n_validation_explained"}
    return {
        "rows": len(shap_values),
        "candidates": len(expected),
        "explained_candidates": len(explained),
        "random_forest_candidates": len(rf_expected),
        "random_forest_explained": len(rf_explained),
        "columns_ok": required.issubset(shap_values.columns),
        "missing_candidates": sorted(expected - explained),
        "missing_random_forest": sorted(rf_expected - rf_explained),
        "ok": required.issubset(shap_values.columns) and expected == explained and rf_expected.issubset(rf_explained),
    }


def determinism_checks() -> dict[str, object]:
    current = pd.read_csv(TABLE_DIR / "modeling_test_results_candidates.csv")
    if not SHAP_REFERENCE.exists():
        return {"reference": str(SHAP_REFERENCE.relative_to(ROOT)), "reference_exists": False, "ok": False}
    previous = pd.read_csv(SHAP_REFERENCE)
    columns = [
        "dataset",
        "candidate_label",
        "feature_set",
        "model_name",
        "validation_macro_f1",
        "test_macro_f1",
        "test_balanced_accuracy",
        "n_features_used",
    ]
    current_cmp = current[columns].sort_values(["dataset", "candidate_label", "feature_set", "model_name"]).reset_index(drop=True)
    previous_cmp = previous[columns].sort_values(["dataset", "candidate_label", "feature_set", "model_name"]).reset_index(drop=True)
    equal = current_cmp.equals(previous_cmp)
    changed = []
    if not equal and len(current_cmp) == len(previous_cmp):
        for idx, (now, old) in enumerate(zip(current_cmp.to_dict(orient="records"), previous_cmp.to_dict(orient="records"))):
            if now != old:
                changed.append({"row": idx, "previous": old, "current": now})
    return {
        "reference": str(SHAP_REFERENCE.relative_to(ROOT)),
        "reference_exists": True,
        "rows_current": len(current_cmp),
        "rows_previous": len(previous_cmp),
        "changed_rows": changed[:10],
        "ok": equal,
    }


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    nb = nbformat.read(NOTEBOOK, as_version=4)
    cells = nb.cells
    obs = observations(cells)
    figures = figure_checks(cells)
    visible = visible_text(cells)
    source = source_checks(cells)
    repeated = repeated_phrases(obs)
    execution_errors = [i for i, c in enumerate(cells, start=1) if c.get("cell_type") == "code" and any(o.get("output_type") == "error" for o in c.get("outputs", []))]
    grid = grid_checks()
    preds = prediction_checks()
    stable = stable_config_checks()
    shap_real = shap_real_checks()
    shap_coverage = shap_coverage_checks()
    determinism = determinism_checks()
    report = {
        "outputs_without_observation": outputs_without_observation(cells),
        "n_observations": len(obs),
        "observation_numeric_ratio": sum(cites_number(o) for o in obs) / max(1, len(obs)),
        "repeated_long_phrases": repeated,
        "section_intros": section_intros(cells),
        "figures": figures,
        "execution_errors": execution_errors,
        "visible_text": visible,
        "source": source,
        "grid": grid,
        "predictions": preds,
        "stable_config": stable,
        "shap_real": shap_real,
        "shap_coverage": shap_coverage,
        "determinism": determinism,
    }
    checks = {
        "a_outputs_have_observation": not report["outputs_without_observation"],
        "b_no_repeated_long_phrases": not repeated,
        "c_numeric_observations_ge_70pct": report["observation_numeric_ratio"] >= 0.70,
        "d_section_intros_ok": all(row["ok"] for row in report["section_intros"]),
        "e_figures_saved_match_displayed": figures["ok"],
        "f_execution_clean": not execution_errors,
        "g_no_big_bang": not source["big_bang_hits"],
        "h_no_internal_audit_visible": not visible["internal_words"],
        "i_no_forbidden_visible_tables": not visible["table_words"],
        "j_src_import_present": source["src_import"],
        "k_no_pipeline_vocabulary": not visible["pipeline_words"],
        "l_grid_baseline_plus_12": grid["all_13_sets"] and grid["roster_ok"],
        "m_boruta_confirmed_sizes": grid["boruta_ok"],
        "n_predictions_by_row": preds["ok"],
        "o_stable_model_config": stable["ok"],
        "p_shap_real_library_used": shap_real["ok"],
        "q_shap_values_for_all_candidates": shap_coverage["ok"],
        "r_test_candidates_deterministic": determinism["ok"],
    }
    report["checks"] = checks

    def default(value):
        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return float(value)
        if isinstance(value, (np.bool_,)):
            return bool(value)
        return str(value)

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=default), encoding="utf-8")
    print(json.dumps({"checks": checks, "report": str(REPORT_PATH.relative_to(ROOT))}, ensure_ascii=False, indent=2, default=default))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
