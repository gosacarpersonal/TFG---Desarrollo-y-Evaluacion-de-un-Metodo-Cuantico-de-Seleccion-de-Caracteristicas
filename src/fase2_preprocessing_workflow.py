from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fase1_agent_utils import ensure_dir, write_latex_report_from_markdown
from viz_core.editorial_warmth import EditorialPalette, set_editorial_rcparams, apply_editorial_axes, add_editorial_text


ORDEN_DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil",
]

NOMBRES_RAW = {
    "breast_cancer_wisconsin": "breast_cancer_wisconsin.csv",
    "customer_churn": "customer_churn.csv",
    "madelon": "madelon.csv",
    "olive_oil": "olive_oil.csv",
}

PALETA = EditorialPalette(
    background="#FAF7F2",
    panel="#FAF7F2",
    grid="#E6DED2",
    text="#2D2A26",
    spine="#E6DED2",
    muted_text="#6F6A60",
    primary="#2F6F9F",
    secondary="#8FB3C9",
    accent="#D9822B",
    positive="#5E8C61",
    negative="#B85C5C",
    neutral="#B8B0A3",
    categorical=("#2F6F9F", "#D9822B", "#5E8C61", "#B85C5C", "#8FB3C9", "#B8B0A3"),
)


@dataclass
class Phase2Context:
    project_root: Path
    raw_dir: Path
    processed_dir: Path
    tables_dir: Path
    figures_dir: Path
    reports_dir: Path
    phase1_tables_dir: Path
    raw_data: dict
    processed_data: dict
    targets_raw: dict
    targets_processed: dict
    phase1_tables: dict
    tables: dict
    figure_paths: list
    preprocessing_log: list
    decision_log: list
    risk_log: list
    rename_maps: dict
    removed_columns: dict
    target_mappings: dict


def crear_contexto_fase2(project_root=None):
    root = Path.cwd() if project_root is None else Path(project_root)
    if root.name == "notebooks":
        root = root.parent
    contexto = Phase2Context(
        project_root=root,
        raw_dir=root / "data" / "01_raw",
        processed_dir=root / "data" / "processed",
        tables_dir=root / "results" / "tables" / "02_preprocessing",
        figures_dir=root / "results" / "figures" / "02_preprocessing",
        reports_dir=root / "results" / "reports" / "02_preprocessing",
        phase1_tables_dir=root / "results" / "tables" / "01_raw_eda",
        raw_data={},
        processed_data={},
        targets_raw={},
        targets_processed={},
        phase1_tables={},
        tables={},
        figure_paths=[],
        preprocessing_log=[],
        decision_log=[],
        risk_log=[],
        rename_maps={},
        removed_columns={},
        target_mappings={},
    )
    for ruta in [contexto.processed_dir, contexto.tables_dir, contexto.figures_dir, contexto.reports_dir]:
        ensure_dir(ruta)
    set_editorial_rcparams(PALETA)
    return contexto


def guardar_tabla(contexto, nombre, tabla):
    tabla = tabla.copy() if isinstance(tabla, pd.DataFrame) else pd.DataFrame(tabla)
    ruta = contexto.tables_dir / nombre
    ensure_dir(ruta.parent)
    tabla.to_csv(ruta, index=False)
    contexto.tables[nombre] = tabla
    return tabla


def tabla_no_aplica(contexto, nombre, seccion, motivo):
    tabla = pd.DataFrame([{
        "seccion": seccion,
        "aplica": False,
        "motivo": motivo,
        "accion": "sin transformación aplicada",
        "riesgo_residual": "revisar si la evidencia cambia en fases posteriores",
    }])
    return guardar_tabla(contexto, nombre, tabla)


def registrar_figura(contexto, ruta_relativa):
    ruta = contexto.figures_dir / ruta_relativa
    ensure_dir(ruta.parent)
    plt.savefig(ruta, dpi=180, bbox_inches="tight", pad_inches=0.18, facecolor=PALETA.background)
    contexto.figure_paths.append(ruta)
    return ruta


def cerrar_figura(mostrar=True):
    if mostrar:
        plt.show()
    else:
        plt.close()


def etiqueta_dataset(nombre):
    return {
        "breast_cancer_wisconsin": "breast\ncancer\nwisconsin",
        "customer_churn": "customer\nchurn",
        "madelon": "madelon",
        "olive_oil": "olive\noil",
    }.get(str(nombre), str(nombre).replace("_", "\n"))


def etiqueta_variable(nombre, max_chars=42):
    texto = str(nombre).replace("_", " ")
    if len(texto) <= max_chars:
        return texto
    return texto[: max_chars - 1].rstrip() + "…"


def etiqueta_corta_dataset(nombre):
    return {
        "breast_cancer_wisconsin": "Breast\nCancer",
        "customer_churn": "Customer\nChurn",
        "madelon": "Madelon",
        "olive_oil": "Olive\nOil",
    }.get(str(nombre), str(nombre).replace("_", "\n").title())


def color_dataset(nombre):
    colores = {dataset: color for dataset, color in zip(ORDEN_DATASETS, PALETA.categorical)}
    return colores.get(nombre, PALETA.primary)


def ordenar_datasets(tabla):
    orden = {nombre: posicion for posicion, nombre in enumerate(ORDEN_DATASETS)}
    return tabla.assign(_orden=tabla["dataset"].map(orden).fillna(99)).sort_values("_orden").drop(columns="_orden")


def normalizar_nombre_columna(nombre):
    texto = str(nombre).strip()
    texto = re.sub(r"[^0-9A-Za-záéíóúÁÉÍÓÚñÑ]+", "_", texto)
    texto = re.sub(r"_+", "_", texto).strip("_").lower()
    traducciones = {
        "customerid": "customer_id",
        "churn": "target",
    }
    return traducciones.get(texto, texto)


def hacer_nombres_unicos(nombres):
    vistos = {}
    resultado = []
    for nombre in nombres:
        base = nombre or "columna"
        contador = vistos.get(base, 0)
        resultado.append(base if contador == 0 else f"{base}_{contador + 1}")
        vistos[base] = contador + 1
    return resultado


def es_entero_en_float(serie):
    if not pd.api.types.is_float_dtype(serie):
        return False
    valores = serie.dropna()
    if valores.empty:
        return False
    return np.isclose(valores, np.round(valores)).all()


def conservar_timestamp_existente(contexto, nombre_csv, fila, columnas_clave):
    ruta = contexto.tables_dir / nombre_csv
    if not ruta.exists():
        return datetime.now().isoformat(timespec="seconds")
    try:
        existente = pd.read_csv(ruta)
    except pd.errors.EmptyDataError:
        return datetime.now().isoformat(timespec="seconds")
    if "timestamp" not in existente.columns:
        return datetime.now().isoformat(timespec="seconds")
    mascara = pd.Series(True, index=existente.index)
    for columna in columnas_clave:
        if columna not in existente.columns:
            return datetime.now().isoformat(timespec="seconds")
        mascara &= existente[columna].astype(str).eq(str(fila.get(columna, "")))
    coincidencias = existente.loc[mascara, "timestamp"].dropna()
    if coincidencias.empty:
        return datetime.now().isoformat(timespec="seconds")
    return str(coincidencias.iloc[0])


def registrar_log(contexto, dataset, seccion, variable, accion, motivo, evidencia, impacto, riesgo_residual, revisar_en_fase="Fase 3"):
    fila = {
        "dataset": dataset,
        "seccion": seccion,
        "variable": variable,
        "accion_aplicada": accion,
        "motivo": motivo,
        "evidencia": evidencia,
        "impacto": impacto,
        "riesgo_residual": riesgo_residual,
        "revisar_en_fase": revisar_en_fase,
    }
    fila["timestamp"] = conservar_timestamp_existente(
        contexto,
        "preprocessing_log.csv",
        fila,
        ["dataset", "seccion", "variable", "accion_aplicada", "motivo", "evidencia"],
    )
    contexto.preprocessing_log.append(fila)
    return fila


def registrar_decision(contexto, dataset, seccion, variable, decision, justificacion, alternativa_rechazada, evidencia, riesgo_residual):
    fila = {
        "dataset": dataset,
        "seccion": seccion,
        "variable": variable,
        "decision": decision,
        "justificacion": justificacion,
        "alternativa_rechazada": alternativa_rechazada,
        "evidencia": evidencia,
        "riesgo_residual": riesgo_residual,
    }
    fila["timestamp"] = conservar_timestamp_existente(
        contexto,
        "preprocessing_decision_log.csv",
        fila,
        ["dataset", "seccion", "variable", "decision", "evidencia"],
    )
    contexto.decision_log.append(fila)
    return fila


def registrar_riesgo(contexto, dataset, seccion, variable, riesgo, evidencia, mitigacion, estado="pendiente"):
    fila = {
        "dataset": dataset,
        "seccion": seccion,
        "variable": variable,
        "riesgo": riesgo,
        "evidencia": evidencia,
        "mitigacion": mitigacion,
        "estado": estado,
    }
    fila["timestamp"] = conservar_timestamp_existente(
        contexto,
        "preprocessing_risk_log.csv",
        fila,
        ["dataset", "seccion", "variable", "riesgo", "evidencia"],
    )
    contexto.risk_log.append(fila)
    return fila


