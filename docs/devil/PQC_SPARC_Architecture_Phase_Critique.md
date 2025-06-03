# Devil's Advocate Critique: PQC SPARC Architecture Phase

**Version:** 1.0
**Date:** 2025-06-02
**Project:** Fava PQC Integration
**Artifacts Reviewed:**
*   Architecture Documents (v1.0):
    *   [`docs/architecture/PQC_Data_At_Rest_Arch.md`](../../docs/architecture/PQC_Data_At_Rest_Arch.md)
    *   [`docs/architecture/PQC_Data_In_Transit_Arch.md`](../../docs/architecture/PQC_Data_In_Transit_Arch.md)
    *   [`docs/architecture/PQC_Hashing_Arch.md`](../../docs/architecture/PQC_Hashing_Arch.md)
    *   [`docs/architecture/PQC_WASM_Module_Integrity_Arch.md`](../../docs/architecture/PQC_WASM_Module_Integrity_Arch.md)
    *   [`docs/architecture/PQC_Cryptographic_Agility_Arch.md`](../../docs/architecture/PQC_Cryptographic_Agility_Arch.md)
*   Specification Documents (v1.1): (Referenced for context)
    *   [`docs/specifications/PQC_Data_At_Rest_Spec.md`](../../docs/specifications/PQC_Data_At_Rest_Spec.md)
    *   [`docs/specifications/PQC_Data_In_Transit_Spec.md`](../../docs/specifications/PQC_Data_In_Transit_Spec.md)
    *   [`docs/specifications/PQC_Hashing_Spec.md`](../../docs/specifications/PQC_Hashing_Spec.md)
    *   [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md)
    *   [`docs/specifications/PQC_Cryptographic_Agility_Spec.md`](../../docs/specifications/PQC_Cryptographic_Agility_Spec.md)
*   Pseudocode Documents (v1.0/v1.1): (Referenced for context)
    *   [`docs/pseudocode/PQC_Data_At_Rest_Pseudo.md`](../../docs/pseudocode/PQC_Data_At_Rest_Pseudo.md)
    *   [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md)
    *   [`docs/pseudocode/PQC_Hashing_Pseudo.md`](../../docs/pseudocode/PQC_Hashing_Pseudo.md)
    *   [`docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md`](../../docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md)
    *   [`docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md`](../../docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md)
