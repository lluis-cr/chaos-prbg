# test_all.py
import os
import glob
from tests_main import main, print_results  # from your existing tests_main.py

def test_all():
    # 1) Identify the directory of this script (so we can find files next to it):
    folder = os.path.dirname(os.path.abspath(__file__))

    # 2) Gather the threshold-based and scale-based .txt files
    thresh_files = sorted(glob.glob(os.path.join(folder, "thresh_*.txt")))
    scale_files = sorted(glob.glob(os.path.join(folder, "scale_*.txt")))

    # We'll store results in a list of (filename, testResults)
    all_results = []

    # 3) For each threshold-based file, read bits and run tests
    for tf in thresh_files:
        with open(tf, "r") as f:
            data = f.read().strip()   # big string of '0'/'1'
        # Call tests_main.py's main() function
        results = main(data=data)
        all_results.append((tf, results))

    # 4) Same for scale-based
    for sf in scale_files:
        with open(sf, "r") as f:
            data = f.read().strip()
        results = main(data=data)
        all_results.append((sf, results))

    # 5) Print everything
    for filename, rset in all_results:
        print(f"\n=== Results for {filename} ===")
        print_results(rset)

if __name__ == "__main__":
    test_all()
import os

print("Current working directory (os.getcwd()):", os.getcwd())

this_script_dir = os.path.dirname(os.path.abspath(__file__))
print("Directory containing test_all.py:", this_script_dir)

print("Listing files in that directory:")
print(os.listdir(this_script_dir))
