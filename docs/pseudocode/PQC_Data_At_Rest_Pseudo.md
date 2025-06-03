# Pseudocode: PQC Data at Rest Module

**Version:** 1.0
**Date:** 2025-06-02
**Based on Specification:** [`docs/specifications/PQC_Data_At_Rest_Spec.md`](docs/specifications/PQC_Data_At_Rest_Spec.md) (v1.1)

## 1. Overview

This document provides language-agnostic pseudocode for integrating Post-Quantum Cryptography (PQC) for data at rest within the Fava application. It covers encryption and decryption of Beancount files using a hybrid PQC scheme, classical GPG, key management, and error handling.

## 2. Global Configuration Constants (Conceptual - from Fava Options)

CONSTANT `CONFIG_PQC_DATA_AT_REST_ENABLED`: BOOLEAN
CONSTANT `CONFIG_PQC_ACTIVE_SUITE_ID`: STRING
CONSTANT `CONFIG_PQC_SUITES`: MAP<STRING, PQCSuiteDefinition>
CONSTANT `CONFIG_PQC_KEY_MANAGEMENT_MODE`: STRING ("PASSPHRASE_DERIVED", "EXTERNAL_KEY_FILE")
CONSTANT `CONFIG_PQC_KEY_SOURCE_DETAIL`: STRING (e.g., salt, key file path)
CONSTANT `CONFIG_PQC_FALLBACK_TO_GPG`: BOOLEAN

STRUCTURE `PQCSuiteDefinition`:
    `description`: STRING
    `classical_kem_algorithm`: STRING (e.g., "X25519")
    `pqc_kem_algorithm`: STRING (e.g., "ML-KEM-768")
    `symmetric_algorithm`: STRING (e.g., "AES256GCM")
    `kdf_algorithm_for_hybrid_sk`: STRING (e.g., "HKDF-SHA3-512", for deriving symmetric key from KEM outputs)
    `kdf_algorithm_for_passphrase`: STRING (e.g., "HKDF-SHA3-512", for deriving KEM keys from passphrase)

## 3. Data Structures

STRUCTURE `EncryptedFileBundle` (for Fava-PQC-Hybrid Encrypted Files):
    `format_identifier`: STRING (e.g., "FAVA_PQC_HYBRID_V1")
    `suite_id`: STRING (references key in `CONFIG_PQC_SUITES`)
    `classical_kem_ephemeral_public_key`: BYTES (OPTIONAL, e.g., for ECDH-like KEMs)
    `pqc_kem_encapsulated_key`: BYTES (Ciphertext from PQC KEM operation)
    `symmetric_cipher_iv_or_nonce`: BYTES
    `encrypted_data_ciphertext`: BYTES
    `authentication_tag`: BYTES (e.g., from AES-GCM)
    `kdf_salt_for_passphrase_derived_keys`: BYTES (OPTIONAL, used if KEM keys were derived from passphrase)
    `kdf_salt_for_hybrid_sk_derivation`: BYTES (OPTIONAL, if KDF for symmetric key from KEMs uses a salt)

## 4. Error Types

EXCEPTION `DecryptionError` (inherits Exception)
EXCEPTION `EncryptionError` (inherits Exception)
EXCEPTION `ConfigurationError` (inherits Exception)
EXCEPTION `MissingDependencyError` (inherits Exception)
EXCEPTION `KeyManagementError` (inherits Exception)

## 5. Key Management Functions

