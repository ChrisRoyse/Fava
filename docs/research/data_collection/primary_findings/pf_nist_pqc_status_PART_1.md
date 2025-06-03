# Primary Findings: NIST PQC Standardization Status and Timelines - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "Latest updates and timelines for NIST PQC standardization, selected algorithms for KEMs and digital signatures, and their characteristics (key sizes, signature sizes, performance benchmarks).", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings regarding the NIST Post-Quantum Cryptography (PQC) standardization process, focusing on timelines, selected algorithms, and their general characteristics.

## 1. Standardization Timeline Overview

The NIST PQC standardization process has been ongoing since 2016 and is moving towards finalization, with several key milestones achieved and upcoming:

*   **2016-2022:** Initial algorithm submissions and multiple rounds of evaluation [5].
*   **August 2024:** Finalization of the first three PQC standards [4]:
    *   **FIPS 203:** Module-Lattice-based Key-Encapsulation Mechanism (ML-KEM), widely known as CRYSTALS-Kyber.
    *   **FIPS 204:** Module-Lattice-based Digital Signature Algorithm (ML-DSA), widely known as CRYSTALS-Dilithium.
    *   **FIPS 205:** Stateless Hash-Based Digital Signature Algorithm (SLH-DSA), an instantiation of SPHINCS+.
*   **March 11, 2025:** HQC (Hamming Quasi-Cyclic) was selected as the fifth algorithm for standardization, primarily for KEM use [2, 3].
*   **September 2025 (Planned):** The Sixth PQC Standardization Conference is scheduled, likely for further discussions and updates [1].
*   **2025 (Expected):** Draft standard for FALCON/FN-DSA (FIPS 206) for digital signatures [3].
*   **2026 (Expected):** Draft standard publication for HQC [3].
*   **2027 (Expected):** Final standard publication for HQC [3].

NIST encourages organizations to begin transitioning to the already finalized PQC standards [4].

## 2. Selected Algorithms and General Characteristics

### 2.1. Key Encapsulation Mechanisms (KEMs)

| Algorithm Name (Common Name) | Standardization Status | Cryptographic Basis | Key Characteristics / Notes                               |
| :--------------------------- | :--------------------- | :------------------ | :-------------------------------------------------------- |
| **ML-KEM** (CRYSTALS-Kyber)  | Finalized (FIPS 203)   | Lattice-based       | Optimized for performance [4, 5].                         |
| **HQC**                      | Selected (March 2025)  | Code-based          | Noted for resistance to side-channel attacks [2, 3].      |

### 2.2. Digital Signature Algorithms

| Algorithm Name (Common Name)      | Standardization Status     | Cryptographic Basis | Key Characteristics / Notes                               |
| :-------------------------------- | :------------------------- | :------------------ | :-------------------------------------------------------- |
| **ML-DSA** (CRYSTALS-Dilithium)   | Finalized (FIPS 204)       | Lattice-based       | Modular design [4].                                       |
| **SLH-DSA** (SPHINCS+)            | Finalized (FIPS 205)       | Hash-based          | Stateless signatures [4].                                 |
| **FALCON / FN-DSA**               | Draft Expected 2025 (FIPS 206) | Lattice-based       | Aims for smaller signature sizes compared to ML-DSA [3]. |

### 2.3. General Evaluation Criteria

NIST's selection process for these algorithms emphasizes several criteria [3, 5]:

*   **Security:** Primarily, resistance against attacks by both classical and quantum computers.
*   **Performance:** Efficiency in terms of computational speed for key generation, encapsulation/decapsulation, signing, and verification.
*   **Implementation Characteristics:** Including key sizes, signature sizes, and ease of implementation.
*   **Compatibility:** Considerations for integration into existing protocols and infrastructure.

## 3. Transition Deadlines for Classical Cryptography

The broader context for PQC adoption includes NIST's guidance on phasing out classical public-key algorithms vulnerable to quantum attacks:

*   **By 2030:** Vulnerable algorithms (e.g., ECDSA, RSA, classical DH, EdDSA for signatures) are to be deprecated [3].
*   **By 2035:** These classical methods are to be disallowed entirely [3].

This provides a 5-10 year window for migration, reinforcing the recommendation to adopt standardized PQC algorithms promptly [3, 4].

## 4. Identified Knowledge Gaps from this Search

*   **Specific Key Sizes, Signature Sizes, and Performance Benchmarks:** While the search confirmed these are key evaluation criteria, the provided results did not contain specific quantitative data (e.g., Kyber-768 key sizes in bytes, Dilithium-III signature sizes, typical operation latencies) for the standardized algorithms. This information is expected to be detailed in the official FIPS publications and related NIST documentation. **Further targeted research is needed to obtain these specific metrics.**
*   **Official OIDs:** Object Identifiers for these algorithms were not mentioned in the search results.

*(This document will be updated or appended as more information is gathered.)*