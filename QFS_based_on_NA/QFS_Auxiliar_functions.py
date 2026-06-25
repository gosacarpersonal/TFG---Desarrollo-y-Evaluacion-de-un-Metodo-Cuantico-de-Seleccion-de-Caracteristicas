# ================================================================
# QFS_Auxiliar_functions.py — Annotated Version
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
import ast

import matplotlib.pyplot as plt
import matplotlib.pylab as plt
import matplotlib.cm as cm

import networkx as nx

from tqdm import tqdm
from sklearn.manifold import MDS
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder

try:
    import gurobipy as gp
    from gurobipy import GRB
except ModuleNotFoundError:
    gp = None
    GRB = None

try:
    from braket.ahs.atom_arrangement import AtomArrangement, SiteType
    from braket.ahs.driving_field import DrivingField
    from braket.ahs.local_detuning import LocalDetuning
    from braket.ahs.field import Field
    from braket.ahs.pattern import Pattern
    from braket.tasks.analog_hamiltonian_simulation_quantum_task_result import AnalogHamiltonianSimulationQuantumTaskResult
    from braket.ahs.analog_hamiltonian_simulation import AnalogHamiltonianSimulation
    from braket.timings.time_series import TimeSeries
    from braket.devices import LocalSimulator

    simulator = LocalSimulator("braket_ahs")
except ModuleNotFoundError:
    AtomArrangement = None
    DrivingField = None
    LocalDetuning = None
    AnalogHamiltonianSimulation = None
    TimeSeries = None
    simulator = None

try:
    from ahs_utils import (
        show_register,
        show_drive_and_local_detuning,
        show_final_avg_density,
        show_global_drive,
    )
except ModuleNotFoundError:
    show_register = None
    show_drive_and_local_detuning = None
    show_final_avg_density = None
    show_global_drive = None


def Delta_2step(t, t_max, Delta_max):
    #Two-step global detuning schedule Δ(t): strong negative in the first half,
    if t < t_max/2:
        return -Delta_max -Delta_max*np.cos(np.pi*t/(t_max/2))
    else:
        return 0
        
def Delta_local_2step(t, t_max, Delta_local_max):
    #Two-step local detuning schedule Δ_l(t): zero in first half; positive cosine
    if t > t_max/2:
        return Delta_local_max +Delta_local_max*np.cos(np.pi*t/(t_max/2))
    else:
        return 0

def Omega_global(t, t_max, Omega_max):
    #Smooth global Rabi amplitude schedule Ω(t) using a nested sine.
    return Omega_max*(np.sin((np.pi/2)*np.sin(np.pi*t/t_max)))**2

