# ================================================================
# Data_functions.py — Annotated Version
# ------------------------------------------------
# This file preserves the original code exactly. Only comments were
# added/translated and short docstrings were inserted at the start of
# each function to explain its purpose and returns.
# ================================================================

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

    #Prepare features/labels and split into train/test sets.

    #Args:
    #df (pd.DataFrame): Input dataframe with features and target.
    #target (str): Name of the target column.
    #test_size (float): Fraction of data to allocate to the test set.
    #random_state (int): Seed for reproducible split.
    #stratify (bool): If True, stratify by the target distribution.
    #encode_objects (bool): If True, label-encode object/category columns.

    #Returns:
    #Tuple[pd.DataFrame, pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray, list]:
    #X (full feature df), X_train, y_train, X_test, y_test, feature_names.\"\"\"

    df = df.copy()

    # Encode object/category columns minimally if requested
    if encode_objects:
        for col in df.select_dtypes(include=["object", "category"]).columns:
            le = LabelEncoder()
    # Encode labels for estimators requiring numeric classes
            df[col] = le.fit_transform(df[col].astype(str))

    feature_names = [c for c in df.columns if c != target]
    # Exclude target column from feature list
    X = df[feature_names]
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(
        # Stratified split if requested for class balance
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
    #Compute feature relevance to target and feature-to-feature redundancy.

    #Args:
    #X_df (pd.DataFrame): Feature dataframe.
    #y (np.ndarray): Target vector.
    #n_bins (int): Number of discretization bins for KBinsDiscretizer.
    #random_state (int): Seed for deterministic MI estimation.

    #Returns:
    #Tuple[np.ndarray, np.ndarray, pd.DataFrame, list]:
    #MI_x_y, R (redundancy matrix), mi_df (sorted by MI), feature_names.

    X_df = X_df.copy()
    feature_names = list(X_df.columns)

    # Ensure numeric dtype for all columns (may be redundant if preprocessed)
    for col in X_df.columns:
        if X_df[col].dtype == "object":
            X_df[col] = X_df[col].astype("category").cat.codes

    # Light discretization for all features to homogenize types
    discretizer = KBinsDiscretizer(n_bins=n_bins, encode="ordinal", strategy="uniform")
    # Ordinal-encode bins to integers for MI/NMI
    X_disc = discretizer.fit_transform(X_df.values)
    X_disc = np.asarray(X_disc, dtype=int)  # para NMI necesitamos enteros/categorías

    # Feature relevance with respect to the target (MI)
    MI_x_y = mutual_info_classif(
        # Mutual information per feature with the target
        X_disc, y,
        discrete_features=True,
        random_state=random_state
    )

    # Feature redundancy: pairwise symmetric normalized mutual information (NMI)
    n = X_disc.shape[1]
    R = np.eye(n, dtype=float)
    # Start with identity; we'll fill upper triangle and mirror
    for i in range(n):
        xi = X_disc[:, i]
        for j in range(i + 1, n):
            xj = X_disc[:, j]
            nmi = normalized_mutual_info_score(xi, xj, average_method="arithmetic")
            R[i, j] = nmi
            R[j, i] = nmi

    # Importance DataFrame sorted by MI
    mi_df = pd.DataFrame({
        "Feature": feature_names,
        "MutualInformation": MI_x_y
    }).sort_values("MutualInformation", ascending=False).reset_index(drop=True)

    return MI_x_y, R, mi_df, feature_names
    
def Boruta_selection(X_train, y_train):

    #Run Boruta feature selection using an XGBoost base estimator.

    #Args:
    #X_train (pd.DataFrame): Training features.
    #y_train (pd.Series or np.ndarray): Training labels.

    #Returns:
    #list: Names of the features selected by Boruta

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
    #Train an XGBoost model and sort features by model-derived importance.

    #Args:
    #X_train (pd.DataFrame): Training features.
    #y_train (pd.Series or np.ndarray): Training labels.

    #Returns:
    #Tuple[pd.DataFrame, list]:
    #importance_df (feature, importance), and ordered feature list (descending).

    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    
    # Fit XGBoost model
    model = XGBClassifier(eval_metric='logloss', random_state=42)
    model.fit(X_train, y_train_encoded)
    
    # Extract model-derived feature importances
    importances = model.feature_importances_
    importance_df = pd.DataFrame({'Feature': X_train.columns, 'Importance': importances})
    # Map feature names to their importance
    importance_df = importance_df.sort_values(by='Importance', ascending=False)
    Imp_features_rank = list(importance_df['Feature'])
    
    return importance_df, Imp_features_rank


def MI_complete_det(X_df, y_target, threshold=0.001, random_state=42):
    #Deterministic MI pipeline: discretize continuous columns, filter by MI with target,
    #    then recompute MI(x;y) and MI(x;x), and min-max normalize.

    #Args:
    #X_df (pd.DataFrame): Input features dataframe (mixed types allowed).
    #y_target (np.ndarray): Target labels.
    #threshold (float): Minimum MI(x;y) to retain features initially.
    #random_state (int): Seed for deterministic discretization and MI.

    #Returns:
    #Tuple[np.ndarray, np.ndarray, pd.DataFrame, np.ndarray]:
    #MI_x_y_final, MI_x_x_final (matrix), mi_df_final, final_features.

    # Step 1: Identify discrete and continuous columns
    discrete_cols = [col for col in X_df.columns if X_df[col].dtype == 'object' or X_df[col].nunique() <= 10]
    continuous_cols = [col for col in X_df.columns if X_df[col].dtype in ['int64', 'float64'] and X_df[col].nunique() > 10]

    # Step 2: Discretize continuous columns
    df_discretized = X_df[discrete_cols].copy()
    discretizer = KBinsDiscretizer(
        # Consistent binning across continuous columns
        n_bins=5,
        encode='ordinal',
        strategy='uniform',
        subsample=200_000,
        random_state=random_state  # <- Ensures deterministic discretization
    )

    for col in continuous_cols:
        binned_col = pd.DataFrame(
            discretizer.fit_transform(X_df[[col]]),
            columns=[col],
            index=X_df.index
        )
        df_discretized = pd.concat([df_discretized, binned_col], axis=1)

    # Step 3: Compute initial MI(x;y)
    MI_x_y = mutual_info_classif(
        df_discretized,
        y_target,
        discrete_features='auto',
        random_state=random_state  # <- Ensures deterministic MI computation
    )

    feature_names = df_discretized.columns
    mi_df = pd.DataFrame({'Feature': feature_names, 'Mutual Information': MI_x_y})

    # Filter features with MI(x;y) > threshold
    selected_features = mi_df[mi_df['Mutual Information'] > threshold]['Feature'].values
    X_df_red = df_discretized[selected_features]

    # Step 4: Recompute MI(x;y) and MI(x;x) with filtered features
    MI_x_y_final = mutual_info_classif(
        X_df_red,
        y_target,
        discrete_features='auto',
        random_state=random_state
    )

    MI_x_x_final = calculate_mutual_info_matrix(X_df_red)

    # Step 5: Min-max normalization using MI_xx range
    min_w = np.min(MI_x_x_final)
    max_w = np.max(MI_x_x_final) 

    MI_x_y_final = normalizar_max_min(weights=MI_x_y_final, min=min_w, max=max_w)
    MI_x_x_final = normalizar_max_min(weights=MI_x_x_final, min=min_w, max=max_w)

    # Step 6: Build final DataFrame keeping MI > 0
    mi_df_final = pd.DataFrame({'Feature': X_df_red.columns, 'Mutual Information': MI_x_y_final})
    mi_df_final = mi_df_final[mi_df_final['Mutual Information'] > 0].reset_index(drop=True)

    # Update matrix and feature names based on final selection
    final_features = mi_df_final['Feature'].values
    X_df_red = X_df_red[final_features]
    MI_x_y_final = mi_df_final['Mutual Information'].values
    MI_x_x_final = calculate_mutual_info_matrix(X_df_red)

    return MI_x_y_final, MI_x_x_final, mi_df_final, final_features



def calculate_mutual_info_matrix(X):

    #Compute a symmetric matrix of mutual information between all pairs of features.

    #Args:
    #X (pd.DataFrame): Discrete-coded feature dataframe.

    #Returns:
    #np.ndarray: Symmetric matrix MI[i, j] = MI(X_i, X_j); zeros on diagonal.

    n_features = X.shape[1]
    mi_matrix = np.zeros((n_features, n_features))

    for i in range(n_features):
        # Iterate over feature pairs (i, j)
        for j in range(i, n_features):
            if i == j:
                mi_matrix[i, j] = 0  # Zero diagonal by definition
            else:
                # Compute mutual information between features
                mi = mutual_info_classif(X.iloc[:, [i]], X.iloc[:, j], discrete_features='auto')
                
                # Ensure a scalar value (not a 1-element array)
                mi = mi.item() if hasattr(mi, 'item') else mi
                
                # Assign MI to the symmetric matrix entries
                mi_matrix[i, j] = mi
                mi_matrix[j, i] = mi  # Matriz simétrica

    return mi_matrix


def normalizar_max_min(weights, min = 0, max = 1):
    #Min-max normalize an array-like set of weights to the [min, max] range provided.

    #Args:
    #weights (array-like): Values to normalize.
    #min (float): Lower bound used for normalization.
    #max (float): Upper bound used for normalization.

    #Returns:
    #np.ndarray: Normalized weights.

    weights_normalizados = (weights - min) / (max - min)
    
    return weights_normalizados












