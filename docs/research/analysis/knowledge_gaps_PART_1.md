# Identified Knowledge Gaps for PQC Integration in Fava - Part 1 (Updated 2025-06-02)

**Date Compiled:** 2025-06-02 (Originally 2025-06-02, updated based on follow-up research)

This document consolidates identified knowledge gaps from research into Post-Quantum Cryptography (PQC) integration for Fava. Updates reflect findings from targeted research addressing previously identified gaps.

## 1. From NIST PQC Standardization Status (`pf_nist_pqc_status_PART_1.md`)

*   **G1.1: Specific PQC Algorithm Metrics:**
    *   **Gap (Original):** Lack of specific, consolidated quantitative data for standardized PQC algorithms (ML-KEM/Kyber, ML-DSA/Dilithium, SLH-DSA/SPHINCS+, Falcon, HQC) regarding key sizes, signature sizes, ciphertext sizes, and typical performance benchmarks.
    *   **Rationale (Original):** Crucial for algorithm selection, assessing impact, and estimating performance.
    *   **Update (2025-06-02):**
        *   **G1.1 (FIPS Details): Resolved.** Latest details on FIPS 203, 204, 205 (ML-KEM, ML-DSA, SLH-DSA) including finalization dates and links to official documents have been compiled in [`docs/research/data_collection/primary_findings/pf_nist_fips_updates_g1_1_PART_1.md`](../data_collection/primary_findings/pf_nist_fips_updates_g1_1_PART_1.md). No substantive changes or errata since August 2024 were found for these core documents. Supporting documents like SP 800-227 for ML-KEM are noted.
        *   **G1.3 (Performance Benchmarks): Resolved.** Concrete performance benchmarks (latency, throughput, memory) for Kyber, Dilithium, Falcon, and SPHINCS+ in C library contexts (relevant for Python wrappers) have been researched and documented in [`docs/research/data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md). Python overhead considerations are included.
        *   **G1.4 (Security Levels): Resolved.** NIST PQC security level comparisons (Levels 1-5) for Kyber, Dilithium, Falcon, and SPHINCS+, including their classical equivalents and specific parameter sets, are detailed in [`docs/research/data_collection/primary_findings/pf_pqc_security_levels_g1_4_PART_1.md`](../data_collection/primary_findings/pf_pqc_security_levels_g1_4_PART_1.md).

*   **G1.2: Official OIDs for PQC Algorithms:**
    *   **Gap (Original):** Lack of a clear list of official Object Identifiers (OIDs) assigned to NIST standardized PQC algorithms for X.509 certificates.
    *   **Rationale (Original):** Necessary for interoperability.
    *   **Update (2025-06-02): Resolved.** Research on finalized/adopted OIDs for ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+), and Falcon for X.509/CMS, along with IETF draft references, has been documented in [`docs/research/data_collection/primary_findings/pf_pqc_oids_x509_g1_2_PART_1.md`](../data_collection/primary_findings/pf_pqc_oids_x509_g1_2_PART_1.md). While many are still "TBD" in drafts, these represent the current direction.

## 2. From Cryptographic Agility for PQC (`pf_crypto_agility_pqc_PART_1.md`)

*   **G2.1: Detailed `CryptoService` Design Patterns for PQC:**
    *   **Gap (Original):** Need for detailed design patterns for a PQC `CryptoService`.
    *   **Rationale (Original):** Effective abstraction of PQC primitives.
    *   **Update (2025-06-02): Refined.** While this specific gap wasn't a primary focus of the follow-up, the research into hybrid scheme best practices ([`docs/research/data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md`](../data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md)) provides crucial input for designing such a service, particularly methods for KEM and signature construction.

*   **G2.2: Concrete Hybrid Scheme Implementation Details:**
    *   **Gap (Original):** Lack of detailed examples for common hybrid PQC schemes.
    *   **Rationale (Original):** Practical implementation guidance needed.
    *   **Update (2025-06-02): Resolved.**
        *   Best practices for constructing hybrid KEMs (secret concatenation, KDF usage) and hybrid signatures (concatenation) with IETF references are documented in [`docs/research/data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md`](../data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md).
        *   Specific recommendations for Fava's context (data-at-rest, data-in-transit, data integrity) including algorithm pairings and construction methods are detailed in [`docs/research/data_collection/primary_findings/pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md`](../data_collection/primary_findings/pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md).

*   **G2.3: Managing Configuration Complexity for PQC Agility:**
    *   **Gap (Original):** Best practices for managing complex configurations for a crypto-agile service.
    *   **Rationale (Original):** Ensuring manageable and secure configuration.
    *   **Update (2025-06-02): No specific update in this cycle.** This remains an area for design consideration during implementation.

## 3. From PQC Threat Model & Security Considerations (`pf_pqc_threat_model_security_PART_1.md`)

*   **G3.1: Detailed Side-Channel Attack Vectors & Countermeasures for NIST PQC Finalists:**
    *   **Update (2025-06-02): No specific update in this cycle.** Remains an ongoing concern for library selection and implementation.
*   **G3.2: Quantitative Performance Impact of Larger PQC Data Sizes:**
    *   **Update (2025-06-02): Partially Addressed.** Performance benchmarks in [`docs/research/data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md) provide data on key/signature/ciphertext sizes and operational latencies, which inform this gap. System-level impact still requires Fava-specific testing.
