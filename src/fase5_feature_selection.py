"""Funciones granulares para la Fase 5: selección clásica de características."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, f_classif, mutual_info_classif, mutual_info_regression
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import mutual_info_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.svm import LinearSVC

try:  # BorutaPy vive como dependencia externa del entorno qfs_env.
    from boruta import BorutaPy
except Exception:  # pragma: no cover
    BorutaPy = None


RANDOM_STATE = 42
SEEDS_ESTABILIDAD = [13, 42, 97]
N_PERMUTACIONES = 20
DATASETS = [
    "breast_cancer_wisconsin",
    "customer_churn",
    "madelon",
    "olive_oil_3class",
    "olive_oil_9class",
]
ROSTER_12 = [
    "variance",
    "f_classif",
    "mutual_info",
    "mutual_correlation",
    "feature_similarity",
    "mrmr_approx",
    "rrfs",
    "boruta",
    "rfe",
    "l1_logistic",
    "random_forest",
    "linear_svm",
]
METODOS_PERMUTACION = ["f_classif", "mutual_info"]
PROHIBITED_FEATURES = {"target", "area", "region", "class", "label", "original_index"}
TABLE_DIR = Path("results/tables/05_feature_selection")
FIGURE_DIR = Path("results/figures/05_feature_selection")
REPORT_DIR = Path("results/reports")
PHASE_REPORT_DIR = Path("results/reports/05_feature_selection")
LOG_DIR = Path("results/logs/05_feature_selection")
SELECTED_DIR = Path("data/selected_features")


@dataclass(frozen=True)
class DatasetBundle:
    dataset: str
    x_train_raw: pd.DataFrame
    x_validation_raw: pd.DataFrame
    x_test_raw: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series
    y_test: pd.Series
    x_train: pd.DataFrame
    x_validation: pd.DataFrame
    x_test: pd.DataFrame
    preprocessor: ColumnTransformer


@dataclass(frozen=True)
class MIDiscretization:
    x_discrete: pd.DataFrame
    continuous_columns: list[str]
    discrete_columns: list[str]
    n_bins: int
    strategy: str
    normalization_note: str


def asegurar_directorios() -> None:
    for path in [TABLE_DIR, FIGURE_DIR, REPORT_DIR, PHASE_REPORT_DIR, LOG_DIR, SELECTED_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def marca_temporal() -> str:
    return datetime.now().isoformat(timespec="seconds")


def guardar_csv(tabla: pd.DataFrame, nombre: str, directorio: Path = TABLE_DIR) -> Path:
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / nombre
    tabla.to_csv(ruta, index=False)
    return ruta


def extraer_target(tabla_y: pd.DataFrame) -> pd.Series:
    columnas = [col for col in tabla_y.columns if col != "original_index"]
    if not columnas:
        columnas = list(tabla_y.columns)
    return tabla_y[columnas[-1]].reset_index(drop=True)


def cargar_split(dataset: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    base = Path("data/splits") / dataset
    x_train = pd.read_csv(base / "X_train.csv")
    x_validation = pd.read_csv(base / "X_validation.csv")
    x_test = pd.read_csv(base / "X_test.csv")
    y_train = extraer_target(pd.read_csv(base / "y_train.csv"))
    y_validation = extraer_target(pd.read_csv(base / "y_validation.csv"))
    y_test = extraer_target(pd.read_csv(base / "y_test.csv"))
    return x_train, x_validation, x_test, y_train, y_validation, y_test


def columnas_predictoras_validas(tabla: pd.DataFrame) -> list[str]:
    columnas = []
    for columna in tabla.columns:
        nombre = str(columna).lower()
        if nombre in PROHIBITED_FEATURES or nombre.endswith("_target") or "target" in nombre:
            continue
        columnas.append(columna)
    return columnas


def crear_preprocesador(x_train: pd.DataFrame) -> ColumnTransformer:
    numericas = x_train.select_dtypes(include=[np.number]).columns.tolist()
    categoricas = [col for col in x_train.columns if col not in numericas]
    transformadores: list[tuple[str, Pipeline, list[str]]] = []
    if numericas:
        transformadores.append(
            (
                "num",
                Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]),
                numericas,
            )
        )
    if categoricas:
        transformadores.append(
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categoricas,
            )
        )
    return ColumnTransformer(transformadores, remainder="drop", verbose_feature_names_out=False)


def construir_matriz(
    dataset: str,
    x_train_raw: pd.DataFrame,
    x_validation_raw: pd.DataFrame,
    x_test_raw: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, ColumnTransformer]:
    columnas = columnas_predictoras_validas(x_train_raw)
    preprocessor = crear_preprocesador(x_train_raw[columnas])
    x_train = pd.DataFrame(preprocessor.fit_transform(x_train_raw[columnas]), columns=preprocessor.get_feature_names_out())
    x_validation = pd.DataFrame(preprocessor.transform(x_validation_raw[columnas]), columns=x_train.columns)
    x_test = pd.DataFrame(preprocessor.transform(x_test_raw[columnas]), columns=x_train.columns)
    x_train.columns = [str(col).replace(" ", "_") for col in x_train.columns]
    x_validation.columns = x_train.columns
    x_test.columns = x_train.columns
    return x_train, x_validation, x_test, preprocessor


def cargar_dataset(dataset: str) -> DatasetBundle:
    x_train_raw, x_validation_raw, x_test_raw, y_train, y_validation, y_test = cargar_split(dataset)
    x_train, x_validation, x_test, preprocessor = construir_matriz(dataset, x_train_raw, x_validation_raw, x_test_raw)
    return DatasetBundle(
        dataset,
        x_train_raw,
        x_validation_raw,
        x_test_raw,
        y_train,
        y_validation,
        y_test,
        x_train,
        x_validation,
        x_test,
        preprocessor,
    )


def resumen_dataset(bundle: DatasetBundle) -> dict[str, Any]:
    return {
        "dataset": bundle.dataset,
        "n_train": len(bundle.x_train),
        "n_validation": len(bundle.x_validation),
        "n_test": len(bundle.x_test),
        "n_features": bundle.x_train.shape[1],
        "n_classes_train": bundle.y_train.nunique(),
        "minority_class_train_pct": 100 * bundle.y_train.value_counts(normalize=True).min(),
    }


def construir_registro_metodos() -> pd.DataFrame:
    registros = [
        ("variance", "base mínima", False, "ranking", "varianza tras escalado"),
        ("f_classif", "relevancia pura", True, "ranking", "F univariante"),
        ("mutual_info", "relevancia pura", True, "ranking", "I(x;y)"),
        ("mutual_correlation", "redundancia pura", False, "ranking", "Pearson medio"),
        ("feature_similarity", "redundancia pura", False, "ranking", "clusters varianza-covarianza"),
        ("mrmr_approx", "relevancia-redundancia", True, "ranking", "MI menos correlación"),
        ("rrfs", "relevancia-redundancia", True, "ranking", "Fisher con poda de similitud"),
        ("boruta", "wrapper all-relevant", True, "conjunto natural", "shadow features"),
        ("rfe", "wrapper minimal-optimal", True, "ranking", "eliminación recursiva"),
        ("l1_logistic", "embedded", True, "ranking", "coeficientes L1"),
        ("random_forest", "embedded", True, "ranking", "importancia de bosque"),
        ("linear_svm", "embedded", True, "ranking", "margen lineal"),
    ]
    return pd.DataFrame(registros, columns=["method", "familia", "usa_target", "salida", "criterio_tecnico"])


def valores_k(n_features: int) -> list[int]:
    candidatos = [5, 10, 15, 20, 30, 50, int(round(math.sqrt(n_features))), max(1, n_features // 10)]
    validos = sorted({k for k in candidatos if 1 <= k <= n_features})
    if n_features <= 12:
        validos = sorted({3, 5, min(8, n_features), n_features} & set(range(1, n_features + 1)))
    if n_features <= 5:
        validos = list(range(1, n_features + 1))
    return validos


def crear_muestra(
    x: pd.DataFrame,
    y: pd.Series,
    max_rows: int = 5000,
    seed: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    if len(x) <= max_rows:
        return x, y, {"sample_applied": False, "sample_size": len(x), "train_size": len(x), "seed": seed}
    x_sample, _, y_sample, _ = train_test_split(x, y, train_size=max_rows, random_state=seed, stratify=y)
    return (
        x_sample.reset_index(drop=True),
        y_sample.reset_index(drop=True),
        {"sample_applied": True, "sample_size": len(x_sample), "train_size": len(x), "seed": seed},
    )


def vector_fisher(x: pd.DataFrame, y: pd.Series) -> np.ndarray:
    scores, _ = f_classif(x, y)
    return np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)


def calcular_mi_relevancia(x: pd.DataFrame, y: pd.Series, semilla: int) -> pd.Series:
    x_discrete = discretizar_matriz_train(x, semilla).x_discrete
    valores = mutual_info_classif(x_discrete, y, random_state=semilla, discrete_features=True)
    return pd.Series(valores, index=x.columns, name="I_i")


def calcular_mi_pares(x: pd.DataFrame, semilla: int) -> pd.DataFrame:
    x_discrete = discretizar_matriz_train(x, semilla).x_discrete
    valores = x_discrete.to_numpy()
    n_features = valores.shape[1]
    matriz = np.zeros((n_features, n_features), dtype=float)
    for i in range(n_features):
        xi = valores[:, i]
        for j in range(i + 1, n_features):
            mi = mutual_info_score(xi, valores[:, j])
            matriz[i, j] = mi
            matriz[j, i] = mi
    matriz = pd.DataFrame(matriz, index=x.columns, columns=x.columns)
    np.fill_diagonal(matriz.values, 0.0)
    return matriz


def discretizar_matriz_train(x_train: pd.DataFrame, semilla: int = RANDOM_STATE, n_bins: int = 5) -> MIDiscretization:
    """Discretiza train con la convención QFS: continuas a 5 bins uniformes."""
    columnas_discretas: dict[str, np.ndarray] = {}
    continuous_columns: list[str] = []
    discrete_columns: list[str] = []
    for column in x_train.columns:
        serie = x_train[column]
        if str(serie.dtype) == "object" or serie.nunique(dropna=True) <= 10:
            discrete_columns.append(column)
            columnas_discretas[column] = pd.Categorical(serie).codes.astype(int)
        else:
            continuous_columns.append(column)
            discretizer = KBinsDiscretizer(
                n_bins=n_bins,
                encode="ordinal",
                strategy="uniform",
                subsample=200_000,
                random_state=semilla,
            )
            columnas_discretas[column] = discretizer.fit_transform(serie.to_frame()).ravel().astype(int)
    x_discrete = pd.DataFrame(columnas_discretas, index=x_train.index)
    return MIDiscretization(
        x_discrete=x_discrete[x_train.columns],
        continuous_columns=continuous_columns,
        discrete_columns=discrete_columns,
        n_bins=n_bins,
        strategy="uniform",
        normalization_note="MI discreta sin filtro por umbral y sin normalización min-max en Fase 5; verificar en Fase 8 para no normalizar dos veces.",
    )


def scores_mutual_correlation(x: pd.DataFrame) -> np.ndarray:
    corr = x.corr(method="pearson").abs().fillna(0.0).to_numpy()
    np.fill_diagonal(corr, 0.0)
    remaining = list(range(x.shape[1]))
    removal_order: list[int] = []
    while remaining:
        sub = corr[np.ix_(remaining, remaining)]
        means = sub.mean(axis=1) if len(remaining) > 1 else np.zeros(1)
        remove_local = int(np.argmax(means))
        removal_order.append(remaining.pop(remove_local))
    scores = np.zeros(x.shape[1], dtype=float)
    for rank, feature_idx in enumerate(reversed(removal_order), start=1):
        scores[feature_idx] = rank
    return scores


def scores_feature_similarity(x: pd.DataFrame, k_objetivo: int | None = None) -> np.ndarray:
    corr = x.corr(method="pearson").abs().fillna(0.0)
    distancia = np.clip(1.0 - corr.to_numpy(), 0.0, 1.0)
    np.fill_diagonal(distancia, 0.0)
    if len(corr) <= 1:
        return np.ones(len(corr))
    linkage_matrix = linkage(squareform(distancia, checks=False), method="average")
    n_clusters = max(1, min(k_objetivo or int(round(math.sqrt(x.shape[1]))), x.shape[1]))
    clusters = fcluster(linkage_matrix, t=n_clusters, criterion="maxclust")
    varianzas = x.var(axis=0).to_numpy()
    scores = np.zeros(x.shape[1], dtype=float)
    for cluster_id in sorted(set(clusters)):
        idx = np.where(clusters == cluster_id)[0]
        orden = idx[np.argsort(-varianzas[idx])]
        for posicion, feature_idx in enumerate(orden):
            scores[feature_idx] = (x.shape[1] - posicion) / (1 + len(idx))
    return scores


def scores_mrmr_aproximado(x: pd.DataFrame, y: pd.Series, semilla: int) -> np.ndarray:
    relevancia = calcular_mi_relevancia(x, y, semilla).to_numpy()
    corr = x.corr(method="spearman").abs().fillna(0).to_numpy()
    seleccionadas: list[int] = []
    pendientes = set(range(x.shape[1]))
    scores = np.zeros(x.shape[1], dtype=float)
    for puesto in range(x.shape[1]):
        mejor = None
        mejor_score = -np.inf
        for candidato in pendientes:
            redundancia = float(corr[candidato, seleccionadas].mean()) if seleccionadas else 0.0
            score = float(relevancia[candidato]) - redundancia
            if score > mejor_score:
                mejor_score = score
                mejor = candidato
        if mejor is None:
            break
        seleccionadas.append(mejor)
        pendientes.remove(mejor)
        scores[mejor] = x.shape[1] - puesto + mejor_score / (abs(mejor_score) + 1.0)
    return scores


def scores_rrfs(x: pd.DataFrame, y: pd.Series, semilla: int) -> np.ndarray:
    relevancia = calcular_mi_relevancia(x, y, semilla).to_numpy()
    corr = x.corr(method="pearson").abs().fillna(0.0).to_numpy()
    np.fill_diagonal(corr, 0.0)
    orden_relevancia = list(np.argsort(-relevancia))
    elegidas: list[int] = []
    pendientes = orden_relevancia.copy()
    scores = np.zeros(x.shape[1], dtype=float)
    while pendientes:
        candidato = pendientes.pop(0)
        if elegidas:
            redundancia = float(corr[candidato, elegidas].max())
        else:
            redundancia = 0.0
        score = float(relevancia[candidato]) / (1.0 + redundancia)
        elegidas.append(candidato)
        scores[candidato] = x.shape[1] - len(elegidas) + 1 + score / (abs(score) + 1.0)
        pendientes = sorted(pendientes, key=lambda idx: relevancia[idx] / (1.0 + (corr[idx, elegidas].max() if elegidas else 0.0)), reverse=True)
    return scores


def scores_rfe(x: pd.DataFrame, y: pd.Series, k: int, semilla: int) -> np.ndarray:
    estimador = LogisticRegression(max_iter=1500, class_weight="balanced", random_state=semilla, n_jobs=-1)
    selector = RFE(estimator=estimador, n_features_to_select=max(1, min(k, x.shape[1])), step=0.2)
    selector.fit(x, y)
    return (x.shape[1] + 1 - selector.ranking_).astype(float)


def ranking_desde_scores(
    dataset: str,
    metodo: str,
    familia: str,
    semilla: int,
    k_values: list[int],
    features: list[str],
    scores: np.ndarray,
    elapsed: float,
    sample_size: int,
    status: str = "ok",
) -> pd.DataFrame:
    scores_limpios = np.nan_to_num(np.asarray(scores, dtype=float), nan=-np.inf, posinf=np.inf, neginf=-np.inf)
    orden = np.argsort(-scores_limpios)
    ranks = np.empty_like(orden)
    ranks[orden] = np.arange(1, len(features) + 1)
    filas = []
    for feature, score, rank in zip(features, scores_limpios, ranks):
        for k in k_values:
            filas.append(
                {
                    "dataset": dataset,
                    "method": metodo,
                    "family": familia,
                    "seed": semilla,
                    "k": int(k),
                    "feature": feature,
                    "rank": int(rank),
                    "score": float(score) if np.isfinite(score) else np.nan,
                    "selected": bool(rank <= k),
                    "elapsed_seconds": elapsed,
                    "sample_size": int(sample_size),
                    "status": status,
                }
            )
    return pd.DataFrame(filas)


def ranking_boruta(
    dataset: str,
    x: pd.DataFrame,
    y: pd.Series,
    semilla: int,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    inicio = time.perf_counter()
    status = "ok"
    warning = ""
    if BorutaPy is None:
        status = "failed"
        warning = "BorutaPy no disponible"
        support = np.zeros(x.shape[1], dtype=bool)
        ranking = np.arange(1, x.shape[1] + 1)
    else:
        bosque = RandomForestClassifier(
            n_estimators=180,
            max_depth=7,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=semilla,
            n_jobs=-1,
        )
        selector = BorutaPy(
            estimator=bosque,
            n_estimators="auto",
            max_iter=25,
            perc=100,
            alpha=0.05,
            random_state=semilla,
            verbose=0,
        )
        try:
            selector.fit(x.to_numpy(), y.to_numpy())
            support = selector.support_.astype(bool)
            ranking = selector.ranking_.astype(int)
        except Exception as exc:  # noqa: BLE001
            status = "failed"
            warning = repr(exc)
            support = np.zeros(x.shape[1], dtype=bool)
            ranking = np.arange(1, x.shape[1] + 1)
    elapsed = time.perf_counter() - inicio
    k_natural = int(support.sum())
    if k_natural == 0 and status == "ok":
        k_natural = 1
        support[np.argmin(ranking)] = True
    scores = x.shape[1] + 1 - ranking
    filas = []
    for feature, rank, score, selected in zip(x.columns, ranking, scores, support):
        filas.append(
            {
                "dataset": dataset,
                "method": "boruta",
                "family": "wrapper all-relevant",
                "seed": semilla,
                "k": k_natural,
                "feature": feature,
                "rank": int(rank),
                "score": float(score),
                "selected": bool(selected),
                "elapsed_seconds": elapsed,
                "sample_size": len(x),
                "status": status,
            }
        )
    natural = pd.DataFrame(
        [{"dataset": dataset, "method": "boruta", "seed": semilla, "k_confirmed": k_natural, "n_features": x.shape[1]}]
    )
    log = {
        "timestamp": marca_temporal(),
        "dataset": dataset,
        "method": "boruta",
        "seed": semilla,
        "elapsed_seconds": elapsed,
        "sample_size": len(x),
        "sample_applied": False,
        "status": status,
        "warning": warning,
    }
    return pd.DataFrame(filas), log, natural


def ejecutar_selector(
    metodo: str,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    k: int | None,
    semilla: int,
    dataset: str,
    familia: str,
    k_values: list[int] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    features = list(x_train.columns)
    if metodo in {"variance", "f_classif", "mutual_correlation", "feature_similarity"}:
        x_fit, y_fit, sample_info = x_train, y_train, {"sample_applied": False, "sample_size": len(x_train), "train_size": len(x_train)}
    else:
        x_fit, y_fit, sample_info = crear_muestra(x_train, y_train, seed=semilla)
    if metodo == "boruta":
        ranking, log, natural = ranking_boruta(dataset, x_fit, y_fit, semilla)
        log["sample_applied"] = sample_info["sample_applied"]
        return ranking, log, natural
    inicio = time.perf_counter()
    status = "ok"
    warning = ""
    try:
        if metodo == "variance":
            scores = x_train.var(axis=0).to_numpy()
        elif metodo == "f_classif":
            scores = vector_fisher(x_train, y_train)
        elif metodo == "mutual_info":
            scores = calcular_mi_relevancia(x_fit, y_fit, semilla).reindex(features).to_numpy()
        elif metodo == "mutual_correlation":
            scores = scores_mutual_correlation(x_train)
        elif metodo == "feature_similarity":
            scores = scores_feature_similarity(x_train, k)
        elif metodo == "mrmr_approx":
            scores = scores_mrmr_aproximado(x_fit, y_fit, semilla)
        elif metodo == "rrfs":
            scores = scores_rrfs(x_fit, y_fit, semilla)
        elif metodo == "rfe":
            scores = scores_rfe(x_fit, y_fit, int(k or min(10, x_fit.shape[1])), semilla)
        elif metodo == "l1_logistic":
            modelo = LogisticRegression(penalty="l1", solver="saga", C=0.2, max_iter=2500, class_weight="balanced", random_state=semilla, n_jobs=-1)
            modelo.fit(x_fit, y_fit)
            scores = np.abs(modelo.coef_).mean(axis=0)
        elif metodo == "random_forest":
            modelo = RandomForestClassifier(n_estimators=160, min_samples_leaf=2, class_weight="balanced_subsample", random_state=semilla, n_jobs=-1)
            modelo.fit(x_fit, y_fit)
            scores = modelo.feature_importances_
        elif metodo == "linear_svm":
            modelo = LinearSVC(C=0.05, class_weight="balanced", dual="auto", random_state=semilla, max_iter=6000)
            modelo.fit(x_fit, y_fit)
            scores = np.abs(modelo.coef_).mean(axis=0)
        else:
            raise ValueError(f"Método no registrado: {metodo}")
    except Exception as exc:  # noqa: BLE001
        status = "failed"
        warning = repr(exc)
        scores = np.full(len(features), np.nan)
    elapsed = time.perf_counter() - inicio
    valores = k_values if k_values is not None else [int(k or min(10, len(features)))]
    ranking = ranking_desde_scores(dataset, metodo, familia, semilla, valores, features, scores, elapsed, sample_info["sample_size"], status)
    log = {
        "timestamp": marca_temporal(),
        "dataset": dataset,
        "method": metodo,
        "seed": semilla,
        "elapsed_seconds": elapsed,
        "sample_size": sample_info["sample_size"],
        "sample_applied": sample_info["sample_applied"],
        "status": status,
        "warning": warning,
    }
    return ranking, log, pd.DataFrame()


def calcular_jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else np.nan


def permutar_target(y: pd.Series, semilla: int) -> pd.Series:
    rng = np.random.default_rng(semilla)
    return pd.Series(rng.permutation(y.to_numpy()))


def configurar_estilo() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.facecolor": "#fbfaf7",
            "axes.facecolor": "#fbfaf7",
            "axes.edgecolor": "#d8d1c7",
            "axes.labelcolor": "#2f2f2f",
            "xtick.color": "#2f2f2f",
            "ytick.color": "#2f2f2f",
            "font.size": 10,
            "axes.titleweight": "bold",
            "savefig.bbox": "tight",
        }
    )


def guardar_figura(fig: plt.Figure, ruta_png: Path) -> Path:
    ruta_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_png, dpi=300)
    fig.savefig(ruta_png.with_suffix(".pdf"))
    plt.close(fig)
    return ruta_png


def calcular_estabilidad(rankings: pd.DataFrame) -> pd.DataFrame:
    filas = []
    base = rankings[(rankings["status"].eq("ok")) & (rankings["method"].ne("boruta"))]
    for (dataset, method, k), grupo in base.groupby(["dataset", "method", "k"]):
        seeds = sorted(grupo["seed"].unique())
        for i, seed_a in enumerate(seeds):
            set_a = set(grupo[(grupo["seed"].eq(seed_a)) & (grupo["selected"])]["feature"])
            for seed_b in seeds[i + 1 :]:
                set_b = set(grupo[(grupo["seed"].eq(seed_b)) & (grupo["selected"])]["feature"])
                filas.append({"dataset": dataset, "method": method, "k": k, "seed_a": seed_a, "seed_b": seed_b, "jaccard": calcular_jaccard(set_a, set_b)})
    return pd.DataFrame(filas)


def resumen_redundancia(x: pd.DataFrame, features: list[str]) -> dict[str, Any]:
    if len(features) <= 1:
        return {"mean_abs_corr": 0.0, "max_abs_corr": 0.0, "high_corr_pairs": 0, "n_features": len(features)}
    corr = x[features].corr(method="spearman").abs()
    valores = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack()
    return {
        "mean_abs_corr": float(valores.mean()) if len(valores) else 0.0,
        "max_abs_corr": float(valores.max()) if len(valores) else 0.0,
        "high_corr_pairs": int((valores >= 0.85).sum()) if len(valores) else 0,
        "n_features": len(features),
    }


def calcular_redundancia_interna(bundles: dict[str, DatasetBundle], rankings: pd.DataFrame) -> pd.DataFrame:
    filas = []
    base = rankings[(rankings["seed"].eq(RANDOM_STATE)) & (rankings["status"].eq("ok"))]
    for dataset, bundle in bundles.items():
        full = resumen_redundancia(bundle.x_train, list(bundle.x_train.columns))
        for (method, k), grupo in base[base["dataset"].eq(dataset)].groupby(["method", "k"]):
            features = grupo[grupo["selected"]].sort_values("rank")["feature"].tolist()
            selected = resumen_redundancia(bundle.x_train, features)
            filas.append(
                {
                    "dataset": dataset,
                    "method": method,
                    "k": k,
                    "full_mean_abs_corr": full["mean_abs_corr"],
                    "selected_mean_abs_corr": selected["mean_abs_corr"],
                    "delta_mean_abs_corr": selected["mean_abs_corr"] - full["mean_abs_corr"],
                    "selected_max_abs_corr": selected["max_abs_corr"],
                    "selected_high_corr_pairs": selected["high_corr_pairs"],
                    "n_selected_features": selected["n_features"],
                }
            )
    return pd.DataFrame(filas)


def ejecutar_permutaciones(
    bundle: DatasetBundle,
    metodo: str,
    familia: str,
    k: int,
    n_permutations: int = N_PERMUTACIONES,
) -> pd.DataFrame:
    real, _, _ = ejecutar_selector(metodo, bundle.x_train, bundle.y_train, k, RANDOM_STATE, bundle.dataset, familia, [k])
    real_top = real[(real["selected"]) & (real["status"].eq("ok"))].drop_duplicates("feature")
    filas = []
    for _, row in real_top.iterrows():
        nulos = []
        for perm_id in range(n_permutations):
            y_perm = permutar_target(bundle.y_train, RANDOM_STATE + perm_id + 1)
            perm, _, _ = ejecutar_selector(metodo, bundle.x_train, y_perm, k, RANDOM_STATE + perm_id + 1, bundle.dataset, familia, [k])
            match = perm[perm["feature"].eq(row["feature"])]
            if not match.empty:
                nulos.append(float(match["score"].iloc[0]))
        nulos = np.asarray(nulos, dtype=float)
        nulos = nulos[np.isfinite(nulos)]
        p95 = float(np.percentile(nulos, 95)) if len(nulos) else np.nan
        p_emp = (1 + np.sum(nulos >= row["score"])) / (len(nulos) + 1) if len(nulos) else np.nan
        filas.append(
            {
                "dataset": bundle.dataset,
                "method": metodo,
                "feature": row["feature"],
                "real_score": row["score"],
                "null_p95": p95,
                "empirical_p_value": p_emp,
                "above_null_p95": bool(np.isfinite(p95) and row["score"] > p95),
                "n_permutations": n_permutations,
            }
        )
    return pd.DataFrame(filas)


def guardar_tablas_granulares(rankings: pd.DataFrame, boruta_natural: pd.DataFrame) -> pd.DataFrame:
    base_dir = TABLE_DIR / "granular"
    rows = []
    for (dataset, method, k), grupo in rankings.groupby(["dataset", "method", "k"], sort=True):
        local_dir = base_dir / dataset / method
        local_dir.mkdir(parents=True, exist_ok=True)
        nombre = f"k_{int(k)}.csv"
        ruta = local_dir / nombre
        grupo.sort_values(["seed", "rank", "feature"]).to_csv(ruta, index=False)
        seleccionadas = grupo[grupo["selected"]].sort_values(["seed", "rank", "feature"])
        ruta_sel = local_dir / f"k_{int(k)}_seleccionadas.csv"
        seleccionadas.to_csv(ruta_sel, index=False)
        rows.append({"dataset": dataset, "method": method, "k": int(k), "ranking_table": str(ruta), "selected_table": str(ruta_sel), "rows": len(grupo)})
    if not boruta_natural.empty:
        guardar_csv(boruta_natural, "fs_boruta_confirmed_sets.csv")
    return pd.DataFrame(rows)


def vista_pivot_seleccion(rankings: pd.DataFrame) -> pd.DataFrame:
    base = rankings[(rankings["seed"].eq(RANDOM_STATE)) & (rankings["selected"]) & (rankings["status"].eq("ok"))]
    pivot = (
        base.groupby(["dataset", "method", "k"], as_index=False)
        .agg(variables=("feature", lambda valores: ", ".join(map(str, valores))))
        .pivot_table(index=["dataset", "method"], columns="k", values="variables", aggfunc="first", fill_value="")
        .reset_index()
    )
    pivot.columns = [f"k_{col}" if isinstance(col, int) else str(col) for col in pivot.columns]
    return pivot


def guardar_datasets_reducidos(bundles: dict[str, DatasetBundle], rankings: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base = rankings[(rankings["seed"].eq(RANDOM_STATE)) & (rankings["selected"]) & (rankings["status"].eq("ok"))]
    for dataset, bundle in bundles.items():
        for (method, k), grupo in base[base["dataset"].eq(dataset)].groupby(["method", "k"]):
            features = grupo.sort_values("rank")["feature"].tolist()
            salida = SELECTED_DIR / dataset / method / f"k_{int(k)}"
            salida.mkdir(parents=True, exist_ok=True)
            bundle.x_train[features].to_csv(salida / "X_train_selected.csv", index=False)
            bundle.x_validation[features].to_csv(salida / "X_validation_selected.csv", index=False)
            bundle.x_validation[features].to_csv(salida / "X_val_selected.csv", index=False)
            bundle.x_test[features].to_csv(salida / "X_test_selected.csv", index=False)
            pd.DataFrame({"feature": features, "rank": range(1, len(features) + 1)}).to_csv(salida / "selected_features.csv", index=False)
            rows.append({"dataset": dataset, "method": method, "k": int(k), "n_features": len(features), "path": str(salida)})
    return pd.DataFrame(rows)


def materializar_matrices_qfs(bundle: DatasetBundle) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    discretization = discretizar_matriz_train(bundle.x_train, RANDOM_STATE)
    vector = calcular_mi_relevancia(bundle.x_train, bundle.y_train, RANDOM_STATE).rename_axis("feature").reset_index()
    vector.insert(0, "dataset", bundle.dataset)
    matriz = calcular_mi_pares(bundle.x_train, RANDOM_STATE)
    matriz_csv = matriz.copy()
    matriz_csv.insert(0, "feature", matriz_csv.index)
    vector_path = guardar_csv(vector, f"fs_qfs_mi_target_vector__{bundle.dataset}.csv")
    matrix_path = guardar_csv(matriz_csv, f"fs_qfs_pairwise_mi_matrix__{bundle.dataset}.csv")
    resumen = pd.DataFrame(
        [
            {
                "dataset": bundle.dataset,
                "n_features": bundle.x_train.shape[1],
                "mi_target_vector_table": str(vector_path),
                "pairwise_mi_matrix_table": str(matrix_path),
                "mean_I_i": float(vector["I_i"].mean()),
                "max_I_i": float(vector["I_i"].max()),
                "mean_R_ij_offdiag": float(matriz.where(~np.eye(len(matriz), dtype=bool)).stack().mean()),
                "max_R_ij_offdiag": float(matriz.where(~np.eye(len(matriz), dtype=bool)).stack().max()),
                "n_continuous_binned": len(discretization.continuous_columns),
                "n_discrete_kept": len(discretization.discrete_columns),
                "mi_bins": discretization.n_bins,
                "mi_strategy": discretization.strategy,
                "normalization_note": discretization.normalization_note,
            }
        ]
    )
    return resumen, vector, matriz_csv


def plot_estabilidad(jaccard: pd.DataFrame) -> Path:
    tabla = jaccard.groupby(["dataset", "method"])["jaccard"].mean().unstack()
    fig, ax = plt.subplots(figsize=(12, 4.8))
    sns.heatmap(tabla, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1, linewidths=0.5, linecolor="#ffffff", ax=ax)
    ax.set_title("La estabilidad por semillas separa métodos deterministas y métodos sensibles al ajuste")
    ax.set_xlabel("")
    ax.set_ylabel("")
    return guardar_figura(fig, FIGURE_DIR / "stability" / "fs_stability_jaccard_heatmap.png")


def plot_permutaciones(summary: pd.DataFrame) -> Path:
    tabla = summary.pivot_table(index="dataset", columns="method", values="n_features_above_null", aggfunc="mean", fill_value=0)
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    sns.heatmap(tabla, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, linecolor="#ffffff", ax=ax)
    ax.set_title("Las permutaciones distinguen señal real de rankings inducidos por azar")
    ax.set_xlabel("")
    ax.set_ylabel("")
    return guardar_figura(fig, FIGURE_DIR / "permutation" / "fs_permutation_above_null_heatmap.png")


def plot_redundancia(redundancia: pd.DataFrame) -> Path:
    base = redundancia[redundancia["method"].ne("boruta")].copy()
    fig, ax = plt.subplots(figsize=(12, 5.2))
    sns.stripplot(data=base, x="delta_mean_abs_corr", y="method", hue="dataset", dodge=True, size=5, ax=ax)
    ax.axvline(0, color="#333333", linewidth=1)
    ax.set_title("El control de redundancia se observa como desplazamiento frente al espacio completo")
    ax.set_xlabel("Cambio de correlación absoluta media")
    ax.set_ylabel("")
    ax.legend(title="", bbox_to_anchor=(1.02, 1), loc="upper left")
    return guardar_figura(fig, FIGURE_DIR / "redundancy" / "fs_redundancy_delta.png")


def plot_roster_dataset(rankings: pd.DataFrame, dataset: str) -> Path:
    base = rankings[(rankings["dataset"].eq(dataset)) & (rankings["seed"].eq(RANDOM_STATE)) & (rankings["selected"]) & (rankings["status"].eq("ok"))]
    frecuencia = base.groupby("method", as_index=False).agg(n_variables=("feature", "nunique"), score_mediano=("score", "median"))
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    sns.barplot(data=frecuencia, y="method", x="n_variables", color="#5f8f8b", ax=ax)
    ax.set_title(f"{dataset}: Boruta fija su tamaño y el resto sigue la escalera de k")
    ax.set_xlabel("Variables únicas seleccionadas en la lectura principal")
    ax.set_ylabel("")
    return guardar_figura(fig, FIGURE_DIR / "roster_by_dataset" / f"{dataset}_roster_comparison.png")


def plot_heatmap_metodo_feature(rankings: pd.DataFrame, dataset: str) -> Path:
    base = rankings[(rankings["dataset"].eq(dataset)) & (rankings["seed"].eq(RANDOM_STATE)) & (rankings["selected"]) & (rankings["status"].eq("ok"))]
    top = base["feature"].value_counts().head(18).index
    matriz = base[base["feature"].isin(top)].assign(valor=1).pivot_table(index="method", columns="feature", values="valor", aggfunc="max", fill_value=0)
    fig, ax = plt.subplots(figsize=(min(13, 4 + 0.42 * len(top)), 5.0))
    sns.heatmap(matriz, cmap=["#f0ece3", "#b65f50"], cbar=False, linewidths=0.45, linecolor="#ffffff", ax=ax)
    ax.set_title(f"{dataset}: coincidencias método-variable en el k de referencia")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=45)
    return guardar_figura(fig, FIGURE_DIR / "method_feature_heatmaps" / f"{dataset}_method_feature_heatmap.png")


def registrar_decisiones_figuras(figuras: list[dict[str, Any]]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = REPORT_DIR / "figure_decisions.md"
    figuras_unicas: dict[str, dict[str, Any]] = {}
    for figura in figuras:
        figuras_unicas.setdefault(str(figura["family_id"]), figura)
    bloques = [
        "# Decisiones de visualización\n",
        "## Fase 5: familias añadidas o reutilizadas\n",
    ]
    for figura in figuras_unicas.values():
        bloques.append(
            "\n".join(
                [
                    f"### {figura['family_id']}",
                    f"- Tier: {figura['tier']}",
                    f"- Pregunta: {figura['question']}",
                    f"- Familia: {figura['visual_family']}",
                    f"- Decisión: {figura['decision']}",
                    f"- Ruta PNG: {figura['png_path']}",
                    f"- Ruta PDF: {Path(figura['png_path']).with_suffix('.pdf')}",
                    "",
                ]
            )
        )
    texto = "\n".join(bloques)
    if ruta.exists():
        previo = ruta.read_text(encoding="utf-8")
        if "## Fase 5: familias añadidas o reutilizadas" in previo:
            previo = previo.split("## Fase 5: familias añadidas o reutilizadas")[0].rstrip()
        ruta.write_text(previo + "\n\n" + texto, encoding="utf-8")
    else:
        ruta.write_text(texto, encoding="utf-8")
    return ruta
