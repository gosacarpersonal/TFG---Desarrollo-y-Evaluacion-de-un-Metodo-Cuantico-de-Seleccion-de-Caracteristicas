# Decisión Fase 4: formulaciones de Olive Oil

La revisión de Fase 1, Fase 2 y Fase 3 confirma que `olive_oil` contiene dos formulaciones supervisadas distintas: `Area` con 3 clases y `Region/target` con 9 clases.

Por tanto, Fase 4 no trata `olive_oil` como un único dataset operativo. Se crean dos variantes trazables:

| formulacion | target | n_clases | columnas_excluidas_de_X | evidencia | decision | justificacion |
| --- | --- | --- | --- | --- | --- | --- |
| olive_oil_3class | area | 3 | target;palmitic | data/01_raw/olive_oil.csv contiene Area con 3 clases; processed conserva area | usar como variante separada | Permite auditar la tarea macro-región sin que la región de 9 clases ni su código proxy entren en X. |
| olive_oil_9class | target | 9 | area;palmitic | Fases 1-3 tratan olive_oil como multiclase de 9 regiones; Area/palmitic son proxies | usar como variante separada | Mantiene la formulación usada hasta Fase 3, pero excluye la macro-región y el código perfecto de región. |

Regla de leakage: para la tarea de 3 clases se excluyen la región de 9 clases y su código proxy; para la tarea de 9 clases se excluyen la macro-región de 3 clases y el código proxy. Las fases posteriores deben cargar `olive_oil_3class` y `olive_oil_9class`, no `olive_oil` ambiguo.