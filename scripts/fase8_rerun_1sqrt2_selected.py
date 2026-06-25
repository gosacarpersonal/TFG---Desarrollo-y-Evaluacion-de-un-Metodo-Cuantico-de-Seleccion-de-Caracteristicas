"""Re-ejecuta QFS-NA a dist_ratio=1/sqrt(2) en la beta SELECCIONADA de cada
dataset y compara el subconjunto top-k con el canonico (que uso 0.45).

Objetivo: saber si usar el valor del paper (1/sqrt(2)) cambia las variables
seleccionadas y, por tanto, los resultados reportados. Reusa la logica de
fase 8 (preseleccion mRMR, QFS_NA_Solver, top-k por densidad de Rydberg).
"""
from __future__ import annotations
import contextlib, io, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "QFS_based_on_NA"))
from QFS_Auxiliar_functions import QFS_NA_Solver  # noqa: E402

TIN = ROOT / "results" / "tables" / "05_feature_selection"
OUT = ROOT / "results" / "tables" / "08_quantum" / "rerun_1sqrt2"
OUT.mkdir(parents=True, exist_ok=True)

K_BY = {"olive_oil_3class": 5, "olive_oil_9class": 5, "customer_churn": 10,
        "breast_cancer_wisconsin": 10, "madelon": 10}
PRESELECT_TO = {"breast_cancer_wisconsin": 20, "madelon": 20}
BETA_SEL = {"breast_cancer_wisconsin": 0.2, "customer_churn": 0.3,
            "madelon": 0.5, "olive_oil_3class": 0.0, "olive_oil_9class": 0.4}
RATIO = 1 / np.sqrt(2)


def inputs(ds):
    vec = pd.read_csv(TIN / f"fs_qfs_mi_target_vector__{ds}.csv")
    mat = pd.read_csv(TIN / f"fs_qfs_pairwise_mi_matrix__{ds}.csv", index_col=0)
    feats = vec["feature"].tolist()
    mat = mat.loc[feats, feats]
    I_i = vec["I_i"].to_numpy(float); R_ij = mat.to_numpy(float)
    if ds in PRESELECT_TO:
        keep = pd.read_csv(ROOT / "data" / "selected_features" / ds / "mrmr_approx"
                           / f"k_{PRESELECT_TO[ds]}" / "selected_features.csv").sort_values("rank")["feature"].tolist()
        pos = [feats.index(f) for f in keep]
        I_i = I_i[pos]; R_ij = R_ij[np.ix_(pos, pos)]; feats = keep
    return feats, I_i, R_ij


canon = pd.read_csv(ROOT / "results" / "tables" / "08_quantum" / "qfs_selected_all.csv")
filas = []
for ds in K_BY:
    feats, I_i, R_ij = inputs(ds)
    k = K_BY[ds]; beta = BETA_SEL[ds]
    with contextlib.redirect_stdout(io.StringIO()):
        costs, counts, bits, dens = QFS_NA_Solver(
            I_i, R_ij, feats, f"{ds}_r1sqrt2", E_dist_fraction=0.1, shots=10000,
            t=4, beta=beta, mds_max_iter=100, mds_runs=100, make_plots=False,
            dist_ratio_rydberg=RATIO)
    dens = np.asarray(dens, float)
    top = sorted(feats[i] for i in np.argsort(dens)[::-1][:k])
    row = canon[(canon.dataset == ds) & (canon.configuration == "qfs_na")].iloc[0]
    canon_feats = sorted(f for f in str(row.selected_features).split("|") if f)
    igual = set(top) == set(canon_feats)
    filas.append({"dataset": ds, "beta": beta, "k": k, "iguales": igual,
                  "jaccard": len(set(top) & set(canon_feats)) / len(set(top) | set(canon_feats)),
                  "top_1sqrt2": "|".join(top), "canonico_0p45": "|".join(canon_feats)})
    print(f"{ds:24} beta={beta} iguales={igual} J={filas[-1]['jaccard']:.2f}")

df = pd.DataFrame(filas)
df.to_csv(OUT / "comparacion_seleccion_1sqrt2_vs_0p45.csv", index=False)
print(f"\nGuardado: {OUT / 'comparacion_seleccion_1sqrt2_vs_0p45.csv'}")
print(f"\n¿Todas iguales?: {df['iguales'].all()}  | Jaccard medio: {df['jaccard'].mean():.3f}")
