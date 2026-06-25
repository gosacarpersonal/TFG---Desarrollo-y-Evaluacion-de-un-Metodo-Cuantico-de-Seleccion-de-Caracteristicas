# Auditoría de refinamiento — Fase 1

## Checks superados
- **Ejecución completa del notebook:** superado. Evidencia: nbconvert con qfs_env terminó sin errores antes de generar esta auditoría.
- **Código del notebook más limpio:** superado. Evidencia: 32 celdas de código; máximo 22 líneas.
- **Módulos compilables:** superado. Evidencia: py_compile superado para fase1_agent_utils.py y fase1_refined_workflow.py.
- **Figuras guardadas y mostradas:** superado. Evidencia: 36 salidas image/png y 36 PNG guardados.
- **Figuras no vacías:** superado. Evidencia: 0 PNG sospechosos.
- **Tablas importantes existentes:** superado. Evidencia: todas presentes.
- **Markdown y LaTeX actualizados:** superado. Evidencia: raw_phase1_results_report.tex coincide con Plantilla_Latex_GCD/tfgs/tex/resultados_fase1.tex.
- **Cifras trazadas a CSV:** superado. Evidencia: 54 líneas derivadas de CSV verificadas; faltantes 0.
- **Conclusiones científicas preservadas:** superado. Evidencia: conteos clave coinciden: 59 candidatas, 29 sospechosas, Madelon ruido 493, Breast redundancia 29, Olive Oil 9 clases.

## Incidencias abiertas
- No quedan incidencias bloqueantes tras el refinamiento.

## Código limpiado
- Se sustituyó el notebook largo por una versión orquestadora con celdas compactas y flujo narrativo sección a sección.
- Se eliminó del notebook la lógica extensa de cálculo, visualización e informes; ahora vive en `src/fase1_refined_workflow.py`.
- Se mantuvo `src/fase1_agent_utils.py` como capa de utilidades base para lectura, guardado, FDR, roles, outliers, tamaños de efecto y LaTeX.

## Funciones movidas o refactorizadas
- Carga y estructura: `cargar_datasets_crudos`, `auditar_estructura`.
- Calidad, target y muestreo: `auditar_calidad`, `analizar_target`, `crear_muestras_visuales`.
- Estadística exploratoria: `analizar_univariante`, `analizar_normalidad`, `analizar_asociacion_target`, `analizar_fdr_y_efectos`, `analizar_redundancia`, `analizar_dimensionalidad_y_pca`.
- Riesgos, preclasificación e informes: `detectar_riesgos_espurios`, `preclasificar_variables`, `construir_perfiles_dataset`, `generar_informes_fase1`, `generar_checklist_y_handoff`, `generar_revision_critica`.
- Visualizaciones: funciones `plot_*` por sección, con estilo editorial compartido mediante `PALETA`, `preparar_ejes` y helpers de etiquetas.

## Figuras sustituidas
- Se sustituyeron las 36 figuras guardadas manteniendo las mismas rutas PNG bajo `results/figures/01_raw_eda/`.
- Cambios visuales aplicados: fondo cálido, paleta consistente, rejillas suaves, ejes menos ruidosos, escalas logarítmicas donde la diferencia de escala lo requiere, etiquetas directas y títulos más narrativos.
- Las figuras candidatas para memoria siguen siendo las mismas rutas registradas en `raw_figures_selected_for_report.csv`.

## Figuras eliminadas
- No se eliminó ninguna figura guardada. Se mantuvieron rutas estables para no romper trazabilidad con informes ni Fase 2.
- Se mantiene la decisión metodológica de no crear heatmaps de nulos vacíos porque no hay nulos reales.

## Confirmaciones finales
- Ejecución completa: confirmada con `conda run -n qfs_env jupyter nbconvert --execute notebooks/fase1.ipynb`.
- Figuras guardadas y mostradas: confirmadas por igualdad entre salidas `image/png` del notebook y PNG guardados.
- Trazabilidad de cifras: confirmada contra tablas CSV guardadas.
- Informes actualizados: `raw_phase1_results_report.md`, `raw_phase1_results_report.tex` y `Plantilla_Latex_GCD/tfgs/tex/resultados_fase1.tex` regenerados.
- Integración LaTeX: no hay motor LaTeX local disponible; se valida estructura, copia en plantilla y consistencia de contenido.

## ¿Cambiaron las conclusiones científicas?
- No. El refinamiento cambió arquitectura, legibilidad y estética visual, pero no cambió el objetivo científico ni las conclusiones auditadas.
- Se preservan las cautelas: `customer_churn` no se sobreinterpreta por tamaño muestral; `madelon` se interpreta como alta dimensionalidad/ruido con señal residual; `olive_oil` queda multiclase desbalanceado; `breast_cancer_wisconsin` mantiene señal fuerte con redundancia alta.

## Puntos que deben vigilarse en Fase 2
- IDs: excluir o aislar columnas `posible_id` antes de entrenar.
- Baja varianza/dominancia: revisar `raw_low_variance_features.csv`.
- Codificación: ajustar codificadores solo con train.
- Escalado: ajustar escaladores solo con train, especialmente para PCA/distancias.
- Outliers: revisar `raw_outlier_summary.csv`; evitar eliminación automática.
- Splits: estratificar; especial atención a `olive_oil`.
- Leakage/proxies: revisar `raw_spurious_risk_features.csv` y `raw_proxy_leakage_candidates.csv`.
- Redundancia: controlar `raw_high_correlation_pairs.csv`, especialmente en `breast_cancer_wisconsin`.
