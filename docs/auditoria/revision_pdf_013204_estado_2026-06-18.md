# Estado de la revisión `review-2026-06-18-013204.pdf`

> Auditoría contra el estado actual del repositorio, posterior a la poda visual.
> El PDF es anterior a la revisión visual; por tanto, las observaciones sobre
> ubicación o exceso de figuras se evalúan contra `resultados.tex` y
> `apendice.tex` actuales.

## Resumen

La revisión es útil y mayoritariamente compatible con los cambios ya hechos. Los
hallazgos técnicos T1--T5 estaban resueltos o muy mitigados por correcciones
anteriores; esta pasada ha aplicado las correcciones menores que seguían vivas.

## Estado por hallazgo

| ID | Estado actual | Evidencia / acción |
|---|---|---|
| T1. Delta coste negativo frente a "óptimo exacto" | Aplicado antes de esta pasada | `resultados.tex` explica que el control es `mucke_k` a presupuesto fijo y que el delta se reevalúa en `alpha=0.5`, por lo que puede ser negativo. |
| T2. `alpha` promete presupuestos unitarios | Aplicado antes de esta pasada | `marco_teorico.tex`, `metodologia.tex` y `resultados.tex` hablan de escalera discreta con saltos y restricción explícita de cardinalidad. |
| T3. Colisión `R_ij` redundancia/distancia física | Aplicado antes de esta pasada | El marco teórico reserva `R_{ij}` para redundancia y usa distancia física separada en las ecuaciones de interacción. |
| T4. Distancia con `beta` sin normalización/ceros | Aplicado en esta pasada | `metodologia.tex` usa ahora `\widehat R_{ij}` y `\widehat I_i`, declara normalización a `[0,1]` con entrenamiento y fija distancia máxima si `\widehat R_{ij}=0`. |
| T5. MDS "refutado" con fuerza excesiva | Aplicado antes de esta pasada | El texto actual dice que los datos no respaldan atribuir la caída al MDS y que no se sostiene como causa geométrica demostrada. |
| T6. Reproducibilidad de QFS-NA sin repetición completa | Aplicado en esta pasada | `resultados.tex` sustituye reproducibilidad por trazabilidad de entradas fijas y declara que no se estimó reproducibilidad completa por no re-ejecutar fase cuántica. |
| T7. 20 permutaciones como "señal clara" | Aplicado antes y afinado ahora | El cuerpo habla de evidencia de cribado compatible con señal; el apéndice muestra `p_min=1/21`. |
| C1. `orquin2026` como evidencia publicada | Aplicado en esta pasada | `estado_arte.tex` y `metodologia.tex` usan "evidencia preliminar" y "cifras preliminares de la referencia". |
| C2. Validación adversarial sin umbral | Aplicado en esta pasada | `resultados.tex` fija el umbral operativo `|AUC-0.5|<0.05` como señal no accionable; metodología y apéndice quedan alineados. |
| E1. Anglicismos | Aplicado parcialmente | Se sustituyeron `paper`, `drivers` y `encoding` no literal. Se conserva `label encoding` por ser denominación técnica concreta. |
| E2. Capitalización de datasets | Aplicado | `Breast Cancer Wisconsin` y `Customer Churn` en metodología. |
| E3. Encabezados y p-valores de tablas | Aplicado | `Vars leakage`; `p_min=1/21` y `p_min=1/501`. |

## Elementos no cerrados por esta pasada

- Verificación externa de `orquin2026`: la bibliografía sigue como
  `@unpublished`, así que el texto se mantiene en tono de referencia preliminar.
  Actualizar a DOI/preprint solo si existe una versión pública.
- Refuerzo local de la hipótesis MDS: no se añaden métricas nuevas de vecinos,
  bloqueo o distorsión local porque requeriría análisis adicional. El texto se
  limita a no atribuir el deterioro al MDS con la evidencia disponible.
- Re-ejecuciones completas de QFS: no se infiere robustez multi-semilla; queda
  como trabajo futuro.

## Verificación pendiente tras esta auditoría

Ejecutar:

```bash
python3 scripts/verify_memoria_figuras.py
cd Plantilla_Latex_GCD/tfgs && conda run -n qfs_env tectonic ejemplo-memoria.tex
```

La verificación debe comprobar que los cambios textuales no rompen referencias ni
compilación.
