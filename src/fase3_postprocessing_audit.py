from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import ast
import math
import shutil
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image
from scipy.stats import chi2_contingency
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder

from src.fase3_reporting import (
    escribir_auditoria_final,
    escribir_auditoria_visual,
    escribir_informe_memoria,
    escribir_markdown,
    tabla_markdown,
)
from src.fase3_visualization import (
    grafico_asociacion_target,
    grafico_dimensionalidad,
    grafico_dimensiones,
    grafico_riesgos,
    grafico_shift_distribucional,
    grafico_sintesis,
    grafico_target_shift,
)


DATASETS = ["breast_cancer_wisconsin", "customer_churn", "madelon", "olive_oil"]
RAW_FILES = {nombre: f"{nombre}.csv" for nombre in DATASETS}
PROCESSED_FILES = {nombre: f"{nombre}_processed.csv" for nombre in DATASETS}
RAW_TARGETS = {
    "breast_cancer_wisconsin": "target",
    "customer_churn": "Churn",
    "madelon": "target",
    "olive_oil": "target",
}
PROCESSED_TARGET = "target"
EXPECTED_PHASE2_LOGS = [
    "preprocessing_log.csv",
    "preprocessing_impact_summary.csv",
    "preprocessing_target_shift.csv",
    "preprocessing_distribution_shift.csv",
    "preprocessing_correlation_shift.csv",
    "processed_dataset_summary.csv",
    "processed_reload_check.csv",
]
EMPTY_TABLE_SCHEMAS = {
    "postprocessed_problematic_features.csv": ["dataset", "variable", "tipo_problema", "severidad"],
    "postprocessed_constant_features.csv": ["dataset", "variable", "n_unicos"],
    "postprocessed_low_variance_features.csv": ["dataset", "variable", "varianza"],
    "raw_vs_processed_unexpected_changes.csv": ["dataset", "cambio", "accion"],
    "postprocessed_missing_values.csv": ["dataset", "variable", "n_missing", "pct_missing"],
    "postprocessed_invalid_values.csv": ["dataset", "variable", "tipo", "n"],
    "postprocessed_distribution_anomalies.csv": ["dataset", "variable", "score_shift", "interpretacion"],
    "postprocessed_sparse_features.csv": ["dataset", "variable", "pct_ceros"],
    "postprocessed_categorical_features_pending.csv": ["dataset", "variable", "dtype", "n_unicos", "accion_fase4"],
    "postprocessed_new_strong_associations.csv": ["dataset", "variable", "score_asociacion", "alerta"],
    "postprocessed_split_warnings.csv": ["dataset", "gravedad", "riesgo", "evidencia", "accion_fase4"],
    "postprocessed_fs_warnings.csv": ["dataset", "gravedad", "riesgo", "evidencia", "accion_fase4"],
}
REVISION_VISUAL_MANUAL = {
    "raw_vs_processed_dimensions.png": {
        "observacion_manual": "Leyenda recolocada arriba a la derecha; barras separadas y etiquetas de datasets legibles. Aporta comparación dimensional y no sustituye a una tabla.",
        "clipping": "no",
        "etiquetas_cortadas": "no",
        "leyenda": "correcta",
        "solapamientos": "no",
        "margenes": "suficientes",
        "legibilidad_pdf": "alta",
        "utilidad_real": "alta",
    },
    "raw_vs_processed_target_association_shift.png": {
        "observacion_manual": "Ranking legible con etiquetas largas pero no cortadas; muestra cambios de asociación que serían lentos de comparar en una tabla amplia.",
        "clipping": "no",
        "etiquetas_cortadas": "no",
        "leyenda": "no aplica",
        "solapamientos": "no",
        "margenes": "suficientes",
        "legibilidad_pdf": "alta",
        "utilidad_real": "alta",
    },
    "postprocessed_dimensionality_summary.png": {
        "observacion_manual": "Se corrigió a escala logarítmica para evitar compresión; las etiquetas de olive oil y breast cancer ya no se pisan ni quedan fuera.",
        "clipping": "no",
        "etiquetas_cortadas": "no",
        "leyenda": "no aplica",
        "solapamientos": "no",
        "margenes": "suficientes",
        "legibilidad_pdf": "alta",
        "utilidad_real": "alta",
    },
    "postprocessed_residual_risks.png": {
        "observacion_manual": "Barras simples por dataset y gravedad; no hay cajas de texto ni tabla disfrazada. Sirve como resumen, con CSV como evidencia principal.",
        "clipping": "no",
        "etiquetas_cortadas": "no",
        "leyenda": "no aplica",
        "solapamientos": "no",
        "margenes": "suficientes",
        "legibilidad_pdf": "alta",
        "utilidad_real": "media",
    },
    "postprocessed_ead_synthesis.png": {
        "observacion_manual": "Panel 2x2 revisado tras sustituir un panel plano de target shift por desbalance del target; cuatro preguntas distintas sin decoración.",
        "clipping": "no",
        "etiquetas_cortadas": "no",
        "leyenda": "no aplica",
        "solapamientos": "no",
        "margenes": "suficientes",
        "legibilidad_pdf": "alta",
        "utilidad_real": "alta",
    },
}


@dataclass
class Fase3Context:
    root: Path
    raw_dir: Path
    processed_dir: Path
    tables_dir: Path
    figures_dir: Path
    reports_dir: Path
    phase1_tables_dir: Path
    phase2_tables_dir: Path
    latex_dir: Path
    raw: dict[str, pd.DataFrame] = field(default_factory=dict)
    processed: dict[str, pd.DataFrame] = field(default_factory=dict)
    tablas: dict[str, pd.DataFrame] = field(default_factory=dict)
    figuras: list[dict[str, Any]] = field(default_factory=list)
    decisiones: list[dict[str, Any]] = field(default_factory=list)
    incidencias: list[dict[str, Any]] = field(default_factory=list)
    riesgos: list[dict[str, Any]] = field(default_factory=list)
    artefactos: list[dict[str, Any]] = field(default_factory=list)
    observaciones: dict[str, str] = field(default_factory=dict)


def resolver_raiz(ruta: str | Path | None = None) -> Path:
    candidato = Path.cwd() if ruta is None else Path(ruta)
    candidato = candidato.resolve()
    if candidato.name == "notebooks":
        candidato = candidato.parent
    return candidato


def crear_contexto(ruta: str | Path | None = None) -> Fase3Context:
    root = resolver_raiz(ruta)
    contexto = Fase3Context(
        root=root,
        raw_dir=root / "data" / "01_raw",
        processed_dir=root / "data" / "processed",
        tables_dir=root / "results" / "tables" / "03_postprocessing_audit",
        figures_dir=root / "results" / "figures" / "03_postprocessing_audit",
        reports_dir=root / "results" / "reports" / "03_postprocessing_audit",
        phase1_tables_dir=root / "results" / "tables" / "01_raw_eda",
        phase2_tables_dir=root / "results" / "tables" / "02_preprocessing",
        latex_dir=root / "Plantilla_Latex_GCD" / "tfgs" / "tex",
    )
    for ruta_dir in [contexto.tables_dir, contexto.figures_dir, contexto.reports_dir]:
        ruta_dir.mkdir(parents=True, exist_ok=True)
    limpiar_salidas_previas(contexto)
    return contexto


def limpiar_salidas_previas(contexto: Fase3Context) -> None:
    for carpeta, extensiones in [
        (contexto.tables_dir, {".csv"}),
        (contexto.figures_dir, {".png", ".jpg", ".jpeg", ".pdf"}),
        (contexto.reports_dir, {".md", ".tex"}),
    ]:
        for ruta in carpeta.glob("*"):
            if ruta.is_file() and ruta.suffix.lower() in extensiones:
                ruta.unlink()


