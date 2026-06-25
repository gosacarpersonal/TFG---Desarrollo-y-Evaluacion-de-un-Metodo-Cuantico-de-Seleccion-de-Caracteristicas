# Delta de cierre para la memoria `.tex`

Fecha: 2026-06-15. Este documento **no edita** la memoria: deja la lista exacta de cambios para cerrar el TFG con los resultados canónicos 100×100.

Fuentes canónicas: `results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv`, `qfs_quality_control_*.csv`, `qfs_embedding_error.csv`, `docs/auditoria/hallazgos_fase10.md`, `docs/auditoria/revision_independiente_postrerun.md`.

## Cambios obligatorios

| Archivo/línea actual | Acción exacta | Sustituir/insertar | Fuente |
|---|---|---|---|
| `Plantilla_Latex_GCD/tfgs/tex/resultados.tex:409-426`, tabla `tab:qfs-control` | Actualizar filas y ampliar lectura del control. | Usar valores canónicos a beta elegido: Madelon Hamming `4`, Δcoste `-0.059`; Customer Churn Hamming `6`, Δcoste `+0.622`. Añadir si cabe BCW `6`, `-1.270`; Olive3 `2`, `-0.165`; Olive9 `4`, `+0.903`, o aclarar que la tabla resume protagonistas. | `results/tables/08_quantum/qfs_quality_control_*.csv`; `docs/auditoria/hallazgos_fase10.md#b9`. |
| `resultados.tex:439-447` | Reescribir interpretación. | Cambiar “Madelon Δ≈-0.010” por “Madelon Δ=-0.059, coste NA no peor que el oráculo a α=0.5; el fallo sigue siendo de criterio porque el oráculo macro-F1=0.643 queda lejos del baseline 0.813”. Cambiar “Churn Δ=+1.323” por “Churn Δ=+0.622 y pérdida macro-F1 total 0.030; déficit de optimizador leve”. Eliminar la frase que liga Churn a relajación geométrica como causa. | `qfs_quality_control_*`; `comparacion_qfs_configuraciones_vs_baseline.csv`; `qfs_embedding_error.csv`. |
| `resultados.tex:460-479`, tabla `tab:qfs-comparacion` | Actualizar cifras QFS canónicas. | Breast Cancer W.: baseline `0.937`, QFS-NA `0.937`, QFS-oráculo `0.937`, equivalente. Customer Churn: `1.000`, `0.969`, `0.999`, deterioro. Madelon: `0.813`, `0.603`, `0.643`, deterioro. Olive3: `1.000`, `1.000`, `1.000`, equivalente. Olive9: `0.839`, `0.842`, `0.906`, equivalente/inconcluso por n=86. | `results/tables/08_quantum/comparacion_qfs_configuraciones_vs_baseline.csv`. |
| `resultados.tex:518-533` | Reescribir diagnóstico criterio ↔ optimizador. | Sustituir la simetría implícita por: “Madelon: criterio grande, baseline 0.813 → oráculo 0.643 → QFS-NA 0.603; pérdidas criterio `0.170`, optimizador `0.040`, total `0.210`. Churn: criterio casi nulo `0.001`, optimizador `0.030`, total `0.030`; no es fallo de magnitud comparable”. | Figura `diag_atribucion_qfs.png`; `hallazgos_fase10.md#c`. |
| `resultados.tex:380-387` y `conclusiones.tex:65-70` | Matizar geometría. | Mantener que se probó `dist_ratio` `0.45/0.35/0.25`, pero decir que en los beta elegidos canónicos todos aceptan `0.45`. Añadir: error MDS Churn `0.217`, menor que BCW `0.231` y Madelon `0.250`; por tanto la hipótesis one-hot/geometría queda refutada como causa demostrada. | `results/tables/08_quantum/qfs_embedding_error.csv`; `results/tables/10_memoria_b9_embedding_error.csv`. |
| `conclusiones.tex:84-88` | Ajustar trabajo futuro. | Cambiar “fallo del simulador + necesidad de relajar geometría” por “déficit leve de optimizador en Churn, no explicado por el error MDS; futura ablación dirigida de encoding/drop-first o multi-seed QFS si se quiere aislar el mecanismo fino”. | `revision_independiente_postrerun.md`, gates G-b/G-c. |

## Inserciones de estructura

