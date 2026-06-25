# Auditoría notebook×fuentes (huecos metodológicos contra papers + código original)

> 2026-06-14. Contraste de los 7 notebooks (fases 1-7) contra las fuentes PRIMARIAS:
> PAPER_QFS, QFS_D2, Mücke 2023, Solorio 2020 (papers) y `QFS_based_on_NA/`
> (Data_functions.py, QFS_Auxiliar_functions.py, Prediction_and_results.py).
> Mismo criterio que en LaTeX: los `.md` de IA son secundarios; el hecho lo fija el
> código + el paper + la matemática.
>
> Método: extracción de los 169+156+100+122+48+38+36 = **669 celdas markdown**, búsqueda
> dirigida de afirmaciones verificables y contraste contra fuentes leídas.

## Tabla por notebook

| Notebook | Estado vs. fuentes | Hallazgo principal |
|---|---|---|
| Fase 1 | ✅ Bien anclado | Citas correctas a PAPER_QFS (relevancia I(x;y), redundancia R_ij vía MDS). Conecta cada bloque con la cadena cuántica. |
| Fase 2 | ✅ Bien anclado | Cita PAPER_QFS §V.A para justificar label-encoding de categóricas; difiere one-hot al post-split correctamente. |
| Fase 3 | ✅ Bien anclado | Justifica la auditoría post-preprocesado por su impacto en los detunings locales y la geometría MDS. |
| Fase 4 | ✅ Bien anclado | Drift KS/Wasserstein/PSI explicado con rigor; umbrales declarados. |
| **Fase 5** | ⚠️ **1 contradicción factual** | md#36: "variance sobre datos crudos ordena por escala" — **FALSO** (el código calcula sobre StandardScaler; Solorio estandariza). Mismo error que ya corregimos en LaTeX. |
| Fase 6 | ⚠️ Coherente con bug ya conocido | md#131 describe SHAP como "media de valores absolutos sobre validation" — consistente con el bug ya fichado (`shap_values_array:560` colapsa la matriz). md#32 declara correctamente la divergencia con XGBoost+AUC del paper. |
| Fase 7 | ✅ Bien anclado | md#126, 130: declara explícitamente la cautela metodológica frente al paper. Discute con honestidad el resultado de olive 9-class (sin evidencia para mejora ni deterioro). |

## Lo que confirman las fuentes primarias (y se respeta en los notebooks)

