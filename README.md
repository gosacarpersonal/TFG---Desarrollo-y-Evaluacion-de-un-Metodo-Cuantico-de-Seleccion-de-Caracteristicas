# TFG - Desarrollo y evaluacion de un metodo cuantico de seleccion de caracteristicas

Repositorio de entrega del Trabajo Fin de Grado:

**Desarrollo y evaluacion de un metodo cuantico de seleccion de caracteristicas**.

Repositorio final: <https://github.com/gosacarpersonal/TFG---Desarrollo-y-Evaluacion-de-un-Metodo-Cuantico-de-Seleccion-de-Caracteristicas>

## Contenido

- `Memoria - Quantum Feature Selection.pdf`: PDF final de la memoria.
- `Plantilla_Latex_GCD/tfgs/`: fuente LaTeX de la memoria, bibliografia, figuras finales y PDF compilado.
- `data/`: datos crudos, procesados, particiones y subconjuntos de variables usados en los experimentos.
- `notebooks/`: cuadernos de las fases de analisis.
- `src/`: utilidades y pipelines de preparacion, seleccion, modelado y visualizacion.
- `scripts/`: scripts de reconstruccion, generacion de figuras y verificacion.
- `results/`: tablas, figuras, predicciones y reportes generados por el pipeline.
- `docs/`: notas metodologicas, decisiones y documentacion auxiliar.

## Entorno

Se recomienda usar un entorno virtual de Python:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`gurobipy` requiere una instalacion/licencia valida de Gurobi. `amazon-braket-sdk`
requiere configurar AWS/Braket para ejecuciones remotas. Las verificaciones
documentales, la compilacion de la memoria y la inspeccion de resultados
versionados no dependen de enviar trabajos remotos.

## Memoria

La memoria se compila desde:

```powershell
cd Plantilla_Latex_GCD\tfgs
latexmk -pdf -interaction=nonstopmode -halt-on-error ejemplo-memoria.tex
```

El PDF generado es `Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf`. Para mantener
la copia de entrega en la raiz:

```powershell
Copy-Item "Plantilla_Latex_GCD\tfgs\ejemplo-memoria.pdf" "Memoria - Quantum Feature Selection.pdf" -Force
Copy-Item "Plantilla_Latex_GCD\tfgs\ejemplo-memoria.pdf" "Plantilla_Latex_GCD\tfgs\Memoria - Quantum Feature Selection.pdf" -Force
```

## Verificaciones

Comprobar que todas las figuras referenciadas por la memoria existen:

```powershell
$env:PYTHONUTF8='1'
python scripts\verify_memoria_figuras.py
```

Verificaciones utiles por fase:

```powershell
python scripts\verify_fase1_notebook.py
python scripts\verify_fase2_notebook.py
python scripts\verify_fase3_notebook.py
python scripts\verify_fase4_notebook.py
python scripts\verify_fase5_notebook.py
python scripts\verify_fase6_notebook.py
python scripts\verify_fase7_notebook.py
python scripts\verify_fase8_ejecucion.py
python scripts\verify_fase8_solver.py
python scripts\verify_fase9_evaluacion.py
```

## Archivos grandes

GitHub no permite subir archivos individuales de mas de 100 MB. Si la entrega
contiene una carpeta `large_files_parts/`, esos archivos se han dividido en
fragmentos para poder versionarlos sin perder trazabilidad.

Para reconstruirlos en sus rutas originales:

```powershell
python scripts\reconstruct_split_files.py
```

El manifiesto `large_files_parts/manifest.json` documenta la ruta original,
tamano, hash SHA-256 y lista de fragmentos de cada archivo dividido.

## Reproducibilidad

Los resultados de la memoria proceden de los artefactos versionados en `results/`
y de los scripts/cuadernos del repositorio. Para una reproduccion completa, las
fases deben ejecutarse en orden y conservar la separacion `train/validation/test`
ya materializada en `data/splits/`.
