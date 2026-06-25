# Análisis multidimensional de QFS — aterrizado en las variables (canónico 100×100)

Fecha: 2026-06-15. Análisis sobre los resultados canónicos verificados (`revision_independiente_postrerun.md`).
No menciona dimensiones en abstracto: cada una se relaciona con las variables reales. Lentes: **L1 fidelidad,
L2 posición-en-métodos, L3 robustez, L4 parsimonia-coherencia**. Espina: régimen → mecanismo → resultado.

## 1. Por dataset (régimen, en variables concretas)
- **Breast Cancer:** la señal vive en las medidas **"_worst"** (concave_points_worst I=0.415, radius_worst 0.404,
  concave_points_mean 0.398). La redundancia es la **familia de tamaño**: radius~perimeter~area (R_ij hasta
  **1.13**, VIF 3806). Régimen: señal fuerte + multicolinealidad extrema en un eje (tamaño).
- **Customer Churn:** señal concentrada en **support_calls (0.229) ≫ total_spend (0.164) > contract_Monthly
  (0.130) > payment_delay (0.092) > age (0.086)**; el resto ~0. Única redundancia real: la espiga one-hot
  **gender_Female~gender_Male (0.68)** + dummies de subscription/contract (~0.17). Régimen: señal en 4-5
  continuas, fondo independiente, baseline saturable (≈1.0).
- **Madelon:** **todas las I_i son ínfimas** (feat_241 es la "top" con 0.026; el resto ≤0.023). Redundancia
  alta solo en pares construidos (feat_48~feat_378=0.99, feat_241~feat_475=0.94). Régimen: la MI por pares es
  **estructuralmente ciega** (PCA 295/500). 
- **Olive 3/9:** composición de ácidos grasos; relevancia en **other, linolenic, linoleic, stearic**;
  redundancia compositional moderada (linoleic~linolenic ~0.5). Régimen: separable; Olive9 limitado por n=86.

## 2. Métodos de selección — dónde cae QFS entre los 12 (por variables)
- **QFS es clase-mRMR donde el régimen lo permite:** Olive3 QFS≈oráculo (difieren solo stearic↔linoleic, ambos
  →1.0); Madelon QFS∩oráculo = 8/10.
- **Churn — el desvío que explica el deterioro:** QFS-NA seleccionó **grupos one-hot ENTEROS** (las 3
  subscription_type + contract Annual&Monthly) y **descartó continuas con señal** (payment_delay, tenure,
  last_interaction). El **oráculo** hace lo correcto: 1 dummy por grupo (subscription_Premium, contract_Monthly)
  + las continuas. → QFS cae fuera del nicho mRMR (L2) y ese es el mecanismo del déficit de optimizador.
- **Breast Cancer:** QFS-NA retiene radius_mean + radius_worst + perimeter_mean (pares redundantes de tamaño):
  control de redundancia imperfecto, pero el resultado iguala al baseline (régimen permisivo).

## 3. k — no el número, sino qué variable entra (orden de mérito)
La escalera-α del óptimo exacto ES el orden natural de entrada por presupuesto:
- **BCW:** concave_points_worst (α0.1) → concave_points_mean, texture_worst (α0.6) → … el "frente útil"
  aparece pronto; subir k añade tamaño redundante.
- **Churn:** support_calls (α0.1) → contract_Monthly (0.3) → total_spend (0.4) → payment_delay (0.5) → age
  (0.6) → gender/tenure (0.7). El orden prioriza las continuas; los dummies entran tarde. (QFS-NA invierte
  esto: mete dummies antes de payment_delay → su error de k es seleccionar el grupo equivocado.)
- **Madelon:** feat_241 (α0.1) y luego **escalera PLANA hasta α0.9-1.0** (entran 16 de golpe). No hay "frente":
  con I_i≈0.02 el criterio no puede ordenar variables → ningún k pequeño captura la señal. **k no arregla
  Madelon** porque el problema es el criterio, no el presupuesto.

## 4. alpha — el mando de cardinalidad, leído en su INPUT
α recorre la cardinalidad (Mücke) en los 5 datasets (L1: el mecanismo funciona). Pero su **calidad depende del
input I_i**: en BCW/Churn/Olive la escalera ordena variables con sentido; en **Madelon la escalera es
degenerada** (plana) porque las relevancias son ~0.02 — α funciona, pero recibe relevancias casi sin
información. Separar "α funciona" de "α recibe señal" es la lectura correcta del fallo de Madelon.

## 5. beta — reordena, pero no es la causa del deterioro
β elegidos: BCW 0.2, Churn 0.3, Madelon 0.5, Olive3 0.0, Olive9 0.4; dist_ratio 0.45 (relajado desde 0.707,
declarado). β reordena la densidad de Rydberg (mando real, L1), pero con el embebido canónico (100 MDS) el
**error de embebido de Churn (0.217) es el más bajo de los grandes** → la geometría/β **no** explica el déficit
de Churn (refutado). β queda como segundo grado de libertad documentado, no como causa.