- **Discretización 5 bins uniforme** (fase 5 md#60) — fiel a `Data_functions.py:230-234`.
- **`MI > 0.001` y normalización min-max diferidos a fase 8** (fase 5 md#60) — consistente con el comentario del propio código `fase5_feature_selection.py:313`.
- **Boruta a su tamaño confirmado, no recortado a k** (fase 5 md#68, md#71, fase 6 md#42) — coincide con `QFS_MAIN.ipynb` y con la práctica de PAPER_QFS.
- **k = 10 (grandes) y 5 (olive)** (fase 6 md#42) — coherente con la evidencia de "plateau >7 vars" de PAPER_QFS.
- **Validación + test consultado una vez** (fase 6 md#9, md#96) — buena práctica que el paper no hace explícita pero que aquí refuerza el rigor.

## Lo que falta declarar (huecos argumentales, no bugs)

Son los mismos que detecté en la memoria y ya cerré ahí; conviene replicarlos en el notebook por coherencia:

1. **Fase 5: variance.** Corregir md#36 y la celda análoga. La afirmación "sobre datos
   crudos ordena por escala" es falsa (Solorio estandariza; el código del TFG estandariza).
   Sustituir por la versión correcta: baseline degenerado tras estandarización.
2. **Fase 5: roster MC/FSFS.** Declarar honestamente que en Solorio 2020 son de los
   filtros UFS de menor rendimiento; se incluyen como espejo estructural del término de
   redundancia, no por competitividad. Esto ya se añadió a `metodologia.tex`.
3. **Fase 6: SHAP.** El propio markdown describe correctamente lo que el código hace
   (media|SHAP|), por lo que ningún arreglo de texto resuelve el bug. Arreglar el
   código (ya en `prompt_fase6.md`).

## Hallazgos primarios NUEVOS (de leer QFS_Auxiliar_functions.py y Mücke pp.1-8)

Estos NO afectan a los notebooks 1-7 pero condicionan el planteamiento de la fase
cuántica y, en parte, lo que la memoria LaTeX dice del método:

### Q-1. α↔k es un teorema sobre el QUBO, no sobre la implementación NA

- **Mücke Proposición 1 (pág. 6) y Algorithm 1 (pág. 8):** α↔k se obtiene mediante
  **búsqueda binaria sobre α**, llamando a un oráculo que resuelve `Q*(α)` exactamente.
  Es un resultado para el QUBO puro resuelto exacto/clásico.
- **QFS_Auxiliar_functions.py:95:** el solver neutral-atom usa **α = 0.5 hardcodeado**.
  El ranking de variables sale de las **densidades de Rydberg** medias filtradas por las
  configuraciones de menor energía, y k se elige por top-k sobre ese ranking, **no**
  recorriendo α.
- **Implicación para LaTeX:** `marco_teorico.tex:65-74` ("α controla k... recorrer α
  equivale a recorrer la escalera de presupuestos") es **correcto sobre el QUBO de
  Mücke**, pero el lector puede inferir que es lo que QFS-NA hace. Conviene un matiz
  explícito en `metodologia.tex` (sección del método cuántico) declarando que en la
  implementación neutral-atom α se fija y k se obtiene por top-k sobre la densidad de
  Rydberg, y que el resultado de Mücke es teórico (sobre el QUBO).

### Q-2. β no está implementado en el código que tenemos

- **QFS_D2 eq 14** introduce `β` (separa variables de alta relevancia en el embedding).
- **QFS_Auxiliar_functions.py:** no hay β. `arrange_atoms_robust_MDS` y
  `distance_matrix_from_redundancy` usan solo `d_ij = (1/R_ij)^(1/6)` (sin término β).
- **Implicación para fase 8:** el barrido de β del paper no se puede replicar tal cual
  con el código actual; o se implementa β en el solver, o se renuncia a barrerlo y se
  documenta como divergencia respecto a QFS_D2. La conclusión que ya hicimos en
  `conclusiones.tex` ("los parámetros α y β se calibrarán") asume que β estará disponible
  en fase 8: o se implementa, o se ajusta la conclusión.

### Q-3. Doble normalización en el handoff

- **`Data_functions.py::MI_complete_det` (líneas 272-277):** normaliza `MI_x_y` y
  `MI_x_x` con **el rango de MI_x_x** (raro y específico).
- **`QFS_Auxiliar_functions.py:98, 103, 555-575`:** el solver vuelve a normalizar por su
  cuenta — `normalize_list` (min-max independiente sobre I_xy) y `normalize_matrix`
  (min-max independiente sobre MI_xx).
- **Implicación:** la frase de `metodologia.tex:170-175` ("QFS consume exactamente las
  mismas cantidades informacionales que los métodos clásicos") es **literalmente cierta
  solo si fase 8 pasa al solver matrices NO normalizadas** (para que el solver las
  normalice una sola vez, como en la implementación original). Fase 5 ya difiere la
  normalización a fase 8 (`fase5_feature_selection.py:313`), por lo que el contrato se
  respeta. Confirmado primario: **no es un bug**.

### Q-4. Discretización: el paper Mücke usa cuantiles, el código del grupo usa uniforme

- **Mücke pág. 3:** "B+1-cuantiles" (bins por cuantiles).
- **`Data_functions.py`:** `strategy='uniform'`.
- **Implicación:** el grupo se aparta del paper Mücke. Es legítimo (la referencia
  metodológica del TFG es el código del grupo, no Mücke), pero conviene declararlo en la
  memoria si se cita Mücke como origen del estimador, para que un lector cuidadoso no se
  confunda.

### Q-5. Comparadores del código original

- **`QFS_MAIN.ipynb`** compara contra **Boruta + Importance ranking** y evalúa con
  **XGBoost** Y **Random Forest** (no solo XGBoost, como hace literalmente PAPER_QFS).
- **Implicación:** el TFG usa logistic + SVM lineal + RF. **RF coincide con el código
  original**; XGBoost no está. Esto refuerza la decisión metodológica ya declarada en
  `metodologia.tex` (divergencia con XGBoost por homogeneidad interna).

## Veredicto de coherencia notebooks × fuentes

- **Estructura argumental de los 7 notebooks: sólida** y bien anclada en las fuentes
  primarias. La narrativa cita PAPER_QFS, QFS_D2 y la propuesta donde corresponde, y
  conecta cada bloque del bloque clásico con su rol en la cadena cuántica.
- **Único bug factual a corregir en los notebooks: fase 5 md#36** (variance sobre datos
  crudos), por coherencia con el código y la LaTeX corregida.
- **Lo demás son refuerzos de declaración**, no errores: añadir el matiz de MC/FSFS
  (espejo, no top-performers) en fase 5, y añadir en LaTeX el matiz de "α controla k es
  teorema sobre QUBO, no sobre QFS-NA".

Relacionado: `contraste_papers.md`, `fundamentacion_fuentes.md`,
`planteamiento_fase_cuantica.md`, `auditoria_notebooks.md`.