def QFS_NA_Solver(MI_xy, MI_xx, feature_names, label, E_dist_fraction=0.2, shots = 1000, t = 4, 
                  Omega_max = 15 *1e6, Delta_max =  30 * 1e6, Delta_local_max = 30 * 1e6,
                  beta=0.0, mds_max_iter=100, mds_runs=100, make_plots=True,
                  dist_ratio_rydberg=1/np.sqrt(2)):
    
   #Quantum Feature Selection (QFS) solver on a neutral-atom (Rydberg) analog simulator.
    #Builds atom arrangement from redundancy, defines driving/ detuning schedules,
    #runs the AHS program, filters bitstrings by cost, and plots results.

    #Args:
    #MI_xy (array-like): Feature–target mutual information.
    #MI_xx (2D array): Feature–feature redundancy matrix.
    #feature_names (list): Names of features.
    #label (str): Label used for plot/output filenames.
    #E_dist_fraction (float): Top fraction (by cost) of samples to keep.
    #shots (int): Number of simulator shots.
    #t (float): Total evolution time in microseconds.
    #Omega_max (float): Max global Rabi amplitude.
    #Delta_max (float): Max global detuning.
    #Delta_local_max (float): Max local detuning.

    #Returns:
    #Tuple[list, list, list, np.ndarray]:
    #Cost_f_filtered, counts_filtered, bitstring_unicos_list, avg_density

    if simulator is None:
        raise RuntimeError("amazon-braket-sdk is required to run QFS_NA_Solver")


    C = 862690 * 2 * np.pi *1e6 # um^6 * rad / us
    alpha = 0.5
    og_weights = normalize_list(MI_xy)
    # Normalize feature-target MI into [0,1]

    n_atoms = len(og_weights)
    
    R_ij = normalize_matrix(MI_xx)
    # Scale redundancy matrix to [0,1] for distance mapping

    t0 = 0
    time_max = t*1e-6
    
    time = np.linspace(t0, time_max, 100)
    
    omega_array = [Omega_global(t, time_max, Omega_max) for t in time]
    delta_array = [Delta_2step(t, time_max, Delta_max) for t in time]
    delta_local_array = [Delta_local_2step(t, time_max, Delta_local_max) for t in time]
    phi_array = np.zeros_like(omega_array)
    
    omega = TimeSeries()
    # Build Braket time series for drive amplitude
    for t_step, val in zip(time, omega_array):
        omega.put(t_step, val)
    global_detuning = TimeSeries()
    # Global detuning Δ(t)
    for t_step, val in zip(time, delta_array):
        global_detuning.put(t_step, val)
    phi = TimeSeries()
    # Drive phase φ(t) (kept at zero here)
    for t_step, val in zip(time, phi_array):
        phi.put(t_step, val)
    
    drive = DrivingField(amplitude=omega,
                         phase=phi,
                         detuning=global_detuning)

    local_detuning_drive = LocalDetuning.from_lists(times=time,
                                                        values=delta_local_array,
                                                        pattern=list(np.array(og_weights)))

    #show_drive_and_local_detuning(drive , local_detuning_drive)

    R_b = (C/np.sqrt((Delta_local_max)**2))**(1/6)
    # Estimate Rydberg blockade radius from max local detuning

    print('Rydberg Radius(um) for selected drivings:', R_b)

    print('Computing arrangement...')
    
    min_radius, MDS_dist_matrix, D_matrix, positions, error_matrix = arrange_atoms_robust_MDS(
        R_b,
        og_weights,
        R_ij,
        dist_ratio_rydberg,
        max_iter=mds_max_iter,
        n_mds_runs=mds_runs,
        beta=beta,
    )
    
    grid_space = min_radius*1e-6
    positions = np.array(positions)*1e-6

    print('Grid spacing computed:', min_radius)
    
    new_x, new_y = positions[:, 0], positions[:, 1]

    V_ij = C/((grid_space*1e6)**6)

    Driving_ratio = Delta_max/V_ij

    print('Driving / Interaction Ratio:', np.sqrt(Omega_max**2 + Delta_max**2)/V_ij)
    print('Detuning / Interaction Ratio:', Driving_ratio)
    print(f"Error Matrix Mean = {np.mean(error_matrix):.4f}, Std = {np.std(error_matrix):.4f}")

    new_atoms = AtomArrangement()
    
    for i in range(n_atoms):
        new_atoms.add([new_x[i], new_y[i]])

    if make_plots:
        print('Visualizing properties...')
        Visualize_prop(R_ij, np.array(MDS_dist_matrix), positions, og_weights, error_matrix, label)    

    print('Performing simulation...')

    program = AnalogHamiltonianSimulation(hamiltonian=drive + local_detuning_drive, register=new_atoms)
    result = simulator.run(program, shots=shots, blockade_radius = R_b*1e-6, steps = 40).result()
    # Execute AHS locally; returns samples of g/r strings

    counters = result.get_counts()
    gr_list = list(counters.keys())
    Counts = list(counters.values())
    
    bit_list = [[0 if char == 'g' else 1 for char in gr] for gr in gr_list]
    # Map 'g'→0 and 'r'→1 for each sampled string

    expanded_bit_list = [bit for bit, count in zip(bit_list, Counts) for _ in range(count)]
    # Expand to one row per shot for cost computation

    ## First computation of the cost function (Q)
    Cost_f = [cost_function(np.array(og_weights), np.array(R_ij), np.array(bit) , alpha) for bit in expanded_bit_list]

    n_top = max(1, int(len(Cost_f) * E_dist_fraction))

    top_indices = np.argsort(Cost_f)[:n_top]

    ## Bitstrings filtered by cost (Q)
    filtered_bit_list = [expanded_bit_list[i] for i in top_indices]

    ## Build a list of unique bitstrings with their counts
    filtered_as_tuples = [tuple(bit) for bit in filtered_bit_list]
    bitstring_counts = Counter(filtered_as_tuples)
    bitstring_unicos_list = list(bitstring_counts.keys())
    counts_filtered = list(bitstring_counts.values())

    ## Second computation of the cost function (Q)
    Cost_f_filtered = [cost_function(np.array(og_weights), np.array(R_ij), np.array(bit), alpha) for bit in bitstring_unicos_list]
    
    if make_plots:
        avg_density = results_plotter(filtered_bit_list, feature_names, Cost_f_filtered, counts_filtered, label)
    else:
        avg_density = np.array(filtered_bit_list).mean(axis=0)
    
    return Cost_f_filtered, counts_filtered, bitstring_unicos_list, avg_density