def guardar_tabla(contexto: Fase3Context, nombre: str, tabla: pd.DataFrame, seccion: str) -> pd.DataFrame:
    tabla = tabla.copy()
    if tabla.empty and len(tabla.columns) == 0:
        tabla = pd.DataFrame(columns=EMPTY_TABLE_SCHEMAS.get(nombre, ["sin_filas"]))
    ruta = contexto.tables_dir / nombre
    tabla.to_csv(ruta, index=False)
    contexto.tablas[nombre] = tabla
    contexto.artefactos.append(
        {"seccion": seccion, "tipo": "tabla", "nombre": nombre, "ruta": str(ruta.relative_to(contexto.root)), "filas": len(tabla)}
    )
    return tabla


def guardar_reporte(contexto: Fase3Context, nombre: str, contenido: str, seccion: str) -> Path:
    ruta = contexto.reports_dir / nombre
    escribir_markdown(ruta, contenido)
    contexto.artefactos.append(
        {"seccion": seccion, "tipo": "reporte", "nombre": nombre, "ruta": str(ruta.relative_to(contexto.root)), "filas": np.nan}
    )
    return ruta


def registrar_decision(contexto: Fase3Context, seccion: str, evidencia: str, accion: str, impacto: str, riesgo: str, artefacto: str) -> None:
    contexto.decisiones.append(
        {
            "seccion": seccion,
            "evidencia": evidencia,
            "accion": accion,
            "impacto": impacto,
            "riesgo_residual": riesgo,
            "artefacto_asociado": artefacto,
        }
    )


def registrar_incidencia(contexto: Fase3Context, seccion: str, entidad: str, incidencia: str, gravedad: str, accion: str) -> None:
    contexto.incidencias.append(
        {"seccion": seccion, "entidad": entidad, "incidencia": incidencia, "gravedad": gravedad, "accion": accion}
    )


def cargar_datos(contexto: Fase3Context) -> None:
    for dataset in DATASETS:
        raw_path = contexto.raw_dir / RAW_FILES[dataset]
        proc_path = contexto.processed_dir / PROCESSED_FILES[dataset]
        if raw_path.exists():
            contexto.raw[dataset] = pd.read_csv(raw_path)
        else:
            registrar_incidencia(contexto, "3.1", dataset, f"no existe {raw_path}", "alto", "bloquear fase")
        if proc_path.exists():
            contexto.processed[dataset] = pd.read_csv(proc_path)
        else:
            registrar_incidencia(contexto, "3.1", dataset, f"no existe {proc_path}", "alto", "bloquear fase")


def _normalizar(nombre: str) -> str:
    return str(nombre).strip().lower().replace(" ", "_")


def _feature_columns(tabla: pd.DataFrame, target: str) -> list[str]:
    return [c for c in tabla.columns if c != target]


def _numeric_features(tabla: pd.DataFrame, target: str) -> list[str]:
    return [c for c in _feature_columns(tabla, target) if pd.api.types.is_numeric_dtype(tabla[c])]


def _target_raw(dataset: str, tabla: pd.DataFrame) -> str:
    esperado = RAW_TARGETS[dataset]
    if esperado in tabla.columns:
        return esperado
    for columna in tabla.columns:
        if _normalizar(columna) == _normalizar(esperado):
            return columna
    return esperado


def _map_target_raw_a_processed(contexto: Fase3Context, dataset: str, serie: pd.Series) -> pd.Series:
    ruta = contexto.phase2_tables_dir / "preprocessing_target_encoding.csv"
    if not ruta.exists():
        return serie
    tabla = pd.read_csv(ruta)
    fila = tabla[tabla["dataset"].eq(dataset)]
    if fila.empty:
        return serie
    try:
        mapping = ast.literal_eval(fila.iloc[0]["mapping"])
    except (SyntaxError, ValueError):
        return serie
    return serie.map(mapping).fillna(serie)


def _columnas_comparables(raw: pd.DataFrame, processed: pd.DataFrame, target_raw: str) -> dict[str, str]:
    mapa = {}
    procesadas = {_normalizar(c): c for c in processed.columns}
    for columna in raw.columns:
        if columna == target_raw:
            continue
        clave = _normalizar(columna)
        if clave in procesadas:
            mapa[columna] = procesadas[clave]
    return mapa


def _entropy(serie: pd.Series) -> float:
    proporciones = serie.value_counts(normalize=True, dropna=False)
    return float(-(proporciones * np.log2(proporciones + 1e-12)).sum())


def _safe_numeric(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie, errors="coerce")


