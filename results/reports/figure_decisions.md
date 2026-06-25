# Decisiones de visualización

## Fase 5: familias de figura

### fase5_estabilidad_jaccard
- Tier: 2
- Pregunta: ¿Qué métodos son estables entre semillas en cada dataset?
- Familia: heatmap anotado.
- Decisión: se usa una matriz dataset-método porque el mensaje principal es localizar estabilidad alta y baja en 5 datasets y 11 métodos con ranking.
- Ruta PNG: results/figures/05_feature_selection/stability/fs_stability_jaccard_heatmap.png
- Ruta PDF: results/figures/05_feature_selection/stability/fs_stability_jaccard_heatmap.pdf

### fase5_permutaciones_target
- Tier: 2
- Pregunta: ¿Qué variables de los métodos de relevancia pura quedan por encima del nulo por permutación?
- Familia: heatmap anotado.
- Decisión: se muestra el recuento sobre p95 nulo porque la tabla contiene p-valores por variable y la figura aporta lectura comparativa inmediata.
- Ruta PNG: results/figures/05_feature_selection/permutation/fs_permutation_above_null_heatmap.png
- Ruta PDF: results/figures/05_feature_selection/permutation/fs_permutation_above_null_heatmap.pdf

### fase5_redundancia_interna
- Tier: 2
- Pregunta: ¿La selección reduce o concentra redundancia respecto al espacio completo?
- Familia: dot plot con línea cero.
- Decisión: se conserva el signo del cambio y la dispersión por dataset; una tabla obligaría a calcular mentalmente qué métodos quedan a cada lado de cero.
- Ruta PNG: results/figures/05_feature_selection/redundancy/fs_redundancy_delta.png
- Ruta PDF: results/figures/05_feature_selection/redundancy/fs_redundancy_delta.pdf

### fase5_comparacion_roster_dataset
- Tier: 0
- Pregunta: ¿Cómo cambia el tamaño seleccionado entre métodos para un dataset?
- Familia: barras horizontales repetidas por dataset.
- Decisión: se reutiliza la misma familia con escala local para separar el tamaño natural de Boruta de los cortes top-k del resto del roster.
- Ruta PNG ejemplo: results/figures/05_feature_selection/roster_by_dataset/madelon_roster_comparison.png
- Ruta PDF ejemplo: results/figures/05_feature_selection/roster_by_dataset/madelon_roster_comparison.pdf

### fase5_heatmap_metodo_variable
- Tier: 0
- Pregunta: ¿Qué coincidencias aparecen entre métodos y variables seleccionadas?
- Familia: heatmap binario.
- Decisión: se usa como apoyo visual de coincidencias método-variable; la tabla granular mantiene k, ranking y score exactos.
- Ruta PNG ejemplo: results/figures/05_feature_selection/method_feature_heatmaps/madelon_method_feature_heatmap.png
- Ruta PDF ejemplo: results/figures/05_feature_selection/method_feature_heatmaps/madelon_method_feature_heatmap.pdf


## Fase 6: familias de figura

### fase6_baseline_vs_metodos_ic
- Tier: 2
- Pregunta: ¿Qué candidatos finales superan o igualan al baseline con incertidumbre visible?
- Familia: dot plot con intervalos de confianza.
- Decisión: se prioriza Macro-F1 en test con IC bootstrap 95%; las barras evitan leer solo el punto estimado.

### fase6_shap_dataset
- Tier: 2
- Pregunta: ¿Qué variables sostienen la explicación local de los candidatos finales?
- Familia: beeswarm SHAP con valores firmados por instancia.
- Decisión: se persiste la matriz SHAP cruda y se reserva la media de |SHAP| para tablas auxiliares; en olive se separa además por clase.

### fase6_coste_rendimiento
- Tier: 2
- Pregunta: ¿Dónde aparece el compromiso entre coste dimensional, tiempo y Macro-F1?
- Familia: scatter coste-rendimiento.
- Decisión: se codifican variables usadas, Macro-F1, modelo y tiempo para mostrar el frente práctico que la tabla no revela.
