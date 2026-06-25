# Protocolo de revisión del trabajo de Codex (fase10 / análisis multidimensional)

> 2026-06-15. Preparado ANTES de que Codex termine. Premisa: Codex puede sacar conclusiones correctas
> localmente pero ERRÓNEAS globalmente por no tener toda la vista. Por eso la revisión es **verificación
> independiente (recomputar, no creer) + triangulación (≥2 instrumentos por conclusión) + falsación
> (buscar el dataset/perilla donde su afirmación general se rompe)**. No dar por bueno ningún número ni
> ninguna frase "demuestra X" sin contrastarla.

## 0. Integridad y alcance (primero de todo)
- ¿El notebook `fase10` corre de principio a fin desde núcleo limpio SIN errores? (ejecutar y comprobar).
- **¿Respetó los límites?** NO debió re-ejecutar fases 1–7 ni regenerar resultados ni editar los `.tex`.
  Comprobar `git status`/timestamps: si cambiaron CSVs de `results/tables/01..07` o ficheros `tex/`, es
  bandera roja → investigar qué tocó y por qué.
- ¿Las figuras están en `results/figures/10_memoria/` + copia a `figs/`? ¿Existe `hallazgos_fase10.md`?

## 1. Riesgos concretos donde Codex puede equivocarse → su chequeo
1. **One-hot/Churn como causa (no como hipótesis).** Riesgo: afirmarlo como hecho. Falsación: Madelon tiene
   redundancia media MENOR (R̄_ij 0.006) que Churn (0.019) y embebe bien (Δcoste≈0) → "baja redundancia⇒mal
   embebido" NO es monótono. Verificar que el error de embebido de B9 sea coherente en los 5 (no cherry-pick
   de Churn) y que Madelon salga con error bajo. Si Codex concluye causalidad one-hot sin la ablación → degradar a hipótesis.
2. **Escalera α.** Riesgo: presentar la escalera como si la hiciera el simulador analógico (fija α=0.5);
   la escalera es del ÓPTIMO EXACTO. Verificar la distinción y que la cardinalidad sea de hecho ~monótona en
   `qfs_oracle_*` (mirar los datos, no asumir la proposición de Mücke).
3. **Espacio de métodos.** Riesgo: normalización de "relevancia capturada" distinta → coordenadas distintas;
   y comparar Boruta/rfe (k variable) con los de k fijo (manzanas/naranjas). Verificar definiciones y que la
   conclusión "QFS=clase-mRMR en limpios, se desvía donde falla" se sostiene en las DOS vistas (coords+Jaccard).
4. **Dependencia del modelo.** Riesgo: usar cifras obsoletas. El +0.28 es baseline lineal/bosque; +0.094 es
   XGBoost. Verificar deltas POR MODELO contra `modeling_cost_performance.csv`.
5. **k-trayectoria.** Riesgo: extrapolar QFS a k donde no hay datos. Verificar que los puntos QFS existen a
   los k dibujados (`ev6_rendimiento_vs_k`/operational), no inventados.
6. **Atribución (síntesis).** Riesgo: recomputar con COSTE Q en vez de macro-F1 (coste no comparable entre
   datasets + desajuste α/cardinalidad). Verificar descomposición predictiva: criterio=baseline−oráculo,
   optimizador=oráculo−QFS-NA, ADITIVA.
7. **Régimen-como-predictor.** Riesgo: relato post-hoc circular ("predigo lo que ya sé"). Exigir que la
   lógica de régimen aplique a los 5 (incluidos BCW/Olive3 = "ambos ejes bien"), no solo a los que fallan.
8. **Honestidad estadística.** Olive9 INCONCLUSO (n=86): no debe figurar como victoria pese a oráculo 0.906.
   Churn = empate práctico en clásico pero deterioro en QFS: no confundir. macro-F1 primaria.
9. **Síntesis "todo en conjunto".** Riesgo: lista de hallazgos sin integrar. Exigir el relato causal
   régimen→mecanismo→resultado real.

## 2. Verificación numérica independiente — "answer key" (recomputar y comparar)
Recomputar desde artefactos y comparar con lo que Codex reporte (tolerancia de redondeo):
- **Atribución (macro-F1):** Madelon total ≈0.180 = **0.170 criterio + 0.010 optimizador**; Churn ≈0.078 =
  **0.001 criterio + 0.077 optimizador**; BCW −0.013; Olive3 0; Olive9 ≈0 (criterio −0.067, opt +0.064).
- **Espacio de métodos:** Olive3 QFS≡mRMR (J=1.00); Churn QFS↔mRMR J=**0.27** (el más bajo), máx con
  mutual_correlation 0.67; Madelon máx mRMR J=**0.25**; QFS redundancia interna Churn la MÁS ALTA (~0.041).
