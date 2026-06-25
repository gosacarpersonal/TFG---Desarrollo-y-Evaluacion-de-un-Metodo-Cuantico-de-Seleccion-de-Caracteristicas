# Lectura de Resultados sin figuras — 2026-06-18

> Artefacto editorial derivado de `resultados.tex`. No sustituye a CSV, código,
> notebooks ni tablas. Su objetivo es probar la hipótesis: "si quitamos las
> figuras, ¿dónde se rompe de verdad la lectura?".

## 1. Criterio usado

Para cada tramo de `resultados.tex` se ha leído la afirmación principal como si
la figura no estuviera. Se clasifica así:

- **Necesita figura de cuerpo**: sin una visualización, la afirmación pierde
  legibilidad o fuerza argumental.
- **Puede vivir con tabla/texto**: la tabla o el párrafo ya prueban lo necesario.
- **Debe ir a apéndice**: es evidencia real, pero granular o diagnóstica.
- **Candidata a rediseño**: la pregunta es necesaria, pero la figura actual no
  tiene la limpieza visual suficiente.

## 2. Lectura por secciones

### 2.1. Construcción y auditoría de la base experimental

El texto de apertura necesita una figura porque la tesis del banco es espacial:
tamaño, dimensión, desbalance y señal no se leen bien como lista de cifras. Aquí
sí hace falta una figura de cuerpo.

**Afirmaciones que necesitan apoyo visual**

- El banco mezcla regímenes muy distintos.
- `Madelon` tiene presión dimensional extrema.
- `Customer Churn` tiene tamaño masivo y margen casi saturado.
- La macro-F1 queda justificada por desbalance/multiclase.

**Afirmaciones que pueden vivir con tabla/texto**

- No hay nulos, duplicados ni columnas constantes.
- Se excluyen identificadores y proxies.
- Las proporciones del target se conservan.
- El particionado no pierde clases.

**Decisión**

`F01_banco_regimenes.pdf` o una versión más limpia debe sobrevivir. La figura
debe ser la puerta de entrada al capítulo. No necesita competir con otra figura
de regímenes.

### 2.2. Señal supervisada y anticipación de Madelon

Esta parte también necesita visualización porque prepara el diagnóstico QFS:
`Madelon` casi no tiene señal univariante y eso no es un detalle técnico, sino
un antecedente causal de la conclusión.

**Afirmaciones que necesitan apoyo visual**

- `Madelon` es un caso límite para criterios basados en MI por pares.
- La significancia y la magnitud no dicen lo mismo.
- `Customer Churn` puede ser estadísticamente significativo por tamaño muestral
  sin ser difícil predictivamente.

**Decisión**

`F02_senal_fdr_efecto.pdf` debe sobrevivir o fusionarse parcialmente con F1. Si
se fusiona, hay que conservar explícitamente el contraste: "muchas variables con
FDR" frente a "magnitud útil".

### 2.3. Auditoría de confianza

El texto ya está bastante completo: tablas de postprocesado, particiones,
drift, leakage y validación adversarial prueban la limpieza experimental. La
figura ayuda, pero no parece imprescindible para el cuerpo si se quiere una
memoria más severa.

**Afirmaciones que pueden vivir con tabla/texto**

- AUC adversarial compatible con 0.5.
- No hay leakage duro tras excluir proxies.
- El preprocesado conserva rankings.
- El drift se interpreta como cautela, no como defecto.

**Decisión**

`F03_base_confiable.pdf` es frontera. Puede quedarse si el cuerpo quiere mostrar
la auditoría visualmente, pero en una versión más limpia puede bajar al apéndice
y dejar en cuerpo solo tabla + frase de veredicto.

### 2.4. Regímenes antes de QFS

El texto ya explica dataset por dataset los regímenes con variables y cifras. La
tabla `tab:regimenes` cumple bien la función de resumen. La figura
`f10_a_regimenes_dataset.png` no añade una capa argumental nueva respecto a F1,
F2, F3 y la tabla.

**Decisión**

`f10_a_regimenes_dataset.png` debe salir del cuerpo. Puede ir al apéndice como
lámina de régimen o desaparecer si las figuras F1/F2/F3 se rediseñan bien.

### 2.5. Caracterización de selectores clásicos

El bloque clásico sí necesita una figura, pero no varias. El lector debe ver el
espacio de selectores como espejo de QFS: relevancia, redundancia, estabilidad y
coste. La tabla de perfil aporta cifras, pero sin figura se pierde la relación
entre familias.

**Afirmaciones que necesitan apoyo visual**

- mRMR controla redundancia con coste moderado.
- Los wrappers pagan coste.
- La estabilidad no discrimina tanto como la redundancia.
- La selección no parece ruido frente a permutaciones.

