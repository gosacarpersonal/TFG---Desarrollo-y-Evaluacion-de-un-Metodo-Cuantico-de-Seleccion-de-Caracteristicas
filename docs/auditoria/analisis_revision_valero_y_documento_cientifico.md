# Analisis de la revision de Valero y del documento formal adjunto

Fecha: 2026-06-16.

Entrada analizada:

- `Elaboración_de_un_documento_científico.ods.zip`, que en realidad es un
  documento OpenDocument Spreadsheet (`.ods`) empaquetado.
- Comentarios de Valero sobre otro TFG revisado por el profesor.
- Memoria actual del TFG QFS en `Plantilla_Latex_GCD/tfgs/`.

El `.ods` queda extraido en:

- `docs/auditoria/_adjuntos_profesor/elaboracion_documento_cientifico_ods/`

## 1. Contenido util del documento del profesor

El adjunto contiene cinco hojas: `FIGURAS`, `ESTILO`, `ESTRUCTURA`,
`CONTENIDO` y `REFERENCIAS`.

### FIGURAS Y TABLAS

Criterios extraidos:

- No usar capturas de pantalla salvo que sean necesarias y de mucha calidad.
- En toda grafica: ejes con nombre, leyenda, texto legible, limpieza visual y
  elementos justificados.
- Al insertar figuras: no deformar el aspect ratio, evitar pixelado, usar pies
  descriptivos, definir cada parte de la figura y referenciarla/comentarla en el
  texto principal.
- En tablas: pocas cifras significativas, resaltar valores importantes,
  normalizar cuando facilite la comparacion y convertir tablas muy grandes en
  graficas de vistazo.

Adaptacion al TFG QFS:

- La arquitectura visual actual ya sigue buena parte de esto: figuras generadas
  como PNG de alta resolucion, no capturas, con narrativa F1--F10 y apendice.
- Riesgo pendiente: hay 20 figuras en `resultados.tex`. Aunque varias son
  defendibles, hay que comprobar que cada una responde una pregunta de defensa y
  no duplica una figura de apendice.
- Prioridad: revisar captions de cuerpo. Algunas ya son correctas, pero los
  pies pueden definir mejor los paneles y el caveat metodologico, sobre todo en
  F8--F10.
- Prioridad: tablas finales con 3--4 cifras significativas. Hay valores como
  0.9998 en texto; son utiles para diagnostico fino, pero deben usarse con
  criterio y no inundar tablas generales.

### ESTILO

Criterios extraidos:

- Esfuerzo por prioridad: resumen, conclusiones, introduccion, resultados y
  despues el resto.
- Evitar redundancias innecesarias, pero aceptar redundancia controlada entre
  resumen, cuerpo y conclusiones.
- Explicar con detalle lo que falte, mantener claridad, conexion entre ideas y
  nivel formal.
- Consistencia de idioma en texto, variables y ejes.
- Paginas numeradas, encabezado/pie, texto justificado, espacio correcto en
  titulos.
- Sin faltas de ortografia.
- Evitar acronimos; si se usan, definirlos la primera vez y volver a definirlos
  si reaparecen mucho despues.
- Numeros con puntuacion correcta y 3--4 cifras significativas.
- Evitar enlaces; si existen, que sean accesibles en PDF impreso.
- No hacer parrafos muy largos.
- Referencias con DOI cuando proceda; cada idea clave necesita referencia o
  justificacion detallada.
- Toda seccion/subseccion debe tener texto despues del titulo, especialmente
  entre titulo de capitulo y primera seccion.
- Variables de formulas consistentes y definidas cerca de la formula; distinguir
  escalares, vectores y matrices.

Adaptacion al TFG QFS:

- El TFG ya tiene objetivos en el capitulo 1 y el resumen prioriza ciencia de
  datos: seleccion de caracteristicas, modelos, contrastes, macro-F1,
  interpretabilidad y atribucion criterio--optimizador.
- Punto a reforzar: resumen/abstract/resum deben explicar QFS, QFS-NA, oraculo,
  MDS y macro-F1 de forma menos densa. El resumen actual es correcto, pero muy
  comprimido.
- Punto a reforzar: el abstract no puede depender de que el lector ya sepa que
  es QFS, Rydberg blockade, pairwise mutual information, readout o MDS.
