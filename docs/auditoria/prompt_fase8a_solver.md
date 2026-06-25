# Prompt de arreglo — Fase 8a (solver QFS): β + oráculo Q*(α)

Implementa dos extensiones al solver original `QFS_based_on_NA/QFS_Auxiliar_functions.py`
(decisiones aprobadas y respaldadas en `metodologia.tex`, sección método cuántico,
y `conclusiones.tex`).

Fuentes primarias obligatorias: leer y respetar
- `QFS_based_on_NA/QFS_Auxiliar_functions.py` (solver original; no romper).
- `docs/papers/QFS_D2.pdf` §4.4–4.5 (definición de β y ec. 14).
- `docs/papers/2203.13261v2.pdf` (Mücke), Proposición 1 y Algoritmo 1.
- `docs/auditoria/planteamiento_fase_cuantica.md` (plan operativo y restricciones).

NO usar como autoridad los `.md` de `docs/decisions/` ni los worklog generados por IA.
NO modificar `*_OG.py` (son la referencia inmutable).

## Cambio 1 — β en la matriz de distancias

Extender `distance_matrix_from_redundancy(R_ij, d_max, d_min)` y
`arrange_atoms_robust_MDS(R_b, I_i, R_ij, dist_ratio_rydberg, max_iter, n_mds_runs)` para
soportar un nuevo parámetro `beta: float = 0.0`. Cuando `beta == 0.0` el comportamiento
es **exactamente** el actual (no debe cambiar ningún resultado existente). Cuando
`beta > 0`, la distancia base de la eq. del solver se sustituye por

```
d_ij = (1 / R_ij)^(1/6) + beta * (1 + I_i) * (1 + I_j)
```

es decir, eq. 14 de QFS_D2. Reescalar luego al intervalo `[d_min, d_max]` como hace el
código actual. El parámetro `I_i` ya entra por la firma del MDS robusto; basta con
propagarlo a `distance_matrix_from_redundancy`.

Añadir `beta: float = 0.0` también a la firma de `QFS_NA_Solver(...)` y propagarlo a la
construcción de la arquitectura atómica. NO tocar la lógica del driving ni el cálculo
del coste `cost_function(I_i, R_ij, bitstring, alpha)` (que es Q(x;α) puro y no depende
de β).

Criterio de aceptación de C1:
- Con `beta=0.0`, el solver produce las mismas posiciones (salvo aleatoriedad del MDS
  ya presente) y el mismo `Cost_f` que la versión actual sobre un mismo dataset y
  semilla.
- Con `beta=0.5`, las distancias entre pares de alta relevancia (`I_i+I_j` grande)
  aumentan respecto a `beta=0.0`, comprobable inspeccionando `D_matrix` antes del MDS.

## Cambio 2 — Oráculo Q*(α) exacto y recorrido de α (Mücke Algorithm 1)

Añadir en el mismo archivo (o en un módulo nuevo si prefieres, p. ej.
`QFS_based_on_NA/qubo_oracle.py`) dos funciones:

1. `oracle_Q_star(I_i: np.ndarray, R_ij: np.ndarray, alpha: float, k_target: int | None = None) -> tuple[np.ndarray, float]`
   que devuelve `(x_opt, Q_opt)`, el subconjunto que minimiza Q(x;α) en
   `{0,1}^n`. Implementación:
   - Si `n <= 20`, enumeración exhaustiva sobre `2^n` bitstrings reutilizando
     `cost_function`.
   - Si `n > 20`, fallback a Gurobi (`gurobipy` ya importado en QFS_MAIN.ipynb) con
     el modelo cuadrático binario equivalente a Q(x;α).
   - Si `k_target` es no None, restringir además a `||x||_1 == k_target` (suma de
     binarias).

2. `mucke_alpha_for_k(I_i, R_ij, k_target, alpha_low=0.0, alpha_high=1.0, tol=1e-6) -> tuple[float, np.ndarray]`
   que implementa Algoritmo 1 de Mücke (búsqueda binaria sobre α llamando a
   `oracle_Q_star` con `k_target=None` y midiendo `||x*||_1`).

Criterio de aceptación de C2:
- Sobre un dataset pequeño (olive_oil_3class, 8 vars), `mucke_alpha_for_k(..., k_target=5)`
  devuelve un α tal que `||x_opt(α)||_1 == 5`.
- `oracle_Q_star(..., alpha=0.5)` sobre olive_oil_3class produce un `Q_opt` menor o
  igual que el `Cost_f` reportado por `QFS_NA_Solver` con la misma α y entradas.

## Sin tocar (mantener la referencia primaria intacta)

- No modificar `*_OG.py`.
- No cambiar las normalizaciones internas (`normalize_list`, `normalize_matrix`).
- No tocar `cost_function`.
- No tocar el protocolo de driving (`Omega_global`, `Delta_2step`, `Delta_local_2step`).

## Verificación

Añadir `scripts/verify_fase8_solver.py` con tres pruebas: (1) `beta=0.0` reproduce el
solver original sobre olive_oil_3class; (2) `beta=0.5` modifica `D_matrix` como se
espera; (3) `mucke_alpha_for_k` devuelve un k correcto sobre el mismo dataset.

Reportar al final: diff del solver, salida del verify, y dos cifras: tiempo de
`oracle_Q_star` sobre olive_oil_3class y sobre customer_churn (10 vars).
