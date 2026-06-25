from __future__ import annotations

import math
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier
import warnings


RANDOM_STATE = 20260607
N_BOOTSTRAP = 400
N_PAIRWISE_PERMUTATIONS = 2000
N_LABEL_PERMUTATIONS = 500
SHAP_MAX_EXPLAIN_ROWS = 1200
DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]
ROSTER_12 = [
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
]
MODEL_NAMES = ["logistic_regression", "linear_svm", "random_forest", "xgboost"]
BINARY_DATASETS = {"breast_cancer_wisconsin", "customer_churn"}


@dataclass(frozen=True)
class Phase6Paths:
    root: Path
    tables: Path
    figures: Path
    predictions: Path
    logs: Path


class LabelEncodedXGBClassifier(BaseEstimator, ClassifierMixin):
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 5,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        tree_method: str = "hist",
        eval_metric: str = "logloss",
        random_state: int = RANDOM_STATE,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.tree_method = tree_method
        self.eval_metric = eval_metric
        self.random_state = random_state

    def fit(self, X: np.ndarray, y: pd.Series | np.ndarray):
        self.label_encoder_ = LabelEncoder()
        y_encoded = self.label_encoder_.fit_transform(np.asarray(y))
        self.classes_ = self.label_encoder_.classes_
        self.model_ = XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            tree_method=self.tree_method,
            eval_metric=self.eval_metric,
            random_state=self.random_state,
        )
        self.model_.fit(X, y_encoded)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        y_encoded = self.model_.predict(X)
        return self.label_encoder_.inverse_transform(np.asarray(y_encoded, dtype=int))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model_.predict_proba(X)


def phase6_paths(root: str | Path = ".") -> Phase6Paths:
    base = Path(root).resolve()
    paths = Phase6Paths(
        root=base,
        tables=base / "results" / "tables" / "06_modeling",
        figures=base / "results" / "figures" / "06_modeling",
        predictions=base / "results" / "predictions" / "06_modeling",
        logs=base / "results" / "logs" / "06_modeling",
    )
    for folder in [paths.tables, paths.figures, paths.predictions, paths.logs]:
        folder.mkdir(parents=True, exist_ok=True)
    return paths


def limpiar_salidas_fase6(paths: Phase6Paths) -> None:
    for folder in [paths.tables, paths.figures, paths.predictions, paths.logs]:
        if folder.exists():
            for child in folder.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        folder.mkdir(parents=True, exist_ok=True)


def configurar_estilo() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.facecolor": "#fbfaf7",
            "axes.facecolor": "#fbfaf7",
            "axes.edgecolor": "#d8d1c7",
            "axes.labelcolor": "#2f2f2f",
            "xtick.color": "#2f2f2f",
            "ytick.color": "#2f2f2f",
            "font.size": 10,
            "axes.titleweight": "bold",
            "savefig.bbox": "tight",
        }
    )


def guardar_csv(tabla: pd.DataFrame, ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(ruta, index=False)
    return ruta


def guardar_figura(fig: plt.Figure, ruta_png: Path) -> Path:
    ruta_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_png, dpi=300)
    fig.savefig(ruta_png.with_suffix(".pdf"))
    plt.close(fig)
    return ruta_png


def extraer_target(tabla_y: pd.DataFrame) -> pd.Series:
    columnas = [col for col in tabla_y.columns if col != "original_index"]
    return tabla_y[columnas[-1]].reset_index(drop=True)


def cargar_split_crudo(paths: Phase6Paths, dataset: str, split: str) -> tuple[pd.DataFrame, pd.Series]:
    folder = paths.root / "data" / "splits" / dataset
    x = pd.read_csv(folder / f"X_{split}.csv").drop(columns=["original_index"], errors="ignore")
    y = extraer_target(pd.read_csv(folder / f"y_{split}.csv"))
    return x, y


def resumen_splits(paths: Phase6Paths) -> pd.DataFrame:
    filas = []
    for dataset in DATASETS:
        x_train, y_train = cargar_split_crudo(paths, dataset, "train")
        x_val, y_val = cargar_split_crudo(paths, dataset, "validation")
        x_test, y_test = cargar_split_crudo(paths, dataset, "test")
        filas.append(
            {
                "dataset": dataset,
                "train_rows": len(x_train),
                "validation_rows": len(x_val),
                "test_rows": len(x_test),
                "raw_features": x_train.shape[1],
                "train_classes": y_train.nunique(),
                "validation_classes": y_val.nunique(),
                "test_classes": y_test.nunique(),
            }
        )
    return pd.DataFrame(filas)


