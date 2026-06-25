from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.viz_core.editorial_warmth import EditorialPalette, apply_editorial_axes, set_editorial_rcparams


PALETA = EditorialPalette(
    background="#FAF7F2",
    panel="#FAF7F2",
    grid="#E6DED2",
    text="#2D2A26",
    spine="#D8D0C5",
    muted_text="#6F6A60",
    primary="#2F6F9F",
    secondary="#8FB3C9",
    accent="#D9822B",
    positive="#5E8C61",
    negative="#B85C5C",
    neutral="#B8B0A3",
    categorical=("#2F6F9F", "#D9822B", "#5E8C61", "#B85C5C", "#8FB3C9", "#B8B0A3"),
)


def configurar_estilo() -> None:
    set_editorial_rcparams(PALETA)


def guardar_figura(figura, ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(ruta, dpi=190, bbox_inches="tight", pad_inches=0.22, facecolor=PALETA.background)
    return ruta


def grafico_dimensiones(tabla: pd.DataFrame, ruta: Path) -> Path:
    configurar_estilo()
    datos = tabla.sort_values("delta_columnas_pct", key=lambda s: s.abs(), ascending=True)
    figura, eje = plt.subplots(figsize=(9.5, 4.9))
    posiciones = range(len(datos))
    eje.barh(posiciones, datos["columnas_raw"], height=0.36, color=PALETA.secondary, label="raw")
    eje.barh(
        [p + 0.38 for p in posiciones],
        datos["columnas_processed"],
        height=0.36,
        color=PALETA.primary,
        label="processed",
    )
    eje.set_yticks([p + 0.19 for p in posiciones])
    eje.set_yticklabels(datos["dataset"].str.replace("_", "\n"))
    eje.set_xlabel("número de columnas")
    eje.set_title("El preprocesado cambia sobre todo la dimensionalidad, no el número de muestras")
    eje.legend(frameon=False, ncol=2, loc="upper right")
    eje.margins(y=0.12)
    apply_editorial_axes(eje, PALETA, grid_axis="x")
    return guardar_figura(figura, ruta)


def grafico_target_shift(tabla: pd.DataFrame, ruta: Path) -> Path:
    configurar_estilo()
    datos = tabla.copy()
    datos["clase"] = datos["clase"].astype(str)
    pivot = datos.pivot_table(index=["dataset", "clase"], values="delta_proporcion_pct", aggfunc="sum").reset_index()
    pivot["etiqueta"] = pivot["dataset"].str.replace("_", " ") + " | " + pivot["clase"]
    pivot = pivot.sort_values("delta_proporcion_pct")
    altura = max(4.8, 0.28 * len(pivot))
    figura, eje = plt.subplots(figsize=(9.5, altura))
    colores = [PALETA.negative if v < 0 else PALETA.positive for v in pivot["delta_proporcion_pct"]]
    eje.barh(pivot["etiqueta"], pivot["delta_proporcion_pct"], color=colores)
    eje.axvline(0, color=PALETA.muted_text, linewidth=0.8)
    eje.set_xlabel("cambio en proporción de clase (puntos porcentuales)")
    eje.set_title("Las proporciones del target se conservan salvo cambios derivados de limpieza previa")
    apply_editorial_axes(eje, PALETA, grid_axis="x")
    return guardar_figura(figura, ruta)


def grafico_shift_distribucional(tabla: pd.DataFrame, ruta: Path) -> Path:
    configurar_estilo()
    datos = tabla.sort_values("score_shift", ascending=False).head(20).sort_values("score_shift")
    figura, eje = plt.subplots(figsize=(9.5, 6.0))
    eje.barh(datos["dataset"] + " | " + datos["variable"], datos["score_shift"], color=PALETA.accent)
    eje.set_xlabel("score de cambio robusto")
    eje.set_title("Variables con mayor cambio robusto entre raw y processed")
    apply_editorial_axes(eje, PALETA, grid_axis="x")
    return guardar_figura(figura, ruta)


def grafico_asociacion_target(tabla: pd.DataFrame, ruta: Path) -> Path:
    configurar_estilo()
    datos = tabla.sort_values("delta_score_abs", ascending=False).head(20).sort_values("delta_score_abs")
    figura, eje = plt.subplots(figsize=(9.5, 6.0))
    eje.barh(datos["dataset"] + " | " + datos["variable"], datos["delta_score_abs"], color=PALETA.primary)
    eje.set_xlabel("cambio absoluto en asociación con target")
    eje.set_title("Cambios relevantes en la señal variable-target tras preprocesado")
    apply_editorial_axes(eje, PALETA, grid_axis="x")
    return guardar_figura(figura, ruta)


def grafico_dimensionalidad(tabla: pd.DataFrame, ruta: Path) -> Path:
    configurar_estilo()
    figura, eje = plt.subplots(figsize=(7.8, 5.6))
    datos = tabla.copy()
    datos["muestras_plot"] = datos["n_muestras"].clip(lower=1)
    datos["features_plot"] = datos["n_features"].clip(lower=1)
    eje.scatter(datos["muestras_plot"], datos["features_plot"], s=120, color=PALETA.primary, alpha=0.9)
    desplazamientos = {
        "breast_cancer_wisconsin": (10, 10),
        "olive_oil": (10, 10),
        "madelon": (10, 8),
        "customer_churn": (10, 0),
    }
    for _, fila in datos.iterrows():
        dx, dy = desplazamientos.get(fila["dataset"], (8, 5))
        eje.annotate(
            fila["dataset"].replace("_", " "),
            (fila["muestras_plot"], fila["features_plot"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=8,
            color=PALETA.text,
        )
    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_ylim(datos["features_plot"].min() * 0.72, datos["features_plot"].max() * 1.35)
    eje.set_xlabel("muestras")
    eje.set_ylabel("features post-preprocesado")
    eje.set_title("Dificultad final antes del split: muestras frente a features (escala log)")
    apply_editorial_axes(eje, PALETA, grid_axis="both")
    return guardar_figura(figura, ruta)


def grafico_riesgos(tabla: pd.DataFrame, ruta: Path) -> Path:
    configurar_estilo()
    datos = tabla.groupby(["dataset", "gravedad"]).size().reset_index(name="n_riesgos")
    orden = {"alto": 3, "medio": 2, "bajo": 1}
    datos["orden"] = datos["gravedad"].map(orden).fillna(0)
    datos = datos.sort_values(["orden", "n_riesgos"], ascending=True)
    figura, eje = plt.subplots(figsize=(8.8, 4.8))
    colores = datos["gravedad"].map({"alto": PALETA.negative, "medio": PALETA.accent, "bajo": PALETA.neutral})
    eje.barh(datos["dataset"] + " | " + datos["gravedad"], datos["n_riesgos"], color=colores)
    eje.set_xlabel("número de riesgos residuales")
    eje.set_title("Riesgos residuales que pasan a Fase 4")
    apply_editorial_axes(eje, PALETA, grid_axis="x")
    return guardar_figura(figura, ruta)


def grafico_sintesis(tablas: dict[str, pd.DataFrame], ruta: Path) -> Path:
    configurar_estilo()
    dimensiones = tablas["postprocessed_dimensionality_summary.csv"]
    target = tablas["postprocessed_target_integrity.csv"]
    riesgos = tablas["postprocessed_residual_risks.csv"]
    cambios = tablas["raw_vs_processed_dimensions.csv"]

    figura, ejes = plt.subplots(2, 2, figsize=(12.0, 8.0))
    ejes = ejes.ravel()

    ejes[0].barh(cambios["dataset"], cambios["delta_columnas_pct"], color=PALETA.primary)
    ejes[0].set_title("Cambio relativo de columnas")
    ejes[0].set_xlabel("%")

    ejes[1].barh(target["dataset"], target["ratio_mayoritaria_minoritaria"], color=PALETA.positive)
    ejes[1].set_title("Desbalance del target")
    ejes[1].set_xlabel("ratio mayor/minor")

    ejes[2].barh(dimensiones["dataset"], dimensiones["ratio_features_muestras"], color=PALETA.accent)
    ejes[2].set_title("Ratio features/muestras")

    conteo = riesgos.groupby("dataset").size().reset_index(name="n")
    ejes[3].barh(conteo["dataset"], conteo["n"], color=PALETA.negative)
    ejes[3].set_title("Riesgos residuales")

    for eje in ejes:
        apply_editorial_axes(eje, PALETA, grid_axis="x")
    figura.suptitle("Síntesis post-preprocesado para decidir el paso al split", fontsize=15, y=1.02)
    figura.tight_layout()
    return guardar_figura(figura, ruta)
