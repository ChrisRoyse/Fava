# PQC Integration Specification: Cryptographic Agility

**Version:** 1.0
**Date:** 2025-06-02

## 1. Introduction

This document details the specifications for implementing cryptographic agility within the Fava application as part of its Post-Quantum Cryptography (PQC) upgrade. Cryptographic agility is the ability of a system to adapt to evolving cryptographic standards and algorithm choices with minimal code changes, primarily through configuration. This is crucial given the dynamic nature of the PQC landscape.

This specification consolidates agility aspects mentioned in other PQC focus area documents (Data at Rest, Hashing, WASM Integrity, Data in Transit) and refers to the overall PQC integration plan ([`docs/Plan.MD`](../../docs/Plan.MD)), research findings ([`docs/research/`](../../docs/research/)), and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The goal is to ensure Fava can gracefully transition between cryptographic algorithms (classical, PQC, hybrid) as new standards emerge, vulnerabilities are found, or different performance/security trade-offs are desired.

## 2. Functional Requirements

*   **FR2.1 (Central CryptoService - Backend):** A central `CryptoService` (e.g., in `fava.crypto_service.py`) MUST be implemented to abstract all core backend cryptographic operations. This includes:
    *   Symmetric encryption/decryption.
    *   PQC KEM encapsulation/decapsulation.
    *   Hybrid encryption/decryption schemes (combining KEMs and symmetric ciphers).
    *   Digital signature generation/verification (classical and PQC).
    *   Hashing.
*   **FR2.2 (Crypto Abstraction - Frontend):** A similar cryptographic abstraction layer (e.g., in `frontend/src/lib/crypto.ts` or `frontend/src/lib/pqcCrypto.ts`) MUST be implemented for frontend cryptographic needs (hashing, PQC signature verification for WASM).
*   **FR2.3 (Configurable Algorithms):** Fava's configuration (`FavaOptions`) MUST allow administrators to specify the desired cryptographic algorithms and their parameters for different contexts:
    *   Data at Rest (Beancount file decryption): KEM algorithm, symmetric cipher, hybrid mode details.
    *   Hashing: Hash algorithm (e.g., SHA3-256, SHA-256).
    *   WASM Module Integrity: PQC Signature algorithm (implicitly via public key type, or explicitly if multiple signature algorithm types are supported by the verification library for different keys).
*   **FR2.4 (Service Registry/Factory):** The backend `CryptoService` and frontend abstraction MUST use a registry or factory pattern to instantiate and provide the appropriate algorithm implementation based on the current configuration.
*   **FR2.5 (Algorithm Switching):** Changing the configured cryptographic algorithm (e.g., from SHA-256 to SHA3-256, or from one PQC KEM to another for new data) MUST NOT require code changes in the core application logic that *uses* the crypto service. It should only require a configuration update and potentially a restart of Fava.
*   **FR2.6 (Support for Hybrid Modes):** The `CryptoService` MUST explicitly support hybrid cryptographic schemes (classical + PQC) for KEMs and potentially signatures, allowing for a phased transition. The exact construction of hybrid schemes must be configurable or follow a defined standard.
*   **FR2.7 (Graceful Fallback/Error Handling):** If a configured algorithm is unavailable (e.g., library missing, misconfiguration), the `CryptoService` MUST handle this gracefully:
    *   Log a clear error.
    *   Potentially fall back to a known-good default if specified and appropriate for the context (e.g., SHA-256 if a PQC hash fails to initialize AND fallback is configured).
    *   Fail securely if no safe fallback exists for a critical operation (e.g., decryption).
*   **FR2.8 (Clear Separation of Concerns):** Cryptographic logic (algorithm implementation, key handling primitives) MUST be strictly isolated within the `CryptoService` / frontend abstraction, separate from Fava's business logic.

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The cryptographic agility framework itself MUST NOT introduce security vulnerabilities. Configuration changes should be auditable. Default configurations should be secure.
*   **NFR3.2 (Maintainability):** Adding new cryptographic algorithms or updating existing ones within the `CryptoService` or frontend abstraction MUST be straightforward and well-documented.
*   **NFR3.3 (Testability):** The `CryptoService` and its individual algorithm implementations MUST be highly testable with unit tests using known vectors. Agility itself (switching algorithms) must be testable via integration tests.
*   **NFR3.4 (Performance):** The abstraction layer SHOULD NOT introduce significant performance overhead beyond the inherent cost of the chosen cryptographic algorithms.
*   **NFR3.5 (Usability - Admin):** Configuration of cryptographic algorithms via `FavaOptions` MUST be clear, well-documented, and provide sensible defaults.
*   **NFR3.6 (Interoperability):** When switching algorithms, Fava must remain interoperable with data or systems using the newly configured algorithm (e.g., PQC-encrypted files created with a tool using the same PQC KEM).

