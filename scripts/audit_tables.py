from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "docs/auditoria"
INV = OUTDIR / "inventario_tablas_2026-06-16.csv"
FAM = OUTDIR / "inventario_tablas_familias_2026-06-16.csv"
MD = OUTDIR / "auditoria_tablas_directorio_2026-06-16.md"

TABLE_EXTS = {".csv", ".tsv", ".xlsx"}
SOURCE_EXTS = {".py", ".ipynb", ".md", ".tex", ".txt", ".json", ".yaml", ".yml", ".bib", ".toml", ".sh"}
EXCLUDE_DIRS = {".git", "__pycache__"}
GENERIC_NAMES = {
    "X_train.csv", "X_test.csv", "X_val.csv", "X_validation.csv",
    "y_train.csv", "y_test.csv", "y_val.csv", "y_validation.csv",
    "X_train_selected.csv", "X_test_selected.csv", "X_val_selected.csv", "X_validation_selected.csv",
    "y_train_selected.csv", "y_test_selected.csv", "y_val_selected.csv", "y_validation_selected.csv",
}

QUESTION_BY_PHASE = {
    "01_raw_eda": "Datos crudos: estructura, señales iniciales y riesgos.",
    "02_preprocessing": "Preprocesado: transformaciones y datasets procesados.",
    "03_postprocessing_audit": "Auditoría postprocesado: leakage, drift, duplicados, coherencia.",
    "04_split_audit": "Splits: índices, balance y reproducibilidad train/validation/test.",
    "05_feature_selection": "Selección clásica: variables, estabilidad, coste y redundancia.",
    "06_modeling": "Modelado: métricas, candidatos, intervalos, contrastes e interpretación.",
    "07_final_comparison": "Síntesis clásica final y handoff hacia QFS.",
    "08_quantum": "QFS: runs, selección, calidad, oráculos y comparación contra baseline.",
    "10_memoria": "Memoria: tablas de síntesis para figuras/narrativa.",
    "data_raw": "Fuente original de datos.",
    "data_processed": "Datos procesados listos para análisis.",
    "data_splits": "Filas/columnas de cada split reproducible.",
    "data_selected_features": "Matrices resultantes de selectores por dataset/k/split.",
    "predictions": "Predicciones por fila para verificación y fases posteriores.",
    "legacy_qfs": "Resultados históricos o auxiliares del QFS heredado.",
    "legacy_qfs_data": "Datasets heredados del código QFS auxiliar.",
    "logs": "Logs tabulares de ejecución/verificación.",
    "previous_run_logs": "Tablas archivadas de runs anteriores.",
    "audit_outputs": "Salidas de esta propia auditoría de tablas.",
    "agents_aux": "Assets de skills/agentes, fuera del núcleo TFG.",
    "other": "Tabla auxiliar no clasificada automáticamente.",
}

QUESTION_BY_NAME = [
    (re.compile(r"prediction|predicciones|predictions", re.I), "Predicciones por fila: y real, clase/probabilidad/modelo."),
    (re.compile(r"shap", re.I), "Interpretabilidad SHAP por observación, feature o candidato."),
    (re.compile(r"confidence|interval", re.I), "Incertidumbre: intervalos bootstrap o rangos de métricas."),
    (re.compile(r"pairwise|comparison|contraste|permutation|pvalue|p_value", re.I), "Contrastes estadísticos y diferencias frente a baseline."),
    (re.compile(r"jaccard|stability|estabilidad", re.I), "Estabilidad o solape entre subconjuntos/selectores."),
    (re.compile(r"redund|vif|correlation", re.I), "Redundancia, correlación o colinealidad entre variables."),
    (re.compile(r"cost|time|elapsed|operational", re.I), "Coste operacional: tiempos, variables o recursos."),
    (re.compile(r"oracle|quality|control", re.I), "Control de calidad/oráculo QFS."),
    (re.compile(r"selected|seleccion|rank|ranking|roster", re.I), "Selección de variables: rankings, conjuntos o roster."),
    (re.compile(r"split|indices", re.I), "Particionado: índices y balance de splits."),
]


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in filenames:
            yield Path(dirpath) / filename


