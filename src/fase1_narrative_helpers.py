from pathlib import Path

import numpy as np
import pandas as pd


DATASET_LABELS = {
    "breast_cancer_wisconsin": "Breast Cancer Wisconsin",
    "customer_churn": "Customer Churn",
    "madelon": "Madelon",
    "olive_oil": "Olive Oil",
}


DATASET_NOTES = {
    "carga": {
        "breast_cancer_wisconsin": "Se lee correctamente un dataset pequeño y denso; en esta sección solo queda validada la lectura.",
        "customer_churn": "Se lee correctamente el dataset con mayor volumen muestral; por eso las figuras posteriores pueden usar muestra visual.",
        "madelon": "Se lee correctamente el dataset de mayor dimensionalidad bruta; la calidad y señal se evalúan después.",
        "olive_oil": "Se lee correctamente un dataset pequeño con target multiclase; el desbalance se cuantifica en la sección 1.4.",
    },
    "estructura": {
        "breast_cancer_wisconsin": "Tiene 30 features analíticas y un posible ID; el ratio features/muestras es bajo, aunque habrá que vigilar redundancia.",
        "customer_churn": "El ratio features/muestras es muy bajo por su tamaño, pero contiene variables categóricas e identificador potencial.",
        "madelon": "El ratio 0.25 activa una alerta interna de dimensionalidad: muchas variables frente a 2.000 muestras.",
        "olive_oil": "La estructura es compacta, con posible ID y target multiclase; el riesgo inicial no es dimensional sino de balance y clases.",
    },
    "calidad": {
        "breast_cancer_wisconsin": "No aparecen nulos, duplicados, constantes ni baja variabilidad en la auditoría cruda.",
        "customer_churn": "No hay nulos ni duplicados, pero sí variables de baja cardinalidad relativa o dominancia que Fase 2 debe revisar.",
        "madelon": "No hay nulos ni duplicados; la alerta aparece en variables de baja variabilidad dentro de una matriz muy amplia.",
        "olive_oil": "No hay nulos ni duplicados; queda una variable con baja variabilidad/dominancia para revisión posterior.",
    },
    "target": {
        "breast_cancer_wisconsin": "Binario con desbalance moderado; conviene usar métricas macro o balanceadas junto a accuracy.",
        "customer_churn": "Binario con ratio moderado y mucho tamaño muestral; los splits deben preservar proporciones.",
        "madelon": "Binario perfectamente balanceado; el reto no está en el target, sino en ruido y dimensionalidad.",
        "olive_oil": "Multiclase y claramente desbalanceado; Fase 2 debe usar estratificación y métricas macro o balanceadas.",
    },
    "univariante": {
        "breast_cancer_wisconsin": "Presenta asimetría media alta y outliers IQR en varias variables, sin decidir limpieza automática.",
        "customer_churn": "Las variables numéricas agregadas muestran baja tasa de outliers; la interpretación debe considerar variables discretas.",
        "madelon": "La media global de outliers es baja; interesa revisar rankings, no las 500 variables una a una.",
        "olive_oil": "La distribución univariante es manejable, pero con asimetrías suficientes para preferir métodos robustos.",
    },
    "normalidad": {
        "breast_cancer_wisconsin": "Todas las variables testadas rechazan normalidad; esto orienta a pruebas robustas, no a transformar automáticamente.",
        "customer_churn": "El rechazo completo puede deberse también a potencia estadística por tamaño muestral; no debe leerse aislado.",
        "madelon": "Solo una parte de las variables rechaza normalidad; el reto principal sigue siendo dimensional y de señal dispersa.",
        "olive_oil": "Rechazo completo de normalidad en variables testadas; se recomienda prudencia no paramétrica en Fase 2.",
    },
    "asociacion": {
        "breast_cancer_wisconsin": "Hay señal univariante fuerte, pero varias variables están correlacionadas y no equivalen a selección final.",
        "customer_churn": "Muchas variables son significativas; por el tamaño muestral deben leerse junto al efecto y no solo por p-value.",
        "madelon": "La señal tras FDR existe pero es limitada frente a 500 variables; no se concluye ausencia total de señal.",
        "olive_oil": "La asociación es fuerte en todas las variables analíticas, con alertas que requieren revisión semántica.",
    },
    "redundancia": {
        "breast_cancer_wisconsin": "La redundancia alta es relevante y debe controlarse antes de seleccionar variables.",
        "customer_churn": "No se detectan pares por encima del umbral 0.85; se conserva como control documentado.",
        "madelon": "Aparecen pares altos, pero el foco principal sigue siendo dimensionalidad y ruido univariante.",
        "olive_oil": "Hay pocos pares altamente correlacionados; se revisan como posible redundancia local.",
    },
    "dimensionalidad": {
        "breast_cancer_wisconsin": "Riesgo dimensional bajo, con muchas señales fuertes y poca señal débil residual.",
        "customer_churn": "Riesgo dimensional bajo por volumen muestral; la cautela principal es interpretación de significancia.",
        "madelon": "Riesgo medio por ratio features/muestras y gran volumen de posible ruido univariante.",
        "olive_oil": "Riesgo dimensional bajo; PCA se usa solo como diagnóstico de estructura, no como validación predictiva.",
    },
    "riesgos": {
        "breast_cancer_wisconsin": "Una variable con efecto casi perfecto se marca para revisión semántica; sospechosa no significa eliminar.",
        "customer_churn": "Una variable combina FDR significativo con efecto mínimo; debe vigilarse la relevancia práctica.",
        "madelon": "Predominan variables significativas sin sobrevivir FDR; son advertencias de falsos positivos exploratorios.",
        "olive_oil": "Dos variables con efecto casi perfecto requieren revisión semántica antes de modelar.",
    },
    "preclasificacion": {
        "breast_cancer_wisconsin": "Señal fuerte abundante, pero con redundancia que Fase 2 debe controlar.",
        "customer_churn": "La señal existe, aunque la lectura se modera por tamaño muestral y efectos pequeños.",
        "madelon": "Domina el posible ruido univariante, con señal residual que justifica fases posteriores.",
        "olive_oil": "Señal fuerte en variables analíticas, pero con desbalance multiclase y revisión de proxies.",
    },
}


