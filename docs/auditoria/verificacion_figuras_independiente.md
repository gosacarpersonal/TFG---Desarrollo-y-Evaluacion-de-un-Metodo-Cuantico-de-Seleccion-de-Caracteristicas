# Verificación independiente de las figuras de Codex (foco: omisión de información)

> 2026-06-15. Revisión propia (código + inspección visual de los PNG renderizados) del
> trabajo de Codex sobre las figuras de la memoria. Foco: que ninguna figura compare un
> subconjunto cuando debería cubrir todo (datasets/métodos/modelos). El "todo OK" del
> verificador de Codex es técnico (existen, DPI, rutas); NO detecta omisión de contenido.

## Veredicto: hay omisiones reales. La principal es justo la que temías.

### Problemas (con evidencia visual)

1. **F6 SHAP — solo 2 de 5 datasets [GRAVE, tu preocupación exacta].** El beeswarm pinta
   únicamente Breast Cancer y Madelon (`build_memoria_figuras.py:395-396`, hardcodeado).
   Faltan customer_churn, olive_oil_3class y olive_oil_9class. Codex siguió la spec
   ("2 representativos"), pero el resto del SHAP no se muestra.
2. **A4 — el "resto" del SHAP tampoco está [GRAVE].** A4 debía ser concordancia
   SHAP↔selección↔fase 1 + beeswarm por clase en olive. En realidad es una **barra de la
   suma de las 5 importancias top por dataset** (`figure_a4`), un agregado sin
   interpretación. → El SHAP de churn/olive no aparece en NINGUNA figura de la memoria.
3. **F3 Panel C — conservación con olive vacío (3 de 5).** La tabla de fase 3 usa la clave
   `olive_oil` (sin separar) y la figura reindexa a `olive_oil_3class/9class`, así que
   ambas filas de olive salen vacías. Omite la conservación de olive.
4. **A8 — no responde la pregunta.** "Solape QFS vs clásicos" debía mostrar QUÉ variables
   comparten; muestra el **tamaño** de los subconjuntos por configuración. No hay solape.
5. **A9 — incompleta.** "Macro-F1 vs AUC en binarios" muestra **solo AUC**; falta el
   contraste con macro-F1 que justifica la elección de métrica.
6. **Menores:** F10 omite los IC bootstrap que la spec pedía (puntos sin barras de error);
   F4 panel D tiene la barra de color descuadrada respecto a los valores anotados; A6
   reduce el handoff a medias I_i/R_ij (pierde la estructura de matriz).

### Lo que SÍ está bien (verificado por imagen y código)

- **Cobertura completa y composición limpia:** F1, F2 (4 filas = realidad de fase 1, olive
  aún sin separar — correcto), F3 paneles A/B, **F4** (12 métodos, 2×2, leyenda única,
  panel D honesto sobre que la permutación solo aplica a filtros de relevancia), F5 (5
  datasets), F7, F8 (5 datasets en panel A), **F9** (5 datasets, cuadrantes claros), F10 (5
  datasets, 4 series).
- **Integración LaTeX correcta:** las 10 figuras nuevas referenciadas en `resultados.tex`,
  A1-A9 en `apendice.tex`, sin restos de las figuras antiguas; la memoria compila.

## Patrón del fallo

Codex omite/degrada justo donde (a) la spec decía "representativo" y lo tomó literal (F6),
(b) un desajuste de clave silencioso tira filas (F3-C olive), y (c) la figura de apéndice
era más difícil y cayó en un agregado trivial (A4, A8, A9). Tu principio se cumple al
revés: las conclusiones pueden centrarse en unos datasets, pero las **figuras no deben
omitir** el resto. Aquí sí omiten.

## Correcciones propuestas

- **F6:** convertir en small multiples de **los 5 datasets** (un beeswarm por dataset, mejor
  candidato de cada uno); olive por clase → A4.
- **A4:** rehacer como concordancia real (SHAP top-k vs selección vs asociación fase 1) y/o
  beeswarm por clase de olive_3/9. Eliminar la barra-suma.
- **F3-C:** mapear la clave `olive_oil` de fase 3 a las dos formulaciones (o mostrar olive
  combinado y anotarlo) para que no queden filas vacías.
- **A8:** matriz binaria/solape real de variables QFS vs Boruta/mRMR.
- **A9:** barras agrupadas macro-F1 vs AUC en los dos binarios.
- **Menores:** añadir IC en F10; corregir la escala de color del panel D de F4.

## Cómo proceder
Estas correcciones requieren rebuild + re-verificación visual (el mismo bucle). Se pueden
hacer aquí directamente o devolver a Codex con un prompt corregido que (1) prohíba
explícitamente subsetear datasets/métodos en cualquier figura salvo declaración expresa,
(2) exija que cada figura de apéndice responda su pregunta (no un agregado), (3) verifique
por imagen la COBERTURA (nº de datasets/series presentes), no solo la existencia.