- Punto a reforzar: detectar parrafos largos. Se localizaron parrafos largos en
  `estado_arte.tex`, `introduccion.tex`, `metodologia.tex` y `resultados.tex`.
- Punto a reforzar: bibliografia. `bibliografia.bib` no contiene campos `doi`;
  esto contradice la recomendacion formal del profesor.

### ESTRUCTURA

Criterios extraidos:

- Portada, indice, indice de figuras e indice de tablas.
- Resumen y agradecimientos.
- Introduccion con motivacion, objetivos y descripcion del documento.
- Nudo: problema, estado del arte, propuesta propia, modelos y datos.
- Desenlace: experimentos y resultados.
- Epilogo: conclusiones como resumen de lo conseguido.
- Descripcion exhaustiva de datos, modelos, objetivo matematico y optimizacion.
- Si el documento supera unas 40 paginas, incluir lista de figuras y tablas.
- Numeracion correcta, elementos relacionados cerca, sin huecos en blanco.

Adaptacion al TFG QFS:

- La estructura principal ya cumple: resumenes, indices de figuras/tablas,
  introduccion con objetivos, marco teorico, estado del arte, metodologia,
  resultados, conclusiones y anexos.
- La advertencia de Valero "mete los objetivos en el capitulo 1" ya esta
  resuelta en `introduccion.tex`.
- Punto a revisar: que no queden paginas raras o huecos por acumulacion de
  figuras. Esto requiere compilar y revisar el PDF final, no se puede inferir
  solo del `.tex`.
- Punto a revisar: el capitulo de resultados es largo y contiene muchas figuras;
  puede necesitar enviar algunas figuras mecanisticas a apendice si rompen el
  ritmo.

### CONTENIDO

Criterios extraidos:

- Revision bibliografica.
- Datos correctos y descritos de forma exhaustiva: calidad, dimensiones,
  cantidad, idealmente con tabla.
- Modelos correctos y justificados frente a alternativas.
- Objetivo matematico y forma de evaluarlo alineados con el objetivo conceptual.
- Experimentos correctos.
- Resultados soportan conclusiones.
- Tema novedoso, interesante e importante.
- Calidad de la idea justificada respecto al estado del arte y a las
  restricciones del problema.

Adaptacion al TFG QFS:

- Este es el punto fuerte actual del TFG: el trabajo ya esta narrado como
  ciencia de datos experimental, no como finanzas ni como plataforma.
- La revision de Valero sobre "dar mas peso a ciencia de datos" se traduce aqui
  en no dejar que el QFS o la fisica tapen el bloque de datos, seleccion,
  modelado, validacion, SHAP y comparacion estadistica.
- Ya existen ejemplos de datos y regimenes en resultados: Breast Cancer,
  Customer Churn, Madelon y Olive Oil. Aun asi, conviene asegurar que en
  metodologia hay un ejemplo concreto de bloque/fila/variable y no solo
  descripciones agregadas.
- Las metricas principales estan definidas o contextualizadas, pero hay que
  auditar si macro-F1, AUC adversarial, FDR, PSI/KS/Wasserstein, Jaccard, VIF,
  SHAP, QUBO, criterio y readout tienen definicion conceptual y, cuando toca,
  matematica.

### REFERENCIAS

El `.ods` solo lista tres enlaces generales sobre redaccion y evaluacion de
documentos cientificos. No son fuentes primarias metodologicas del TFG; sirven
como criterio formal, no como bibliografia tecnica para la memoria.

## 2. Comentarios de Valero: que aplicar y como

### "Darle mas peso a la ciencia de datos"

Aplicacion directa, alta prioridad.

En el TFG QFS ya se ha hecho en gran parte: el hilo actual es seleccion de
caracteristicas, auditoria de datos, particiones, modelado, SHAP y comparacion
estadistica. La mejora no es anadir mas experimentos, sino vigilar el lenguaje:

- En resumen y abstract, abrir desde el problema de ciencia de datos:
  seleccion de caracteristicas supervisada y evaluacion rigurosa.
- Introducir QFS como una formulacion candidata dentro de seleccion de
  caracteristicas, no como protagonista fisico aislado.
