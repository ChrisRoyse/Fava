# Pseudocode: PQC Cryptographic Agility

This document outlines the pseudocode for the PQC Cryptographic Agility module,
enabling Fava to configure and switch cryptographic algorithms for various operations,
including data-at-rest encryption/decryption, hashing, and WASM integrity verification.

## 1. Global Configuration Management

MODULE GlobalConfig
    CONSTANT FAVA_CRYPTO_SETTINGS_PATH = "fava_options.py OR dedicated crypto_config.py" // Placeholder for actual path

    PRIVATE GlobalCryptoSettingsCache = NULL

    FUNCTION LoadCryptoSettings()
        // FR2.3: Fava's configuration (`FavaOptions`) MUST allow administrators to specify desired cryptographic algorithms.
        // TEST: test_load_crypto_settings_loads_valid_config_from_path()
        // TEST: test_load_crypto_settings_handles_missing_file_gracefully_returns_defaults_or_throws_critical()
        // TEST: test_load_crypto_settings_validates_schema_against_spec_8_1_FAVA_CRYPTO_SETTINGS()
        // TEST: test_load_crypto_settings_parses_all_sections_data_at_rest_hashing_wasm_integrity_pqc_library()
        OUTPUT: CryptoSettingsObject // Represents the FAVA_CRYPTO_SETTINGS structure from spec 8.1
        BEGIN
            TRY
                RawConfigContent = READ_FILE_CONTENT(FAVA_CRYPTO_SETTINGS_PATH)
                ParsedConfig = PARSE_PYTHON_LIKE_STRUCTURE(RawConfigContent) // Or other appropriate parsing mechanism
                
                // Validate against the expected schema (spec 8.1)
                VALIDATE_SCHEMA(ParsedConfig, FAVA_CRYPTO_SETTINGS_ExpectedSchema) 
                IF ValidationFails THEN
                    THROW ConfigurationError("Crypto settings schema validation failed.")
                END IF

                LOG_INFO("Successfully loaded and validated crypto settings.")
                RETURN ParsedConfig
            CATCH FileNotFoundError AS e
                LOG_ERROR("Crypto settings file not found at " + FAVA_CRYPTO_SETTINGS_PATH + ": " + e.message)
                // Decide: return hardcoded defaults or throw critical error. For PQC, likely critical.
                THROW CriticalConfigurationError("Crypto settings file is missing.")
            CATCH ParsingError AS e
                LOG_ERROR("Failed to parse crypto settings: " + e.message)
                THROW CriticalConfigurationError("Crypto settings file is malformed.")
            CATCH ConfigurationError AS e // Includes schema validation errors
                LOG_ERROR("Invalid crypto settings: " + e.message)
                THROW CriticalConfigurationError("Crypto settings are invalid.")
            END TRY
        END FUNCTION

    FUNCTION GetCryptoSettings()
        // TEST: test_get_crypto_settings_returns_cached_settings_after_first_load()
        // TEST: test_get_crypto_settings_calls_load_crypto_settings_if_cache_is_empty()
        OUTPUT: CryptoSettingsObject
        BEGIN
            IF GlobalCryptoSettingsCache IS NULL THEN
                GlobalCryptoSettingsCache = LoadCryptoSettings()
            END IF
            RETURN GlobalCryptoSettingsCache
        END FUNCTION
END MODULE

## 2. Backend CryptoService (Conceptual: fava.crypto_service.py)

