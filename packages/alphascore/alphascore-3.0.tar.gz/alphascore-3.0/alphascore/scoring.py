"""Core DataQualityScore engine"""
from typing import Dict, Any
import pandas as pd
from .checks import Checks
from jinja2 import Environment, FileSystemLoader
import os

DEFAULT_WEIGHTS = {
    'completeness': 0.25,
    'uniqueness': 0.10,
    'validity': 0.20,
    'consistency': 0.15,
    'accuracy': 0.20,
    'integrity': 0.10
}

class DataQualityScore:
    def __init__(self, df: pd.DataFrame, name: str = 'dataset', weights: Dict[str,float]=None):
        if not isinstance(df, pd.DataFrame):
            raise TypeError('df must be a pandas.DataFrame')
        self.df = df.copy()
        self.name = name
        self.weights = weights or DEFAULT_WEIGHTS
        self.checks = Checks(self.df)
        self.results: Dict[str,Any] = {}

    def compute(self) -> Dict[str,Any]:
        dims = ['completeness','uniqueness','validity','consistency','accuracy','integrity']
        details = {}
        for d in dims:
            details[d] = getattr(self.checks, d)()
        final = 0.0
        for d in dims:
            w = self.weights.get(d, 0)
            final += details[d]['score'] * w
        final = round(final,2)
        self.results = {'final_score': final, 'dimensions': details, 'name': self.name}
        return self.results

    def to_json(self) -> Dict[str,Any]:
        if not self.results:
            self.compute()
        return self.results

    def to_html(self, out_path: str):
        if not self.results:
            self.compute()
        here = os.path.dirname(__file__)
        tmpl_dir = os.path.join(here, 'templates')
        env = Environment(loader=FileSystemLoader(tmpl_dir))
        tmpl = env.get_template('report_template.html')
        html = tmpl.render(result=self.results)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