def generate_sets_from_density(avg_density, R_ij, feature_names, 
                               max_sets=4, redundancy_threshold=0.7):

    #"Generate redundancy-aware feature sets from average Rydberg densities and
    #construct the best set per target size k.

    #Args:
    #avg_density (array-like): Mean excitation per feature.
    #R_ij (2D array): Redundancy matrix (higher means more redundant).
    #feature_names (list): Feature names.
   # max_sets (int): Number of alternative sets to propose.
    #redundancy_threshold (float): Max allowed redundancy between chosen features.

   # Returns:
    #Tuple[list, dict]:
    #alt_sets (list of lists), best_sets (dict: size k -> list of features).

    N = len(feature_names)
    feature_names = list(feature_names)  
    feat_to_idx = {f: i for i, f in enumerate(feature_names)}  

    order = np.argsort(avg_density)[::-1]  
    alt_sets = []

    # 1. Construir las alternativas con shifts
    for shift in range(max_sets):
        chosen = []
        for idx in order[shift:]:
            f = idx
            # comprobar compatibilidad
            compatible = True
            for g in chosen:
                if R_ij[f][g] > redundancy_threshold:
                    compatible = False
                    break
            if compatible:
                chosen.append(f)
        alt_sets.append([feature_names[i] for i in chosen])

    # 2. Construir el mejor set para cada tamaño k
    best_sets = {}
    for k in range(1, N+1):
        best_set = None
        best_score = -np.inf
        for s in alt_sets:
            if len(s) >= k:
                dens_sorted = sorted(s, key=lambda f: avg_density[feat_to_idx[f]], reverse=True)
                candidate = dens_sorted[:k]
                score = np.mean([avg_density[feat_to_idx[f]] for f in candidate])
                if score > best_score:
                    best_score = score
                    best_set = candidate
        
        # fallback si no hay conjunto compatible suficiente
        if best_set is None or len(best_set) < k:
            # coger top-k según densidad global, ignorando redundancias
            fallback = [feature_names[i] for i in order[:k]]
            best_set = fallback

        best_sets[k] = best_set

    return alt_sets, best_sets


