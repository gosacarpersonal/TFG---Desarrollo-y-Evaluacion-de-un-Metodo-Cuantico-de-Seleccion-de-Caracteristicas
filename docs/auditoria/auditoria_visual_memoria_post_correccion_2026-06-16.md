# Auditoria visual de la memoria tras correcciones formales

Fecha: 2026-06-16.

Estado auditado:

- PDF compilado: `Plantilla_Latex_GCD/tfgs/ejemplo-memoria.pdf`.
- Figuras de cuerpo: 20 en `Plantilla_Latex_GCD/tfgs/tex/resultados.tex`.
- Figuras de apendice: 9 en `Plantilla_Latex_GCD/tfgs/tex/apendice.tex`.
- Verificador global nuevo: `python scripts/verify_memoria_figuras.py`.
- Hojas de contacto generadas para inspeccion:
  - `docs/auditoria/_visual_audit_assets/body_contact_sheet.jpg`
  - `docs/auditoria/_visual_audit_assets/appendix_contact_sheet.jpg`
  - `docs/auditoria/_visual_audit_assets/pdf_contact_sheet.jpg`

## 1. Resultado ejecutivo

La memoria ya no tiene un problema de ausencia de visualizaciones ni de
trazabilidad basica. Las figuras existen, tienen caption, estan referenciadas,
no estan duplicadas entre cuerpo y apendice y el PDF compila. El problema real
es de jerarquia:

> El cuerpo de resultados contiene mas figuras de las que necesita para
> defender la tesis principal.

La secuencia F1--F10 funciona como arquitectura argumental. Sin embargo, se han
subido al cuerpo varias figuras mecanisticas de fase 10 que son utiles, pero no
todas tienen el mismo rango narrativo. Un tribunal exigente puede leer esa zona
como inventario visual: alpha, beta, embebido, cadena de tests, consistencia,
Jaccard, mapa de metodos, trayectoria en k. Todas aportan, pero juntas reducen
la fuerza de la figura central: `diag_atribucion_qfs.png`.

Recomendacion general:

- Mantener en cuerpo las figuras que responden preguntas de defensa global.
- Mover a apendice las figuras que preservan trazabilidad o mecanismo local.
- No regenerar figuras salvo que se decida una nueva composicion; el problema
  principal es seleccion/ubicacion, no calidad tecnica.

## 2. Evidencia objetiva

Verificador global:

- `labels`: 63
- `refs`: 50
- `graphics`: 34
- `figure_blocks`: 31
- referencias rotas: 0
- graficos faltantes: 0
- figuras sin caption: 0
- figuras sin label: 0
- captions cortas: 0
- graficos duplicados: 0

Compilacion:

- `conda run -n qfs_env tectonic ejemplo-memoria.tex` genera PDF.
- No quedan `Overfull \hbox`.
- Persisten `Underfull \vbox` en paginas con saltos/figuras. Esto no rompe la
  memoria, pero confirma que la maquetacion esta al limite en zonas visuales.

Dimensiones:

- Todas las figuras tienen resolucion suficiente.
- Riesgo de legibilidad por formato panoramico:
  - `explor_mapa_metodos.png` aspect ratio 4.20.
  - `f10_b9_atomos_mds_error.png` aspect ratio 3.60.
  - `f10_b8_cadena_tests.png` aspect ratio 3.41.
  - `f10_b2_jaccard_12_metodos.png` aspect ratio 2.81.
  - `f10_b5_beta_geometria.png` aspect ratio 2.81.

## 3. Veredicto por figura de cuerpo