FUNCTION `derive_kem_keys_from_passphrase(passphrase, salt, kdf_algorithm, classical_kem_spec, pqc_kem_spec)`:
    INPUT: `passphrase` (STRING), `salt` (BYTES), `kdf_algorithm` (STRING), `classical_kem_spec` (STRING), `pqc_kem_spec` (STRING)
    OUTPUT: TUPLE (`classical_key_pair`, `pqc_key_pair`) OR RAISE `KeyManagementError`
    // Derives classical and PQC KEM key pairs using a KDF from the passphrase and salt.
    // TEST: `test_key_derivation_from_passphrase_produces_valid_key_pairs_for_specified_algorithms()`
    // TEST: `test_key_derivation_from_passphrase_uses_salt_correctly()`
    // TEST: `test_key_derivation_fails_gracefully_for_unsupported_kdf_or_kem_spec()`
    LOG "Deriving KEM keys from passphrase using KDF: " + `kdf_algorithm`
    `derived_key_material` = KDF(`passphrase`, `salt`, `kdf_algorithm`, required_length_for_both_key_pairs)
    `classical_key_pair` = EXTRACT_AND_GENERATE_CLASSICAL_KEM_KEYS_FROM (`derived_key_material`, `classical_kem_spec`)
    `pqc_key_pair` = EXTRACT_AND_GENERATE_PQC_KEM_KEYS_FROM (`derived_key_material`, `pqc_kem_spec`)
    RETURN (`classical_key_pair`, `pqc_key_pair`)
    CATCH any crypto library error: RAISE `KeyManagementError`("Failed to derive keys from passphrase")

FUNCTION `load_keys_from_external_file(key_file_path_config)`:
    INPUT: `key_file_path_config` (STRING or MAP detailing paths for classical/PQC keys)
    OUTPUT: TUPLE (`classical_key_pair`, `pqc_key_pair`) OR RAISE `KeyManagementError`
    // Loads classical and PQC KEM key pairs from specified file(s).
    // TEST: `test_external_key_file_loading_parses_keys_correctly_for_supported_formats()`
    // TEST: `test_external_key_file_loading_fails_if_key_file_missing_or_invalid_format()`
    LOG "Loading KEM keys from external file(s): " + `key_file_path_config`
    // Actual parsing logic depends on key file format
    `classical_key_pair` = LOAD_CLASSICAL_KEYS_FROM_FILE(`key_file_path_config`)
    `pqc_key_pair` = LOAD_PQC_KEYS_FROM_FILE(`key_file_path_config`)
    RETURN (`classical_key_pair`, `pqc_key_pair`)
    CATCH file I/O error or parsing error: RAISE `KeyManagementError`("Failed to load keys from file")

FUNCTION `export_fava_managed_pqc_private_keys(key_context, export_format)`:
    INPUT: `key_context` (identifies which keys), `export_format` (STRING)
    OUTPUT: FORMATTED_KEY_DATA (BYTES or STRING) OR RAISE `KeyManagementError`
    // FR2.9: Allows users to export their Fava-managed PQC private keys.
    // This implies Fava stores or can re-derive these keys.
    // TEST: `test_key_export_retrieves_correct_fava_managed_keys_for_context()`
    // TEST: `test_key_export_formats_keys_correctly_for_documented_export_format()`
    // TEST: `test_key_export_fails_if_keys_not_found_for_context()`
    LOG "Exporting Fava-managed PQC private keys for context: " + `key_context`
    `pqc_private_key` = RETRIEVE_STORED_OR_DERIVED_PQC_PRIVATE_KEY(`key_context`)
    IF `pqc_private_key` IS NULL: RAISE `KeyManagementError`("PQC private key not found for export")
    `formatted_data` = FORMAT_KEY_FOR_EXPORT(`pqc_private_key`, `export_format`)
    RETURN `formatted_data`

## 6. Crypto Handlers

INTERFACE `AbstractCryptoHandler`:
    METHOD `can_handle(file_path: STRING, content_bytes_peek: BYTES_OR_NULL, config: MAP) -> BOOLEAN`
    METHOD `decrypt_content(encrypted_content_bundle: BYTES, suite_config: MAP, key_material: ANY) -> STRING`
        // RAISES `DecryptionError`, `MissingDependencyError`
    METHOD `encrypt_content(plaintext_content: STRING, suite_config: MAP, key_material: ANY) -> BYTES`
        // RAISES `EncryptionError`, `MissingDependencyError`

