# PQC Integration Specification: Cryptographic Agility

**Version:** 1.1
**Date:** 2025-06-02

**Revision History:**
*   **1.1 (2025-06-02):** Revised based on new research findings and Devil's Advocate critique. Key changes include:
    *   Incorporated specific algorithm examples (Kyber, Dilithium, SHA3-256, X25519) based on other revised specs.
    *   Added considerations for managing data encrypted with multiple past PQC schemes (Critique 3.5).
    *   Refined data models for crypto settings to be more comprehensive.
    *   Updated TDD anchors to reflect more detailed service interfaces and configuration.
    *   Emphasized reliance on `oqs-python` and `liboqs-js`.
*   **1.0 (2025-06-02):** Initial version.

## 1. Introduction

This document details the specifications for implementing cryptographic agility within the Fava application as part of its Post-Quantum Cryptography (PQC) upgrade. Cryptographic agility is the ability of a system to adapt to evolving cryptographic standards and algorithm choices with minimal code changes, primarily through configuration. This is crucial given the dynamic nature of the PQC landscape and the need to support transitions.

This specification consolidates agility aspects from other PQC focus area documents, research findings ([`docs/research/`](../../docs/research/), particularly `pf_crypto_agility_pqc_PART_1.md`, `pf_hybrid_pqc_schemes_g2_1_PART_1.md`), and the overall PQC integration plan ([`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md)).

The goal is to ensure Fava can gracefully transition between cryptographic algorithms (classical, PQC, hybrid) as new standards emerge, vulnerabilities are found, or different performance/security trade-offs are desired.

## 2. Functional Requirements

*   **FR2.1 (Central CryptoService - Backend):** A central `CryptoService` (e.g., in `fava.crypto_service.py`) MUST be implemented to abstract all core backend cryptographic operations. This includes:
    *   Symmetric encryption/decryption (e.g., AES-256-GCM).
    *   Classical KEM operations (e.g., X25519).
    *   PQC KEM encapsulation/decapsulation (e.g., ML-KEM/Kyber-768).
    *   Hybrid encryption/decryption schemes (combining classical KEM, PQC KEM, and symmetric ciphers).
    *   Digital signature generation/verification (classical e.g., ECDSA, and PQC e.g., ML-DSA/Dilithium3 - primarily for build-time tools managed via this service's principles).
    *   Hashing (e.g., SHA3-256, SHA-256).
*   **FR2.2 (Crypto Abstraction - Frontend):** A similar cryptographic abstraction layer (e.g., in `frontend/src/lib/pqcCrypto.ts` or `frontend/src/lib/crypto.ts`) MUST be implemented for frontend cryptographic needs:
    *   Hashing (SHA3-256, SHA-256).
    *   PQC signature verification for WASM (Dilithium3).
*   **FR2.3 (Configurable Algorithms):** Fava's configuration (`FavaOptions`) MUST allow administrators to specify desired cryptographic algorithms and their parameters for different contexts:
    *   **Data at Rest (Beancount file encryption/decryption):** Active hybrid suite ID, definitions for suites including classical KEM, PQC KEM, symmetric cipher, KDF.
    *   **Hashing:** Default hash algorithm (SHA3-256, SHA-256).
    *   **WASM Module Integrity:** PQC Signature algorithm (implicitly Dilithium3 via public key type, or explicitly if multiple PQC signature types are supported by `liboqs-js`). Public key for verification.
*   **FR2.4 (Service Registry/Factory):** The backend `CryptoService` and frontend abstraction MUST use a registry or factory pattern to instantiate and provide the appropriate algorithm implementation based on the current configuration.
*   **FR2.5 (Algorithm Switching):** Changing the configured cryptographic algorithm (e.g., from SHA-256 to SHA3-256, or from one PQC KEM suite to another for *new* data encryption) MUST NOT require code changes in the core application logic that *uses* the crypto service. It should only require a configuration update and potentially a restart of Fava.
*   **FR2.6 (Support for Hybrid Modes):** The `CryptoService` MUST explicitly support hybrid cryptographic schemes (classical KEM + PQC KEM + symmetric cipher) for data at rest, following IETF best practices (e.g., secret concatenation and KDF usage).
*   **FR2.7 (Graceful Fallback/Error Handling):** If a configured algorithm is unavailable (e.g., library missing, misconfiguration), the `CryptoService` MUST handle this gracefully:
    *   Log a clear error.
    *   For critical operations (e.g., decryption), fail securely if no safe alternative can be determined.
    *   For less critical operations or where defaults are defined (e.g., hashing), potentially fall back to a known-good default (e.g., SHA3-256 if a misconfigured hash algo is chosen) and log a warning.
*   **FR2.8 (Clear Separation of Concerns):** Cryptographic logic MUST be strictly isolated within the `CryptoService` / frontend abstraction.
*   **FR2.9 (Support for Decrypting Older Formats - Data at Rest):**
    *   While one "active" suite is used for *new* encryptions, the `CryptoService` for data at rest decryption SHOULD be designed to attempt decryption with multiple configured/known past suites if the primary active suite fails.
    *   This requires storing enough metadata with encrypted files (or Fava having a way to infer) which suite might have been used (e.g., a format version or suite identifier in the encrypted file header).
    *   The list of "legacy" suites to try for decryption should be configurable.

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The cryptographic agility framework itself MUST NOT introduce vulnerabilities. Configuration changes should be auditable. Default configurations MUST be secure (e.g., recommending Kyber-768, Dilithium3, SHA3-256).
*   **NFR3.2 (Maintainability):** Adding new cryptographic algorithms or suites within the `CryptoService` or frontend abstraction MUST be straightforward and well-documented.
*   **NFR3.3 (Testability):** The `CryptoService` and its algorithm implementations MUST be highly testable. Agility (switching algorithms) must be testable.
*   **NFR3.4 (Performance):** The abstraction layer SHOULD NOT introduce significant performance overhead beyond the inherent cost of the chosen cryptographic algorithms.
*   **NFR3.5 (Usability - Admin):** Configuration of cryptographic algorithms via `FavaOptions` MUST be clear, well-documented, and provide sensible defaults.
*   **NFR3.6 (Interoperability):** When switching algorithms for new operations, Fava must remain interoperable with data or systems using the newly configured algorithm. For decryption, it must handle files encrypted with its known supported schemes.

## 4. User Stories

*   **US4.1:** As a Fava administrator, I want to easily switch the default hashing algorithm from SHA-256 to SHA3-256 by changing a single configuration setting.
*   **US4.2:** As a Fava developer, when a new NIST-standardized PQC KEM (e.g., HQC) becomes widely supported in `oqs-python`, I want to add support for it as a new suite in Fava's `CryptoService` for Beancount file encryption/decryption without refactoring large parts of the application.
*   **US4.3:** As a Fava administrator, if a PQC algorithm initially chosen (e.g., Kyber-768) is later superseded by a stronger variant (e.g., Kyber-1024) for new encryptions, I want to reconfigure Fava to use the new variant for encrypting new files, while still being able to decrypt files encrypted with Kyber-768.
*   **US4.4:** As a Fava user, I want Fava to transparently handle decryption of my Beancount files, whether they were encrypted with an older supported PQC scheme or a newer one, based on Fava's current configuration and my key material.

## 5. Use Cases

### 5.1. Use Case: Administrator Changes Default Hashing Algorithm

*   **Actor:** Fava Administrator
*   **Preconditions:**
    *   Fava currently uses SHA-256 (configured).
    *   `CryptoService` supports SHA-256 and SHA3-256.
*   **Main Flow:**
    1.  Admin stops Fava.
    2.  Admin modifies Fava config: `pqc_hashing_algorithm = "SHA3-256"`.
    3.  Admin restarts Fava.
    4.  `CryptoService`'s hashing component now uses SHA3-256.
    5.  Subsequent hashing operations use SHA3-256.
*   **Postconditions:** Fava uses SHA3-256 for hashing. No code changes needed.

### 5.2. Use Case: Developer Adds Support for a New PQC KEM Suite

*   **Actor:** Fava Developer
*   **Preconditions:**
    *   New PQC KEM `ML-KEM-NewAlgo` is supported by `oqs-python`.
    *   `CryptoService` has defined interfaces for KEMs and symmetric ciphers.
*   **Main Flow:**
    1.  Developer adds `ML-KEM-NewAlgo` implementation to `CryptoService` (wrapping `oqs-python`).
    2.  Developer defines a new suite in `FavaOptions` structure (e.g., `FAVA_HYBRID_X25519_NEWKEM_AES256GCM`).
    3.  Developer registers the new KEM with the `CryptoService` factory.
    4.  Developer updates documentation. Adds unit tests for the new KEM service.
*   **Postconditions:** Fava can be configured to use the new suite for encrypting/decrypting files. Core logic is unchanged.

### 5.3. Use Case: Fava Decrypts File Encrypted with a Previous PQC Suite

*   **Actor:** Fava System
*   **Preconditions:**
    *   User's file `old_data.bc.pqc_fava` was encrypted with `Suite_Old (e.g., Kyber-768 based)`.
    *   Fava's current `active_suite_id` for new encryptions is `Suite_New (e.g., Kyber-1024 based)`.
    *   `Suite_Old` is listed in Fava's configuration as a known legacy suite for decryption.
    *   File metadata in `old_data.bc.pqc_fava` indicates it was encrypted with `Suite_Old` (or can be inferred).
*   **Main Flow:**
    1.  Fava attempts to decrypt `old_data.bc.pqc_fava` using `Suite_New` (the active suite). Decryption fails.
    2.  Fava's `CryptoService` (or ledger loader) checks file metadata or tries known legacy suites.
    3.  It identifies or attempts decryption with `Suite_Old`.
    4.  Decryption with `Suite_Old` and correct key material succeeds.
*   **Postconditions:** File is successfully decrypted. User is unaware of the internal fallback unless logged.

## 6. Edge Cases & Error Handling

*   **EC6.1:** Config specifies an algorithm/suite unknown to `CryptoService` factory: Fail initialization for that context, log critical error.
*   **EC6.2:** Required PQC library (`oqs-python`, `liboqs-js`) missing/fails for a configured algorithm: Similar to EC6.1.
*   **EC6.3:** Incompatible parameters for chosen algorithm: Implementation should detect and error.
*   **EC6.4 (Data at Rest - Decryption):** If a file is encrypted with an unknown/unsupported PQC suite (not in active or legacy config), decryption will fail. Clear error message needed.
*   **EC6.5 (Data at Rest - Key Migration):** If a user wishes to re-encrypt data from an old PQC suite to the new active PQC suite, Fava might offer a utility or guidance, but automatic re-encryption of all user files is out of scope for initial agility. The focus is on decrypting old, encrypting new.

## 7. Constraints

*   **C7.1:** Agility bounded by `oqs-python` (backend) and `liboqs-js` (frontend) capabilities.
*   **C7.2:** Managing keys for multiple PQC algorithms/suites can be complex for users. Fava's key management for its direct encryption should aim for simplicity (e.g., passphrase-derived keys per suite, with clear association).
*   **C7.3:** Performance varies between PQC algorithms.
*   **C7.4:** On-the-fly algorithm switching without restart is not required; config changes + restart is acceptable.
*   **C7.5:** For data at rest, the file format for Fava-PQC-encrypted files must include identifiable metadata for the suite used.

## 8. Data Models

### 8.1. `CryptoService` Configuration in `FavaOptions` (Revised)

```python
# In Fava's configuration (e.g., fava_options.py or dedicated crypto_config.py)

FAVA_CRYPTO_SETTINGS = {
    "data_at_rest": {
        "pqc_decryption_enabled": True,
        "pqc_encryption_enabled": True, # New flag for Fava-driven encryption
        "active_encryption_suite_id": "HYBRID_X25519_MLKEM768_AES256GCM",
        "decryption_attempt_order": [ # Order to try decrypting files
            "HYBRID_X25519_MLKEM768_AES256GCM", # Try active first
            "HYBRID_X25519_MLKEM1024_AES256GCM", # Example legacy
            "CLASSICAL_GPG" # Fallback to GPG
        ],
        "suites": {
            "HYBRID_X25519_MLKEM768_AES256GCM": {
                "description": "Hybrid: X25519 + ML-KEM-768 (Kyber) with AES-256-GCM",
                "type": "FAVA_HYBRID_PQC",
                "classical_kem_algorithm": "X25519",
                "pqc_kem_algorithm": "ML-KEM-768", # FIPS 203 name
                "symmetric_algorithm": "AES256GCM",
                "kdf_algorithm": "HKDF-SHA3-512", # For deriving symmetric key
                "key_management_mode": "PASSPHRASE_DERIVED", # PASSPHRASE_DERIVED, EXTERNAL_KEY_FILE
                # "key_source_detail_template": "fava_pqc_{suite_id}_{user_id}.key" # If external
            },
            "HYBRID_X25519_MLKEM1024_AES256GCM": { # Example of another suite
                "description": "Hybrid: X25519 + ML-KEM-1024 (Kyber) with AES-256-GCM",
                "type": "FAVA_HYBRID_PQC",
                "classical_kem_algorithm": "X25519",
                "pqc_kem_algorithm": "ML-KEM-1024",
                "symmetric_algorithm": "AES256GCM",
                "kdf_algorithm": "HKDF-SHA3-512",
                "key_management_mode": "PASSPHRASE_DERIVED",
            },
            "CLASSICAL_GPG": {
                "description": "Classical GPG Decryption",
                "type": "CLASSICAL_GPG",
                # GPG specific params if needed, e.g., gpg_executable_path
            }
        },
        "passphrase_kdf_salt_global": "some_fava_global_salt_for_passphrase_keys" # Example
    },
    "hashing": {
        "default_algorithm": "SHA3-256" # Options: "SHA3-256", "SHA256"
    },
    "wasm_integrity": {
        "verification_enabled": True,
        "public_key_dilithium3_base64": "BASE64_ENCODED_DILITHIUM3_PUBLIC_KEY",
        "signature_algorithm": "Dilithium3" # Matches key type
    },
    "pqc_library_config": { # For oqs-python, liboqs-js
        "oqs_python_lib_path": None, # Optional override for liboqs C library path
    }
}
```

## 9. UI/UX Flow Outlines

*   **UI9.1 (Admin Configuration Panel):**
    *   Section for "Cryptographic Settings".
    *   Data at Rest:
        *   Select `active_encryption_suite_id`.
        *   Manage `decryption_attempt_order`.
        *   Configure parameters for `key_management_mode` (e.g., change master passphrase salt if applicable and understood).
    *   Hashing: Select `default_algorithm`.
    *   WASM Integrity: Toggle `verification_enabled`. Display current public key info.
    *   Clear explanations, security implications, links to docs.

## 10. Initial TDD Anchors or Pseudocode Stubs

### 10.1. Backend `CryptoServiceLocator` and `CryptoHandler` Interfaces

```python
# In fava.crypto_service.py

class CryptoHandler(ABC):
    @abstractmethod
    def get_suite_id(self) -> str: pass
    @abstractmethod
    def encrypt(self, plaintext: bytes, key_material: Any, config: Dict) -> bytes: pass # Returns bundle
    @abstractmethod
    def decrypt(self, bundle: bytes, key_material: Any, config: Dict) -> bytes: pass # Returns plaintext

# _HANDLER_REGISTRY = {} # Maps suite_id to CryptoHandler instance or factory

# def register_crypto_handler(suite_id: str, factory_or_instance): pass
# def get_crypto_handler(suite_id: str) -> CryptoHandler: pass
# def get_configured_decryption_handlers(fava_options: FavaOptions) -> List[CryptoHandler]:
#    # Returns handlers in order of fava_options.data_at_rest.decryption_attempt_order
#    pass
# def get_active_encryption_handler(fava_options: FavaOptions) -> CryptoHandler: pass

# TEST: test_crypto_service_locator_returns_active_encryption_handler()
#   SETUP: Configure Fava with HYBRID_X25519_MLKEM768_AES256GCM as active. Register a mock handler for it.
#   ACTION: Call get_active_encryption_handler(fava_options).
#   ASSERT: Returns the mock handler for HYBRID_X25519_MLKEM768_AES256GCM.

# TEST: test_crypto_service_locator_returns_decryption_handlers_in_order()
#   SETUP: Configure Fava with decryption_attempt_order = ["SUITE_A", "SUITE_B"]. Register mock handlers.
#   ACTION: Call get_configured_decryption_handlers(fava_options).
#   ASSERT: Returns list containing [MockHandler_A, MockHandler_B].

# TEST: test_hybrid_pqc_handler_encrypt_decrypt_with_passphrase_derived_key()
#   SETUP:
#     Mock oqs.KeyEncapsulation for ML-KEM-768.
#     Mock cryptography lib for X25519 and AES256GCM.
#     Instantiate your HybridPqcCryptoHandler for "HYBRID_X25519_MLKEM768_AES256GCM".
#     Plaintext data, a passphrase.
#     Suite config dict from FAVA_CRYPTO_SETTINGS.
#   ACTION:
#     Derive key_material from passphrase (conceptual: KDFs to get KEM keys and symmetric key).
#     encrypted_bundle = handler.encrypt(plaintext_bytes, key_material, suite_config)
#     decrypted_bytes = handler.decrypt(encrypted_bundle, key_material, suite_config)
#   ASSERT: decrypted_bytes == plaintext_bytes.
```

### 10.2. Frontend Abstraction (Conceptual - Agility Focus)

```typescript
// In frontend/src/lib/pqcCryptoFacade.ts

// // Hashing - Fetches algorithm from Fava config API
// export async function calculateConfiguredHash(data: string): Promise<string> {
//   const favaConfig = await getFavaRuntimeOptions(); // API call
//   const configuredAlgo = favaConfig.crypto.hashing.default_algorithm || "SHA3-256";
//   return internalCalculateHash(data, configuredAlgo); // internalCalculateHash has switch
// }

// // WASM Sig Verification - Fetches pubkey/algo from Fava config API
// export async function verifyWasmSignatureWithConfig(wasmBuffer: ArrayBuffer, sigBuffer: ArrayBuffer): Promise<boolean> {
//   const favaConfig = await getFavaRuntimeOptions();
//   const wasmSigConfig = favaConfig.crypto.wasm_integrity;
//   if (!wasmSigConfig.verification_enabled) return true; // Or specific handling

//   return internalVerifySignature(
//     wasmBuffer,
//     sigBuffer,
//     wasmSigConfig.public_key_dilithium3_base64,
//     wasmSigConfig.signature_algorithm // e.g., "Dilithium3"
//   );
// }

// TEST (Frontend): test_calculateConfiguredHash_uses_sha3_by_default_from_mock_api()
//   SETUP: Mock Fava API to return { crypto: { hashing: { default_algorithm: "SHA3-256" } } }. Spy internalCalculateHash.
//   ACTION: Call `calculateConfiguredHash("test")`.
//   ASSERT: `internalCalculateHash` called with "SHA3-256".

// TEST (Frontend): test_verifyWasmSignatureWithConfig_uses_dilithium3_from_mock_api()
//   SETUP: Mock Fava API for wasm_integrity config. Spy internalVerifySignature.
//   ACTION: Call `verifyWasmSignatureWithConfig(wasmBuf, sigBuf)`.
//   ASSERT: `internalVerifySignature` called with Dilithium3 pubkey and algo name.
```

## 11. Dependencies

*   **External Libraries:** `oqs-python`, `cryptography` (Python), `liboqs-js`, `js-sha3` (JS/WASM).
*   **Internal Fava Modules:**
    *   `fava.core.FavaOptions`: Central source for `FAVA_CRYPTO_SETTINGS`.
    *   `fava.crypto_service` (new): Backend abstraction and handler implementations.
    *   `frontend/src/lib/pqcCrypto.ts` (or similar): Frontend abstraction.
    *   All Fava components performing crypto ops refactored to use these abstractions.
    *   Fava API endpoints to expose necessary crypto config to frontend.

## 12. Integration Points

*   **IP12.1 (Configuration Loading):** `FavaOptions` loads `FAVA_CRYPTO_SETTINGS`. `CryptoServiceLocator` initialized.
*   **IP12.2 (Backend Service Usage):** `FavaLedger` calls `get_active_encryption_handler()` for saves, and iterates `get_configured_decryption_handlers()` for loads. Hashing uses `get_hashing_service()`.
*   **IP12.3 (Frontend Service Usage):** Frontend abstractions call Fava API to get current algo configs, then call internal implementations.
*   **IP12.4 (API for Frontend Configuration):** API exposes relevant parts of `FAVA_CRYPTO_SETTINGS.hashing` and `FAVA_CRYPTO_SETTINGS.wasm_integrity` to the frontend.