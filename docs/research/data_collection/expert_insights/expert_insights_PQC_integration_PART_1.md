# Expert Insights & Consensus on PQC Integration for Fava - Part 1

**Date Compiled:** 2025-06-02

This document synthesizes expert insights and areas of general consensus derived from the initial research into Post-Quantum Cryptography (PQC) integration relevant to the Fava project. These are based on information from standards bodies (NIST), security guidance, and observed trends in PQC adoption.

## 1. Urgency and Phased Approach to PQC Transition

*   **Insight:** There is a strong consensus, underscored by NIST and various security bodies, on the eventual necessity of transitioning to PQC due to the threat posed by future fault-tolerant quantum computers to current public-key cryptography [Sources: pf_nist_pqc_status_PART_1.md, pf_crypto_agility_pqc_PART_1.md].
*   **Recommendation:** A phased approach is broadly recommended:
    1.  **Cryptographic Agility First:** Implement abstraction layers (`CryptoService`) to decouple cryptographic primitives from application logic. This is a foundational step before introducing PQC algorithms directly [Sources: pf_crypto_agility_pqc_PART_1.md, Plan.MD].
    2.  **Hybrid Modes:** Adopt hybrid schemes (classical + PQC) as an interim measure. This provides backward compatibility and defense-in-depth, as an attacker would need to break both cryptographic components [Sources: pf_crypto_agility_pqc_PART_1.md, pf_tls_proxies_python_pqc_PART_1.md, pf_pqc_certs_browsers_PART_1.md].
    3.  **Pure PQC:** Transition to pure PQC modes once standards are fully mature, libraries are stable, and the ecosystem (e.g., CAs, browsers, tools like GPG) has broader support.
*   **Timeline:** NIST's deprecation timeline (classical algorithms deprecated by 2030, disallowed by 2035) provides a window for this transition [Source: pf_nist_pqc_status_PART_1.md].

## 2. Algorithm Selection: Focus on NIST Standards

*   **Insight:** The NIST PQC Standardization process is the primary driver for algorithm selection. Algorithms chosen and standardized by NIST (ML-KEM/Kyber, ML-DSA/Dilithium, SLH-DSA/SPHINCS+, and upcoming ones like Falcon, HQC) are considered to have undergone rigorous security and performance evaluation [Source: pf_nist_pqc_status_PART_1.md].
*   **Recommendation:** Prioritize the use of NIST-standardized PQC algorithms for new implementations. For Fava, this means focusing research and potential PoCs on libraries that implement these standards (e.g., `liboqs`).

## 3. Importance of Cryptographic Agility

*   **Insight:** The PQC landscape is still evolving, and even standardized algorithms could face new cryptanalytic insights or require parameter adjustments. Therefore, designing systems to be cryptographically agile is paramount [Source: pf_crypto_agility_pqc_PART_1.md, Plan.MD].
*   **Recommendation:** Fava's plan to introduce a `CryptoService` is well-aligned with this expert consensus. This service should be designed to easily switch between algorithms and manage configurations.

## 4. Data at Rest (Encrypted Beancount Files via GPG)

*   **Insight:** The PQC readiness of GnuPG is a critical dependency for Fava if it continues to rely on GPG for Beancount file encryption. Current stable GPG versions lack native PQC support [Source: pf_gpg_beancount_pqc_PART_1.md].
*   **Recommendation:** Fava should closely monitor GPG's PQC development. In parallel, exploring the Fava-side decryption abstraction (as per Plan.MD) using Python PQC libraries for users who need PQC encryption sooner than GPG might support it, or for formats not tied to GPG, is a prudent strategy.

## 5. Data in Transit (TLS)

*   **Insight:** PQC in TLS is progressing, primarily through hybrid KEMs (e.g., X25519Kyber768). Browser support is experimental and not yet default. Reverse proxies are the recommended way for applications like Fava to adopt PQC TLS, dependent on OpenSSL (or equivalent) PQC support [Sources: pf_tls_proxies_python_pqc_PART_1.md, pf_pqc_certs_browsers_PART_1.md].
*   **Recommendation:** Fava should recommend users employ PQC-capable reverse proxies for TLS termination. Direct PQC TLS implementation within Fava's Python web server (Cheroot/Flask) is likely complex and dependent on rapid Python `ssl` module evolution.

## 6. Hashing for Data Integrity

*   **Insight:** While SHA-256's quantum resistance is reduced by Grover's algorithm, it's not considered immediately broken for many common integrity uses. However, SHA-3 (and its XOF variants like SHAKE) offers better long-term quantum resistance due to its different internal structure [Source: pf_hashing_pqc_frontend_PART_1.md].
*   **Recommendation:** For new systems or significant upgrades requiring long-term security, transitioning from SHA-256 to SHA3-256 (or SHAKE128/256) is advisable. Fava should plan for this, especially if a `CryptoService` for hashing is implemented. Native browser support for SHA-3 in `window.crypto.subtle` is currently lacking, requiring JavaScript libraries for frontend SHA-3 hashing.

## 7. WASM Module Integrity

*   **Insight:** PQC digital signatures (e.g., Dilithium) offer stronger authenticity and integrity for WASM modules compared to SRI hashes alone. `liboqs-js` provides a viable path for client-side verification [Source: pf_wasm_pqc_sri_PART_1.md].
*   **Recommendation:** For enhanced security of Fava's WASM modules (like `tree-sitter-beancount.wasm`), using PQC signatures is a good long-term goal. Hybrid signature schemes or careful public key distribution mechanisms will be needed. SRI can be used as a complementary measure.

## 8. PQC Libraries

*   **Insight:** `liboqs` (and its Python wrapper `oqs-python`, and JS version `liboqs-js`) is a central open-source project providing implementations of many NIST PQC candidates and standards. It's a key enabler for experimentation and integration [Sources: pf_pqc_python_js_libs_PART_1.md, pf_wasm_pqc_sri_PART_1.md].
*   **Recommendation:** Leverage `liboqs`-based libraries for initial PQC implementation efforts in Fava, while monitoring the PQC support roadmap for standard Python libraries (`cryptography` package) and browser native APIs.

## 9. Performance and Key/Signature Sizes

*   **Insight:** PQC algorithms generally come with larger key sizes, larger signature/ciphertext sizes, and different performance characteristics compared to classical algorithms. These impacts need to be carefully assessed for each use case (file encryption, TLS, signatures) [Sources: pf_pqc_threat_model_security_PART_1.md, pf_fava_sidedecryption_kems_PART_1.md].
*   **Recommendation:** Fava should include performance benchmarking and consideration of data size impacts as part of its PQC integration PoCs and design.

*(This document reflects insights based on the initial research phase and will be updated.)*