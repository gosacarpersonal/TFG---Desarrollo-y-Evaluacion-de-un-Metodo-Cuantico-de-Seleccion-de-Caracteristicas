# Síntesis: qué cambian los hallazgos (VIF, PCA, regímenes) y cómo afectan al análisis de QFS

> 2026-06-15. Respuesta a tres preguntas, contrastando con TODOS los resultados (clásico + cuántico).
> Capturado por escrito (no en la cabeza). Cifras de `results/tables/` (fases 1–9).

> **⚠ ACTUALIZADO TRAS RE-RUN CANÓNICO 100×100 MDS (2026-06-15).** Las cifras QFS de las secciones
> originales se calcularon con el atajo de 4 corridas MDS y quedan OBSOLETAS. Answer key vigente en
> `protocolo_revision_fase10.md`. Cambios clave: **Churn deterioro 0.078→0.030** (optimizador leve, no
> fuerte); **BCW "mejora" 0.950 era ESPURIA → ahora 0.937 = baseline**; Madelon criterio 0.170 intacto.
> **La hipótesis geométrica/one-hot de Churn queda REFUTADA por el error de embebido canónico**: Churn
> (0.217) embebe MEJOR que Madelon (0.250) y BCW (0.231) y aun así se deteriora → el embebido NO es la
> causa. La sección "β/geometría" de abajo está reescrita en consecuencia.

---

## Q1 — ¿Cómo afectan estos hallazgos a lo que ya sabíamos de los datasets?

No contradicen lo que sabíamos; lo **cuantifican, lo agudizan y lo hacen accionable**. Antes teníamos
descripciones cualitativas ("BCW tiene redundancia", "Madelon vive en interacciones"). Ahora tenemos una
**descomposición de la dificultad de cada dataset en dos ejes** — relevancia y redundancia — que es
exactamente el sistema de coordenadas del método QFS (y del espejo de 12). Tres saltos concretos:

1. **VIF separa dos redundancias que antes se confundían.** BCW: VIF máx **3806**, 23 vars ≥10 →
   multicolinealidad lineal *pervasiva*. Madelon: VIF≈**1.3** en casi todo, solo feat_28/48/64 (~70–103) →
   redundancia *escasa y local*. Churn: VIF≈1 → *sin* colinealidad. Olive: VIF 326 (5 vars) → redundancia
   composicional. Implicación: **el término de redundancia del criterio (Σ R_ij) solo tiene "trabajo" que
   hacer en BCW y Olive**; en Madelon y Churn está prácticamente ocioso.
2. **PCA cuantifica la dimensión intrínseca.** Madelon: **295/500** componentes para el 80% de varianza →
   el ruido es alta-dim genuina, no un manifold bajo. BCW 5, Churn 6, Olive 3 → datos genuinamente
   bajo-dimensionales (por eso seleccionar a k=5–10 no pierde nada). El **gap entre dim. intrínseca (295) y
   dim. de la señal (20 por construcción)** es la huella numérica del "desierto de distractores".
3. **La estructura fina de R_ij en Churn** (verificada): casi plana con **una espiga one-hot**
   (`gender_Female↔Male`=0.68) y un triple `subscription_type` (~0.17); 1 solo par >0.3 de 105. Esto NO se
   sabía y es decisivo (ver Q3-β y Q3-optimizador).

**Lo nuevo y más potente:** podemos decir, por dataset, **cuál de las dos mitades del criterio MI está en
juego**: Madelon = problema del eje RELEVANCIA (MI ciega, redundancia ociosa); BCW = eje REDUNDANCIA
cargado (VIF 3806) con relevancia fuerte; Churn = ambos ejes fáciles; Olive = relevancia fuerte + redund.
moderada. El plano criterio/optimizador no podía resolver esto; VIF+PCA sí.

---

## Q2 — ¿Aporta valor extra a la memoria del TFG?

Sí, y cambia el *estatus* del bloque clásico:

- **Convierte la caracterización en un instrumento PREDICTIVO, no en contexto.** Antes la fase 1 "describía"
  los datos. Ahora el régimen (VIF/PCA/efecto) **predice el modo de fallo de QFS antes de ejecutarlo**:
  "Madelon: efecto 0.02 + PCA 295 + VIF≈1 ⇒ un criterio MI fallará por relevancia, lo herede quien lo
  herede" — y se cumple (mRMR clásico y QFS caen igual). El bloque clásico deja de ser "preparación" y pasa
  a ser una **teoría falsable del comportamiento de QFS**.
- **Blinda flancos de defensa.** A "¿el fallo de Madelon es mala suerte?" se responde con dimensión
  intrínseca y ceguera estructural de la MI de pares. A "¿por qué Churn cae (poco)?" se responde, tras el
  re-run canónico, que NO es geometría (embebe mejor que los demás) sino un déficit menor de optimizador
  cerca de un baseline saturado — no un encogimiento de hombros, pero tampoco la historia geométrica.
