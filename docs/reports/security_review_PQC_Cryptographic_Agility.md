# Security Review Report: PQC Cryptographic Agility

**Module Identifier:** PQC_Cryptographic_Agility
**Date of Review:** 2025-06-03
**Report Version:** 1.0
**Reviewer:** AI Security Reviewer (SPARC Aligned)

## 1. Executive Summary

This report details the security review of the "PQC Cryptographic Agility" feature within the Fava application. The review focused on the provided Python source code modules and associated design documents.

Overall, the architecture for cryptographic agility is well-conceived, emphasizing configuration-driven algorithm selection and abstraction of cryptographic operations. However, several areas require attention, primarily concerning the secure loading and validation of cryptographic configurations, robust parsing of encrypted data bundles, and the security of the API endpoint providing configuration to the frontend. The current implementation relies heavily on placeholder modules for actual cryptographic operations and configuration file interactions; the security of the feature will critically depend on the secure implementation of these placeholders.

**Key Findings:**
*   **Total Vulnerabilities Identified:** 6 (excluding informational items)
*   **High Severity:** 2
*   **Medium Severity:** 2
*   **Low Severity:** 2

Significant security risks were identified related to configuration loading and bundle parsing that require immediate attention. Other findings relate to potential weaknesses in salt management and API security.

## 2. Scope of Review

The review covered the following artifacts:

*   **Specification Document:** [`docs/specifications/PQC_Cryptographic_Agility_Spec.md`](docs/specifications/PQC_Cryptographic_Agility_Spec.md) (v1.1)
*   **Architecture Document:** [`docs/architecture/PQC_Cryptographic_Agility_Arch.md`](docs/architecture/PQC_Cryptographic_Agility_Arch.md) (v1.0)
*   **Source Code Files:**
    *   [`src/fava/pqc/exceptions.py`](src/fava/pqc/exceptions.py)
    *   [`src/fava/pqc/interfaces.py`](src/fava/pqc/interfaces.py)
    *   [`src/fava/pqc/global_config.py`](src/fava/pqc/global_config.py)
    *   [`src/fava/pqc/backend_crypto_service.py`](src/fava/pqc/backend_crypto_service.py)
    *   [`src/fava/pqc/frontend_crypto_facade.py`](src/fava/pqc/frontend_crypto_facade.py) (conceptual Python)
    *   [`src/fava/pqc/app_startup.py`](src/fava/pqc/app_startup.py)
    *   [`src/fava/pqc/global_config_helpers.py`](src/fava/pqc/global_config_helpers.py) (placeholders)
    *   [`src/fava/pqc/crypto_lib_helpers.py`](src/fava/pqc/crypto_lib_helpers.py) (placeholders)
    *   [`src/fava/pqc/frontend_lib_helpers.py`](src/fava/pqc/frontend_lib_helpers.py) (placeholders)

## 3. Methodology

The security review was conducted by performing:
*   **Documentation Review:** Analysis of specification and architecture documents to understand intended design and security mechanisms.
*   **Static Application Security Testing (SAST):** Manual source code review of the Python files, focusing on common vulnerabilities (OWASP Top 10, CWEs), secure coding practices, input validation, error handling, configuration management, and cryptographic primitive usage orchestration.
*   **Conceptual Threat Modeling:** Identifying potential threats based on the feature's functionality (cryptographic agility, configuration management).
*   **Conceptual Software Composition Analysis (SCA):** Noting dependencies on underlying cryptographic libraries.

Dynamic Application Security Testing (DAST) was not performed.

## 4. Vulnerability Details

