# Contraste de hallazgos contra fuentes primarias (papers + código QFS)

> 2026-06-14. Verificación de la auditoría contra las **fuentes primarias** únicamente:
> `docs/papers/` (leídos: PAPER_QFS, QFS_D2, Solorio UFS review) y `QFS_based_on_NA/`
> (código original). Los `.md` de `docs/decisions` quedan como secundarios.
>
> Conclusión breve: 1 hallazgo se **revierte** (variance), aparecen **divergencias de
> protocolo** entre el bloque clásico del TFG y el protocolo de los papers QFS, y el
> resto de hallazgos de código se mantienen.

## Qué dicen las fuentes primarias

**PAPER_QFS.pdf (Orquín-Marqués et al., "QFS based on Neutral Atom arrays"):**
- Objetivo (eq 6): `Q(x;α) = -α Σ I_i x_i + (1-α) Σ_{i<j} R_ij x_i x_j`, con `I_i=I(x_i;y)`,
  `R_ij=I(x_i;x_j)`. El roster clásico del TFG (relevancia + redundancia) lo refleja. ✓
- **Clásicos comparados: SOLO dos** — ranking de importancia de **XGBoost** y **Boruta**
  (con XGBoost de base). Boruta = referencia gold-standard.
- **Modelo de evaluación: XGBoost.** **Métrica: AUC-ROC** (+ precision/recall).
- Datasets: Adult, Bank Marketing, Telco Churn — **binarios, ≤20 variables**.
- Resultado: QFS es competitivo sobre todo en **subconjuntos compactos (2-5 vars)**; los
  clásicos alcanzan/superan al crecer k.

**QFS_D2.pdf:** mismo objetivo (eq 11); introduce **β** (eq 14:
`d_ij = (C6/R_ij)^(1/6) + β(1+I_i)(1+I_j)`, β∈[0,1]) para separar variables importantes
en el embedding. Mismos benchmarks (**Boruta + ranking XGBoost**), misma métrica (**AUC**),
datasets Telco Churn y Oral Cancer. Hallazgo clave del paper: "Boruta **sobreestima** el
nº de variables; AUC se aplana más allá de ~7 variables".

**Solorio-Fernández et al. 2020 (review UFS):** evaluación sistemática de 18 filtros UFS.
- **Estandariza TODOS los datos** (pág. 4: "each dimension normalized to mean 0 and
  standard deviation 1"), **incluido antes de variance**.
- Clasificadores de validación: **kNN, SVM, Naive Bayes** (no XGBoost).
- Mejores métodos por rank medio: **NDFS, MCFS, Laplacian Score, SVD-Entropy, USFSM,
  MRSF, RRFS** (espectrales/sparse no supervisados). **MC y Variance están entre los más
  flojos** (MC ~12/18, Variance ~10/18).

## 1. Hallazgo REVERTIDO — `variance` (antes F5-1, ALTO → ahora MEDIO)

Mi turno anterior afirmó (heredando el `.md` de IA) que calcular `variance` sobre datos
estandarizados era un bug y que "debía ser sobre datos crudos". **La fuente primaria lo
contradice:** Solorio estandariza todo y usa variance-sobre-estandarizado como baseline
(degenerado, rank ~10/18). Es decir, el código del TFG (`fase5_feature_selection.py:547`
sobre datos de `StandardScaler`) es **consistente con el protocolo de referencia**, no lo
viola. El `.md` `roster_clasico_espejo.md:71` ("la estandarización NO se aplica antes de
variance") **no está respaldado por Solorio**.

Lo que SÍ era un defecto real (MEDIO, trazabilidad): el **etiquetado**. El registro del
código llamaba al método "varianza cruda" y la narrativa de IA decía "ordena por escala"
— ninguna describía lo que el código hace (varianza sobre estandarizado ≈ baseline
degenerado/casi aleatorio). **Estado actual:** se mantiene el cálculo sobre estandarizado
(como Solorio) y se corrigió la etiqueta a "varianza tras escalado", de forma que
código↔etiqueta↔memoria cuentan una sola historia.

## 2. Divergencia de protocolo TFG vs papers QFS [IMPORTANTE para el enfoque]

El bloque clásico (fase 6) y los papers QFS **no evalúan igual**:

| Eje | Papers QFS (primario) | TFG fase 6 (actual) |
|---|---|---|
| Modelo de evaluación | **XGBoost** | logistic_regression, linear_svm, random_forest |
| Métrica | **AUC-ROC** | macro-F1, balanced accuracy |
| Clásicos comparados | ranking XGBoost + **Boruta** | roster de 12 métodos |
| Datasets | binarios ≤20 vars | + madelon (500) y olive multiclase (3/9) |

Implicación para el objetivo final (comparar el bloque clásico con QFS): si el QFS se
evaluó con **XGBoost + AUC + Boruta**, la comparación clásica debería compartir ese terreno
común, o la comparación final QFS↔clásico no será homogénea. **No es un bug**, es una
decisión de diseño a tomar conscientemente:
- Mínimo defendible: incluir **XGBoost** como modelo y **AUC** como métrica (al menos en
  los datasets binarios) para conectar con los resultados de los papers.
- El roster de 12 y los modelos extra son una extensión legítima (más completa que el
  paper), pero conviene declarar que el *ancla de comparabilidad* con QFS es XGBoost+AUC+Boruta.

## 3. Sobre "qué métodos son buenos" (evidencia de Solorio)

- Solorio es **no supervisado**; QFS es **supervisado** (usa `I(x;y)`). Por eso sus
  "mejores" (NDFS, MCFS, Laplacian) NO son el comparador natural de QFS, y excluirlos del
  roster (como hizo el TFG) es defendible.
- Pero dentro del roster del TFG, **MC y FSFS son flojos en Solorio**. Se incluyen por
  *mirroring estructural* (aíslan el término de redundancia), no por rendimiento; eso debe
  decirse explícitamente en la memoria para que no parezca que se eligieron por buenos.
- **Boruta** como gold-standard y los **presupuestos k pequeños (5-10)** están
  fuertemente respaldados por ambos papers QFS. ✓

## 4. Hallazgos que se MANTIENEN (hechos de código, no dependen de `.md`)

- **SHAP colapsado (fase 6)**: sigue siendo real. SHAP no está en los papers (es aporte
  propio del TFG), pero si se calcula, tirarlo es desperdicio. ALTO.
- **Tie-break hardcodeado por dataset (fase 6)**: sin respaldo en papers ni código
  original. MEDIO.
- **Estructura paso-2 en 5-7** (núcleo en `src`): MEDIO.
- **MI discretizado 5-bins**: verificado FIEL a `QFS_based_on_NA/Data_functions.py`. ✓

## Verificación pendiente (fase 8 / handoff)

- Replicar la **normalización peculiar del original** (`MI_complete_det`: min-max usando
  el rango de `MI_x_x` para normalizar tanto `I_i` como `R_ij`) para que "QFS consume las
  mismas cantidades" sea literal.
- Confirmar el manejo de **α** (recorre k) y **β** (separación en el embedding) cuando se
  implemente el solver, contra `QFS_Auxiliar_functions.py` y eq 14 de QFS_D2.