## 4. User Stories

*   **US4.1:** As a Fava administrator, I want to easily switch the default hashing algorithm from SHA-256 to SHA3-256 by changing a single configuration setting, to improve long-term security.
*   **US4.2:** As a Fava developer, when a new NIST-standardized PQC KEM becomes widely supported, I want to add support for it in Fava's `CryptoService` for Beancount file decryption without refactoring large parts of the application.
*   **US4.3:** As a Fava administrator, if a PQC algorithm initially chosen is later found to have weaknesses, I want to be able to quickly reconfigure Fava to use a different, more secure PQC algorithm for new operations, assuming one is supported.
*   **US4.4:** As a Fava user, I want Fava to transparently handle decryption of my Beancount files, whether they were encrypted with an older supported PQC scheme or a newer one, based on Fava's current configuration and key.

## 5. Use Cases

### 5.1. Use Case: Administrator Changes Default Hashing Algorithm

*   **Actor:** Fava Administrator
*   **Preconditions:**
    *   Fava is currently using SHA-256 as its configured hashing algorithm.
    *   The `CryptoService` supports both SHA-256 and SHA3-256 implementations.
*   **Main Flow:**
    1.  Administrator stops Fava.
    2.  Administrator modifies Fava's configuration file (`fava_options`) to set `pqc_hashing_algorithm = "SHA3-256"`.
    3.  Administrator restarts Fava.
    4.  Fava initializes, and the `CryptoService`'s hashing component now uses the SHA3-256 implementation based on the new configuration.
    5.  All subsequent hashing operations (backend file integrity, frontend optimistic concurrency if it fetches this config) now use SHA3-256.
*   **Postconditions:**
    *   Fava uses SHA3-256 for hashing.
    *   No code changes were required.
    *   Existing data hashed with SHA-256 (if any stored hashes are still relevant and not recomputed) would no longer match new SHA3-256 hashes for the same data. (This implies that stored hashes for comparison, like in some optimistic locking scenarios if not just for transient checks, might need a migration strategy if the algorithm changes fundamentally).

### 5.2. Use Case: Developer Adds Support for a New PQC KEM

*   **Actor:** Fava Developer
*   **Preconditions:**
    *   A new PQC KEM, `NewPQC_KEM`, has been standardized and a Python library supporting it is available.
    *   Fava's `CryptoService` has a defined interface for KEM operations.
*   **Main Flow:**
    1.  Developer adds the new Python PQC library as a dependency.
    2.  Developer creates a new class `NewPQCKEMService` implementing the KEM interface within `fava.crypto_service`, wrapping the new library's functions for encapsulation/decapsulation.
    3.  Developer registers `NewPQCKEMService` with the `CryptoService` factory, associating it with a configuration string (e.g., "NEW_PQC_KEM_HYBRID_AES").
    4.  Developer updates Fava's documentation and default configuration options if `NewPQC_KEM` is to become a new recommended option.
    5.  Developer adds unit tests for `NewPQCKEMService` using test vectors for `NewPQC_KEM`.
*   **Postconditions:**
    *   Fava can now be configured to use `NewPQC_KEM` for decrypting Beancount files (assuming users encrypt files with a compatible tool).
    *   Core Fava logic (e.g., `FavaLedger`) did not require changes, as it interacts with the KEM via the abstract `CryptoService` interface.

## 6. Edge Cases & Error Handling

*   **EC6.1:** Configuration specifies an algorithm unknown to the `CryptoService` factory: Fava should fail to initialize the service for that context, log a critical error, and potentially refuse to start or operate in a degraded mode if the crypto context is essential.
*   **EC6.2:** A required PQC library for a configured algorithm is not installed or fails to load: Similar to EC6.1, the service for that algorithm cannot be initialized.
*   **EC6.3:** Incompatible parameters configured for a chosen algorithm (e.g., wrong key size for a KEM variant): The specific algorithm implementation within `CryptoService` should detect this during initialization or first use and raise an error.
*   **EC6.4:** Switching algorithms for data at rest where old data was encrypted with a previous algorithm: Fava, by default, will only be able to decrypt data matching its *current* KEM configuration and key. Supporting decryption of files encrypted with multiple past KEMs simultaneously would require more complex key/metadata management, potentially by trying multiple configured decryptors if the first fails. This is an advanced agility feature. For simplicity, the initial focus is on configuring *one active set* of algorithms at a time for a given context.

