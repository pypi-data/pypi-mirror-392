import matplotlib
matplotlib.use("Agg")  # safe for headless/CI
from matplotlib import pyplot as plt
import pandas as pd
import os

def save_simple_hist(series: pd.Series, filename: str):
    fig, ax = plt.subplots()
    series.dropna().plot.hist(ax=ax, bins=20)
    ax.set_title(str(series.name))
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return filename

def save_bar_top(series: pd.Series, filename: str, top_n=10):
    fig, ax = plt.subplots()
    series.dropna().value_counts().head(top_n).plot.bar(ax=ax)
    ax.set_title(str(series.name))
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return filename
