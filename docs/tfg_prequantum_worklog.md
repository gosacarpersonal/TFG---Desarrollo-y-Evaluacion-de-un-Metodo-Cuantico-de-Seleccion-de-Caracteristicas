# Bitácora de trabajo pre-cuántico (Fases 1-7)

Registro único de cambios, validaciones y evidencias para la redacción de la memoria.
Entorno de ejecución: conda `qfs_env` (Python 3.12, scikit-learn, pandas, matplotlib).

## Estado inicial (2026-06-11)

- Fase 1 (`notebooks/fase1.ipynb`, 268 celdas): reconstruida con narrativa por dataset; ejecutada sin errores. Tests explicados (D'Agostino, Mann-Whitney/Cliff, Kruskal-Wallis/épsilon², chi-cuadrado/V de Cramér, FDR Benjamini-Hochberg). Sin texto dirigido al agente. Sin tablas con texto manual.
- Fase 2 (`fase2.ipynb`, 236 celdas): correcciones del checklist verificadas: 2.3 registra `olive_oil_3class`/`olive_oil_9class` desde la separación X/y; 2.5 trata la evidencia de Fase 1 como herencia con lectura Markdown ("Lectura de la Evidencia Heredada"); 2.9 selecciona variables por dimensionalidad en Madelon y lo justifica; 2.10 explica codificación target/leakage (fit solo con train). Pendiente: celda de funciones de 2.9 con 221 líneas (dividir).
- Fase 3 (`fase3.ipynb`, 210 celdas): parámetros (`MAX_SAMPLE_*`, `CHUNK_SIZE_DATASET`, `HIGH_CORRELATION_THRESHOLD=0.85`, `DIMENSIONALITY_RATIO_REFERENCE=0.20`) justificados en Markdown; 3.2 sustituye la tabla visible de categóricas pendientes por observación Markdown; 3.4-3.8 explican delta de proporciones, chi², Fisher, KS, Wasserstein, PSI, JS, Spearman, FDR, MI, VIF y Cramér's V. Sin comentarios para agente.
- Fase 4 (`fase4.ipynb`, 211 celdas): configuración justifica `MAX_SAMPLE_*` y umbrales de revisión (PSI/KS/Wasserstein, AUC/NMI=0.99); 4.5 y 4.6 con explicación e interpretación por dataset; usa las cinco formulaciones operativas (incluye `olive_oil_3class`/`olive_oil_9class`); conclusiones conectadas a Fase 5.
- Fase 5 (`fase5.ipynb`, 51 celdas): NO cumple el estándar. Es una capa de lectura sobre CSVs precalculados por `src/fase5_feature_selection.py` (`run_phase5`). Markdown con sangrado roto, sin secciones por dataset, muestra tablas con texto manual (`fs_method_configurations.decision`, `fs_phase6_input_recommendations.justificacion`, checklist y handoff narrativos), figuras escasas. Rehacer.
- Fase 6 (`fase6.ipynb`, 39 celdas): orquesta `run_phase6` (src/phase6_modeling/pipeline.py) y está ejecutada, pero con interpretación escasa, sin secciones por dataset y sin explicación de tests (bootstrap CI, comparaciones pareadas, permutation test). Mejorar narrativa.
- Fase 7 (`fase7.ipynb`, 452 celdas): plantilla de agente SIN ejecutar, con "Protocolo obligatorio para el agente" y `olive_oil` ambiguo. Rehacer por completo.
- LaTeX (`Plantilla_Latex_GCD/tfgs/`): borradores de resultados fases 1-5; fase 6 solo resumen de 11 líneas; sin fase 7; introducción/metodología/conclusiones mínimas. `pdflatex` no disponible en el sistema.
- Artefactos: `results/tables|figures|reports|logs/0{1..6}_*` completos (Fase 5: 68 tablas, Fase 6: 16 tablas + 8 figuras). `data/splits` y `data/selected_features` con las 5 formulaciones.
- CSVs de Fase 5 con columnas de texto manual (logs de decisión del agente): `fs_decision_log`, `fs_initial_audit`, `fs_risk_log`, `fs_phase5_handoff_to_phase6`, etc. No deben mostrarse como evidencia en el notebook.

## Trabajo realizado

### Fases 1-4 (verificación y reejecución)

- Verificado punto a punto el checklist de correcciones: todas estaban aplicadas (ver "Estado inicial").
- Fase 2.9: dividida la celda de funciones de 221 líneas en tres bloques (métricas IQR / selección representativa / visualización) con Markdown introductorio. `notebooks/fase2.ipynb` pasa de 236 a 241 celdas.
- Reejecutadas las cuatro fases desde kernel limpio (`jupyter nbconvert --execute`): 0 errores, 0 celdas sin ejecutar (~1 min total).

### Fase 5 (reconstrucción completa)

- `src/fase5_feature_selection.py`: `run_phase5` refactorizada en funciones de etapa invocables desde el notebook (`cargar_bundles`, `etapa_auditoria_entradas`, `etapa_protocolo`, `etapa_plan_k`, `etapa_muestreo`, `etapa_seleccion`, `etapa_estabilidad`, `etapa_permutaciones_target`, `etapa_redundancia_subconjuntos`, `etapa_cruce_eda`, `etapa_datasets_reducidos`, `etapa_perfiles_metodos`, `etapa_figuras`, `etapa_cierre`, `guardar_artefactos`). `run_phase5` las compone (compatible hacia atrás).
- Corregidos tres defectos reales del pipeline:
  1. `cruzar_con_eda` referenciaba tablas de fases 1-4 que ya no existen (los notebooks reconstruidos cambiaron los nombres) → recableado a `fase1_variables_revision_riesgos`, `fase3_correlaciones_altas`, `fase4_leakage_screening` (flags ≥0.99 o nombre sospechoso) y `fase4_drift_variables` (drift_flag), con mapeo `olive_oil`→ambas formulaciones.
  2. El emparejamiento de evidencia usaba solo el primer token del nombre (cobertura 0 o >1 sin sentido) → emparejamiento por prefijo más largo (respeta one-hot) y agregación de fuentes sin duplicados. Cobertura resultante: bcw 0.99, churn 0.05, madelon 0.55, olive 0.78-1.00.
  3. `construir_recomendaciones_fase6` fijaba k_referencia=8 para olive_oil (=p, selección trivial) → ahora exige reducción real: k_ref=5 para ambas formulaciones (10 en el resto). **Esto cambia las entradas principales de Fase 6 para olive_oil.**
  4. `fs_inherited_warnings` recableado a `fase4_resumen_para_fase5.csv` + `fase4_formulaciones_olive_oil.csv`.
- Figuras nuevas: `plot_stability_heatmap` (Jaccard dataset×método, revisada visualmente: Madelon mrmr/MI=0.11 destaca en rojo) y `plot_redundancy_delta` (dot plot con baseline 0; mRMR único método ≤0, revisada visualmente).
- `notebooks/fase5.ipynb` reconstruido desde cero (68 celdas, generador en `scripts/rebuild_fase5_notebook.py`): ejecuta las etapas reales (no lee CSVs precalculados), explica los 7 métodos, Jaccard/Kuncheva, permutaciones (p mínimo 1/21≈0.048), redundancia y cruce EDA; secciones por dataset en 5.5; parámetros justificados; sin tablas con texto manual; conexión explícita con QFS (mRMR↔QUBO, presupuesto k≈5-10).
- Ejecutado 2 veces desde kernel limpio; observaciones ajustadas a las cifras reales de esta ejecución (difieren en detalle del run del 7-jun por entorno): 105 ejecuciones sin fallos, ~22 s de selectores, 0 variables sospechosas, 168 comprobaciones de consistencia ok, 68 artefactos.
- Resultados clave para la memoria: Madelon con Jaccard 0.11 (mrmr/MI) y mediana p permutación 0.52-0.57 (señal univariante frágil); bcw delta redundancia +0.26..+0.32 en filtros univariantes; mRMR controla redundancia; parrilla principal Fase 6 = 4 métodos × {k=10 (bcw/churn/madelon), k=5 (olive×2)}.

### Fase 6 (reconstrucción completa)

- `src/phase6_modeling/pipeline.py`: dos correcciones reales:
  1. `audit_inputs` referenciaba tablas inexistentes de Fase 4 (`split_final_checklist.csv`, `split_to_modeling_warnings.csv`) → recableado a `fase4_resumen_para_fase5.csv` (estado derivado de solapes/leakage) y `fase4_drift_variables.csv` (drift_flag).
  2. **El baseline `all_features` entrenaba con `original_index` como predictora** (load_dataset_splits no la filtraba; Fase 5 sí). Corregido: se elimina de X en carga. También retirado `multi_class` deprecado de LogisticRegression.
- `notebooks/fase6.ipynb` reconstruido (42 celdas, generador `scripts/rebuild_fase6_notebook.py`): ejecuta el pipeline por secciones (auditoría de entradas → parrilla → validación → candidatos → test+bootstrap → contrastes → coste → confusión → importancias → guardado), explica macro-F1, bootstrap (400), permutation test de etiquetas (500, p mín 0.002) y contraste pareado por signos (2000); protocolo en Markdown (no tabla de texto); observaciones por dataset con cifras reales. Ejecutado desde kernel limpio sin errores (~2 min).
- Resultados clave (test): bcw `mrmr_approx_k10` 0.950 vs baseline 0.937 (30 vars); churn empate práctico 0.997/0.991; **madelon selección 0.843-0.850 vs baseline 0.613, IC pareado [0.17,0.30], p≈0.02 (única mejora significativa)**; olive_3class 1.000 con 5 vars; olive_9class 0.855 vs 0.839 (no concluyente, n_test=86). Los 15 candidatos pasan el permutation test (p=0.002). Figuras revisadas visualmente (intervalos test, confusión olive_9class: confusión concentrada en clases 2 y 5).

### Fase 7 (creada desde cero)

- La plantilla anterior (452 celdas "notebook agente", sin ejecutar, con `olive_oil` ambiguo) se sustituye por un notebook real de 48 celdas (generador `scripts/rebuild_fase7_notebook.py`) sobre el nuevo módulo `src/fase7_evidencia.py`.
- Secciones: inventario de 14 artefactos de fases 1-6 → tabla maestra de candidatos (test + IC + contrastes) → validación de completitud → comparación final con veredicto por dataset (criterio explícito: mejora solo si delta>0, IC pareado excluye 0 y p<0.05) → síntesis estabilidad-redundancia-rendimiento → mapa de evidencia por dataset (5 narrativas con citas a artefactos) → handoff QFS (`fase7_handoff_qfs.csv`: k de referencia, F1 a igualar, objetivo por dataset) → limitaciones → conclusiones del bloque.
- Figuras nuevas revisadas visualmente: `fase7_test_baseline_vs_seleccion.png` (5 paneles con IC), `fase7_panorama_validacion_delta.png`, `fase7_estabilidad_vs_rendimiento.png` (separa el régimen Madelon).
- Veredictos: madelon mejora_significativa; resto equivalente_dentro_del_ruido. Artefactos en `results/tables|figures/07_final_comparison/`.

### Redacción LaTeX (parte pre-cuántica)

- Capítulos redactados a mano en español académico impersonal (`Plantilla_Latex_GCD/tfgs/tex/`): `introduccion.tex` (contexto QFS/Rydberg, objetivos de la propuesta, estructura), `metodologia.tex` (datasets con tabla, separación Olive Oil 3/9, diseño en 7 fases, control de leakage, validación de splits, 7 selectores con Jaccard/Kuncheva/permutación/redundancia, protocolo de modelado y contrastes, reproducibilidad), `resultados.tex` (resultados por fase con 7 figuras y la tabla de comparación final; discusión), `conclusiones.tex` (5 conclusiones parciales + limitaciones + trabajo futuro QFS), `apendice.tex` (reproducibilidad y trazabilidad).
- `ejemplo-memoria.tex`: título real, autor Carlos Gómez Sáez, tutores Yolanda Vives Gilabert y José D. Martín Guerrero, convocatoria Julio 2026; resumen/abstract/resum reales (con `TODO_EVIDENCIA` para los resultados cuánticos futuros).
- `bib/bibliografia.bib`: añadidas 10 referencias (Guyon 2003/2004, Peng mRMR, Benjamini-Hochberg, Kuncheva, scikit-learn, Mücke QFS 2023, Henriet átomos neutros, Street BCW, Forina Olive Oil).
- Desacoplados los generadores automáticos: `fase5_feature_selection.py` y `pipeline.py` ya no escriben .tex dentro de la plantilla (solo en `results/reports/`), para que las reejecuciones no pisen la memoria.
- `tfg.cls`: eliminada la opción `[pdftex]` de graphicx (autodetección; compatible con pdflatex y tectonic).
- **Compilado con éxito** (`tectonic`, instalado en qfs_env; pdflatex del sistema no disponible): `ejemplo-memoria.pdf` (~37 págs), 10 citas resueltas, revisadas visualmente las páginas de resumen, selección, comparación final y discusión.

### Validación final y limpieza (2026-06-11)

- Reejecución completa Fase 1→7 desde kernel limpio: 0 errores, 0 celdas sin ejecutar, sin outputs de texto masivos (~4,5 min). Cifras de la comparación final idénticas a las citadas en notebooks y memoria.
- Recompilación final de la memoria tras la limpieza: OK.
- Limpieza ejecutada: `prompts_raw/` duplicado, `notebooks/results/` vacío, `__pycache__`, intermedios LaTeX, 6 .tex autogenerados huérfanos en la plantilla, 9 módulos src muertos (fase1_agent_utils, fase1_refined_workflow, fase1_narrative_helpers, fase2_preprocessing_workflow, fase3_postprocessing_audit, fase3_reporting, fase3_visualization, fase4_split_audit, fase5_notebook_builder) e informes de auditoría obsoletos de sesiones previas (todo `results/reports/01_raw_eda/`, restos en 02 y 05). `src/_DIRECTORY_SUMMARY.md` actualizado.
- Estado de cierre en `docs/tfg_prequantum_final_status.md`.

## 2026-06-13 — Pendiente acordado: sección de validación estadística en la memoria

Acordado con el autor elevar la disciplina anti-espurias a contenido de primera
clase en la memoria (hoy está operativamente descrita pero no reivindicada como
principio). Tres piezas, con marcadores TODO_VALIDACION_ESTADISTICA en los .tex:
1. Marco teórico: nueva 2.5 "Validación estadística y control de relaciones
   espurias" (FDR/benjamini1995, significancia vs tamaño de efecto, permutaciones
   como nulos empíricos, bootstrap/efron1979); la integración pasa a 2.6.
   Referencias canónicas opcionales verificadas: Mann-Whitney 1947, Kruskal-Wallis
   1952, Cliff 1993.