## 6. Modelos — qué variable sostiene cada modelo (SHAP) y dependencia del modelo
- **BCW:** SHAP top = texture_worst (0.96), radius_worst (0.88), area_worst (0.86), concave_points_worst —
  **todas en la selección de QFS** → coherencia (L4): lo que el modelo usa es lo que la selección retuvo.
- **Churn:** **support_calls domina (SHAP 3.65)**, luego age/total_spend/contract_Monthly — todas presentes en
  QFS-NA. Por eso, aunque QFS malgaste cupos en dummies redundantes, **conserva el driver dominante** → el
  deterioro es pequeño (0.03).
- **Madelon (la prueba del criterio):** el modelo se apoya en **feat_336, feat_105, feat_153** — que la **MI NO
  rankeó alto** (su top era feat_241). El criterio MI y lo que el modelo necesita **no coinciden** → fallo de
  criterio confirmado a nivel de variable. Dependencia del modelo: la ganancia de seleccionar cae +0.28 (RF) →
  +0.094 (XGBoost), porque XGBoost recupera de los distractores señal de interacción que la MI no ve.
- **Olive:** SHAP = other, linolenic, linoleic, stearic — presentes en las selecciones.

## 7. Métricas — macro-F1 vs AUC, por qué importa
- **Churn:** el deterioro es pequeño también en AUC (QFS-NA 0.983 vs baseline 1.000): no es un artefacto de la
  métrica, es un techo saturado con poco margen.
- **Olive9:** multiclase desbalanceado (9 clases, n_test=86) → **AUC binario no aplica**; macro-F1 es la métrica
  correcta y su IC ancho es lo que vuelve el caso inconcluso (honestidad, no mejora oculta).

## 8. Tests estadísticos — resolución y qué autorizan
- Selección: 20 permutaciones → p mínimo 1/21≈**0.048**; FDR conserva en Madelon **13/500** (la multiplicidad
  muerde donde la señal es escasa).
- Modelado: bootstrap **400** (test CI) y sign-permutation **2000**; label-permutation **500** → p mínimo
  1/501≈**0.002**. Estos contrastes son los que **autorizan atribuir** los deterioros a criterio/optimizador en
  vez de al azar/fuga/split.

## 9. Consistencia (3 semillas / permutaciones / bootstrap) — y qué variable baila
- **Selección:** filtros y MI (mrmr, f_classif) → **Jaccard 1.00** (deterministas). La variabilidad se
  concentra en **random_forest** (estocástico, Jaccard 0.82) y en empates casi-exactos. **Lo que baila son
  sustitutos equivalentes:** Madelon RF intercambia **feat_28↔feat_48** (los de VIF 95/68, redundantes por
  construcción); Churn mRMR intercambia **subscription_type_Basic↔Standard** (dummies mutuamente excluyentes);
  Olive9 RF **palmitoleic↔stearic** (compositionalmente próximos). → inestabilidad **benigna**: cambia el
  representante, no la información (L3).
- **Modelado y QFS:** una sola corrida; su robustez NO es por re-semillar sino por **bootstrap + permutación**
  (modelado) y **100 inicializaciones MDS + 10000 shots** (QFS). Honesto: la consistencia es heterogénea; una
  consistencia "fuerte" multi-seed de modelado/QFS sería experimento nuevo.
- Lectura: la estabilidad alta NO discrimina entre métodos (todos estables) → el diferenciador es la
  redundancia interna, no la reproducibilidad. Y donde QFS "falla" (Churn), falla justo eligiendo entre los
  sustitutos casi-equivalentes (dummies) que también hacen bailar a los clásicos.

## 10. Todo en conjunto — régimen → mecanismo → resultado (con variables)
- **Madelon** = criterio: I_i≈0.02 (escalera α plana) + el modelo usa feat_336/105/153 que la MI no ve →
  oráculo también cae (0.643) → el límite es la formulación MI, no el hardware. Deterioro grande (0.21).
- **Churn** = optimizador leve: régimen de señal continua + one-hot; QFS-NA mete grupos de dummies y suelta
  payment_delay/tenure → pierde 0.03 frente a un baseline saturado; el oráculo (continuas + 1 dummy/grupo)
  recupera 0.999. No es geometría. Deterioro pequeño.
- **BCW / Olive3** = sin fallo: QFS iguala con menos variables, las mismas que sostienen el modelo (SHAP).
- **Olive9** = inconcluso (n=86): el oráculo sube a 0.906 con stearic/oleic, QFS-NA usa palmitoleic/linoleic;
  el IC no permite afirmar.

**Veredicto por lentes:** L1 el método se comporta como su teoría (α↔cardinalidad, β reordena, MDS verificado);
L2 QFS = clase-mRMR salvo en Churn (se sale del nicho hacia los dummies); L3 selección estable, inestabilidad
solo entre sustitutos equivalentes; L4 lo seleccionado coincide con lo que el modelo usa (salvo Madelon, donde
ni la MI ni la selección ven lo que el modelo necesita). La aportación se sostiene: una referencia clásica que
**predice (por régimen) y atribuye (criterio vs optimizador)** el comportamiento de QFS, a nivel de variable.
