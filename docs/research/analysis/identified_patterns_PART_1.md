# Identified Patterns in PQC Integration Research - Part 1

**Date Compiled:** 2025-06-02

This document outlines key patterns and recurring themes observed during the initial data collection phase for Post-Quantum Cryptography (PQC) integration relevant to Fava.

## 1. Pattern: Gradual Ecosystem Maturation and Standardization Dependence

*   **Observation:** Across multiple areas (GPG, TLS libraries, CAs, browser support, Python standard libraries), full PQC support is generally not yet mature or widely deployed in stable, production-ready forms. Development is often experimental, in progress, or awaiting further finalization and adoption of NIST standards.
*   **Examples:**
    *   GnuPG lacks native PQC in stable releases; PQC support is experimental or via forks ([`pf_gpg_beancount_pqc_PART_1.md`](../data_collection/primary_findings/pf_gpg_beancount_pqc_PART_1.md)).
    *   TLS PQC in reverse proxies and Python depends on OpenSSL 3.2+ and specific compilations/configurations, which are not yet universally standard ([`pf_tls_proxies_python_pqc_PART_1.md`](../data_collection/primary_findings/pf_tls_proxies_python_pqc_PART_1.md)).
    *   CAs are not expected to issue PQC certificates until at least 2026 due to HSM and audit requirements ([`pf_pqc_certs_browsers_PART_1.md`](../data_collection/primary_findings/pf_pqc_certs_browsers_PART_1.md)).
    *   Standard Python crypto libraries plan PQC support post-NIST finalization ([`pf_pqc_python_js_libs_PART_1.md`](../data_collection/primary_findings/pf_pqc_python_js_libs_PART_1.md)).
*   **Implication for Fava:** Fava's PQC integration timeline will be significantly influenced by this external ecosystem maturity. A patient, phased approach is necessary, relying on abstraction and monitoring developments.

## 2. Pattern: Hybrid Approaches as a Dominant Transitional Strategy

*   **Observation:** For many PQC applications (TLS KEMs, digital signatures in certificates, potentially file encryption), a hybrid approach combining classical cryptography with PQC is the most commonly recommended and implemented transitional strategy.
*   **Examples:**
    *   Hybrid KEMs like X25519Kyber768 for TLS ([`pf_tls_proxies_python_pqc_PART_1.md`](../data_collection/primary_findings/pf_tls_proxies_python_pqc_PART_1.md)).
    *   Suggestions for hybrid certificates (classical + PQC signatures) ([`pf_pqc_certs_browsers_PART_1.md`](../data_collection/primary_findings/pf_pqc_certs_browsers_PART_1.md)).
    *   General best practice for cryptographic agility ([`pf_crypto_agility_pqc_PART_1.md`](../data_collection/primary_findings/pf_crypto_agility_pqc_PART_1.md)).
*   **Implication for Fava:** Fava's `CryptoService` should be designed with hybrid modes as a primary consideration, allowing for graceful fallback or combined security.

## 3. Pattern: Increased Resource Requirements (Size & Performance)

*   **Observation:** PQC algorithms generally involve larger key sizes, signature sizes, and ciphertexts, and can have different (often higher) computational performance overhead compared to their classical counterparts.
*   **Examples:**
    *   Kyber public keys and Dilithium signatures are significantly larger than RSA/ECC equivalents ([`pf_pqc_threat_model_security_PART_1.md`](../data_collection/primary_findings/pf_pqc_threat_model_security_PART_1.md), [`pf_fava_sidedecryption_kems_PART_1.md`](../data_collection/primary_findings/pf_fava_sidedecryption_kems_PART_1.md)).
    *   TLS handshakes with PQC KEMs have increased latency and data size ([`pf_tls_proxies_python_pqc_PART_1.md`](../data_collection/primary_findings/pf_tls_proxies_python_pqc_PART_1.md)).
    *   PQC key generation and some operations can be slower without hardware acceleration ([`pf_fava_sidedecryption_kems_PART_1.md`](../data_collection/primary_findings/pf_fava_sidedecryption_kems_PART_1.md)).