2. Metodología: párrafo marco al inicio de 4.5 con la regla transversal
   (contraste + corrección por multiplicidad + tamaño de efecto + nulo empírico).
3. Discusión: cierre conectando la disciplina con los dos hallazgos (FDR en
   Madelon, significancia-vs-efecto en Churn) y con la herencia al contrato
   cuántico.
Motivo: es el diferenciador metodológico del TFG y la respuesta anticipada a la
pregunta "¿cómo sabes que no es azar?"; distribuido en subsecciones no se ve.

## 2026-06-13 — Pulido de la memoria con las decisiones cerradas desde los papers

Aplicados a la memoria (compila 44 págs, 0 refs rotas):
1. 4.4.2: envolvente fijada en ~20 variables (validación del paper de referencia),
   parámetros de simulación heredados explícitos (10000 shots, 4 us, top 10%,
   100 inits MDS) y NUEVO párrafo del control de calidad por gap al óptimo
   exacto de Q(x;alfa) (computable por enumeración con n<=20), separando
   "optimiza bien su criterio" de "el criterio es predictivo".
2. 4.5.3: explicitado que las pareadas se calculan sobre predicciones por fila
   archivadas → incorporar el método cuántico no requiere reentrenar la
   referencia clásica.
3. 3.4 (estado del arte): la línea de trabajo valida contra el óptimo QUBO
   exacto (práctica adoptada por esta evaluación).
