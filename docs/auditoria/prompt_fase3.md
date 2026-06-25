# Prompt de arreglo — Fase 3

Trabaja sobre `scripts/rebuild_fase3_notebook.py` (genera `notebooks/fase3.ipynb`).
Respeta `docs/estilo_redaccion_tfg.md` y `docs/auditoria/estructura_notebooks.md`.
Regenera y valida con `scripts/verify_fase3_notebook.py`.

La estructura, las funciones inline y las constantes (parámetros ya justificados en
Markdown, según `docs/tfg_prequantum_worklog.md:10`) son correctas; NO las muevas a `src`
ni las recortes. Solo:

1. **[MEDIO] Heatmaps que duplican tablas:** `fase3_asociacion` (×4) y `fase3_redundancia`
   (×4) repiten las tablas de correlación/redundancia. Para cada una: elimínala si la
   tabla ya lo cubre, o transfórmala en algo que la tabla no pueda mostrar, y añade una
   frase de lectura por figura. Aplica la regla: la visualización solo entra si aporta más
   que la tabla.

NO toques `fase3_distribucion_conservacion` (distribucional, correcta).

Criterio de aceptación: cada heatmap restante aporta algo que su tabla no, con su frase de
lectura; estructura intacta; `verify_fase3_notebook.py` pasa.