| Figura | Archivo | Veredicto | Razon |
|---|---|---|---|
| F1 | `f1_banco.png` | Mantener cuerpo | Abre el banco, justifica diversidad y macro-F1. |
| F2 | `f2_senal_fdr_efecto.png` | Mantener cuerpo | Anticipa el fallo de criterio en Madelon; esencial. |
| F3 | `f3_base_confiable.png` | Mantener cuerpo | Blinda datos, splits y preprocesado. |
| Regimenes | `f10_a_regimenes_dataset.png` | Mantener o fusionar texto | Es buena como puente hacia QFS, pero duplica parcialmente F1--F3. Mantener si el texto la usa para predecir mecanismos. |
| F4 | `f4_perfil_selectores.png` | Mantener cuerpo | Justifica los doce selectores como sistema de coordenadas. |
| O1 | `o1_organismo_seleccion.png` | Mantener con cautela | Muy potente para Madelon, pero densa. Se justifica porque explica el frente de consenso y los distractores. |
| F5 | `f5_coste_rendimiento.png` | Mantener si se lee como redundancia vs k | La caption ya corrige que no es rendimiento. Sirve como mecanismo, no cierre. |
| F7 | `f7_significancia_magnitud.png` | Mantener cuerpo | Figura de honestidad estadistica; esencial. |
| F6 | `f6_shap_variables.png` | Mantener cuerpo | Conecta seleccion, modelo e interpretabilidad. |
| Mapa metodos | `explor_mapa_metodos.png` | Candidata a apendice o rediseño | Aspect ratio 4.20 y mucha densidad. Aporta contexto, pero compite con F9/F10. |
| Jaccard QFS | `f10_b2_jaccard_12_metodos.png` | Mover a apendice | Es trazabilidad de solape, no argumento central. Ya existe A8 como solape resumido. |
| F8 | `f8_qfs_alpha_beta.png` | Mantener cuerpo | Explica los dos mandos QFS con caveat de oraculo. |
| F9 | `diag_atribucion_qfs.png` | Mantener cuerpo y destacar | Es la figura central de la memoria. Debe quedar rodeada de menos ruido, no mas. |
| F10 | `f10_qfs_vs_clasico.png` | Mantener cuerpo | Cierra comparacion baseline--clasico--QFS--oraculo. |
| EV6 | `ev6_rendimiento_vs_k.png` | Mantener o mover segun espacio | Es buena comprobacion de robustez frente a k, pero puede vivir en apendice si el cuerpo se satura. |
| Alpha | `f10_b4_escalera_alpha.png` | Mover a apendice si F8 ya cubre alpha | Mecanismo util, pero F8 ya explica el mando. |
| Beta | `f10_b5_beta_geometria.png` | Mover a apendice si F8 ya cubre beta | Muy panoramica; funciona como respaldo tecnico, no como argumento principal. |
| MDS | `f10_b9_atomos_mds_error.png` | Mantener solo si se usa para refutar Churn | Es clave para descartar hipotesis geometrica, pero visualmente panoramica. Alternativa: mover a apendice y dejar el resultado en texto. |
| Cadena tests | `f10_b8_cadena_tests.png` | Mover a apendice | Es buena como garantia metodologica, pero como figura de cuerpo llega tarde y no anade resultado nuevo. |
| Consistencia | `f10_b10_consistencia.png` | Mover a apendice | Es cierre de robustez; mejor como respaldo final que como argumento de cuerpo. |

## 4. Veredicto por figura de apendice

| Figura | Archivo | Veredicto | Razon |
|---|---|---|---|
| A1 | `a1_permutacion_senal_nulo.png` | Mantener apendice | Buen respaldo de separacion frente al nulo. |
| A2 | `a2_leakage.png` | Mantener apendice | Respalda leakage; limpio y defendible. |
| A3 | `a3_roster_completo.png` | Mantener apendice | Trazabilidad del roster completo; no debe subir al cuerpo. |
| A4 | `a4_shap_concordancia.png` | Mantener apendice | Complementa F6 para Olive Oil. |
| A5 | `a5_panorama_deltas.png` | Mantener apendice | Detalle de deltas por selector; evita inventario en cuerpo. |
| A6 | `a6_handoff_ir.png` | Mantener apendice | Respalda entradas QFS `I_i/R_ij`. |
| A7 | `a7_coste_cuantico.png` | Mantener apendice | Coste simulado; buen caveat metodologico. |
| A8 | `a8_solape_qfs_clasicos.png` | Mantener apendice | Solape resumido suficiente si se mueve Jaccard completo. |
| A9 | `a9_macro_f1_auc_binarios.png` | Mantener apendice | Contexto AUC sin desplazar macro-F1 como metrica primaria. |

