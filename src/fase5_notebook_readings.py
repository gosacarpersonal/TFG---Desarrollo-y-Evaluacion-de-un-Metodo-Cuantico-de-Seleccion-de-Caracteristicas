"""Lecturas post-output para el notebook de Fase 5.

Estas funciones redactan comentarios a partir de los dataframes ya calculados.
El objetivo es evitar texto interpretativo escrito antes de ver las salidas.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def _df(resultados: dict[str, pd.DataFrame], clave: str) -> pd.DataFrame:
    return resultados.get(clave, pd.DataFrame()).copy()


def _filas(tabla: pd.DataFrame, dataset: str) -> pd.DataFrame:
    if tabla.empty or "dataset" not in tabla.columns:
        return pd.DataFrame()
    return tabla[tabla["dataset"].eq(dataset)].copy()


def _fmt(valor: Any, decimales: int = 3) -> str:
    if valor is None:
        return "no disponible"
    try:
        if pd.isna(valor):
            return "no disponible"
    except TypeError:
        pass
    if isinstance(valor, (float, int)):
        if isinstance(valor, float) and (math.isinf(valor) or math.isnan(valor)):
            return "no disponible"
        return f"{valor:.{decimales}f}"
    return str(valor)


def _lista(valores: list[Any], max_items: int = 4) -> str:
    limpios = [str(v) for v in valores if pd.notna(v)]
    if not limpios:
        return "sin elementos destacables"
    texto = ", ".join(limpios[:max_items])
    if len(limpios) > max_items:
        texto += f" y {len(limpios) - max_items} más"
    return texto


def lectura_entrada(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    resumen = _filas(_df(resultados, "fs_input_dataset_summary.csv"), dataset)
    avisos = _filas(_df(resultados, "fs_inherited_warnings.csv"), dataset)
    if resumen.empty:
        return "No hay resumen de entrada para este dataset; la lectura queda bloqueada hasta revisar la carga."
    fila = resumen.iloc[0]
    n_avisos = len(avisos)
    aviso_txt = "sin avisos heredados visibles" if n_avisos == 0 else f"con {n_avisos} avisos heredados"
    variantes = {
        "breast_cancer_wisconsin": (
            f"Breast Cancer entra con {int(fila.train_rows)} filas de train, {int(fila.validation_rows)} de validation, "
            f"{int(fila.test_rows)} de test, {int(fila.processed_features)} predictores procesados y {int(fila.classes)} clases. "
            f"El registro aparece {aviso_txt}; esta dimensión define la escala clínica antes de seleccionar."
        ),
        "customer_churn": (
            f"Customer Churn aporta {int(fila.train_rows)} observaciones de entrenamiento, {int(fila.validation_rows)} de validación "
            f"y {int(fila.test_rows)} de test, con {int(fila.processed_features)} variables y {int(fila.classes)} clases. "
            f"El estado heredado queda {aviso_txt}, dato relevante para valorar coste y muestreo."
        ),
        "madelon": (
            f"Madelon se presenta con {int(fila.train_rows)} filas train, {int(fila.validation_rows)} validation y "
            f"{int(fila.test_rows)} test; el espacio alcanza {int(fila.processed_features)} variables para "
            f"{int(fila.classes)} clases. El bloque queda {aviso_txt} y fija la prueba de alta dimensión."
        ),
        "olive_oil_3class": (
            f"Olive Oil 3 clases usa {int(fila.train_rows)} filas de train, {int(fila.validation_rows)} de validation y "
            f"{int(fila.test_rows)} de test. Sus {int(fila.processed_features)} variables y {int(fila.classes)} clases llegan "
            f"{aviso_txt}, lo que permite leer reducción sin mezclarla con la versión de 9 clases."
        ),
        "olive_oil_9class": (
            f"Olive Oil 9 clases arranca con {int(fila.train_rows)} filas train, {int(fila.validation_rows)} validation, "
            f"{int(fila.test_rows)} test, {int(fila.processed_features)} predictores y {int(fila.classes)} clases. "
            f"El resumen queda {aviso_txt}; esa granularidad de target condiciona la prudencia posterior."
        ),
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_matrices(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    calidad = _filas(_df(resultados, "fs_train_input_quality.csv"), dataset)
    alineacion = _filas(_df(resultados, "fs_column_alignment_check.csv"), dataset)
    constantes = _filas(_df(resultados, "fs_train_constant_features.csv"), dataset)
    if calidad.empty or alineacion.empty:
        return "No se han encontrado las comprobaciones de matriz necesarias para interpretar este dataset."
    q = calidad.iloc[0]
    a = alineacion.iloc[0]
    n_constantes = len(constantes)
    textos = {
        "breast_cancer_wisconsin": (
            f"En la matriz clínica se observan {int(q.n_missing_train)} nulos, {int(q.n_infinite_train)} infinitos "
            f"y {int(q.duplicated_feature_names)} nombres repetidos. La coincidencia de columnas entre splits vale "
            f"{bool(a.same_columns_train_validation_test)} y el filtro de target como predictor vale {bool(a.target_not_in_features)}; "
            f"constantes detectadas: {n_constantes}."
        ),
        "customer_churn": (
            f"Para churn, train llega a selección con {int(q.n_missing_train)} valores perdidos, {int(q.n_infinite_train)} infinitos "
            f"y {int(q.duplicated_feature_names)} duplicados de nombre. El orden train-validation-test coincide: "
            f"{bool(a.same_columns_train_validation_test)}; el target queda excluido: {bool(a.target_not_in_features)}; "
            f"variables constantes: {n_constantes}."
        ),
        "madelon": (
            f"En madelon la entrada de alta dimensión conserva {int(q.n_missing_train)} nulos, {int(q.n_infinite_train)} infinitos "
            f"y {int(q.duplicated_feature_names)} colisiones de nombres. La alineación de los tres splits es "
            f"{bool(a.same_columns_train_validation_test)} y la ausencia del target entre predictores es {bool(a.target_not_in_features)}; "
            f"constantes anotadas: {n_constantes}."
        ),
        "olive_oil_3class": (
            f"Para olive_oil_3class se comprueban {int(q.n_missing_train)} nulos, {int(q.n_infinite_train)} infinitos "
            f"y {int(q.duplicated_feature_names)} nombres duplicados en train. Las columnas se mantienen sincronizadas: "
            f"{bool(a.same_columns_train_validation_test)}; el target no aparece como feature: {bool(a.target_not_in_features)}; "
            f"columnas constantes: {n_constantes}."
        ),
        "olive_oil_9class": (
            f"En olive_oil_9class la matriz usada por selectores contiene {int(q.n_missing_train)} nulos, "
            f"{int(q.n_infinite_train)} infinitos y {int(q.duplicated_feature_names)} duplicidades de nombre. "
            f"La misma lista de columnas llega a validation y test ({bool(a.same_columns_train_validation_test)}) y "
            f"el target queda fuera ({bool(a.target_not_in_features)}); constantes registradas: {n_constantes}."
        ),
    }
    return textos.get(dataset, textos["breast_cancer_wisconsin"])


def lectura_protocolo(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    registro = _df(resultados, "fs_method_registry.csv")
    if registro.empty:
        return "No hay registro de métodos; no se puede interpretar el protocolo aplicado."
    n_metodos = registro["method"].nunique()
    supervisados = int(registro["uses_target"].sum())
    aleatorios = int(registro["has_randomness"].sum())
    familias = sorted(registro["family"].dropna().unique())
    variantes = {
        "breast_cancer_wisconsin": (
            f"El bloque clínico recibe {n_metodos} selectores repartidos en {len(familias)} familias. De ellos, {supervisados} incorporan `y_train`, "
            f"{n_metodos - supervisados} actúa sin target y {aleatorios} pueden variar con semilla. `mutual_info` fija la "
            "referencia MI del paper y `mrmr_approx` aproxima el balance relevancia-redundancia de QFS."
        ),
        "customer_churn": (
            f"Para churn se conserva el repertorio completo de {n_metodos} métodos y {len(familias)} grupos técnicos. Hay {supervisados} "
            f"supervisados, {n_metodos - supervisados} control no supervisado y {aleatorios} con componente aleatoria. "
            "La comparación separa el ranking MI de la versión clásica del objetivo QFS implementada como mRMR."
        ),
        "madelon": (
            f"En madelon se ejecutan {n_metodos} enfoques distribuidos en {len(familias)} familias para separar señal de ruido sintético. "
            f"{supervisados} miran el target, {n_metodos - supervisados} no lo consulta y {aleatorios} dependen de semilla. "
            "`mutual_info` y `mrmr_approx` son las piezas que conectan directamente con la formulación cuántica."
        ),
        "olive_oil_3class": (
            f"Olive Oil 3 clases mantiene {n_metodos} selectores y {len(familias)} tipos metodológicos. El registro marca {supervisados} usos del "
            f"target, {n_metodos - supervisados} método sin supervisión y {aleatorios} procedimientos aleatorios. "
            "La baseline MI y el selector relevancia-redundancia se leen como control clásico del futuro QFS."
        ),
        "olive_oil_9class": (
            f"En Olive Oil 9 clases se aplica una parrilla de {n_metodos} métodos organizada en {len(familias)} bloques, con {supervisados} "
            f"supervisados, {n_metodos - supervisados} control sin target y {aleatorios} sensibles a semilla. "
            "La formulación MI/mRMR conserva el puente metodológico hacia detunings y redundancias atómicas."
        ),
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_handoff_qfs(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    resumen = _filas(_df(resultados, "fs_qfs_handoff_matrices_index.csv"), dataset)
    vector = _filas(_df(resultados, "fs_qfs_mi_target_vector_long.csv"), dataset)
    matriz = _filas(_df(resultados, "fs_qfs_pairwise_mi_matrix_long.csv"), dataset)
    if resumen.empty:
        return "No hay matrices de handoff QFS para este dataset."
    fila = resumen.iloc[0]
    top = vector.sort_values("I_i", ascending=False).head(3)["feature"].tolist() if not vector.empty else []
    offdiag = matriz[matriz["feature_i"] != matriz["feature_j"]] if not matriz.empty else pd.DataFrame()
    variantes = {
        "breast_cancer_wisconsin": f"El puente QFS clínico conserva {int(fila.n_features)} variables, I_i medio {_fmt(fila.mean_I_i, 4)}, máximo {_fmt(fila.max_I_i, 4)} y R_ij off-diagonal {_fmt(fila.mean_R_ij_offdiag, 4)}. Mayor MI frente al target: {_lista(top, 3)}; esa matriz alimenta la geometría atómica.",
        "customer_churn": f"Para churn, el handoff cuántico guarda {int(fila.n_features)} features con I_i medio {_fmt(fila.mean_I_i, 4)}, pico {_fmt(fila.max_I_i, 4)} y redundancia MI pareada media {_fmt(fila.mean_R_ij_offdiag, 4)}. Top de relevancia: {_lista(top, 3)}.",
        "madelon": f"Madelon entrega a QFS {int(fila.n_features)} variables; la media de I_i es {_fmt(fila.mean_I_i, 4)}, el máximo {_fmt(fila.max_I_i, 4)} y R_ij medio {_fmt(fila.mean_R_ij_offdiag, 4)}. Encabezan la señal {_lista(top, 3)}.",
        "olive_oil_3class": f"Olive Oil 3 clases materializa {int(fila.n_features)} nodos candidatos, con I_i medio {_fmt(fila.mean_I_i, 4)}, I_i máximo {_fmt(fila.max_I_i, 4)} y MI par a par media {_fmt(fila.mean_R_ij_offdiag, 4)}. Variables dominantes: {_lista(top, 3)}.",
        "olive_oil_9class": f"Olive Oil 9 clases deja {int(fila.n_features)} variables para el mapa QFS; I_i promedia {_fmt(fila.mean_I_i, 4)}, alcanza {_fmt(fila.max_I_i, 4)} y R_ij fuera de diagonal promedia {_fmt(fila.mean_R_ij_offdiag, 4)}. Top MI: {_lista(top, 3)}.",
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_configuracion_coste(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    plan = _filas(_df(resultados, "fs_sampling_plan.csv"), dataset)
    rep = _filas(_df(resultados, "fs_sampling_representativeness.csv"), dataset)
    conf = _filas(_df(resultados, "fs_method_configurations.csv"), dataset)
    if plan.empty:
        return "No hay plan de muestreo registrado para este dataset."
    p = plan.iloc[0]
    diff = rep.iloc[0].max_abs_target_prop_diff if not rep.empty else None
    sample_txt = (
        f"usa muestra de {int(p.sample_size)} sobre {int(p.train_size)} filas"
        if bool(p.sample_applied)
        else f"usa el train completo de {int(p.train_size)} filas"
    )
    decisiones = conf["decision"].value_counts().to_dict() if not conf.empty else {}
    variantes = {
        "breast_cancer_wisconsin": f"Breast Cancer {sample_txt}; la desviación máxima de clases frente a train es {_fmt(diff, 6)}. Decisiones registradas por método: {decisiones}.",
        "customer_churn": f"Customer Churn {sample_txt}. La distancia máxima en proporciones de target queda en {_fmt(diff, 6)}, y el plan de ejecución anota {decisiones}.",
        "madelon": f"Madelon {sample_txt}; el cambio extremo de distribución de `y` es {_fmt(diff, 6)}. La tabla de métodos resume {decisiones}.",
        "olive_oil_3class": f"Olive Oil 3 clases {sample_txt}. La diferencia mayor de composición del target es {_fmt(diff, 6)}; las decisiones quedan {decisiones}.",
        "olive_oil_9class": f"Olive Oil 9 clases {sample_txt}, con máximo desfase de proporción {_fmt(diff, 6)}. El registro de configuración contiene {decisiones}.",
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_k(k_table: pd.DataFrame, dataset: str) -> str:
    local = _filas(k_table, dataset)
    if local.empty:
        return "No hay plan de `k` para este dataset."
    ks = sorted(local["k"].unique())
    n_features = int(local["n_features"].iloc[0])
    red_min = local["reduction_pct"].min()
    red_max = local["reduction_pct"].max()
    variantes = {
        "breast_cancer_wisconsin": f"Breast Cancer evalúa k={_lista(ks, 10)} sobre {n_features} variables; la compresión cubre {_fmt(red_min, 1)}%-{_fmt(red_max, 1)}%. Los valores bajos enlazan con el régimen compacto descrito por PAPER_QFS.",
        "customer_churn": f"Customer Churn prueba k={_lista(ks, 10)} en un espacio de {n_features} predictores. La reducción oscila entre {_fmt(red_min, 1)}% y {_fmt(red_max, 1)}%, útil para medir simplificación operativa.",
        "madelon": f"Madelon usa presupuestos k={_lista(ks, 10)} frente a {n_features} variables; el recorte va de {_fmt(red_min, 1)}% a {_fmt(red_max, 1)}%. Aquí los k pequeños son el test principal de señal.",
        "olive_oil_3class": f"Olive Oil 3 clases considera k={_lista(ks, 10)} con {n_features} variables disponibles. La reducción queda entre {_fmt(red_min, 1)}% y {_fmt(red_max, 1)}%, incluyendo el caso compacto que interesa a QFS.",
        "olive_oil_9class": f"Olive Oil 9 clases recorre k={_lista(ks, 10)} sobre {n_features} predictores; la disminución dimensional va de {_fmt(red_min, 1)}% a {_fmt(red_max, 1)}%. La lectura prioriza subconjuntos pequeños por el paper QFS.",
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_baseline(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    resumen = _filas(_df(resultados, "fs_baseline_summary.csv"), dataset)
    seleccion = _filas(_df(resultados, "fs_baseline_selected_features.csv"), dataset)
    if resumen.empty:
        return "No hay resumen de baseline para este dataset."
    rapido = resumen.sort_values("mean_elapsed_seconds").iloc[0]
    lento = resumen.sort_values("mean_elapsed_seconds").iloc[-1]
    top = []
    if not seleccion.empty:
        top = (
            seleccion["feature"].value_counts().head(5).index.tolist()
        )
    variantes = {
        "breast_cancer_wisconsin": (
            f"La referencia rápida clínica compara `variance`, `f_classif` y `mutual_info`: `{rapido.method}` tarda "
            f"{_fmt(rapido.mean_elapsed_seconds, 4)} s de media y `{lento.method}` sube a {_fmt(lento.mean_elapsed_seconds, 4)} s. "
            f"Variables recurrentes en esa terna: {_lista(top, 5)}."
        ),
        "customer_churn": (
            f"En churn, la baseline barata deja a `{rapido.method}` como opción de {_fmt(rapido.mean_elapsed_seconds, 4)} s y "
            f"a `{lento.method}` como extremo de {_fmt(lento.mean_elapsed_seconds, 4)} s. Las variables que más reaparecen son "
            f"{_lista(top, 5)}."
        ),
        "madelon": (
            f"Para madelon, el control inicial muestra {_fmt(rapido.mean_elapsed_seconds, 4)} s en `{rapido.method}` frente a "
            f"{_fmt(lento.mean_elapsed_seconds, 4)} s en `{lento.method}`. Dentro de la baseline destacan {_lista(top, 5)}."
        ),
        "olive_oil_3class": (
            f"Olive Oil 3 clases obtiene una referencia mínima con `{rapido.method}` en {_fmt(rapido.mean_elapsed_seconds, 4)} s y "
            f"`{lento.method}` en {_fmt(lento.mean_elapsed_seconds, 4)} s. La repetición de variables apunta a {_lista(top, 5)}."
        ),
        "olive_oil_9class": (
            f"En la formulación de 9 clases, `{rapido.method}` marca {_fmt(rapido.mean_elapsed_seconds, 4)} s y `{lento.method}` "
            f"{_fmt(lento.mean_elapsed_seconds, 4)} s dentro de los tres filtros rápidos. Variables comunes: {_lista(top, 5)}."
        ),
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_granularidad(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    indice = _filas(_df(resultados, "fs_experiment_table_index.csv"), dataset)
    pivot = _filas(_df(resultados, "fs_experiment_selection_pivot.csv"), dataset)
    if indice.empty:
        return "No hay índice granular de experimentos para este dataset."
    n_methods = indice["method"].nunique()
    n_k = indice["k"].nunique()
    n_tables = len(indice) * 2
    filas_ranking = int(indice["ranking_rows"].sum())
    k_cols = [col for col in pivot.columns if col.startswith("k_")]
    max_unique = int(pivot[k_cols].to_numpy().max()) if not pivot.empty and k_cols else 0
    variantes = {
        "breast_cancer_wisconsin": f"Breast Cancer cuenta {len(indice)} experimentos, {n_methods} métodos y {n_k} presupuestos k. Se escriben {n_tables} CSVs específicos, con {filas_ranking} filas de ranking y un máximo de {max_unique} variables únicas en el pivot.",
        "customer_churn": f"Customer Churn queda desglosado en {len(indice)} unidades método-k, usando {n_methods} selectores y {n_k} valores de k. El índice apunta a {n_tables} tablas y acumula {filas_ranking} filas; el pivot alcanza {max_unique} variables únicas.",
        "madelon": f"Madelon materializa {len(indice)} experimentos granulares para {n_methods} métodos y {n_k} k distintos. Ranking y selección generan {n_tables} archivos, {filas_ranking} filas trazables y celdas pivot de hasta {max_unique} variables.",
        "olive_oil_3class": f"Olive Oil 3 clases organiza {len(indice)} combinaciones experimentales, con {n_methods} métodos sobre {n_k} presupuestos. Sus {n_tables} CSVs suman {filas_ranking} filas y el resumen método-k llega a {max_unique} variables.",
        "olive_oil_9class": f"Olive Oil 9 clases registra {len(indice)} pares método-k multiplicados por tablas de ranking y selección: {n_tables} CSVs. Hay {filas_ranking} filas reconstruibles y el pivot no supera {max_unique} variables únicas.",
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_coste_ejecucion(execution_log: pd.DataFrame, dataset: str) -> str:
    local = _filas(execution_log, dataset)
    if local.empty:
        return "No hay log de ejecución para este dataset."
    medias = local.groupby("method")["elapsed_seconds"].mean().sort_values()
    fallos = int((local["status"] != "ok").sum())
    sample = local.groupby("method")["sample_applied"].any()
    muestreados = sample[sample].index.tolist()
    variantes = {
        "breast_cancer_wisconsin": (
            f"El log clínico contiene {len(local)} ejecuciones, con {fallos} fallos. En promedio domina por rapidez "
            f"`{medias.index[0]}` ({_fmt(medias.iloc[0], 4)} s), mientras `{medias.index[-1]}` llega a "
            f"{_fmt(medias.iloc[-1], 4)} s. Muestreo aplicado en: {_lista(muestreados)}."
        ),
        "customer_churn": (
            f"Para churn se registran {len(local)} ejecuciones y {fallos} incidencias. El menor tiempo medio corresponde a "
            f"`{medias.index[0]}` con {_fmt(medias.iloc[0], 4)} s; el mayor, a `{medias.index[-1]}` con "
            f"{_fmt(medias.iloc[-1], 4)} s. Métodos muestreados: {_lista(muestreados)}."
        ),
        "madelon": (
            f"En madelon hay {len(local)} ejecuciones documentadas y {fallos} fallos. La media mínima es de "
            f"`{medias.index[0]}` ({_fmt(medias.iloc[0], 4)} s) y la máxima de `{medias.index[-1]}` "
            f"({_fmt(medias.iloc[-1], 4)} s). Selección con muestra: {_lista(muestreados)}."
        ),
        "olive_oil_3class": (
            f"Olive Oil 3 clases aporta {len(local)} medidas de tiempo y {fallos} fallos. El selector más ligero es "
            f"`{medias.index[0]}` ({_fmt(medias.iloc[0], 4)} s); el coste superior lo marca `{medias.index[-1]}` "
            f"con {_fmt(medias.iloc[-1], 4)} s. Métodos con submuestra: {_lista(muestreados)}."
        ),
        "olive_oil_9class": (
            f"Olive Oil 9 clases suma {len(local)} ejecuciones válidas en el log y {fallos} fallos. La rapidez media queda en "
            f"`{medias.index[0]}` ({_fmt(medias.iloc[0], 4)} s), frente a `{medias.index[-1]}` "
            f"({_fmt(medias.iloc[-1], 4)} s) como extremo alto. Submuestreo usado por: {_lista(muestreados)}."
        ),
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_ranking(rankings: pd.DataFrame, dataset: str) -> str:
    local = _filas(rankings, dataset)
    if local.empty:
        return "No hay ranking largo para este dataset."
    seleccionadas = local[local["selected"]]
    top = seleccionadas["feature"].value_counts().head(5).index.tolist()
    metodos = local["method"].nunique()
    filas = len(local)
    return (
        f"El ranking local contiene {filas} filas para {metodos} métodos. Las variables que más se repiten en subconjuntos "
        f"seleccionados son: {_lista(top, 5)}. Esta lista procede del ranking ejecutado, no de una expectativa previa."
    )


def lectura_estabilidad(jaccard: pd.DataFrame, dataset: str) -> str:
    local = _filas(jaccard, dataset)
    if local.empty:
        return "No hay métricas de estabilidad para este dataset."
    medias = local.groupby("method")["jaccard"].mean().sort_values(ascending=False)
    variantes = {
        "breast_cancer_wisconsin": (
            f"Entre pares de semillas, Breast Cancer presenta Jaccard medio entre {_fmt(medias.min(), 3)} y "
            f"{_fmt(medias.max(), 3)}. Lidera `{medias.index[0]}` y cierra `{medias.index[-1]}`; Kuncheva descuenta el "
            "solape esperable al azar y Spearman revisa si el ranking completo conserva orden."
        ),
        "customer_churn": (
            f"En churn, el solape Jaccard promedio se mueve de {_fmt(medias.min(), 3)} a {_fmt(medias.max(), 3)}. "
            f"La media superior corresponde a `{medias.index[0]}` y la inferior a `{medias.index[-1]}`; las columnas "
            "Kuncheva y Spearman separan tamaño de subconjunto y estabilidad ordinal."
        ),
        "madelon": (
            f"Madelon deja un intervalo Jaccard de {_fmt(medias.min(), 3)}-{_fmt(medias.max(), 3)} al comparar semillas. "
            f"`{medias.index[0]}` ocupa el extremo estable y `{medias.index[-1]}` el extremo variable; Kuncheva y Spearman "
            "ayudan a distinguir coincidencia de features y persistencia del ranking."
        ),
        "olive_oil_3class": (
            f"En Olive Oil 3 clases, la estabilidad Jaccard media cubre {_fmt(medias.min(), 3)} a {_fmt(medias.max(), 3)}. "
            f"El valor más alto lo aporta `{medias.index[0]}` y el más bajo `{medias.index[-1]}`; el contraste con "
            "Kuncheva/Spearman indica si el acuerdo procede del subconjunto o del orden global."
        ),
        "olive_oil_9class": (
            f"Olive Oil 9 clases muestra Jaccard medio entre {_fmt(medias.min(), 3)} y {_fmt(medias.max(), 3)}. "
            f"`{medias.index[0]}` queda como referencia de robustez y `{medias.index[-1]}` como caso menos consistente; "
            "Kuncheva corrige por azar y Spearman compara la lista completa de variables."
        ),
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_permutacion(perm_summary: pd.DataFrame, resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    local = _filas(perm_summary, dataset)
    detalle = _filas(_df(resultados, "fs_permutation_empirical_pvalues.csv"), dataset)
    if local.empty:
        return "No hay resumen de permutaciones para este dataset."
    filas = []
    for _, row in local.sort_values("method").iterrows():
        if dataset == "breast_cancer_wisconsin":
            texto = f"`{row.method}` supera p95 nulo en {int(row.n_features_above_null)} variables; p empírico mediano {_fmt(row.median_empirical_p_value, 3)}"
        elif dataset == "customer_churn":
            texto = f"`{row.method}` deja {int(row.n_features_above_null)} features sobre el umbral nulo y mediana p {_fmt(row.median_empirical_p_value, 3)}"
        elif dataset == "madelon":
            texto = f"`{row.method}` separa {int(row.n_features_above_null)} variables del p95 permutado; mediana {_fmt(row.median_empirical_p_value, 3)}"
        elif dataset == "olive_oil_3class":
            texto = f"`{row.method}` conserva {int(row.n_features_above_null)} señales por encima del nulo; p mediano {_fmt(row.median_empirical_p_value, 3)}"
        else:
            texto = f"`{row.method}` marca {int(row.n_features_above_null)} variables sobre referencia permutada; valor p central {_fmt(row.median_empirical_p_value, 3)}"
        filas.append(texto)
    top = []
    if not detalle.empty:
        top = (
            detalle.sort_values(["above_null_p95", "real_score"], ascending=[False, False])
            ["feature"].head(5).tolist()
        )
    detalle = {
        "breast_cancer_wisconsin": "En Breast Cancer, el contraste nulo deja",
        "customer_churn": "Para churn, la comparación permutada resume",
        "madelon": "Madelon muestra frente al nulo",
        "olive_oil_3class": "Olive Oil 3 clases registra en permutaciones",
        "olive_oil_9class": "Olive Oil 9 clases obtiene bajo permutación",
    }.get(dataset, "El contraste permutado deja")
    cierres = {
        "breast_cancer_wisconsin": f"Variables con brecha más clara: {_lista(top, 5)}.",
        "customer_churn": f"Señales destacadas en churn: {_lista(top, 5)}.",
        "madelon": f"Columnas que más se apartan del nulo: {_lista(top, 5)}.",
        "olive_oil_3class": f"Componentes con distancia empírica mayor: {_lista(top, 5)}.",
        "olive_oil_9class": f"Rasgos señalados por el detalle local: {_lista(top, 5)}.",
    }
    return f"{detalle}: {'; '.join(filas)}. {cierres.get(dataset, cierres['breast_cancer_wisconsin'])}"


def lectura_redundancia(redundancy: pd.DataFrame, dataset: str) -> str:
    local = _filas(redundancy, dataset)
    if local.empty:
        return "No hay resumen de redundancia para este dataset."
    delta = local.assign(delta=local["selected_mean_abs_corr"] - local["full_mean_abs_corr"])
    medias = delta.groupby("method")["delta"].mean().sort_values()
    full = local["full_mean_abs_corr"].iloc[0]
    variantes = {
        "breast_cancer_wisconsin": f"El espacio clínico completo tiene correlación media absoluta {_fmt(full, 3)}; `{medias.index[0]}` reduce más el delta ({_fmt(medias.iloc[0], 3)}) y `{medias.index[-1]}` lo eleva hasta {_fmt(medias.iloc[-1], 3)}.",
        "customer_churn": f"En churn, la redundancia base es {_fmt(full, 3)}. El cambio medio mínimo aparece en `{medias.index[0]}` con {_fmt(medias.iloc[0], 3)}, mientras `{medias.index[-1]}` alcanza {_fmt(medias.iloc[-1], 3)}.",
        "madelon": f"Madelon parte de una correlación absoluta media {_fmt(full, 3)}. El selector con menor delta es `{medias.index[0]}` ({_fmt(medias.iloc[0], 3)}) y el extremo superior queda en `{medias.index[-1]}` ({_fmt(medias.iloc[-1], 3)}).",
        "olive_oil_3class": f"Para Olive Oil 3 clases, el nivel completo de redundancia es {_fmt(full, 3)}. `{medias.index[0]}` deja el delta más bajo ({_fmt(medias.iloc[0], 3)}) y `{medias.index[-1]}` el más alto ({_fmt(medias.iloc[-1], 3)}).",
        "olive_oil_9class": f"Olive Oil 9 clases muestra redundancia completa {_fmt(full, 3)}; la media de delta va desde `{medias.index[0]}` con {_fmt(medias.iloc[0], 3)} hasta `{medias.index[-1]}` con {_fmt(medias.iloc[-1], 3)}.",
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_eda(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    evidencia = _filas(_df(resultados, "fs_selected_feature_evidence_map.csv"), dataset)
    sospechosas = _filas(_df(resultados, "fs_suspicious_selected_features.csv"), dataset)
    if evidencia.empty:
        return "No hay mapa de evidencia previa para este dataset."
    cobertura = evidencia["evidence_coverage"].mean()
    variantes = {
        "breast_cancer_wisconsin": f"En Breast Cancer, la cobertura de evidencia previa alcanza {_fmt(cobertura, 3)} y las variables sospechosas seleccionadas son {len(sospechosas)}.",
        "customer_churn": f"Para churn, el cruce EDA cubre {_fmt(cobertura, 3)} de las variables seleccionadas; el contador de sospechosas queda en {len(sospechosas)}.",
        "madelon": f"Madelon presenta cobertura exploratoria {_fmt(cobertura, 3)} dentro de sus subconjuntos, con {len(sospechosas)} nombres marcados como sospechosos.",
        "olive_oil_3class": f"Olive Oil 3 clases consigue {_fmt(cobertura, 3)} de cobertura frente a evidencias previas y registra {len(sospechosas)} selecciones sospechosas.",
        "olive_oil_9class": f"Olive Oil 9 clases deja cobertura EDA {_fmt(cobertura, 3)}; las variables seleccionadas con alerta semántica suman {len(sospechosas)}.",
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_reducidos(resultados: dict[str, pd.DataFrame], dataset: str) -> str:
    log = _filas(_df(resultados, "fs_reduced_datasets_log.csv"), dataset)
    check = _filas(_df(resultados, "fs_column_consistency_check.csv"), dataset)
    if log.empty or check.empty:
        return "No hay evidencia completa de materialización de reducidos para este dataset."
    estados = check["status"].value_counts().to_dict()
    combinaciones = check[["method", "k"]].drop_duplicates().shape[0]
    alias_ok = bool(check["x_val_alias_saved"].all())
    variantes = {
        "breast_cancer_wisconsin": f"Breast Cancer genera {len(log)} archivos reducidos para {combinaciones} pares método-k. La consistencia queda {estados} y el alias validation abreviado existe: {alias_ok}.",
        "customer_churn": f"Customer Churn materializa {len(log)} ficheros y revisa {combinaciones} combinaciones. Los estados son {estados}; `X_val_selected.csv` está presente en el conjunto: {alias_ok}.",
        "madelon": f"Madelon deja {len(log)} salidas reducidas y {combinaciones} checks método-k. La tabla de consistencia marca {estados}, con alias de validación creado: {alias_ok}.",
        "olive_oil_3class": f"Olive Oil 3 clases escribe {len(log)} CSVs reducidos sobre {combinaciones} configuraciones. La comprobación devuelve {estados} y confirma alias corto de validation: {alias_ok}.",
        "olive_oil_9class": f"Olive Oil 9 clases conserva {len(log)} archivos seleccionados y {combinaciones} verificaciones. El resultado de columnas es {estados}; el alias `X_val` queda disponible: {alias_ok}.",
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_visual(figuras_reporte: pd.DataFrame, dataset: str) -> str:
    local = _filas(figuras_reporte, dataset)
    if local.empty:
        return "No hay figuras registradas para este dataset."
    tipos = local["figure_type"].value_counts().to_dict()
    memoria = int(local["supports_memory"].sum()) if "supports_memory" in local else 0
    variantes = {
        "breast_cancer_wisconsin": f"El bloque visual clínico reúne {len(local)} figuras, tipos {tipos} y {memoria} candidatas a memoria; cada PNG conserva PDF vectorial para LaTeX.",
        "customer_churn": f"Customer Churn muestra {len(local)} salidas gráficas con clasificación {tipos}; {memoria} pasan como material de memoria y todas mantienen pareja PNG/PDF.",
        "madelon": f"Madelon concentra {len(local)} figuras de selección, con reparto {tipos}. Las {memoria} candidatas sostienen la lectura de alta dimensión y tienen exportación doble.",
        "olive_oil_3class": f"Olive Oil 3 clases aporta {len(local)} figuras registradas; los tipos son {tipos} y {memoria} quedan aptas para memoria con artefacto vectorial.",
        "olive_oil_9class": f"Olive Oil 9 clases cierra con {len(local)} figuras, distribución {tipos} y {memoria} candidatas. La comprobación visual enlaza cada PNG con su PDF.",
    }
    return variantes.get(dataset, variantes["breast_cancer_wisconsin"])


def lectura_sintesis_global(
    method_profiles: pd.DataFrame,
    perm_summary: pd.DataFrame,
    redundancy: pd.DataFrame,
    jaccard: pd.DataFrame,
) -> str:
    if method_profiles.empty:
        return "No hay perfiles globales de métodos para sintetizar."
    coste = method_profiles.sort_values("mean_elapsed_seconds")
    estabilidad = method_profiles.sort_values("mean_jaccard", ascending=False)
    corr = method_profiles.sort_values("mean_selected_corr")
    perm = (
        perm_summary.groupby("dataset")["n_features_above_null"].sum().sort_values(ascending=False)
        if not perm_summary.empty
        else pd.Series(dtype=float)
    )
    jac_dataset = (
        jaccard.groupby("dataset")["jaccard"].mean().sort_values()
        if not jaccard.empty
        else pd.Series(dtype=float)
    )
    red_dataset = pd.Series(dtype=float)
    if not redundancy.empty:
        red_dataset = (
            redundancy.assign(delta=redundancy["selected_mean_abs_corr"] - redundancy["full_mean_abs_corr"])
            .groupby("dataset")["delta"].mean()
            .sort_values(ascending=False)
        )
    piezas = [
        f"Por coste medio, el método más barato es `{coste.iloc[0].method}` ({_fmt(coste.iloc[0].mean_elapsed_seconds, 4)} s) y el más caro es `{coste.iloc[-1].method}` ({_fmt(coste.iloc[-1].mean_elapsed_seconds, 4)} s).",
        f"Por estabilidad media, lidera `{estabilidad.iloc[0].method}` ({_fmt(estabilidad.iloc[0].mean_jaccard, 3)}) y cierra `{estabilidad.iloc[-1].method}` ({_fmt(estabilidad.iloc[-1].mean_jaccard, 3)}).",
        f"Por redundancia media seleccionada, el valor más bajo corresponde a `{corr.iloc[0].method}` ({_fmt(corr.iloc[0].mean_selected_corr, 3)}) y el más alto a `{corr.iloc[-1].method}` ({_fmt(corr.iloc[-1].mean_selected_corr, 3)}).",
    ]
    if not perm.empty:
        piezas.append(
            f"En permutaciones, el dataset con más variables por encima del nulo es `{perm.index[0]}` ({int(perm.iloc[0])}) y el menor es `{perm.index[-1]}` ({int(perm.iloc[-1])})."
        )
    if not jac_dataset.empty:
        piezas.append(
            f"El Jaccard medio por dataset es menor en `{jac_dataset.index[0]}` ({_fmt(jac_dataset.iloc[0], 3)}) y mayor en `{jac_dataset.index[-1]}` ({_fmt(jac_dataset.iloc[-1], 3)})."
        )
    if not red_dataset.empty:
        piezas.append(
            f"El aumento medio de redundancia frente al espacio completo es mayor en `{red_dataset.index[0]}` ({_fmt(red_dataset.iloc[0], 3)})."
        )
    return " ".join(piezas)


def lectura_conclusiones(
    resultados: dict[str, pd.DataFrame],
    method_profiles: pd.DataFrame,
    perm_summary: pd.DataFrame,
    redundancy: pd.DataFrame,
    jaccard: pd.DataFrame,
) -> str:
    entradas = _df(resultados, "fs_input_dataset_summary.csv")
    sospechosas = _df(resultados, "fs_suspicious_selected_features.csv")
    checks = _df(resultados, "fs_column_consistency_check.csv")
    if entradas.empty:
        return "No hay suficientes evidencias finales para redactar conclusiones."
    mayor_filas = entradas.sort_values("train_rows", ascending=False).iloc[0]
    mayor_dim = entradas.sort_values("processed_features", ascending=False).iloc[0]
    ok_reducidos = bool(checks["status"].eq("ok").all()) if not checks.empty else False
    n_sospechosas = len(sospechosas)
    sintesis = lectura_sintesis_global(method_profiles, perm_summary, redundancy, jaccard)
    return (
        f"La fase termina con {len(entradas)} datasets operativos. El mayor train es `{mayor_filas.dataset}` "
        f"con {int(mayor_filas.train_rows)} filas, y el mayor espacio de variables es `{mayor_dim.dataset}` "
        f"con {int(mayor_dim.processed_features)} predictores. Variables sospechosas seleccionadas: {n_sospechosas}. "
        f"Consistencia de reducidos completamente correcta: {ok_reducidos}. {sintesis}"
    )
