# Decisión: roster clásico "espejo de QFS" (2026-06-13)

## Contexto

El bloque clásico se ejecutó inicialmente con 7 selectores genéricos de sklearn
(`variance, f_classif, mutual_info, mrmr_approx, l1_logistic, random_forest,
linear_svm`). Esa lista NO se corresponde con:

- La investigación previa del autor (documento "18 Métodos Clásicos Finalistas",
  basado en Solorio-Fernández et al. 2020 "A Systematic Evaluation of Filter
  Unsupervised Feature Selection" + el paper QFS).
- La guía explícita del tutor: "para empezar FSFS y MC; también Boruta [...] si
  vas bien de tiempo incluye algún otro algoritmo clásico del paper". Boruta es
  el benchmark gold-standard que QFS debe igualar.

Se corrige con un roster diseñado como **espejo de la estructura de QFS**.

## Principio de selección

QFS optimiza globalmente la función de coste
`Q(x;alfa) = -alfa * sum_i I(x_i;y) * x_i + (1-alfa) * sum_{i<j} I(x_i;x_j) * x_i x_j`,
cuyos dos únicos ingredientes son **relevancia** (información mutua con el target)
y **redundancia** (información mutua entre pares), combinados y resueltos de forma
global. El roster clásico se elige para que cada método aísle o combine esos
ingredientes, más los benchmarks de referencia del campo. Así la comparación es
*atribuible*: permite saber si QFS gana por la relevancia, por el control de
redundancia, por la optimización global o por el benchmark que bate, en lugar de
ser un concurso genérico de selectores.

## Roster definitivo (12 métodos)

| Rol respecto a QFS | Métodos | Justificación |
|---|---|---|
| Baseline mínimo | `variance` | Suelo honesto. CAVEAT: la varianza sobre datos crudos ordena por escala/unidades; se declara como baseline, no como criterio de relevancia. Coincide con el paper UFS (peor método). |
| Relevancia pura (supervisada) | `f_classif`, `mutual_info` | Son el término de relevancia I(x;y) de QFS. `mutual_info` es además una de las dos baselines del paper QFS y la cantidad exacta que QFS codifica en los detunings. |
| Redundancia pura (no supervisada) | `mutual_correlation` (MC), `feature_similarity` (FSFS) | Son el término de redundancia I(x;x) de QFS. Recomendados explícitamente por el tutor. No miran el target. |
| Relevancia + redundancia combinada | `mrmr_approx`, `rrfs` (RRFS) | El análogo clásico directo del objetivo Q(x;alfa): combinan ambos términos de forma voraz/secuencial. mRMR es el rival conceptual principal. |
| Benchmark wrapper | `boruta`, `rfe` | Boruta = benchmark gold-standard del tutor (all-relevant, tamaño determinado por test estadístico, NO por k). RFE = wrapper minimal-optimal (k fijo). |
| Embedded (en contexto de modelo) | `l1_logistic`, `random_forest`, `linear_svm` | Selección como subproducto del entrenamiento; cubren lineal disperso, no lineal por impureza y margen. |

## Métodos nuevos a implementar respecto a la versión de 7

- `mutual_correlation` (MC): eliminación voraz de la variable con mayor
  correlación media con el resto. Implementación propia (Pearson). No supervisado.
- `feature_similarity` (FSFS): clustering de variables por similitud
  varianza-covarianza, un representante por cluster. Implementación propia.
- `rrfs` (RRFS): dos pasos, relevancia (Fisher/varianza) luego poda por
  redundancia (similitud). Implementación propia.
- `boruta`: BorutaPy sobre RandomForest. Produce UN conjunto confirmado por
  dataset (tamaño dado por el test de las shadow features), no una escalera de k.
- `rfe`: `sklearn.feature_selection.RFE`. Produce subconjunto de tamaño k exacto.

## Excluidos deliberadamente (documentar, no ejecutar)

Los filtros espectrales no supervisados (MCFS, Laplacian Score, NDFS, SPEC) y los
bio-inspirados (UFSACO, MGSACO) del documento de 18 quedan FUERA de la ejecución
por coste de implementación/dependencias (scikit-feature) y porque su naturaleza
no supervisada los aleja del eje supervisado QFS. Se citan en el estado del arte
(capítulo 3 de la memoria) como referencia de la literatura UFS, no como
comparadores ejecutados. SUD/SVD-Entropy quedan fuera por inviabilidad
computacional documentada en el paper.

## Implicaciones de tratamiento

- Boruta y RFE no encajan en el molde "ranking -> subconjuntos por k": Boruta se
  compara a su tamaño natural confirmado; RFE al k de referencia. Esto debe
  explicitarse en la narrativa (es un punto metodológico, no un defecto).
- Re-ejecutar fases 5, 6, 7; regenerar handoff y matrices; actualizar memoria
  (4.2 métodos, 5.2 resultados, tabla de comparación final, handoff QFS).
- La estandarización NO se aplica antes de los filtros de varianza/relevancia
  (contrato train-only ya vigente); revisar que cada método nuevo respeta ese
  contrato.

Fuente: documento "18 Métodos Clásicos Finalistas" (Carlos Gómez, 2026-01-01) y
guía del tutor. Paper UFS: docs/papers/A Systematic Evaluation of Filter
Unsupervised Feature Selection.pdf.