def infer_phase(rel: str) -> str:
    parts = Path(rel).parts
    if parts and parts[0] == ".agents":
        return "agents_aux"
    if rel.startswith("docs/auditoria/inventario_tablas_") or rel.startswith("docs/auditoria/auditoria_tablas_"):
        return "audit_outputs"
    if parts[:2] == ("QFS_based_on_NA", "Datasets"):
        return "legacy_qfs_data"
    if parts[:2] == ("QFS_based_on_NA", "Results"):
        return "legacy_qfs"
    if len(parts) >= 2 and parts[0] == "data":
        return {
            "01_raw": "data_raw",
            "processed": "data_processed",
            "splits": "data_splits",
            "selected_features": "data_selected_features",
        }.get(parts[1], "other")
    if len(parts) >= 2 and parts[:2] == ("results", "predictions"):
        return "predictions"
    if len(parts) == 3 and parts[:2] == ("results", "tables") and parts[2].startswith("10_memoria_"):
        return "10_memoria"
    if len(parts) >= 3 and parts[:2] == ("results", "tables"):
        return parts[2]
    if len(parts) >= 2 and parts[:2] == ("results", "logs"):
        if "previous_tables_" in rel:
            return "previous_run_logs"
        return "logs"
    return "other"


def infer_family(rel: str) -> str:
    low = rel.lower()
    name = Path(rel).name.lower()
    if "/granular/" in low:
        return "granular_rankings"
    if "selected_features" in low:
        return "selected_feature_matrices"
    if "/predictions/" in low or "predictions" in name:
        return "predictions"
    if "shap" in low:
        return "shap"
    if "qfs" in low or "quantum" in low:
        return "qfs_quantum"
    if "modeling" in low or "06_modeling" in low:
        return "modeling"
    if "feature_selection" in low or name.startswith("fs_"):
        return "feature_selection"
    if "split" in low or "indices" in low:
        return "splits"
    if "raw" in low or "01_raw" in low:
        return "raw_data_or_eda"
    if "processed" in low or "preprocessing" in low:
        return "processed_data"
    if "comparison" in low or "comparacion" in low or "contraste" in low:
        return "comparisons"
    if Path(rel).suffix.lower() == ".xlsx":
        return "spreadsheet"
    return "other_tables"


def infer_origin(rel: str, phase: str) -> str:
    if phase.startswith("0") and phase[:2].isdigit():
        return f"Fase {int(phase[:2])}: results/tables/{phase}/"
    return {
        "data_raw": "Dataset fuente externo o descargado manualmente en data/01_raw/",
        "data_processed": "Fase 2/preprocesado: versión procesada en data/processed/",
        "data_splits": "Fase 4: splits reproducibles en data/splits/",
        "data_selected_features": "Fase 5: matrices exportadas por selector/k en data/selected_features/",
        "predictions": "Fase 6/8/9: predicciones por fila en results/predictions/",
        "legacy_qfs": "Código auxiliar/histórico QFS_based_on_NA/Results/",
        "agents_aux": "Assets de .agents; no núcleo del TFG.",
    }.get(phase, "Origen no inferido automáticamente; revisar ruta/referencias.")


def infer_question(rel: str, phase: str) -> str:
    for regex, question in QUESTION_BY_NAME:
        if regex.search(rel):
            return question
    return QUESTION_BY_PHASE.get(phase, QUESTION_BY_PHASE["other"])


