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
        "public_key_base64": "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",
        "module_path": "/static/tree-sitter-beancount.wasm",
        "signature_path_suffix": ".dilithium3.sig"
    }
} 