CLASS `HybridPqcHandler` IMPLEMENTS `AbstractCryptoHandler`:
    METHOD `can_handle(file_path, content_bytes_peek, config)`:
        // Checks if file extension suggests PQC (e.g., ".pqc_hybrid_fava")
        // OR if `content_bytes_peek` matches `EncryptedFileBundle.format_identifier`
        // OR if `config` explicitly mandates PQC handling for this path.
        // TEST: `test_hybrid_pqc_handler_can_handle_by_extension()`
        // TEST: `test_hybrid_pqc_handler_can_handle_by_magic_bytes()`
        // TEST: `test_hybrid_pqc_handler_cannot_handle_unrelated_file()`
        RETURN TRUE IF determined to be PQC hybrid, ELSE FALSE

    METHOD `encrypt_content(plaintext_content, suite_config, key_material)`:
        // `key_material` contains PQC public keys (classical & PQC)
        // TEST: `test_hybrid_pqc_handler_encrypts_decrypts_successfully()` (from spec)
        // TEST: `test_hybrid_pqc_handler_encrypt_uses_correct_algorithms_from_suite_config()`
        LOG "Encrypting content with Hybrid PQC suite: " + `suite_config.description`
        TRY
            `classical_kem_alg = suite_config.classical_kem_algorithm`
            `pqc_kem_alg = suite_config.pqc_kem_algorithm`
            `symmetric_alg = suite_config.symmetric_algorithm`
            `kdf_for_hybrid_sk_alg = suite_config.kdf_algorithm_for_hybrid_sk`

            // 1. Obtain KEM public keys from `key_material`
            `classical_recipient_pk = key_material.classical_public_key`
            `pqc_recipient_pk = key_material.pqc_public_key`

            // 2. Classical KEM operation (e.g., X25519)
            `classical_ephemeral_sk, classical_ephemeral_pk` = GENERATE_KEM_KEY_PAIR(`classical_kem_alg`)
            `classical_shared_secret_part` = KEM_ENCAPSULATE(`classical_kem_alg`, `classical_recipient_pk`, `classical_ephemeral_sk`) // Or perform DH

            // 3. PQC KEM operation (e.g., ML-KEM-768)
            `pqc_encapsulated_key, pqc_shared_secret_part` = KEM_ENCAPSULATE(`pqc_kem_alg`, `pqc_recipient_pk`)
            // TEST: `test_pqc_kem_encapsulation_produces_valid_ciphertext_and_shared_secret()`

            // 4. Combine shared secrets and derive symmetric key using KDF
            `combined_kem_secrets` = CONCATENATE(`classical_shared_secret_part`, `pqc_shared_secret_part`)
            `kdf_salt_for_hybrid_sk` = GENERATE_RANDOM_BYTES() // If KDF uses a salt for this step
            `derived_symmetric_key` = KDF(`combined_kem_secrets`, `kdf_salt_for_hybrid_sk`, `kdf_for_hybrid_sk_alg`, required_length_for_`symmetric_alg`)
            // TEST: `test_hybrid_kem_derives_consistent_symmetric_key_using_kdf()`

            // 5. Symmetric encryption (e.g., AES-256-GCM)
            `iv_or_nonce` = GENERATE_IV_FOR_SYMMETRIC_CIPHER(`symmetric_alg`)
            `encrypted_data, auth_tag` = SYMMETRIC_ENCRYPT(`plaintext_content`, `derived_symmetric_key`, `iv_or_nonce`, `symmetric_alg`)
            // TEST: `test_aes_gcm_encryption_produces_valid_tag_and_iv()` (from spec idea)

            // 6. Construct EncryptedFileBundle
            `bundle` = NEW `EncryptedFileBundle`
            `bundle.format_identifier` = "FAVA_PQC_HYBRID_V1"
            `bundle.suite_id` = `suite_config.id` // Assuming suite_config has an id
            `bundle.classical_kem_ephemeral_public_key` = `classical_ephemeral_pk`
            `bundle.pqc_kem_encapsulated_key` = `pqc_encapsulated_key`
            `bundle.symmetric_cipher_iv_or_nonce` = `iv_or_nonce`
            `bundle.encrypted_data_ciphertext` = `encrypted_data`
            `bundle.authentication_tag` = `auth_tag`
            `bundle.kdf_salt_for_passphrase_derived_keys` = `key_material.passphrase_salt` IF `key_material` from passphrase
            `bundle.kdf_salt_for_hybrid_sk_derivation` = `kdf_salt_for_hybrid_sk`

            RETURN SERIALIZE_TO_BYTES(`bundle`)
        CATCH crypto library error as e:
            RAISE `EncryptionError`("Hybrid PQC encryption failed: " + e.message)
        CATCH missing library error:
            RAISE `MissingDependencyError`("Required PQC/crypto library not found for encryption")

    METHOD `decrypt_content(encrypted_content_bundle_bytes, suite_config, key_material)`:
        // `key_material` contains PQC private keys (classical & PQC)
        // TEST: `test_hybrid_pqc_handler_decrypt_fails_for_wrong_key()` (from spec)
        // TEST: `test_hybrid_pqc_handler_decrypt_fails_on_tampered_ciphertext_or_tag()` (EC6.1, EC6.4)
        // TEST: `test_hybrid_pqc_handler_decrypt_fails_for_corrupted_kem_ciphertext()`
        LOG "Decrypting content with Hybrid PQC suite: " + `suite_config.description`
        TRY
            `bundle` = PARSE_ENCRYPTED_FILE_BUNDLE_FROM_BYTES(`encrypted_content_bundle_bytes`)
            // TEST: `test_encrypted_bundle_parser_extracts_all_fields_correctly()`

            IF `bundle.format_identifier` IS NOT "FAVA_PQC_HYBRID_V1" OR `bundle.suite_id` IS NOT `suite_config.id`:
                RAISE `DecryptionError`("Unsupported file format or suite mismatch.")
                // TEST: `test_decrypt_fails_for_mismatched_suite_id_or_format_identifier()`

            `classical_kem_alg = suite_config.classical_kem_algorithm`
            `pqc_kem_alg = suite_config.pqc_kem_algorithm`
            `symmetric_alg = suite_config.symmetric_algorithm`
            `kdf_for_hybrid_sk_alg = suite_config.kdf_algorithm_for_hybrid_sk`

            // 1. Obtain KEM private keys from `key_material`
            `classical_recipient_sk = key_material.classical_private_key`
            `pqc_recipient_sk = key_material.pqc_private_key`

            // 2. Classical KEM decapsulation
            `classical_shared_secret_part` = KEM_DECAPSULATE(`classical_kem_alg`, `bundle.classical_kem_ephemeral_public_key`, `classical_recipient_sk`)

            // 3. PQC KEM decapsulation
            `pqc_shared_secret_part` = KEM_DECAPSULATE(`pqc_kem_alg`, `bundle.pqc_kem_encapsulated_key`, `pqc_recipient_sk`)
            // TEST: `test_pqc_kem_decapsulation_yields_correct_shared_secret()`

            // 4. Combine shared secrets and derive symmetric key using KDF
            `combined_kem_secrets` = CONCATENATE(`classical_shared_secret_part`, `pqc_shared_secret_part`)
            `derived_symmetric_key` = KDF(`combined_kem_secrets`, `bundle.kdf_salt_for_hybrid_sk_derivation`, `kdf_for_hybrid_sk_alg`, required_length_for_`symmetric_alg`)

            // 5. Symmetric decryption
            `plaintext_bytes` = SYMMETRIC_DECRYPT(`bundle.encrypted_data_ciphertext`, `derived_symmetric_key`, `bundle.symmetric_cipher_iv_or_nonce`, `bundle.authentication_tag`, `symmetric_alg`)
            // TEST: `test_aes_gcm_decryption_verifies_tag_and_decrypts_correctly()` (from spec idea)
            IF `plaintext_bytes` IS NULL (decryption/tag verification failed):
                RAISE `DecryptionError`("Symmetric decryption failed. Data may be corrupt or key incorrect.")

            RETURN DECODE_BYTES_TO_STRING(`plaintext_bytes`)
        CATCH parsing error:
            RAISE `DecryptionError`("Failed to parse encrypted file bundle.")
        CATCH crypto library error as e:
            RAISE `DecryptionError`("Hybrid PQC decryption failed: " + e.message)
        CATCH missing library error:
            RAISE `MissingDependencyError`("Required PQC/crypto library not found for decryption")

