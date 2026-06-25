import numpy as np
import numpy.typing as npt
import pandas as pd
import pickle
import time
import itertools
from collections import Counter

import matplotlib.pyplot as plt
import matplotlib.pylab as plt
import matplotlib.cm as cm
import seaborn as sns


from tqdm import tqdm

from sklearn.feature_selection import (mutual_info_classif, chi2, SequentialFeatureSelector)
from sklearn.preprocessing import (LabelEncoder, MinMaxScaler, StandardScaler, KBinsDiscretizer)
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import (roc_auc_score, accuracy_score, precision_recall_curve, roc_curve, 
                             f1_score, confusion_matrix, classification_report, normalized_mutual_info_score)
from sklearn.ensemble import RandomForestClassifier
from sklearn.manifold import MDS

import gurobipy as gp
from gurobipy import GRB

#import shap
from boruta import BorutaPy
from sklearn.inspection import permutation_importance
import xgboost as xgb
from xgboost import XGBClassifier

import importlib
import Data_functions


def prepare_train_test_simple(df: pd.DataFrame,
                              target: str = "Recurrence",
                              test_size: float = 0.15,
                              random_state: int = 42,
                              stratify: bool = True,
                              encode_objects: bool = True):

    df = df.copy()

    # Codificar objetos si procede (mínimo imprescindible)
    if encode_objects:
        for col in df.select_dtypes(include=["object", "category"]).columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))

    feature_names = [c for c in df.columns if c != target]
    X = df[feature_names]
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y if stratify else None
    )

    return X, X_train, y_train, X_test, y_test, feature_names

def compute_importance_and_redundancy_simple(X_df: pd.DataFrame,
                                             y: np.ndarray,
                                             n_bins: int = 5,
                                             random_state: int = 42):
    X_df = X_df.copy()
    feature_names = list(X_df.columns)

    # Asegurar numérico (si te llega todo preprocesado, esto ya es innecesario)
    for col in X_df.columns:
        if X_df[col].dtype == "object":
            X_df[col] = X_df[col].astype("category").cat.codes

    # Discretización ligera para todo (homogeneiza tipo)
    discretizer = KBinsDiscretizer(n_bins=n_bins, encode="ordinal", strategy="uniform")
    X_disc = discretizer.fit_transform(X_df.values)
    X_disc = np.asarray(X_disc, dtype=int)  # para NMI necesitamos enteros/categorías

    # Importancia respecto al target
    MI_x_y = mutual_info_classif(
        X_disc, y,
        discrete_features=True,
        random_state=random_state
    )

    # Redundancia entre features: NMI simétrica
    n = X_disc.shape[1]
    R = np.eye(n, dtype=float)
    for i in range(n):
        xi = X_disc[:, i]
        for j in range(i + 1, n):
            xj = X_disc[:, j]
            nmi = normalized_mutual_info_score(xi, xj, average_method="arithmetic")
            R[i, j] = nmi
            R[j, i] = nmi

    # DataFrame de importancia
    mi_df = pd.DataFrame({
        "Feature": feature_names,
        "MutualInformation": MI_x_y
    }).sort_values("MutualInformation", ascending=False).reset_index(drop=True)

    return MI_x_y, R, mi_df, feature_names
    
def Boruta_selection(X_train, y_train):

    xgb = XGBClassifier(eval_metric='logloss', random_state=42)
    
    boruta_selector = BorutaPy(
        xgb, 
        n_estimators='auto',  
        perc=75,             
        random_state=42
    )
        
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    
    boruta_selector.fit(X_train, y_train_encoded)

    selected_features = X_train.columns[boruta_selector.support_].tolist()
    rejected_features = X_train.columns[~boruta_selector.support_].tolist()
    
    print(f"Boruta's Selected Features: {selected_features}")
    print(f"Boruta's Rejected Features: {rejected_features}")

    return selected_features