4. Cap. 6 (trabajo futuro): la QPU real como proyección justificada (el método
   de referencia es íntegramente en simulación; evaluar en simulador es fiel).
Pospuestos: actualización 7→9 fases (cuando existan fase8/9) y mención del gap
en la futura sección 2.5 de validación estadística (TODO_VALIDACION_ESTADISTICA).

## 2026-06-13 — Sección de validación estadística COMPLETADA en la memoria

Las tres piezas acordadas, redactadas y compiladas (44 págs, 0 refs rotas):
1. Nueva 2.5 "Validación estadística y control de relaciones espurias" (las 4
   salvaguardas: FDR, significancia vs tamaño de efecto, nulos por permutación,
   bootstrap; cierre conectando con el gap al óptimo exacto). Integración
   renumerada a 2.6.
2. Párrafo marco al inicio de 4.5 con la regla transversal anti-espurias.
3. Cierre de la Discusión (FDR-Madelon, efecto-Churn, herencia al contrato
   cuántico).
Referencias añadidas (canónicas verificadas): mann1947, kruskal1952, cliff1993.
Bib: 29 entradas. Marcadores TODO_VALIDACION_ESTADISTICA eliminados; chip de
tarea retirado.

## 2026-06-13 — Pulido Tier C de la memoria (camino a MH)
- Bib: eliminadas 4 entradas dummy de plantilla (einstein, latexcompanion,
  knuthwebsite, notsoshort); 25 entradas reales, ninguna dummy citada.
