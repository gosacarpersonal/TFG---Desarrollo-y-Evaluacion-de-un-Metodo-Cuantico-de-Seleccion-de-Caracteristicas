# Roadmap de cambios por fase y cierre del bloque clásico-cuántico

> 2026-06-14. Síntesis final tras la auditoría completa contra fuentes primarias
> (PAPER_QFS, QFS_D2, Mücke 2023, Solorio 2020 y `QFS_based_on_NA/`).
> Este documento es el plan de trabajo final: qué tocar, en qué orden, qué NO tocar y
> cómo queda definida la fase cuántica para que la comparación clásico↔cuántico cierre
> sin huecos argumentales.
>
> Criterios guía: (1) mínimo cambio, máximo valor; (2) respetar la estructura canónica
> de 1-4 (`estructura_notebooks.md`); (3) anclar todo en fuentes primarias; (4) garantizar
> coherencia código↔notebook↔memoria; (5) no prometer lo que el solver original no
> permite (β, α↔k vía oráculo).
>
> **Estado de las tres decisiones de diseño (aprobadas 2026-06-14):**
> - **T2.1 XGBoost** en fase 6 → APROBADO (memoria LaTeX ya actualizada).
> - **T4.1 β** implementado en el solver → APROBADO (memoria LaTeX ya actualizada).
> - **T4.2 oráculo $Q^*(\alpha)$ exacto + recorrido de α** → APROBADO (memoria LaTeX ya
>   actualizada).
>
> Las tres decisiones están ya respaldadas en `metodologia.tex` (protocolo de modelado,
> sección del método cuántico) y `conclusiones.tex` (trabajo futuro), con citas a
> `chen2016` (XGBoost), `mucke2023` (Proposición 1 + Algorithm 1) y `orquin2026`
> (implementación del grupo).

## Roadmap por tier

El orden refleja dependencias y coste/beneficio. Cada tier es autocontenido: se puede
parar al final de un tier y la siguiente sesión tiene un estado consistente.

### Tier 1 — Correctitud crítica (bloque clásico)

**Objetivo:** eliminar los dos defectos ALTOS de correctitud antes de tocar nada más.

- **T1.1 [Fase 6 — SHAP real].** Reescribir `shap_candidato` y `plot_shap_dataset` en
  `src/phase6_modeling/pipeline.py` para (a) persistir la matriz SHAP cruda (signo, por
  instancia, por clase) en disco; (b) sustituir el `sns.barplot` actual por un
  `shap.summary_plot` (beeswarm) por modelo-dataset; (c) desglose por clase en olive 3/9.
  Re-ejecutar solo fase 6 SHAP, no todo el modelado.
- **T1.2 [Fase 6 — desempate neutral].** Eliminar `SELECTOR_TIE_PRIORITY_BY_DATASET`
  (líneas 53-63) y sustituir por desempate alfabético sobre `selector`. Comprobar que
  la selección de candidatos a test no cambia de forma que invalide conclusiones;
  documentar en el cuaderno.
- **T1.3 [Fase 5 — regenerar].** Regenerar `notebooks/fase5.ipynb` desde el script ya
  corregido (variance/MC/FSFS narrativa coherente con código). Verificar con
  `verify_fase5_notebook.py`.

**Re-ejecuciones:** fase 6 SHAP (rápido, no toca entrenamiento). Fase 5 solo regenera
notebook (no re-ejecuta selectores).

### Tier 2 — Estructura paso 2 y ancla de comparabilidad

**Objetivo:** cerrar los dos huecos estructurales/metodológicos restantes.

- **T2.1 [Fase 6 — añadir XGBoost].** Recomendado. Añadir XGBoost al protocolo
  (`MODEL_NAMES`) como cuarto modelo, manteniendo logistic+SVM+RF y macro-F1. Esto crea
  el ancla de comparabilidad cuantitativa con PAPER_QFS y QFS_D2 que hoy falta. Coste:
  ~25 % más experimentos (4 modelos × 12 selectores × 5 datasets = 240 validation).
  Acoplado a T2.2 (re-ejecutar fase 6 implica re-ejecutar SHAP de T1.1; agruparlos).