def mostrar_tabla(tabla, columnas=None, ordenar_por=None, ascendente=True, formato=None):
    vista = tabla.copy()
    if ordenar_por is not None and ordenar_por in vista.columns:
        vista = vista.sort_values(ordenar_por, ascending=ascendente)
    if columnas is not None:
        vista = vista[columnas]
    if formato:
        return vista.style.format(formato)
    return vista


def carga_compacta(contexto):
    tabla = contexto.tables["raw_load_summary.csv"].copy()
    tabla["archivo"] = tabla["archivo"].map(lambda ruta: Path(str(ruta)).name)
    return tabla[["dataset", "archivo", "filas", "columnas", "target_detectado", "carga_correcta", "incidencias"]]


def target_balance_compacto(contexto):
    balance = contexto.tables["raw_target_balance_summary.csv"].drop(columns=["estado"], errors="ignore").copy()
    distribucion = contexto.tables["raw_target_distribution.csv"].copy()
    filas = []
    for dataset, grupo in distribucion.groupby("dataset", sort=False):
        mayor = grupo.sort_values("n", ascending=False).iloc[0]
        menor = grupo.sort_values("n", ascending=True).iloc[0]
        filas.append({
            "dataset": dataset,
            "clase_mayoritaria": mayor["clase"],
            "n_mayoritaria": int(mayor["n"]),
            "clase_minoritaria": menor["clase"],
            "n_minoritaria": int(menor["n"]),
        })
    extremos = pd.DataFrame(filas)
    return balance.merge(extremos, on="dataset", how="left")[
        ["dataset", "target", "n_clases", "clase_minoritaria", "n_minoritaria", "clase_mayoritaria", "n_mayoritaria", "ratio_mayoritaria_minoritaria"]
    ]


