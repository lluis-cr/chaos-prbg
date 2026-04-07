# Method

## Approach
This project uses a chaos-based approach to generate pseudo-random binary sequences. The logistic map is iterated to produce a sequence of real numbers, which are then transformed into binary values. Said bitstreams are put through a statistical randomness test suite to validate them as secure keys for cryptographic algorithms.

## Model Components

### 1. Chaotic Generator
- Logistic map:
  x_{n+1} = r x_n (1 - x_n)
- Parameter r chosen in chaotic regime

### 2. Binarization
Real-valued outputs from the logistic map are converted into binary sequences using a fixed-point scaling and bit extraction method.

For each value \(x_n \in (0,1)\):
- The value is scaled by \(2^B\)
- The integer part is extracted:
  y_n = floor(x_n · 2^B)
- The resulting integer is converted into its binary representation
- B bits are extracted from this representation (which correspond to the least significant bits of the scaled integer)

This method allows multiple bits to be derived from each iteration of the chaotic map, but may introduce statistical biases depending on the choice of B and the underlying dynamics.

The choice of B introduces a trade-off:
- Larger B increases bit output per iteration
- However, it may amplify correlations or biases in the sequence

### 3. Statistical Testing
- Generated sequences are tested using NIST SP800-22
- Tests include:
  - Frequency test
  - Runs test
  - Others depending on implementation

## Tools Used
- R for sequences generation and transformation
- Python for implementation
- External NIST testing suite (also Python)

## Pipeline
1. Initialize parameters and seed
2. Generate chaotic sequence
3. Convert to binary sequence
4. Run statistical tests
5. Store and analyze results
6. Show applicability in cryptographic algorithm