# Pseudocode: PQC Hashing Module

**Version:** 1.0
**Date:** 2025-06-02

## 1. Introduction

This document provides detailed, language-agnostic pseudocode for Fava's Post-Quantum Cryptography (PQC) Hashing module. It covers the backend `HashingService`, the frontend hashing abstraction, and the configuration flow, as specified in [`docs/specifications/PQC_Hashing_Spec.md`](docs/specifications/PQC_Hashing_Spec.md). The pseudocode includes Test-Driven Development (TDD) anchors to guide test creation.

## 2. Global Constants and Assumed Utilities

CONSTANT DEFAULT_ALGORITHM_BACKEND = "SHA3-256"
CONSTANT SUPPORTED_ALGORITHMS_BACKEND = ["SHA3-256", "SHA256"] // Normalized to uppercase

CONSTANT DEFAULT_ALGORITHM_FRONTEND = "SHA3-256" // Should align with backend
CONSTANT SUPPORTED_ALGORITHMS_FRONTEND = ["SHA3-256", "SHA-256"] // WebCrypto uses "SHA-256"

// Assumed Utilities:
//   logger: A generic logging interface (e.g., logger.info, logger.warn, logger.error).
//   TO_UPPERCASE(string): Converts string to uppercase.
//   TO_HEX_STRING(bytes_or_byte): Converts byte array or single byte to a hexadecimal string.
//     TO_HEX_STRING(byte, padding_length): Pads hex string with leading zeros to meet length.
//   TextEncoder: Standard mechanism to encode strings to UTF-8 byte arrays (frontend).
//   NATIVE_CRYPTO_LIBRARY: Placeholder for the system's primary crypto library (e.g., Python's hashlib).
//   FALLBACK_SHA3_LIBRARY: Placeholder for a secondary SHA3 library (e.g., pysha3).
//   SHA3_JS_LIBRARY: Placeholder for a JavaScript SHA3 library (e.g., js-sha3).
//   FavaConfigurationProvider: An interface to access Fava's application settings.
//   Custom Error Types: HashingAlgorithmUnavailableError, InternalHashingError, FrontendHashingError.

## 3. Backend Hashing (`fava.crypto_service`)