CLASS `GpgHandler` IMPLEMENTS `AbstractCryptoHandler`:
    METHOD `can_handle(file_path, content_bytes_peek, config)`:
        // Checks if file extension is ".gpg" or similar
        // OR if `content_bytes_peek` indicates GPG format
        // OR if `config.pqc_fallback_to_classical_gpg` is true and other handlers failed.
        // TEST: `test_gpg_handler_can_handle_by_extension_or_magic_bytes()`
        RETURN TRUE IF determined to be GPG, ELSE FALSE

    METHOD `decrypt_content(encrypted_content_bundle_bytes, suite_config, key_material)`:
        // `suite_config` might contain path to GPG executable or GPG options.
        // `key_material` is often implicit (GPG agent).
        // TEST: `test_gpg_handler_decrypts_valid_gpg_file()` (from spec)
        // TEST: `test_gpg_handler_decrypt_fails_for_invalid_gpg_file_or_wrong_key()`
        LOG "Attempting GPG decryption for file."
        TRY
            `plaintext_bytes` = INVOKE_GPG_DECRYPTION_PROCESS_OR_LIBRARY(`encrypted_content_bundle_bytes`, `suite_config.gpg_options`)
            IF `plaintext_bytes` IS NULL:
                RAISE `DecryptionError`("GPG decryption failed.")
            RETURN DECODE_BYTES_TO_STRING(`plaintext_bytes`)
        CATCH GPG process error or library error as e:
            RAISE `DecryptionError`("GPG decryption failed: " + e.message)
        CATCH missing GPG executable/library:
            RAISE `MissingDependencyError`("GPG tool or library not found.")

    METHOD `encrypt_content(plaintext_content, suite_config, key_material)`:
        // Typically not Fava-driven for GPG if focus is PQC for new encryption.
        RAISE `NotImplementedError`("GPG encryption via Fava CryptoService not supported.")