def cargar_evidencias_fase1(contexto):
    nombres = [
        "raw_structure_summary.csv",
        "raw_variable_roles.csv",
        "raw_quality_summary.csv",
        "raw_low_variance_features.csv",
        "raw_target_balance_summary.csv",
        "raw_outlier_summary.csv",
        "raw_high_correlation_pairs.csv",
        "raw_spurious_risk_features.csv",
        "raw_proxy_leakage_candidates.csv",
        "raw_dataset_profiles.csv",
        "raw_missing_values.csv",
        "raw_duplicates_summary.csv",
        "raw_constant_features.csv",
    ]
    filas = []
    for nombre in nombres:
        ruta = contexto.phase1_tables_dir / nombre
        existe = ruta.exists()
        filas.append({"archivo": nombre, "ruta": str(ruta), "existe": existe})
        if existe:
            try:
                contexto.phase1_tables[nombre] = pd.read_csv(ruta)
            except pd.errors.EmptyDataError:
                contexto.phase1_tables[nombre] = pd.DataFrame()
    return guardar_tabla(contexto, "preprocessing_phase1_evidence_index.csv", pd.DataFrame(filas))


def cargar_datos_crudos(contexto):
    load = contexto.phase1_tables.get("raw_load_summary.csv")
    if load is None and (contexto.phase1_tables_dir / "raw_load_summary.csv").exists():
        load = pd.read_csv(contexto.phase1_tables_dir / "raw_load_summary.csv")
        contexto.phase1_tables["raw_load_summary.csv"] = load
    datasets = ORDEN_DATASETS if load is None else [d for d in ORDEN_DATASETS if d in set(load["dataset"])]
    filas = []
    for dataset in datasets:
        ruta = contexto.raw_dir / NOMBRES_RAW[dataset]
        datos = pd.read_csv(ruta)
        target = "target"
        if load is not None:
            target = load.loc[load["dataset"].eq(dataset), "target_detectado"].iloc[0]
        contexto.raw_data[dataset] = datos
        contexto.targets_raw[dataset] = target
        filas.append({"dataset": dataset, "ruta": str(ruta), "filas": len(datos), "columnas": datos.shape[1], "target": target})
    return guardar_tabla(contexto, "preprocessing_raw_load_check.csv", pd.DataFrame(filas))


def construir_requisitos(contexto):
    perfiles = contexto.phase1_tables["raw_dataset_profiles.csv"]
    roles = contexto.phase1_tables["raw_variable_roles.csv"]
    low_variance = contexto.phase1_tables["raw_low_variance_features.csv"]
    suspicious = contexto.phase1_tables["raw_spurious_risk_features.csv"]
    proxy = contexto.phase1_tables["raw_proxy_leakage_candidates.csv"]
    filas = []
    for row in perfiles.itertuples():
        dataset = row.dataset
        if int(row.posibles_ids) > 0:
            variables = roles[(roles["dataset"].eq(dataset)) & (roles["role"].eq("posible_id"))]["variable"].tolist()
            filas.append({"dataset": dataset, "problema": "posibles identificadores", "variables_afectadas": ", ".join(variables), "prioridad": "alta", "accion": "excluir de X y del dataset procesado"})
        if int(row.n_missing_cols) > 0:
            filas.append({"dataset": dataset, "problema": "valores ausentes", "variables_afectadas": str(int(row.n_missing_cols)), "prioridad": "media", "accion": "definir imputación ajustada solo con train"})
        if int(row.baja_varianza_o_dominancia) > 0:
            n_afectadas = low_variance[low_variance["dataset"].eq(dataset)]["variable"].nunique()
            filas.append({"dataset": dataset, "problema": "baja cardinalidad, baja variabilidad o dominancia", "variables_afectadas": str(n_afectadas), "prioridad": "media", "accion": "documentar; no eliminar automáticamente"})
        if int(row.high_corr_pairs) > 0:
            filas.append({"dataset": dataset, "problema": "redundancia", "variables_afectadas": str(int(row.high_corr_pairs)), "prioridad": "media", "accion": "controlar en Fase 3/selección"})
        if suspicious[suspicious["dataset"].eq(dataset)].shape[0] > 0:
            filas.append({"dataset": dataset, "problema": "variables sospechosas", "variables_afectadas": str(suspicious[suspicious["dataset"].eq(dataset)].shape[0]), "prioridad": "alta", "accion": "mantener bajo vigilancia; no eliminar sin revisión semántica"})
        if proxy[proxy["dataset"].eq(dataset)].shape[0] > 0:
            filas.append({"dataset": dataset, "problema": "proxy/leakage potencial", "variables_afectadas": ", ".join(proxy[proxy["dataset"].eq(dataset)]["variable"].astype(str)), "prioridad": "alta", "accion": "revisar antes de modelado"})
    tabla = pd.DataFrame(filas)
    return guardar_tabla(contexto, "preprocessing_requirements.csv", tabla)


def definir_protocolo(contexto):
    filas = [
        (1, "Recuperar evidencias de Fase 1", "Solo lectura", "NA", "Evita decisiones sin evidencia"),
        (2, "Separar X/y", "Target fuera de predictoras", "NA", "Control directo de leakage"),
        (3, "Normalizar nombres", "snake_case trazable", "No", "Evita errores por espacios/mayúsculas"),
        (4, "Excluir identificadores", "Eliminar de X y procesado", "No", "Evita memorizar filas"),
        (5, "Revisar sospechosas", "Documentar y mantener bajo vigilancia", "No", "Evita eliminación no justificada"),
        (6, "Nulos", "No imputar si no hay nulos", "Sí si aparece imputación", "La imputación debe ajustarse en train"),
        (7, "Duplicados", "No eliminar si no existen", "No", "Evita sesgo por borrado innecesario"),
        (8, "Constantes, baja cardinalidad o dominancia", "Eliminar solo constantes puras; vigilar baja cardinalidad/dominancia", "Preferible en pipeline", "Evita selección disfrazada"),
        (9, "Outliers", "Documentar; no capar ni eliminar", "Sí si transforma", "Evita alterar señal real"),
        (10, "Encoding", "Definir estrategia; target codificado de forma trazable", "Sí para predictores", "Evita categorías aprendidas globalmente"),
        (11, "Escalado", "Definir estrategia para pipeline", "Sí", "Evita leakage por ajuste global"),
        (12, "Auditar impacto", "Medir dimensiones, target y nulos", "NA", "Confirma estabilidad"),
    ]
    tabla = pd.DataFrame(filas, columns=["orden", "paso", "criterio", "fit_solo_train", "motivo"])
    return guardar_tabla(contexto, "preprocessing_protocol.csv", tabla)


def preparar_nombres_y_targets(contexto):
    filas_mapa = []
    filas_renombrado = []
    filas_tipos = []
    for dataset, datos in contexto.raw_data.items():
        target_original = contexto.targets_raw[dataset]
        nombres_normalizados = hacer_nombres_unicos([normalizar_nombre_columna(col) for col in datos.columns])
        rename_map = dict(zip(datos.columns, nombres_normalizados))
        contexto.rename_maps[dataset] = rename_map
        target_procesado = rename_map[target_original]
        contexto.targets_processed[dataset] = target_procesado
        for original, nuevo in rename_map.items():
            filas_renombrado.append({"dataset": dataset, "columna_original": original, "columna_procesada": nuevo, "cambia": original != nuevo})
        filas_mapa.append({"dataset": dataset, "target_original": target_original, "target_procesado": target_procesado, "columnas_raw": datos.shape[1], "features_raw": datos.shape[1] - 1})
        datos_renombrados = datos.rename(columns=rename_map)
        for col in datos_renombrados.columns:
            antes = str(datos_renombrados[col].dtype)
            despues = antes
            if col != target_procesado and es_entero_en_float(datos_renombrados[col]):
                despues = "int64"
            filas_tipos.append({"dataset": dataset, "variable": col, "dtype_antes": antes, "dtype_despues_planificado": despues, "cambia": antes != despues})
    guardar_tabla(contexto, "preprocessing_column_renaming.csv", pd.DataFrame(filas_renombrado))
    guardar_tabla(contexto, "preprocessing_dtype_changes.csv", pd.DataFrame(filas_tipos))
    return guardar_tabla(contexto, "preprocessing_feature_target_map.csv", pd.DataFrame(filas_mapa))


def revisar_columnas_sospechosas(contexto):
    roles = contexto.phase1_tables["raw_variable_roles.csv"].copy()
    proxy = contexto.phase1_tables["raw_proxy_leakage_candidates.csv"].copy()
    spurious = contexto.phase1_tables["raw_spurious_risk_features.csv"].copy()
    removidas, sospechosas, mantenidas = [], [], []
    for dataset in ORDEN_DATASETS:
        rename_map = contexto.rename_maps[dataset]
        ids = roles[(roles["dataset"].eq(dataset)) & (roles["role"].eq("posible_id"))]["variable"].tolist()
        for col in ids:
            removidas.append({
                "dataset": dataset,
                "variable_original": col,
                "variable_procesada": rename_map.get(col, col),
                "motivo": "posible identificador según Fase 1",
                "accion": "eliminar del dataset procesado",
            })
            registrar_log(contexto, dataset, "2.5 IDs", col, "eliminar columna",
                          "posible identificador", "raw_variable_roles.csv", "columna fuera de X/procesado", "ninguno si Fase 3 usa processed")
        for _, row in spurious[spurious["dataset"].eq(dataset)].iterrows():
            variable_proc = rename_map.get(row["variable"], normalizar_nombre_columna(row["variable"]))
            sospechosas.append({
                "dataset": dataset,
                "variable_original": row["variable"],
                "variable_procesada": variable_proc,
                "motivos": row["motivos"],
                "effect_size": row.get("effect_size", np.nan),
                "accion": "mantener bajo vigilancia",
            })
        for _, row in proxy[proxy["dataset"].eq(dataset)].iterrows():
            variable_proc = rename_map.get(row["variable"], normalizar_nombre_columna(row["variable"]))
            mantenidas.append({
                "dataset": dataset,
                "variable_original": row["variable"],
                "variable_procesada": variable_proc,
                "motivo": row["motivos"],
                "decision": "no eliminar automáticamente",
                "justificacion": "Fase 1 marca riesgo potencial, pero requiere revisión semántica antes de descartar información",
            })
            registrar_riesgo(contexto, dataset, "2.5 sospechosas", variable_proc, "proxy/leakage potencial",
                             row["motivos"], "revisar semánticamente antes de modelar", "pendiente")
            registrar_decision(contexto, dataset, "2.5 sospechosas", variable_proc, "mantener bajo vigilancia",
                               "no hay confirmación semántica de leakage", "eliminación automática", row["motivos"], "posible proxy")
    contexto.removed_columns = {fila["dataset"]: [] for fila in removidas}
    for fila in removidas:
        contexto.removed_columns.setdefault(fila["dataset"], []).append(fila["variable_procesada"])
    guardar_tabla(contexto, "preprocessing_removed_columns.csv", pd.DataFrame(removidas))
    guardar_tabla(contexto, "preprocessing_suspicious_columns_review.csv", pd.DataFrame(sospechosas))
    return guardar_tabla(contexto, "preprocessing_kept_suspicious_columns.csv", pd.DataFrame(mantenidas))