MODULE PQC_Hashing_Backend

  CLASS HashingService
    PRIVATE algorithm_name_internal : STRING
    PRIVATE logger : Logger // Instance of a logger

    // TEST: HashingService.constructor_initializes_with_sha3_256_by_default()
    //   SETUP: No algorithm name provided to constructor.
    //   ACTION: Instantiate HashingService().
    //   ASSERT: Internal algorithm is "SHA3-256".

    // TEST: HashingService.constructor_initializes_with_provided_sha3_256_correctly()
    //   SETUP: Algorithm name "SHA3-256" (case-insensitive).
    //   ACTION: Instantiate HashingService("sHa3-256").
    //   ASSERT: Internal algorithm is "SHA3-256".

    // TEST: HashingService.constructor_initializes_with_provided_sha256_correctly()
    //   SETUP: Algorithm name "SHA256" (case-insensitive, or "SHA-256").
    //   ACTION: Instantiate HashingService("sha256").
    //   ASSERT: Internal algorithm is "SHA256".

    // TEST: HashingService.constructor_defaults_to_sha3_256_and_logs_warning_for_unsupported_algorithm()
    //   SETUP: Algorithm name "MD5_INVALID".
    //   ACTION: Instantiate HashingService("MD5_INVALID").
    //   ASSERT: Internal algorithm is "SHA3-256".
    //   ASSERT: Warning logged regarding "MD5_INVALID".

    CONSTRUCTOR(configured_algorithm_name : STRING nullable)
      logger = GET_LOGGER_INSTANCE() // Initialize logger
      IF configured_algorithm_name IS NULL OR configured_algorithm_name IS EMPTY THEN
        this.algorithm_name_internal = DEFAULT_ALGORITHM_BACKEND
        logger.info("HashingService: No algorithm configured, defaulting to " + DEFAULT_ALGORITHM_BACKEND)
      ELSE
        normalized_algo = TO_UPPERCASE(configured_algorithm_name)
        IF normalized_algo == "SHA-256" THEN normalized_algo = "SHA256" ENDIF // Normalize

        IF normalized_algo IS IN SUPPORTED_ALGORITHMS_BACKEND THEN
          this.algorithm_name_internal = normalized_algo
        ELSE
          logger.warn("HashingService: Unsupported hash algorithm '" + configured_algorithm_name + "'. Defaulting to '" + DEFAULT_ALGORITHM_BACKEND + "'.")
          this.algorithm_name_internal = DEFAULT_ALGORITHM_BACKEND
        ENDIF
      ENDIF
    END CONSTRUCTOR

    // TEST: HashingService.hash_data_sha3_256_produces_correct_hex_digest()
    //   SETUP: HashingService configured for "SHA3-256". Known_data_bytes. Known_sha3_256_hex_digest.
    //   ACTION: Call hash_data(Known_data_bytes).
    //   ASSERT: Result equals Known_sha3_256_hex_digest.

    // TEST: HashingService.hash_data_sha256_produces_correct_hex_digest()
    //   SETUP: HashingService configured for "SHA256". Known_data_bytes. Known_sha256_hex_digest.
    //   ACTION: Call hash_data(Known_data_bytes).
    //   ASSERT: Result equals Known_sha256_hex_digest.

    // TEST: HashingService.hash_data_handles_empty_input_correctly_for_sha3_256()
    //   SETUP: HashingService configured for "SHA3-256". Empty_byte_array. Known_sha3_256_hex_digest_of_empty.
    //   ACTION: Call hash_data(Empty_byte_array).
    //   ASSERT: Result equals Known_sha3_256_hex_digest_of_empty.

    // TEST: HashingService.hash_data_sha3_256_uses_fallback_if_primary_unavailable_and_logs_info()
    //   SETUP: HashingService configured for "SHA3-256". Mock NATIVE_CRYPTO_LIBRARY.sha3_256 to raise "NotAvailableError". Mock FALLBACK_SHA3_LIBRARY to succeed. Known_data_bytes. Known_sha3_256_hex_digest.
    //   ACTION: Call hash_data(Known_data_bytes).
    //   ASSERT: Result equals Known_sha3_256_hex_digest.
    //   ASSERT: Info/warning logged about using fallback.

    // TEST: HashingService.hash_data_raises_error_if_sha3_256_unavailable_and_no_fallback()
    //   SETUP: HashingService configured for "SHA3-256". Mock NATIVE_CRYPTO_LIBRARY.sha3_256 to raise "NotAvailableError". Mock FALLBACK_SHA3_LIBRARY to be unavailable or also raise error. Known_data_bytes.
    //   ACTION: Call hash_data(Known_data_bytes).
    //   ASSERT: Raises HashingAlgorithmUnavailableError.

    FUNCTION hash_data(data : BYTES_ARRAY) RETURNS STRING
      // INPUT: data - The byte array to hash.
      // OUTPUT: Hexadecimal string representation of the hash digest.
      // THROWS: HashingAlgorithmUnavailableError, InternalHashingError.
      TRY
        IF this.algorithm_name_internal == "SHA3-256" THEN
          TRY
            digest = NATIVE_CRYPTO_LIBRARY.sha3_256(data) // Attempt primary
            RETURN TO_HEX_STRING(digest)
          CATCH NativeNotAvailableError
            logger.info("HashingService: Primary SHA3-256 not available, attempting fallback.")
            IF FALLBACK_SHA3_LIBRARY_IS_AVAILABLE() THEN
              TRY
                digest = FALLBACK_SHA3_LIBRARY.sha3_256(data)
                RETURN TO_HEX_STRING(digest)
              CATCH FallbackLibraryError as err
                logger.error("HashingService: SHA3-256 fallback library failed: " + err.message)
                THROW NEW HashingAlgorithmUnavailableError("SHA3-256 fallback library failed.")
              END TRY
            ELSE
              logger.error("HashingService: SHA3-256 is configured but no implementation (native or fallback) is available.")
              THROW NEW HashingAlgorithmUnavailableError("SHA3-256 implementation not available.")
            ENDIF
          END TRY
        ELSE IF this.algorithm_name_internal == "SHA256" THEN
          TRY
            digest = NATIVE_CRYPTO_LIBRARY.sha256(data)
            RETURN TO_HEX_STRING(digest)
          CATCH NativeNotAvailableError
             logger.error("HashingService: SHA256 native library not available.")
             THROW NEW HashingAlgorithmUnavailableError("SHA256 implementation not available.")
          END TRY
        ELSE
          logger.error("HashingService: Internal error - hash_data called with unsupported algorithm: " + this.algorithm_name_internal)
          THROW NEW InternalHashingError("Unsupported hash algorithm encountered post-initialization.")
        ENDIF
      CATCH AnyException as e
          logger.error("HashingService: Unexpected error during hashing: " + e.message)
          THROW NEW InternalHashingError("Unexpected error during hashing: " + e.message)
      END TRY
    END FUNCTION

    FUNCTION get_configured_algorithm_name() RETURNS STRING
        RETURN this.algorithm_name_internal
    END FUNCTION

  END CLASS

  // TEST: get_hashing_service_creates_service_with_algorithm_from_config()
  //   SETUP: Mock FavaConfigProvider to return "SHA256" for 'pqc_hashing_algorithm'.
  //   ACTION: Call get_hashing_service(FavaConfigProvider).
  //   ASSERT: Returned HashingService instance is configured for "SHA256".

  FUNCTION get_hashing_service(fava_config_provider : FavaConfigurationProvider) RETURNS HashingService
    configured_algo_name = fava_config_provider.get_string_option("pqc_hashing_algorithm", DEFAULT_ALGORITHM_BACKEND)
    RETURN NEW HashingService(configured_algo_name)
  END FUNCTION

  // Conceptual helper
  FUNCTION FALLBACK_SHA3_LIBRARY_IS_AVAILABLE() RETURNS BOOLEAN
    // Implementation-specific check if the fallback library can be loaded/used.
    RETURN true // Assume available for pseudocode clarity; tests would mock.
  END FUNCTION

