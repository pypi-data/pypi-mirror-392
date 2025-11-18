from typing import Dict, Any, List
import pandas as pd
from .utils import pct, top_categories, numeric_summary, detect_outliers_iqr
from .viz import save_simple_hist, save_bar_top
import os

def summarize(df: pd.DataFrame) -> Dict[str, Any]:
    total = len(df)
    dtypes = df.dtypes.astype(str).to_dict()
    missing = df.isna().sum().to_dict()
    missing_pct = {k: pct(v, total) for k, v in missing.items()}

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    numeric_summaries = {c: numeric_summary(df[c]) for c in numeric_cols}
    top_categories_summary = {c: top_categories(df[c]) for c in cat_cols}

    return {
        "rows": int(total),
        "columns": int(df.shape[1]),
        "dtypes": dtypes,
        "missing_count": missing,
        "missing_pct": missing_pct,
        "numeric_summary": numeric_summaries,
        "top_categories": top_categories_summary,
    }

def recommend_viz(df: pd.DataFrame, max_recs=10) -> List[Dict[str, str]]:
    recs = []
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    for c in num_cols:
        recs.append({"column": c, "viz": "histogram", "reason": "distribution & outliers"})
        for c2 in num_cols:
            if c != c2:
                recs.append({"column": f"{c} vs {c2}", "viz": "scatter", "reason": "relationship"})
    for c in cat_cols:
        recs.append({"column": c, "viz": "bar", "reason": "top categories / counts"})
    return recs[:max_recs]

def explain(df: pd.DataFrame, show_plots: bool = False, save_plots: bool = False, outdir: str = "datahero_plots", sample_rows: int = 5) -> Dict[str, Any]:
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    os.makedirs(outdir, exist_ok=True)
    summary = summarize(df)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    corr_report = []
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr().abs()
        pairs = []
        for i, c1 in enumerate(numeric_cols):
            for j, c2 in enumerate(numeric_cols):
                if j <= i:
                    continue
                val = corr.loc[c1, c2]
                pairs.append((c1, c2, float(val)))
        pairs_sorted = sorted(pairs, key=lambda x: x[2], reverse=True)
        for a, b, v in pairs_sorted[:10]:
            corr_report.append({"pair": f"{a} & {b}", "corr_abs": round(v, 3)})

    outliers = {}
    for c in numeric_cols:
        s = df[c].dropna()
        if s.empty:
            continue
        out = detect_outliers_iqr(s)
        if out["n_outliers"] > 0:
            outliers[c] = out

    sample = df.head(sample_rows).to_dict(orient="records")

    saved = []
    if save_plots:
        for c in numeric_cols:
            fname = os.path.join(outdir, f"{c}_hist.png")
            save_simple_hist(df[c], fname)
            saved.append(fname)
        for c in df.select_dtypes(include=["object", "category", "bool"]).columns:
            fname = os.path.join(outdir, f"{c}_bar.png")
            save_bar_top(df[c], fname)
            saved.append(fname)

    result = {
        "summary": summary,
        "correlations": corr_report,
        "outliers": outliers,
        "sample": sample,
        "recommendations": recommend_viz(df),
        "saved_plots": saved if save_plots else [],
    }

    if show_plots:
        pass

    return result