def arrange_atoms_robust_MDS(R_b, I_i, R_ij, dist_ratio_rydberg=1/np.sqrt(2), max_iter=100, n_mds_runs=100, beta=0.0):
    min_d_allowed = dist_ratio_rydberg * R_b
    best_error = np.inf
    best_result = None
    best_dmin_dmax = None

    d_min, d_max = R_b, 4 * R_b
    history = []

    print(f"{'Iter':<5} {'d_min':<10} {'d_max':<10} {'min_radius':<14} {'mean_error':<12}")

    for it in range(max_iter):
        D_matrix = distance_matrix_from_redundancy(R_ij, d_max, d_min, I_i=I_i, beta=beta)
        # Map redundancy → distances within [d_min, d_max]

        best_local_error = np.inf
        best_local_result = None

        # Run n_mds_runs MDS seeds with different random states
        for seed in range(n_mds_runs):
            # The QFS protocol documents N independent MDS starts.  Pin n_init=1 so
            # each seed in n_mds_runs corresponds to one start, independent of the
            # scikit-learn default (4 in current versions, 1 in future releases).
            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=seed, n_init=1)
            positions = mds.fit_transform(D_matrix)

            new_x, new_y = positions[:, 0] * 1e-6, positions[:, 1] * 1e-6
            MDS_dist_matrix = calculate_D_matrix(new_x, new_y)
            min_radius = second_minor(MDS_dist_matrix)

            if min_radius < min_d_allowed:
                # Enforce minimal allowed inter-atom spacing
                continue

            error_matrix = calculate_error_matrix(D_matrix, MDS_dist_matrix)
            # Relative error between target and embedded distances
            avg_error = np.mean(error_matrix)

            if avg_error < best_local_error:
                best_local_error = avg_error
                best_local_result = (min_radius, MDS_dist_matrix, D_matrix, positions, error_matrix)

        # If no MDS solution satisfies the minimum distance, expand the range
        if best_local_result is None:
            d_min += 0.2
            d_max += 0.4
            continue

        history.append((it, d_min, d_max, best_local_result[0], best_local_error))
        print(f"{it:<5} {d_min:<10.4f} {d_max:<10.4f} {best_local_result[0]:<14.4f} {best_local_error:<12.6f}")

        if best_local_error < best_error:
            best_error = best_local_error
            best_result = best_local_result
            best_dmin_dmax = (d_min, d_max)

        d_min += 0.1
        d_max += 0.2

    if best_result is not None:
        print(f"\n✅ Best result obtained with con d_min = {best_dmin_dmax[0]:.4f}, d_max = {best_dmin_dmax[1]:.4f}")
        print(f"📉 Mean relative error reached: {best_error:.6f}")
        return best_result
    else:
        raise ValueError("❌ Valid arrangemen not found.")



def Visualize_prop(R_ij, MDS_dist_matrix, positions, og_weights, error_matrix, label):

    cmap = "viridis"

    # =========================
    # ESTÉTICA (AJUSTABLE)
    # =========================
    FS_SUPTITLE = 30
    FS_TITLE    = 22
    FS_TICKS    = 18
    FS_CB       = 18
    FS_ATOMS    = 14

    TICK_W      = 2.0
    GRID_LW     = 1.2

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 13))

    # ----------- Redundancy matrix
    R_plot = ax1.imshow(np.array(R_ij), cmap=cmap)
    cbar1 = fig.colorbar(R_plot, ax=ax1)
    cbar1.ax.tick_params(labelsize=FS_CB, width=TICK_W)
    
    ax1.set_title("Redundancy matrix", fontsize=FS_TITLE)
    ax1.tick_params(axis="both", labelsize=FS_TICKS, width=TICK_W)
    
    n = np.array(R_ij).shape[0]
    ax1.set_xticks(np.arange(n))
    ax1.set_yticks(np.arange(n))

    # ----------- MDS Distance matrix
    D_plot = ax2.imshow(np.array(MDS_dist_matrix), cmap=cmap)
    cbar2 = fig.colorbar(D_plot, ax=ax2)
    cbar2.ax.tick_params(labelsize=FS_CB, width=TICK_W)

    ax2.set_title("MDS Distance matrix", fontsize=FS_TITLE)
    ax2.tick_params(axis="both", labelsize=FS_TICKS, width=TICK_W)

    # ----------- Relative Error matrix
    E_plot = ax3.imshow(np.array(error_matrix), cmap=cmap)
    cbar3 = fig.colorbar(E_plot, ax=ax3)
    cbar3.ax.tick_params(labelsize=FS_CB + 4, width=TICK_W)

    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.set_title("Relative Error matrix in MDS", fontsize=FS_TITLE)

    # ----------- Atom arrangement
    x_vals, y_vals = positions[:, 0], positions[:, 1]
    scatter = ax4.scatter(
        x_vals, y_vals,
        c=og_weights, cmap="plasma",
        s=130, zorder=2
    )

    for i, (x, y) in enumerate(positions):
        ax4.text(
            x + 1e-6, y + 1e-6, str(i),
            color="black",
            fontsize=FS_ATOMS,
            ha="center", va="center",
            zorder=3
        )

    ax4.grid(True, linestyle="--", color="gray", alpha=0.5, linewidth=GRID_LW)
    ax4.tick_params(axis="both", labelsize=FS_TICKS, width=TICK_W)

    ax4.set_aspect("equal")
    ax4.set_title("Atom arrangement", fontsize=FS_TITLE)

    cbar4 = plt.colorbar(scatter, ax=ax4)
    cbar4.ax.tick_params(labelsize=FS_CB, width=TICK_W)

    fig.suptitle("Pre-simulation properties", fontsize=FS_SUPTITLE, fontweight="bold")

    plt.tight_layout()
    plt.savefig(f"Results/{label}/PRESIMULATION_PROPERTIES_{label}.png", dpi=150)
    plt.show()




