# Plan operativo de poda visual — Resultados

> Plan derivado de `auditoria_visual_profunda_2026-06-18.md` y
> `lectura_sin_figuras_resultados_2026-06-18.md`. No aplica cambios todavía a
> `resultados.tex`; define una intervención segura para que el cuerpo deje de
> parecer una sucesión de outputs.

## 1. Objetivo de la poda

Pasar de 18 figuras en `resultados.tex` a una versión de 8--9 figuras
argumentales. Las figuras retiradas no se eliminan del repositorio: se mueven al
apéndice o quedan como evidencia disponible.

La poda busca comprobar si el capítulo respira mejor antes de invertir tiempo en
rediseñar.

## 2. Versión recomendada

### Opción A: severa, 8 figuras de Resultados

Mantener en cuerpo:

1. `F01_banco_regimenes.pdf`
2. `F02_senal_fdr_efecto.pdf`
3. `F04_perfil_selectores.pdf`
4. `F07_significancia_magnitud.pdf`
5. `F06_shap_beeswarm_instancias.pdf`
6. `qfs_organismo_cuantico.pdf`
7. `F09_atribucion_criterio_optimizador.pdf`
8. `F10_comparacion_final_clasico_qfs.pdf`

Mover al apéndice:

- `F03_base_confiable.pdf`
- `f10_a_regimenes_dataset.png`
- `o1_organismo_seleccion.png`
- `f5_coste_rendimiento.png`
- `ev6_rendimiento_vs_k.png`
- `f10_b4_escalera_alpha.png`
- `f10_b5_beta_geometria.png`
- `f10_b9_atomos_mds_error.png`
- `f10_b10_consistencia.png`

### Opción B: equilibrada, 9 figuras de Resultados

Igual que la opción A, pero mantiene `F03_base_confiable.pdf` en cuerpo. Es la
opción recomendada si se quiere que el tribunal vea explícitamente la auditoría
de datos sin saltar al apéndice.

## 3. Cambios concretos en `resultados.tex`

### 3.1. Banco y confianza

Eliminar del cuerpo el bloque de figura:

- `f10_a_regimenes_dataset.png`
- label actual: `fig:f10-regimenes`

Reescritura necesaria:

- Cambiar "La Tabla ... y la Figura ..." por "La Tabla ... resume...".
- Conservar la explicación dataset por dataset, que ya funciona sin esa figura.

Si se adopta opción A:

- mover también `F03_base_confiable.pdf` al apéndice;
- reemplazar la referencia a Figura `fig:adversarial` por referencia a tabla y
  apéndice.

Si se adopta opción B:

- mantener `F03_base_confiable.pdf` en cuerpo.

### 3.2. Selección clásica

Mantener:

- `F04_perfil_selectores.pdf`
- label: `fig:perfil-selectores`

Retirar del cuerpo:

- `o1_organismo_seleccion.png`
- `f5_coste_rendimiento.png`
- `f10_b10_consistencia.png`

Reescrituras necesarias:

- Convertir el párrafo de `o1_organismo_seleccion` en una referencia al apéndice:
  "El mapa completo de Madelon se conserva en el apéndice...".
- Cambiar el cierre de la figura `f5_coste_rendimiento`, que ahora remite a
  `fig:rendimiento-k`, porque `ev6` también bajaría al apéndice.
- En `Comparación final y mapa de evidencia`, sustituir:
  `Figuras~\ref{fig:perfil-selectores} y~\ref{fig:coste-rendimiento}`
  por una referencia a `fig:perfil-selectores` y al apéndice.

### 3.3. Modelado e interpretabilidad

Mantener:

- `F07_significancia_magnitud.pdf`
- `F06_shap_beeswarm_instancias.pdf`

No mover todavía `F06`; primero conviene rediseñarla. Si no se rediseña, debe
bajar al apéndice en una segunda ronda.

### 3.4. QFS

Mantener:

- `qfs_organismo_cuantico.pdf`
- `F09_atribucion_criterio_optimizador.pdf`
- `F10_comparacion_final_clasico_qfs.pdf`

Retirar del cuerpo:

- `F08_mandos_qfs_alpha_beta.pdf` solo en la versión más agresiva.

Recomendación: mantener `F08` por ahora, pero como candidata a rediseño/fusión.
Si se mantiene `F08`, las figuras `f10_b4` y `f10_b5` deben bajar al apéndice.

Retirar del cuerpo:

- `ev6_rendimiento_vs_k.png`
- `f10_b4_escalera_alpha.png`
- `f10_b5_beta_geometria.png`
- `f10_b9_atomos_mds_error.png`

Reescrituras necesarias:

- La sección que introduce `ev6` puede quedar como párrafo con referencia al
  apéndice.
- La explicación de `alpha` puede mantenerse textual y apuntar a una figura de
  apéndice.
- La explicación de `beta` puede mantenerse textual y apuntar a una figura de
  apéndice.
- La comprobación MDS puede mantenerse con la tabla `tab:embedding` y una
  referencia al apéndice.

