from typing import Any, Dict
import pandas as pd

def safe_div(numerator: float, denominator: float) -> float:
    return (numerator / denominator) if denominator else 0.0

def summarize_column(df: pd.DataFrame, col: str) -> Dict[str, Any]:
    s = df[col]
    return {
        'dtype': str(s.dtype),
        'n_missing': int(s.isna().sum()),
        'n_unique': int(s.nunique(dropna=True)),
        'n_total': int(len(s))
    }
