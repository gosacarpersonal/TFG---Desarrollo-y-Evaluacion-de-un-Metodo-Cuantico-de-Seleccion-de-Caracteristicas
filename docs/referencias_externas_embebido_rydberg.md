# Fuentes externas: embebido geométrico y radio de bloqueo en QFS

Documentación de las referencias externas (papers oficiales, no contenido de
IA) que respaldan el tratamiento del embebido geométrico de QFS sobre átomos
neutros, en particular la **factibilidad del embebido a radio de bloqueo fijo**
y su **relajación** cuando el grafo de redundancia no es realizable.

Contexto: en la sección 4.4.2 de la memoria, el embebido MDS exige una
distancia mínima entre átomos igual a `dist_ratio · R_b`. El paper de
referencia (orquin2026 / PAPER_QFS) usa `dist_ratio = 1/√2 ≈ 0.707`; este
trabajo la relaja a 0.45 por factibilidad. Estas fuentes documentan **por qué
ese tipo de relajación es necesaria** (no toda matriz de redundancia es un
grafo de discos unitarios) y **cómo lo aborda la literatura**.

## Qué respaldan (y qué no)

- **Respaldan el fenómeno**: que a radio de bloqueo fijo el embebido puede ser
  inviable es un resultado conocido — hallar una realización de grafo de discos
  unitarios (*unit-disk graph*, UDG) es NP-duro y existen grafos sin ninguna
  realización UDG.
- **No respaldan los valores concretos** (0.45/0.35/0.25): ningún paper fija
  esa lista. Los enfoques publicados relajan de forma *principiada* (radio de
  bloqueo local, grafos de discos de radio variable, arrays 3D, átomos
  auxiliares), no bajando un ratio global. La elección de 0.45 es empírica de
  este trabajo.

## Referencias

1. **Nguyen, Liu, Wurtz, Lukin, Wang, Pichler (2023).** *Quantum Optimization
   with Arbitrary Connectivity Using Rydberg Atom Arrays.* PRX Quantum 4(1),
   010316. DOI: 10.1103/PRXQuantum.4.010316. arXiv:2209.03965.
   - Clave bib: `nguyen2023`.
   - Aporta: muestra que no todo grafo es UDG y propone codificar conectividad
     arbitraria con átomos auxiliares; sustenta la limitación de embebido a
     radio fijo.

2. **Bermot, Valor, Coelho, Henry, Pearson (2025).** *Local Rydberg Blockade
   Regimes for Disk Graph Embedding and Quantum Optimization.* arXiv:2506.13228.
   - Clave bib: `bermot2025`.
   - Aporta: *"embedding such graphs requires moving beyond the standard,
     globally uniform blockade model"*; usa radios de bloqueo locales
     (`r_B^L ≈ 0.49 [r_B^G(Ω1)+r_B^G(Ω2)]`) para realizar grafos de discos.
     Es el respaldo más directo de "qué hacer cuando el embebido uniforme no
     es factible".

3. **Ebadi et al. (2022).** *Quantum optimization of maximum independent set
   using Rydberg atom arrays.* Science 376, 1209. (Ya en bibliografía como
   `ebadi2022`.)
   - Aporta: demostración a gran escala (hasta 289 átomos) y dependencia del
     rendimiento respecto de la dureza geométrica de la instancia.

4. **Embedding scheme for the maximum-independent-set problem on 3D
   Rydberg-atom arrays.** Phys. Rev. A.
   https://journals.aps.org/pra/abstract/10.1103/516n-6wtx
   - Aporta: alternativa 3D + reducción de grafo para embeber grafos arbitrarios
     (no citada en la memoria; se conserva aquí como respaldo de contexto).

## Búsquedas realizadas (junio 2026)

- "Rydberg atom array maximum independent set unit disk graph embedding minimum
  distance blockade radius feasibility"
- "neutral atom quantum optimization non-unit-disk graph embedding infeasible
  blockade radius relaxation"

## Valores de separación mínima en la literatura (para referencia)

- `1/√2 ≈ 0.707 · R_b` — orquin2026 (PAPER_QFS), garantiza el umbral de bloqueo.
- `~0.9 · R_b` — Bermot et al. 2025 (separación uniforme experimental).
- `0.45 · R_b` — este trabajo (más permisivo que cualquiera de los anteriores).
