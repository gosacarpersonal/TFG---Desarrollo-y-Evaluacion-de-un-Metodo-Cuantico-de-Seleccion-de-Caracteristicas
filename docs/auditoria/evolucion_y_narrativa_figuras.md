# Evolución y narrativa: última vuelta a las visualizaciones

> 2026-06-15. Tres cosas en un mismo plan: (1) corregir las omisiones detectadas,
> (2) añadir la capa que falta —**evolución del proceso, no solo endpoints**—, y
> (3) contar la historia (foco sobre contexto, caveat de espaguetización). Idea rectora
> del autor: en un TFG así, la evolución del proceso pesa casi como el resultado final.

## Principio: de endpoints a trayectorias

Casi todas las figuras actuales muestran un valor final (macro-F1 tras X, delta final…).
Eso responde "quién gana", pero no "cómo se llega". Las trayectorias responden el "cómo"
y, a menudo, explican el "porqué" mejor que el endpoint. Donde una trayectoria genere
espagueti (muchas líneas), se aplica el patrón del skill: **contexto en gris + una línea
protagonista** (o small multiples), nunca 12 líneas saturadas.

## Qué evolución TENEMOS ya (sin recomputar)

- **α → cardinalidad y coste del óptimo** (`qfs_oracle_*`: `alpha`, `cardinality`, `q_opt`):
  evolución limpia 0→1. (Hoy: F8-A solo cardinalidad; se puede añadir el coste.)
- **β → rendimiento y selección** (`qfs_validation_results`: `beta`, `validation_macro_f1`;
  `qfs_runs_*`: `cost_f`, densidades): evolución del macro-F1 al barrer β. (Hoy F8-B solo
  pinta densidad×β; falta la curva de rendimiento vs β, que es la lectura del paper QFS_D2
  fig 17/18.)
- **Selección a lo largo de la escalera de k** (`fs_all_rankings`: k=1..50; redundancia y
  estabilidad por k): cómo evoluciona la selección al crecer k, por método.
- **Embudo dimensional del pipeline** (`qfs_preselection_summary`: `original_n`→`qfs_n`→
  `k_budget`; + recuentos por fase): la historia del TFG, 500→20→k.
- **Evolución adiabática (el mecanismo)**: Ω(t), Δ_global(t), Δ_local(t) en μs, deterministas
  desde `QFS_Auxiliar_functions.py` (`Omega_global`, `Delta_2step`, `Delta_local_2step`).
  Es la "película" de cómo corre QFS; ilustra el proceso cuántico mejor que cualquier
  endpoint.

## Evolución añadida con re-modelado dirigido

- **Rendimiento vs tamaño del subconjunto** (`ev6_rendimiento_vs_k.csv`): la fase 6 solo
  modeló el k de referencia, así que se añadió un re-modelado acotado, no un re-run completo:
  baseline, `mrmr_approx` y QFS-NA top densidad, usando el `random_forest` y la métrica de
  fase 6 sobre la escalera de k disponible por dataset. Esta EV6 da la curva de rendimiento
  del paper en versión trazable y asumible.

## Figuras de evolución propuestas (última vuelta)

- **EV1 — "Cómo α fija el tamaño y a qué coste"** (mejora de F8-A): doble curva por dataset,
  cardinalidad(α) y coste Q*(α); evolución + el punto donde α da el k de referencia.
  `qfs_oracle_*`. Caveat: QUBO exacto (oráculo), no el simulador.
- **EV2 — "β no es cosmético: mueve el rendimiento"** (mejora de F8-B): curva
  macro-F1(β) en validación por dataset (línea protagonista + contexto), junto al mapa de
  densidad. `qfs_validation_results`. Convierte β de "parámetro" en "palanca con efecto".
- **EV3 — "La selección se estabiliza al crecer k"** (nueva): por método, redundancia
  interna o score acumulado vs k (1..50); **una línea protagonista (mRMR)** sobre las demás
  en gris (caveat espagueti); small multiples si hace falta. `fs_all_rankings`.
- **EV4 — "El embudo: de 500 variables a un puñado"** (nueva, narrativa del TFG): funnel/
  step de la dimensionalidad a lo largo del pipeline (crudo → auditado → seleccionado →
  envolvente QFS) por dataset; cuenta la historia completa de reducción.
  `qfs_preselection_summary` + recuentos por fase.
- **EV5 — "La evolución adiabática de QFS"** (nueva, mecanismo → va a metodología/marco):
  Ω(t), Δ_global(t), Δ_local(t) en μs; el protocolo de dos pasos. Deterministas del solver.
  Es el "cómo funciona por dentro" que hoy no se ve.
- **EV6 — "Rendimiento al crecer el subconjunto"** (implementada): macro-F1 de validación
  vs k para baseline / mRMR / QFS-NA, con small multiples por dataset. Eleva F10 con una
  lectura de trayectoria sin saturar el cuerpo del texto.

## Cómo encaja con el set actual (storytelling)

- F8 deja de ser dos heatmaps sueltos y pasa a **EV1+EV2** (dos evoluciones: α y β con su
  efecto). Mucho más narrativo.
- F5 abandona endpoints y pasa a **EV3** (madurez/redundancia vs k); **EV6** entra junto a
  F10 como curva de rendimiento dirigida.
- Se añade **EV4 (embudo)** al inicio de resultados como hilo conductor, y **EV5
  (adiabática)** a metodología (mecanismo).
- **EV3** entra en la caracterización de selectores (junto a F4) como "la selección madura
  con k".
- En todas: título=hallazgo, protagonista resaltado, contexto gris, ≤3 anotaciones; donde
  haya muchas líneas, highlight-over-context o small multiples.

## Correcciones aplicadas en la pasada final

- **F6:** SHAP de los **5 datasets** en small multiples.
- **A4:** SHAP real por clase de Olive 3 y Olive 9.
- **F3-C:** clave Olive corregida, sin filas vacías.
- **A8:** solape real de variables QFS vs Boruta/mRMR.
- **A9:** macro-F1 vs AUC en binarios, sin etiquetas superpuestas.
- **Menores:** IC en F10; barra de color del panel D de F4; captions LaTeX actualizadas.
