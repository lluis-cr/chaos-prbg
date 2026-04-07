#!/usr/bin/env python3

import os
import glob
import re
from tests_main import main  # Import your existing test battery

def analyze_scale():
    """
    This optimized script:
      - Looks in 'data/scale/' for files named 'scale_k<kVal>_file<idx>.txt'
      - e.g. scale_k3_file1.txt => k=3
      - Reads each file's bits, runs tests_main.main(data=bits).
      - Sums the pass/fail for each test at each k.
      - Produces one table with rows= test names, columns= k=..., cell= pass count (0..10).
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    scale_dir  = os.path.join(script_dir, "data", "scale")

    print("Scale-based folder:", scale_dir)

    # 1) Gather all scale-based files
    pattern = os.path.join(scale_dir, "scale_k*_file*.txt")
    scale_files = sorted(glob.glob(pattern))
    print("Found scale files:", scale_files)

    # Data structures
    # passCount[kVal][testName] => how many sequences in [0..10] passed
    passCount = {}
    all_test_names = set()
    k_values = set()

    def process_scale_file(fname):
        """
        Parse e.g. 'scale_k5_file3.txt' => k=5, file=3
        Read bits, run test battery, accumulate pass counts.
        """
        base = os.path.basename(fname)
        # e.g. scale_k10_file3.txt => re.match -> group(1)=10, group(2)=3
        m = re.match(r"scale_k(\d+)_file(\d+)\.txt", base)
        if not m:
            print(f"Warning: {fname} does not match 'scale_k<k>_file<n>.txt'")
            return

        kStr  = m.group(1)  # e.g. "10"
        fileN = m.group(2)  # e.g. "3"
        kVal  = int(kStr)
        k_values.add(kVal)

        with open(fname, "r") as f:
            bitstring = f.read().strip()

        if not bitstring:
            print(f"Warning: {fname} is empty.")
            return

        results = main(data=bitstring)  # e.g. [ (testName, (p_value, success)), ... ]

        if kVal not in passCount:
            passCount[kVal] = {}

        for (testName, outcome) in results:
            all_test_names.add(testName)
            # outcome can be (pval, success) or dict with outcome["success"]
            if isinstance(outcome, tuple):
                pval, succ = outcome
                if succ:
                    passCount[kVal][testName] = passCount[kVal].get(testName, 0) + 1
            elif isinstance(outcome, dict):
                if outcome.get("success", False):
                    passCount[kVal][testName] = passCount[kVal].get(testName, 0) + 1

    # 2) Process all scale-based files
    for sf in scale_files:
        process_scale_file(sf)

    # 3) Sort the test names and k values
    testNamesSorted = sorted(all_test_names, key=_test_sort_key)
    sorted_kvals    = sorted(k_values)

    # 4) Build a table: each row = test name, each column = k=...
    from tabulate import tabulate

    headers = ["Test Name"] + [f"k={k}" for k in sorted_kvals]
    table_data = []
    for tName in testNamesSorted:
        row = [tName]
        for kv in sorted_kvals:
            c = passCount.get(kv, {}).get(tName, 0)
            row.append(c)  # pass count (0..10)
        table_data.append(row)

    print("\n=== SCALE-BASED TABLE (ASCII) ===")
    ascii_table = tabulate(table_data, headers=headers, tablefmt="pretty")
    print(ascii_table)

    latex_snippet = tabulate(table_data, headers=headers, tablefmt="latex")
    print("\n=== SCALE-BASED TABLE (LaTeX) ===\n")
    print(latex_snippet)
    print("\n(Copy/paste into your .tex if desired)\n")

def _test_sort_key(tName):
    """
    Sort test names by numeric prefix. E.g. "01. Frequency Test" => 1
    Fallback to 9999 if no prefix, so they appear last.
    """
    import re
    m = re.match(r"(\d+)\.", tName)
    if m:
        return int(m.group(1))
    else:
        return 9999

if __name__ == "__main__":
    analyze_scale()
