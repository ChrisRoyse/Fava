# PQC Integration Specification: Data at Rest

**Version:** 1.0
**Date:** 2025-06-02

## 1. Introduction

This document outlines the specifications for integrating Post-Quantum Cryptography (PQC) to protect Data at Rest within the Fava application, primarily focusing on encrypted Beancount files. It draws upon the overall PQC integration plan ([`docs/Plan.MD`](../../docs/Plan.MD)), research findings ([`docs/research/`](../../docs/research/)), and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The primary goal is to ensure that Beancount files, when encrypted, are protected against threats from both classical and quantum computers.

## 2. Functional Requirements

*   **FR2.1:** The system MUST support decryption of Beancount files encrypted with a NIST-selected PQC Key Encapsulation Mechanism (KEM) in a hybrid scheme (PQC KEM + classical symmetric cipher, e.g., AES-GCM). The specific PQC KEM (e.g., CRYSTALS-Kyber) and symmetric cipher will be configurable.
*   **FR2.2:** The system MUST support decryption of Beancount files encrypted using classical GPG, as per current Fava functionality, to maintain backward compatibility.
*   **FR2.3:** The system MUST allow configuration of the active PQC KEM, associated parameters (e.g., security level), and the symmetric encryption algorithm for PQC-protected files.
*   **FR2.4:** Fava's core logic (loading, parsing, querying) MUST operate correctly on data decrypted from PQC-protected Beancount files, identical to how it operates on classically encrypted or unencrypted files.
*   **FR2.5:** The system SHOULD provide a mechanism or clear guidance for users to encrypt their Beancount files using the supported PQC hybrid scheme. (This might involve recommending external tools if Fava does not directly implement encryption.)
*   **FR2.6:** The system MUST clearly indicate to the user if a Beancount file is PQC-encrypted, classically encrypted, or unencrypted, if discernible.
*   **FR2.7:** The system MUST provide informative error messages if decryption fails due to incorrect keys, unsupported algorithms, or corrupted data for both classical and PQC encrypted files.

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The PQC implementation for data at rest MUST adhere to NIST standards and best practices for the chosen algorithms (e.g., CRYSTALS-Kyber). Key management practices must be secure.
*   **NFR3.2 (Performance):** Decryption of PQC-encrypted files SHOULD NOT introduce prohibitive performance overhead compared to classically encrypted files. Target: Decryption overhead for PQC should be within X% of GPG RSA-4096 decryption for a typical Beancount file size (X to be determined during development, e.g., 50-100% initially).
*   **NFR3.3 (Usability):** If Fava manages PQC keys or configurations, the process MUST be as user-friendly as possible. Users should be clearly guided on how to manage PQC keys and configure decryption.
*   **NFR3.4 (Reliability):** The PQC decryption process MUST be reliable and consistently decrypt validly encrypted files.
*   **NFR3.5 (Interoperability):** If relying on external tools (e.g., a PQC-enabled GPG), Fava MUST be compatible with the output of these tools.
*   **NFR3.6 (Maintainability):** The PQC decryption logic MUST be implemented in a modular way (e.g., via the proposed `CryptoService`) to facilitate updates and algorithm changes.
*   **NFR3.7 (Cryptographic Agility):** The system MUST allow switching between different PQC KEMs or hybrid configurations with minimal code changes, primarily through configuration updates. (See [`PQC_Cryptographic_Agility_Spec.md`](PQC_Cryptographic_Agility_Spec.md))

## 4. User Stories

*   **US4.1:** As a security-conscious user, I want to encrypt my Beancount file using a quantum-resistant algorithm (hybrid PQC KEM + AES) so that my financial data remains confidential even against future quantum threats.
*   **US4.2:** As a Fava user, I want to open my PQC-encrypted Beancount file in Fava seamlessly, just like I open my GPG-encrypted or unencrypted files.
*   **US4.3:** As a Fava user, if I try to open a PQC-encrypted file with the wrong key or if the file is corrupted, I want to receive a clear error message explaining the problem.
*   **US4.4:** As a Fava administrator, I want to configure Fava to use a specific PQC KEM (e.g., Kyber-1024) and symmetric cipher for decrypting Beancount files.
*   **US4.5:** As a long-time Fava user, I want to continue using my existing GPG-encrypted Beancount files without any issues after Fava is updated with PQC support.

