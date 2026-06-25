# ================================================================
# Prediction_and_results.py — Annotated Version
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
import os
import ast

from tqdm import tqdm

from sklearn.feature_selection import (mutual_info_classif, chi2, SequentialFeatureSelector)
from sklearn.preprocessing import (LabelEncoder, MinMaxScaler, StandardScaler, KBinsDiscretizer)
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import (roc_auc_score, accuracy_score, precision_recall_curve, roc_curve, 
                             f1_score, confusion_matrix, classification_report, normalized_mutual_info_score, 
                                roc_auc_score, precision_score, recall_score)
from sklearn.ensemble import RandomForestClassifier
from sklearn.manifold import MDS

import gurobipy as gp
from gurobipy import GRB

from boruta import BorutaPy
from sklearn.inspection import permutation_importance
import xgboost as xgb
from xgboost import XGBClassifier

import importlib


def sort_by_rydberg_dens(avg_density, feature_names):

    sorted_pairs = sorted(zip(avg_density, feature_names), reverse=True)
    
    sorted_avg_density, sorted_features = zip(*sorted_pairs)
    
    sorted_avg_density = list(sorted_avg_density)
    sorted_features = list(sorted_features)
    return sorted_features


# XGBoost (optional)
try:
    from xgboost import XGBClassifier
    _HAS_XGB = True
except Exception:
    _HAS_XGB = False

from sklearn.ensemble import RandomForestClassifier

# Successive Halving (if available)
try:
    from sklearn.experimental import enable_halving_search_cv  # noqa: F401
    from sklearn.model_selection import HalvingRandomSearchCV
    _HAS_HALVING = True
except Exception:
    _HAS_HALVING = False


def AUC_from_features(
    X_df_train, X_df_test, y_train, y_test, features,
    model: str = 'xgb',        # 'xgb' o 'rf'
    speed_up: bool = True,     # acelera RF con Halving si está disponible
    cv_rf: int = 3,            # folds para RF cuando buscamos velocidad
    n_iter_xgb: int = 50,
    n_iter_rf: int = 25,
    min_resources_rf: int = 100,
    max_resources_rf: int = 400
):
    #Evaluate model performance using only the provided features. For each of 5 seeds,
    #run hyperparameter search (XGBoost or RandomForest), take the top-5 CV candidates,
    #re-fit on train, and score on test. Returns per-seed/per-top configuration metrics.

    #Args:
    #X_df_train (pd.DataFrame): Training features.
    #X_df_test (pd.DataFrame): Test features.
    #y_train (array-like): Training labels.
    #y_test (array-like): Test labels.
    #features (list): Feature subset to use.
    #model (str): 'xgb' or 'rf' (default 'xgb').
    #speed_up (bool): Use Halving for RF if available.
    #cv_rf (int): CV folds for RF (fast mode).
    #n_iter_xgb (int): RandomizedSearch iterations for XGB.
    #n_iter_rf (int): RandomizedSearch iterations for RF fallback.
   # min_resources_rf (int): Min trees for Halving RF.
    #max_resources_rf (int): Max trees for Halving RF.

    #Returns:
    #Tuple[list, list, list, list]:
    #all_AUC, all_auc_values_cv, all_precision, all_recall.\"\"\"

   # """
    #NOTE: Returns the same outputs as the original function:
   # all_AUC, all_auc_values_cv, all_precision, all_recall.
   # """

    random_states=[0, 1, 2, 3, 4]

    if model not in ('xgb', 'rf'):
        raise ValueError("Parámetro 'model' debe ser 'xgb' o 'rf'.")
    if model == 'xgb' and not _HAS_XGB:
        raise ImportError("xgboost no está disponible. Instálalo o usa model='rf'.")

    all_AUC, all_auc_values_cv, all_precision, all_recall = [], [], [], []

    # Escalado para mantener el flujo original
    scaler = StandardScaler()
    # Standardize features before model fitting
    X_train = scaler.fit_transform(X_df_train[features])
    # Fit on train, transform train
    X_test = scaler.transform(X_df_test[features])
    # Transform test with the same scaler

    for seed in random_states:
        AUC, precision, recall, auc_values_cv = [], [], [], []

        if model == 'xgb':
            base_estimator = XGBClassifier(
                eval_metric='logloss',
                random_state=seed
            )
            param_dist = {
                'n_estimators': [100, 200, 300, 500],
                'learning_rate': [0.01, 0.05, 0.1, 0.2],
                'max_depth': [3, 5, 7, 10],
                'subsample': [0.6, 0.8, 1.0],
                'colsample_bytree': [0.6, 0.8, 1.0],
                'gamma': [0, 0.1, 0.5, 1],
                'min_child_weight': [1, 5, 10],
            }

            search = RandomizedSearchCV(  # hyperparameter search

                estimator=base_estimator,
                param_distributions=param_dist,
                n_iter=n_iter_xgb,
                scoring='roc_auc',
                cv=5,
                verbose=0,
                random_state=seed,
                n_jobs=-1
            )

        else:  # model == 'rf'
            base_estimator = RandomForestClassifier(random_state=seed)

            # Espacio de búsqueda "rápido" (sin n_estimators cuando usamos Halving)
            rf_param_dist_fast = {
                # OJO: sin 'n_estimators' si usamos Halving con resource='n_estimators'
                'max_depth': [None, 12, 20],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2],
                'max_features': ['sqrt', 0.5],
                'bootstrap': [True],
                'class_weight': [None, 'balanced_subsample'],
                'max_samples': [None, 0.8, 0.6],  # si tu sklearn no lo soporta, lo filtramos abajo
            }

            # Filtrar claves no soportadas por la versión de sklearn instalada
            supported = base_estimator.get_params().keys()
            rf_param_dist_fast = {k: v for k, v in rf_param_dist_fast.items() if k in supported}

            if speed_up and _HAS_HALVING:
                # Successive Halving (NO incluir n_estimators en param_dist)
                search = HalvingRandomSearchCV(  # faster RF via successive halving

                    estimator=base_estimator,
                    param_distributions=rf_param_dist_fast,
                    resource='n_estimators',
                    min_resources=min_resources_rf,
                    max_resources=max_resources_rf,
                    factor=3,
                    scoring='roc_auc',
                    cv=cv_rf,
                    random_state=seed,
                    n_jobs=-1,
                    verbose=0
                )
            else:
                # Fallback: RandomizedSearchCV (aquí sí podemos buscar n_estimators)
                rf_param_dist_fallback = {
                    'n_estimators': [100, 200, 300, 400],
                    **rf_param_dist_fast
                }
                # Filtrado por si alguna clave no existe
                rf_param_dist_fallback = {k: v for k, v in rf_param_dist_fallback.items() if k in supported}

                search = RandomizedSearchCV(
                    estimator=base_estimator,
                    param_distributions=rf_param_dist_fallback,
                    n_iter=n_iter_rf,
                    scoring='roc_auc',
                    cv=cv_rf,
                    verbose=0,
                    random_state=seed,
                    n_jobs=-1
                )

        # ---- Ajuste ----
        search.fit(X_train, y_train)
        # Run hyperparameter search with CV

        # AUC medio en CV de todas las combinaciones evaluadas
        auc_values_cv.extend(search.cv_results_['mean_test_score'])
        # Collect mean CV AUC for all evaluated configs

        # Top-5 a test
        results_df = pd.DataFrame(search.cv_results_).sort_values(by='rank_test_score').head(5)
        # Take top-5 configurations by CV rank
        for _, row in results_df.iterrows():
            if model == 'xgb':
                clf = XGBClassifier(eval_metric='logloss', random_state=seed, **row['params'])
            # Recreate model with best-found params
            else:
                clf = RandomForestClassifier(random_state=seed, **row['params'])
            # Recreate model with best-found params

            clf.fit(X_train, y_train)
            y_proba_test = clf.predict_proba(X_test)[:, 1]
            # Positive-class probabilities for ROC AUC
            y_pred_test = clf.predict(X_test)
            # Class predictions for precision/recall

            AUC.append(roc_auc_score(y_test, y_proba_test))
            precision.append(precision_score(y_test, y_pred_test, zero_division=0))
            recall.append(recall_score(y_test, y_pred_test, zero_division=0))

        all_AUC.extend(AUC)
        all_precision.extend(precision)
        all_recall.extend(recall)
        all_auc_values_cv.extend(auc_values_cv)

    return all_AUC, all_auc_values_cv, all_precision, all_recall