- Añadidos índice de figuras, índice de tablas y "Lista de acrónimos" (18 siglas:
  ANOVA, AUC, EDA, FDR, FSFS, KS, MC, MDS, MI, mRMR, MWIS, PSI, QFS, QUBO, RFE,
  RRFS, SHAP, SVM). Compila a 52 págs, 0 errores, 0 refs rotas.
- Pendiente Tier C: agradecimientos personales (TODO_PERSONAL, los escribe Carlos).

## 2026-06-13 — M2 fase 7: lógica adaptada + corrección de multiplicidad (trabajo autónomo)
Estado: lógica de src/fase7_evidencia.py COMPLETA y verificada EN AISLADO contra
los artefactos reales de fases 5/6 re-ejecutadas. Notebook fase7 AÚN NO regenerado.

Cambios en src/fase7_evidencia.py:
1. Corrección por multiplicidad (nueva func corregir_multiplicidad): FDR
   (Benjamini-Hochberg) + Holm sobre la familia de contrastes pareados
   candidato-vs-baseline. Columnas paired_pvalue_fdr / paired_pvalue_holm en la
   tabla maestra; veredicto usa el p corregido (FDR).
2. Umbral de efecto práctico: UMBRAL_EFECTO_PRACTICO = 0.01. Una diferencia
   significativa pero < 0.01 de macro-F1 -> "empate_practico" (significancia !=
   relevancia, coherente con sec. 2.5). DECISIÓN A REVISAR POR CARLOS (valor del
   umbral y etiqueta).
