# Auditoría visual profunda — 2026-06-18

> Este documento es un artefacto de auditoría editorial, no una fuente primaria.
> Las fuentes primarias siguen siendo los CSV de `results/tables/`, el código, los
> notebooks, las figuras generadas y los `.tex` de la memoria. La auditoría se
> apoya en el estado actual de `Plantilla_Latex_GCD/tfgs/tex/` y en las figuras de
> `Plantilla_Latex_GCD/tfgs/figs/`.

## 1. Diagnóstico ejecutivo

La sensación de rechazo hacia las figuras está justificada, pero no porque todas
las visualizaciones sean inútiles. El problema principal es sistémico:

1. El cuerpo de Resultados sigue saturado: hay 18 figuras en
   `resultados.tex`, más una figura metodológica QFS fuera de Resultados. Esto
   contradice la arquitectura declarada de 8--10 figuras argumentales.
2. Las figuras mezclan tres lenguajes visuales:
   - composición editorial cálida (`F01`--`F10`);
   - figuras de notebook o diagnóstico técnico (`f10_b*`, `ev6`, `o1`);
   - figuras conceptuales/mecánicas (`qfs_organismo_cuantico`,
     `ev5_evolucion_adiabatica`).
3. Varias figuras responden preguntas reales, pero están ubicadas en el cuerpo
   cuando su función es de evidencia granular. Eso hace que el capítulo parezca
   una cadena de outputs, no una narración.
4. Algunas figuras tienen títulos fuertes que ya contienen la conclusión, pero el
   diseño visual no la jerarquiza con suficiente limpieza; el lector debe leer
   demasiado para entender por qué la figura está ahí.
5. El verificador `scripts/verify_memoria_figuras.py` pasa, pero solo prueba
   integridad mecánica: referencias, captions, labels y existencia de archivos.
   No valida dirección de arte, necesidad narrativa ni calidad visual.

Conclusión: no conviene "quitarlas todas" como decisión final, pero sí conviene
hacer una retirada editorial temporal: analizar el capítulo sin figuras, decidir
qué afirmaciones necesitan defensa visual, y reinsertar solo las figuras que
superen ese test. La intuición del autor es correcta: el problema es de sistema
visual, no de una figura aislada.

## 2. Estado actual comprobado

Comprobación realizada:

- Se leyeron los protocolos:
  - `docs/auditoria/protocolo_agentes_visualizaciones.md`;
  - `docs/auditoria/estrategia_visual_memoria.md`;
  - `docs/auditoria/especificacion_figuras_memoria.md`;
  - `docs/auditoria/INSTRUCCIONES_CODEX.md`.
- Se extrajeron las figuras incluidas en:
  - `marco_teorico.tex`;
  - `metodologia.tex`;
  - `resultados.tex`;
  - `apendice.tex`.
- Se generaron láminas de contacto temporales en `/tmp/tfg_visual_audit/`.
- Se ejecutó:

```bash
python3 scripts/verify_memoria_figuras.py
```

Resultado del verificador: `OVERALL: PASS`.

Conteo observado:

| Zona | Figuras incluidas |
|---|---:|
| Marco/metodología/resultados | 19 |
| Solo `resultados.tex` | 18 |
| Apéndice | 11 |

El estado actual no es una memoria visualmente seca. Es una memoria visualmente
saturada.

## 3. Por qué probablemente disgustan tanto

### 3.1. Hay demasiadas figuras con apariencia de "prueba intermedia"

El lector pasa de banco, a señal, a auditoría, a régimen, a selectores, a
organismo, a redundancia, a test, a SHAP, a QFS, a alpha/beta, a atribución, a
comparación final, a rendimiento por k, a escalera alpha, a beta, a MDS, a
consistencia. La mayoría son defendibles individualmente, pero juntas producen
fatiga.

La memoria no respira. El texto queda subordinado a una sucesión de imágenes.

### 3.2. Varias figuras compiten por la misma función

Ejemplos claros:

- `F01_banco_regimenes.pdf`, `F02_senal_fdr_efecto.pdf`,
  `F03_base_confiable.pdf` y `f10_a_regimenes_dataset.png` se solapan en la
  función de caracterizar el régimen del banco.
