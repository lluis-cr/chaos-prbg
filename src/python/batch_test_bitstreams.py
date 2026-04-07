#!/usr/bin/env python3
"""
batch_test_bitstreams.py

Batch-run the NIST suite over multiple bitstring files and save:
1) a long-form CSV with one row per file per test
2) a pivot summary CSV with pass counts by file and test

This is the cleaned batch-testing layer for parameter sweeps.
"""

from __future__ import annotations

import argparse
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
        raise ValueError(f"Found non-binary characters in {file_path.name}: {sorted(invalid)}")
    return bits


def _is_number(x: Any) -> bool:
    try:
        val = float(x)
        return math.isfinite(val)
    except Exception:
        return False


def extract_rows(file_name: str, results: list[list[Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for test_name, outcome in results:
        p_value = None
        passed = None

        if isinstance(outcome, tuple) and len(outcome) >= 2:
            if _is_number(outcome[0]):
                p_value = float(outcome[0])
            if isinstance(outcome[1], bool):
                passed = outcome[1]

        elif isinstance(outcome, dict):
            if "p_value" in outcome and _is_number(outcome["p_value"]):
                p_value = float(outcome["p_value"])
            elif "p" in outcome and _is_number(outcome["p"]):
                p_value = float(outcome["p"])

            if "success" in outcome and isinstance(outcome["success"], bool):
                passed = outcome["success"]
            elif "passed" in outcome and isinstance(outcome["passed"], bool):
                passed = outcome["passed"]

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
                p_value = numeric_candidates[0]

        if passed is None and p_value is not None:
            passed = p_value >= 0.01

        rows.append(
            {
                "file_name": file_name,
                "test_name": test_name,
                "p_value": p_value,
                "passed": passed,
                "raw_result": str(outcome),
            }
        )

    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch-run the NIST test suite on multiple bitstring files."
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing .txt bitstring files.",
    )
    parser.add_argument(
        "--pattern",
        default="*.txt",
        help="Glob pattern for matching files inside input-dir. Default: *.txt",
    )
    parser.add_argument(
        "--long-csv-out",
        default=None,
        help="Optional path to save long-form results CSV.",
    )
    parser.add_argument(
        "--pivot-csv-out",
        default=None,
        help="Optional path to save pivoted pass/fail summary CSV.",
    )
    return parser.parse_args()


def main_cli() -> None:
    args = parse_args()

    input_dir = Path(args.input_dir).resolve()
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    files = sorted(input_dir.glob(args.pattern))
    if not files:
        raise FileNotFoundError(
            f"No files matched pattern '{args.pattern}' in {input_dir}"
        )

    all_rows: list[dict[str, Any]] = []

    print(f"Found {len(files)} files.")
    for file_path in files:
        print(f"Testing: {file_path.name}")
        bits = read_bitstring(file_path)
        results = main(data=bits)
        all_rows.extend(extract_rows(file_path.name, results))

    df = pd.DataFrame(all_rows)

    print("\n=== BATCH RESULTS (head) ===")
    print(df.head().to_string(index=False))

    if args.long_csv_out:
        long_csv = Path(args.long_csv_out).resolve()
        long_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(long_csv, index=False)
        print(f"\nSaved long-form CSV to: {long_csv}")

    if args.pivot_csv_out:
        pivot_csv = Path(args.pivot_csv_out).resolve()
        pivot_csv.parent.mkdir(parents=True, exist_ok=True)

        pivot = (
            df.assign(passed_num=df["passed"].fillna(False).astype(int))
              .pivot_table(
                  index="file_name",
                  columns="test_name",
                  values="passed_num",
                  aggfunc="sum",
                  fill_value=0,
              )
              .reset_index()
        )

        pivot.to_csv(pivot_csv, index=False)
        print(f"Saved pivot summary CSV to: {pivot_csv}")


if __name__ == "__main__":
    main_cli()