def k_referencia(dataset: str) -> int:
    return 5 if dataset.startswith("olive_oil") else 10


def cargar_conjuntos_fase5(paths: Phase6Paths) -> pd.DataFrame:
    selected = pd.read_csv(paths.root / "results" / "tables" / "05_feature_selection" / "fs_selected_feature_sets.csv")
    boruta = pd.read_csv(paths.root / "results" / "tables" / "05_feature_selection" / "fs_boruta_confirmed_sets.csv")
    rows = []
    for dataset in DATASETS:
        for method in ROSTER_12:
            if method == "boruta":
                k_value = int(boruta.loc[boruta["dataset"].eq(dataset), "k_confirmed"].iloc[0])
            else:
                k_value = k_referencia(dataset)
            match = selected[
                selected["dataset"].eq(dataset)
                & selected["method"].eq(method)
                & selected["k"].eq(k_value)
            ]
            if match.empty:
                row = materializar_topk_desde_ranking_fase5(paths, dataset, method, k_value, selected)
            else:
                row = match.iloc[0].to_dict()
            rows.append(
                {
                    "dataset": dataset,
                    "feature_set": f"{method}_k{k_value}" if method != "boruta" else f"boruta_confirmed_{k_value}",
                    "selector": method,
                    "k": k_value,
                    "n_features": int(row["n_features"]),
                    "feature_path": str(paths.root / row["path"]),
                    "source": "confirmed_by_boruta" if method == "boruta" else "reference_k",
                }
            )
    return pd.DataFrame(rows)


def materializar_topk_desde_ranking_fase5(
    paths: Phase6Paths,
    dataset: str,
    method: str,
    k_value: int,
    selected_sets: pd.DataFrame,
) -> dict[str, Any]:
    rankings = pd.read_csv(paths.root / "results" / "tables" / "05_feature_selection" / "fs_all_rankings.csv")
    local_rank = rankings[
        rankings["dataset"].eq(dataset)
        & rankings["method"].eq(method)
        & rankings["seed"].eq(42)
    ].sort_values("rank").drop_duplicates("feature")
    features = local_rank.head(k_value)["feature"].tolist()
    if len(features) != k_value:
        raise FileNotFoundError(f"No se puede derivar top-{k_value} para {dataset}/{method}")
    available = selected_sets[
        selected_sets["dataset"].eq(dataset)
        & selected_sets["method"].eq(method)
        & selected_sets["n_features"].ge(k_value)
    ].sort_values("n_features")
    if available.empty:
        raise FileNotFoundError(f"No hay matriz base para derivar {dataset}/{method}/k={k_value}")
    base_path = paths.root / available.iloc[0]["path"]
    target_path = paths.root / "data" / "selected_features" / dataset / method / f"k_{k_value}"
    target_path.mkdir(parents=True, exist_ok=True)
    for split_name, file_name in [
        ("train", "X_train_selected.csv"),
        ("validation", "X_validation_selected.csv"),
        ("test", "X_test_selected.csv"),
    ]:
        matrix = pd.read_csv(base_path / file_name)
        matrix[features].to_csv(target_path / file_name, index=False)
        if split_name == "validation":
            matrix[features].to_csv(target_path / "X_val_selected.csv", index=False)
    pd.DataFrame({"feature": features, "rank": range(1, len(features) + 1)}).to_csv(target_path / "selected_features.csv", index=False)
    return {
        "dataset": dataset,
        "method": method,
        "k": k_value,
        "n_features": k_value,
        "path": str(target_path.relative_to(paths.root)),
    }


