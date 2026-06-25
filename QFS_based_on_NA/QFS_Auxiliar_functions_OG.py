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

import networkx as nx

from tqdm import tqdm
from sklearn.manifold import MDS
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder

import gurobipy as gp
from gurobipy import GRB

from braket.ahs.atom_arrangement import AtomArrangement, SiteType
from braket.ahs.driving_field import DrivingField
from braket.ahs.local_detuning import LocalDetuning
from braket.ahs.field import Field
from braket.ahs.pattern import Pattern
from braket.tasks.analog_hamiltonian_simulation_quantum_task_result import AnalogHamiltonianSimulationQuantumTaskResult
from braket.ahs.analog_hamiltonian_simulation import AnalogHamiltonianSimulation
from braket.timings.time_series import TimeSeries
from braket.devices import LocalSimulator

from ahs_utils import (
    show_register,
    show_drive_and_local_detuning,
    show_final_avg_density,
    show_global_drive,
)

simulator = LocalSimulator("braket_ahs")


def Delta_2step(t, t_max, Delta_max):
    if t < t_max/2:
        return -Delta_max -Delta_max*np.cos(np.pi*t/(t_max/2))
    else:
        return 0
        
def Delta_local_2step(t, t_max, Delta_local_max):
    if t > t_max/2:
        return Delta_local_max +Delta_local_max*np.cos(np.pi*t/(t_max/2))
    else:
        return 0

def Omega_global(t, t_max, Omega_max):
    return Omega_max*(np.sin((np.pi/2)*np.sin(np.pi*t/t_max)))**2

def QFS_NA_Solver(MI_xy, MI_xx, feature_names, label, E_dist_fraction=0.2, shots = 1000, t = 4, 
                  Omega_max = 15 *1e6, Delta_max =  30 * 1e6, Delta_local_max = 30 * 1e6):
    
    C = 862690 * 2 * np.pi *1e6 # um^6 * rad / us
    alpha = 0.5
    dist_ratio_rydberg=1/np.sqrt(2)
    
    og_weights = normalize_list(MI_xy)

    n_atoms = len(og_weights)
    
    R_ij = normalize_matrix(MI_xx)

    t0 = 0
    time_max = t*1e-6
    
    time = np.linspace(t0, time_max, 100)
    
    omega_array = [Omega_global(t, time_max, Omega_max) for t in time]
    delta_array = [Delta_2step(t, time_max, Delta_max) for t in time]
    delta_local_array = [Delta_local_2step(t, time_max, Delta_local_max) for t in time]
    phi_array = np.zeros_like(omega_array)
    
    omega = TimeSeries()
    for t_step, val in zip(time, omega_array):
        omega.put(t_step, val)
    global_detuning = TimeSeries()
    for t_step, val in zip(time, delta_array):
        global_detuning.put(t_step, val)
    phi = TimeSeries()
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

    print('Rydberg Radius(um) for selected drivings:', R_b)

    print('Computing arrangement...')
    
    min_radius, MDS_dist_matrix, D_matrix, positions, error_matrix = arrange_atoms_robust_MDS(R_b, og_weights, R_ij, dist_ratio_rydberg)
    
    grid_space = min_radius*1e-6
    positions = np.array(positions)*1e-6

    print('Grid spacing computed:', min_radius)
    
    new_x, new_y = positions[:, 0], positions[:, 1]

    V_ij = C/((grid_space*1e6)**6)

    Driving_ratio = Delta_max/V_ij

    print('Driving / Interaction Ratio:', np.sqrt(Omega_max**2 + Delta_max**2)/V_ij)
    print('Detuning / Interaction Ratio:', Driving_ratio)

    new_atoms = AtomArrangement()
    
    for i in range(n_atoms):
        new_atoms.add([new_x[i], new_y[i]])

    print('Visualizing properties...')
        
    Visualize_prop(R_ij, np.array(MDS_dist_matrix), positions, og_weights, error_matrix, label)    

    print('Performing simulation...')

    program = AnalogHamiltonianSimulation(hamiltonian=drive + local_detuning_drive, register=new_atoms)
    result = simulator.run(program, shots=shots, blockade_radius = R_b*1e-6, steps = 40).result()

    counters = result.get_counts()
    gr_list = list(counters.keys())
    Counts = list(counters.values())
    
    bit_list = [[0 if char == 'g' else 1 for char in gr] for gr in gr_list]

    expanded_bit_list = [bit for bit, count in zip(bit_list, Counts) for _ in range(count)]

    ## Primer cálculo de FCoste
    Cost_f = [cost_function(np.array(og_weights), np.array(R_ij), np.array(bit) , alpha) for bit in expanded_bit_list]

    n_top = max(1, int(len(Cost_f) * E_dist_fraction))

    top_indices = np.argsort(Cost_f)[:n_top]

    ## Bitrsings filtrados según FCost
    filtered_bit_list = [expanded_bit_list[i] for i in top_indices]

    ## Aquí se crea una lista con los bistrings unicos y sus cuentas
    filtered_as_tuples = [tuple(bit) for bit in filtered_bit_list]
    bitstring_counts = Counter(filtered_as_tuples)
    bitstring_unicos_list = list(bitstring_counts.keys())
    counts_filtered = list(bitstring_counts.values())

    ## Segundo cálculo de Fcoste
    Cost_f_filtered = [cost_function(np.array(og_weights), np.array(R_ij), np.array(bit), alpha) for bit in bitstring_unicos_list]
    
    avg_density = results_plotter(filtered_bit_list, feature_names, Cost_f_filtered, counts_filtered, label)
    
    #avg_density_2 = results_plotter_v2(filtered_bit_list, feature_names, Cost_f_filtered, counts, gurobi_fcost)

    return Cost_f_filtered, counts_filtered, bitstring_unicos_list, avg_density


