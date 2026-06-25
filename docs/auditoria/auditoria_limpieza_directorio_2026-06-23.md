# Auditoria de limpieza del directorio - 2026-06-23

**Estado:** solo lectura. No se ha eliminado ni movido ningun archivo.

**Objetivo:** identificar residuos, dependencias vivas y candidatos a mover a `basura/` en una fase posterior, sin comprometer la reproducibilidad del TFG ni la memoria.

## 1. Foto actual del arbol

Comandos usados como evidencia:

- `git status --short`
- `git status --short --ignored`
- `git ls-files`
- busquedas `rg` sobre rutas clave
- inventario de tamanos por carpeta con PowerShell
- comparacion de `\includegraphics` frente a `Plantilla_Latex_GCD/tfgs/figs`
- duplicados por SHA256 para ficheros mayores de 1 MB, excluyendo `.git`

Tamanos actuales por raiz:

| Raiz | Tamano aprox. | Ficheros | Lectura |
|---|---:|---:|---|
| `data/` | 2522 MB | 1312 | Datos crudos, procesados, splits y `selected_features`; pesado pero vivo. |
| `.git/` | 1468 MB | 307 | Historia muy pesada por binarios grandes ya versionados. No se arregla moviendo archivos; requiere decision aparte. |
| `results/` | 832 MB | 1592 | Tablas, figuras, reports, logs y predicciones generadas. Mezcla de nucleo y regenerables. |
| `basura/` | 730 MB | 602 | Ya es archivo local ignorado por git. Contiene un zip grande y figuras/resultados descartados. |
| `.agents/` | 459 MB | 4340 | Skills/assets de apoyo, no nucleo cientifico del TFG. Esta versionado en gran parte. |
| `docs/` | 80 MB | 264 | Auditorias, papers, propuesta y decisiones. Incluye PDFs de referencia. |
| `notebooks/` | 24 MB | 9 | Notebooks fase 1-9. Vivo. |
| `Plantilla_Latex_GCD/` | 15 MB | 71 | Memoria y figuras finales. Vivo. |
| `QFS_based_on_NA/` | 6 MB | 37 | Solver/codigo QFS usado por fase 8 y figuras. Vivo. |
| `scripts/` | 2 MB | 54 | Reconstructores y verificadores. Vivo. |
| `src/` | 2 MB | 65 | Codigo fuente del pipeline. Vivo. |
| `promtps_raw/` | 0.16 MB | 9 | Prompts historicos. Sin peso; valor documental, no ejecucion. |

Git actual:

- 7659 ficheros versionados.
- Raices con mas ficheros versionados: `.agents/` 4329, `results/` 1584, `data/` 1312, `docs/` 264.
- Cambios pendientes previos a esta auditoria: memoria/PDF/README de la revision de tutores.
- Ignorados presentes: `basura/`, `results/predictions/`, `__pycache__/` y artefactos intermedios de LaTeX.

## 2. Dependencias vivas comprobadas

### No tocar

Estas rutas tienen referencias directas o por patron de ejecucion:

| Ruta | Evidencia | Veredicto |
|---|---|---|
| `data/01_raw/` | origen de carga en scripts/notebooks | No tocar. |
| `data/processed/` | entrada de fases posteriores | No tocar. |
| `data/splits/` | leido por fases 5, 6, 8, 9 | No tocar. |
| `data/selected_features/` | leido por `phase6_modeling/pipeline.py`, fase 8 y fase 10 | No tocar sin redisenar reproducibilidad. |
| `QFS_based_on_NA/` | importado por `scripts/rebuild_fase8_notebook.py`, verificadores y figuras | No tocar. |
| `results/tables/` | fuente de memoria, figuras y verificadores | No tocar salvo items concretos ya auditados. |
| `Plantilla_Latex_GCD/tfgs/tex/` | fuente de memoria | No tocar salvo edicion editorial. |
| Figuras incluidas por LaTeX | 32 referencias detectadas entre `ejemplo-memoria.tex`, `tfg.cls` y `tex/*.tex`; 0 faltantes en la compilacion real | No tocar las referenciadas. |
| `results/predictions/06_modeling/` | requerido por `verify_fase6_notebook.py` y usado por fase 9 | Regenerable, pero vivo para verificar sin recomputar. |
| `results/predictions/08_quantum/` | requerido por `verify_fase9_evaluacion.py` | Regenerable, pero vivo para verificar sin recomputar. |

### Trampa importante: duplicados que no son basura

