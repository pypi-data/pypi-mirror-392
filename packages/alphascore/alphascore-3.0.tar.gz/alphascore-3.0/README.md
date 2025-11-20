# AlphaScore v3.0

AlphaScore is a Data Quality Scoring Engine that computes a reproducible 0–100 data-quality score for tabular datasets (Pandas DataFrames / CSV / Parquet), produces JSON and HTML reports, and provides a CLI.

**Author:** Shivam Mishra

## Features

- Six-dimension scoring: completeness, uniqueness, validity, consistency, accuracy, integrity
- Customizable weights
- HTML report generation (Jinja2)
- CLI for quick checks
- Simple API for integration

## Quickstart

```bash
pip install .
```

```python
import pandas as pd
from alphascore import DataQualityScore

df = pd.read_csv('data.csv')
engine = DataQualityScore(df, name='customers')
res = engine.compute()
print(res['final_score'])
engine.to_html('report.html')
```

## CLI

```bash
alphascore data.csv --output report.html
```
