# Primary Findings: PQC Algorithm Security Level Comparisons (Addressing Gap G1.4)

**Date Compiled:** 2025-06-02
**Research Focus:** G1.4: Security level comparisons (NIST levels) for chosen algorithms.
**Source:** AI Search (Perplexity MCP) - Query: "Comparison of NIST PQC security levels (Level 1, 2, 3, 4, 5) for Kyber (ML-KEM), Dilithium (ML-DSA), Falcon, and SPHINCS+ (SLH-DSA). Explain what each NIST security level corresponds to in terms of classical cryptographic algorithm strength (e.g., AES key sizes, SHA hash output sizes). Provide specific parameter sets for each PQC algorithm that meet these NIST levels. Cite NIST FIPS documents or official NIST PQC project reports."

This document summarizes findings on NIST PQC security levels and how selected algorithms (Kyber, Dilithium, Falcon, SPHINCS+) map to these levels with specific parameter sets.

## NIST PQC Security Categories

NIST defines five security categories (or levels) for PQC algorithms. These levels are benchmarked against the difficulty of breaking well-established classical cryptographic algorithms, both by classical computers and (hypothetically) by large-scale quantum computers.

*   **Level 1:** Security comparable to AES-128 key exhaustion (or SHA256 collision search). Considered the minimum acceptable strength for most new applications.
*   **Level 2:** Security comparable to finding a SHA-384 collision. (Note: Sometimes this level is associated with AES-192 strength, but the primary benchmark is often hash collision resistance for this intermediate level).
*   **Level 3:** Security comparable to AES-192 key exhaustion.
*   **Level 4:** Security comparable to finding a SHA-512 collision. (Similar to Level 2, this intermediate level is often benchmarked against hash collision).
*   **Level 5:** Security comparable to AES-256 key exhaustion. Represents the highest security strength defined by NIST for PQC.

It's important to note that "comparable security" means that attacking the PQC algorithm (with the best known classical or quantum attacks) is considered at least as hard as breaking the corresponding classical primitive.

## Algorithm Parameter Sets and NIST Security Levels

The following tables detail specific parameter sets for Kyber, Dilithium, Falcon, and SPHINCS+ that meet these NIST security levels, based on their respective FIPS documents (FIPS 203 for ML-KEM, FIPS 204 for ML-DSA, FIPS 205 for SLH-DSA) and NIST PQC project reports.

### CRYSTALS-Kyber (ML-KEM) - FIPS 203

| NIST Security Level | Kyber Parameter Set | Classical Equivalent | Public Key (bytes) | Private Key (bytes) | Ciphertext (bytes) |
|---------------------|---------------------|----------------------|--------------------|---------------------|--------------------|
| 1                   | `ML-KEM-512`        | AES-128              | 800                | 1632                | 768                |
| 3                   | `ML-KEM-768`        | AES-192              | 1184               | 2400                | 1088               |
| 5                   | `ML-KEM-1024`       | AES-256              | 1568               | 3168                | 1568               |

### CRYSTALS-Dilithium (ML-DSA) - FIPS 204

| NIST Security Level | Dilithium Parameter Set | Classical Equivalent | Public Key (bytes) | Private Key (bytes) | Signature (bytes) |
|---------------------|-------------------------|----------------------|--------------------|---------------------|-------------------|
| 2                   | `ML-DSA-44` (Dilithium2) | AES-128 / SHA-256    | 1312               | 2528                | 2420              |
| 3                   | `ML-DSA-65` (Dilithium3) | AES-192 / SHA-384    | 1952               | 4000                | 3293              |
| 5                   | `ML-DSA-87` (Dilithium5) | AES-256 / SHA-512    | 2592               | 4864                | 4595              |
*(Note: FIPS 204 maps ML-DSA-44 to Level 2, ML-DSA-65 to Level 3, and ML-DSA-87 to Level 5. The classical equivalencies are often simplified; Level 2 aims for >128-bit strength, Level 3 for >192-bit, and Level 5 for >256-bit against all attackers).*

### Falcon - (To be standardized, e.g., FIPS 206 Draft)

Falcon is designed for situations requiring smaller signature sizes, often targeting higher security levels.

| NIST Security Level | Falcon Parameter Set | Classical Equivalent | Public Key (bytes) | Private Key (bytes) | Signature (bytes) |
|---------------------|----------------------|----------------------|--------------------|---------------------|-------------------|
| 1                   | `Falcon-512`         | AES-128              | 897                | 1281                | 690 (avg)         |
| 5                   | `Falcon-1024`        | AES-256              | 1793               | 2305                | 1330 (avg)        |
*(Note: Falcon parameter names directly indicate the polynomial degree 'n'. Falcon-512 targets Level 1, Falcon-1024 targets Level 5. Intermediate levels might be achievable with other parameterizations not yet fully standardized or commonly benchmarked under these specific level categories.)*

### SPHINCS+ (SLH-DSA) - FIPS 205

SPHINCS+ offers various parameter sets based on the underlying hash function (SHA-256 or SHAKE256) and other parameters (e.g., `n`, `k`, `h`, `d`, `w`). The "f" (fast) variants prioritize speed, while "s" (small) variants prioritize smaller signatures.

| NIST Security Level | SPHINCS+ Parameter Set Example         | Classical Equivalent | Public Key (bytes) | Private Key (bytes) | Signature (bytes) |
|---------------------|----------------------------------------|----------------------|--------------------|---------------------|-------------------|
| 1                   | `SLH-DSA-SHA2-128f` (SPHINCS+-SHA256-128f) | AES-128              | 32                 | 64                  | 17088             |
| 1                   | `SLH-DSA-SHAKE-128f` (SPHINCS+-SHAKE256-128f)| AES-128              | 32                 | 64                  | 17088             |
| 1                   | `SLH-DSA-SHA2-128s` (SPHINCS+-SHA256-128s) | AES-128              | 32                 | 64                  | 7856              |
| 3                   | `SLH-DSA-SHA2-192f`                    | AES-192              | 48                 | 96                  | 35664             |
| 3                   | `SLH-DSA-SHAKE-192s`                   | AES-192              | 48                 | 96                  | 16224             |
| 5                   | `SLH-DSA-SHA2-256f`                    | AES-256              | 64                 | 128                 | 49856             |
| 5                   | `SLH-DSA-SHAKE-256s`                   | AES-256              | 64                 | 128                 | 29792             |

**Key Points for SPHINCS+:**
*   Public and private keys are very small.
*   Signatures are significantly larger than lattice-based schemes like Dilithium or Falcon.
*   Security relies on the properties of the underlying hash functions.

## References:

*   **NIST FIPS 203:** Module-Lattice-based Key-Encapsulation Mechanism Standard (ML-KEM).
*   **NIST FIPS 204:** Module-Lattice-based Digital Signature Standard (ML-DSA).
*   **NIST FIPS 205:** Stateless Hash-Based Digital Signature Standard (SLH-DSA).
*   Various NIST PQC Project reports and presentations (e.g., those by Regenscheid, Newhouse, and others involved in the standardization process).
*   NIST IR 8547: "Status Report on the Third Round of the NIST Post-Quantum Cryptography Standardization Process" (and subsequent status reports).

This information addresses knowledge gap G1.4 by comparing NIST PQC security levels for the chosen algorithms and providing corresponding parameter sets.