def resumen_por_dataset(tabla, metricas):
    agregaciones = {}
    for columna, operacion in metricas.items():
        if operacion == "abs_mean":
            agregaciones[columna] = lambda serie: np.nanmean(np.abs(serie))
        else:
            agregaciones[columna] = operacion
    return tabla.groupby("dataset").agg(agregaciones).reset_index()


def top_por_dataset(tabla, columna_orden, n=5, columnas=None, ascendente=False):
    partes = []
    for dataset, grupo in tabla.groupby("dataset", sort=False):
        ordenado = grupo.sort_values(columna_orden, ascending=ascendente)
        partes.append(ordenado.iloc[:n])
    resultado = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    if columnas is not None and not resultado.empty:
        resultado = resultado[columnas]
    return resultado


def resumen_riesgos(contexto):
    riesgos = contexto.tables["raw_spurious_risk_features.csv"]
    if riesgos.empty:
        return pd.DataFrame(columns=["dataset", "n_riesgos", "motivos"])
    return (
        riesgos.groupby("dataset")
        .agg(
            n_riesgos=("variable", "count"),
            motivos=("motivos", lambda valores: "; ".join(sorted(set(";".join(valores).split(";"))))),
        )
        .reset_index()
    )


def componentes_pca_80(contexto):
    pca = contexto.tables["raw_pca_variance_summary.csv"]
    if pca.empty:
        return pd.DataFrame(columns=["dataset", "componentes_80"])
    filas = []
    for dataset, grupo in pca.groupby("dataset", sort=False):
        supera = grupo[grupo["cumulative"] >= 0.80]
        componentes = int(supera.iloc[0]["component"]) if not supera.empty else np.nan
        filas.append({"dataset": dataset, "componentes_80": componentes})
    return pd.DataFrame(filas)


def dimensionalidad_compacta(contexto):
    tabla = contexto.tables["raw_dimensionality_summary.csv"].copy()
    return tabla.merge(componentes_pca_80(contexto), on="dataset", how="left")


def handoff_compacto():
    return pd.DataFrame([
        ["IDs", "raw_variable_roles.csv", "Excluir o aislar posibles IDs antes de entrenar.", "Leakage o señal artificial por identificadores."],
        ["Baja varianza", "raw_low_variance_features.csv", "Decidir eliminación, recodificación o conservación justificada.", "Eliminar automáticamente puede perder variables discretas útiles."],
        ["Outliers", "raw_outlier_summary.csv", "Aplicar tratamiento robusto si procede, ajustado solo con train.", "No confundir outlier estadístico con error de dato."],
        ["Encoding/escalado", "raw_dtype_summary.csv y raw_variable_roles.csv", "Codificar categóricas y escalar donde el método lo requiera.", "Evitar ajuste con información de test."],
        ["Splits", "raw_target_balance_summary.csv", "Usar estratificación cuando proceda, especialmente en olive_oil.", "Clases minoritarias mal representadas."],
        ["Leakage/proxies", "raw_spurious_risk_features.csv", "Revisión semántica antes de modelar; no eliminar solo por sospecha.", "Variables proxy pueden inflar resultados posteriores."],
        ["Redundancia", "raw_high_correlation_pairs.csv", "Controlar bloques correlacionados antes de selección formal.", "Selección inestable y sobrepeso de familias de variables."],
    ], columns=["tema", "evidencia_fase1", "decision_fase2", "riesgo_residual"])


def resumen_artefactos(contexto):
    auditoria = contexto.tables["raw_phase1_artifact_audit.csv"]
    return (
        auditoria.groupby("tipo")
        .agg(esperados=("artefacto", "count"), existentes=("existe", "sum"))
        .reset_index()
        .assign(incidencias=lambda tabla: tabla["esperados"] - tabla["existentes"])
    )


def notas_dataset(seccion):
    notas = DATASET_NOTES[seccion]
    return pd.DataFrame(
        [{"dataset": dataset, "observacion": texto} for dataset, texto in notas.items()]
    )
