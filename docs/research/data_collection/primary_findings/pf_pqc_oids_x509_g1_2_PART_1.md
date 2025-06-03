# Primary Findings: PQC Algorithm OIDs for X.509 and CMS (Addressing Gap G1.2)

**Date Compiled:** 2025-06-02
**Research Focus:** G1.2: Finalized OIDs for PQC KEMs/Signatures in X.509.
**Source:** AI Search (Perplexity MCP) - Query: "Official or widely adopted OIDs (Object Identifiers) for NIST PQC algorithms ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+), and Falcon for use in X.509 certificates and CMS (Cryptographic Message Syntax). Include references to IETF drafts or relevant standards body publications."

This document summarizes findings on Object Identifiers (OIDs) for NIST PQC algorithms, focusing on their use in X.509 certificates and Cryptographic Message Syntax (CMS), based on available IETF drafts and NIST information.

## ML-KEM (Kyber)

*   **OID Status:** OIDs for ML-KEM (Kyber) variants are being defined in IETF drafts. The specific OID structure often involves a base OID for Kyber, with arcs to differentiate parameter sets (e.g., Kyber-512, Kyber-768, Kyber-1024).
*   **Relevant IETF Draft:** `draft-turner-lamps-nist-pqc-kem-certificates` (though the search result cited an older version, newer versions like `draft-ietf-lamps-pqc-kem-certificates` are more current). These drafts specify algorithm identifiers for NIST PQC KEMs.
    *   Example (conceptual, actual OIDs are assigned by IANA under IETF): `id-alg-kyber` as a base, with specific arcs for parameter sets. The search mentioned `id-KyberTBD`, indicating a placeholder pending final assignment.
*   **X.509 Encoding:**
    *   The public key is typically encoded as an `OCTET STRING`. For Kyber, this involves the concatenation of the seed `rho` and the public vector `t`, potentially compressed.
    *   The `AlgorithmIdentifier` in `SubjectPublicKeyInfo` for Kyber generally omits the `parameters` field (it's an ASN.1 SEQUENCE containing only the OID).
    *   **Conceptual ASN.1 for `SubjectPublicKeyInfo`:**
        ```asn.1
        SubjectPublicKeyInfo ::= SEQUENCE {
          algorithm   AlgorithmIdentifier { {SupportedPQCAlgorithms} }, -- e.g., id-kyber768
          publicKey   BIT STRING -- Containing the OCTET STRING of the Kyber public key
        }
        ```
*   **CMS Usage:** For key agreement schemes using KEMs like Kyber, the `KeyAgreeRecipientInfo` structure in CMS would reference the Kyber OID. The `CMS-SharedInfo` structure is often used to derive the symmetric key, incorporating KDF parameters.

## ML-DSA (Dilithium)

*   **OID Status:** OIDs for ML-DSA (Dilithium) variants are being defined in IETF drafts.
*   **Relevant IETF Draft:** `draft-ietf-lamps-dilithium-certificates` (e.g., version -02 or later).
    *   The search mentioned `id-dilithiumTBD` as a placeholder OID from the draft, indicating it's pending final IANA assignment. Different OIDs will distinguish security levels (e.g., Dilithium2, Dilithium3, Dilithium5).
*   **X.509 Encoding:**
    *   **Public Key:** The `DilithiumPublicKey` is an `OCTET STRING` containing the seed `rho` and the public vector `t1`.
    *   The `AlgorithmIdentifier` in `SubjectPublicKeyInfo` for Dilithium omits the `parameters` field.
    *   **Conceptual ASN.1 for `SubjectPublicKeyInfo`:**
        ```asn.1
        SubjectPublicKeyInfo ::= SEQUENCE {
          algorithm   AlgorithmIdentifier { {SupportedPQCSignatureAlgorithms} }, -- e.g., id-dilithium2
          publicKey   BIT STRING -- Containing the OCTET STRING of the Dilithium public key
        }
        ```
    *   **Signature Value:** The `signature` field in an X.509 certificate or a CMS `SignerInfo` structure would contain the Dilithium signature value, which itself is a structured sequence.
        ```asn.1
        DilithiumSignatureValue ::= SEQUENCE {
          c      OCTET STRING, -- The hash of the message and tr
          z      OCTET STRING, -- The polynomial vector z
          h      BIT STRING OPTIONAL -- The hint vector h (for some variants)
        }
        ```
        (Note: The exact structure can vary slightly based on the draft version).
*   **CMS Usage:** The `SignatureAlgorithmIdentifier` in `SignerInfo` would carry the Dilithium OID.

## SLH-DSA (SPHINCS+)

*   **OID Status:** OIDs for SLH-DSA (SPHINCS+) are under development within IETF. While NIST SP 800-208 standardizes SPHINCS+, the corresponding IETF work for X.509/CMS OIDs is ongoing.
*   **Relevant IETF Drafts:** Likely to appear in drafts related to hash-based signatures or broader PQC signature suites. Specific draft names for SPHINCS+ OIDs were not highlighted in the immediate search results but would be the authoritative source.
*   **Expected OID Pattern:** Likely `id-sphincsPlusTBD` or similar, with arcs for different parameter sets (e.g., SPHINCS+-SHA256-128f-simple, SPHINCS+-SHAKE256-192s-robust).
*   **X.509/CMS Encoding:** Will follow patterns similar to other signature algorithms, with the public key and signature values encoded as `OCTET STRING`s.

## Falcon

*   **OID Status:** OIDs for Falcon are under development. NIST's standardization of Falcon is slightly behind Kyber/Dilithium/SPHINCS+, with a draft FIPS expected later in 2024 or 2025. IETF OID definition will follow.
*   **Relevant IETF Drafts:** Drafts specifying Falcon OIDs for X.509/CMS are anticipated.
*   **Expected OID Pattern:** Likely `id-falconTBD` or similar, with arcs for parameter sets (e.g., Falcon-512, Falcon-1024).
*   **X.509/CMS Encoding:** Public keys and signatures will be encoded, likely as `OCTET STRING`s.

## General Considerations for PQC OIDs in X.509/CMS

*   **IANA Registration:** Final OIDs are typically registered with IANA under the arcs managed by IETF or other relevant standards bodies.
*   **Parameterization:** Many PQC algorithms have multiple parameter sets offering different security levels. The OID structure must accommodate this, often by assigning a unique OID to each standardized parameter set.
*   **Hybrid Schemes:** For hybrid signatures or KEMs (combining classical and PQC algorithms), specific OIDs or conventions for indicating the constituent algorithms will be necessary. These are also being actively discussed in IETF.
*   **NIST SP 800-208:** This NIST Special Publication, "Recommendation for Stateful Hash-Based Signature Schemes," while focused on stateful HBS, provides context on how NIST approaches PQC algorithm specifications, which informs the IETF process.
*   **NCCoE PQC Migration Project:** The NIST National Cybersecurity Center of Excellence (NCCoE) is working on PQC migration and has projects that involve testing PQC in TLS and digital signatures, which will help drive consensus on OID usage and encoding.

## Summary

The OIDs for the first wave of NIST PQC standards (ML-KEM, ML-DSA, SLH-DSA) and the upcoming Falcon are actively being defined and refined within IETF working groups (primarily LAMPS - Limited Additional Mechanisms for PKIX and SMIME). While many are currently "TBD" placeholders in drafts, these drafts represent the most current direction for official assignment. Implementers should monitor these IETF activities closely.

This information addresses knowledge gap G1.2 by detailing the current status and sources for PQC algorithm OIDs.