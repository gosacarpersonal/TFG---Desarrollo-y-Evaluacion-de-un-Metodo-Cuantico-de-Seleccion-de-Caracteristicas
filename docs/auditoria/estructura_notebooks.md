# Estructura canónica de los notebooks (referencia obligatoria)

> La estructura **correcta** es la de los notebooks de las fases 1-4. Todo arreglo o
> regeneración de cualquier fase debe respetar este patrón. La fase 4 es el ejemplo de
> referencia mejor ejecutado.

## Patrón por sección

1. **Markdown explicativo de la sección** + explicación de *todo lo que se usa* (qué
   método, qué parámetro, por qué). El lector entiende antes de ver código.
2. **Chunks de creación/importación de funciones.** Se *crea* la función (visible, con
   `def`) o se *importa* si ya existe. En las fases serias (5-7) el núcleo metodológico
   debe poder verse construirse, no solo invocarse (ver "Regla para fases pesadas").
3. **Markdown con el título del dataset** (`### <dataset>`).
4. **Aplicación de las funciones a ese dataset** + salidas + tablas.
5. **Visualización** — solo si facilita entender las tablas o aporta más narrativa que
   ellas. Si la figura duplica la tabla, sobra.
6. **Markdown explicativo de qué ha ocurrido en ese dataset** (uno por dataset).
7. (Repetir 3-6 por cada dataset.)
8. **Markdown de resumen/comparación de la sección.**
9. **Aplicación de las funciones a toda la sección** + salidas + tablas + visualización
   de conjunto.

## Regla para fases pesadas (5, 6, 7)

El motivo de que las fases 5 y 6 sean largas y con mucha carga (12 selectores;
modelado + bootstrap 400 + permutaciones 2000/500 + SHAP) es justo lo que hace que la
**transparencia importe más**, no menos. Hoy esas fases conservan la narrativa por
dataset y la lectura por figura —eso está bien—, pero el paso 2 está colapsado: el
núcleo metodológico vive entero en `src/` y el cuaderno solo llama a `fs.*`, `p6.*`,
`f7.*`. En las fases donde el método ES la contribución, el lector debe poder ver cómo se
construye.

- **Sí debe verse en el cuaderno (creación visible):** la lógica que constituye el aporte
  — los selectores espejo de QFS, el cálculo de relevancia/redundancia, el protocolo de
  contraste (bootstrap, permutaciones), el cálculo SHAP. Aunque alargue el cuaderno.
- **Puede importarse de `src` (plumbing):** E/S, guardado de tablas/figuras, formateo de
  presentación, utilidades repetidas.

La longitud no es el problema; esconder la maquinaria del aporte sí lo es.

## Estado de cumplimiento (medido 2026-06-14)

| Fase | Estructura por sección | Narrativa por dataset | Paso 2 (funciones visibles) |
|---|---|---|---|
| 1-3 | ✅ | ✅ | ✅ (creación inline) — **correcto, no tocar** |
| 4 | ✅ (referencia) | ✅ | ✅ |
| 5 | ✅ | ✅ (5.9 por dataset) | ⚠️ núcleo en `src` (`fs.*`) |
| 6 | ✅ | ✅ (6.6 por dataset) | ⚠️ núcleo en `src` (`p6.*`) |
| 7 | ✅ | ✅ (7.4 por dataset) | ⚠️ núcleo en `src` (`f7.*`) |

Conclusión: el único defecto estructural transversal es el **paso 2 en 5-7** (núcleo
metodológico no visible). NO hay déficit de narrativa por dataset. La "asimetría
narrativa" que sugería una auditoría previa era falsa.