- `F08_mandos_qfs_alpha_beta.pdf`, `f10_b4_escalera_alpha.png` y
  `f10_b5_beta_geometria.png` explican mandos QFS en tres niveles distintos.
- `qfs_organismo_cuantico.pdf`, `f10_b9_atomos_mds_error.png`,
  `f10_b5_beta_geometria.png` y `F09_atribucion_criterio_optimizador.pdf`
  compiten por explicar por qué QFS falla o no falla.
- `F04_perfil_selectores.pdf`, `o1_organismo_seleccion.png`,
  `f5_coste_rendimiento.png` y `f10_b10_consistencia.png` cubren selección
  clásica, estabilidad y redundancia con demasiada granularidad para cuerpo.

La repetición no se percibe como rigor; se percibe como inseguridad narrativa.

### 3.3. La paleta común ayuda, pero no basta

Muchas figuras usan fondo crema, títulos en cabecera y colores consistentes. Aun
así, el conjunto no termina de verse como un sistema porque cambian demasiado:

- densidad de paneles;
- tamaño de títulos;
- escala de tipografías;
- uso de leyendas;
- cantidad de anotaciones;
- estructura de márgenes;
- relación figura/caption.

Una paleta compartida no sustituye a una gramática visual compartida.

### 3.4. Algunas figuras son buenas evidencias, pero malas figuras de cuerpo

Una figura de cuerpo debe hacer una afirmación casi sin pedir permiso. Varias
figuras actuales obligan al lector a descifrar:

- qué eje importa;
- qué panel es el principal;
- qué conclusión debe extraer;
- por qué la figura está en ese punto y no en el apéndice.

Esto no significa que sean malas como evidencia. Significa que su sitio natural
es el apéndice o una lámina técnica.

## 4. Auditoría figura por figura

### Figuras fuera de Resultados

| Figura | Diagnóstico | Veredicto |
|---|---|---|
| `ev5_evolucion_adiabatica.png` | Útil para método, pero muy genérica. Se entiende, aunque parece más didáctica que experimental. | Conservar en metodología si el capítulo necesita explicar el protocolo físico; rediseñar solo si se rehace el lenguaje visual completo. |
| Esquemas de marco teórico | No están en la lámina de contacto como raster, pero cumplen función conceptual. | No son el problema principal; no tocarlas primero. |

### Resultados: banco y confianza

| Figura | Función actual | Problema visual/narrativo | Veredicto |
|---|---|---|---|
| `F01_banco_regimenes.pdf` | Presenta tamaño, dimensión, desbalance y señal. | Es una buena apertura, pero ya contiene parte de F2 y compite con `f10_a_regimenes_dataset`. | Conservar como candidata de cuerpo, quizá simplificada. |
| `F02_senal_fdr_efecto.pdf` | Señal univariante y efecto; anticipa Madelon. | Tiene función argumental clara. Visualmente es sobria, pero no especialmente memorable. | Conservar o fusionar con F1 si se decide reducir fuerte. |
| `F03_base_confiable.pdf` | AUC adversarial, drift y conservación. | Necesaria para blindar el protocolo, pero densa y técnica. | Conservar en cuerpo solo si se quiere mostrar auditoría explícita; si no, mover a apéndice y dejar tabla/veredicto en cuerpo. |
| `f10_a_regimenes_dataset.png` | Resume régimen antes de QFS. | Duplica parcialmente F1/F2/F3. Tiene aspecto de apoyo diagnóstico. | Mover al apéndice o eliminar si F1-F3 cubren la función. |

### Resultados: selección clásica