*   **Implication for Fava:** Performance testing and consideration of storage/bandwidth implications will be crucial for each PQC integration point. UI responsiveness and file handling times could be affected.

## 4. Pattern: Central Role of `liboqs` and its Derivatives

*   **Observation:** The Open Quantum Safe (OQS) project, with its `liboqs` C library and wrappers like `oqs-python` and `liboqs-js`, appears to be a central and widely referenced resource for accessing implementations of NIST PQC candidates and standards.
*   **Examples:**
    *   `oqs-python` is the leading comprehensive PQC library for Python ([`pf_pqc_python_js_libs_PART_1.md`](../data_collection/primary_findings/pf_pqc_python_js_libs_PART_1.md)).
    *   `liboqs-js` is a key enabler for frontend/WASM PQC operations ([`pf_wasm_pqc_sri_PART_1.md`](../data_collection/primary_findings/pf_wasm_pqc_sri_PART_1.md), [`pf_pqc_python_js_libs_PART_1.md`](../data_collection/primary_findings/pf_pqc_python_js_libs_PART_1.md)).
*   **Implication for Fava:** Leveraging `liboqs`-based libraries is a strong candidate strategy for Fava's initial PQC implementations, especially for backend services and potentially for frontend WASM verification if direct PQC handling is chosen.

## 5. Pattern: Cryptographic Agility as a Foundational Requirement

*   **Observation:** The need for cryptographic agility (the ability to easily switch algorithms) is a consistent theme in all PQC transition discussions.
*   **Examples:**
    *   Explicitly recommended as a best practice ([`pf_crypto_agility_pqc_PART_1.md`](../data_collection/primary_findings/pf_crypto_agility_pqc_PART_1.md)).
    *   Underpins the design of Fava's proposed `CryptoService` ([`docs/Plan.MD`](../../Plan.MD)).
*   **Implication for Fava:** Validates the strategic direction in [`docs/Plan.MD`](../../Plan.MD). The design and implementation of the `CryptoService` will be a critical success factor.

## 6. Pattern: Hashing Transition - SHA-3 as the Preferred Successor

*   **Observation:** For hashing, while SHA-256 is not immediately broken for all use cases, SHA-3 (and its variants like SHAKE) is consistently recommended as the more quantum-resistant and future-proof successor due to its different internal design.
*   **Examples:**
    *   SHA-3 offers better quantum resistance profiles ([`pf_hashing_pqc_frontend_PART_1.md`](../data_collection/primary_findings/pf_hashing_pqc_frontend_PART_1.md)).
    *   NIST recommends SHA3-256 for new systems needing quantum resistance ([`pf_hashing_pqc_frontend_PART_1.md`](../data_collection/primary_findings/pf_hashing_pqc_frontend_PART_1.md)).
*   **Implication for Fava:** If Fava updates its hashing (currently SHA-256), SHA3-256 is the prime candidate. This has implications for frontend hashing, as native browser support for SHA-3 via `window.crypto.subtle` is lacking.

## 7. Pattern: Implementation Complexity and New Security Considerations

*   **Observation:** PQC algorithms, being newer and based on different mathematical problems, introduce new implementation complexities and potential security vulnerabilities (e.g., side-channel attacks) that differ from classical algorithms.
*   **Examples:**
    *   Side-channel concerns for lattice-based KEMs/signatures and hash-based signatures ([`pf_pqc_threat_model_security_PART_1.md`](../data_collection/primary_findings/pf_pqc_threat_model_security_PART_1.md)).
    *   Challenges in PQC key management and secure user key provision if handled directly by applications ([`pf_fava_sidedecryption_kems_PART_1.md`](../data_collection/primary_findings/pf_fava_sidedecryption_kems_PART_1.md)).
*   **Implication for Fava:** Direct implementation of PQC primitives requires deep expertise. Relying on well-vetted libraries (like `liboqs`) is crucial. Even then, careful integration and testing are needed.

*(This document will be updated as further analysis is conducted.)*