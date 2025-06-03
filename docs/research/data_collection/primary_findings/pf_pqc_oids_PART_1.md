# Primary Findings: Object Identifiers (OIDs) for NIST PQC Standards - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Tool: `get_documentation`, Query: "Official Object Identifiers (OIDs) for NIST PQC standards ML-KEM (CRYSTALS-Kyber), ML-DSA (CRYSTALS-Dilithium), SLH-DSA (SPHINCS+)", Context: "Locate and list assigned OIDs for different security levels/variants of these PQC algorithms, as used in X.509 certificates or other cryptographic standards (e.g., IETF RFCs, PKCS).") - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings on Object Identifiers (OIDs) for the NIST Post-Quantum Cryptography (PQC) standards: ML-KEM (CRYSTALS-Kyber), ML-DSA (CRYSTALS-Dilithium), and SLH-DSA (SPHINCS+). OIDs are crucial for identifying these algorithms in contexts like X.509 certificates and other cryptographic protocols.

## 1. General Status of PQC OID Assignment

*   NIST completed the assignment of OIDs for all newly standardized PQC algorithms (ML-KEM, ML-DSA, SLH-DSA) approximately two weeks after the standards were finalized in August 2024 [5].
*   These OIDs are essential for interoperability and allow systems to unambiguously identify the PQC algorithms being used.

## 2. OIDs for ML-KEM (CRYSTALS-Kyber)

An IETF draft document, `draft-uni-qsckeys-kyber-00` (dated 2022, so pre-final NIST OID assignment, but indicative of structure), discusses OIDs for CRYSTALS-Kyber parameter sets [4].

*   **Structure:** The `AlgorithmIdentifier` ASN.1 structure is used:
    ```asn.1
    AlgorithmIdentifier ::= SEQUENCE {
      algorithm OBJECT IDENTIFIER,
      parameters pqcAlgorithmParameterName OPTIONAL
    }

    pqcAlgorithmParameterName ::= PrintableString
    ```
    Where `pqcAlgorithmParameterName` would be a string like "kyber512", "kyber768", or "kyber1024".
*   **Proposed OID Arc (from IETF Draft [4]):** The draft proposed OIDs under an arc like `1.3.6.1.4.1.5.8.2.2` for Kyber variants.
    *   `kyber512`: Proposed as `1.3.6.1.4.1.5.8.2.2.1`
    *   `kyber768`: Proposed as `1.3.6.1.4.1.5.8.2.2.2`
    *   `kyber1024`: Proposed as `1.3.6.1.4.1.5.8.2.2.3`
*   **Final NIST OIDs:** While the IETF draft provides a structural basis and proposed OIDs, the definitive, final OIDs assigned by NIST in August/September 2024 should be consulted from official NIST publications or registries. The search results confirm NIST made these assignments [5] but did not list the final numeric OID values themselves.

## 3. OIDs for ML-DSA (CRYSTALS-Dilithium)

*   NIST has assigned OIDs for ML-DSA variants (e.g., Dilithium2, Dilithium3, Dilithium5) [5].
*   The specific numeric OID values and their structure (e.g., the arc under which they are registered) were not detailed in the direct output of this search query. They are expected to be found in NIST's official OID registry or related FIPS documentation.

## 4. OIDs for SLH-DSA (SPHINCS+)

*   NIST has assigned OIDs for SLH-DSA parameter sets (e.g., SPHINCS+-SHAKE-128s, etc.) [5].
*   Similar to ML-DSA, the specific numeric OID values and their registration details were not provided by this search query and would need to be sourced from official NIST documentation.

## 5. Usage in X.509 Certificates and Protocols

*   The assigned OIDs will be used in the `algorithm` field of ASN.1 structures like `AlgorithmIdentifier` within X.509 certificates (e.g., in `SubjectPublicKeyInfo` to identify the public key type, and in `signatureAlgorithm` to identify the signature algorithm used on the certificate).
*   Protocols like TLS will also use these identifiers (or corresponding codepoints/names) to negotiate PQC algorithms.

## 6. Identified Knowledge Gaps from this Search (Related to G1.2)

*   **Definitive List of Final NIST OIDs:** The primary gap remains: a consolidated, official list of the *final numeric OID values* assigned by NIST for all security levels/variants of ML-KEM, ML-DSA, and SLH-DSA. While their assignment is confirmed [5] and a structural example for Kyber exists [4], the actual values are missing from the current search output.
*   **OID Registration Details:** Information on where these OIDs are formally registered (e.g., specific branches of the OID tree managed by NIST or other bodies).

*(This document will be updated or appended as more information is gathered, particularly once the final numeric OID values are located from official NIST sources.)*