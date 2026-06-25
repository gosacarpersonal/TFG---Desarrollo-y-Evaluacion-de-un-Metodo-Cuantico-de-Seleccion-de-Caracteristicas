# Auditoría visual final — Fase 1

Fecha de ejecución: 2026-06-04.

## Alcance

Esta auditoría documenta el refinamiento exclusivo de la capa visual de la Fase 1. No se ha rehecho el análisis científico ni se han cambiado nombres de CSV. Las figuras se han regenerado manteniendo rutas PNG estables y trazabilidad con las tablas de `results/tables/01_raw_eda/`.

Skills aplicadas:

- `.agents/scientific-narrative-notebook-builder/SKILL.md`.
- `.agents/arquitecto-codigo-limpio/SKILL.md`.
- `.agents/ds-visual-storyteller-definitive/SKILL.md`.

Ruta visual obligatoria aplicada: pregunta analítica, forma de datos, intención analítica, métrica derivada, restricción científica, familia visual, puerta de figura combinada, alternativas rechazadas, brief narrativo, pase de calidez editorial y revisión notebook/PDF.

## Cambios principales

- Se sustituyó texto visible provisional por castellano natural y prudente en títulos, ejes, subtítulos y anotaciones.
- Se eliminó un bloque técnico impreso en el notebook que no aportaba evidencia visual.
- Se corrigió el ranking visual de `olive_oil` en asociación variable-target para mostrar los mayores efectos, sin alterar tablas ni métricas.
- Se rediseñó el cuadro final EAD para leer sus conteos desde `raw_dataset_profiles.csv`, evitando valores escritos a mano que podían desincronizarse.
- Se mantuvieron las rutas PNG existentes y se actualizaron captions en `raw_figures_selected_for_report.csv`, `raw_phase1_results_report.md`, `raw_phase1_results_report.tex` y `Plantilla_Latex_GCD/tfgs/tex/resultados_fase1.tex`.

## Decisiones por familia visual

| Sección | Pregunta analítica | Forma de datos | Intención | Métrica derivada | Restricción científica | Tipo visual | Familia elegida | Alternativas rechazadas | Acción |
|---|---|---|---|---|---|---|---|---|---|
| Carga inicial | ¿Qué datasets dominan por muestras y variables? | Categoría + magnitud | Comparar escala | Filas y columnas en escala log | Rangos muy distintos | Panel comparativo homogéneo | Barras horizontales | Tabla aislada, barras verticales comprimidas | Ajuste editorial |
| Estructura | ¿Qué riesgo inicial aporta el ratio variables/muestras? | Dos magnitudes + ratio | Diagnóstico | Ratio variables/muestras | Alta dimensionalidad en `madelon` | Panel comparativo heterogéneo | Scatter log + barras horizontales | Mapa de calor estructural, tabla sola | Ajuste editorial |
| Calidad | ¿Qué incidencias accionables existen si nulos/duplicados son cero? | Categoría + conteo | Detectar riesgo | Variables con baja variabilidad/dominancia | Evitar heatmap vacío | Visualización simple | Dot/lollipop horizontal | Heatmap de nulos sin señal, figura decorativa | Ajuste editorial |
| Target | ¿Cómo se reparte la variable objetivo? | Composición + conteo | Mostrar composición y desbalance | Proporciones y ratio mayoritaria/minoritaria | Binario frente a multiclase | Panel comparativo heterogéneo | Barras 100% + barras horizontales | Gráfico de tarta, tabla sin lectura visual | Ajuste editorial |
| Muestreo | ¿La muestra visual preserva el target? | Composición pareada | Comparar antes/después | Diferencia absoluta de proporciones | Dataset grande muestreado | Visualización simple | Barras 100% apiladas pareadas | Tabla sola, barras no normalizadas | Ajuste editorial |
| Univariante | ¿Qué variable concentra más outliers y cómo se distribuye? | Ranking + distribución | Diagnosticar distribución | Tasa de outliers IQR | Evitar paneles masivos ilegibles | Figura compuesta multifamilia | Barras horizontales + histograma/KDE + boxplot | Grid completo de histogramas, pairplot | Rediseño fuerte previo mantenido y pulido |
| Normalidad | ¿Qué proporción rechaza normalidad por dataset? | Categoría + proporción | Diagnóstico metodológico | Proporción de tests con p < 0.05 | Potencia excesiva con muestras grandes | Visualización simple | Dot plot con tamaño contextual | QQ plots masivos, histograma de p-values | Ajuste editorial |
| Asociación variable-target | ¿Qué variables combinan significación FDR y efecto? | Efecto + p-value FDR | Relación y ranking | -log10(FDR), tamaño de efecto absoluto | No exagerar p-values | Figura compuesta multifamilia | Volcano + ranking; barras para `olive_oil` | Scatter denso único, tabla extensa | Rediseño fuerte y corrección visual |
| FDR | ¿Cuánto cambia la señal tras corregir múltiples comparaciones? | Categoría + conteos pareados | Comparar antes/después | Significativas sin corregir y tras FDR | Control de falsos positivos | Visualización simple | Barras agrupadas horizontales | Histogramas de p-values, tabla sola | Ajuste editorial |
| Tamaños de efecto | ¿Qué variables tienen mayor magnitud de asociación? | Ranking | Ordenar efectos | Valor absoluto del tamaño de efecto | Comparabilidad por métrica interna | Visualización simple | Lollipop/Cleveland | Barras verticales, tabla extensa | Ajuste editorial |
| Redundancia | ¿Dónde existe colinealidad relevante? | Matriz + conteo | Diagnóstico de redundancia | Pares con \|Spearman\| >= 0.85 | Mapas de calor grandes pueden ser ilegibles | Paneles/figuras según dataset | Mapa de calor enfocado + lollipop resumen + tarjeta si no hay pares | Mapa de calor vacío, clustermap innecesario | Rediseño y ajuste de anotación |
| Dimensionalidad/PCA | ¿Qué datasets requieren reducción o control dimensional? | Perfil + curva | Diagnóstico | Ratio variables/muestras y varianza acumulada | PCA exploratorio sin modelado | Panel comparativo homogéneo + líneas | Tarjeta de perfil + curva de varianza | PCA 3D, scatter PC1/PC2 sin pregunta | Ajuste editorial |
| Riesgos espurios/leakage | ¿Qué variables requieren revisión semántica? | Efecto + FDR + alerta | Detectar riesgo | Indicadores de sospecha | Riesgo potencial, no confirmación | Panel comparativo heterogéneo | Volcano resaltado o tabla visual | Heatmap de riesgos, red causal no justificada | Ajuste editorial |
| Preclasificación | ¿Cómo se distribuyen las categorías preliminares? | Categoría + conteo/proporción | Comparar composición | Conteo absoluto y proporción relativa | Escalas de datasets muy distintas | Panel comparativo homogéneo | Barras apiladas absolutas y 100% | Pie chart, treemap | Ajuste editorial |
| Perfil EAD | ¿Qué perfil de riesgo queda por dataset? | Matriz de estados | Resumir perfil | Indicadores de `raw_dataset_profiles.csv` | No crear conclusiones nuevas | Panel comparativo homogéneo | Cuadro tipo matriz | Tabla densa, mapa de calor numérico sin contexto | Rediseño fuerte y corrección visual |

