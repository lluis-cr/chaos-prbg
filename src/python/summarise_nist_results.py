#!/usr/bin/env python3
"""
summarize_nist_results.py

Run the full NIST suite on one bitstring file and save a clean summary table
(CSV and/or JSON) with p-values and pass/fail information when available.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
SUITE_DIR = SCRIPT_DIR / "randomness_testsuite"

if str(SUITE_DIR) not in sys.path:
    sys.path.insert(0, str(SUITE_DIR))

try:
    from tests_main import main
except ImportError as e:
    raise ImportError(
        f"Could not import tests_main.py from {SUITE_DIR}."
    ) from e


def read_bitstring(file_path: Path) -> str:
    bits = file_path.read_text(encoding="utf-8").strip()
    if not bits:
        raise ValueError(f"Bitstring file is empty: {file_path}")
    invalid = set(bits) - {"0", "1"}
    if invalid:
        raise ValueError(f"Found non-binary characters: {sorted(invalid)}")
    return bits


def _is_number(x: Any) -> bool:
    try:
        val = float(x)
        return math.isfinite(val)
    except Exception:
        return False


def extract_summary(results: list[list[Any]]) -> pd.DataFrame:
    """
    Convert the mixed output structure from tests_main.main(data=...)
    into a summary table.

    Each row:
      - test_name
      - p_value (best-effort extraction)
      - passed (best-effort extraction)
      - raw_result (string form)
    """
    rows = []

    for test_name, outcome in results:
        p_value = None
        passed = None

        # Common case: tuple like (p_value, success)
        if isinstance(outcome, tuple) and len(outcome) >= 2:
            if _is_number(outcome[0]):
                p_value = float(outcome[0])
            if isinstance(outcome[1], bool):
                passed = outcome[1]

        # Some tests may return dict-like structures
        elif isinstance(outcome, dict):
            if "p_value" in outcome and _is_number(outcome["p_value"]):
                p_value = float(outcome["p_value"])
            elif "p" in outcome and _is_number(outcome["p"]):
                p_value = float(outcome["p"])

            if "success" in outcome and isinstance(outcome["success"], bool):
                passed = outcome["success"]
            elif "passed" in outcome and isinstance(outcome["passed"], bool):
                passed = outcome["passed"]

        # Some tests return lists / nested lists
        elif isinstance(outcome, list):
            numeric_candidates = []

            def collect_numbers(obj: Any) -> None:
                if isinstance(obj, list):
                    for item in obj:
                        collect_numbers(item)
                elif isinstance(obj, tuple):
                    for item in obj:
                        collect_numbers(item)
                elif _is_number(obj):
                    numeric_candidates.append(float(obj))

            collect_numbers(outcome)

            if numeric_candidates:
                # Use first numeric value as best-effort summary
                p_value = numeric_candidates[0]

        rows.append(
            {
                "test_name": test_name,
                "p_value": p_value,
                "passed": passed,
                "raw_result": str(outcome),
            }
        )

    df = pd.DataFrame(rows)

    # If pass flag is missing but p-value exists, infer by the 0.01 threshold
    missing_pass = df["passed"].isna() & df["p_value"].notna()
    df.loc[missing_pass, "passed"] = df.loc[missing_pass, "p_value"] >= 0.01

    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run NIST tests and summarize results into a CSV/JSON table."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input bitstring .txt file.",
    )
    parser.add_argument(
        "--csv-out",
        default=None,
        help="Optional path to save summary as CSV.",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional path to save summary as JSON.",
    )
    return parser.parse_args()


def main_cli() -> None:
    args = parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    bits = read_bitstring(input_path)
    results = main(data=bits)
    df = extract_summary(results)

    print("\n=== NIST SUMMARY TABLE ===")
    print(df[["test_name", "p_value", "passed"]].to_string(index=False))

    if args.csv_out:
        csv_path = Path(args.csv_out).resolve()
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"\nSaved CSV summary to: {csv_path}")

    if args.json_out:
        json_path = Path(args.json_out).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(df.to_json(orient="records", indent=2), encoding="utf-8")
        print(f"Saved JSON summary to: {json_path}")


if __name__ == "__main__":
    main_cli()