- **T2.2 [Fase 5/6/7 — paso 2 de la estructura].** Subir al cuaderno la creación visible
  del núcleo metodológico (no a `src`):
  - Fase 5: mostrar las funciones de los selectores espejo de QFS (relevancia $I(x;y)$,
    redundancia $I(x;x)$, mrmr/rrfs). Es ~100 líneas de código adicional.
  - Fase 6: mostrar el cálculo SHAP (post T1.1) y la regla del contraste estadístico.
  - Fase 7: mostrar la regla de decisión del veredicto final (delta/IC/p-valor).
- **T2.3 [Fase 7 — verificar `UMBRAL_EFECTO_PRACTICO`].** Comprobar definición y
  justificación; si es número mágico, justificarlo en el cuaderno y la memoria.

### Tier 3 — Limpieza editorial (fases 1-4)

**Objetivo:** pulir la presentación sin tocar la estructura ni la metodología.

- **T3.1 [Fase 1].** Minimizar `COLUMNAS_PRESENTACION` (~100 entradas de renombrado de
  presentación): aplicar el renombrado localmente a cada tabla, no como muro inicial.
- **T3.2 [Fase 2].** Trocear la celda de funciones de 222 líneas (sección 2.9). Funciones
  más pequeñas, todas visibles inline. Pendiente fichado en worklog.
- **T3.3 [Fases 1 y 3 — heatmaps duplicados].** Para `01_08_asociacion`, `01_11_redundancia`,
  `fase3_asociacion`, `fase3_redundancia`: eliminar las que solo repiten la tabla o
  transformar en clustermap/umbral que aporte algo que la tabla no.
- **T3.4 [Fase 4 — matiz chi²].** Reforzar la nota de que el chi² entre splits
  estratificados es coherencia, no test de hipótesis informativo.

### Tier 4 — Fase cuántica (fase 8)

**Objetivo:** ejecutar QFS sobre el bloque clásico cerrado y comparar con homogeneidad.

Detalles en la sección «Definición de la parte cuántica» más abajo. Resumen del orden:

- **T4.1.** Implementar β (QFS_D2 eq 14) en `arrange_atoms_robust_MDS` /
  `distance_matrix_from_redundancy` del solver. ~10 líneas; si se decide renunciar,
  ajustar `conclusiones.tex`.
- **T4.2.** Implementar el oráculo $Q^*(\alpha)$ exacto (enumeración para $n\le 20$, o
  Gurobi como QFS_D2 §4.3) y el barrido de α de Mücke Algorithm 1. Es el control de
  calidad declarado en `metodologia.tex:234-243`.
- **T4.3.** Pre-selección híbrida: bcw 30→20 y madelon 500→20 con `mrmr_approx`
  (declarado). Olive y churn entran directos.
- **T4.4.** Ejecutar QFS con $\alpha=0.5$ fijo (operativo, como el código original) **y**
  con $\alpha$ recorrida vía oráculo (control). Barrer β∈[0,1] paso 0.1.
- **T4.5.** Evaluación con el protocolo exacto de fase 6 (mismos modelos, macro-F1,
  bootstrap, permutaciones), reutilizando las predicciones por fila ya archivadas.
- **T4.6.** Comparación final (extensión natural de fase 7): el QFS aparece como una fila
  más en cada veredicto por dataset, con el mismo criterio de mejora significativa.

## Qué NO hacer (decisiones explícitas)

- **No** mover las funciones inline de fases 1-4 a `src`: son la estructura preferida.
- **No** hacer los cuadernos más delgados; al contrario, en 5-7 el núcleo se sube.
- **No** inventar métodos clásicos fuera del roster de 12.
- **No** sustituir macro-F1 por AUC en el protocolo de fase 6/7. AUC se cita solo como
  contexto del paper y se reproduce únicamente como métrica secundaria si se decide
  añadir XGBoost (incluso entonces, decisión primaria sigue siendo macro-F1).