- **dist_ratio:** BCW/Olive **0.45**, Churn/Madelon **0.35** (vs 0.707 del paper).
- **Régimen:** Madelon FDR **13/500**, efecto **0.02**, PCA **295/500**, VIF≈1.3 (salvo feat_28/48/64);
  BCW VIF máx **3806** (23≥10); Churn VIF≈1, R_ij espiga gender **0.68** (1 par >0.3 de 105); Olive VIF 326.
- **Δcoste/Hamming:** Madelon Δ≈**−0.010** (alcanza óptimo); Churn Δ=**+1.323**, Hamming 8.
Si algún número de Codex no cuadra → rastrear su cálculo (no asumir que el mío es el correcto; reconciliar).

## 3. Triangulación (cada conclusión, ≥2 instrumentos independientes)
- *Churn = optimizador*: atribución (opt 0.077) + método-espacio (expulsado de mRMR) + Δcoste +1.32 + error
  de embebido B9 + oráculo recupera 0.999. Deben coincidir; si uno disiente, investigar.
- *Madelon = criterio*: atribución (crit 0.170) + oráculo también cae (0.643) + FDR 13/500 + PCA 295 +
  embebido OK (Δcoste≈0). Coherencia obligatoria.
- *QFS=clase-mRMR*: coords + Jaccard. Marcar cualquier conclusión que dependa de un SOLO instrumento.

## 4. Consistencia externa
- **Con la memoria (.tex):** las nuevas conclusiones no deben contradecir el texto actual; si lo hacen, es
  hallazgo a investigar, no a tapar.
- **Con el paper:** competitividad en k pequeño; "baja redundancia→embebido difícil"; α↔cardinalidad (Mücke).
- **Con mi síntesis previa** (`sintesis_hallazgos_vs_qfs.md`) y el blueprint.

## 5. Integridad visual (reglas viz-definitive)
Ejes con baseline 0 donde mide magnitud; escalas etiquetadas; n/denominadores visibles; sin doble-eje ni
coste-como-eje-comparable; color no engañoso; cada figura del cuerpo responde una pregunta de defensa.

## 6. Robustez (niveles de exigencia)
- **Crítico (recomputar + triangular + falsar):** la tesis criterio↔optimizador; régimen-como-predictor;
  hipótesis one-hot; descomposición de atribución. Aquí no basta "parece bien".
- **Secundario (spot-check + coherencia):** k, modelos, métricas, cadena de tests.
- **Editorial (revisión visual):** legibilidad, captions, reparto cuerpo/apéndice.

## RESULTADO DE LA REVISIÓN (2026-06-15, tras ejecución de Codex)

**Frente 0 (integridad/alcance): PASA.** Los `.tex` tienen mtime 11:2x (sesión previa), NO 18:55 → fase10
no los editó. Ningún CSV clásico (01–07) modificado → pipeline no relanzado. Notebook, core, hallazgos y
figuras presentes.

**Verificación numérica: CUADRA.** Atribución (Madelon 0.170+0.010; Churn 0.001+0.077) exacta; régimen
(VIF 3806/1.1, Madelon PCA 295 / efecto 0.02 / FDR 13/500) exacto; B6 +0.280→+0.094 exacto; B7 AUC ok.
B2: el Jaccard mRMR-Churn que yo tenía (0.27) vs Codex (0.33) es solo agregación de semillas; conclusión
idéntica (QFS↔mutual_correlation 0.67 ≫ mRMR 0.33). **Honestidad: Codex NO afirmó one-hot como causa.** ✓

**HALLAZGO ROBUSTO (2ª pasada, contraste con papers/documentación): B9 NO SIGUE EL PROCEDIMIENTO
DOCUMENTADO → sus números están INVENTADOS.** `scripts/fase10_visualizaciones_core.py` (build_b9):
- **Parchea el MDS del solver** con `NotebookMDS(SklearnMDS)` forzando `n_init=1` (líneas 435-445) y lo corre
  con **`max_iter=14, n_mds_runs=6`** (líneas 474-475).
- El procedimiento CANÓNICO es **100×100**: solver `arrange_atoms_robust_MDS(..., max_iter=100, n_mds_runs=100)`
  y `QFS_NA_Solver(..., mds_max_iter=100, mds_runs=100)`; memoria "100 inicializaciones independientes del
  MDS"; paper "N = 100 independent MDS runs with different random initializations" (para evitar mínimos locales).
- Con 6 corridas el MDS cae en mínimos locales malos → los errores de embebido B9 (BCW 0.242, Churn 0.227,
  Madelon 0.256...) **no son la cantidad documentada ni la que usaron las corridas reales de fase 8**. Son
  un atajo inventado por velocidad. **B9 es inválido tal cual.**

