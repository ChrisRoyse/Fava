# Primary Findings: Best Practices for Hybrid PQC Schemes (Addressing Gap G2.1)

**Date Compiled:** 2025-06-02
**Research Focus:** G2.1: Best practices for constructing hybrid schemes (e.g., KEM concatenation, signature chaining).
**Source:** AI Search (Perplexity MCP) - Query: "Best practices and IETF recommendations for constructing hybrid post-quantum cryptographic schemes. Specifically, detail methods for hybrid Key Encapsulation Mechanisms (KEMs) such as shared secret concatenation or KDF usage, and for hybrid digital signatures such as signature concatenation or chaining. Include security considerations, potential pitfalls, and references to relevant IETF drafts or academic papers (e.g., RFC 9370, RFC 9258, NIST SP 800-56C)."

This document summarizes best practices and recommendations for constructing hybrid post-quantum cryptographic (PQC) schemes, focusing on Key Encapsulation Mechanisms (KEMs) and digital signatures.

## Rationale for Hybrid Schemes

Hybrid schemes combine a classical cryptographic algorithm with a PQC algorithm. The primary goal is to provide security against both classical and quantum adversaries. If the classical algorithm is broken by a quantum computer, the PQC algorithm still provides protection. Conversely, if a flaw is found in the new PQC algorithm, the well-understood classical algorithm still offers security against classical attacks. This approach is crucial during the transition period to full PQC adoption.

## Hybrid Key Encapsulation Mechanisms (KEMs)

The goal of a hybrid KEM is to establish a shared secret that is secure if *either* the classical KEM *or* the PQC KEM is secure.

**Common Construction Methods:**

1.  **Shared Secret Concatenation and KDF:**
    *   **Process:**
        1.  Perform a key exchange/encapsulation with the classical KEM (e.g., ECDH X25519) to obtain classical shared secret `ss_c`.
        2.  Perform a key exchange/encapsulation with the PQC KEM (e.g., Kyber/ML-KEM) to obtain PQC shared secret `ss_pqc`.
        3.  Concatenate the two shared secrets: `combined_ss = ss_c || ss_pqc`.
        4.  Feed `combined_ss` into a Key Derivation Function (KDF), such as HKDF (HMAC-based Key Derivation Function) as specified in RFC 5869, or a KDF from NIST SP 800-56C.
        5.  The output of the KDF is the final shared secret key used for symmetric encryption.
    *   **Public Key/Ciphertext Handling:** Public keys from both KEMs are typically concatenated and transmitted. Similarly, ciphertexts (encapsulated keys) from both KEMs are concatenated.
    *   **IETF Guidance:**
        *   `draft-ietf-tls-hybrid-design` discusses mechanisms for hybrid key exchange in TLS 1.3, often involving sending concatenated public keys or KEM ciphertexts.
        *   `draft-ietf-lamps-pqc-kem-certificates` (and its predecessors like `draft-connolly-cfrg-xwing-kem` which proposed X-Wing: X25519 and ML-KEM-768) explore structures for hybrid KEMs in X.509 and CMS.
        *   Hybrid Public Key Encryption (HPKE) as defined in RFC 9180 is being extended to support PQC/T hybrid KEMs.

**Security Considerations for Hybrid KEMs:**

*   **Independence of Secrets:** The security relies on the KDF properly combining the secrets. The KDF should ensure that the final key is secure if at least one of the input secrets (`ss_c` or `ss_pqc`) is secure.
*   **KDF Choice:** Use a cryptographically strong KDF. NIST SP 800-56C provides recommendations for KDFs in key-establishment schemes.
*   **Domain Separation:** If the same KDF is used for multiple purposes, ensure proper domain separation (e.g., by including context strings in the KDF input).

## Hybrid Digital Signatures

The goal of a hybrid digital signature is to produce a signature that is valid if *both* the classical signature *and* the PQC signature are valid and correctly verified against their respective public keys.

