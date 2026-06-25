# Prompt — Construir las figuras de la memoria con verificación VISUAL

Construye las figuras del TFG conforme a la especificación elevada y la skill de
visualización, **verificándolas visualmente** (abriendo y mirando cada imagen renderizada,
no solo comprobando que el script corre), corrigiendo composición/espacios donde haga falta
y re-renderizando hasta que cada figura pase.

## Fuentes de verdad (leer antes de tocar nada)

1. `docs/auditoria/especificacion_figuras_memoria.md` — diseño figura a figura (10
   compuestas de cuerpo F1-F10 con **F4 a 4 paneles**, + 9 de apéndice A1-A9). Es el
   contrato: familia, composición, roles de panel, título/subtítulo, paleta, caveats y
   tablas de origen de cada figura.
2. `.agents/viz-definitive/skills/viz-definitive/SKILL.md` y sus `references/`
   (especialmente `combined-figure-router.md`, `three-panel-figures.md`,
   `composition-patterns.md`, `layout-hierarchy.md`, `legend-design.md`,
   `editorial-benchmark-warmth-system.md`). Aplica las 5 puertas; cuerpo = Tier 2.
3. `src/viz_core/` (paleta y helpers `editorial_warmth.py`: `set_editorial_rcparams`,
   `apply_editorial_axes`, `add_editorial_text`, `annotate_focus`,
   `save_editorial_figure`). Úsalos; NO inventes otra paleta.

## Reglas duras (no negociables)

- **No alterar datos** al dibujar: nada de imputar, escalar, winsorizar, recortar
  outliers, rebalancear, agregar ni muestrear para cálculo. Muestreo solo visual y
  etiquetado. Toda cifra sale de una tabla real bajo `results/`.
- Paleta editorial-warmth EXACTA de `src/viz_core/config.py`; identidad de color estable
  (mismo color por dataset y por familia de método en TODAS las figuras).
- Patrón de cabecera: **título = hallazgo**, subtítulo = métrica/n/umbral; contexto en
  gris, color solo en la evidencia; ≤3 anotaciones por figura.
- Barras de magnitud con base 0; nada de doble eje, pie/donut ni 3D; escalas log
  etiquetadas; IC y n visibles cuando aplique.
- No tocar `*_OG.py` ni recomputar fases 1-9: estas figuras LEEN artefactos de `results/`.

## Dónde va el código y las salidas

- Generador: `scripts/build_memoria_figuras.py` (funciones por figura, una por F1-F10 y
  A1-A9), invocable y reproducible. Estructura legible (cada figura, su función visible).
- Salidas: PNG (300 dpi) + PDF vectorial en `results/figures/10_memoria/`. Además, copia
  cada figura de la memoria a `Plantilla_Latex_GCD/tfgs/figs/` con el nombre EXACTO que la
  memoria referenciará (define nombres `f1_banco.png` … `f10_qfs_vs_clasico.png`,
  `a1_...`).

## Bucle de verificación VISUAL (lo esencial de este encargo)

Para CADA figura, repite este ciclo hasta que pase:

1. **Renderiza** la figura a PNG en `results/figures/10_memoria/`.
2. **ÁBRELA y MÍRALA de verdad** (inspección visual de la imagen, no `assert exists`).
   Evalúa contra esta lista (todo debe cumplirse):
   - **Composición y espacios:** sin solapes entre paneles, ejes, títulos o leyendas; sin
     etiquetas cortadas; márgenes generosos; en multipanel, rejilla equilibrada (usa
     `constrained_layout`/`gridspec`, ajusta `figsize`, `wspace/hspace`); F4 en 2×2 con una
     sola leyenda de familia (no una por panel).
   - **Legibilidad a tamaño PDF:** texto legible al tamaño de impresión, no solo en
     pantalla grande; ticks no amontonados; etiquetas largas rotadas o en barras H.
   - **Jerarquía narrativa:** título=hallazgo presente; subtítulo con métrica/n/umbral;
     protagonista resaltado y contexto en gris; ≤3 anotaciones.
   - **Corrección científica:** base 0 donde toca; escala log etiquetada; IC visibles;
     paleta estable y colorblind-safe; el color codifica algo (no decorativo).
   - **Coincidencia con la spec:** familia, paneles y roles son los de
     `especificacion_figuras_memoria.md`.
3. **Si algo falla, corrige** —prioriza el **juego de espacios y composición** (figsize,
   layout, wspace/hspace, tamaño de fuente, posición de leyenda, rotación de etiquetas,
   anchura relativa de paneles)— y **vuelve al paso 1**. No te quedes en el primer render.
4. Cuando pase, **guarda también el PDF vectorial** y registra la figura como aceptada.

Un script no puede juzgar composición: el chequeo de espacios/legibilidad lo haces TÚ
mirando la imagen. Itera al menos hasta que no haya solapes ni recortes y la jerarquía sea
clara.

## Verificador técnico (complementa, no sustituye, la inspección visual)

`scripts/verify_memoria_figuras.py`: comprueba que (1) existen las 19 figuras (PNG+PDF) en
`results/figures/10_memoria/` y sus copias en `figs/` con el nombre correcto; (2) DPI ≥ 300;
(3) cada figura procede de su tabla declarada (sin rutas inventadas). Debe pasar al final.

## Integración en la memoria (tras aceptar las figuras)

1. En `Plantilla_Latex_GCD/tfgs/tex/resultados.tex`, sustituye las figuras antiguas por las
   compuestas según el mapa "Sustituye" de la especificación (F1↔Q1/Q2, F3↔Q5/Q6/Q4,
   F4↔Q8-Q12, F7↔Q16/Q17, F8↔Q19/Q20, etc.), con el `\caption` = subtítulo de la spec y
   `\label` coherente; coloca F1-F7 en §5.1-5.2 y F8-F10 en §5.3. Apéndice A1-A9 →
   `apendice.tex`.
2. Recompila: `cd Plantilla_Latex_GCD/tfgs && conda run -n qfs_env tectonic ejemplo-memoria.tex`.
   Debe terminar sin errores y sin referencias/figuras indefinidas. **Abre el PDF y
   verifica visualmente** que cada figura se ve bien embebida (tamaño, nitidez, no se sale
   de márgenes).

## Entrega / reporte

Devuelve una **tabla de auditoría visual**: por figura → nº de iteraciones, qué se corrigió
(sobre todo espacios/composición), y captura final aceptada. Más: diff de
`build_memoria_figuras.py`, salida de `verify_memoria_figuras.py`, y confirmación de que la
memoria compila limpia con las figuras nuevas.

## Orden sugerido (huecos de mayor valor primero)

F9 (criterio-vs-optimizador) y F4 (perfil 2×2) primero por ser las de composición más
exigente; luego F2, F3, F5, F6, F7, F8, F10, F1; después apéndice. Reusa plotters de
`src/viz_core`/fases donde la spec lo indique (F3 adversarial, F7-A, F8-B β-map, A1, A5) y
copia/re-tematiza F6 (beeswarm ya generado).
