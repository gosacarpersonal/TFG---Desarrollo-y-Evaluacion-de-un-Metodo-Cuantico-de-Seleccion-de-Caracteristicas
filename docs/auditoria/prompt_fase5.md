# Prompt de arreglo — Fase 5

Lógica en `src/fase5_feature_selection.py`; notebook generado por
`scripts/rebuild_fase5_notebook.py` (`notebooks/fase5.ipynb`). Respeta
`docs/estilo_redaccion_tfg.md` y `docs/auditoria/estructura_notebooks.md`. Regenera y
valida con `scripts/verify_fase5_notebook.py`.

Arregla estos fallos verificados:

1. **[MEDIO — trazabilidad, NO correctitud] `variance`: el cálculo es correcto, el
   ETIQUETADO miente.** Corrección respecto a la versión anterior de este prompt: tras
   leer la fuente primaria (Solorio-Fernández et al. 2020, `docs/papers`), la referencia
   UFS **estandariza todos los datos antes de variance** y lo usa como baseline degenerado.
   Por tanto, que el código calcule `x_train.var(axis=0)` (`fase5_feature_selection.py:547`)
   sobre datos de `StandardScaler` (`:148`) **es consistente con el protocolo de
   referencia — NO es un bug**. (El `.md` de IA que decía "variance sobre datos crudos"
   estaba equivocado; no lo sigas.)
   El defecto real es el **etiquetado/narrativa**: el registro llama al método "varianza
   cruda" (`fase5_feature_selection.py:217`) y la narrativa dice "ordena por escala", pero
   el cálculo real es varianza sobre estandarizado ≈ baseline degenerado/casi aleatorio.
   **Arreglo recomendado:** mantener el cálculo sobre estandarizado y **corregir etiqueta
   y narrativa** para describirlo honestamente como baseline degenerado (citando Solorio).
   Que código, etiqueta y memoria cuenten UNA sola historia coherente. (Alternativa solo si
   se decide a propósito: variance sobre crudo como baseline "ordena por escala", pero eso
   DIVERGE de Solorio y hay que justificarlo en el texto.)
   NOTA: el estimador de MI discretizado (5-bins uniforme) **ya es fiel al original**:
   verificado contra `QFS_based_on_NA/Data_functions.py::MI_complete_det` (fuente primaria).
   No tocar.

2. **[MEDIO] Muestreo inconsistente entre métodos.** `variance`, `f_classif`,
   `mutual_correlation` y `feature_similarity` usan el `x_train` completo; el resto pasa
   por `crear_muestra` (`:534-537`). Decide y documenta: homogeneiza el tamaño muestral o
   justifica explícitamente por qué unos métodos no se submuestrean.

3. **[MEDIO — estructura, paso 2] Mostrar la creación del núcleo, no solo invocarlo.** El
   cuaderno YA narra bien por dataset (§5.9) y por figura — eso NO se toca. Lo que falta es
   el paso 2 de la estructura: el roster de 12 selectores se invoca con `fs.*` sin verse
   construir. Dado que el roster ES la contribución de la fase, sube al cuaderno la
   creación visible de al menos los selectores espejo de QFS (relevancia `I(x;y)`,
   redundancia `I(x;x)`, mRMR/RRFS que combinan ambos), dejando en `src` solo el plumbing
   (E/S, formateo, guardado). Acepta que el cuaderno se alargue. Ver
   `estructura_notebooks.md`.

4. **[BAJO — figuras]** Todas las figuras son heatmaps/resúmenes que duplican tablas.
   Añade al menos una visualización que aporte una lectura que la tabla no dé, o retira las
   redundantes.

Criterio de aceptación: varianzas de numéricas no degeneradas y coherentes con la
narrativa; muestreo homogéneo o justificado; los selectores núcleo se ven construir en el
cuaderno; `verify_fase5_notebook.py` pasa.
