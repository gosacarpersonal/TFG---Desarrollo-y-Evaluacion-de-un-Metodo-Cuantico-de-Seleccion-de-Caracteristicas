"""Prototype F10 with plotnine.

This script is deliberately separate from the production figure builder. It
tests whether plotnine makes the QFS-vs-classical comparison clearer and more
declarative without changing the LaTeX memory.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

try:
    from plotnine import (
        aes,
        coord_cartesian,
        geom_errorbarh,
        geom_point,
        ggplot,
        labs,
        scale_color_manual,
        scale_x_continuous,
        scale_y_continuous,
    )
except ModuleNotFoundError as exc:  # pragma: no cover - dependency gate
    raise SystemExit(
        "plotnine is not installed. Install plotnine>=0.15.7 or run this "
        "prototype in the temporary evaluation environment."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.viz_core.plotnine_theme import save_plotnine, theme_tfg

OUT = ROOT / "results" / "figures" / "10_memoria"

NEUTRAL = "#bdbdbd"
SECONDARY = "#4f81bd"
ACCENT = "#d95f5f"
ORACLE = "#d9b382"

DATASET_ORDER = [
    "olive_oil_9class",
    "olive_oil_3class",
    "madelon",
    "customer_churn",
    "breast_cancer_wisconsin",
]
DATASET_LABELS = {
    "breast_cancer_wisconsin": "Breast Cancer",
    "customer_churn": "Customer Churn",
    "madelon": "Madelon",
    "olive_oil_3class": "Olive 3",
    "olive_oil_9class": "Olive 9",
}
CONFIG_ORDER = ["Baseline", "Mejor clásico", "QFS-NA", "QFS-oráculo"]
CONFIG_COLORS = {
    "Baseline": NEUTRAL,
    "Mejor clásico": SECONDARY,
    "QFS-NA": ACCENT,
    "QFS-oráculo": ORACLE,
}


def build_dataframe() -> pd.DataFrame:
    q = pd.read_csv(ROOT / "results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv")
    hand = pd.read_csv(ROOT / "results/tables/07_final_comparison/fase7_handoff_qfs.csv").set_index("dataset")

    rows: list[dict[str, object]] = []
    for dataset in DATASET_ORDER:
        base = float(hand.loc[dataset, "baseline_test_macro_f1"])
        classic = float(hand.loc[dataset, "seleccion_test_macro_f1"])
        rows.append(
            {
                "dataset": dataset,
                "dataset_label": DATASET_LABELS[dataset],
                "config": "Baseline",
                "macro_f1": base,
                "xmin": None,
                "xmax": None,
            }
        )
        rows.append(
            {
                "dataset": dataset,
                "dataset_label": DATASET_LABELS[dataset],
                "config": "Mejor clásico",
                "macro_f1": classic,
                "xmin": None,
                "xmax": None,
            }
        )
        for cfg, label in [("qfs_na", "QFS-NA"), ("qfs_oracle_mucke", "QFS-oráculo")]:
            row = q[(q.dataset == dataset) & (q.configuration == cfg)].iloc[0]
            f1 = float(row.qfs_test_macro_f1)
            baseline = float(row.baseline_test_macro_f1)
            rows.append(
                {
                    "dataset": dataset,
                    "dataset_label": DATASET_LABELS[dataset],
                    "config": label,
                    "macro_f1": f1,
                    "xmin": baseline + float(row.delta_ci_low),
                    "xmax": baseline + float(row.delta_ci_high),
                }
            )
    df = pd.DataFrame(rows)
    df["dataset_label"] = pd.Categorical(
        df["dataset_label"],
        categories=[DATASET_LABELS[d] for d in DATASET_ORDER],
        ordered=True,
    )
    df["config"] = pd.Categorical(df["config"], categories=CONFIG_ORDER, ordered=True)
    offsets = {"Baseline": -0.27, "Mejor clásico": -0.09, "QFS-NA": 0.09, "QFS-oráculo": 0.27}
    base_y = {label: i for i, label in enumerate(df["dataset_label"].cat.categories)}
    df["y"] = df.apply(lambda r: base_y[r["dataset_label"]] + offsets[str(r["config"])], axis=1)
    return df


def build() -> None:
    df = build_dataframe()
    qfs_intervals = df[df["config"].isin(["QFS-NA", "QFS-oráculo"])].dropna(subset=["xmin", "xmax"])

    p = (
        ggplot(df, aes("macro_f1", "y", color="config"))
        + geom_errorbarh(
            qfs_intervals,
            aes(xmin="xmin", xmax="xmax", y="y", color="config"),
            height=0.055,
            alpha=0.42,
            size=0.8,
            inherit_aes=False,
        )
        + geom_point(size=3.0, stroke=0.25)
        + scale_color_manual(values=CONFIG_COLORS, limits=CONFIG_ORDER)
        + scale_y_continuous(
            breaks=list(range(len(DATASET_ORDER))),
            labels=[DATASET_LABELS[d] for d in DATASET_ORDER],
        )
        + scale_x_continuous(breaks=[0.6, 0.7, 0.8, 0.9, 1.0])
        + coord_cartesian(xlim=(0.55, 1.02))
        + labs(
            title="QFS iguala con señal clara; cuando se deteriora, F9 explica por qué",
            subtitle="Macro-F1 en test por dataset; barras = IC bootstrap del delta frente a baseline",
            x="Macro-F1 test",
            y="",
            color="",
        )
        + theme_tfg(width=12.4, height=6.0, base_size=12)
    )

    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / "prototype_f10_plotnine.png"
    pdf = OUT / "prototype_f10_plotnine.pdf"
    save_plotnine(p, png, width=12.4, height=6.0)
    save_plotnine(p, pdf, width=12.4, height=6.0)
    print(f"prototype written: {png}")


if __name__ == "__main__":
    build()
