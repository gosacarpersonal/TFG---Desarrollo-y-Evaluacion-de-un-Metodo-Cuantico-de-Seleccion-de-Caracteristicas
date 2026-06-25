"""Fase 10: eficiencia y generalizacion de la seleccion de caracteristicas.

Mide, de forma simetrica para el bloque clasico y el cuantico, los beneficios
de la seleccion que la memoria enuncia pero no medi­a:

  - sobreajuste: brecha train-test de macro-F1,
  - coste de entrenamiento: fit_seconds frente al baseline,
  - coste de inferencia: tiempo de predict por muestra.

Barre varias semillas de modelo para una lectura robusta. Reusa los
subconjuntos ya materializados (clasico de fase 5, cuantico de fase 9): NO
reejecuta la seleccion clasica ni la simulacion analogica QFS.

Salida: results/tables/10_eficiencia_generalizacion/eficiencia_generalizacion.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from phase6_modeling import pipeline as p6  # noqa: E402

# Semillas de modelo. La primera es la canonica de fase 6/9 (p6.RANDOM_STATE),
# de modo que esa fila reproduce el resultado ya publicado.
SEEDS = [p6.RANDOM_STATE, 1, 7, 13, 21, 34, 55, 89, 144, 233]
N_INFER_REPEATS = 25  # repeticiones del predict para estabilizar el tiempo

TABLE6 = PROJECT_ROOT / "results" / "tables" / "06_modeling"
TABLE8 = PROJECT_ROOT / "results" / "tables" / "08_quantum"
OUT_DIR = PROJECT_ROOT / "results" / "tables" / "10_eficiencia_generalizacion"
OUT_DIR.mkdir(parents=True, exist_ok=True)

paths6 = p6.phase6_paths(PROJECT_ROOT)


def feature_list(value: str) -> list[str]:
    return [item for item in str(value).split("|") if item and item != "nan"]


def cargar_split_qfs(dataset: str, split: str, features: list[str]):
    """Replica fiel de fase 9: one-hot del split crudo y seleccion de columnas QFS."""
    X, y = p6.cargar_split_crudo(paths6, dataset, split)
    if any(feature not in X.columns for feature in features):
        X = pd.get_dummies(X, drop_first=False)
        for feature in features:
            if feature not in X.columns:
                X[feature] = 0
    missing = [feature for feature in features if feature not in X.columns]
    if missing:
        raise KeyError(f"{dataset}/{split}: features QFS ausentes: {missing[:5]}")
    return X[features].copy(), y


def cargar_matrices(spec: dict) -> dict:
    dataset = spec["dataset"]
    salida = {}
    if spec["kind"] == "baseline":
        for split in ("train", "validation", "test"):
            salida[split] = p6.cargar_split_crudo(paths6, dataset, split)
    elif spec["kind"] == "classical":
        feature_path = Path(spec["feature_path"])
        for split in ("train", "validation", "test"):
            _, y = p6.cargar_split_crudo(paths6, dataset, split)
            X = pd.read_csv(feature_path / f"X_{split}_selected.csv")
            salida[split] = (X, y)
    else:  # qfs
        for split in ("train", "validation", "test"):
            salida[split] = cargar_split_qfs(dataset, split, spec["features"])
    return salida


def macro_f1(estimator, X, y) -> float:
    return p6.calcular_metricas(y, estimator.predict(X))["macro_f1"]


def evaluar(spec: dict, mats: dict, model_name: str, seed: int) -> dict:
    x_train, y_train = mats["train"]
    x_val, y_val = mats["validation"]
    x_test, y_test = mats["test"]

    estimator = p6.construir_pipeline_modelo(model_name, x_train)
    try:
        estimator.set_params(model__random_state=seed)
    except (ValueError, KeyError):
        pass  # modelos sin random_state efectivo (p. ej. lbfgs determinista)

    started = time.perf_counter()
    estimator.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - started

    f1_train = macro_f1(estimator, x_train, y_train)
    f1_val = macro_f1(estimator, x_val, y_val)
    f1_test = macro_f1(estimator, x_test, y_test)

    # Coste de inferencia: mejor tiempo de varios predict sobre test (ya en cache).
    best_predict = np.inf
    for _ in range(N_INFER_REPEATS):
        t0 = time.perf_counter()
        estimator.predict(x_test)
        best_predict = min(best_predict, time.perf_counter() - t0)

    return {
        "block": spec["block"],
        "dataset": spec["dataset"],
        "feature_set": spec["label"],
        "model_name": model_name,
        "seed": seed,
        "n_features": int(x_train.shape[1]),
        "n_test": int(len(y_test)),
        "train_macro_f1": f1_train,
        "validation_macro_f1": f1_val,
        "test_macro_f1": f1_test,
        "train_test_gap": f1_train - f1_test,
        "train_val_gap": f1_train - f1_val,
        "fit_seconds": fit_seconds,
        "predict_seconds_test": best_predict,
        "predict_us_per_sample": best_predict / max(len(y_test), 1) * 1e6,
    }


def construir_specs() -> list[dict]:
    specs: list[dict] = []

    # 1) Baseline (todas las variables) por dataset.
    for dataset in p6.DATASETS:
        specs.append({"kind": "baseline", "block": "baseline", "dataset": dataset, "label": "all_features"})

    # 2) Mejor subconjunto clasico por dataset (candidato con mayor test macro-F1).
    candidatos = pd.read_csv(TABLE6 / "modeling_test_results_candidates.csv")
    validacion = pd.read_csv(TABLE6 / "modeling_validation_results_all.csv")
    fp_map = (
        validacion.dropna(subset=["feature_path"])
        .query("feature_path != ''")
        .drop_duplicates(["dataset", "feature_set"])
        .set_index(["dataset", "feature_set"])["feature_path"]
    )
    seleccionados = candidatos[candidatos["candidate_label"] != "baseline_mejor_en_validation"]
    for dataset, grupo in seleccionados.groupby("dataset"):
        mejor = grupo.sort_values("test_macro_f1", ascending=False).iloc[0]
        feature_path = fp_map.get((dataset, mejor["feature_set"]))
        if feature_path is None:
            print(f"  AVISO: sin feature_path para {dataset}/{mejor['feature_set']}, se omite")
            continue
        specs.append({
            "kind": "classical", "block": "clasico", "dataset": dataset,
            "label": f"clasico:{mejor['feature_set']}", "feature_path": feature_path,
        })

    # 3) Subconjuntos QFS (operativo y oraculo) por dataset.
    qfs = pd.read_csv(TABLE8 / "qfs_selected_all.csv")
    etiqueta = {"qfs_na": "qfs_na", "qfs_oracle_mucke": "qfs_oracle"}
    for row in qfs.itertuples(index=False):
        specs.append({
            "kind": "qfs", "block": "cuantico", "dataset": row.dataset,
            "label": etiqueta.get(row.configuration, row.configuration),
            "features": feature_list(row.selected_features),
        })

    return specs


def main() -> int:
    specs = construir_specs()
    print(f"Configuraciones de variables: {len(specs)} | semillas: {len(SEEDS)} | modelos: {len(p6.MODEL_NAMES)}")
    filas = []
    for spec in specs:
        mats = cargar_matrices(spec)  # se carga una vez por configuracion
        for model_name in p6.MODEL_NAMES:
            for seed in SEEDS:
                filas.append(evaluar(spec, mats, model_name, seed))
        print(f"  hecho: {spec['dataset']:20} {spec['label']}")

    df = pd.DataFrame(filas)

    # Reduccion de variables frente al baseline del mismo dataset.
    base_n = (
        df[df["block"] == "baseline"].groupby("dataset")["n_features"].first().rename("n_features_baseline")
    )
    df = df.merge(base_n, on="dataset", how="left")
    df["feature_reduction_ratio"] = 1 - df["n_features"] / df["n_features_baseline"]

    out = OUT_DIR / "eficiencia_generalizacion.csv"
    df.to_csv(out, index=False)
    print(f"\nGuardado: {out}  ({len(df)} filas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
