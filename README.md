# Desarrollo y evaluación de un método cuántico de selección de características

Repositorio final del Trabajo de Fin de Grado de Carlos Gómez Sáez.

Este TFG estudia si un método cuántico de selección de características puede ser
una alternativa razonable a técnicas clásicas de selección en problemas de
aprendizaje supervisado. La idea central es formular la selección como un
problema binario de relevancia y redundancia, expresarlo como una función QUBO y
resolverlo mediante una simulación inspirada en átomos neutros con bloqueo de
Rydberg.

El objetivo no es presentar el método cuántico como una mejora general, sino
evaluarlo con una referencia clásica sólida. Por eso el proyecto compara QFS
(`Quantum Feature Selection`) con un banco de selectores clásicos, mide
rendimiento predictivo, estabilidad, redundancia, coste y consistencia, y separa
dos preguntas que suelen mezclarse: si el criterio de selección es adecuado y si
el proceso de optimización encuentra buenas soluciones.

Repositorio:
<https://github.com/gosacarpersonal/TFG---Desarrollo-y-Evaluacion-de-un-Metodo-Cuantico-de-Seleccion-de-Caracteristicas>

## Qué Contiene

- `Desarrollo y evaluación de un método.pdf`: PDF final de la memoria.
- `Plantilla_Latex_GCD/tfgs/`: fuente LaTeX, bibliografía, figuras finales y
  PDF compilado dentro de la plantilla.
- `data/`: datasets originales, datos procesados y particiones
  `train/validation/test`.
- `notebooks/`: cuadernos usados durante las fases de análisis.
- `src/`: código principal de preparación, auditoría, selección, modelado y
  visualización.
- `results/`: tablas, figuras, predicciones, logs y reportes generados durante
  la evaluación.
- `QFS_based_on_NA/`: código base y artefactos asociados al enfoque QFS con
  átomos neutros.
- `large_files_parts/`: fragmentos de archivos demasiado grandes para GitHub.
- `scripts/reconstruct_split_files.py`: utilidad mínima para reconstruir esos
  archivos grandes.

## Estructura Del Trabajo

El TFG sigue una cadena experimental cerrada:

1. Preparación y auditoría de los datasets.
2. Construcción de particiones reproducibles de entrenamiento, validación y
   test.
3. Evaluación de selectores clásicos como referencia.
4. Entrenamiento y comparación de modelos supervisados sobre subconjuntos de
   variables.
5. Formulación y ejecución del método QFS.
6. Comparación final entre la referencia clásica, el óptimo QUBO y las
   soluciones cuánticas aproximadas.

Los resultados principales están explicados en la memoria. Los CSV, figuras y
artefactos del repositorio sirven como evidencia trazable de esas conclusiones.

## Entorno

Para inspeccionar o reproducir partes del proyecto se recomienda crear un
entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Algunas dependencias tienen requisitos externos:

- `gurobipy` requiere una instalación/licencia válida de Gurobi.
- `amazon-braket-sdk` requiere credenciales y configuración de AWS/Braket para
  ejecuciones remotas.

La memoria, las tablas ya generadas y las figuras finales pueden revisarse sin
volver a lanzar ejecuciones remotas.

## Memoria

La memoria LaTeX se encuentra en `Plantilla_Latex_GCD/tfgs/`. Para compilarla:

```powershell
cd Plantilla_Latex_GCD\tfgs
latexmk -pdf -interaction=nonstopmode -halt-on-error ejemplo-memoria.tex
```

El PDF compilado principal dentro de la plantilla es
`Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf`. En la raíz del repositorio se
incluye también una copia de entrega con nombre descriptivo.

## Archivos Grandes

GitHub no permite subir archivos individuales de más de 100 MB. Por eso algunos
CSV de predicciones se han dividido en fragmentos dentro de
`large_files_parts/`.

Para reconstruirlos en sus rutas originales:

```powershell
python scripts\reconstruct_split_files.py
```

El manifiesto `large_files_parts/manifest.json` guarda, para cada archivo
dividido, su ruta original, tamaño, SHA-256 y lista de fragmentos. El script
comprueba el tamaño y el hash al reconstruir.

## Nota De Lectura

Este repositorio está pensado como entrega del TFG, no como paquete Python
publicado. La forma más directa de entender el proyecto es leer primero la
memoria y después consultar `results/`, `data/`, `notebooks/` y `src/` cuando se
quiera comprobar la evidencia de una figura, tabla o conclusión concreta.
