# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 1

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

## 1. Introduction

This guide provides a technical overview for developers working on or extending Fava's Post-Quantum Cryptography (PQC) capabilities. It details the architecture of PQC modules, the cryptographic agility framework, API details (if any), and key considerations for development.

The integration of PQC into Fava aims to enhance long-term security against quantum threats, ensuring the confidentiality and integrity of user data. This guide assumes familiarity with Fava's general architecture and the core concepts of PQC.

**Key Reference Documents:**
*   Project Master Plan: [`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md)
*   PQC Specification Documents: [`docs/specifications/`](../../docs/specifications/)
*   PQC Architecture Documents: [`docs/architecture/`](../../docs/architecture/)
*   PQC Pseudocode Documents: [`docs/pseudocode/`](../../docs/pseudocode/)

## 2. PQC Integration Overview

Fava's PQC integration is designed to be modular and configurable, addressing several key areas:
*   **Data at Rest:** Protecting Beancount files using hybrid PQC encryption.
*   **Data in Transit:** Ensuring secure communication through PQC-TLS enabled reverse proxies.
*   **Hashing:** Employing PQC-resistant hash functions for data integrity.
*   **WASM Module Integrity:** Verifying the integrity of WebAssembly modules using PQC signatures.
*   **Cryptographic Agility:** Allowing Fava to adapt to new cryptographic standards over time.

The core principle is to abstract cryptographic operations, allowing the main Fava application logic to remain largely independent of specific PQC algorithm choices. This is primarily achieved through a backend `BackendCryptoService` and frontend cryptographic abstractions.

### 2.1. High-Level Architecture

The PQC features are integrated into Fava through a combination of backend services and frontend components.

*   **Backend:**
    *   A central `BackendCryptoService` (located conceptually in `src/fava/pqc/backend_crypto_service.py`) manages cryptographic operations like encryption, decryption, and hashing.
    *   It utilizes specific handlers (e.g., `HybridPqcCryptoHandler`, `GpgCryptoHandler`) for different cryptographic schemes.
    *   Configuration is managed via `FavaOptions` and a global PQC configuration structure (e.g., `FAVA_CRYPTO_SETTINGS` loaded by a `GlobalConfig` module in `src/fava/pqc/global_config.py`).
    *   [`FavaLedger`](../../src/fava/core/ledger.py) interacts with the `BackendCryptoService` for encrypting and decrypting Beancount files.
*   **Frontend:**
    *   Cryptographic operations like hashing and PQC signature verification are handled by abstractions (e.g., in `frontend/src/lib/pqcCrypto.ts`).
    *   Frontend components fetch necessary PQC configuration (e.g., active hashing algorithm, WASM public key) from backend APIs (e.g., `/api/pqc_config` served by `src/fava/json_api.py`).
    *   WASM module loading (e.g., `tree-sitter-beancount.wasm` in `frontend/src/codemirror/beancount.ts`) incorporates PQC signature verification using libraries like `liboqs-js`.

The overall system architecture emphasizes cryptographic agility, allowing administrators to configure and switch algorithms as standards evolve.

## 3. Core PQC Modules & Services (Backend)

The backend PQC integration revolves around the `BackendCryptoService` and its associated components.

### 3.1. `BackendCryptoService` and `CryptoHandler` Architecture

As detailed in [`docs/architecture/PQC_Cryptographic_Agility_Arch.md`](../../docs/architecture/PQC_Cryptographic_Agility_Arch.md) and [`docs/architecture/PQC_Data_At_Rest_Arch.md`](../../docs/architecture/PQC_Data_At_Rest_Arch.md):

*   **`BackendCryptoService` (Conceptual Path: `src/fava/pqc/backend_crypto_service.py`):**
    *   Acts as a central point for accessing cryptographic functionalities.
    *   Uses a registry and factory pattern to manage and provide `CryptoHandler` instances.
    *   Retrieves active configurations from the `GlobalConfig` module.
    *   Provides methods like:
        *   `GetCryptoHandler(suite_id: str) -> CryptoHandler`: Retrieves a specific handler.
        *   `GetActiveEncryptionHandler() -> CryptoHandler`: Gets the handler for the currently configured active encryption suite for data at rest.
        *   `GetConfiguredDecryptionHandlers() -> List[CryptoHandler]`: Returns an ordered list of handlers to attempt for decryption, based on `FAVA_CRYPTO_SETTINGS.data_at_rest.decryption_attempt_order`.
        *   It also encompasses or provides access to the `HashingService`.

*   **`CryptoHandler` (Interface):**
    *   Defines a common interface for different cryptographic schemes.
    *   Key methods:
        *   `get_suite_id() -> str`: Returns the unique identifier of the suite.
        *   `encrypt(plaintext: bytes, key_material: Any, suite_specific_config: Dict) -> bytes`: Encrypts data, returning an `EncryptedFileBundle`.
        *   `decrypt(bundle: bytes, key_material: Any, suite_specific_config: Dict) -> bytes`: Decrypts data from an `EncryptedFileBundle`.
        *   `can_handle(file_path: str, content_bytes_peek: Optional[bytes], config: Dict) -> bool`: (Primarily for decryption) Checks if the handler can process the given file/content.

*   **Handler Registration (`src/fava/pqc/app_startup.py`):**
    *   During application startup, concrete `CryptoHandler` implementations (or their factories) are registered with the `BackendCryptoService`.
    *   This registration is driven by the `FAVA_CRYPTO_SETTINGS.data_at_rest.suites` configuration.

### 3.2. PQC Handlers

#### 3.2.1. `HybridPqcCryptoHandler`
*   **Purpose:** Implements Fava-driven PQC hybrid encryption and decryption for data at rest.
*   **Default Scheme:** X25519 (classical KEM) + ML-KEM-768 (Kyber PQC KEM) + AES-256-GCM (symmetric cipher). The specific algorithms are defined by the suite configuration in `FAVA_CRYPTO_SETTINGS`.
*   **Responsibilities:**
    *   Manages the `EncryptedFileBundle` format (see Section 3.4).
    *   Performs KEM encapsulation/decapsulation for both classical and PQC components.
    *   Derives symmetric keys using a KDF (e.g., HKDF-SHA3-512) from combined KEM shared secrets.
    *   Encrypts/decrypts actual file content using the symmetric cipher (AES-256-GCM).
    *   Interacts with the `KeyManagement` module (see Section 3.3) to obtain cryptographic keys.
*   **Reference:** [`docs/architecture/PQC_Data_At_Rest_Arch.md#73-hybridpqchandler`](../../docs/architecture/PQC_Data_At_Rest_Arch.md#73-hybridpqchandler)

#### 3.2.2. `GpgCryptoHandler`
*   **Purpose:** Provides backward compatibility for decrypting classically GPG-encrypted Beancount files.
*   **Responsibilities:**
    *   Interacts with the system's GPG tool/agent (e.g., via `subprocess` calls to `gpg --decrypt`).
    *   Fava-driven encryption using GPG is generally out of scope for the PQC enhancements; this handler focuses on decryption.
*   **Reference:** [`docs/architecture/PQC_Data_At_Rest_Arch.md#74-gpghandler`](../../docs/architecture/PQC_Data_At_Rest_Arch.md#74-gpghandler)
*   **Conceptual Path:** `src/fava/pqc/gpg_handler.py`

### 3.3. Key Management (`src/fava/pqc/keys.py` or within `backend_crypto_service.py`)

The key management module is responsible for handling cryptographic keys for the `HybridPqcCryptoHandler`.

*   **Responsibilities:**
    *   **Passphrase-Based Key Derivation:**
        *   Derives PQC KEM key pairs and classical KEM key pairs from a user-provided passphrase.
        *   This process MUST use a strong Password-Based Key Derivation Function (PBKDF) like **Argon2id** for passphrase stretching, using a unique salt (stored in the `EncryptedFileBundle`).
        *   The output of the PBKDF is then used as Input Keying Material (IKM) for a Key Derivation Function (KDF) like **HKDF-SHA3-512** to derive the actual KEM keys.
    *   **External Key File Loading:** Optionally supports loading raw PQC/classical key material from user-specified files (paths configured in Fava options).
    *   **Secure Key Handling:** Ensures keys are handled securely in memory and zeroized when no longer needed, where possible.
    *   **Key Export (FR2.9):** Provides a mechanism to export Fava-managed PQC private keys. This feature has significant security implications and must be implemented with extreme caution, including strong user warnings and potentially encrypted export formats (see ADR-005 in [`docs/architecture/PQC_Data_At_Rest_Arch.md`](../../docs/architecture/PQC_Data_At_Rest_Arch.md)).
*   **Key Functions (Conceptual):**
    *   `derive_kem_keys_from_passphrase(passphrase: str, salt: bytes, suite_config: Dict) -> KeyMaterial`
    *   `load_keys_from_external_file(key_file_paths_config: Dict) -> KeyMaterial`
    *   `export_fava_managed_pqc_private_keys(key_context: Any, export_format: str, export_passphrase: Optional[str]) -> bytes`
*   **Reference:** [`docs/architecture/PQC_Data_At_Rest_Arch.md#75-key-management-modulefunctions`](../../docs/architecture/PQC_Data_At_Rest_Arch.md#75-key-management-modulefunctions)

### 3.4. Encrypted File Bundle (`src/fava/core/encrypted_file_bundle.py` or similar)

This structure defines the format for Beancount files encrypted by Fava's PQC hybrid scheme.

*   **Purpose:** To store the encrypted data along with all necessary metadata for decryption.
*   **Key Fields (as per [`docs/architecture/PQC_Data_At_Rest_Arch.md#82-encryptedfilebundle`](../../docs/architecture/PQC_Data_At_Rest_Arch.md#82-encryptedfilebundle)):
    *   `format_identifier`: e.g., "FAVA_PQC_HYBRID_V1"
    *   `suite_id_used`: Identifier of the cryptographic suite used (e.g., "HYBRID_X25519_MLKEM768_AES256GCM")
    *   `classical_kem_ephemeral_public_key`: (Optional, if applicable to the classical KEM)
    *   `pqc_kem_encapsulated_key`: Ciphertext from the PQC KEM
    *   `symmetric_cipher_iv_or_nonce`: IV/nonce for the symmetric cipher
    *   `encrypted_data_ciphertext`: The actual encrypted Beancount data
    *   `authentication_tag`: AEAD authentication tag (e.g., from AES-GCM)
    *   `pbkdf_salt_for_passphrase_derivation`: Salt used with Argon2id if keys were passphrase-derived.
    *   `kdf_salt_for_hybrid_sk_derivation`: (Optional) Salt for KDF deriving symmetric key from KEM outputs.
*   **Serialization:** The bundle is serialized to bytes for storage and deserialized during decryption.
*   **Developer Notes:**
    *   The `suite_id_used` field is crucial for cryptographic agility, allowing Fava to identify the correct decryption handler and parameters.
    *   Proper management of salts (PBKDF salt especially) is critical for security if using passphrase-derived keys. Salts must be unique per encryption and stored with the bundle.

---
End of Part 1. More content will follow in Part 2.