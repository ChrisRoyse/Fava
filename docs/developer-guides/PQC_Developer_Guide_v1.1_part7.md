# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 7

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 7 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   Part 2: [PQC_Developer_Guide_v1.1_part2.md](PQC_Developer_Guide_v1.1_part2.md)
*   Part 3: [PQC_Developer_Guide_v1.1_part3.md](PQC_Developer_Guide_v1.1_part3.md)
*   Part 4: [PQC_Developer_Guide_v1.1_part4.md](PQC_Developer_Guide_v1.1_part4.md)
*   Part 5: [PQC_Developer_Guide_v1.1_part5.md](PQC_Developer_Guide_v1.1_part5.md)
*   Part 6: [PQC_Developer_Guide_v1.1_part6.md](PQC_Developer_Guide_v1.1_part6.md)

This part details Fava's Cryptographic Agility Framework, starting with the central configuration.

## 8. Cryptographic Agility Framework

Cryptographic agility is a core design principle in Fava's PQC integration, enabling the system to adapt to new cryptographic standards and algorithms with minimal code changes, primarily through configuration.

### 8.1. `FAVA_CRYPTO_SETTINGS` Structure and Usage

*   **Central Configuration:** A comprehensive configuration structure, notionally named `FAVA_CRYPTO_SETTINGS`, is the heart of the agility framework. This is typically loaded from Fava's main options file (e.g., part of `fava_options.py` or a dedicated `crypto_config.py`).
*   **Key Sections within `FAVA_CRYPTO_SETTINGS` (Illustrative Structure):**
    ```python
    FAVA_CRYPTO_SETTINGS = {
        "data_at_rest": {
            "pqc_decryption_enabled": True,
            "pqc_encryption_enabled": True,
            "active_encryption_suite_id": "HYBRID_X25519_MLKEM768_AES256GCM",
            "decryption_attempt_order": [
                "HYBRID_X25519_MLKEM768_AES256GCM",
                "CLASSICAL_GPG"
            ],
            "suites": {
                "HYBRID_X25519_MLKEM768_AES256GCM": {
                    "description": "Hybrid: X25519 + ML-KEM-768 with AES-256-GCM",
                    "type": "FAVA_HYBRID_PQC",
                    "classical_kem_algorithm": "X25519",
                    "pqc_kem_algorithm": "ML-KEM-768",
                    "symmetric_algorithm": "AES256GCM",
                    "kdf_algorithm_for_hybrid_sk": "HKDF-SHA3-512",
                    "pbkdf_algorithm_for_passphrase": "Argon2id",
                    "kdf_algorithm_for_passphrase_ikm": "HKDF-SHA3-512",
                    "key_management_mode": "PASSPHRASE_DERIVED",
                },
                "CLASSICAL_GPG": {
                    "description": "Classical GPG Decryption",
                    "type": "CLASSICAL_GPG",
                }
                # Add other suites here, e.g., for ML-KEM-1024
            },
            # "passphrase_kdf_salt_global": "some_fava_global_salt..." # Example
        },
        "hashing": {
            "default_algorithm": "SHA3-256" # Options: "SHA3-256", "SHA256"
        },
        "wasm_integrity": {
            "verification_enabled": True,
            "public_key_dilithium3_base64": "YOUR_DILITHIUM3_PUBLIC_KEY_BASE64",
            "signature_algorithm": "Dilithium3"
        },
        "pqc_library_config": {
            # "oqs_python_lib_path": None, # Optional override
        }
    }
    ```
*   **Loading and Validation:**
    *   A `GlobalConfig` module (conceptual path: `src/fava/pqc/global_config.py`) is responsible for loading this structure, validating its schema against expected types and values, caching it, and providing access to other modules.
    *   Robust validation at Fava's startup is crucial to prevent issues arising from misconfigurations. Errors in this configuration should be clearly logged, and Fava might refuse to start or operate with PQC features disabled if critical settings are invalid.

---
End of Part 7. More content will follow in Part 8.