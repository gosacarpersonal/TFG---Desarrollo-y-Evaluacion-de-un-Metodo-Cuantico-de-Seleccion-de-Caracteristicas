from __future__ import annotations

import ast
import html
import json
import re
from collections import Counter
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "fase4.ipynb"
FIGURES = ROOT / "results" / "figures" / "04_split_audit"
PHASE3_TABLES = ROOT / "results" / "tables" / "03_postprocessing_audit"

DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]

PHASE3_REQUIRED_TABLES = [
    "fase3_resumen_metricas_split.csv",
    "fase3_target_resumen.csv",
    "fase3_dimensionalidad_final.csv",
    "fase3_correlaciones_resumen.csv",
]

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
    "audit",
    "completitud",
    "control tecnico de evidencias",
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
    "apto_con_cautela",
    "schema",
    "warnings",
]

BIG_BANG_PATTERNS = [
    r"\bforce\s*=\s*True\b",
    r"\brun_[A-Za-z0-9_]*\s*\(",
    r"\bresultados\s*\[\s*[\"'][^\"']+\.csv[\"']\s*\]",
]


def cell_source(cell) -> str:
    return cell.get("source", "") or ""


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


def output_text(cell) -> str:
    chunks: list[str] = []
    for output in cell.get("outputs", []):
        if output.get("output_type") == "stream":
            chunks.append(output.get("text", ""))
        if output.get("output_type") == "error":
            chunks.extend(output.get("traceback", []))
        data = output.get("data", {})
        for value in data.values():
            if isinstance(value, str):
                chunks.append(value)
            elif isinstance(value, list):
                chunks.append("".join(map(str, value)))
    return "\n".join(chunks)


def markdown_text(cell) -> str:
    return re.sub(r"\s+", " ", cell_source(cell).strip())


def is_observation(cell) -> bool:
    if cell.get("cell_type") != "markdown":
        return False
    text = markdown_text(cell)
    return bool(text) and not text.startswith("#")


def observation_cells(cells) -> list[str]:
    observations = []
    for index, cell in enumerate(cells):
        if cell.get("cell_type") != "markdown":
            continue
        previous = cells[index - 1] if index > 0 else None
        if previous and has_visible_output(previous) and is_observation(cell):
            observations.append(markdown_text(cell))
    return observations


def outputs_without_observation(cells) -> list[int]:
    bad = []
    for index, cell in enumerate(cells):
        if not has_visible_output(cell):
            continue
        if "display(Markdown(" in cell_source(cell):
            continue
        next_cell = cells[index + 1] if index + 1 < len(cells) else None
        if not next_cell or not is_observation(next_cell):
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


def section_intro_checks(cells) -> list[dict[str, object]]:
    rows = []
    for cell in cells:
        if cell.get("cell_type") != "markdown":
            continue
        text = cell_source(cell).strip()
        match = re.match(r"^## (4\.\d+) ", text)
        if not match:
            continue
        parts = text.split("\n\n", 1)
        intro = parts[1].strip() if len(parts) > 1 else ""
        word_count = len(re.findall(r"\w+", intro))
        mentions_method = bool(
            re.search(
                r"target|split|estratifica|índice|indice|solape|drift|PSI|KS|Wasserstein|PCA|AUC|NMI|leakage|proxy|validación|auditoría|QFS|PAPER_QFS|umbral|partición",
                intro,
                flags=re.IGNORECASE,
            )
        )
        rows.append(
            {
                "section": match.group(1),
                "word_count": word_count,
                "mentions_method": mentions_method,
                "ok": word_count > 20 and mentions_method,
            }
        )
    return rows


def execution_errors(cells) -> list[int]:
    rows = []
    for index, cell in enumerate(cells, start=1):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                rows.append(index)
    return rows


def saved_pngs() -> set[str]:
    return {str(path.relative_to(ROOT)) for path in FIGURES.rglob("*.png")}


