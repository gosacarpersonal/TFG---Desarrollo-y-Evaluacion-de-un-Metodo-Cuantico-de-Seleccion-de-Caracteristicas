# Cierre de memoria: reescritura granular

Fecha: 2026-06-15. Objetivo: convertir la memoria `.tex` en el relato completo del proceso, no en un parche de tablas. Se siguió `docs/estilo_redaccion_tfg.md` y se usaron como fuentes de verdad `analisis_multidimensional_qfs.md`, `revision_independiente_postrerun.md`, `sintesis_hallazgos_vs_qfs.md`, `hallazgos_fase10.md` y los artefactos canónicos de `results/tables/`.

## Secciones reescritas o expandidas

| Archivo | Sección | Qué quedó plasmado |
|---|---|---|
| `Plantilla_Latex_GCD/tfgs/ejemplo-memoria.tex` | Resumen/Abstract/Resum | Se actualizó la tesis: referencia clásica como instrumento para predecir por régimen y atribuir por mecanismo. Se incluyeron cifras canónicas: Madelon `0.603` vs `0.813`, Churn `0.969` vs `1.000`, y refutación geométrica de Churn. |
| `tex/introduccion.tex` | Motivación, objetivos y estructura | Se reformuló el objetivo para enfatizar proceso, régimen, mecanismo y atribución criterio--optimizador. Se declaró que la memoria no busca un podio, sino una lectura variable a variable. |
| `tex/estado_arte.tex` | Hueco de investigación | Se amplió la laguna: no basta evaluar QFS contra un baseline; hace falta separar régimen del dato, familia de selector y mecanismo de fallo. |
| `tex/metodologia.tex` | Datos | Se añadió la razón de cada dataset como régimen experimental: BCW redundante, Churn continuo + categórico nominal, Madelon alta dimensión/interacciones, Olive composicional/multiclase. |
| `tex/metodologia.tex` | Olive/Churn | Se declaró el one-hot de Churn como decisión metodológica defendible y divergencia frente al paper, sin afirmarlo como causa. |
| `tex/metodologia.tex` | Métodos clásicos | Se reforzó la idea de los 12 métodos como sistema de coordenadas relevancia--redundancia para situar QFS. |
| `tex/metodologia.tex` | QFS | Se documentó el MDS verificado del solver: 100 inicializaciones independientes, `n_init=1`, 10 000 shots, y guardado del error de embebido. |
| `tex/metodologia.tex` | Diseño experimental | Se pasó de nueve a diez fases, añadiendo fase10 como síntesis visual/auditoría sin reejecutar fases previas. |
| `tex/resultados.tex` | Nueva subsección `Regímenes del banco como predictores` | Se incorporaron FDR, efecto, VIF, PCA, drift, adversarial y leakage como predictores del cuello de botella, con variables concretas: `concave_points_worst`, `radius_worst`, `support_calls`, `payment_delay`, `feat_241`, ácidos de Olive. |
| `tex/resultados.tex` | Nueva subsección `El espacio de métodos como espejo de QFS` | Se añadieron las figuras `explor_mapa_metodos` y `f10_b2_jaccard_12_metodos`. Se explica que QFS es clase-mRMR salvo Churn, donde selecciona grupos one-hot y deja fuera continuas relevantes. |
| `tex/resultados.tex` | Modelado/SHAP | Se añadió dependencia del modelo en Madelon: mejora cercana a `+0.28` con modelos más sensibles a distractores y `+0.094` con XGBoost. Se incluyó que SHAP usa `feat_336`, `feat_105`, `feat_153`, frente a la MI que rankea `feat_241`. |
| `tex/resultados.tex` | Tablas QFS | Se actualizaron `tab:qfs-control` y `tab:qfs-comparacion` con cifras canónicas 100x100. Churn pasa a `0.969`; BCW a `0.937`; Madelon a `0.603`. |
| `tex/resultados.tex` | k/alpha/beta | Se añadió la lectura de la escalera alpha como orden de entrada: Churn introduce continuas antes que dummies; Madelon permanece plano hasta alpha alto. Beta reordena densidades pero no explica Churn. |
| `tex/resultados.tex` | Átomos/MDS | Se incorporó `f10_b9_atomos_mds_error.png` y la refutación geométrica: Churn error `0.217`, mejor que BCW `0.231` y Madelon `0.250`. |
| `tex/resultados.tex` | Nueva sección `Diagnóstico criterio--optimizador` | Se convirtió el plano de atribución en clímax de la tesis: Madelon criterio grande `0.170`/total `0.210`; Churn optimizador leve `0.030`, sin geometría demostrada. |
| `tex/resultados.tex` | Nueva sección `Consistencia, pruebas y discusión` | Se integraron p_min selección `0.048`, label-perm `0.002`, bootstrap `400`, sign-perms `2000`, estabilidad Jaccard y sustitutos equivalentes (`feat_28/48`, dummies Churn, `palmitoleic/stearic`). |
| `tex/conclusiones.tex` | Conclusiones completas | Se sustituyó la lista breve por un cierre narrativo: referencia clásica, regímenes, espacio de métodos, QFS canónico, atribución y consistencia. |
| `tex/conclusiones.tex` | Trabajo futuro | Se reorientó a: criterio/HUBO para Madelon; readout/optimización en baja redundancia para Churn; ablación encoding; consistencia multi-seed; hardware real. |
| `tex/apendice.tex` | Reproducibilidad y figuras | Se actualizó de fases 1--9 a 1--10 y se añadieron figuras fase10: Jaccard QFS vs 12, embebido MDS y consistencia. |

## Verificaciones realizadas

- Compilación ejecutada con `conda run -n qfs_env tectonic ejemplo-memoria.tex`.
- Resultado: PDF escrito correctamente en `Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf`.
- Quedan avisos tipográficos de `Overfull/Underfull hbox/vbox`, sin errores de compilación.
- Búsqueda de cifras obsoletas de 4 corridas: no quedan `0.922`, `0.633`, `1.323` ni `-0.010` en la memoria como resultados vigentes.
- La memoria usa las cifras canónicas: Churn `0.969`, BCW `0.937`, Madelon `0.603`; Churn error MDS `0.217`, BCW `0.231`, Madelon `0.250`.

## Lectura final plasmada

La memoria queda cerrada alrededor de una tesis única: el bloque clásico permite **predecir** el cuello de botella por régimen y el control QFS permite **atribuir** el resultado por mecanismo. Madelon es fallo grande de criterio porque la MI por pares no ve la señal de interacción. Churn es déficit leve de optimizador/readout cerca de techo, no fallo geométrico demostrado. BCW y Olive3 no muestran fallo atribuible. Olive9 queda inconcluso por tamaño de prueba.