| Ubicación recomendada | Inserción | Contenido mínimo |
|---|---|---|
| Inicio del capítulo de resultados, antes de selección clásica o como `\subsection{Regímenes del banco}` en 5.1 | Nueva subsección “Regímenes como predictores”. | Usar `f10_a_regimenes_dataset.png`. Lectura: BCW señal fuerte + VIF 3806/23 vars; Churn VIF 1.1 y baseline saturable; Madelon FDR 13/500, efecto 0.02, PCA80=295; Olive3 separable; Olive9 n_test=86. Cerrar con “el régimen predice el cuello de botella”. |
| Después de comparar QFS con baseline, cerca de `fig:criterio-optimizador` | Subsection “Diagnóstico criterio frente a optimizador”. | Usar `diag_atribucion_qfs.png` como clímax. Explicitar que la simetría de dos fallos iguales es falsa: Madelon total `0.210`; Churn total `0.030`. |
| Tras el diagnóstico QFS o en Discusión | Subsection “Consistencia y robustez”. | Usar `f10_b10_consistencia.png`. Decir: selección con 3 semillas; filtros/MI Jaccard mínimo `1.00`; RF baja a Madelon `0.88`, Olive9 `0.78`; variación benigna entre sustitutos (`feat_28↔48`, `subscription_Basic↔Standard`, `palmitoleic↔stearic`). Modelado/QFS no tienen multi-seed fuerte: robustez por 400 bootstraps, 2000 sign-perms, label-perm p_min `0.002`, 100 MDS. |
| Apéndice `Plantilla_Latex_GCD/tfgs/tex/apendice.tex:18-25` | Actualizar fases reproducibles de 1--9 a 1--10. | Añadir que fase10 no reentrena ni reejecuta QFS: lee artefactos canónicos y produce visualizaciones/hallazgos de cierre. |
| Apéndice tras `apendice.tex:116-122` | Añadir figuras complementarias fase10. | Incluir `f10_b2_jaccard_12_metodos.png`, `f10_b9_atomos_mds_error.png`, `f10_b10_consistencia.png` y opcionalmente `f10_b7_macro_f1_auc.png`. |

## Figuras listas para citar

- `Plantilla_Latex_GCD/tfgs/figs/f10_a_regimenes_dataset.png`: cuerpo, antes del veredicto QFS.
- `Plantilla_Latex_GCD/tfgs/figs/explor_mapa_metodos.png` y `f10_b2_jaccard_12_metodos.png`: posición en métodos.
- `Plantilla_Latex_GCD/tfgs/figs/f10_b3_trayectoria_k.png`: trayectoria k.
- `Plantilla_Latex_GCD/tfgs/figs/f10_b4_escalera_alpha.png`: fidelidad Mücke/α.
- `Plantilla_Latex_GCD/tfgs/figs/f10_b5_beta_geometria.png`: β reordena densidades.
- `Plantilla_Latex_GCD/tfgs/figs/f10_b9_atomos_mds_error.png`: geometría refutada para Churn.
- `Plantilla_Latex_GCD/tfgs/figs/f10_b10_consistencia.png`: nueva consistencia.
- `Plantilla_Latex_GCD/tfgs/figs/diag_atribucion_qfs.png`: clímax criterio↔optimizador.
- `Plantilla_Latex_GCD/tfgs/figs/f6_shap_beeswarm_bcw.png`: coherencia SHAP variable-level.

## Texto de cierre recomendado

La memoria debe cerrar con esta lectura: la referencia clásica no solo compara, sino que **predice por régimen** y **atribuye por mecanismo**. Madelon no falla por hardware: falla porque la MI de pares no ve la señal que el modelo sí usa. Churn no es otro fallo grande: es un déficit leve de optimizador cerca de techo, sin evidencia de que la geometría MDS sea la causa. BCW y Olive3 son equivalentes; Olive9 queda inconcluso por tamaño de test.

## Decisiones restantes

1. `n_init`: mantener `n_init=1` documentado como interpretación literal del paper (“100 independent MDS runs”) o volver a default `_OG`. Recomendación: mantener `1` y declararlo.
2. Consistencia multi-seed fuerte: no existe para modelado/QFS sin experimento nuevo. Recomendación: declarar robustez por bootstrap/permutación/100 MDS y dejar multi-seed como trabajo futuro opcional.