def modelo_registro() -> dict[str, Any]:
    return {
        "logistic_regression": LogisticRegression(max_iter=2500, class_weight="balanced", solver="lbfgs", random_state=RANDOM_STATE),
        "linear_svm": LinearSVC(class_weight="balanced", dual="auto", max_iter=5000, random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(
            n_estimators=80,
            max_depth=12,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            max_samples=0.25,
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "xgboost": LabelEncodedXGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method="hist",
            eval_metric="logloss",
            random_state=RANDOM_STATE,
        ),
    }


def construir_parrilla(paths: Phase6Paths, conjuntos: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        x_train, _ = cargar_split_crudo(paths, dataset, "train")
        for model_name in MODEL_NAMES:
            rows.append(
                {
                    "dataset": dataset,
                    "feature_set": "all_features",
                    "selector": "all_features",
                    "k": x_train.shape[1],
                    "n_features": x_train.shape[1],
                    "feature_path": "",
                    "source": "baseline",
                    "model_name": model_name,
                }
            )
        for row in conjuntos[conjuntos["dataset"].eq(dataset)].itertuples(index=False):
            for model_name in MODEL_NAMES:
                rows.append({**row._asdict(), "model_name": model_name})
    grid = pd.DataFrame(rows)
    grid["experiment_id"] = [
        f"{r.dataset}__{r.feature_set}__{r.model_name}".replace("/", "_")
        for r in grid.itertuples(index=False)
    ]
    return grid


def cargar_matrices_experimento(paths: Phase6Paths, row: Any) -> dict[str, Any]:
    matrices = {}
    for split in ["train", "validation", "test"]:
        x, y = cargar_split_crudo(paths, row.dataset, split)
        matrices[f"X_{split}"] = x
        matrices[f"y_{split}"] = y
    if row.feature_set != "all_features":
        feature_path = Path(row.feature_path)
        matrices["X_train"] = pd.read_csv(feature_path / "X_train_selected.csv")
        matrices["X_validation"] = pd.read_csv(feature_path / "X_validation_selected.csv")
        matrices["X_test"] = pd.read_csv(feature_path / "X_test_selected.csv")
    return matrices


def construir_pipeline_modelo(model_name: str, x_train: pd.DataFrame) -> Pipeline:
    numeric = x_train.select_dtypes(include="number").columns.tolist()
    categorical = [col for col in x_train.columns if col not in numeric]
    transformers = []
    if numeric:
        transformers.append(("numeric", StandardScaler(), numeric))
    if categorical:
        transformers.append(("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical))
    preprocessor = ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=False)
    return Pipeline([("preprocessor", preprocessor), ("model", clone(modelo_registro()[model_name]))])


def extraer_score_binario(estimator: Pipeline, x: pd.DataFrame) -> np.ndarray | None:
    if hasattr(estimator, "predict_proba"):
        probabilities = estimator.predict_proba(x)
        if probabilities.ndim == 2 and probabilities.shape[1] == 2:
            return probabilities[:, 1]
    if hasattr(estimator, "decision_function"):
        scores = estimator.decision_function(x)
        if np.asarray(scores).ndim == 1:
            return np.asarray(scores, dtype=float)
        if np.asarray(scores).ndim == 2 and np.asarray(scores).shape[1] == 2:
            return np.asarray(scores, dtype=float)[:, 1]
    return None


def calcular_metricas(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    y_score: np.ndarray | None = None,
) -> dict[str, float]:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="y_pred contains classes not in y_true")
        metrics = {
            "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
            "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
            "accuracy": float(np.mean(np.asarray(y_true) == np.asarray(y_pred))),
        }
    if y_score is not None and pd.Series(y_true).nunique(dropna=True) == 2:
        try:
            metrics["auc_roc"] = float(roc_auc_score(y_true, y_score))
        except ValueError:
            pass
    return metrics


def filas_prediccion(row: Any, split: str, y_true: pd.Series, y_pred: np.ndarray) -> list[dict[str, Any]]:
    return [
        {
            "experiment_id": row.experiment_id,
            "dataset": row.dataset,
            "feature_set": row.feature_set,
            "model_name": row.model_name,
            "split": split,
            "row_position": int(i),
            "y_true": yt,
            "y_pred": yp,
            "correct": bool(yt == yp),
        }
        for i, (yt, yp) in enumerate(zip(y_true.to_numpy(), y_pred))
    ]


def entrenar_experimento_validation(paths: Phase6Paths, row: Any) -> tuple[dict[str, Any], pd.DataFrame, Pipeline]:
    matrices = cargar_matrices_experimento(paths, row)
    estimator = construir_pipeline_modelo(row.model_name, matrices["X_train"])
    started = time.perf_counter()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=ConvergenceWarning)
        estimator.fit(matrices["X_train"], matrices["y_train"])
    fit_seconds = time.perf_counter() - started
    y_pred = estimator.predict(matrices["X_validation"])
    y_score = extraer_score_binario(estimator, matrices["X_validation"]) if row.dataset in BINARY_DATASETS else None
    metrics = calcular_metricas(matrices["y_validation"], y_pred, y_score)
    result = {
        **row._asdict(),
        **metrics,
        "split": "validation",
        "fit_seconds": fit_seconds,
        "n_train": len(matrices["y_train"]),
        "n_validation": len(matrices["y_validation"]),
        "n_features_used": matrices["X_train"].shape[1],
    }
    predictions = pd.DataFrame(filas_prediccion(row, "validation", matrices["y_validation"], y_pred))
    return result, predictions, estimator


def enriquecer_validation(validation: pd.DataFrame) -> pd.DataFrame:
    enriched = validation.copy()
    baseline = (
        enriched[enriched["feature_set"].eq("all_features")]
        [["dataset", "model_name", "macro_f1", "balanced_accuracy", "fit_seconds"]]
        .rename(
            columns={
                "macro_f1": "baseline_macro_f1_same_model",
                "balanced_accuracy": "baseline_balanced_accuracy_same_model",
                "fit_seconds": "baseline_fit_seconds_same_model",
            }
        )
    )
    enriched = enriched.merge(baseline, on=["dataset", "model_name"], how="left")
    enriched["delta_macro_f1_vs_same_model_baseline"] = enriched["macro_f1"] - enriched["baseline_macro_f1_same_model"]
    enriched["delta_balanced_accuracy_vs_same_model_baseline"] = enriched["balanced_accuracy"] - enriched["baseline_balanced_accuracy_same_model"]
    all_features = enriched.groupby("dataset")["n_features_used"].transform("max")
    enriched["feature_reduction_ratio"] = 1 - enriched["n_features_used"] / all_features
    enriched = enriched.sort_values(["dataset", "macro_f1", "balanced_accuracy", "fit_seconds"], ascending=[True, False, False, True])
    enriched["validation_rank"] = enriched.groupby("dataset").cumcount() + 1
    return enriched


def seleccionar_candidatos_test(validation: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset, group in validation.groupby("dataset", sort=False):
        baseline = group[group["feature_set"].eq("all_features")].sort_values(["macro_f1", "balanced_accuracy", "fit_seconds"], ascending=[False, False, True]).head(1)
        selected_pool = group[~group["feature_set"].eq("all_features")].copy()
        selected = selected_pool.sort_values(
            ["macro_f1", "balanced_accuracy", "feature_reduction_ratio", "selector", "feature_set", "fit_seconds"],
            ascending=[False, False, False, True, True, True],
        ).drop_duplicates("feature_set").head(2)
        local = pd.concat([baseline, selected], ignore_index=True)
        reasons = ["baseline_mejor_en_validation"] + [f"subconjunto_top_{i}_validation" for i in range(1, len(local))]
        local["candidate_label"] = reasons
        rows.append(local)
    return pd.concat(rows, ignore_index=True)


def evaluar_candidato_test(paths: Phase6Paths, candidate: Any, estimator: Pipeline) -> tuple[dict[str, Any], pd.DataFrame]:
    matrices = cargar_matrices_experimento(paths, candidate)
    y_pred = estimator.predict(matrices["X_test"])
    y_score = extraer_score_binario(estimator, matrices["X_test"]) if candidate.dataset in BINARY_DATASETS else None
    metrics = calcular_metricas(matrices["y_test"], y_pred, y_score)
    result = {
        "experiment_id": candidate.experiment_id,
        "dataset": candidate.dataset,
        "feature_set": candidate.feature_set,
        "selector": candidate.selector,
        "k": int(candidate.k),
        "model_name": candidate.model_name,
        "candidate_label": candidate.candidate_label,
        "validation_macro_f1": candidate.macro_f1,
        "validation_balanced_accuracy": candidate.balanced_accuracy,
        "test_macro_f1": metrics["macro_f1"],
        "test_balanced_accuracy": metrics["balanced_accuracy"],
        "test_accuracy": metrics["accuracy"],
        **({"test_auc_roc": metrics["auc_roc"]} if "auc_roc" in metrics else {}),
        "n_test": len(matrices["y_test"]),
        "n_features_used": matrices["X_test"].shape[1],
    }
    predictions = pd.DataFrame(filas_prediccion(candidate, "test", matrices["y_test"], y_pred))
    return result, predictions


def bootstrap_intervalos(predictions: pd.DataFrame, split: str, n_bootstrap: int = N_BOOTSTRAP) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)
    rows = []
    for experiment_id, group in predictions.groupby("experiment_id", sort=False):
        y_true = group["y_true"].to_numpy()
        y_pred = group["y_pred"].to_numpy()
        samples = []
        for _ in range(n_bootstrap):
            idx = rng.integers(0, len(group), len(group))
            samples.append(calcular_metricas(y_true[idx], y_pred[idx]))
        frame = pd.DataFrame(samples)
        meta = group.iloc[0][["dataset", "feature_set", "model_name"]].to_dict()
        for metric in ["macro_f1", "balanced_accuracy", "accuracy"]:
            rows.append(
                {
                    "experiment_id": experiment_id,
                    "split": split,
                    **meta,
                    "metric": metric,
                    "estimate": calcular_metricas(y_true, y_pred)[metric],
                    "ci_low": float(frame[metric].quantile(0.025)),
                    "ci_high": float(frame[metric].quantile(0.975)),
                    "n_bootstrap": n_bootstrap,
                }
            )
    return pd.DataFrame(rows)


def comparaciones_pareadas(pred_test: pd.DataFrame, test_results: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE + 11)
    rows = []
    for dataset, group in test_results.groupby("dataset", sort=False):
        baseline_id = group[group["feature_set"].eq("all_features")]["experiment_id"].iloc[0]
        baseline = pred_test[pred_test["experiment_id"].eq(baseline_id)].sort_values("row_position")
        for candidate_id in group[~group["experiment_id"].eq(baseline_id)]["experiment_id"]:
            candidate = pred_test[pred_test["experiment_id"].eq(candidate_id)].sort_values("row_position")
            diffs = []
            for _ in range(N_BOOTSTRAP):
                idx = rng.integers(0, len(candidate), len(candidate))
                base_score = calcular_metricas(baseline["y_true"].to_numpy()[idx], baseline["y_pred"].to_numpy()[idx])["macro_f1"]
                cand_score = calcular_metricas(candidate["y_true"].to_numpy()[idx], candidate["y_pred"].to_numpy()[idx])["macro_f1"]
                diffs.append(cand_score - base_score)
            observed = calcular_metricas(candidate["y_true"], candidate["y_pred"])["macro_f1"] - calcular_metricas(baseline["y_true"], baseline["y_pred"])["macro_f1"]
            correctness_diff = candidate["correct"].to_numpy().astype(int) - baseline["correct"].to_numpy().astype(int)
            p_value = permutacion_signos(correctness_diff, rng)
            rows.append(
                {
                    "dataset": dataset,
                    "baseline_experiment_id": baseline_id,
                    "candidate_experiment_id": candidate_id,
                    "difference_macro_f1": observed,
                    "ci_low": float(np.quantile(diffs, 0.025)),
                    "ci_high": float(np.quantile(diffs, 0.975)),
                    "sign_permutation_p_value": p_value,
                    "n_bootstrap": N_BOOTSTRAP,
                    "n_sign_permutations": N_PAIRWISE_PERMUTATIONS,
                }
            )
    return pd.DataFrame(rows)


def permutacion_signos(values: np.ndarray, rng: np.random.Generator) -> float:
    non_zero = values[values != 0]
    if len(non_zero) == 0:
        return 1.0
    observed = abs(float(np.mean(non_zero)))
    null = []
    for _ in range(N_PAIRWISE_PERMUTATIONS):
        null.append(abs(float(np.mean(non_zero * rng.choice([-1, 1], len(non_zero))))))
    return float((np.sum(np.asarray(null) >= observed) + 1) / (N_PAIRWISE_PERMUTATIONS + 1))


def permutacion_etiquetas(pred_test: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE + 17)
    rows = []
    for experiment_id, group in pred_test.groupby("experiment_id", sort=False):
        y_true = group["y_true"].to_numpy()
        y_pred = group["y_pred"].to_numpy()
        observed = calcular_metricas(y_true, y_pred)["macro_f1"]
        null_scores = [calcular_metricas(rng.permutation(y_true), y_pred)["macro_f1"] for _ in range(N_LABEL_PERMUTATIONS)]
        meta = group.iloc[0][["dataset", "feature_set", "model_name"]].to_dict()
        rows.append(
            {
                "experiment_id": experiment_id,
                **meta,
                "observed_macro_f1": observed,
                "null_mean": float(np.mean(null_scores)),
                "null_p95": float(np.quantile(null_scores, 0.95)),
                "p_value": float((np.sum(np.asarray(null_scores) >= observed) + 1) / (N_LABEL_PERMUTATIONS + 1)),
                "n_permutations": N_LABEL_PERMUTATIONS,
            }
        )
    return pd.DataFrame(rows)


def coste_rendimiento(validation: pd.DataFrame, test_results: pd.DataFrame) -> pd.DataFrame:
    test_cols = test_results[["experiment_id", "test_macro_f1", "test_balanced_accuracy"]]
    return validation.merge(test_cols, on="experiment_id", how="left")


def nombres_modelo(estimator: Pipeline, x_train: pd.DataFrame) -> list[str]:
    preprocessor = estimator.named_steps["preprocessor"]
    try:
        return list(preprocessor.get_feature_names_out())
    except Exception:
        return list(x_train.columns)


def matriz_transformada_densa(preprocessor: ColumnTransformer, x: pd.DataFrame) -> np.ndarray:
    transformed = preprocessor.transform(x)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    return np.asarray(transformed, dtype=float)


def muestra_background_shap(x_train_transformed: np.ndarray, max_rows: int = 100) -> np.ndarray:
    if x_train_transformed.shape[0] <= max_rows:
        return x_train_transformed
    rng = np.random.default_rng(RANDOM_STATE)
    indices = rng.choice(x_train_transformed.shape[0], size=max_rows, replace=False)
    return x_train_transformed[np.sort(indices)]


def indices_muestra_shap(n_rows: int, max_rows: int = SHAP_MAX_EXPLAIN_ROWS) -> np.ndarray:
    if n_rows <= max_rows:
        return np.arange(n_rows)
    rng = np.random.default_rng(RANDOM_STATE + n_rows)
    return np.sort(rng.choice(n_rows, size=max_rows, replace=False))


def shap_values_array(explanation: Any) -> np.ndarray:
    values = explanation.values if hasattr(explanation, "values") else explanation
    if isinstance(values, list):
        values = np.stack([np.asarray(item) for item in values], axis=-1)
    values = np.asarray(values, dtype=float)
    if values.ndim in {1, 2, 3}:
        return values
    raise ValueError(f"Forma SHAP no soportada: {values.shape}")


def shap_mean_abs_by_feature(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.ndim == 3:
        return np.mean(np.abs(values), axis=(0, 2))
    if values.ndim == 2:
        return np.mean(np.abs(values), axis=0)
    if values.ndim == 1:
        return np.abs(values)
    raise ValueError(f"Forma SHAP no soportada: {values.shape}")


def safe_experiment_filename(experiment_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", experiment_id)


def shap_output_labels(model: Any, values: np.ndarray) -> list[str]:
    if values.ndim != 3:
        return []
    classes = getattr(model, "classes_", None)
    if classes is not None and len(classes) == values.shape[2]:
        return [str(item) for item in classes]
    return [str(i) for i in range(values.shape[2])]


def guardar_shap_crudo(
    paths: Phase6Paths,
    candidate: Any,
    values: np.ndarray,
    feature_values: np.ndarray,
    feature_names: list[str],
    output_labels: list[str],
) -> tuple[Path, Path]:
    safe_name = safe_experiment_filename(candidate.experiment_id)
    values_path = paths.tables / f"modeling_shap_values_full_{safe_name}.csv"
    features_path = paths.tables / f"modeling_shap_feature_values_{safe_name}.csv"

    feature_frame = pd.DataFrame(feature_values, columns=feature_names)
    feature_frame.insert(0, "row_position", range(len(feature_frame)))
    guardar_csv(feature_frame, features_path)

    if values.ndim == 3:
        columns = [
            f"{feature}__class_{label}"
            for label_index, label in enumerate(output_labels)
            for feature in feature_names
        ]
        matrix = np.concatenate([values[:, :, label_index] for label_index in range(values.shape[2])], axis=1)
    elif values.ndim == 2:
        columns = feature_names
        matrix = values
    else:
        columns = feature_names[: len(values)]
        matrix = values.reshape(1, -1)

    values_frame = pd.DataFrame(matrix, columns=columns)
    values_frame.insert(0, "row_position", range(len(values_frame)))
    guardar_csv(values_frame, values_path)
    return values_path, features_path


def shap_candidato(paths: Phase6Paths, candidate: Any, estimator: Pipeline) -> pd.DataFrame:
    matrices = cargar_matrices_experimento(paths, candidate)
    preprocessor = estimator.named_steps["preprocessor"]
    model = estimator.named_steps["model"]
    x_train_transformed = matriz_transformada_densa(preprocessor, matrices["X_train"])
    x_validation_transformed = matriz_transformada_densa(preprocessor, matrices["X_validation"])
    shap_indices = indices_muestra_shap(x_validation_transformed.shape[0])
    x_validation_shap = x_validation_transformed[shap_indices]
    background = muestra_background_shap(x_train_transformed)
    if candidate.model_name in {"random_forest", "xgboost"}:
        shap_model = model.model_ if isinstance(model, LabelEncodedXGBClassifier) else model
        explainer = shap.TreeExplainer(shap_model, data=background)
        explanation = explainer(x_validation_shap, check_additivity=False)
    elif candidate.model_name in {"logistic_regression", "linear_svm"}:
        explainer = shap.LinearExplainer(model, background)
        explanation = explainer(x_validation_shap)
    else:
        raise ValueError(f"Modelo sin explicador SHAP configurado: {candidate.model_name}")
    raw_shap_values = shap_values_array(explanation)
    mean_abs_shap = shap_mean_abs_by_feature(raw_shap_values)
    names = nombres_modelo(estimator, matrices["X_train"])
    if len(names) != len(mean_abs_shap):
        names = [f"feature_{i}" for i in range(len(mean_abs_shap))]
    output_labels = shap_output_labels(model, raw_shap_values)
    values_path, feature_values_path = guardar_shap_crudo(
        paths,
        candidate,
        raw_shap_values,
        x_validation_shap,
        names,
        output_labels,
    )
    order = np.argsort(mean_abs_shap)[::-1]
    rows = []
    for rank, idx in enumerate(order, start=1):
        rows.append(
            {
                "experiment_id": candidate.experiment_id,
                "dataset": candidate.dataset,
                "feature_set": candidate.feature_set,
                "model_name": candidate.model_name,
                "feature": names[idx],
                "mean_abs_shap": float(mean_abs_shap[idx]),
                "rank": rank,
                "n_validation_explained": len(shap_indices),
                "n_validation_available": len(matrices["X_validation"]),
                "raw_values_path": str(values_path.relative_to(paths.root)),
                "feature_values_path": str(feature_values_path.relative_to(paths.root)),
                "shap_value_shape": "x".join(map(str, raw_shap_values.shape)),
                "output_labels": "|".join(output_labels),
            }
        )
    return pd.DataFrame(rows)



def plot_baseline_vs_methods(paths: Phase6Paths, dataset: str, test_results: pd.DataFrame, intervals: pd.DataFrame) -> Path:
    local = test_results[test_results["dataset"].eq(dataset)].copy()
    ci = intervals[(intervals["dataset"].eq(dataset)) & (intervals["metric"].eq("macro_f1"))][["experiment_id", "ci_low", "ci_high"]]
    local = local.merge(ci, on="experiment_id", how="left")
    local["label"] = local["feature_set"] + "\n" + local["model_name"]
    fig, ax = plt.subplots(figsize=(9.5, max(3.8, 0.55 * len(local))))
    y = np.arange(len(local))
    ax.errorbar(local["test_macro_f1"], y, xerr=[local["test_macro_f1"] - local["ci_low"], local["ci_high"] - local["test_macro_f1"]], fmt="o", color="#2f6f8f", ecolor="#8ab6c2", capsize=3)
    ax.set_yticks(y)
    ax.set_yticklabels(local["label"])
    ax.set_xlim(0, 1.02)
    ax.set_xlabel("Macro-F1 en test con IC bootstrap 95%")
    ax.set_title(f"{dataset}: test se consulta solo para candidatos cerrados en validation")
    return guardar_figura(fig, paths.figures / f"test_macro_f1_confidence_intervals_{dataset}.png")


def plot_coste_rendimiento(paths: Phase6Paths, dataset: str, cost: pd.DataFrame) -> Path:
    local = cost[cost["dataset"].eq(dataset)].copy()
    fig, ax = plt.subplots(figsize=(8.8, 5.0))
    sns.scatterplot(data=local, x="n_features_used", y="macro_f1", hue="model_name", style="source", size="fit_seconds", sizes=(30, 180), ax=ax)
    ax.set_title(f"{dataset}: coste dimensional frente a Macro-F1 de validation")
    ax.set_xlabel("Variables usadas")
    ax.set_ylabel("Macro-F1 validation")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", title="")
    return guardar_figura(fig, paths.figures / f"validation_cost_performance_{dataset}.png")


def cargar_shap_crudo(paths: Phase6Paths, shap_row: Any) -> tuple[np.ndarray, pd.DataFrame, list[str], list[str]]:
    raw = pd.read_csv(paths.root / shap_row.raw_values_path).drop(columns=["row_position"], errors="ignore")
    feature_values = pd.read_csv(paths.root / shap_row.feature_values_path).drop(columns=["row_position"], errors="ignore")
    output_labels = [item for item in str(shap_row.output_labels).split("|") if item and item != "nan"]
    if output_labels:
        n_outputs = len(output_labels)
        n_features = raw.shape[1] // n_outputs
        values = np.stack(
            [
                raw.iloc[:, output_index * n_features : (output_index + 1) * n_features].to_numpy()
                for output_index in range(n_outputs)
            ],
            axis=2,
        )
        feature_names = list(feature_values.columns[:n_features])
    else:
        values = raw.to_numpy()
        feature_names = list(feature_values.columns)
    return values, feature_values[feature_names], feature_names, output_labels


def plot_shap_dataset(paths: Phase6Paths, dataset: str, shap_values: pd.DataFrame) -> list[Path]:
    local = shap_values[shap_values["dataset"].eq(dataset)].sort_values(["rank", "mean_abs_shap"], ascending=[True, False])
    candidate_row = local.drop_duplicates("experiment_id").iloc[0]
    values, feature_values, feature_names, output_labels = cargar_shap_crudo(paths, candidate_row)
    paths_out: list[Path] = []

    plt.figure(figsize=(8.8, 5.2))
    if values.ndim == 3:
        shap.summary_plot(
            np.mean(values, axis=2),
            feature_values,
            feature_names=feature_names,
            show=False,
            max_display=min(12, len(feature_names)),
            plot_size=None,
        )
    else:
        shap.summary_plot(
            values,
            feature_values,
            feature_names=feature_names,
            show=False,
            max_display=min(12, len(feature_names)),
            plot_size=None,
        )
    fig = plt.gcf()
    fig.suptitle(f"{dataset}: beeswarm SHAP del candidato {candidate_row.model_name}", y=1.02)
    paths_out.append(guardar_figura(fig, paths.figures / f"shap_summary_{dataset}.png"))

    if values.ndim == 3 and dataset.startswith("olive_oil"):
        for output_index, label in enumerate(output_labels):
            plt.figure(figsize=(8.8, 5.2))
            shap.summary_plot(
                values[:, :, output_index],
                feature_values,
                feature_names=feature_names,
                show=False,
                max_display=min(12, len(feature_names)),
                plot_size=None,
            )
            fig = plt.gcf()
            fig.suptitle(f"{dataset}: clase {label}", y=1.02)
            safe_label = safe_experiment_filename(label)
            paths_out.append(guardar_figura(fig, paths.figures / f"shap_summary_{dataset}_class_{safe_label}.png"))
    return paths_out


def registrar_decisiones_figuras(paths: Phase6Paths) -> Path:
    report = paths.root / "results" / "reports" / "figure_decisions.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    block = """

## Fase 6: familias de figura

### fase6_baseline_vs_metodos_ic
- Tier: 2
- Pregunta: ¿Qué candidatos finales superan o igualan al baseline con incertidumbre visible?
- Familia: dot plot con intervalos de confianza.
- Decisión: se prioriza Macro-F1 en test con IC bootstrap 95%; las barras evitan leer solo el punto estimado.

### fase6_shap_dataset
- Tier: 2
- Pregunta: ¿Qué variables sostienen la explicación local de los candidatos finales?
- Familia: beeswarm SHAP con valores firmados por instancia.
- Decisión: se persiste la matriz SHAP cruda y se reserva la media de |SHAP| para tablas auxiliares; en olive se separa además por clase.

### fase6_coste_rendimiento
- Tier: 2
- Pregunta: ¿Dónde aparece el compromiso entre coste dimensional, tiempo y Macro-F1?
- Familia: scatter coste-rendimiento.
- Decisión: se codifican variables usadas, Macro-F1, modelo y tiempo para mostrar el frente práctico que la tabla no revela.
"""
    previous = report.read_text(encoding="utf-8") if report.exists() else "# Decisiones de visualización\n"
    if "## Fase 6: familias de figura" in previous:
        previous = previous.split("## Fase 6: familias de figura")[0].rstrip()
    report.write_text(previous.rstrip() + "\n" + block, encoding="utf-8")
    return report