- **No** introducir validación cruzada anidada (la propuesta acepta partición única).
- **No** tocar el preprocesado ni los splits (cerrados y auditados).
- **No** prometer en la memoria capacidades del solver no implementadas (ya corregido).

## Definición de la parte cuántica (fase 8)

### Solver y parámetros

| Pieza | Decisión | Origen |
|---|---|---|
| Solver | `QFS_NA_Solver` (`QFS_Auxiliar_functions.py`) sobre simulador AHS de Braket | Código original del grupo |
| α (operativo QFS-NA) | **0.5 fijo**; k se obtiene por **top-k sobre densidad de Rydberg media** | `QFS_NA_Solver:95` |
| α (control de calidad) | **Recorrer α∈[0,1] vía Algorithm 1 de Mücke** con oráculo exacto $Q^*(\alpha)$ | Mücke Prop. 1 + Algorithm 1 |
| β | **Implementar QFS_D2 eq 14** (`d_ij = (C_6/R_{ij})^{1/6} + \beta(1+I_i)(1+I_j)`); barrer β∈{0, 0.1, …, 1.0}; **elegir β por validation** | QFS_D2 §4.5 |
| Discretización del MI | KBinsDiscretizer 5 bins uniforme (heredada de fase 5) | `Data_functions.py::MI_complete_det` |
| Normalización | Solver normaliza por su cuenta (`normalize_list`, `normalize_matrix`); fase 5 entrega sin normalizar | `QFS_Auxiliar_functions.py:98,103,555-575` |
| Shots / E_dist_fraction / t | 10 000 / 0.1 / 4 μs (heredados del original) | `QFS_MAIN.ipynb` cell 14 |
| MDS | `n_mds_runs=100` (heredado) | `arrange_atoms_robust_MDS:276` |

### Datasets y envolvente operativa

| Dataset | n_vars | Entra a QFS | Pre-selección |
|---|---|---|---|
| olive_oil_3class | 8 | Directo | — |
| olive_oil_9class | 8 | Directo | — |
| customer_churn | 10 | Directo | — |
| breast_cancer_wisconsin | 30 | Tras pre-selección | mrmr_approx (30→20) |
| madelon | 500 | Tras pre-selección | mrmr_approx (500→20) |

Justificación: la envolvente de ~20 átomos es la documentada en
`metodologia.tex:218-232` y coincide con la práctica de PAPER_QFS y QFS_D2. mrmr es el
análogo voraz directo del objetivo QFS, así que la pre-selección es coherente con el
criterio cuántico (no introduce un sesgo extraño). Esto define un **método híbrido**
declarado.

### Presupuestos k

Idénticos a fase 6: $k=10$ en bcw (post-preselección), churn y madelon
(post-preselección); $k=5$ en olive×2. Justificado por el plateau >7 vars de PAPER_QFS y
por la dimensionalidad de cada dataset.

### Control de calidad QUBO exacto

Para cada α del recorrido (T4.2), comparar el subconjunto QFS-NA contra el óptimo de
$Q(x;\alpha)$ obtenido por enumeración exhaustiva (cabe en ≤20 vars) o Gurobi. Se
reportan:

- **Distancia de Hamming** entre la solución de QFS-NA y la óptima.
- **Δcoste** $Q(x_{NA};\alpha) - Q(x^*;\alpha)$.

Esto separa dos preguntas que la comparación final no debe confundir (anunciado en
`metodologia.tex:234-243`): si el simulador analógico optimiza bien su criterio, y si
ese criterio produce subconjuntos predictivos.

### Protocolo de evaluación (estricto)

Idéntico al de fase 6 (`metodologia.tex:355-400`):

- Modelos: logistic_regression, linear_svm, random_forest (+xgboost si T2.1 se acepta).
- Métrica primaria: macro-F1; secundaria: balanced_accuracy.
- Predicciones por fila archivadas → comparación pareada QFS↔baseline sobre las mismas
  filas (reutilizando lo guardado por fase 6, sin reentrenar baselines).
