#!/usr/bin/env python3
import os
import glob
import re
from tests_main import main  # from your existing test battery

def analyze_params():
    """
    This script looks in:
      data/thresh/<files>   named like:  thresh_0.3_file3.txt
      data/scale/<files>    named like:  scale_5_file2.txt
    Each param => exactly 10 files => passCount[(paramVal, 'thresh')][testName] = X
    We'll build 2 tables:
       1) threshold-based: 6 rows (one per threshold param)
       2) scale-based:     6 rows (one per scale param)
    Each cell is X/10 if you made 10 files for that param.
    """

    # Determine the directories where files are stored
    script_dir = os.path.dirname(os.path.abspath(__file__))
    thresh_dir = os.path.join(script_dir, "data", "thresh")
    scale_dir  = os.path.join(script_dir, "data", "scale")

    print("Threshold folder:", thresh_dir)
    print("Scale folder:",     scale_dir)

    # Find all threshold-based, scale-based files
    # E.g. "thresh_0.3_file7.txt" or "scale_5_file1.txt"
    thresh_files = sorted(glob.glob(os.path.join(thresh_dir, "thresh_*_file*.txt")))
    scale_files  = sorted(glob.glob(os.path.join(scale_dir,  "scale_*_file*.txt")))

    print("Found threshold files:", thresh_files)
    print("Found scale files:",    scale_files)

    # passCount[(paramVal, "thresh")][testName] = integer pass count
    # passCount[(paramVal, "scale")][testName]  = integer pass count
    passCount = {}
    # Keep track of test names to build columns
    all_test_names = set()
    # Keep track of distinct param values for threshold & scale
    thresh_params = set()
    scale_params  = set()

    def process_file(fname, paramVal, transform):
        """
        Reads bits from 'fname', runs test battery, increments pass counts for each test that passes.
        paramVal can be e.g. "0.3" or "5"
        transform is 'thresh' or 'scale'
        """
        with open(fname, "r") as f:
            bitstring = f.read().strip()

        results = main(data=bitstring)  # => [ (testName, outcome), ... ]
        key = (paramVal, transform)
        if key not in passCount:
            passCount[key] = {}
        for (testName, outcome) in results:
            all_test_names.add(testName)
            if isinstance(outcome, tuple):
                pval, succ = outcome
                if succ:
                    passCount[key][testName] = passCount[key].get(testName, 0) + 1
            elif isinstance(outcome, dict):
                if outcome.get("success", False):
                    passCount[key][testName] = passCount[key].get(testName, 0) + 1

    # We'll parse the param from the filename using a regex
    # For threshold => "thresh_(.+)_file(\d+).txt"
    # For scale     => "scale_(.+)_file(\d+).txt"
    def parse_thresh(fname):
        base = os.path.basename(fname)
        m = re.match(r"thresh_(.+)_file(\d+)\.txt", base)
        if not m:
            return None, None
        return m.group(1), m.group(2)  # (paramStr, fileIndex)

    def parse_scale(fname):
        base = os.path.basename(fname)
        m = re.match(r"scale_(.+)_file(\d+)\.txt", base)
        if not m:
            return None, None
        return m.group(1), m.group(2)

    # Process threshold-based files
    for tf in thresh_files:
        paramStr, fIdx = parse_thresh(tf)
        if paramStr is None: 
            continue
        # paramStr might be "0.3" => you can keep as str or convert to float
        thresh_params.add(paramStr)
        process_file(tf, paramStr, "thresh")

    # Process scale-based files
    for sf in scale_files:
        paramStr, fIdx = parse_scale(sf)
        if paramStr is None:
            continue
        scale_params.add(paramStr)
        process_file(sf, paramStr, "scale")

    # Now passCount[(paramVal,"thresh")][testName] => X out of 10
    # Similarly for scale.

    # Build two separate tables

    # 1) threshold-based table
    # Rows => sorted paramStr, columns => sorted test names
    # Each cell => passCount for that param/test
    testNamesSorted = sorted(list(all_test_names), key=_test_sort_key)

    # Convert paramStr to float for sorting if numeric
    def try_float(x):
        try:
            return float(x)
        except ValueError:
            return x  # fallback if it's not numeric
    threshParamSorted = sorted(list(thresh_params), key=try_float)
    scaleParamSorted  = sorted(list(scale_params),  key=try_float)

    print("\n=== THRESHOLD-BASED TABLE ===")
    header = ["ThresholdParam"] + testNamesSorted
    rows = []
    for pVal in threshParamSorted:
        row = [pVal]
        paramKey = (pVal, "thresh")
        for tName in testNamesSorted:
            c = passCount.get(paramKey, {}).get(tName, 0)
            row.append(f"{c}/10")  # we assume 10 files per param => c out of 10
        rows.append(row)
    print_table(header, rows)

    print("\n=== SCALE-BASED TABLE ===")
    header2 = ["ScaleParam"] + testNamesSorted
    rows2   = []
    for pVal in scaleParamSorted:
        row = [pVal]
        paramKey = (pVal, "scale")
        for tName in testNamesSorted:
            c = passCount.get(paramKey, {}).get(tName, 0)
            row.append(f"{c}/10")
        rows2.append(row)
    print_table(header2, rows2)

def _test_sort_key(tName):
    # numeric prefix "01.", "02.", etc
    import re
    m = re.match(r"(\d+)\.", tName)
    if m:
        return int(m.group(1))
    else:
        return 9999

def print_table(header, rows):
    try:
        from tabulate import tabulate
        print(tabulate(rows, headers=header, tablefmt="pretty"))
    except ImportError:
        print(" | ".join(header))
        for r in rows:
            print(" | ".join(r))

if __name__ == "__main__":
    analyze_params()
