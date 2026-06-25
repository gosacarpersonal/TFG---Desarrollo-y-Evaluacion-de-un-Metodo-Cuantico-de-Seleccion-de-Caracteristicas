# Prompt de arreglo — Fase 2

Trabaja sobre `scripts/rebuild_fase2_notebook.py` (genera `notebooks/fase2.ipynb`).
Respeta `docs/estilo_redaccion_tfg.md` y `docs/auditoria/estructura_notebooks.md`.
Regenera y valida con `scripts/verify_fase2_notebook.py`.

La estructura y las funciones inline son correctas; NO muevas funciones a `src`. Solo:

1. **[MEDIO] Celda de funciones de 222 líneas (sección 2.9).** Ya está fichada como
   pendiente en el worklog (`docs/tfg_prequantum_worklog.md:9`). Trocéala en funciones más
   pequeñas y legibles **dentro del cuaderno**, cada una con su propósito claro y, si
   procede, una frase Markdown que explique qué hace. El objetivo es legibilidad, no
   esconder la maquinaria: las funciones siguen visibles, solo mejor divididas.

NO toques `fase2_distribuciones_numericas` ni `fase2_outliers_iqr` (narrativas
correctas).

Criterio de aceptación: ninguna celda de funciones supera ~80 líneas; cada función
troceada es comprensible por sí sola; estructura por sección y por dataset intacta;
`verify_fase2_notebook.py` pasa.