## 7. CryptoServiceLocator

CLASS `CryptoServiceLocator`:
    `registered_handlers`: LIST of `AbstractCryptoHandler` instances

    CONSTRUCTOR(`fava_options`):
        Initialize `registered_handlers` (e.g., `HybridPqcHandler`, `GpgHandler`)

    METHOD `get_handler_for_file(file_path, content_bytes_peek, fava_options)`:
        // TEST: `test_crypto_service_locator_selects_pqc_handler_for_pqc_file()` (from spec)
        // TEST: `test_crypto_service_locator_selects_gpg_handler_for_gpg_file()` (from spec)
        // TEST: `test_crypto_service_locator_prioritizes_handlers_correctly()`
        FOR `handler` IN `self.registered_handlers`:
            IF `handler.can_handle(file_path, content_bytes_peek, fava_options)`:
                RETURN `handler`
        IF `fava_options.pqc_fallback_to_classical_gpg`: // Simplified fallback logic
            FOR `handler` IN `self.registered_handlers` WHERE `handler` IS `GpgHandler`:
                 IF `handler.can_handle(file_path, content_bytes_peek, fava_options)`: // Re-check for GPG
                    RETURN `handler`
        RETURN NULL // Or a `NullHandler` that assumes plaintext or raises error.
        // TEST: `test_crypto_service_locator_returns_null_or_errors_if_no_handler_matches()`

    METHOD `get_pqc_encrypt_handler(suite_config, fava_options)`:
        // Returns a configured HybridPqcHandler instance for encryption.
        // TEST: `test_crypto_service_locator_returns_correct_pqc_encrypt_handler_for_suite()`
        IF `suite_config.pqc_kem_algorithm` IS NOT NULL: // Basic check for PQC suite
            RETURN NEW `HybridPqcHandler()` // Potentially pass `fava_options` if handler needs them
        RAISE `ConfigurationError`("No PQC encryption handler for the specified suite.")

## 8. FavaLedger Integration (Conceptual Stubs)