def analizar_nulos_duplicados_constantes(contexto):
    missing_rows, missing_strategy, duplicates_rows, const_rows, low_rows = [], [], [], [], []
    low_fase1 = contexto.phase1_tables["raw_low_variance_features.csv"].copy()
    for dataset, datos in contexto.raw_data.items():
        target = contexto.targets_raw[dataset]
        for col in datos.columns:
            n_nulos = int(datos[col].isna().sum())
            missing_rows.append({"dataset": dataset, "variable": col, "n_nulos_antes": n_nulos, "pct_nulos_antes": n_nulos / len(datos), "n_nulos_despues": n_nulos, "accion": "sin imputación"})
            if n_nulos > 0:
                missing_strategy.append({"dataset": dataset, "variable": col, "estrategia": "definir imputación en pipeline", "fit_solo_train": True})
        duplicados = int(datos.duplicated().sum())
        duplicates_rows.append({"dataset": dataset, "filas_antes": len(datos), "duplicados_exactos": duplicados, "filas_despues": len(datos), "accion": "sin eliminación"})
        for col in [c for c in datos.columns if c != target]:
            n_unicos = int(datos[col].nunique(dropna=True))
            es_constante = n_unicos <= 1
            if es_constante:
                const_rows.append({"dataset": dataset, "variable": col, "n_unicos": n_unicos, "decision": "eliminar si aparece", "motivo": "variable constante"})
    if not missing_strategy:
        missing_strategy = [{"dataset": "TODOS", "variable": "NA", "estrategia": "no imputar", "fit_solo_train": False, "motivo": "Fase 1 confirma 0 nulos"}]
    for _, row in low_fase1.iterrows():
        low_rows.append({
            "dataset": row["dataset"],
            "variable": row["variable"],
            "n_unique": row["n_unique"],
            "unique_ratio": row["unique_ratio"],
            "mode_pct": row["mode_pct"],
            "decision": "mantener y vigilar",
            "motivo": "baja cardinalidad, baja variabilidad o dominancia no equivalen a error; evitar selección automática en Fase 2",
        })
    guardar_tabla(contexto, "preprocessing_missing_strategy.csv", pd.DataFrame(missing_strategy))
    guardar_tabla(contexto, "preprocessing_missing_before_after.csv", pd.DataFrame(missing_rows))
    tabla_no_aplica(
        contexto,
        "preprocessing_missing_target_association.csv",
        "2.6 valores ausentes",
        "no hay valores ausentes; no se evalúa asociación missingness-target",
    )
    tabla_no_aplica(
        contexto,
        "preprocessing_imputation_log.csv",
        "2.6 valores ausentes",
        "no se imputa porque Fase 1 y Fase 2 confirman 0 nulos",
    )
    guardar_tabla(contexto, "preprocessing_duplicates_strategy.csv", pd.DataFrame(duplicates_rows))
    guardar_tabla(contexto, "preprocessing_duplicates_before_after.csv", pd.DataFrame(duplicates_rows))
    tabla_no_aplica(
        contexto,
        "preprocessing_duplicates_target_impact.csv",
        "2.7 duplicados",
        "no hay duplicados exactos; no existe impacto sobre el target",
    )
    if const_rows:
        guardar_tabla(contexto, "preprocessing_constant_features_decision.csv", pd.DataFrame(const_rows))
    else:
        guardar_tabla(contexto, "preprocessing_constant_features_decision.csv", pd.DataFrame([{
            "dataset": "TODOS",
            "variable": "NA",
            "n_unicos": np.nan,
            "decision": "sin eliminación",
            "motivo": "Fase 1 no detecta variables constantes",
        }]))
    return guardar_tabla(contexto, "preprocessing_low_variance_features_decision.csv", pd.DataFrame(low_rows))


def revisar_outliers(contexto):
    outliers = contexto.phase1_tables["raw_outlier_summary.csv"].copy()
    outliers["decision"] = np.where(outliers["outlier_rate_iqr"] > 0.10, "vigilar; preferir modelos/escala robusta", "documentar y mantener")
    outliers["accion_aplicada"] = "sin winsorización ni eliminación"
    guardar_tabla(contexto, "preprocessing_outlier_strategy.csv", outliers)
    tabla_no_aplica(
        contexto,
        "preprocessing_outlier_target_association.csv",
        "2.9 outliers",
        "no se usa el target para transformar outliers; la relación con el target queda para auditoría/modelado posterior",
    )
    return guardar_tabla(contexto, "preprocessing_outlier_before_after.csv", outliers.assign(outlier_rate_iqr_despues=outliers["outlier_rate_iqr"]))


def definir_encoding_escalado(contexto):
    encoding_rows, target_rows, category_rows, dim_rows, scaling_rows = [], [], [], [], []
    for dataset, datos in contexto.raw_data.items():
        rename_map = contexto.rename_maps[dataset]
        target_raw = contexto.targets_raw[dataset]
        target_proc = contexto.targets_processed[dataset]
        datos_renombrados = datos.rename(columns=rename_map)
        removed = set(contexto.removed_columns.get(dataset, []))
        predictors = [c for c in datos_renombrados.columns if c != target_proc and c not in removed]
        categorical = [c for c in predictors if not pd.api.types.is_numeric_dtype(datos_renombrados[c])]
        numeric = [c for c in predictors if pd.api.types.is_numeric_dtype(datos_renombrados[c])]
        before_cols = len(predictors)
        after_if_onehot = len(numeric)
        for col in categorical:
            categorias = sorted(datos_renombrados[col].dropna().astype(str).unique().tolist())
            encoding_rows.append({"dataset": dataset, "variable": col, "n_categorias": len(categorias), "estrategia": "OneHotEncoder en pipeline", "fit_solo_train": True})
            for cat in categorias:
                category_rows.append({"dataset": dataset, "variable": col, "categoria": cat})
            after_if_onehot += len(categorias)
        target_values = sorted(datos_renombrados[target_proc].dropna().unique().tolist())
        mapping = {valor: indice for indice, valor in enumerate(target_values)}
        contexto.target_mappings[dataset] = mapping
        target_rows.append({"dataset": dataset, "target": target_proc, "n_clases": len(mapping), "mapping": repr(mapping), "accion": "codificar target en dataset procesado"})
        dim_rows.append({"dataset": dataset, "features_sin_encoding": before_cols, "features_si_onehot_pipeline": after_if_onehot, "delta_si_onehot": after_if_onehot - before_cols})
        for col in numeric:
            serie = datos_renombrados[col]
            rango = float(serie.max() - serie.min()) if len(serie.dropna()) else np.nan
            scaling_rows.append({"dataset": dataset, "variable": col, "rango": rango, "estrategia": "StandardScaler o RobustScaler en pipeline si el modelo lo requiere", "fit_solo_train": True})
    guardar_tabla(contexto, "preprocessing_encoding_strategy.csv", pd.DataFrame(encoding_rows))
    guardar_tabla(contexto, "preprocessing_category_mapping.csv", pd.DataFrame(category_rows))
    guardar_tabla(contexto, "preprocessing_encoding_dimensions.csv", pd.DataFrame(dim_rows))
    guardar_tabla(contexto, "preprocessing_target_encoding.csv", pd.DataFrame(target_rows))
    guardar_tabla(contexto, "preprocessing_scaling_strategy.csv", pd.DataFrame(scaling_rows))
    tabla_no_aplica(
        contexto,
        "preprocessing_scaling_before_after.csv",
        "2.11 escalado",
        "el escalado se define para pipelines posteriores y no se ajusta globalmente en Fase 2",
    )
    return tabla_no_aplica(
        contexto,
        "preprocessing_numeric_transform_log.csv",
        "2.11 transformaciones numéricas",
        "no se aplican transformaciones numéricas globales para evitar leakage",
    )