def Metrics_Results_Comparison(X_train, X_test, y_train, y_test, boruta_features, Imp_features_rank, sorted_features, model = 'xgb',
                               save_path = 'Results/Metrics_comparison.csv'):

    #\"\"\"Compute metrics across three methods: Boruta (single set), a growing prefix of
    #Importance Ranking, and a growing prefix of Quantum-sorted features. Stores a CSV
    #with per-method metrics (median across top-5 per seed) and returns a metrics dict.

    #Args:
    #X_train, X_test, y_train, y_test: Train/test splits.
    #boruta_features (list): Features selected by Boruta.
    #Imp_features_rank (list): Features sorted by classical importance.
    #sorted_features (list): Features sorted by quantum density/logic.
    #model (str): 'xgb' or 'rf'.
    #save_path (str): CSV output path.

    #Returns:
    #dict: metrics_dict with entries for 'Boruta', 'Quantum', and 'Ranking'.\"\"\"

    print('Computing predictions for Boruta Features...')
    
    Boruta_Results = {
        "n_var": [],
        "AUC_test": [],
        "AUC_CV": [],
        "Precision_test": [],
        "Recall_test": []}

    AUC_boruta, auc_values_cv_boruta, precision_boruta, recall_boruta = AUC_from_features(X_train, 
                                                                                X_test, y_train, y_test, boruta_features, model)

    Boruta_Results['n_var'].append(len(boruta_features))  
    Boruta_Results['AUC_CV'].append(auc_values_cv_boruta)
    Boruta_Results['AUC_test'].append(AUC_boruta)
    Boruta_Results['Precision_test'].append(precision_boruta)
    Boruta_Results['Recall_test'].append(recall_boruta)

    print('Computing predictions for Importance Ranking Features...')

    Importance_Rank_Results = {
        "n_var": [],
        "AUC_test": [],
        "AUC_CV": [],
        "Precision_test": [],
        "Recall_test": []}
        
    for i in tqdm(range(len(Imp_features_rank))):
        
        feat_r = Imp_features_rank[:i+1]
        AUC_r, AUC_CV_r, Precision_r, Recall_r = AUC_from_features(X_train, X_test, y_train, y_test, feat_r, model)

        Importance_Rank_Results['n_var'].append(len(feat_r))  
        Importance_Rank_Results['AUC_CV'].append(AUC_CV_r)
        Importance_Rank_Results['AUC_test'].append(AUC_r)
        Importance_Rank_Results['Precision_test'].append(Precision_r)
        Importance_Rank_Results['Recall_test'].append(Recall_r)

    print('Computing predictions for Quantum Features...')

    Quantum_Results = {
        "n_var": [],
        "AUC_test": [],
        "AUC_CV": [],
        "Precision_test": [],
        "Recall_test": []}
        
    for i in tqdm(range(len(sorted_features))):
        
        feat_q = sorted_features[:i+1]
        AUC_q, AUC_CV_q, Precision_q, Recall_q = AUC_from_features(X_train, X_test, y_train, y_test, feat_q, model)

        Quantum_Results['n_var'].append(len(feat_q)) 
        Quantum_Results['AUC_CV'].append(AUC_CV_q)
        Quantum_Results['AUC_test'].append(AUC_q)
        Quantum_Results['Precision_test'].append(Precision_q)
        Quantum_Results['Recall_test'].append(Recall_q)
    
    
    # === CREAR DICCIONARIO ÚNICO ===
    metrics_dict = {
        "Boruta": {
            "features": boruta_features,
            "AUC": AUC_boruta,
            "Precision": precision_boruta,
            "Recall": recall_boruta
        },
        "Quantum": Quantum_Results,
        "Ranking": Importance_Rank_Results
    }
    
    # === CREAR DATAFRAME PARA CSV ===
    records = []
    
    # Quantum con idx y n separados
    for idx, (n, auc_vals, prec_vals, rec_vals) in enumerate(zip(
        metrics_dict["Quantum"]["n_var"],
        metrics_dict["Quantum"]["AUC_test"],
        metrics_dict["Quantum"]["Precision_test"],
        metrics_dict["Quantum"]["Recall_test"]
    )):
        records.append({
            "Method": "Quantum",
            "n_features": n,
            "AUC": np.median(auc_vals),
            "Precision": np.median(prec_vals),
            "Recall": np.median(rec_vals),
            "Features": sorted_features[:n]  # usamos idx, no n
        })
    
    # Ranking con idx y n separados
    for idx, (n, auc_vals, prec_vals, rec_vals) in enumerate(zip(
        metrics_dict["Ranking"]["n_var"],
        metrics_dict["Ranking"]["AUC_test"],
        metrics_dict["Ranking"]["Precision_test"],
        metrics_dict["Ranking"]["Recall_test"]
    )):
        records.append({
            "Method": "Ranking",
            "n_features": n,
            "AUC": np.median(auc_vals),
            "Precision": np.median(prec_vals),
            "Recall": np.median(rec_vals),
            "Features": Imp_features_rank[:n]  # usamos los n mejores features
        })
    
    # Boruta (único set)
    records.append({
        "Method": "Boruta",
        "n_features": len(metrics_dict["Boruta"]["features"]),
        "AUC": np.median(metrics_dict["Boruta"]["AUC"]),
        "Precision": np.median(metrics_dict["Boruta"]["Precision"]),
        "Recall": np.median(metrics_dict["Boruta"]["Recall"]),
        "Features": str(metrics_dict["Boruta"]["features"])
    })
    
    df_metrics = pd.DataFrame(records)
    df_metrics.to_csv(save_path, index=False)
    print(f"✅ DATA STORED IN {save_path}")

    return metrics_dict


