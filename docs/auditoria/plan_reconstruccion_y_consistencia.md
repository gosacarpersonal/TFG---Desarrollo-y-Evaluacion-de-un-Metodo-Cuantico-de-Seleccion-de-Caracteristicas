# Plan: reconstrucción tras el re-run, dimensión de consistencia e impacto en la memoria

> 2026-06-15. Pensado mientras Codex re-ejecuta fase8/9 con MDS verificado (100×100). Foco rector:
> dejar una **base sólida (clásica y cuántica)** verificando que **cada elemento del TFG tiene PROPÓSITO
> (por qué está), SENTIDO (sigue el método documentado) y EFECTO (cambia/demuestra algo real)**. Captura
> escrita, no mental.

## 1. Qué revisar cuando Codex termine (post-100-MDS)
**Integridad/alcance** (como antes): que use `QFS_MDS_RUNS=100`, `MAX_ITER=100`; que exista
`qfs_embedding_error.csv` con valores reales; que fase8+9 se re-ejecutaran (timestamps); clásico (01–07) y
`.tex` intactos; informe `correcciones_codex.md` honesto.

**Lo científico (clave):** ¿cambia el veredicto con 100 corridas?
- **RE-DERIVAR el answer key desde los NUEVOS artefactos** — el answer key del protocolo (atribución, Jaccard,
  Δcoste, dist_ratio) se calculó con los resultados de 4 corridas y queda **STALE**. No anclar en él.
- Test real de Churn: ¿se RECUPERA (→ el fallo era artefacto de las 4 corridas / mínimo local) o PERSISTE
  (→ optimizador/criterio real)? Madelon=criterio NO debería cambiar (es criterio, no embebido). BCW/Olive3
  equivalencias deberían sostenerse; Olive9 inconcluso.
- B9 ahora debe LEER el error real (sin monkeypatch); comprobar que el relato de embebido sale de ahí.

## 2. Mapa de dependencias: qué se reconstruye y qué es estable
**ESTABLE (independiente del embebido QFS) — no se toca:** todo el bloque clásico (fases 1–7): regímenes
(VIF/PCA/FDR/efecto), los 12 selectores, estabilidad, modelado clásico, comparación clásica, SHAP. Sus
conclusiones quedan asentadas.

**EN RIESGO (cuelga del embebido QFS) — re-verificar/reconstruir si cambian los números:**
- Artefactos: `qfs_runs/operational_summary/oracle/quality_control/comparacion_*`, `qfs_embedding_error`.
- Análisis: atribución criterio↔optimizador (C), método-espacio B2 (coords+Jaccard de QFS), trayectoria k
  B3 (línea QFS), β/B5, átomos B9.
- **Docs/conclusiones nuestras que quedan STALE:** `sintesis_hallazgos_vs_qfs.md` (la historia de Churn:
  one-hot/geometría/optimizador), el answer key del protocolo, y la sección de Churn de
  `analisis-proceso-no-podio`. **CONGELAR la narrativa de Churn** hasta tener los números de 100 corridas.
- Tablas de la memoria (resultados.tex `tab:qfs-control`, `tab:qfs-comparacion`): sus cifras pueden cambiar
  → marcar para la etapa de reescritura (no editar ahora).

## 3. Procedimiento de reconstrucción
1) Re-derivar answer key desde nuevos artefactos. 2) Recomputar atribución, B2, B3, B9 (ya los hace fase10;
verificar). 3) Re-verificar cada conclusión "asentada" contra los nuevos números, marcando: se mantiene /
cambia magnitud / cambia veredicto. 4) Actualizar `sintesis_hallazgos_vs_qfs.md` y el answer key. 5) Solo
entonces tocar la memoria.

