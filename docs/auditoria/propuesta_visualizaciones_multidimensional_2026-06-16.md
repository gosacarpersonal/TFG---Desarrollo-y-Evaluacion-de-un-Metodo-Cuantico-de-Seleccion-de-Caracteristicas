# Propuesta de visualizaciones multidimensionales para la memoria

Fecha: 2026-06-16.

## Principio rector

La memoria no debe defender una configuracion ganadora aislada. Debe mostrar que las conclusiones salen de patrones que se mantienen, se matizan o se rompen al variar:

- dataset;
- selector/metodo;
- cardinalidad `k`;
- semilla;
- modelo;
- metrica;
- split validation/test;
- parametro QFS, especialmente `beta`;
- criterio cuantico/oraculo/geometria.

Por tanto, cada visualizacion debe responder una pregunta concreta y declarar que dimensiones recorre. Los zooms son validos, pero solo despues de un panorama que demuestre que no hay cherry-picking.

## Estructura narrativa recomendada

1. **Trazabilidad**: de donde salen los datos y como se protege el pipeline.
2. **Cartografia experimental**: que espacio de combinaciones se exploro.
3. **Seleccion clasica**: que hacen los selectores y como cambian con `k`/semilla/dataset.
4. **Modelado**: que parte depende del selector, del modelo y de la metrica.
5. **Mecanismo**: por que algunas variables o criterios funcionan/fallan.
6. **QFS**: que aporta el criterio cuantico y como se comporta al variar `beta`.
7. **Sintesis**: conclusion final como compresion del recorrido, no como punto de partida.

## Figuras para el cuerpo de la memoria

### F0. Cadena de evidencia del TFG

**Pregunta:** que camino sigue la evidencia desde datos crudos hasta conclusion final.

**Datos origen:** inventario de artefactos y rutas de fase; puede construirse desde estructura de `data/`, `results/tables/`, notebooks y reports.

**Que dibuja:** diagrama horizontal o vertical:

`raw -> processed -> splits -> feature selection -> modeling -> QFS -> memoria`.

Cada bloque muestra artefactos clave: tablas, predicciones, figuras, verificadores.

**Dimensiones cubiertas:** fases, artefactos, controles de calidad.

**Refuerza:** metodologia y reproducibilidad. Evita que el lector vea solo resultados finales.

**Ubicacion:** metodologia o inicio de resultados.

### F1. Mapa de cobertura experimental

**Pregunta:** que espacio experimental se recorrio realmente.

**Datos origen:** `fs_selected_feature_sets.csv`, `modeling_validation_results_all.csv`, `qfs_phase8_summary.csv`, `qfs_runs_*.csv`.

**Que dibuja:** matriz/heatmap de cobertura:

- filas: datasets;
- columnas agrupadas: selector, `k`, modelo, metrica, beta/configuracion QFS;
- marca: existe/no existe, validation/test/QFS.

**Dimensiones cubiertas:** dataset, metodo, k, modelo, metrica, beta.

**Refuerza:** no se trabajo sobre una combinacion aislada. Es la figura anti-cherry-picking principal.

**Ubicacion:** inicio de resultados.

### F2. Espacio-problema de los datasets

**Pregunta:** que tipo de problema representa cada dataset.

**Datos origen:** `fs_input_dataset_summary.csv` y tablas de Fase 1/4 si se quiere incluir desbalance/splits.

**Que dibuja:** scatter:

- x: numero de features, escala log si hace falta;
- y: numero de muestras de train;
- color: desbalance/minority class;
- tamano: numero de clases;
- etiqueta: dataset.

**Dimensiones cubiertas:** dataset, n, p, clases, desbalance.

**Refuerza:** justifica que no todos los datasets deben leerse igual. Madelon, Churn, Breast Cancer y Olive no son el mismo regimen.

**Ubicacion:** resultados iniciales.

### F3. Perfil global de selectores

**Pregunta:** que personalidad operacional tiene cada selector.

**Datos origen:** `fs_method_profiles.csv`, `fs_all_execution_times.csv`, `fs_redundancy_vs_full.csv`, `fs_jaccard_stability.csv`.

**Que dibuja:** scatter o small multiples:

- x: estabilidad media;
- y: redundancia media;
- tamano: coste/tiempo;
- color: familia de metodo;
- etiqueta: metodo.

**Dimensiones cubiertas:** metodo, coste, estabilidad, redundancia.

**Refuerza:** situa a QFS respecto a selectores clasicos de relevancia-redundancia. No compara solo rendimiento; compara comportamiento.

**Caveat:** `fs_jaccard_stability.csv` mide estabilidad intra-metodo entre semillas, no solape metodo-metodo.

### F4. Estabilidad frente a semillas y k

**Pregunta:** que selectores son robustos cuando cambia la semilla y la cardinalidad.

