# Reporte de ejecución — reequilibrio cuántico de la memoria (2026-06-18)

Ejecución de `plan_reequilibrio_cuantico_2026-06-18.md` (dos ejes: contenido
cuántico↔clásico + capa visual). PDF compilado con **tectonic** en `qfs_env`,
85 páginas, EXIT 0, sin referencias rotas.

## Resultado medido (capítulo de Resultados, palabras de cuerpo)
| | Antes | Después |
|---|---|---|
| Clásico | 3 299 (64 %) | 2 796 (52 %) |
| **Cuántico + comparativa** | **1 365 (27 %)** | **2 133 (39 %)** |
| Discusión | 480 (9 %) | 481 (9 %) |

El bloque cuántico (2 133) es ya la **mayor sección individual** del capítulo;
el clásico es la suma de dos secciones preparatorias, ninguna mayor que el
bloque cuántico. El % se trató como termómetro, no meta (condición del revisor):
no se infló texto ni se vació la referencia clásica.

## Eje 1 — contenido
- **Marco §2.3** (adiabática): expansión acotada (gap mínimo, condición
  adiabática, conexión con Ω/Δ/detuning local). Sin convertirlo en física.
- **§5.3.1 NUEVA — "El mecanismo de QFS sobre el banco"** + **figura del
  organismo cuántico** (Figura 5.10): 5 paneles, átomos en posición MDS, color =
  densidad de Rydberg, anillo = seleccionado. Construida desde datos verificados
  (`positions_json` + `density__<var>`), reproducible en
  `scripts/fig_organismo_cuantico.py`. Reglas de legibilidad estrictas (color +
  anillo + etiqueta solo en seleccionados, leyenda y colorbar comunes).
- **§5.3** evaluación cuántica reorganizada en subsecciones (mecanismo / mandos y
  control).
- **§5.4** absorbe el antiguo §5.2.4 ("espejo de QFS", que estaba mal ubicado
  antes de presentar QFS); comparación leída en las **4 coordenadas**; dos tablas
  nuevas: robustez del veredicto por modelo (`tab:qfs-robustez`) y solape
  NA/oráculo/mRMR (`tab:qfs-solape`).
- **§5.5** ampliada con el diagnóstico por densidad (Churn = readout deja
  `tenure`/`last_interaction` con densidad baja; Madelon = densidad alta correcta
  pero criterio plano), atado a la figura del organismo.
- Condensada la prosa clásica más mecánica (§5.2.1 coste, §5.2.2 "patrón
  consistente") sin tocar veredictos ni regímenes.

## Eje 2 — capa visual
- **`booktabs` + `tabularx`** adoptados; 16 tablas convertidas a
  `\toprule/\midrule/\bottomrule`.
- **Cuerpo = tablas de veredicto** (7): comparacion, qfs-comparacion, qfs-control,
  qfs-robustez, qfs-solape, atribucion, regimenes. **Apéndice = densas** (9):
  senal, postproc, particiones, perfil, candidatos, embedding, cadena-tests,
  qfs-modelos + trazabilidad. Todas **referenciadas inline** desde el cuerpo.
- **Figura 5.19 (cadena de tests) eliminada**: su contenido ya vive en
  `tab:cadena-tests` (tabla legible) — justo lo que pedía la revisión.
- **Tabla A.1 (trazabilidad) rediseñada**: de "CSV en papel" (3 columnas con
  rutas y prosa) a `tabularx` de 2 columnas (bloque → artefacto).
- `tab:candidatos` compactada (se quitó la columna bal.\ acc., `\footnotesize`).
- Captions con forma corta donde llevan math.

## Verificación
- Compila EXIT 0; refs resuelven. Revisión visual: organismo cuántico (pág. 56),
  mandos/control con Δcoste canónicos (pág. 57), tablas de veredicto en márgenes.
- 4 `Overfull \hbox` (29–72 pt) **preexistentes** en las figuras-volcado F01/F02;
  no afectan a las tablas nuevas (verificadas en márgenes).

## Pendiente menor
- Las figuras horizontales antiguas (`f10_b*`, `explor_*`) se movieron al apéndice
  pero no se rediseñaron; quedan como apoyo referenciado.