## 4. Nueva dimensión: CONSISTENCIA (semillas / permutaciones / bootstrap)
Enriquece convirtiendo "usamos 3 semillas, 20 perms, 400–2000 bootstrap" (hoy nota de limitaciones) en
**evidencia de robustez medida**. PERO es HETEROGÉNEA (verificado) — hay que contarlo con honestidad:
- **Selección (fase5): 3 semillas reales (13/42/97)** → estabilidad Jaccard/Kuncheva ya medida
  (`fs_jaccard_stability`). Mide consistencia *de la selección* ante reinicio.
- **Modelado (fase6): UNA corrida** (sin columna de semilla) → la robustez NO es por re-semillar sino por
  **bootstrap (400–2000) + permutación de etiquetas (500)**: ancho de IC y separación del nulo.
- **QFS (fase8): UNA corrida por config** → robustez por **MDS 100 corridas + 10000 shots**, no por semilla.
- **Resolución del nulo:** 20 perms en selección ⇒ p mínimo 1/21≈0.048; 500 perms en modelado ⇒ 1/501≈0.002.

**Qué demuestra (lente L3):** que los veredictos no son frágiles a la resolución elegida — o, donde sí lo
son, declararlo (Olive9: IC ancho por n=86 + bootstrap). **Instrumento propuesto (B-consistencia):** por
conclusión, su margen de estabilidad: Jaccard entre semillas (selección), ancho de IC bootstrap y p de
permutación (modelado/QFS), resolución del nulo. Vive en fase10 (apéndice) + una nota en cuerpo.

**Decisión para el autor:** la consistencia de *modelado/QFS* hoy es por resampling, no por re-ejecución.
Si se quiere consistencia "fuerte" (¿el veredicto QFS aguanta varias semillas de QFS/modelo?), es un
experimento NUEVO (multi-seed) — opcional; coste vs riqueza. Por defecto: reportar la robustez por
resampling y declarar la asimetría como limitación, no inventar una consistencia que no se ejecutó.

## 5. Impacto en la estructura / índice de la memoria
Cambios MÍNIMOS y con propósito (no reestructurar por reestructurar):
- **Cap. 5.1:** reencuadrar la caracterización de datasets como **régimen predictor** (VIF/PCA como ejes
  relevancia/redundancia), no como contexto descriptivo. (Quizá subsección "Regímenes del banco".)
- **Cap. 5.3/5.4:** elevar el **diagnóstico criterio↔optimizador** de "discusión" a subsección propia (es la
  tesis); incluir el espacio-de-métodos (los 12) y, si Churn cambia con 100 corridas, reescribir su causa.
- **Nueva subsección "Consistencia y robustez"** (en 5.2/5.4 o transversal): estabilidad por semillas +
  resampling + resolución del nulo. Hoy está disperso en limitaciones; merece un sitio con propósito-efecto.
- **Apéndice:** añadir **fase10** a la lista de notebooks reproducibles (hoy lista 1–9) y las tablas
  derivadas (B2 Jaccard, B9 embedding_error, consistencia).
- **Marco teórico:** una línea sobre los ejes relevancia/redundancia (VIF/PCA) como base del diagnóstico.
- NO se justifica tocar la macroestructura de 6 capítulos; son ajustes dentro de Cap.5 + apéndice.

## 6. Lente propósito / sentido / efecto (aplicar a todo)
Para cada elemento (dataset, método, k, α, β, modelo, métrica, test, semilla/perm/bootstrap): **propósito**
(por qué está), **sentido** (sigue el método documentado — lo que acabamos de auditar), **efecto** (¿cambia
algo? ¿lo demuestra una figura/cifra?). Si algo no pasa los tres → o se justifica, o se simplifica, o se
declara. Esta es la prueba final de "base sólida con todo con un porqué".

## 7. Decisiones para el autor (gates)
- G-a: tras el re-run, ¿Churn se recupera o persiste? (define la narrativa cuántica).
- G-b: ¿consistencia fuerte multi-seed (experimento nuevo) o robustez por resampling + limitación declarada?
- G-c: validar los ajustes de índice (5.1 regímenes, 5.3 diagnóstico, subsección consistencia, fase10 en apéndice).
