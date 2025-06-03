# Security Review Report: PQC Data at Rest

**Date:** 2025-06-03
**Feature:** PQC Data at Rest
**Reviewed Files:**
*   [`src/fava/crypto/keys.py`](src/fava/crypto/keys.py)
*   [`src/fava/crypto/handlers.py`](src/fava/crypto/handlers.py)
*   [`src/fava/crypto/locator.py`](src/fava/crypto/locator.py)
*   [`src/fava/core/encrypted_file_bundle.py`](src/fava/core/encrypted_file_bundle.py)
*   Relevant PQC integration sections in [`src/fava/core/ledger.py`](src/fava/core/ledger.py)
**Referenced Documents:**
*   [`docs/specifications/PQC_Data_At_Rest_Spec.md`](docs/specifications/PQC_Data_At_Rest_Spec.md)
*   [`docs/pseudocode/PQC_Data_At_Rest_Pseudo.md`](docs/pseudocode/PQC_Data_At_Rest_Pseudo.md)
*   [`docs/architecture/PQC_Data_At_Rest_Arch.md`](docs/architecture/PQC_Data_At_Rest_Arch.md)
*   [`docs/ProjectMasterPlan_PQC.md`](docs/ProjectMasterPlan_PQC.md)

## 1. Executive Summary

A security review of the "PQC Data at Rest" feature implementation was conducted. The review focused on cryptographic operations, key management, data handling, and adherence to specified security requirements.

**Overall Findings:**
*   **Total Vulnerabilities/Weaknesses Identified:** 8
    *   **Critical:** 2
    *   **High:** 1
    *   **Medium:** 2
    *   **Low:** 1
    *   **Informational:** 2

**Critical and High Severity Issues Require Immediate Attention.** These vulnerabilities impact core security assumptions and functionality of the PQC data at rest feature.

## 2. Methodology

The review involved:
*   **Manual Static Application Security Testing (SAST):** Line-by-line review of the Python code in the specified files.
*   **Cryptographic Primitive Review:** Verification of the correct usage and configuration of ML-KEM (Kyber), X25519, AES-256-GCM, Argon2id, and HKDF.
*   **Key Management Review:** Assessment of key generation, derivation from passphrases, conceptual storage, and handling procedures.
*   **Data Handling Review:** Examination of how plaintext, ciphertext, passphrases, and keys are processed and protected.
*   **Adherence Check:** Comparison against security requirements in specification and architecture documents.
*   **Conceptual Software Composition Analysis (SCA):** Noting dependencies like `mlkem`, `cryptography`, `argon2-cffi` and assuming their general integrity for this review's scope.

## 3. Detailed Findings

### 3.1. Critical Vulnerabilities

**PQC-DAR-CRIT-001: Non-Deterministic PQC Key Generation from Passphrase**
*   **File:** [`src/fava/crypto/keys.py`](src/fava/crypto/keys.py)
*   **Approximate Line:** 291 (within `derive_kem_keys_from_passphrase` specifically the call to `MLKEMBridge.generate_keypair()`)
*   **Description:** The `derive_kem_keys_from_passphrase` function, intended to derive keys for PQC encryption based on a user's passphrase, currently generates a *new random* PQC key pair (`pk_kem_bytes`, `sk_kem_bytes`) each time it's called, even for the same passphrase and salt. The `mlkem.generate_keypair()` function is inherently random. The derived `master_key` from Argon2id is used for the DEM (AES-GCM) but not to deterministically derive or seed the PQC KEM key pair.
*   **Impact:** This makes passphrase-based PQC encryption non-functional for persistent data. Data encrypted with a key pair generated in one session cannot be decrypted in a subsequent session using the same passphrase because a different key pair will be generated. The core promise of deriving keys from a passphrase for persistent storage is broken for the PQC component.
*   **Recommendation:** Modify the PQC key derivation to be deterministic from the passphrase-derived `master_key` (or a further derived key from it). This likely involves:
    1.  Using the `master_key` (or a KDF-derived portion of it) as a seed for a deterministic PQC key generation function if the `mlkem` library supports it (e.g., `mlkem.keypair_from_seed(seed)` if available).
    2.  If direct seeding isn't supported, investigate if the library allows constructing keys from raw secret key bytes that could be deterministically derived from the `master_key`.
    3.  Ensure the chosen method is cryptographically sound and aligns with ML-KEM standards for deterministic key generation from a seed. The current `MLKEMBridge.keypair_from_secret()` is for loading *existing* raw secret keys, not generating them from a seed.