## 7. Constraints

*   **C7.1:** Agility is bounded by the availability of PQC libraries for Python (backend) and JS/WASM (frontend).
*   **C7.2:** Managing keys for multiple different PQC algorithms simultaneously can become complex for users. The agility framework should aim for simplicity in configuration where possible.
*   **C7.3:** Performance characteristics can vary significantly between different PQC algorithms. Switching algorithms might have performance implications.
*   **C7.4:** True "on-the-fly" algorithm switching without restart might be complex; configuration changes requiring a restart is an acceptable model for Fava.
*   **C7.5:** For data at rest, if the encryption format itself changes significantly with a new PQC scheme (beyond just algorithm choice), the `CryptoService` might need more substantial updates than just swapping an algorithm implementation. The abstraction should aim to cover common KEM+Symmetric cipher patterns.

## 8. Data Models (if applicable)

### 8.1. `CryptoService` Configuration in `FavaOptions` (Conceptual Consolidation)

```
# In Fava's configuration (e.g., fava_options.py or a dedicated crypto config section)

crypto_settings = {
    "data_at_rest": {
        "decryption_enabled": True,
        "active_suite_id": "default_pqc_hybrid", # User selects a pre-defined or custom suite
        "suites": {
            "default_pqc_hybrid": {
                "description": "Default PQC Hybrid: Kyber768 with AES-256-GCM",
                "kem_algorithm": "KYBER768", # Internal name for CryptoService factory
                "kem_key_source_type": "FILE", # e.g., FILE, ENV_VAR, GPG_AGENT_PQC
                "kem_key_source_detail": "/path/to/kyber768_private.key",
                "symmetric_algorithm": "AES256GCM", # Internal name
                "fallback_to_classical_gpg": True
            },
            "legacy_gpg": {
                "description": "Classical GPG Decryption",
                "type": "CLASSICAL_GPG", # Special type for GPG passthrough
                "gpg_key_id": "0xUSERKEYID" # Optional, if needed
            }
            # Users or future updates could add more suites here
            # "another_pqc_suite": { ... }
        },
        "gpg_decryption_enabled": True # Separate toggle for classical GPG if not part of suites
    },
    "hashing": {
        "default_algorithm": "SHA3-256" # Options: "SHA3-256", "SHAKE256_256", "SHA256"
    },
    "wasm_integrity": {
        "verification_enabled": True,
        # Public key and algorithm name might be compiled in or part of build config,
        # but could be overridable here for advanced scenarios or key rotation.
        "public_key_pem": "BEGIN PQC PUBLIC KEY...", # Or path to key
        "signature_algorithm": "Dilithium2"
    }
}
```
*This structure allows defining multiple "suites" for data at rest, with one being active. The `CryptoService` would be configured based on the `active_suite_id`.*

## 9. UI/UX Flow Outlines (if applicable)

*   **UI9.1 (Admin Configuration Panel):**
    *   A dedicated section in Fava's settings UI for "Cryptographic Settings".
    *   Dropdowns or selection fields for:
        *   Data at Rest: Choosing an `active_suite_id` from available `suites`. UI could allow defining new suites or editing parameters for existing ones (key paths, etc.).
        *   Hashing: Selecting the `default_algorithm`.
        *   WASM Integrity: Toggling `verification_enabled`, potentially displaying current public key info (not editing it directly in UI for security).
    *   Clear explanations for each option, security implications, and links to relevant documentation.
    *   Warnings if experimental or non-default algorithms are selected.

## 10. Initial TDD Anchors or Pseudocode Stubs

### 10.1. Backend `CryptoService` Abstraction and Factory

