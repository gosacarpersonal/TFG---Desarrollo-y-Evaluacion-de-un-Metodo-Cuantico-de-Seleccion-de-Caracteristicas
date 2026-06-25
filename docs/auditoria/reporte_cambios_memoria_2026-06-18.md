# Reporte de cambios aplicados a la memoria — 2026-06-18

Ejecución del encargo: aplicar **toda** la lista del autor + los 10 patrones
detectados en `auditoria_redaccion_memoria_2026-06-18.md`, compilar el PDF y
dejar el repositorio listo para push.

PDF compilado con **tectonic** (entorno `qfs_env`): `ejemplo-memoria.pdf`,
83 páginas, **EXIT 0**, sin referencias sin resolver. Todas las cifras nuevas
proceden de los CSV canónicos de `results/tables/` (verificadas, no inventadas).

Balance de evidencia tras la intervención:
- **Resultados: de 3 a 12 tablas** (20 figuras) — se invierte el desequilibrio
  "todo figuras, sin tablas".
- **Marco teórico: de 0 a 2 figuras** (diagramas conceptuales).
- Cuerpo total: **15 tablas** (antes 5).

---

## 1. Marco teórico (`marco_teorico.tex`)
- **§2.3 Diagrama de evolución adiabática** (TikZ, Fig. 2.1): niveles $E_0/E_1$,
  gap mínimo $\Delta_{\min}$, $H_{\text{inicial}}\to H_{\text{final}}$.
- **§2.4 Diagrama del bloqueo de Rydberg** (TikZ, Fig. 2.2): radio de bloqueo,
  átomo excitado/bloqueado/lejano, conexión con el MWIS.
- **§2.5** se definen ahora los contrastes en el punto de uso (Mann--Whitney,
  Kruskal--Wallis, $\chi^2$, **Spearman** —antes nunca definido—, KS, Wasserstein,
  PSI) y se añaden **forward-references** a las tablas de resultados que cobran
  cada salvaguarda (Tablas \ref{tab:senal}, postproc, particiones, cadena-tests).

## 2. Estado del arte (`estado_arte.tex`)
- **§3.4**: recortada la letanía de garantías redundante (ya estaba en la
  introducción). El hueco se enuncia sin repetir la solución.

## 3. Metodología (`metodologia.tex`)
- **§4.4.2**: forward-reference a la Tabla de control QFS y a la de atribución
  (§5.5), que es donde se demuestra el "separar dos preguntas".
- **§4.5**: **eliminada la figura del recorrido de 10 fases** (duplicaba la
  lista enumerada inmediatamente posterior).
- **§4.5.3**: forward-reference a la tabla de auditoría de particiones (§5.1.3).
- **§4.5.5 (Entorno)**: condensada a una frase que remite al apéndice
  (eliminada la duplicación con §A.1/§A.2).

## 4. Resultados (`resultados.tex`) — el grueso
Tablas nuevas (todas desde CSV canónicos):
| Tabla | Sección | Contenido |
|---|---|---|
| `tab:senal` | §5.1.1 | señal univariante y redundancia por conjunto (FDR, efecto, pares $\rho$) |
| `tab:postproc` | §5.1.2 | invarianza del preprocesado (Spearman, KS/Wass/PSI, $\Delta$MI) |
| `tab:particiones` | §5.1.3 | auditoría de las 5 particiones (drift, PSI, AUC adversarial, leakage) |
| `tab:regimenes` | §5.1.4 | regímenes (efecto, VIF, vars VIF≥10, PCA-80%) |
| `tab:perfil` | §5.2.1 | perfil de los 12 selectores (Jaccard, redundancia, coste) |
| `tab:candidatos` | §5.2.2 | candidatos por dataset×modelo (F1, bal.acc, AUC, vars) |
| `tab:embedding` | §5.4 | error MDS por formulación al β elegido |
| `tab:atribucion` | §5.5 | **descomposición criterio/optimizador** (prioridad nº1) |
| `tab:cadena-tests` | §5.6 | cadena de controles → confusor → evidencia |

Otros cambios:
- **Trivialidades eliminadas** ("se cargan íntegros", "sin fallos", "170/260
  ejecuciones sin fallos").
- **Jaccard** se recuerda en el punto de uso ("solape entre subconjuntos de
  semillas distintas").
- **§5.2.2**: párrafo nuevo que **nombra las variables** de los subconjuntos
  ganadores (churn, olive 3/9, BCW, madelon) y remite al roster del apéndice.
- **§5.2.3 y §5.4**: el cierre se hace sobre las **cuatro coordenadas**
  (rendimiento, redundancia, estabilidad, coste), no solo rendimiento.
- **§5.2.4**: reescrito el arranque para declarar su propósito (situar QFS
  *antes* de medir su F1; QFS-NA se anticipa aquí y se detalla en §5.3).
- **§5.3**: las "8 / 15 variables" se nombran y se enlazan con §5.1.4; caption de
  la Tabla de control reescrito para ser autoexplicativo (Hamming, signo de Δ).
- **Purga de "fase N"**: 16 fugas de andamiaje eliminadas en resultados y
  conclusiones (traducidas a lenguaje de contenido).
- **Captions con forma corta** en figuras/tablas con math (arreglan además un
  fallo de compilación al volcarse al índice).

### Corrección factual NUEVA (fuera del audit de redacción)
La **Tabla 5.2 (control QFS)** y dos cifras de Δcoste en prosa estaban
**obsoletas** (era `dist_ratio=0.45`); los macro-F1 sí estaban a 1/√2. Se han
regenerado desde `qfs_quality_control_*.csv` al β seleccionado por validación:

| Dataset | Antes (H / Δ) | Ahora (H / Δ, 1/√2) |
|---|---|---|
| Breast Cancer W. | 6 / −1.270 | 6 / −4.399 |
| Customer Churn | 6 / +0.622 | 6 / +1.194 |
| Madelon | 4 / −0.059 | 2 / −0.008 |
| Olive Oil (3 cl.) | 2 / −0.165 | 2 / −0.165 |
| Olive Oil (9 cl.) | 4 / +0.903 | 2 / +0.164 |

La **narrativa cualitativa se conserva**: Churn Δ>0 (déficit de optimizador),
Madelon Δ≈0 (no es el optimizador). Prosa de §5.4 actualizada en consecuencia.

## 5. Conclusiones (`conclusiones.tex`)
- Condensada la **re-narración verbatim** de cifras de Madelon/Churn → ahora
  remite a `tab:atribucion` y `tab:embedding`.
- Dedup de "no actúa como simple baseline".

## 6. Infraestructura (`ejemplo-memoria.tex`)
- `\usepackage{multirow}` (tabla de candidatos), `\usetikzlibrary{babel}`,
  arreglos TikZ para babel-spanish (flechas con tips `latex`, curvas con
  `plot[smooth]` para evitar el conflicto `..` ↔ shorthand de spanish).

---

## Pendiente menor (no bloqueante)
- Dos `Overfull \hbox` de 60–72 pt en las páginas de las figuras F01/F02
  (volcados de tablas en PNG, preexistentes); no afectan a las tablas nuevas,
  que se verificaron una a una dentro de márgenes.
- Las matrices de confusión se describen en texto pero no se grafican; se dejó
  como está (no se promete figura).
