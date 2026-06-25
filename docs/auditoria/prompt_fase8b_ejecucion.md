# Prompt de arreglo — Fase 8b (ejecución QFS): pre-selección + barrido (α, β)

Construye `notebooks/fase8.ipynb` y su generador `scripts/rebuild_fase8_notebook.py`
siguiendo la estructura canónica (`docs/auditoria/estructura_notebooks.md`) y respetando
todos los criterios de `docs/auditoria/planteamiento_fase_cuantica.md`.

Requisito previo: Fase 8a (`prompt_fase8a_solver.md`) completada y verificada.

## Insumos

- `Iᵢ` y `Rᵢⱼ` por dataset, sin normalizar y con discretización 5 bins uniforme,
  generados por fase 5 (`results/tables/05_feature_selection/...`). El solver normaliza
  por su cuenta; no normalizar dos veces.
- Splits cerrados de fase 4.

## Sección 8.1 — Pre-selección híbrida para datasets que superan la envolvente

Envolvente operativa del simulador: ≤ 20 átomos. Aplicar pre-selección clásica solo
con `train`, declarándola como método híbrido en el cuaderno:

| Dataset | n_vars original | Entra a QFS | Pre-selector |
|---|---|---|---|
| olive_oil_3class | 8 | 8 (directo) | — |
| olive_oil_9class | 8 | 8 (directo) | — |
| customer_churn | 10 | 10 (directo) | — |
| breast_cancer_wisconsin | 30 | 20 | `mrmr_approx` (importado de `src/fase5_feature_selection.py`) |
| madelon | 500 | 20 | `mrmr_approx` |

Razón documentada en el cuaderno: mrmr es el análogo voraz directo del criterio QFS
(combina relevancia y redundancia), por lo que la pre-selección es coherente con el
criterio cuántico y no introduce un sesgo extraño.

## Sección 8.2 — Ejecución operativa (α=0.5, código original)

Para cada dataset, ejecutar `QFS_NA_Solver(MI_xy, MI_xx, feature_names, label,
E_dist_fraction=0.1, shots=10000, t=4, beta=β)` para cada `β ∈ {0, 0.1, 0.2, …, 1.0}`.
Hereda α=0.5 fijo del solver original (no es decisión del cuaderno).

Guardar por cada `(dataset, β)`: densidades de Rydberg, bitstrings filtrados, `Cost_f`.
Derivar el subconjunto top-k para cada k del presupuesto (`k=5` en olive×2; `k=10` en
los demás).

## Sección 8.3 — Control de calidad: oráculo Q*(α) exacto

Para cada dataset (post pre-selección), recorrer α∈{0.0, 0.1, …, 1.0} llamando a
`oracle_Q_star(I_i, R_ij, alpha)` (de fase 8a). Reportar por α: cardinalidad ||x*||_1,
`Q_opt` y bitstring óptimo. Adicionalmente, para cada k del presupuesto, llamar a
`mucke_alpha_for_k(I_i, R_ij, k_target=k)` y guardar el `(α*, x*_k)` resultante.

Comparar el subconjunto del simulador analógico (con α=0.5 fijo y top-k sobre densidad
de Rydberg) contra `x*_k` del oráculo:
- **Distancia de Hamming** entre ambos vectores binarios.
- **Δcoste** `Q(x_NA; 0.5) − Q(x*; 0.5)`.

Esta comparación es el control declarado en `metodologia.tex` sec:contrato y separa
"calidad del optimizador analógico" de "calidad del criterio QUBO".

## Sección 8.4 — Selección de (α, β) por validation

Para cada dataset, evaluar **en validation** (con el primer modelo del banco, p. ej.
random_forest, para no encarecer) el macro-F1 del subconjunto obtenido por cada
combinación válida:
- Operativo: top-k por densidad sobre cada `β`.
- Oráculo: `x*_k` de `mucke_alpha_for_k` (independiente de β, dado que el oráculo
  optimiza Q(x;α) sin término de embedding).

Elegir, por dataset, el `(α*, β*)` operativo que maximiza macro-F1 en validation,
con desempate por balanced_accuracy y por compacidad. Registrar también el subconjunto
del oráculo como configuración separada.

## Artefactos a guardar

- `results/tables/08_quantum/qfs_runs_{dataset}_{beta}.csv` (densidades, bitstrings).
- `results/tables/08_quantum/qfs_oracle_{dataset}.csv` (recorrido de α y x*).
- `results/tables/08_quantum/qfs_quality_control_{dataset}.csv` (Hamming y Δcoste).
- `results/tables/08_quantum/qfs_selected_{dataset}.csv` (subconjuntos finales por
  configuración para fase 8c).
- `results/figures/08_quantum/qfs_beta_map_{dataset}.png` (mapa β × k, análogo a
  fig. 17/18 de QFS_D2).

## Verificación

`scripts/verify_fase8_ejecucion.py`: comprobar que para cada dataset existen los
artefactos esperados, que los subconjuntos tienen el k correcto y que la pre-selección
híbrida en bcw y madelon dejó exactamente 20 variables.

Estructura del cuaderno: respeta la canónica de 1-4 (markdown sección → funciones
visibles inline → por dataset → narrativa por dataset → síntesis). NO esconder en `src`
el cálculo del control de calidad ni el barrido — debe verse construir.