**Datos origen:** `fs_jaccard_stability.csv`.

**Que dibuja:** heatmap o ridge por dataset:

- x: `k`;
- y: metodo;
- color: Jaccard medio entre semillas;
- facet: dataset.

**Dimensiones cubiertas:** dataset, metodo, k, semilla.

**Refuerza:** separa resultados robustos de resultados fragiles. Es clave para no depender de una sola semilla.

**Ubicacion:** seleccion clasica.

### F5. Solape entre metodos

**Pregunta:** distintos selectores llegan a subconjuntos parecidos o exploran zonas distintas.

**Datos origen:** `10_memoria_b2_jaccard_metodos.csv` o tabla metodo-metodo equivalente. No debe basarse solo en `fs_jaccard_stability.csv`.

**Que dibuja:** heatmap metodo x metodo:

- color: Jaccard inter-metodo;
- facet: dataset o un dataset representativo en cuerpo y todos en apendice.

**Dimensiones cubiertas:** dataset, metodo A, metodo B, k si la tabla lo conserva.

**Refuerza:** diversidad de selectores. Explica por que el ensemble de metodos tiene sentido y donde QFS se parece o se diferencia.

### F6. Senal frente al nulo

**Pregunta:** la seleccion esta capturando senal real o ruido compatible con permutacion.

**Datos origen:** `fs_permutation_empirical_pvalues.csv`, `fs_permutation_summary.csv`.

**Que dibuja:** stripplot/ECDF:

- x: p-valor empirico o distancia al nulo;
- y/facet: dataset;
- color: metodo o familia;
- linea: umbral FDR.

**Dimensiones cubiertas:** dataset, metodo, feature, nulo/permutacion.

**Refuerza:** validez estadistica de la seleccion. En Madelon puede mostrar que el problema no se resuelve solo con MI marginal.

### F7. Embudo de candidatos: de validation a test

**Pregunta:** como se pasa del espacio completo de modelos/subconjuntos a los candidatos finales.

**Datos origen:** `modeling_validation_results_all.csv`, `modeling_test_results_candidates.csv`.

**Que dibuja:** sankey ligero, dot plot o diagrama de etapas:

- candidatos evaluados en validation;
- top por dataset/modelo/selector;
- candidatos cerrados;
- evaluacion en test.

**Dimensiones cubiertas:** dataset, selector, k, modelo, split.

**Refuerza:** honestidad metodologica. Evita que el lector piense que el test se uso para elegir.

**Ubicacion:** puente seleccion-modelado.

### F8. Dependencia del modelo

**Pregunta:** cuanto dependen los resultados del modelo clasificador usado.

**Datos origen:** `modeling_validation_results_all.csv`.

**Que dibuja:** slopegraph o heatmap:

- filas: dataset;
- columnas: modelo (`linear_svm`, `logistic_regression`, `random_forest`, `xgboost`);
- color: macro-F1 o balanced accuracy;
- opcional: facet por selector/familia o mostrar mejores por selector.

**Dimensiones cubiertas:** dataset, modelo, selector, metrica.

**Refuerza:** controla una amenaza interpretativa: que el efecto atribuido al selector sea en realidad efecto del modelo.

**Prioridad:** alta. Deberia estar en cuerpo o cerca del cuerpo.

### F9. Rendimiento multidimensional: selector x k x dataset

**Pregunta:** que ocurre al variar `k`, no solo en el k elegido.

**Datos origen:** `modeling_validation_results_all.csv`, `modeling_cost_performance.csv`.

**Que dibuja:** lineas o heatmap:

- x: reduccion de features o `k`;
- y: delta macro-F1 frente a baseline mismo modelo;
- color: selector;
- facet: dataset;
- opcion secundaria: balanced accuracy.

**Dimensiones cubiertas:** dataset, selector, k, modelo, metrica.

**Refuerza:** no hay dependencia de un unico k. Permite ver zonas estables, deterioros y trade-offs.

### F10. Coste vs rendimiento

**Pregunta:** que trade-off se obtiene al reducir variables.

**Datos origen:** `modeling_cost_performance.csv`.

**Que dibuja:** scatter/curvas:

- x: `feature_reduction_ratio`;
- y: delta macro-F1 o test macro-F1;
- color: selector;
- tamano: fit_seconds o n_features_used;
- facet: dataset.

**Dimensiones cubiertas:** dataset, selector, k, modelo, coste, rendimiento.

**Refuerza:** eficiencia, no solo exactitud. Muy importante para justificar seleccion de caracteristicas.

### F11. Magnitud y significancia de las mejoras

**Pregunta:** las diferencias observadas son grandes y estadisticamente sostenibles.

**Datos origen:** `modeling_pairwise_comparison_tests.csv`, `modeling_test_results_candidates.csv`, `modeling_test_confidence_intervals.csv`.