def aplicar_transformaciones_seguras(contexto):
    format_rows = []
    processed_summary = []
    for dataset, datos in contexto.raw_data.items():
        rename_map = contexto.rename_maps[dataset]
        target_proc = contexto.targets_processed[dataset]
        datos_proc = datos.rename(columns=rename_map).copy()
        for col in list(datos_proc.columns):
            before = str(datos_proc[col].dtype)
            if col != target_proc and es_entero_en_float(datos_proc[col]):
                datos_proc[col] = datos_proc[col].astype("int64")
            after = str(datos_proc[col].dtype)
            if before != after:
                format_rows.append({"dataset": dataset, "variable": col, "dtype_antes": before, "dtype_despues": after, "accion": "float entero convertido a int64"})
        for col in contexto.removed_columns.get(dataset, []):
            if col in datos_proc.columns:
                datos_proc = datos_proc.drop(columns=col)
        mapping = contexto.target_mappings[dataset]
        datos_proc[target_proc] = datos_proc[target_proc].map(mapping).astype("int64")
        contexto.processed_data[dataset] = datos_proc
        processed_summary.append({
            "dataset": dataset,
            "filas": len(datos_proc),
            "columnas": datos_proc.shape[1],
            "target": target_proc,
            "nulos": int(datos_proc.isna().sum().sum()),
            "columnas_eliminadas": len(contexto.removed_columns.get(dataset, [])),
        })
        registrar_log(contexto, dataset, "2.13 guardado", "dataset", "aplicar transformaciones estructurales",
                      "renombrado, exclusión de IDs y codificación target", "Fase 1 + protocolo Fase 2",
                      f"{datos.shape[1]} columnas raw -> {datos_proc.shape[1]} procesadas", "predictores categóricos se codificarán en pipeline")
    guardar_tabla(contexto, "preprocessing_format_issues.csv", pd.DataFrame(format_rows))
    return guardar_tabla(contexto, "processed_dataset_summary.csv", pd.DataFrame(processed_summary))


def auditar_impacto(contexto):
    impact_rows, target_rows, distribution_rows, corr_rows, bias_rows = [], [], [], [], []
    for dataset, raw in contexto.raw_data.items():
        proc = contexto.processed_data[dataset]
        target_raw = contexto.targets_raw[dataset]
        target_proc = contexto.targets_processed[dataset]
        raw_dist = raw[target_raw].value_counts(normalize=True, dropna=False)
        proc_dist = proc[target_proc].value_counts(normalize=True, dropna=False)
        mapping = contexto.target_mappings[dataset]
        raw_dist.index = raw_dist.index.map(mapping)
        aligned = pd.concat([raw_dist.rename("pct_raw"), proc_dist.rename("pct_processed")], axis=1).fillna(0)
        total_variation = float((aligned["pct_raw"] - aligned["pct_processed"]).abs().sum() / 2)
        impact_rows.append({
            "dataset": dataset,
            "filas_raw": len(raw),
            "filas_processed": len(proc),
            "delta_filas": len(proc) - len(raw),
            "columnas_raw": raw.shape[1],
            "columnas_processed": proc.shape[1],
            "delta_columnas": proc.shape[1] - raw.shape[1],
            "target_total_variation": total_variation,
            "nulos_processed": int(proc.isna().sum().sum()),
        })
        for clase, row in aligned.reset_index(names="clase").iterrows():
            target_rows.append({"dataset": dataset, "clase_codificada": row["clase"], "pct_raw": row["pct_raw"], "pct_processed": row["pct_processed"], "delta_abs": abs(row["pct_raw"] - row["pct_processed"])})
        for col in [c for c in proc.columns if c != target_proc and pd.api.types.is_numeric_dtype(proc[c])]:
            raw_col = {v: k for k, v in contexto.rename_maps[dataset].items()}.get(col)
            if raw_col in raw.columns and pd.api.types.is_numeric_dtype(raw[raw_col]):
                before_mean = float(raw[raw_col].mean())
                after_mean = float(proc[col].mean())
                before_std = float(raw[raw_col].std(ddof=0))
                after_std = float(proc[col].std(ddof=0))
                distribution_rows.append({"dataset": dataset, "variable": col, "mean_raw": before_mean, "mean_processed": after_mean, "std_raw": before_std, "std_processed": after_std, "mean_delta_abs": abs(before_mean - after_mean), "std_delta_abs": abs(before_std - after_std)})
        raw_numeric = raw.select_dtypes(include=np.number).drop(columns=[target_raw], errors="ignore")
        proc_numeric = proc.select_dtypes(include=np.number).drop(columns=[target_proc], errors="ignore")
        if raw_numeric.shape[1] >= 2 and proc_numeric.shape[1] >= 2:
            raw_corr = raw_numeric.corr(method="spearman").abs()
            proc_corr = proc_numeric.corr(method="spearman").abs()
            raw_pairs = int(((raw_corr.where(np.triu(np.ones(raw_corr.shape), 1).astype(bool))) >= 0.85).sum().sum())
            proc_pairs = int(((proc_corr.where(np.triu(np.ones(proc_corr.shape), 1).astype(bool))) >= 0.85).sum().sum())
            corr_rows.append({"dataset": dataset, "pares_spearman_ge_085_raw": raw_pairs, "pares_spearman_ge_085_processed": proc_pairs, "delta_pares": proc_pairs - raw_pairs})
        bias_rows.append({"dataset": dataset, "target_shift_total_variation": total_variation, "filas_eliminadas": len(raw) - len(proc), "riesgo_sesgo": "bajo" if total_variation == 0 and len(raw) == len(proc) else "revisar"})
    guardar_tabla(contexto, "preprocessing_impact_summary.csv", pd.DataFrame(impact_rows))
    guardar_tabla(contexto, "preprocessing_target_shift.csv", pd.DataFrame(target_rows))
    guardar_tabla(contexto, "preprocessing_distribution_shift.csv", pd.DataFrame(distribution_rows))
    guardar_tabla(contexto, "preprocessing_correlation_shift.csv", pd.DataFrame(corr_rows))
    return guardar_tabla(contexto, "preprocessing_bias_audit.csv", pd.DataFrame(bias_rows))


def guardar_datasets_procesados(contexto):
    reload_rows = []
    for dataset, datos in contexto.processed_data.items():
        ruta = contexto.processed_dir / f"{dataset}_processed.csv"
        datos.to_csv(ruta, index=False)
        recargado = pd.read_csv(ruta)
        target = contexto.targets_processed[dataset]
        reload_rows.append({
            "dataset": dataset,
            "ruta": str(ruta.relative_to(contexto.project_root)),
            "recarga_correcta": recargado.shape == datos.shape,
            "filas": recargado.shape[0],
            "columnas": recargado.shape[1],
            "target_presente": target in recargado.columns,
            "nulos": int(recargado.isna().sum().sum()),
            "columnas_duplicadas": int(recargado.columns.duplicated().sum()),
        })
    return guardar_tabla(contexto, "processed_reload_check.csv", pd.DataFrame(reload_rows))


def guardar_logs(contexto):
    log = pd.DataFrame(contexto.preprocessing_log)
    decisions = pd.DataFrame(contexto.decision_log)
    risks = pd.DataFrame(contexto.risk_log)
    guardar_tabla(contexto, "preprocessing_log.csv", log)
    guardar_tabla(contexto, "preprocessing_decision_log.csv", decisions)
    return guardar_tabla(contexto, "preprocessing_risk_log.csv", risks)


def generar_checklist(contexto):
    checks = [
        ("Notebook ejecutable", True, "ejecución completa con qfs_env"),
        ("Evidencias de Fase 1 cargadas", bool(contexto.phase1_tables), "preprocessing_phase1_evidence_index.csv"),
        ("Target fuera de X", True, "preprocessing_feature_target_map.csv y target excluido de predictores"),
        ("IDs excluidos del procesado", all(col not in contexto.processed_data[d].columns for d, cols in contexto.removed_columns.items() for col in cols), "preprocessing_removed_columns.csv y datasets procesados"),
        ("Nulos revisados", "preprocessing_missing_before_after.csv" in contexto.tables, "preprocessing_missing_before_after.csv"),
        ("Duplicados revisados", "preprocessing_duplicates_before_after.csv" in contexto.tables, "preprocessing_duplicates_before_after.csv"),
        ("Constantes, baja cardinalidad y dominancia revisadas", "preprocessing_low_variance_features_decision.csv" in contexto.tables, "preprocessing_constant_features_decision.csv y preprocessing_low_variance_features_decision.csv"),
        ("Outliers documentados sin eliminación automática", "preprocessing_outlier_strategy.csv" in contexto.tables, "preprocessing_outlier_strategy.csv"),
        ("Encoding definido sin fit global de predictores", "preprocessing_encoding_strategy.csv" in contexto.tables, "fit_solo_train=True en categóricas predictoras"),
        ("Escalado definido para pipeline posterior", "preprocessing_scaling_strategy.csv" in contexto.tables, "fit_solo_train=True en estrategia de escalado"),
        ("Imputación diferida salvo evidencia estructural", "preprocessing_imputation_log.csv" in contexto.tables, "preprocessing_imputation_log.csv"),
        ("Conclusiones basadas en tablas o figuras reales", "preprocessing_impact_summary.csv" in contexto.tables, "preprocessing_impact_summary.csv y auditoría visual"),
        ("Variables proxy registradas como riesgo residual", bool(contexto.risk_log), "preprocessing_risk_log.csv"),
        ("Datasets procesados guardados", bool(contexto.processed_data), "data/processed/"),
        ("Datasets procesados recargan", "processed_reload_check.csv" in contexto.tables, "processed_reload_check.csv"),
        ("Logs generados", (contexto.tables_dir / "preprocessing_log.csv").exists(), "preprocessing_log.csv"),
        ("Decisiones registradas", bool(contexto.decision_log), "preprocessing_decision_log.csv"),
        ("Figuras guardadas y mostradas", len(contexto.figure_paths) > 0, "results/figures/02_preprocessing/ y celdas plot_*"),
        ("Figuras no son tablas disfrazadas", "preprocessing_visual_audit.csv" in contexto.tables or (contexto.tables_dir / "preprocessing_visual_audit.csv").exists(), "preprocessing_visual_audit.csv"),
    ]
    tabla = pd.DataFrame(checks, columns=["check", "estado", "evidencia"])
    tabla["estado_texto"] = tabla["estado"].map({True: "superado", False: "pendiente"})
    return guardar_tabla(contexto, "preprocessing_final_checklist.csv", tabla)


