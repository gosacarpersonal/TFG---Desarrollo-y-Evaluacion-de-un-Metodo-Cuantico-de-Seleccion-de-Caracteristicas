# Auditoría de redacción y evidencia de la memoria — 2026-06-18

Origen: el autor para la lectura tras detectar problemas recurrentes en los
capítulos 1–5 (hasta §5.3). Este documento (1) evalúa cada observación suya,
(2) eleva esas observaciones a **patrones sistemáticos** cuantificados sobre
los `.tex`, y (3) barre lo que aún no había leído (§5.4–§5.6, conclusiones y
apéndice) buscando los mismos defectos.

Ficheros auditados: `Plantilla_Latex_GCD/tfgs/tex/{introduccion,marco_teorico,
estado_arte,metodologia,resultados,conclusiones,apendice}.tex`.

---

## 0. Diagnóstico de cabecera (lo que une todas sus quejas)

Tres mediciones objetivas sobre el cuerpo sostienen casi toda su crítica:

| Métrica | Dato | Implicación |
|---|---|---|
| **Figuras vs tablas en el cuerpo** | resultados: **20 figuras / 3 tablas**; apéndice: 9 fig / 1 tabla; metodología: 2 fig / 1 tabla | El documento "habla con cifras en prosa y las ilustra con gráficas", pero **casi nunca tabula**. De ahí "faltan tablas" + "gráficas pochas". |
| **Fugas de andamiaje "fase N"** | 16 apariciones de `fase [0-9]` en resultados + conclusiones | El texto final conserva el lenguaje de proceso interno (fase 1…10). |
| **Letanía de garantías repetida** | "datos auditados / particiones sin fuga / contrastes estadísticos explícitos" aparece **3 veces** casi literal (intro l.88-89, estado_arte l.101-102) + variantes | Boilerplate copiado entre capítulos → sensación de relleno y de redacción que "cambia y se repite". |

El defecto raíz es **uno**, y explica el 80 % de la lista: **la memoria afirma
y promete mucho ("se comprobó", "se confirmará", "separa dos preguntas",
nombra 6 tests) pero NO cierra el bucle evidencia↔afirmación**: o no enseña la
tabla, o no apunta a dónde está, o la entierra en una figura ilegible. La regla
correctora es una sola y debe aplicarse en todo el documento:

> **Toda magnitud que se nombre debe (a) estar definida la primera vez que se
> usa, (b) materializarse en una tabla con valores reales, y (c) cuando se
> anuncia en metodología/marco, llevar un forward-reference a la tabla de
> resultados donde se demuestra.** Nada se queda "en el aire".

Esto es exactamente lo que ya pediste para §2.6 (que cruza secciones): replícalo
con **tablas de resultados**, no solo con secciones.

---

## 1. Evaluación de TUS observaciones (una a una)