def classify_role(phase: str, strong_refs: int, weak_refs: int) -> str:
    if strong_refs:
        return "usada_directamente_por_ruta"
    if weak_refs:
        return "mencionada_por_nombre"
    if phase in {"data_raw", "data_processed", "data_splits"}:
        return "entrada_de_pipeline_por_convencion"
    if phase == "data_selected_features":
        return "consumida_por_patron_directorio_fase6"
    if phase == "predictions":
        return "salida_regenerable_o_consumida_por_fases_posteriores"
    if phase.startswith("0"):
        return "artefacto_de_fase_no_referenciado_directamente"
    if phase == "agents_aux":
        return "auxiliar_agents_fuera_nucleo_tfg"
    return "sin_uso_detectado"


def inspect_table(path: Path):
    size = path.stat().st_size
    suffix = path.suffix.lower()
    columns: list[str] = []
    ncols: int | str = ""
    nrows: int | str = ""
    readable = True
    error = ""
    try:
        if suffix != ".xlsx":
            delimiter = "\t" if suffix == ".tsv" else ","
            with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
                sample = handle.read(8192)
                handle.seek(0)
                try:
                    delimiter = csv.Sniffer().sniff(sample).delimiter if sample else delimiter
                except Exception:
                    pass
                header = next(csv.reader(handle, delimiter=delimiter), [])
                columns = [col.strip() for col in header]
            ncols = len(columns)
            if size <= 75_000_000:
                with path.open("rb") as handle:
                    line_count = sum(chunk.count(b"\n") for chunk in iter(lambda: handle.read(1024 * 1024), b""))
                nrows = max(0, line_count - 1)
    except Exception as exc:
        readable = False
        error = f"{type(exc).__name__}: {str(exc)[:160]}"
    return columns, ncols, nrows, readable, error


def describe_contents(rel: str, phase: str, columns: list[str]) -> str:
    low = rel.lower()
    if phase == "data_selected_features":
        return "Matriz seleccionada por split con columnas de features; una fila por muestra."
    if phase in {"data_raw", "data_processed", "data_splits"}:
        return "Dataset/matriz de datos; variables, target o índices según fase."
    if "prediction" in low or "/predictions/" in low:
        return "Predicciones por observación: etiqueta real/predicha, probabilidades o modelo."
    if "shap" in low:
        return "Valores o inputs SHAP por observación, feature o candidato."
    if "ranking" in low or "rankings" in low:
        return "Ranking de variables con método, score, seed, k o posición."
    if "selected" in low or "seleccion" in low:
        return "Conjuntos de variables seleccionadas y metadatos de selector/k."
    if "validation" in low or "test" in low or "results" in low:
        return "Resultados de experimento: métricas, modelo, dataset, selector y split."
    if columns:
        preview = ", ".join(columns[:8])
        return f"Tabla con columnas: {preview}" + ("..." if len(columns) > 8 else "")
    return "Contenido no inspeccionado o formato sin cabecera legible."