END MODULE


## 4. Frontend Hashing (`frontend/src/lib/crypto.ts`)

MODULE PQC_Hashing_Frontend

  // TEST: calculateHash_sha3_256_produces_correct_hex_digest_for_known_string()
  //   SETUP: Known_input_string. Known_sha3_256_hex_digest_of_utf8_encoded_string. Mock SHA3_JS_LIBRARY.calculate_digest_as_hex.
  //   ACTION: AWAIT calculateHash(Known_input_string, "SHA3-256").
  //   ASSERT: Result equals Known_sha3_256_hex_digest.

  // TEST: calculateHash_sha256_produces_correct_hex_digest_for_known_string_using_webcrypto()
  //   SETUP: Known_input_string. Known_sha256_hex_digest_of_utf8_encoded_string. Mock window.crypto.subtle.digest for "SHA-256".
  //   ACTION: AWAIT calculateHash(Known_input_string, "SHA-256"). // Or "SHA256" from config
  //   ASSERT: Result equals Known_sha256_hex_digest.

  // TEST: calculateHash_defaults_to_sha256_and_logs_warning_if_unsupported_algorithm_and_sha3_unavailable()
  //   SETUP: Input_string. Mock SHA3_JS_LIBRARY_IS_AVAILABLE_AND_WORKING to return FALSE.
  //   ACTION: AWAIT calculateHash(Input_string, "INVALID_ALGO_XYZ").
  //   ASSERT: Result is SHA-256 hash of Input_string (using WebCrypto).
  //   ASSERT: Warning logged for "INVALID_ALGO_XYZ" and SHA3 unavailability.

  // TEST: calculateHash_throws_error_if_sha3_js_library_fails_when_sha3_256_is_requested()
  //   SETUP: Input_string. Mock SHA3_JS_LIBRARY_IS_AVAILABLE_AND_WORKING to return TRUE, but SHA3_JS_LIBRARY.calculate_digest_as_hex to throw error.
  //   ACTION: AWAIT calculateHash(Input_string, "SHA3-256").
  //   ASSERT: Throws FrontendHashingError. Error logged.

  // TEST: calculateHash_uses_utf8_encoding_for_input_string()
  //   SETUP: String_with_multibyte_chars. Algorithm "SHA-256". Spy on TextEncoder.encode. Mock window.crypto.subtle.digest.
  //   ACTION: AWAIT calculateHash(String_with_multibyte_chars, "SHA-256").
  //   ASSERT: TextEncoder.encode was called with String_with_multibyte_chars.

  ASYNC FUNCTION calculateHash(data_string : STRING, algorithm_name_from_config : STRING) RETURNS STRING
    // INPUT: data_string - The string data to hash.
    // INPUT: algorithm_name_from_config - Algorithm name from Fava config (e.g., "SHA3-256", "SHA256").
    // OUTPUT: Hexadecimal string representation of the hash digest.
    // THROWS: FrontendHashingError for critical errors.
    logger = GET_LOGGER_INSTANCE() // Assume console or similar
    LET effective_algorithm : STRING
    normalized_config_algo = TO_UPPERCASE(algorithm_name_from_config)

    IF normalized_config_algo == "SHA256" THEN normalized_config_algo = "SHA-256" ENDIF // Align with WebCrypto name

    IF normalized_config_algo == "SHA3-256" THEN
      effective_algorithm = "SHA3-256"
    ELSE IF normalized_config_algo == "SHA-256" THEN
      effective_algorithm = "SHA-256"
    ELSE
      logger.warn("FrontendHashing: Unsupported algorithm '" + algorithm_name_from_config + "' from config.")
      IF SHA3_JS_LIBRARY_IS_AVAILABLE_AND_WORKING() THEN
        logger.warn("FrontendHashing: Defaulting to preferred " + DEFAULT_ALGORITHM_FRONTEND)
        effective_algorithm = DEFAULT_ALGORITHM_FRONTEND
      ELSE
        logger.warn("FrontendHashing: SHA3 library unavailable. Falling back to SHA-256.")
        effective_algorithm = "SHA-256"
      ENDIF
    ENDIF

    TRY
      text_encoder = NEW TextEncoder() // UTF-8
      data_buffer = text_encoder.encode(data_string)
      LET hash_hex_string : STRING

      IF effective_algorithm == "SHA3-256" THEN
        IF NOT SHA3_JS_LIBRARY_IS_AVAILABLE_AND_WORKING() THEN
          logger.error("FrontendHashing: SHA3-256 library unavailable when required.")
          THROW NEW FrontendHashingError("SHA3-256 library unavailable.")
        ENDIF
        TRY
          hash_hex_string = SHA3_JS_LIBRARY.calculate_digest_as_hex(data_buffer) // Placeholder
        CATCH LibraryError as lib_err
          logger.error("FrontendHashing: Error using SHA3-256 JS library: " + lib_err.message)
          THROW NEW FrontendHashingError("Failed to compute SHA3-256 hash: " + lib_err.message)
        END TRY
      ELSE IF effective_algorithm == "SHA-256" THEN
        TRY
          hash_buffer = AWAIT window.crypto.subtle.digest("SHA-256", data_buffer)
          hash_array = NEW Uint8Array(hash_buffer)
          hash_hex_string = ""
          FOR EACH byte_val IN hash_array DO
            hash_hex_string = hash_hex_string + TO_HEX_STRING(byte_val, 2) // Pad to 2 chars
          END FOR
        CATCH WebCryptoError as wc_err
          logger.error("FrontendHashing: Error using Web Crypto for SHA-256: " + wc_err.message)
          THROW NEW FrontendHashingError("Failed to compute SHA-256 hash: " + wc_err.message)
        END TRY
      ELSE
        logger.error("FrontendHashing: Internal error - reached unsupported algorithm state: " + effective_algorithm)
        THROW NEW FrontendHashingError("Internal error in frontend hashing.")
      ENDIF
      RETURN hash_hex_string
    CATCH AnyException as e
        logger.error("FrontendHashing: Unexpected error in calculateHash: " + e.message)
        THROW NEW FrontendHashingError("Unexpected frontend hashing error: " + e.message)
    END TRY
  END ASYNC FUNCTION

  // Conceptual helper
  FUNCTION SHA3_JS_LIBRARY_IS_AVAILABLE_AND_WORKING() RETURNS BOOLEAN
    // Checks if the SHA3 JS library is loaded, initialized, and usable.
    // RETURN (typeof SHA3_JS_LIBRARY !== 'undefined' && SHA3_JS_LIBRARY.isReady())
    RETURN true // Assume available for pseudocode clarity; tests would mock.
  END FUNCTION