```python
# In fava.crypto_service.py

# --- Interfaces ---
class KEMService(ABC):
    @abstractmethod
    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]: # ciphertext, shared_secret
        pass
    @abstractmethod
    def decapsulate(self, private_key: bytes, encapsulated_key: bytes) -> bytes: # shared_secret
        pass

class SymmetricEncryptionService(ABC):
    @abstractmethod
    def encrypt(self, plaintext: bytes, key: bytes, aad: Optional[bytes] = None) -> bytes: # ciphertext with nonce/tag
        pass
    @abstractmethod
    def decrypt(self, ciphertext: bytes, key: bytes, aad: Optional[bytes] = None) -> bytes: # plaintext
        pass

class HashingService(ABC): # Defined in PQC_Hashing_Spec.md
    @abstractmethod
    def hash_data(self, data: bytes) -> str: pass

class SignatureService(ABC):
    @abstractmethod
    def sign(self, message: bytes, private_key: bytes) -> bytes: pass
    @abstractmethod
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool: pass

# --- Hybrid Decryption Service for Data at Rest (Example) ---
class HybridDecryptionService:
    def __init__(self, kem_service: KEMService, sym_service: SymmetricEncryptionService, kem_priv_key: bytes):
        self.kem_service = kem_service
        self.sym_service = sym_service
        self.kem_priv_key = kem_priv_key

    def decrypt(self, pqc_encrypted_data_bundle: bytes) -> str:
        # 1. Parse pqc_encrypted_data_bundle to extract:
        #    - encapsulated_kem_key
        #    - symmetric_ciphertext (which includes nonce/tag)
        #    - aad (if used)
        #    (This parsing depends on the chosen on-disk format for hybrid encrypted files)
        # conceptual_encapsulated_key, conceptual_sym_ciphertext, conceptual_aad = self._parse_bundle(pqc_encrypted_data_bundle)

        # shared_secret = self.kem_service.decapsulate(self.kem_priv_key, conceptual_encapsulated_key)
        # Derive symmetric key from shared_secret if necessary (e.g., using HKDF with shared_secret as IKM)
        # derived_symmetric_key = self._hkdf_derive(shared_secret, salt="fava-sym-key", length=32)

        # plaintext_bytes = self.sym_service.decrypt(conceptual_sym_ciphertext, derived_symmetric_key, conceptual_aad)
        # return plaintext_bytes.decode('utf-8')
        raise NotImplementedError("HybridDecryptionService.decrypt stub")

# --- CryptoServiceLocator / Factory ---
# _KEM_REGISTRY = {}
# _SYM_REGISTRY = {}
# _HASH_REGISTRY = {}
# _SIGNATURE_REGISTRY = {}
# _HYBRID_DECRYPTION_CONFIG = None # Loaded from FavaOptions

# def register_kem_service(name: str, service_class: type[KEMService]): _KEM_REGISTRY[name] = service_class
# def register_sym_service(name: str, service_class: type[SymmetricEncryptionService]): _SYM_REGISTRY[name] = service_class
# # ... similar for hash and signature

# def configure_crypto_services(fava_options: FavaOptions):
#     # global _HYBRID_DECRYPTION_CONFIG, _CURRENT_HASH_ALGO_NAME, ...
#     # Parse fava_options.crypto_settings
#     # _HYBRID_DECRYPTION_CONFIG = fava_options.crypto_settings["data_at_rest"]["suites"][active_suite_id]
#     # _CURRENT_HASH_ALGO_NAME = fava_options.crypto_settings["hashing"]["default_algorithm"]
#     pass

# def get_hybrid_decryption_service() -> HybridDecryptionService:
#     if not _HYBRID_DECRYPTION_CONFIG: raise RuntimeError("Crypto services not configured")
#     kem_algo_name = _HYBRID_DECRYPTION_CONFIG["kem_algorithm"]
#     sym_algo_name = _HYBRID_DECRYPTION_CONFIG["symmetric_algorithm"]
#     kem_key_path = _HYBRID_DECRYPTION_CONFIG["kem_key_source_detail"] # Simplified

#     kem_service_class = _KEM_REGISTRY.get(kem_algo_name)
#     sym_service_class = _SYM_REGISTRY.get(sym_algo_name)
#     if not kem_service_class or not sym_service_class:
#         raise ValueError(f"Unsupported KEM/Symmetric algo: {kem_algo_name}/{sym_algo_name}")

#     # kem_priv_key_bytes = _load_key_from_path(kem_key_path) # Implement key loading
#     # return HybridDecryptionService(kem_service_class(), sym_service_class(), kem_priv_key_bytes)
#     raise NotImplementedError("get_hybrid_decryption_service stub")


# def get_hashing_service() -> HashingService:
#     # hash_service_class = _HASH_REGISTRY.get(_CURRENT_HASH_ALGO_NAME)
#     # return hash_service_class()
#     raise NotImplementedError("get_hashing_service stub")

# TEST: test_configure_crypto_services_loads_settings_from_fava_options()
#   SETUP: Mock FavaOptions with specific crypto_settings.
#   ACTION: Call configure_crypto_services(mock_fava_options).
#   ASSERT: Internal state of crypto_service module (e.g., _HYBRID_DECRYPTION_CONFIG) is set correctly.

# TEST: test_get_hybrid_decryption_service_returns_configured_kem_and_sym_impl()
#   SETUP:
#     Register mock KEMService (MockKyberService) for "KYBER768".
#     Register mock SymmetricEncryptionService (MockAesService) for "AES256GCM".
#     Configure crypto_services with active suite using "KYBER768" and "AES256GCM".
#     Mock key loading to provide dummy key bytes.
#   ACTION: Call get_hybrid_decryption_service().
#   ASSERT: Returned HybridDecryptionService contains instances of MockKyberService and MockAesService.

# TEST: test_switching_active_data_at_rest_suite_changes_services_used()
#   SETUP:
#     Register two sets of mock KEM/Symmetric services (e.g., Kyber+AES, NewKEM+ChaCha).
#     Configure Fava for Kyber+AES suite and call get_hybrid_decryption_service(), verify types.
#     Re-configure Fava (conceptually, by re-calling configure_crypto_services with different options) for NewKEM+ChaCha suite.
#   ACTION: Call get_hybrid_decryption_service() again.
#   ASSERT: Returned service now uses NewKEMService and ChaChaService instances.
```

