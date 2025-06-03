# PQC Integration Specification: Data at Rest

**Version:** 1.1
**Date:** 2025-06-02

**Revision History:**
*   **1.1 (2025-06-02):** Revised based on new research findings and Devil's Advocate critique. Key changes include:
    *   Incorporated specific algorithm choices (Kyber-768, AES-256-GCM for hybrid PQC).
    *   Updated performance NFRs with more concrete targets based on benchmark research.
    *   Expanded scope to include Fava-driven PQC encryption for new files, addressing critique on user experience.
    *   Refined data models for configuration and encrypted file metadata.
    *   Updated user stories, use cases, and TDD anchors to reflect Fava-driven encryption.
    *   Addressed external tooling dependencies and contingency plans.
    *   Removed "TBD" placeholders where possible.
*   **1.0 (2025-06-02):** Initial version.

## 1. Introduction

This document outlines the specifications for integrating Post-Quantum Cryptography (PQC) to protect Data at Rest within the Fava application, primarily focusing on encrypted Beancount files. It draws upon the overall PQC integration plan ([`docs/ProjectMasterPlan_PQC.md`](../../docs/ProjectMasterPlan_PQC.md)), comprehensive research findings ([`docs/research/`](../../docs/research/)), and the high-level test strategy ([`docs/research/PQC_High_Level_Test_Strategy.md`](../../docs/research/PQC_High_Level_Test_Strategy.md)).

The primary goal is to ensure that Beancount files, when encrypted, are protected against threats from both classical and quantum computers. This revision incorporates recent research on PQC algorithm performance, library maturity (e.g., `oqs-python`), hybrid scheme constructions, and addresses critiques regarding Fava's role in the encryption process.

## 2. Functional Requirements

*   **FR2.1:** The system MUST support decryption of Beancount files encrypted with a hybrid scheme combining a classical KEM (X25519), a NIST-selected PQC Key Encapsulation Mechanism (ML-KEM/Kyber-768), and a classical symmetric cipher (AES-256-GCM). The specific algorithms are configurable but default to this suite.
*   **FR2.2:** The system MUST support decryption of Beancount files encrypted using classical GPG (e.g., RSA, ECC based keys with AES), as per current Fava functionality, to maintain backward compatibility for existing user files.
*   **FR2.3:** The system MUST allow configuration of the active PQC KEM (e.g., `ML-KEM-768`), associated parameters (e.g., security level), the classical KEM component (e.g., `X25519`), and the symmetric encryption algorithm (e.g., `AES256GCM`) for PQC-protected files via Fava's options.
*   **FR2.4:** Fava's core logic (loading, parsing, querying) MUST operate correctly on data decrypted from PQC-hybrid-protected Beancount files, identical to how it operates on classically GPG-encrypted or unencrypted files.
*   **FR2.5:** The system MUST provide a mechanism for users to encrypt their Beancount files using the supported PQC hybrid scheme (X25519 + Kyber-768 + AES-256-GCM) directly within Fava or through a tightly integrated workflow.
    *   **FR2.5.1:** Fava SHOULD offer a user interface or command-line option to encrypt a specified Beancount file using the configured PQC hybrid scheme.
    *   **FR2.5.2:** This Fava-driven encryption process MUST securely manage or prompt for necessary key material (e.g., user passphrase for deriving keys, or paths to pre-generated PQC key files).
*   **FR2.6:** The system MUST clearly indicate to the user if a Beancount file is PQC-hybrid encrypted, classically GPG-encrypted, or unencrypted, if discernible from metadata or configuration.
*   **FR2.7:** The system MUST provide informative error messages if decryption fails due to incorrect keys, unsupported algorithms, or corrupted data for classical GPG, PQC-hybrid, and Fava-PQC-encrypted files.
*   **FR2.8:** If Fava manages PQC key generation or derivation (e.g., from a passphrase), it MUST use cryptographically sound methods (e.g., strong KDFs like HKDF with SHA3-512) to derive PQC KEM keys and symmetric keys.
*   **FR2.9:** The system MUST allow users to export their Fava-managed PQC private keys (or keying material) in a secure and documented format if they wish to use them with external tools or for backup.

