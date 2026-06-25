# Fundamentación del bloque clásico desde las fuentes primarias

> 2026-06-14. Objetivo: que **cada decisión** del bloque clásico (parámetros, métodos,
> k, modelos, métricas, visualizaciones) derive de las fuentes primarias —papers de
> `docs/papers`, propuesta de `docs/propuesta`, código de `QFS_based_on_NA`— y no de
> intuición ni de `.md` de IA. Esta es la base fiable para la revisión final de los
> notebooks y para cerrar la comparación clásico↔cuántico sin huecos argumentales.
>
> Fuentes primarias usadas: **Propuesta** (objetivos/alcance), **PAPER_QFS** y **QFS_D2**
> (método cuántico, benchmarks, métricas), **Solorio-Fernández 2020** (qué filtros UFS
> rinden), **Mücke 2023** (origen QUBO, α↔k), **QFS_based_on_NA/** (código de referencia).
> Pendiente de lectura profunda: Mücke (Proposición 1 formal) y el solver
> `QFS_Auxiliar_functions.py` para la fase cuántica.

## Lo que fija la propuesta (contrato del TFG)

Objetivo fundamental: analizar la **viabilidad** de un método de selección por bloqueo de
Rydberg. Objetivos específicos: (1) revisión de métodos clásicos **"más utilizados y con
mejor rendimiento"**; (2) datasets de referencia diversos; (3) comparativa de clásicos;
(4) desarrollo del método cuántico; (5) comparativa cuántico **vs. los mejores clásicos**.
→ Implica que la elección de métodos debe estar guiada por **evidencia de rendimiento**, y
que el cierre es una comparación homogénea cuántico↔mejores-clásicos.

## Mapa decisión → fuente → estado

| Decisión del TFG | Qué dicen las fuentes (primario) | Estado | Acción |
|---|---|---|---|
| **Objetivo relevancia+redundancia** | PAPER_QFS eq 6 / QFS_D2 eq 11: `Q(x;α)=-αΣI_i x_i+(1-α)ΣR_ij x_i x_j` | ✅ Fiel | — |
| **MI discretizada 5 bins uniforme** | `Data_functions.py::MI_complete_det` (KBins 5, uniform, ordinal) | ✅ Verificado fiel | Mantener; verificar normalización en fase 8 |
| **Roster espejo (relevancia/redundancia/combinado/wrapper/embedded)** | Estructura de `Q(x;α)`; tutor pidió FSFS, MC, Boruta | ✅ Justificado por construcción | Declarar que MC/FSFS son espejo estructural, no top-performers |
| **Boruta como gold-standard** | PAPER_QFS §V.C y QFS_D2: único wrapper de referencia | ✅ | — |
| **Presupuestos k pequeños (≤10; 5 en olive)** | Ambos papers: QFS gana en subconjuntos compactos (2-5); "AUC se aplana >7 vars; Boruta sobreestima" | ✅ Correcto | Citar esa evidencia al justificar k (hoy no se cita en metodología) |
| **`variance` sobre datos estandarizados** | Solorio §3.1: estandariza TODO antes de variance; baseline degenerado | ✅ Consistente con la referencia | **Corregir narrativa**: la memoria dice "datos sin estandarizar/refleja escala" (FALSO) |
| **Modelos de evaluación: logistic/SVM/RF** | Papers QFS usan **XGBoost**; Solorio usa kNN/SVM/NB | ⚠️ Divergencia | Declarar la elección y su porqué frente a XGBoost (hoy solo se justifica la métrica) |
| **Métrica: macro-F1** | Papers QFS usan **AUC-ROC** (binario) | ⚠️ Divergencia ya justificada (multiclase/desbalance) | Mantener; reforzar el puente con el AUC del estado del arte |
| **Sin búsqueda de hiperparámetros** | Papers QFS hacen RandomizedSearchCV | ⚠️ Divergencia | Defendible (aísla el efecto del espacio de variables); ya justificado |
| **Datasets: bcw, churn, madelon, olive 3/9** | Papers: Adult/Bank/Telco (binarios ≤20). Churn **solapa** | ✅ Extensión deliberada | Mencionar el solape de Churn como ancla de comparabilidad |
| **Validación estadística (FDR, efecto, permutación, bootstrap)** | No en los papers; es aporte de rigor del TFG | ✅ Fortaleza propia | — |
| **SHAP** | No en los papers; aporte propio | ✅ pero mal usado (ver auditoría) | Beeswarm real, no barra de media\|SHAP\| |
| **α controla k; β separa relevantes** | Mücke (α↔k monótono) + QFS_D2 eq 14 (β) | ✅ En marco_teorico | Verificar contra el solver al implementar fase 8 |

## Huecos argumentales a cerrar (para que la comparación no tenga fisuras)

1. **`variance` (factual, ALTO en la memoria):** `metodologia.tex:84-88` afirma que ordena
   "sobre datos sin estandarizar" reflejando la escala. El código calcula sobre
   estandarizado (degenerado), igual que Solorio. Corregir el texto a la realidad.
2. **Protocolo vs. papers (MEDIO):** la comparación interna clásico↔cuántico del TFG es
   consistente (mismo protocolo para ambos, `metodologia.tex:245-255`). El hueco es que
   ese protocolo **difiere del de los papers** (XGBoost+AUC). La métrica ya se justifica;
   falta una frase análoga sobre el **modelo**, dejando explícito que el TFG re-evalúa todo
   bajo su propio protocolo unificado, de modo que las cifras del paper no son
   directamente comparables (la conexión con el paper es cualitativa, vía estado del arte).
   *No* obliga a añadir XGBoost; basta con declarar la elección. (Añadir XGBoost+AUC sería
   un plus de comparabilidad, opcional.)
3. **Grounding de k (BAJO):** citar en metodología la evidencia de los papers (plateau >7,
   Boruta sobreestima) que respalda k≤10.
4. **Roster (BAJO):** declarar que MC y FSFS se incluyen por espejo estructural del término
   de redundancia, no por ser top-performers (en Solorio rinden flojo).

## Qué va en la memoria y qué se queda fuera

- **A la memoria (depende solo de documentación/investigación):** corrección de `variance`;
  frase de protocolo vs. papers; grounding de k; matiz del roster; el estado del arte y el
  marco teórico ya están bien.
- **Fuera de la memoria (trabajo interno):** este mapa, la auditoría de notebooks, el
  control de fuentes, los prompts de arreglo. Son QA y trazabilidad, no contenido de la
  memoria.

Relacionado: `contraste_papers.md`, `auditoria_notebooks.md`, `estructura_notebooks.md`.