*   Primary Project Planning Document: [`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md) (v1.1)
*   High-Level Acceptance Tests: (Referenced for context)
    *   [`tests/acceptance/PQC_Data_At_Rest_Acceptance_Tests.md`](../../../tests/acceptance/PQC_Data_At_Rest_Acceptance_Tests.md)
    *   [`tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md`](../../../tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md)
    *   [`tests/acceptance/PQC_Hashing_Acceptance_Tests.md`](../../../tests/acceptance/PQC_Hashing_Acceptance_Tests.md)
    *   [`tests/acceptance/PQC_WASM_Module_Integrity_Acceptance_Tests.md`](../../../tests/acceptance/PQC_WASM_Module_Integrity_Acceptance_Tests.md)
    *   [`tests/acceptance/PQC_Cryptographic_Agility_Acceptance_Tests.md`](../../../tests/acceptance/PQC_Cryptographic_Agility_Acceptance_Tests.md)
*   External Research: Perplexity MCP query results on PQC KEM key derivation from passphrases.

## 1. Introduction

This document provides a critical evaluation of the PQC Architecture phase artifacts for the Fava project. The review focuses on robustness, scalability, maintainability, security, and alignment with input specifications and pseudocode, leveraging the SPARC framework context.
## 2. General Observations and Cross-Cutting Concerns

*   **Clarity and Detail:** The architecture documents are generally well-detailed, with C4 diagrams providing good visual context. The alignment sections within each document are particularly helpful for tracing decisions back to specifications and pseudocode.
*   **Dependency Management:** The project heavily relies on external libraries like `oqs-python` and `liboqs-js`. While acknowledged as a risk in the Master Plan, the architecture phase should ensure that interfaces to these libraries are well-abstracted to mitigate impacts from upstream changes or bugs. The `CryptoService` and frontend facades aim to do this.
*   **Error Handling and Logging:** While mentioned, the architecture documents could benefit from more explicit high-level strategies for error propagation and user feedback, particularly for failures in cryptographic operations. Consistent logging levels and formats across modules will be crucial.
*   **Performance Measurement:** The architecture documents acknowledge performance NFRs. It's vital that the "Basic Performance Indicator Tests" planned for the Refinement and Completion phases are designed early to provide feedback on architectural choices.
## 3. Critique of Specific Architectural Areas

### 3.1. PQC Data at Rest Architecture ([`docs/architecture/PQC_Data_At_Rest_Arch.md`](../../docs/architecture/PQC_Data_At_Rest_Arch.md))

*   **Strengths:**
    *   The `CryptoService` layer (ADR-001) is a strong design choice for modularity and cryptographic agility.
    *   Fava-driven hybrid PQC encryption (ADR-002) improves UX and reduces reliance on immature external GPG PQC tooling.
    *   The `EncryptedFileBundle` (ADR-004) is well-defined and includes necessary metadata for versioning and decryption.
*   **Weaknesses/Potential Risks & Recommendations:**
    *   **Key Management (ADR-003 - `PASSPHRASE_DERIVED`):**
        *   **Risk:** Deriving PQC KEM keys (e.g., Kyber-768 requiring ~256-bit security) directly from user passphrases, even with HKDF-SHA3-512, poses a significant security risk if passphrases have low entropy. User education on passphrase strength is insufficient mitigation for cryptographic keys.
        *   **Recommendation 1 (High Priority):** For the `PASSPHRASE_DERIVED` mode, mandate the use of a strong Password-Based Key Derivation Function (PBKDF) like **Argon2id** to stretch the user's passphrase *before* its output is used as the Input Keying Material (IKM) for HKDF. HKDF is excellent for deriving multiple keys from an already strong key, but not ideal for directly strengthening low-entropy passphrases against offline attacks. The output of Argon2id would then feed into HKDF to derive the specific classical and PQC KEM keys.
        *   **Recommendation 2:** If Argon2id is not adopted, the documentation and UI *must* strongly guide users to use high-entropy passphrases (e.g., generated by password managers, diceware phrases of sufficient length) for this mode, and clearly state the risks of using weak, memorable passphrases. The term "passphrase" itself can be misleading; "master encryption key phrase" might be better.
        *   **Clarification Needed:** The architecture mentions "salt for passphrase derivation must be unique per key derivation instance... stored securely (e.g., within the `EncryptedFileBundle` if per-file)". This is good. Ensure this salt is indeed per-encryption and sufficiently random.
    *   **Key Export (FR2.9):** The architecture mentions `export_fava_managed_pqc_private_keys()`. The security implications of this feature are significant.
        *   **Recommendation:** The export process must be heavily guarded, require explicit user confirmation with strong warnings, and the export format must be clearly documented and secure (e.g., encrypted itself). Consider if this feature is truly necessary for the initial release or if it can be deferred.
*   **Alignment:** Generally well-aligned with its corresponding specification ([`docs/specifications/PQC_Data_At_Rest_Spec.md`](../../docs/specifications/PQC_Data_At_Rest_Spec.md)) and pseudocode ([`docs/pseudocode/PQC_Data_At_Rest_Pseudo.md`](../../docs/pseudocode/PQC_Data_At_Rest_Pseudo.md)), especially after spec v1.1 incorporated Fava-driven encryption.

### 3.2. PQC Data in Transit Architecture ([`docs/architecture/PQC_Data_In_Transit_Arch.md`](../../docs/architecture/PQC_Data_In_Transit_Arch.md))

*   **Strengths:**
    *   Reliance on an external PQC-capable reverse proxy (ADR-001) is a pragmatic and secure approach, offloading complex TLS PQC logic from Fava.
    *   Focus on Fava's role in documentation and potential awareness (via headers/config) is appropriate.
*   **Weaknesses/Potential Risks & Recommendations:**
    *   **Proxy-to-Fava Link Security:** The architecture assumes the link between the reverse proxy and Fava is a "trusted, secure network environment."
        *   **Risk:** If the proxy and Fava are on different hosts or in a less trusted segment, this unencrypted link is a vulnerability.
        *   **Recommendation:** The architecture and subsequent deployment documentation *must* strongly emphasize that if the proxy-Fava link is not localhost or a physically/virtually secured private network, it *must* be independently secured (e.g., using classical TLS for this internal hop, mTLS, or an IPSec tunnel). This needs to be a prominent warning.
*   **Alignment:** Well-aligned with its specification ([`docs/specifications/PQC_Data_In_Transit_Spec.md`](../../docs/specifications/PQC_Data_In_Transit_Spec.md)) and pseudocode ([`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../../docs/pseudocode/PQC_Data_In_Transit_Pseudo.md)).