def generate_sets_from_density(avg_density, R_ij, feature_names, 
                               max_sets=4, redundancy_threshold=0.7):

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


def arrange_atoms_robust_MDS(R_b, I_i, R_ij, dist_ratio_rydberg=1/np.sqrt(2), max_iter=100, n_mds_runs=100):
    min_d_allowed = dist_ratio_rydberg * R_b
    best_error = np.inf
    best_result = None
    best_dmin_dmax = None

    d_min, d_max = R_b, 4 * R_b
    history = []

    print(f"{'Iter':<5} {'d_min':<10} {'d_max':<10} {'min_radius':<14} {'mean_error':<12}")

    for it in range(max_iter):
        D_matrix = distance_matrix_from_redundancy(R_ij, d_max, d_min)

        best_local_error = np.inf
        best_local_result = None

        # Ejecutar 100 MDS con diferentes random states
        for seed in range(n_mds_runs):
            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=seed)
            positions = mds.fit_transform(D_matrix)

            new_x, new_y = positions[:, 0] * 1e-6, positions[:, 1] * 1e-6
            MDS_dist_matrix = calculate_D_matrix(new_x, new_y)
            min_radius = second_minor(MDS_dist_matrix)

            if min_radius < min_d_allowed:
                continue

            error_matrix = calculate_error_matrix(D_matrix, MDS_dist_matrix)
            avg_error = np.mean(error_matrix)

            if avg_error < best_local_error:
                best_local_error = avg_error
                best_local_result = (min_radius, MDS_dist_matrix, D_matrix, positions, error_matrix)

        # Si ninguno de los MDS cumple el mínimo, ampliar rango
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

    cmap = 'viridis'
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    fig.set_size_inches(15, 12)

    #-----------
    R_plot = ax1.imshow(np.array(R_ij), cmap=cmap)
    fig.colorbar(R_plot,ax=ax1)

    ax1.set_title('Redundancy matrix')

    #-----------    
    D_plot = ax2.imshow(np.array(MDS_dist_matrix), cmap=cmap)
    fig.colorbar(D_plot,ax=ax2)
    ax2.set_title('MDS Distance matrix')

    #-----------
    E_plot = ax3.imshow(np.array(error_matrix), cmap=cmap)
    fig.colorbar(E_plot,ax=ax3)
    ax3.set_title('Relative Error matrix in MDS')

    
    x_vals, y_vals = positions[:, 0], positions[:, 1]
    
    scatter = ax4.scatter(x_vals, y_vals, c=og_weights, cmap='plasma', s=100, zorder=2)

    for i, (x, y) in enumerate(positions):
            ax4.text(x + 1e-6, y + 1e-6, str(i), color='black', fontsize=9,  ha='center', va='center', zorder=3)
        
    # Rejilla
    ax4.grid(True, linestyle='--', color='gray', alpha=0.5)

    ax4.set_aspect('equal')
    ax4.set_title('Atom arrangement')
    plt.colorbar(scatter,ax=ax4)

    fig.suptitle('Pre-simulation properties')
    plt.savefig(f'Results/PRESIMULATION_PROPERTIES_{label}.png', dpi=100)

    plt.show()



