# Prompt de arreglo — QFS_MAIN (parte cuántica)

Notebook: `QFS_based_on_NA/QFS_MAIN.ipynb`. Es la parte cuántica (QFS sobre Neutral
Atoms). Hoy es un cuaderno de investigación crudo, muy desigual frente a las fases 1-7
generadas. Respeta `docs/estilo_redaccion_tfg.md`.

Arregla estos fallos verificados:

1. **[MEDIO] Doble import de matplotlib.** En la celda 1 conviven
   `import matplotlib.pyplot as plt` e `import matplotlib.pylab as plt`; el segundo pisa
   al primero. Elimina `matplotlib.pylab` y deja solo `matplotlib.pyplot`.

2. **[MEDIO — defensibilidad] Datasets desconectados del pipeline clásico.** QFS_MAIN usa
   Telco Churn, Adult y Bank Marketing, mientras las fases 1-7 usan breast_cancer,
   customer_churn, madelon y olive_oil. Decide y documenta: o alineas los datasets con el
   pipeline clásico (idealmente reutilizando los splits de `data/splits`), o justificas
   explícitamente por qué la parte cuántica usa otros. Sin esa justificación, la memoria
   tiene un salto sin puente entre la parte clásica y la cuántica.

3. **[BAJO] Reproducibilidad de un tirón.** Hay mucho código comentado (celdas 5, 16, 22,
   25) y el `label` se cambia a mano (CHURN→ADULT en la celda 31, que referencia
   resultados quizá no generados en la misma corrida). Reestructura para que el cuaderno
   corra de principio a fin sin edición manual: parametriza el dataset una sola vez al
   inicio y elimina o encapsula el código muerto.

4. **[MEDIO] Nivel de acabado.** Eleva el cuaderno al estándar narrativo de las fases
   1-7: intro de sección → cálculo → lectura con cifras, en castellano, siguiendo la
   guía de estilo.

Criterio de aceptación: un único import de matplotlib; datasets alineados o justificados;
el notebook corre de extremo a extremo sin tocar `label` a mano; narrativa al nivel de
las fases generadas.
