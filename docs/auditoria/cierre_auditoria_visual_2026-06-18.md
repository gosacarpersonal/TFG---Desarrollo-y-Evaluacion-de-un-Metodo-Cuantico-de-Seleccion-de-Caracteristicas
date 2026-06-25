# Cierre de auditoría visual — 2026-06-18

## Objetivo atendido

El objetivo era auditar en profundidad las visualizaciones de la memoria,
entender por qué el sistema visual resultaba desagradable, probar la hipótesis de
leer la memoria "a secas" y replantear qué figuras son necesarias.

## Evidencia creada

1. `docs/auditoria/auditoria_visual_profunda_2026-06-18.md`
   - Inventario visual.
   - Diagnóstico del malestar.
   - Auditoría figura por figura.
   - Primera clasificación: conservar, rediseñar, mover a apéndice o eliminar.

2. `docs/auditoria/lectura_sin_figuras_resultados_2026-06-18.md`
   - Lectura de `resultados.tex` sin asumir que las figuras actuales son
     necesarias.
   - Identificación de afirmaciones que necesitan figura de cuerpo.
   - Nuevo mapa mínimo de figuras.

3. `docs/auditoria/plan_poda_visual_resultados_2026-06-18.md`
   - Plan operativo de poda.
   - Variante aplicada.
   - Lista de figuras mantenidas en cuerpo.
   - Lista de figuras movidas al apéndice.
   - Verificación ejecutada.

## Decisión editorial aplicada

Se aplicó una poda conservadora: `resultados.tex` pasa de 18 figuras a 10.

Figuras que permanecen en el cuerpo de Resultados:

1. `F01_banco_regimenes.pdf`
2. `F02_senal_fdr_efecto.pdf`
3. `F03_base_confiable.pdf`
4. `F04_perfil_selectores.pdf`
5. `F07_significancia_magnitud.pdf`
6. `F06_shap_beeswarm_instancias.pdf`
7. `qfs_organismo_cuantico.pdf`
8. `F08_mandos_qfs_alpha_beta.pdf`
9. `F09_atribucion_criterio_optimizador.pdf`
10. `F10_comparacion_final_clasico_qfs.pdf`

Figuras movidas al apéndice con nuevos labels:

- `f10_a_regimenes_dataset.png` -> `fig:ap-regimenes`
- `o1_organismo_seleccion.png` -> `fig:ap-organismo-seleccion`
- `f5_coste_rendimiento.png` -> `fig:ap-redundancia-k`
- `ev6_rendimiento_vs_k.png` -> `fig:ap-rendimiento-k`
- `f10_b4_escalera_alpha.png` -> `fig:ap-alpha`
- `f10_b5_beta_geometria.png` -> `fig:ap-beta`
- `f10_b9_atomos_mds_error.png` -> `fig:ap-atomos-mds`
- `f10_b10_consistencia.png` -> `fig:ap-consistencia`

## Diagnóstico del malestar visual

El rechazo del autor estaba justificado. El problema no era falta de rigor ni que
todas las figuras fueran falsas, sino una mezcla de:

- saturación del cuerpo;
- figuras de evidencia granular colocadas como si fueran argumento principal;
- tres lenguajes visuales coexistiendo;
- figuras que compiten por la misma función;
- exceso de huella del proceso experimental dentro del capítulo de resultados.

La solución madura no es una memoria sin figuras. Es un cuerpo con pocas figuras
argumentales y un apéndice que funcione como atlas de evidencia.

## Estado verificado

Comandos ejecutados:

```bash
python3 scripts/verify_memoria_figuras.py
cd Plantilla_Latex_GCD/tfgs && conda run -n qfs_env tectonic ejemplo-memoria.tex
```

Resultados:

- `verify_memoria_figuras.py`: `OVERALL: PASS`.
- Tectonic: genera `Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf`.
- Conteo actual:
  - `resultados.tex`: 10 figuras.
  - `apendice.tex`: 19 figuras.
- No quedan referencias a los labels antiguos movidos del cuerpo:
  - `fig:f10-regimenes`
  - `fig:organismo-seleccion`
  - `fig:coste-rendimiento`
  - `fig:rendimiento-k`
  - `fig:f10-alpha`
  - `fig:f10-beta`
  - `fig:f10-atomos`
  - `fig:f10-consistencia`

## Trabajo posterior recomendado

La auditoría y la poda están cerradas. El siguiente trabajo ya no es auditoría,
sino rediseño visual de las supervivientes:

1. `F09_atribucion_criterio_optimizador.pdf`
2. `F10_comparacion_final_clasico_qfs.pdf`
3. `qfs_organismo_cuantico.pdf`
4. `F04_perfil_selectores.pdf`
5. `F06_shap_beeswarm_instancias.pdf`
6. `F01/F02` si se decide fusionar o simplificar la apertura.

Ese rediseño debe hacerse desde fuentes primarias y no desde gusto abstracto.
