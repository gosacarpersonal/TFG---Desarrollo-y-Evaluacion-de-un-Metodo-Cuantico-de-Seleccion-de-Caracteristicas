# Investigación: plotnine para las visualizaciones de la memoria

Fecha: 2026-06-15.

## Qué es

`plotnine` es una implementación en Python de la gramática de gráficos,
inspirada en `ggplot2`. La idea central es construir figuras declarando
capas: datos, mapeos estéticos, geometrías, escalas, facetas, etiquetas y
tema. La documentación oficial lo presenta como una vía para pasar de
gráficos ad hoc a figuras publicables usando esa gramática.

Fuentes primarias consultadas:

- Documentación oficial: https://plotnine.org/
- Instalación oficial: https://plotnine.org/guide/install.html
- PyPI: https://pypi.org/project/plotnine/
- Repositorio: https://github.com/has2k1/plotnine

Estado actual consultado: `plotnine 0.15.7`, publicado en PyPI el
2026-06-13, requiere Python `>=3.10` y se instala como `pip install
plotnine`.

## Encaje con este TFG

La memoria tiene dos familias de figuras distintas:

1. **Figuras declarativas de evidencia**: una tabla larga se convierte en
   puntos, barras, líneas, intervalos, facetas o heatmaps. Aquí `plotnine`
   encaja muy bien porque el código queda cerca de la pregunta científica:
   `aes(x=..., y=..., color=...) + geom_* + facet_*`.
2. **Figuras editoriales/coreografiadas**: flechas, cajas de proceso,
   anotaciones colocadas a mano, regiones semánticas y composición muy
   dirigida. Aquí `plotnine` puede ayudar parcialmente, pero no conviene
   forzarlo; `matplotlib` o `Pillow` dan más control.

## Figuras candidatas a plotnine

Alta prioridad:

- **F2 señal FDR/efecto**: dot plots y anotación de Madelon. Gramática
  natural: puntos por dataset, escala común, color de protagonista.
- **F3 base confiable**: tres paneles/facetas con AUC adversarial, drift y
  conservación. Muy apta para capas con bandas de referencia.
- **F7 significancia/magnitud**: dumbbell/intervalos con línea de cero y
  umbral práctico.
- **F10 QFS vs clásico**: puntos por configuración, IC y facetas por
  dataset; ideal para una tabla larga `dataset/configuration/F1/CI`.
- **EV6 rendimiento vs k**: líneas por método y facetas por dataset.
- **A1/A5/A8**: heatmaps y matrices de apoyo.

Prioridad media:

- **F4 perfil selectores**: viable si se acepta una composición por
  facetas/paneles; si se quiere control editorial fino, mantener
  Matplotlib.
- **F5 redundancia frente a k**: viable como small multiples.
- **F8 alpha/beta**: viable para el panel de alpha y para heatmap beta,
  aunque la composición final puede seguir siendo Matplotlib.
- **F9 atribución QFS**: viable con `geom_rect`, `geom_point` y
  anotaciones, pero la figura actual ya funciona como clímax; migrarla solo
  si queremos homogeneizar estilo, no por necesidad.

No prioritarias:

- **EV4 recorrido del TFG**: mejor con `Pillow` o Matplotlib manual. Es una
  figura de proceso, no una visualización tabular pura.
- **O1 organismo de selección**: puede hacerse como heatmap en plotnine,
  pero el control de anotaciones y densidad actual es delicado.
- **F6 SHAP beeswarm**: plotnine no aporta mucho si ya necesitamos lógica
  propia de empaquetado/jitter y color por valor.

## Ventajas

- Código más declarativo y legible para figuras basadas en dataframes.
- Facetas sin bucles manuales: útil para las figuras por dataset.
- Escalas, leyendas y temas centralizables.
- Menos riesgo de inconsistencias entre figuras si se define un tema común
  `theme_tfg()`.
- Buena alineación conceptual con la memoria: cada figura responde una
  pregunta mapeando variables a evidencia visual.

## Costes y riesgos

- No elimina la dependencia de Matplotlib; `plotnine` se apoya en ese
  ecosistema. No resuelve por sí solo el problema del entorno actual sin
  `matplotlib`.
- Añade otra abstracción. Para figuras ya correctas y muy personalizadas,
  migrar puede consumir tiempo sin mejorar el PDF.
- Las composiciones multipanel muy editoriales pueden requerir ajustar
  manualmente tamaños, márgenes o combinar salidas.
- Conviene fijar versión o al menos registrar `plotnine>=0.15.7` si se
  adopta, para evitar cambios visuales entre releases.

## Recomendación

Adoptar `plotnine` de forma selectiva, no reescribir todo.

Ruta sensata:

1. Crear un helper `src/viz_core/plotnine_theme.py` con paleta, tamaños,
   fondo editorial y función `save_plotnine`.
2. Migrar primero una figura de bajo riesgo y alto valor declarativo:
   **EV6** o **F10**.
3. Si el resultado mejora legibilidad y reduce código, migrar después
   **F2**, **F3** y **F7**.
4. Mantener **EV4**, **O1**, **F6** y posiblemente **F9** en sus
   generadores actuales salvo que haya una razón visual fuerte.

Mi criterio: `plotnine` debe entrar donde convierta una tabla en argumento
visual con menos ruido de implementación. No debe entrar por estética de
librería ni para rehacer figuras que ya están narrativamente cerradas.

## Prototipo ejecutado

Se creó `scripts/build_f10_plotnine.py` como prueba separada del generador
principal. El script lee exactamente las mismas fuentes que F10:

- `results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv`
- `results/tables/07_final_comparison/fase7_handoff_qfs.csv`

La prueba se ejecutó en un entorno temporal fuera del repositorio con
`plotnine==0.15.7` y generó:

- `results/figures/10_memoria/prototype_f10_plotnine.png`
- `results/figures/10_memoria/prototype_f10_plotnine.pdf`

Resultado: el prototipo confirma que `plotnine` encaja bien para F10. El
código queda más declarativo que el Matplotlib actual: una tabla larga,
`geom_point`, `geom_errorbarh`, escalas manuales y tema. Sin embargo, la figura
actual de producción sigue siendo más editorial y más integrada con el resto de
la memoria. Por tanto, **no se sustituye F10 todavía**. La prueba queda como
base para una migración gradual si se decide homogeneizar las figuras
declarativas.

Detalle técnico: el primer intento usó una escala discreta con posiciones
numéricas desplazadas y falló; la versión correcta usa `scale_y_continuous`
con etiquetas de dataset y `coord_cartesian` para no descartar intervalos al
recortar el eje x.

El prototipo ya usa un helper común:

- `src/viz_core/plotnine_theme.py::theme_tfg`
- `src/viz_core/plotnine_theme.py::save_plotnine`

Esto evita que cada figura `plotnine` replique tema, DPI, tamaño y guardado.
También deja clara la frontera: `plotnine` entra como backend opcional para
figuras declarativas, no como sustituto global de todo `viz_core`.

## Decisión actual

Como ya existe un script real de prototipo que lo usa, se añade:

```text
plotnine>=0.15.7
```

No se añade `plotnine[extra]` por ahora. Si queremos etiquetas repelidas
automáticamente en figuras con muchas anotaciones, evaluar el extra oficial:

```text
plotnine[extra]>=0.15.7
```