`data/selected_features/**/X_val_selected.csv` duplica `X_validation_selected.csv` en muchos casos. Esta duplicacion ya estaba documentada y sigue siendo intencionada: el generador escribe ambos alias y verificadores/pipelines pueden esperarlos. No deduplicar sin cambiar codigo y tests.

Tambien hay duplicados por selector/k en `customer_churn` cuando varios metodos seleccionan las mismas columnas. Eso no implica residuo: son artefactos por contrato de fase.

## 3. Candidatos residuales clasificados

### Baja friccion, bajo riesgo

Estos pueden limpiarse en una fase posterior si se acepta mover a `basura/` o borrar regenerables:

| Candidato | Tamano aprox. | Motivo | Riesgo |
|---|---:|---|---|
| `__pycache__/` en `src/`, `scripts/`, `QFS_based_on_NA/`, `.agents/...` | pequeno | cache Python ignorada | Muy bajo. |
| Intermedios LaTeX `*.aux`, `*.bbl`, `*.blg`, `*.log`, `*.out`, `*.toc`, `*.lof`, `*.lot` | <1 MB | regenerables por `latexmk`; ignorados | Muy bajo. |
| `Plantilla_Latex_GCD/tfgs/pdflatex31323.fls` | despreciable | resto de compilacion puntual | Muy bajo. |
| PNG espejo no referenciado en `Plantilla_Latex_GCD/tfgs/figs/` | pocos MB | algunos PDF equivalentes si estan usados | Bajo, revisar uno a uno. |
| `promtps_raw/` | 0.16 MB | prompts historicos, no ejecucion | Bajo; conservar si aporta trazabilidad. |

Figuras de `tfgs/figs` sin referencia directa detectada:

- `ETSE.jpg`
- `F01_banco_regimenes.png` (PDF usado)
- `F04_perfil_selectores.png` (PDF usado)
- `F05_campo_validacion_selectores.pdf`
- `F09_atribucion_criterio_optimizador.png` (PDF usado)
- `escudo_logo_UV.jpg`
- `qfs_organismo_cuantico.png` (PDF usado)

Nota: antes de mover logos conviene verificar visualmente portada/contraportada; algunos logos pueden quedar como respaldo aunque no sean llamados por el flujo actual.

### Regenerables, pero con dependencia de verificacion

| Candidato | Tamano aprox. | Evidencia | Recomendacion |
|---|---:|---|---|
| `results/predictions/` | ~691 MB | ignorado por `.gitignore`; leido por verificadores fase 6/9 y por scripts de comparacion | No mover hasta cerrar memoria y verificaciones. Si se mueve, documentar que hay que regenerar fase 6/9 para verificar. |
| `results/logs/05_feature_selection/previous_tables_20260613_112241/` | 45 MB / 420 ficheros | snapshot de regresion usado como referencia opcional por verificacion de fase 5 | Archivar solo si no se van a reejecutar comparaciones contra la version previa. |
| `results/reports/01_raw_eda/` y `05_feature_selection/` | ~11 MB total | reports regenerados/auxiliares; no son fuente directa de la memoria actual | Conservar si se quiere trazabilidad; archivar si se busca entrega limpia. |

### Alto impacto / requiere decision explicita

| Candidato | Tamano aprox. | Motivo | Riesgo |
|---|---:|---|---|
| `.agents/` | 459 MB en disco, 4329 ficheros versionados | tooling de skills, no nucleo del TFG; contiene zips y carpetas duplicadas | Medio si se saca del arbol; alto si se pretende limpiar la historia git. |
| `.agents/*.zip` | ~212 MB | duplican skills descomprimidas | Bajo para ejecucion del TFG, pero afecta trazabilidad de herramientas auxiliares. |
| `data/selected_features/` | ~2.4 GB | regenerable, pero contrato vivo de fases 5-10 | Medio/alto; no mover sin decidir nueva politica de reproducibilidad. |
| `.git/` | 1.47 GB | historia pesada por binarios | Alto; reducirlo requiere `git filter-repo` o equivalente y reescritura de hashes. |

## 4. Hallazgos de duplicados por hash

Duplicados relevantes:

- `.agents/` contiene duplicados claros entre variantes de skills (`ds-visual-storyteller`, `visualizations-skill`, `viz-definitive`): notebooks, GIFs, PNGs y zips de ejemplo.
- `data/selected_features/customer_churn/**/X_val_selected.csv` y `X_validation_selected.csv` duplican por diseno. No tocar.
- `Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf` y `Memoria - Quantum Feature Selection.pdf` son identicos tras la sincronizacion. Es intencional: uno es salida de compilacion y otro nombre de entrega.
- `docs/papers/2203.13261v2.pdf` y `docs/papers/Feature Selection on Quantum Computers.pdf` son duplicados por hash; `docs/papers/Feature Selection.pdf` y `docs/papers/QFS_D2.pdf` tambien. Candidato a revisar bibliografia antes de mover.
- En `basura/` y `docs/auditoria/_archivo_limpieza_2026-06-16/` hay duplicados de figuras ya archivadas. Como ambas rutas son archivo historico, no urge.

