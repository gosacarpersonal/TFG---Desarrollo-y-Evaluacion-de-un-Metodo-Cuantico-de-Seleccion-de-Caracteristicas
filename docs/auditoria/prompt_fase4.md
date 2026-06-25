# Prompt de arreglo — Fase 4

Trabaja sobre `scripts/rebuild_fase4_notebook.py` (genera `notebooks/fase4.ipynb`).
Respeta `docs/estilo_redaccion_tfg.md`. Regenera y valida con
`scripts/verify_fase4_notebook.py`.

Fase 4 está mayormente bien (drift KS/Wasserstein/PSI y PCA son análisis real). Arregla
solo lo menor:

1. **Infraestructura inline** (6 constantes). Recórtala a lo imprescindible visible.

2. **chi² de proporciones de clase entre splits (línea ~860).** Si los splits son
   estratificados, el contraste es casi circular. El texto ya lo matiza (línea ~803);
   refuerza esa nota dejando explícito que el chi² aquí es una comprobación de coherencia
   del estratificado, no una prueba de hipótesis informativa, para que un tribunal no lo
   malinterprete.

3. Añade una frase de lectura por figura en `fase4_drift` y `fase4_pca` si no la tienen.

Criterio de aceptación: nota explícita sobre el chi²; figuras con lectura;
`verify_fase4_notebook.py` pasa.
