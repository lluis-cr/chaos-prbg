# Problem Definition

## Main Question
Can chaos-based pseudo-random bit generators (PRBGs) produce sequences that satisfy statistical randomness tests required for cryptographic applications?

## Why it Matters
Secure cryptographic systems rely on high-quality randomness for key generation and encryption processes. Traditional pseudo-random number generators (PRNGs) are deterministic and rely on computational hardness assumptions for security.

Advances in computational capabilities, including quantum computing, challenge some of these assumptions by reducing the difficulty of certain problems. As a result, the robustness of underlying components such as random number generation becomes increasingly critical.

Chaos-based systems have been proposed as alternatives due to their sensitivity to initial conditions and complex dynamics. However, practical implementations may suffer from finite precision effects and structural weaknesses that impact randomness.

This project evaluates whether chaos-based PRBGs can produce sequences that meet statistical randomness standards required for cryptographic use.

## Target Outcome
What does success look like?
- Generate binary sequences using a chaos-based system
- Evaluate randomness using statistical tests (NIST SP800-22)
- Identify strengths and weaknesses of the approach