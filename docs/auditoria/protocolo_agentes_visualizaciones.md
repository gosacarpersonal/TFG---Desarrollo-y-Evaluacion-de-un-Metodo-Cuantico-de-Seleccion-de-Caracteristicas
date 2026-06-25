# Protocolo para agentes — visualizaciones del TFG QFS

> Objetivo: impedir que un agente reduzca el TFG a rankings, medias o figuras
> bonitas. Cada visualizacion debe defender una parte del camino experimental:
> datos fiables -> seleccion caracterizada -> modelos evaluados -> QFS
> diagnosticado -> comparacion final.

## 1. Diagnostico del problema

El riesgo actual no es la ausencia de artefactos. El repositorio contiene una
capa extensa de tablas, figuras, notebooks y documentos de auditoria. El riesgo
es que un agente entre por una figura concreta, acepte una narrativa previa como
verdad absoluta y haga cambios locales sin reconstruir el argumento completo.

Por tanto, la unidad de trabajo no es "hacer una grafica", sino responder:

| Pregunta | Evidencia primaria | Salida visual esperada |
|---|---|---|
| Que tipo de problema es cada dataset? | `results/tables/01_raw_eda/`, `04_split_audit/` | Banco, desbalance, dimensionalidad, regimenes |
| La base experimental esta limpia? | `03_postprocessing_audit/`, `04_split_audit/` | Drift, leakage, adversarial validation, conservacion |
| Que hacen los selectores clasicos? | `05_feature_selection/` | Roster, estabilidad, redundancia, coste, permutacion |
| Que ocurre al entrenar modelos? | `06_modeling/`, `07_final_comparison/` | Curvas por `k`, IC, deltas, efecto practico, SHAP |
| Que hace QFS por dentro? | `08_quantum/` | `alpha`, `beta`, densidades, oraculo, coste, Hamming |
| Si QFS falla, por que falla? | `comparacion_qfs_configuraciones_vs_baseline.csv`, `qfs_quality_control_*.csv` | Descomposicion criterio frente a optimizador |
| Que conclusion resiste? | `.tex`, tablas finales y figuras F1--F10 | Comparacion clasico--cuantica por regimen, no ranking plano |

## 2. Reglas no negociables

1. **No aceptar planes antiguos como autoridad.** Los `.md` de `docs/auditoria/`
   orientan, pero no prueban. La prueba esta en codigo, CSV, notebooks, figuras y
   LaTeX.
2. **No reducir a medias.** Una media solo puede cerrar un argumento si antes se
   ha mostrado variacion por dataset, `k`, selector, modelo, metrica o parametros
   cuando esos ejes existen.
3. **Figura = pregunta de defensa.** Si una figura no responde una pregunta que
   podria aparecer en tribunal, va a apendice o se elimina.
4. **Granularidad antes que resumen.** Toda figura resumen debe tener una figura,
   tabla o notebook que conserve la granularidad que la justifica.
5. **QFS no es solo resultado final.** Hay que separar criterio, oraculo exacto,
   simulador neutral-atom, `alpha`, `beta`, geometria y rendimiento.
6. **La referencia clasica no es preparacion.** Es la condicion de posibilidad
   para diagnosticar QFS; debe verse como construccion experimental auditada.
7. **Toda afirmacion debe tener fuente.** Si el texto dice "Madelon falla por
   criterio" o "Churn por optimizador", debe apuntar a F9, tabla de control y CSV.

## 3. Procedimiento obligatorio antes de editar

1. Leer `AGENTS.md` y este protocolo.
2. Leer la seccion relevante de:
   - `docs/auditoria/estrategia_visual_memoria.md`
   - `docs/auditoria/especificacion_figuras_memoria.md`
   - `Plantilla_Latex_GCD/tfgs/tex/resultados.tex`
3. Localizar las fuentes primarias de la figura o tabla:
   - declaraciones en `scripts/build_memoria_figuras.py` (`FIGURE_FILES` y
     `SOURCES`);
   - CSVs de `results/tables/`;
   - artefactos en `results/figures/` y copias en `Plantilla_Latex_GCD/tfgs/figs/`.
4. Formular por escrito, en el commit o respuesta final:
   - pregunta que responde;
   - evidencia usada;
   - que eje de granularidad conserva;
   - que resumen produce;
   - donde aparece en la memoria.

Si no se puede completar este mini-informe, no se debe tocar la figura.

## 4. Mapa experimental minimo que el agente debe tener en mente

Estado inspeccionado el 2026-06-16:

| Capa | Evidencia observada |
|---|---|
| Datasets | 5 formulaciones: `breast_cancer_wisconsin`, `customer_churn`, `madelon`, `olive_oil_3class`, `olive_oil_9class` |
| Seleccion clasica | 12 metodos en `fs_all_selected_features.csv` / `fs_all_rankings.csv`; 116334 filas de rankings; 9267 filas de features seleccionadas |
| Estabilidad | `fs_jaccard_stability.csv` con 735 comparaciones |
| Modelado | 260 CSVs de validacion en `results/tables/06_modeling/experiments_validation/` y 15 CSVs de test |
| Comparacion clasica final | `fase7_comparacion_final_con_qfs.csv` con 15 filas y 5 datasets |
| QFS | `qfs_validation_results.csv` con 60 configuraciones; `qfs_model_results.csv` con 40 evaluaciones modelo-configuracion; `qfs_selected_all.csv` con 10 selecciones finales |
| Figuras memoria | `scripts/build_memoria_figuras.py` declara F1--F10, EV5, EV6 y A1--A9 con fuentes |
| Memoria | `resultados.tex` referencia figuras de cuerpo, apendice y tablas finales |

Estos numeros no sustituyen a una auditoria nueva si cambian los CSVs; sirven
para que el agente entienda la escala antes de opinar.

## 5. Arquitectura visual recomendada

El cuerpo debe funcionar como diez argumentos compuestos, no como inventario:

| Figura | Funcion |
|---|---|
| F1 | Presentar banco, dimensionalidad, clases y desbalance |
| F2 | Mostrar senal supervisada y anticipar el caso Madelon |
| F3 | Blindar base experimental: particiones, drift, conservacion |
| F4 | Caracterizar los doce selectores clasicos |
| F5 / EV6 | Relacion entre `k`, redundancia, coste dimensional y rendimiento |
| F6 | Hacer visible la interpretabilidad por instancia con SHAP |
| F7 | Separar significancia estadistica y magnitud practica |
| F8 | Explicar mandos de QFS: `alpha` y `beta` |
| F9 | Diagnosticar criterio frente a optimizador |
| F10 | Comparar baseline, mejor clasico, QFS-NA y oraculo por regimen |

El apendice conserva trazabilidad: permutaciones, leakage, roster completo,
handoff `I_i/R_ij`, coste cuantico simulado, solapes y metricas secundarias.

## 6. Patron de diseno para cada nueva figura

Usar esta ficha antes de programar:

```text
ID:
Seccion de memoria:
Pregunta de defensa:
Fuente primaria:
Unidad experimental: dataset / metodo / k / modelo / metrica / alpha / beta / seed
Figura granular:
Figura resumen:
Conclusion que permite defender:
Caveat metodologico:
Verificacion:
```

Ejemplo de buen planteamiento:

```text
ID: F9
Pregunta de defensa: si QFS se deteriora, falla el criterio o el optimizador?
Fuente primaria: comparacion_qfs_configuraciones_vs_baseline.csv + qfs_quality_control_*.csv
Unidad experimental: dataset, baseline, oraculo exacto, QFS-NA, macro-F1
Figura granular: tabla de control Hamming / delta coste por dataset
Figura resumen: plano criterio vs optimizador en puntos de macro-F1
Conclusion: Madelon queda limitado por criterio; Churn por optimizacion simulada
Caveat: oraculo exacto es control clasico del QUBO, no hardware cuantico
Verificacion: python3 scripts/verify_memoria_figuras.py
```

## 7. Verificaciones antes de cerrar

Ejecutar:

```bash
python3 scripts/verify_memoria_figuras.py
```

Si se modifica una fase concreta:

```bash
python3 scripts/verify_faseN_notebook.py
```

Si se modifica el generador de figuras:

```bash
python3 scripts/build_memoria_figuras.py
python3 scripts/verify_memoria_figuras.py
```

Si se modifica LaTeX, comprobar que cada `\includegraphics` tiene archivo en
`Plantilla_Latex_GCD/tfgs/figs/` y que no se ha introducido una figura sin
fuente primaria documentada.

## 8. Como debe razonar el agente

La respuesta correcta ante una peticion de "mejorar visualizaciones" no es
empezar por seaborn/matplotlib. El orden correcto es:

1. reconstruir el arco experimental;
2. detectar que pregunta no esta visualmente defendida;
3. localizar los datos que prueban esa pregunta;
4. elegir granularidad y resumen;
5. generar o ajustar la figura;
6. verificar que la memoria, el CSV y la figura cuentan lo mismo.

Solo despues de eso se decide estilo, paleta, layout y anotaciones.
