from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
QFS_DIR = ROOT / "QFS_based_on_NA"
TABLE_DIR = ROOT / "results" / "tables" / "05_feature_selection"
REPORT_PATH = ROOT / "results" / "logs" / "08_quantum" / "fase8_solver_verification_report.json"


def load_module(path: Path, name: str):
    sys.path.insert(0, str(QFS_DIR))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def load_qfs_inputs(dataset: str) -> tuple[np.ndarray, np.ndarray]:
    vector = pd.read_csv(TABLE_DIR / f"fs_qfs_mi_target_vector__{dataset}.csv")
    matrix = pd.read_csv(TABLE_DIR / f"fs_qfs_pairwise_mi_matrix__{dataset}.csv", index_col=0)
    value_col = "I_i" if "I_i" in vector.columns else vector.select_dtypes(include="number").columns[-1]
    return vector[value_col].to_numpy(dtype=float), matrix.to_numpy(dtype=float)


def second_minor(matrix: np.ndarray) -> float:
    unique_values = np.unique(matrix)
    if len(unique_values) < 2:
        raise ValueError("Not enough unique values")
    return float(unique_values[1])


def original_distance_matrix_from_redundancy(R_ij: np.ndarray, d_max: float, d_min: float) -> np.ndarray:
    R_ij = np.asarray(R_ij, dtype=float)
    n = R_ij.shape[0]
    D = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                D[i][j] = 0
            elif R_ij[i][j] == 0:
                D[i][j] = d_max
                D[j][i] = d_max
            else:
                dij = (1 / R_ij[i][j]) ** (1 / 6)
                D[i][j] = dij
                D[j][i] = dij
    min_matrix = second_minor(D)
    max_matrix = np.max(D)
    D_matrix = np.round(d_min + ((D - min_matrix) / (max_matrix - min_matrix)) * (d_max - d_min), 4)
    np.fill_diagonal(D_matrix, 0)
    return D_matrix


def pair_with_largest_relevance_sum(I_i: np.ndarray) -> tuple[int, int]:
    n = len(I_i)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    return max(pairs, key=lambda ij: I_i[ij[0]] + I_i[ij[1]])


def main() -> int:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    qfs = load_module(QFS_DIR / "QFS_Auxiliar_functions.py", "qfs_solver")

    I_olive, R_olive = load_qfs_inputs("olive_oil_3class")
    I_churn, R_churn = load_qfs_inputs("customer_churn")
    d_min, d_max = 1.0, 4.0

    D_new_beta0 = qfs.distance_matrix_from_redundancy(R_olive, d_max, d_min, I_i=I_olive, beta=0.0)
    D_og = original_distance_matrix_from_redundancy(R_olive, d_max, d_min)
    beta0_matches_og = bool(np.allclose(D_new_beta0, D_og))

    D_beta = qfs.distance_matrix_from_redundancy(R_olive, d_max, d_min, I_i=I_olive, beta=0.5)
    high_pair = pair_with_largest_relevance_sum(I_olive)
    beta_changes_distance = bool(not np.allclose(D_beta, D_new_beta0))
    high_pair_distance_non_decrease = bool(D_beta[high_pair] >= D_new_beta0[high_pair])

    started = time.perf_counter()
    alpha_olive, x_olive = qfs.mucke_alpha_for_k(I_olive, R_olive, k_target=5)
    mucke_seconds_olive = time.perf_counter() - started
    mucke_cardinality_ok = int(x_olive.sum()) == 5

    started = time.perf_counter()
    x_star_olive, q_star_olive = qfs.oracle_Q_star(I_olive, R_olive, alpha=0.5)
    oracle_seconds_olive = time.perf_counter() - started
    q_candidate = qfs.cost_function(I_olive, R_olive, np.ones_like(x_star_olive), alpha=0.5)
    oracle_beats_naive = bool(q_star_olive <= q_candidate)

    started = time.perf_counter()
    x_star_churn, q_star_churn = qfs.oracle_Q_star(I_churn, R_churn, alpha=0.5)
    oracle_seconds_churn = time.perf_counter() - started

    report = {
        "beta0_matches_og": beta0_matches_og,
        "beta_changes_distance": beta_changes_distance,
        "high_pair": high_pair,
        "high_pair_distance_beta0": float(D_new_beta0[high_pair]),
        "high_pair_distance_beta05": float(D_beta[high_pair]),
        "high_pair_distance_non_decrease": high_pair_distance_non_decrease,
        "mucke_alpha_olive_k5": float(alpha_olive),
        "mucke_cardinality_olive": int(x_olive.sum()),
        "mucke_seconds_olive": mucke_seconds_olive,
        "oracle_q_star_olive_alpha05": float(q_star_olive),
        "oracle_cardinality_olive_alpha05": int(x_star_olive.sum()),
        "oracle_seconds_olive_alpha05": oracle_seconds_olive,
        "oracle_q_star_churn_alpha05": float(q_star_churn),
        "oracle_cardinality_churn_alpha05": int(x_star_churn.sum()),
        "oracle_seconds_churn_alpha05": oracle_seconds_churn,
        "oracle_beats_naive_all_ones": oracle_beats_naive,
    }
    checks = {
        "a_beta0_reproduces_original_distance": beta0_matches_og,
        "b_beta05_changes_distance_matrix": beta_changes_distance,
        "c_high_relevance_pair_not_closer": high_pair_distance_non_decrease,
        "d_mucke_returns_target_k": mucke_cardinality_ok,
        "e_oracle_beats_naive_candidate": oracle_beats_naive,
    }
    report["checks"] = checks
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"checks": checks, "report": str(REPORT_PATH.relative_to(ROOT)), "timings": {
        "oracle_seconds_olive_alpha05": oracle_seconds_olive,
        "oracle_seconds_churn_alpha05": oracle_seconds_churn,
    }}, indent=2, ensure_ascii=False))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