## Figuras rediseñadas o ajustadas

Se regeneraron y mostraron en el notebook las 36 figuras siguientes:

- `results/figures/01_raw_eda/01_01_carga/raw_load_rows_columns.png`
- `results/figures/01_raw_eda/01_02_estructura/raw_structure_summary.png`
- `results/figures/01_raw_eda/01_03_calidad/raw_quality_issues_summary.png`
- `results/figures/01_raw_eda/01_04_target/raw_target_balance_ratio.png`
- `results/figures/01_raw_eda/01_04_target/raw_target_distribution_panel.png`
- `results/figures/01_raw_eda/01_05_muestreo/customer_churn_target_full_vs_sample.png`
- `results/figures/01_raw_eda/01_06_univariante/breast_cancer_wisconsin_selected_numeric_distributions.png`
- `results/figures/01_raw_eda/01_06_univariante/customer_churn_selected_numeric_distributions.png`
- `results/figures/01_raw_eda/01_06_univariante/madelon_selected_numeric_distributions.png`
- `results/figures/01_raw_eda/01_06_univariante/olive_oil_selected_numeric_distributions.png`
- `results/figures/01_raw_eda/01_07_normalidad/raw_normality_rejection_by_dataset.png`
- `results/figures/01_raw_eda/01_08_asociacion_target/breast_cancer_wisconsin_volcano_ranking.png`
- `results/figures/01_raw_eda/01_08_asociacion_target/customer_churn_volcano_ranking.png`
- `results/figures/01_raw_eda/01_08_asociacion_target/madelon_volcano_ranking.png`
- `results/figures/01_raw_eda/01_08_asociacion_target/olive_oil_volcano_ranking.png`
- `results/figures/01_raw_eda/01_09_fdr/raw_fdr_before_after.png`
- `results/figures/01_raw_eda/01_10_tamanos_efecto/breast_cancer_wisconsin_effect_size_lollipop.png`
- `results/figures/01_raw_eda/01_10_tamanos_efecto/customer_churn_effect_size_lollipop.png`
- `results/figures/01_raw_eda/01_10_tamanos_efecto/madelon_effect_size_lollipop.png`
- `results/figures/01_raw_eda/01_10_tamanos_efecto/olive_oil_effect_size_lollipop.png`
- `results/figures/01_raw_eda/01_11_redundancia/breast_cancer_wisconsin_spearman_heatmap.png`
- `results/figures/01_raw_eda/01_11_redundancia/customer_churn_spearman_heatmap.png`
- `results/figures/01_raw_eda/01_11_redundancia/madelon_spearman_heatmap.png`
- `results/figures/01_raw_eda/01_11_redundancia/olive_oil_spearman_heatmap.png`
- `results/figures/01_raw_eda/01_11_redundancia/raw_high_corr_pairs_by_dataset.png`
- `results/figures/01_raw_eda/01_12_dimensionalidad/breast_cancer_wisconsin_pca_scree.png`
- `results/figures/01_raw_eda/01_12_dimensionalidad/customer_churn_pca_scree.png`
- `results/figures/01_raw_eda/01_12_dimensionalidad/madelon_pca_scree.png`
- `results/figures/01_raw_eda/01_12_dimensionalidad/olive_oil_pca_scree.png`
- `results/figures/01_raw_eda/01_12_dimensionalidad/raw_dimensionality_summary.png`
- `results/figures/01_raw_eda/01_13_espurias/breast_cancer_wisconsin_spurious_risk_volcano.png`
- `results/figures/01_raw_eda/01_13_espurias/customer_churn_spurious_risk_volcano.png`
- `results/figures/01_raw_eda/01_13_espurias/madelon_spurious_risk_volcano.png`
- `results/figures/01_raw_eda/01_13_espurias/olive_oil_spurious_risk_volcano.png`
- `results/figures/01_raw_eda/01_14_preclasificacion/raw_feature_preclassification_stacked.png`
- `results/figures/01_raw_eda/01_15_ead/raw_dataset_profile_heatmap.png`

