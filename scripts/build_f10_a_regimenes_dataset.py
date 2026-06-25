from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "Plantilla_Latex_GCD" / "tfgs" / "figs"
TABLES = ROOT / "results" / "tables"

DATASETS = [
    "madelon",
    "customer_churn",
    "breast_cancer_wisconsin",
    "olive_oil_3class",
    "olive_oil_9class",
]

LABELS = {
    "breast_cancer_wisconsin": "Breast Cancer",
    "customer_churn": "Customer Churn",
    "madelon": "Madelon",
    "olive_oil_3class": "Olive 3",
    "olive_oil_9class": "Olive 9",
}

COLORS = {
    "breast_cancer_wisconsin": "#4f81bd",
    "customer_churn": "#d9b382",
    "madelon": "#d95f5f",
    "olive_oil_3class": "#8fb7a8",
    "olive_oil_9class": "#7aa6c2",
}


def load_regimes() -> pd.DataFrame:
    assoc = pd.read_csv(TABLES / "01_raw_eda" / "fase1_asociacion_target_resumen.csv")
    pca = pd.read_csv(TABLES / "01_raw_eda" / "fase1_pca_resumen.csv")
    vif = pd.read_csv(TABLES / "03_postprocessing_audit" / "fase3_vif_processed.csv")
    adv = pd.read_csv(TABLES / "04_split_audit" / "fase4_validacion_adversarial.csv")

    source_dataset = {
        "breast_cancer_wisconsin": "breast_cancer_wisconsin",
        "customer_churn": "customer_churn",
        "madelon": "madelon",
        "olive_oil_3class": "olive_oil",
        "olive_oil_9class": "olive_oil",
    }
    vif_max = vif.groupby("dataset", as_index=False)["vif"].max().rename(columns={"vif": "vif"})

    rows = []
    for dataset in DATASETS:
        source = source_dataset[dataset]
        assoc_row = assoc.loc[assoc["dataset"].eq(source)]
        pca_row = pca.loc[pca["dataset"].eq(source)]
        vif_row = vif_max.loc[vif_max["dataset"].eq(source)]
        adv_row = adv.loc[adv["dataset"].eq(dataset)]
        if assoc_row.empty or pca_row.empty or vif_row.empty or adv_row.empty:
            missing = {
                "assoc": assoc_row.empty,
                "pca": pca_row.empty,
                "vif": vif_row.empty,
                "adv": adv_row.empty,
            }
            raise ValueError(f"Faltan datos canonicos para {dataset}: {missing}")
        rows.append(
            {
                "dataset": dataset,
                "efecto": float(assoc_row["efecto_abs_mediano"].iloc[0]),
                "vif": float(vif_row["vif"].iloc[0]),
                "pca80": float(pca_row["componentes_80"].iloc[0]),
                "auc_cv": float(adv_row["auc_cv"].iloc[0]),
            }
        )
    return pd.DataFrame(rows)


def annotate_bars(ax, values, fmt, log_axis: bool = False) -> None:
    vals = np.asarray(values, dtype=float)
    for yi, val in enumerate(vals):
        if log_axis:
            x = val * 1.10
        else:
            x = val + max(vals.max() * 0.025, 0.01)
        ax.text(x, yi, fmt(val), va="center", ha="left", fontsize=8.4, color="#5b5853")


def main() -> None:
    df = load_regimes()
    y = np.arange(len(df))
    labels = [LABELS[d] for d in df.dataset]
    colors = [COLORS[d] for d in df.dataset]

    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "font.size": 9,
            "axes.labelcolor": "#333333",
            "xtick.color": "#6f6a60",
            "ytick.color": "#333333",
            "text.color": "#333333",
        }
    )

    fig, axes = plt.subplots(2, 2, figsize=(10.6, 6.4))
    axes = axes.ravel()
    fig.subplots_adjust(left=0.18, right=0.96, bottom=0.12, top=0.80, wspace=0.36, hspace=0.46)
    fig.text(
        0.02,
        0.96,
        "Regímenes del dato: la predicción antes de mirar QFS",
        ha="left",
        va="top",
        fontsize=15,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.915,
        "Orden común por señal univariante; las cifras directas separan criterio, embebido y cautela de test.",
        ha="left",
        va="top",
        fontsize=9.5,
        color="#5b5853",
    )

    panels = [
        ("efecto", "A. Señal univariante", "efecto mediano", lambda v: f"{v:.2f}", False),
        ("vif", "B. Redundancia lineal", "VIF máximo (log)", lambda v: f"{v:.0f}" if v >= 10 else f"{v:.1f}", True),
        ("pca80", "C. Dimensión intrínseca", "componentes PCA 80%", lambda v: f"{v:.0f}", False),
        ("auc_cv", "D. Calidad del split", "AUC adversarial", lambda v: f"{v:.3f}", False),
    ]

    for ax, (col, title, xlabel, fmt, log_axis) in zip(axes, panels):
        vals = df[col].to_numpy(float)
        ax.barh(y, vals, color=colors, edgecolor="#ffffff", linewidth=0.8)
        annotate_bars(ax, vals, fmt, log_axis=log_axis)
        ax.set_yticks(y, labels)
        ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.grid(False)
        ax.spines["left"].set_color("#c2c2c2")
        ax.spines["bottom"].set_color("#c2c2c2")
        if log_axis:
            ax.set_xscale("log")
            ax.set_xlim(0.8, vals.max() * 2.2)
        else:
            ax.set_xlim(0, vals.max() * 1.22)
        if col == "auc_cv":
            ax.axvline(0.5, color="#6f6a60", lw=1.0, ls="--")
            ax.set_xlim(0, 0.62)

    FIGS.mkdir(parents=True, exist_ok=True)
    out = FIGS / "f10_a_regimenes_dataset.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"built {out}")


if __name__ == "__main__":
    main()
