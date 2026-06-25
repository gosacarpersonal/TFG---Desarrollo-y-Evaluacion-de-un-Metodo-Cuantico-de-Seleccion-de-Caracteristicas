"""Lecturas post-output y validaciones del notebook de Fase 6."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]

TONO = {
    "breast_cancer_wisconsin": "En la lectura clínica",
    "customer_churn": "En churn",
    "madelon": "En Madelon",
    "olive_oil_3class": "En Olive Oil de tres clases",
    "olive_oil_9class": "En Olive Oil de nueve clases",
}


def filas_dataset(tabla: pd.DataFrame, dataset: str) -> pd.DataFrame:
    if tabla is None or tabla.empty or "dataset" not in tabla.columns:
        return pd.DataFrame()
    return tabla[tabla["dataset"].eq(dataset)].copy()


def fmt(valor: Any, decimales: int = 3) -> str:
    if pd.isna(valor):
        return "no disponible"
    if isinstance(valor, float):
        return f"{valor:.{decimales}f}"
    return str(valor)


def top_features(tabla: pd.DataFrame, max_items: int = 5) -> str:
    if tabla.empty or "feature" not in tabla.columns:
        return "sin variables destacadas"
    valores = tabla.sort_values("mean_abs_shap", ascending=False)["feature"].head(max_items).tolist()
    return ", ".join(map(str, valores))


def lectura_entrada(input_audit: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(input_audit, dataset)
    if local.empty:
        return "No hay auditoría de entrada para este dataset."
    row = local.iloc[0]
    return (
        f"{dataset}: estado `{row.status}`; train={int(row.n_train)}, validation={int(row.n_validation)}, "
        f"test={int(row.n_test)}, variables={int(row.n_features_all)}. Principales={int(row.principal_para_modelado)}, "
        f"auxiliares={int(row.auxiliar_exploratorio)}, incidencias={int(row.incidencias_abiertas)}; "
        f"{TONO.get(dataset, dataset).lower()} queda apto para modelado controlado."
    )


def lectura_protocolo(protocol: pd.DataFrame, strategy: pd.DataFrame) -> str:
    return (
        f"El bloque común fija {len(protocol)} reglas de evaluación y {len(strategy)} decisiones estratégicas: "
        "validation ordena configuraciones, test queda reservado para candidatos cerrados y SHAP cubre selector-k "
        "sin reabrir la selección."
    )


def lectura_protocolo_dataset(protocol: pd.DataFrame, strategy: pd.DataFrame, grid: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(grid, dataset)
    if local.empty:
        return f"{TONO.get(dataset, dataset)} no dispone de parrilla local tras aplicar el protocolo común."
    modelos = ", ".join(sorted(local["model_name"].unique()))
    values = (len(protocol), len(strategy), len(local), local.feature_set.nunique(), local.model_name.nunique(), modelos)
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer aplica {0} reglas y {1} decisiones; la parrilla clínica suma {2} cruces, {3} conjuntos y {4} modelos: {5}.",
        "customer_churn": "Customer Churn usa {2} entrenamientos bajo {0} reglas; {3} feature sets y {4} clasificadores sostienen una lectura operativa con {1} decisiones comunes ({5}).",
        "madelon": "Madelon conserva {3} conjuntos frente a distractores; el protocolo aporta {0} reglas, {1} decisiones y {2} filas con modelos {5}.",
        "olive_oil_3class": "Olive Oil 3 clases queda como control separable: {2} filas, {4} modelos, {3} conjuntos, {0} reglas y {1} decisiones.",
        "olive_oil_9class": "Olive Oil 9 clases exige cautela multiclase; se revisan {2} experimentos, {3} conjuntos, {4} modelos, {0} reglas y {1} decisiones ({5}).",
    }
    return templates.get(dataset, "{2} experimentos locales.").format(*values)


def lectura_metricas(validation: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(validation, dataset)
    if local.empty:
        return "No hay resultados de validation para inferir métricas."
    best = local.sort_values(["macro_f1", "balanced_accuracy"], ascending=False).iloc[0]
    return (
        f"{dataset}: mejor validation `{best.feature_set}` + `{best.model_name}`; Macro F1={fmt(best.macro_f1)}, "
        f"Balanced Accuracy={fmt(best.balanced_accuracy)}, accuracy={fmt(best.accuracy)}. "
        f"{TONO.get(dataset, dataset)} usa Macro F1 como lectura principal."
    )


def lectura_preparacion(grid: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(grid, dataset)
    if local.empty:
        return "No hay parrilla experimental para este dataset."
    values = (len(local), local.feature_set.nunique(), int(local.k.min()), int(local.k.max()), local.model_name.nunique())
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer prepara {0} filas: {1} conjuntos, k entre {2} y {3}, con {4} modelos auditables.",
        "customer_churn": "Customer Churn deja {0} configuraciones; {4} modelos recorren {1} conjuntos y k va de {2} a {3}.",
        "madelon": "Madelon combina {1} subconjuntos con {4} clasificadores; aparecen {0} filas y el rango k={2}-{3}.",
        "olive_oil_3class": "Olive Oil 3 clases mantiene {0} cruces, {1} feature sets, k_min={2}, k_max={3} y {4} modelos.",
        "olive_oil_9class": "Olive Oil 9 clases replica {0} pruebas locales; {1} conjuntos y {4} modelos cubren k desde {2} hasta {3}.",
    }
    return templates.get(dataset, "{0} filas preparadas.").format(*values)


def lectura_modelos(grid: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(grid, dataset)
    modelos = sorted(local["model_name"].unique()) if not local.empty else []
    local = filas_dataset(grid, dataset)
    total = len(local)
    values = (len(modelos), ", ".join(modelos), local.feature_set.nunique() if not local.empty else 0, total)
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer usa {0} modelos ({1}) sobre {2} conjuntos; las {3} configuraciones conservan hiperparámetros cerrados.",
        "customer_churn": "Customer Churn compara {3} filas: {2} conjuntos multiplicados por {0} modelos, listados como {1}.",
        "madelon": "Madelon enfrenta ruido con {0} clasificadores y {2} feature sets; el total visible es {3}.",
        "olive_oil_3class": "Olive Oil 3 clases cruza {2} conjuntos por {0} modelos; {3} resultados permiten comprobar el control positivo.",
        "olive_oil_9class": "Olive Oil 9 clases mantiene {3} configuraciones; los modelos son {1} y no se reajustan con test.",
    }
    return templates.get(dataset, "{3} configuraciones.").format(*values)


def lectura_baseline(validation: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(validation, dataset)
    base = local[local["feature_set"].eq("all_features")]
    if base.empty:
        return "No hay baseline all_features para este dataset."
    best = base.sort_values(["macro_f1", "balanced_accuracy"], ascending=False).iloc[0]
    worst = base.sort_values("macro_f1").iloc[0]
    values = (best.model_name, fmt(best.macro_f1), fmt(best.balanced_accuracy), int(best.n_features_used), fmt(worst.macro_f1))
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer toma `{0}` como baseline superior: Macro F1={1}, BA={2}, variables={3}; mínimo baseline={4}.",
        "customer_churn": "Customer Churn sitúa el baseline ganador en `{0}` con {1} de Macro F1 y {2} de BA; usa {3} variables, peor={4}.",
        "madelon": "Madelon parte de `{0}` como referencia completa: F1={1}, BA={2}, p={3}; el baseline inferior marca {4}.",
        "olive_oil_3class": "Olive Oil 3 clases alcanza baseline `{0}` con Macro F1 {1}; BA {2}; variables {3}; suelo {4}.",
        "olive_oil_9class": "Olive Oil 9 clases fija `{0}` como referencia: {1} Macro F1, {2} BA, {3} variables y mínimo {4}.",
    }
    return templates.get(dataset, "Baseline disponible.").format(*values)


def lectura_seleccion(validation: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(validation, dataset)
    selected = local[~local["feature_set"].eq("all_features")]
    if selected.empty:
        return "No hay experimentos con variables seleccionadas para este dataset."
    best = selected.sort_values(["macro_f1", "balanced_accuracy"], ascending=False).iloc[0]
    delta = best.delta_macro_f1_vs_same_model_baseline
    reduced = int(best.n_features_used)
    return (
        f"{TONO.get(dataset, dataset)} encuentra su subconjunto más fuerte en `{best.feature_set}` con "
        f"`{best.model_name}`: Macro F1={fmt(best.macro_f1)}, delta frente a su baseline {fmt(delta)} "
        f"y {reduced} variables usadas."
    )


def lectura_validation(validation: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(validation, dataset)
    if local.empty:
        return "No hay resultados de validation."
    best = local.sort_values(["macro_f1", "balanced_accuracy", "fit_seconds"], ascending=[False, False, True]).iloc[0]
    worst = local.sort_values("macro_f1").iloc[0]
    spread = best.macro_f1 - worst.macro_f1
    values = (len(local), best.feature_set, best.model_name, fmt(best.macro_f1), worst.feature_set, worst.model_name, fmt(worst.macro_f1), fmt(spread))
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer ordena {0} filas; líder `{1}`/`{2}`={3}, cola `{4}`/`{5}`={6}, rango={7}.",
        "customer_churn": "Customer Churn muestra una banda de {7}: mejor `{1}` con `{2}` llega a {3}; peor `{4}` con `{5}` queda en {6}.",
        "madelon": "Madelon expone {0} configuraciones y amplitud {7}; arriba `{1}`/`{2}` ({3}), abajo `{4}`/`{5}` ({6}).",
        "olive_oil_3class": "Olive Oil 3 clases conserva {0} filas validation; techo {3} en `{1}`/`{2}` y suelo {6} en `{4}`/`{5}`.",
        "olive_oil_9class": "Olive Oil 9 clases reparte {0} pruebas; `{1}`/`{2}` domina con {3}, `{4}`/`{5}` baja a {6}, distancia {7}.",
    }
    return templates.get(dataset, "Validation ordenada.").format(*values)


def lectura_candidatos(candidates: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(candidates, dataset)
    if local.empty:
        return "No hay candidatos fijados para test."
    best = local.sort_values(["macro_f1", "balanced_accuracy"], ascending=False).iloc[0]
    return (
        f"{dataset}: candidatos_test={len(local)}; líder_validation=`{best.feature_set}`/`{best.model_name}`; "
        f"Macro F1={fmt(best.macro_f1)}. Motivos: {', '.join(local['candidate_reason'].astype(str).tolist())}."
    )


def lectura_test(test: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(test, dataset)
    if local.empty:
        return "No hay evaluación test para este dataset."
    best = local.sort_values(["test_macro_f1", "test_balanced_accuracy"], ascending=False).iloc[0]
    base = local[local["feature_set"].eq("all_features")]
    delta = best.test_macro_f1 - base.iloc[0].test_macro_f1 if not base.empty else pd.NA
    values = (best.feature_set, best.model_name, fmt(best.test_macro_f1), fmt(best.test_balanced_accuracy), fmt(delta))
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer test: `{0}`/`{1}` lidera, Macro F1={2}, BA={3}, delta baseline={4}.",
        "customer_churn": "Customer Churn confirma `{0}` con `{1}`; F1 test {2}, BA {3}, diferencia completa {4}.",
        "madelon": "Madelon cambia en test hacia `{0}`/`{1}`: Macro F1 {2}, Balanced Accuracy {3}, delta {4}.",
        "olive_oil_3class": "Olive Oil 3 clases mantiene `{0}` y `{1}` con F1 {2}; BA={3}; margen frente a baseline={4}.",
        "olive_oil_9class": "Olive Oil 9 clases deja como mejor `{0}`/`{1}`: F1={2}, BA={3}, delta={4}.",
    }
    return templates.get(dataset, "Test calculado.").format(*values)


def lectura_intervalos(intervals: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(intervals, dataset)
    macro = local[local["metric"].eq("macro_f1")]
    if macro.empty:
        return "No hay intervalos de Macro F1 para este dataset."
    widest = macro.assign(width=macro["ci_high"] - macro["ci_low"]).sort_values("width", ascending=False).iloc[0]
    narrow = macro.assign(width=macro["ci_high"] - macro["ci_low"]).sort_values("width").iloc[0]
    values = (int(widest.n_bootstrap), widest.feature_set, fmt(widest.width), narrow.feature_set, fmt(narrow.width))
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer bootstrap={0}: intervalo mayor `{1}` amplitud {2}; menor `{3}` amplitud {4}.",
        "customer_churn": "Customer Churn usa {0} remuestreos; `{1}` abre {2} y `{3}` cierra {4}.",
        "madelon": "Madelon necesita cautela: {0} bootstraps, ancho máximo {2} en `{1}`, mínimo {4} en `{3}`.",
        "olive_oil_3class": "Olive Oil 3 clases reporta {0} remuestreos; IC amplio `{1}`={2}; IC corto `{3}`={4}.",
        "olive_oil_9class": "Olive Oil 9 clases estima incertidumbre con {0}; rango mayor {2} (`{1}`) y menor {4} (`{3}`).",
    }
    return templates.get(dataset, "Bootstrap calculado.").format(*values)


def lectura_comparaciones(pairwise: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(pairwise, dataset)
    if local.empty:
        return "No hay comparación pareada frente a baseline para este dataset."
    best = local.sort_values("difference_candidate_minus_baseline", ascending=False).iloc[0]
    values = (len(local), fmt(best.difference_candidate_minus_baseline), fmt(best.ci_low), fmt(best.ci_high), fmt(best.paired_correctness_permutation_pvalue))
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer pareado: n={0}, diff_max={1}, IC {2}-{3}, p={4}.",
        "customer_churn": "Customer Churn compara {0} candidatos contra baseline; diferencia superior {1}, intervalo {2}/{3}, p {4}.",
        "madelon": "Madelon ofrece {0} contrastes; el salto máximo es {1} con límites {2} y {3}, p={4}.",
        "olive_oil_3class": "Olive Oil 3 clases pareado: {0} filas resumen, diff {1}, IC [{2}, {3}], p {4}.",
        "olive_oil_9class": "Olive Oil 9 clases registra {0} contrastes; máximo {1}, extremos {2}-{3}, p={4}.",
    }
    return templates.get(dataset, "Comparación pareada lista.").format(*values)


def lectura_permutaciones(permutations: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(permutations, dataset)
    if local.empty:
        return "No hay permutation test para este dataset."
    max_p = local["p_value"].max()
    min_margin = (local["observed_score"] - local["null_p95"]).min()
    values = (len(local), fmt(max_p), fmt(min_margin), int(local.n_permutations.iloc[0]))
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer permutation: candidatos={0}, p_max={1}, margen_min={2}, perm={3}.",
        "customer_churn": "Customer Churn contrasta {0} predicciones finales; p máximo {1}, separación mínima {2}, {3} permutaciones.",
        "madelon": "Madelon frente a nula: {0} candidatos, p_max {1}, margen {2}, permutaciones {3}.",
        "olive_oil_3class": "Olive Oil 3 clases obtiene p_max={1} en {0} candidatos; margen_min={2}; perm={3}.",
        "olive_oil_9class": "Olive Oil 9 clases valida {0} candidatos con {3} permutaciones, p_max {1} y margen {2}.",
    }
    return templates.get(dataset, "Permutation test disponible.").format(*values)


def lectura_shap(shap_top: pd.DataFrame, shap_coverage: pd.DataFrame, dataset: str) -> str:
    cov = filas_dataset(shap_coverage, dataset)
    top = filas_dataset(shap_top, dataset)
    if cov.empty:
        return "No hay cobertura SHAP para este dataset."
    ok = int(cov["status"].eq("ok").sum())
    recurrent = top.groupby("feature", as_index=False)["mean_abs_shap"].mean() if not top.empty else top
    max_value = recurrent["mean_abs_shap"].max() if not recurrent.empty else pd.NA
    values = (ok, len(cov), top_features(recurrent), fmt(max_value))
    templates = {
        "breast_cancer_wisconsin": "Breast Cancer SHAP {0}/{1}; top={2}; valor medio absoluto máximo {3}, coherente con señal morfológica.",
        "customer_churn": "Customer Churn SHAP cubre {0} de {1}; variables dominantes {2}; máximo {3} en escala explicativa.",
        "madelon": "Madelon SHAP_ok={0}/{1}; destacan {2}; max_mean_abs={3}, útil para separar señal de distractores.",
        "olive_oil_3class": "Olive Oil 3 clases explica {0}/{1} combinaciones; {2} sostienen los subconjuntos; SHAP máximo {3}.",
        "olive_oil_9class": "Olive Oil 9 clases completa {0}/{1}; top variables {2}; pico SHAP medio absoluto {3}.",
    }
    return templates.get(dataset, "SHAP calculado.").format(*values)


def lectura_coste(cost: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(cost, dataset)
    if local.empty:
        return "No hay tabla coste-rendimiento para este dataset."
    efficient = local.sort_values(["validation_macro_f1", "n_features_used"], ascending=[False, True]).iloc[0]
    tested = int(local["test_macro_f1"].notna().sum())
    return (
        f"{dataset}: puntos_coste={len(local)}; con_test={tested}; opción_eficiente=`{efficient.feature_set}`/"
        f"`{efficient.model_name}`; variables={int(efficient.n_features_used)}; "
        f"Macro F1 validation={fmt(efficient.validation_macro_f1)}."
    )


def lectura_confusion(confusion: pd.DataFrame, dataset: str) -> str:
    local = filas_dataset(confusion, dataset)
    if local.empty:
        return "No hay matriz de confusión para este dataset."
    diagonal = local[local["actual"].astype(str).eq(local["predicted"].astype(str))]["proportion"].mean()
    return f"La diagonal media normalizada de las matrices registradas es {fmt(diagonal)}."


def lectura_ead(validation: pd.DataFrame, test: pd.DataFrame, shap_top: pd.DataFrame, dataset: str) -> str:
    return " ".join([
        lectura_validation(validation, dataset),
        lectura_test(test, dataset),
        lectura_shap(shap_top, pd.DataFrame(), dataset) if False else "",
    ]).strip()


def lectura_checklist(checklist: pd.DataFrame) -> str:
    if checklist.empty:
        return "No hay checklist final."
    pendientes = checklist[~checklist["cumple"]]
    if pendientes.empty:
        return f"Checklist completo: {len(checklist)} checks en estado OK."
    return f"Checklist con {len(pendientes)} checks pendientes: {', '.join(pendientes['check'].tolist())}."


def auditar_estructura_notebook(path: Path) -> pd.DataFrame:
    notebook = json.loads(Path(path).read_text(encoding="utf-8"))
    headings = []
    lectura_cells = 0
    dataset_sections = {f"6.{i}": 0 for i in range(1, 17)}
    errors = []
    code_without_markdown = []
    for index, cell in enumerate(notebook["cells"], start=1):
        source = "".join(cell.get("source", []))
        if cell["cell_type"] == "markdown":
            stripped = source.strip()
            if stripped.startswith("## 6."):
                headings.append(stripped.splitlines()[0])
            if stripped.startswith("### 6."):
                section = stripped.split()[1].split(".")
                key = ".".join(section[:2])
                if key in dataset_sections:
                    dataset_sections[key] += 1
        if cell["cell_type"] == "code":
            if "Lectura basada en salida" in source:
                lectura_cells += 1
            if index == 1 or notebook["cells"][index - 2]["cell_type"] != "markdown":
                code_without_markdown.append(index)
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    errors.append(index)
    rows = [
        {"check": "secciones_6_1_a_6_17", "cumple": all(any(f"## 6.{i} " in h for h in headings) for i in range(1, 18)), "evidence": "; ".join(headings)},
        {"check": "mini_apartados_dataset_6_1_a_6_16", "cumple": all(count == 5 for count in dataset_sections.values()), "evidence": str(dataset_sections)},
        {"check": "lecturas_post_output", "cumple": lectura_cells >= 70, "evidence": f"{lectura_cells} celdas con lectura basada en salida"},
        {"check": "codigo_con_markdown_previo", "cumple": not code_without_markdown, "evidence": str(code_without_markdown)},
        {"check": "sin_errores_renderizados", "cumple": not errors, "evidence": str(errors)},
    ]
    return pd.DataFrame(rows)


def actualizar_checklist_con_notebook(checklist: pd.DataFrame, notebook_audit: pd.DataFrame) -> pd.DataFrame:
    updated = checklist.copy()
    mapping = {
        "mini_apartados_por_dataset_requeridos": "mini_apartados_dataset_6_1_a_6_16",
        "lecturas_post_output_requeridas": "lecturas_post_output",
    }
    for checklist_name, audit_name in mapping.items():
        audit_row = notebook_audit[notebook_audit["check"].eq(audit_name)]
        if audit_row.empty:
            continue
        mask = updated["check"].eq(checklist_name)
        updated.loc[mask, "cumple"] = bool(audit_row["cumple"].iloc[0])
        updated.loc[mask, "evidence"] = audit_row["evidence"].iloc[0]
        updated.loc[mask, "status"] = updated.loc[mask, "cumple"].map(lambda value: "ok" if value else "revisar")
    return updated