def Metrics_Results_Comparison_subsets(X_train, X_test, y_train, y_test, boruta_features, Imp_features_rank, best_sets, model = 'XGB',
                               save_path = 'Results/Metrics_comparison.csv'):

    #\"\"\"Like Metrics_Results_Comparison but uses precomputed quantum best_sets (dict size→features)
    #instead of simple prefixes for the quantum method.

    #Args:
    #X_train, X_test, y_train, y_test: Train/test splits.
   # boruta_features (list): Features selected by Boruta.
   # Imp_features_rank (list): Features sorted by classical importance.
    #best_sets (dict): {k: list of features} quantum candidates per size.
    #model (str): 'xgb' or 'rf'.
    #save_path (str): CSV output path.

    #Returns:
    #dict: metrics_dict with entries for 'Boruta', 'Quantum', and 'Ranking'.\"\"\"

    print('Computing predictions for Boruta Features...')
    
    Boruta_Results = {
        "n_var": [],
        "AUC_test": [],
        "AUC_CV": [],
        "Precision_test": [],
        "Recall_test": []}
    
    AUC_boruta, auc_values_cv_boruta, precision_boruta, recall_boruta = AUC_from_features(X_train, 
                                                                                X_test, y_train, y_test, boruta_features, model)
        
    Boruta_Results['n_var'].append(len(boruta_features))  
    Boruta_Results['AUC_CV'].append(auc_values_cv_boruta)
    Boruta_Results['AUC_test'].append(AUC_boruta)
    Boruta_Results['Precision_test'].append(precision_boruta)
    Boruta_Results['Recall_test'].append(recall_boruta)

    print('Computing predictions for Importance Ranking Features...')

    Importance_Rank_Results = {
        "n_var": [],
        "AUC_test": [],
        "AUC_CV": [],
        "Precision_test": [],
        "Recall_test": []}
        
    for i in tqdm(range(len(Imp_features_rank))):
        feat_r = Imp_features_rank[:i+1]
    
        AUC_r, AUC_CV_r, Precision_r, Recall_r = AUC_from_features(X_train, X_test, y_train, y_test, feat_r, model)

        Importance_Rank_Results['n_var'].append(len(feat_r))  
        Importance_Rank_Results['AUC_CV'].append(AUC_CV_r)
        Importance_Rank_Results['AUC_test'].append(AUC_r)
        Importance_Rank_Results['Precision_test'].append(Precision_r)
        Importance_Rank_Results['Recall_test'].append(Recall_r)

    print('Computing predictions for Quantum Features...')

    Quantum_Results = {
        "n_var": [],
        "AUC_test": [],
        "AUC_CV": [],
        "Precision_test": [],
        "Recall_test": []}
        
    for i in tqdm(range(len(best_sets))):
        feat_q = best_sets[i+1]
    
        AUC_q, AUC_CV_q, Precision_q, Recall_q = AUC_from_features(X_train, X_test, y_train, y_test, feat_q, model)
        
        Quantum_Results['n_var'].append(len(feat_q)) 
        Quantum_Results['AUC_CV'].append(AUC_CV_q)
        Quantum_Results['AUC_test'].append(AUC_q)
        Quantum_Results['Precision_test'].append(Precision_q)
        Quantum_Results['Recall_test'].append(Recall_q)
    
    
    # === CREAR DICCIONARIO ÚNICO ===
    metrics_dict = {
        "Boruta": {
            "features": boruta_features,
            "AUC": AUC_boruta,
            "Precision": precision_boruta,
            "Recall": recall_boruta
        },
        "Quantum": Quantum_Results,
        "Ranking": Importance_Rank_Results
    }
    
    # === CREAR DATAFRAME PARA CSV ===
    records = []
    
    # Quantum con idx y n separados
    for idx, (n, auc_vals, prec_vals, rec_vals) in enumerate(zip(
        metrics_dict["Quantum"]["n_var"],
        metrics_dict["Quantum"]["AUC_test"],
        metrics_dict["Quantum"]["Precision_test"],
        metrics_dict["Quantum"]["Recall_test"]
    )):
        records.append({
            "Method": "Quantum",
            "n_features": n,
            "AUC": np.median(auc_vals),
            #"AUC_values": auc_vals
            "Precision": np.median(prec_vals),
            #"Precision_values": prec_vals,
            "Recall": np.median(rec_vals),
            "Features": best_sets[i]  # usamos idx, no n
        })
    
    # Ranking con idx y n separados
    for idx, (n, auc_vals, prec_vals, rec_vals) in enumerate(zip(
        metrics_dict["Ranking"]["n_var"],
        metrics_dict["Ranking"]["AUC_test"],
        metrics_dict["Ranking"]["Precision_test"],
        metrics_dict["Ranking"]["Recall_test"]
    )):
        records.append({
            "Method": "Ranking",
            "n_features": n,
            "AUC": np.median(auc_vals),
            "Precision": np.median(prec_vals),
            "Recall": np.median(rec_vals),
            "Features": Imp_features_rank[:n]  # usamos los n mejores features
        })
    
    # Boruta (único set)
    records.append({
        "Method": "Boruta",
        "n_features": len(metrics_dict["Boruta"]["features"]),
        "AUC": np.median(metrics_dict["Boruta"]["AUC"]),
        "Precision": np.median(metrics_dict["Boruta"]["Precision"]),
        "Recall": np.median(metrics_dict["Boruta"]["Recall"]),
        "Features": str(metrics_dict["Boruta"]["features"])
    })
    
    df_metrics = pd.DataFrame(records)
    df_metrics.to_csv(save_path, index=False)
    print(f"✅ DATA STORED IN {save_path}")

    return metrics_dict