*   **G3.3: Status of Protocol Updates for PQC (X.509, TLS):**
    *   **Update (2025-06-02): Partially Addressed.** OID status for X.509 is covered in [`docs/research/data_collection/primary_findings/pf_pqc_oids_x509_g1_2_PART_1.md`](../data_collection/primary_findings/pf_pqc_oids_x509_g1_2_PART_1.md). PQC-TLS reverse proxy status (which depends on TLS protocol updates) is covered in [`docs/research/data_collection/primary_findings/pf_pqc_tls_proxies_clients_g4_2_PART_1.md`](../data_collection/primary_findings/pf_pqc_tls_proxies_clients_g4_2_PART_1.md).

## 4. From GnuPG (GPG) and Beancount PQC Support (`pf_gpg_beancount_pqc_PART_1.md`)

*   **G4.1: Specific GnuPG PQC Roadmap and Algorithm Choices:**
    *   **Gap (Original):** Lack of a detailed, official GnuPG PQC roadmap.
    *   **Rationale (Original):** Critical for Fava's GPG-encrypted file strategy.
    *   **Update (2025-06-02): Resolved.** Current status indicates no official native PQC support in stable GPG. A realistic roadmap is likely long-term. Alternatives and contingency plans are documented in [`docs/research/data_collection/primary_findings/pf_gpg_pqc_status_g4_1_PART_1.md`](../data_collection/primary_findings/pf_gpg_pqc_status_g4_1_PART_1.md) and [`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](../data_collection/primary_findings/pf_tooling_contingency_PART_1.md).

*   **G4.2: GnuPG PQC Command-Line Interface (CLI) / GPGME API:**
    *   **Gap (Original):** Unclear CLI/API for experimental GPG PQC.
    *   **Rationale (Original):** Needed for integration/guidance.
    *   **Update (2025-06-02): Addressed as part of G4.1.** Since official support is distant, specific CLI/APIs are not yet defined.

*   **G4.3: Beancount Community Stance/Plans on PQC:**
    *   **Update (2025-06-02): No specific update in this cycle.** Fava's strategy will likely need to be independent of Beancount's direct PQC adoption in the near term.

## 5. From Fava-Side PQC Decryption & KEMs (`pf_fava_sidedecryption_kems_PART_1.md`)

*   **G5.1: Mature Python PQC Key Management Libraries:**
    *   **Update (2025-06-02): Partially Addressed.** `oqs-python` ([`docs/research/data_collection/primary_findings/pf_oqs_python_analysis_g3_1_PART_1.md`](../data_collection/primary_findings/pf_oqs_python_analysis_g3_1_PART_1.md)) provides primitives. Higher-level key management remains a design consideration for Fava if implementing direct PQC handling.
*   **G5.2: Standardized Metadata Formats for Hybrid PQC Encrypted Files:**
    *   **Update (2025-06-02): Partially Addressed.** Hybrid KEM construction best practices ([`docs/research/data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md`](../data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md)) touch upon transmitting concatenated ciphertexts/keys, implying metadata needs. Formal standards are still emerging via IETF.
*   **G5.3: Usability of Raw PQC Keys for End-Users:**
    *   **Update (2025-06-02): No specific update in this cycle.** Remains a UX challenge if Fava implements direct PQC key handling.
*   **G5.4: PQC KEM Performance Benchmarks on Diverse User Hardware:**
    *   **Update (2025-06-02): Addressed.** Covered by G1.3 findings in [`docs/research/data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md).

## 6. From PQC-Resistant Hashing & Frontend (`pf_hashing_pqc_frontend_PART_1.md`)

*   **G6.1: Maturity and Security Audits of JavaScript SHA-3 Libraries:**
    *   **Update (2025-06-02): Refined.** While not a deep dive into specific JS SHA-3 library audits, the JS/WASM PQC library research ([`docs/research/data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md)) acknowledges the need for frontend crypto libraries and general security considerations for them.
*   **G6.2: Frontend Bundle Size Impact of JS/WASM SHA-3 Libraries:**
    *   **Update (2025-06-02): Addressed conceptually.** Covered in the `liboqs-js` analysis ([`docs/research/data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md)) regarding bundle size concerns for WASM crypto.
