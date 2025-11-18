# DataHero

DataHero produces a quick, human-readable explanation of a pandas DataFrame:
summary, missing data, outliers, correlations, and suggested visualizations.

## Author
**Ganeshamoorthy**  
Email: ganeshms110@gmail.com  
LinkedIn: https://www.linkedin.com/in/ganeshamoorthy-s-8466b7332

## Quick example
```python
import pandas as pd
from datahero import explain

df = pd.read_csv("sales.csv")
report = explain(df, save_plots=True, outdir="plots")
print(report["summary"])
