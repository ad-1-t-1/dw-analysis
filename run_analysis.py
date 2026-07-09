#!/usr/bin/env python3
"""CLI entry point.

    python run_analysis.py                          # data/raw + legacy pickle
    python run_analysis.py --raw data/raw --out results
    python run_analysis.py --legacy-pkl merged_solar_desiccant.pkl
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dw_analysis.pipeline import run  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default="data/raw", help="raw CSV folder tree")
    ap.add_argument("--legacy-pkl", default="data/legacy/merged_solar_desiccant.pkl",
                    help="historical merged pickle (optional)")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    res = run(raw_dir=args.raw, legacy_pkl=args.legacy_pkl, out_dir=args.out)
    print("\n=== Season totals ===")
    for k, v in res["totals"].items():
        print(f"  {k:32s} {v}")
    for k, v in {**res["solar"], **res["balance"]}.items():
        print(f"  {k:32s} {v}")
    print(f"\nReport: {Path(args.out) / 'SUMMARY.md'}")
