# Modelo del sistema de evidencia — 2026-06-21

Diseño (sobre el papel, antes de prototipar) del sistema que corrige el hallazgo
central de las dos auditorías: el colapso al ganador. Basado en las decisiones de
Carlos:

- **Eje a desplegar en el cuerpo:** los **12 selectores** (no modelos/β/α/métricas
  en el cuerpo; esos van a apéndice/anexo).
- **Reparto:** cuerpo = distribución · apéndice = resúmenes · anexo digital = los
  1107 CSV con manifiesto.

## Restricción de protocolo (fija el diseño)

| Conjunto | Qué hay | Implicación |
|---|---|---|
| **Validación** | rejilla de 260 = 13 selectores × 5 datasets × 4 modelos (48 pts/dataset) | **Aquí vive el campo completo de los 12** |
| **Test** | solo 15 candidatos (reserva deliberada) | El test **no** puede mostrar los 12 sin romper la reserva |

QFS-NA y oráculo tienen `validation_macro_f1` → se sitúan en el **mismo eje de
validación**. El test sigue siendo el cierre, solo para candidatos.

> Regla de oro del sistema: **"el campo se ve en validación; el veredicto se
> sella en test".** Honra el held-out y a la vez muestra dónde cae QFS.

## Pieza central nueva (cuerpo): "Campo de validación de los 12 selectores"

- **Qué muestra:** por dataset, la **distribución** de macro-F1 de validación de
  los 12 selectores, con baseline marcado, y **QFS-NA y oráculo resaltados** sobre
  esa misma distribución. Responde: ¿QFS está en la mediana, el cuartil alto, o
  solo gana a un ganador flojo?
- **Encoding candidato:** strip/box horizontal, una fila por dataset, eje x =
  macro-F1 validación. Puntos = selectores; QFS-NA (rombo), oráculo (triángulo),
  baseline (línea/gris).
- **Fuente:** `modeling_validation_results_all.csv` (260) + `qfs_validation_results.csv` (60).
- **Compañera (tabla):** posición de QFS en el campo por dataset — mín/mediana/máx
  (o cuartiles) de los 12, rank de QFS dentro del campo, gap al mejor y al oráculo.

## Reorganización de las figuras existentes (resuelve redundancia)

| Figura | Rol en el sistema nuevo |
|---|---|
| **[NUEVA] campo validación 12** | centro de la comparación; hoy no existe |
| `tab:comparacion` (test) | veredicto en test (se mantiene) |
| `F10` | cierre baseline/mejor/QFS/oráculo en **test** (canónica del cierre) |
| `F09` | atribución criterio/optimizador (se mantiene, es única) |
| `ev7` | **redundante con F10** → fusionar o degradar a apéndice |
| `a5_panorama_deltas` | **reconstruir** como dot plot de deltas de los 12 (o absorber en la pieza central) |
| `a8` (Boruta invisible) | arreglar o sustituir por solape vs 12 |

## Capa de apéndice

- Resúmenes actuales (`tab:senal`, `tab:postproc`, `tab:particiones`, `tab:perfil`): se mantienen.
- **Exponer las 4 métricas** (balanced-acc, accuracy, AUC), hoy calculadas y
  ocultas: tabla por selector × métrica, al menos para los candidatos.
- Sensibilidad QFS a **β** (curva, `qfs_validation_results`) y a **α** (`qfs_oracle_*`):
  ampliar lo que ya hay (`fig:ap-beta`, `fig:ap-alpha`) con la trayectoria completa.

## Anexo digital + manifiesto (refleja los 260 sin saturar)

Estructura propuesta del manifiesto (`results/MANIFEST.md` o CSV índice):

| Columna | Contenido |
|---|---|
| afirmación / bloque | a qué resultado de la memoria respalda |
| fuente canónica | CSV exacto (p.ej. `modeling_validation_results_all.csv`) |
| familia | resultado / granular / andamiaje |
| nivel de exposición | cuerpo / apéndice / solo anexo |

Clasificar los 1107 en las tres familias; publicar el árbol versionado (repo/DOI)
y citarlo **una vez** en el cuerpo.

## Decisiones abiertas (para pensar juntos antes de prototipar)

1. **Modelos en la pieza central:** ¿48 puntos (12 selectores × 4 modelos) o
   agregamos por selector (mejor/medio de sus 4 modelos) para no saturar?
2. **Encoding:** ¿box, strip, o dot plot ordenado por rendimiento?
3. **QFS en la pieza:** ¿punto único (β elegido) o mostramos su rango de β como
   banda sobre el campo?
4. **a5:** ¿reconstruir como pieza independiente o absorberla en la central?
5. **Canónica del cierre:** confirmar F10 como cierre en test y degradar `ev7`.

## Estado

Diseño listo para discutir. No se ha prototipado nada. Auditorías de respaldo:
[figuras](auditoria_visual_figuras_2026-06-21.md) · [tablas](auditoria_tablas_csv_2026-06-21.md).