**PQC-DAR-CRIT-002: Insecure Placeholder for Secure Key Export Format**
*   **File:** [`src/fava/crypto/keys.py`](src/fava/crypto/keys.py)
*   **Approximate Line:** 415 (within `PQCKeyManager.export_fava_managed_keys`)
*   **Description:** The `secure_format_for_export` function, called by `export_fava_managed_keys`, is currently a placeholder (`return private_key_pem # Placeholder`). It does not implement any actual secure formatting or encryption for the exported private keys (X25519 or PQC secret keys). Exporting raw private key material without strong protection is highly insecure.
*   **Impact:** If this function is used as is, sensitive private keys would be exported in a trivially accessible format, completely undermining their security.
*   **Recommendation:** Implement a strong, standardized, and passphrase-protected format for exporting private keys. Consider:
    1.  **PKCS#8 with PBE:** Use a standard like PKCS#8 with a strong Password-Based Encryption scheme (e.g., PBES2 using AES-256 and a strong KDF like PBKDF2 or Argon2id) to encrypt the private key material. The `cryptography` library provides tools for this.
    2.  Clearly document the format and the parameters used (algorithms, iteration counts, etc.).
    3.  Ensure the passphrase for export is obtained securely and is sufficiently strong.

### 3.2. High Severity Vulnerabilities

**PQC-DAR-HIGH-001: Non-Functional PQC Private Key Loading in `MLKEMBridge`**
*   **File:** [`src/fava/crypto/keys.py`](src/fava/crypto/keys.py)
*   **Approximate Line:** 341 (within `MLKEMBridge.keypair_from_secret`)
*   **Description:** The `MLKEMBridge.keypair_from_secret` method is intended to load a PQC key pair from raw secret key bytes. However, the `mlkem` library's `KemKeypair.from_secret_key()` expects the *full* secret key which includes the public key and other components, not just the raw PQC secret key bytes (`sk_kem_bytes`). The current implementation passes only `sk_kem_bytes`.
*   **Impact:** This makes loading externally generated raw PQC secret keys (for `mlkem` KEMs) non-functional. If Fava intends to support importing such keys, this will fail.
*   **Recommendation:**
    1.  Clarify the expected format for "raw secret key bytes" for ML-KEM.
    2.  If the `mlkem` library requires the concatenated full secret key (which often includes `sk || pk || hash(pk) || z` or similar structure depending on the specific ML-KEM variant and library convention), the import function must expect this full structure or reconstruct it if only partial material is provided (though reconstructing is less ideal).
    3.  Alternatively, if the goal is to load from a seed (as discussed in PQC-DAR-CRIT-001), a different library function would be needed. The current function name `keypair_from_secret` implies loading an existing, fully formed secret key.

### 3.3. Medium Severity Vulnerabilities

**PQC-DAR-MED-001: Insufficient Salt Uniqueness/Management for KDFs**
*   **File:** [`src/fava/crypto/keys.py`](src/fava/crypto/keys.py) (e.g., lines 288, 186)
*   **Description:** While salts are used for Argon2id (`derive_key_from_passphrase`, `derive_aes_gcm_key_from_passphrase`) and HKDF (`derive_aes_gcm_key_from_master`), the generation, storage, and association of these salts with specific keys or encrypted data are not explicitly detailed. The `EncryptedFileBundle` stores a `kem_salt` and `dem_salt`, but their uniqueness per encryption or per key is crucial. Reusing salts, especially with KDFs like Argon2id for different purposes or across different keys derived from the same passphrase, can weaken security.
*   **Impact:** Potential weakening of key derivation security if salts are not unique per key or per use case as appropriate.
*   **Recommendation:**
    1.  Ensure salts for Argon2id are generated randomly and are unique for each distinct key being derived (e.g., unique salt per Fava-managed key if passphrases are reused).
    2.  Store salts alongside the ciphertext or key material they were used to derive. The `EncryptedFileBundle` seems to do this, but ensure these are always freshly generated for new encryptions.
    3.  For HKDF, the salt can be non-secret but should ideally be random. If deriving multiple keys from the same IKM using HKDF, ensure the `info` parameter is distinct for each derived key.

**PQC-DAR-MED-002: Potential for GPG Key ID Collision/Ambiguity**
*   **File:** [`src/fava/crypto/handlers.py`](src/fava/crypto/handlers.py) (within `GPGHandler`)
*   **Description:** The GPG handler uses key IDs (fingerprints or short IDs) for encryption. While full fingerprints are generally unique, if short key IDs are used or if users have multiple keys with similar-looking IDs, there's a potential for ambiguity or encrypting to the wrong key if not handled carefully by the underlying `gpg` library calls and Fava's selection logic.
*   **Impact:** Accidental encryption to an unintended GPG key if key ID management is not robust.
*   **Recommendation:**
    1.  Preferentially use full GPG key fingerprints for specifying recipients.
    2.  If short IDs are supported, ensure Fava's UI or configuration clearly warns about potential ambiguities and provides mechanisms for users to resolve them (e.g., by listing matching full fingerprints).
    3.  Ensure the `gpg` command-line calls are constructed to be specific and avoid ambiguity (e.g., using `!` suffix for exact fingerprint match if supported by the `gpg` version).