## 3. Non-Functional Requirements

*   **NFR3.1 (Security):** The PQC implementation for data at rest MUST adhere to NIST standards (FIPS 203 for ML-KEM/Kyber) and IETF best practices for hybrid schemes (e.g., shared secret concatenation and KDF usage as per `pf_hybrid_pqc_schemes_g2_1_PART_1.md`). Key management practices (generation, storage, derivation) within Fava MUST be secure.
*   **NFR3.2 (Performance):**
    *   **Decryption:** Decryption of PQC-hybrid encrypted files (Kyber-768 + AES-256-GCM) SHOULD NOT introduce prohibitive overhead. Target: For a 1MB Beancount file, PQC hybrid decryption latency should be within 200-500ms on typical server hardware (e.g., modern x86-64 CPU), acknowledging Python overhead on C library calls (based on `pf_pqc_performance_benchmarks_g1_3_PART_1.md`). This is estimated to be within 100-200% of GPG RSA-4096 decryption time.
    *   **Encryption:** If Fava performs encryption, PQC hybrid encryption latency for a 1MB file should also be within a similar range (e.g., 200-600ms), considering key generation/derivation and encapsulation.
*   **NFR3.3 (Usability):**
    *   The process for encrypting and decrypting PQC-hybrid protected files using Fava MUST be as user-friendly as possible.
    *   Users should be clearly guided on how to manage PQC keys (if Fava-managed) or provide necessary key material.
    *   Error messages related to PQC operations must be clear and actionable.
*   **NFR3.4 (Reliability):** The PQC encryption/decryption process MUST be reliable and consistently process validly encrypted files.
*   **NFR3.5 (Interoperability):**
    *   If Fava defines its own PQC-hybrid encrypted file format, this format MUST be clearly documented to allow for potential external tool development.
    *   If Fava relies on or suggests external tools for key management or initial encryption (as a fallback), it MUST be compatible with their output formats, based on research into PQC CLI tools (`pf_pqc_cli_signing_tools_g4_3_PART_1.md`) and contingency plans (`pf_tooling_contingency_PART_1.md`).
*   **NFR3.6 (Maintainability):** The PQC encryption/decryption logic MUST be implemented in a modular way (e.g., via the proposed `CryptoService`) to facilitate updates and algorithm changes.
*   **NFR3.7 (Cryptographic Agility):** The system MUST allow switching between different PQC KEMs or hybrid configurations with minimal code changes, primarily through configuration updates. (See [`PQC_Cryptographic_Agility_Spec.md`](PQC_Cryptographic_Agility_Spec.md))

## 4. User Stories

*   **US4.1:** As a security-conscious user, I want to encrypt my new Beancount file using Fava with a quantum-resistant hybrid algorithm (X25519 + Kyber-768 + AES-256-GCM) so that my financial data remains confidential even against future quantum threats.
*   **US4.2:** As a Fava user, I want to open my PQC-hybrid-encrypted Beancount file in Fava seamlessly, just like I open my GPG-encrypted or unencrypted files.
*   **US4.3:** As a Fava user, if I try to open a PQC-hybrid-encrypted file with the wrong key/passphrase or if the file is corrupted, I want to receive a clear error message explaining the problem.
*   **US4.4:** As a Fava administrator, I want to configure Fava to use a specific PQC KEM (e.g., Kyber-1024 if available and configured) and symmetric cipher for encrypting/decrypting Beancount files.
*   **US4.5:** As a long-time Fava user, I want to continue using my existing GPG-encrypted Beancount files without any issues after Fava is updated with PQC support.
*   **US4.6:** As a Fava user encrypting a file with PQC, I want Fava to guide me through setting up or providing the necessary PQC key material (e.g., via a strong passphrase).
*   **US4.7:** As a Fava user, I want to be able to export my Fava-managed PQC private key if I need to decrypt my file outside of Fava.

## 5. Use Cases

### 5.1. Use Case: Load PQC-Hybrid Encrypted Beancount File (Happy Path)

