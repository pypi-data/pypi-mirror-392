"""Checks implementation for data quality dimensions"""
from typing import Dict, Any
import pandas as pd
import numpy as np
from .utils import safe_div

class Checks:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.n_rows = len(df)
        self.n_cells = df.size

    def completeness(self) -> Dict[str, Any]:
        total_missing = int(self.df.isna().sum().sum())
        missing_ratio = safe_div(total_missing, self.n_cells)
        score = 100.0 - (missing_ratio * 100.0)
        return {'score': round(score,2), 'total_missing': total_missing, 'missing_ratio': round(missing_ratio,4)}

    def uniqueness(self) -> Dict[str, Any]:
        dup_count = int(self.df.duplicated().sum())
        dup_ratio = safe_div(dup_count, self.n_rows)
        score = 100.0 - (dup_ratio * 100.0)
        return {'score': round(score,2), 'duplicate_rows': dup_count, 'duplicate_ratio': round(dup_ratio,4)}

    def validity(self) -> Dict[str, Any]:
        invalid = 0
        total = 0
        for col in self.df.columns:
            s = self.df[col]
            total += s.size
            if pd.api.types.is_numeric_dtype(s):
                # count non-finite values as invalid
                invalid += int(~np.isfinite(s.fillna(np.nan)).sum())
            elif pd.api.types.is_string_dtype(s):
                invalid += int(s.fillna(""").astype(str).str.strip().eq("").sum())
            else:
                # other dtypes: count NAs as invalid
                invalid += int(s.isna().sum())
        invalid_ratio = safe_div(invalid, total)
        score = 100.0 - (invalid_ratio * 100.0)
        return {'score': round(score,2), 'invalid_count': int(invalid), 'invalid_ratio': round(invalid_ratio,4)}

    def consistency(self) -> Dict[str, Any]:
        mixed = 0
        for col in self.df.columns:
            s = self.df[col].dropna()
            if s.empty:
                continue
            types = s.map(lambda x: type(x)).unique()
            if len(types) > 1:
                mixed += 1
        inconsistency_ratio = safe_div(mixed, len(self.df.columns))
        score = 100.0 - (inconsistency_ratio * 100.0)
        return {'score': round(score,2), 'mixed_type_columns': int(mixed)}

    def accuracy(self) -> Dict[str, Any]:
        outlier_count = 0
        total_numeric = 0
        for col in self.df.select_dtypes(include=[np.number]).columns:
            s = self.df[col].dropna()
            total_numeric += len(s)
            if s.empty:
                continue
            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outlier_count += int(((s < lower) | (s > upper)).sum())
        outlier_ratio = safe_div(outlier_count, total_numeric)
        score = 100.0 - (outlier_ratio * 100.0)
        return {'score': round(score,2), 'outlier_count': int(outlier_count), 'outlier_ratio': round(outlier_ratio,4)}

    def integrity(self) -> Dict[str, Any]:
        violations = 0
        total_checks = 0
        for col in self.df.columns:
            lname = col.lower()
            if 'age' in lname or 'price' in lname or 'amount' in lname or 'salary' in lname:
                s = pd.to_numeric(self.df[col], errors='coerce').dropna()
                total_checks += len(s)
                violations += int((s < 0).sum())
        violation_ratio = safe_div(violations, total_checks)
        score = 100.0 - (violation_ratio * 100.0)
        return {'score': round(score,2), 'violations': int(violations), 'checked_values': int(total_checks)}
