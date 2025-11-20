"""Command-line interface for alphascore"""
import argparse
import pandas as pd
import sys
from .scoring import DataQualityScore

def parse_args(argv=None):
    p = argparse.ArgumentParser(prog='alphascore', description='Compute data quality score for CSV or Parquet files')
    p.add_argument('input', help='Input file (CSV or Parquet)')
    p.add_argument('--name', '-n', help='Dataset name', default='dataset')
    p.add_argument('--output', '-o', help='Output HTML report path', default=None)
    p.add_argument('--json', '-j', help='Also write JSON output path', default=None)
    return p.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    try:
        if args.input.lower().endswith('.parquet'):
            df = pd.read_parquet(args.input)
        else:
            df = pd.read_csv(args.input)
    except Exception as e:
        print(f"Failed to read input file: {e}", file=sys.stderr)
        return 2
    engine = DataQualityScore(df, name=args.name)
    res = engine.compute()
    if args.json:
        import json
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=2)
    if args.output:
        engine.to_html(args.output)
        print(f"Wrote HTML report to {args.output}")
    print(f"AlphaScore: {res['final_score']}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