*   **Actor:** Fava User
*   **Preconditions:**
    *   Fava is configured to support the `X25519_KYBER768_AES256GCM` hybrid suite.
    *   User possesses a Beancount file (`data.bc.pqc_hybrid`) encrypted with this suite.
    *   User has the correct PQC decryption key material (e.g., passphrase for Fava-managed key, or path to private key file) accessible to Fava.
*   **Main Flow:**
    1.  User instructs Fava to load `data.bc.pqc_hybrid`.
    2.  Fava identifies the file as potentially PQC-hybrid encrypted (based on configuration or file metadata).
    3.  Fava's `CryptoService` attempts decryption using the configured `X25519_KYBER768_AES256GCM` suite and the provided key material.
    4.  The classical KEM (X25519) and PQC KEM (Kyber-768) decapsulate parts of the shared secret.
    5.  These are combined (e.g., via KDF) to derive the AES-256-GCM symmetric key.
    6.  The symmetric key is used with AES-256-GCM to decrypt the file content.
    7.  Fava receives the plaintext Beancount data.
    8.  Fava loads, parses, and displays the Beancount data.
*   **Postconditions:**
    *   User can view and interact with their financial data in Fava.
    *   Fava logs successful PQC-hybrid decryption (e.g., `INFO: Successfully decrypted 'data.bc.pqc_hybrid' using PQC Hybrid Suite: [SuiteName]`).

### 5.2. Use Case: Encrypt New Beancount File with PQC-Hybrid using Fava

*   **Actor:** Fava User
*   **Preconditions:**
    *   Fava is configured with `X25519_KYBER768_AES256GCM` as the active encryption suite.
    *   User has an unencrypted Beancount file (`data.bc`).
*   **Main Flow:**
    1.  User initiates PQC encryption for `data.bc` via Fava's UI or CLI.
    2.  Fava prompts the user for key material (e.g., a new strong passphrase, or to select/generate a PQC key pair).
    3.  `CryptoService` generates/derives PQC KEM key pair (e.g., Kyber-768) and classical KEM key pair (e.g., X25519) if not already existing for this user/file context.
    4.  A fresh symmetric key (e.g., for AES-256-GCM) is generated.
    5.  The symmetric key is encapsulated using the hybrid KEM (X25519 + Kyber-768 public keys). This produces classical and PQC KEM ciphertexts.
    6.  The Beancount file content is encrypted using the symmetric key with AES-256-GCM.
    7.  Fava stores the encrypted content along with necessary metadata (e.g., KEM ciphertexts, IV/nonce, AEAD tag, algorithm identifiers) as `data.bc.pqc_hybrid_fava`.
    8.  Fava confirms successful encryption to the user.
*   **Postconditions:**
    *   `data.bc.pqc_hybrid_fava` is created, encrypted with the configured PQC hybrid suite.
    *   User is informed of the location of the encrypted file and any relevant key management advice.

### 5.3. Use Case: Attempt to Load PQC-Hybrid Encrypted File with Incorrect Key/Passphrase

*   **Actor:** Fava User
*   **Preconditions:**
    *   Same as 5.1, but the PQC decryption key material provided to Fava is incorrect for `data.bc.pqc_hybrid`.
*   **Main Flow:**
    1.  User instructs Fava to load `data.bc.pqc_hybrid`.
    2.  Fava attempts decryption (Steps 2-6 from 5.1).
    3.  The KEM decapsulation or symmetric decryption fails due to the incorrect key material.
    4.  Fava detects the decryption failure.
    5.  Fava displays an error message to the user (e.g., "Error: Failed to decrypt Beancount file. Incorrect key/passphrase or corrupted file.").
*   **Postconditions:**
    *   The Beancount file is not loaded.
    *   Fava remains operational.
    *   Fava logs the decryption failure.

### 5.4. Use Case: Load Classically GPG-Encrypted Beancount File (Backward Compatibility)

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

