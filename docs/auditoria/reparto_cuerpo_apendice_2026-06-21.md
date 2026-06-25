# Reparto de figuras y tablas: cuerpo · apéndice · anexo — 2026-06-21

Criterio rector: **el cuerpo cuenta la historia con la pieza mínima suficiente;
el apéndice respalda con detalle; el anexo digital guarda la granularidad
completa (1107 CSV).** Regla de protocolo: *el campo se ve en validación; el
veredicto se sella en test.*

Leyenda: ✅ se mantiene · ➕ nuevo · 🔧 arreglar/reconstruir · ⬇️ degradar a apéndice.

---

## CUERPO — Figuras

| # | Figura | Bloque narrativo | Por qué va al cuerpo | Estado |
|---|---|---|---|---|
| 1 | `F01_banco_regimenes` | Banco y régimen | Sitúa los 5 datasets en el plano del problema; abre el capítulo | ✅ |
| 2 | `F02_senal_fdr_efecto` | Señal supervisada | Establece que la señal es real (y débil en Madelon): premisa de todo | ✅ |
| 3 | `F03_base_confiable` | Base auditada | Demuestra particiones intercambiables y preprocesado conservador | ✅ |
| 4 | `F04_perfil_selectores` | Selección clásica | Perfil de los 12 (redundancia/coste/estabilidad): presenta el campo | ✅ |
| 5 | **Campo de validación de los 12** | Selección clásica | **Pieza que faltaba**: dónde cae QFS entre los 12 en rendimiento. Sostiene la tesis | ➕ |
| 6 | `F07_significancia_magnitud` | Veredicto | Significancia + magnitud del veredicto en test | ✅ |
| 7 | `F06_shap_beeswarm_instancias` | Interpretabilidad | Qué variables sostienen los modelos elegidos | ✅ |
| 8 | `qfs_organismo_cuantico` | QFS mecanismo | Embebido atómico MDS: el mecanismo cuántico hecho visible | ✅ |
| 9 | `F08_mandos_qfs_alpha_beta` | QFS mandos | α fija tamaño, β mueve rendimiento: los mandos del método | ✅ |
| 10 | `F09_atribucion_criterio_optimizador` | QFS diagnóstico | Aportación central: criterio vs optimizador. Única, insustituible | ✅ |
| 11 | `F10_comparacion_final_clasico_qfs` | Cierre | Veredicto final en test: baseline/mejor/QFS/oráculo. **Canónica del cierre** | ✅ |

Metodología: `ev5_evolucion_adiabatica` ✅ (ilustra la evolución adiabática).

➜ Cuerpo pasa de 10 a **11 figuras** (+ la nueva pieza central). `ev7` **no se
promociona** (redundante con F10).

## CUERPO — Tablas

| # | Tabla | Bloque | Por qué va al cuerpo | Estado |
|---|---|---|---|---|
| 1 | Conjuntos de datos (metodología) | Método | Define el banco: dimensiones, N, clases | ✅ |
| 2 | Composición del banco experimental | Banco | Coordenadas del estudio | ✅ |
| 3 | Señal univariante por dataset | Señal | Cifra de FDR/efecto por dataset | ✅ |
| 4 | Auditoría de confianza (`tab:regimenes`) | Base | AUC adversarial / régimen | ✅ |
| 5 | Perfil de los 12 selectores | Selección | Resumen redundancia/coste/estabilidad | ✅ |
| 6 | **Posición de QFS en el campo** | Selección | **Nueva**: rank de QFS entre los 12, gap al mejor y al oráculo, cuartiles | ➕ |
| 7 | Comparación final en test (`tab:comparacion`) | Veredicto | El veredicto sellado en test (candidatos) | ✅ |
| 8 | Diferencia pareada en test | Veredicto | Significancia pareada del mejor candidato | ✅ |
| 9 | Variables que sostienen los modelos | Interpret. | Soporte de la lectura SHAP | ✅ |
| 10 | Mandos QFS (`tab:qfs-control`) | QFS | Barrido α/β operativo | ✅ |
| 11 | Comparación QFS–baseline (`tab:qfs-comparacion`) | QFS | Veredicto QFS en test | ✅ |
| 12 | Robustez QFS por modelo (`tab:qfs-robustez`) | QFS | Veredicto robusto al clasificador | ✅ |
| 13 | Solape QFS (`tab:qfs-solape`) | QFS | Posición de QFS en el nicho de métodos | ✅ |
| 14 | Atribución criterio/optimizador (`tab:atribucion`) | QFS | Descomposición del deterioro | ✅ |

➜ Cuerpo pasa de ~13 a **14 tablas** (+ posición de QFS en el campo).

---

## APÉNDICE — Figuras (respaldo, no saturan el cuerpo)

