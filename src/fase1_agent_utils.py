from pathlib import Path
import json
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


IDENTIFIER_PATTERNS = (
    "id",
    "customerid",
    "customer_id",
    "patientid",
    "patient_id",
    "sampleid",
    "sample_id",
)


def ensure_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_table(df, path, index=False):
    path = Path(path)
    ensure_dir(path.parent)
    df.to_csv(path, index=index, encoding="utf-8")
    return path


def save_json(obj, path):
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
    return path


def latex_escape(value):
    text = "" if value is None else str(value)
    replacements = {
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
        "≥": r"$\geq$",
        "≤": r"$\leq$",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def latex_inline(value):
    text = "" if value is None else str(value)
    parts = text.split("`")
    formatted = []
    for idx, part in enumerate(parts):
        escaped = latex_escape(part)
        if idx % 2 == 1:
            formatted.append(rf"\texttt{{{escaped}}}")
        else:
            formatted.append(escaped)
    return "".join(formatted)


def markdown_report_to_latex(markdown_text, title="Informe de resultados -- Fase 1"):
    lines = [
        "% Documento generado automáticamente desde notebooks/fase1.ipynb.",
        "% Pensado para integrarse en Plantilla_Latex_GCD/tfgs/tex/resultados.tex.",
        rf"\section{{{latex_escape(title)}}}",
        "",
    ]
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            lines.append(r"\end{itemize}")
            lines.append("")
            in_list = False

    skipped_first_heading = False
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            close_list()
            continue
        if line.startswith("# "):
            close_list()
            heading = line[2:].strip()
            if not skipped_first_heading and heading.lower().startswith("informe de resultados"):
                skipped_first_heading = True
                continue
            lines.append(rf"\section{{{latex_inline(heading)}}}")
        elif line.startswith("## "):
            close_list()
            lines.append(rf"\subsection{{{latex_inline(line[3:].strip())}}}")
        elif line.startswith("### "):
            close_list()
            lines.append(rf"\subsubsection{{{latex_inline(line[4:].strip())}}}")
        elif line.startswith("- "):
            if not in_list:
                lines.append(r"\begin{itemize}")
                in_list = True
            lines.append(rf"\item {latex_inline(line[2:].strip())}")
        else:
            close_list()
            lines.append(latex_inline(line))
    close_list()
    return "\n".join(lines)


def write_latex_report_from_markdown(markdown_text, path, title="Informe de resultados -- Fase 1"):
    path = Path(path)
    ensure_dir(path.parent)
    latex_text = markdown_report_to_latex(markdown_text, title=title)
    path.write_text(latex_text, encoding="utf-8")
    return path


def save_current_figure(path, dpi=170):
    path = Path(path)
    ensure_dir(path.parent)
    plt.tight_layout()
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    return path


def safe_read_table(path):
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(path)
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding="latin-1")
    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t")
    raise ValueError(f"Formato no soportado: {path}")


def infer_target_column(df, preferred=None):
    if preferred and preferred in df.columns:
        return preferred
    candidates = [
        "target", "Target", "TARGET", "class", "Class", "CLASS", "label", "Label", "LABEL",
        "y", "Y", "churn", "Churn", "diagnosis", "Diagnosis", "region", "Region",
        "species", "Area",
    ]
    for col in candidates:
        if col in df.columns:
            return col
    return None


def is_identifier_column(name, series=None):
    normalized = re.sub(r"[^a-z0-9]", "", str(name).lower())
    if normalized in IDENTIFIER_PATTERNS or normalized.endswith("id"):
        return True
    if series is None:
        return False
    nunique = series.nunique(dropna=True)
    return nunique == len(series) and len(series) > 20


def get_feature_columns(df, target, include_identifiers=False):
    cols = [c for c in df.columns if c != target]
    if include_identifiers:
        return cols
    return [c for c in cols if not is_identifier_column(c, df[c])]


def numeric_features(df, target):
    return [c for c in get_feature_columns(df, target) if pd.api.types.is_numeric_dtype(df[c])]


def categorical_features(df, target):
    return [c for c in get_feature_columns(df, target) if not pd.api.types.is_numeric_dtype(df[c])]


def classify_columns(df, target=None):
    rows = []
    for col in df.columns:
        series = df[col]
        nunique = series.nunique(dropna=True)
        is_num = pd.api.types.is_numeric_dtype(series)
        if col == target:
            role = "target"
        elif is_identifier_column(col, series):
            role = "posible_id"
        elif is_num and nunique <= 2:
            role = "binaria_numérica"
        elif is_num:
            role = "numérica"
        elif nunique <= 2:
            role = "binaria_categórica"
        else:
            role = "categórica"
        rows.append({
            "variable": col,
            "dtype": str(series.dtype),
            "n_unique": int(nunique),
            "missing": int(series.isna().sum()),
            "missing_pct": float(series.isna().mean()),
            "role": role,
        })
    return pd.DataFrame(rows)


def robust_outlier_rate(series):
    x = pd.to_numeric(series, errors="coerce").dropna()
    if len(x) < 4:
        return np.nan
    q1, q3 = x.quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr == 0:
        return 0.0
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return float(((x < lo) | (x > hi)).mean())


def benjamini_hochberg(pvalues):
    p = np.asarray(pvalues, dtype=float)
    out = np.full_like(p, np.nan, dtype=float)
    valid = ~np.isnan(p)
    pv = p[valid]
    m = len(pv)
    if m == 0:
        return out
    order = np.argsort(pv)
    ranked = pv[order]
    adj = ranked * m / (np.arange(1, m + 1))
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.clip(adj, 0, 1)
    restored = np.empty_like(adj)
    restored[order] = adj
    out[valid] = restored
    return out


def cliffs_delta(x, y):
    x = pd.Series(x).dropna().to_numpy()
    y = pd.Series(y).dropna().to_numpy()
    if len(x) == 0 or len(y) == 0:
        return np.nan
    try:
        from scipy.stats import rankdata

        values = np.concatenate([x, y])
        ranks = rankdata(values)
        rank_x = ranks[: len(x)].sum()
        m, n = len(x), len(y)
        return float((2 * rank_x - m * (m + 1)) / (m * n) - 1)
    except Exception:
        gt = sum((xi > y).sum() for xi in x)
        lt = sum((xi < y).sum() for xi in x)
        return float((gt - lt) / (len(x) * len(y)))


def cramers_v(confusion):
    try:
        from scipy.stats import chi2_contingency

        chi2 = chi2_contingency(confusion)[0]
        n = confusion.to_numpy().sum()
        r, k = confusion.shape
        denom = n * max(min(k - 1, r - 1), 1)
        return float(np.sqrt(chi2 / denom)) if denom > 0 else np.nan
    except Exception:
        return np.nan
