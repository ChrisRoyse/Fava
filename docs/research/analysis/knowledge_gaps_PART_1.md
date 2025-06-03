# Identified Knowledge Gaps for PQC Integration in Fava - Part 1

**Date Compiled:** 2025-06-02

This document consolidates the identified knowledge gaps from the initial round of primary research into Post-Quantum Cryptography (PQC) integration for Fava. These gaps will inform targeted research queries in subsequent cycles.

## 1. From NIST PQC Standardization Status (`pf_nist_pqc_status_PART_1.md`)

*   **G1.1: Specific PQC Algorithm Metrics:**
    *   **Gap:** Lack of specific, consolidated quantitative data for standardized PQC algorithms (ML-KEM/Kyber, ML-DSA/Dilithium, SLH-DSA/SPHINCS+, Falcon, HQC) regarding:
        *   Public key sizes (in bytes for each security level).
        *   Private key sizes (in bytes for each security level).
        *   Signature sizes (in bytes for each security level).
        *   Ciphertext/encapsulated key sizes (for KEMs, each security level).
        *   Typical performance benchmarks (e.g., operations/second or latency in milliseconds for key generation, encapsulation, decapsulation, signing, verification) on common hardware platforms (e.g., modern x86 CPU, common ARM cores).
    *   **Rationale:** This data is crucial for making informed decisions about algorithm selection in Fava, assessing storage/bandwidth impact, and estimating performance overhead. While NIST FIPS documents will contain this, a consolidated summary is needed.
*   **G1.2: Official OIDs for PQC Algorithms:**
    *   **Gap:** Lack of a clear list of official Object Identifiers (OIDs) assigned to the NIST standardized PQC algorithms for use in X.509 certificates and other cryptographic protocols.
    *   **Rationale:** OIDs are necessary for interoperability and correct identification of algorithms in various data structures.

## 2. From Cryptographic Agility for PQC (`pf_crypto_agility_pqc_PART_1.md`)

*   **G2.1: Detailed `CryptoService` Design Patterns for PQC:**
    *   **Gap:** While the concept of a `CryptoService` abstraction layer is sound, detailed design patterns or reference architectures specifically tailored for PQC (covering KEMs, signatures, hybrid logic, parameter management for different PQC schemes) are needed.
    *   **Rationale:** Abstracting PQC primitives effectively requires careful interface design to accommodate their unique characteristics (e.g., KEMs returning both ciphertext and shared secret).
*   **G2.2: Concrete Hybrid Scheme Implementation Details:**
    *   **Gap:** Lack of detailed examples or pseudocode for common hybrid PQC schemes (e.g., how to precisely combine classical and PQC keys/signatures, specific authenticated encryption modes for hybrid KEM outputs, data formatting for combined cryptographic outputs).
    *   **Rationale:** Practical implementation of hybrid modes needs clear guidance on cryptographic construction.
*   **G2.3: Managing Configuration Complexity for PQC Agility:**
    *   **Gap:** Best practices or examples for structuring and managing potentially complex configurations for a crypto-agile service that supports multiple PQC algorithms, classical algorithms, and hybrid modes.
    *   **Rationale:** As options grow, configuration must remain manageable and secure.

## 3. From PQC Threat Model & Security Considerations (`pf_pqc_threat_model_security_PART_1.md`)

*   **G3.1: Detailed Side-Channel Attack Vectors & Countermeasures for NIST PQC Finalists:**
    *   **Gap:** While general side-channel concerns for PQC algorithm classes (lattice, code, hash-based) were noted, specific, publicly documented side-channel attacks against mature implementations of the *specific NIST PQC finalists/standards* (Kyber, Dilithium, Falcon, SPHINCS+, HQC) and their widely accepted, practical countermeasures are not yet detailed.
    *   **Rationale:** Understanding concrete vulnerabilities and mitigations is crucial for secure implementation.
*   **G3.2: Quantitative Performance Impact of Larger PQC Data Sizes:**
    *   **Gap:** While "larger" key/signature sizes are known, precise quantitative data on the performance impact (e.g., latency increase in milliseconds for TLS handshakes with specific hybrid KEMs on typical server/client hardware, database storage growth, network transmission overhead) is needed.
    *   **Rationale:** To accurately predict and plan for the system-level impact of PQC.
*   **G3.3: Status of Protocol Updates for PQC (X.509, TLS):**
    *   **Gap:** Specific IETF draft RFCs or concrete working group progress on updating protocols like X.509 (for PQC certificate structures) or TLS (for defining PQC cipher suites beyond general hybrid concepts) were not detailed.
    *   **Rationale:** Fava's PQC integration will depend on these evolving standards.

## 4. From GnuPG (GPG) and Beancount PQC Support (`pf_gpg_beancount_pqc_PART_1.md`)

*   **G4.1: Specific GnuPG PQC Roadmap and Algorithm Choices:**
    *   **Gap:** Lack of a detailed, official roadmap from the GnuPG project specifying which NIST PQC algorithms (KEMs, signatures) they definitively plan to integrate, their target GPG versions, and estimated timelines for stable releases.
    *   **Rationale:** Fava's reliance on GPG for Beancount file encryption makes this critical.
*   **G4.2: GnuPG PQC Command-Line Interface (CLI) / GPGME API:**
    *   **Gap:** If experimental PQC support exists in GPG development branches, the specific CLI options or GPGME (GnuPG Made Easy library) API extensions for using PQC (key generation, encryption, decryption, signing, verification) are not yet clear.
    *   **Rationale:** Needed for potential integration or user guidance.
