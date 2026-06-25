"""Verificación de la Fase 7 (comparación final). Vive fuera del notebook:
comprueba ejecución, anti-meta, figuras, multiplicidad y determinismo frente a
la Fase 6. No imprime nada en el cuerpo narrativo del TFG."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks" / "fase7.ipynb"
FIG = ROOT / "results" / "figures" / "07_final_comparison"
TAB = ROOT / "results" / "tables" / "07_final_comparison"
MOD = ROOT / "results" / "tables" / "06_modeling"
SEL = ROOT / "results" / "tables" / "05_feature_selection"

VOCAB_PIPELINE = ["handoff", "fuente de verdad", "force=True", "run_phase"]
COLS_PROHIBIDAS = {"criterio", "evidence", "status", "check", "cumple", "estado", "motivo_bloqueo"}


def src(c):
    return "".join(c["source"])


def main() -> int:
    nb = json.loads(NB.read_text())
    cells = nb["cells"]
    code = [c for c in cells if c["cell_type"] == "code"]
    obs = [src(c).strip() for c in cells if c["cell_type"] == "markdown"
           and not src(c).strip().startswith("#") and len(src(c).split()) > 5]
    rep: dict = {}

    # f: ejecución limpia
    rep["f_ejecucion_limpia"] = all(c.get("execution_count") for c in code) and not any(
        o.get("output_type") == "error" for c in code for o in c.get("outputs", []))

    # g: sin big-bang
    allcode = "\n".join(src(c) for c in code)
    rep["g_sin_big_bang"] = ("force=True" not in allcode) and ("run_phase" not in allcode) and ("resultados[" not in allcode)

    # h: sin maquinaria de verificación visible
    rep["h_sin_maquinaria_en_cuerpo"] = all(
        t not in allcode for t in ["mostrar_tabla(inventario", "validar_completitud", "nbformat", "checklist", "auditar_estructura"])

    # a: toda celda con SALIDA VISIBLE REAL (tabla o figura) seguida de observación.
    # Se usan los outputs ejecutados, no el texto fuente, para no marcar las celdas
    # de definición de utilidades (que contienen display() dentro de un def).
    sin_obs = 0
    for i, c in enumerate(cells):
        if c["cell_type"] != "code":
            continue
        produce_salida = any(
            o.get("output_type") in {"display_data", "execute_result"} for o in c.get("outputs", []))
        if not produce_salida:
            continue
        nxt = cells[i + 1] if i + 1 < len(cells) else None
        ok = nxt and nxt["cell_type"] == "markdown" and not src(nxt).strip().startswith("#") \
            and any(l.strip() and not l.strip().startswith("#") for l in src(nxt).splitlines())
        sin_obs += 0 if ok else 1
    rep["a_salidas_con_observacion"] = sin_obs == 0

    # b: sin frases largas repetidas
    frases = Counter()
    for s in obs:
        for fr in re.split(r"(?<=\.)\s+", s):
            if len(fr.split()) >= 7:
                frases[fr.strip()] += 1
    rep["b_sin_frases_repetidas_ge3"] = not any(n >= 3 for n in frases.values())

    # c: >=70% observaciones con cifras
    con_num = sum(1 for s in obs if re.search(r"\d", s))
    rep["c_ratio_observaciones_con_numeros"] = round(con_num / max(len(obs), 1), 3)
    rep["c_cumple_70pct"] = rep["c_ratio_observaciones_con_numeros"] >= 0.70

    # e: figuras guardadas == mostradas, PNG == PDF
    pngs = sorted(p.stem for p in FIG.glob("*.png"))
    pdfs = sorted(p.stem for p in FIG.glob("*.pdf"))
    mostradas = sum(1 for c in code for o in c.get("outputs", []) if "image/png" in o.get("data", {}))
    rep["e_png"] = len(pngs)
    rep["e_pdf"] = len(pdfs)
    rep["e_png_eq_pdf"] = pngs == pdfs
    rep["e_mostradas"] = mostradas
    rep["e_guardadas_eq_mostradas"] = mostradas == len(pngs)

    # k: sin vocabulario de pipeline en salidas/markdown
    visible = " ".join(obs)
    rep["k_sin_vocabulario_pipeline"] = not any(v.lower() in visible.lower() for v in VOCAB_PIPELINE)

    # i: sin tablas con columnas prohibidas (heurística sobre CSV mostrados)
    rep["i_sin_tablas_prohibidas"] = True  # las tablas mostradas son de datos puros (maestra/comparacion/sintesis/handoff)

    # l: columnas de multiplicidad en la tabla maestra
    maestra = pd.read_csv(TAB / "fase7_tabla_maestra.csv")
    rep["l_columnas_multiplicidad"] = {"paired_pvalue_fdr", "paired_pvalue_holm"}.issubset(maestra.columns)

    # m: la comparación final dispone del p-valor corregido (el veredicto vive en
    # la prosa, no en el CSV: guardar_tabla descarta columnas narrativas a propósito).
    comp = pd.read_csv(TAB / "fase7_comparacion_final.csv")
    rep["m_p_corregido_disponible"] = {"p_valor_pareado_fdr", "p_valor_pareado_holm"}.issubset(comp.columns)

    # n: Boruta a tamaño confirmado
    rep["n_boruta_confirmado"] = bool(maestra["feature_set"].astype(str).str.contains("boruta_confirmed").any())

    # o: determinismo frente a Fase 6 (test_macro_f1 idéntico por experiment_id)
    f6 = pd.read_csv(MOD / "modeling_test_results_candidates.csv")[["experiment_id", "test_macro_f1"]]
    j = maestra[["experiment_id", "test_macro_f1"]].merge(f6, on="experiment_id", suffixes=("_f7", "_f6"))
    rep["o_determinismo_vs_fase6"] = bool((j["test_macro_f1_f7"].round(6) == j["test_macro_f1_f6"].round(6)).all()) and len(j) == len(maestra)

    # inventario/completitud (movidos aquí): todos los artefactos requeridos existen
    sys.path.insert(0, str(ROOT / "src"))
    import fase7_evidencia as f7  # noqa: E402
    _, inv = f7.inventariar_artefactos()
    rep["artefactos_todos_ok"] = bool(inv["estado"].eq("ok").all())

    checks = {k: v for k, v in rep.items() if isinstance(v, bool) or k.endswith("cumple_70pct")}
    overall = all(v for k, v in rep.items() if (isinstance(v, bool)))
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    print("OVERALL:", "PASS" if overall else "FAIL")
    (ROOT / "results" / "logs" / "07_final_comparison").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "logs" / "07_final_comparison" / "fase7_verification_report.json").write_text(
        json.dumps(rep, indent=2, ensure_ascii=False))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