MODULE BackendCryptoService
    // FR2.1: Central CryptoService for backend operations.
    // FR2.4: Use a registry or factory pattern.
    // FR2.8: Cryptographic logic strictly isolated.

    PRIVATE _HANDLER_REGISTRY = NEW Map() // Maps suite_id (String) to CryptoHandlerFactory or CryptoHandlerInstance

    // As per spec 10.1
    INTERFACE CryptoHandler 
        FUNCTION get_suite_id() -> String
            // TEST: test_crypto_handler_get_suite_id_returns_correct_unique_id() for each concrete handler.

        // key_material: Could be passphrase, raw key bytes, or a structured object.
        // suite_specific_config: Dictionary for this suite from FAVA_CRYPTO_SETTINGS.data_at_rest.suites[suite_id].
        FUNCTION encrypt(plaintext: Bytes, key_material: Any, suite_specific_config: Dictionary) -> EncryptedBundle
            // TEST: test_crypto_handler_encrypt_output_not_equal_to_plaintext()
            // TEST: test_crypto_handler_encrypt_throws_error_for_invalid_key_material_type()
            // TEST: test_crypto_handler_encrypt_throws_error_for_missing_required_suite_config()

        FUNCTION decrypt(bundle: EncryptedBundle, key_material: Any, suite_specific_config: Dictionary) -> Bytes
            // TEST: test_crypto_handler_decrypt_reverses_encrypt_operation_successfully()
            // TEST: test_crypto_handler_decrypt_throws_error_for_incorrect_key_material()
            // TEST: test_crypto_handler_decrypt_throws_error_for_tampered_or_malformed_bundle()
    END INTERFACE

    STRUCTURE EncryptedBundle // As per spec, needs to carry enough info for decryption
        suite_id_used: String   // Identifier of the suite used for this encryption (e.g., "HYBRID_X25519_MLKEM768_AES256GCM")
        ciphertext: Bytes
        metadata: Dictionary    // e.g., { iv: Bytes, salt: Bytes (if KDF salt is per-encryption), kem_outputs: Bytes }
    END STRUCTURE

    // As per spec 10.1
    FUNCTION RegisterCryptoHandler(suite_id: String, factory_or_instance: Any)
        // TEST: test_register_crypto_handler_successfully_adds_new_handler_to_registry()
        // TEST: test_register_crypto_handler_throws_error_if_suite_id_is_null_or_empty()
        // TEST: test_register_crypto_handler_allows_overwriting_existing_handler_if_policy_permits_logs_warning()
        BEGIN
            IF suite_id IS NULL OR EMPTY(suite_id) OR factory_or_instance IS NULL THEN
                LOG_ERROR("Attempted to register crypto handler with invalid arguments.")
                THROW InvalidArgumentError("suite_id and factory/instance must be provided.")
            END IF
            IF _HANDLER_REGISTRY.HAS(suite_id) THEN
                LOG_WARNING("Overwriting existing crypto handler for suite_id: " + suite_id)
            END IF
            _HANDLER_REGISTRY.SET(suite_id, factory_or_instance)
            LOG_INFO("Crypto handler registered for suite: " + suite_id)
        END FUNCTION

    // As per spec 10.1
    FUNCTION GetCryptoHandler(suite_id: String) -> CryptoHandler
        // TEST: test_get_crypto_handler_returns_correctly_registered_handler_instance()
        // TEST: test_get_crypto_handler_correctly_uses_factory_to_create_handler_instance()
        // TEST: test_get_crypto_handler_throws_algorithm_not_found_error_for_unregistered_suite_id() (EC6.1)
        BEGIN
            IF NOT _HANDLER_REGISTRY.HAS(suite_id) THEN
                LOG_ERROR("No crypto handler registered for suite_id: " + suite_id)
                THROW AlgorithmNotFoundError("Handler for suite '" + suite_id + "' not registered.")
            END IF

            handler_entry = _HANDLER_REGISTRY.GET(suite_id)
            IF IS_FACTORY_TYPE(handler_entry) THEN // Assume a way to check if it's a factory
                AppConfig = GlobalConfig.GetCryptoSettings()
                SuiteConfig = AppConfig.data_at_rest.suites[suite_id]
                IF SuiteConfig IS NULL THEN
                     THROW ConfigurationError("Missing suite configuration for " + suite_id + " needed by factory.")
                END IF
                RETURN handler_entry.CREATE_INSTANCE(SuiteConfig) // Factory creates instance with its specific config
            ELSE
                RETURN handler_entry // It's already an instance
            END IF
        END FUNCTION
    
    // As per spec 10.1
    FUNCTION GetActiveEncryptionHandler() -> CryptoHandler
        // TDD Anchor: test_crypto_service_locator_returns_active_encryption_handler()
        // FR2.5: Algorithm switching via configuration.
        BEGIN
            AppConfig = GlobalConfig.GetCryptoSettings()
            ActiveSuiteID = AppConfig.data_at_rest.active_encryption_suite_id
            IF ActiveSuiteID IS NULL OR EMPTY(ActiveSuiteID) THEN
                 LOG_CRITICAL("Active encryption suite ID ('active_encryption_suite_id') is not configured.")
                 THROW ConfigurationError("Mandatory 'active_encryption_suite_id' is missing from crypto settings.")
            END IF
            // TEST: test_get_active_encryption_handler_retrieves_handler_matching_active_suite_id_in_config()
            TRY
                RETURN GetCryptoHandler(ActiveSuiteID)
            CATCH AlgorithmNotFoundError AS e
                LOG_CRITICAL("Configured active encryption handler '" + ActiveSuiteID + "' is not registered or its library is unavailable (e.g. oqs-python). " + e.message) // EC6.2
                THROW CriticalConfigurationError("Active encryption algorithm '" + ActiveSuiteID + "' is unavailable.") // Fail securely
            END TRY
        END FUNCTION

    // As per spec 10.1
    FUNCTION GetConfiguredDecryptionHandlers() -> List<CryptoHandler>
        // TDD Anchor: test_crypto_service_locator_returns_decryption_handlers_in_order()
        // FR2.9: Support for decrypting older formats.
        BEGIN
            AppConfig = GlobalConfig.GetCryptoSettings()
            DecryptionOrderList = AppConfig.data_at_rest.decryption_attempt_order
            HandlersList = NEW List()

            IF DecryptionOrderList IS NULL OR DecryptionOrderList IS EMPTY THEN
                LOG_WARNING("No 'decryption_attempt_order' configured. Only active suite (if any) might be attempted implicitly elsewhere.")
                RETURN HandlersList // Return empty list, or could add active handler by default. Spec implies explicit list.
            END IF

            FOR EACH suite_id IN DecryptionOrderList
                TRY
                    Handler = GetCryptoHandler(suite_id)
                    HandlersList.ADD(Handler)
                CATCH AlgorithmNotFoundError
                    LOG_WARNING("Crypto handler for suite_id '" + suite_id + "' (listed in 'decryption_attempt_order') not found/registered. It will be skipped for decryption attempts.")
                    // TEST: test_get_configured_decryption_handlers_skips_unregistered_suite_ids_and_logs_warning()
                END TRY
            END FOR
            // TEST: test_get_configured_decryption_handlers_returns_list_of_handlers_matching_order_in_config()
            RETURN HandlersList
        END FUNCTION

    // --- Example HybridPqcCryptoHandler (Illustrative for FR2.6) ---
    CLASS HybridPqcCryptoHandler IMPLEMENTS CryptoHandler
        PRIVATE my_suite_id: String
        PRIVATE my_suite_config: Dictionary // From FAVA_CRYPTO_SETTINGS.data_at_rest.suites[my_suite_id]

        CONSTRUCTOR(suite_id_param: String, full_suite_config: Dictionary)
            // TEST: test_hybrid_handler_constructor_sets_id_and_config_validates_essential_params()
            // TEST: test_hybrid_handler_constructor_throws_if_req_params_like_kem_symm_kdf_missing_in_config()
            this.my_suite_id = suite_id_param
            this.my_suite_config = full_suite_config
            // VALIDATE this.my_suite_config for required fields like classical_kem_algorithm, pqc_kem_algorithm, symmetric_algorithm, kdf_algorithm
        END CONSTRUCTOR

        FUNCTION get_suite_id() -> String
            RETURN this.my_suite_id
        END FUNCTION

        FUNCTION _derive_symmetric_key_from_passphrase(passphrase: String, salt: Bytes) -> SymmetricKeyBytes
            // TEST: test_hybrid_derive_keys_uses_kdf_from_suite_config_hkdf_sha3_512()
            // TEST: test_hybrid_derive_keys_produces_deterministic_key_for_same_passphrase_salt()
            KdfAlgorithm = this.my_suite_config.kdf_algorithm // e.g., "HKDF-SHA3-512"
            // Actual KDF logic using KdfAlgorithm, passphrase, salt, and context info (e.g., "FavaDataAtRest")
            // to derive a symmetric key of appropriate length for this.my_suite_config.symmetric_algorithm.
            RETURN KDF_LIBRARY.derive(passphrase, salt, KdfAlgorithm, GET_SYMMETRIC_KEY_LENGTH(this.my_suite_config.symmetric_algorithm), "FavaSymmetricKey")
        END FUNCTION

        FUNCTION encrypt(plaintext: Bytes, key_material: Any, suite_config_override: Dictionary OPTIONAL) -> EncryptedBundle
            // TDD Anchor: test_hybrid_pqc_handler_encrypt_decrypt_with_passphrase_derived_key() (encrypt part)
            // FR2.6: Support for Hybrid Modes. This simplified version focuses on passphrase-derived symmetric key.
            // A full hybrid KEM exchange is more complex and typically for key agreement, not direct data-at-rest from passphrase.
            // The suite KEMs (classical_kem_algorithm, pqc_kem_algorithm) might be used if key_material was a public key set.
            // For PASSPHRASE_DERIVED, the KDF is central.
            // TEST: test_hybrid_encrypt_uses_symmetric_algo_from_suite_config_aes256gcm()
            // TEST: test_hybrid_encrypt_generates_unique_iv_per_encryption()
            // TEST: test_hybrid_encrypt_includes_suite_id_iv_salt_in_bundle_metadata()
            CurrentConfig = suite_config_override IF PROVIDED ELSE this.my_suite_config
            SymmetricKey: Bytes
            SaltToStore: Bytes = NULL

            IF CurrentConfig.key_management_mode == "PASSPHRASE_DERIVED" THEN
                // Assume key_material is the passphrase string
                Passphrase = CAST_TO_STRING(key_material)
                // Salt can be global (less ideal for passphrases) or generated per encryption.
                // Using per-encryption salt stored in bundle is better.
                GeneratedSalt = GENERATE_RANDOM_BYTES(16) // Example salt size
                SaltToStore = GeneratedSalt
                SymmetricKey = _derive_symmetric_key_from_passphrase(Passphrase, GeneratedSalt)
            // ELIF CurrentConfig.key_management_mode == "EXTERNAL_KEY_FILE" THEN
                // Logic to load/use externally managed key based on key_material
                // SymmetricKey = ...
            ELSE
                THROW ConfigurationError("Unsupported key_management_mode: " + CurrentConfig.key_management_mode)
            END IF

            IV = GENERATE_RANDOM_BYTES(GET_IV_LENGTH(CurrentConfig.symmetric_algorithm)) // e.g., 12 bytes for AES-GCM
            SymmetricCipher = GET_SYMMETRIC_CIPHER_INSTANCE(CurrentConfig.symmetric_algorithm) // e.g., AES-256-GCM
            
            TRY
                CiphertextWithAuthTag = SymmetricCipher.encrypt(plaintext, SymmetricKey, IV) // AEAD ciphers produce this
            CATCH CryptoError AS e // From underlying crypto library
                LOG_ERROR("Symmetric encryption failed for suite " + this.my_suite_id + ": " + e.message)
                THROW EncryptionFailedError("Underlying symmetric encryption failed.") // EC6.3 if params incompatible
            END TRY

            RETURN NEW EncryptedBundle(
                suite_id_used: this.my_suite_id,
                ciphertext: CiphertextWithAuthTag,
                metadata: { "iv": IV, "salt": SaltToStore } // SaltToStore might be null if not used
            )
        END FUNCTION

        FUNCTION decrypt(bundle: EncryptedBundle, key_material: Any, suite_config_override: Dictionary OPTIONAL) -> Bytes
            // TDD Anchor: test_hybrid_pqc_handler_encrypt_decrypt_with_passphrase_derived_key() (decrypt part)
            // TEST: test_hybrid_decrypt_uses_symmetric_algo_from_suite_config_aes256gcm()
            // TEST: test_hybrid_decrypt_extracts_iv_salt_from_bundle_metadata_correctly()
            // TEST: test_hybrid_decrypt_throws_decryption_error_on_auth_failure_for_aead()
            CurrentConfig = suite_config_override IF PROVIDED ELSE this.my_suite_config
            SymmetricKey: Bytes

            IF bundle.suite_id_used != this.my_suite_id AND suite_config_override IS NULL THEN
                 // This check is more for the orchestrating DecryptDataAtRest function.
                 // A handler should assume it's called appropriately for its suite.
            END IF

            IF bundle.metadata IS NULL OR bundle.metadata.iv IS NULL THEN
                THROW DecryptionError("Missing IV in encrypted bundle metadata for suite " + this.my_suite_id)
            END IF
            IV = bundle.metadata.iv
            SaltFromBundle = bundle.metadata.salt // May be null if global salt was used or not applicable

            IF CurrentConfig.key_management_mode == "PASSPHRASE_DERIVED" THEN
                Passphrase = CAST_TO_STRING(key_material)
                IF SaltFromBundle IS NULL THEN // This case implies a fixed/global salt was used during encryption.
                    // This is less secure and makes assumptions. Prefer salt in bundle.
                    // GlobalSalt = GlobalConfig.GetCryptoSettings().data_at_rest.passphrase_kdf_salt_global
                    // SymmetricKey = _derive_symmetric_key_from_passphrase(Passphrase, GlobalSalt)
                    THROW DecryptionError("Missing salt in bundle metadata for passphrase-derived key, and global salt use is ambiguous/discouraged here.")
                ELSE
                    SymmetricKey = _derive_symmetric_key_from_passphrase(Passphrase, SaltFromBundle)
                END IF
            // ELIF ...
            ELSE
                THROW ConfigurationError("Unsupported key_management_mode for decryption: " + CurrentConfig.key_management_mode)
            END IF

            SymmetricCipher = GET_SYMMETRIC_CIPHER_INSTANCE(CurrentConfig.symmetric_algorithm)
            TRY
                Plaintext = SymmetricCipher.decrypt(bundle.ciphertext, SymmetricKey, IV) // AEAD handles auth tag
            CATCH CryptoError AS e // e.g., AuthenticationTagMismatch, DecryptionFailed
                LOG_WARNING("Symmetric decryption failed for suite " + this.my_suite_id + " (bundle from " + bundle.suite_id_used + "): " + e.message)
                THROW DecryptionError("Underlying symmetric decryption failed (e.g., bad key or tampered data).")
            END TRY
            RETURN Plaintext
        END FUNCTION
    END CLASS

    // --- Hashing Service (FR2.1) ---
    MODULE HashingProvider
        FUNCTION GetConfiguredHasher() -> HasherInterface
            // TEST: test_hashing_provider_returns_sha3_256_hasher_if_configured()
            // TEST: test_hashing_provider_returns_sha256_hasher_if_configured()
            // TEST: test_hashing_provider_falls_back_to_sha3_256_and_logs_warning_if_configured_algo_unavailable() (FR2.7)
            // TEST: test_hashing_provider_throws_if_no_hasher_can_be_provided()
            BEGIN
                AppConfig = GlobalConfig.GetCryptoSettings()
                ConfiguredAlgoName = AppConfig.hashing.default_algorithm
                TRY
                    RETURN GET_HASHER_INSTANCE(ConfiguredAlgoName)
                CATCH AlgorithmUnavailableError AS e
                    LOG_WARNING("Configured hash algorithm '" + ConfiguredAlgoName + "' is unavailable: " + e.message + ". Attempting fallback to SHA3-256.")
                    TRY
                        RETURN GET_HASHER_INSTANCE("SHA3-256") // Assume SHA3-256 is a mandatory baseline
                    CATCH AlgorithmUnavailableError AS fe
                        LOG_CRITICAL("Fallback hash algorithm SHA3-256 is also unavailable: " + fe.message)
                        THROW CriticalServiceError("No hashing service available.")
                    END TRY
                END TRY
            END FUNCTION
        // HasherInterface and concrete implementations (SHA256Impl, SHA3_256Impl) would be defined.
    END MODULE

    // --- General Decryption Orchestration for Data at Rest (FR2.9) ---
    FUNCTION DecryptDataAtRestWithAgility(raw_encrypted_bytes: Bytes, key_material_input: Any) -> PlaintextBytes
        // TEST: test_decrypt_data_at_rest_tries_handlers_from_decryption_attempt_order()
        // TEST: test_decrypt_data_at_rest_succeeds_if_one_handler_in_order_decrypts()
        // TEST: test_decrypt_data_at_rest_fails_with_decryption_failed_error_if_all_handlers_fail() (EC6.4)
        // TEST: test_decrypt_data_at_rest_parses_bundle_header_to_get_suite_id_for_targeted_first_attempt() (C7.5)
        BEGIN
            // Attempt to parse a common bundle header to find suite_id_used (C7.5)
            // This allows a targeted attempt before iterating the full list.
            ParsedHeader = PARSE_COMMON_ENCRYPTED_BUNDLE_HEADER(raw_encrypted_bytes) // Returns { suite_id, actual_bundle_data_for_handler } or failure
            
            AppConfig = GlobalConfig.GetCryptoSettings()
            DecryptionHandlerInstances = GetConfiguredDecryptionHandlers() // Already in preferred order

            IF ParsedHeader.was_successful AND ParsedHeader.suite_id IS NOT NULL THEN
                // Try the handler matching the bundle's declared suite_id first, if it's in our configured list
                FOR EACH Handler IN DecryptionHandlerInstances
                    IF Handler.get_suite_id() == ParsedHeader.suite_id THEN
                        LOG_INFO("Attempting decryption with handler '" + ParsedHeader.suite_id + "' identified from bundle header.")
                        TRY
                            SuiteSpecificConfig = AppConfig.data_at_rest.suites[ParsedHeader.suite_id]
                            // Assume ParsedHeader.actual_bundle_data_for_handler is the EncryptedBundle structure
                            RETURN Handler.decrypt(ParsedHeader.actual_bundle_data_for_handler, key_material_input, SuiteSpecificConfig)
                        CATCH DecryptionError AS e
                            LOG_INFO("Targeted decryption with handler '" + ParsedHeader.suite_id + "' failed: " + e.message)
                            // Fall through to iterate all configured handlers
                            BREAK // Stop trying this targeted handler, proceed to general iteration
                        CATCH Exception AS ex
                            LOG_ERROR("Unexpected error with targeted handler '" + ParsedHeader.suite_id + "': " + ex.message)
                            BREAK
                        END TRY
                    END IF
                END FOR
            END IF

            // Iterate through all configured decryption handlers in the specified order
            FOR EACH Handler IN DecryptionHandlerInstances
                SuiteID = Handler.get_suite_id()
                LOG_INFO("Attempting decryption with handler from configured order: " + SuiteID)
                TRY
                    // Each handler might need to re-parse the raw_encrypted_bytes into its expected EncryptedBundle format
                    // Or, if PARSE_COMMON_ENCRYPTED_BUNDLE_HEADER was very generic, its output could be used.
                    // For robustness, assume handler can take raw bytes or a pre-parsed common structure.
                    // Let's assume we need to re-construct/parse the bundle for each handler if header parsing wasn't definitive.
                    ThisHandlerBundle = PARSE_BUNDLE_FOR_HANDLER(raw_encrypted_bytes, SuiteID) // Handler-specific parsing
                    SuiteSpecificConfig = AppConfig.data_at_rest.suites[SuiteID]
                    RETURN Handler.decrypt(ThisHandlerBundle, key_material_input, SuiteSpecificConfig)
                CATCH DecryptionError AS e
                    LOG_INFO("Decryption with handler '" + SuiteID + "' failed: " + e.message + ". Trying next.")
                    // Continue to the next handler in the list
                CATCH BundleParsingError AS bpe 
                    LOG_INFO("Could not parse bundle for handler '" + SuiteID + "': " + bpe.message + ". Trying next.")
                CATCH Exception AS ex // Catch other unexpected errors from this handler
                    LOG_ERROR("Unexpected error with handler '" + SuiteID + "' during decryption attempt: " + ex.message + ". Trying next.")
                END TRY
            END FOR

            LOG_ERROR("All configured decryption attempts failed for the provided data.")
            THROW DecryptionFailedError("Unable to decrypt data: No configured cryptographic suite succeeded.") // EC6.4
        END FUNCTION