def md_table(rows: list[dict], cols: list[str]) -> str:
    if not rows:
        return "_Sin filas._"
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")) for col in cols) + " |")
    return "\n".join(lines)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    source_files = []
    for path in iter_files(ROOT):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(".agents/") or path.suffix.lower() not in SOURCE_EXTS:
            continue
        try:
            if path.stat().st_size <= 25_000_000:
                source_files.append((rel, path.read_text(encoding="utf-8", errors="ignore")))
        except Exception:
            pass

    table_files = [
        (path.relative_to(ROOT).as_posix(), path)
        for path in iter_files(ROOT)
        if path.suffix.lower() in TABLE_EXTS
    ]
    table_files.sort()

    rows_out = []
    family_counter: defaultdict[tuple[str, str], Counter] = defaultdict(Counter)
    for rel, path in table_files:
        phase = infer_phase(rel)
        family = infer_family(rel)
        columns, ncols, nrows, readable, error = inspect_table(path)
        basename = Path(rel).name
        strong, weak = [], []
        for src_rel, text in source_files:
            if rel in text or f"./{rel}" in text:
                strong.append(src_rel)
            elif basename not in GENERIC_NAMES and basename in text:
                weak.append(src_rel)
        strong = sorted(set(strong))
        weak = sorted(set(weak))
        role = classify_role(phase, len(strong), len(weak))
        stat = path.stat()
        row = {
            "path": rel,
            "root": Path(rel).parts[0] if Path(rel).parts else "",
            "phase": phase,
            "family": family,
            "role": role,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / 1048576, 3),
            "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            "rows_counted": nrows,
            "n_columns": ncols,
            "columns_preview": " | ".join(columns[:20]),
            "content_summary": describe_contents(rel, phase, columns),
            "question_answered": infer_question(rel, phase),
            "probable_origin": infer_origin(rel, phase),
            "strong_ref_count": len(strong),
            "weak_ref_count": len(weak),
            "reference_examples": " | ".join((strong + weak)[:8]),
            "readable": readable,
            "read_error": error,
        }
        rows_out.append(row)
        counter = family_counter[(phase, family)]
        counter["files"] += 1
        counter["bytes"] += stat.st_size
        counter[f"role:{role}"] += 1

    with INV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows_out[0].keys()))
        writer.writeheader()
        writer.writerows(rows_out)

    fam_rows = []
    for (phase, family), counter in sorted(family_counter.items()):
        roles = {key.split(":", 1)[1]: value for key, value in counter.items() if key.startswith("role:")}
        fam_rows.append({
            "phase": phase,
            "family": family,
            "files": counter["files"],
            "size_mb": round(counter["bytes"] / 1048576, 3),
            "direct_refs": roles.get("usada_directamente_por_ruta", 0),
            "name_refs": roles.get("mencionada_por_nombre", 0),
            "pattern_or_convention": sum(
                value for key, value in roles.items()
                if key not in {
                    "usada_directamente_por_ruta", "mencionada_por_nombre",
                    "sin_uso_detectado", "auxiliar_agents_fuera_nucleo_tfg",
                    "artefacto_de_fase_no_referenciado_directamente",
                }
            ),
            "phase_artifacts_unreferenced": roles.get("artefacto_de_fase_no_referenciado_directamente", 0),
            "no_use_detected": roles.get("sin_uso_detectado", 0),
            "agents_aux": roles.get("auxiliar_agents_fuera_nucleo_tfg", 0),
            "question": QUESTION_BY_PHASE.get(phase, QUESTION_BY_PHASE["other"]),
        })

    with FAM.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fam_rows[0].keys()))
        writer.writeheader()
        writer.writerows(fam_rows)

    root_counts = Counter(row["root"] for row in rows_out)
    role_counts = Counter(row["role"] for row in rows_out)
    core = [row for row in rows_out if row["root"] != ".agents" and row["phase"] != "audit_outputs"]
    core_phase = Counter(row["phase"] for row in core)
    used_roles = {
        "usada_directamente_por_ruta", "mencionada_por_nombre",
        "entrada_de_pipeline_por_convencion", "consumida_por_patron_directorio_fase6",
        "salida_regenerable_o_consumida_por_fases_posteriores",
    }
    phase_summary = []
    for phase, count in sorted(core_phase.items()):
        subset = [row for row in core if row["phase"] == phase]
        phase_summary.append({
            "phase": phase,
            "files": count,
            "size_mb": round(sum(row["size_bytes"] for row in subset) / 1048576, 1),
            "used_or_convention": sum(1 for row in subset if row["role"] in used_roles),
            "no_direct_ref": sum(1 for row in subset if row["role"] not in used_roles),
            "question": QUESTION_BY_PHASE.get(phase, QUESTION_BY_PHASE["other"]),
        })
    large = sorted(core, key=lambda row: row["size_bytes"], reverse=True)[:20]
    large_rows = [
        {key: row[key] for key in ["path", "phase", "family", "role", "size_mb", "rows_counted", "n_columns"]}
        for row in large
    ]

    report = f"""# Auditoría de tablas del directorio

Fecha: 2026-06-16.

## Alcance

Se inventariaron ficheros `.csv`, `.tsv` y `.xlsx` en todo el repositorio, excluyendo `.git`. La auditoría separa el núcleo del TFG (`data/`, `results/`, `QFS_based_on_NA/`) de `.agents/`, porque `.agents/` contiene assets de skills y no resultados científicos del trabajo.

Artefactos generados:

- `docs/auditoria/inventario_tablas_2026-06-16.csv`: inventario fila a fila.
- `docs/auditoria/inventario_tablas_familias_2026-06-16.csv`: resumen por fase/familia.
- `docs/auditoria/auditoria_tablas_directorio_2026-06-16.md`: este informe.

## Resumen ejecutivo

- Tablas totales detectadas: {len(rows_out)}.
- Tablas del núcleo TFG, sin `.agents` ni salidas de esta auditoría: {len(core)}.
- Tablas en `.agents`: {root_counts.get(".agents", 0)}.
- Tablas con referencia directa por ruta: {role_counts.get("usada_directamente_por_ruta", 0)}.
- Tablas mencionadas por nombre: {role_counts.get("mencionada_por_nombre", 0)}.
- Tablas consumidas por convención/patrón: {role_counts.get("entrada_de_pipeline_por_convencion", 0) + role_counts.get("consumida_por_patron_directorio_fase6", 0) + role_counts.get("salida_regenerable_o_consumida_por_fases_posteriores", 0)}.
- Artefactos de fase sin referencia directa detectada: {role_counts.get("artefacto_de_fase_no_referenciado_directamente", 0)}.
- Sin uso detectado automático: {role_counts.get("sin_uso_detectado", 0)}.

La lectura importante: muchas tablas no aparecen citadas una a una porque son consumidas por patrón de carpeta. El caso más claro es `data/selected_features/`, donde Fase 6 consume matrices por dataset/selector/k/split, no por referencias literales a cada CSV.

## Resumen por fase/zona

{md_table(phase_summary, ["phase", "files", "size_mb", "used_or_convention", "no_direct_ref", "question"])}

## Top tablas por tamaño en el núcleo TFG

{md_table(large_rows, ["path", "phase", "family", "role", "size_mb", "rows_counted", "n_columns"])}

## Cómo leer la columna `role`

- `usada_directamente_por_ruta`: algún script/notebook/doc/tex contiene la ruta exacta.
- `mencionada_por_nombre`: aparece el nombre del archivo, pero no la ruta completa; puede ser uso real o mención documental.
- `entrada_de_pipeline_por_convencion`: dataset de entrada esperado por estructura de carpetas.
- `consumida_por_patron_directorio_fase6`: matrices de `data/selected_features/` consumidas por patrón; no deben deduplicarse ni borrarse por falta de referencia literal.
- `salida_regenerable_o_consumida_por_fases_posteriores`: predicciones por fila; algunas están ignoradas en git pero siguen siendo necesarias/regenerables.
- `artefacto_de_fase_no_referenciado_directamente`: tabla de resultados disponible para auditoría/reporte, aunque ningún archivo la cite literalmente.
- `sin_uso_detectado`: no se infirió uso ni por ruta, ni por nombre, ni por convención conocida.
- `auxiliar_agents_fuera_nucleo_tfg`: CSV de `.agents`; fuera del análisis científico principal.

## De dónde salen y qué preguntan

### `data/01_raw/`

Datos fuente externos. Responden qué información original entra al proyecto. No se consideran outputs limpiables.

### `data/processed/`

Salidas de preprocesado. Responden cómo queda cada dataset tras normalización, limpieza y codificación.

### `data/splits/`

Salidas de Fase 4. Responden qué filas quedan en train, validation y test, y permiten reproducir los splits.

### `data/selected_features/`

Salidas de Fase 5. Responden qué matriz resulta al aplicar cada selector y cada k a train/validation/test. Se consumen por patrón de directorio en Fase 6. Los pares `X_val_selected.csv` y `X_validation_selected.csv` son alias intencionados.

### `results/tables/01_raw_eda/` a `results/tables/04_split_audit/`

Tablas de auditoría de datos, preprocesado, postprocesado y particionado. Responden a calidad, leakage, drift, consistencia y trazabilidad antes del modelado.

### `results/tables/05_feature_selection/`

Tablas de ranking, estabilidad, redundancia, permutación, handoff y granularidad de selectores. Responden qué variables se eligen, con qué robustez y bajo qué coste.

### `results/tables/06_modeling/`

Tablas de validation/test, candidatos, intervalos, contrastes, coste y SHAP. Responden qué modelos/subconjuntos rinden mejor y cómo se interpretan. Incluyen XGBoost en la parrilla actual.

### `results/tables/07_final_comparison/`

Síntesis final clásica y handoff hacia QFS. Importante: `fase7_comparacion_final.csv` se conserva porque lo lee Fase 9 como baseline clásico.

### `results/tables/08_quantum/`

Resultados QFS: runs por beta/configuración, selección de variables, calidad, oráculos, comparaciones contra baseline y validación. Responden si QFS aporta o no frente a alternativas clásicas.

### `results/tables/10_*`

Tablas auxiliares de memoria/figuras narrativas. Responden preguntas de síntesis visual, consistencia y atribución para la memoria.

### `results/predictions/`

Predicciones por fila. Son pesadas y regenerables, pero útiles para verificación, Fase 9 y comparación por instancia.

### `QFS_based_on_NA/Results/`

Resultados históricos o auxiliares del código QFS heredado. Conviene tratarlos como referencia/legacy, no como run canónico salvo que un notebook actual los cite.

### `.agents/`

Contiene CSVs de assets/ejemplos de skills. No forman parte del pipeline TFG.

## Hallazgos prácticos

1. El grueso de tablas no está en `results/tables`, sino en `data/selected_features/` y predicciones. Eso no implica basura: muchas son entradas derivadas para modelado.
2. Las tablas más claramente vivas por uso directo son las citadas en scripts/notebooks de fases posteriores: splits, resultados de modelado, comparación final clásica y predicciones.
3. Las tablas de `results/tables/05_feature_selection/granular/` y muchos CSV de `experiments_validation/` no suelen citarse individualmente; son trazabilidad granular.
4. `.agents/` aporta ruido para una auditoría científica. Puede excluirse de informes TFG salvo que se auditen skills.
5. `results/predictions/06_modeling/test_predictions*.csv` están ignoradas/desindexadas pero siguen presentes y son regenerables.

## Limitaciones

- La detección de uso literal busca rutas/nombres en código, notebooks, docs y LaTeX. No ejecuta análisis dinámico de paths construidos con variables.
- Las tablas muy grandes no siempre tienen conteo exacto de filas para evitar una pasada costosa sobre gigabytes; sí se extrae cabecera cuando es legible.
- `artefacto_de_fase_no_referenciado_directamente` no significa borrable: significa que no hay referencia literal detectada. En resultados científicos puede ser trazabilidad útil.

## Recomendación para limpieza futura

Para decidir limpieza futura, filtrar `inventario_tablas_2026-06-16.csv` por:

1. `role == sin_uso_detectado` y `root != .agents`.
2. `role == artefacto_de_fase_no_referenciado_directamente`, revisando fase/familia.
3. `size_mb` descendente.
4. No tocar `data/selected_features/` salvo decisión explícita de reproducibilidad.
"""
    MD.write_text(report, encoding="utf-8")
    print(json.dumps({
        "tables": len(rows_out),
        "core_tables": len(core),
        "agents_tables": root_counts.get(".agents", 0),
        "inventory": str(INV.relative_to(ROOT)),
        "families": str(FAM.relative_to(ROOT)),
        "report": str(MD.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