3. Adaptación de esquema al nuevo fase 6: fase6_comparaciones ahora usa
   difference_macro_f1 y sign_permutation_p_value (renombrados internamente);
   intervalos filtran split==test; handoff: k_referencia pasa a dict documentado
   (10/10/10/5/5) porque fs_phase6_input_recommendations.csv ya no existe.
4. Generador rebuild_fase7_notebook.py: referencias de columna actualizadas a
   p_valor_pareado_{crudo,fdr,holm}.

VEREDICTOS RESULTANTES (verificados): madelon mejora_significativa (delta +0.280,
FDR 0.0012, Holm 0.005 — sobrevive a todo); customer_churn empate_practico
(delta +0.006 significativo por n=66k pero por debajo del umbral, RESTAURA la
lectura que ya tenía la memoria); bcw / olive_3 / olive_9 equivalente.

HALLAZGO para Carlos: el sign-permutation p-value de churn pasó de ~0.89 (corrida
vieja) a 0.0005 (nueva) — NO es bug: con n=66k cualquier ventaja consistente
mínima es significativa; es justo el caso significancia-vs-efecto. Por eso el
umbral de efecto es necesario.

PENDIENTE de M2: regenerar+ejecutar notebooks/fase7.ipynb, limpieza anti-meta del
generador (quitar inventario/completitud del cuerpo -> verify_fase7), figuras
viz-definitive, verificación a-o. NO se ha re-ejecutado el notebook todavía:
no se han "publicado" conclusiones nuevas, solo validado la lógica en aislado.