### VULN-PQC-AGL-001: Insecure Configuration Loading Mechanism
*   **Description:** The `GlobalConfig` module in [`src/fava/pqc/global_config.py`](src/fava/pqc/global_config.py) uses a placeholder path (`FAVA_CRYPTO_SETTINGS_PATH`) for the cryptographic settings file. If this path is predictable or can be influenced by an attacker (e.g., if Fava runs with excessive permissions allowing an attacker to write to the default location), a malicious configuration file could be loaded. Furthermore, the file reading, parsing (`parser.parse_python_like_structure`), and schema validation (`validator.validate_schema`) rely on placeholder helpers. Weaknesses in the real implementations of these helpers could lead to arbitrary code execution (if parsing is insecure, e.g., using `eval` on untrusted input) or acceptance of a misconfigured/malicious crypto policy.
*   **File & Line:** [`src/fava/pqc/global_config.py:19`](src/fava/pqc/global_config.py:19), [`src/fava/pqc/global_config.py:42-54`](src/fava/pqc/global_config.py:42)
*   **Severity:** High
*   **Recommendation:**
    1.  The path to the cryptographic settings file should be securely managed, ideally derived from Fava's main, trusted configuration system and protected by appropriate file permissions.
    2.  Implement robust and secure file reading mechanisms.
    3.  Use a safe parsing method for the configuration file (e.g., `ast.literal_eval` for Python-like structures if strictly controlled, or a standard safe format like JSON/YAML with a mature parser). Avoid `eval()` or `exec()`.
    4.  Implement comprehensive schema validation for `FAVA_CRYPTO_SETTINGS` against the structure defined in the specification, ensuring all cryptographic parameters are present, correctly typed, and within acceptable ranges/values.

### VULN-PQC-AGL-002: Non-Robust Encrypted Bundle Header Parsing
*   **Description:** The `parse_common_encrypted_bundle_header` function in [`src/fava/pqc/backend_crypto_service.py`](src/fava/pqc/backend_crypto_service.py) is a placeholder and explicitly stated as "not robust." This function is critical as it attempts to identify the `suite_id_used` to select the correct decryption handler. A vulnerability in this parsing logic (e.g., buffer overflows, type confusion, parsing inconsistencies) when processing untrusted encrypted bundle data could lead to Denial of Service, incorrect handler selection (potentially leaking information through error side-channels), or crashes.
*   **File & Line:** [`src/fava/pqc/backend_crypto_service.py:340-365`](src/fava/pqc/backend_crypto_service.py:340)
*   **Severity:** High
*   **Recommendation:**
    1.  Define a fixed, unambiguous, and secure format for the `HybridEncryptedBundle` header, clearly specifying how `suite_id_used` and other necessary metadata are encoded (e.g., fixed-length fields, TLV structures, or a small JSON prefix).
    2.  Implement a robust and secure parser for this header, with strict validation of lengths, types, and values.
    3.  Ensure the parser handles malformed or malicious headers gracefully, preventing crashes or unintended behavior.

### VULN-PQC-AGL-003: Insecure Frontend Configuration API
*   **Description:** The [`FrontendCryptoFacade`](src/fava/pqc/frontend_crypto_facade.py) fetches its cryptographic configuration from a backend API endpoint (`/api/fava-crypto-configuration`). If this API endpoint is not properly secured (e.g., lacks authentication/authorization, not served over HTTPS), an attacker (e.g., via Man-in-the-Middle) could inject malicious cryptographic settings (e.g., disable WASM verification, specify weak hashing algorithms for frontend operations).
*   **File & Line:** [`src/fava/pqc/frontend_crypto_facade.py:41-63`](src/fava/pqc/frontend_crypto_facade.py:41) (conceptual API call)
*   **Severity:** Medium
*   **Recommendation:**
    1.  Ensure the `/api/fava-crypto-configuration` endpoint requires proper authentication and authorization, allowing only privileged users/contexts to access it if it exposes sensitive configuration details.
    2.  Mandate that all Fava API communication, especially for configuration, occurs over HTTPS.
    3.  Consider if the frontend truly needs the full spectrum of crypto settings or if it can operate with a more limited, less sensitive subset.

