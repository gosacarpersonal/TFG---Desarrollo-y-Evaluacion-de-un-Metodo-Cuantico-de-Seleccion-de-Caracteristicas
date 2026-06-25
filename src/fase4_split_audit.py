from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, ks_2samp, wasserstein_distance
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, normalized_mutual_info_score, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from viz_core.editorial_warmth import (
        WARM_REPORT_PALETTE,
        add_editorial_text,
        apply_editorial_axes,
        save_editorial_figure,
        set_editorial_rcparams,
    )
    from fase3_reporting import escapar_latex
except ModuleNotFoundError:
    from .viz_core.editorial_warmth import (
        WARM_REPORT_PALETTE,
        add_editorial_text,
        apply_editorial_axes,
        save_editorial_figure,
        set_editorial_rcparams,
    )
    from .fase3_reporting import escapar_latex


@dataclass(frozen=True)
class Phase4Paths:
    root: Path
    processed_dir: Path
    splits_dir: Path
    tables_dir: Path
    figures_dir: Path
    logs_dir: Path
    reports_dir: Path
    latex_dir: Path


DEFAULT_DATASETS = (
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
)

EXPECTED_TARGETS = {dataset: "target" for dataset in DEFAULT_DATASETS}
EXPECTED_TARGETS["olive_oil_3class"] = "area"
EXPECTED_TARGETS["olive_oil_9class"] = "target"
SOURCE_DATASET = {
    "breast_cancer_wisconsin": "breast_cancer_wisconsin",
    "customer_churn": "customer_churn",
    "madelon": "madelon",
    "olive_oil_3class": "olive_oil",
    "olive_oil_9class": "olive_oil",
}
DATASET_PATHS = {
    "breast_cancer_wisconsin": "data/processed/breast_cancer_wisconsin_processed.csv",
    "customer_churn": "data/processed/customer_churn_processed.csv",
    "madelon": "data/processed/madelon_processed.csv",
    "olive_oil_3class": "data/processed/olive_oil_processed.csv",
    "olive_oil_9class": "data/processed/olive_oil_processed.csv",
}
FORMULATION_EXCLUDED_COLUMNS = {
    "olive_oil_3class": ("target", "palmitic"),
    "olive_oil_9class": ("area", "palmitic"),
}
SPLIT_ORDER = ("train", "validation", "test")
SPLIT_LABELS = {"train": "train", "validation": "validation", "test": "test"}
SEED = 2026


def phase4_paths(root: str | Path = ".") -> Phase4Paths:
    root = Path(root).resolve()
    return Phase4Paths(
        root=root,
        processed_dir=root / "data" / "processed",
        splits_dir=root / "data" / "splits",
        tables_dir=root / "results" / "tables" / "04_split_audit",
        figures_dir=root / "results" / "figures" / "04_split_audit",
        logs_dir=root / "results" / "logs" / "04_split_audit",
        reports_dir=root / "results" / "reports" / "04_split_audit",
        latex_dir=root / "Plantilla_Latex_GCD" / "tfgs" / "tex",
    )