**Motivación / Objetivos (intro l.43-51 y l.86-98).** De acuerdo en el fondo,
matiz importante: esas dos frases ("para que la evaluación sea defendible…
caracterizar dónde reside la señal, la redundancia, la dimensionalidad
efectiva…") **no son el problema en sí: son un contrato**. El problema es que el
contrato **no se cobra visiblemente**. La caracterización SÍ existe (§5.1.4
"Regímenes del banco", VIF/PCA/I_i), pero la motivación no dice "esto se
demuestra en la Tabla X / Figura Y". Acción: o conviertes esas frases en
promesa con destino ("…como se caracteriza en la Tabla de regímenes, §5.1.4"),
o las recortas. Tal como están, anuncian sin firmar.

**Comp. cuántica adiabática (§2.3) — diagrama.** Correcto y barato de arreglar.
Hoy §2.3 es 100 % prosa. Un único esquema (H_inicial → evolución lenta →
H_final, con el gap de energía) ancla el teorema adiabático. Idéntico para…

**Átomos neutros y bloqueo de Rydberg (§2.4) — diagrama.** De acuerdo. Es el
mecanismo central del TFG y se explica solo con texto y la fórmula van der
Waals (eq. 2.5). Un esquema (dos átomos, radio de bloqueo, "solo cabe una
excitación") es la figura conceptual que más rentabiliza el capítulo. **Nota
de coherencia:** son los **dos únicos diagramas conceptuales** que pedirías en
todo el marco — y el marco hoy tiene **0 figuras**. Eso refuerza que el
problema no es "faltan figuras" en general, sino que **están donde no aportan
(resultados) y faltan donde explicarían (marco)**.

**§2.5 Validación estadística — apuntar a las tablas de resultados.** Totalmente
de acuerdo y es **el patrón nº1 del documento**. §2.5 enumera 4 salvaguardas y
~8 tests (BH, Cliff, ε², Cramér, permutación, bootstrap…) y **no apunta a
ninguna evidencia**. Igual que §2.6 cruza secciones, §2.5 debe cruzar a las
**tablas** donde cada salvaguarda se cobra. Hoy el lector llega al final del
marco con una promesa y sin recibo. (Ver §3.1 de este informe: hay tests que ni
siquiera se explican.)

**§3.4 (estado_arte l.97-104) "El hueco que este TFG aborda…".** De acuerdo: es
**redundante**. Repite casi literalmente la letanía "datos auditados,
particiones sin fuga, contrastes estadísticos explícitos, estabilidad y
redundancia" que ya está en intro l.88-89. El estado del arte debe decir **qué
falta en la literatura** (lo dice bien: solo binarios, dim. moderada, un
protocolo); **no** repetir tu solución. Recorta la segunda mitad del párrafo a
una frase.

**§4.4.2 (metodología l.397-400) "separa dos preguntas…".** Matiz clave que
te tranquiliza: **esto SÍ se demuestra** — es la Tabla 5.2 (`qfs-control`,
Hamming + Δcoste) y la Figura `criterio-optimizador` (F09). El defecto no es
que falte evidencia, sino que **la metodología no remite a ella**. Añade
"(véase Tabla~\ref{tab:qfs-control} y §5.5)". Patrón nº1 otra vez.

**§4.5 — "sobra el gráfico de mierda" (Figura `recorrido-tfg`, ev4).** Es la
figura del recorrido de 10 fases. Decisión tuya como autor; mi lectura: el
diagrama **duplica** la lista enumerada de 10 fases que está justo debajo
(l.453-496). O te quedas con la figura **o** con la lista, no con ambas. Si la
figura es de las "pochas" (volcado de cajas), elimínala y deja la enumeración,
que es más precisa.

**§4.5.1-5 — faltan evidencias / referencias a las tablas, y ¿sobra §4.5.5?**
De acuerdo en ambos:
- §4.5.3 (validación de particiones) lista χ², KS, Wasserstein, PSI, adversarial,
  pantalla de leakage **sin remitir a §5.1.3**, donde están los valores. Forward-
  reference obligatorio.
- §4.5.5 (Entorno y reproducibilidad) **es redundante con el apéndice**
  (`cap:apendice` §A.1 "Condiciones de reproducción" dice lo mismo: Python 3.12,
  semillas, separación lógica/ejecución). **Recomiendo fundir §4.5.5 en el
  apéndice** y dejar en metodología, como mucho, una frase. Tu instinto es
  correcto.

**§5.1.1 — "se confirmó que se cargan íntegros" es obvio; faltan explicar
M-W/K-W/χ²/BH y Spearman + tabla.** De acuerdo en todo:
- "se cargan íntegros / sin nulos / sin duplicados" → es verificación de
  fontanería; **degrádalo a media frase** o elimínalo.
- **Spearman no se define en ningún sitio** (verificado: solo aparece en
  resultados, nunca en el marco). Mann-Whitney/Kruskal-Wallis se **nombran**
  pero solo se explica su *tamaño de efecto* (Cliff/ε²), no qué contrastan.
- Falta la **tabla síntesis** (por dataset: nº vars que sobreviven FDR, efecto
  mediano, ρ Spearman pre/post). Las cifras existen en prosa (l.54-66): hay que
  **sacarlas a una tabla**.

**§5.1.2 — poner valores reales / cuidado figura que parte el párrafo.** De
acuerdo. El párrafo l.88-99 enuncia "KS, Wasserstein y PSI prácticamente nulos",
"Spearman 0.9996 / 1.0 / 0.988", "ΔMI < 0.02" — **todo tabulable**. Y sí: hay
figuras (`F03_base_confiable`) insertadas en medio del hilo de auditoría que lo
cortan. Regla: **una figura nunca dentro de un párrafo sin cerrar**; va tras el
punto y aparte, y referenciada antes de aparecer.

**§5.1.3 y §5.1.4 — tablas mejor que "visualizaciones pochas".** De acuerdo, y
es generalizable: §5.1.3 (particiones) y §5.1.4 (regímenes) son **densos en
números** (PSI máx 0.50; AUC adversarial 0.476–0.535; VIF 3806; PCA 295;
I_i por variable) que hoy van **en prosa + figura**. Una tabla por dataset
comunica esto sin pérdida. Las figuras `f10_a_regimenes` / `F03` pueden quedar
como **apoyo**, no como portadora única de la evidencia.

**§5.2.1 — "¿qué coño es un Jaccard medio?" + falta tabla + figuras ilegibles.**
De acuerdo, y es el ejemplo canónico del defecto. "Jaccard medio mínimo 0.76":
Jaccard SÍ está definido en metodología (eq. 4.x), pero **en el punto de uso no
se recuerda qué mide ni sobre qué se promedia** (¿entre semillas? ¿entre k?).
Toda esta subsección (estabilidad, permutación p≈0.048, redundancia interna,
coste 0.007/0.1-0.34/0.9/2.5 s) **es una tabla pidiendo nacer**: una fila por
método, columnas Jaccard / Kuncheva / p-perm / Δredundancia / coste. Hoy son
tres párrafos de cifras sueltas + figuras que no las contienen. Tu diagnóstico
("no cuesta nada poner una tabla") es exactamente la acción correcta.

**§5.2.2 — sección abstracta: falta dataset×modelo, métricas (no solo F1), y
qué variables eligió cada método.** **La observación más fuerte de tu lista** y
la comparto del todo. §5.2.2 (l.323-453) resume 260 experimentos en prosa +
una tabla que solo muestra **el mejor** subconjunto por dataset (Tabla 5.1).
No hay:
- desglose **por modelo** (LogReg/SVM/RF/XGB) — solo se menciona XGBoost en
  Madelon;
- métricas secundarias (AUC en binarios, exactitud balanceada) salvo de pasada;
- **qué variables selecciona cada método** en cada dataset (eso vive solo en el
  apéndice, Figura roster `a3`, y no se nombra en el cuerpo).
  Esto choca con tu tesis: prometes leer el proceso "variable a variable" y aquí
  el cuerpo no nombra ni una selección por método. Necesita una **tabla de
  candidatos por dataset×modelo** y, al menos, **nombrar las variables** de los
  mejores subconjuntos.

**§5.2.3 — solo se habla de "superar"; faltan las otras 2 dimensiones.** De
acuerdo y es un **fallo de coherencia con la tesis**. Desde la intro insistes en
relevancia/redundancia/estabilidad/coste como sistema de coordenadas, pero
§5.2.3 (comparación final, l.466-489) reduce el cierre a "igualar o superar
rendimiento". Debe cerrar **en las cuatro coordenadas**, no solo macro-F1.

**§5.2.4 — "no me queda claro qué queremos decir".** De acuerdo: §5.2.4
("El espacio de métodos como espejo de QFS", l.491-547) **adelanta resultados
de QFS** (Jaccard QFS-NA vs mRMR, J=0.82 churn…) **antes** de haber presentado
QFS (§5.3). Es un salto temporal confuso: usas QFS para "situarlo" en el espejo
clásico cuando el lector aún no sabe qué es QFS-NA. O se mueve **después** de
§5.3, o se reescribe como "predicción" pura sin cifras de QFS.

**§5.3 — "8 vars / 15 vars" sin nombrar cuáles; figura y Cuadro 5.2
ilegibles.** De acuerdo:
- l.553-555: "Olive Oil, 8 variables; Customer Churn, 15 tras one-hot" **no
  enlaza** con la composición real ni con §5.1.4 donde sí se nombran las
  variables. Añadir referencia cruzada.
- "Cuadro 5.2" = Tabla `qfs-control` (Hamming + Δcoste). Que "no se entienda" es
  problema de **caption insuficiente**: Hamming sobre qué espacio, signo de
  Δcoste, por qué α=0.5. El caption debe ser autoexplicativo.
- La figura señalada (`F08 mandos α-β` o el `beta_map`) entra en el patrón
  "gráfica que carga toda la conclusión y no se lee".

---

## 2. Los patrones, nombrados (para aplicarlos a TODO el documento)

1. **P1 — Afirmación sin recibo.** Se nombra una magnitud/test/propiedad y no
   se tabula ni se remite a dónde se demuestra. *(El más frecuente.)*
2. **P2 — Cifras en prosa que deberían ser tabla.** Listas de números dentro de
   un párrafo (Jaccards, p-valores, costes, VIF, errores MDS).
3. **P3 — Término usado sin definir en el punto de uso** (Spearman nunca; M-W/
   K-W/KS/Wasserstein/PSI solo nombrados; Jaccard/Kuncheva definidos lejos).
4. **P4 — Fuga de andamiaje de proceso** ("fase N", "170 ejecuciones", "260
   experimentos", "sin fallos"): registro de log, no de memoria.
5. **P5 — Boilerplate repetido** (letanía de garantías; "no es un mero
   baseline"; "régimen-mecanismo-resultado"; "espejo").
6. **P6 — Figura que parte el párrafo / figura como única portadora de
   evidencia que debería ir en tabla** ("gráficas pochas").
7. **P7 — Trivialidad de fontanería** ("se cargan íntegros", "sin fallos",
   "sin nulos") presentada como hallazgo.
8. **P8 — Caption no autoexplicativo** (no define ejes/unidades/signos).
9. **P9 — Incoherencia con la tesis de 4 coordenadas** (cerrar solo en
   rendimiento cuando se prometió relevancia/redundancia/estabilidad/coste).
10. **P10 — Orden temporal roto** (usar QFS antes de presentarlo).

---

## 3. Barrido de lo que NO habías leído (§5.4, §5.5, §5.6, conclusiones, apéndice)

### §5.4 Comparación entre enfoques (resultados l.643-794)
- **P4**: "protocolo idéntico de la **fase 6**" (l.647), "guardado por la **fase
  8**" (l.771).
- **P1/P9**: la comparación se cierra en macro-F1 (Tabla 5.3) y deltas; las
  coordenadas de redundancia/estabilidad de QFS-NA **no se tabulan** aquí pese a
  ser el eje de la tesis.
- **P6**: bloque de figuras encadenadas `F10` + `ev6_rendimiento_vs_k` +
  `f10_b4` + `f10_b5` + `f10_b9` (cinco figuras seguidas con `\clearpage`) y
  **cero tablas nuevas** salvo la 5.3. El subargumento del embebido (l.771-784:
  "0.234 vs 0.225 vs 0.247") es **P2** puro: tres números clave en prosa que
  refutan la hipótesis geométrica y merecen tabla.
- **P8**: captions de `f10_b5_beta_geometria` y `f10_b9_atomos_mds_error`
  remiten a "leer junto al error de embebido" sin dar el número en el propio pie.

### §5.5 Diagnóstico criterio-optimizador (l.796-839)
- **P2 (grave)**: la descomposición numérica clave del TFG está **solo en
  prosa**: Madelon 0.813/0.643/0.647 → pérdida 0.166, criterio 0.170; Churn
  0.9998/0.9991/0.987 → criterio 0.0007, optimizador 0.012. **Esto es LA tabla
  del capítulo** (dataset × {baseline, oráculo, QFS-NA, Δcriterio, Δoptimizador})
  y no existe; se delega todo a la Figura F09. Es el caso más claro de "figura
  cargando una conclusión que pide tabla".
- **P5**: "descarta la simetría de dos fallos iguales" se repite aquí (l.822) y
  en §5.6 (l.910-913) y en conclusiones (l.61-63).
- **P3**: "AUC binario no aplica a multiclase" se explica aquí por 3ª vez
  (ya en metodología l.573-579 y resultados l.835-837).

### §5.6 Consistencia, pruebas y discusión (l.841-916)
- **P1/P2**: §5.6 enumera la cadena de tests (FDR, efecto, permutación 20×,
  bootstrap 400, signos 2000, etiquetas 500) **en prosa** y la ilustra con
  `f10_b8_cadena_tests` (figura). Es justo lo que pediste para §2.5: esta es la
  tabla-resumen de tests que debería existir **y** estar referida desde §2.5 y
  §4.5. Hoy es una figura ("pocha") en vez de la tabla canónica.
- **P2**: consistencia Jaccard (1.00 filtros; RF 0.88 Madelon / 0.78 olive9;
  mRMR 0.88 churn) → otra vez números en prosa + figura `f10_b10`. Tabla.
- **P4**: "fase 3 / fase 4" (l.847-848).
- **Positivo**: §5.6 (l.892-902) declara honestamente la limitación de
  consistencia (no multi-semilla). Eso **sí** está bien escrito y debe
  conservarse; es el modelo de tono para el resto.

### Conclusiones (conclusiones.tex)
- **P5 (intenso)**: el capítulo **re-narra** Madelon y Churn con las **mismas
  cifras** ya dadas en §5.5 (0.647/0.813, 0.170; 0.987/0.9998, 0.0007/0.012,
  errores MDS 0.234/0.225/0.247). Conclusiones debe **sintetizar**, no repetir
  el detalle numérico verbatim. Recorta a la lectura, remite a las tablas.
- **P5**: "no actúa como simple baseline, sino como instrumento" (l.115) =
  reformulación de la tesis de intro l.53. Una vez basta.
- **Bien**: la sección de trabajo futuro es concreta y deriva de limitaciones
  reales (criterio→HUBO, readout, ablación one-hot, multi-semilla, hardware).
  No tocar salvo P4 si aparece.

### Apéndice (apendice.tex)
- **Redundancia con §4.5.5** (ver arriba): §A.1 "Condiciones de reproducción" y
  §A.2 "Coste computacional" repiten metodología §4.5.5 y §4.5.2. Unificar.
- **Punto fuerte / oportunidad**: la Tabla `ap-indice-trazabilidad` (dimensión →
  artefacto CSV → cobertura) es **exactamente el modelo de "cerrar el bucle"**
  que falta en el cuerpo. Aprovéchala: las tablas que faltan en resultados
  pueden derivarse de esos mismos CSV ya inventariados aquí.
- **P6/P1**: el apéndice es 9 figuras / 1 tabla. Varias (`a1` permutación, `a5`
  panorama deltas, `a8` solape) son de nuevo evidencia tabulable usada como
  figura. Coherente con el patrón global.
- **P1**: §4.5.4 menciona SHAP y matrices de confusión como evidencia; en el
  cuerpo SHAP sí aparece (F06), pero **las matrices de confusión no se muestran
  en ningún sitio** pese a citarse (metodología l.588, resultados l.411-414).
  Afirmación sin recibo: o se añaden (apéndice) o se deja de prometerlas.

---

## 4. Recomendaciones priorizadas

**Nivel A — estructural (cierra el 80 % de las quejas):**
1. **Crear las tablas que faltan** (derivables de los CSV del apéndice):
   T-regímenes (§5.1.4), T-perfil-selectores (§5.2.1), T-candidatos por
   dataset×modelo (§5.2.2), **T-atribución criterio/optimizador (§5.5)** ←
   prioridad máxima, T-cadena-tests (§5.6 ↔ §2.5/§4.5), T-consistencia (§5.6).
2. **Forward-references**: §2.5 y §4.5.3/4.4.2 → a sus tablas de resultados.
3. **Degradar/eliminar figuras "pochas"** cuya carga sea tabulable; conservar
   solo figuras que razonen algo que una tabla no puede (esto enlaza con tu
   contrato `rediseno_figuras_memoria_2026-06-16.md`: figura = instrumento).

**Nivel B — limpieza transversal:**
4. **Purga de "fase N"** (16 sitios) → traducir a lenguaje de contenido
   ("la auditoría exploratoria", "el modelado") o a referencias de sección.
5. **De-duplicar boilerplate**: letanía de garantías (3×), "no es un baseline"
   (2×), "simetría de fallos" (3×), "AUC no aplica" (3×).
6. **Definir en el punto de uso**: Spearman (+ meterlo en §2.5), una línea para
   M-W/K-W/KS/Wasserstein/PSI; recordar qué mide Jaccard al usarlo.
7. **Eliminar trivialidades** ("se cargan íntegros", "sin fallos", "sin nulos").

**Nivel C — coherencia fina:**
8. **§5.2.4 → mover tras §5.3** o despojarlo de cifras de QFS (P10).
9. **Cerrar §5.2.3 y §5.4 en las 4 coordenadas**, no solo rendimiento (P9).
10. **Captions autoexplicativos** (ejes, unidades, signo de Δ, valor clave en
    el pie) — empezar por `qfs-control`, `f10_b5`, `f10_b9`, `F08`.
11. **Fundir §4.5.5 en el apéndice**; añadir matrices de confusión al apéndice
    o dejar de prometerlas.
12. **Decidir figura O lista** en el recorrido de fases (§4.5).

**Coherencia de registro (tu "la redacción cambió a medida que avanzas"):** el
salto es real y medible — intro/marco son prosa expositiva limpia; resultados
es registro de log (fase N, recuentos, "sin fallos"). La purga P4 + sacar
cifras a tablas **homogeneíza el registro** automáticamente: el cuerpo pasa de
"narrar la ejecución" a "presentar evidencia".