### VULN-PQC-AGL-004: Potential Use of Global Static Salt for Passphrase KDF
*   **Description:** The specification document ([`docs/specifications/PQC_Cryptographic_Agility_Spec.md:171`](docs/specifications/PQC_Cryptographic_Agility_Spec.md:171)) defines `FAVA_CRYPTO_SETTINGS.data_at_rest.passphrase_kdf_salt_global`. If this global salt is used directly and statically for deriving keys from user passphrases across all users or multiple encryption instances for the same user without a unique, per-encryption random salt, it negates the primary benefit of salting against pre-computation attacks (e.g., rainbow tables). The `HybridEncryptedBundle` interface includes `kdf_salt_for_passphrase_derived_keys: Optional[bytes]`, which is good if it stores a *per-encryption* random salt. The risk arises if the "global" salt from config is the *only* salt used in the KDF for passphrases.
*   **File & Line:** Specification: [`docs/specifications/PQC_Cryptographic_Agility_Spec.md:171`](docs/specifications/PQC_Cryptographic_Agility_Spec.md:171). Code Impact: [`src/fava/pqc/interfaces.py:20`](src/fava/pqc/interfaces.py:20) (bundle structure), and how `KDF_LIBRARY.derive` is used with passphrases (currently mocked).
*   **Severity:** Medium
*   **Recommendation:**
    1.  Ensure that when deriving keys from passphrases, a cryptographically random salt is generated for each new key derivation/encryption operation. This salt should be stored alongside the encrypted data (as suggested by `kdf_salt_for_passphrase_derived_keys` in the bundle).
    2.  The `passphrase_kdf_salt_global` from the configuration should NOT be used as the sole salt for KDFs applied to user passphrases. If it's intended for a different purpose (e.g., as a pepper, or part of a salt for a global master key not directly tied to user passphrases), its role and usage must be clearly documented and carefully reviewed for security implications.

### VULN-PQC-AGL-005: Hardcoded KDF Salt Length
*   **Description:** In [`HybridPqcCryptoHandler.encrypt`](src/fava/pqc/backend_crypto_service.py:212), the salt for deriving the hybrid symmetric key (`kdf_salt_hybrid_sk`) is generated with a hardcoded length of 16 bytes: `UTILITY_LIBRARY.generate_random_bytes(16)`. While 16 bytes (128 bits) is often a standard salt length, it's preferable for salt lengths to be guided by cryptographic best practices for the specific KDF algorithm in use or be a configurable secure default.
*   **File & Line:** [`src/fava/pqc/backend_crypto_service.py:212`](src/fava/pqc/backend_crypto_service.py:212)
*   **Severity:** Low
*   **Recommendation:**
    1.  Determine the recommended salt length for the `kdf_hybrid_alg` being used (e.g., HKDF-SHA3-512).
    2.  Use this recommended length. If variable, consider making it part of the suite configuration or deriving it from the KDF algorithm's properties.

### VULN-PQC-AGL-006: Robustness of Decryption Loop on Initial Parsing Failure
*   **Description:** In [`decrypt_data_at_rest_with_agility`](src/fava/pqc/backend_crypto_service.py:414-417), if the initial `parse_common_encrypted_bundle_header` fails to produce a `bundle_object`, the subsequent loop through `decryption_handlers` will likely also fail for handlers expecting a pre-parsed bundle. The code logs a warning and continues, but this means decryption attempts might be skipped.
*   **File & Line:** [`src/fava/pqc/backend_crypto_service.py:414-417`](src/fava/pqc/backend_crypto_service.py:414)
*   **Severity:** Low
*   **Recommendation:**
    1.  Clarify the contract for `CryptoHandler.decrypt`: should it expect a pre-parsed `HybridEncryptedBundle` dictionary, or should it be capable of parsing `raw_encrypted_bytes` itself if the common header parsing fails or is insufficient for that specific handler?
    2.  If handlers are expected to parse raw bytes, then `raw_encrypted_bytes` should be passed to them in the loop if `parsed_bundle_attempt["bundle_object"]` is unavailable.
    3.  Improve error reporting to clearly indicate why decryption failed if all attempts are exhausted due to parsing issues versus cryptographic failures.

## 5. General Recommendations