## 5. Propuesta de fases futuras

### Fase 0: no destructiva

No mover nada. Solo conservar esta auditoria y usarla como lista de decision.

### Fase 1: limpieza local segura

Acciones candidatas:

- Mover o borrar caches `__pycache__/`.
- Mover intermedios LaTeX ignorados si se quiere arbol visualmente limpio.
- Dejar intactos `ejemplo-memoria.fdb_latexmk` y `ejemplo-memoria.fls` mientras esten versionados; si se decide, desversionarlos en una fase git separada.

Riesgo: muy bajo.

### Fase 2: archivo de regenerables

Acciones candidatas:

- Mover `results/predictions/` a `basura/results_predictions_YYYYMMDD/` tras cerrar verificaciones.
- Mover `previous_tables_20260613_112241/` a `basura/previous_tables_YYYYMMDD/`.
- Mover reports no citados si se decide que la memoria/PDF y tablas son la fuente entregable.

Riesgo: bajo/medio. Los verificadores que esperan predicciones fallaran hasta regenerar.

### Fase 3: higiene de entrega

Acciones candidatas:

- Revisar los 7 ficheros no referenciados de `tfgs/figs`.
- Revisar duplicados exactos de `docs/papers`.
- Decidir si `promtps_raw/` queda como trazabilidad o se archiva.

Riesgo: bajo si se verifica LaTeX despues.

### Fase 4: salud real del repositorio

Acciones candidatas:

- Sacar `.agents/` del repo o moverlo a `basura/agents_YYYYMMDD/` si ya no se necesita en la entrega.
- Si se quiere recuperar espacio en `.git/`, planificar reescritura de historia con confirmacion explicita.

Riesgo: medio/alto. No hacerlo sin commit limpio y backup.

## 6. Recomendacion actual

Para entregar el TFG sin sustos:

1. No tocar `data/`, `results/tables/`, `QFS_based_on_NA/`, `src/`, `scripts/`, `notebooks/` ni figuras referenciadas por LaTeX.
2. Mantener `results/predictions/` hasta que no haga falta ejecutar verificadores.
3. Posponer `.agents/` y `.git/`: son el mayor problema de peso, pero no afectan a la memoria y requieren decision de repositorio.
4. Si se quiere una limpieza visible y segura, empezar por caches, intermedios LaTeX y los pocos ficheros no referenciados en `tfgs/figs`.
5. Cualquier movimiento debe ir a `basura/` con subcarpeta fechada y registro, no a borrado directo.

## 7. Limpieza ejecutada

Tras la revision inicial, se movieron a `basura/limpieza_2026-06-23/` elementos clasificados como seguros o no entregables: caches, auxiliares de LaTeX, figuras no referenciadas, salidas regenerables, snapshots antiguos, prompts historicos, duplicados/documentos auxiliares, tooling local (`.agents`, `.codex`) y el archivo vacio `AGENTS.md`.

Revision posterior: dado que el TFG debe quedar cerrado y con todos sus resultados presentes, se restauraron `results/predictions`, `results/logs/05_feature_selection/previous_tables_20260613_112241`, las figuras fuente movidas desde `Plantilla_Latex_GCD/tfgs/figs`, `Elaboracion_de_un_documento_cientifico.ods.zip` y los PDFs `docs/papers/2203.13261v2.pdf` y `docs/papers/Feature Selection.pdf`.

Tambien se verifico por SHA256 que `docs/papers/2203.13261v2.pdf` duplica `docs/papers/Feature Selection on Quantum Computers.pdf` y que `docs/papers/Feature Selection.pdf` duplica `docs/papers/QFS_D2.pdf`; se restauraron igualmente para mantener los nombres historicos.

No se movieron los datos base, datos procesados, codigo principal, notebooks, tablas de resultados usadas por la memoria, fuentes LaTeX ni figuras referenciadas.

El detalle historico esta en `basura/limpieza_2026-06-23/MANIFEST.csv`; el estado corregido y las restauraciones quedan resumidos en `basura/limpieza_2026-06-23/REGISTRO.md`.
