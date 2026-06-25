# Hallazgos de la revisión a fondo de docs/papers (2026-06-13)

Revisión completa de QFS_D2.pdf, "Feature Selection on Quantum Computers"
(Mücke et al., = 2203.13261), "A Systematic Evaluation of Filter Unsupervised
Feature Selection" (Solorio-Fernández et al. 2020) y la decisión olive oil.
Cosas que NO teníamos bien y que cambian teoría/decisiones.

## 1. alfa controla el NÚMERO de variables (Mücke, Proposición 1) [CRÍTICO]

En la formulación QUBO Q(x;alfa), recorrer alfa de 0 a 1 hace crecer de forma
monótona el número de variables seleccionadas, de 0 a p, en pasos de 1. Para cada
k existe un alfa cuyo óptimo tiene exactamente k variables; NO hace falta
penalización de cardinalidad. Implicación: alfa no es "un balance que se calibra a
un valor único" (como decía la memoria); es el mecanismo que recorre la escalera
de presupuestos k. Corregido en marco_teorico 2.2 y metodologia 4.4.

## 2. Hay DOS parámetros: alfa y beta [CRÍTICO]

- alfa: en el coste QUBO, controla k (punto 1).
- beta (QFS_D2 eq 14): término aditivo en la distancia,
  d_ij = (C6/R_ij)^(1/6) + beta*(1+I_i)(1+I_j). Separa variables de alta
  relevancia para que dos importantes pero redundantes no caigan en el mismo
  volumen de bloqueo. En QFS_D2 es el knob empírico que barren de 0 a 1.
La memoria solo mencionaba alfa. Corregido en metodologia 4.4 (codificación y
contrato): ambos se barren y se fijan en validation.

## 3. El método produce un RANKING (densidades de Rydberg), no un subconjunto directo

Sobre átomos neutros se mide la densidad de Rydberg media de las configuraciones
de menor energía -> ranking de variables -> top-k. (El QUBO puro de Mücke da un
subconjunto directo; la versión neutral-atom da ranking.) Corregido en 4.4.

## 4. Estimador de MI: discretizado (referencia) vs sklearn k-NN (nuestro handoff) [SE ARREGLA EN LA RE-EJECUCIÓN DE FASE 5]

Verificado en el código real. La implementación de referencia
(QFS_based_on_NA/Data_functions.py::MI_complete_det y calculate_mutual_info_matrix)
DISCRETIZA las continuas con KBinsDiscretizer(n_bins=5, encode='ordinal',
strategy='uniform') y calcula la MI sobre los datos binados; además filtra por
umbral (MI>0.001) y normaliza min-max. NOTA: el paper *escrito* (Mücke) dice
cuantiles, pero el *código* usa uniforme de 5 bins; lo que QFS consume lo decide
el código -> uniforme 5 bins es la referencia correcta. Nuestro handoff
(src/fase5_feature_selection.py::calcular_mi_relevancia) usaba
mutual_info_classif(..., discrete_features=False) sobre datos CRUDOS = estimador
k-NN (Kraskov). Son cantidades distintas.
DECISIÓN: un solo estimador de MI en toda la fase 5 — discretizar 5 bins uniforme
sobre train, MI sobre datos binados — usado por mutual_info, mrmr_approx, rrfs
(término de relevancia) Y el handoff I_i/R_ij. Así la frase de la memoria ("el
método cuántico consume exactamente las mismas cantidades que los clásicos") es
literalmente cierta. Solo binar continuas (nunique>10); las categóricas/discretas
ya cuentan como discretas. Fit del discretizador en train (contrato train-only).
No adoptar el umbral-drop de la referencia (queremos todas las features del
candidato). Verificar convención de normalización contra el solver en el smoke
test de fase 8 (no doble-normalizar). Esto CAMBIA legítimamente los resultados de
mutual_info y mrmr_approx respecto a su versión k-NN; f_classif, variance,
l1_logistic, random_forest, linear_svm NO se ven afectados. Memoria 4.3 corregida
(dice "cinco intervalos uniformes").

## 5. Boruta sobreestima el nº de variables (QFS_D2 4.5.3) [REFUERZO]

El AUC se estabiliza más allá de ~7 variables; QFS iguala a Boruta con menos
features y en Oral Cancer lo supera. Refuerza: (a) Boruta como benchmark del
roster, (b) los presupuestos k pequeños, (c) la narrativa del TFG. Añadido a
estado_arte 3.4.

## 6. Mücke es el ORIGEN exacto de Q(x;alfa) [REFUERZO DE LINAJE]

Eq 2 de Mücke = eq 6 de PAPER_QFS = nuestra eq 4.1. Linaje: Mücke (QUBO-FS
genérico, gate/annealer) -> grupo (misma QUBO sobre Rydberg). Explicitado en 2.2 y 3.4.

## 7. Datasets del grupo y solape [REFUERZO]

PAPER_QFS: Adult, Bank Marketing, Telco Churn. QFS_D2: Telco Churn, Oral Cancer.
Nuestro Customer Churn SOLAPA con el suyo -> comparabilidad directa. Madelon (500)
y olive multiclase son extensiones genuinas (ellos solo binarios <=20 vars).

## 8. La estandarización neutraliza variance (Solorio 3.1) [REFUERZO BASELINE]

En la review UFS estandarizan todo (media 0, sd 1) y variance es el peor método:
con sd=1 la varianza es ~constante, el ranking es casi aleatorio. En nuestro
pipeline variance se calcula sobre train crudo (ordena por escala). En ambos casos
es un baseline degenerado -> confirma tratarlo como "suelo" con caveat, nunca como
criterio. Coherente con roster_clasico_espejo.md.

## 9. Confirmaciones del roster (Solorio) [REFUERZO]

MC: supervisado o no supervisado, eliminación voraz por correlación media. FSFS:
clustering por similitud varianza-covarianza, un representante por cluster. RRFS:
dos pasos, relevancia (MI en modo supervisado) + poda por redundancia. Las tres
implementaciones propias del roster-espejo quedan validadas contra la fuente.
