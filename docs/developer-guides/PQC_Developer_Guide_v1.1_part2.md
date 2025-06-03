# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 2

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 2 of the PQC Developer Guide. Part 1 can be found [here](PQC_Developer_Guide_v1.1_part1.md).

## 4. Data at Rest (Fava-Driven Encryption)

Fava implements its own PQC hybrid encryption scheme for protecting Beancount files at rest. This section details its technical aspects and integration.

### 4.1. Hybrid Encryption Scheme

*   **Algorithms Used:**
    *   **Classical Key Encapsulation Mechanism (KEM):** X25519.
    *   **Post-Quantum KEM:** ML-KEM-768 (Kyber-768, NIST Level 3).
    *   **Symmetric Cipher:** AES-256-GCM (Authenticated Encryption with Associated Data).
    *   **Password-Based Key Derivation Function (PBKDF):** Argon2id (for passphrase stretching).
    *   **Key Derivation Function (KDF):** HKDF-SHA3-512 (for deriving KEM keys from PBKDF output and for deriving the symmetric key from KEM shared secrets).

*   **Encryption Process Overview:**
    1.  **Key Material Acquisition:**
        *   If passphrase-derived: Generate a unique Argon2id salt. Stretch passphrase with Argon2id and salt to get an Intermediate Keying Material (IKM). Use HKDF-SHA3-512 with IKM to derive X25519 & Kyber-768 key pairs.
        *   If external keys: Load recipient's X25519 & Kyber-768 public keys.
    2.  **Symmetric Key Derivation:**
        *   Generate ephemeral X25519 key pair. Derive shared secret (SS1) with recipient's X25519 public key.
        *   Encapsulate a shared secret (SS2) using recipient's Kyber-768 public key, yielding PQC ciphertext (CT_PQC).
        *   Concatenate `SS1 || SS2` to form `CombinedSecret`.
        *   Derive final AES-256-GCM key (`SymKey_AES`) from `CombinedSecret` using HKDF-SHA3-512 (optionally with a KDF salt).
    3.  **Symmetric Encryption:**
        *   Generate fresh AES-256-GCM IV/nonce.
        *   Encrypt Beancount data with `SymKey_AES` and IV, yielding Ciphertext_File and AuthTag_File.
    4.  **Bundle Creation:** Assemble `EncryptedFileBundle` with: `format_identifier`, `suite_id_used`, X25519 ephemeral public key, CT_PQC, AES IV/nonce, AuthTag_File, Argon2id salt (if used), KDF salt (if used), and Ciphertext_File.

*   **Decryption Process Overview:**
    1.  **Parse Bundle:** Deserialize `EncryptedFileBundle`. Retrieve PBKDF salt.
    2.  **Key Material Acquisition:**
        *   If passphrase-derived: Use passphrase and bundle's Argon2id salt with Argon2id to get IKM. Use HKDF-SHA3-512 with IKM to re-derive X25519 & Kyber-768 private keys.
        *   If external keys: Load recipient's X25519 & Kyber-768 private keys.
    3.  **Symmetric Key Derivation:**
        *   Re-derive SS1 using recipient's X25519 private key and sender's X25519 ephemeral public key (from bundle).
        *   Decapsulate SS2 using recipient's Kyber-768 private key and CT_PQC (from bundle).
        *   Concatenate `SS1 || SS2` to form `CombinedSecret`.
        *   Re-derive `SymKey_AES` from `CombinedSecret` using HKDF-SHA3-512 (and KDF salt from bundle, if used).
    4.  **Symmetric Decryption:** Decrypt Ciphertext_File using `SymKey_AES`, AES IV/nonce, and AuthTag_File. Verify authenticity.

*   **Rationale:** Provides layered security (classical + PQC). Argon2id protects passphrases. AES-256-GCM offers strong authenticated encryption. HKDF-SHA3-512 is a robust KDF.
*   **References:** [`docs/specifications/PQC_Data_At_Rest_Spec.md`](../../docs/specifications/PQC_Data_At_Rest_Spec.md), [`docs/architecture/PQC_Data_At_Rest_Arch.md`](../../docs/architecture/PQC_Data_At_Rest_Arch.md).

---
End of Part 2. More content will follow in Part 3.