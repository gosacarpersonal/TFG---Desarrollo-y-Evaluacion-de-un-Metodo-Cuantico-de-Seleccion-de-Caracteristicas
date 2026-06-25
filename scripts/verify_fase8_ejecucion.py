from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks" / "fase8.ipynb"
TABLE = ROOT / "results" / "tables" / "08_quantum"
FIG = ROOT / "results" / "figures" / "08_quantum"
DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]
BETA_LABELS = [f"{x / 10:.1f}".replace(".", "p") for x in range(11)]
K_BY_DATASET = {
    "olive_oil_3class": 5,
    "olive_oil_9class": 5,
    "customer_churn": 10,
    "breast_cancer_wisconsin": 10,
    "madelon": 10,
}


def count_features(value: str) -> int:
    if pd.isna(value) or not str(value):
        return 0
    return len(str(value).split("|"))


def main() -> int:
    report: dict[str, object] = {}
    report["notebook_exists"] = NB.exists()

    pre_path = TABLE / "qfs_preselection_summary.csv"
    report["preselection_exists"] = pre_path.exists()
    if pre_path.exists():
        pre = pd.read_csv(pre_path)
        report["preselection_has_5_datasets"] = sorted(pre["dataset"].tolist()) == sorted(DATASETS)
        report["bcw_preselected_20"] = int(pre.loc[pre["dataset"].eq("breast_cancer_wisconsin"), "qfs_n"].iloc[0]) == 20
        report["madelon_preselected_20"] = int(pre.loc[pre["dataset"].eq("madelon"), "qfs_n"].iloc[0]) == 20
        report["customer_churn_direct_real_15"] = int(pre.loc[pre["dataset"].eq("customer_churn"), "qfs_n"].iloc[0]) == 15

    selected_path = TABLE / "qfs_selected_all.csv"
    validation_path = TABLE / "qfs_validation_results.csv"
    summary_path = TABLE / "qfs_phase8_summary.csv"
    embedding_path = TABLE / "qfs_embedding_error.csv"
    report["selected_all_exists"] = selected_path.exists()
    report["validation_results_exists"] = validation_path.exists()
    report["summary_exists"] = summary_path.exists()
    report["embedding_error_exists"] = embedding_path.exists()

    if selected_path.exists():
        selected = pd.read_csv(selected_path)
        report["selected_two_per_dataset"] = bool(selected.groupby("dataset").size().eq(2).all()) and selected["dataset"].nunique() == 5
        selected["n_features_counted"] = selected["selected_features"].map(count_features)
        report["selected_k_correct"] = bool(
            all(
                row.n_features_counted == K_BY_DATASET[row.dataset]
                for row in selected.itertuples(index=False)
            )
        )
        report["selected_has_qfs_na_and_oracle"] = bool(
            selected.groupby("dataset")["configuration"].apply(lambda s: {"qfs_na", "qfs_oracle_mucke"}.issubset(set(s))).all()
        )

    if embedding_path.exists():
        embedding = pd.read_csv(embedding_path)
        report["embedding_has_55_rows"] = len(embedding) == len(DATASETS) * len(BETA_LABELS)
        report["embedding_has_all_datasets"] = sorted(embedding["dataset"].unique().tolist()) == sorted(DATASETS)
        report["embedding_mds_runs_100"] = bool(embedding["mds_runs"].eq(100).all())
        report["embedding_mds_max_iter_100"] = bool(embedding["mds_max_iter"].eq(100).all())
        report["embedding_positions_present"] = bool(embedding["positions_json"].astype(str).str.len().gt(10).all())
        report["embedding_errors_finite"] = bool(
            embedding[["embedding_error_mean", "embedding_error_p95", "min_radius"]]
            .apply(pd.to_numeric, errors="coerce")
            .notna()
            .all()
            .all()
        )

    missing_runs = []
    missing_oracle = []
    missing_quality = []
    missing_selected = []
    missing_figures = []
    run_rows_positive = True
    quality_nonempty = True
    for dataset in DATASETS:
        for beta_label in BETA_LABELS:
            run_path = TABLE / f"qfs_runs_{dataset}_{beta_label}.csv"
            if not run_path.exists():
                missing_runs.append(str(run_path.relative_to(ROOT)))
            else:
                run_rows_positive = run_rows_positive and len(pd.read_csv(run_path)) > 0
        for kind, bucket in [
            (f"qfs_oracle_{dataset}.csv", missing_oracle),
            (f"qfs_quality_control_{dataset}.csv", missing_quality),
            (f"qfs_selected_{dataset}.csv", missing_selected),
        ]:
            path = TABLE / kind
            if not path.exists():
                bucket.append(str(path.relative_to(ROOT)))
            elif "quality" in kind:
                quality_nonempty = quality_nonempty and len(pd.read_csv(path)) == 11
        fig = FIG / f"qfs_beta_map_{dataset}.png"
        if not fig.exists():
            missing_figures.append(str(fig.relative_to(ROOT)))

    report["all_qfs_runs_exist"] = not missing_runs
    report["qfs_run_rows_positive"] = run_rows_positive
    report["all_oracle_tables_exist"] = not missing_oracle
    report["all_quality_tables_exist"] = not missing_quality
    report["quality_has_11_beta_rows"] = quality_nonempty
    report["all_selected_tables_exist"] = not missing_selected
    report["all_beta_maps_exist"] = not missing_figures
    report["missing_runs"] = missing_runs[:10]
    report["missing_oracle"] = missing_oracle
    report["missing_quality"] = missing_quality
    report["missing_selected"] = missing_selected
    report["missing_figures"] = missing_figures

    bool_checks = {k: v for k, v in report.items() if isinstance(v, bool)}
    overall = all(bool_checks.values())
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("OVERALL:", "PASS" if overall else "FAIL")
    (ROOT / "results" / "logs" / "08_quantum").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "logs" / "08_quantum" / "fase8_ejecucion_verification_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