def plot_metrics_combined(metrics_dict, save_path="Results/PLOT_metrics_comparison.png"):
    #Plot median AUC/Precision/Recall vs feature-set size for Quantum and Ranking,
    #with Boruta shown as a horizontal reference line. Saves a PNG.

    #Args:
    #metrics_dict (dict): Output from Metrics_Results_Comparison(_subsets).
    #save_path (str): Path to save the figure.

    #Returns:
    #None\"\"\"

    n_vars_q = metrics_dict["Quantum"]["n_var"]
    n_vars_r = metrics_dict["Ranking"]["n_var"]

    # Full range of feature-set sizes
    x_min = min(min(n_vars_q), min(n_vars_r))
    x_max = max(max(n_vars_q), max(n_vars_r))
    x_ticks = list(range(x_min, x_max + 1))

    # Compute medians across top-5×seeds
    median_AUC_q = [np.median(v) for v in metrics_dict["Quantum"]["AUC_test"]]
    median_AUC_r = [np.median(v) for v in metrics_dict["Ranking"]["AUC_test"]]
    median_AUC_b = np.median(metrics_dict["Boruta"]["AUC"])

    median_Prec_q = [np.median(v) for v in metrics_dict["Quantum"]["Precision_test"]]
    median_Prec_r = [np.median(v) for v in metrics_dict["Ranking"]["Precision_test"]]
    median_Prec_b = np.median(metrics_dict["Boruta"]["Precision"])

    median_Rec_q = [np.median(v) for v in metrics_dict["Quantum"]["Recall_test"]]
    median_Rec_r = [np.median(v) for v in metrics_dict["Ranking"]["Recall_test"]]
    median_Rec_b = np.median(metrics_dict["Boruta"]["Recall"])

    # Dynamic Boruta label showing its number of vars
    boruta_label = f"Boruta ({len(metrics_dict['Boruta']['features'])} vars)"

    # Create a figure with 3 subplots (AUC, Precision, Recall)
    fig, axs = plt.subplots(1, 3, figsize=(18, 4))

    # --- AUC ---
    axs[0].plot(n_vars_q, median_AUC_q, marker="o", color="green", label="Quantum")
    axs[0].plot(n_vars_r, median_AUC_r, marker="s", color="orange", label="Ranking")
    axs[0].axhline(y=median_AUC_b, color="gray", linestyle="--", label=boruta_label)
    axs[0].set_title("AUC")
    axs[0].set_xlabel("Feature set size")
    axs[0].set_ylabel("AUC")
    axs[0].set_xticks(x_ticks)
    axs[0].grid(True)
    axs[0].legend(loc="lower right")

    # --- Precision ---
    axs[1].plot(n_vars_q, median_Prec_q, marker="o", color="green", label="Quantum")
    axs[1].plot(n_vars_r, median_Prec_r, marker="s", color="orange", label="Ranking")
    axs[1].axhline(y=median_Prec_b, color="gray", linestyle="--", label=boruta_label)
    axs[1].set_title("Precision")
    axs[1].set_xlabel("Feature set size")
    axs[1].set_ylabel("Precision")
    axs[1].set_xticks(x_ticks)
    axs[1].grid(True)
    axs[1].legend(loc="lower right")

    # --- Recall ---
    axs[2].plot(n_vars_q, median_Rec_q, marker="o", color="green", label="Quantum")
    axs[2].plot(n_vars_r, median_Rec_r, marker="s", color="orange", label="Ranking")
    axs[2].axhline(y=median_Rec_b, color="gray", linestyle="--", label=boruta_label)
    axs[2].set_title("Recall")
    axs[2].set_xlabel("Feature set size")
    axs[2].set_ylabel("Recall")
    axs[2].set_xticks(x_ticks)
    axs[2].grid(True)
    axs[2].legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()
    print(f"✅ PLOT STORED IN {save_path}")