**Que dibuja:** forest plot:

- filas: dataset/candidato;
- x: diferencia macro-F1;
- intervalo: bootstrap CI;
- color: p-valor/FDR o veredicto.

**Dimensiones cubiertas:** dataset, candidato, metrica, incertidumbre.

**Refuerza:** separa mejora numerica de mejora fiable. No basta con ranking.

### F12. SHAP vs MI: discordancia criterio-modelo

**Pregunta:** donde divergen relevancia marginal y utilidad predictiva/model-dependent.

**Datos origen:** `modeling_shap_feature_importance.csv` unido con `fs_qfs_mi_target_vector_long.csv` por `(dataset, feature)`.

**Que dibuja:** scatter facetado:

- x: `I_i`;
- y: importancia SHAP media;
- color: seleccionado/no seleccionado o selector;
- facet: dataset;
- etiquetas: outliers.

**Dimensiones cubiertas:** dataset, feature, MI, SHAP, modelo/candidato.

**Refuerza:** mecanismo. Explica por que un criterio basado en informacion marginal puede fallar en algunos regimenes.

**Caveat:** no debe venderse como prueba absoluta de fallo del criterio; SHAP depende del modelo y del candidato.

### F13. SHAP beeswarm representativo

**Pregunta:** como se distribuye el impacto de variables en instancias reales.

**Datos origen:** `modeling_shap_values_full_*`, `modeling_shap_feature_values_*`.

**Que dibuja:** beeswarm para un dataset representativo en cuerpo; todos los datasets en apendice.

**Dimensiones cubiertas:** instancia, feature, valor feature, SHAP.

**Refuerza:** interpretabilidad local/global. Convierte F12 en lectura concreta.

**Recomendacion:** cuerpo: Madelon si se quiere explicar criterio; apendice: resto.

### F14. Barrido QFS beta: rendimiento y cardinalidad

**Pregunta:** como cambia la seleccion QFS al variar beta.

**Datos origen:** `qfs_phase8_summary.csv` y `qfs_runs_<dataset>_<beta>.csv`.

**Que dibuja:** 2 paneles:

- panel 1: validation macro-F1 vs beta;
- panel 2: cardinalidad/k o n_features seleccionadas vs beta;
- lineas: dataset o configuracion.

**Dimensiones cubiertas:** dataset, beta, configuracion, rendimiento, cardinalidad.

**Refuerza:** QFS no se evalua en un punto; se estudia como paisaje parametrico.

### F15. QFS vs baseline clasico

**Pregunta:** QFS mejora, empata o empeora frente al baseline clasico.

**Datos origen:** `comparacion_qfs_vs_baseline.csv`, `comparacion_qfs_configuraciones_vs_baseline.csv`.

**Que dibuja:** forest plot/slopegraph:

- filas: dataset/configuracion;
- x: delta test macro-F1;
- intervalo: CI;
- color: veredicto;
- anotacion: p-FDR.

**Dimensiones cubiertas:** dataset, configuracion QFS, baseline, metrica, incertidumbre.

**Refuerza:** conclusion comparativa central.

### F16. Control QFS-NA frente a oraculo

**Pregunta:** el comportamiento QFS se debe al criterio/optimizador o a errores de construccion.

**Datos origen:** `qfs_quality_control_*.csv`, `qfs_oracle_*.csv`.

**Que dibuja:** 2 paneles o 2x2 fusionable con F14:

- Hamming vs beta;
- delta coste vs beta;
- lineas: dataset/configuracion.

**Dimensiones cubiertas:** dataset, beta, oraculo, calidad, coste.

**Refuerza:** validez tecnica del modulo cuantico.

**Decision:** fusionable con F14 si no queda demasiado denso.

### F17. Geometria fisica de atomos Rydberg

**Pregunta:** que embedding fisico subyace a la formulacion QFS.

**Datos origen:** `qfs_embedding_error.csv`, especialmente `positions_json`.

**Que dibuja:** scatter de atomos:

- x/y: coordenadas MDS;
- color: seleccion/relevancia/coste;
- facet: dataset;
- anotacion: error de embedding.

**Dimensiones cubiertas:** dataset, feature/atomo, geometria, error.

**Refuerza:** interpretacion cuantica material. Hace visible el sustrato fisico.

**Ubicacion recomendada:** apendice o cuerpo si la seccion cuantica necesita apoyo visual.

### F18. Ocupacion feature x beta

**Pregunta:** que features/atomos aparecen o desaparecen al variar beta.

**Datos origen:** `qfs_runs_<dataset>_<beta>.csv`, columnas de seleccion/densidad si estan disponibles.

**Que dibuja:** heatmap:

- x: beta;
- y: feature;
- color: seleccion/frecuencia/densidad;
- facet: dataset.