*   **Implement Placeholder Modules:** The security of the PQC agility feature critically depends on the secure implementation of the placeholder helper modules:
    *   [`src/fava/pqc/global_config_helpers.py`](src/fava/pqc/global_config_helpers.py): Secure file reading, robust parsing, and comprehensive schema validation.
    *   [`src/fava/pqc/crypto_lib_helpers.py`](src/fava/pqc/crypto_lib_helpers.py): Correct and secure usage of underlying libraries like `oqs-python` and `cryptography`.
    *   [`src/fava/pqc/frontend_lib_helpers.py`](src/fava/pqc/frontend_lib_helpers.py): Correct usage of `liboqs-js` and other frontend crypto libraries.
*   **Software Composition Analysis (SCA):** Once actual cryptographic libraries (`oqs-python`, `cryptography`, `liboqs-js`, `js-sha3`, etc.) are integrated, perform regular SCA to identify and mitigate known vulnerabilities in these dependencies.
*   **Input Validation for Crypto Parameters:** Ensure all cryptographic parameters (key lengths, algorithm names, curve names, etc.) derived from configuration are strictly validated before use by cryptographic functions to prevent misuse or attacks via malformed configurations.
*   **Thorough Testing:** Implement comprehensive unit and integration tests covering various cryptographic agility scenarios, including algorithm switching, fallback mechanisms, error conditions, and handling of malformed configurations or data.
*   **Security of Key Material:** The generation, storage, and handling of actual key materials (passphrases, derived keys, private keys) are paramount. While detailed key management is somewhat outside the direct scope of these agility modules (which consume key material), ensure the overall system handles them securely.
*   **Constant-Time Operations:** For implementations of actual cryptographic operations (in `crypto_lib_helpers.py`'s real counterparts), ensure they are constant-time where necessary to prevent side-channel attacks, especially for private key operations.

## 6. Self-Reflection

*   **Thoroughness:** The review covered all provided Python code files and relevant sections of the specification and architecture documents. The focus was on the orchestration of cryptographic agility rather than the cryptographic primitives themselves, due to the use of placeholder libraries.
*   **Certainty of Findings:**
    *   High confidence in vulnerabilities related to configuration loading (VULN-PQC-AGL-001) and bundle parsing (VULN-PQC-AGL-002) due to explicit placeholder nature and lack of robust implementation details.
    *   Medium confidence in API security (VULN-PQC-AGL-003) and salt usage (VULN-PQC-AGL-004, VULN-PQC-AGL-005) as these depend on common security practices and interpretation of the spec/code.
    *   Low confidence for VULN-PQC-AGL-006 as it's more a robustness/edge case.
*   **Limitations:**
    *   The review could not assess the security of the actual cryptographic operations as they are implemented in placeholder modules.
    *   No dynamic analysis (DAST) was performed.
    *   The frontend code is a Python representation; a review of actual JavaScript/TypeScript would be needed for the true frontend.
    *   The exact mechanism for how `FavaOptions` integrates `FAVA_CRYPTO_SETTINGS` and protects the main configuration file was not detailed in the provided code, impacting full assessment of VULN-PQC-AGL-001's attack surface.

## 7. Quantitative Summary

*   **Total Vulnerabilities Identified:** 6
*   **High Severity:** 2
    *   VULN-PQC-AGL-001: Insecure Configuration Loading Mechanism
    *   VULN-PQC-AGL-002: Non-Robust Encrypted Bundle Header Parsing
*   **Medium Severity:** 2
    *   VULN-PQC-AGL-003: Insecure Frontend Configuration API
    *   VULN-PQC-AGL-004: Potential Use of Global Static Salt for Passphrase KDF
*   **Low Severity:** 2
    *   VULN-PQC-AGL-005: Hardcoded KDF Salt Length
    *   VULN-PQC-AGL-006: Robustness of Decryption Loop on Initial Parsing Failure
*   **Informational (Dependencies):** 1 (Placeholder Crypto Libraries)

This concludes the security review for the PQC Cryptographic Agility feature.