| Figura | Función actual | Problema visual/narrativo | Veredicto |
|---|---|---|---|
| `F04_perfil_selectores.pdf` | Resume redundancia, coste, estabilidad y nulo. | Es la figura clásica más completa, pero muy cargada. | Conservar como única figura de selección clásica, rediseñada con más jerarquía. |
| `o1_organismo_seleccion.png` | Abre Madelon por variable/selector. | Interesante pero parece heatmap de notebook; demasiado específico para cuerpo salvo que Madelon sea el protagonista visual. | Mover al apéndice o transformar en una lámina de evidencia de Madelon. |
| `f5_coste_rendimiento.png` | Redundancia interna frente a k. | El nombre histórico dice coste-rendimiento, pero el contenido es redundancia. Añade una capa más al bloque clásico. | Mover al apéndice o fusionar con F4/EV6; no mantener como figura autónoma de cuerpo. |
| `F07_significancia_magnitud.pdf` | Diferencia pareada con IC. | Clara y necesaria. Es de las más limpias. | Conservar en cuerpo. |
| `F06_shap_beeswarm_instancias.pdf` | Interpretabilidad por instancia. | Metodológicamente importante, pero visualmente chirría frente al estilo editorial: densidad alta, colores SHAP, mucho microtexto. | Conservar solo si se rediseña/retematiza; si no, pasar a apéndice y dejar una figura SHAP más selectiva en cuerpo. |

### Resultados: QFS

| Figura | Función actual | Problema visual/narrativo | Veredicto |
|---|---|---|---|
| `qfs_organismo_cuantico.pdf` | Muestra átomos, densidad y selección por dataset. | Es muy informativa, pero visualmente parece otro sistema. Puede ser protagonista si se rediseña como figura central QFS. | Conservar como candidata de cuerpo, pero rediseñar. |
| `F08_mandos_qfs_alpha_beta.pdf` | Explica alpha y beta. | Función clara, pero tiene mucha información y compite con `f10_b4` y `f10_b5`. | Conservar una sola figura de mandos; mover detalles a apéndice. |
| `F09_atribucion_criterio_optimizador.pdf` | Diagnóstico central criterio vs optimizador. | Es argumentalmente la figura más importante. Visualmente debe ser más limpia y más solemne. | Conservar sí o sí; rediseñar como figura-clímax. |
| `F10_comparacion_final_clasico_qfs.pdf` | Cierre final clásico-QFS. | Necesaria, pero algo pequeña y densa para cerrar. | Conservar; rediseñar para cierre más claro. |
| `ev6_rendimiento_vs_k.png` | Sensibilidad/rendimiento frente a k. | Evidencia buena, pero es diagnóstico adicional tras el cierre. En cuerpo corta el ritmo. | Mover al apéndice salvo que sustituya a otra figura de rendimiento. |
| `f10_b4_escalera_alpha.png` | Escalera alpha exacta. | Buena evidencia técnica, no figura de cuerpo si F8 ya existe. | Apéndice. |
| `f10_b5_beta_geometria.png` | Densidad frente a beta. | Evidencia técnica, no argumento principal. | Apéndice. |
| `f10_b9_atomos_mds_error.png` | MDS/error por dataset. | Importante para descartar hipótesis geométrica, pero visualmente de apoyo. | Apéndice, con referencia explícita desde el texto. |
| `f10_b10_consistencia.png` | Estabilidad entre semillas. | Evidencia metodológica; llega tarde y visualmente no aporta al hilo principal. | Apéndice. |

### Apéndice

El apéndice visual está más cerca de lo correcto: contiene evidencia granular.
Sin embargo, todavía parece mezcla de outputs porque no está suficientemente
rotulado como atlas por familias.

| Figura | Veredicto |
|---|---|
| `a1_permutacion_senal_nulo.png` | Conservar en apéndice. |
| `a2_leakage.png` | Conservar en apéndice. |
| `a3_roster_completo.png` | Conservar, pero quizá necesita rediseño si el texto la usa mucho. |
| `a4_shap_concordancia.png` | Conservar si F6 queda en cuerpo; si F6 baja, reorganizar SHAP completo aquí. |
| `a5_panorama_deltas.png` | Conservar como evidencia secundaria de modelado. |
| `a6_handoff_ir.png` | Conservar: puente claro hacia QFS. |
| `a7_coste_cuantico.png` | Conservar: caveat de coste importante. |
| `explor_mapa_metodos.png` | Conservar solo si el texto lo referencia como coordenada conceptual; si no, fusionar con solapes. |
| `f10_b2_jaccard_12_metodos.png` | Conservar como atlas de solape; no subir al cuerpo. |
| `a8_solape_qfs_clasicos.png` | Puede fusionarse con `f10_b2_jaccard_12_metodos`. |
| `a9_macro_f1_auc_binarios.png` | Conservar si se menciona el puente AUC con papers; si no, tabla breve. |