END MODULE // BackendCryptoService


## 3. Frontend Cryptographic Abstraction (Conceptual: frontend/src/lib/pqcCryptoFacade.ts)

MODULE FrontendCryptoFacade
    // FR2.2: Cryptographic abstraction layer for frontend.
    PRIVATE _favaConfigCache = NULL
    PRIVATE _configCacheTimestamp = 0
    CONSTANT CONFIG_CACHE_TTL_MS = 60000 // e.g., 1 minute

    ASYNC FUNCTION _getFavaRuntimeCryptoOptions() -> CryptoConfigSectionObject
        // TEST: test_fe_get_runtime_options_fetches_from_api_if_cache_empty_or_stale()
        // TEST: test_fe_get_runtime_options_returns_cached_data_if_fresh()
        // TEST: test_fe_get_runtime_options_handles_api_error_returns_stale_or_default_or_throws()
        BEGIN
            CurrentTime = GET_SYSTEM_TIME_MS()
            IF _favaConfigCache IS NULL OR (CurrentTime - _configCacheTimestamp > CONFIG_CACHE_TTL_MS) THEN
                TRY
                    // IP12.4: API exposes relevant parts of FAVA_CRYPTO_SETTINGS
                    ApiResponse = AWAIT HTTP_GET_JSON("/api/fava-crypto-configuration") // Assumed API endpoint
                    _favaConfigCache = ApiResponse.crypto_settings // Assuming structure like { hashing: {...}, wasm_integrity: {...} }
                    _configCacheTimestamp = CurrentTime
                    LOG_INFO("Frontend fetched and cached Fava crypto configuration.")
                CATCH NetworkError AS e
                    LOG_ERROR("Frontend failed to fetch Fava crypto configuration from API: " + e.message)
                    IF _favaConfigCache IS NOT NULL THEN
                        LOG_WARNING("Returning stale frontend crypto config due to API error.")
                        RETURN _favaConfigCache // Return stale if available
                    ELSE
                        // Critical: if no defaults, operations might fail.
                        THROW ConfigurationError("Unable to fetch crypto configuration for frontend operations.")
                    END IF
                END TRY
            END IF
            RETURN _favaConfigCache
        END FUNCTION

    // --- Hashing (FR2.2) ---
    ASYNC FUNCTION CalculateConfiguredHash(data_string: String) -> HexString
        // TDD Anchor: test_calculateConfiguredHash_uses_sha3_by_default_from_mock_api()
        // TEST: test_fe_calculate_hash_uses_algorithm_from_api_config_sha256()
        // TEST: test_fe_calculate_hash_falls_back_to_sha3_256_if_api_config_algo_unavailable_logs_warning()
        // TEST: test_fe_calculate_hash_throws_if_all_hash_attempts_fail()
        BEGIN
            TRY
                CryptoConfig = AWAIT _getFavaRuntimeCryptoOptions()
                ConfiguredAlgo = CryptoConfig.hashing.default_algorithm // e.g., "SHA3-256" or "SHA256"
                
                IF ConfiguredAlgo IS NULL THEN // Should not happen if API is well-defined
                    LOG_WARNING("No default hashing algorithm in frontend config. Defaulting to SHA3-256.")
                    ConfiguredAlgo = "SHA3-256"
                END IF

                DataBytes = UTF8_ENCODE(data_string)
                HashedBytes = _internalCalculateHash(DataBytes, ConfiguredAlgo)
                RETURN BYTES_TO_HEX_STRING(HashedBytes)
            CATCH Error AS e // Covers config fetch errors, internal hash errors
                LOG_ERROR("CalculateConfiguredHash failed with primary algorithm: " + e.message + ". Attempting fallback.")
                // FR2.7: Fallback for less critical ops
                TRY
                    DataBytes = UTF8_ENCODE(data_string)
                    HashedBytes = _internalCalculateHash(DataBytes, "SHA3-256") // Default fallback
                    LOG_WARNING("Used fallback SHA3-256 for hashing.")
                    RETURN BYTES_TO_HEX_STRING(HashedBytes)
                CATCH FallbackError AS fe
                    LOG_CRITICAL("Frontend hashing failed completely, even with fallback SHA3-256: " + fe.message)
                    THROW HashingOperationFailedError("All hashing attempts failed.")
                END TRY
            END TRY
        END FUNCTION

    FUNCTION _internalCalculateHash(data_bytes: Bytes, algorithm_name: String) -> Bytes
        // TEST: test_fe_internal_hash_calls_sha256_lib_correctly()
        // TEST: test_fe_internal_hash_calls_sha3_256_lib_correctly_js_sha3()
        // TEST: test_fe_internal_hash_throws_algorithm_not_supported_for_unknown_name()
        BEGIN
            SWITCH algorithm_name
                CASE "SHA256":
                    RETURN SHA256_JS_LIBRARY.hash(data_bytes)
                CASE "SHA3-256":
                    RETURN SHA3_256_JS_LIBRARY.hash(data_bytes) // e.g., from js-sha3
                DEFAULT:
                    THROW AlgorithmNotSupportedError("Unsupported frontend hash algorithm: " + algorithm_name)
            END SWITCH
        END FUNCTION

    // --- WASM Signature Verification (FR2.2) ---
    ASYNC FUNCTION VerifyWasmSignatureWithConfig(wasm_module_buffer: ArrayBuffer, signature_buffer: ArrayBuffer) -> Boolean
        // TDD Anchor: test_verifyWasmSignatureWithConfig_uses_dilithium3_from_mock_api()
        // TEST: test_fe_verify_wasm_sig_returns_true_if_verification_disabled_in_api_config()
        // TEST: test_fe_verify_wasm_sig_returns_false_if_public_key_or_algo_missing_in_api_config_and_enabled()
        // TEST: test_fe_verify_wasm_sig_calls_internal_verify_with_params_from_api_config()
        // TEST: test_fe_verify_wasm_sig_returns_false_on_any_verification_error_fail_securely()
        BEGIN
            TRY
                CryptoConfig = AWAIT _getFavaRuntimeCryptoOptions()
                WasmIntegritySettings = CryptoConfig.wasm_integrity

                IF WasmIntegritySettings IS NULL OR WasmIntegritySettings.verification_enabled IS FALSE THEN
                    LOG_INFO("WASM signature verification is disabled in configuration.")
                    RETURN TRUE // Verification not required or disabled
                END IF

                PublicKeyBase64 = WasmIntegritySettings.public_key_dilithium3_base64
                SignatureAlgoName = WasmIntegritySettings.signature_algorithm // Should be "Dilithium3" as per spec

                IF PublicKeyBase64 IS NULL OR SignatureAlgoName IS NULL THEN
                    LOG_ERROR("WASM integrity verification enabled, but public key or algorithm name is missing from config.")
                    RETURN FALSE // Fail securely: cannot verify
                END IF
                
                // EC6.2: If liboqs-js fails for configured algo, _internalVerifySignature should handle it.
                RETURN _internalVerifySignature(wasm_module_buffer, signature_buffer, PublicKeyBase64, SignatureAlgoName)
            CATCH Error AS e // Covers config fetch errors, internal verify errors
                LOG_ERROR("VerifyWasmSignatureWithConfig encountered an error: " + e.message + ". Failing securely.")
                RETURN FALSE // Fail securely
            END TRY
        END FUNCTION

    FUNCTION _internalVerifySignature(message_buffer: ArrayBuffer, signature_buffer: ArrayBuffer, public_key_b64: String, algorithm_name: String) -> Boolean
        // TEST: test_fe_internal_verify_sig_calls_liboqs_js_dilithium3_verify_correctly()
        // TEST: test_fe_internal_verify_sig_returns_false_if_liboqs_js_verify_fails()
        // TEST: test_fe_internal_verify_sig_throws_algorithm_not_supported_for_unknown_name()
        BEGIN
            PublicKeyBytes = BASE64_DECODE(public_key_b64)
            SWITCH algorithm_name
                CASE "Dilithium3": // C7.1: Bounded by liboqs-js capabilities
                    TRY
                        // Conceptual call to liboqs-js, e.g.,
                        // OqsSig = NEW OQS.Signature(OQS.SIG.Dilithium3) // Or appropriate algorithm constant
                        // IsValid = OqsSig.verify(message_buffer, signature_buffer, PublicKeyBytes)
                        // OqsSig.free()
                        // RETURN IsValid
                        LOG_INFO("Performing conceptual Dilithium3 verification using liboqs-js.")
                        RETURN MOCK_LIBOQS_JS_DILITHIUM3_VERIFY(message_buffer, signature_buffer, PublicKeyBytes) // Placeholder
                    CATCH LibOqsJsError AS oqse // EC6.2
                        LOG_ERROR("liboqs-js verification failed for Dilithium3: " + oqse.message)
                        RETURN FALSE
                    END TRY
                DEFAULT:
                    THROW AlgorithmNotSupportedError("Unsupported frontend signature algorithm for WASM: " + algorithm_name)
            END SWITCH
        END FUNCTION