- Cuando aparezcan terminos cuanticos, definirlos por su papel experimental:
  `QUBO` = funcion de coste binaria; `oraculo` = optimo exacto clasico del
  criterio; `QFS-NA` = simulacion analogica neutral-atom; `MDS` = embebido
  geometrico.

### "No queda claro el objetivo"

En el TFG del companero parecia haber una plataforma. En este TFG no aplica como
plataforma; si se menciona repositorio, debe ser por reproducibilidad, no por
objetivo.

Aplicacion adaptada:

- Mantener el objetivo general ya existente: evaluar la viabilidad de QFS frente
  a una referencia clasica.
- Reforzar en resumen e introduccion que el resultado no es una aplicacion, sino
  un protocolo experimental reproducible y una atribucion de fallos.
- En anexos o reproducibilidad, indicar que el repositorio contiene codigo,
  notebooks, CSV y figuras. Si la entrega requiere GitHub, no sustituye a los
  anexos ni a los artefactos dentro del PDF.

### "Me hubiese gustado ver machine learning o redes neuronales"

Aplicacion parcial.

En nuestro TFG si hay aprendizaje automatico: regresion logistica, SVM lineal,
random forest y XGBoost, con SHAP e incertidumbre. No es necesario anadir redes
neuronales salvo que el tribunal lo exija; seria un experimento nuevo con coste
y riesgo narrativo.

Como blindaje textual:

- Explicar que XGBoost se anade como modelo no lineal fuerte y comparable con la
  referencia QFS.
- Justificar que redes neuronales no son el centro porque el objetivo es evaluar
  seleccion de caracteristicas y atribucion criterio--optimizador, no maximizar
  rendimiento predictivo con arquitectura profunda.

### "Alguna pagina acaba raro"

Aplicacion directa, pendiente de compilacion.

- Compilar el PDF final.
- Revisar saltos de pagina alrededor de figuras grandes y tablas.
- Evitar que una subseccion termine con solo titulo, una linea suelta o una
  figura sin comentario.

### Abstract: referencias, terminos concretos, conceptualidad

Aplicacion directa.

- LaTeX permite citas en resumen, pero conviene verificar normas de la plantilla
  y del tribunal. Si se aceptan, citar Guyon/Elisseeff para feature selection,
  Mucke/Orquin para QFS y Henriet/Ebadi para atomos neutros.
- Si no se quieren citas dentro del abstract, al menos definir conceptualmente:
  seleccion de caracteristicas, QFS, neutral atoms, Rydberg blockade, macro-F1,
  criterio de informacion mutua por pares, oraculo exacto y readout.
- Evitar que el abstract sea solo una sucesion de resultados numericos. Debe
  contener motivacion, problema, solucion y resultados.

### Capitulo 3: terminos no definidos, datos y metricas

Aplicacion adaptada.

En nuestro TFG el "Cap 3" es estado del arte, pero la critica vale para cualquier
capitulo tecnico:

- No introducir simbolos como $I_i$, $R_{ij}$, $\alpha$, $\beta$, QFS-NA,
  oraculo o MDS sin definicion local o referencia hacia donde se definieron.
- Incluir ejemplos concretos de datos/variables cuando se hable de bloques o
  regimenes: una fila conceptual, una variable real, un subconjunto de Madelon,
  una familia one-hot de Churn.
- Definir metricas conceptualmente y, para las centrales, matematicamente:
  macro-F1, informacion mutua, redundancia, QUBO, Jaccard, AUC adversarial,
  FDR, SHAP y delta pareado.

### Resultados/conclusiones: "no entiendo los bloques"

Aplicacion directa como defensa de claridad.

El TFG QFS usa fases, formulaciones, presupuestos `k`, configuraciones
`alpha/beta`, semillas y mediciones. Hay que evitar que el lector vea "muchas
operaciones" sin unidad experimental.

Checklist de claridad:

- Definir al principio de resultados que una formulacion operativa es un
  problema dataset-target-preprocesado.
- Definir que un subconjunto seleccionado se evalua con el mismo protocolo de
  modelado que el baseline.
- Explicar que "funciona bien" significa: macro-F1 equivalente/mejor con IC,
  p-valor corregido y umbral de efecto practico, no solo una media mayor.
