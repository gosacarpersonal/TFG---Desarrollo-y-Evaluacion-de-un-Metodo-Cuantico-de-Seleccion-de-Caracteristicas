# Huecos: promesa vs entrega — 2026-06-21

Auditoría de lo que la memoria **afirma al principio** frente a lo que
**realmente muestra** después. Detonada por la observación de Carlos: el plano
relevancia-redundancia de los 12 métodos + QFS, y "dónde gana cada dataset
(clásico y cuántico): velocidad, puntuación...". Todo el dato necesario **ya
existe** en `results/tables/` (no hay que reentrenar).

## HUECO 1 — El plano relevancia-redundancia prometido NO se entrega [ALTA]

**Promesa (literal):**
- `metodologia.tex` 164–172: *"Esta taxonomía permite leer los doce métodos como
  un sistema de coordenadas... En el capítulo de resultados, **QFS se situará en
  este plano** comparando tanto **coordenadas agregadas (relevancia capturada y
  redundancia interna)** como subconjuntos por nombre de variable."*
- `resultados.tex` 226: *"se caracteriza qué selecciona cada método **en el plano
  relevancia-redundancia**"*.

**Entrega real:** `F04_perfil_selectores` = redundancia interna, coste,
estabilidad y separación frente al nulo. **No es el plano relevancia-redundancia
y QFS no aparece en él.** QFS solo aparece después en solape Jaccard
(`explor_mapa`, `a8`) y en su handoff `I_i`/`R_ij` (`a6`) — nunca en el plano de
coordenadas prometido con los 12 + QFS juntos.

**Propuesta:** figura nueva **"Plano relevancia-redundancia: los 12 + QFS por
dataset"**. Scatter por dataset: x = redundancia interna del subconjunto, y =
relevancia capturada; cada selector un punto, **QFS-NA y oráculo resaltados**.
Entrega la promesa textual y, de paso, enriquece QFS (lo sitúa en sus propias
coordenadas nativas, las del QUBO).

**Datos:** redundancia → `fs_selected_redundancy_summary.csv`
(`selected_mean_abs_corr`, 168 filas); relevancia capturada → `I_i` de las
seleccionadas (`fs_qfs_mi_target_vector__*` + `fs_selection_vs_eda_evidence.csv`,
`selected`); QFS → `qfs_selected_*`.

## HUECO 2 — "Dónde gana cada dataset" (ventajas de la selección) no está consolidado [MEDIA]

**Promesa:** la memoria vende las ventajas de la selección desde el inicio —
`introduccion` 16 (*"reduciendo dimensionalidad, redundancia y coste"*),
`marco_teorico` 19–21 (*menos coste, modelos más interpretables, menor
sobreajuste*). Pero esas ventajas (velocidad, puntuación, reducción de
dimensión, redundancia) **nunca se muestran juntas por dataset**.

**Entrega real:** dispersa — coste en `F04`, puntuación final en `F10`,
reducción solo como número suelto. El lector no ve, de un vistazo, *qué compra*
la selección en cada dataset frente a usar todas las variables.

**Propuesta:** figura/tabla **"Qué gana cada dataset"** — por dataset, para el
**mejor clásico y QFS** frente al baseline: Δ macro-F1, reducción de variables
(%), aceleración (×), Δ redundancia. Un panel o scorecard por dataset.

**Datos:** `modeling_cost_performance.csv` (260: `macro_f1`, `fit_seconds`,
`feature_reduction_ratio`, `delta_macro_f1_vs_same_model_baseline`,
`n_features_used`) + `qfs_operational_summary.csv` / `qfs_model_results.csv`.

## HUECO 3 — QFS es el protagonista pero su despliegue es desigual [MEDIA]

QFS es el método bajo estudio (la comparación es *con lo cuántico*), así que
merece densidad proporcional. Hoy en el cuerpo: `F08` (mandos α/β), `F09`
(atribución), `qfs_organismo` (MDS) + 5 tablas. Es sustancial, pero:

- El **barrido de β** se colapsa a un punto en el cuerpo; la curva completa vive
  en apéndice. Para el protagonista, conviene la **curva macro-F1 vs β** visible.
- QFS no aparece en el **plano relevancia-redundancia** (Hueco 1) — su hábitat
  natural.
- Falta una lectura de **comportamiento de QFS por dataset** ligada a su régimen
  (dónde el criterio funciona y dónde el optimizador falla), que conecte `F09`
  con la geometría (`qfs_runs_*`, densidades de Rydberg).

**Propuesta:** asegurar en el cuerpo la curva β, la posición de QFS en el plano
(Hueco 1), y una síntesis por dataset del régimen QFS. Datos:
`qfs_validation_results.csv`, `qfs_oracle_*`, `qfs_runs_*`.

## Otros huecos menores a verificar

- `introduccion` 90 promete evaluación multidimensional ("estabilidad,
  redundancia interna, interpretabilidad, coste") → mayormente cubierto por
  `F04` + SHAP, pero **interpretabilidad** solo se muestra para algunos datasets
  (SHAP en Olive/BC); revisar cobertura.
- "subconjuntos por nombre de variable" (metod. 172) → parcial (`a3` roster,
  `o1`); el roster `a3` además está entre las figuras a reconstruir.

## Impacto en el reparto cuerpo/apéndice

Añadir al **cuerpo**:
- ➕ Figura **Plano relevancia-redundancia (12 + QFS)** — entrega Hueco 1.
- ➕ Figura/tabla **"Qué gana cada dataset"** — entrega Hueco 2.
- ➕ Curva **macro-F1 vs β** visible (Hueco 3) — o consolidar en F08.

Con esto el cuerpo añadiría ~2–3 piezas más sobre las ya acordadas (campo de
validación + posición de QFS). Todas con dato existente.