def displayed_pngs(cells) -> set[str]:
    displayed = set()
    source = "\n".join(cell_source(cell) for cell in cells if cell.get("cell_type") == "code")
    literal_pattern = re.compile(r"guardar_figura\([^,]+,\s*[f]?[\"']([^\"']+\.png)[\"']\)")
    for name in literal_pattern.findall(source):
        if "{" not in name:
            displayed.add(f"results/figures/04_split_audit/{name}")
    for pattern in [
        "fase4_target_{nombre_dataset}.png",
        "fase4_drift_{nombre_dataset}.png",
        "fase4_pca_{nombre_dataset}.png",
    ]:
        if pattern in source:
            prefix, suffix = pattern.split("{nombre_dataset}")
            for dataset in DATASETS:
                displayed.add(f"results/figures/04_split_audit/{prefix}{dataset}{suffix}")
    return displayed


def pngs_without_pdf(pngs: set[str]) -> list[str]:
    missing = []
    for rel_path in sorted(pngs):
        if not (ROOT / rel_path).with_suffix(".pdf").exists():
            missing.append(rel_path)
    return missing


def forbidden_pipeline_hits(cells) -> dict[str, list[int]]:
    hits = {word: [] for word in PIPELINE_WORDS}
    for index, cell in enumerate(cells, start=1):
        visible = cell_source(cell) if cell.get("cell_type") == "markdown" else output_text(cell)
        for word in PIPELINE_WORDS:
            if re.search(re.escape(word), visible, flags=re.IGNORECASE):
                hits[word].append(index)
    return {word: rows for word, rows in hits.items() if rows}


def internal_audit_hits(cells) -> dict[str, list[int]]:
    hits = {word: [] for word in INTERNAL_AUDIT_WORDS}
    for index, cell in enumerate(cells, start=1):
        source = cell_source(cell)
        for word in INTERNAL_AUDIT_WORDS:
            if word == "audit":
                pattern = r"(?<!\w)audit(?!\w)"
            else:
                pattern = re.escape(word)
            if re.search(pattern, source, flags=re.IGNORECASE):
                hits[word].append(index)
    return {word: rows for word, rows in hits.items() if rows}


def big_bang_hits(cells) -> dict[str, list[int]]:
    hits = {pattern: [] for pattern in BIG_BANG_PATTERNS}
    for index, cell in enumerate(cells, start=1):
        if cell.get("cell_type") != "code":
            continue
        source = cell_source(cell)
        for pattern in BIG_BANG_PATTERNS:
            if re.search(pattern, source):
                hits[pattern].append(index)
    return {pattern: rows for pattern, rows in hits.items() if rows}


def strip_html_tags(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


def displayed_table_forbidden_hits(cells) -> dict[str, list[int]]:
    hits = {word: [] for word in TABLE_FORBIDDEN_WORDS}
    for index, cell in enumerate(cells, start=1):
        for output in cell.get("outputs", []):
            html_text = output.get("data", {}).get("text/html", "")
            if isinstance(html_text, list):
                html_text = "".join(html_text)
            if "<table" not in html_text:
                continue
            table_text = strip_html_tags(html_text)
            for word in TABLE_FORBIDDEN_WORDS:
                if re.search(rf"(?<!\w){re.escape(word)}(?!\w)", table_text, flags=re.IGNORECASE):
                    hits[word].append(index)
    return {word: rows for word, rows in hits.items() if rows}


def imported_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def top_level_calls(node: ast.AST) -> list[str]:
    calls = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, inner_node):  # noqa: N802
            return

        def visit_Lambda(self, inner_node):  # noqa: N802
            return

        def visit_Call(self, inner_node):  # noqa: N802
            if isinstance(inner_node.func, ast.Name):
                calls.append(inner_node.func.id)
            self.generic_visit(inner_node)

    Visitor().visit(node)
    return calls