def MDS_matrix(n_it, D_matrix):
    #Average multiple MDS embeddings (with fixed random_state) and return the distance
    #matrix, minimum pairwise distance, and positions.

    #Args:
    #n_it (int): Number of MDS runs to average.
    #D_matrix (2D array): Target distance matrix.

    #Returns:
    #Tuple[np.ndarray, float, np.ndarray]: (MDS_dist_matrix, min_radius, positions).

    n_atoms = D_matrix.shape[0]
    positions = np.zeros((n_atoms,2))
    
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=200)
    
    for it in range(n_it):
        positions += mds.fit_transform(D_matrix)
    
    positions = positions/n_it
    
    new_x, new_y = positions[:, 0]*1e-6, positions[:, 1]*1e-6
    
    MDS_dist_matrix = calcular_matriz_distancias(new_x, new_y)
    #error_matrix = calculate_error_matrix(D_matrix, MDS_dist_matrix)
    
    min_radius=second_minor(MDS_dist_matrix)

    return MDS_dist_matrix, min_radius, positions


def distance_matrix_from_redundancy(R_ij, d_max, d_min, I_i=None, beta=0.0):
    #Map redundancy values to a metric-like distance matrix and rescale into [d_min, d_max],
    #enforcing zeros on the diagonal.

    #Args:
    #R_ij (2D array): Redundancy matrix.
    #d_max (float): Maximum target distance.
    #d_min (float): Minimum target distance.

    #Returns:
    #np.ndarray: Distance matrix derived from redundancy.

    R_ij = np.asarray(R_ij, dtype=float)
    n = np.shape(R_ij)[0]
    if I_i is None:
        I_i = np.zeros(n)
    I_i = np.asarray(I_i, dtype=float)
    if len(I_i) != n:
        raise ValueError("I_i must have the same length as R_ij")

    D = np.ones((n,n))
    for i in range(n):
        for j in range(n):
            if i == j:
                D[i][j]=0
            elif R_ij[i][j] == 0:
                D[i][j] = d_max
                D[j][i] = d_max
            else:
                dij = ((1/(R_ij[i][j]))**(1/6))
                if beta > 0:
                    dij += beta * (1 + I_i[i]) * (1 + I_i[j])
                D[i][j] = dij
                D[j][i] = dij

    min_matrix = second_minor(D)
    max_matrix = np.max(D)
    if max_matrix == min_matrix:
        D_matrix = np.full_like(D, d_min, dtype=float)
    else:
        D_matrix = np.round(d_min + ((D - min_matrix) / (max_matrix - min_matrix)) * (d_max - d_min),4)
    np.fill_diagonal(D_matrix, 0)

    return D_matrix

def calculate_error_matrix(M_original, M_pred):
    #Compute relative error matrix between an original distance matrix and a predicted one.

    #Args:
    #M_original (2D array): Reference distance matrix.
    #M_pred (2D array): Predicted/embedded distance matrix.

    #Returns:
    #np.ndarray: Relative error per entry; zeros on the diagonal.

    dim = len(M_original)
    error_matrix = np.zeros((dim,dim))

    for i in range(dim):
        for j in range(dim):
            if i == j :
                error_matrix[i][j] = 0
            else:
                error_matrix[i][j] = np.round(np.abs(M_original[i][j] - M_pred[i][j])/M_original[i][j], 4)

    return error_matrix