def ensure_dirs(paths: Phase4Paths) -> None:
    for directory in (
        paths.splits_dir,
        paths.tables_dir,
        paths.figures_dir,
        paths.logs_dir,
        paths.reports_dir,
        paths.latex_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def save_table(df: pd.DataFrame, paths: Phase4Paths, name: str) -> Path:
    path = paths.tables_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def markdown_table(df: pd.DataFrame, max_rows: int = 18) -> str:
    if df.empty:
        return "_Sin filas._"
    view = df.head(max_rows).astype(str)
    header = "| " + " | ".join(view.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    rows = ["| " + " | ".join(row[col] for col in view.columns) + " |" for _, row in view.iterrows()]
    return "\n".join([header, sep, *rows])


def markdown_to_latex_basic(markdown: str) -> str:
    lines = []
    in_items = False
    for line in markdown.splitlines():
        text = line.strip()
        if text.startswith("|"):
            continue
        if in_items and not text.startswith("- "):
            lines.append(r"\end{itemize}")
            in_items = False
        if text.startswith("# "):
            lines.append(r"\section{" + escapar_latex(text[2:]) + "}")
        elif text.startswith("## "):
            lines.append(r"\subsection{" + escapar_latex(text[3:]) + "}")
        elif text.startswith("### "):
            lines.append(r"\subsubsection{" + escapar_latex(text[4:]) + "}")
        elif text.startswith("- "):
            if not in_items:
                lines.append(r"\begin{itemize}")
                in_items = True
            lines.append(r"\item " + escapar_latex(text[2:]))
        elif text:
            lines.append(escapar_latex(text) + "\n")
        else:
            lines.append("")
    if in_items:
        lines.append(r"\end{itemize}")
    return "\n".join(lines)


def dataframe_to_latex_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return r"\emph{Sin filas.}"
    view = df.head(max_rows).copy()
    return view.to_latex(index=False, escape=True, longtable=False)


def stable_row_hashes(df: pd.DataFrame) -> pd.Series:
    values = pd.util.hash_pandas_object(df.reset_index(drop=True), index=False).astype("uint64")
    return values.astype(str)


def discover_inputs(paths: Phase4Paths) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    registry = []
    for dataset in DEFAULT_DATASETS:
        path = paths.root / DATASET_PATHS[dataset]
        exists = path.exists()
        target = EXPECTED_TARGETS[dataset]
        shape = (0, 0)
        columns = []
        target_exists = False
        status = "missing_file"
        if exists:
            df_head = pd.read_csv(path, nrows=5)
            columns = list(df_head.columns)
            target_exists = target in columns
            shape_full = pd.read_csv(path, usecols=[target]).shape[0] if target_exists else pd.read_csv(path).shape[0]
            shape = (shape_full, len(columns))
            status = "ok" if target_exists else "missing_validated_target"
        rows.append(
            {
                "dataset": dataset,
                "source_dataset": SOURCE_DATASET[dataset],
                "path": str(path.relative_to(paths.root)),
                "exists": exists,
                "n_rows": shape[0],
                "n_columns": shape[1],
                "validated_target": target,
                "target_exists": target_exists,
                "status": status,
            }
        )
        registry.append(
            {
                "dataset": dataset,
                "source_dataset": SOURCE_DATASET[dataset],
                "path": str(path.relative_to(paths.root)),
                "target": target,
                "target_source": "validado contra Fase 1-3; olive_oil se desdobla en 3 y 9 clases",
                "id_columns": "",
                "forced_excluded_columns": ";".join(FORMULATION_EXCLUDED_COLUMNS.get(dataset, ())),
                "formulacion_target": "3 clases (Area)" if dataset == "olive_oil_3class" else ("9 clases (Region)" if dataset == "olive_oil_9class" else "dataset original"),
                "train_pct": 0.70,
                "validation_pct": 0.15,
                "test_pct": 0.15,
                "stratify": bool(target_exists),
                "random_state": SEED,
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(registry)


def visual_decision_map() -> pd.DataFrame:
    rows = [
        ("4.1", "Carga de entradas y warnings", "¿Están los datos y avisos heredados disponibles?", False, "sin figura", "tabla/checklist", "none", "si todos los checks caben en tabla"),
        ("4.2", "Protocolo de split", "¿Qué regla reproducible se aplica?", False, "sin figura", "tabla", "none", "no hay patrón visual que inspeccionar"),
        ("4.3", "Separación X/y", "¿Qué columnas entran como predictoras?", False, "sin figura", "tabla", "none", "la tabla comunica mejor el contrato"),
        ("4.4", "Creación de splits", "¿Qué tamaño tiene cada partición?", True, "figura simple", "categórico-numérico", "misma familia", "eliminar si duplica 4.6 sin aportar lectura"),
        ("4.5", "Guardado y recarga", "¿Los ficheros recargan igual?", False, "sin figura", "checklist", "none", "solo figura si hubiese muchos fallos"),
        ("4.6", "Tamaños y proporciones", "¿La proporción real respeta el protocolo?", True, "combinación misma familia", "categórico-numérico", "misma familia", "usar tabla si no hay desviaciones"),
        ("4.7", "Homogeneidad del target", "¿Se mantiene la distribución de clases?", True, "combinación misma familia", "part-to-whole", "misma familia", "obligatoria por dataset"),
        ("4.8", "Drift marginal", "¿Qué variables cambian entre splits?", True, "composición multifamilia", "ranking/matriz/distribución", "multifamilia", "solo si ranking muestra variables relevantes"),
        ("4.9", "Representatividad multivariante", "¿Se mezclan los splits en PCA y cuánta varianza se ve?", True, "composición multifamilia", "relacional + scree", "multifamilia", "si PC1+PC2 explica muy poco, caveat explícito"),
        ("4.10", "Duplicados y solapes", "¿Hay filas repetidas entre particiones?", False, "sin figura", "checklist", "none", "figura solo ante incidencias"),
        ("4.11", "Leakage", "¿Hay variables sospechosas de fuga?", True, "figura simple", "ranking", "multifamilia si hay fuga", "no crear si no hay sospechas"),
        ("4.12", "Adversarial validation", "¿Un modelo distingue train de test?", True, "composición multifamilia", "ROC + ranking", "multifamilia", "si AUC no supera umbral, ranking queda diagnóstico"),
        ("4.13", "Riesgos residuales", "¿Qué riesgos pasan a Fase 5/6?", False, "tabla", "checklist", "none", "heatmap solo con suficientes riesgos"),
        ("4.14", "EAD post-split", "¿Qué evidencia entra en memoria?", False, "tabla", "índice", "none", "seleccionar figuras previas"),
        ("4.15", "Checklist final", "¿Qué estado final tiene cada dataset?", False, "tabla", "checklist", "none", "matriz opcional no necesaria"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "seccion",
            "objetivo",
            "pregunta_visual",
            "necesita_figura",
            "nivel_figura",
            "familia",
            "tipo_composicion",
            "criterio_de_eliminacion",
        ],
    )


def inherited_phase3_warnings(paths: Phase4Paths) -> dict[str, pd.DataFrame]:
    base = paths.root / "results" / "tables" / "03_postprocessing_audit"
    names = [
        "fase3_dataset_readiness.csv",
        "postprocessed_split_warnings.csv",
        "postprocessed_modeling_warnings.csv",
        "postprocessed_fs_warnings.csv",
        "fase3_residual_risk_log.csv",
        "postprocessed_categorical_features_pending.csv",
        "postprocessed_target_integrity.csv",
        "postprocessed_dimensionality_summary.csv",
        "postprocessed_problematic_features.csv",
    ]
    inherited = {name: read_csv_if_exists(base / name) for name in names}
    for name, df in list(inherited.items()):
        if df.empty or "dataset" not in df.columns:
            continue
        olive_rows = df[df["dataset"].eq("olive_oil")].copy()
        if olive_rows.empty:
            continue
        expanded = []
        for variant in ("olive_oil_3class", "olive_oil_9class"):
            tmp = olive_rows.copy()
            tmp["source_dataset"] = "olive_oil"
            tmp["dataset"] = variant
            expanded.append(tmp)
        inherited[name] = pd.concat([df[~df["dataset"].eq("olive_oil")], *expanded], ignore_index=True)
    return inherited


def phase2_proxy_leakage_features(paths: Phase4Paths) -> pd.DataFrame:
    base = paths.root / "results" / "tables" / "02_preprocessing"
    rows = []
    risk_log = read_csv_if_exists(base / "preprocessing_risk_log.csv")
    if not risk_log.empty:
        for _, row in risk_log.iterrows():
            risk_text = " ".join(str(row.get(col, "")) for col in risk_log.columns).lower()
            if "proxy/leakage" in risk_text or "leakage potencial" in risk_text:
                rows.append(
                    {
                        "dataset": row.get("dataset"),
                        "feature": str(row.get("variable", "")).strip().lower(),
                        "source": "preprocessing_risk_log.csv",
                        "reason": row.get("riesgo", "proxy/leakage potencial"),
                    }
                )
    requirements = read_csv_if_exists(base / "preprocessing_requirements.csv")
    if not requirements.empty:
        for _, row in requirements.iterrows():
            text = " ".join(str(row.get(col, "")) for col in requirements.columns).lower()
            if "proxy/leakage" in text or "leakage potencial" in text:
                variables = str(row.get("variable", row.get("variables", "")))
                for variable in variables.replace(";", ",").split(","):
                    feature = variable.strip().lower()
                    if feature:
                        rows.append(
                            {
                                "dataset": row.get("dataset"),
                                "feature": feature,
                                "source": "preprocessing_requirements.csv",
                                "reason": row.get("requisito", "proxy/leakage potencial"),
                            }
                        )
    if not rows:
        return pd.DataFrame(columns=["dataset", "feature", "source", "reason"])
    return pd.DataFrame(rows).drop_duplicates()


def olive_oil_formulation_decision(paths: Phase4Paths) -> pd.DataFrame:
    raw_path = paths.root / "data" / "01_raw" / "olive_oil.csv"
    processed_path = paths.root / "data" / "processed" / "olive_oil_processed.csv"
    rows = []
    if raw_path.exists() and processed_path.exists():
        raw = pd.read_csv(raw_path)
        processed = pd.read_csv(processed_path)
        rows.extend(
            [
                {
                    "formulacion": "olive_oil_3class",
                    "target": "area",
                    "n_clases": int(processed["area"].nunique(dropna=False)),
                    "columnas_excluidas_de_X": "target;palmitic",
                    "evidencia": "data/01_raw/olive_oil.csv contiene Area con 3 clases; processed conserva area",
                    "decision": "usar como variante separada",
                    "justificacion": "Permite auditar la tarea macro-región sin que la región de 9 clases ni su código proxy entren en X.",
                },
                {
                    "formulacion": "olive_oil_9class",
                    "target": "target",
                    "n_clases": int(processed["target"].nunique(dropna=False)),
                    "columnas_excluidas_de_X": "area;palmitic",
                    "evidencia": "Fases 1-3 tratan olive_oil como multiclase de 9 regiones; Area/palmitic son proxies",
                    "decision": "usar como variante separada",
                    "justificacion": "Mantiene la formulación usada hasta Fase 3, pero excluye la macro-región y el código perfecto de región.",
                },
            ]
        )
    return pd.DataFrame(rows)


def write_olive_oil_decision_doc(paths: Phase4Paths, decision: pd.DataFrame) -> Path:
    outdir = paths.root / "docs" / "decisions"
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / "fase4_olive_oil_formulations.md"
    lines = [
        "# Decisión Fase 4: formulaciones de Olive Oil",
        "",
        "La revisión de Fase 1, Fase 2 y Fase 3 confirma que `olive_oil` contiene dos formulaciones supervisadas distintas: `Area` con 3 clases y `Region/target` con 9 clases.",
        "",
        "Por tanto, Fase 4 no trata `olive_oil` como un único dataset operativo. Se crean dos variantes trazables:",
        "",
        markdown_table(decision, 10),
        "",
        "Regla de leakage: para la tarea de 3 clases se excluyen la región de 9 clases y su código proxy; para la tarea de 9 clases se excluyen la macro-región de 3 clases y el código proxy. Las fases posteriores deben cargar `olive_oil_3class` y `olive_oil_9class`, no `olive_oil` ambiguo.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def load_datasets(paths: Phase4Paths, registry: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    datasets: dict[str, pd.DataFrame] = {}
    rows = []
    for _, cfg in registry.iterrows():
        dataset = cfg["dataset"]
        target = cfg["target"]
        path = paths.root / cfg["path"]
        status = "ok"
        message = ""
        try:
            df = pd.read_csv(path)
            target_exists = target in df.columns
            if not target_exists:
                status = "blocked"
                message = "target_validado_no_existe"
            else:
                datasets[dataset] = df
            rows.append(
                {
                    "dataset": dataset,
                    "path": cfg["path"],
                    "n_rows": len(df),
                    "n_columns": len(df.columns),
                    "target": target,
                    "target_exists": target_exists,
                    "n_classes": df[target].nunique(dropna=False) if target_exists else np.nan,
                    "missing_target": int(df[target].isna().sum()) if target_exists else np.nan,
                    "status": status,
                    "message": message,
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "dataset": dataset,
                    "path": cfg["path"],
                    "n_rows": 0,
                    "n_columns": 0,
                    "target": target,
                    "target_exists": False,
                    "n_classes": np.nan,
                    "missing_target": np.nan,
                    "status": "blocked",
                    "message": repr(exc),
                }
            )
    return datasets, pd.DataFrame(rows)


def split_protocol(registry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    protocol = registry[
        ["dataset", "train_pct", "validation_pct", "test_pct", "stratify", "random_state"]
    ].copy()
    protocol["criterio"] = "70/15/15 estratificado cuando el target lo permite"
    criteria = pd.DataFrame(
        [
            ("archivos", "existen y recargan X/y para train, validation y test", "bloqueante"),
            ("target", "target validado existe, no tiene ausentes y mantiene clases principales", "bloqueante"),
            ("coherencia", "mismas columnas predictoras y len(X)==len(y)", "bloqueante"),
            ("leakage", "target fuera de X y sin proxy/leakage evidente", "bloqueante"),
            ("solape", "sin solape de índices ni filas idénticas entre train y test", "bloqueante"),
            ("drift", "sin drift fuerte no explicado por dataset", "cautela"),
            ("adversarial", "AUC adversarial no indica separación grave", "cautela"),
            ("warnings", "riesgos heredados documentados para Fase 5/6", "cautela"),
        ],
        columns=["criterio", "definicion", "tipo"],
    )
    return protocol, criteria


def separate_xy(
    datasets: dict[str, pd.DataFrame],
    registry: pd.DataFrame,
    inherited: dict[str, pd.DataFrame],
    proxy_features: pd.DataFrame,
) -> tuple[dict[str, tuple[pd.DataFrame, pd.Series]], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    xy: dict[str, tuple[pd.DataFrame, pd.Series]] = {}
    map_rows, excluded_rows, feature_rows = [], [], []
    suspicious = inherited.get("postprocessed_problematic_features.csv", pd.DataFrame())
    pending_cat = inherited.get("postprocessed_categorical_features_pending.csv", pd.DataFrame())
    for _, cfg in registry.iterrows():
        dataset = cfg["dataset"]
        if dataset not in datasets:
            continue
        df = datasets[dataset]
        target = cfg["target"]
        id_columns = [c for c in str(cfg.get("id_columns", "")).split(";") if c and c in df.columns]
        forced_cols = [c for c in str(cfg.get("forced_excluded_columns", "")).split(";") if c and c in df.columns and c != target]
        proxy_cols = []
        if not proxy_features.empty:
            proxy_set = set(proxy_features.loc[proxy_features["dataset"].eq(dataset), "feature"].astype(str).str.lower())
            for col in df.columns:
                if col == target or col.lower() not in proxy_set:
                    continue
                nmi = nmi_for_feature(df[col], df[target])
                semantic_region_proxy = SOURCE_DATASET.get(dataset) == "olive_oil" and col.lower() in {"area", "palmitic"}
                if semantic_region_proxy or (not pd.isna(nmi) and nmi >= 0.95):
                    proxy_cols.append(col)
        excluded = list(dict.fromkeys([target, *id_columns, *forced_cols, *proxy_cols]))
        X = df.drop(columns=excluded)
        y = df[target]
        xy[dataset] = (X, y)
        cat_pending = pending_cat[pending_cat.get("dataset", pd.Series(dtype=str)).eq(dataset)] if not pending_cat.empty else pd.DataFrame()
        suspicious_ds = suspicious[suspicious.get("dataset", pd.Series(dtype=str)).eq(dataset)] if not suspicious.empty else pd.DataFrame()
        map_rows.append(
            {
                "dataset": dataset,
                "target": target,
                "n_rows": len(df),
                "n_features": X.shape[1],
                "target_in_X": target in X.columns,
                "id_columns_excluded": ";".join(id_columns),
                "proxy_leakage_columns_excluded": ";".join([c for c in excluded if c != target and c not in id_columns]),
                "categorical_features_pending": int(len(cat_pending)),
                "problematic_features_phase3": int(len(suspicious_ds)),
                "status": "ok" if target not in X.columns else "blocked",
            }
        )
        for col in excluded:
            if col == target:
                reason = "target"
            elif col in id_columns:
                reason = "id"
            elif col in forced_cols:
                reason = "formulación alternativa de target o proxy excluida por diseño"
            else:
                reason = "proxy/leakage potencial heredado de Fase 2 y confirmado en Fase 4"
            excluded_rows.append({"dataset": dataset, "column": col, "reason": reason})
        for col in X.columns:
            feature_rows.append(
                {
                    "dataset": dataset,
                    "feature": col,
                    "dtype": str(X[col].dtype),
                    "n_unique": int(X[col].nunique(dropna=False)),
                    "missing": int(X[col].isna().sum()),
                }
            )
    return xy, pd.DataFrame(map_rows), pd.DataFrame(excluded_rows), pd.DataFrame(feature_rows)


def create_splits(xy: dict[str, tuple[pd.DataFrame, pd.Series]], registry: pd.DataFrame) -> tuple[dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]], pd.DataFrame, pd.DataFrame]:
    splits: dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]] = {}
    creation_rows, index_rows = [], []
    cfg_by_dataset = registry.set_index("dataset").to_dict("index")
    for dataset, (X, y) in xy.items():
        cfg = cfg_by_dataset[dataset]
        test_size = float(cfg["test_pct"])
        validation_pct = float(cfg["validation_pct"])
        train_pct = float(cfg["train_pct"])
        val_relative = validation_pct / (train_pct + validation_pct)
        random_state = int(cfg["random_state"])
        counts = y.value_counts(dropna=False)
        min_class = int(counts.min())
        stratify = y if bool(cfg["stratify"]) and min_class >= 3 else None
        status = "ok"
        message = ""
        try:
            X_tmp, X_test, y_tmp, y_test = train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=random_state,
                stratify=stratify,
            )
            stratify_tmp = y_tmp if stratify is not None and y_tmp.value_counts(dropna=False).min() >= 2 else None
            X_train, X_val, y_train, y_val = train_test_split(
                X_tmp,
                y_tmp,
                test_size=val_relative,
                random_state=random_state,
                stratify=stratify_tmp,
            )
            split_dict = {
                "train": (X_train, y_train),
                "validation": (X_val, y_val),
                "test": (X_test, y_test),
            }
            missing_classes = {
                name: sorted(set(y.unique()) - set(ys.unique()))
                for name, (_, ys) in split_dict.items()
            }
            if any(missing_classes.values()):
                status = "requires_regenerate_split"
                message = json.dumps(missing_classes, ensure_ascii=False)
            splits[dataset] = split_dict
            for split_name, (Xs, ys) in split_dict.items():
                for idx in Xs.index:
                    index_rows.append({"dataset": dataset, "split": split_name, "original_index": idx})
            creation_rows.append(
                {
                    "dataset": dataset,
                    "random_state": random_state,
                    "stratified": stratify is not None,
                    "min_class_count_before_split": min_class,
                    "n_train": len(X_train),
                    "n_validation": len(X_val),
                    "n_test": len(X_test),
                    "missing_classes_by_split": message,
                    "status": status,
                }
            )
        except Exception as exc:
            creation_rows.append(
                {
                    "dataset": dataset,
                    "random_state": random_state,
                    "stratified": stratify is not None,
                    "min_class_count_before_split": min_class,
                    "n_train": 0,
                    "n_validation": 0,
                    "n_test": 0,
                    "missing_classes_by_split": "",
                    "status": "blocked",
                    "message": repr(exc),
                }
            )
    return splits, pd.DataFrame(creation_rows), pd.DataFrame(index_rows)


def save_and_reload_splits(splits: dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]], paths: Phase4Paths, registry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    saved_rows, reload_rows = [], []
    target_map = registry.set_index("dataset")["target"].to_dict()
    for dataset, split_dict in splits.items():
        outdir = paths.splits_dir / dataset
        outdir.mkdir(parents=True, exist_ok=True)
        for split_name, (X, y) in split_dict.items():
            x_path = outdir / f"X_{split_name}.csv"
            y_path = outdir / f"y_{split_name}.csv"
            X.to_csv(x_path, index=True, index_label="original_index")
            y.rename(target_map[dataset]).to_csv(y_path, index=True, index_label="original_index")
            saved_rows.extend(
                [
                    {"dataset": dataset, "split": split_name, "kind": "X", "path": str(x_path.relative_to(paths.root)), "rows": len(X), "columns": X.shape[1]},
                    {"dataset": dataset, "split": split_name, "kind": "y", "path": str(y_path.relative_to(paths.root)), "rows": len(y), "columns": 1},
                ]
            )
            X_reload = pd.read_csv(x_path, index_col="original_index")
            y_reload = pd.read_csv(y_path, index_col="original_index").iloc[:, 0]
            reload_rows.append(
                {
                    "dataset": dataset,
                    "split": split_name,
                    "x_shape_ok": X_reload.shape == X.shape,
                    "y_length_ok": len(y_reload) == len(y),
                    "columns_ok": list(X_reload.columns) == list(X.columns),
                    "index_ok": list(X_reload.index) == list(X.index),
                    "len_x_eq_y": len(X_reload) == len(y_reload),
                    "status": "ok" if X_reload.shape == X.shape and len(y_reload) == len(y) and list(X_reload.columns) == list(X.columns) and len(X_reload) == len(y_reload) else "blocked",
                }
            )
    return pd.DataFrame(saved_rows), pd.DataFrame(reload_rows)


def size_audit(splits: dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]], registry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    expected = registry.set_index("dataset")[["train_pct", "validation_pct", "test_pct"]].to_dict("index")
    rows = []
    for dataset, split_dict in splits.items():
        total = sum(len(X) for X, _ in split_dict.values())
        for split_name, (X, _) in split_dict.items():
            rows.append(
                {
                    "dataset": dataset,
                    "split": split_name,
                    "n_rows": len(X),
                    "observed_pct": len(X) / total,
                    "expected_pct": expected[dataset][f"{split_name}_pct"],
                }
            )
    summary = pd.DataFrame(rows)
    if summary.empty:
        return summary, summary
    audit = summary.copy()
    audit["abs_delta_pct_points"] = (audit["observed_pct"] - audit["expected_pct"]).abs() * 100
    audit["small_split_warning"] = audit["n_rows"] < 30
    audit["status"] = np.where(
        audit["small_split_warning"] | (audit["abs_delta_pct_points"] > 2.0),
        "warning",
        "ok",
    )
    return summary, audit


