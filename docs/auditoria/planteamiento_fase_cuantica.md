# Planteamiento de la fase cuántica (fase 8) desde las fuentes primarias

> 2026-06-14. Plan operativo de la fase cuántica derivado de PAPER_QFS, QFS_D2, Mücke y
> el código `QFS_based_on_NA/`. NO va a la memoria (depende de ejecución); va aquí como
> base de decisiones. Cuando se ejecute, los resultados sí entran en la memoria.
>
> **Decisiones aprobadas el 2026-06-14 (memoria LaTeX ya actualizada):**
> 1. **XGBoost añadido a fase 6** (T2.1 aceptado) como ancla cuantitativa con
>    PAPER_QFS~\cite{chen2016}~\cite{orquin2026}. macro-F1 sigue siendo métrica primaria;
>    AUC-ROC se registra en los binarios como contexto.
> 2. **β implementado** extendiendo `arrange_atoms_robust_MDS` /
>    `distance_matrix_from_redundancy` con el término aditivo $\beta(1+I_i)(1+I_j)$
>    (QFS_D2 eq 14). Barrido $\beta\in\{0,0.1,\ldots,1\}$, elección por validation.
> 3. **Oráculo $Q^*(\alpha)$ exacto implementado** como control de calidad
>    (enumeración para $n\le 20$, Gurobi como respaldo), recorriendo $\alpha$ vía
>    Algorithm 1 de Mücke~\cite{mucke2023}. Convive con la ejecución operativa con
>    $\alpha=0.5$ fijo del código original.

## Contrato heredado del bloque clásico (ya en `metodologia.tex:245-255`)

- **Entradas:** vector $I_i$ y matriz $R_{ij}$ por formulación, materializados en fase 5
  con la misma discretización (5 bins uniforme) que la referencia
  (`Data_functions.py::MI_complete_det`).
- **Parámetros a barrer:** $\alpha \in [0,1]$ (recorre $k$, Mücke), $\beta \in [0,1]$
  (separa relevantes, QFS_D2 eq 14).
- **Selección de hiperparámetros:** solo con `validation`; `test` se consulta una vez.
- **Modelos / métrica / contrastes:** los mismos de fase 6 (logistic / linear_svm / RF;
  macro-F1; bootstrap 400; comparaciones pareadas; permutación de etiquetas).
- **Presupuestos $k$:** 10 (bcw, churn, madelon), 5 (olive 3/9). En `madelon` (500 vars >
  envolvente operativa ~20), preselección clásica previa **solo con train**, declarada
  como método híbrido.

## Decisiones operativas que cierran los huecos

1. **Normalización del handoff (verificar).** `Data_functions.py::MI_complete_det` aplica
   min-max usando el rango de `MI_x_x` *tanto* para $I_i$ como para $R_{ij}$, y filtra
   `MI > 0.001`. Fase 5 difiere el filtro/normalización a fase 8 (documentado en
   `fase5_feature_selection.py:313`). Para que "QFS consume las mismas cantidades" sea
   literal, fase 8 debe replicar exactamente esa normalización, no introducir otra. Es la
   primera comprobación a hacer.

2. **Recorrido de $\alpha$ y $\beta$.** Barrido equiespaciado en $[0,1]$ (10–11 valores
   por dimensión, como en QFS_D2 fig. 17/18). $\alpha$ fija $k$ por el resultado de Mücke;
   $\beta$ se elige por validación dentro de cada $k$. Se reportan los mapas
   $k \times \beta$ análogos a las figuras 17/18 del paper para que la lectura sea
   directamente comparable.

3. **Solver de control de calidad: óptimo QUBO exacto.** En la envolvente operativa
   ($\le 20$ variables), el óptimo exacto de $Q(x;\alpha)$ es enumerable (o resoluble con
   Gurobi como en QFS_D2 §4.3). Para cada $\alpha$ se compara el subconjunto del
   simulador analógico con el óptimo exacto, separando "calidad de la optimización" de
   "calidad del criterio optimizado" (ya anunciado en `metodologia.tex:234-243`).

4. **Datasets de entrada al QFS.**
   - `olive_oil_3class` (8 var) y `olive_oil_9class` (8 var): entran directos.
   - `customer_churn` (10 var): entra directo.
   - `breast_cancer_wisconsin` (30 var): pre-selección clásica a ~20 con un selector
     defendible (p. ej. mrmr_approx por ser análogo voraz del criterio, declarado).
   - `madelon` (500 var): pre-selección obligatoria a ~20; declarar híbrido.

5. **Reutilizar predicciones por fila para la comparación pareada.** Las predicciones de
   fase 6 ya están archivadas por fila (`metodologia.tex:393-400`); la incorporación de
   QFS no requiere reentrenar los baselines y la comparación pareada se calcula sobre el
   mismo registro común. Esto es ahorro real y elimina la posibilidad de divergencia.

## Lo que SÍ va en la memoria (cuando exista evidencia)

- Resultados QFS por dataset y $k$, con la **misma tabla y figura** que fase 7 (para que
  la comparación cuántico↔clásico se lea de un vistazo).
- Distancia al óptimo QUBO exacto (control de calidad del simulador).
- Veredicto por dataset bajo la misma regla de decisión que fase 7
  (delta + IC + p-valor pareado + permutación de etiquetas).
- Discusión de $\alpha$ (recorre $k$) y $\beta$ (separación), con cita Mücke / QFS_D2.

## Lo que NO va en la memoria (queda en docs)

- Este plan operativo.
- La auditoría/prompts de notebooks.
- El control de fuentes y la fundamentación.