def calculate_D_matrix(x, y):
    #\"\"\"Compute pairwise Euclidean distances (in micrometers) from x,y coordinates (in meters)
    #and round to 4 decimals.

    #Args:
    #x (array-like): x positions in meters.
    #y (array-like): y positions in meters.

    #Returns:
    #np.ndarray: Distance matrix in micrometers.\"\"\"

    num_puntos = len(x)
    matriz_distancias = np.zeros((num_puntos, num_puntos))
    
    for i in range(num_puntos):
        for j in range(num_puntos):
            dist = 1e6*np.sqrt((x[i] - x[j])**2 + (y[i] - y[j])**2)
            matriz_distancias[i][j] = np.round(dist,4)
    
    return matriz_distancias
    
def cost_function(I_i, R_ij, bitstring, alpha):
    #Objective function Q = -(alpha) * sum(I_i * bitstring) + (1-alpha) * sum(R_ij * outer(bit, bit)).

    #Args:
    #I_i (array-like): Feature importance weights.
    #R_ij (2D array): Redundancy matrix.
    #bitstring (array-like): 0/1 selection vector.
    #alpha (float): Trade-off between importance and redundancy.

    #Returns:
    #float: Cost value (lower is better)

    # importance term
    I = - alpha * np.sum(I_i * bitstring)

    # Redundance term
    R = (1 - alpha) * np.sum(R_ij * np.outer(bitstring, bitstring))

    # Q = primer término + segundo término
    Q = I + R

    return Q


def _oracle_Q_star_exhaustive(I_i: np.ndarray, R_ij: np.ndarray, alpha: float, k_target: int | None = None) -> tuple[np.ndarray, float]:
    n = len(I_i)
    total = 1 << n
    chunk_size = min(131072, total)
    shifts = np.arange(n - 1, -1, -1, dtype=np.uint64)
    best_x = None
    best_q = np.inf

    for start in range(0, total, chunk_size):
        stop = min(start + chunk_size, total)
        values = np.arange(start, stop, dtype=np.uint64)
        X = ((values[:, None] >> shifts) & 1).astype(float)
        if k_target is not None:
            mask = X.sum(axis=1) == k_target
            if not np.any(mask):
                continue
            X_eval = X[mask]
        else:
            X_eval = X
        relevance = X_eval @ I_i
        redundancy = np.einsum("bi,ij,bj->b", X_eval, R_ij, X_eval, optimize=True)
        costs = -alpha * relevance + (1 - alpha) * redundancy
        local = int(np.argmin(costs))
        local_q = float(costs[local])
        if local_q < best_q:
            best_q = local_q
            best_x = X_eval[local].astype(int)

    if best_x is None:
        raise ValueError("No feasible bitstring found")
    return best_x, best_q


def oracle_Q_star(I_i: np.ndarray, R_ij: np.ndarray, alpha: float, k_target: int | None = None) -> tuple[np.ndarray, float]:
    I_i = np.asarray(I_i, dtype=float)
    R_ij = np.asarray(R_ij, dtype=float)
    n = len(I_i)
    if R_ij.shape != (n, n):
        raise ValueError("R_ij must be a square matrix with len(I_i) rows")
    if k_target is not None and not 0 <= k_target <= n:
        raise ValueError("k_target must be between 0 and n")

    if n <= 20:
        return _oracle_Q_star_exhaustive(I_i, R_ij, alpha, k_target=k_target)

    if gp is None or GRB is None:
        raise RuntimeError("gurobipy is required for oracle_Q_star when n > 20")

    model = gp.Model("qfs_qubo_oracle")
    model.Params.OutputFlag = 0
    x = model.addVars(n, vtype=GRB.BINARY, name="x")
    objective = gp.quicksum(-alpha * float(I_i[i]) * x[i] for i in range(n))
    objective += gp.quicksum((1 - alpha) * float(R_ij[i, j]) * x[i] * x[j] for i in range(n) for j in range(n))
    model.setObjective(objective, GRB.MINIMIZE)
    if k_target is not None:
        model.addConstr(gp.quicksum(x[i] for i in range(n)) == int(k_target))
    model.optimize()
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(f"Gurobi did not find an optimal solution. Status={model.Status}")
    x_opt = np.asarray([int(round(x[i].X)) for i in range(n)], dtype=int)
    return x_opt, float(model.ObjVal)