- Bootstrap 400, permutación signos 2 000, permutación etiquetas 500.
- Veredicto por dataset con la misma regla de fase 7 (delta + IC + p pareado con
  FDR/Holm + permutación de etiquetas).

### Selección de hiperparámetros de QFS

Solo con `validation`. Se barre $(α, β)$ y se elige el $(α^*, β^*)$ por dataset que
maximiza macro-F1 en validation, con desempate por balanced_accuracy y por compacidad
($k$ menor). `test` se consulta una sola vez sobre $(α^*, β^*)$ fijados.

### Output esperado

- Tabla maestra cuántica análoga a la de fase 7 (un candidato QFS por dataset y k, con
  IC bootstrap, p pareado vs baseline, p label-perm).
- Mapas $\beta$ × $k$ por dataset (análogos a fig. 17/18 de QFS_D2).
- Distancia al óptimo QUBO por α (control de calidad).
- Veredicto QFS por dataset, integrado en la tabla final de fase 7 extendida.

## Cuadro de cierre: métodos, modelos, métricas, k, α, β

Este es el contrato definitivo del bloque, anclado en fuentes primarias.

### Métodos clásicos (roster espejo de QFS)

| Rol | Método | Justificación primaria |
|---|---|---|
| Baseline degenerado | `variance` (sobre estandarizado) | Solorio 2020 |
| Relevancia pura | `f_classif`, `mutual_info` | PAPER_QFS eq 6 (término $I_i$) |
| Redundancia pura (espejo estructural, no top-performer) | `mutual_correlation` (MC), `feature_similarity` (FSFS) | PAPER_QFS eq 6 (término $R_{ij}$) + Solorio |
| Combinado relevancia–redundancia | `mrmr_approx`, `rrfs` | Análogo voraz directo de $Q(x;\alpha)$ |
| Wrappers | `boruta` (gold-standard), `rfe` | PAPER_QFS §V.C + tutor |
| Embedded | `l1_logistic`, `random_forest`, `linear_svm` | Cobertura de familias |

### Modelos de evaluación

- **Decisión recomendada:** logistic_regression + linear_svm + random_forest **+
  xgboost** (T2.1 aceptado). RF coincide con `QFS_MAIN.ipynb`; XGBoost coincide con
  PAPER_QFS y QFS_D2. Logistic y SVM extienden la cobertura de familias y son
  baselines defendibles. Hiperparámetros fijos, pesos balanceados.
- **Si T2.1 no se acepta:** mantener los tres actuales y declarar la divergencia como
  está hoy (`metodologia.tex` ya corregida en esta sesión).

### Métricas

- **Primaria:** macro-F1 (multiclase + desbalance).
- **Secundaria (desempate):** balanced_accuracy.
- **Incertidumbre:** IC 95 % por bootstrap (400 remuestreos) sobre predicciones.
- **Significancia:** permutación de signos pareada (2 000) + permutación de etiquetas
  (500), corregidas por FDR Benjamini-Hochberg y Holm.
- **AUC-ROC:** solo como métrica de contexto frente al paper (en binarios, si XGBoost
  entra). NO sustituye a macro-F1.

### Presupuestos k

| Dataset | k |
|---|---|
| olive_oil_3class | 5 |
| olive_oil_9class | 5 |
| customer_churn | 10 |
| breast_cancer_wisconsin | 10 (post pre-selección 30→20) |
| madelon | 10 (post pre-selección 500→20) |
| Boruta (cualquier dataset) | tamaño confirmado por el método (no recortado) |

Justificación primaria: plateau >7 vars (PAPER_QFS §VI) y ventaja de QFS en subconjuntos
compactos (PAPER_QFS, QFS_D2 §4.5.3).

### α — dos lecturas, una contradicción ya aclarada en LaTeX

- **α en el QUBO puro (Mücke):** $\alpha\leftrightarrow k$ monótono (Proposición 1).
  Mecanismo operativo: Algorithm 1 (búsqueda binaria sobre α con oráculo $Q^*$).
