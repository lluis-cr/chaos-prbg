import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from collections import Counter

# --- Load binary sequence ---
file_path = Path("~/Documents/PythonProjects/binary/BenfordRNG/src/randomness_testsuite/data/scale/scale_k6_file6.txt").expanduser()
with file_path.open( "r") as file:
    binary_sequence = file.read().strip()

# --- Convert to ±1 and compute cumulative sum (random walk) ---
sequence = np.array([1 if bit == '1' else -1 for bit in binary_sequence])
cumsum_vals = np.cumsum(sequence)
cumsum_vals = np.concatenate(([0], cumsum_vals, [0]))

# --- Count zero-crossing cycles ---
positions = np.where(cumsum_vals == 0)[0]
cycles = [cumsum_vals[positions[i]:positions[i+1]+1] for i in range(len(positions)-1)]
num_cycles = len(cycles)
print("Number of valid excursions (cycles):", num_cycles)

# --- Visualize the cumulative sum (random walk) ---
plt.figure(figsize=(12, 5))
plt.plot(cumsum_vals, linewidth=0.7)
plt.title("Cumulative Sum (Random Walk) of the Sequence")
plt.xlabel("Index")
plt.ylabel("Cumulative Sum")
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Count visits to each state of interest ---
states_of_interest = [-4, -3, -2, -1, 1, 2, 3, 4]
state_visit_counts = Counter()
for cycle in cycles:
    for state in states_of_interest:
        state_visit_counts[state] += np.sum(cycle == state)

# --- Bit balance check ---
num_ones = binary_sequence.count('1')
num_zeros = binary_sequence.count('0')
total_bits = len(binary_sequence)
print("Total bits:", total_bits)
print("Number of 1s:", num_ones, f"({100 * num_ones / total_bits:.2f}%)")
print("Number of 0s:", num_zeros, f"({100 * num_zeros / total_bits:.2f}%)")
print("Bit Bias (|1s - 0s|):", abs(num_ones - num_zeros))

# --- Expected state visits based on NIST theoretical probabilities ---
def get_pi_values(x):
    pi_vals = []
    for k in range(6):
        if k == 0:
            val = 1 - 1.0 / (2 * abs(x))
        elif k >= 5:
            val = (1.0 / (2 * abs(x))) * (1 - 1.0 / (2 * abs(x))) ** 4
        else:
            val = (1.0 / (4 * x * x)) * (1 - 1.0 / (2 * abs(x))) ** (k - 1)
        pi_vals.append(val)
    return np.array(pi_vals)

expected_visits = {}
for x in states_of_interest:
    pi_k = get_pi_values(x)
    expected_total = num_cycles * np.sum(pi_k)
    expected_visits[x] = expected_total

# --- Summary table of observed vs expected ---
observed_vs_expected = pd.DataFrame({
    "State": states_of_interest,
    "Observed Visits": [state_visit_counts[x] for x in states_of_interest],
    "Expected Visits": [expected_visits[x] for x in states_of_interest]
})

observed_vs_expected["(O-E)^2 / E"] = (
    (observed_vs_expected["Observed Visits"] - observed_vs_expected["Expected Visits"]) ** 2
    / observed_vs_expected["Expected Visits"]
)

print("\nObserved vs Expected State Visits:")
print(observed_vs_expected)
