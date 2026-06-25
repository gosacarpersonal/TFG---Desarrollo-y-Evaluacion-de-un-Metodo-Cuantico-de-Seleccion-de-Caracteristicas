# Auditoría de notebooks — fallos verificados y plan de arreglo

> Fecha: 2026-06-14 (revisado tras contraste con fuentes primarias y con la estructura
> canónica). Severidad: **ALTO** (correctitud / defensibilidad fuerte) · **MEDIO**
> (calidad o defensibilidad) · **BAJO** (estilo / cosmético).
>
> **Fiabilidad de fuentes (crítico):** los `.md` de `docs/` (decisions, worklog,
> final_status) fueron generados por otras IAs → son fuente **SECUNDARIA**, a verificar,
> no autoridad. Las fuentes **PRIMARIAS** son: el código `QFS_based_on_NA/` (incl. los
> `*_OG.py`), los papers de `docs/papers` y la propuesta de `docs/propuesta`. Todos los
> hallazgos de correctitud de este informe se sostienen sobre evidencia primaria (el
> código de `src/` + matemática), no sobre los `.md`. Donde un `.md` coincide, se trata
> como corroboración secundaria.
>
> **Corrección de marco (importante):** la estructura de los notebooks 1-4 (narrativa
> rica con funciones visibles) es la **correcta** — ver `estructura_notebooks.md`. Por
> tanto, las "funciones inline" de 1-4 NO son un fallo. Y, medido celda a celda, las
> fases 5-7 **sí** conservan la narrativa por dataset: NO son cascarones narrativos. El
> único defecto estructural real es que en 5-7 el núcleo metodológico vive en `src` y no
> se ve construir (paso 2 de la estructura).

## Resumen ejecutivo

| Notebook | Fallo más grave | Severidad |
|---|---|---|
| fase1 | Heatmaps que duplican tablas (figuras, no estructura) | MEDIO |
| fase2 | Celda de funciones de 222 líneas (ya fichada en worklog) | MEDIO |
| fase3 | Heatmaps `asociacion`/`redundancia` que duplican tablas | MEDIO |
| fase4 | chi² de clases entre splits casi circular (ya matizado) | BAJO |
| fase5 | `variance` mal etiquetado ("cruda" pero calcula sobre estandarizado) | MEDIO |
| **fase6** | **SHAP colapsado a media\|SHAP\|; beeswarm tirado; tie-break hardcodeado; protocolo ≠ papers (XGBoost/AUC)** | **ALTO** |
| fase7 | Figuras de resumen sin lectura por figura (la narrativa sí está) | BAJO |
| QFS_MAIN | Datasets distintos a fases 1-7; doble import; código comentado | MEDIO |
| **Transversal** | **En 5-7 el núcleo metodológico vive en `src` y no se ve construir (paso 2)** | **MEDIO** |

> Nota: el `COLUMNAS_PRESENTACION` de fase 1 (capa de presentación, no analítica) se
> puede minimizar, pero las *funciones* visibles de 1-4 son la estructura deseada y NO se
> tocan. La gravedad transversal baja de ALTO a MEDIO: no es una asimetría de calidad
> narrativa, sino un único paso (creación de funciones visible) ausente en las fases
> pesadas.

Métricas reales medidas en los `.ipynb`:

| nb | celdas code | celda máx (líneas) | const. MAYÚS | celdas markdown | figuras PNG |
|---|---|---|---|---|---|
| fase1 | 119 | 181 | 3 | 169 | 30 |
| fase2 | 97 | **222** | 2 | 156 | 14 |
| fase3 | 109 | 185 | 7 | 100 | 20 |
| fase4 | 105 | 111 | 6 | 122 | 18 |
| fase5 | 27 | 57 | 0 | 48 | 0 (solo PDF) |
| fase6 | 19 | 26 | 0 | 38 | 15 |
| fase7 | 21 | 20 | 0 | 36 | 8 |

Lectura corregida: 1-4 tienen más celdas porque crean las funciones inline (estructura
deseada). 5-7 tienen menos celdas de código porque importan el núcleo de `src/`, **pero
conservan la narrativa por dataset** (secciones `### <dataset>` en fase5 §5.9, fase6
§6.6, fase7 §7.4, verificadas). No es un cascarón narrativo; el déficit es solo que el
núcleo metodológico no se ve construir (paso 2).

---

## Fase 1 — `notebooks/fase1.ipynb` (gen: `scripts/rebuild_fase1_notebook.py`)

- **F1-1 [BAJO]** `COLUMNAS_PRESENTACION` (`rebuild_fase1_notebook.py:191`) es un dict de
  ~100 entradas de presentación (renombrado identidad / `snake_case`→texto). Es capa de
  presentación, no función analítica; se puede minimizar y aplicar localmente. **No** es
  el caso de "función inline a sacar": las funciones analíticas inline son la estructura
  deseada y se quedan.
