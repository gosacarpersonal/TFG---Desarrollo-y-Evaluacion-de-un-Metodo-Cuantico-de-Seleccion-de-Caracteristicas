from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from phase6_modeling import pipeline as p6


TABLE_OUT = ROOT / "results" / "tables" / "08_quantum"
MODEL_NAME = "random_forest"
K_LADDERS = {
    "breast_cancer_wisconsin": [3, 5, 10, 15, 20],
    "customer_churn": [1, 4, 5, 10, 15],
    "madelon": [5, 10, 15, 20],
    "olive_oil_3class": [3, 5, 8],
    "olive_oil_9class": [3, 5, 8],
}


def beta_token(beta: float) -> str:
    return f"{beta:.1f}".replace(".", "p")


def load_split_encoded(paths: p6.Phase6Paths, dataset: str, split: str, features: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    x, y = p6.cargar_split_crudo(paths, dataset, split)
    if any(feature not in x.columns for feature in features):
        x = pd.get_dummies(x, drop_first=False)
        for feature in features:
            if feature not in x.columns:
                x[feature] = 0
    missing = [feature for feature in features if feature not in x.columns]
    if missing:
        raise KeyError(f"{dataset}/{split}: features no presentes: {missing[:5]}")
    return x[features].copy(), y


def qfs_density_order(dataset: str) -> list[str]:
    selected = pd.read_csv(TABLE_OUT / "qfs_selected_all.csv")
    row = selected[(selected.dataset == dataset) & (selected.configuration == "qfs_na")].iloc[0]
    run = pd.read_csv(TABLE_OUT / f"qfs_runs_{dataset}_{beta_token(float(row.beta))}.csv").iloc[0]
    densities = {
        col.removeprefix("density__"): float(run[col])
        for col in run.index
        if str(col).startswith("density__")
    }
    return [feature for feature, _ in sorted(densities.items(), key=lambda item: item[1], reverse=True)]


def mrmr_features(dataset: str, k: int) -> list[str]:
    path = ROOT / "data" / "selected_features" / dataset / "mrmr_approx" / f"k_{k}" / "selected_features.csv"
    if not path.exists():
        rankings = pd.read_csv(ROOT / "results" / "tables" / "05_feature_selection" / "fs_all_rankings.csv")
        local = (
            rankings[
                rankings.dataset.eq(dataset)
                & rankings.method.eq("mrmr_approx")
                & rankings.seed.eq(42)
            ]
            .sort_values("rank")
            .drop_duplicates("feature")
        )
        return local.head(k)["feature"].astype(str).tolist()
    return pd.read_csv(path)["feature"].astype(str).head(k).tolist()


def evaluate(paths: p6.Phase6Paths, dataset: str, feature_set: str, k: int, features: list[str] | None) -> dict[str, object]:
    if features is None:
        x_train, y_train = p6.cargar_split_crudo(paths, dataset, "train")
        x_val, y_val = p6.cargar_split_crudo(paths, dataset, "validation")
        n_features = x_train.shape[1]
    else:
        x_train, y_train = load_split_encoded(paths, dataset, "train", features)
        x_val, y_val = load_split_encoded(paths, dataset, "validation", features)
        n_features = len(features)

    estimator = p6.construir_pipeline_modelo(MODEL_NAME, x_train)
    started = time.perf_counter()
    estimator.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - started
    pred = estimator.predict(x_val)
    metrics = p6.calcular_metricas(y_val, pred)
    return {
        "dataset": dataset,
        "feature_set": feature_set,
        "model_name": MODEL_NAME,
        "k": k,
        "n_features_used": n_features,
        "validation_macro_f1": metrics["macro_f1"],
        "validation_balanced_accuracy": metrics["balanced_accuracy"],
        "validation_accuracy": metrics["accuracy"],
        "fit_seconds": fit_seconds,
        "selected_features": "" if features is None else "|".join(features),
    }


def main() -> int:
    paths = p6.phase6_paths(ROOT)
    rows: list[dict[str, object]] = []
    for dataset, ladder in K_LADDERS.items():
        qfs_order = qfs_density_order(dataset)
        baseline_cache = evaluate(paths, dataset, "baseline_rf", max(ladder), None)
        for k in ladder:
            rows.append({**baseline_cache, "k": k})
            rows.append(evaluate(paths, dataset, "mrmr_approx", k, mrmr_features(dataset, k)))
            rows.append(evaluate(paths, dataset, "qfs_na_top_density", k, qfs_order[:k]))
            print(f"EV6 {dataset} k={k}: baseline/mRMR/QFS")

    out = pd.DataFrame(rows)
    out.to_csv(TABLE_OUT / "ev6_rendimiento_vs_k.csv", index=False)
    print(f"wrote {TABLE_OUT / 'ev6_rendimiento_vs_k.csv'} ({len(out)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
