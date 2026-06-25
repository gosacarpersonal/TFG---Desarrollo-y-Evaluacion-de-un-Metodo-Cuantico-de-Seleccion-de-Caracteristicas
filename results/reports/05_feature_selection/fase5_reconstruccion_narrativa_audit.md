# Auditoría de reconstrucción narrativa - Fase 5

## Secciones corregidas

- Se sustituyó el patrón repetitivo `Objetivo/Evidencia/Decisión/Revisión` por preguntas científicas específicas en 5.1-5.16.
- Se movieron las figuras a las secciones donde explican el diseño o la interpretación: k en 5.5, permutaciones en 5.11, variables recurrentes en 5.7-5.8 y síntesis visual en 5.15.
- Se separaron explícitamente evidencia, interpretación, decisión e implicación para Fase 6 en texto narrativo.

## Tablas resumidas

- Se reemplazó la exposición directa de CSV largos por vistas compactas derivadas en memoria.
- El detalle completo se preserva en `results/tables/05_feature_selection/`.
- Las vistas principales son: dimensionalidad por dataset, familias de métodos, plan de ejecución, k por dataset, muestreo, variables recurrentes, estabilidad, permutaciones, redundancia y recomendaciones para Fase 6.

## `.head()` eliminados o justificados

- El notebook reconstruido no usa `.head()` como evidencia principal.
- Las vistas compactas usan una función explícita `mostrar_tabla_compacta`, que informa cuántas filas existen en el CSV completo y cuántas se muestran.

## Figuras recolocadas/rediseñadas

- No se rediseñaron métricas ni figuras guardadas para no alterar resultados.
- Se recolocaron figuras existentes en el argumento narrativo.
- La lámina de revisión visual se conserva como síntesis, y los heatmaps densos permanecen como apéndice auditado.

## Criterios metodológicos explicitados

- Contrato train-only.
- Separación de `olive_oil_3class` y `olive_oil_9class`.
- Interpretación de familias de métodos.
- Justificación de k, muestreo, semillas, estabilidad, permutaciones y redundancia.
- Distinción entre `principal_para_modelado` y `auxiliar_exploratorio` en Fase 6.

## Conclusiones preservadas

- No se cambiaron métricas, rankings, datasets reducidos ni rutas de artefactos.
- La interpretación sigue siendo prudente: la utilidad predictiva final queda para Fase 6.

## Artefactos preservados

- CSV completos en `results/tables/05_feature_selection/`.
- Figuras en `results/figures/05_feature_selection/`.
- Datasets reducidos en `data/selected_features/`.
- Informes Markdown/LaTeX y handoff existentes.

## Incidencias abiertas

- El notebook depende de artefactos previos: si se borran CSV o figuras, se detiene con error explícito.
- La auditoría visual final debe revisarse también en el PDF/visor humano de la memoria.
- Fase 6 debe validar rendimiento; Fase 5 no declara un selector óptimo.

## Limpieza final de presentación

- Se eliminaron rutas absolutas de tablas visibles y se sustituyeron por rutas relativas cuando la ruta aporta trazabilidad.
- Se limitaron las vistas compactas a ocho columnas por defecto para reducir roturas en PDF.
- Se truncaron textos largos en columnas narrativas o de ruta sin modificar los CSV completos.
- Se evitó una construcción de pandas sensible a avisos futuros y se mantuvo la misma lectura agregada.
- Las 14 figuras auditadas se muestran en el notebook con tamaño fijo legible, ancho responsive y texto alternativo; los ficheros originales no se modificaron.
- La comprobación final de presentación exporta HTML/PDF desde el notebook ejecutado para revisar warnings, tablas, rutas visibles y legibilidad.
- Esta pasada no cambió métricas, rankings, datasets reducidos, rutas de artefactos guardados ni conclusiones científicas.