*   **EC6.1:** File is corrupted (PQC-hybrid encrypted): System should detect corruption (e.g., failed integrity check from AEAD cipher like AES-GCM) and report an error, not crash.
*   **EC6.2:** Configured PQC algorithm in Fava does not match the algorithm used to encrypt the file: System should report a specific error if metadata allows detection, otherwise decryption will fail.
*   **EC6.3:** PQC key file is missing, inaccessible, or passphrase for derived key is incorrect: System should report an error.
*   **EC6.4:** Symmetric cipher decryption fails after successful KEM decapsulation (e.g., wrong symmetric key derived, or file tampered post-KEM): Report specific error.
*   **EC6.5:** Extremely large Beancount file encrypted with PQC-hybrid: Monitor for excessive decryption/encryption time and potential timeouts. System should remain responsive.
*   **EC6.6:** PQC library (`oqs-python`) dependency is missing or fails to initialize: Fava should start with PQC features disabled and log a clear error, or fail to start if PQC is mandated by configuration for the target file.
*   **EC6.7:** Beancount file path contains unusual characters and is PQC-hybrid encrypted.
*   **EC6.8:** User attempts to save/modify a PQC-hybrid-encrypted file: If Fava has performed decryption, it SHOULD offer to re-encrypt with the same (or currently configured) PQC-hybrid scheme upon saving. Direct modification of the ciphertext is not possible.
*   **EC6.9:** Key generation/derivation failure during Fava-driven encryption: Report specific error to user.

## 7. Constraints

*   **C7.1:** Implementation will rely on `oqs-python` for PQC KEM primitives (Kyber) and the `cryptography` library for classical KEM (X25519) and symmetric ciphers (AES-256-GCM).
*   **C7.2:** The choice of PQC algorithms will be initially focused on ML-KEM/Kyber-768 (NIST Level 3) for the PQC component of the hybrid scheme.
*   **C7.3:** Fava's PQC key management for Fava-driven encryption will initially focus on:
    *   Derivation from user-provided passphrases using strong KDFs.
    *   Optionally, allowing users to provide paths to externally managed raw PQC key files.
    *   Secure storage of derived keys is critical and may involve OS keychain integration or other secure local storage if keys are persisted by Fava. This is a complex area requiring careful design.
*   **C7.4:** Performance of PQC operations must be acceptable on typical user hardware where Fava server runs. See NFR3.2.
*   **C7.5:** The Fava-side decryption and encryption abstraction (`CryptoService`) is preferred for agility and to manage the hybrid scheme logic directly.

## 8. Data Models

### 8.1. PQC Configuration Parameters (Conceptual)

Stored within Fava's options/configuration system:

*   `pqc_data_at_rest_enabled`: boolean (Enable/disable PQC encryption/decryption)
*   `pqc_data_at_rest_active_suite_id`: string (e.g., "FAVA_HYBRID_X25519_KYBER768_AES256GCM")
*   `pqc_data_at_rest_suites`: dictionary (Allows defining multiple suites)
    *   Example suite definition:
        ```json
        "FAVA_HYBRID_X25519_KYBER768_AES256GCM": {
            "description": "Fava Hybrid: X25519 + Kyber-768 KEM with AES-256-GCM",
            "classical_kem_algorithm": "X25519",
            "pqc_kem_algorithm": "ML-KEM-768", // NIST FIPS 203 name
            "symmetric_algorithm": "AES256GCM",
            "kdf_algorithm": "HKDF-SHA3-512" // For deriving symmetric key from hybrid KEM output
        }
        ```
*   `pqc_key_management_mode`: string (e.g., "PASSPHRASE_DERIVED", "EXTERNAL_KEY_FILE")
*   `pqc_key_source_detail`: string (e.g., path to key file if `EXTERNAL_KEY_FILE`, or salt/parameters if `PASSPHRASE_DERIVED` and persisted) - *Sensitive, handle with care.*
*   `pqc_fallback_to_classical_gpg`: boolean (Default: true for decryption attempts)

### 8.2. Encrypted File Metadata (Conceptual, for Fava-PQC-Hybrid Encrypted Files)

