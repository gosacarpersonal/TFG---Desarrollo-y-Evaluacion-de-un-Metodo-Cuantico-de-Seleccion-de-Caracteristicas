# Prompt de arreglo — Transversal (estructura de las fases pesadas 5-7)

Este no es un bug de un notebook concreto, sino un ajuste de estructura que afecta a las
fases 5, 6 y 7. Lee primero `docs/auditoria/estructura_notebooks.md` (estructura
canónica) — la de las fases 1-4 es la correcta.

## Diagnóstico corregido

NO hay asimetría de narrativa: las 7 fases narran por sección y por dataset (verificado:
fase5 §5.9, fase6 §6.6, fase7 §7.4). El único defecto transversal es el **paso 2** de la
estructura en las fases pesadas: el núcleo metodológico —que es la contribución del
TFG— vive en `src/` y el cuaderno solo lo invoca (`fs.*`, `p6.*`, `f7.*`), sin verse
construir. Precisamente porque 5 y 6 son las fases serias y con más carga, es donde la
transparencia importa más.

## Qué hacer (aplicar a 5, 6 y 7 con el mismo criterio)

- **Subir al cuaderno la CREACIÓN visible del núcleo metodológico:**
  - Fase 5: los selectores espejo de QFS (relevancia `I(x;y)`, redundancia `I(x;x)`,
    mRMR/RRFS).
  - Fase 6: el cálculo SHAP y el protocolo de contraste (bootstrap, permutaciones).
  - Fase 7: la regla de decisión del veredicto final (delta/IC/p-valor).
- **Dejar en `src/` solo el *plumbing*:** E/S, carga de splits, guardado de
  tablas/figuras, formateo de presentación, utilidades repetidas.
- **Aceptar que los cuadernos se alarguen.** La longitud no es el problema; esconder la
  maquinaria del aporte sí lo es. NO hacer los cuadernos más delgados.
- **No tocar** la narrativa por dataset ni las funciones inline de 1-4: son el modelo.

## Nota práctica sobre coste

Los arreglos de correctitud (variance en fase 5, SHAP en fase 6) obligan a re-ejecutar
pipelines pesados. Agrupa todos los cambios de cada fase en una sola re-ejecución
(toda fase 5 de una vez; toda fase 6 de una vez) en lugar de re-correr por cada cambio.

## Criterio de aceptación

- En 5-7, el núcleo metodológico (no el plumbing) se ve construir en el cuaderno.
- La narrativa por dataset y la estructura por sección se conservan intactas.
- Los `scripts/verify_fase*_notebook.py` siguen pasando para las 7 fases.