## 2026-06-13 — HALLAZGO MAYOR (revisar memoria): la inestabilidad de mRMR era un artefacto del estimador
Al re-ejecutar con MI discretizada (determinista) en vez de k-NN (estocástico),
mrmr_approx y mutual_info en madelon pasan de Jaccard ~0.11 (inestables, corrida
vieja) a Jaccard = 1.000 (estables). Causa: el estimador k-NN dependía de la
semilla; la MI discretizada es determinista, así que mRMR deja de "cambiar de
subconjunto con la semilla". 
IMPLICACIÓN CRÍTICA: la narrativa "QFS llena el hueco de la inestabilidad de mRMR
en alta dimensión" YA NO SE SOSTIENE con el estimador correcto. Aparece en:
memoria sec. 5.2/Discusión/Conclusiones, y en marco/estado como motivación de QFS.
La motivación de QFS debe reorientarse: NO a estabilidad (los clásicos ahora son
estables, Jaccard 1.0 salvo random_forest 0.78 y Boruta sin medida), SINO a
(a) control de redundancia -mrmr_approx es el ÚNICO con delta_redundancia<0
(-0.012) en madelon; el resto la aumenta- y (b) compacidad (igualar al mejor con
menos variables). 
Números nuevos madelon (sintesis): mejor_delta_val boruta 0.303, rfe 0.283,
linear_svm 0.273, random_forest 0.240 (jaccard 0.78), f_classif 0.233, mrmr 0.110.
label_permutation_p = 0.002 (mínimo) para todos -> nada compatible con azar.
PENDIENTE para Carlos: aprobar la reorientación de la motivación de QFS en la
memoria (de "estabilidad" a "redundancia+compacidad"). NO tocada la memoria aún.

## 2026-06-13 — Fase 7 COMPLETA y verificada (OVERALL PASS)
Notebook regenerado (57 celdas, 21 code, 0 errores) + verify_fase7_notebook.py creado.
- Anti-meta: inventario (7.1) y completitud (7.3) sacados del cuerpo -> verify;
  renumeración 7.1 maestra, 7.2 comparación, 7.3 síntesis, 7.4 mapa, 7.5 referencia
  QFS, 7.6 limitaciones, 7.7 conclusiones. Sin big-bang, sin vocabulario pipeline.
- Multiplicidad: tabla maestra y comparación con p crudo + FDR + Holm; veredicto
  por FDR + umbral de efecto. Verificado.
- Figuras (3 principales + 5 fichas, PNG+PDF, calidad memoria):
  * test_baseline_vs_seleccion: anotación madelon ahora data-driven (+0.280).
  * estabilidad_vs_rendimiento: REDISEÑADA a 2 paneles (panel A estabilidad
    uniforme; panel B redundancia vs rendimiento, mRMR único que reduce
    redundancia en madelon). Cuenta el hallazgo del artefacto.
  * panorama_validacion: anotación de rango data-driven.
- Determinismo confirmado: test macro-F1 de fase 7 == fase 6 (check o).
- Limpieza: removidas de ARTEFACTOS_REQUERIDOS dos entradas muertas
  (fase5_recomendaciones, fase6_importancias) que ya no genera la fase 5/6.
Veredictos finales: madelon mejora_significativa (+0.280, FDR 0.001); churn
empate_practico; bcw/olive3/olive9 equivalente. label-perm p=0.002 en todos.

## 2026-06-13 — M3: memoria actualizada con resultados definitivos (sin narrar el camino)
Por indicación del autor, la memoria NO menciona el estimador k-NN previo ni "lo
que salió mal": presenta la MI discretizada como la metodología y la motivación de
QFS como redundancia+compacidad, sin changelog.
Cambios en la memoria LaTeX (compila 52 págs, 0 errores, 0 refs rotas):
- 5.2.1: estabilidad uniforme (Jaccard min 0.76); separación frente al azar
  p=0.048 en los cinco; redundancia con mRMR único que la reduce (hasta -0.27).
- 5.2.2: tabla de comparación final reescrita (bcw Boruta 22/0.950; churn mRMR
  empate práctico; madelon Boruta 19/0.893 +0.280 FDR 0.001/Holm 0.005; olive3
  SVM 5/1.000; olive9 Boruta 8/0.839); parrilla 195 experimentos; multiplicidad.
- 5.2.3: figura estabilidad->2 paneles (estabilidad uniforme + redundancia
  diferenciador); narrativa reorientada.
- Discusión y Conclusiones: motivación de QFS reorientada de estabilidad a
  redundancia/compacidad; +0.280; sin "inestabilidad de mRMR".
- Abstracts (es/en/val): +0.280 y "doce selectores".
- Apéndice: 195 experimentos.
- Figuras refrescadas en figs/ desde results/ (fs_stability/permutation/redundancy
  + fase7 test y estabilidad_vs_rendimiento rediseñada).
Verificado: 0 rastros de "0.237", "Jaccard 0.11", "k-NN", "75 experimentos",
"siete selectores".