**Afirmaciones que deben ir a apéndice**

- Mapa variable por variable de `Madelon`.
- Redundancia interna frente a cada `k`.
- Estabilidad detallada por selector/dataset.

**Decisión**

Debe sobrevivir una única figura de cuerpo para selectores: `F04` rediseñada.
`o1_organismo_seleccion.png`, `f5_coste_rendimiento.png` y
`f10_b10_consistencia.png` deben salir del cuerpo.

### 2.6. Modelado y veredicto estadístico

La figura de significancia/magnitud es necesaria porque materializa la regla de
decisión. Una tabla dice el resultado, pero la figura enseña la honestidad:
intervalos, cero, umbral práctico y casos inconclusos.

**Afirmaciones que necesitan apoyo visual**

- Solo `Madelon` mejora de forma relevante.
- `Customer Churn` puede tener diferencia estadística pero no práctica.
- `Olive Oil 9` no permite afirmar mejora aunque el punto parezca alto.

**Decisión**

`F07_significancia_magnitud.pdf` debe sobrevivir. Es de las pocas figuras que
realmente reducen ambigüedad.

### 2.7. Interpretabilidad SHAP

Sin figura, el texto puede afirmar qué variables sostienen el modelo, pero
pierde credibilidad visual porque SHAP por instancia es precisamente una
evidencia de distribución, no solo de ranking. Aun así, la figura actual no
parece integrada con el resto del sistema.

**Afirmaciones que necesitan apoyo visual**

- Las variables retenidas son las que el modelo usa.
- En `Madelon`, SHAP y el vector `I_i` no coinciden plenamente.
- La discrepancia anticipa el fallo de criterio de QFS.

**Decisión**

La función de SHAP merece figura, pero `F06_shap_beeswarm_instancias.pdf` es
candidata fuerte a rediseño. Alternativa: dejar en cuerpo una figura SHAP muy
selectiva centrada en `Madelon` y enviar el atlas SHAP completo al apéndice.

### 2.8. Mecanismo QFS

Aquí sí hace falta una figura de cuerpo. El texto describe una cadena física y
operativa: grafo informacional -> embebido -> densidad de Rydberg -> corte top-k.
Sin imagen, la explicación queda abstracta.

**Afirmaciones que necesitan apoyo visual**

- Cada átomo es una variable.
- La densidad de Rydberg funciona como ranking operativo.
- El corte top-k selecciona átomos de alta densidad.
- Churn y Madelon muestran mecanismos distintos.

**Decisión**

`qfs_organismo_cuantico.pdf` debe sobrevivir, pero rediseñado. Es más importante
que varias figuras técnicas posteriores. Debe verse como figura de mecanismo, no
como nube de puntos decorativa.

### 2.9. Mandos alpha/beta y control exacto

La explicación de alpha y beta necesita apoyo visual, pero solo uno. El texto
posterior ya desarrolla alpha, beta y MDS con bastante detalle. Mantener F8,
f10_b4 y f10_b5 en cuerpo produce repetición.

**Afirmaciones que necesitan apoyo visual**

- `alpha` controla una escalera discreta de cardinalidades del QUBO exacto.
- `beta` reordena densidades en el simulador QFS-NA.
- El panel alpha no es salida del simulador analógico.

**Decisión**

Debe sobrevivir `F08_mandos_qfs_alpha_beta.pdf` o una versión nueva que lo haga
mejor. `f10_b4_escalera_alpha.png` y `f10_b5_beta_geometria.png` deben ir al
apéndice.

### 2.10. Diagnóstico criterio--optimizador

Esta es la figura más necesaria de todo el capítulo. Sin ella, la memoria vuelve
a parecer "QFS pierde". Con ella, aparece la tesis: se puede separar criterio de
optimizador.

**Afirmaciones que necesitan apoyo visual**

- `Madelon` falla por criterio.
- `Customer Churn` cae por optimizador/readout.
- Los deterioros no son simétricos.
- El oráculo exacto convierte el resultado nulo en diagnóstico.

**Decisión**

`F09_atribucion_criterio_optimizador.pdf` debe sobrevivir sí o sí. Además debe
rediseñarse como figura de clímax: menos ruido, más jerarquía, y lectura clara de
cuadrantes.

### 2.11. Comparación final clásico--QFS

El cierre necesita figura: baseline, mejor clásico, QFS-NA y oráculo son cuatro
referencias que en tabla se leen de forma plana. La figura permite ver régimen,
intervalos y separación NA/oráculo.

**Afirmaciones que necesitan apoyo visual**