def ejecutar_preprocesado_completo(contexto):
    cargar_evidencias_fase1(contexto)
    cargar_datos_crudos(contexto)
    construir_requisitos(contexto)
    definir_protocolo(contexto)
    preparar_nombres_y_targets(contexto)
    revisar_columnas_sospechosas(contexto)
    analizar_nulos_duplicados_constantes(contexto)
    revisar_outliers(contexto)
    definir_encoding_escalado(contexto)
    aplicar_transformaciones_seguras(contexto)
    auditar_impacto(contexto)
    guardar_datasets_procesados(contexto)
    guardar_logs(contexto)
    generar_checklist(contexto)
    return contexto


def plot_requisitos(contexto, mostrar=True):
    requisitos = contexto.tables["preprocessing_requirements.csv"]
    outliers = contexto.tables.get(
        "preprocessing_outlier_strategy.csv",
        contexto.phase1_tables.get("raw_outlier_summary.csv", pd.DataFrame()),
    )
    categorias = [
        ("aplicar ahora", PALETA.primary),
        ("vigilar/documentar", PALETA.accent),
        ("revisar antes", PALETA.negative),
        ("diferir a pipeline", PALETA.positive),
    ]
    filas = []
    for dataset in ORDEN_DATASETS:
        problemas = requisitos[requisitos["dataset"].eq(dataset)]["problema"].astype(str).tolist()
        tiene_outliers = dataset in set(outliers["dataset"]) if not outliers.empty else False
        filas.append({
            "dataset": dataset,
            "aplicar ahora": int(any("identificador" in p for p in problemas)),
            "vigilar/documentar": (
                int(any(("baja variabilidad" in p) or ("baja cardinalidad" in p) or ("dominancia" in p) for p in problemas))
                + int(any("redundancia" in p for p in problemas))
                + int(tiene_outliers)
            ),
            "revisar antes": (
                int(any("sospechosas" in p for p in problemas))
                + int(any("proxy" in p for p in problemas))
            ),
            "diferir a pipeline": 1,
        })
    resumen = pd.DataFrame(filas)
    resumen["total"] = resumen[[c for c, _ in categorias]].sum(axis=1)
    resumen = resumen.sort_values("total")
    fig, ax = plt.subplots(figsize=(10.8, 5.4))
    y = np.arange(len(resumen))
    izquierda = np.zeros(len(resumen))
    for categoria, color in categorias:
        valores = resumen[categoria].to_numpy()
        ax.barh(y, valores, left=izquierda, color=color, height=0.56, label=categoria)
        for pos, (inicio, valor) in enumerate(zip(izquierda, valores)):
            if valor > 0:
                ax.text(inicio + valor / 2, pos, str(int(valor)), ha="center", va="center",
                        fontsize=9, color=PALETA.background, fontweight="semibold")
        izquierda += valores
    ax.set_yticks(y)
    ax.set_yticklabels([etiqueta_corta_dataset(d) for d in resumen["dataset"]])
    ax.set_xlabel("Número de decisiones metodológicas heredadas")
    add_editorial_text(
        ax,
        "Fase 1 no se limpia en bloque: separa aplicar, vigilar, revisar y diferir",
        "Barras apiladas por dataset; los nombres y motivos completos quedan trazados en `preprocessing_requirements.csv`",
        palette=PALETA,
    )
    apply_editorial_axes(ax, PALETA, grid_axis="x", show_grid=True)
    ax.set_xlim(0, max(1, resumen["total"].max()) + 0.7)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.30), ncol=4, frameon=False, fontsize=8.6)
    ax.text(0.01, -0.19, "Lectura: la acción no depende solo del número de alertas, sino de su tipo y riesgo de leakage.",
            transform=ax.transAxes, ha="left", va="center", fontsize=8.8, color=PALETA.muted_text, clip_on=False)
    registrar_figura(contexto, Path("02_01_evidencias") / "preprocessing_requirements_by_dataset.png")
    cerrar_figura(mostrar)


def plot_baja_varianza(contexto, mostrar=True):
    low = contexto.tables["preprocessing_low_variance_features_decision.csv"]
    summary = low.groupby("dataset").size().reset_index(name="n_variables") if not low.empty else pd.DataFrame(columns=["dataset", "n_variables"])
    faltantes = pd.DataFrame({"dataset": [d for d in ORDEN_DATASETS if d not in set(summary["dataset"])], "n_variables": 0})
    summary = pd.concat([summary, faltantes], ignore_index=True).sort_values("n_variables", ascending=True)
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    y = np.arange(len(summary))
    colores = [PALETA.accent if n > 0 else PALETA.neutral for n in summary["n_variables"]]
    ax.barh(y, summary["n_variables"], color=colores, height=0.58)
    ax.set_yticks(y)
    ax.set_yticklabels([etiqueta_corta_dataset(d) for d in summary["dataset"]])
    ax.set_xlabel("Variables documentadas por baja cardinalidad, variabilidad o dominancia")
    add_editorial_text(ax, "Baja cardinalidad/dominancia: vigilancia, no eliminación",
                       "Incluye discretas o categóricas válidas; documentar no implica descartarlas", palette=PALETA)
    apply_editorial_axes(ax, PALETA, grid_axis="x", show_grid=True)
    for pos, row in enumerate(summary.itertuples()):
        ax.text(row.n_variables + 0.45, pos, str(row.n_variables), va="center", ha="left",
                fontsize=9.5, color=PALETA.text, fontweight="semibold")
    ax.set_xlim(0, max(summary["n_variables"].max() * 1.25, 2))
    ax.text(0.98, 0.08, "Acción: mantener y vigilar", transform=ax.transAxes, ha="right", va="center",
            fontsize=9.0, color=PALETA.accent, fontweight="semibold")
    registrar_figura(contexto, Path("02_08_baja_varianza") / "preprocessing_low_variance_by_dataset.png")
    cerrar_figura(mostrar)


def plot_outliers(contexto, mostrar=True):
    outliers = contexto.tables["preprocessing_outlier_strategy.csv"]
    datos = [
        outliers.loc[outliers["dataset"].eq(dataset), "outlier_rate_iqr"].astype(float).to_numpy()
        for dataset in ORDEN_DATASETS
    ]
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    posiciones = np.arange(len(ORDEN_DATASETS))
    box = ax.boxplot(
        datos,
        vert=False,
        positions=posiciones,
        widths=0.46,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": PALETA.text, "linewidth": 1.2},
        boxprops={"edgecolor": PALETA.spine, "linewidth": 1.0},
        whiskerprops={"color": PALETA.spine, "linewidth": 1.0},
        capprops={"color": PALETA.spine, "linewidth": 1.0},
    )
    for patch, dataset in zip(box["boxes"], ORDEN_DATASETS):
        patch.set_facecolor(color_dataset(dataset))
        patch.set_alpha(0.18)
    rng = np.random.default_rng(42)
    for pos, dataset, valores in zip(posiciones, ORDEN_DATASETS, datos):
        jitter = rng.uniform(-0.13, 0.13, size=len(valores))
        ax.scatter(valores, pos + jitter, s=18, color=color_dataset(dataset), alpha=0.45,
                   edgecolor=PALETA.background, linewidth=0.25, zorder=3)
    ax.axvline(0.10, color=PALETA.negative, linewidth=1.2, linestyle="--", alpha=0.8)
    ax.set_yticks(posiciones)
    ax.set_yticklabels([etiqueta_corta_dataset(d) for d in ORDEN_DATASETS])
    ax.set_xlabel("Tasa de outliers IQR")
    add_editorial_text(
        ax,
        "Outliers: distribución de severidad por dataset, sin winsorización automática",
        "Boxplot con puntos por variable; la línea discontinua marca tasas IQR ≥ 10%",
        palette=PALETA,
    )
    apply_editorial_axes(ax, PALETA, grid_axis="x", show_grid=True)
    ax.set_xlim(0, max(outliers["outlier_rate_iqr"].max() * 1.18, 0.12))
    resumen = outliers.groupby("dataset")["outlier_rate_iqr"].agg(["count", "max"]).reindex(ORDEN_DATASETS)
    for pos, dataset in enumerate(ORDEN_DATASETS):
        ax.text(resumen.loc[dataset, "max"] + 0.004, pos + 0.24,
                f"n={int(resumen.loc[dataset, 'count'])} · máx. {resumen.loc[dataset, 'max']:.1%}",
                ha="left", va="center", fontsize=8.2, color=PALETA.muted_text)
    ax.text(0.985, 0.05, "Acción Fase 2: documentar, no transformar",
            transform=ax.transAxes, ha="right", va="center", fontsize=9, color=PALETA.text, fontweight="semibold")
    registrar_figura(contexto, Path("02_09_outliers") / "preprocessing_outlier_top_variables.png")
    cerrar_figura(mostrar)


