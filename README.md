# Chaos-Based Pseudo-Random Bit Generator (PRBG)

## Overview
This project investigates the viability of chaos-based pseudo-random bit generators (PRBGs) for cryptographic applications. It focuses on generating binary sequences from chaotic systems and evaluating their statistical randomness using established testing frameworks.

## Objective
To determine whether a chaos-based generator can produce bit sequences that satisfy statistical randomness criteria (NIST SP800-22), and to identify the factors that influence performance.

## Method

### Chaotic Generator
Logistic map used in the chaotic regime:
x_{n+1} = r x_n (1 - x_n)

### Binarization
Real-valued outputs are transformed into binary using fixed-point scaling and bit extraction:
    - Each value is scaled by \(2^B\)
    - The integer part is extracted
    - Binary representation is computed
    - B bits are extracted (least significant bits)

### Evaluation
Generated sequences are tested using the NIST SP800-22 statistical test suite

## Repository Structure
- `src/` → core implementation (R + Python)
- `docs/` → full modelling process and reasoning
- `outputs/` → test results and generated data
- `archive/` → legacy or experimental code

## Results
- The generator produces sequences that pass the majority of NIST statistical tests
- Some tests fail (specifically the Random Excursions tests), indicating structural deviations from expected statistical behaviour
- Failures are linked to:
  - finite precision effects
  - intrinsic properties of the chaotic map
  - the chosen bit extraction method

## Key Insights
- Chaos alone does not guarantee cryptographic randomness  
- The binarization (bit extraction) process is a critical determinant of statistical quality  
- Finite precision can introduce hidden periodicity, degrading randomness  

## How to Run
1. Install dependencies:
pip install -r requirements.txt

2. Generate sequences:
python src/python/main.py

3. Statistical Testing
Statistical evaluation is performed using the NIST SP800-22 test suite.

This project uses an external implementation available here:
(https://github.com/stevenang/randomness_testsuite/tree/master)

Refer to that repository for:
- installation instructions
- running individual tests
- interpretation of results

Generated bit sequences from this project can be used as input to the test suite.

## Limitations
- Passing statistical tests does not guarantee cryptographic security  
- Results depend on parameter selection and extraction method  
- Finite precision affects chaotic dynamics  

## Next Steps
- Improve binarization techniques  
- Explore alternative chaotic maps  
- Analyse key space regions  
- Benchmark against standard PRNGs  