- QFS iguala en problemas de señal clara.
- Se deteriora en `Madelon` y `Customer Churn` por causas distintas.
- `Olive Oil 9` queda abierto.
- La separación QFS-NA/oráculo enlaza con F9.

**Decisión**

`F10_comparacion_final_clasico_qfs.pdf` debe sobrevivir, pero puede ganar mucho
si se rediseña como cierre más limpio.

### 2.12. Sensibilidad por k, alpha, beta, MDS y consistencia

Estas secciones son metodológicamente valiosas, pero no todas necesitan figura
de cuerpo. El texto ya cuenta la lectura y las tablas sostienen la cifra. Las
figuras funcionan mejor como atlas de evidencia.

**Debe ir al apéndice**

- `ev6_rendimiento_vs_k.png`;
- `f10_b4_escalera_alpha.png`;
- `f10_b5_beta_geometria.png`;
- `f10_b9_atomos_mds_error.png`;
- `f10_b10_consistencia.png`.

**Matiz importante**

`f10_b9_atomos_mds_error.png` prueba una hipótesis descartada: la geometría MDS
no explica Churn. Es evidencia importante, pero precisamente por ser descarte
diagnóstico debe estar en apéndice o en una lámina técnica referenciada, no
interrumpir el cierre principal.

## 3. Nuevo mapa mínimo de figuras necesarias

### Versión severa: 8 figuras de Resultados

| Slot | Pregunta | Figura actual candidata | Acción |
|---:|---|---|---|
| 1 | ¿Qué régimen tiene el banco? | `F01` + parte de `F02` | Rediseñar/fusionar con foco en régimen. |
| 2 | ¿Por qué Madelon anticipa fallo de criterio? | `F02` | Conservar si no se fusiona. |
| 3 | ¿Cómo se comportan los selectores clásicos? | `F04` | Rediseñar como única figura de selección. |
| 4 | ¿Qué diferencias son afirmables? | `F07` | Conservar. |
| 5 | ¿Qué variables usa realmente el modelo? | `F06` | Rediseñar, quizá centrado en Madelon + uno de señal clara. |
| 6 | ¿Cómo decide QFS físicamente? | `qfs_organismo_cuantico` | Rediseñar. |
| 7 | ¿Falla el criterio o el optimizador? | `F09` | Rediseñar como figura central. |
| 8 | ¿Cómo queda QFS frente al clásico? | `F10` | Rediseñar como cierre. |

En esta versión, `F03` baja al apéndice y el blindaje de datos queda cubierto por
tablas + texto.

### Versión equilibrada: 9 figuras de Resultados

La misma versión anterior, pero conservando `F03_base_confiable.pdf` como figura
de auditoría explícita. Esta es la opción más defendible si se quiere que el
tribunal vea la trazabilidad experimental sin ir al apéndice.

## 4. Figuras actuales que no deberían estar en cuerpo

| Figura | Nuevo destino |
|---|---|
| `f10_a_regimenes_dataset.png` | Apéndice o eliminar tras fusionar con F1/F2/F3. |
| `o1_organismo_seleccion.png` | Apéndice, familia "Selección clásica / Madelon". |
| `f5_coste_rendimiento.png` | Apéndice, familia "Selección clásica / k y redundancia". |
| `ev6_rendimiento_vs_k.png` | Apéndice, familia "Sensibilidad por k". |
| `f10_b4_escalera_alpha.png` | Apéndice, familia "QFS interno / alpha". |
| `f10_b5_beta_geometria.png` | Apéndice, familia "QFS interno / beta". |
| `f10_b9_atomos_mds_error.png` | Apéndice, familia "QFS interno / MDS y geometría". |
| `f10_b10_consistencia.png` | Apéndice, familia "Consistencia y estabilidad". |

## 5. Qué rediseñar primero

Orden recomendado:

1. `F09`: si esta figura no funciona, la tesis QFS no funciona visualmente.
2. `F10`: cierre final, debe quedar limpio y memorable.
3. `qfs_organismo_cuantico`: mecanismo; debe verse profesional y no como output.
4. `F04`: bloque clásico; debe explicar el espejo clásico de QFS.
5. `F01/F02`: apertura del banco y anticipo de Madelon.
6. `F06`: interpretabilidad, solo si se puede integrar visualmente.

## 6. Conclusión de la lectura a secas

La memoria no necesita quedarse sin figuras. Necesita dejar de usar figuras como
prueba de que se ha trabajado mucho.

El texto, leído sin imágenes, revela que las figuras verdaderamente necesarias
son las que hacen una de estas cuatro cosas:

1. muestran régimen;
2. muestran incertidumbre;
3. muestran mecanismo;
4. muestran atribución causal.

Todo lo demás puede y debe vivir en tablas, apéndice o atlas de evidencia.
