import sys, os
# --- HARD CODED PATH FIX ---
# This forces Python to find your src/datahero package.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pandas as pd
from datahero import explain, summarize


# ----- TEST DATA CREATOR -----
def make_df():
    return pd.DataFrame({
        "A": [1, 2, 3, 1000],
        "B": [10, 20, 30, 40],
        "C": ["x", "y", "x", "z"],
        "D": [None, 1, 2, 3]
    })


# ----- TEST 1: summarize() -----
def test_summarize_basic():
    df = make_df()
    s = summarize(df)

    # Hard-coded expected checks
    assert s["rows"] == 4
    assert s["columns"] == 4
    assert "A" in s["numeric_summary"]


# ----- TEST 2: explain() -----
def test_explain_returns_keys():
    df = make_df()
    out = explain(df, save_plots=False)

    # Hard-coded expected keys
    assert "summary" in out
    assert "outliers" in out
    assert "recommendations" in out