### 3.4. Low Severity Vulnerabilities

**PQC-DAR-LOW-001: Error Handling in Cryptographic Operations Could Be More Specific**
*   **File:** Various files within `src/fava/crypto/`
*   **Description:** While `try...except` blocks are used, some exceptions caught are generic (e.g., `Exception as e`). In cryptographic contexts, more specific exception handling can improve robustness and provide better diagnostics. For instance, distinguishing between a decryption failure due to a wrong key/passphrase versus a corrupted ciphertext.
*   **Impact:** Generic error messages might obscure the true nature of a cryptographic failure, making debugging harder for users and developers.
*   **Recommendation:** Catch more specific exceptions where possible (e.g., `cryptography.exceptions.InvalidTag` for AES-GCM MAC failure, specific errors from `mlkem` or `gpg`). Provide user-friendly error messages that guide the user without revealing excessive internal details.

### 3.5. Informational Findings

**PQC-DAR-INFO-001: Missing Explicit Zeroization of Sensitive Key Material**
*   **File:** Various files within `src/fava/crypto/`
*   **Description:** Sensitive intermediate key material (e.g., raw symmetric keys, PQC secret key bytes) held in memory is not explicitly zeroized after use. While Python's garbage collection will eventually reclaim memory, explicit zeroization is a defense-in-depth measure.
*   **Impact:** Theoretical risk of sensitive data persisting in memory longer than necessary, potentially accessible in memory dumps or via certain sophisticated attacks.
*   **Recommendation:** For highly sensitive variables holding key material, consider explicitly overwriting them with zeros or random data once they are no longer needed. Libraries like `cryptography` sometimes provide utilities or context managers for this. This is a best-practice hardening measure.

**PQC-DAR-INFO-002: Configuration of Argon2id Parameters**
*   **File:** [`src/fava/crypto/keys.py`](src/fava/crypto/keys.py) (e.g., line 181)
*   **Description:** Argon2id parameters (time_cost, memory_cost, parallelism) are hardcoded. While the chosen values (`time_cost=3`, `memory_cost=65536`, `parallelism=4`) are reasonable starting points, these may need adjustment based on typical user hardware or evolving security recommendations.
*   **Impact:** Suboptimal performance or security if default parameters are not suitable for all environments or over time.
*   **Recommendation:** Consider making Argon2id parameters configurable, perhaps with sensible defaults, as part of Fava's advanced settings. Document the implications of changing these parameters.

## 4. Self-Reflection on Review Process

*   **Comprehensiveness:** The review focused on the core cryptographic logic and key management aspects of the "PQC Data at Rest" feature. Areas like UI for passphrase entry or detailed file I/O interactions were considered out of scope for this specific cryptographic code review but are important for overall security. The security of the `mlkem`, `cryptography`, and `argon2-cffi` libraries themselves was assumed.
*   **Certainty of Findings:**
    *   Critical & High: High certainty. These point to direct contradictions with secure cryptographic principles or fundamental implementation flaws making features non-functional securely.
    *   Medium & Low: Moderate to high certainty. These represent areas where security could be improved or potential ambiguities exist.
*   **Limitations:**
    *   Static analysis only; no dynamic testing or fuzzing was performed.
    *   Interaction with the actual `oqs-python` (if `mlkem` is a wrapper) or direct `liboqs` behavior was inferred from the `mlkem` library's apparent API.
    *   The review assumed the provided code snippets and file paths were representative of the final implemented logic for the core crypto operations.
    *   Some security-critical components, like secure passphrase prompting and handling in the UI, are currently mocked or not fully implemented, and will require their own dedicated security reviews once finalized.
*   **Quantitative Summary:** 2 Critical, 1 High, 2 Medium, 1 Low, 2 Informational.

## 5. Conclusion & Next Steps

The "PQC Data at Rest" feature, in its current state as reviewed, contains critical and high-severity vulnerabilities that **must be addressed before it can be considered secure or functionally correct for passphrase-based PQC encryption and secure key export.** Remediation of PQC-DAR-CRIT-001, PQC-DAR-CRIT-002, and PQC-DAR-HIGH-001 should be prioritized.

It is recommended that the development team:
1.  Address all Critical and High vulnerabilities.
2.  Consider and address Medium severity vulnerabilities.
3.  Review and implement Low/Informational recommendations as appropriate for hardening.
4.  Conduct further testing, including negative test cases and integration testing, after fixes are applied.
5.  Ensure that UI components for passphrase handling are also reviewed for security once implemented.