*   **G4.3: Beancount Community Stance/Plans on PQC:**
    *   **Gap:** Lack of specific discussions, plans, or official statements from the Beancount development community regarding PQC support for encrypted Beancount files.
    *   **Rationale:** Understanding Beancount's direction is important for Fava's strategy.

## 5. From Fava-Side PQC Decryption & KEMs (`pf_fava_sidedecryption_kems_PART_1.md`)

*   **G5.1: Mature Python PQC Key Management Libraries:**
    *   **Gap:** Beyond raw PQC primitive libraries (like `oqs-python`), information on mature Python libraries specifically designed for higher-level PQC key management tasks (e.g., secure storage, user-friendly key derivation, PQC key file format handling) is lacking.
    *   **Rationale:** Simplifies secure PQC implementation in Fava if direct handling is pursued.
*   **G5.2: Standardized Metadata Formats for Hybrid PQC Encrypted Files:**
    *   **Gap:** Are there emerging best practices or draft standards for structuring metadata within files that use hybrid PQC encryption (e.g., identifying the PQC KEM, symmetric cipher, KEM ciphertext, IVs, tags)?
    *   **Rationale:** Important for interoperability and robust Fava-side decryption.
*   **G5.3: Usability of Raw PQC Keys for End-Users:**
    *   **Gap:** More research into the practicalities and user experience aspects of how typical Fava users would manage raw PQC key files or derive PQC keys from passphrases if Fava implemented direct PQC handling.
    *   **Rationale:** User-friendliness is key for adoption.
*   **G5.4: PQC KEM Performance Benchmarks on Diverse User Hardware:**
    *   **Gap:** While some general performance notes for KEMs like Kyber exist, more detailed benchmarks across a wider range of typical user hardware (CPUs, memory) for key generation and KEM operations would be valuable.
    *   **Rationale:** To understand real-world performance implications for Fava users.

## 6. From PQC-Resistant Hashing & Frontend (`pf_hashing_pqc_frontend_PART_1.md`)

*   **G6.1: Maturity and Security Audits of JavaScript SHA-3 Libraries:**
    *   **Gap:** While JS libraries for SHA-3 (e.g., `js-sha3`) exist, their security audit status, long-term maintenance outlook, and suitability for production security functions need verification.
    *   **Rationale:** Critical for ensuring the integrity of frontend hashing if SHA-3 is adopted.
*   **G6.2: Frontend Bundle Size Impact of JS/WASM SHA-3 Libraries:**
    *   **Gap:** Quantitative data on the impact of adding JS/WASM SHA-3 libraries on Fava's frontend bundle size.
    *   **Rationale:** Performance and load time consideration for the web interface.
*   **G6.3: JavaScript Libraries for SHAKE128/256:**
    *   **Gap:** Information on readily available, well-maintained, and easy-to-use JavaScript libraries specifically for SHAKE128/SHAKE256, particularly for generating fixed-length outputs comparable to SHA3-256.
    *   **Rationale:** SHAKE algorithms are often recommended in PQC contexts.

## 7. From PQC Signatures for WASM Integrity & SRI (`pf_wasm_pqc_sri_PART_1.md`)

*   **G7.1: Standardized Formats for PQC Signatures/Keys in Web Contexts for WASM:**
    *   **Gap:** Lack of standardized or widely accepted best practices for how PQC signatures and public keys for WASM modules should be referenced, embedded, or fetched for JavaScript-based verification.
    *   **Rationale:** Important for robust and interoperable WASM integrity solutions.
*   **G7.2: Maturity and Audit Status of `liboqs-js` for Signatures:**
    *   **Gap:** Detailed information on the security audits, maintenance status, and production-readiness of `liboqs-js` specifically for PQC signature verification in browsers.
    *   **Rationale:** Critical for the security of WASM module verification.
*   **G7.3: Real-World Performance of PQC WASM Verification in Fava's Frontend:**
    *   **Gap:** Specific benchmarks of PQC signature verification (e.g., using `liboqs-js`) within Fava's Svelte frontend environment, also considering the bundle size impact.
    *   **Rationale:** To understand practical performance implications for Fava.

## 8. From Python and JavaScript/WASM PQC Libraries (`pf_pqc_python_js_libs_PART_1.md`)

*   **G8.1: Maturity & Security Audits of `PQCrypto` (Python) and `PQCrypto.js`:**
    *   **Gap:** More details on the development status, algorithm coverage, and security reviews for these alternative libraries.
    *   **Rationale:** To assess their viability as alternatives or complements to `liboqs`-based solutions.
*   **G8.2: Practical Installation/Deployment of `liboqs` for Fava:**
    *   **Gap:** Specific guidance or best practices for bundling/distributing the `liboqs` C library if Fava were to depend on `oqs-python`, especially concerning cross-platform compatibility and ease of installation for Fava users.
    *   **Rationale:** User installation experience is important.
*   **G8.3: Detailed PQC Performance Benchmarks for Python/JS Libraries:**
    *   **Gap:** More granular performance benchmarks for `oqs-python` and `liboqs-js` operations (key-gen, sign, verify, encaps, decaps) on typical user hardware, beyond general statements.
    *   **Rationale:** For accurate performance expectation setting.
*   **G8.4: Browser Compatibility Nuances for WASM PQC Libraries:**
    *   **Gap:** Any specific browser versions or WASM features (e.g., SIMD, multi-threading if applicable) required for optimal performance or compatibility of libraries like `liboqs-js`.
    *   **Rationale:** To ensure broad usability.

*(This document will be updated as further analysis is conducted and new gaps are identified or existing ones are filled.)*