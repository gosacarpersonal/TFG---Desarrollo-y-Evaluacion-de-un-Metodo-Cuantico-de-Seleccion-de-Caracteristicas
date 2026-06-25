from __future__ import annotations

from pathlib import Path

import pandas as pd


def escribir_markdown(ruta: Path, contenido: str) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def tabla_markdown(tabla: pd.DataFrame, max_filas: int = 12) -> str:
    if tabla.empty:
        return "_Sin filas._"
    vista = tabla.head(max_filas).astype(str)
    columnas = list(vista.columns)
    cabecera = "| " + " | ".join(columnas) + " |"
    separador = "| " + " | ".join(["---"] * len(columnas)) + " |"
    filas = ["| " + " | ".join(str(fila[col]) for col in columnas) + " |" for _, fila in vista.iterrows()]
    return "\n".join([cabecera, separador, *filas])


def escapar_latex(texto: object) -> str:
    resultado = str(texto)
    reemplazos = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for origen, destino in reemplazos.items():
        resultado = resultado.replace(origen, destino)
    return resultado


def markdown_a_latex_basico(markdown: str) -> str:
    lineas = []
    for linea in markdown.splitlines():
        texto = linea.strip()
        if texto.startswith("# "):
            lineas.append(r"\section{" + escapar_latex(texto[2:]) + "}")
        elif texto.startswith("## "):
            lineas.append(r"\subsection{" + escapar_latex(texto[3:]) + "}")
        elif texto.startswith("### "):
            lineas.append(r"\subsubsection{" + escapar_latex(texto[4:]) + "}")
        elif texto.startswith("- "):
            lineas.append(r"\begin{itemize}\item " + escapar_latex(texto[2:]) + r"\end{itemize}")
        elif texto.startswith("|"):
            continue
        elif texto:
            lineas.append(escapar_latex(texto) + "\n")
        else:
            lineas.append("")
    return "\n".join(lineas)


def escribir_informe_memoria(tablas: dict[str, pd.DataFrame], figuras: list[dict], ruta_md: Path, ruta_tex: Path) -> None:
    readiness = tablas.get("fase3_dataset_readiness.csv", pd.DataFrame())
    riesgos = tablas.get("postprocessed_residual_risks.csv", pd.DataFrame())
    dimensiones = tablas.get("postprocessed_dimensionality_summary.csv", pd.DataFrame())
    visual = tablas.get("fase3_visual_audit.csv", pd.DataFrame())

    contenido = [
        "# Fase 3. Auditoría post-preprocesado antes del split",
        "",
        "La Fase 3 verifica si los datasets procesados conservan la representación del problema original y están listos para dividirse en train, validación y test.",
        "",
        "## Metodología",
        "",
        "La revisión cruza datasets raw, datasets processed, evidencias de Fase 1 y logs de Fase 2. Cada conclusión procede de tablas generadas en `results/tables/03_postprocessing_audit/`.",
        "",
        "## Decisión por dataset",
        "",
        tabla_markdown(readiness, 20),
        "",
        "## Perfil dimensional",
        "",
        tabla_markdown(dimensiones[["dataset", "n_muestras", "n_features", "ratio_features_muestras", "perfil_dificultad"]] if not dimensiones.empty else dimensiones, 20),
        "",
        "## Riesgos residuales",
        "",
        tabla_markdown(riesgos[["dataset", "gravedad", "riesgo", "evidencia", "accion_fase4"]] if not riesgos.empty else riesgos, 30),
        "",
        "## Variables categóricas pendientes",
        "",
        tabla_markdown(tablas.get("postprocessed_categorical_features_pending.csv", pd.DataFrame()), 20),
        "",
        "## Figuras candidatas para memoria",
        "",
        tabla_markdown(visual[visual.get("candidata_memoria", False) == True][["figura", "seccion", "pregunta_analitica", "estado_final", "motivo", "observacion_manual"]] if not visual.empty else visual, 20),
        "",
        "## Limitaciones",
        "",
        "La auditoría no sustituye al split ni a la selección de características. PCA, correlaciones y asociaciones se usan como diagnósticos exploratorios, no como pruebas definitivas de separabilidad ni causalidad.",
    ]
    markdown = "\n".join(contenido)
    escribir_markdown(ruta_md, markdown)
    escribir_markdown(ruta_tex, markdown_a_latex_basico(markdown))


def escribir_auditoria_visual(tabla: pd.DataFrame, ruta_md: Path) -> None:
    aprobadas = int((tabla["estado_final"] == "aceptada").sum()) if not tabla.empty else 0
    descartadas = int((tabla["estado_final"] == "descartada").sum()) if not tabla.empty else 0
    contenido = [
        "# Auditoría visual real - Fase 3",
        "",
        f"Figuras aceptadas: {aprobadas}. Figuras descartadas: {descartadas}.",
        "",
        "La revisión combina comprobaciones automáticas mínimas con observaciones manuales por figura: clipping, márgenes, legibilidad, solapamientos, exceso de texto, leyendas, utilidad analítica y uso para memoria.",
        "",
        "No se aceptan como figura las evidencias que comunican mejor como tabla; en esta fase se descartaron visualizaciones planas de target shift y cambio distribucional.",
        "",
        tabla_markdown(tabla, 50),
    ]
    escribir_markdown(ruta_md, "\n".join(contenido))


def escribir_auditoria_final(tablas: dict[str, pd.DataFrame], ruta_md: Path) -> None:
    checklist = tablas.get("fase3_final_checklist.csv", pd.DataFrame())
    readiness = tablas.get("fase3_dataset_readiness.csv", pd.DataFrame())
    contenido = [
        "# Auditoría final - Fase 3",
        "",
        "La fase queda cerrada solo si el notebook ejecuta completo, los módulos compilan y las cifras principales son trazables a CSV.",
        "",
        "## Checklist",
        "",
        tabla_markdown(checklist, 40),
        "",
        "## Preparación para Fase 4",
        "",
        tabla_markdown(readiness, 20),
    ]
    escribir_markdown(ruta_md, "\n".join(contenido))