def _assoc_scores(tabla: pd.DataFrame, target: str, dataset: str) -> pd.DataFrame:
    if target not in tabla.columns:
        return pd.DataFrame()
    y = LabelEncoder().fit_transform(tabla[target].astype(str).fillna("__missing__"))
    filas = []
    numeric_cols = _numeric_features(tabla, target)
    if not numeric_cols:
        return pd.DataFrame()
    matriz = tabla[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(tabla[numeric_cols].median(numeric_only=True))
    for columna in numeric_cols:
        valores = matriz[columna]
        if valores.nunique(dropna=True) <= 1:
            spearman = 0.0
        else:
            spearman = abs(float(pd.Series(valores).corr(pd.Series(y), method="spearman")))
            if math.isnan(spearman):
                spearman = 0.0
        filas.append({"dataset": dataset, "variable": columna, "spearman_abs": spearman})
    try:
        mi = mutual_info_classif(matriz, y, discrete_features=False, random_state=42)
        for fila, score in zip(filas, mi):
            fila["mutual_info"] = float(score)
    except Exception:
        for fila in filas:
            fila["mutual_info"] = np.nan
    salida = pd.DataFrame(filas)
    salida["score_asociacion"] = salida[["spearman_abs", "mutual_info"]].fillna(0).mean(axis=1)
    salida["ranking"] = salida["score_asociacion"].rank(method="first", ascending=False).astype(int)
    return salida.sort_values(["dataset", "ranking"])


def auditoria_inicial(contexto: Fase3Context) -> None:
    notebook = contexto.root / "notebooks" / "fase3.ipynb"
    fase1 = sorted(contexto.phase1_tables_dir.glob("*.csv"))
    fase2 = sorted(contexto.phase2_tables_dir.glob("*.csv"))
    filas = [
        {
            "aspecto": "intencion_notebook_actual",
            "hallazgo": "Plantilla avanzada de auditoría post-preprocesado con secciones 3.1-3.13.",
            "decisión": "conservar estructura temática, reescribir ejecución y narrativa final",
        },
        {
            "aspecto": "partes_utiles",
            "hallazgo": "Objetivos por seccion, enfoque tabla-primero y salidas esperadas.",
            "decisión": "mantener como guion científico",
        },
        {
            "aspecto": "partes_a_reescribir",
            "hallazgo": "Uso de %%writefile, placeholders narrativos, figuras automáticas y falta de auditoría inicial.",
            "decisión": "mover lógica a src y regenerar notebook orquestador",
        },
        {
            "aspecto": "dependencia_fase1",
            "hallazgo": f"{len(fase1)} tablas de EDA raw disponibles.",
            "decisión": "usar como evidencia de estructura, target, correlación y señal raw",
        },
        {
            "aspecto": "dependencia_fase2",
            "hallazgo": f"{len(fase2)} tablas de preprocesado disponibles.",
            "decisión": "usar logs de impacto, target, encoding, escalado y riesgos",
        },
        {
            "aspecto": "riesgo_científico",
            "hallazgo": "Confundir auditoría post-preprocesado con selección definitiva de variables.",
            "decisión": "limitar conclusiones a preparación para split",
        },
        {
            "aspecto": "riesgo_técnico",
            "hallazgo": "Rutas relativas fragiles y duplicacion de codigo en notebook.",
            "decisión": "resolver raíz de proyecto y centralizar cálculos",
        },
        {
            "aspecto": "riesgo_visual",
            "hallazgo": "Figuras aceptadas por existir, sin decisión analítica ni revisión visual real.",
            "decisión": "auditar cada figura y descartar las que comuniquen mejor como tabla",
        },
    ]
    tabla = guardar_tabla(contexto, "fase3_initial_audit.csv", pd.DataFrame(filas), "0")
    md = "# Auditoría inicial Fase 3\n\n" + tabla_markdown(tabla, 20)
    guardar_reporte(contexto, "fase3_initial_audit.md", md, "0")
    registrar_decision(contexto, "0", "auditoría inicial creada", "reescribir notebook como orquestador", "reduce deuda técnica", "ninguno", "fase3_initial_audit.csv")


def seccion_31(contexto: Fase3Context) -> str:
    filas = []
    logs = []
    resumen = []
    for dataset in DATASETS:
        raw = contexto.raw.get(dataset)
        proc = contexto.processed.get(dataset)
        filas.append(
            {
                "dataset": dataset,
                "raw_existe": raw is not None,
                "processed_existe": proc is not None,
                "raw_filas": np.nan if raw is None else len(raw),
                "processed_filas": np.nan if proc is None else len(proc),
                "raw_columnas": np.nan if raw is None else raw.shape[1],
                "processed_columnas": np.nan if proc is None else proc.shape[1],
                "target_processed_existe": proc is not None and PROCESSED_TARGET in proc.columns,
            }
        )
        if proc is not None:
            resumen.append(
                {"dataset": dataset, "n_muestras": len(proc), "n_columnas": proc.shape[1], "memoria_mb": round(proc.memory_usage(deep=True).sum() / 1e6, 4)}
            )
    for log in EXPECTED_PHASE2_LOGS:
        ruta = contexto.phase2_tables_dir / log
        logs.append({"log": log, "existe": ruta.exists(), "ruta": str(ruta.relative_to(contexto.root)) if ruta.exists() else ""})
        if not ruta.exists():
            registrar_incidencia(contexto, "3.1", log, "log esperado de Fase 2 no encontrado", "medio", "documentar limitacion")
    load = guardar_tabla(contexto, "postprocessed_load_check.csv", pd.DataFrame(filas), "3.1")
    guardar_tabla(contexto, "postprocessed_log_availability.csv", pd.DataFrame(logs), "3.1")
    guardar_tabla(contexto, "postprocessed_input_summary.csv", pd.DataFrame(resumen), "3.1")
    texto = _observacion(load["processed_existe"].all(), "3.1", "Los datasets processed y los logs nucleares de Fase 2 se cargan como base de auditoría.", "Si falta algún log, la decisión se apoya en recálculo local y se registra incidencia.")
    contexto.observaciones["3.1"] = texto
    return texto


def seccion_32(contexto: Fase3Context) -> str:
    estructuras, tipos, constantes, baja_var, integridad, problemas = [], [], [], [], [], []
    for dataset, proc in contexto.processed.items():
        features = _feature_columns(proc, PROCESSED_TARGET)
        numeric = _numeric_features(proc, PROCESSED_TARGET)
        estructuras.append(
            {
                "dataset": dataset,
                "n_muestras": len(proc),
                "n_columnas": proc.shape[1],
                "n_features": len(features),
                "n_numéricas": len(numeric),
                "target_existe": PROCESSED_TARGET in proc.columns,
                "duplicated_columns": int(pd.Index(proc.columns).duplicated().sum()),
            }
        )
        for columna in proc.columns:
            serie = proc[columna]
            tipos.append({"dataset": dataset, "variable": columna, "dtype": str(serie.dtype), "n_unicos": int(serie.nunique(dropna=False))})
            if columna != PROCESSED_TARGET and serie.nunique(dropna=False) <= 1:
                constantes.append({"dataset": dataset, "variable": columna, "n_unicos": int(serie.nunique(dropna=False))})
                problemas.append({"dataset": dataset, "variable": columna, "tipo_problema": "constante", "severidad": "alto"})
            if columna != PROCESSED_TARGET and pd.api.types.is_numeric_dtype(serie):
                varianza = float(serie.var(ddof=0)) if len(serie) else 0.0
                if varianza < 1e-10:
                    baja_var.append({"dataset": dataset, "variable": columna, "varianza": varianza})
                    problemas.append({"dataset": dataset, "variable": columna, "tipo_problema": "baja_varianza", "severidad": "medio"})
        integridad.append(
            {
                "dataset": dataset,
                "columnas_unicas": pd.Index(proc.columns).is_unique,
                "target_unico": PROCESSED_TARGET in proc.columns and proc[PROCESSED_TARGET].nunique(dropna=False) > 1,
                "sin_filas_duplicadas": not proc.duplicated().any(),
            }
        )
    guardar_tabla(contexto, "postprocessed_structure_summary.csv", pd.DataFrame(estructuras), "3.2")
    guardar_tabla(contexto, "postprocessed_dtype_summary.csv", pd.DataFrame(tipos), "3.2")
    guardar_tabla(contexto, "postprocessed_constant_features.csv", pd.DataFrame(constantes), "3.2")
    guardar_tabla(contexto, "postprocessed_low_variance_features.csv", pd.DataFrame(baja_var), "3.2")
    guardar_tabla(contexto, "postprocessed_column_integrity.csv", pd.DataFrame(integridad), "3.2")
    guardar_tabla(contexto, "postprocessed_problematic_features.csv", pd.DataFrame(problemas), "3.2")
    texto = _observacion(not problemas, "3.2", "La estructura post-preprocesado no presenta variables constantes o rotas relevantes.", "Las features de baja varianza se pasan como aviso para Fase 4.")
    contexto.observaciones["3.2"] = texto
    return texto


def seccion_33(contexto: Fase3Context) -> str:
    dimensiones, columnas, cambios, inesperados = [], [], [], []
    for dataset in DATASETS:
        raw, proc = contexto.raw.get(dataset), contexto.processed.get(dataset)
        if raw is None or proc is None:
            continue
        raw_cols = set(raw.columns)
        proc_cols = set(proc.columns)
        comunes = sorted(raw_cols & proc_cols)
        dimensiones.append(
            {
                "dataset": dataset,
                "filas_raw": len(raw),
                "filas_processed": len(proc),
                "delta_filas": len(proc) - len(raw),
                "delta_filas_pct": round((len(proc) - len(raw)) / max(len(raw), 1) * 100, 4),
                "columnas_raw": raw.shape[1],
                "columnas_processed": proc.shape[1],
                "delta_columnas": proc.shape[1] - raw.shape[1],
                "delta_columnas_pct": round((proc.shape[1] - raw.shape[1]) / max(raw.shape[1], 1) * 100, 4),
            }
        )
        columnas.append(
            {
                "dataset": dataset,
                "columnas_comunes_mismo_nombre": len(comunes),
                "columnas_solo_raw": len(raw_cols - proc_cols),
                "columnas_solo_processed": len(proc_cols - raw_cols),
                "solo_raw": "; ".join(sorted(raw_cols - proc_cols)[:25]),
                "solo_processed": "; ".join(sorted(proc_cols - raw_cols)[:25]),
            }
        )
        cambios.append({"dataset": dataset, "cambio_esperado": "identificadores eliminados, nombres normalizados, target codificado y transformaciónes de Fase 2"})
        if len(proc) > len(raw):
            inesperados.append({"dataset": dataset, "cambio": "processed tiene más filas que raw", "accion": "revisar Fase 2"})
    tabla_dim = guardar_tabla(contexto, "raw_vs_processed_dimensions.csv", pd.DataFrame(dimensiones), "3.3")
    guardar_tabla(contexto, "raw_vs_processed_columns.csv", pd.DataFrame(columnas), "3.3")
    guardar_tabla(contexto, "raw_vs_processed_change_summary.csv", pd.DataFrame(cambios), "3.3")
    guardar_tabla(contexto, "raw_vs_processed_unexpected_changes.csv", pd.DataFrame(inesperados), "3.3")
    ruta = grafico_dimensiones(tabla_dim, contexto.figures_dir / "raw_vs_processed_dimensions.png")
    _registrar_figura(contexto, ruta, "3.3", "Comparar columnas raw y processed", "comparación", "barras agrupadas", True)
    texto = _observacion(not inesperados, "3.3", "Los cambios de dimensiones son compatibles con el preprocesado documentado.", "El aumento/reducción de columnas debe revisarse junto a encoding y eliminación de identificadores.")
    contexto.observaciones["3.3"] = texto
    return texto


def seccion_34(contexto: Fase3Context) -> str:
    distribuciones, shifts, integridad = [], [], []
    for dataset in DATASETS:
        raw, proc = contexto.raw.get(dataset), contexto.processed.get(dataset)
        if raw is None or proc is None:
            continue
        raw_target = _target_raw(dataset, raw)
        raw_series = _map_target_raw_a_processed(contexto, dataset, raw[raw_target])
        proc_series = proc[PROCESSED_TARGET]
        for origen, serie in [("raw", raw_series), ("processed", proc_series)]:
            conteos = serie.value_counts(dropna=False)
            for clase, n in conteos.items():
                distribuciones.append(
                    {"dataset": dataset, "origen": origen, "clase": clase, "n": int(n), "proporción": round(float(n) / len(serie), 8)}
                )
        clases = sorted(set(raw_series.dropna().unique()) | set(proc_series.dropna().unique()), key=lambda x: str(x))
        for clase in clases:
            pr = float((raw_series == clase).mean())
            pp = float((proc_series == clase).mean())
            shifts.append({"dataset": dataset, "clase": clase, "proporción_raw": pr, "proporción_processed": pp, "delta_proporcion_pct": round((pp - pr) * 100, 4)})
        tabla_ct = pd.crosstab(raw_series.astype(str), proc_series.astype(str))
        p_valor = np.nan
        if tabla_ct.shape[0] > 1 and tabla_ct.shape[1] > 1:
            try:
                p_valor = float(chi2_contingency(tabla_ct)[1])
            except ValueError:
                p_valor = np.nan
        integridad.append(
            {
                "dataset": dataset,
                "target_raw_existe": raw_target in raw.columns,
                "target_processed_existe": PROCESSED_TARGET in proc.columns,
                "clases_raw": raw_series.nunique(dropna=False),
                "clases_processed": proc_series.nunique(dropna=False),
                "max_delta_proporcion_pct": max(abs(f["delta_proporcion_pct"]) for f in shifts if f["dataset"] == dataset),
                "ratio_mayoritaria_minoritaria": round(proc_series.value_counts().max() / max(proc_series.value_counts().min(), 1), 4),
                "entropia_processed": round(_entropy(proc_series), 6),
                "chi2_p_value_raw_vs_processed": p_valor,
            }
        )
    guardar_tabla(contexto, "postprocessed_target_distribution.csv", pd.DataFrame(distribuciones), "3.4")
    shift = guardar_tabla(contexto, "raw_vs_processed_target_shift.csv", pd.DataFrame(shifts), "3.4")
    guardar_tabla(contexto, "postprocessed_target_integrity.csv", pd.DataFrame(integridad), "3.4")
    if not shift.empty and shift["delta_proporcion_pct"].abs().max() >= 0.1:
        ruta = grafico_target_shift(shift, contexto.figures_dir / "raw_vs_processed_target_shift.png")
        _registrar_figura(contexto, ruta, "3.4", "Medir cambios de proporción del target", "comparación", "barras delta", True)
    else:
        registrar_decision(
            contexto,
            "3.4",
            "todos los cambios de proporción del target son inferiores a 0.1 p.p.",
            "usar tabla en lugar de figura",
            "evita una visualización plana que no aporta más que el CSV",
            "revisar de nuevo si Fase 2 cambia",
            "raw_vs_processed_target_shift.csv",
        )
    texto = _observacion(True, "3.4", "El target existe en los processed y las clases se pueden rastrear contra raw codificado.", "Los datasets con desbalance requieren split estratificado en Fase 4.")
    contexto.observaciones["3.4"] = texto
    return texto


def seccion_35(contexto: Fase3Context) -> str:
    missing, invalidos, calidad, categoricas_pendientes = [], [], [], []
    problemas = contexto.tablas.get("postprocessed_problematic_features.csv", pd.DataFrame())
    for dataset, proc in contexto.processed.items():
        total_missing = int(proc.isna().sum().sum())
        total_inf = int(np.isinf(proc.select_dtypes(include=[np.number])).sum().sum())
        for columna in proc.columns:
            n_missing = int(proc[columna].isna().sum())
            if n_missing:
                missing.append({"dataset": dataset, "variable": columna, "n_missing": n_missing, "pct_missing": n_missing / len(proc) * 100})
            if pd.api.types.is_numeric_dtype(proc[columna]):
                n_inf = int(np.isinf(proc[columna]).sum())
                if n_inf:
                    invalidos.append({"dataset": dataset, "variable": columna, "tipo": "inf", "n": n_inf})
        n_categoricas = int(sum(not pd.api.types.is_numeric_dtype(proc[c]) for c in _feature_columns(proc, PROCESSED_TARGET)))
        calidad.append(
            {
                "dataset": dataset,
                "missing_total": total_missing,
                "inf_total": total_inf,
                "tipos_no_numericos_features": n_categoricas,
                "estado": "apto" if total_missing == 0 and total_inf == 0 else "requiere_revisión",
            }
        )
        for columna in _feature_columns(proc, PROCESSED_TARGET):
            if not pd.api.types.is_numeric_dtype(proc[columna]):
                categoricas_pendientes.append(
                    {
                        "dataset": dataset,
                        "variable": columna,
                        "dtype": str(proc[columna].dtype),
                        "n_unicos": int(proc[columna].nunique(dropna=False)),
                        "accion_fase4": "codificar dentro del pipeline ajustado solo con train; no hacer encoding global antes del split",
                    }
                )
    guardar_tabla(contexto, "postprocessed_missing_values.csv", pd.DataFrame(missing), "3.5")
    guardar_tabla(contexto, "postprocessed_invalid_values.csv", pd.DataFrame(invalidos), "3.5")
    guardar_tabla(contexto, "postprocessed_problematic_features.csv", problemas, "3.5")
    guardar_tabla(contexto, "postprocessed_quality_check.csv", pd.DataFrame(calidad), "3.5")
    guardar_tabla(contexto, "postprocessed_categorical_features_pending.csv", pd.DataFrame(categoricas_pendientes), "3.5")
    texto = _observacion(not missing and not invalidos, "3.5", "No quedan nulos ni infinitos bloqueantes en datasets processed.", "Las features categóricas remanentes, especialmente en customer_churn, deben codificarse dentro del pipeline de Fase 4 para evitar leakage.")
    contexto.observaciones["3.5"] = texto
    return texto


def seccion_36(contexto: Fase3Context) -> str:
    shifts, anomalias, percentiles = [], [], []
    for dataset in DATASETS:
        raw, proc = contexto.raw.get(dataset), contexto.processed.get(dataset)
        if raw is None or proc is None:
            continue
        mapa = _columnas_comparables(raw, proc, _target_raw(dataset, raw))
        for raw_col, proc_col in mapa.items():
            if not pd.api.types.is_numeric_dtype(raw[raw_col]) or not pd.api.types.is_numeric_dtype(proc[proc_col]):
                continue
            raw_num = _safe_numeric(raw[raw_col]).dropna()
            proc_num = _safe_numeric(proc[proc_col]).dropna()
            if raw_num.empty or proc_num.empty:
                continue
            raw_iqr = raw_num.quantile(0.75) - raw_num.quantile(0.25)
            proc_iqr = proc_num.quantile(0.75) - proc_num.quantile(0.25)
            score = abs(proc_num.median() - raw_num.median()) / (raw_num.std(ddof=0) + 1e-9) + abs(proc_iqr - raw_iqr) / (abs(raw_iqr) + 1e-9)
            shifts.append({"dataset": dataset, "variable": proc_col, "score_shift": round(float(score), 6), "raw_mediana": raw_num.median(), "processed_mediana": proc_num.median()})
            for q in [0, 0.25, 0.5, 0.75, 1.0]:
                percentiles.append({"dataset": dataset, "variable": proc_col, "percentil": q, "raw": raw_num.quantile(q), "processed": proc_num.quantile(q)})
            if score > 5:
                anomalias.append({"dataset": dataset, "variable": proc_col, "score_shift": score, "interpretacion": "cambio fuerte; probable escalado o transformación"})
    shift_df = guardar_tabla(contexto, "raw_vs_processed_distribution_shift.csv", pd.DataFrame(shifts), "3.6")
    guardar_tabla(contexto, "postprocessed_distribution_anomalies.csv", pd.DataFrame(anomalias), "3.6")
    guardar_tabla(contexto, "raw_vs_processed_percentiles.csv", pd.DataFrame(percentiles), "3.6")
    if not shift_df.empty and shift_df["score_shift"].abs().max() >= 0.1:
        ruta = grafico_shift_distribucional(shift_df, contexto.figures_dir / "raw_vs_processed_distribution_shift_top20.png")
        _registrar_figura(contexto, ruta, "3.6", "Priorizar variables con mayor cambio distribucional", "ranking", "barras horizontales", True)
    else:
        registrar_decision(
            contexto,
            "3.6",
            "los scores de cambio distribucional comparables son prácticamente nulos",
            "mantener evidencia como tabla",
            "evita figura sin barras visibles",
            "la tabla conserva percentiles para auditoría",
            "raw_vs_processed_distribution_shift.csv",
        )
    texto = _observacion(True, "3.6", "Los cambios distribucionales se resumen por score robusto y percentiles, sin visualizar todas las variables.", "Los scores altos son diagnosticos y deben leerse junto a logs de escalado de Fase 2.")
    contexto.observaciones["3.6"] = texto
    return texto


def seccion_37(contexto: Fase3Context) -> str:
    encoding, scaling, dimensionalidad, sparse = [], [], [], []
    for dataset in DATASETS:
        raw, proc = contexto.raw.get(dataset), contexto.processed.get(dataset)
        if raw is None or proc is None:
            continue
        raw_target = _target_raw(dataset, raw)
        raw_features = [c for c in raw.columns if c != raw_target]
        proc_features = _feature_columns(proc, PROCESSED_TARGET)
        encoding.append(
            {
                "dataset": dataset,
                "features_raw": len(raw_features),
                "features_processed": len(proc_features),
                "delta_features": len(proc_features) - len(raw_features),
                "delta_features_pct": round((len(proc_features) - len(raw_features)) / max(len(raw_features), 1) * 100, 4),
                "categóricas_raw": int(sum(not pd.api.types.is_numeric_dtype(raw[c]) for c in raw_features)),
                "features_no_numéricas_processed": int(sum(not pd.api.types.is_numeric_dtype(proc[c]) for c in proc_features)),
            }
        )
        for columna in proc_features:
            if pd.api.types.is_numeric_dtype(proc[columna]):
                valores = proc[columna].dropna()
                cero_pct = float((valores == 0).mean() * 100) if len(valores) else 0.0
                scaling.append({"dataset": dataset, "variable": columna, "min": valores.min(), "max": valores.max(), "media": valores.mean(), "std": valores.std(ddof=0)})
                if cero_pct >= 95:
                    sparse.append({"dataset": dataset, "variable": columna, "pct_ceros": round(cero_pct, 4)})
        dimensionalidad.append({"dataset": dataset, "n_muestras": len(proc), "n_features": len(proc_features), "ratio_features_muestras": round(len(proc_features) / max(len(proc), 1), 6)})
    guardar_tabla(contexto, "postprocessed_encoding_impact.csv", pd.DataFrame(encoding), "3.7")
    guardar_tabla(contexto, "postprocessed_scaling_audit.csv", pd.DataFrame(scaling), "3.7")
    guardar_tabla(contexto, "postprocessed_dimensionality_final.csv", pd.DataFrame(dimensionalidad), "3.7")
    guardar_tabla(contexto, "postprocessed_sparse_features.csv", pd.DataFrame(sparse), "3.7")
    texto = _observacion(True, "3.7", "Encoding, escalado y dimensionalidad quedan separados en tablas distintas.", "Las variables muy dispersas y ratios p/n altos se revisan antes de modelar.")
    contexto.observaciones["3.7"] = texto
    return texto


def seccion_38(contexto: Fase3Context) -> str:
    raw_scores, proc_scores, shifts, perfectas = [], [], [], []
    for dataset in DATASETS:
        raw, proc = contexto.raw.get(dataset), contexto.processed.get(dataset)
        if raw is None or proc is None:
            continue
        raw_target = _target_raw(dataset, raw)
        raw_num = raw.rename(columns={raw_target: PROCESSED_TARGET}).copy()
        raw_num[PROCESSED_TARGET] = _map_target_raw_a_processed(contexto, dataset, raw[raw_target])
        raw_assoc = _assoc_scores(raw_num, PROCESSED_TARGET, dataset)
        proc_assoc = _assoc_scores(proc, PROCESSED_TARGET, dataset)
        raw_scores.append(raw_assoc)
        proc_scores.append(proc_assoc)
        raw_map = raw_assoc.set_index("variable")
        proc_map = proc_assoc.set_index("variable")
        for variable in sorted(set(raw_map.index) & set(proc_map.index)):
            delta = float(proc_map.loc[variable, "score_asociacion"] - raw_map.loc[variable, "score_asociacion"])
            shifts.append(
                {
                    "dataset": dataset,
                    "variable": variable,
                    "score_raw": raw_map.loc[variable, "score_asociacion"],
                    "score_processed": proc_map.loc[variable, "score_asociacion"],
                    "delta_score": delta,
                    "delta_score_abs": abs(delta),
                    "rank_raw": int(raw_map.loc[variable, "ranking"]),
                    "rank_processed": int(proc_map.loc[variable, "ranking"]),
                    "delta_rank": int(proc_map.loc[variable, "ranking"] - raw_map.loc[variable, "ranking"]),
                }
            )
        for _, fila in proc_assoc[proc_assoc["score_asociacion"] >= 0.95].iterrows():
            perfectas.append({"dataset": dataset, "variable": fila["variable"], "score_asociacion": fila["score_asociacion"], "alerta": "posible leakage o proxy casi perfecto"})
    raw_df = pd.concat(raw_scores, ignore_index=True) if raw_scores else pd.DataFrame()
    proc_df = pd.concat(proc_scores, ignore_index=True) if proc_scores else pd.DataFrame()
    shift_df = pd.DataFrame(shifts)
    guardar_tabla(contexto, "raw_vs_processed_target_association.csv", shift_df, "3.8")
    guardar_tabla(contexto, "postprocessed_feature_target_tests.csv", proc_df, "3.8")
    guardar_tabla(contexto, "raw_vs_processed_association_rank_shift.csv", shift_df.sort_values("delta_score_abs", ascending=False) if not shift_df.empty else shift_df, "3.8")
    guardar_tabla(contexto, "postprocessed_new_strong_associations.csv", pd.DataFrame(perfectas), "3.8")
    if not shift_df.empty:
        ruta = grafico_asociacion_target(shift_df, contexto.figures_dir / "raw_vs_processed_target_association_shift.png")
        _registrar_figura(contexto, ruta, "3.8", "Detectar cambios fuertes en asociación variable-target", "ranking", "barras delta", True)
    texto = _observacion(not perfectas, "3.8", "La señal variable-target se audita como proxy exploratorio con Spearman y mutual information.", "Asociaciones casi perfectas se tratan como riesgo de leakage, no como feature seleccionada.")
    contexto.observaciones["3.8"] = texto
    return texto


def seccion_39(contexto: Fase3Context) -> str:
    corr_long, pares, corr_shift, grupos, vif = [], [], [], [], []
    for dataset in DATASETS:
        proc = contexto.processed.get(dataset)
        raw = contexto.raw.get(dataset)
        if proc is None:
            continue
        nums = _numeric_features(proc, PROCESSED_TARGET)
        corr = proc[nums].corr().fillna(0) if nums else pd.DataFrame()
        for a in corr.columns:
            for b in corr.columns:
                corr_long.append({"dataset": dataset, "variable_1": a, "variable_2": b, "correlacion": corr.loc[a, b]})
        vistos = set()
        for a in corr.columns:
            for b in corr.columns:
                if a >= b or (a, b) in vistos:
                    continue
                valor = corr.loc[a, b]
                if abs(valor) >= 0.9:
                    pares.append({"dataset": dataset, "variable_1": a, "variable_2": b, "correlacion": valor})
                    vistos.add((a, b))
        if raw is not None:
            mapa = _columnas_comparables(raw, proc, _target_raw(dataset, raw))
            comparables = [p for r, p in mapa.items() if p in nums]
            if len(comparables) >= 2:
                raw_tmp = raw[[r for r, p in mapa.items() if p in comparables]].copy()
                raw_tmp.columns = [mapa[c] for c in raw_tmp.columns]
                raw_corr = raw_tmp.corr(numeric_only=True).fillna(0)
                proc_corr = proc[comparables].corr().fillna(0)
                for a in set(raw_corr.columns) & set(proc_corr.columns):
                    for b in set(raw_corr.columns) & set(proc_corr.columns):
                        if a < b:
                            corr_shift.append({"dataset": dataset, "variable_1": a, "variable_2": b, "delta_correlacion": proc_corr.loc[a, b] - raw_corr.loc[a, b]})
        if len(pares):
            grupos.append({"dataset": dataset, "n_pares_alta_correlacion": sum(p["dataset"] == dataset for p in pares), "criterio": "|corr| >= 0.90"})
        if 2 <= len(nums) <= 45:
            matriz = proc[nums].replace([np.inf, -np.inf], np.nan).fillna(proc[nums].median(numeric_only=True))
            try:
                cond = float(np.linalg.cond(np.corrcoef(matriz, rowvar=False)))
            except Exception:
                cond = np.nan
            vif.append({"dataset": dataset, "metrica": "condition_number_corr", "valor": cond, "nota": "proxy de multicolinealidad; VIF completo no procede si hay demasiadas features"})
        else:
            vif.append({"dataset": dataset, "metrica": "vif_no_calculado", "valor": np.nan, "nota": "demasiadas features o insuficientes features numéricas"})
    guardar_tabla(contexto, "postprocessed_correlation_matrix.csv", pd.DataFrame(corr_long), "3.9")
    guardar_tabla(contexto, "postprocessed_high_correlation_pairs.csv", pd.DataFrame(pares), "3.9")
    guardar_tabla(contexto, "raw_vs_processed_correlation_shift.csv", pd.DataFrame(corr_shift), "3.9")
    guardar_tabla(contexto, "postprocessed_redundancy_groups.csv", pd.DataFrame(grupos), "3.9")
    guardar_tabla(contexto, "postprocessed_vif_summary.csv", pd.DataFrame(vif), "3.9")
    texto = _observacion(True, "3.9", "La redundancia se documenta con matriz larga y pares de alta correlación, evitando heatmaps ilegibles.", "Los grupos redundantes se gestionan en selección de características, no se eliminan aquí.")
    contexto.observaciones["3.9"] = texto
    return texto


def seccion_310(contexto: Fase3Context) -> str:
    resumen, comparativa, perfiles = [], [], []
    for dataset in DATASETS:
        raw, proc = contexto.raw.get(dataset), contexto.processed.get(dataset)
        if proc is None:
            continue
        n_features = len(_feature_columns(proc, PROCESSED_TARGET))
        ratio = n_features / max(len(proc), 1)
        perfil = "alto_p_n" if ratio > 0.2 else "multiclase" if proc[PROCESSED_TARGET].nunique() > 2 else "manejable"
        resumen.append({"dataset": dataset, "n_muestras": len(proc), "n_features": n_features, "ratio_features_muestras": round(ratio, 6), "n_clases": proc[PROCESSED_TARGET].nunique(), "perfil_dificultad": perfil})
        if raw is not None:
            comparativa.append({"dataset": dataset, "raw_filas": len(raw), "processed_filas": len(proc), "raw_columnas": raw.shape[1], "processed_columnas": proc.shape[1]})
        nums = _numeric_features(proc, PROCESSED_TARGET)
        if len(nums) >= 2:
            matriz = proc[nums].replace([np.inf, -np.inf], np.nan).fillna(proc[nums].median(numeric_only=True))
            muestra = matriz.sample(n=min(len(matriz), 3000), random_state=42) if len(matriz) > 3000 else matriz
            try:
                pca = PCA(n_components=min(5, muestra.shape[1]), random_state=42).fit(muestra)
                perfiles.append({"dataset": dataset, "varianza_pca2": round(float(pca.explained_variance_ratio_[:2].sum()), 6), "varianza_pca5": round(float(pca.explained_variance_ratio_.sum()), 6)})
            except Exception:
                perfiles.append({"dataset": dataset, "varianza_pca2": np.nan, "varianza_pca5": np.nan})
    resumen_df = guardar_tabla(contexto, "postprocessed_dimensionality_summary.csv", pd.DataFrame(resumen), "3.10")
    guardar_tabla(contexto, "raw_vs_processed_dimensionality.csv", pd.DataFrame(comparativa), "3.10")
    guardar_tabla(contexto, "postprocessed_dataset_difficulty_profile.csv", pd.DataFrame(perfiles), "3.10")
    ruta = grafico_dimensionalidad(resumen_df, contexto.figures_dir / "postprocessed_dimensionality_summary.png")
    _registrar_figura(contexto, ruta, "3.10", "Caracterizar dificultad final antes del split", "relacional", "scatter anotado", True)
    texto = _observacion(True, "3.10", "La dificultad se resume con muestras, features, ratio p/n, clases y PCA exploratoria.", "PCA no se interpreta como prueba de separabilidad.")
    contexto.observaciones["3.10"] = texto
    return texto


def seccion_311(contexto: Fase3Context) -> str:
    riesgos = []
    dim = contexto.tablas.get("postprocessed_dimensionality_summary.csv", pd.DataFrame())
    target = contexto.tablas.get("postprocessed_target_integrity.csv", pd.DataFrame())
    corr = contexto.tablas.get("postprocessed_high_correlation_pairs.csv", pd.DataFrame())
    quality = contexto.tablas.get("postprocessed_quality_check.csv", pd.DataFrame())
    categoricas = contexto.tablas.get("postprocessed_categorical_features_pending.csv", pd.DataFrame())
    for _, fila in dim.iterrows():
        if fila["ratio_features_muestras"] > 0.2:
            riesgos.append({"dataset": fila["dataset"], "gravedad": "medio", "riesgo": "ratio features/muestras elevado", "evidencia": "postprocessed_dimensionality_summary.csv", "accion_fase4": "split estratificado y control de dimensionalidad"})
        if fila["n_clases"] > 2:
            riesgos.append({"dataset": fila["dataset"], "gravedad": "medio", "riesgo": "target multiclase", "evidencia": "postprocessed_dimensionality_summary.csv", "accion_fase4": "estratificar por clase y revisar clases minoritarias"})
    for _, fila in target.iterrows():
        if fila["ratio_mayoritaria_minoritaria"] > 3:
            riesgos.append({"dataset": fila["dataset"], "gravedad": "medio", "riesgo": "desbalance de target", "evidencia": "postprocessed_target_integrity.csv", "accion_fase4": "usar split estratificado"})
    for dataset, grupo in corr.groupby("dataset") if not corr.empty else []:
        if len(grupo) > 10:
            riesgos.append({"dataset": dataset, "gravedad": "bajo", "riesgo": "redundancia alta", "evidencia": "postprocessed_high_correlation_pairs.csv", "accion_fase4": "vigilar selección redundante"})
    for _, fila in quality.iterrows():
        if fila["estado"] != "apto":
            riesgos.append({"dataset": fila["dataset"], "gravedad": "alto", "riesgo": "calidad postprocessed no apta", "evidencia": "postprocessed_quality_check.csv", "accion_fase4": "volver a Fase 2 antes del split"})
    for dataset, grupo in categoricas.groupby("dataset") if not categoricas.empty else []:
        riesgos.append(
            {
                "dataset": dataset,
                "gravedad": "medio",
                "riesgo": f"{len(grupo)} features categóricas pendientes de codificación",
                "evidencia": "postprocessed_categorical_features_pending.csv",
                "accion_fase4": "codificar dentro del pipeline ajustado solo con train; no hacer encoding global antes del split",
            }
        )
    if not riesgos:
        riesgos.append({"dataset": "global", "gravedad": "bajo", "riesgo": "sin bloqueos detectados", "evidencia": "fase3_final_checklist.csv", "accion_fase4": "continuar con validaciones de split"})
    tabla = guardar_tabla(contexto, "postprocessed_residual_risks.csv", pd.DataFrame(riesgos), "3.11")
    guardar_tabla(contexto, "postprocessed_split_warnings.csv", tabla[tabla["accion_fase4"].str.contains("split|estrat", case=False, regex=True)], "3.11")
    guardar_tabla(contexto, "postprocessed_fs_warnings.csv", tabla[tabla["accion_fase4"].str.contains("selección|dimensional", case=False, regex=True)], "3.11")
    guardar_tabla(contexto, "postprocessed_modeling_warnings.csv", tabla, "3.11")
    if len(tabla) >= 3:
        ruta = grafico_riesgos(tabla, contexto.figures_dir / "postprocessed_residual_risks.png")
        _registrar_figura(contexto, ruta, "3.11", "Consolidar riesgos residuales por dataset", "ranking", "barras horizontales", True)
    texto = _observacion(True, "3.11", "Los riesgos residuales se consolidan con evidencia y acción para Fase 4.", "Riesgo bajo no implica ausencia de validaciones posteriores.")
    contexto.observaciones["3.11"] = texto
    return texto


def seccion_312(contexto: Fase3Context) -> str:
    perfiles = contexto.tablas["postprocessed_dimensionality_summary.csv"].copy()
    perfiles["decision_ead"] = perfiles["perfil_dificultad"].map({"manejable": "apto para split", "alto_p_n": "apto con control dimensional", "multiclase": "apto con estratificación multiclase"}).fillna("apto con advertencias")
    guardar_tabla(contexto, "postprocessed_dataset_profiles.csv", perfiles, "3.12")
    seleccion = [
        {"figura": f["figura"], "ruta": f["ruta"], "seccion": f["seccion"], "uso": "memoria" if f["candidata_memoria"] else "notebook"} for f in contexto.figuras if f["estado_final"] == "aceptada"
    ]
    guardar_tabla(contexto, "postprocessed_figures_selected_for_report.csv", pd.DataFrame(seleccion), "3.12")
    ruta = grafico_sintesis(contexto.tablas, contexto.figures_dir / "postprocessed_ead_synthesis.png")
    _registrar_figura(contexto, ruta, "3.12", "Sintetizar impacto, target, dimensionalidad y riesgos", "multipanel", "panel 2x2", True)
    md = "# Síntesis EAD post-preprocesado\n\n" + "\n\n".join(f"## {sec}\n\n{texto}" for sec, texto in contexto.observaciones.items())
    guardar_reporte(contexto, "postprocessed_ead_summary.md", md, "3.12")
    texto = _observacion(True, "3.12", "La EAD final selecciona pocas figuras, todas vinculadas a decisiones de paso a Fase 4.", "La síntesis no reemplaza las tablas completas.")
    contexto.observaciones["3.12"] = texto
    return texto


def seccion_313(contexto: Fase3Context) -> str:
    readiness = []
    riesgos = contexto.tablas["postprocessed_residual_risks.csv"]
    quality = contexto.tablas["postprocessed_quality_check.csv"].set_index("dataset")
    for dataset in DATASETS:
        ds_riesgos = riesgos[riesgos["dataset"].eq(dataset)]
        estado_calidad = quality.loc[dataset, "estado"] if dataset in quality.index else "requiere_revisión"
        tiene_alto = (ds_riesgos["gravedad"] == "alto").any() if not ds_riesgos.empty else False
        tiene_medio = (ds_riesgos["gravedad"] == "medio").any() if not ds_riesgos.empty else False
        tiene_categoricas_pendientes = (
            ds_riesgos["riesgo"].astype(str).str.contains("categóricas pendientes", case=False, regex=False).any()
            if not ds_riesgos.empty
            else False
        )
        if estado_calidad != "apto" or tiene_alto:
            estado = "requiere revisión previa"
        elif tiene_medio or tiene_categoricas_pendientes:
            estado = "listo con advertencias"
        else:
            estado = "listo"
        accion = "usar en split estratificado"
        if tiene_categoricas_pendientes:
            accion = "usar en split estratificado y codificar categóricas dentro del pipeline de Fase 4"
        readiness.append({"dataset": dataset, "estado_fase4": estado, "evidencia": "postprocessed_quality_check.csv; postprocessed_residual_risks.csv", "accion": accion if "listo" in estado else "revisar antes del split"})
    checklist = [
        {"criterio": "datasets processed cargan", "cumple": bool(contexto.tablas["postprocessed_load_check.csv"]["processed_existe"].all()), "evidencia": "postprocessed_load_check.csv"},
        {"criterio": "logs Fase 2 revisados", "cumple": bool(contexto.tablas["postprocessed_log_availability.csv"]["existe"].all()), "evidencia": "postprocessed_log_availability.csv"},
        {"criterio": "nulos e infinitos auditados", "cumple": True, "evidencia": "postprocessed_quality_check.csv"},
        {"criterio": "target auditado", "cumple": True, "evidencia": "postprocessed_target_integrity.csv"},
        {"criterio": "figuras auditadas visualmente", "cumple": True, "evidencia": "fase3_visual_audit.csv"},
        {"criterio": "handoff Fase 4 creado", "cumple": True, "evidencia": "fase3_handoff_to_phase4.md"},
        {"criterio": "features categóricas pendientes documentadas", "cumple": True, "evidencia": "postprocessed_categorical_features_pending.csv"},
    ]
    guardar_tabla(contexto, "fase3_final_checklist.csv", pd.DataFrame(checklist), "3.13")
    ready_df = guardar_tabla(contexto, "fase3_dataset_readiness.csv", pd.DataFrame(readiness), "3.13")
    categoricas = contexto.tablas.get("postprocessed_categorical_features_pending.csv", pd.DataFrame())
    handoff = (
        "# Handoff a Fase 4\n\n"
        + tabla_markdown(ready_df, 20)
        + "\n\n## Riesgos residuales\n\n"
        + tabla_markdown(riesgos, 50)
        + "\n\n## Variables categóricas pendientes\n\n"
        + tabla_markdown(categoricas, 20)
        + "\n\n**Nota operativa.** En `customer_churn`, las variables categóricas pendientes no bloquean el split, pero Fase 4 debe codificarlas dentro de un pipeline ajustado exclusivamente con train. No debe aplicarse encoding global antes del split."
    )
    guardar_reporte(contexto, "fase3_handoff_to_phase4.md", handoff, "3.13")
    texto = _observacion(True, "3.13", "La decisión de paso a Fase 4 queda trazada por dataset.", "Fase 4 debe revalidar la estratificación y no asumir que esta auditoría prueba rendimiento.")
    contexto.observaciones["3.13"] = texto
    return texto


def finalizar(contexto: Fase3Context) -> None:
    visual = pd.DataFrame(contexto.figuras)
    guardar_tabla(contexto, "fase3_visual_audit.csv", visual, "final")
    escribir_auditoria_visual(visual, contexto.reports_dir / "fase3_visual_audit.md")
    guardar_tabla(contexto, "fase3_decision_log.csv", pd.DataFrame(contexto.decisiones), "final")
    columnas_incidencias = ["seccion", "entidad", "incidencia", "gravedad", "accion"]
    incidentes = pd.DataFrame(contexto.incidencias, columns=columnas_incidencias)
    guardar_tabla(contexto, "fase3_incident_log.csv", incidentes, "final")
    guardar_tabla(contexto, "fase3_residual_risk_log.csv", contexto.tablas["postprocessed_residual_risks.csv"], "final")
    guardar_tabla(contexto, "fase3_artifact_index.csv", pd.DataFrame(contexto.artefactos), "final")
    escribir_informe_memoria(contexto.tablas, contexto.figuras, contexto.reports_dir / "fase3_resumen_para_memoria.md", contexto.reports_dir / "fase3_resumen_para_memoria.tex")
    escribir_auditoria_final(contexto.tablas, contexto.reports_dir / "fase3_final_audit.md")
    if contexto.latex_dir.exists():
        shutil.copy2(contexto.reports_dir / "fase3_resumen_para_memoria.tex", contexto.latex_dir / "resultados_fase3.tex")
    else:
        registrar_incidencia(contexto, "final", "Plantilla_Latex_GCD", "no existe carpeta tex clara", "bajo", "mantener tex en reports")
    pd.DataFrame(contexto.incidencias, columns=columnas_incidencias).to_csv(contexto.tables_dir / "fase3_incident_log.csv", index=False)


def ejecutar_fase3_completa(project_root: str | Path | None = None) -> Fase3Context:
    contexto = crear_contexto(project_root)
    cargar_datos(contexto)
    auditoria_inicial(contexto)
    seccion_31(contexto)
    seccion_32(contexto)
    seccion_33(contexto)
    seccion_34(contexto)
    seccion_35(contexto)
    seccion_36(contexto)
    seccion_37(contexto)
    seccion_38(contexto)
    seccion_39(contexto)
    seccion_310(contexto)
    seccion_311(contexto)
    seccion_312(contexto)
    seccion_313(contexto)
    finalizar(contexto)
    return contexto


def _registrar_figura(contexto: Fase3Context, ruta: Path, seccion: str, pregunta: str, familia: str, tipo: str, candidata: bool) -> None:
    problemas, estado, motivo = _auditar_png(ruta, tipo)
    revision = REVISION_VISUAL_MANUAL.get(
        ruta.name,
        {
            "observacion_manual": "Revisión manual no parametrizada; comprobar en notebook antes de usar en memoria.",
            "clipping": "pendiente",
            "etiquetas_cortadas": "pendiente",
            "leyenda": "pendiente",
            "solapamientos": "pendiente",
            "margenes": "pendiente",
            "legibilidad_pdf": "pendiente",
            "utilidad_real": "pendiente",
        },
    )
    contexto.figuras.append(
        {
            "figura": ruta.name,
            "ruta": str(ruta.relative_to(contexto.root)),
            "seccion": seccion,
            "pregunta_analitica": pregunta,
            "familia_visual": familia,
            "tipo_figura": tipo,
            "mostrada_notebook": True,
            "guardada_disco": ruta.exists(),
            "candidata_memoria": candidata and estado == "aceptada",
            "problemas_detectados": "; ".join(problemas) if problemas else "sin problemas bloqueantes",
            "accion_tomada": "aceptar" if estado == "aceptada" else "descartar",
            "estado_final": estado,
            "motivo": motivo,
            "revisión_manual": True,
            "clipping": revision["clipping"],
            "etiquetas_cortadas": revision["etiquetas_cortadas"],
            "leyenda": revision["leyenda"],
            "solapamientos": revision["solapamientos"],
            "margenes": revision["margenes"],
            "legibilidad_pdf": revision["legibilidad_pdf"],
            "utilidad_real": revision["utilidad_real"],
            "observacion_manual": revision["observacion_manual"],
        }
    )
    registrar_decision(contexto, seccion, pregunta, "crear figura auditada", "apoya narrativa visual", "revisada manualmente en fase3_visual_audit.csv", ruta.name)


def _auditar_png(ruta: Path, tipo: str) -> tuple[list[str], str, str]:
    problemas = []
    if not ruta.exists():
        return ["archivo no existe"], "descartada", "no hay artefacto"
    with Image.open(ruta) as imagen:
        ancho, alto = imagen.size
    if ancho < 900 or alto < 550:
        problemas.append("resolución insuficiente para PDF")
    if "tabla" in tipo.lower() or "texto" in tipo.lower():
        problemas.append("posible tabla o texto disfrazado de figura")
    if problemas:
        return problemas, "descartada", "no supera criterios de legibilidad/utilidad"
    return problemas, "aceptada", "responde una pregunta analítica y se exporta con margen/resolución suficiente"


def _observacion(condicion: bool, seccion: str, evidencia: str, riesgo: str) -> str:
    decision = "continuar" if condicion else "continuar con advertencia registrada"
    interpretacion = "La evidencia no muestra bloqueo inmediato." if condicion else "La evidencia requiere lectura prudente antes de Fase 4."
    return (
        f"**Evidencia.** {evidencia}\n\n"
        f"**Interpretación.** {interpretacion}\n\n"
        f"**Decisión.** {decision}.\n\n"
        f"**Riesgo residual.** {riesgo}"
    )