**RETRACTACIÓN (integridad):** mi conclusión del 1er pase ("la geometría queda REFUTADA porque Madelon 0.256
> Churn 0.227") **se apoyaba en estos números inválidos y queda RETIRADA**. La pregunta geométrica está
**sin resolver** (ni confirmada ni refutada) hasta recomputar B9 con 100×100 (o hacer que fase 8 guarde el
error real).

**Lo que SÍ se sostiene (independiente de B9):** Churn = fallo de OPTIMIZADOR por la vía **predictiva
scale-free** (oráculo 0.999 vs QFS-NA 0.922, gap 0.077) + **posición en métodos** (QFS eligió grupos de
dummies redundantes → fuera del nicho mRMR; J↔mRMR la más baja). Madelon = criterio (oráculo también cae a
0.643; FDR 13/500; PCA 295). Estas dos atribuciones NO dependen de B9.

**Nota de consistencia (secundaria):** B2 usa "redundancia interna" = media de **R_ij (información mutua)**,
mientras fase5/memoria define redundancia interna = media de **correlación absoluta** (`selected_mean_abs_corr`,
`corr_media_seleccionada`). Son métricas distintas (defendible usar R_ij por ser lo que QFS optimiza), pero
hay que **declararlo** para no tener dos "redundancias" incompatibles en la memoria.

**Acciones:** (1) recomputar B9 con el procedimiento canónico 100×100 (o guardar el error en fase 8) antes de
usar nada de embebido; (2) no narrar el fallo de Churn como geométrico mientras B9 no sea canónico;
(3) declarar la definición de redundancia de B2. Resto de instrumentos (A, B2-Jaccard, B3, B4, B5, B6, B7, C):
leen artefactos canónicos, verificados, sin invención.

## RESULTADO TRAS RE-RUN CANÓNICO 100×100 (2026-06-15) — answer key VIGENTE

Integridad: PASS (fase8 runs=100/iter=100; `qfs_embedding_error.csv` con posiciones reales; clásico y .tex
intactos salvo `fase7_comparacion_final_con_qfs.csv`, legítimo aguas abajo). Números re-derivados =
coinciden con Codex. Correcciones (B9 lee artefacto, B2=R_ij declarado, olive FDR de artefacto, sin doble
norm): aplicadas y verificadas. Informe `correcciones_codex.md`: honesto y completo.

**ANSWER KEY VIGENTE (100 MDS) — el de las 4 corridas queda OBSOLETO:**
| dataset | base | oracle | NA | criterio | optimizador | total | veredicto |
|---|---|---|---|---|---|---|---|
| BCW | 0.9374 | 0.9374 | 0.9374 | 0 | 0 | 0 | equivalente |
| Churn | 0.9998 | 0.9991 | 0.9695 | 0.0007 | **0.0296** | 0.0303 | deterioro |
| Madelon | 0.8130 | 0.6433 | 0.6032 | **0.1697** | 0.0401 | 0.2098 | deterioro |
| Olive3 | 1.0 | 1.0 | 1.0 | 0 | 0 | 0 | equivalente |
| Olive9 | 0.8387 | 0.9060 | 0.8424 | −0.0672 | 0.0635 | −0.0037 | equivalente |
Error embebido (β elegido): BCW 0.231, Churn 0.217, Madelon 0.250, Olive3 0.125, Olive9 0.143 → Churn NO
anómalo (embebido no explica su fallo).

**CAMBIOS NARRATIVOS (reconstrucción obligatoria):**
- **Churn:** deterioro 0.078→**0.030**; optimizador 0.077→0.030. Sigue siendo optimizador pero LEVE — el
  4-run inflaba el fallo. La simetría "dos fallos de igual magnitud" YA NO aplica: Madelon (0.21, criterio)
  es grande; Churn (0.03, optimizador) es pequeño.
- **BCW:** 0.950→0.937 (= baseline). La "mejora" anterior era ESPURIA (artefacto del 4-run). Ahora equivalente.
- Madelon=criterio (0.170≫0.040) y Olive9 inconcluso: intactos.
- Docs STALE a actualizar con estas cifras: `sintesis_hallazgos_vs_qfs.md`, tablas QFS de la memoria.

**DESVIACIÓN NUEVA (documentada por Codex, decisión del autor):** solver `MDS(...)` pasó de n_init=4 (_OG
default) a **n_init=1** (QFS_Auxiliar_functions.py:331), justificado como "100 semillas = 100 corridas".
Defendible y declarado, pero deja el solver distinto del _OG. Decidir: estricto-_OG (n_init=4) vs literal-paper
(n_init=1). Impacto menor (ambos con 100 runs).

## 7. La pregunta final (foco del TFG)
¿El conjunto sostiene la AMBICIÓN —analizar el proceso (no el podio) y demostrar que la referencia clásica
PREDICE y ATRIBUYE el comportamiento de QFS por las 9 dimensiones— sin sobreafirmar, con cada veredicto
trazable a un artefacto y honesto en lo inconcluso? Si sí, pasamos a Etapa 3 (curar) y 4 (memoria). Si no,
listar exactamente qué falta o qué se sobreafirmó, con su evidencia.