### 10.2. Frontend Abstraction (Conceptual)

```typescript
// In frontend/src/lib/pqcCryptoFacade.ts (example name)

// // For Hashing (from PQC_Hashing_Spec.md)
// export async function calculateFrontendHash(data: string): Promise<string> {
//   const configuredAlgo = await getFavaConfiguredHashAlgorithm(); // API call
//   return internalCalculateHash(data, configuredAlgo); // internalCalculateHash is the one with switch/if-else
// }

// // For WASM Signature Verification (from PQC_WASM_Module_Integrity_Spec.md)
// export async function verifyFrontendWasmSignature(
//   wasmBuffer: ArrayBuffer,
//   signatureBuffer: ArrayBuffer
// ): Promise<boolean> {
//   const { publicKey, algorithm } = await getFavaWasmVerificationConfig(); // API call
//   return internalVerifySignature(wasmBuffer, signatureBuffer, publicKey, algorithm);
// }

// TEST (Frontend): test_calculateFrontendHash_uses_algorithm_from_fava_config_api()
//   SETUP:
//     Mock API endpoint for Fava config to return "SHA3-256" for hashing.
//     Spy on `internalCalculateHash`.
//   ACTION: Call `calculateFrontendHash("test data")`.
//   ASSERT: `internalCalculateHash` was called with "test data" and "SHA3-256".
```

## 11. Dependencies

*   **External Libraries:** Python and JS/WASM PQC libraries (e.g., `oqs-python`, `liboqs-js`, `pysha3`, `js-sha3`).
*   **Internal Fava Modules:**
    *   `fava.core.FavaOptions`: Central source for cryptographic configuration.
    *   `fava.crypto_service` (new): Backend abstraction layer.
    *   `frontend/src/lib/pqcCrypto.ts` (or similar, new): Frontend abstraction layer.
    *   All Fava components that currently perform cryptographic operations (file loading, hashing in backend, hashing in frontend, WASM loading) will need to be refactored to use these new abstraction layers.
    *   Fava API endpoints to provide necessary crypto configuration to the frontend (e.g., active hash algorithm, WASM public key if not compiled in).

## 12. Integration Points

*   **IP12.1 (Configuration Loading):** `FavaOptions` loads the `crypto_settings` block. The `configure_crypto_services` function is called early in Fava's startup to initialize the crypto service locator/factory based on these options.
*   **IP12.2 (Backend Service Usage):**
    *   `FavaLedger` (for Data at Rest) calls `get_hybrid_decryption_service().decrypt()`.
    *   `src/fava/core/file.py` (for backend hashing) calls `get_hashing_service().hash_data()`.
*   **IP12.3 (Frontend Service Usage):**
    *   `SliceEditor.svelte` (for frontend hashing) calls `calculateFrontendHash()`.
    *   `frontend/src/codemirror/beancount.ts` (for WASM integrity) calls `verifyFrontendWasmSignature()`.
*   **IP12.4 (API for Frontend Configuration):** The frontend abstractions (`calculateFrontendHash`, `verifyFrontendWasmSignature`) will likely need to fetch their specific algorithm configurations (e.g., which hash algo to use, which public key for WASM sig) from a Fava API endpoint that exposes parts of `FavaOptions.crypto_settings`.