- **Distingue el TFG del paper.** El paper evalúa 3 binarios sin análisis de régimen; **el valor añadido del
  TFG es caracterizar CUÁNDO y POR QUÉ el método funciona en función del régimen del dato** — justo lo que
  la propuesta pedía ("estudio comparativo") elevado a explicación causal.
- **Observación metodológica (one-hot), degradada a nota:** el TFG codificó Churn con **one-hot** frente al
  **label-encoding** del paper; el one-hot crea redundancias entre dummies complementarias (gender 0.68).
  Era candidato a causa del fallo de Churn, pero el error de embebido canónico lo **descarta como mecanismo**
  (Churn embebe mejor que Madelon/BCW). Queda como diferencia de preprocesado declarable (limitación/contexto),
  NO como causa del deterioro. Una ablación de encoding solo-Churn lo cerraría del todo, pero ya no es prioritaria.

---

## Q3 — Cómo afecta al análisis de QFS por dimensión (contraste clásico ↔ cuántico)

### Dataset
El régimen pasa a ser la variable ORGANIZADORA: cada veredicto de QFS se *explica* por régimen.
Madelon→criterio, Churn→optimizador, BCW/Olive3→sin fallo, Olive9→inconcluso por n. Ya no es un marcador.

### Métodos de selección
La descomposición por VIF dice **qué mitad del criterio ejercita QFS**. En BCW (VIF 3806) el término de
redundancia es portante → probar QFS-como-mRMR es significativo (y lo cumple, ≈mRMR). En Madelon (VIF≈1) el
término de redundancia está ocioso → QFS es de facto un *ranker de relevancia*, y por eso falla como todos
los de relevancia. El mapa de los 12 debe **leerse a través de la estructura VIF**, no en abstracto.

### k
La dim. intrínseca (PCA) fija el "k natural": BCW 5, Olive 3, Churn 6 ⇒ k=5–10 es lossless. Madelon: dim.
intrínseca 295 pero señal en 20 ⇒ **ningún k pequeño captura la varianza, pero sí la señal** — la
trayectoria en k debe contrastar dim-intrínseca vs dim-señal. Conecta con el "QFS brilla en k pequeño" del
paper: aquí solo aplica donde hay señal compacta (no Madelon).

### α
El mecanismo (recorrer α = recorrer cardinalidad, Mücke) **funciona siempre** (L1 fidelidad) — pero su
INPUT (I_i) está degenerado en Madelon (efecto 0.02 ⇒ I_i casi plano ⇒ orden casi aleatorio). Separar
"α funciona" de "α recibe relevancias informativas" (depende del régimen) es la lectura correcta.

### β / geometría  (REESCRITO tras re-run canónico — la cadena geométrica queda REFUTADA)
La hipótesis previa (one-hot ⇒ R_ij plana ⇒ MDS frustrado ⇒ optimizador falla) **no sobrevive a los números
canónicos**. Con MDS 100×100, el **error de embebido de Churn (0.217) es el MÁS BAJO de los tres datasets
grandes** (Madelon 0.250, BCW 0.231): Churn embebe *mejor* y aun así es el que se deteriora por optimizador.
Por tanto **el embebido NO explica el fallo de Churn**, y la geometría/one-hot deja de ser el mecanismo (era,
en buena parte, un artefacto del atajo de 4 corridas, que inflaba Δcoste y el deterioro).
Lo que SÍ se sostiene: Churn = **déficit menor de optimizador** (total 0.030; optimizador 0.030 vs criterio
0.0007), cerca de un baseline saturado (≈1.0) que deja poco margen. El **oráculo recupera 0.999** → el
criterio está bien; el pequeño hueco proviene del readout analógico (densidad top-k) en un espacio de
redundancia casi plana, que retiene dummies complementarias — pero el efecto es pequeño y NO geométrico.
β sigue siendo un mando real (reordena densidades), y dist_ratio (0.45/0.35/0.25) sigue declarado como
divergencia honesta; pero **no son la causa del deterioro de Churn**. La cadena "régimen de redundancia →
fallo de optimizador" queda como conjetura no confirmada, no como hallazgo.

### Modelos
La dependencia del modelo es función de la dim. intrínseca: XGBoost maneja los 295 dims de distractores de
Madelon (árboles/regularización) y recupera señal aun con ruido ⇒ la ganancia de selección **se desploma
+0.28→+0.094**. La "necesidad de seleccionar" depende del modelo *en proporción a la dim. intrínseca del
ruido*. En datasets bajo-dim (BCW/Olive/Churn) el modelo apenas cambia el veredicto.

### Métricas
El régimen de Olive 9 (desbalance 8.24 + 86 filas test) explica a la vez **por qué macro-F1** (no AUC
binario) y **por qué es inconcluso** (IC anchos). Métrica y prudencia son consecuencia del régimen, no
decisiones sueltas.