## Figuras mantenidas o eliminadas

- Figuras mantenidas sin eliminación: todas las rutas PNG existentes se conservaron.
- Figuras eliminadas: ninguna.
- No se añadieron figuras decorativas.
- Donde una figura podía ser vacía o poco informativa, se mantuvo una representación explícita y sobria solo si respondía una pregunta concreta; por ejemplo, `customer_churn_spearman_heatmap.png` comunica la ausencia de pares por encima del umbral en lugar de forzar un heatmap vacío.

## Pase de calidez editorial

- Superficie: fondo cálido claro (`#FAF7F2`) apto para notebook y memoria.
- Acento principal: azul sobrio para magnitudes centrales; naranja para umbrales/anotaciones; rojo/verde/amarillo solo para estados de riesgo.
- Contexto atenuado: elementos secundarios en gris cálido, rejillas suaves y spines mínimos.
- Jerarquía textual: títulos narrativos prudentes, subtítulos con denominador o restricción cuando aporta, anotaciones limitadas a focos analíticos.
- Honestidad científica: se mantienen escalas logarítmicas etiquetadas, FDR visible, umbrales explícitos, conteos de variables y advertencias de potencia estadística.

## Validación final

- Ejecución completa de `notebooks/fase1.ipynb` con `qfs_env`: correcta, sin errores.
- `py_compile` correcto para:
  - `src/viz_core/editorial_warmth.py`
  - `src/fase1_refined_workflow.py`
  - `src/fase1_agent_utils.py`
- Salidas `image/png` en notebook: 36.
- PNG guardados en `results/figures/01_raw_eda/`: 36.
- Figuras vacías detectadas: 0.
- Figuras con tamaño anómalo detectadas: 0.
- Tablas clave presentes: confirmadas.
- Informes actualizados: `raw_phase1_results_report.md`, `raw_phase1_results_report.tex` y `Plantilla_Latex_GCD/tfgs/tex/resultados_fase1.tex`.
- Cifras trazadas verificadas:
  - 59 variables candidatas univariantes.
  - 29 variables con riesgo exploratorio.
  - 493 variables de posible ruido univariante en `madelon`.
  - 29 pares de alta correlación en `breast_cancer_wisconsin`.
  - 9 clases en `olive_oil`.

## Conclusiones científicas

Las conclusiones científicas no cambiaron. El refinamiento mejora legibilidad, composición y trazabilidad visual. La única corrección sustantiva en una figura fue alinear el cuadro EAD y el ranking visual de `olive_oil` con los CSV ya generados; no se modificaron tablas, métricas ni conclusiones.

## Incidencias abiertas

- No quedan incidencias visuales bloqueantes.
- La compilación completa del documento LaTeX no se ejecutó en esta auditoría; se verificó la actualización de los archivos `.tex` generados y de la copia de plantilla.