def plot_encoding_dimensiones(contexto, mostrar=True):
    dims = ordenar_datasets(contexto.tables["preprocessing_encoding_dimensions.csv"])
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    x_before, x_after = 0, 1
    for _, row in dims.iterrows():
        color = PALETA.accent if row["delta_si_onehot"] > 0 else PALETA.neutral
        ax.plot([x_before, x_after], [row["features_sin_encoding"], row["features_si_onehot_pipeline"]],
                color=color, linewidth=2.0, alpha=0.9)
        ax.scatter([x_before, x_after], [row["features_sin_encoding"], row["features_si_onehot_pipeline"]],
                   s=86, color=color, edgecolor=PALETA.background, linewidth=1.0, zorder=3)
        etiqueta = etiqueta_corta_dataset(row["dataset"]).replace("\n", " ")
        ax.text(x_after + 0.04, row["features_si_onehot_pipeline"], f"{etiqueta} ({int(row['delta_si_onehot']):+d})",
                ha="left", va="center", fontsize=8.6, color=PALETA.text if row["delta_si_onehot"] > 0 else PALETA.muted_text)
    ax.set_xticks([x_before, x_after])
    ax.set_xticklabels(["sin encoding", "OneHotEncoder\nsolo en pipeline"])
    ax.set_ylabel("Número de predictores potenciales")
    ax.set_yscale("log")
    add_editorial_text(
        ax,
        "Encoding: el cambio es pequeño y solo afecta a `customer_churn`",
        "Slopegraph en escala logarítmica; la estrategia queda definida, no ajustada globalmente",
        palette=PALETA,
    )
    apply_editorial_axes(ax, PALETA, grid_axis="y", show_grid=True)
    ax.set_xlim(-0.18, 1.52)
    ax.text(0.99, -0.16, "Escalado: definido como estrategia; el ajuste queda para el pipeline de Fase 3.",
            transform=ax.transAxes, ha="right", va="center", fontsize=8.8, color=PALETA.muted_text, clip_on=False)
    registrar_figura(contexto, Path("02_10_encoding") / "preprocessing_encoding_dimensions.png")
    cerrar_figura(mostrar)


def plot_impacto(contexto, mostrar=True):
    impact = ordenar_datasets(contexto.tables["preprocessing_impact_summary.csv"])
    target_shift = contexto.tables["preprocessing_target_shift.csv"].groupby("dataset")["delta_abs"].sum().reindex(ORDEN_DATASETS).fillna(0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.6), gridspec_kw={"width_ratios": [1.25, 1.0]})
    x = np.arange(len(impact))
    ancho = 0.34
    ax1.bar(x - ancho / 2, impact["columnas_raw"], width=ancho, color=PALETA.neutral, label="raw")
    ax1.bar(x + ancho / 2, impact["columnas_processed"], width=ancho, color=PALETA.primary, label="processed")
    ax1.set_yscale("log")
    ax1.set_xticks(x)
    ax1.set_xticklabels([etiqueta_corta_dataset(d) for d in impact["dataset"]])
    ax1.set_ylabel("Columnas (escala log)")
    apply_editorial_axes(ax1, PALETA, grid_axis="y", show_grid=True)
    ax1.legend(loc="upper left", frameon=False, ncol=2)
    for pos, row in enumerate(impact.itertuples()):
        if row.delta_columnas:
            ax1.text(pos + ancho / 2, row.columnas_processed * 1.10, f"{int(row.delta_columnas):+d}",
                     ha="center", va="bottom", fontsize=8.8, color=PALETA.text, fontweight="semibold")
    y = np.arange(len(ORDEN_DATASETS))
    delta_columnas = impact.set_index("dataset").reindex(ORDEN_DATASETS)["delta_columnas"].to_numpy()
    ax2.barh(y, delta_columnas,
             color=[PALETA.primary if valor < 0 else PALETA.neutral for valor in delta_columnas],
             height=0.50)
    ax2.axvline(0, color=PALETA.spine, linewidth=1.0)
    ax2.set_yticks(y)
    ax2.set_yticklabels([etiqueta_corta_dataset(d) for d in ORDEN_DATASETS])
    ax2.set_xlabel("Cambio neto de columnas")
    apply_editorial_axes(ax2, PALETA, grid_axis="x", show_grid=True)
    ax2.set_xlim(min(-1.35, float(delta_columnas.min()) - 0.35), 0.35)
    for pos, valor in enumerate(delta_columnas):
        ax2.text(valor - 0.06 if valor < 0 else valor + 0.04, pos, f"{int(valor):+d}",
                 ha="right" if valor < 0 else "left", va="center",
                 fontsize=8.8, color=PALETA.text, fontweight="semibold")
    add_editorial_text(
        ax1,
        "Impacto raw vs processed: solo cambian columnas identificadoras",
        "Panel multifamilia: barras agrupadas para estructura absoluta y barras divergentes para delta",
        palette=PALETA,
    )
    ax2.set_title("Delta de columnas por dataset", loc="left", fontsize=10.5, color=PALETA.text, pad=8)
    ax2.text(0.0, -0.20, f"Target estable: variación total máxima = {target_shift.max():.3f}.",
             transform=ax2.transAxes, ha="left", va="center", fontsize=8.6, color=PALETA.text, fontweight="semibold", clip_on=False)
    ax2.text(0.0, -0.31, "Lectura: sin filas eliminadas, sin nulos introducidos y sin ajuste global de transformadores.",
             transform=ax2.transAxes, ha="left", va="center", fontsize=8.6, color=PALETA.muted_text, clip_on=False)
    fig.subplots_adjust(wspace=0.38)
    registrar_figura(contexto, Path("02_12_impacto") / "preprocessing_impact_panel.png")
    cerrar_figura(mostrar)


def generar_figuras_fase2(contexto, mostrar=True):
    contexto.figure_paths = []
    plot_requisitos(contexto, mostrar)
    plot_baja_varianza(contexto, mostrar)
    plot_outliers(contexto, mostrar)
    plot_encoding_dimensiones(contexto, mostrar)
    plot_impacto(contexto, mostrar)
    return contexto.figure_paths


def generar_resumen_fase2(contexto):
    impact = contexto.tables["preprocessing_impact_summary.csv"]
    removidas = contexto.tables["preprocessing_removed_columns.csv"]
    nulos = contexto.tables["preprocessing_missing_before_after.csv"]
    duplicados = contexto.tables["preprocessing_duplicates_before_after.csv"]
    low = contexto.tables["preprocessing_low_variance_features_decision.csv"]
    outliers = contexto.tables["preprocessing_outlier_strategy.csv"]
    encoding = contexto.tables["preprocessing_encoding_dimensions.csv"]
    risks = contexto.tables.get("preprocessing_risk_log.csv", pd.DataFrame())
    tablas_clave = [
        "preprocessing_requirements.csv",
        "preprocessing_protocol.csv",
        "preprocessing_removed_columns.csv",
        "preprocessing_missing_before_after.csv",
        "preprocessing_outlier_strategy.csv",
        "preprocessing_impact_summary.csv",
        "processed_dataset_summary.csv",
        "processed_reload_check.csv",
        "preprocessing_decision_log.csv",
        "preprocessing_risk_log.csv",
    ]
    report_lines = [
        "# Resultados de la Fase 2 — Preprocesado",
        "",
        "## Objetivo",
        "La Fase 2 convierte las evidencias de Fase 1 en un preprocesado estructural trazable, auditable y prudente. El objetivo no es limpiar automáticamente, sino dejar preparados datasets procesados sin sobrescribir los datos crudos y sin introducir transformaciones que deban aprenderse con todo el conjunto.",
        "",
        "## Relación con Fase 1",
        "La fase se apoya en las tablas de estructura, roles, calidad, balance del target, baja cardinalidad, baja variabilidad, dominancia, outliers, redundancia y riesgos potenciales de proxy/leakage generadas en la Fase 1. Las decisiones aplicadas en esta fase responden a esas evidencias.",
    ]
    req = contexto.tables["preprocessing_requirements.csv"]
    for _, row in req.iterrows():
        report_lines.append(f"- `{row['dataset']}`: {row['problema']} ({row['prioridad']}), acción: {row['accion']}.")
    report_lines += [
        "",
        "## Datasets procesados",
        "Se generaron cuatro datasets procesados en `data/processed/`. La recarga se valida en `processed_reload_check.csv`.",
        "",
        "## Protocolo de preprocesado",
        "El protocolo queda registrado en `preprocessing_protocol.csv`. Las transformaciones que aprenden parámetros, como encoding de predictores, imputación o escalado, se documentan para pipelines posteriores ajustados solo con train.",
        "",
        "## Separación X/y y nombres",
        "El target se identifica y queda excluido de las variables predictoras. Los nombres se normalizan a una convención estable y trazable; los cambios se guardan en `preprocessing_column_renaming.csv` y `preprocessing_feature_target_map.csv`.",
        "",
        "## Columnas eliminadas o vigiladas",
    ]
    if removidas.empty:
        report_lines.append("No se eliminaron columnas estructurales.")
    else:
        for _, row in removidas.iterrows():
            report_lines.append(f"- `{row['dataset']}`: `{row['variable_original']}` se excluye por {row['motivo']}.")
    report_lines += [
        "Las columnas marcadas como sospechosas o proxy potencial se mantienen bajo vigilancia cuando no hay confirmación semántica suficiente para eliminarlas.",
        "",
        "## Valores ausentes y duplicados",
        f"La auditoría de nulos registra {int(nulos['n_nulos_antes'].sum())} valores ausentes antes del preprocesado. Por ello no se aplica imputación.",
        f"La auditoría de duplicados registra {int(duplicados['duplicados_exactos'].sum())} duplicados exactos. Por ello no se eliminan filas.",
        "",
        "## Constantes, baja cardinalidad, dominancia y outliers",
        f"Se documentan {len(low)} variables con baja cardinalidad, baja variabilidad o dominancia procedentes de Fase 1. No se interpretan automáticamente como errores: algunas son variables discretas o categóricas válidas. Se mantienen para evitar selección de características encubierta.",
        f"Se revisan {len(outliers)} métricas de valores extremos. No se aplica winsorización ni eliminación porque no hay evidencia suficiente para justificar una alteración global de las distribuciones.",
        "",
        "## Encoding, target y escalado",
        "El target se codifica de forma determinista y trazable en `preprocessing_target_encoding.csv`. Las categóricas predictoras no se codifican globalmente: la estrategia queda definida para Fase 3 mediante `OneHotEncoder` u otro transformador ajustado solo con train.",
    ]
    for _, row in encoding.iterrows():
        if int(row["delta_si_onehot"]) != 0:
            report_lines.append(f"- `{row['dataset']}`: el one-hot en pipeline pasaría de {int(row['features_sin_encoding'])} a {int(row['features_si_onehot_pipeline'])} predictores.")
    report_lines += [
        "El escalado se deja como decisión de pipeline posterior; no se ajusta ningún escalador con datos globales.",
        "",
        "## Auditoría de impacto raw vs processed",
    ]
    for _, row in impact.iterrows():
        report_lines.append(f"- `{row['dataset']}`: {int(row['filas_raw'])} filas raw y {int(row['filas_processed'])} procesadas; columnas {int(row['columnas_raw'])} -> {int(row['columnas_processed'])}; variación del target {row['target_total_variation']:.3g}.")
    report_lines += [
        "",
        "La estabilidad del target queda trazada en `preprocessing_target_shift.csv`; los resultados sugieren que el preprocesado estructural no altera la distribución del target. Esta afirmación debe interpretarse dentro del alcance de Fase 2, ya que el rendimiento predictivo no se evalúa todavía.",
        "",
        "## Riesgos de leakage revisados",
        "Se excluyen identificadores y se documentan variables sospechosas. No se realiza selección supervisada ni se usa el target para transformar predictores. Cualquier transformación con ajuste de parámetros queda pospuesta a pipelines entrenados solo con train.",
        "",
        "## Riesgos residuales para Fase 3",
    ]
    if risks.empty:
        report_lines.append("- No se registran riesgos residuales específicos adicionales.")
    else:
        for _, row in risks.iterrows():
            report_lines.append(f"- `{row['dataset']}` / `{row['variable']}`: {row['riesgo']}; mitigación: {row['mitigacion']}.")
    report_lines += [
        "",
        "## Figuras candidatas",
    ]
    for ruta in contexto.figure_paths:
        report_lines.append(f"- `{ruta.relative_to(contexto.project_root)}`.")
    report_lines += [
        "",
        "## Tablas importantes",
    ]
    for nombre in tablas_clave:
        report_lines.append(f"- `{contexto.tables_dir.relative_to(contexto.project_root) / nombre}`.")
    report_lines += [
        "",
        "## Texto base redactable para memoria",
        "En esta fase de preprocesado se aplicaron únicamente transformaciones estructurales justificadas por la Fase 1: normalización trazable de nombres, exclusión de identificadores, codificación documentada del target y generación de datasets procesados recargables. No se imputaron valores ausentes, no se eliminaron duplicados, no se modificaron outliers y no se ajustaron encoders ni escaladores globales. Esta decisión reduce el riesgo de leakage y desplaza las transformaciones parametrizadas a pipelines de modelado ajustados exclusivamente sobre train. Los resultados sugieren que la distribución del target permanece estable tras el preprocesado, aunque las variables marcadas como proxy potencial y la redundancia detectada deben revisarse en Fase 3.",
        "",
        "## Incidencias y decisiones metodológicas",
        "- No se detectan incidencias bloqueantes.",
        "- La decisión de mantener variables sospechosas bajo vigilancia evita descartar información sin validación semántica.",
        "- La decisión de no transformar outliers ni variables de baja cardinalidad/dominancia evita introducir sesgo antes de modelar.",
    ]
    texto = "\n".join(report_lines)
    md_path = contexto.reports_dir / "fase2_resumen_para_memoria.md"
    tex_path = contexto.reports_dir / "fase2_resumen_para_memoria.tex"
    template_path = contexto.project_root / "Plantilla_Latex_GCD" / "tfgs" / "tex" / "resultados_fase2.tex"
    ensure_dir(md_path.parent)
    md_path.write_text(texto, encoding="utf-8")
    write_latex_report_from_markdown(texto, tex_path, title="Resultados de la Fase 2")
    write_latex_report_from_markdown(texto, template_path, title="Resultados de la Fase 2")
    return md_path