- Cuando se mencione anexo, referenciar `Apéndice~...`,
  `Figura~\ref{...}` o `Tabla~\ref{...}`, no "ver carpeta" ni enlaces externos.

## 3. Diagnostico rapido de la memoria actual

Fortalezas observadas:

- Objetivos ya estan en el capitulo 1.
- El resumen y la introduccion ya parten de seleccion de caracteristicas y
  aprendizaje automatico, no de una aplicacion externa.
- La memoria tiene listas de figuras y tablas.
- Las figuras son PNG generados de alta resolucion, no capturas pixeladas.
- La conclusion resume objetivos, resultados y limitaciones con cautela.
- No se detectan enlaces web incrustados en los `.tex` ni en la bibliografia.

Riesgos observados:

- `scripts/verify_memoria_figuras.py`, exigido por `AGENTS.md`, no existe en el
  checkout actual. Hay verificadores por fase, pero no el verificador global de
  memoria.
- `bibliografia.bib` no contiene campos DOI.
- Hay parrafos largos que pueden dificultar lectura:
  `estado_arte.tex`, `introduccion.tex`, `metodologia.tex` y `resultados.tex`.
- El cuerpo de `resultados.tex` contiene 20 figuras. Debe comprobarse si todas
  son de cuerpo o si algunas deben bajar a apendice.
- El resumen/abstract/resum son correctos pero densos: mucha informacion tecnica
  en un solo bloque.
- En el texto aparecen muchos acronimos y simbolos tecnicos. Debe auditarse si
  todos se definen la primera vez y si reaparecen definidos tras muchas paginas.

## 4. Plan de aplicacion priorizado

### Prioridad 1: resumen, abstract y resum

- Reescribir para que sigan claramente:
  motivacion -> problema -> solucion experimental -> resultados -> conclusion.
- Definir QFS sin asumir conocimiento previo.
- Mantener las cifras principales, pero reducir densidad de siglas.
- Decidir si incluir citas en los resumenes segun criterio de plantilla.

### Prioridad 2: glosario local de siglas/simbolos

- Auditar primeras apariciones de QFS, QFS-NA, QUBO, MDS, SHAP, FDR, VIF, PSI,
  KS, AUC, macro-F1, $I_i$, $R_{ij}$, $\alpha$ y $\beta$.
- Asegurar definicion conceptual y, donde proceda, matematica.

### Prioridad 3: figuras y captions

- Revisar las 20 figuras del cuerpo con la regla: pregunta de defensa, fuente,
  comentario en texto y caveat.
- Mejorar captions de F8--F10 para definir oraculo, QFS-NA, alpha/beta y unidad
  de lectura.
- Confirmar que las figuras mecanisticas de fase 10 que no sean esenciales van
  al apendice.

### Prioridad 4: bibliografia

- Anadir DOI cuando exista, especialmente a referencias centrales:
  Guyon 2003, Peng 2005, Benjamini--Hochberg 1995, Pedregosa 2011, Mucke 2023,
  Henriet 2020, Breiman 2001, Efron 1979, Lundberg 2017, Kursa 2010,
  Chen--Guestrin 2016, Ebadi 2022.
- Mantener referencias no publicadas como `orquin2026` sin DOI si aun no existe.

### Prioridad 5: compilar y revisar forma final

- Compilar PDF.
- Revisar paginas con cortes raros, huecos blancos, figuras desplazadas y tablas
  que rompan la lectura.
- Verificar que cada anexo citado existe y cada figura referenciada esta en
  `Plantilla_Latex_GCD/tfgs/figs/`.

## 5. Decision importante

La recomendacion externa no pide cambiar la tesis del TFG. La adaptacion correcta
es reforzar que el trabajo es ciencia de datos experimental:

> datos auditados -> seleccion clasica -> modelado e incertidumbre -> SHAP ->
> QFS simulado -> oraculo exacto -> diagnostico criterio--optimizador.

No conviene convertirlo en una memoria de plataforma, ni anadir redes neuronales
por inercia, ni llenar el abstract de fisica. El punto fuerte defendible es que
la referencia clasica no es decorativa: permite explicar por que QFS falla de
formas distintas en `Madelon` y `Customer Churn`.