END MODULE


## 5. Configuration Flow

MODULE PQC_Hashing_Configuration

  // Backend Configuration Loading:
  // 1. Fava application loads its global configuration.
  // 2. This configuration includes `pqc_hashing_algorithm: STRING` (Default: "SHA3-256").
  // 3. The `PQC_Hashing_Backend.get_hashing_service(fava_config_provider)` function is used to
  //    obtain an instance of `HashingService`, initialized based on this configuration value.

  // API Endpoint for Frontend Configuration:
  // An API endpoint (e.g., `/api/fava/settings` or `/api/crypto/config`) exposes the
  // configured `pqc_hashing_algorithm` to the frontend.

  // TEST: API_get_crypto_config_returns_correct_hashing_algorithm()
  //   SETUP: Fava backend configured with `pqc_hashing_algorithm = "SHA256"`.
  //   ACTION: Simulate frontend API call to fetch crypto config.
  //   ASSERT: API response payload contains `{"hashing_algorithm": "SHA256"}`.

  FUNCTION handle_get_crypto_config_request(fava_config_provider : FavaConfigurationProvider) RETURNS ApiResponse
    // INPUT: fava_config_provider to access current Fava settings.
    // OUTPUT: An ApiResponse object suitable for sending to the client.
    logger = GET_LOGGER_INSTANCE()
    TRY
      current_hashing_algo = fava_config_provider.get_string_option("pqc_hashing_algorithm", DEFAULT_ALGORITHM_BACKEND)
      // The name sent to frontend (e.g. "SHA256" or "SHA3-256") will be handled by frontend's calculateHash.
      response_data = CREATE_MAP({"hashing_algorithm": current_hashing_algo})
      RETURN NEW ApiResponse(HTTP_STATUS_OK, response_data)
    CATCH ConfigError as e
      logger.error("API: Error retrieving hashing_algorithm from config: " + e.message)
      response_data = CREATE_MAP({"error": "Failed to retrieve hashing configuration"})
      RETURN NEW ApiResponse(HTTP_STATUS_SERVER_ERROR, response_data)
    END TRY
  END FUNCTION

  // Frontend Configuration Fetching:
  // 1. Frontend application, on initialization or as needed, calls the API endpoint.
  // 2. The received `hashing_algorithm` string is stored and used when calling
  //    `PQC_Hashing_Frontend.calculateHash(data, received_algo_name)`.

  // TEST: Frontend_fetches_and_uses_hashing_algorithm_from_API()
  //   SETUP: Mock API to return `{"hashing_algorithm": "SHA3-256"}`. Spy on `PQC_Hashing_Frontend.calculateHash`.
  //   ACTION: Frontend logic (e.g., editor component init) fetches config and then triggers a hash calculation.
  //   ASSERT: `PQC_Hashing_Frontend.calculateHash` is called with "SHA3-256" as `algorithm_name_from_config`.

  MODULE Example_Frontend_SliceEditor_Integration_Conceptual
    PRIVATE configured_hash_algorithm_from_api : STRING
    PRIVATE logger : Logger

    ASYNC PROCEDURE initialize_editor_component()
      logger = GET_LOGGER_INSTANCE()
      this.configured_hash_algorithm_from_api = AWAIT fetch_hashing_config_setting_from_api()
    END ASYNC PROCEDURE

    ASYNC FUNCTION fetch_hashing_config_setting_from_api() RETURNS STRING
      TRY
        api_response = AWAIT HTTP_CLIENT.get("/api/crypto/config") // Placeholder for actual API call
        IF api_response.status == HTTP_STATUS_OK AND api_response.body.hashing_algorithm IS NOT NULL THEN
          logger.info("FrontendConfig: Received hashing algorithm: " + api_response.body.hashing_algorithm)
          RETURN api_response.body.hashing_algorithm
        ELSE
          logger.warn("FrontendConfig: Failed to fetch valid hashing config from API (Status: " + api_response.status + "). Defaulting to " + DEFAULT_ALGORITHM_FRONTEND)
          RETURN DEFAULT_ALGORITHM_FRONTEND
        ENDIF
      CATCH NetworkError as e
        logger.error("FrontendConfig: Network error fetching hashing config: " + e.message + ". Defaulting to " + DEFAULT_ALGORITHM_FRONTEND)
        RETURN DEFAULT_ALGORITHM_FRONTEND
      END TRY
    END ASYNC FUNCTION

    // Example usage:
    ASYNC FUNCTION handle_content_save(content_to_save : STRING)
      // ...
      client_side_hash = AWAIT PQC_Hashing_Frontend.calculateHash(content_to_save, this.configured_hash_algorithm_from_api)
      // ... send content_to_save and client_side_hash to backend for optimistic concurrency check.
    END ASYNC FUNCTION

  END MODULE

END MODULE