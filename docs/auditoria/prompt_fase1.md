# Prompt de arreglo — Fase 1

Trabaja sobre `scripts/rebuild_fase1_notebook.py` (genera `notebooks/fase1.ipynb`).
Respeta `docs/estilo_redaccion_tfg.md` y la estructura canónica de
`docs/auditoria/estructura_notebooks.md` (la de fases 1-4 es la correcta). Tras editar,
regenera el notebook y pásalo por `scripts/verify_fase1_notebook.py`.

IMPORTANTE: las funciones analíticas visibles inline son la **estructura deseada**. NO
las muevas a `src` ni las escondas. Solo se ajusta lo siguiente:

1. **[BAJO] `COLUMNAS_PRESENTACION` (línea ~191).** Es capa de presentación (~100 entradas
   de renombrado), no función analítica. Minimízala: aplica el renombrado solo a las
   columnas que cada tabla concreta muestra, donde se muestra, en lugar de un dict global
   de 100 líneas al principio. (Esto NO es "sacar funciones a src": es reducir un mapa de
   presentación que no aporta análisis.)

2. **[MEDIO] Figuras que duplican tablas.** De 30 figuras, `01_08_asociacion` (×4) y
   `01_11_redundancia` (×4) son heatmaps que repiten tablas ya mostradas. Para cada una:
   elimínala si la tabla ya lo dice todo, o conviértela en algo que la tabla NO pueda
   mostrar (clustermap con dendrograma, o resaltar solo pares por encima de un umbral), y
   añade una frase de lectura por figura ("qué enseña la imagen que la tabla no").
   Recuerda la regla de la estructura: la visualización solo entra si facilita entender
   la tabla o aporta más narrativa que ella.

NO toques `01_06_univariante` ni `01_07_normalidad` (distribucionales correctas) ni la
estructura de funciones inline.

Criterio de aceptación: presentación de columnas local y mínima; cada figura restante
aporta algo que su tabla no, con su frase de lectura; estructura por sección y por
dataset intacta; `verify_fase1_notebook.py` pasa.
