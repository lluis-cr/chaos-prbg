#!/usr/bin/env python3
import os
import glob
import re

from tests_main import main  # from your existing tests_main.py

def process_file(filename, passCounter, all_test_names):
    """
    Reads a bitstring from 'filename',
    runs tests_main.main(data=bitstring),
    and increments passCounter[testName] if that sequence passes the test.
    Also adds each testName to all_test_names for sorting later.
    """
    with open(filename, "r") as f:
        bitstring = f.read().strip()

    results = main(data=bitstring)
    # results is typically [ (testName, outcome), (testName, outcome), ... ]

    for (testName, outcome) in results:
        # Track the test name
        all_test_names.add(testName)
        # 'outcome' might be a tuple (p_value, success) or a dict with outcome["success"]
        if isinstance(outcome, tuple):
            # If it's (pval, succ)
            pval, succ = outcome
            if succ:
                passCounter[testName] = passCounter.get(testName, 0) + 1
        elif isinstance(outcome, dict):
            # If it's a dict
            if outcome.get("success", False):
                passCounter[testName] = passCounter.get(testName, 0) + 1
        else:
            # Unexpected format
            print(f"Warning: test '{testName}' returned unknown outcome format: {outcome}")

def _test_sort_key(tName):
    """
    Helps sort test names by their prefix "01.", "02.", etc.
    If there's no prefix number, fallback to alphabetical.
    """
    match = re.match(r"(\d+)\.", tName)
    if match:
        return int(match.group(1))
    else:
        return 9999

def print_table(header, rows):
    """
    A simple function to print an ASCII table of pass counts.
    If you have 'tabulate' installed, you can use that for a prettier table.
    """
    try:
        from tabulate import tabulate
        print(tabulate(rows, headers=header, tablefmt="pretty"))
    except ImportError:
        # fallback manual printing
        print(" | ".join(header))
        for r in rows:
            print(" | ".join(r))

def analyze_all():
    """
    1) Finds 'thresh_*.txt' and 'scale_*.txt'
    2) Runs tests_main.main(...) on each file
    3) Accumulates pass counts for each test
    4) Prints a table: columns = test names, rows = threshold vs scale
    """

    folder = os.path.dirname(os.path.abspath(__file__))

    # Gather the threshold-based and scale-based text files
    thresh_files = sorted(glob.glob(os.path.join(folder, "thresh_*.txt")))
    scale_files  = sorted(glob.glob(os.path.join(folder, "scale_*.txt")))

    print("Found threshold files:", thresh_files)
    print("Found scale files:",    scale_files)

    # We'll track pass counts in dictionaries:
    threshPassCount = {}
    scalePassCount  = {}

    # We also want to keep track of all test names
    all_test_names  = set()

    # Process threshold-based files
    for tf in thresh_files:
        print(f"Processing threshold file: {tf}")
        process_file(tf, threshPassCount, all_test_names)

    # Process scale-based files
    for sf in scale_files:
        print(f"Processing scale file: {sf}")
        process_file(sf, scalePassCount, all_test_names)

    # Now we expect each set (threshold, scale) to have 10 files,
    # so each test can get up to 10 passes.
    testNamesSorted = sorted(list(all_test_names), key=_test_sort_key)

    # Build final table: 2 rows, one for threshold, one for scale
    header = ["Transformation"] + testNamesSorted
    rowThreshold = ["Threshold-based"]
    rowScale     = ["Scale-based"]

    for tName in testNamesSorted:
        tcount = threshPassCount.get(tName, 0)
        rowThreshold.append(f"{tcount}/10")

        scount = scalePassCount.get(tName, 0)
        rowScale.append(f"{scount}/10")

    # Print the table
    print("\n=== FINAL PASS-COUNT TABLE ===")
    print_table(header, [rowThreshold, rowScale])

if __name__ == "__main__":
    analyze_all()