END MODULE // FrontendCryptoFacade


## 4. Initialization and Registration Flow (Backend)

// During Fava application startup (IP12.1):
// 1. GlobalConfig.LoadCryptoSettings() is called to load and validate FAVA_CRYPTO_SETTINGS.
// 2. For each suite defined in `FAVA_CRYPTO_SETTINGS.data_at_rest.suites`:
//    a. Determine the handler type (e.g., "FAVA_HYBRID_PQC", "CLASSICAL_GPG").
//    b. Create an instance of the corresponding concrete CryptoHandler (e.g., `HybridPqcCryptoHandler`, `GpgHandler`)
//       or a factory for it, passing the specific suite's configuration.
//    c. Register the handler/factory with `BackendCryptoService.RegisterCryptoHandler(suite_id, handler_or_factory)`.
//
// Example:
// PROCEDURE InitializeBackendCryptoService
//   BEGIN
//     AppConfig = GlobalConfig.GetCryptoSettings()
//     FOR EACH suite_id, suite_conf IN AppConfig.data_at_rest.suites.items()
//       TRY
//         IF suite_conf.type == "FAVA_HYBRID_PQC" THEN
//           HandlerInstance = NEW HybridPqcCryptoHandler(suite_id, suite_conf)
//           BackendCryptoService.RegisterCryptoHandler(suite_id, HandlerInstance)
//         ELIF suite_conf.type == "CLASSICAL_GPG" THEN
//           // HandlerInstance = NEW GpgCryptoHandler(suite_id, suite_conf) // Assuming GpgHandler exists
//           // BackendCryptoService.RegisterCryptoHandler(suite_id, HandlerInstance)
//           LOG_INFO("GPG Handler registration placeholder for suite: " + suite_id)
//         ELSE
//           LOG_WARNING("Unknown crypto suite type '" + suite_conf.type + "' for suite_id '" + suite_id + "'. Cannot register handler.")
//         END IF
//       CATCH Error AS e
//          LOG_ERROR("Failed to initialize or register handler for suite '" + suite_id + "': " + e.message)
//          // Depending on policy, this could be a critical failure if the suite is essential.
//       END TRY
//     END FOR
//     // Verify active encryption handler can be loaded
//     TRY
//        BackendCryptoService.GetActiveEncryptionHandler() 
//        LOG_INFO("Active encryption handler successfully loaded.")
//     CATCH Error AS e
//        LOG_CRITICAL("Failed to load active encryption handler post-registration: " + e.message + ". Application may not function correctly.")
//        // This should be a startup-blocking error.
//        THROW ApplicationStartupError("Critical failure: Active encryption handler unavailable.")
//     END TRY
//   END PROCEDURE
//
// TEST: test_app_startup_registers_all_valid_handlers_from_config_suites()
// TEST: test_app_startup_logs_warning_for_unknown_suite_types_in_config()
// TEST: test_app_startup_throws_critical_error_if_active_encryption_handler_cannot_be_loaded_after_registration()