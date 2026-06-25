# Auditoría visual de figuras de memoria

Fecha: 2026-06-15.

Nota metodológica: el verificador técnico comprueba existencia, DPI, copias y
procedencia de fuentes declaradas; no juzga composición. La aceptación visual se
hizo abriendo los PNG renderizados y mirando también páginas del PDF compilado
contra la checklist: composición/espacios, legibilidad a tamaño PDF, jerarquía
narrativa, corrección científica y coincidencia con la especificación. Un script
no puede juzgar si una figura respira bien en página; esa inspección la hizo
Codex mirando las imágenes.

| Figura | Iteraciones visuales | Correcciones de espacios/composición | Captura final aceptada |
|---|---:|---|---|
| F9 atribución QFS | 1 | Sustituida por el plano de atribución en macro-F1: Madelon queda limitado por criterio y Customer Churn por optimizador simulado. | `results/figures/10_memoria/diag_atribucion_qfs.png` |
| F4 perfil selectores | 3 | Panel D compactado a métodos con contraste de permutación disponible; colorbar con base cero; retirada de hueco artificial; leyenda única de familia conservada. | `results/figures/10_memoria/f4_perfil_selectores.png` |
| O1 organismo de selección | 1 | Subida al cuerpo para hacer visible la profundidad clásica: doce selectores recorriendo las 500 variables de Madelon y separando consenso de distractores. | `results/figures/10_memoria/o1_organismo_seleccion.png` |
| F2 señal FDR efecto | 1 | Primer render aceptado: dos paneles legibles, Madelon destacado, etiquetas k/total sin recortes. | `results/figures/10_memoria/f2_senal_fdr_efecto.png` |
| F3 base confiable | 2 | Se corrigió la clave de Olive para que las dos formulaciones no quedasen en blanco; tres roles no redundantes y escala Spearman legible. | `results/figures/10_memoria/f3_base_confiable.png` |
| F5 madurez de selección | 4 | Sustituida la lectura endpoint por trayectoria de redundancia vs k; small multiples por dataset; contexto gris + mRMR protagonista; retirada de anotación que pisaba ticks en Madelon. | `results/figures/10_memoria/f5_coste_rendimiento.png` |
| F6 SHAP cinco datasets | 2 | Beeswarm por instancia para Breast Cancer, Customer Churn y Madelon; barras de importancia SHAP media para las formulaciones multiclase de Olive. | `results/figures/10_memoria/f6_shap_variables.png` |
| F7 significancia magnitud | 3 | Leyenda movida y finalmente eliminada del área de datos; codificación gris/azul pasada al subtítulo para no tapar IC. | `results/figures/10_memoria/f7_significancia_magnitud.png` |
| F8 alpha/beta QFS | 2 | Pasó de dos heatmaps a EV1+EV2: alpha cardinalidad/coste y beta rendimiento/densidad; wspace/hspace ajustados y colorbar estrecha. | `results/figures/10_memoria/f8_qfs_alpha_beta.png` |
| F10 QFS vs clásico | 2 | Se añadieron IC bootstrap del delta frente a baseline; leyenda inferior sin solapes; inspección PDF confirmó legibilidad embebida. | `results/figures/10_memoria/f10_qfs_vs_clasico.png` |
| F1 banco | 3 | Fuente cambiada a cinco formulaciones reales de fase 4; offsets de Olive 3/Olive 9 y Customer Churn; colores de dataset restaurados. | `results/figures/10_memoria/f1_banco.png` |
| EV5 dinámica adiabática | 1 | Nueva figura de metodología; curvas Omega/Delta con línea de cambio de paso; width LaTeX ajustado a 0.86 para mantener caption y sección siguiente en página. | `results/figures/10_memoria/ev5_evolucion_adiabatica.png` |
| EV6 rendimiento vs k | 2 | Nuevo re-modelado dirigido; small multiples por dataset con baseline gris, mRMR azul y QFS-NA rojo; se corrigió la colocación LaTeX con `\clearpage` para evitar flotantes fuera de orden. | `results/figures/10_memoria/ev6_rendimiento_vs_k.png` |
| A1 permutación | 1 | Primer render aceptado como apoyo: heatmap compacto con valores visibles. | `results/figures/10_memoria/a1_permutacion_senal_nulo.png` |
| A2 leakage | 1 | Primer render aceptado: umbrales 0.99 visibles y puntos dentro de márgenes. | `results/figures/10_memoria/a2_leakage.png` |
| A3 roster | 1 | Primer render aceptado: heatmap de roster legible en apéndice. | `results/figures/10_memoria/a3_roster_completo.png` |
| A4 SHAP por clase | 2 | Sustituido resumen genérico por SHAP real por clase para Olive 3 y Olive 9; rotación de etiquetas y colorbar revisados. | `results/figures/10_memoria/a4_shap_concordancia.png` |
| A5 panorama deltas | 1 | Primer render aceptado: divergente centrado en cero, valores visibles. | `results/figures/10_memoria/a5_panorama_deltas.png` |
| A6 handoff I/R | 1 | Primer render aceptado: dos paneles con ejes claros y sin solapes. | `results/figures/10_memoria/a6_handoff_ir.png` |
| A7 coste cuántico | 1 | Primer render aceptado: barras horizontales de tiempo legibles. | `results/figures/10_memoria/a7_coste_cuantico.png` |
| A8 solape QFS | 2 | Sustituida figura de materialización por Jaccard real QFS-NA vs mRMR/Boruta; heatmap y colorbar inspeccionados en apéndice. | `results/figures/10_memoria/a8_solape_qfs_clasicos.png` |
| A9 macro-F1/AUC binarios | 3 | Primer scatter tenía etiquetas superpuestas; se reemplazaron rótulos por forma de marcador + leyenda; ejes recortados para el rango real. | `results/figures/10_memoria/a9_macro_f1_auc_binarios.png` |

Verificación técnica ejecutada:

```text
VERIFY memoria figuras: OK
- Figuras comprobadas: 23 en results/figures/10_memoria, incluidas la F9 narrativa
  `diag_atribucion_qfs.png` y O1 `o1_organismo_seleccion.png`
- Copias comprobadas: 23 PNG en Plantilla_Latex_GCD/tfgs/figs
- DPI: todos los PNG >= 300
- Procedencia: todas las fuentes declaradas existen
```

Verificación embebida en PDF: se compiló
`Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf` con Tectonic y se
renderizaron/abrieron páginas de metodología, resultados y apéndice
(incluidas 35, 47--51, 58--59). EV5, F8, F9, F10, EV6, A8 y A9 quedan
dentro de márgenes, con captions visibles y sin recortes. La compilación
termina con código 0; tras sustituir guiones largos Unicode, no quedan
avisos de caracteres no representables, solo warnings tipográficos de
underfull/overfull e inconsistencia de rerun de bibliografía.