### 3.5. Consistencia

Retirar del cuerpo:

- `f10_b10_consistencia.png`

Reescritura necesaria:

- Mantener el párrafo de consistencia con referencia a `tab:perfil` y al apéndice.
- Quitar la figura autónoma del cuerpo.

## 4. Cambios concretos en `apendice.tex`

Añadir una subsección nueva o ampliar `Solapes, métricas secundarias y
consistencia` para incluir las figuras movidas:

- `fig:ap-regimenes` -> `f10_a_regimenes_dataset.png`
- `fig:ap-organismo-seleccion` -> `o1_organismo_seleccion.png`
- `fig:ap-redundancia-k` -> `f5_coste_rendimiento.png`
- `fig:ap-rendimiento-k` -> `ev6_rendimiento_vs_k.png`
- `fig:ap-alpha` -> `f10_b4_escalera_alpha.png`
- `fig:ap-beta` -> `f10_b5_beta_geometria.png`
- `fig:ap-atomos-mds` -> `f10_b9_atomos_mds_error.png`
- `fig:ap-consistencia` -> `f10_b10_consistencia.png`

Si se elige opción A, añadir también:

- `fig:ap-base-confiable` -> `F03_base_confiable.pdf`

Modificar el cierre actual de `apendice.tex`, que dice:

```tex
El error de embebido MDS y la consistencia global se mantienen en el
cuerpo de resultados ...
```

Nueva idea:

```tex
El error de embebido MDS, la sensibilidad de alpha/beta y la consistencia
global se conservan aquí como atlas de evidencia para no sobrecargar el
cuerpo de resultados.
```

## 5. Riesgos de la poda

1. **Referencias rotas**: habrá que sustituir labels `fig:*` del cuerpo por
   nuevos labels `fig:ap-*` si las figuras se mueven.
2. **Captions duplicadas**: al mover figuras, no conviene copiar captions sin
   ajustar su función; en apéndice deben explicar qué afirmación del cuerpo
   auditan.
3. **Cuerpo demasiado seco**: si se elige opción A y baja también `F03`, el
   capítulo puede perder una señal visible de auditoría. Por eso la opción B es
   más equilibrada.
4. **Figuras sin rediseñar**: mover no arregla la calidad visual de las
   supervivientes. La poda solo despeja el campo.

## 6. Verificación tras aplicar

Comandos mínimos:

```bash
python3 scripts/verify_memoria_figuras.py
cd Plantilla_Latex_GCD/tfgs && conda run -n qfs_env tectonic ejemplo-memoria.tex
```

Comprobaciones editoriales manuales:

- `resultados.tex` debe tener 8--9 figuras, no 18.
- Ninguna figura de cuerpo debe existir solo como "detalle".
- Todo lo movido al apéndice debe estar referenciado desde el cuerpo.
- El apéndice debe leerse como atlas, no como carpeta de outputs.

## 7. Recomendación final

Aplicar primero la opción B: 9 figuras en Resultados. Es una poda fuerte pero no
deja la memoria sin auditoría visual. Después de compilar y leer, decidir si
`F03` también baja al apéndice.

La secuencia más segura es:

1. poda de cuerpo;
2. compilación;
3. lectura del PDF podado;
4. rediseño de supervivientes (`F09`, `F10`, organismo QFS, `F04`, `F01/F02`,
   `F06`);
5. reorganización estética del apéndice.

## 8. Poda aplicada como prueba editorial

Tras la primera aplicación se eligió una variante ligeramente más conservadora:
10 figuras en `resultados.tex`, manteniendo también `F08_mandos_qfs_alpha_beta`
porque el texto de QFS necesita separar visualmente `alpha` y `beta` antes de
entrar en la atribución criterio--optimizador.

Figuras que quedan en cuerpo:

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

Figuras movidas al apéndice con labels nuevos:

- `f10_a_regimenes_dataset.png` -> `fig:ap-regimenes`
- `o1_organismo_seleccion.png` -> `fig:ap-organismo-seleccion`
- `f5_coste_rendimiento.png` -> `fig:ap-redundancia-k`
- `ev6_rendimiento_vs_k.png` -> `fig:ap-rendimiento-k`
- `f10_b4_escalera_alpha.png` -> `fig:ap-alpha`
- `f10_b5_beta_geometria.png` -> `fig:ap-beta`
- `f10_b9_atomos_mds_error.png` -> `fig:ap-atomos-mds`
- `f10_b10_consistencia.png` -> `fig:ap-consistencia`

Verificación aplicada:

```bash
python3 scripts/verify_memoria_figuras.py
cd Plantilla_Latex_GCD/tfgs && conda run -n qfs_env tectonic ejemplo-memoria.tex
```

Resultado:

- `verify_memoria_figuras.py`: `OVERALL: PASS`.
- Tectonic: escribe `ejemplo-memoria.pdf`.
- Conteo tras poda: 10 figuras en `resultados.tex` y 19 en `apendice.tex`.
- Se eliminaron los avisos por guiones largos Unicode en los `.tex`.
