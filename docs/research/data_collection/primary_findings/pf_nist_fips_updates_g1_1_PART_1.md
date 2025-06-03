# Primary Findings: NIST FIPS 203, 204, 205 Updates (Addressing Gap G1.1)

**Date Compiled:** 2025-06-02
**Research Focus:** G1.1: Definitive NIST FIPS 203, 204, 205 details (if any updates since last research).
**Source:** AI Search (Perplexity MCP) - Query: "Latest official publication status, key details, and any updates or errata since August 2024 for NIST FIPS 203 (ML-KEM/Kyber), FIPS 204 (ML-DSA/Dilithium), and FIPS 205 (SLH-DSA/SPHINCS+). Provide direct links to official NIST documents."

This document summarizes the latest information on the specified NIST FIPS documents relevant to Post-Quantum Cryptography.

## NIST FIPS PQC Standards Overview

NIST's post-quantum cryptography standardization reached critical milestones in 2024-2025 with three finalized standards. Active development in supporting documentation and further standardization continues.

### FIPS 203: Module-Lattice-based Key-Encapsulation Mechanism Standard (ML-KEM)
*   **Formerly:** Kyber
*   **Current Status:** Finalized August 13, 2024.
    *   **Official Document:** [NIST FIPS 203 PDF](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf)
*   **Primary Use:** General-purpose public-key encryption (Key Encapsulation Mechanism).
*   **Key Features (as reported by search):**
    *   Offers various security levels. For example, Kyber-768 aims for security comparable to AES-192, with public keys around 1184 bytes and ciphertexts around 1088 bytes. (Note: The search result mentioned "1,024-bit security with 768-byte public keys" which seems to conflate security level with a parameter set name; FIPS 203 itself details specific parameter sets like ML-KEM-512, ML-KEM-768, ML-KEM-1024).
    *   Designed for efficiency, with relatively small key and ciphertext sizes compared to some other PQC families.
    *   Reported encryption/decryption speeds under 2ms on modern CPUs.
*   **Updates & Supporting Documents (since August 2024):**
    *   NIST Special Publication (SP) 800-227 (Draft, January 2025): "Guidelines for ML-KEM Implementations." This document provides implementation guidance for FIPS 203.
    *   NIST will review the standard every five years (next review by 2029) and monitor for weaknesses.
*   **Security Monitoring:** Comments and potential vulnerabilities can be reported to fips-203-comments@nist.gov.
*   **Errata:** No substantive changes or errata have been reported for FIPS 203 since its release in August 2024.

### FIPS 204: Module-Lattice-based Digital Signature Standard (ML-DSA)
*   **Formerly:** Dilithium
*   **Current Status:** Finalized August 13, 2024.
    *   **Official Document:** Available via the [NIST Computer Security Resource Center (CSRC) Publications](https://csrc.nist.gov/publications/search?series%5B%5D=FIPS). (Direct link not provided in search results, but it follows the same pattern, e.g., `https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.204.pdf`).
*   **Primary Use:** Digital signatures.
*   **Key Features (as reported by search):**
    *   Offers various security levels. For example, Dilithium2 aims for security comparable to AES-128, with public keys around 1312 bytes and signatures around 2420 bytes. (Search mentioned "128-bit security with 1,312-byte signatures" - likely referring to a specific parameter set).
    *   Reported 2.7x faster verification than RSA-3076.
*   **Development Context:**
    *   Expected to replace a significant percentage (e.g., 92%) of NIST's current signature use cases by 2026.
    *   Interoperability testing with major TLS implementations is ongoing.
*   **Errata:** No substantive changes or errata have been reported for FIPS 204 since its release in August 2024.

### FIPS 205: Stateless Hash-Based Digital Signature Standard (SLH-DSA)
*   **Formerly:** SPHINCS+
*   **Current Status:** Finalized August 13, 2024.
    *   **Official Document:** Available via the [NIST CSRC Publications](https://csrc.nist.gov/publications/search?series%5B%5D=FIPS). (Direct link not provided in search results, e.g., `https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.205.pdf`).
*   **Primary Use:** Digital signatures, often considered as a backup or alternative to lattice-based signatures due to its different mathematical foundation.
*   **Key Features (as reported by search):**
    *   Hash-based construction, offering security based on well-understood hash functions.
    *   Offers various security levels and parameter sets (e.g., SPHINCS+-SHA256-128f, SPHINCS+-SHAKE256-128s).
    *   Signatures can be larger (e.g., SPHINCS+-SHA256-128f signatures are around 17KB, search mentioned 41kB which might be for a higher security level or different variant).
*   **Adoption Timeline & Guidance:**
    *   May be required for systems needing dual-signature fallback by Q2 2026.
    *   NSA guidance reportedly recommends parallel deployment with ML-DSA.
*   **Errata:** No substantive changes or errata have been reported for FIPS 205 since its release in August 2024.

## Post-Standardization Developments & Future Outlook

1.  **HQC (Key Encapsulation Mechanism):**
    *   NIST announced HQC (code-based KEM) as a backup algorithm to ML-KEM in March 2025.
    *   A draft standard for HQC is expected in 2026.
2.  **FALCON (Digital Signature Algorithm):**
    *   FALCON (a lattice-based signature algorithm, distinct from Dilithium) is expected to be standardized as FIPS 206.
    *   It was entering final review, with a target release in late 2025.
3.  **Migration Guidance:**
    *   NIST plans to release sector-specific transition frameworks and migration guides by Q3 2025, prioritizing areas like healthcare and critical infrastructure.

## Summary of Updates Since August 2024

*   The core FIPS 203, 204, and 205 documents themselves have not undergone substantive changes or received errata since their finalization in August 2024.
*   Supporting documentation, such as implementation guidelines (e.g., SP 800-227 for ML-KEM), is being developed.
*   The broader PQC standardization process continues with algorithms like HQC and FALCON moving towards standardization.

This information addresses knowledge gap G1.1 by providing the latest status and details for the initial set of NIST PQC standards.