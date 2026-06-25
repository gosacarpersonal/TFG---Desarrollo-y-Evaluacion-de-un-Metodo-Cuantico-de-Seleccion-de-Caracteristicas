"""Barrido de factibilidad geométrica del dist_ratio (sin simular cuánticamente).

Pregunta: ¿cuál es el mayor dist_ratio (más cercano a 1/sqrt(2) del paper) que
produce un embebido MDS válido en cada dataset? El runner de fase 8 solo probó
[0.45, 0.35, 0.25] y usó 0.45 en todos; nunca se exploró el tramo (0.45, 0.707].

Reusa exactamente la geometría del solver (arrange_atoms_robust_MDS, R_b,
normalizaciones, n_mds_runs=100, max_iter=100, beta seleccionada por dataset).
NO ejecuta la dinámica cuántica (Braket), así que es barato.
"""
from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "QFS_based_on_NA"))

from QFS_Auxiliar_functions import (  # noqa: E402
    arrange_atoms_robust_MDS,
    normalize_list,
    normalize_matrix,
)

TABLE_IN = ROOT / "results" / "tables" / "05_feature_selection"

# Constantes del solver (QFS_NA_Solver): R_b se deriva del detuning local máximo.
C = 862690 * 2 * np.pi * 1e6  # um^6 * rad / us
DELTA_LOCAL_MAX = 30 * 1e6
R_B = (C / np.sqrt(DELTA_LOCAL_MAX**2)) ** (1 / 6)

PRESELECT_TO = {"breast_cancer_wisconsin": 20, "madelon": 20}
BETA_SEL = {
    "breast_cancer_wisconsin": 0.2,
    "customer_churn": 0.3,
    "madelon": 0.5,
    "olive_oil_3class": 0.0,
    "olive_oil_9class": 0.4,
}
DATASETS = list(BETA_SEL)
RATIOS = [0.71, 0.65, 0.60, 0.55, 0.50, 0.45]  # de cerca de 1/sqrt(2)=0.707 hacia abajo
N_MDS_RUNS = 100
MAX_ITER = 100


def cargar_inputs(dataset):
    vector = pd.read_csv(TABLE_IN / f"fs_qfs_mi_target_vector__{dataset}.csv")
    matrix = pd.read_csv(TABLE_IN / f"fs_qfs_pairwise_mi_matrix__{dataset}.csv", index_col=0)
    features = vector["feature"].tolist()
    if matrix.index.tolist() != features:
        matrix = matrix.loc[features, features]
    I_i = vector["I_i"].to_numpy(dtype=float)
    R_ij = matrix.to_numpy(dtype=float)
    if dataset in PRESELECT_TO:
        keep = pd.read_csv(
            ROOT / "data" / "selected_features" / dataset / "mrmr_approx"
            / f"k_{PRESELECT_TO[dataset]}" / "selected_features.csv"
        ).sort_values("rank")["feature"].tolist()
        pos = [features.index(f) for f in keep]
        I_i = I_i[pos]
        R_ij = R_ij[np.ix_(pos, pos)]
        features = keep
    return features, normalize_list(I_i), normalize_matrix(R_ij)


def probar(dataset, ratio):
    _, og_weights, R_ij = cargar_inputs(dataset)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            res = arrange_atoms_robust_MDS(
                R_B, og_weights, R_ij, ratio,
                max_iter=MAX_ITER, n_mds_runs=N_MDS_RUNS, beta=BETA_SEL[dataset],
            )
        error_matrix = res[4]
        upper = np.triu_indices(error_matrix.shape[0], k=1)
        return True, float(np.mean(error_matrix[upper]))
    except ValueError:
        return False, np.nan


def main() -> int:
    print(f"R_b = {R_B:.4f} um | n_mds_runs={N_MDS_RUNS} max_iter={MAX_ITER}")
    filas = []
    for ds in DATASETS:
        for ratio in RATIOS:
            ok, err = probar(ds, ratio)
            filas.append({"dataset": ds, "beta_sel": BETA_SEL[ds], "dist_ratio": ratio,
                          "factible": ok, "embedding_error_mean": err})
            print(f"  {ds:24} ratio={ratio:.2f}  factible={ok}  err={err if ok else float('nan'):.4f}")
    df = pd.DataFrame(filas)
    out = ROOT / "results" / "tables" / "08_quantum" / "qfs_dist_ratio_feasibility_sweep.csv"
    df.to_csv(out, index=False)
    print(f"\nGuardado: {out}")
    print("\n=== Mayor dist_ratio factible por dataset ===")
    for ds in DATASETS:
        fac = df[(df.dataset == ds) & (df.factible)]
        best = fac["dist_ratio"].max() if len(fac) else None
        print(f"  {ds:24} -> {best}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