*   **G6.3: JavaScript Libraries for SHAKE128/256:**
    *   **Update (2025-06-02): No specific update on dedicated SHAKE JS libraries in this cycle.** `liboqs-js` would be the primary source if SHAKE is used as part of a supported PQC scheme.

## 7. From PQC Signatures for WASM Integrity & SRI (`pf_wasm_pqc_sri_PART_1.md`)

*   **G7.1: Standardized Formats for PQC Signatures/Keys in Web Contexts for WASM:**
    *   **Update (2025-06-02): Partially Addressed.** OID research ([`docs/research/data_collection/primary_findings/pf_pqc_oids_x509_g1_2_PART_1.md`](../data_collection/primary_findings/pf_pqc_oids_x509_g1_2_PART_1.md)) is relevant for key identification. Hybrid signature construction ([`docs/research/data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md`](../data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md)) discusses signature concatenation.
*   **G7.2: Maturity and Audit Status of `liboqs-js` for Signatures:**
    *   **Update (2025-06-02): Resolved.** Covered in the `liboqs-js` deep dive: [`docs/research/data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md).
*   **G7.3: Real-World Performance of PQC WASM Verification in Fava's Frontend:**
    *   **Update (2025-06-02): Addressed conceptually.** Performance of `liboqs-js` and general WASM crypto considerations are discussed in [`docs/research/data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md). Fava-specific benchmarks would be needed during implementation.

## 8. From Python and JavaScript/WASM PQC Libraries (`pf_pqc_python_js_libs_PART_1.md`)

*   **G8.1: Maturity & Security Audits of `PQCrypto` (Python) and `PQCrypto.js`:**
    *   **Update (2025-06-02): Addressed.** Alternatives to `oqs-python` were researched in [`docs/research/data_collection/primary_findings/pf_oqs_python_alternatives_g3_2_PART_1.md`](../data_collection/primary_findings/pf_oqs_python_alternatives_g3_2_PART_1.md), finding limited mature alternatives. `PQCrypto` was not prominent.
*   **G8.2: Practical Installation/Deployment of `liboqs` for Fava:**
    *   **Update (2025-06-02): Resolved.** `oqs-python` analysis ([`docs/research/data_collection/primary_findings/pf_oqs_python_analysis_g3_1_PART_1.md`](../data_collection/primary_findings/pf_oqs_python_analysis_g3_1_PART_1.md)) confirms simplified installation with automatic `liboqs` handling.
*   **G8.3: Detailed PQC Performance Benchmarks for Python/JS Libraries:**
    *   **Update (2025-06-02): Resolved.** C library benchmarks (relevant for wrappers) are in [`docs/research/data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md). `liboqs-js` performance considerations are in [`docs/research/data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md).
*   **G8.4: Browser Compatibility Nuances for WASM PQC Libraries:**
    *   **Update (2025-06-02): Addressed.** Discussed in `liboqs-js` analysis ([`docs/research/data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md]).

## 9. External Tooling & Dependencies (New Section based on Targeted Research)

*   **G4.1 (GPG PQC Support): Status Updated.** See Section 4, G4.1 update. Contingencies in [`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](../data_collection/primary_findings/pf_tooling_contingency_PART_1.md).
*   **G4.2 (PQC-TLS Reverse Proxies): Status Updated.** Maturity and client tool availability researched in [`docs/research/data_collection/primary_findings/pf_pqc_tls_proxies_clients_g4_2_PART_1.md`](../data_collection/primary_findings/pf_pqc_tls_proxies_clients_g4_2_PART_1.md). Contingencies in [`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](../data_collection/primary_findings/pf_tooling_contingency_PART_1.md).
*   **G4.3 (PQC CLI Signing Tool): Status Updated.** Availability and maturity for WASM signing researched in [`docs/research/data_collection/primary_findings/pf_pqc_cli_signing_tools_g4_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_cli_signing_tools_g4_3_PART_1.md). Contingencies in [`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](../data_collection/primary_findings/pf_tooling_contingency_PART_1.md).

## 10. Contingency Planning (New Section based on Targeted Research)

*   **Overall Status:** Viable contingency plans for key external dependencies (GPG, PQC-TLS Proxies, PQC Signing Tools) have been researched and documented in [`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](../data_collection/primary_findings/pf_tooling_contingency_PART_1.md). These focus on application-level PQC, alternative tooling, and hybrid strategies.

*(This document has been updated to reflect findings from the targeted research cycle of 2025-06-02. Many initial gaps have been resolved or significantly refined.)*