- **α en QFS-NA (código del grupo):** $\alpha=0.5$ **fijo**; k vía top-k sobre densidad
  de Rydberg. **No** se usa el mecanismo de Mücke en la implementación neutral-atom.
- **En el TFG:** se ejecuta lo operativo ($\alpha=0.5$ + top-k) **y** se reproduce el
  oráculo $Q^*(\alpha)$ como control de calidad. El matiz ya está en
  `metodologia.tex` (esta sesión).

### β — segundo grado de libertad

- **Definición primaria:** $d_{ij} = (C_6/R_{ij})^{1/6} + \beta(1+I_i)(1+I_j)$
  (QFS_D2 eq 14). Separa variables de alta relevancia para evitar que dos importantes
  pero redundantes caigan en el mismo volumen de bloqueo.
- **Estado en el código del grupo:** **no implementado** en `QFS_Auxiliar_functions.py`.
- **Decisión:** **implementarlo** (T4.1, ~10 líneas) y barrer β∈[0,1] paso 0.1, como
  QFS_D2 fig. 17/18. Si se renuncia, ajustar `conclusiones.tex` (hoy lo anuncia).

## Cómo encaja todo en la fase cuántica (vista de cierre)

1. Fase 5 produce, sin normalizar, $I_i$ y $R_{ij}$ por dataset con discretización 5
   bins uniforme (`fase5_feature_selection.py:313` lo deja explícito). Estos son los
   **únicos** insumos cuánticos. La frase "QFS consume las mismas cantidades que los
   clásicos" (`metodologia.tex:172-175`) queda **literal**: los selectores `mutual_info`,
   `mrmr_approx` y `rrfs` consumen exactamente esos $I_i, R_{ij}$.

2. Fase 6 produce la **referencia clásica** sobre macro-F1 con los mismos modelos y
   contrastes que usará QFS. Sus predicciones por fila se archivan para que la
   comparación pareada con QFS no necesite reentrenar nada.

3. Fase 7 produce el **veredicto clásico** por dataset con la regla de decisión
   delta+IC+p-FDR/Holm. Esa misma regla se aplicará al QFS para que el veredicto
   cuántico tenga el mismo umbral.

4. Fase 8 ejecuta QFS-NA, calibra $(α, β)$ con validation, evalúa en test bajo el
   protocolo de fase 6, controla la calidad del optimizador contra $Q^*(\alpha)$ exacto
   y produce su veredicto. Se integra como **una fila más** en la tabla maestra de fase
   7 por dataset.

5. La comparación cierra sin huecos porque (a) las entradas son las mismas, (b) los
   modelos y métricas son los mismos, (c) los contrastes son los mismos, (d) el control
   de calidad separa "criterio optimizado" de "calidad del optimizador" y (e) las
   divergencias respecto al paper (modelo, métrica, datasets) están declaradas
   explícitamente en la memoria.

## Resumen ejecutivo del coste

- Tier 1: pequeño (SHAP rápido, tie-break trivial, regenerar fase 5 instantáneo).
- Tier 2: medio (re-ejecución fase 6 con +XGBoost; subir núcleo a cuadernos).
- Tier 3: bajo (editorial puro, fases 1-3).
- Tier 4: el más grande (implementar β + oráculo + ejecución QFS por dataset y barrido
  $(α, β)$ + integración con fase 7).

Orden propuesto: **T1 → T3 (en paralelo, no se pisan) → T2 (re-ejecuta fase 6 una sola
vez con los cuatro modelos) → T4**. Con las tres decisiones aprobadas, fase 6 se
re-ejecuta una única vez con XGBoost incluido y fase 8 se planifica con β implementado
y oráculo $Q^*(\alpha)$. La estimación de coste total queda condicionada por la
re-ejecución de fase 6 con XGBoost (~25 % más experimentos) y por el barrido $(α, β)$
de fase 8 (11 valores de β × ~10 valores de α de control + el ejecutado operativo, por
dataset).