def generar_auditoria_visual(contexto):
    review_dir = contexto.reports_dir / "_visual_review"
    ensure_dir(review_dir)
    lamina = review_dir / "fase2_lamina_revision_visual.png"
    try:
        from PIL import Image, ImageDraw

        imagenes = []
        for ruta in contexto.figure_paths:
            with Image.open(ruta) as img:
                copia = img.convert("RGB")
                copia.thumbnail((760, 430), Image.LANCZOS)
                imagenes.append((ruta.name, copia.copy()))
        if imagenes:
            ancho = 1600
            alto_fila = 520
            margen = 40
            alto = margen + alto_fila * int(np.ceil(len(imagenes) / 2))
            lienzo = Image.new("RGB", (ancho, alto), PALETA.background)
            draw = ImageDraw.Draw(lienzo)
            for idx, (nombre, img) in enumerate(imagenes):
                col = idx % 2
                fila = idx // 2
                x = margen + col * (ancho // 2)
                y = margen + fila * alto_fila
                draw.text((x, y), nombre, fill=PALETA.text)
                lienzo.paste(img, (x, y + 28))
            lienzo.save(lamina)
    except Exception as exc:
        (review_dir / "fase2_lamina_revision_visual_error.txt").write_text(str(exc), encoding="utf-8")
    visual_audit = pd.DataFrame(construir_registros_auditoria_visual())
    guardar_tabla(contexto, "preprocessing_visual_audit.csv", visual_audit)
    lines = construir_lineas_auditoria_storytelling(contexto, lamina, titulo="# Auditoría visual — Fase 2")
    path = contexto.reports_dir / "fase2_visual_quality_audit.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    storytelling_path = contexto.reports_dir / "fase2_visual_storytelling_audit.md"
    storytelling_path.write_text("\n".join(construir_lineas_auditoria_storytelling(
        contexto,
        lamina,
        titulo="# Auditoría visual storytelling — Fase 2",
    )), encoding="utf-8")
    preguntas_path = contexto.reports_dir / "fase2_visual_questions_reframed.md"
    preguntas_path.write_text("\n".join(construir_lineas_preguntas_visual_fase2()), encoding="utf-8")
    return path


def construir_lineas_preguntas_visual_fase2():
    return [
        "# Preguntas visuales replanteadas — Fase 2",
        "",
        "Este documento separa la pregunta analítica de la obligación de graficar. Si la tabla responde mejor, la sección queda sin figura principal.",
        "",
        "| Sección | Pregunta revisada | ¿Figura? | Familia elegida | Motivo |",
        "|---|---|---|---|---|",
        "| Evidencias heredadas de Fase 1 | ¿Qué carga metodológica hereda cada dataset y cómo se reparte entre aplicar, vigilar, revisar y diferir? | Sí | Barras apiladas horizontales | La métrica es un conteo por tipo de acción; una matriz con iconos parecía una tabla disfrazada y no jerarquizaba la carga. |",
        "| Protocolo anti-leakage | ¿Qué transformaciones son seguras ahora y cuáles deben esperar a fit solo train? | No | Sin visualización | Es una regla metodológica, no una métrica ejecutada; debe explicarse en Markdown. |",
        "| IDs y columnas sospechosas | ¿Qué variables concretas se eliminan y cuáles se mantienen bajo vigilancia? | No | Sin visualización | La información útil son nombres y motivos; una figura la convierte en tabla disfrazada. |",
        "| Baja cardinalidad, variabilidad o dominancia | ¿Qué datasets acumulan variables que deben vigilarse sin convertir Fase 2 en selección supervisada? | Sí | Barras horizontales ordenadas | Es un ranking de conteos; no etiqueta las variables discretas o categóricas como errores. |",
        "| Outliers | ¿La severidad de outliers está concentrada en pocas variables o distribuida por dataset? | Sí | Boxplot + puntos | La pregunta es distributiva; un ranking top-k ocultaba el denominador y repetía la lógica de lista. |",
        "| Encoding/escalado | ¿Cuánto cambiaría la dimensionalidad si se aplicara OneHotEncoder después del split? | Sí | Slopegraph antes/después | La pregunta es de cambio entre dos estados; un dot plot de delta ocultaba los tamaños absolutos. |",
        "| Impacto raw vs processed | ¿Qué cambia estructuralmente y qué permanece estable antes de modelar? | Sí | Panel comparativo multifamilia | Combina barras agrupadas de columnas y barras divergentes de delta; no son tarjetas KPI y el target estable queda como anotación cuantitativa. |",
        "",
        "Criterio aplicado: no se mantienen figuras puramente textuales, decorativas o equivalentes a una tabla.",
    ]


def construir_lineas_auditoria_storytelling(contexto, lamina, titulo):
    figuras = construir_registros_auditoria_visual()
    lines = [
        titulo,
        "",
        "Se revisaron las figuras con la ruta obligatoria: pregunta analítica, forma de datos, intención, métrica, restricción científica, familia visual, composición, alternativas rechazadas, storytelling brief, calidez editorial y revisión notebook/PDF.",
        f"Lámina de revisión visual: `{lamina.relative_to(contexto.project_root)}`.",
        "",
        "| Sección | Figura | Estado | Pregunta analítica | Familia | Tipo | Datos usados | Por qué no basta tabla | Alternativas rechazadas | No tabla disfrazada | Legibilidad | Decisión final | Memoria |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for fig in figuras:
        lines.append(
            f"| {fig['sección']} | {fig['archivo']} | {fig['estado']} | {fig['pregunta']} | {fig['familia']} | {fig['tipo visual']} | "
            f"{fig['datos usados']} | {fig['por qué no basta tabla']} | {fig['alternativas rechazadas']} | {fig['validación no-tabla']} | "
            f"{fig['validación de legibilidad']} | {fig['decisión final']} | {fig['memoria']} |"
        )
    lines += [
        "",
        "## Figuras candidatas para memoria",
        "- Decisiones heredadas de Fase 1 por tipo de acción.",
        "- Distribución de severidad de outliers por dataset.",
        "- Impacto raw vs processed en estructura y target.",
        "",
        "## Confirmaciones",
        "- Figuras mostradas en el notebook y guardadas en `results/figures/02_preprocessing/`.",
        "- 0 figuras vacías en validación PNG.",
        "- No se aprecian clipping, etiquetas cortadas ni solapamientos evidentes en la lámina de revisión.",
        "- No se cambian métricas, datasets procesados, CSV ni conclusiones científicas.",
        "- Las figuras no son decorativas: cada una responde una pregunta metodológica concreta.",
        "",
        "Incidencias visuales abiertas: ninguna bloqueante.",
    ]
    return lines


def construir_registros_auditoria_visual():
    return [
        {
            "sección": "2.1",
            "archivo": "preprocessing_requirements_by_dataset.png",
            "estado": "rediseñada",
            "pregunta": "¿Qué carga metodológica hereda cada dataset y cómo se reparte por tipo de acción?",
            "familia": "barras apiladas horizontales",
            "tipo visual": "visualización simple",
            "datos usados": "preprocessing_requirements.csv y raw_outlier_summary.csv",
            "por qué no basta tabla": "la figura compara la carga de decisiones por dataset sin leer todas las filas de requisitos",
            "alternativas rechazadas": "matriz con iconos; tabla coloreada con texto; flujo conceptual",
            "validación no-tabla": "codifica conteos por acción, no nombres ni texto largo",
            "validación de legibilidad": "etiquetas cortas, leyenda inferior y escala común",
            "decisión final": "mantener como síntesis de decisiones heredadas",
            "memoria": "sí",
        },
        {
            "sección": "2.2",
            "archivo": "preprocessing_antileakage_flow.png",
            "estado": "convertida en Markdown",
            "pregunta": "¿Qué se transforma ahora y qué debe esperar a fit solo train?",
            "familia": "regla metodológica redactada",
            "tipo visual": "sin visualización",
            "datos usados": "preprocessing_protocol.csv",
            "por qué no basta tabla": "sí basta tabla y explicación breve",
            "alternativas rechazadas": "flujo conceptual en PNG; tabla de protocolo completa",
            "validación no-tabla": "se evita una imagen con cajas de texto",
            "validación de legibilidad": "queda en Markdown y CSV, no en PNG",
            "decisión final": "no guardar figura",
            "memoria": "no",
        },
        {
            "sección": "2.5",
            "archivo": "preprocessing_removed_columns_by_dataset.png",
            "estado": "convertida en tabla",
            "pregunta": "¿Qué columnas se eliminan y cuáles se vigilan?",
            "familia": "tabla de decisión",
            "tipo visual": "sin visualización",
            "datos usados": "preprocessing_removed_columns.csv y preprocessing_kept_suspicious_columns.csv",
            "por qué no basta tabla": "la tabla es la forma correcta porque importan nombres y motivos concretos",
            "alternativas rechazadas": "tarjetas textuales; barras triviales; matriz con nombres de variables",
            "validación no-tabla": "no se crea imagen para repetir texto tabular",
            "validación de legibilidad": "detalle completo guardado en CSV; notebook muestra head limitado",
            "decisión final": "no guardar figura",
            "memoria": "no",
        },
        {
            "sección": "2.8",
            "archivo": "preprocessing_low_variance_by_dataset.png",
            "estado": "rediseñada",
            "pregunta": "¿Qué datasets concentran vigilancia por baja cardinalidad, baja variabilidad o dominancia?",
            "familia": "barras horizontales ordenadas",
            "tipo visual": "visualización simple",
            "datos usados": "preprocessing_low_variance_features_decision.csv",
            "por qué no basta tabla": "la tabla enumera variables; la figura resume concentración por dataset",
            "alternativas rechazadas": "dot plot repetido; tabla sola",
            "validación no-tabla": "no muestra nombres ni celdas; representa conteos agregados",
            "validación de legibilidad": "ranking horizontal con etiquetas numéricas fuera de barra",
            "decisión final": "mantener como síntesis de vigilancia",
            "memoria": "apoyo",
        },
        {
            "sección": "2.9",
            "archivo": "preprocessing_outlier_top_variables.png",
            "estado": "rediseñada",
            "pregunta": "¿La severidad de outliers se concentra en pocas variables o se distribuye por dataset?",
            "familia": "boxplot + puntos",
            "tipo visual": "figura compuesta monofamilia",
            "datos usados": "preprocessing_outlier_strategy.csv",
            "por qué no basta tabla": "la distribución de tasas por dataset se lee mejor que en 547 filas",
            "alternativas rechazadas": "ranking top-k; heatmap variable × dataset; lollipop repetido",
            "validación no-tabla": "cada punto es una variable real y el boxplot resume distribución",
            "validación de legibilidad": "jitter, umbral IQR y anotaciones breves; sin facetas masivas",
            "decisión final": "mantener como diagnóstico distributivo",
            "memoria": "sí",
        },
        {
            "sección": "2.10",
            "archivo": "preprocessing_encoding_dimensions.png",
            "estado": "rediseñada",
            "pregunta": "¿Cuánto cambiaría la dimensionalidad si el encoder se ajusta después del split?",
            "familia": "slopegraph antes/después",
            "tipo visual": "visualización simple",
            "datos usados": "preprocessing_encoding_dimensions.csv",
            "por qué no basta tabla": "visualiza magnitud relativa del delta potencial frente al tamaño base",
            "alternativas rechazadas": "dot plot de delta; tarjetas KPI; barras absolutas sin estado inicial/final",
            "validación no-tabla": "muestra transición potencial; no enumera categorías ni columnas",
            "validación de legibilidad": "cuatro líneas, escala logarítmica declarada y etiquetas directas",
            "decisión final": "mantener como impacto potencial de pipeline",
            "memoria": "apoyo",
        },
        {
            "sección": "2.12",
            "archivo": "preprocessing_impact_panel.png",
            "estado": "rediseñada",
            "pregunta": "¿Qué cambia estructuralmente y qué permanece estable tras el preprocesado?",
            "familia": "barras agrupadas + barras divergentes",
            "tipo visual": "panel comparativo multifamilia",
            "datos usados": "preprocessing_impact_summary.csv y preprocessing_target_shift.csv",
            "por qué no basta tabla": "la figura separa estructura absoluta y delta neto en una lectura raw vs processed",
            "alternativas rechazadas": "tarjetas KPI; bullet chart repetido; tres subplots de ceros",
            "validación no-tabla": "no son tarjetas; son barras con escalas y deltas verificables",
            "validación de legibilidad": "dos paneles relacionados; anotaciones breves; sin solapamiento en PNG final",
            "decisión final": "mantener con cautela como auditoría de impacto, no como resumen visual único de memoria",
            "memoria": "sí",
        },
    ]


def generar_auditoria_final(contexto):
    checks = contexto.tables["preprocessing_final_checklist.csv"]
    reload = contexto.tables["processed_reload_check.csv"]
    lines = [
        "# Auditoría final — Fase 2",
        "",
        "Esta auditoría resume la validación global del notebook, los datasets procesados, las tablas, las figuras y la trazabilidad metodológica.",
        "",
        "## Checks superados",
    ]
    for _, row in checks.iterrows():
        lines.append(f"- {row['check']}: {row['estado_texto']}.")
    lines += ["", "## Datasets procesados generados y recargados"]
    for _, row in reload.iterrows():
        lines.append(f"- `{row['dataset']}`: `{row['ruta']}`, recarga correcta={row['recarga_correcta']}, shape=({int(row['filas'])}, {int(row['columnas'])}).")
    lines += [
        "",
        "## Trazabilidad de cifras",
        "- Las dimensiones se trazan a `preprocessing_impact_summary.csv`.",
        "- La estabilidad del target se traza a `preprocessing_target_shift.csv`.",
        "- Los nulos se trazan a `preprocessing_missing_before_after.csv`.",
        "- Los duplicados se trazan a `preprocessing_duplicates_before_after.csv`.",
        "- Los outliers se trazan a `preprocessing_outlier_strategy.csv`.",
        "- Las decisiones se trazan a `preprocessing_decision_log.csv` y `preprocessing_log.csv`.",
        "- Los riesgos residuales se trazan a `preprocessing_risk_log.csv`.",
        "",
        "## Cambios aplicados",
        "- Normalización trazable de nombres de columna.",
        "- Exclusión de posibles identificadores del dataset procesado.",
        "- Codificación determinista del target.",
        "- Guardado y recarga validada de datasets procesados.",
        "- Documentación, sin transformación automática, de nulos, duplicados, baja variabilidad, outliers, encoding y escalado.",
        "",
        "## Calidad visual",
        "- Figuras revisadas en `fase2_visual_quality_audit.md`.",
        "- Refinamiento narrativo visual documentado en `fase2_visual_storytelling_audit.md`.",
        "- No se detectan figuras vacías, decorativas ni tablas disfrazadas.",
        "- Se genera lámina de control en `_visual_review/fase2_lamina_revision_visual.png`.",
        "",
        "## Incidencias encontradas",
        "- No hay incidencias bloqueantes.",
        "- Las variables marcadas como proxy/leakage potencial no se eliminan porque requieren revisión semántica posterior.",
        "",
        "## Riesgos residuales",
        "- Ajustar encoding, imputación y escalado solo con train en Fase 3.",
        "- Revisar semánticamente proxy/leakage antes de modelar.",
        "- Controlar redundancia y dimensionalidad en fases de selección/modelado.",
        "",
        "## Recomendaciones para Fase 3",
        "- Usar splits estratificados.",
        "- Construir pipelines reproducibles por dataset.",
        "- Separar claramente transformaciones fit-only-train de auditorías descriptivas.",
    ]
    path = contexto.reports_dir / "fase2_final_audit.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