### Tests estadísticos
Las lecturas de la cadena adquieren significado de régimen: FDR mata 25/500 en Madelon (donde la
multiplicidad muerde), efecto 0.02 (magnitud), shift=0 y adversarial≈0.5 (descartan que preprocesado/split
expliquen nada), permutación+bootstrap hacen **creíbles los deterioros** (no ruido). Los tests son lo que
permite ATRIBUIR en vez de adivinar — sin ellos, Madelon y Churn serían "QFS pierde" indistinto.

### Todo en conjunto
Emerge un **modelo causal régimen → mecanismo → resultado**: el bloque clásico mide el régimen; el régimen
predice cuál de {relevancia-criterio, redundancia/embebido-optimizador} será el cuello de botella; la fase
cuántica confirma la predicción. El TFG no reporta "QFS empata/pierde": construye y valida una **teoría
predictiva de cuándo se rompe cada componente de QFS**, sobre 5 regímenes.

---

## Cómo proceder a partir de aquí (implicaciones)

1. **El blueprint del notebook (`plan_notebook_visualizaciones.md`) gana un eje rector:** cada instrumento
   se ancla en el régimen y termina en "qué predijo el régimen / qué confirmó el resultado".
2. **Reordenar la PARTE A** para incluir VIF y PCA como ejes explícitos (relevancia-eje vs redundancia-eje),
   no solo efecto/redundancia cualitativos.
3. **El recompute de átomos (D9) tiene ahora una pregunta concreta:** ¿la R_ij one-hot de Churn produce un
   embebido frustrado (alto error, dist_ratio bajo) frente a Olive/BCW? Es la prueba de la hipótesis causal.
4. **Nuevo material para la memoria:** (a) régimen como predictor; (b) one-hot vs label-encoding como causa
   raíz candidata del fallo de Churn (limitación + future-work); (c) decomposición relevancia/redundancia
   por VIF como lectura del espejo de 12.
5. **Honestidad:** la cadena de Churn es una **hipótesis bien motivada** (verificada en estructura R_ij +
   dist_ratio + Δcoste + corroborada por el paper), pendiente de confirmar con el error de embebido del
   recompute. Madelon embebe bien (Δcoste≈0): su fallo NO es geométrico, es de criterio. No mezclar.

---

## REVISIÓN (2026-06-15): ¿one-hot fue un error? ¿la del paper es mejor? ¿re-ejecutar?

**Corrección a una sobreafirmación previa:** dije que el one-hot "fabrica la redundancia patológica" como
causa clara del fallo de Churn. Es más sutil y podría ser al revés. Matices:

- **¿Hicimos mal?** No. Churn tiene categóricas NOMINALES (gender, subscription_type, contract_length).
  Con modelos lineales, label-encoding impone orden falso (Basic<Premium<Standard); el one-hot lo evita.
  El paper label-encodea **por conveniencia** (su texto), no por rigor. En el bloque clásico, one-hot es
  defendible y arguablemente MÁS correcto.
- **¿La del paper es mejor? Trade-off, no inequívoco.** One-hot inyecta redundancia artificial
  (gender_Female↔Male=0.68 es la codificación, no redundancia real). PERO el paper dice "baja redundancia →
  matriz plana → embebido más difícil"; Churn tiene redundancia intrínsecamente ~nula (VIF≈1), así que
  label-encoding la dejaría AÚN MÁS PLANA → podría EMPEORAR el embebido. La espiga one-hot es artificial pero
  es casi la única estructura. **No se puede saber sin probarlo.**
- **¿Afecta a los resultados? No los invalida.** Comparación interna justa (QFS y clásicos consumen las
  mismas I_i,R_ij). El bloque clásico con one-hot es correcto. El deterioro de Churn ya era "fallo de
  optimizador"; esto solo enriquece la causa candidata. Es CIENCIA (sensibilidad de QFS al preprocesado en
  baja redundancia), no error a esconder. Dato verificado: QFS-NA seleccionó grupos de dummies enteros
  (gender_Female+Male, las 3 subscription, las 3 contract) → redundante, justo lo que debía evitar.
- **¿Re-ejecutar TODO? NO.** Sobrerreacción cara para algo no roto. Orden recomendado: (1) **D9 barato**:
  recomputar solo el embebido MDS desde R_ij existentes y comparar error de embebido Churn vs Olive/BCW (sin
  re-ejecutar QFS); (2) **si se quiere certeza causal: ablación TARGETED solo Churn** (fases 8–9) con
  variante label-encoding y/o one-hot `drop_first` → resuelve si el encoding es la causa o si falla igual por
  baja redundancia intrínseca; (3) **no tocar** bloque clásico ni los otros 4 datasets. Decisión del autor
  pendiente.