CLASS `FavaLedger`:
    `fava_options`: Fava application options (contains PQC config)
    `crypto_service_locator`: INSTANCE of `CryptoServiceLocator`

    METHOD `_get_key_material_for_operation(fava_options, file_context, operation_type, handler_type_hint)`:
        // FR2.5.2, C7.3
        // TEST: `test_fava_ledger_obtains_correct_key_material_for_decryption_passphrase()`
        // TEST: `test_fava_ledger_obtains_correct_key_material_for_encryption_external_file()`
        // TEST: `test_fava_ledger_handles_key_generation_from_new_passphrase_for_encryption()`
        `key_management_mode = fava_options.CONFIG_PQC_KEY_MANAGEMENT_MODE`
        `key_source_detail = fava_options.CONFIG_PQC_KEY_SOURCE_DETAIL`
        `active_suite = fava_options.CONFIG_PQC_SUITES[fava_options.CONFIG_PQC_ACTIVE_SUITE_ID]`

        IF `key_management_mode == "PASSPHRASE_DERIVED"`:
            `passphrase` = PROMPT_USER_FOR_PASSPHRASE_SECURELY("Enter passphrase for " + `file_context`)
            `salt` = RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT(`file_context`, `key_source_detail`) // `key_source_detail` might be master salt
            IF `operation_type == 'encrypt'`:
                // For encryption, we need public keys. Derivation gives both.
                `classical_keys, pqc_keys` = `derive_kem_keys_from_passphrase(passphrase, salt, active_suite.kdf_algorithm_for_passphrase, active_suite.classical_kem_algorithm, active_suite.pqc_kem_algorithm)`
                RETURN OBJECT { `classical_public_key`: `classical_keys.public`, `pqc_public_key`: `pqc_keys.public`, `passphrase_salt`: `salt` }
            ELSE IF `operation_type == 'decrypt'`:
                // For decryption, we need private keys.
                `classical_keys, pqc_keys` = `derive_kem_keys_from_passphrase(passphrase, salt, active_suite.kdf_algorithm_for_passphrase, active_suite.classical_kem_algorithm, active_suite.pqc_kem_algorithm)`
                RETURN OBJECT { `classical_private_key`: `classical_keys.private`, `pqc_private_key`: `pqc_keys.private` }
        ELSE IF `key_management_mode == "EXTERNAL_KEY_FILE"`:
            `classical_keys, pqc_keys` = `load_keys_from_external_file(key_source_detail)`
            IF `operation_type == 'encrypt'`:
                RETURN OBJECT { `classical_public_key`: `classical_keys.public`, `pqc_public_key`: `pqc_keys.public` }
            ELSE IF `operation_type == 'decrypt'`:
                RETURN OBJECT { `classical_private_key`: `classical_keys.private`, `pqc_private_key`: `pqc_keys.private` }
        RAISE `KeyManagementError`("Unsupported key management mode or operation.")

    METHOD `_try_decrypt_content(file_path, content_bytes)`:
        // FR2.1, FR2.2, FR2.7, US4.2, US4.3, US4.5, EC6.1-EC6.4, EC6.6
        // TEST: `test_fava_ledger_uses_crypto_locator_to_get_handler_for_decryption()`
        `content_peek = first N bytes of content_bytes`
        `handler = self.crypto_service_locator.get_handler_for_file(file_path, content_peek, self.fava_options)`
        IF `handler IS NOT NULL`:
            TRY
                `key_material = self._get_key_material_for_operation(self.fava_options, file_path, 'decrypt', TYPEOF(handler))`
                `suite_id_for_handler` = DETERMINE_SUITE_ID_FROM_FILE_OR_CONFIG(`file_path`, `content_peek`, `handler`, `self.fava_options`)
                `suite_config = self.fava_options.CONFIG_PQC_SUITES[suite_id_for_handler]` IF `suite_id_for_handler` else GET_DEFAULT_GPG_CONFIG()
                `plaintext = handler.decrypt_content(content_bytes, suite_config, key_material)`
                LOG_INFO("Successfully decrypted " + `file_path` + " using " + TYPEOF(handler))
                RETURN `plaintext`
            CATCH `DecryptionError` as e:
                LOG_ERROR("Decryption failed for " + `file_path` + ": " + e.message)
                SHOW_USER_ERROR_MESSAGE(e.message)
                RETURN NULL
            CATCH `MissingDependencyError` as e:
                LOG_ERROR("Missing dependency for " + `file_path` + ": " + e.message)
                SHOW_USER_ERROR_MESSAGE("Cannot decrypt " + `file_path` + ", required library missing.")
                // Potentially disable handler type for session.
                RETURN NULL
            CATCH `KeyManagementError` as e:
                LOG_ERROR("Key management error for " + `file_path` + ": " + e.message)
                SHOW_USER_ERROR_MESSAGE("Key error for " + `file_path` + ": " + e.message)
                RETURN NULL
        ELSE IF file seems plaintext (e.g. no handler matched, or NullHandler returned):
            RETURN DECODE_BYTES_TO_STRING(`content_bytes`)
        RETURN NULL // All attempts failed

    METHOD `save_file_pqc(output_file_path, content_str, original_file_context)`:
        // FR2.5, US4.1, US4.6, EC6.9
        // TEST: `test_fava_ledger_saves_and_reloads_pqc_encrypted_file()` (from spec)
        // TEST: `test_fava_ledger_retrieves_active_pqc_suite_config_for_saving()`
        IF NOT `self.fava_options.CONFIG_PQC_DATA_AT_REST_ENABLED`:
            LOG_WARNING("PQC encryption is disabled. File not encrypted with PQC.")
            // Proceed with non-PQC save or error.
            RETURN
        `active_suite_id = self.fava_options.CONFIG_PQC_ACTIVE_SUITE_ID`
        `suite_config = self.fava_options.CONFIG_PQC_SUITES[active_suite_id]`
        `handler = self.crypto_service_locator.get_pqc_encrypt_handler(suite_config, self.fava_options)`
        IF `handler IS NULL`:
            LOG_ERROR("No PQC encryption handler found for active suite: " + `active_suite_id`)
            SHOW_USER_ERROR_MESSAGE("Cannot encrypt: PQC configuration error.")
            RAISE `EncryptionError`("PQC encryption handler not found.")
        TRY
            `key_material = self._get_key_material_for_operation(self.fava_options, original_file_context, 'encrypt', TYPEOF(handler))`
            // TEST: `test_fava_ledger_obtains_or_generates_key_material_for_encryption_pqc()`
            `encrypted_bundle_bytes = handler.encrypt_content(content_str, suite_config, key_material)`
            WRITE_BYTES_TO_FILE(`output_file_path`, `encrypted_bundle_bytes`)
            LOG_INFO("Successfully encrypted and saved to " + `output_file_path` + " with PQC Hybrid Suite: " + `active_suite_id`)
            SHOW_USER_SUCCESS_MESSAGE("File encrypted and saved to " + `output_file_path`)
        CATCH `EncryptionError` as e:
            LOG_ERROR("PQC Encryption failed for " + `output_file_path` + ": " + e.message)
            SHOW_USER_ERROR_MESSAGE("Encryption failed: " + e.message)
        CATCH `MissingDependencyError` as e:
            LOG_ERROR("Missing dependency for PQC encryption: " + e.message)
            SHOW_USER_ERROR_MESSAGE("Cannot encrypt: required PQC library missing.")
        CATCH `KeyManagementError` as e:
            LOG_ERROR("Key management error during encryption: " + e.message)
            SHOW_USER_ERROR_MESSAGE("Key error during encryption: " + e.message)

## 9. UI/UX Flow Considerations (Mapping to Pseudocode)

*   **Configuration (UI9.1):** User interactions map to setting `CONFIG_PQC_*` constants. Passphrase setting/changing would involve `_get_key_material_for_operation` (or a dedicated key setup function) to test/store new salt/derived key check.
*   **File Loading (UI9.2):** `FavaLedger._try_decrypt_content` handles decryption. Errors are propagated for UI display. Status indicators can be based on which handler successfully processed the file.
*   **File Encryption (UI9.3):** "Encrypt with PQC Hybrid" option triggers `FavaLedger.save_file_pqc`. Modal for passphrase/key selection maps to `_get_key_material_for_operation`.