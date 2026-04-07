# Results

## Key Outputs
- Binary sequences generated from the chaotic system
- Results from NIST statistical tests

## Observations
- Majority of tests pass, indicating acceptable randomness in most aspects
- Some tests fail (specifically the two Random Excursions tests), indicating structural deviations from expected statistical behaviour, as measured against the chi-squared distribution

## Interpretation
- Failures may be linked to:
  - Finite precision effects
  - Poor binarization strategy
  - Underlying periodic behavior

## Insights
- Chaos alone does not guarantee cryptographic randomness
- Implementation details significantly affect performance (what randomness requirements are necessary in each specific situation)
- Efficiency of PRBG depends on size of key space which is yet to be limited (need further testing)