def plot_metrics_combined_two_csvs(
    path_dir: str,
    title: str,
    csv_xgb: str,
    csv_rf: str,
    dataset_label: str = "DATASET",
    save_path: str | None = None
):

    #Load two CSVs (XGB and RF) and plot side-by-side curves for Quantum and Ranking
    #under each classifier, with Boruta as reference. Saves a PNG and returns its path.

    #Args:
    #path_dir (str): Directory containing the CSVs.
    #title (str): Figure suptitle.
    #csv_xgb (str): Filename for XGB CSV.
    #csv_rf (str): Filename for RF CSV.
    #dataset_label (str): Unused label for future extensions.
    #save_path (str|None): If None, auto-generate output file path.

    #Returns:
    #str: Path of the saved plot.\"\"\"

    def _load_one(csv_path: str):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")
        df = pd.read_csv(csv_path)

        # Normalizar nombre de columna de tamaño de features
        ncol = "n_features" if "n_features" in df.columns else ("n_var" if "n_var" in df.columns else None)
        if ncol is None:
            raise ValueError("El CSV debe tener 'n_features' o 'n_var'.")

        # Partition by method (case-insensitive)
        def pick(method):
            return df[df["Method"].str.lower() == method].copy()

        d_q = pick("quantum")
        d_r = pick("ranking")
        d_b = pick("boruta")  # puede ser una fila

        if d_q.empty or d_r.empty:
            raise ValueError("El CSV debe contener filas para 'Quantum' y 'Ranking'.")

        # X axis values: n_features per method
        n_q = d_q[ncol].astype(int).tolist()
        n_r = d_r[ncol].astype(int).tolist()

        # Metrics are already aggregated per n_features in these CSVs
        out = {
            "n_q": n_q,
            "n_r": n_r,
            "AUC_q": d_q["AUC"].tolist(),
            "AUC_r": d_r["AUC"].tolist(),
            "Prec_q": d_q["Precision"].tolist(),
            "Prec_r": d_r["Precision"].tolist(),
            "Rec_q": d_q["Recall"].tolist(),
            "Rec_r": d_r["Recall"].tolist(),
        }

        # Boruta (if present): use median value as horizontal line and vars count for label
        if not d_b.empty:
            out["Boruta_AUC"] = float(d_b["AUC"].median())
            out["Boruta_Prec"] = float(d_b["Precision"].median())
            out["Boruta_Rec"] = float(d_b["Recall"].median())
            # si hay varias filas Boruta, cogemos la primera para el nº de vars
            try:
                out["Boruta_n"] = int(d_b[ncol].iloc[0])
            except Exception:
                out["Boruta_n"] = None
        else:
            out["Boruta_AUC"] = None
            out["Boruta_Prec"] = None
            out["Boruta_Rec"] = None
            out["Boruta_n"] = None

        return out

    # Load both CSV files
    data_xgb = _load_one(os.path.join(path_dir, csv_xgb))
    data_rf  = _load_one(os.path.join(path_dir, csv_rf))

    # Prepare shared x-ticks
    all_x = data_xgb["n_q"] + data_xgb["n_r"] + data_rf["n_q"] + data_rf["n_r"]
    x_min, x_max = int(min(all_x)), int(max(all_x))
    x_ticks = list(range(x_min, x_max + 1))

    # Boruta labels for legend
    boruta_label_xgb = f"Boruta – XGBoost ({data_xgb['Boruta_n']} vars)" if data_xgb["Boruta_n"] else "Boruta – XGB"
    boruta_label_rf  = f"Boruta – RF ({data_rf['Boruta_n']} vars)"       if data_rf["Boruta_n"] else "Boruta – RF"

    # --- Figure (3 subplots: AUC, Precision, Recall) ---
    fig, axs = plt.subplots(1, 3, figsize=(20, 5))

    # === AUC ===
    axs[0].plot(data_xgb["n_q"], data_xgb["AUC_q"], marker="o", linestyle="-",  color="green",  label="Quantum – XGB")
    axs[0].plot(data_rf["n_q"],  data_rf["AUC_q"],  marker="o", linestyle=":",  color="green",  label="Quantum – RF")
    axs[0].plot(data_xgb["n_r"], data_xgb["AUC_r"], marker="s", linestyle="-",  color="orange", label="Ranking – XGB")
    axs[0].plot(data_rf["n_r"],  data_rf["AUC_r"],  marker="s", linestyle=":",  color="orange", label="Ranking – RF")
    if data_xgb["Boruta_AUC"] is not None:
        axs[0].axhline(y=data_xgb["Boruta_AUC"], linestyle="--", color="gray", label=boruta_label_xgb)
    if data_rf["Boruta_AUC"] is not None:
        axs[0].axhline(y=data_rf["Boruta_AUC"], linestyle=":", color="gray",  label=boruta_label_rf)
    axs[0].set_title("AUC")
    axs[0].set_xlabel("Feature set size")
    axs[0].set_ylabel("AUC")
    axs[0].set_xticks(x_ticks)
    axs[0].grid(True)
    axs[0].legend(loc="lower right")

    # === Precision ===
    axs[1].plot(data_xgb["n_q"], data_xgb["Prec_q"], marker="o", linestyle="-",  color="green",  label="Quantum – XGB")
    axs[1].plot(data_rf["n_q"],  data_rf["Prec_q"],  marker="o", linestyle=":",  color="green",  label="Quantum – RF")
    axs[1].plot(data_xgb["n_r"], data_xgb["Prec_r"], marker="s", linestyle="-",  color="orange", label="Ranking – XGB")
    axs[1].plot(data_rf["n_r"],  data_rf["Prec_r"],  marker="s", linestyle=":",  color="orange", label="Ranking – RF")
    if data_xgb["Boruta_Prec"] is not None:
        axs[1].axhline(y=data_xgb["Boruta_Prec"], linestyle="--", color="gray", label=boruta_label_xgb)
    if data_rf["Boruta_Prec"] is not None:
        axs[1].axhline(y=data_rf["Boruta_Prec"], linestyle=":", color="gray",  label=boruta_label_rf)
    axs[1].set_title("Precision")
    axs[1].set_xlabel("Feature set size")
    axs[1].set_ylabel("Precision")
    axs[1].set_xticks(x_ticks)
    axs[1].grid(True)
    axs[1].legend(loc="lower right")

    # === Recall ===
    axs[2].plot(data_xgb["n_q"], data_xgb["Rec_q"], marker="o", linestyle="-",  color="green",  label="Quantum – XGB")
    axs[2].plot(data_rf["n_q"],  data_rf["Rec_q"],  marker="o", linestyle=":",  color="green",  label="Quantum – RF")
    axs[2].plot(data_xgb["n_r"], data_xgb["Rec_r"], marker="s", linestyle="-",  color="orange", label="Ranking – XGB")
    axs[2].plot(data_rf["n_r"],  data_rf["Rec_r"],  marker="s", linestyle=":",  color="orange", label="Ranking – RF")
    if data_xgb["Boruta_Rec"] is not None:
        axs[2].axhline(y=data_xgb["Boruta_Rec"], linestyle="--", color="gray", label=boruta_label_xgb)
    if data_rf["Boruta_Rec"] is not None:
        axs[2].axhline(y=data_rf["Boruta_Rec"], linestyle=":", color="gray",  label=boruta_label_rf)
    axs[2].set_title("Recall")
    axs[2].set_xlabel("Feature set size")
    axs[2].set_ylabel("Recall")
    axs[2].set_xticks(x_ticks)
    axs[2].grid(True)
    axs[2].legend(loc="lower right")

    fig.suptitle(title, fontsize=24)

    plt.tight_layout()

    # Save figure and display
    if save_path is None:
        save_path = os.path.join(path_dir, f"PLOT_{csv_xgb[:-4]}_XGB_vs_RF.png")
    plt.savefig(save_path, dpi=300)
    plt.show()  # <- asegura que se vea en el notebook

    print(f"✅ PLOT STORED IN {save_path}")
    return save_path