**Common Construction Methods:**

1.  **Signature Concatenation:**
    *   **Process:**
        1.  Sign the message/data with the classical signature algorithm (e.g., ECDSA P-256) to produce `sig_c`.
        2.  Sign the *same* message/data with the PQC signature algorithm (e.g., Dilithium/ML-DSA) to produce `sig_pqc`.
        3.  Concatenate the two signatures: `hybrid_sig = sig_c || sig_pqc`.
        4.  The verifier must possess both the classical and PQC public keys. Verification involves:
            *   Separating `hybrid_sig` into `sig_c` and `sig_pqc`.
            *   Verifying `sig_c` against the classical public key and the message.
            *   Verifying `sig_pqc` against the PQC public key and the message.
            *   The hybrid signature is valid if and only if both individual verifications succeed.
    *   **Public Key Handling:** Both public keys need to be distributed and associated with the signer. In X.509 certificates, this might involve custom extensions or multiple `SubjectPublicKeyInfo` fields if standard OIDs and structures for such hybrid keys are not yet defined. IETF drafts like `draft-ietf-lamps-dilithium-certificates` focus on individual PQC algorithms first.
2.  **Separate Signatures (Less Common for "Hybrid" Definition):**
    *   Sometimes, systems might opt to send two entirely separate signature blocks, one classical and one PQC. This is less of a "hybrid signature object" and more of a dual-signature policy.

**Security Considerations for Hybrid Signatures:**

*   **Message Integrity:** Both signatures must be computed over the exact same message data.
*   **Verification Logic:** The verifier must correctly implement the logic to check both signatures.
*   **Cross-Algorithm Interference:** Ensure that the signing or verification process of one algorithm does not negatively impact the other. This is generally not an issue with concatenation of independent signatures.

## General Best Practices and Pitfalls

*   **Algorithm Selection:** Choose well-vetted classical algorithms and NIST-selected PQC algorithms.
*   **Implementation Complexity:** Hybrid schemes are inherently more complex than single-algorithm schemes. This increases the risk of implementation errors. Rigorous testing is essential.
*   **Performance Overhead:** Using two cryptographic algorithms will incur performance costs (computation, bandwidth for larger keys/signatures). This needs to be benchmarked and considered for the specific application.
*   **Key Management:** Managing two sets of keys (classical and PQC) adds complexity to key generation, distribution, storage, and revocation.
*   **"Harvest Now, Decrypt Later":** Hybrid KEMs are particularly important for protecting data confidentiality against future quantum attacks on currently encrypted data.
*   **Standardization:** Rely on IETF drafts and NIST recommendations where available. Avoid ad-hoc constructions. The landscape is evolving, so cryptographic agility in how hybrid schemes are implemented is also beneficial.
*   **NCSC (UK) Guidance:** The UK's National Cyber Security Centre has also published whitepapers recommending PQC/T (Post-Quantum/Traditional) hybrid schemes as an interim measure, emphasizing a flexible cryptographic framework.

## Relevant Standards and Documents:

*   **NIST SP 800-56C Rev. 2:** Recommendation for Key-Derivation Methods in Key-Establishment Schemes.
*   **RFC 9370:** Multiple Key Exchanges in TLS 1.3 (provides a framework that can be used for hybrid KEMs).
*   **RFC 9180:** Hybrid Public Key Encryption (HPKE).
*   **IETF Drafts:**
    *   `draft-ietf-tls-hybrid-design` (and its successors) for TLS hybrid key exchange.
    *   Various drafts in the LAMPS working group for PQC in X.509 certificates and CMS (e.g., for Kyber, Dilithium).
    *   `draft-ietf-tls-semistatic-dh` (previously `draft-ietf-tls-kems`) is also relevant for KEM usage in TLS.

This information addresses knowledge gap G2.1 by outlining best practices for constructing hybrid PQC schemes.