def Importance_selection(X_train, y_train):
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    
    # Entrenar modelo
    model = XGBClassifier(eval_metric='logloss', random_state=42)
    model.fit(X_train, y_train_encoded)
    
    # Extraer importancias
    importances = model.feature_importances_
    importance_df = pd.DataFrame({'Feature': X_train.columns, 'Importance': importances})
    importance_df = importance_df.sort_values(by='Importance', ascending=False)
    Imp_features_rank = list(importance_df['Feature'])
    
    return importance_df, Imp_features_rank


def MI_complete_det(X_df, y_target, threshold=0.001, random_state=42):
    # Paso 1: Identificar columnas discretas y continuas
    discrete_cols = [col for col in X_df.columns if X_df[col].dtype == 'object' or X_df[col].nunique() <= 10]
    continuous_cols = [col for col in X_df.columns if X_df[col].dtype in ['int64', 'float64'] and X_df[col].nunique() > 10]

    # Paso 2: Discretizar columnas continuas
    df_discretized = X_df[discrete_cols].copy()
    discretizer = KBinsDiscretizer(
        n_bins=5,
        encode='ordinal',
        strategy='uniform',
        subsample=200_000,
        random_state=random_state  # <- Asegura discretización determinista
    )

    for col in continuous_cols:
        binned_col = pd.DataFrame(
            discretizer.fit_transform(X_df[[col]]),
            columns=[col],
            index=X_df.index
        )
        df_discretized = pd.concat([df_discretized, binned_col], axis=1)

    # Paso 3: Calcular MI(x,y) inicial
    MI_x_y = mutual_info_classif(
        df_discretized,
        y_target,
        discrete_features='auto',
        random_state=random_state  # <- Asegura cálculo MI determinista
    )

    feature_names = df_discretized.columns
    mi_df = pd.DataFrame({'Feature': feature_names, 'Mutual Information': MI_x_y})

    # Filtrar características con MI(x,y) > threshold
    selected_features = mi_df[mi_df['Mutual Information'] > threshold]['Feature'].values
    X_df_red = df_discretized[selected_features]

    # Paso 4: Recalcular MI(x,y) y MI(x,x) con características filtradas
    MI_x_y_final = mutual_info_classif(
        X_df_red,
        y_target,
        discrete_features='auto',
        random_state=random_state
    )

    MI_x_x_final = calculate_mutual_info_matrix(X_df_red)

    # Paso 5: Normalización según MI_xx
    min_w = np.min(MI_x_x_final)
    max_w = np.max(MI_x_x_final) 

    MI_x_y_final = normalizar_max_min(weights=MI_x_y_final, min=min_w, max=max_w)
    MI_x_x_final = normalizar_max_min(weights=MI_x_x_final, min=min_w, max=max_w)

    # Paso 6: Crear DataFrame final con MI > 0
    mi_df_final = pd.DataFrame({'Feature': X_df_red.columns, 'Mutual Information': MI_x_y_final})
    mi_df_final = mi_df_final[mi_df_final['Mutual Information'] > 0].reset_index(drop=True)

    # Actualizar matriz y nombres de features
    final_features = mi_df_final['Feature'].values
    X_df_red = X_df_red[final_features]
    MI_x_y_final = mi_df_final['Mutual Information'].values
    MI_x_x_final = calculate_mutual_info_matrix(X_df_red)

    return MI_x_y_final, MI_x_x_final, mi_df_final, final_features



def calculate_mutual_info_matrix(X):

    n_features = X.shape[1]
    mi_matrix = np.zeros((n_features, n_features))

    for i in range(n_features):
        for j in range(i, n_features):
            if i == j:
                mi_matrix[i, j] = 0  # La diagonal es 0
            else:
                # Calcular la información mutua
                mi = mutual_info_classif(X.iloc[:, [i]], X.iloc[:, j], discrete_features='auto')
                
                # Asegúrate de extraer el escalar del array
                mi = mi.item() if hasattr(mi, 'item') else mi
                
                # Asignar el valor a la matriz de información mutua
                mi_matrix[i, j] = mi
                mi_matrix[j, i] = mi  # Matriz simétrica

    return mi_matrix


def normalizar_max_min(weights, min = 0, max = 1):
    # Normalización usando la fórmula min-max
    weights_normalizados = (weights - min) / (max - min)
    
    return weights_normalizados