def plot_metrics_combined_two_csvs_2(
    path_dir: str,
    title: str,
    csv_xgb: str,
    csv_rf: str,
    dataset_label: str = "DATASET",
    save_path: str | None = None
):
    def _load_one(csv_path: str):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"No se encontró el CSV: {csv_path}")
        df = pd.read_csv(csv_path)

        ncol = "n_features" if "n_features" in df.columns else ("n_var" if "n_var" in df.columns else None)
        if ncol is None:
            raise ValueError("El CSV debe tener 'n_features' o 'n_var'.")

        def pick(method):
            return df[df["Method"].str.lower() == method].copy()

        d_q = pick("quantum")
        d_r = pick("ranking")
        d_b = pick("boruta")

        if d_q.empty or d_r.empty:
            raise ValueError("El CSV debe contener filas para 'Quantum' y 'Ranking'.")

        n_q = d_q[ncol].astype(int).tolist()
        n_r = d_r[ncol].astype(int).tolist()

        out = {
            "n_q": n_q,
            "n_r": n_r,
            "AUC_q": d_q["AUC"].tolist(),
            "AUC_r": d_r["AUC"].tolist(),
            "Prec_q": d_q["Precision"].tolist(),
            "Prec_r": d_r["Precision"].tolist(),
            "Rec_q": d_q["Recall"].tolist(),
            "Rec_r": d_r["Recall"].tolist(),
        }

        if not d_b.empty:
            out["Boruta_AUC"] = float(d_b["AUC"].median())
            out["Boruta_Prec"] = float(d_b["Precision"].median())
            out["Boruta_Rec"] = float(d_b["Recall"].median())
            try:
                out["Boruta_n"] = int(d_b[ncol].iloc[0])
            except Exception:
                out["Boruta_n"] = None
        else:
            out["Boruta_AUC"] = None
            out["Boruta_Prec"] = None
            out["Boruta_Rec"] = None
            out["Boruta_n"] = None

        return out

    # =========================
    # ESTÉTICA (AJUSTABLE)
    # =========================
    FS_SUPTITLE = 30
    FS_TITLE    = 24
    FS_LABEL    = 22
    FS_TICKS    = 18
    FS_LEGEND   = 16

    LW_MAIN     = 3.5   # grosor de curvas
    LW_BORUTA   = 3.0   # grosor de líneas horizontales
    LW_AXES     = 2.0   # grosor de bordes (spines)
    TICK_W      = 2.0   # grosor ticks
    MARKER_SZ   = 9     # tamaño markers
    GRID_LW     = 1.2   # grosor grid

    # Load both CSV files
    data_xgb = _load_one(os.path.join(path_dir, csv_xgb))
    data_rf  = _load_one(os.path.join(path_dir, csv_rf))

    # Prepare shared x-ticks (límite superior = selección Boruta)
    all_x = data_xgb["n_q"] + data_xgb["n_r"] + data_rf["n_q"] + data_rf["n_r"]
    x_min_global, x_max_global = int(min(all_x)), int(max(all_x))

    boruta_ns = [n for n in (data_xgb["Boruta_n"], data_rf["Boruta_n"]) if n is not None]
    if boruta_ns:
        x_max = max(boruta_ns)
        x_max = min(x_max, x_max_global)
    else:
        x_max = x_max_global

    x_min = x_min_global
    x_ticks = list(range(x_min, x_max + 1))

    boruta_label_xgb = f"Boruta – XGBoost ({data_xgb['Boruta_n']} vars)" if data_xgb["Boruta_n"] else "Boruta – XGB"
    boruta_label_rf  = f"Boruta – RF ({data_rf['Boruta_n']} vars)"       if data_rf["Boruta_n"] else "Boruta – RF"

    # --- Figure (3 subplots: AUC, Precision, Recall) ---
    fig, axs = plt.subplots(1, 3, figsize=(22, 6))

    def _style_axis(ax):
        # labels / ticks
        ax.tick_params(axis="both", which="major", labelsize=FS_TICKS, width=TICK_W, length=7)
        ax.tick_params(axis="both", which="minor", width=TICK_W, length=4)

        # spines thickness
        for sp in ax.spines.values():
            sp.set_linewidth(LW_AXES)

        # grid thickness
        ax.grid(True, linewidth=GRID_LW, alpha=0.6)

    # === AUC ===
    axs[0].plot(data_xgb["n_q"], data_xgb["AUC_q"], marker="o", linestyle="-", color="green",
                label="Quantum – XGB", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[0].plot(data_rf["n_q"],  data_rf["AUC_q"],  marker="o", linestyle=":", color="green",
                label="Quantum – RF", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[0].plot(data_xgb["n_r"], data_xgb["AUC_r"], marker="s", linestyle="-", color="orange",
                label="Ranking – XGB", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[0].plot(data_rf["n_r"],  data_rf["AUC_r"],  marker="s", linestyle=":", color="orange",
                label="Ranking – RF", linewidth=LW_MAIN, markersize=MARKER_SZ)

    if data_xgb["Boruta_AUC"] is not None:
        axs[0].axhline(y=data_xgb["Boruta_AUC"], linestyle="--", color="gray",
                       label=boruta_label_xgb, linewidth=LW_BORUTA)
    if data_rf["Boruta_AUC"] is not None:
        axs[0].axhline(y=data_rf["Boruta_AUC"], linestyle=":", color="gray",
                       label=boruta_label_rf, linewidth=LW_BORUTA)

    axs[0].set_title("AUC", fontsize=FS_TITLE)
    axs[0].set_xlabel("Feature set size", fontsize=FS_LABEL)
    axs[0].set_ylabel("AUC", fontsize=FS_LABEL)
    axs[0].set_xticks(x_ticks)
    axs[0].set_xlim(x_min, x_max)
    _style_axis(axs[0])
    axs[0].legend(loc="lower right", fontsize=FS_LEGEND, frameon=True)

    # === Precision ===
    axs[1].plot(data_xgb["n_q"], data_xgb["Prec_q"], marker="o", linestyle="-", color="green",
                label="Quantum – XGB", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[1].plot(data_rf["n_q"],  data_rf["Prec_q"],  marker="o", linestyle=":", color="green",
                label="Quantum – RF", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[1].plot(data_xgb["n_r"], data_xgb["Prec_r"], marker="s", linestyle="-", color="orange",
                label="Ranking – XGB", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[1].plot(data_rf["n_r"],  data_rf["Prec_r"],  marker="s", linestyle=":", color="orange",
                label="Ranking – RF", linewidth=LW_MAIN, markersize=MARKER_SZ)

    if data_xgb["Boruta_Prec"] is not None:
        axs[1].axhline(y=data_xgb["Boruta_Prec"], linestyle="--", color="gray",
                       label=boruta_label_xgb, linewidth=LW_BORUTA)
    if data_rf["Boruta_Prec"] is not None:
        axs[1].axhline(y=data_rf["Boruta_Prec"], linestyle=":", color="gray",
                       label=boruta_label_rf, linewidth=LW_BORUTA)

    axs[1].set_title("Precision", fontsize=FS_TITLE)
    axs[1].set_xlabel("Feature set size", fontsize=FS_LABEL)
    axs[1].set_ylabel("Precision", fontsize=FS_LABEL)
    axs[1].set_xticks(x_ticks)
    axs[1].set_xlim(x_min, x_max)
    _style_axis(axs[1])
    axs[1].legend(loc="lower right", fontsize=FS_LEGEND, frameon=True)

    # === Recall ===
    axs[2].plot(data_xgb["n_q"], data_xgb["Rec_q"], marker="o", linestyle="-", color="green",
                label="Quantum – XGB", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[2].plot(data_rf["n_q"],  data_rf["Rec_q"],  marker="o", linestyle=":", color="green",
                label="Quantum – RF", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[2].plot(data_xgb["n_r"], data_xgb["Rec_r"], marker="s", linestyle="-", color="orange",
                label="Ranking – XGB", linewidth=LW_MAIN, markersize=MARKER_SZ)
    axs[2].plot(data_rf["n_r"],  data_rf["Rec_r"],  marker="s", linestyle=":", color="orange",
                label="Ranking – RF", linewidth=LW_MAIN, markersize=MARKER_SZ)

    if data_xgb["Boruta_Rec"] is not None:
        axs[2].axhline(y=data_xgb["Boruta_Rec"], linestyle="--", color="gray",
                       label=boruta_label_xgb, linewidth=LW_BORUTA)
    if data_rf["Boruta_Rec"] is not None:
        axs[2].axhline(y=data_rf["Boruta_Rec"], linestyle=":", color="gray",
                       label=boruta_label_rf, linewidth=LW_BORUTA)

    axs[2].set_title("Recall", fontsize=FS_TITLE)
    axs[2].set_xlabel("Feature set size", fontsize=FS_LABEL)
    axs[2].set_ylabel("Recall", fontsize=FS_LABEL)
    axs[2].set_xticks(x_ticks)
    axs[2].set_xlim(x_min, x_max)
    _style_axis(axs[2])
    axs[2].legend(loc="lower right", fontsize=FS_LEGEND, frameon=True)

    fig.suptitle(title, fontsize=FS_SUPTITLE, fontweight="bold")
    plt.tight_layout()

    if save_path is None:
        save_path = os.path.join(path_dir, f"PLOT_{csv_xgb[:-4]}_XGB_vs_RF.png")
    plt.savefig(save_path, dpi=300)
    plt.show()

    print(f"✅ PLOT STORED IN {save_path}")
    return save_path



def plot_overlap_from_csv(
    csv_path: str,
    title: str,
    method_q: str = "Quantum",
    method_r: str = "Ranking",
    method_b: str = "Boruta",
    save_path: str = None,
    show_values: bool = True,  # se mantiene por compatibilidad, pero no se usa
):
    # Read CSV and parse lists from strings
    df = pd.read_csv(csv_path)

    def parse_list(x):
        if isinstance(x, list):
            return x
        try:
            return ast.literal_eval(x)
        except Exception:
            return []

    df["Features"] = df["Features"].apply(parse_list)

    # Build map: n -> top-n features (prefix)
    def build_topn_map(df_method):
        out = {}
        for _, row in df_method.iterrows():
            n = int(row["n_features"])
            feats = row["Features"]
            subset = feats[:n] if len(feats) >= n else feats
            out[n] = subset
        return out

    df_q = df[df["Method"] == method_q].copy().sort_values("n_features")
    df_r = df[df["Method"] == method_r].copy().sort_values("n_features")
    df_b = df[df["Method"] == method_b].copy().sort_values("n_features")

    map_q_topn = build_topn_map(df_q)
    map_r_topn = build_topn_map(df_r)

    # 1) Quantum vs Ranking at common n values
    common_ns = sorted(set(map_q_topn.keys()).intersection(map_r_topn.keys()))
    rows = []
    for n in common_ns:
        Qn = set(map_q_topn[n])
        Rn = set(map_r_topn[n])
        inter = Qn.intersection(Rn)
        pct = 100.0 * len(inter) / float(n) if n > 0 else 0.0
        rows.append({
            "Label": f"n={n}",
            "Type": "Q vs R",
            "n": n,
            "Percent": pct,
            "Intersection": len(inter)
        })

    # 2) Boruta vs Quantum using closest n to m
    boruta_rows = []
    if not df_b.empty and len(map_q_topn) > 0:
        q_ns = sorted(map_q_topn.keys())
        for _, row in df_b.iterrows():
            B = set(row["Features"])
            m = int(row["n_features"])
            k = m if m in map_q_topn else min(q_ns, key=lambda x: abs(x - m))
            Qk = set(map_q_topn[k])
            inter = B.intersection(Qk)
            pct_b = 100.0 * len(inter) / float(m) if m > 0 else 0.0
            boruta_rows.append({
                "Label": f"Boruta(m={m})",
                "Type": f"B vs Q(n={k})",
                "n": m,
                "Percent": pct_b,
                "Intersection": len(inter)
            })

    overlaps_df = pd.DataFrame(rows + boruta_rows)

    # Plot order: all Q vs R bars first, then Boruta comparisons
    qr_part = overlaps_df[overlaps_df["Type"] == "Q vs R"].copy()
    boruta_part = overlaps_df[overlaps_df["Type"] != "Q vs R"].copy()
    plot_df = pd.concat([qr_part, boruta_part], ignore_index=True)

    # =========================
    # ESTÉTICA (AJUSTABLE)
    # =========================
    FS_SUPTITLE = 28
    FS_LABEL    = 22
    FS_TICKS    = 18

    LW_AXES     = 2.0
    TICK_W      = 2.0
    BAR_EDGE_LW = 2.0

    GRID_LW_20  = 1.8   # líneas cada 20%
    GRID_A_20   = 0.55
    GRID_LW_100 = 3.2   # línea del 100% destacada
    GRID_A_100  = 0.85

    # Plot
    fig, ax = plt.subplots(figsize=(14, 6))
    x = range(len(plot_df))

    bars = ax.bar(
        x,
        plot_df["Percent"],
        color="#2E7D32",
        edgecolor="black",
        linewidth=BAR_EDGE_LW,
        zorder=3
    )

    # Si existe la barra Boruta, la pintamos en naranja (última barra del plot_df actual)
    if len(bars) > 0 and not boruta_part.empty:
        bars[-1].set_facecolor("#FFA726")

    # Líneas horizontales punteadas cada 20% (20..80) + destacar 100%
    for y in [20, 40, 60, 80]:
        ax.axhline(y=y, linestyle="--", linewidth=GRID_LW_20, alpha=GRID_A_20, zorder=1)
    ax.axhline(y=100, linestyle="--", linewidth=GRID_LW_100, alpha=GRID_A_100, zorder=1)

    # Ejes / ticks
    ax.set_xticks(list(x))
    ax.set_xticklabels(plot_df["Label"], rotation=45, ha="right", fontsize=FS_TICKS)
    ax.set_ylabel("Coincidence", fontsize=FS_LABEL)
    ax.set_ylim(0, 105)

    ax.tick_params(axis="both", which="major", labelsize=FS_TICKS, width=TICK_W, length=7)

    for sp in ax.spines.values():
        sp.set_linewidth(LW_AXES)

    # (Opcional) mantener grid Y suave adicional: lo quitamos para no duplicar
    # ax.grid(axis="y", linestyle="--", alpha=0.4, linewidth=1.0)

    fig.suptitle(title, fontsize=FS_SUPTITLE, fontweight="bold")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()

    return overlaps_df





    