## 5. Figuras que sí merecen sobrevivir en el cuerpo

Primera propuesta conservadora: 9 figuras de cuerpo en Resultados.

| Slot | Figura candidata | Condición |
|---|---|---|
| 1 | F1 banco/regímenes | Simplificar o aceptar como apertura. |
| 2 | F2 señal FDR/efecto | Mantener si Madelon se anticipa visualmente. |
| 3 | F3 base confiable | Mantener solo si se quiere blindaje visual explícito. |
| 4 | F4 perfil selectores | Rediseñar con más jerarquía; debe ser la única figura del bloque de selectores. |
| 5 | F7 significancia/magnitud | Mantener. |
| 6 | F6 SHAP | Rediseñar o sustituir por una versión más limpia y selectiva. |
| 7 | QFS organismo | Rediseñar como figura central del mecanismo QFS. |
| 8 | F9 criterio--optimizador | Mantener y elevar. |
| 9 | F10 comparación final | Mantener y elevar como cierre. |

Si se quiere una versión aún más limpia, F3 puede bajar al apéndice y el cuerpo
quedaría con 8 figuras de Resultados.

## 6. Figuras que deberían salir del cuerpo

Estas figuras no deben desaparecer necesariamente, pero no deberían seguir como
figuras de cuerpo:

- `f10_a_regimenes_dataset.png`;
- `o1_organismo_seleccion.png`;
- `f5_coste_rendimiento.png`;
- `ev6_rendimiento_vs_k.png`;
- `f10_b4_escalera_alpha.png`;
- `f10_b5_beta_geometria.png`;
- `f10_b9_atomos_mds_error.png`;
- `f10_b10_consistencia.png`.

Motivo común: son evidencias de auditoría o diagnóstico granular, no hitos de la
lectura principal.

## 7. Qué haría antes de rediseñar nada

1. Crear una versión de `resultados.tex` sin figuras secundarias de cuerpo:
   dejar solo referencias textuales a las tablas y al apéndice.
2. Leer el capítulo así, "a secas", y marcar cada punto donde el texto realmente
   necesita una figura para no convertirse en una afirmación opaca.
3. Reinsertar figuras por pregunta, no por disponibilidad.
4. Rediseñar solo las sobrevivientes de cuerpo con una gramática única:
   - títulos más cortos;
   - menos paneles por figura;
   - una conclusión visual dominante;
   - menos microtexto;
   - una leyenda máxima;
   - captions que expliquen, no que compensen la figura.
5. Convertir el apéndice en atlas:
   - Auditoría de datos;
   - Selección clásica;
   - Modelado e interpretabilidad;
   - QFS interno;
   - Solapes, costes y métricas secundarias.

## 8. Respuesta a la intuición del autor

Sí: tiene sentido quitar mentalmente todas las figuras y volver a plantearlas.
No como destrucción final, sino como método editorial.

El rechazo probablemente aparece porque la memoria visual actual conserva la
huella de su proceso de investigación: muchas figuras son restos de decisiones,
diagnósticos, hipótesis descartadas y comprobaciones necesarias. Eso es bueno
para el trabajo experimental, pero no siempre es bueno para el cuerpo de la
memoria.

La versión madura no es "más bonita". Es más severa:

- el cuerpo solo muestra lo que cambia la lectura;
- el apéndice conserva lo que permite auditarla;
- cada figura tiene una pregunta, una fuente y una conclusión;
- ninguna figura entra solo porque exista.

El siguiente paso recomendado es una poda editorial controlada del cuerpo antes
de rediseñar: sacar las ocho figuras secundarias listadas arriba hacia el
apéndice o a una zona de cuarentena, recompilar, y leer si el capítulo respira.