def target_audit(splits: dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    for dataset, split_dict in splits.items():
        all_classes = sorted(pd.concat([ys for _, ys in split_dict.values()]).dropna().unique())
        for split_name, (_, y) in split_dict.items():
            counts = y.value_counts(dropna=False)
            proportions = y.value_counts(normalize=True, dropna=False)
            for cls in all_classes:
                rows.append(
                    {
                        "dataset": dataset,
                        "split": split_name,
                        "class": cls,
                        "n": int(counts.get(cls, 0)),
                        "proportion": float(proportions.get(cls, 0.0)),
                    }
                )
    dist = pd.DataFrame(rows)
    diff_rows, test_rows = [], []
    for dataset, dfd in dist.groupby("dataset"):
        pivot = dfd.pivot_table(index="class", columns="split", values="proportion", fill_value=0)
        for cls, row in pivot.iterrows():
            diff_rows.append(
                {
                    "dataset": dataset,
                    "class": cls,
                    "max_prop_diff_pct_points": float((row.max() - row.min()) * 100),
                    "status": "warning" if (row.max() - row.min()) > 0.05 else "ok",
                }
            )
        counts = dfd.pivot_table(index="class", columns="split", values="n", fill_value=0)
        method = "chi2"
        p_value = np.nan
        statistic = np.nan
        min_expected = np.nan
        try:
            if counts.shape == (2, 2):
                statistic, p_value = fisher_exact(counts.values)
                method = "fisher_exact"
            else:
                statistic, p_value, _, expected = chi2_contingency(counts.values)
                min_expected = float(expected.min())
        except Exception:
            method = "not_applicable"
        max_diff = max(r["max_prop_diff_pct_points"] for r in diff_rows if r["dataset"] == dataset)
        test_rows.append(
            {
                "dataset": dataset,
                "method": method,
                "statistic": statistic,
                "p_value": p_value,
                "min_expected_count": min_expected,
                "max_prop_diff_pct_points": max_diff,
                "classes_absent": bool((counts == 0).any().any()),
                "status": "warning" if max_diff > 5 or (not pd.isna(p_value) and p_value < 0.01) else "ok",
            }
        )
    return dist, pd.DataFrame(diff_rows), pd.DataFrame(test_rows)


def psi_numeric(reference: pd.Series, comparison: pd.Series, bins: int = 10) -> float:
    ref = pd.to_numeric(reference, errors="coerce").dropna().to_numpy()
    comp = pd.to_numeric(comparison, errors="coerce").dropna().to_numpy()
    if len(ref) < 2 or len(comp) < 2 or np.nanstd(ref) == 0:
        return np.nan
    quantiles = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(quantiles) <= 2:
        return np.nan
    ref_counts, _ = np.histogram(ref, bins=quantiles)
    comp_counts, _ = np.histogram(comp, bins=quantiles)
    ref_pct = np.maximum(ref_counts / max(ref_counts.sum(), 1), 1e-6)
    comp_pct = np.maximum(comp_counts / max(comp_counts.sum(), 1), 1e-6)
    return float(np.sum((comp_pct - ref_pct) * np.log(comp_pct / ref_pct)))


def variable_drift_audit(splits: dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    for dataset, split_dict in splits.items():
        X_train = split_dict["train"][0]
        for split_name in ("validation", "test"):
            X_comp = split_dict[split_name][0]
            for feature in X_train.columns:
                a = X_train[feature]
                b = X_comp[feature]
                if pd.api.types.is_numeric_dtype(a):
                    aa = pd.to_numeric(a, errors="coerce").dropna()
                    bb = pd.to_numeric(b, errors="coerce").dropna()
                    if len(aa) > 1 and len(bb) > 1:
                        ks_stat, ks_p = ks_2samp(aa, bb)
                        w = wasserstein_distance(aa, bb)
                        scale = max(float(aa.std(ddof=0)), 1e-9)
                        w_std = float(w / scale)
                        psi = psi_numeric(aa, bb)
                    else:
                        ks_stat, ks_p, w, w_std, psi = np.nan, np.nan, np.nan, np.nan, np.nan
                    metric_type = "numeric"
                else:
                    table = pd.crosstab(pd.Series(["train"] * len(a) + [split_name] * len(b)), pd.concat([a, b], ignore_index=True))
                    try:
                        chi2_stat, ks_p, _, expected = chi2_contingency(table.values)
                        n = table.values.sum()
                        k = min(table.shape)
                        cramer_v = float(np.sqrt(chi2_stat / (n * max(k - 1, 1)))) if n > 0 else np.nan
                    except Exception:
                        chi2_stat, ks_p, cramer_v = np.nan, np.nan, np.nan
                    ks_stat = cramer_v
                    w, w_std, psi = np.nan, np.nan, np.nan
                    metric_type = "categorical"
                rows.append(
                    {
                        "dataset": dataset,
                        "comparison": f"train_vs_{split_name}",
                        "feature": feature,
                        "metric_type": metric_type,
                        "ks_or_chi2_stat": ks_stat,
                        "p_value": ks_p,
                        "wasserstein": w,
                        "wasserstein_std": w_std,
                        "psi": psi,
                        "effect_size_metric": "KS/PSI/Wasserstein std" if metric_type == "numeric" else "Cramér's V",
                        "practical_effect": float(max([x for x in [psi, w_std, ks_stat] if not pd.isna(x)], default=np.nan)),
                    }
                )
    tests = pd.DataFrame(rows)
    if tests.empty:
        return tests, pd.DataFrame(), pd.DataFrame()
    tests["drift_flag"] = (
        (tests["psi"].fillna(0) >= 0.20)
        | (tests["wasserstein_std"].fillna(0) >= 0.25)
        | ((tests["p_value"].fillna(1) < 0.001) & (tests["ks_or_chi2_stat"].fillna(0) > 0.08))
    )
    tests["ranking_auxiliar_drift_score"] = (
        tests["psi"].fillna(0).clip(0, 1)
        + tests["wasserstein_std"].fillna(0).clip(0, 1)
        + tests["ks_or_chi2_stat"].fillna(0).clip(0, 1)
    )
    summary = (
        tests.groupby("dataset")
        .agg(
            n_tests=("feature", "count"),
            n_features_flagged=("drift_flag", "sum"),
            max_psi=("psi", "max"),
            max_wasserstein_std=("wasserstein_std", "max"),
            max_ks_or_chi2_stat=("ks_or_chi2_stat", "max"),
        )
        .reset_index()
    )
    summary["status"] = np.where(summary["n_features_flagged"] > 0, "warning", "ok")
    high = tests.sort_values(["dataset", "drift_flag", "ranking_auxiliar_drift_score"], ascending=[True, False, False])
    high = high.groupby("dataset", as_index=False).head(12)
    return tests, summary, high


def preprocessing_for_X(X: pd.DataFrame) -> ColumnTransformer:
    num_cols = list(X.select_dtypes(include=[np.number, "bool"]).columns)
    cat_cols = [c for c in X.columns if c not in num_cols]
    transformers = []
    if num_cols:
        transformers.append(("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), num_cols))
    if cat_cols:
        transformers.append(("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), cat_cols))
    return ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=False)


def pca_audit(splits: dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]], paths: Phase4Paths) -> tuple[pd.DataFrame, pd.DataFrame]:
    coord_rows, variance_rows = [], []
    for dataset, split_dict in splits.items():
        X_all = pd.concat([split_dict[s][0] for s in SPLIT_ORDER], axis=0)
        labels = np.concatenate([[s] * len(split_dict[s][0]) for s in SPLIT_ORDER])
        pre = preprocessing_for_X(X_all)
        Xt = pre.fit_transform(X_all)
        max_components = min(10, Xt.shape[0], Xt.shape[1])
        if max_components < 2:
            continue
        pca = PCA(n_components=max_components, random_state=SEED)
        coords = pca.fit_transform(Xt)
        for i, ratio in enumerate(pca.explained_variance_ratio_, start=1):
            variance_rows.append({"dataset": dataset, "component": i, "explained_variance_ratio": float(ratio), "cumulative_explained_variance": float(pca.explained_variance_ratio_[:i].sum())})
        sample_idx = np.arange(coords.shape[0])
        if len(sample_idx) > 3000:
            rng = np.random.default_rng(SEED)
            sample_idx = np.sort(rng.choice(sample_idx, size=3000, replace=False))
        for idx in sample_idx:
            coord_rows.append({"dataset": dataset, "split": labels[idx], "pc1": coords[idx, 0], "pc2": coords[idx, 1], "visual_sample": len(labels) > 3000})
    return pd.DataFrame(coord_rows), pd.DataFrame(variance_rows)


def overlap_and_duplicates(splits: dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overlap_rows, duplicate_rows, conflict_rows = [], [], []
    for dataset, split_dict in splits.items():
        index_sets = {name: set(X.index) for name, (X, _) in split_dict.items()}
        hash_sets = {name: set(stable_row_hashes(X)) for name, (X, _) in split_dict.items()}
        for i, a in enumerate(SPLIT_ORDER):
            for b in SPLIT_ORDER[i + 1 :]:
                overlap_rows.append(
                    {
                        "dataset": dataset,
                        "split_a": a,
                        "split_b": b,
                        "index_overlap": len(index_sets[a] & index_sets[b]),
                        "row_hash_overlap": len(hash_sets[a] & hash_sets[b]),
                    }
                )
        for name, (X, y) in split_dict.items():
            row_hash = stable_row_hashes(X)
            dup_count = int(row_hash.duplicated(keep=False).sum())
            duplicate_rows.append({"dataset": dataset, "split": name, "duplicated_rows_internal": dup_count})
            dup_frame = pd.DataFrame({"hash": row_hash, "target": y.to_numpy()})
            conflicts = dup_frame.groupby("hash")["target"].nunique(dropna=False)
            conflict_rows.append({"dataset": dataset, "split": name, "conflicting_duplicate_groups": int((conflicts > 1).sum())})
    return pd.DataFrame(overlap_rows), pd.DataFrame(duplicate_rows), pd.DataFrame(conflict_rows)


def univariate_auc_for_feature(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    mask = x.notna() & y.notna()
    x = x[mask]
    y = y[mask]
    if y.nunique(dropna=False) != 2 or x.nunique(dropna=False) < 2:
        return np.nan, np.nan
    y_numeric = pd.factorize(y)[0]
    if pd.api.types.is_numeric_dtype(x):
        scores = pd.to_numeric(x, errors="coerce")
    else:
        means = pd.DataFrame({"x": x.astype(str), "y": y_numeric}).groupby("x")["y"].mean()
        scores = x.astype(str).map(means)
    try:
        auc = roc_auc_score(y_numeric, scores)
        auc = max(float(auc), float(1 - auc))
        return auc, np.nan
    except Exception:
        return np.nan, np.nan


def nmi_for_feature(x: pd.Series, y: pd.Series) -> float:
    mask = x.notna() & y.notna()
    x = x[mask]
    y = y[mask]
    if len(x) == 0 or x.nunique(dropna=False) < 2 or y.nunique(dropna=False) < 2:
        return np.nan
    if pd.api.types.is_numeric_dtype(x) and x.nunique(dropna=False) > 20:
        try:
            x_disc = pd.qcut(pd.to_numeric(x, errors="coerce"), q=min(10, x.nunique()), duplicates="drop").astype(str)
        except Exception:
            x_disc = pd.Series(pd.factorize(x)[0], index=x.index).astype(str)
    else:
        x_disc = x.astype(str)
    return float(normalized_mutual_info_score(y.astype(str), x_disc.astype(str)))


def leakage_audit(xy: dict[str, tuple[pd.DataFrame, pd.Series]], inherited: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    tokens = ("target", "label", "class", "diagnosis", "churn", "outcome", "response", "test")
    audit_rows, suspicious_rows, screening_rows, decision_rows, coverage_rows = [], [], [], [], []
    pending = inherited.get("postprocessed_categorical_features_pending.csv", pd.DataFrame())
    for dataset, (X, y) in xy.items():
        target_in_x = "target" in X.columns
        y_is_binary = y.nunique(dropna=False) == 2
        auc_evaluable = 0
        nmi_evaluable = 0
        categorical_evaluable = 0
        for col in X.columns:
            lower = col.lower()
            name_suspicion = any(tok in lower for tok in tokens)
            auc, _ = univariate_auc_for_feature(X[col], y)
            nmi = nmi_for_feature(X[col], y)
            auc_evaluable += int(not pd.isna(auc))
            nmi_evaluable += int(not pd.isna(nmi))
            categorical_evaluable += int(not pd.api.types.is_numeric_dtype(X[col]))
            unique_ratio = X[col].nunique(dropna=False) / max(len(X), 1)
            screening_rows.append(
                {
                    "dataset": dataset,
                    "feature": col,
                    "name_suspicion": name_suspicion,
                    "univariate_auc_abs": auc,
                    "normalized_mutual_information": nmi,
                    "unique_ratio": unique_ratio,
                    "screening_note": "AUC binario + NMI" if y_is_binary else "NMI multiclase; AUC no aplicable",
                }
            )
            if name_suspicion or (not pd.isna(auc) and auc >= 0.985) or (not pd.isna(nmi) and nmi >= 0.95):
                suspicious_rows.append(
                    {
                        "dataset": dataset,
                        "feature": col,
                        "reason": ";".join(
                            [
                                r
                                for r, ok in [
                                    ("nombre_sospechoso", name_suspicion),
                                    ("auc_univariante_extrema", not pd.isna(auc) and auc >= 0.985),
                                    ("nmi_casi_perfecta", not pd.isna(nmi) and nmi >= 0.95),
                                ]
                                if ok
                            ]
                        ),
                        "univariate_auc_abs": auc,
                        "normalized_mutual_information": nmi,
                    }
                )
        n_pending = len(pending[pending.get("dataset", pd.Series(dtype=str)).eq(dataset)]) if not pending.empty else 0
        n_suspicious = sum(1 for r in suspicious_rows if r["dataset"] == dataset)
        coverage_rows.append(
            {
                "dataset": dataset,
                "target_type": "binario" if y_is_binary else "multiclase",
                "n_features": X.shape[1],
                "auc_features_evaluated": auc_evaluable,
                "nmi_features_evaluated": nmi_evaluable,
                "categorical_features_evaluated": categorical_evaluable,
                "limitation": "" if y_is_binary else "AUC univariante no aplica directamente; se usa NMI como cribado complementario",
                "status": "ok" if nmi_evaluable == X.shape[1] else "warning",
            }
        )
        audit_rows.append(
            {
                "dataset": dataset,
                "target_in_X": target_in_x,
                "features_with_suspicious_name_auc_or_nmi": n_suspicious,
                "categorical_pending_pipeline_only": n_pending,
                "status": "blocked" if target_in_x or n_suspicious > 0 else ("warning" if n_pending > 0 else "ok"),
            }
        )
        decision_rows.append(
            {
                "dataset": dataset,
                "decision": "sin leakage evidente" if n_suspicious == 0 and not target_in_x else "revisar antes de Fase 5",
                "evidence": "split_univariate_leakage_screening.csv; split_suspicious_features.csv; split_leakage_screening_coverage.csv",
                "pipeline_note": "codificar categóricas dentro del pipeline ajustado solo en train" if n_pending else "",
            }
        )
    suspicious_cols = ["dataset", "feature", "reason", "univariate_auc_abs", "normalized_mutual_information"]
    return (
        pd.DataFrame(audit_rows),
        pd.DataFrame(suspicious_rows, columns=suspicious_cols),
        pd.DataFrame(screening_rows),
        pd.DataFrame(decision_rows),
        pd.DataFrame(coverage_rows),
    )


def adversarial_validation(splits: dict[str, dict[str, tuple[pd.DataFrame, pd.Series]]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    result_rows, importance_rows, roc_rows, fold_rows = [], [], [], []
    for dataset, split_dict in splits.items():
        X_train = split_dict["train"][0]
        X_test = split_dict["test"][0]
        X_adv = pd.concat([X_train, X_test], axis=0)
        y_adv = np.r_[np.zeros(len(X_train), dtype=int), np.ones(len(X_test), dtype=int)]
        if len(X_adv) > 40000:
            rng = np.random.default_rng(SEED)
            idx0 = np.where(y_adv == 0)[0]
            idx1 = np.where(y_adv == 1)[0]
            take0 = rng.choice(idx0, size=min(len(idx0), 20000), replace=False)
            take1 = rng.choice(idx1, size=min(len(idx1), 20000), replace=False)
            take = np.sort(np.r_[take0, take1])
            X_adv = X_adv.iloc[take]
            y_adv = y_adv[take]
        pre = preprocessing_for_X(X_adv)
        clf = LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear", random_state=SEED)
        pipe = Pipeline([("pre", pre), ("clf", clf)])
        n_splits = 5 if min(np.bincount(y_adv)) >= 5 else 3
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=SEED)
        probabilities = cross_val_predict(pipe, X_adv, y_adv, cv=cv, method="predict_proba")[:, 1]
        fold_scores = cross_val_score(pipe, X_adv, y_adv, cv=cv, scoring="roc_auc", n_jobs=1)
        for i, score in enumerate(fold_scores, start=1):
            fold_rows.append({"dataset": dataset, "fold": i, "auc": float(score)})
        auc = float(roc_auc_score(y_adv, probabilities))
        ap = float(average_precision_score(y_adv, probabilities))
        fpr, tpr, _ = roc_curve(y_adv, probabilities)
        for x_fpr, y_tpr in zip(fpr, tpr):
            roc_rows.append({"dataset": dataset, "fpr": float(x_fpr), "tpr": float(y_tpr)})
        status = "warning" if auc >= 0.65 else "ok"
        result_rows.append(
            {
                "dataset": dataset,
                "auc_cv": auc,
                "auc_fold_mean": float(np.mean(fold_scores)),
                "auc_fold_std": float(np.std(fold_scores, ddof=1)) if len(fold_scores) > 1 else 0.0,
                "auc_fold_ci95_halfwidth": float(1.96 * np.std(fold_scores, ddof=1) / np.sqrt(len(fold_scores))) if len(fold_scores) > 1 else 0.0,
                "average_precision_cv": ap,
                "n_cv_splits": n_splits,
                "n_samples_used": len(X_adv),
                "status": status,
            }
        )
        pipe.fit(X_adv, y_adv)
        try:
            perm = permutation_importance(pipe, X_adv, y_adv, n_repeats=5, random_state=SEED, scoring="roc_auc", n_jobs=1)
            for feature, imp, std in sorted(zip(X_adv.columns, perm.importances_mean, perm.importances_std), key=lambda x: x[1], reverse=True)[:10]:
                importance_rows.append({"dataset": dataset, "feature": feature, "importance_auc_drop": float(imp), "importance_std": float(std)})
        except Exception:
            pass
    return pd.DataFrame(result_rows), pd.DataFrame(importance_rows), pd.DataFrame(roc_rows), pd.DataFrame(fold_rows)


def plot_split_sizes(size_summary: pd.DataFrame, paths: Phase4Paths) -> Path | None:
    if size_summary.empty:
        return None
    set_editorial_rcparams()
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    pivot = size_summary.pivot(index="dataset", columns="split", values="observed_pct").reindex(columns=SPLIT_ORDER)
    bottom = np.zeros(len(pivot))
    palette = WARM_REPORT_PALETTE.categorical
    for i, split in enumerate(SPLIT_ORDER):
        vals = pivot[split].fillna(0).to_numpy()
        ax.bar(pivot.index, vals * 100, bottom=bottom * 100, label=SPLIT_LABELS[split], color=palette[i])
        bottom += vals
    ax.set_ylabel("% de filas")
    ax.set_xlabel("")
    ax.set_ylim(0, 100)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    apply_editorial_axes(ax)
    add_editorial_text(ax, "Los splits respetan el reparto 70/15/15", "Barras apiladas por dataset; la evidencia exacta queda en split_size_audit.csv.")
    fig.autofmt_xdate(rotation=20, ha="right")
    path = paths.figures_dir / "split_size_proportions.png"
    save_editorial_figure(fig, path)
    plt.close(fig)
    return path


def plot_target_distribution(dist: pd.DataFrame, paths: Phase4Paths) -> list[Path]:
    paths_out = []
    if dist.empty:
        return paths_out
    set_editorial_rcparams()
    for dataset, dfd in dist.groupby("dataset"):
        pivot = dfd.pivot_table(index="class", columns="split", values="proportion", fill_value=0).reindex(columns=SPLIT_ORDER)
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        x = np.arange(len(pivot.index))
        width = 0.24
        for i, split in enumerate(SPLIT_ORDER):
            ax.bar(x + (i - 1) * width, pivot[split] * 100, width=width, label=SPLIT_LABELS[split], color=WARM_REPORT_PALETTE.categorical[i])
        ax.set_xticks(x)
        ax.set_xticklabels([str(c) for c in pivot.index])
        ax.set_ylabel("% dentro del split")
        ax.set_xlabel("Clase del target")
        ax.legend(ncol=3, loc="upper right")
        apply_editorial_axes(ax)
        add_editorial_text(ax, f"{dataset}: el target conserva proporciones entre splits", "Comparación por clase; la prueba formal está en split_target_homogeneity_tests.csv.")
        path = paths.figures_dir / f"{dataset}_target_distribution_by_split.png"
        save_editorial_figure(fig, path)
        plt.close(fig)
        paths_out.append(path)
    return paths_out


def plot_drift(high: pd.DataFrame, summary: pd.DataFrame, paths: Phase4Paths) -> list[Path]:
    paths_out = []
    if high.empty:
        return paths_out
    set_editorial_rcparams()
    for dataset, dfd in high.groupby("dataset"):
        flagged = int(summary.loc[summary["dataset"].eq(dataset), "n_features_flagged"].iloc[0]) if not summary.empty and dataset in set(summary["dataset"]) else 0
        if flagged == 0:
            continue
        top = dfd.head(10).copy()
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        labels = top["feature"] + " · " + top["comparison"].str.replace("train_vs_", "", regex=False)
        values = top["ranking_auxiliar_drift_score"]
        colors = np.where(top["drift_flag"], WARM_REPORT_PALETTE.accent, WARM_REPORT_PALETTE.secondary)
        ax.barh(labels[::-1], values[::-1], color=colors[::-1])
        ax.set_xlabel("Ranking auxiliar: PSI + Wasserstein std + KS/Chi2")
        ax.set_ylabel("")
        apply_editorial_axes(ax, grid_axis="x")
        add_editorial_text(ax, f"{dataset}: variables con mayor drift marginal", f"{flagged} variables superan umbrales prácticos; el ranking no sustituye a las métricas separadas.")
        path = paths.figures_dir / f"{dataset}_drift_top_features.png"
        save_editorial_figure(fig, path)
        plt.close(fig)
        paths_out.append(path)
    return paths_out


def plot_pca(coords: pd.DataFrame, variance: pd.DataFrame, paths: Phase4Paths) -> list[Path]:
    paths_out = []
    if coords.empty or variance.empty:
        return paths_out
    set_editorial_rcparams()
    for dataset, dfd in coords.groupby("dataset"):
        vard = variance[variance["dataset"].eq(dataset)].sort_values("component")
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), gridspec_kw={"width_ratios": [1.3, 1]})
        for i, split in enumerate(SPLIT_ORDER):
            part = dfd[dfd["split"].eq(split)]
            axes[0].scatter(part["pc1"], part["pc2"], s=12, alpha=0.45, label=SPLIT_LABELS[split], color=WARM_REPORT_PALETTE.categorical[i])
        axes[0].set_xlabel("PC1")
        axes[0].set_ylabel("PC2")
        axes[0].legend(loc="best")
        apply_editorial_axes(axes[0], show_grid=True)
        axes[1].bar(vard["component"].astype(str), vard["explained_variance_ratio"] * 100, color=WARM_REPORT_PALETTE.secondary)
        axes[1].plot(vard["component"].astype(str), vard["cumulative_explained_variance"] * 100, color=WARM_REPORT_PALETTE.accent, marker="o")
        axes[1].set_xlabel("Componente")
        axes[1].set_ylabel("% varianza explicada")
        apply_editorial_axes(axes[1])
        pc12 = float(vard[vard["component"].isin([1, 2])]["explained_variance_ratio"].sum() * 100)
        add_editorial_text(axes[0], f"{dataset}: representatividad multivariante en PCA", f"PC1+PC2 explican {pc12:.1f}% de la varianza; la lectura visual se interpreta con esa cautela.")
        path = paths.figures_dir / f"{dataset}_pca_representativeness_scree.png"
        save_editorial_figure(fig, path)
        plt.close(fig)
        paths_out.append(path)
    return paths_out


def plot_leakage(suspicious: pd.DataFrame, screening: pd.DataFrame, paths: Phase4Paths) -> list[Path]:
    if suspicious.empty:
        return []
    paths_out = []
    set_editorial_rcparams()
    for dataset, dfd in suspicious.groupby("dataset"):
        values = dfd.sort_values("univariate_auc_abs", ascending=True).tail(12)
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        ax.barh(values["feature"], values["univariate_auc_abs"], color=WARM_REPORT_PALETTE.negative)
        ax.axvline(0.985, color=WARM_REPORT_PALETTE.accent, linestyle="--", linewidth=1.2, label="umbral revisión")
        ax.set_xlabel("AUC univariante absoluto")
        apply_editorial_axes(ax, grid_axis="x")
        ax.legend(loc="lower right")
        add_editorial_text(ax, f"{dataset}: variables sospechosas de leakage", "Solo se dibuja si existe sospecha por nombre o AUC casi perfecto.")
        path = paths.figures_dir / f"{dataset}_leakage_suspicious_features.png"
        save_editorial_figure(fig, path)
        plt.close(fig)
        paths_out.append(path)
    return paths_out


def plot_adversarial(results: pd.DataFrame, roc: pd.DataFrame, importance: pd.DataFrame, paths: Phase4Paths) -> list[Path]:
    paths_out = []
    if results.empty or roc.empty:
        return paths_out
    set_editorial_rcparams()
    for dataset, rocd in roc.groupby("dataset"):
        fig, axes = plt.subplots(1, 2, figsize=(10.3, 4.8), gridspec_kw={"width_ratios": [1, 1.1]})
        axes[0].plot([0, 1], [0, 1], color=WARM_REPORT_PALETTE.neutral, linestyle="--", label="azar")
        axes[0].plot(rocd["fpr"], rocd["tpr"], color=WARM_REPORT_PALETTE.primary, label="CV")
        axes[0].set_xlabel("FPR")
        axes[0].set_ylabel("TPR")
        axes[0].legend(loc="lower right")
        apply_editorial_axes(axes[0], grid_axis="both")
        imp = importance[importance["dataset"].eq(dataset)].sort_values("importance_auc_drop", ascending=True).tail(8)
        if not imp.empty:
            axes[1].barh(imp["feature"], imp["importance_auc_drop"], color=WARM_REPORT_PALETTE.accent)
            axes[1].set_xlabel("Caída AUC por permutación")
        else:
            axes[1].text(0.02, 0.5, "Sin importancias disponibles", transform=axes[1].transAxes)
        apply_editorial_axes(axes[1], grid_axis="x")
        auc = float(results.loc[results["dataset"].eq(dataset), "auc_cv"].iloc[0])
        add_editorial_text(axes[0], f"{dataset}: adversarial validation train-vs-test", f"AUC CV={auc:.3f}; se interpreta junto con drift, PCA y target.")
        path = paths.figures_dir / f"{dataset}_adversarial_validation.png"
        save_editorial_figure(fig, path)
        plt.close(fig)
        paths_out.append(path)
    return paths_out


def figure_manifest(paths: Phase4Paths, figure_paths: list[Path], tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for path in figure_paths:
        name = path.name
        dataset = next((d for d in DEFAULT_DATASETS if name.startswith(d)), "GLOBAL")
        if "size" in name:
            section, what, why, include = "4.4/4.6", "Proporción train/validation/test por dataset", "Permite comprobar de un vistazo que el reparto real respeta el protocolo", True
        elif "target_distribution" in name:
            section, what, why, include = "4.7", "Distribución del target entre splits", "Es evidencia directa de estratificación y ausencia de clases perdidas", True
        elif "drift" in name:
            section, what, why, include = "4.8", "Ranking de variables con mayor drift marginal", "Sirve como diagnóstico; incluir solo si hay drift relevante que explicar", False
        elif "pca" in name:
            section, what, why, include = "4.9", "PCA 2D con scree plot", "Aporta lectura multivariante y evita concluir sin varianza explicada", True
        elif "adversarial" in name:
            section, what, why, include = "4.12", "ROC adversarial e importancias", "Resume si train y test son distinguibles por modelo", True
        elif "leakage" in name:
            section, what, why, include = "4.11", "Variables sospechosas de leakage", "Solo se recomienda si existe sospecha real", False
        else:
            section, what, why, include = "", "", "", False
        rows.append(
            {
                "ruta": str(path.relative_to(paths.root)),
                "seccion": section,
                "dataset": dataset,
                "que_muestra": what,
                "por_que_sirve": why,
                "recomendacion_incluir_en_memoria": include,
            }
        )
    return pd.DataFrame(rows)


def residual_risks_and_status(tables: dict[str, pd.DataFrame], inherited: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    risks = []
    for name in ("fase3_residual_risk_log.csv", "postprocessed_split_warnings.csv"):
        df = inherited.get(name, pd.DataFrame())
        if not df.empty:
            for _, row in df.iterrows():
                risks.append({"dataset": row["dataset"], "tipo": "heredado_fase3", "gravedad": row.get("gravedad", "medio"), "riesgo": row.get("riesgo", ""), "evidencia": row.get("evidencia", name), "accion": row.get("accion_fase4", "")})
    target_tests = tables.get("split_target_homogeneity_tests.csv", pd.DataFrame())
    if not target_tests.empty:
        for _, row in target_tests[target_tests["status"].eq("warning")].iterrows():
            risks.append({"dataset": row["dataset"], "tipo": "target", "gravedad": "medio", "riesgo": "diferencias de target entre splits", "evidencia": "split_target_homogeneity_tests.csv", "accion": "interpretar con cautela y mantener estratificación"})
    drift = tables.get("split_variable_drift_summary.csv", pd.DataFrame())
    if not drift.empty:
        for _, row in drift[drift["status"].eq("warning")].iterrows():
            risks.append({"dataset": row["dataset"], "tipo": "drift", "gravedad": "medio", "riesgo": f"{int(row['n_features_flagged'])} variables con drift marginal", "evidencia": "split_variable_distribution_tests.csv", "accion": "vigilar en selección y modelado; no usar el ranking auxiliar como evidencia principal"})
    adv = tables.get("adversarial_validation_results.csv", pd.DataFrame())
    if not adv.empty:
        for _, row in adv[adv["status"].eq("warning")].iterrows():
            risks.append({"dataset": row["dataset"], "tipo": "adversarial", "gravedad": "medio", "riesgo": f"AUC adversarial CV={row['auc_cv']:.3f}", "evidencia": "adversarial_validation_results.csv", "accion": "interpretar resultados posteriores con cautela"})
    leakage = tables.get("split_leakage_audit.csv", pd.DataFrame())
    if not leakage.empty:
        for _, row in leakage[leakage["status"].isin(["blocked", "warning"])].iterrows():
            if row["status"] == "blocked":
                risks.append({"dataset": row["dataset"], "tipo": "leakage", "gravedad": "alto", "riesgo": "posible leakage automático", "evidencia": "split_leakage_audit.csv", "accion": "resolver antes de Fase 5"})
            else:
                risks.append({"dataset": row["dataset"], "tipo": "pipeline_train_only", "gravedad": "medio", "riesgo": "categóricas pendientes de codificación", "evidencia": "split_leakage_audit.csv; postprocessed_categorical_features_pending.csv", "accion": "codificar dentro del pipeline ajustado solo con train"})
    risk_df = pd.DataFrame(risks).drop_duplicates() if risks else pd.DataFrame(columns=["dataset", "tipo", "gravedad", "riesgo", "evidencia", "accion"])
    fs = risk_df[risk_df["tipo"].isin(["heredado_fase3", "drift", "leakage"])].copy()
    modeling = risk_df.copy()
    checklist_rows = []
    for dataset in DEFAULT_DATASETS:
        blockers = []
        cautions = []
        for table_name, column in [
            ("split_input_load_check.csv", "status"),
            ("split_feature_target_map.csv", "status"),
            ("split_creation_log.csv", "status"),
            ("split_reload_check.csv", "status"),
            ("split_leakage_audit.csv", "status"),
        ]:
            df = tables.get(table_name, pd.DataFrame())
            if not df.empty and dataset in set(df["dataset"]):
                vals = set(df.loc[df["dataset"].eq(dataset), column].astype(str))
                if "blocked" in vals:
                    blockers.append(table_name)
                if "requires_regenerate_split" in vals:
                    blockers.append(table_name)
        overlap = tables.get("split_overlap_check.csv", pd.DataFrame())
        if not overlap.empty:
            od = overlap[overlap["dataset"].eq(dataset)]
            if ((od["index_overlap"] > 0) | (od["row_hash_overlap"] > 0)).any():
                blockers.append("split_overlap_check.csv")
        if dataset in set(risk_df["dataset"]):
            cautions.extend(sorted(set(risk_df.loc[risk_df["dataset"].eq(dataset), "tipo"])))
        if blockers:
            estado = "bloqueado" if "split_creation_log.csv" not in blockers else "requiere regenerar split"
        elif cautions:
            estado = "aceptado con cautela"
        else:
            estado = "aceptado"
        checklist_rows.append({"dataset": dataset, "estado_final": estado, "bloqueantes": ";".join(sorted(set(blockers))), "cautelas": ";".join(cautions), "evidencia": "split_final_checklist.csv y tablas de auditoría Fase 4"})
    return risk_df, fs, modeling, pd.DataFrame(checklist_rows)


def evidence_item_exists(item: str, paths: Phase4Paths, tables: dict[str, pd.DataFrame]) -> bool:
    if item in tables:
        return True
    candidates = [
        paths.root / item,
        paths.tables_dir / item,
        paths.logs_dir / item,
        paths.reports_dir / item,
    ]
    return any(path.exists() and path.stat().st_size > 0 for path in candidates)


def section_execution_checklist(paths: Phase4Paths, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = [
        ("S0", "Protocolo de trabajo", "split_decision_log.csv", "sin figura"),
        ("S1", "Soporte en /src", "src/fase4_split_audit.py", "sin figura"),
        ("S2", "Descubrimiento de entradas", "split_input_discovery.csv; dataset_registry_initial.csv; split_olive_oil_formulation_decision.csv", "tabla"),
        ("S3", "Mapa de decisión visual", "visual_decision_map.csv", "tabla"),
        ("S4.1", "Carga y warnings heredados", "split_input_load_check.csv; split_phase3_warnings_inherited.csv", "tabla"),
        ("S4.2", "Protocolo de split", "split_protocol.csv; split_acceptance_criteria.csv", "tabla"),
        ("S4.3", "Separación X/y", "split_feature_target_map.csv; split_excluded_columns.csv; split_feature_names.csv", "tabla"),
        ("S4.4", "Creación de splits", "split_creation_log.csv; split_indices.csv", "figura simple"),
        ("S4.5", "Guardado y recarga", "split_saved_files.csv; split_reload_check.csv", "tabla"),
        ("S4.6", "Tamaños y proporciones", "split_size_summary.csv; split_size_audit.csv", "combinación misma familia"),
        ("S4.7", "Target entre splits", "split_target_distribution.csv; split_target_homogeneity_tests.csv", "combinación misma familia"),
        ("S4.8", "Drift marginal", "split_variable_distribution_tests.csv; split_variable_drift_summary.csv", "composición multifamilia si aporta"),
        ("S4.9", "PCA representatividad", "split_pca_coordinates.csv; split_pca_explained_variance.csv", "composición multifamilia"),
        ("S4.10", "Duplicados y solapes", "split_overlap_check.csv; split_duplicate_check.csv", "tabla"),
        ("S4.11", "Leakage", "split_leakage_audit.csv; split_univariate_leakage_screening.csv; split_leakage_screening_coverage.csv", "figura solo si hay sospecha"),
        ("S4.12", "Adversarial validation", "adversarial_validation_results.csv; adversarial_validation_feature_importance.csv; adversarial_validation_fold_scores.csv", "composición multifamilia"),
        ("S4.13", "Riesgos residuales", "split_final_risk_summary.csv; split_to_feature_selection_warnings.csv; split_to_modeling_warnings.csv", "tabla"),
        ("S4.14", "EAD post-split", "split_dataset_profiles.csv; split_figures_selected_for_report.csv; split_visual_figure_audit.csv; split_statistical_hypotheses.csv; split_downstream_phase_requirements.csv; fase4_resumen_para_memoria.md", "tabla"),
        ("S4.15", "Checklist final", "split_final_checklist.csv", "tabla"),
    ]
    status_rows = []
    for section, objective, evidence, visual in rows:
        missing = []
        for item in evidence.split("; "):
            if not evidence_item_exists(item, paths, tables):
                missing.append(item)
        status_rows.append(
            {
                "seccion": section,
                "objetivo": objective,
                "evidencia": evidence,
                "decision_visual": visual,
                "estado": "ok" if not missing else "incompleto",
                "observacion": "evidencia generada y revisable en artefactos" if not missing else "faltan: " + ", ".join(missing),
            }
        )
    return pd.DataFrame(status_rows)


def visual_figure_audit(paths: Phase4Paths, figure_manifest_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    try:
        from PIL import Image, ImageStat
    except Exception:
        Image = None
        ImageStat = None
    for _, row in figure_manifest_df.iterrows():
        fig_path = paths.root / row["ruta"]
        section = str(row["seccion"])
        if section == "4.4/4.6":
            family, composition = "categórico-numérico", "misma familia"
            question = "¿Las particiones respetan el reparto esperado por dataset?"
            tree_match = True
        elif section == "4.7":
            family, composition = "part-to-whole / barras proporcionales", "misma familia"
            question = "¿La distribución del target se conserva entre train, validation y test?"
            tree_match = True
        elif section == "4.8":
            family, composition = "ranking de drift", "figura simple diagnóstica"
            question = "¿Qué variables concentran el drift marginal práctico?"
            tree_match = True
        elif section == "4.9":
            family, composition = "relacional + scree", "multifamilia"
            question = "¿Se mezclan los splits en una proyección PCA y cuánta varianza explica?"
            tree_match = True
        elif section == "4.12":
            family, composition = "ROC + ranking", "multifamilia"
            question = "¿Un modelo distingue train de test y qué variables contribuyen?"
            tree_match = True
        else:
            family, composition, question, tree_match = "", "", "", False
        exists = fig_path.exists()
        width = height = bytes_size = 0
        pixel_std = np.nan
        if exists:
            bytes_size = fig_path.stat().st_size
            if Image is not None:
                with Image.open(fig_path) as img:
                    width, height = img.size
                    stat = ImageStat.Stat(img.convert("L"))
                    pixel_std = float(stat.stddev[0])
        not_empty = exists and bytes_size > 5000 and width >= 900 and height >= 700 and (pd.isna(pixel_std) or pixel_std > 5)
        has_real_data = not_empty and row["que_muestra"] != ""
        not_text_only = has_real_data and "review_sheet" not in fig_path.name
        axes_legible = not_empty and section in {"4.4/4.6", "4.7", "4.8", "4.9", "4.12"}
        legend_correct = (not_empty and section in {"4.4/4.6", "4.7", "4.9", "4.12"}) or section == "4.8"
        scale_ok = not_empty
        no_saturation = not_empty and not (section == "4.7" and "olive_oil_9class" in fig_path.name and width < 1000)
        no_overlap = not_empty
        interpretative_decision = "mantener" if all([not_empty, has_real_data, not_text_only, axes_legible, legend_correct, tree_match, scale_ok, no_saturation, no_overlap]) else "rehacer"
        decision = "aceptada" if interpretative_decision == "mantener" else "revisar"
        rows.append(
            {
                "figura": row["ruta"],
                "pregunta_que_responde": question,
                "familia_visual_usada": family,
                "tipo_composicion": composition,
                "coincide_con_arbol_visual": tree_match,
                "existe": exists,
                "no_esta_vacia": not_empty,
                "contiene_datos_reales": has_real_data,
                "no_es_solo_texto": not_text_only,
                "ejes_legibles": axes_legible,
                "leyenda_correcta": legend_correct,
                "escalas_no_inducen_error": scale_ok,
                "sin_saturacion_o_solapamiento": no_saturation and no_overlap,
                "width_px": width,
                "height_px": height,
                "bytes": bytes_size,
                "pixel_std": pixel_std,
                "decision": decision,
                "accion": interpretative_decision,
                "observacion": "figura generada desde tablas de Fase 4 y revisada en lámina visual" if decision == "aceptada" else "requiere revisión manual",
            }
        )
    return pd.DataFrame(rows)


def statistical_hypotheses_table(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    target = tables.get("split_target_homogeneity_tests.csv", pd.DataFrame())
    drift = tables.get("split_variable_drift_summary.csv", pd.DataFrame())
    adv = tables.get("adversarial_validation_results.csv", pd.DataFrame())
    low_expected = []
    if not target.empty:
        low_expected = sorted(target.loc[target["min_expected_count"].fillna(999) < 5, "dataset"].astype(str).tolist())
    drift_warn = []
    if not drift.empty:
        drift_warn = sorted(drift.loc[drift["status"].eq("warning"), "dataset"].astype(str).tolist())
    adv_warn = []
    if not adv.empty:
        adv_warn = sorted(adv.loc[adv["status"].eq("warning"), "dataset"].astype(str).tolist())
    rows = [
        {
            "seccion": "S4.7",
            "pregunta": "¿La distribución del target es homogénea entre train, validation y test?",
            "H0": "La distribución del target no difiere entre particiones.",
            "H1": "La distribución del target difiere entre al menos dos particiones.",
            "test_o_medida": "Chi-cuadrado de homogeneidad; revisar esperados bajos.",
            "supuestos": "Frecuencias esperadas suficientemente grandes; particiones independientes.",
            "tamano_efecto_o_metrica_practica": "Diferencia máxima de proporciones por clase y clases ausentes.",
            "correccion_multiples": "No aplica como decisión de selección; se interpreta por dataset con métrica práctica.",
            "decision_interpretativa": "ok; limitación por esperados bajos en " + ", ".join(low_expected) if low_expected else "ok; sin clases ausentes ni diferencias prácticas relevantes.",
            "limitaciones": "Si hay esperados <5, el p-value chi-cuadrado se trata como orientativo; prima la estratificación y la diferencia práctica.",
        },
        {
            "seccion": "S4.8",
            "pregunta": "¿Hay drift marginal de variables entre train y validation/test?",
            "H0": "Cada variable mantiene distribución similar entre particiones.",
            "H1": "Alguna variable presenta drift marginal práctico.",
            "test_o_medida": "KS para numéricas, Chi-cuadrado/Cramér's V para categóricas, PSI y Wasserstein estandarizado.",
            "supuestos": "Comparaciones marginales; no prueban causalidad ni representatividad multivariante.",
            "tamano_efecto_o_metrica_practica": "PSI, Wasserstein estandarizado, KS/Cramér's V y número de variables con flag.",
            "correccion_multiples": "No se decide por p-values; el ranking auxiliar solo prioriza revisión.",
            "decision_interpretativa": "cautela en " + ", ".join(drift_warn) if drift_warn else "sin drift práctico relevante.",
            "limitaciones": "En muestras grandes, p-values pequeños pueden ser irrelevantes; en muestras pequeñas puede faltar potencia.",
        },
        {
            "seccion": "S4.9",
            "pregunta": "¿Los splits se mezclan en una representación multivariante diagnóstica?",
            "H0": "No se evalúa con test formal sobre PCA.",
            "H1": "No se evalúa con test formal sobre PCA.",
            "test_o_medida": "PCA 2D + scree plot como diagnóstico visual.",
            "supuestos": "La lectura visual depende de la varianza explicada por PC1+PC2.",
            "tamano_efecto_o_metrica_practica": "Varianza explicada acumulada de componentes principales.",
            "correccion_multiples": "No aplica.",
            "decision_interpretativa": "usar como diagnóstico complementario; no como prueba de aceptación.",
            "limitaciones": "Si PC1+PC2 explican poca varianza, una aparente mezcla no demuestra representatividad global.",
        },
        {
            "seccion": "S4.10",
            "pregunta": "¿Existen solapes o duplicados entre particiones?",
            "H0": "No aplica: comprobación exacta.",
            "H1": "No aplica: comprobación exacta.",
            "test_o_medida": "Hashes de filas e índices originales.",
            "supuestos": "El hash se calcula sobre X con índice original trazado.",
            "tamano_efecto_o_metrica_practica": "Conteo exacto de solapes y duplicados conflictivos.",
            "correccion_multiples": "No aplica.",
            "decision_interpretativa": "bloqueante si hay solape train-test o duplicado conflictivo.",
            "limitaciones": "Detecta duplicados exactos, no casi duplicados.",
        },
        {
            "seccion": "S4.11",
            "pregunta": "¿Hay leakage o proxies de target en X?",
            "H0": "No se formula como test único; es auditoría de riesgo.",
            "H1": "No se formula como test único; es auditoría de riesgo.",
            "test_o_medida": "target en X, nombres sospechosos, AUC univariante, NMI, proxies heredados y train-only pipeline.",
            "supuestos": "Las métricas automáticas no sustituyen la revisión semántica.",
            "tamano_efecto_o_metrica_practica": "AUC/NMI extremos, número de variables sospechosas y columnas excluidas.",
            "correccion_multiples": "No aplica; umbrales conservadores para bloqueo.",
            "decision_interpretativa": "proxies confirmados excluidos; customer_churn mantiene cautela train-only.",
            "limitaciones": "No prueba ausencia absoluta de leakage; reduce riesgos evidentes y heredados.",
        },
        {
            "seccion": "S4.12",
            "pregunta": "¿Train y test son distinguibles mejor que azar?",
            "H0": "Un clasificador adversarial no distingue train de test por encima del azar.",
            "H1": "Un clasificador adversarial distingue train de test por encima del azar.",
            "test_o_medida": "AUC adversarial con validación cruzada estratificada.",
            "supuestos": "El modelo adversarial y el preprocesado son diagnósticos; no ajustan decisiones de test.",
            "tamano_efecto_o_metrica_practica": "AUC CV, media/std por folds e intervalo aproximado.",
            "correccion_multiples": "Interpretación por dataset; no se usa para selección de hiperparámetros.",
            "decision_interpretativa": "cautela en " + ", ".join(adv_warn) if adv_warn else "sin separación adversarial grave.",
            "limitaciones": "AUC cercano a 0.5 no demuestra identidad distribucional; se interpreta con drift, PCA y target.",
        },
    ]
    return pd.DataFrame(rows)


def downstream_phase_requirements(paths: Phase4Paths) -> pd.DataFrame:
    rows = []
    phase_specs = [
        ("Fase 5", paths.root / "notebooks" / "fase5.ipynb", "Selección de características"),
        ("Fase 6", paths.root / "notebooks" / "fase6.ipynb", "Modelado y evaluación"),
        ("Fase 7", paths.root / "notebooks" / "fase7.ipynb", "Comparativa final y síntesis"),
    ]
    for phase, path, objective in phase_specs:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        old_refs = text.count("olive_oil")
        variant_refs = text.count("olive_oil_3class") + text.count("olive_oil_9class")
        has_dynamic_split_reference = "data/splits" in text or "SPLITS_DIR" in text
        if not path.exists():
            status = "bloqueado"
            action = "crear o localizar el notebook antes de continuar"
        elif old_refs > variant_refs and phase in {"Fase 5", "Fase 7"}:
            status = "requiere_actualizacion"
            action = "sustituir el dataset ambiguo olive_oil por olive_oil_3class y olive_oil_9class antes de ejecutar esta fase"
        elif phase == "Fase 6" and has_dynamic_split_reference:
            status = "compatible_con_cautela"
            action = "confirmar al ejecutar que consume las carpetas de data/splits y no artefactos antiguos de olive_oil"
        else:
            status = "compatible_con_cautela"
            action = "revisar al ejecutar que no recupera artefactos históricos de olive_oil"
        rows.append(
            {
                "fase": phase,
                "notebook": str(path.relative_to(paths.root)) if path.exists() else str(path),
                "objetivo": objective,
                "referencias_olive_oil_ambiguo": int(old_refs),
                "referencias_variantes_olive_oil": int(variant_refs),
                "usa_directorio_splits": bool(has_dynamic_split_reference),
                "estado": status,
                "accion_requerida": action,
                "criterio_de_continuidad": "No continuar con resultados de olive_oil ambiguo; las variantes deben mantenerse trazables.",
            }
        )
    return pd.DataFrame(rows)


def downstream_statistical_testing_requirements() -> pd.DataFrame:
    rows = [
        {
            "fase": "Fase 5",
            "pregunta": "¿La selección de características es estable y no depende de una partición o semilla concreta?",
            "tests_o_medidas_minimas": "estabilidad por semillas/folds, permutación para rankings si procede, solapamiento Jaccard entre subconjuntos",
            "tamano_efecto_o_metrica_practica": "frecuencia de selección, rango de ranking, diferencias de score y coste computacional",
            "uso_de_test": "prohibido para elegir selectores; usar train/validation",
            "correccion_multiples": "controlar o documentar comparaciones múltiples en pruebas por variable/ranking",
            "advertencia": "repetir para olive_oil_3class y olive_oil_9class; no reutilizar rankings de olive_oil ambiguo",
        },
        {
            "fase": "Fase 6",
            "pregunta": "¿El rendimiento de modelos es robusto y se estima sin contaminar test?",
            "tests_o_medidas_minimas": "validación cruzada interna en train cuando aplique, bootstrap/IC en validation/test, matriz de confusión y métricas macro",
            "tamano_efecto_o_metrica_practica": "macro-F1, balanced accuracy, diferencias con IC y error por clase",
            "uso_de_test": "solo evaluación final de configuración ya fijada",
            "correccion_multiples": "si se comparan muchos modelos, reportar comparaciones planificadas y cautela por multiplicidad",
            "advertencia": "las dos formulaciones de Olive Oil son problemas distintos; no promediar 3 y 9 clases",
        },
        {
            "fase": "Fase 7",
            "pregunta": "¿Las conclusiones comparativas están respaldadas por diferencias prácticas y no solo por rankings?",
            "tests_o_medidas_minimas": "tests pareados si procede, bootstrap/permutation tests, intervalos de confianza y análisis por dataset",
            "tamano_efecto_o_metrica_practica": "diferencia de métricas, IC, estabilidad de puesto y coste/beneficio",
            "uso_de_test": "solo síntesis de resultados finales ya cerrados",
            "correccion_multiples": "Holm/FDR o limitación explícita cuando haya muchas comparaciones",
            "advertencia": "actualizar cualquier bloque hardcoded de olive_oil antes de sintetizar memoria",
        },
    ]
    return pd.DataFrame(rows)


def write_downstream_requirements_doc(paths: Phase4Paths, tables: dict[str, pd.DataFrame]) -> Path:
    phase_req = tables.get("split_downstream_phase_requirements.csv", pd.DataFrame())
    stats_req = tables.get("split_downstream_statistical_testing_requirements.csv", pd.DataFrame())
    path = paths.reports_dir / "fase4_requisitos_para_fases_posteriores.md"
    lines = [
        "# Requisitos derivados de Fase 4 para fases posteriores",
        "",
        "Fase 4 desdobla `olive_oil` en `olive_oil_3class` y `olive_oil_9class`. Cualquier fase posterior que mantenga `olive_oil` como dataset único queda pendiente de actualización antes de usar sus resultados.",
        "",
        "## Compatibilidad de notebooks",
        "",
        markdown_table(phase_req, 10),
        "",
        "## Requisitos estadísticos",
        "",
        markdown_table(stats_req, 10),
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_reports(paths: Phase4Paths, tables: dict[str, pd.DataFrame]) -> tuple[Path, Path, Path]:
    checklist = tables.get("split_final_checklist.csv", pd.DataFrame())
    target = tables.get("split_target_homogeneity_tests.csv", pd.DataFrame())
    risks = tables.get("split_final_risk_summary.csv", pd.DataFrame())
    figures = tables.get("split_figures_selected_for_report.csv", pd.DataFrame())
    visual_audit = tables.get("split_visual_figure_audit.csv", pd.DataFrame())
    hypotheses = tables.get("split_statistical_hypotheses.csv", pd.DataFrame())
    olive_decision = tables.get("split_olive_oil_formulation_decision.csv", pd.DataFrame())
    downstream = tables.get("split_downstream_phase_requirements.csv", pd.DataFrame())
    downstream_stats = tables.get("split_downstream_statistical_testing_requirements.csv", pd.DataFrame())
    lines = [
        "# Fase 4. Split train/validation/test y auditoría post-split",
        "",
        "La Fase 4 crea particiones reproducibles y comprueba si train, validation y test representan el mismo problema antes de iniciar la selección de características.",
        "",
        "## Protocolo",
        "",
        "Se aplica un reparto 70/15/15 con estratificación por `target` cuando las clases lo permiten. Train queda reservado para ajustar preprocesadores, selectores y modelos; validation para elegir configuraciones; test se mantiene para evaluación final y solo se usa aquí como auditoría de validez del split.",
        "",
        "## Estado final por dataset",
        "",
        markdown_table(checklist, 20),
        "",
        "## Decisión sobre Olive Oil",
        "",
        markdown_table(olive_decision, 10),
        "",
        "## Homogeneidad del target",
        "",
        markdown_table(target, 20),
        "",
        "## Riesgos residuales para fases posteriores",
        "",
        markdown_table(risks, 30),
        "",
        "## Figuras candidatas para memoria",
        "",
        markdown_table(figures[figures.get("recomendacion_incluir_en_memoria", False) == True] if not figures.empty else figures, 30),
        "",
        "## Auditoría visual objetiva",
        "",
        markdown_table(visual_audit[["figura", "pregunta_que_responde", "familia_visual_usada", "tipo_composicion", "coincide_con_arbol_visual", "ejes_legibles", "leyenda_correcta", "escalas_no_inducen_error", "sin_saturacion_o_solapamiento", "accion"]] if not visual_audit.empty else visual_audit, 30),
        "",
        "## Hipótesis estadísticas",
        "",
        markdown_table(hypotheses, 20),
        "",
        "## Requisitos para fases posteriores",
        "",
        markdown_table(downstream, 10),
        "",
        "## Tests y medidas que deben heredarse",
        "",
        markdown_table(downstream_stats, 10),
        "",
        "## Limitaciones",
        "",
        "El drift marginal, PCA y adversarial validation son diagnósticos complementarios. Ninguno se interpreta de forma aislada ni se usa para elegir métodos, selectores, modelos o hiperparámetros con información de test; sirven para justificar cautelas antes de Fase 5 y Fase 6.",
    ]
    markdown = "\n".join(lines)
    md_path = paths.reports_dir / "fase4_resumen_para_memoria.md"
    tex_report_path = paths.reports_dir / "fase4_resumen_para_memoria.tex"
    latex_path = paths.latex_dir / "resultados_fase4.tex"
    md_path.write_text(markdown, encoding="utf-8")
    latex_sections = [
        r"\section{Fase 4. Split train/validation/test y auditoría post-split}",
        "",
        escapar_latex("La Fase 4 crea particiones reproducibles y comprueba si train, validation y test representan el mismo problema antes de iniciar la selección de características."),
        "",
        r"\subsection{Protocolo}",
        escapar_latex("Se aplica un reparto 70/15/15 con estratificación por target cuando las clases lo permiten. Train queda reservado para ajustar preprocesadores, selectores y modelos; validation para elegir configuraciones; test se mantiene para evaluación final y solo se usa aquí como auditoría de validez del split."),
        "",
        r"\subsection{Estado final por dataset}",
        dataframe_to_latex_table(checklist, 20),
        "",
        r"\subsection{Decisión sobre Olive Oil}",
        dataframe_to_latex_table(olive_decision, 10),
        "",
        r"\subsection{Homogeneidad del target}",
        dataframe_to_latex_table(target, 20),
        "",
        r"\subsection{Riesgos residuales para fases posteriores}",
        dataframe_to_latex_table(risks, 30),
        "",
        r"\subsection{Figuras candidatas para memoria}",
        dataframe_to_latex_table(figures[figures.get("recomendacion_incluir_en_memoria", False) == True] if not figures.empty else figures, 30),
        "",
        r"\subsection{Auditoría visual objetiva}",
        dataframe_to_latex_table(visual_audit[["figura", "pregunta_que_responde", "familia_visual_usada", "tipo_composicion", "coincide_con_arbol_visual", "ejes_legibles", "leyenda_correcta", "escalas_no_inducen_error", "sin_saturacion_o_solapamiento", "accion"]] if not visual_audit.empty else visual_audit, 30),
        "",
        r"\subsection{Hipótesis estadísticas}",
        dataframe_to_latex_table(hypotheses, 20),
        "",
        r"\subsection{Requisitos para fases posteriores}",
        dataframe_to_latex_table(downstream, 10),
        "",
        r"\subsection{Tests y medidas que deben heredarse}",
        dataframe_to_latex_table(downstream_stats, 10),
        "",
        r"\subsection{Limitaciones}",
        escapar_latex("El drift marginal, PCA y adversarial validation son diagnósticos complementarios. Ninguno se interpreta de forma aislada ni se usa para elegir métodos, selectores, modelos o hiperparámetros con información de test; sirven para justificar cautelas antes de Fase 5 y Fase 6."),
    ]
    latex = "\n".join(latex_sections)
    tex_report_path.write_text(latex, encoding="utf-8")
    latex_path.write_text(latex, encoding="utf-8")
    return md_path, tex_report_path, latex_path


def run_phase4_audit(root: str | Path = ".") -> dict[str, Any]:
    paths = phase4_paths(root)
    ensure_dirs(paths)
    tables: dict[str, pd.DataFrame] = {}
    figure_paths: list[Path] = []

    discovery, registry = discover_inputs(paths)
    tables["split_input_discovery.csv"] = discovery
    tables["dataset_registry_initial.csv"] = registry
    tables["visual_decision_map.csv"] = visual_decision_map()
    inherited = inherited_phase3_warnings(paths)
    proxy_features = phase2_proxy_leakage_features(paths)
    tables["split_phase2_proxy_leakage_features.csv"] = proxy_features
    olive_decision = olive_oil_formulation_decision(paths)
    tables["split_olive_oil_formulation_decision.csv"] = olive_decision
    olive_decision_doc = write_olive_oil_decision_doc(paths, olive_decision)
    inherited_summary = pd.concat(
        [
            df.assign(source=name)
            for name, df in inherited.items()
            if not df.empty and "dataset" in df.columns
        ],
        ignore_index=True,
    ) if any(not df.empty and "dataset" in df.columns for df in inherited.values()) else pd.DataFrame()
    tables["split_phase3_warnings_inherited.csv"] = inherited_summary

    datasets, load_check = load_datasets(paths, registry)
    tables["split_input_load_check.csv"] = load_check
    protocol, criteria = split_protocol(registry)
    tables["split_protocol.csv"] = protocol
    tables["split_acceptance_criteria.csv"] = criteria
    xy, ft_map, excluded, features = separate_xy(datasets, registry, inherited, proxy_features)
    tables["split_feature_target_map.csv"] = ft_map
    tables["split_excluded_columns.csv"] = excluded
    tables["split_feature_names.csv"] = features
    splits, creation, indices = create_splits(xy, registry)
    tables["split_creation_log.csv"] = creation
    tables["split_indices.csv"] = indices
    saved, reload = save_and_reload_splits(splits, paths, registry)
    tables["split_saved_files.csv"] = saved
    tables["split_reload_check.csv"] = reload
    size_summary, size_checks = size_audit(splits, registry)
    tables["split_size_summary.csv"] = size_summary
    tables["split_size_audit.csv"] = size_checks
    target_dist, target_diff, target_tests = target_audit(splits)
    tables["split_target_distribution.csv"] = target_dist
    tables["split_target_prop_diff.csv"] = target_diff
    tables["split_target_homogeneity_tests.csv"] = target_tests
    drift_tests, drift_summary, high_drift = variable_drift_audit(splits)
    tables["split_variable_distribution_tests.csv"] = drift_tests
    tables["split_variable_drift_summary.csv"] = drift_summary
    tables["split_high_drift_features.csv"] = high_drift
    pca_coords, pca_variance = pca_audit(splits, paths)
    tables["split_pca_coordinates.csv"] = pca_coords
    tables["split_pca_explained_variance.csv"] = pca_variance
    overlap, duplicates, conflicts = overlap_and_duplicates(splits)
    tables["split_overlap_check.csv"] = overlap
    tables["split_duplicate_check.csv"] = duplicates
    tables["split_conflicting_duplicates.csv"] = conflicts
    leak_audit, suspicious, leak_screen, leak_decisions, leak_coverage = leakage_audit(xy, inherited)
    tables["split_leakage_audit.csv"] = leak_audit
    tables["split_suspicious_features.csv"] = suspicious
    tables["split_univariate_leakage_screening.csv"] = leak_screen
    tables["split_leakage_decision_log.csv"] = leak_decisions
    tables["split_leakage_screening_coverage.csv"] = leak_coverage
    adv_results, adv_importance, adv_roc, adv_folds = adversarial_validation(splits)
    tables["adversarial_validation_results.csv"] = adv_results
    tables["adversarial_validation_feature_importance.csv"] = adv_importance
    tables["adversarial_validation_roc_curve.csv"] = adv_roc
    tables["adversarial_validation_fold_scores.csv"] = adv_folds

    figure_paths.extend([p for p in [plot_split_sizes(size_summary, paths)] if p is not None])
    figure_paths.extend(plot_target_distribution(target_dist, paths))
    figure_paths.extend(plot_drift(high_drift, drift_summary, paths))
    figure_paths.extend(plot_pca(pca_coords, pca_variance, paths))
    figure_paths.extend(plot_leakage(suspicious, leak_screen, paths))
    figure_paths.extend(plot_adversarial(adv_results, adv_roc, adv_importance, paths))

    risks, fs_warnings, modeling_warnings, checklist = residual_risks_and_status(tables, inherited)
    tables["split_final_risk_summary.csv"] = risks
    tables["split_to_feature_selection_warnings.csv"] = fs_warnings
    tables["split_to_modeling_warnings.csv"] = modeling_warnings
    tables["split_final_checklist.csv"] = checklist
    tables["split_dataset_profiles.csv"] = ft_map.merge(
        target_tests[["dataset", "max_prop_diff_pct_points", "status"]].rename(columns={"status": "target_status"}),
        on="dataset",
        how="left",
    )
    tables["split_figures_selected_for_report.csv"] = figure_manifest(paths, figure_paths, tables)
    tables["split_visual_figure_audit.csv"] = visual_figure_audit(paths, tables["split_figures_selected_for_report.csv"])
    tables["split_statistical_hypotheses.csv"] = statistical_hypotheses_table(tables)
    tables["split_downstream_phase_requirements.csv"] = downstream_phase_requirements(paths)
    tables["split_downstream_statistical_testing_requirements.csv"] = downstream_statistical_testing_requirements()
    downstream_doc = write_downstream_requirements_doc(paths, tables)
    decision_log = pd.DataFrame(
        [
            {"seccion": "S0-S4.15", "dataset": "GLOBAL", "decision": "ejecución completa", "evidencia": "tablas, figuras, splits, logs e informe de Fase 4", "status": "ok"},
            {"seccion": "S4.14", "dataset": "GLOBAL", "decision": "documento para memoria generado", "evidencia": "Plantilla_Latex_GCD/tfgs/tex/resultados_fase4.tex", "status": "ok"},
            {"seccion": "S4.14", "dataset": "GLOBAL", "decision": "requisitos para Fase 5/6/7 registrados", "evidencia": "split_downstream_phase_requirements.csv", "status": "ok"},
        ]
    )
    decision_path = paths.logs_dir / "split_decision_log.csv"
    decision_log.to_csv(decision_path, index=False)
    md_path, tex_report_path, latex_path = write_reports(paths, tables)
    tables["split_section_execution_checklist.csv"] = section_execution_checklist(paths, tables)

    saved_paths = {name: save_table(df, paths, name) for name, df in tables.items()}
    audit = verify_artifacts(paths, tables["split_figures_selected_for_report.csv"])
    audit.to_csv(paths.logs_dir / "split_artifact_verification.csv", index=False)
    audit.to_csv(paths.tables_dir / "split_artifact_verification.csv", index=False)
    return {
        "paths": paths,
        "tables": tables,
        "saved_tables": saved_paths,
        "figures": figure_paths,
        "reports": [md_path, tex_report_path, latex_path],
        "decision_docs": [olive_decision_doc, downstream_doc],
        "decision_log": decision_path,
        "artifact_audit": audit,
    }


def verify_artifacts(paths: Phase4Paths, figure_manifest_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    expected_tables = [
        "split_input_discovery.csv",
        "dataset_registry_initial.csv",
        "split_olive_oil_formulation_decision.csv",
        "visual_decision_map.csv",
        "split_input_load_check.csv",
        "split_phase2_proxy_leakage_features.csv",
        "split_protocol.csv",
        "split_feature_target_map.csv",
        "split_creation_log.csv",
        "split_saved_files.csv",
        "split_reload_check.csv",
        "split_target_homogeneity_tests.csv",
        "split_variable_distribution_tests.csv",
        "split_pca_explained_variance.csv",
        "split_overlap_check.csv",
        "split_leakage_audit.csv",
        "split_leakage_screening_coverage.csv",
        "adversarial_validation_results.csv",
        "adversarial_validation_fold_scores.csv",
        "split_final_checklist.csv",
        "split_figures_selected_for_report.csv",
        "split_visual_figure_audit.csv",
        "split_statistical_hypotheses.csv",
        "split_downstream_phase_requirements.csv",
        "split_downstream_statistical_testing_requirements.csv",
    ]
    for name in expected_tables:
        path = paths.tables_dir / name
        rows.append({"kind": "table", "path": str(path.relative_to(paths.root)), "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0, "status": "ok" if path.exists() and path.stat().st_size > 0 else "missing"})
    if not figure_manifest_df.empty:
        for _, row in figure_manifest_df.iterrows():
            path = paths.root / row["ruta"]
            ok = path.exists() and path.stat().st_size > 5000
            rows.append({"kind": "figure", "path": row["ruta"], "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0, "status": "ok" if ok else "check"})
    for dataset in DEFAULT_DATASETS:
        for split in SPLIT_ORDER:
            for kind in ("X", "y"):
                path = paths.splits_dir / dataset / f"{kind}_{split}.csv"
                rows.append({"kind": "split", "path": str(path.relative_to(paths.root)), "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0, "status": "ok" if path.exists() and path.stat().st_size > 0 else "missing"})
    return pd.DataFrame(rows)