**Dimensiones cubiertas:** dataset, beta, feature, ocupacion.

**Refuerza:** profundidad cuantica y sensibilidad parametrica.

**Ubicacion:** apendice fuerte.

### F19. Scorecard final multidimensional

**Pregunta:** cual es la lectura final comprimida de todo el recorrido.

**Datos origen:** `fase7_comparacion_final_con_qfs.csv`, `comparacion_qfs_vs_baseline.csv`, tablas de modelado y QFS.

**Que dibuja:** tablero:

- filas: dataset;
- columnas: baseline, mejor clasico, QFS, robustez, coste, interpretabilidad;
- color/icono: gana/empata/pierde/advertencia;
- anotacion: metrica principal y evidencia.

**Dimensiones cubiertas:** dataset, metodo, rendimiento, coste, robustez, veredicto.

**Refuerza:** conclusion final, pero solo despues de haber mostrado el paisaje.

## Figuras de apendice recomendadas

### A1. Grid completo selector x k x dataset

Heatmap completo de rendimiento o estabilidad. Refuerza exhaustividad.

### A2. Estabilidad por semilla detallada

Distribuciones de Jaccard por metodo/dataset/k. Refuerza robustez y variabilidad.

### A3. Rankings granulares por metodo

Top features por metodo/dataset/k desde tablas granulares. Refuerza trazabilidad.

### A4. Redundancia y VIF de seleccionados

Distribuciones de correlacion/redundancia. Refuerza que no basta con seleccionar variables informativas.

### A5. Permutaciones completas

Todas las distribuciones nulas relevantes. Refuerza rigor estadistico.

### A6. Matrices MI par a par

Desde `fs_qfs_pairwise_mi_matrix_*`. Refuerza el puente entre seleccion clasica y formulacion QFS.

### A7. Todos los beeswarms SHAP

Uno por dataset/candidato principal. Refuerza interpretabilidad sin saturar el cuerpo.

### A8. Todos los modelos por selector/k

Vista amplia de `modeling_validation_results_all.csv`. Refuerza que la conclusion no depende de un modelo.

### A9. Metricas alternativas

Balanced accuracy, accuracy, AUC y macro-F1 en paralelo. Refuerza que no se optimizo una sola metrica.

### A10. Paisaje completo QFS por configuracion

`comparacion_qfs_configuraciones_vs_baseline.csv` y `qfs_runs_*`. Refuerza que QFS se estudio como familia parametrica.

### A11. Control de leakage/drift/splits

Tablas de fases 3 y 4. Refuerza validez experimental.

### A12. Logs y runs anteriores

No como resultados principales, sino como trazabilidad historica. Refuerza auditoria; no debe mezclarse con run canonico.

## Figuras que evitaria o degradaria

1. **Una unica curva de un dataset/k/modelo** como evidencia principal.
2. **Un heatmap metodo-metodo construido desde estabilidad entre semillas**: mezcla conceptos.
3. **Un ranking de top features sin mostrar estabilidad o sensibilidad a k**.
4. **Una figura QFS solo en beta optimo**: oculta la sensibilidad parametrica.
5. **Un scorecard final antes del paisaje**: parece conclusion seleccionada a posteriori.

## Orden recomendado en la memoria

1. F0 Cadena de evidencia.
2. F1 Cobertura experimental.
3. F2 Espacio-problema.
4. F3 Perfil de selectores.
5. F4 Estabilidad semilla/k.
6. F5 Solape entre metodos.
7. F6 Senal frente al nulo.
8. F7 Embudo validation-test.
9. F8 Dependencia del modelo.
10. F9 Selector x k x dataset.
11. F10 Coste vs rendimiento.
12. F11 Significancia/magnitud.
13. F12 SHAP vs MI.
14. F13 Beeswarm representativo.
15. F14/F16 Barrido y control QFS, fusionados si cabe.
16. F15 QFS vs baseline.
17. F19 Scorecard final.

## Prioridad de construccion

### Primero

- F1 cobertura experimental;
- F7 embudo validation-test;
- F8 dependencia del modelo;
- F9 selector x k x dataset;
- F14/F16 barrido QFS.

Estas figuras protegen contra cherry-picking.

### Segundo

- F3/F4/F5/F6 bloque de seleccion clasica;
- F10/F11 bloque coste-significancia;
- F12/F13 interpretabilidad.

Estas figuras explican mecanismos.

### Tercero

- F17/F18 y apendices extendidos;
- F19 scorecard final.

Estas figuras cierran y dan profundidad.

## Tesis visual final

La memoria debe poder sostener esta frase:

> La conclusion no se apoya en una configuracion ganadora aislada, sino en la consistencia y las excepciones observadas al recorrer datasets, selectores, cardinalidades, semillas, modelos, metricas y parametros QFS.