### 3.3. PQC Hashing Architecture ([`docs/architecture/PQC_Hashing_Arch.md`](../../docs/architecture/PQC_Hashing_Arch.md))

*   **Strengths:**
    *   Centralized backend `HashingService` (ADR-1) and frontend hashing abstraction (ADR-2) are good for maintainability and agility.
    *   Defaulting to SHA3-256 with SHA-256 fallback (ADR-3) is a sound choice.
    *   Configuration propagation (ADR-4) ensures consistency.
*   **Weaknesses/Potential Risks & Recommendations:**
    *   **Frontend SHA3 Library (ADR-5):** The choice of a JavaScript SHA3 library (e.g., `js-sha3`) or a WASM-based solution has performance and bundle size implications (NFR3.7).
        *   **Recommendation:** The architecture should recommend or mandate early benchmarking of candidate frontend SHA3 libraries during the Refinement phase to ensure NFRs for performance and bundle size are met. Consider if a WASM implementation offers better performance for a manageable size increase.
*   **Alignment:** Excellent alignment with its specification ([`docs/specifications/PQC_Hashing_Spec.md`](../../docs/specifications/PQC_Hashing_Spec.md)) and pseudocode ([`docs/pseudocode/PQC_Hashing_Pseudo.md`](../../docs/pseudocode/PQC_Hashing_Pseudo.md)).

### 3.4. PQC WASM Module Integrity Architecture ([`docs/architecture/PQC_WASM_Module_Integrity_Arch.md`](../../docs/architecture/PQC_WASM_Module_Integrity_Arch.md))

*   **Strengths:**
    *   Modular service-based approach for frontend logic (ADR 001) is clean.
    *   Reliance on `liboqs-js` for Dilithium3 verification (ADR 002) is practical.
*   **Weaknesses/Potential Risks & Recommendations:**
    *   **Public Key Distribution & Rotation (ADR 003):** Configuration via a build-time generated file means public key rotation requires a frontend rebuild and redeployment.
        *   **Risk:** This limits agility if rapid key rotation is needed (e.g., due to a compromise).
        *   **Recommendation:** While likely acceptable for Fava's release cycle, this limitation should be noted. Future consideration could be given to fetching the public key from a trusted, configurable API endpoint (with robust caching and an embedded fallback key) to allow for more dynamic updates without a full frontend deployment.
    *   **Build Process Security:** The security of the WASM signing process and the private key used for signing is paramount.
        *   **Recommendation:** The architecture should briefly mention the need for a secure build environment where the private signing key is protected. This is outside runtime architecture but critical context.