| Figura | Por qué al apéndice | Estado |
|---|---|---|
| `f10_a_regimenes_dataset` | Detalle de regímenes (resume F01) | ✅ (revisar cobertura datasets) |
| `a1_permutacion_senal_nulo` | Separación frente al azar de la selección | 🔧 (heatmap 2-filas → tabla/barras) |
| `a2_leakage` | Pantalla de leakage | ✅ |
| `a3_roster_completo` | Roster de variables por método | 🔧 (heatmap casi constante → tabla) |
| `a4_shap_concordancia` | Concordancia SHAP por clase (Olive) | ✅ |
| **`a5_panorama_deltas`** | Deltas de **todos** los selectores: detalle del campo | 🔧 (reconstruir como dot plot) |
| `a6_handoff_ir`, `a7_coste_cuantico` | Entradas y coste de QFS | ✅ |
| `a8_solape_qfs_clasicos` | Solape QFS vs clásicos | 🔧 (Boruta invisible: arreglar) |
| `a9_macro_f1_auc_binarios` | F1 vs AUC en binarios | 🔧 (colisión etiquetas) |
| `o1_organismo_seleccion` | Consenso de selección en Madelon | ✅ |
| `f5_coste_rendimiento` | Redundancia vs k | ✅ |
| `ev6_rendimiento_vs_k` | Rendimiento vs k (re-modelado) | 🔧 (ilegible: rehacer) |
| `f10_b2/b5/b9/b10`, `explor_mapa` | Solapes, β-geometría, MDS, consistencia | ✅ |

## APÉNDICE — Tablas

| Tabla | Por qué al apéndice | Estado |
|---|---|---|
| `tab:senal`, `tab:postproc`, `tab:particiones`, `tab:perfil` | Auditorías densas citadas en su punto de uso | ✅ |
| `tab:candidatos` | Candidatos por dataset/modelo en test | ✅ |
| `tab:embedding`, `tab:cadena-tests`, `tab:ap-qfs-modelos` | Embebido, cadena de controles, robustez QFS | ✅ |
| `tab:ap-indice-trazabilidad` | Índice bloque→artefacto | ✅ (ampliar a manifiesto) |
| **4 métricas por candidato** | balanced-acc/accuracy/AUC hoy ocultas | ➕ |
| **β completo (curva)** y **α completo** | Trayectorias de sensibilidad QFS | ➕ (ampliar `fig:ap-beta/alpha`) |

---

## ANEXO DIGITAL (fuera del PDF)

Los **1107 CSV** versionados (repo/DOI), clasificados en **resultado / granular /
andamiaje**, con manifiesto que da la **fuente canónica de cada cifra**. Citado
**una vez** en el cuerpo. Es lo que refleja los 260 experimentos sin engordar la
memoria. Fuente canónica de la rejilla: `modeling_validation_results_all.csv`.

## ACTUALIZACIÓN (decisiones de Carlos) — piezas nuevas confirmadas en el cuerpo

Tras la auditoría de huecos ([huecos_promesa_vs_entrega_2026-06-21.md](huecos_promesa_vs_entrega_2026-06-21.md)),
se incorporan al **cuerpo** estas piezas (todas con dato existente):

| # | Pieza nueva | Cubre | Fuente |
|---|---|---|---|
| ➕F | **Campo de validación de los 12 selectores** (dot plot, QFS+oráculo) | colapso de comparación | `modeling_validation_results_all` + `qfs_validation_results` |
| ➕T | **Posición de QFS en el campo** (rank, gap, cuartiles) | compañera de la anterior | idem |
| ➕F | **Plano relevancia-redundancia: 12 + QFS por dataset** | **Hueco 1** (promesa metod. 170-172 incumplida) | `fs_selected_redundancy_summary` + `fs_qfs_mi_target_vector` |
| ➕F/T | **"Qué gana cada dataset"** (Δscore, reducción %, ×velocidad, Δredund.; mejor clásico + QFS) | **Hueco 2** (ventajas de la selección) | `modeling_cost_performance` + `qfs_operational_summary` |
| ➕F | **Curva macro-F1 vs β** visible (o consolidar en F08) | **Hueco 3** (QFS protagonista) | `qfs_validation_results` |
| ➕F | **Registro de átomos sobre plantilla** (estilo paper *neutral atom arrays*: posiciones + estado Rydberg + radio de bloqueo) | 4ª petición; referencia a `qfs_organismo` | `qfs_embedding_error` (`positions_json`, `min_radius`, `dist_ratio_rydberg`) + `qfs_selected_*` |

Paper de referencia para el registro: **"Quantum feature selection based on
neutral atom arrays"** (en `bib/bibliografia.bib`).

## Resumen de cambios (consolidado)

- **Cuerpo:** de 10 a **~15-16 figuras** y de 13 a **~15 tablas**. Núcleo
  intacto; se añade la capa de comparación completa (campo + plano), las
  ventajas por dataset, β visible y el registro atómico referenciado.
  `ev7` no se promociona.
- **Apéndice:** 6 figuras a arreglar/reconstruir (`a1,a3,a5,a8,a9,ev6`); +tabla
  de 4 métricas; +trayectorias β/α completas.
- **Anexo:** manifiesto de los 1107.

## Huecos menores pendientes (transparencia, no bloqueantes)

- **Interpretabilidad (SHAP)** solo se muestra para algunos datasets (Olive/BC);
  revisar si conviene cobertura uniforme.
- **"Subconjuntos por nombre de variable"** (promesa metod. 172): hoy parcial
  (`a3` roster —a reconstruir—, `o1`).