def MDS_matrix(n_it, D_matrix):
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


def distance_matrix_from_redundancy(R_ij, d_max, d_min):
    n = np.shape(R_ij)[0]
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
                D[i][j] = dij
                D[j][i] = dij
            min_matrix = second_minor(D)
            max_matrix = np.max(D)
            
        D_matrix = np.round(d_min + ((D - min_matrix) / (max_matrix - min_matrix)) * (d_max - d_min),4)
        np.fill_diagonal(D_matrix, 0)

    return D_matrix

def calculate_error_matrix(M_original, M_pred):
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
    num_puntos = len(x)
    matriz_distancias = np.zeros((num_puntos, num_puntos))
    
    for i in range(num_puntos):
        for j in range(num_puntos):
            dist = 1e6*np.sqrt((x[i] - x[j])**2 + (y[i] - y[j])**2)
            matriz_distancias[i][j] = np.round(dist,4)
    
    return matriz_distancias
    
def cost_function(I_i, R_ij, bitstring, alpha):
    # importance term
    I = - alpha * np.sum(I_i * bitstring)

    # Redundance term
    R = (1 - alpha) * np.sum(R_ij * np.outer(bitstring, bitstring))

    # Q = primer término + segundo término
    Q = I + R

    return Q


def normalize_list(valores):
    min_val = min(valores)
    max_val = max(valores)
    # Evitar la división por cero si todos los valores son iguales
    if min_val == max_val:
        return [0.5] * len(valores)  # Todos los valores serán iguales
    else:
        return [(x - min_val) / (max_val - min_val) for x in valores]

def normalize_matrix(matrix):

    matrix_min = np.min(matrix)
    matrix_max = np.max(matrix)
    
    # Evita la división por cero en matrices con valores constantes
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
    
    plt.figure(figsize=(20, 20))

    bit_array = np.array(bit_list)  # shape (N, 15)

    avg_density = bit_array.mean(axis=0)  # array de 15 elementos
    
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

    plt.savefig(f'Results/SIMULATION_RESULTS_{label}.png', dpi=100)

    plt.show()

    return avg_density



import pandas as pd

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

import pandas as pd
import ast

def load_results_csv(filename):

    df = pd.read_csv(f"{filename}.csv")
    
    Cost_f = df.loc[0, "Cost_f"]
    
    # Recuperar listas y diccionarios
    Counts = ast.literal_eval(df.loc[0, "Counts"])
    bit_list = ast.literal_eval(df.loc[0, "bit_list"])
    avg_density = ast.literal_eval(df.loc[0, "avg_density"])
    
    return Cost_f, Counts, bit_list, avg_density