*   **Alignment:** Well-aligned with its specification ([`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](../../docs/specifications/PQC_WASM_Module_Integrity_Spec.md)) and pseudocode ([`docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md`](../../docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md)).

### 3.5. PQC Cryptographic Agility Architecture ([`docs/architecture/PQC_Cryptographic_Agility_Arch.md`](../../docs/architecture/PQC_Cryptographic_Agility_Arch.md))

*   **Strengths:**
    *   The centralized `FAVA_CRYPTO_SETTINGS` (ADR-AGL-001) and the `BackendCryptoService` with a registry/factory pattern (ADR-AGL-002) provide a robust foundation for agility.
    *   The `FrontendCryptoFacade` (ADR-AGL-003) ensures consistency.
    *   Standardized metadata (`suite_id_used` in bundles, ADR-AGL-004) and configurable decryption attempt order (ADR-AGL-005) are excellent for handling legacy data.
*   **Weaknesses/Potential Risks & Recommendations:**
    *   **Configuration Complexity:** The `FAVA_CRYPTO_SETTINGS` structure, while comprehensive, is complex.
        *   **Risk:** Administrators might misconfigure these settings, leading to security issues or non-functional crypto.
        *   **Recommendation:** Strongly emphasize the need for exceptionally clear documentation, secure defaults, and potentially a future UI/CLI tool to assist administrators in managing these settings. Validation of the settings structure at startup (as implied by `GlobalConfigModule`) is critical.
    *   **Key Management Agility:** The architecture focuses on algorithm agility. If future cryptographic suites require fundamentally different key types, key derivation methods, or `key_material` structures than currently envisaged for the `HybridPqcCryptoHandler` (e.g., stateful KEMs, different input requirements for KDFs).
        *   **Risk:** This could necessitate non-trivial changes to the `KeyMaterialForEncryption/Decryption` structures and the key acquisition logic within `DataAtRestService` or `FavaLedger`, potentially limiting the "config-only" agility for such transitions.
        *   **Recommendation:** Consider if the `CryptoHandler` interface could be extended to include methods that describe the *nature* or *schema* of the key material it expects. This might allow the key management logic to be more dynamically adaptive or at least provide better error reporting for mismatched key material. This is a more advanced point but worth considering for long-term maintainability.
    *   **Scope of `suite_id_used`:** The `HybridEncryptedBundle` includes `suite_id_used`. Ensure this is robustly parsed and that the `BackendCryptoService.GetCryptoHandler(suite_id)` can reliably map this ID to the correct handler and its specific configuration from `FAVA_CRYPTO_SETTINGS.data_at_rest.suites[suite_id]`.
        *   **Recommendation:** Ensure rigorous testing for the parsing of `suite_id_used` from various bundle versions/states and the subsequent handler lookup and initialization.
*   **Alignment:** Very well-aligned with its specification ([`docs/specifications/PQC_Cryptographic_Agility_Spec.md`](../../docs/specifications/PQC_Cryptographic_Agility_Spec.md)) and pseudocode ([`docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md`](../../docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md)).
## 4. Conclusion

The proposed PQC architecture for Fava is comprehensive and thoughtfully designed, addressing the core areas of data at rest, data in transit, hashing, WASM integrity, and cryptographic agility. The emphasis on modularity (e.g., `CryptoService`) and configurability is commendable and aligns well with the SPARC principles.

The primary areas for deeper consideration and potential refinement are:
1.  **Passphrase-Derived Key Security (Data at Rest):** Strengthening this against low-entropy passphrases by incorporating a PBKDF like Argon2id before HKDF is highly recommended.
2.  **Proxy-to-Fava Link Security (Data in Transit):** Explicitly addressing the security requirements for this link when not on a trusted local host.
3.  **Configuration Complexity (Cryptographic Agility):** While powerful, the crypto settings are complex. Future tooling or very clear guidance will be essential for administrators.

Addressing these points will further enhance the robustness and security of the PQC integration. The architecture provides a solid foundation for the subsequent Refinement (implementation) phase.