def mucke_alpha_for_k(
    I_i,
    R_ij,
    k_target,
    alpha_low=0.0,
    alpha_high=1.0,
    tol=1e-6,
    max_iter=100,
) -> tuple[float, np.ndarray]:
    I_i = np.asarray(I_i, dtype=float)
    R_ij = np.asarray(R_ij, dtype=float)
    if not 0 <= k_target <= len(I_i):
        raise ValueError("k_target must be between 0 and n")

    low = float(alpha_low)
    high = float(alpha_high)
    best_alpha = (low + high) / 2
    best_x, _ = oracle_Q_star(I_i, R_ij, best_alpha)
    best_gap = abs(int(best_x.sum()) - int(k_target))

    for _ in range(max_iter):
        alpha = (low + high) / 2
        x_opt, _ = oracle_Q_star(I_i, R_ij, alpha)
        k_current = int(x_opt.sum())
        gap = abs(k_current - int(k_target))
        if gap < best_gap:
            best_alpha = alpha
            best_x = x_opt
            best_gap = gap
        if k_current == k_target:
            return alpha, x_opt
        if (high - low) <= tol:
            break
        if k_current > k_target:
            high = alpha
        else:
            low = alpha

    x_constrained, _ = oracle_Q_star(I_i, R_ij, best_alpha, k_target=k_target)
    return best_alpha, x_constrained


def normalize_list(valores):

    min_val = min(valores)
    max_val = max(valores)
    # Avoid division by zero if all values are equal
    if min_val == max_val:
        return [0.5] * len(valores)  # All values will be equal
    else:
        return [(x - min_val) / (max_val - min_val) for x in valores]

def normalize_matrix(matrix):

    matrix_min = np.min(matrix)
    matrix_max = np.max(matrix)
    
    # Avoid division by zero for constant-valued matrices
    if matrix_max == matrix_min:
        return np.zeros_like(matrix)
    
    normalized_matrix = (matrix - matrix_min) / (matrix_max - matrix_min)
    return normalized_matrix

def second_minor(matrix):

    valores_unicos = np.unique(matrix)

    if len(valores_unicos) >= 2:
        segundo_menor = valores_unicos[1]
    else:
        print("Not enough elements in list")
    return segundo_menor



def results_plotter(bit_list, feature_names, Cost_f, Counts, label):
    
    #Plot histogram of cost vs. counts and bar plot of average feature density; save under Results/.

    #Args:
    #bit_list (list of lists): Bitstrings kept after filtering.
    #feature_names (list): Feature names.
    #Cost_f (list): Cost values per unique bitstring.
    #Counts (list): Counts per unique bitstring.
    #label (str): Label for output filename.

    #Returns:
    #np.ndarray: Average density per feature.\"\"\"

    plt.figure(figsize=(20, 20))

    bit_array = np.array(bit_list)  # shape (N, 15)

    avg_density = bit_array.mean(axis=0)  # mean excitation per feature

    
    plt.subplot(2, 1, 1)
    plt.bar(Cost_f, Counts, width=0.05)
    plt.xlabel("Cost function value")
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.ylabel("Counts")

    plt.subplot(2, 1, 2)
    plt.bar(list(feature_names), avg_density)
    plt.xlabel("FEATURES")
    plt.ylabel("RYDBERG DENSITY")
    plt.xticks(range(len(avg_density)), rotation=90)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()

    plt.savefig(f'Results/{label}/SIMULATION_RESULTS_{label}.png', dpi=100)

    plt.show()

    return avg_density


def export_results_csv(Cost_f, Counts, bit_list, avg_density, filename):

    data = {
        "Cost_f": [Cost_f],
        "Counts": [Counts],
        "bit_list": [bit_list],
        "avg_density": [list(avg_density)]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(f"{filename}.csv", index=False)
    print(f"✅ Resultados exportados en {filename}.csv")


def load_results_csv(filename):


    df = pd.read_csv(f"{filename}.csv")
    
    Cost_f = df.loc[0, "Cost_f"]
    
    # Recuperar listas y diccionarios
    Counts = ast.literal_eval(df.loc[0, "Counts"])
    bit_list = ast.literal_eval(df.loc[0, "bit_list"])
    avg_density = ast.literal_eval(df.loc[0, "avg_density"])
    
    return Cost_f, Counts, bit_list, avg_density

