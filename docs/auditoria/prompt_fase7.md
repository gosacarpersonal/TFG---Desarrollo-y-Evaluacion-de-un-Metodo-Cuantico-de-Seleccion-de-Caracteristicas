# Prompt de arreglo — Fase 7

Lógica en `src/fase7_evidencia.py`; notebook generado por
`scripts/rebuild_fase7_notebook.py` (`notebooks/fase7.ipynb`). Respeta
`docs/estilo_redaccion_tfg.md` y `docs/auditoria/estructura_notebooks.md`. Regenera y
valida con `scripts/verify_fase7_notebook.py`.

Fase 7 es la comparación final; su estructura y narrativa por dataset (§7.4) están bien.
Arregla lo menor:

1. **[VERIFICAR] Umbrales de decisión.** En `resumen_comparacion_final`
   (`fase7_evidencia.py:236-240`) se usa `UMBRAL_EFECTO_PRACTICO`. Comprueba que está
   definido, justificado y documentado en el texto (de dónde sale el valor, por qué ese
   y no otro). Si es un número mágico, justifícalo o cámbialo por algo defendible.

2. **[BAJO] Lectura por figura.** Las figuras `fase7_mini_resumen_*` ya tienen narrativa
   por dataset; revisa que cada una aporte algo que la tabla no, y retira o transforma las
   que solo la repitan.

3. **[BAJO — estructura, paso 2] Veredicto visible.** Considera mostrar en el cuaderno la
   regla de decisión final (delta/IC/p-valor) en vez de solo invocar `f7.*`, para que el
   lector vea cómo se concluye. Ver `estructura_notebooks.md`.

Criterio de aceptación: `UMBRAL_EFECTO_PRACTICO` justificado; cada figura aporta algo que
la tabla no; `verify_fase7_notebook.py` pasa.
