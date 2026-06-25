# Auditoría de calidad visual — Fase 1

Fecha: 2026-06-04.

## Alcance

Revisión exclusiva de la capa visual. No se modifican métricas, tablas científicas, nombres de CSV ni conclusiones. La revisión no acepta una figura solo por existir: se evaluó si responde una pregunta, si aporta más que el CSV, si es legible en notebook/PDF y si tiene problemas de clipping, solapamiento, exceso de texto o mala familia visual.

Artefactos auxiliares de revisión:

- `results/reports/01_raw_eda/_visual_review/all_figures_review_sheet_final.jpg`
- `results/reports/01_raw_eda/_visual_review/priority_figures_review_sheet_final.jpg`

## Figuras rediseñadas

| Figura | Diagnóstico visual previo | Acción aplicada | Resultado |
|---|---|---|---|
| `01_15_ead/raw_dataset_profile_heatmap.png` | Era una tabla de cajas coloreadas con mucho texto; útil como resumen, pero no como figura de memoria. | Sustituida por matriz de puntos: posición = indicador, color/tamaño = severidad, etiqueta corta = valor trazado. | Visualización real, menos texto, lectura comparativa inmediata. |
| `01_12_dimensionalidad/raw_dimensionality_summary.png` | Tarjetas textuales; parecía una ficha estática más que un gráfico. | Sustituida por bubble/dot plot en escala log: x = ratio variables/muestras, tamaño = número de variables, color = riesgo. | Se ve claramente que `madelon` queda separado y por encima del umbral. |
| `01_13_espurias/*_spurious_risk_volcano.png` | En `madelon` las anotaciones del volcano se solapaban; en `olive_oil` era una tabla visual. | Sustituidas por rankings horizontales de variables marcadas, con color por motivo de alerta. | Sin etiquetas pisadas; cada figura identifica qué variables revisar y cuántas se muestran. |
| `01_11_redundancia/customer_churn_spearman_heatmap.png` | Era una caja de texto, no una visualización. | Sustituida por ranking de pares con mayor \|Spearman\|, manteniendo la línea de umbral 0.85. | Muestra por qué no hay redundancia alta sin forzar un heatmap vacío. |
| `01_11_redundancia/breast_cancer_wisconsin_spearman_heatmap.png` | Heatmap completo de 30 variables con etiquetas densas. | Reducido a variables más implicadas en pares de alta correlación. | Mapa de calor más apto para notebook/PDF y mejor alineado con la pregunta de redundancia. |

## Figuras mantenidas con ajustes menores

| Figura o grupo | Motivo para mantener |
|---|---|
| Carga y estructura inicial | Las escalas logarítmicas y barras/scatter responden la pregunta de escala; no se detectó clipping ni solapamiento relevante. |
| Calidad del dato | Aporta más que una tabla porque prioriza incidencias accionables; no fuerza heatmap de nulos vacío. |
| Distribución y ratio del target | Familia correcta: composición para binarios y ranking para `olive_oil`; etiquetas y márgenes suficientes. |
| Muestreo visual | Comparación 100% apilada adecuada para preservar proporciones; n se deriva del CSV de estrategia. |
| Univariante | Composición multifamilia válida: ranking de outliers + distribución + boxplot. |
| Normalidad | Dot plot adecuado con advertencia metodológica; no fuerza QQ-plots masivos. |
| Asociación variable-target | Volcano + ranking sigue siendo útil; `olive_oil` usa ranking por efecto para evitar un volcano artificial. |
| FDR y tamaños de efecto | Barras/lollipop adecuados para comparación y ranking; sin anotaciones que tapen datos. |
| Preclasificación | Panel absoluto/log y relativo/100% comunica escala y composición; no se detectó clipping de leyenda tras ejecución. |
| PCA exploratorio | Curvas de varianza acumulada legibles; se mantiene como diagnóstico exploratorio. |

## Figuras convertidas en tabla o eliminadas

- No se eliminó ninguna ruta PNG para mantener trazabilidad y outputs esperados del notebook.
- La figura tipo “texto dentro de una caja” de `customer_churn` fue reemplazada por visualización real.
- La figura tipo “tabla de cajas” del perfil EAD fue reemplazada por matriz de severidad. No se conserva como figura textual.

## Diagnóstico por criterios obligatorios

- Pregunta analítica clara: confirmada para las 36 figuras.
- Aportación frente a tabla: corregida en perfil EAD, `customer_churn` redundancia y riesgos `olive_oil`; mantenida en el resto.
- Familia visual correcta: revisada con router de 35 familias y puerta de figura combinada.
- Tipo visual: hay visualizaciones simples, compuestas multifamilia y paneles comparativos; no se usan tartas, 3D ni dual y-axis.
- Exceso de texto: reducido en perfil EAD, dimensionalidad y riesgos.
- Texto tapando datos: corregido en riesgos `madelon` y dimensionalidad.
- Clipping/canvas: revisión manual sobre PNG regenerados; no se detectan etiquetas cortadas evidentes.
- Márgenes: ampliados o simplificados en figuras con anotaciones.
- Orden de categorías: consistente con `ORDEN_DATASETS` o ranking por métrica.
- Escala: barras con baseline cero; log solo en escala/dimensionalidad donde el rango lo exige y se etiqueta.
- Paleta: cálida y semántica; rojo/ámbar/verde solo para severidad/riesgo.
- Notebook/PDF: figuras revisadas en PNG final y miniaturas de control.

## Validación final

- `notebooks/fase1.ipynb` ejecutado completo con `qfs_env` mediante `nbconvert`: correcto.
- `py_compile` correcto para `src/fase1_refined_workflow.py`, `src/fase1_agent_utils.py` y `src/viz_core/editorial_warmth.py`.
- Salidas `image/png` en el notebook: 36.
- PNG guardados en `results/figures/01_raw_eda/`: 36.
- Figuras vacías: 0.
- Tablas clave presentes: confirmadas.
- Informes actualizados: `raw_phase1_results_report.md`, `raw_phase1_results_report.tex` y `Plantilla_Latex_GCD/tfgs/tex/resultados_fase1.tex`.
- Cifras trazadas preservadas: 59 candidatas, 29 riesgos, 493 posibles ruido en `madelon`, 29 pares redundantes en `breast_cancer_wisconsin`, 9 clases en `olive_oil`.

## Conclusiones científicas

No cambian las conclusiones científicas. Los cambios son de forma visual, elección de familia gráfica y legibilidad. Las únicas derivaciones nuevas son visuales y trazables a datos ya existentes: ranking de correlaciones máximas bajo umbral en `customer_churn`, reducción del heatmap de `breast_cancer_wisconsin` a variables implicadas y matriz de severidad EAD desde `raw_dataset_profiles.csv`.

## Incidencias abiertas

- No quedan incidencias visuales bloqueantes.
- Las figuras densas de correlación siguen siendo diagnósticas; para memoria se recomienda priorizar `raw_high_corr_pairs_by_dataset.png` y usar heatmaps completos o reducidos solo como apoyo.
