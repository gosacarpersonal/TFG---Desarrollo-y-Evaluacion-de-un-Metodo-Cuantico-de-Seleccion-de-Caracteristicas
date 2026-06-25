from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "fase5.ipynb"
TABLE_DIR = ROOT / "results" / "tables" / "05_feature_selection"
FIGURE_DIR = ROOT / "results" / "figures" / "05_feature_selection"
LOG_DIR = ROOT / "results" / "logs" / "05_feature_selection"
REPORT_PATH = LOG_DIR / "fase5_verification_report.json"

DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]
ROSTER = {
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
UNAFFECTED_METHODS = ["variance", "f_classif", "l1_logistic", "random_forest", "linear_svm"]

PIPELINE_WORDS = [
    "artefacto",
    "artefactos",
    "handoff",
    "warnings heredados",
    "fuente de verdad",
    "pipeline",
    "filas en el artefacto",
]
INTERNAL_AUDIT_WORDS = [
    "nbformat",
    "checklist",
    "inventario",
    "auto-auditoría",
    "auto-auditoria",
    "completitud",
    "control técnico de evidencias",
]
TABLE_FORBIDDEN_WORDS = [
    "criterio",
    "evidence",
    "reason",
    "risk",
    "mitigation",
    "status",
    "check",
    "cumple",
    "estado",
    "ok",
    "motivo_bloqueo",
    "schema",
    "warnings",
]
BIG_BANG_PATTERNS = [
    r"\bforce\s*=\s*True\b",
    r"\brun_[A-Za-z0-9_]*\s*\(",
    r"\bresultados\s*\[\s*[\"'][^\"']+\.csv[\"']\s*\]",
    r"\betapa_[A-Za-z0-9_]*\s*\(",
]


def cell_source(cell) -> str:
    return cell.get("source", "") or ""


def output_text(cell) -> str:
    chunks: list[str] = []
    for output in cell.get("outputs", []):
        if output.get("output_type") == "stream":
            chunks.append(output.get("text", ""))
        if output.get("output_type") == "error":
            chunks.extend(output.get("traceback", []))
        data = output.get("data", {})
        for key, value in data.items():
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
        data = output.get("data", {})
        if any(key in data for key in ["text/plain", "text/html", "image/png", "image/jpeg"]):
            return True
    return False


def is_observation(cell) -> bool:
    if cell.get("cell_type") != "markdown":
        return False
    text = re.sub(r"\s+", " ", cell_source(cell).strip())
    return bool(text) and not text.startswith("#")


def observations_after_outputs(cells) -> list[str]:
    observations = []
    for index, cell in enumerate(cells[:-1]):
        if has_visible_output(cell) and is_observation(cells[index + 1]):
            observations.append(re.sub(r"\s+", " ", cell_source(cells[index + 1]).strip()))
    return observations


def outputs_without_observation(cells) -> list[int]:
    bad = []
    for index, cell in enumerate(cells[:-1]):
        if has_visible_output(cell) and not is_observation(cells[index + 1]):
            bad.append(index + 1)
    return bad


def repeated_long_phrases(observations: list[str]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for text in observations:
        words = re.findall(r"[\wÁÉÍÓÚÜÑáéíóúüñ`_.=-]+", text.lower())
        seen = set()
        for size in range(7, min(13, len(words)) + 1):
            for start in range(0, len(words) - size + 1):
                seen.add(" ".join(words[start : start + size]))
        counts.update(seen)
    return {phrase: count for phrase, count in counts.items() if count >= 3}


def cites_number(text: str) -> bool:
    return bool(re.search(r"(?<![\w])[-+]?\d+(?:[.,]\d+)?", text))


def section_intro_rows(cells) -> list[dict[str, object]]:
    rows = []
    technical = re.compile(
        r"train|target|QFS|MI|información mutua|Jaccard|permut|redundancia|Boruta|RFE|k|selector|matriz|figura|CSV",
        flags=re.IGNORECASE,
    )
    for cell in cells:
        if cell.get("cell_type") != "markdown":
            continue
        text = cell_source(cell).strip()
        match = re.match(r"^## (5\.\d+) ", text)
        if not match:
            continue
        parts = text.split("\n\n", 1)
        intro = parts[1] if len(parts) > 1 else ""
        word_count = len(re.findall(r"\w+", intro))
        rows.append(
            {
                "section": match.group(1),
                "word_count": word_count,
                "mentions_criterion": bool(technical.search(intro)),
                "ok": word_count > 25 and bool(technical.search(intro)),
            }
        )
    return rows


def figure_checks(cells) -> dict[str, object]:
    pngs = {path.relative_to(ROOT).as_posix() for path in FIGURE_DIR.rglob("*.png")}
    pdfs = {path.relative_to(ROOT).with_suffix(".png").as_posix() for path in FIGURE_DIR.rglob("*.pdf")}
    image_outputs = sum(
        1
        for cell in cells
        if cell.get("cell_type") == "code"
        for output in cell.get("outputs", [])
        if "image/png" in output.get("data", {})
    )
    return {
        "saved_png": len(pngs),
        "saved_pdf": len(pdfs),
        "displayed_images": image_outputs,
        "png_without_pdf": sorted(pngs - pdfs),
        "pdf_without_png": sorted(pdfs - pngs),
        "ok": len(pngs) == len(pdfs) == image_outputs and not (pngs - pdfs) and not (pdfs - pngs),
    }


def latest_previous_tables() -> Path | None:
    candidates = sorted(LOG_DIR.glob("previous_tables_*"))
    return candidates[-1] if candidates else None


def diff_unaffected_methods() -> dict[str, object]:
    previous_dir = latest_previous_tables()
    current_path = TABLE_DIR / "fs_all_rankings.csv"
    if previous_dir is None or not (previous_dir / "fs_all_rankings.csv").exists() or not current_path.exists():
        return {"available": False, "ok": False, "reason": "no hay copia previa comparable"}
    previous = pd.read_csv(previous_dir / "fs_all_rankings.csv")
    current = pd.read_csv(current_path)
    columns = ["dataset", "method", "seed", "k", "feature", "rank", "score", "selected", "status"]
    rows = []
    ok = True
    for method in UNAFFECTED_METHODS:
        a = previous[previous["method"].eq(method)][columns].sort_values(columns[:-2]).reset_index(drop=True)
        b = current[current["method"].eq(method)][columns].sort_values(columns[:-2]).reset_index(drop=True)
        same_shape = a.shape == b.shape
        same_values = same_shape and a.equals(b)
        ok = ok and same_values
        rows.append({"method": method, "previous_rows": len(a), "current_rows": len(b), "identical": bool(same_values)})
    return {"available": True, "ok": bool(ok), "previous_dir": str(previous_dir.relative_to(ROOT)), "methods": rows}


def roster_checks() -> dict[str, object]:
    rankings = pd.read_csv(TABLE_DIR / "fs_all_rankings.csv")
    boruta = pd.read_csv(TABLE_DIR / "fs_boruta_confirmed_sets.csv")
    methods_by_dataset = rankings.groupby("dataset")["method"].nunique().to_dict()
    natural_rows = boruta[["dataset", "method", "k_confirmed", "n_features"]].to_dict(orient="records")
    return {
        "methods": sorted(rankings["method"].unique()),
        "methods_by_dataset": methods_by_dataset,
        "all_12_present": set(rankings["method"].unique()) == ROSTER and all(methods_by_dataset.get(dataset) == 12 for dataset in DATASETS),
        "boruta_natural": natural_rows,
        "boruta_ok": len(boruta) == len(DATASETS) and boruta["k_confirmed"].between(1, boruta["n_features"]).all(),
    }


def visible_text_checks(cells) -> dict[str, object]:
    markdown = "\n".join(cell_source(cell) for cell in cells if cell.get("cell_type") == "markdown")
    outputs = "\n".join(output_text(cell) for cell in cells if cell.get("cell_type") == "code")
    visible = f"{markdown}\n{outputs}".lower()
    return {
        "pipeline_words": [word for word in PIPELINE_WORDS if word in visible],
        "internal_audit_words": [word for word in INTERNAL_AUDIT_WORDS if word in visible],
        "table_forbidden_words": [word for word in TABLE_FORBIDDEN_WORDS if re.search(rf"\b{re.escape(word)}\b", outputs.lower())],
    }


def source_checks(cells) -> dict[str, object]:
    source = "\n".join(cell_source(cell) for cell in cells)
    return {
        "big_bang_hits": [pattern for pattern in BIG_BANG_PATTERNS if re.search(pattern, source)],
        "imports_fine_grain_src": "import fase5_feature_selection as fs" in source,
    }


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    nb = nbformat.read(NOTEBOOK, as_version=4)
    cells = nb.cells
    observations = observations_after_outputs(cells)
    repeated = repeated_long_phrases(observations)
    intros = section_intro_rows(cells)
    figures = figure_checks(cells)
    visible = visible_text_checks(cells)
    source = source_checks(cells)
    diff = diff_unaffected_methods()
    roster = roster_checks()
    execution_errors = [
        index
        for index, cell in enumerate(cells, start=1)
        if cell.get("cell_type") == "code" and any(output.get("output_type") == "error" for output in cell.get("outputs", []))
    ]
    report = {
        "outputs_without_observation": outputs_without_observation(cells),
        "n_observations": len(observations),
        "observation_numeric_ratio": sum(cites_number(obs) for obs in observations) / max(1, len(observations)),
        "repeated_long_phrases": repeated,
        "section_intros": intros,
        "figures": figures,
        "execution_errors": execution_errors,
        "source": source,
        "visible_text": visible,
        "diff_unaffected_methods": diff,
        "roster": roster,
    }
    checks = {
        "a_outputs_have_observation": not report["outputs_without_observation"],
        "b_no_repeated_long_phrases": not repeated,
        "c_numeric_observations_ge_70pct": report["observation_numeric_ratio"] >= 0.70,
        "d_section_intros_ok": all(row["ok"] for row in intros),
        "e_figures_saved_match_displayed": figures["ok"],
        "f_execution_clean": not execution_errors,
        "g_no_big_bang": not source["big_bang_hits"],
        "h_no_internal_audit_visible": not visible["internal_audit_words"],
        "i_no_forbidden_visible_tables": not visible["table_forbidden_words"],
        "j_src_import_present": source["imports_fine_grain_src"],
        "k_no_pipeline_vocabulary": not visible["pipeline_words"],
        "l_unaffected_methods_identical": diff["ok"],
        "m_roster_and_boruta_ok": roster["all_12_present"] and roster["boruta_ok"],
    }
    report["checks"] = checks
    def json_default(value):
        if isinstance(value, (np.bool_,)):
            return bool(value)
        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return float(value)
        return str(value)

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    print(json.dumps({"checks": checks, "report": str(REPORT_PATH.relative_to(ROOT))}, ensure_ascii=False, indent=2, default=json_default))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