## 5. Use Cases

### 5.1. Use Case: Load PQC-Encrypted Beancount File (Happy Path)

*   **Actor:** Fava User
*   **Preconditions:**
    *   Fava is configured to support `PQC_KEM_Algorithm_X` and `Symmetric_Cipher_Y`.
    *   User possesses a Beancount file (`data.bc.pqc`) encrypted with `PQC_KEM_Algorithm_X` + `Symmetric_Cipher_Y`.
    *   User has the correct PQC decryption key (or key material) accessible to Fava (e.g., via configuration, environment variable, or a PQC-GPG agent).
*   **Main Flow:**
    1.  User instructs Fava to load `data.bc.pqc`.
    2.  Fava identifies the file as potentially encrypted (based on configuration or file metadata if available).
    3.  Fava's `CryptoService` (or delegated GPG mechanism) attempts decryption using the configured `PQC_KEM_Algorithm_X` and key.
    4.  The KEM decapsulates the symmetric key.
    5.  The symmetric key is used with `Symmetric_Cipher_Y` to decrypt the file content.
    6.  Fava receives the plaintext Beancount data.
    7.  Fava loads, parses, and displays the Beancount data.
*   **Postconditions:**
    *   User can view and interact with their financial data in Fava.
    *   Fava logs successful PQC decryption (e.g., `INFO: Successfully decrypted 'data.bc.pqc' using PQC KEM: [Algorithm_X_Name]`).

### 5.2. Use Case: Attempt to Load PQC-Encrypted File with Incorrect Key

*   **Actor:** Fava User
*   **Preconditions:**
    *   Same as 5.1, but the PQC decryption key available to Fava is incorrect for `data.bc.pqc`.
*   **Main Flow:**
    1.  User instructs Fava to load `data.bc.pqc`.
    2.  Fava attempts decryption (Steps 2-4 from 5.1).
    3.  The PQC KEM decapsulation fails due to the incorrect key, or the subsequent symmetric decryption yields garbled data.
    4.  Fava detects the decryption failure.
    5.  Fava displays an error message to the user (e.g., "Error: Failed to decrypt Beancount file. Incorrect key or corrupted file.").
*   **Postconditions:**
    *   The Beancount file is not loaded.
    *   Fava remains operational.
    *   Fava logs the decryption failure (e.g., `ERROR: Failed to decrypt 'data.bc.pqc'. Decryption error with PQC KEM: [Algorithm_X_Name].`).

### 5.3. Use Case: Load Classically GPG-Encrypted Beancount File

*   **Actor:** Fava User
*   **Preconditions:**
    *   User possesses a Beancount file (`data.bc.gpg`) encrypted with classical GPG.
    *   User has the correct GPG key accessible via their GPG agent/keyring.
    *   Fava is configured to use GPG for decryption (or this is the default fallback).