- **F1-2 [MEDIO]** Figuras que duplican tablas. De 30 figuras, `01_08_asociacion` (×4) y
  `01_11_redundancia` (×4) son heatmaps de correlación que repiten información ya
  mostrada en tablas. El volumen (30) no se traduce en señal nueva. (Es un punto de
  figuras, no de estructura.)
- **Lo que SÍ está bien (no tocar):** la estructura (sección → funciones inline →
  por-dataset → narrativa). Las figuras `01_06_univariante` (×4, `histplot(kde=True)`) y
  `01_07_normalidad` (×4, QQ-plots) son distribucionales reales. La acusación previa de
  "1 sola figura narrativa" y la de "andamiaje inline = fallo" eran ambas falsas.

## Fase 2 — `notebooks/fase2.ipynb` (gen: `scripts/rebuild_fase2_notebook.py`)

- **F2-1 [MEDIO]** Celda de **222 líneas** (la mayor de las 7 fases; sección 2.9). Es una
  única celda de funciones demasiado grande para seguirla. **Ya está fichada como
  pendiente en el worklog** (`tfg_prequantum_worklog.md:9`: "celda de funciones de 2.9
  con 221 líneas (dividir)"). El arreglo es trocearla en funciones más pequeñas y
  legibles **dentro del cuaderno** (no moverla a `src`): mantiene la estructura deseada.
- **Lo que SÍ está bien:** `fase2_distribuciones_numericas` (×4) y `fase2_outliers_iqr`
  (×4, con boxplots, `graficar_boxplots_outliers:1174`) son narrativas.

## Fase 3 — `notebooks/fase3.ipynb` (gen: `scripts/rebuild_fase3_notebook.py`)

- **F3-1 [MEDIO]** `fase3_asociacion` (×4) y `fase3_redundancia` (×4) son heatmaps que
  duplican las tablas de correlación/redundancia. (Punto de figuras.)
- **Lo que SÍ está bien:** la estructura y la narrativa por dataset; las constantes y
  funciones visibles son la estructura deseada (los parámetros están justificados en
  Markdown, según `tfg_prequantum_worklog.md:10`). `fase3_distribucion_conservacion` (×4)
  es distribucional.

## Fase 4 — `notebooks/fase4.ipynb` (gen: `scripts/rebuild_fase4_notebook.py`)

- **F4-1 [BAJO]** Infra inline (6 constantes).
- **F4-2 [BAJO/verificar]** El chi² de proporciones de clase entre `train/val/test`
  (`:860`) es casi circular si los splits son estratificados; el texto ya lo matiza
  (`:803`), así que es aceptable pero conviene dejarlo explícito.
- **Lo que SÍ está bien:** `fase4_drift` (×5, KS/Wasserstein/PSI desglosado) y
  `fase4_pca` (×5) son análisis real, no duplican tablas.

## Fase 5 — `notebooks/fase5.ipynb` (lógica en `src/fase5_feature_selection.py`)

- **F5-1 [MEDIO — trazabilidad; REVERTIDO]** Antes lo marqué ALTO ("variance debe ir
  sobre datos crudos"), heredando un `.md` de IA. **La fuente primaria lo revierte:**
  Solorio-Fernández et al. 2020 (`docs/papers`) estandariza TODO antes de variance y lo
  usa como baseline degenerado. Por tanto el código (`variance` sobre `StandardScaler`,
  `:547`/`:148`) **es consistente con la referencia, no es un bug**. El defecto real es el
  **etiquetado**: el registro decía "varianza cruda" y la narrativa heredada "ordena por
  escala", pero el cálculo es varianza sobre estandarizado ≈ baseline degenerado. Estado:
  se mantiene el cálculo y se corrigió la etiqueta a "varianza tras escalado". Detalle
  en `contraste_papers.md`.
- **F5-2 [MEDIO]** Muestreo inconsistente entre métodos: `variance`, `f_classif`,
  `mutual_correlation` y `feature_similarity` usan el `x_train` completo, mientras el
  resto pasa por `crear_muestra` (submuestra de filas) (`:534-537`). La comparación
  entre métodos no es homogénea en tamaño muestral. Verificar si es deliberado y, si lo
  es, documentarlo.
- **F5-3 [MEDIO — estructura, paso 2]** El cuaderno SÍ narra por dataset (§5.9) y por
  figura; **no es un cascarón narrativo**. El defecto real: el núcleo de los 12
  selectores vive en `src` y se invoca con `fs.*` sin verse construir. En la fase donde
  el roster ES la contribución, conviene mostrar la creación de al menos los selectores
  espejo de QFS (relevancia, redundancia, mRMR/RRFS) en el cuaderno. Ver
  `estructura_notebooks.md`.
- **F5-4 [BAJO — figuras]** Todas las figuras son heatmaps/resúmenes que duplican tablas
  de estabilidad/redundancia; ninguna añade una lectura que la tabla no dé.

## Fase 6 — `notebooks/fase6.ipynb` (lógica en `src/phase6_modeling/pipeline.py`)

- **F6-1 [ALTO]** SHAP desperdiciado. `shap_candidato` (`:568`) calcula el objeto SHAP
  completo (signo, por instancia, por clase) pero `shap_values_array` (`:554-565`) lo
  colapsa a media|SHAP| por variable (`np.mean(np.abs(values), axis=(0,2))`, `:560`)
  antes de guardar nada. `plot_shap_dataset` (`:633-641`) es un `sns.barplot`, **no** un
  beeswarm, pese a que el fichero se llama `shap_summary_*`. Se tira la dirección del
  efecto, el comportamiento por instancia y por clase (crítico en olive_oil 3/9). La
  matriz cruda no se persiste. **Arreglo:** persistir la matriz y dibujar
  `shap.summary_plot` (beeswarm) por modelo-dataset, con desglose por clase donde
  aplique.
- **F6-2 [MEDIO — defensibilidad]** `SELECTOR_TIE_PRIORITY_BY_DATASET` (`:53-63`):
  prioridades de desempate hardcodeadas solo para `breast_cancer_wisconsin` y
  `olive_oil_3class`, sin justificación en el texto. Aunque solo rompe empates exactos
  de macro-F1/balanced-accuracy/reduction (`:396-399`), es una elección post-hoc que un
  tribunal cuestionaría. Sustituir por un desempate neutral y determinista (p. ej.
  alfabético) o justificar cada prioridad explícitamente.
- **F6-3 [MEDIO — estructura, paso 2]** El cuaderno narra por dataset (§6.6) y por figura
  (§6.12); **no es un cascarón narrativo**. El defecto real: el protocolo que constituye
  el aporte (entrenamiento, bootstrap, permutaciones, SHAP) vive en `src` (`p6.*`) y no
  se ve construir. Conviene mostrar la creación del cálculo SHAP y del contraste en el
  cuaderno. Ver `estructura_notebooks.md`.

## Fase 7 — `notebooks/fase7.ipynb` (lógica en `src/fase7_evidencia.py`)

- **F7-1 [BAJO — estructura, paso 2]** El cuaderno narra por dataset (§7.4 "Evidencia:
  `<dataset>`") con lectura por figura; **no es un cascarón narrativo**. El núcleo
  (consolidación, veredicto) vive en `src` (`f7.*`); mostrar la regla de decisión en el
  cuaderno reforzaría la trazabilidad.
- **F7-2 [BAJO/verificar]** La lógica de decisión (`:236-240`) usa
  `UMBRAL_EFECTO_PRACTICO`; comprobar que está definido y justificado.
- **F7-3 [BAJO]** Las figuras `fase7_mini_resumen_*` ya tienen lectura por dataset en
  §7.4; revisar que cada una aporte algo que la tabla no.

## QFS_MAIN — `QFS_based_on_NA/QFS_MAIN.ipynb` (parte cuántica)

- **Q-1 [MEDIO]** Doble import contradictorio: `import matplotlib.pyplot as plt` y
  `import matplotlib.pylab as plt` (cell 1); el segundo pisa al primero.
- **Q-2 [MEDIO — defensibilidad]** Usa datasets **distintos** a las fases 1-7 (Telco
  Churn, Adult, Bank Marketing) frente a (breast_cancer, customer_churn, madelon,
  olive_oil). La parte cuántica queda desconectada del pipeline clásico; hay que
  alinear datasets o justificar la diferencia.
- **Q-3 [BAJO]** Mucho código comentado (cells 5, 16, 22, 25) y `label` cambiado a mano
  (CHURN→ADULT en cell 31, que referencia resultados quizá no generados en la corrida).
  No es reproducible de un tirón.
- **Q-4 [MEDIO]** Estilo crudo exploratorio frente a las fases generadas pulidas:
  inconsistencia de calidad dentro de la misma memoria.

## Transversal

- **T-1 [MEDIO — estructura]** Corregido respecto a la versión inicial: NO hay asimetría
  de narrativa (las 7 fases narran por dataset). El único defecto transversal es el
  **paso 2 de la estructura canónica** en las fases pesadas (5-7): el núcleo metodológico
  —que es la contribución— vive en `src` y no se ve construir; el cuaderno solo lo invoca
  (`fs.*`, `p6.*`, `f7.*`). El arreglo NO es hacer los cuadernos más delgados (eso sería
  ir en contra de la estructura deseada), sino **subir al cuaderno la creación del núcleo
  metodológico** (selectores espejo de QFS, cálculo SHAP, contraste), dejando en `src`
  solo el *plumbing* (E/S, formateo). Acepta cuadernos más largos. Ver
  `estructura_notebooks.md`. Las funciones inline de 1-4 son el modelo a imitar, no a
  corregir.

---

La estructura canónica que todo arreglo debe respetar está en
`docs/auditoria/estructura_notebooks.md`. El contraste con las fuentes primarias (papers
+ código QFS), que revierte el hallazgo de `variance` y expone la divergencia de protocolo
con los papers, está en `docs/auditoria/contraste_papers.md`. Los prompts de arreglo, uno
por notebook (más `prompt_transversal.md`), están en `docs/auditoria/prompt_*.md`.
