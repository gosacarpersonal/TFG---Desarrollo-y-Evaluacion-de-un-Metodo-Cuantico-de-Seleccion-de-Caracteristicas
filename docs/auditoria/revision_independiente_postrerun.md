# Revisión independiente del re-run canónico QFS (cierre de turno)

Fecha: 2026-06-15. Auditoría independiente del trabajo de Codex (`correcciones_codex.md`) tras re-ejecutar
fase8/9/10 con MDS verificado 100×100. Método: **verificar (recomputar, no creer) + triangular + falsar**,
según `protocolo_revision_fase10.md`. No se re-ejecutó el pipeline; las cifras se re-derivaron de los
artefactos en `results/tables/`.

## 1. Integridad y alcance — PASA

| Check | Resultado |
|---|---|
| Fase8 con MDS verificado | `QFS_MDS_RUNS=100`, `QFS_MDS_MAX_ITER=100` (rebuild_fase8:96-97) ✓ |
| Artefacto de embebido guardado | `qfs_embedding_error.csv` (55 filas, posiciones reales, runs=100) ✓ |
| Pipeline clásico (01–07) intacto | sin CSV modificado salvo `fase7_comparacion_final_con_qfs.csv` (legítimo, aguas abajo de fase9) ✓ |
| `.tex` no editados | mtime 11:2x (sesión previa), no del re-run ✓ |
| B9 sin recomputar MDS | lee `qfs_embedding_error.csv` (fase10_core:433), `NotebookMDS` eliminado ✓ |
| Verificadores | verify_fase8_ejecucion / fase8_solver (A–E) / fase9_evaluacion: PASS (reportado por Codex) |

## 2. Verificación numérica independiente — CUADRA
Answer key re-derivado por mí desde `comparacion_qfs_configuraciones_vs_baseline.csv` (descomposición
predictiva: criterio = baseline−oráculo, optimizador = oráculo−NA). Coincide con Codex.

| Dataset | baseline | oráculo | QFS-NA | criterio | optimizador | total | error embebido (β elegido) | veredicto |
|---|---|---|---|---|---|---|---|---|
| Breast Cancer | 0.9374 | 0.9374 | 0.9374 | 0.0000 | 0.0000 | 0.0000 | 0.231 | equivalente |
| Customer Churn | 0.9998 | 0.9991 | 0.9695 | 0.0007 | **0.0296** | 0.0303 | 0.217 | deterioro (optimizador, leve) |
| Madelon | 0.8130 | 0.6433 | 0.6032 | **0.1697** | 0.0401 | 0.2098 | 0.250 | deterioro (criterio) |
| Olive Oil 3-class | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.125 | equivalente |
| Olive Oil 9-class | 0.8387 | 0.9060 | 0.8424 | −0.0672 | 0.0635 | −0.0037 | 0.143 | equivalente (inconcluso, n=86) |

## 3. Las 6 correcciones — verificadas
1. MDS 100/100 en fase8 ✓ (resultados regenerados). 2. B9 lee el artefacto canónico ✓. 3. B2 declara
redundancia = media R_ij (MI) ✓. 4. Olive FDR desde `fase1_fdr_resumen` ✓. 5. Sin doble normalización
(fase5 entrega MI cruda; solver normaliza una vez) ✓. 6. `hallazgos_fase10.md` regenerado con cifras
canónicas (verificado: C = Madelon 0.170/0.040/0.210, Churn 0.001/0.030/0.030) ✓.

## 4. Desviación NUEVA encontrada (no estaba en el encargo) — documentada, decisión del autor
Codex modificó el **solver de referencia**: `MDS(..., n_init=1)` (QFS_Auxiliar_functions:331), frente al
`_OG` que usa `n_init=4` (default sklearn). Está **documentado y argumentado** ("100 semillas = 100 corridas
independientes"), no es invención silenciosa. Defendible y más fiel a la letra del paper ("100 independent
runs"), pero deja el solver distinto del `_OG`. **Decisión G-b:** estricto-`_OG` (n_init=4) vs literal-paper
(n_init=1). Impacto menor (ambos con 100 runs). Recomendación: mantener n_init=1 documentado.

## 5. Falsación — la hipótesis geométrica/one-hot de Churn queda REFUTADA
Con error de embebido canónico, **Churn (0.217) embebe MEJOR que Madelon (0.250) y BCW (0.231)** y aun así es
el que se deteriora por optimizador. El embebido NO explica el fallo de Churn → la cadena
one-hot⇒MDS-frustrado⇒fallo NO se sostiene (era, en parte, artefacto del atajo de 4 corridas, que inflaba
Δcoste +1.32 → ahora +0.62 y deterioro 0.078 → 0.030). One-hot queda como diferencia de preprocesado
declarable, no como causa.

## 6. Reconstrucción de lo asentado — HECHA
- **Figura F9 `diag_atribucion_qfs`**: subtítulo corregido (era "misma magnitud de daño", falso) → "Madelon:
  gran fallo de criterio; Churn: déficit menor de optimizador"; re-renderizada con cifras canónicas y copiada
  a `figs/`.
- **`sintesis_hallazgos_vs_qfs.md`**: banner de obsolescencia + sección β/geometría reescrita (refutación) +
  one-hot degradado. La parte clásica (regímenes VIF/PCA) se conserva (no afectada por el re-run).
- **Answer key vigente** fijado en `protocolo_revision_fase10.md`.

## 7. Lectura científica (gemela del "veredicto" de Codex, con mi auditoría)
La tesis criterio↔optimizador se sostiene y queda **más limpia**: el único deterioro sustantivo es **Madelon
(criterio, 0.21)**; **Churn es un déficit menor de optimizador (0.03)** junto a un baseline saturado, sin
causa geométrica; BCW/Olive3 equivalentes; Olive9 inconcluso (n=86). La "simetría de dos fallos opuestos de
igual magnitud" era artefacto del atajo de 4 corridas y se descarta. La base cuántica queda **alineada con la
documentación (memoria + paper + solver), verificada y con la narrativa reconstruida a la realidad canónica**.

## 8. Pendiente — diferido por SECUENCIA, no por olvido
- **Tablas QFS de `resultados.tex`** (`tab:qfs-control`, `tab:qfs-comparacion`) tienen cifras viejas
  (Churn 0.922/BCW 0.950/Δcoste +1.32). Se actualizan en la **Etapa 4 (reescritura de la memoria)**, donde
  editar `.tex` es lo correcto. NO se tocan ahora (regla acordada).

## 9. Gates (decisiones del autor)
- **G-b:** `n_init` 4 (estricto-_OG) vs 1 (literal-paper). Recomendación: 1, documentado.
- **G-c1:** consistencia "fuerte" multi-seed de modelado/QFS (experimento nuevo) vs robustez por
  resampling + limitación declarada (lo que hay). Recomendación: declarar; multi-seed solo si hay margen.
- **G-c2:** ajustes de índice (5.1 regímenes-predictor, subsección diagnóstico, subsección consistencia,
  fase10 al apéndice).
- **G-d:** arrancar Etapa 4 (reescritura) con la narrativa canónica (Churn leve, sin geometría).
