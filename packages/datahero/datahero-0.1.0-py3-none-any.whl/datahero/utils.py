import pandas as pd

def pct(n, total):
    return round(100 * n / total, 2) if total else 0.0

def top_categories(series: pd.Series, n=5):
    return series.value_counts().head(n).to_dict()

def numeric_summary(series: pd.Series):
    return {
        "count": int(series.count()),
        "mean": float(series.mean()) if series.count() else None,
        "std": float(series.std()) if series.count() else None,
        "min": float(series.min()) if series.count() else None,
        "25%": float(series.quantile(0.25)) if series.count() else None,
        "50%": float(series.median()) if series.count() else None,
        "75%": float(series.quantile(0.75)) if series.count() else None,
        "max": float(series.max()) if series.count() else None,
    }

def detect_outliers_iqr(series: pd.Series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = series[(series < lower) | (series > upper)]
    return {"lower_bound": float(lower), "upper_bound": float(upper), "n_outliers": int(outliers.count())}
