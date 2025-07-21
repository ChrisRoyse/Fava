# Fava PQC Crypto Settings Configuration
# This file defines the cryptographic algorithms and settings for Fava PQC features

CONFIG = {
    "version": 1,
    "data_at_rest": {
        "active_encryption_suite_id": "HYBRID_KYBER768_AES256",
        "decryption_attempt_order": ["HYBRID_KYBER768_AES256"],
        "suites": {
            "HYBRID_KYBER768_AES256": {
                "type": "FAVA_HYBRID_PQC",
                "description": "Hybrid: X25519 + Kyber-768 KEM with AES-256-GCM",
                "classical_kem_algorithm": "X25519",
                "pqc_kem_algorithm": "Kyber768",
                "symmetric_algorithm": "AES256GCM",
                "kdf_algorithm_for_hybrid_sk": "HKDF-SHA256",
                "format_identifier": "FAVA_PQC_HYBRID_V1"
            }
        }
    },
    "hashing": {
        "default_algorithm": "SHA3-256",
        "integrity_check_algorithm": "HMAC-SHA3-256"
    },
    "key_management": {
        "default_mode": "PASSPHRASE_DERIVED",
        "passphrase_pbkdf": "Argon2id",
        "key_derivation": "HKDF-SHA3-512"
    },
    "wasm_module_integrity": {
        "verification_enabled": True,
        "signature_algorithm": "Dilithium3",
        "module_path": "/static/tree-sitter-beancount.wasm",
        "signature_path_suffix": ".dilithium3.sig",
        # Dynamic key management configuration
        "key_source": "environment",  # Options: environment, file, vault, hsm
        "public_key_env_var": "FAVA_PQC_PUBLIC_KEY",
        "private_key_env_var": "FAVA_PQC_PRIVATE_KEY",
        "key_file_path": "/etc/fava/keys/",
        "key_rotation_enabled": True,
        "key_rotation_interval_days": 90
    }
} 