*   **Main Flow:**
    1.  User instructs Fava to load `data.bc.gpg`.
    2.  Fava (via Beancount's loader or a `CryptoService` GPG implementation) invokes GPG to decrypt the file.
    3.  GPG decrypts the file.
    4.  Fava receives the plaintext Beancount data.
    5.  Fava loads, parses, and displays the Beancount data.
*   **Postconditions:**
    *   User can view and interact with their financial data in Fava.

## 6. Edge Cases & Error Handling

*   **EC6.1:** File is corrupted (PQC encrypted): System should detect corruption (e.g., failed integrity check from AEAD cipher) and report an error, not crash.
*   **EC6.2:** Configured PQC algorithm in Fava does not match the algorithm used to encrypt the file: System should report a specific error.
*   **EC6.3:** PQC key file is missing or inaccessible: System should report an error.
*   **EC6.4:** Symmetric cipher (e.g., AES) decryption fails after successful KEM decapsulation (e.g., wrong symmetric key somehow derived or file tampered post-KEM): Report specific error.
*   **EC6.5:** Extremely large Beancount file encrypted with PQC: Monitor for excessive decryption time and potential timeouts. System should remain responsive.
*   **EC6.6:** PQC library dependency is missing or fails to initialize: Fava should start with PQC features disabled and log a clear error, or fail to start if PQC is mandated.
*   **EC6.7:** Beancount file path contains unusual characters and is PQC encrypted.
*   **EC6.8:** User attempts to save/modify a PQC-encrypted file: Current scope is decryption. Saving PQC-encrypted files from Fava is out of scope for initial PQC integration unless explicitly added. If attempted, Fava should behave as it currently does for GPG-encrypted files (likely disallowing direct save or saving unencrypted).

## 7. Constraints

*   **C7.1:** Initial implementation will rely on external PQC libraries (e.g., `liboqs` via `oqs-python`) as Python's standard library does not yet support PQC.
*   **C7.2:** The choice of PQC algorithms will be limited to those standardized or in late stages of standardization by NIST (e.g., Kyber for KEM).
*   **C7.3:** Fava's direct PQC key management capabilities will be minimal initially. Focus is on using keys provided via configuration or external tools (like a PQC-GPG agent). Secure key storage is primarily the user's responsibility or delegated.
*   **C7.4:** Direct encryption of Beancount files *using PQC from within Fava* is out of scope for the initial phase. The focus is on decryption. Users will need to use external tools for PQC encryption.
*   **C7.5:** Performance of PQC operations must be acceptable on typical user hardware where Fava server runs. See NFR3.2.
*   **C7.6:** Full reliance on Beancount's loader for PQC decryption is contingent on Beancount itself supporting PQC-aware GPG or similar mechanisms. If not, Fava's `CryptoService` will need to handle decryption before passing plaintext to Beancount. (As per [`docs/Plan.MD`](../../docs/Plan.MD), a Fava-side decryption abstraction is preferred for agility).

## 8. Data Models (if applicable)

### 8.1. PQC Configuration Parameters (Conceptual)

Stored within Fava's options/configuration system:

*   `pqc_data_at_rest_enabled`: boolean (Enable/disable PQC decryption for data at rest)
*   `pqc_data_at_rest_algorithm_suite`: string (e.g., "HYBRID_KYBER768_AES256GCM")
    *   This could be broken down further:
        *   `pqc_kem_algorithm`: string (e.g., "KYBER768", "KYBER1024")
        *   `pqc_symmetric_algorithm`: string (e.g., "AES256GCM")
*   `pqc_key_source_type`: string (e.g., "FILE", "ENV_VAR", "GPG_AGENT_PQC")
*   `pqc_key_source_detail`: string (e.g., path to key file, name of environment variable)
*   `pqc_fallback_to_classical_gpg`: boolean (Default: true)

*Note: The exact structure will depend on the `CryptoService` implementation and how keys are managed.*

### 8.2. Encrypted File Metadata (Conceptual, if Fava handles decryption directly)

If Fava directly handles decryption and needs to identify PQC parameters from the file itself (less likely for initial phase, more likely if Fava *encrypts* too). This is highly dependent on the chosen PQC library and any container format used.

A wrapper format for the encrypted Beancount file might include:
*   `format_version`: integer
*   `kem_algorithm_oid_or_name`: string
*   `kem_public_key_recipient_info` (if applicable, e.g., for multiple recipients, though unlikely for Beancount files)
*   `kem_encapsulated_key`: bytes
*   `symmetric_cipher_oid_or_name`: string
*   `symmetric_cipher_iv_or_nonce`: bytes
*   `encrypted_data_ciphertext`: bytes
*   `authentication_tag` (if AEAD): bytes

*For initial phase, Fava will likely assume the configuration dictates the algorithm, and the key provided is for that algorithm. It won't parse such metadata from the file unless a PQC-GPG standard emerges that Fava can leverage.*

## 9. UI/UX Flow Outlines (if applicable)

*   **UI9.1 (Configuration):**
    *   If Fava manages PQC settings directly (not via Beancount options passthrough):
        *   A section in Fava's settings/options UI to configure PQC for data at rest.
        *   Fields for enabling PQC, selecting algorithm suite, specifying key source.
        *   Clear explanations and warnings about the experimental nature or security implications.
*   **UI9.2 (File Loading):**
    *   No significant UI change expected for successful loads.
    *   Error messages for failed PQC decryption should be displayed clearly in the UI (e.g., where file loading errors are currently shown).
    *   Possibly a status indicator if a file is PQC encrypted, if this can be determined and is deemed useful.

## 10. Initial TDD Anchors or Pseudocode Stubs

### 10.1. `CryptoService` Decryption Interface (Backend)

```python
# In fava.crypto_service (conceptual)

class DecryptionService(ABC):
    @abstractmethod
    def can_decrypt(self, file_path: str, config: PQCFileConfig) -> bool:
        """Checks if this service can attempt decryption based on config/file type."""
        pass

    @abstractmethod
    def decrypt_content(self, encrypted_content: bytes, config: PQCFileConfig, key_material: Any) -> str:
        """Decrypts content, returns plaintext string. Raises DecryptionError on failure."""
        pass

# TEST: test_kyber_aes_hybrid_decryption_service_decrypts_valid_file()
#   SETUP: Create a test file encrypted with Kyber768 + AES256-GCM and a known key.
#          Instantiate KyberAesHybridDecryptionService with correct config and key.
#   ACTION: Call decrypt_content() on the encrypted file.
#   ASSERT: Returns correct plaintext. No exceptions raised.

# TEST: test_kyber_aes_hybrid_decryption_service_fails_for_wrong_key()
#   SETUP: Create a test file encrypted with Kyber768 + AES256-GCM and a known key.
#          Instantiate KyberAesHybridDecryptionService with correct config but WRONG key.
#   ACTION: Call decrypt_content() on the encrypted file.
#   ASSERT: Raises DecryptionError.

# TEST: test_gpg_decryption_service_decrypts_valid_gpg_file() (existing behavior wrapper)
#   SETUP: Use an existing GPG encrypted test file and key.
#   ACTION: Call decrypt_content() via GPGDecryptionService.
#   ASSERT: Returns correct plaintext.

# TEST: test_decryption_service_factory_selects_pqc_service_based_on_config()
#   SETUP: Configure Fava for PQC_KEM_X.
#   ACTION: Call get_decryption_service_for_file(file_path, config).
#   ASSERT: Returns an instance of PQC_KEM_X_DecryptionService.

# TEST: test_decryption_service_factory_selects_gpg_service_if_pqc_disabled_or_fallback()
#   SETUP: Configure Fava for PQC disabled or PQC fails and fallback is enabled.
#   ACTION: Call get_decryption_service_for_file(file_path, config).
#   ASSERT: Returns an instance of GPGDecryptionService.
```

### 10.2. `FavaLedger` Integration Stub (Backend)

```python
# In fava.core.FavaLedger (conceptual modification for load_file)

# def _try_decrypt_content(self, file_path: str, content_bytes: bytes) -> str:
#     # 1. Determine if PQC should be attempted based on self.fava_options / PQC config.
#     #    pqc_config = self.fava_options.get_pqc_config_for_file(file_path)
#     #    key_material = self.fava_options.get_pqc_key_material(pqc_config)
#
#     # 2. If PQC enabled for this file:
#     #    try:
#     #        dec_service = get_crypto_service_locator().get_decryption_service(pqc_config.algorithm_name)
#     #        plaintext = dec_service.decrypt_content(content_bytes, pqc_config, key_material)
#     #        log.info("Successfully decrypted with PQC: %s", file_path)
#     #        return plaintext
#     #    except DecryptionError as e:
#     #        log.error("PQC Decryption failed for %s: %s", file_path, e)
#     #        if not pqc_config.fallback_to_classical_gpg:
#     #            raise
#     #        log.info("Falling back to classical GPG for %s", file_path)
#     #    except Exception as e: # Catch other PQC lib errors
#     #        log.error("Unexpected PQC error for %s: %s", file_path, e)
#     #        if not pqc_config.fallback_to_classical_gpg:
#     #            raise
#     #        log.info("Falling back to classical GPG for %s", file_path)
#
#     # 3. If PQC not enabled, or fallback is true:
#     #    try:
#     #        classical_dec_service = get_crypto_service_locator().get_decryption_service("classical_gpg") # or direct call
#     #        plaintext = classical_dec_service.decrypt_content(content_bytes, self.encryption_key) # Assuming content_bytes is what GPG needs
#     #        log.info("Successfully decrypted with classical GPG: %s", file_path)
#     #        return plaintext
#     #    except DecryptionError as e:
#     #        log.error("Classical GPG decryption failed for %s: %s", file_path, e)
#     #        raise
#
#     # 4. If all attempts fail or no encryption was assumed/configured but content is not Beancount
#     #    This logic path needs to be robust. If it's not encrypted, it should just be returned as is (if bytes, decode).
#     #    The current Fava/Beancount loader handles this; the PQC layer is an addition.
#     #    If no encryption method is configured/detected, and it's not plaintext, then it's an error.
#
#     # This stub assumes `content_bytes` is read before calling.
#     # The actual integration point is within `load_uncached` or how `FavaLedger` calls it.
#     # It might involve passing a decryptor function to `beancount.loader.load_file` if Beancount allows,
#     # or decrypting the byte stream before passing it as a string to `beancount.loader.load_string`.

# TEST: test_fava_ledger_loads_pqc_encrypted_file_successfully()
#   SETUP: Fava configured for PQC_KEM_X. Test file encrypted with PQC_KEM_X. Valid key provided.
#   ACTION: FavaLedger.load_file(pqc_encrypted_file_path)
#   ASSERT: Ledger loads, no errors. Data query on ledger returns expected results.
#           Log contains "Successfully decrypted with PQC".

# TEST: test_fava_ledger_falls_back_to_gpg_if_pqc_fails_and_fallback_enabled()
#   SETUP: Fava configured for PQC_KEM_X, fallback enabled. Test file encrypted with GPG.
#          Provide a dummy/wrong PQC key, but valid GPG key in agent.
#   ACTION: FavaLedger.load_file(gpg_encrypted_file_path)
#   ASSERT: Ledger loads, no errors. Data query returns expected results.
#           Log contains "PQC Decryption failed" AND "Falling back to classical GPG" AND "Successfully decrypted with classical GPG".

# TEST: test_fava_ledger_fails_if_pqc_fails_and_fallback_disabled()
#   SETUP: Fava configured for PQC_KEM_X, fallback disabled. Test file encrypted with GPG (or PQC with wrong key).
#   ACTION: FavaLedger.load_file(encrypted_file_path)
#   ASSERT: Ledger loading fails. Appropriate error raised/logged.
#           Log contains "PQC Decryption failed". No fallback message.
```

## 11. Dependencies

*   **External Libraries:**
    *   `oqs-python` (or similar Python PQC library) for PQC algorithm implementations (e.g., Kyber).
    *   Standard Python cryptography libraries for symmetric ciphers (e.g., `cryptography` for AES-GCM).
*   **Internal Fava Modules:**
    *   `fava.core.FavaLedger`: Needs modification to integrate the decryption logic.
    *   `fava.core.FavaOptions`: To store and provide PQC configurations.
    *   `fava.beans.load`: Current GPG decryption path; PQC path will be an alternative or precursor.
    *   New `fava.crypto_service` (or similar module) for abstraction.
*   **External Tools (User Workflow):**
    *   A PQC-capable GPG (if relying on GPG for hybrid mode and key management).
    *   Command-line tools or scripts for users to encrypt their Beancount files with the chosen PQC hybrid scheme if Fava doesn't provide encryption.

## 12. Integration Points

*   **IP12.1 (FavaLedger File Loading):** The primary integration point. When `FavaLedger` loads a Beancount file, it must invoke the new PQC decryption logic (via `CryptoService`) if the file is determined to be PQC encrypted or if PQC decryption is configured. This happens before passing data to `beancount.loader`.
*   **IP12.2 (Fava Configuration):** Fava's configuration loading mechanism must parse and provide PQC-specific settings to the `FavaLedger` and `CryptoService`.
*   **IP12.3 (Error Handling & Logging):** Fava's existing error reporting and logging systems need to incorporate messages specific to PQC decryption successes and failures.
*   **IP12.4 (CryptoService):** This new service will be the central point for all PQC (and potentially classical) cryptographic operations for data at rest, ensuring a clean separation of concerns. It will be called by `FavaLedger`.
*   **IP12.5 (Beancount Loader):**
    *   If Fava decrypts *before* Beancount: Fava passes a plaintext string or stream to `beancount.loader.load_string` or `load_file_contents`.
    *   If Beancount/GPG handles PQC: Fava continues to pass the encrypted file path and key information to `beancount.loader.load_file` as it does now, assuming Beancount's GPG interaction becomes PQC-aware. (The plan favors Fava-side abstraction).