A wrapper format for Fava-PQC-Hybrid encrypted Beancount files might include:
*   `format_identifier`: string (e.g., "FAVA_PQC_HYBRID_V1")
*   `suite_id`: string (References the suite in Fava's config, e.g., "FAVA_HYBRID_X25519_KYBER768_AES256GCM")
*   `classical_kem_ephemeral_public_key`: bytes (If X25519 ECDH is used, the ephemeral public key of sender)
*   `pqc_kem_encapsulated_key`: bytes (Ciphertext from Kyber KEM operation)
*   `symmetric_cipher_iv_or_nonce`: bytes (For AES-GCM)
*   `encrypted_data_ciphertext`: bytes (The actual Beancount data, AES-GCM encrypted)
*   `authentication_tag`: bytes (From AES-GCM)
*   `kdf_salt`: bytes (If KDF used with passphrase or for deriving symmetric key from KEMs)

*This structure ensures all necessary components for decryption are stored with the file.*

## 9. UI/UX Flow Outlines

*   **UI9.1 (Configuration):**
    *   A section in Fava's settings/options UI to configure PQC for data at rest.
    *   Fields for enabling PQC, selecting `active_suite_id`, managing `pqc_key_management_mode`.
    *   If `PASSPHRASE_DERIVED`, UI for setting/changing passphrase securely.
    *   If `EXTERNAL_KEY_FILE`, UI for specifying key file paths.
    *   Clear explanations and warnings about security implications.
*   **UI9.2 (File Loading):**
    *   No significant UI change for successful loads.
    *   Error messages for failed PQC decryption displayed clearly.
    *   Possibly a status indicator (e.g., icon) if a file is PQC-hybrid encrypted.
*   **UI9.3 (File Encryption - New):**
    *   Option in file browser or editor to "Encrypt with PQC Hybrid".
    *   Modal/dialog to confirm, set/confirm passphrase if `PASSPHRASE_DERIVED`, or select key files.
    *   Progress indication for encryption.
    *   Confirmation of success and new file name/location.

## 10. Initial TDD Anchors or Pseudocode Stubs

### 10.1. `CryptoService` Decryption/Encryption Interface (Backend)

```python
# In fava.crypto_service (conceptual)

class DecryptionError(Exception): pass
class EncryptionError(Exception): pass

class AbstractCryptoHandler(ABC):
    @abstractmethod
    def can_handle(self, file_path: str, content_bytes: Optional[bytes], config: Dict) -> bool:
        """Checks if this handler can attempt decryption/encryption based on config/file type/metadata."""
        pass

    @abstractmethod
    def decrypt_content(self, encrypted_content_bundle: bytes, config: Dict, key_material: Any) -> str:
        """Decrypts content, returns plaintext string. Raises DecryptionError on failure."""
        pass

    @abstractmethod
    def encrypt_content(self, plaintext_content: str, config: Dict, key_material: Any) -> bytes:
        """Encrypts content, returns encrypted bundle bytes. Raises EncryptionError on failure."""
        pass

# TEST: test_hybrid_pqc_handler_encrypts_decrypts_successfully()
#   SETUP: Instantiate HybridPqcHandler with Kyber768+AES256GCM config and known key material (e.g., passphrase).
#          Plaintext Beancount data.
#   ACTION: Call encrypt_content() on plaintext.
#           Call decrypt_content() on the resulting ciphertext bundle.
#   ASSERT: Decrypted content matches original plaintext. No exceptions.

# TEST: test_hybrid_pqc_handler_decrypt_fails_for_wrong_key()
#   SETUP: Encrypt data with HybridPqcHandler and key_A.
#   ACTION: Attempt to decrypt with HybridPqcHandler using key_B (wrong key).
#   ASSERT: Raises DecryptionError.

# TEST: test_gpg_handler_decrypts_valid_gpg_file() (existing behavior wrapper)
#   SETUP: Use an existing GPG encrypted test file and key.
#   ACTION: Call decrypt_content() via GpgHandler.
#   ASSERT: Returns correct plaintext.

# TEST: test_crypto_service_locator_selects_pqc_handler_for_pqc_file()
#   SETUP: Configure Fava for PQC. Mock file to appear as PQC encrypted.
#   ACTION: Call crypto_service_locator.get_handler_for_file(file_path, content_peek, config).
#   ASSERT: Returns an instance of HybridPqcHandler.

# TEST: test_crypto_service_locator_selects_gpg_handler_for_gpg_file()
#   SETUP: Configure Fava for GPG. Mock file to appear as GPG encrypted.
#   ACTION: Call crypto_service_locator.get_handler_for_file(file_path, content_peek, config).
#   ASSERT: Returns an instance of GpgHandler.
```

### 10.2. `FavaLedger` Integration Stub (Backend) - Revised for Encryption

```python
# In fava.core.FavaLedger (conceptual modification for load_file and save_file)

# def _try_decrypt_content(self, file_path: str, content_bytes: bytes) -> str:
#     # ... (similar to original, but using AbstractCryptoHandler)
#     # handler = self.crypto_service_locator.get_handler_for_file(file_path, content_bytes_peek, self.fava_options.pqc_config)
#     # if handler:
#     #    key_material = self._get_key_material_for_handler(handler, file_path) # e.g. prompt passphrase
#     #    return handler.decrypt_content(content_bytes, self.fava_options.pqc_config_for_handler, key_material)
#     # ... fallback to GPG or direct load

# def save_file_pqc(self, file_path: str, content_str: str, original_file_path: Optional[str] = None):
#     # 1. Determine encryption parameters from self.fava_options.pqc_config
#     #    active_suite = self.fava_options.pqc_config["data_at_rest"]["active_suite_id"]
#     #    suite_config = self.fava_options.pqc_config["data_at_rest"]["suites"][active_suite]
#     #
#     # 2. Get appropriate PQC encryption handler
#     #    handler = self.crypto_service_locator.get_pqc_encrypt_handler(suite_config) # Simplified
#     #
#     # 3. Get key material (e.g., prompt for passphrase, load from Fava-managed store, or use provided key file path)
#     #    key_material = self._get_or_generate_key_material_for_encryption(suite_config)
#     #
#     # 4. Encrypt content
#     #    encrypted_bundle_bytes = handler.encrypt_content(content_str, suite_config, key_material)
#     #
#     # 5. Write encrypted_bundle_bytes to file_path
#     #    log.info("Successfully encrypted and saved to %s with PQC Hybrid Suite: %s", file_path, active_suite)


# TEST: test_fava_ledger_saves_and_reloads_pqc_encrypted_file()
#   SETUP: Fava configured for PQC_Hybrid_Suite_X. Plaintext data.
#   ACTION: Call FavaLedger.save_file_pqc("test.bc.pqc_fava", plaintext_data).
#           Call FavaLedger.load_file("test.bc.pqc_fava").
#   ASSERT: Ledger loads, no errors. Data query on ledger returns expected results.
#           Log contains "Successfully encrypted" and "Successfully decrypted with PQC".
```

## 11. Dependencies

*   **External Libraries:**
    *   `oqs-python` (for Kyber KEM from `liboqs`).
    *   `cryptography` (for X25519, AES-256-GCM, HKDF, SHA3).
*   **Internal Fava Modules:**
    *   `fava.core.FavaLedger`: Needs modification for encryption and refined decryption logic.
    *   `fava.core.FavaOptions`: To store and provide PQC configurations.
    *   `fava.beans.load`: Current GPG decryption path; PQC path will be an alternative or precursor.
    *   New `fava.crypto_service` (or similar module) for abstraction of crypto handlers.
*   **External Tools (User Workflow - Fallback/Alternative):**
    *   Classical GPG.
    *   Potentially, PQC command-line tools based on `liboqs` if users manage keys externally and Fava supports decrypting such formats (contingency).

## 12. Integration Points

*   **IP12.1 (FavaLedger File Loading & Saving):** Primary integration point. `FavaLedger` will use `CryptoService` for both decryption of existing files and encryption of new/modified files if PQC is active.
*   **IP12.2 (Fava Configuration):** Fava's configuration loading mechanism must parse and provide PQC-specific settings.
*   **IP12.3 (Error Handling & Logging):** Incorporate messages specific to PQC encryption/decryption.
*   **IP12.4 (CryptoService):** Central point for all PQC/classical cryptographic operations for data at rest.
*   **IP12.5 (UI/CLI for Encryption & Key Management):** New UI elements or CLI commands for initiating PQC encryption and managing associated key material (passphrases, key files).