## 5. Propuesta de cuerpo visual depurado

Opcion recomendada: cuerpo con 13--14 figuras, no 20.

Mantener en cuerpo:

1. F1 banco.
2. F2 señal FDR/efecto.
3. F3 base confiable.
4. Regimenes del dato (`f10_a_regimenes_dataset`) si se conserva como puente.
5. F4 perfil selectores.
6. O1 organismo Madelon.
7. F5 redundancia vs k.
8. F7 significancia/magnitud.
9. F6 SHAP.
10. F8 alpha/beta.
11. F9 diagnostico criterio--optimizador.
12. F10 QFS vs clasico.
13. EV6 rendimiento vs k, opcional.
14. MDS, solo si la refutacion geometrica de Churn se considera indispensable
    en cuerpo.

Mover a apendice:

- `explor_mapa_metodos.png` o sustituir por una frase y A8.
- `f10_b2_jaccard_12_metodos.png`.
- `f10_b4_escalera_alpha.png`.
- `f10_b5_beta_geometria.png`.
- `f10_b8_cadena_tests.png`.
- `f10_b10_consistencia.png`.

Decision fina:

- Si se quiere un cuerpo mas sobrio: mover tambien `ev6_rendimiento_vs_k.png`
  y `f10_b9_atomos_mds_error.png`.
- Si se quiere un cuerpo mas defensivo: mantener MDS en cuerpo porque refuta una
  explicacion alternativa de `Customer Churn`.

## 6. Riesgos concretos que miraria el tribunal

1. **Demasiadas figuras seguidas en resultados.** A partir de la comparacion QFS,
   el lector recibe muchas laminas mecanisticas consecutivas. La tesis central
   puede diluirse.
2. **Figuras panoramicas a ancho de pagina.** Algunas tienen texto pequeno en A4.
   No fallan tecnicamente, pero pueden ser dificiles de leer impresas.
3. **Cuerpo vs apendice.** Las figuras de cadena de tests, consistencia y Jaccard
   completo son mas de defensa documental que de argumento principal.
4. **F9 debe respirar.** La figura `diag_atribucion_qfs.png` deberia aparecer
   como climax, no como una mas entre controles.
5. **F8 ya absorbe alpha/beta.** Si despues se muestran alpha y beta por separado,
   hay que justificar que no son repeticion sino detalle mecanistico.

## 7. Plan de actuacion recomendado

### Paso A: cirugia sin regenerar

- Mover a apendice las figuras secundarias listadas arriba.
- Reescribir transiciones para que el cuerpo no pierda evidencia:
  "El detalle completo de alpha/beta/Jaccard/consistencia se conserva en el
  Apéndice...".
- Mantener F9 y F10 como cierre de cuerpo.

### Paso B: solo si queda tiempo

- Rediseñar `explor_mapa_metodos.png` si se quiere mantener en cuerpo:
  version menos panoramica, con menos etiquetas y foco en el desplazamiento de
  QFS respecto a mRMR/MI/Boruta.
- Rediseñar `f10_b9_atomos_mds_error.png` si se queda en cuerpo:
  separar embebidos y barras de error MDS, o dejar solo la evidencia que refuta
  Churn.

### Paso C: verificaciones

- `conda run -n qfs_env python scripts/verify_memoria_figuras.py`
- `conda run -n qfs_env tectonic ejemplo-memoria.tex`
- Revision visual del PDF renderizado por paginas.

## 8. Veredicto final

Las visualizaciones son buenas y estan trazadas, pero el cuerpo esta demasiado
generoso. La mejora no es hacer mas graficas: es bajar de rango las que son
respaldo tecnico. La memoria debe dejar al lector con tres golpes visuales
claros:

1. El banco y la referencia clasica estan auditados.
2. QFS se evalua contra una referencia fuerte.
3. Cuando QFS falla, F9 dice si falla el criterio o el optimizador.

Todo lo demas debe ayudar a esa lectura, no competir con ella.
