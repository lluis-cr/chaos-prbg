#!/usr/bin/env python3
"""
run_nist_suite.py

Run the full NIST SP 800-22-style test battery on one bitstring file.

Expected structure:
python/
├── run_nist_suite.py
└── randomness_testsuite/
    └── tests_main.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SUITE_DIR = SCRIPT_DIR / "randomness_testsuite"

if str(SUITE_DIR) not in sys.path:
    sys.path.insert(0, str(SUITE_DIR))

try:
    from tests_main import main, print_results
except ImportError as e:
    raise ImportError(
        f"Could not import tests_main.py from {SUITE_DIR}. "
        "Make sure the randomness_testsuite folder is present and contains tests_main.py."
    ) from e


def read_bitstring(file_path: Path) -> str:
    bits = file_path.read_text(encoding="utf-8").strip()
    if not bits:
        raise ValueError(f"Bitstring file is empty: {file_path}")
    invalid = set(bits) - {"0", "1"}
    if invalid:
        raise ValueError(
            f"Bitstring file contains non-binary characters: {sorted(invalid)}"
        )
    return bits


def to_serializable(obj: Any) -> Any:
    """Convert numpy / tuples / nested outputs into JSON-safe Python objects."""
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, tuple):
        return [to_serializable(x) for x in obj]
    if isinstance(obj, list):
        return [to_serializable(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): to_serializable(v) for k, v in obj.items()}

    # numpy scalars often appear in these results
    try:
        return obj.item()
    except Exception:
        return str(obj)


def run_suite(bitstring: str) -> list[list[Any]]:
    return main(data=bitstring)


def save_results_json(results: list[list[Any]], output_path: Path) -> None:
    serializable = [
        {"test_name": test_name, "result": to_serializable(result)}
        for test_name, result in results
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the NIST test suite on a single bitstring file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input .txt file containing a binary string.",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional path to save raw results as JSON.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console printing of raw results.",
    )
    return parser.parse_args()


def main_cli() -> None:
    args = parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    bitstring = read_bitstring(input_path)
    results = run_suite(bitstring)

    if not args.quiet:
        print(f"\nRunning NIST suite on: {input_path}")
        print(f"Bit length: {len(bitstring)}")
        print_results(results)

    if args.json_out:
        json_path = Path(args.json_out).resolve()
        save_results_json(results, json_path)
        print(f"\nSaved raw JSON results to: {json_path}")


if __name__ == "__main__":
    main_cli()