def assigned_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, ast.For):
            targets = [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                names.update(element.id for element in target.elts if isinstance(element, ast.Name))
    return names


def function_order_issues(cells) -> list[dict[str, object]]:
    allowed = {
        "abs",
        "all",
        "any",
        "bool",
        "dict",
        "display",
        "enumerate",
        "FileNotFoundError",
        "float",
        "int",
        "isinstance",
        "KeyError",
        "len",
        "list",
        "map",
        "max",
        "min",
        "print",
        "range",
        "reversed",
        "round",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "ValueError",
        "zip",
    }
    defined = set(allowed)
    issues = []
    for index, cell in enumerate(cells, start=1):
        if cell.get("cell_type") != "code":
            continue
        try:
            tree = ast.parse(cell_source(cell))
        except SyntaxError as exc:
            issues.append({"cell": index, "name": "syntax_error", "detail": str(exc)})
            continue
        defined.update(imported_names(tree))
        defined.update(assigned_names(tree))
        defined.update(node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
        for call_name in top_level_calls(tree):
            if call_name not in defined:
                issues.append({"cell": index, "name": call_name, "detail": "call before visible definition/import"})
    return issues


def phase3_preconditions() -> list[str]:
    return [name for name in PHASE3_REQUIRED_TABLES if not (PHASE3_TABLES / name).exists()]


def main() -> None:
    nb = nbformat.read(NOTEBOOK, as_version=4)
    cells = nb.cells
    observations = observation_cells(cells)
    repeated = repeated_long_phrases(observations)
    numeric_count = sum(cites_number(text) for text in observations)
    section_rows = section_intro_checks(cells)
    saved = saved_pngs()
    displayed = displayed_pngs(cells)
    missing_display = sorted(saved - displayed)
    missing_file = sorted(displayed - saved)
    missing_pdf = pngs_without_pdf(saved)
    errors = execution_errors(cells)

    report = {
        "phase3_missing_tables": phase3_preconditions(),
        "a_outputs_without_observation": outputs_without_observation(cells),
        "b_repeated_phrases_ge_3": repeated,
        "c_observations_total": len(observations),
        "c_observations_with_numbers": numeric_count,
        "c_observations_numeric_ratio": numeric_count / len(observations) if observations else 0,
        "d_section_intro_failures": [row for row in section_rows if not row["ok"]],
        "e_saved_png_count": len(saved),
        "e_displayed_png_count": len(displayed),
        "e_saved_not_displayed": missing_display,
        "e_displayed_missing_file": missing_file,
        "e_png_without_pdf": missing_pdf,
        "f_execution_error_cells": errors,
        "g_big_bang_hits": big_bang_hits(cells),
        "h_internal_audit_hits": internal_audit_hits(cells),
        "i_displayed_table_forbidden_hits": displayed_table_forbidden_hits(cells),
        "j_function_order_issues": function_order_issues(cells),
        "k_pipeline_vocabulary_hits": forbidden_pipeline_hits(cells),
    }
    report["checks"] = {
        "phase3_preconditions_available": not report["phase3_missing_tables"],
        "a_observations_after_visible_outputs": not report["a_outputs_without_observation"],
        "b_no_repeated_observation_phrases": not repeated,
        "c_at_least_70_percent_observations_with_numbers": report["c_observations_numeric_ratio"] >= 0.70,
        "d_section_intros_have_context_and_method": not report["d_section_intro_failures"],
        "e_figures_saved_displayed_and_pdf_paired": not missing_display and not missing_file and not missing_pdf,
        "f_notebook_executed_without_errors": not errors,
        "g_no_big_bang_calls": not report["g_big_bang_hits"],
        "h_no_internal_check_cells": not report["h_internal_audit_hits"],
        "i_no_forbidden_displayed_table_language": not report["i_displayed_table_forbidden_hits"],
        "j_functions_defined_or_imported_before_use": not report["j_function_order_issues"],
        "k_no_pipeline_vocabulary_in_markdown_or_outputs": not report["k_pipeline_vocabulary_hits"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not all(report["checks"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
