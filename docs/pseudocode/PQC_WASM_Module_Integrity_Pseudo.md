# Pseudocode: PQC WASM Module Integrity

## 1. Overview

This document outlines the pseudocode for the frontend logic responsible for verifying the integrity of WebAssembly (WASM) modules using Post-Quantum Cryptography (PQC) signatures. Specifically, it details the verification of the `tree-sitter-beancount.wasm` module using the Dilithium3 PQC signature algorithm. This pseudocode is derived from the PQC WASM Module Integrity Specification ([`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](docs/specifications/PQC_WASM_Module_Integrity_Spec.md)).

## 2. Configuration Data (Conceptual)

// Corresponds to Spec Section 8.1: PQC WASM Verification Configuration
// This configuration is assumed to be accessible globally or via a dedicated configuration service/module.

CONSTANT PQC_WASM_CONFIG: Object
  pqcWasmVerificationEnabled: BOOLEAN // Default: TRUE. Enables/disables PQC verification. (FR2.9)
  pqcWasmPublicKeyDilithium3Base64: STRING // Base64 encoded Dilithium3 public key. (FR2.2, FR2.8)
  pqcWasmSignatureAlgorithmName: STRING // Fixed to "Dilithium3" for this version. (FR2.8)
  wasmModulePath: STRING // Path to the WASM module, e.g., "/assets/tree-sitter-beancount.wasm"
  wasmSignaturePathSuffix: STRING // Suffix for the signature file, e.g., ".dilithium3.sig". (FR2.3)
END CONSTANT

## 3. Core PQC Verification Logic (Equivalent to `frontend/src/lib/pqcCrypto.ts`)

// Corresponds to Spec Section 10.1. This section defines the function responsible for the actual PQC signature verification.

FUNCTION verifyPqcWasmSignature(wasmBuffer: ARRAY_BUFFER, signatureBuffer: ARRAY_BUFFER, publicKeyBase64: STRING, algorithmName: STRING) RETURNS BOOLEAN
  // INPUT: wasmBuffer: ArrayBuffer containing the binary data of the WASM module.
  // INPUT: signatureBuffer: ArrayBuffer containing the PQC signature of the WASM module.
  // INPUT: publicKeyBase64: String containing the Base64 encoded PQC public key.
  // INPUT: algorithmName: String specifying the PQC algorithm to use (e.g., "Dilithium3").
  // OUTPUT: TRUE if the signature is valid, FALSE otherwise.
  // This function encapsulates FR2.5.

  // TEST: test_verifyPqcWasmSignature_dilithium3_valid_signature_returns_true() (Based on Spec 10.1)
  //   SETUP: Provide valid wasmBuffer, corresponding valid signatureBuffer (Dilithium3), and correct publicKeyBase64. Mock underlying PQC library's `verify` method to return TRUE.
  //   ACTION: Call `verifyPqcWasmSignature` with these inputs and algorithmName "Dilithium3".
  //   ASSERT: The function returns TRUE.

  // TEST: test_verifyPqcWasmSignature_dilithium3_invalid_signature_returns_false() (Based on Spec 10.1)
  //   SETUP: Provide valid wasmBuffer, an INVALID signatureBuffer, and correct publicKeyBase64. Mock PQC library's `verify` method to return FALSE.
  //   ACTION: Call `verifyPqcWasmSignature` with these inputs and algorithmName "Dilithium3".
  //   ASSERT: The function returns FALSE.

  // TEST: test_verifyPqcWasmSignature_dilithium3_tampered_wasm_returns_false()
  //   SETUP: Provide a tamperedWasmBuffer, the original valid signatureBuffer, and correct publicKeyBase64. Mock PQC library's `verify` method to return FALSE.
  //   ACTION: Call `verifyPqcWasmSignature` with tampered WASM and algorithmName "Dilithium3".
  //   ASSERT: The function returns FALSE.

  // TEST: test_verifyPqcWasmSignature_dilithium3_wrong_public_key_returns_false()
  //   SETUP: Provide valid wasmBuffer, valid signatureBuffer, but an incorrect publicKeyBase64. Mock PQC library's `verify` method to return FALSE.
  //   ACTION: Call `verifyPqcWasmSignature` with the wrong public key and algorithmName "Dilithium3".
  //   ASSERT: The function returns FALSE.

  // TEST: test_verifyPqcWasmSignature_unsupported_algorithm_returns_false()
  //   SETUP: Provide any wasmBuffer, signatureBuffer, publicKeyBase64. Set algorithmName to "UnsupportedAlgorithm".
  //   ACTION: Call `verifyPqcWasmSignature` with "UnsupportedAlgorithm".
  //   ASSERT: The function returns FALSE and logs an error about the unsupported algorithm.

  // TEST: test_verifyPqcWasmSignature_public_key_decoding_failure_returns_false() (EC6.2 partial)
  //   SETUP: Provide valid wasmBuffer, signatureBuffer. Provide an invalid publicKeyBase64 string that cannot be decoded.
  //   ACTION: Call `verifyPqcWasmSignature`.
  //   ASSERT: The function returns FALSE and logs an error about public key decoding.

  LOG "Attempting PQC signature verification. Algorithm: " + algorithmName
  IF algorithmName IS NOT "Dilithium3" THEN
    LOG_ERROR "Unsupported PQC algorithm specified for WASM verification: " + algorithmName
    RETURN FALSE
  END IF

  TRY
    // Step 1: Obtain an instance of the PQC verifier from the PQC library (e.g., liboqs-js).
    // This is a conceptual representation; actual library usage may vary.
    // `GET_PQC_LIBRARY_VERIFIER_FOR_ALGORITHM` might involve initialization if not already done.
    LET pqcVerifier = GET_PQC_LIBRARY_VERIFIER_FOR_ALGORITHM(algorithmName)
    IF pqcVerifier IS NULL OR pqcVerifier IS INVALID THEN
        LOG_ERROR "Failed to obtain/initialize PQC verifier for algorithm: " + algorithmName // (EC6.3 related)
        RETURN FALSE
    END IF

    // Step 2: Decode the Base64 public key into a byte array.
    LET publicKeyBytes = DECODE_BASE64_TO_BYTE_ARRAY(publicKeyBase64)
    IF publicKeyBytes IS NULL OR publicKeyBytes.length IS 0 THEN
      LOG_ERROR "PQC public key decoding failed or resulted in an empty key."
      RETURN FALSE // (EC6.2)
    END IF

    // Step 3: Convert input ArrayBuffers to byte arrays suitable for the PQC library.
    LET messageBytes = NEW_BYTE_ARRAY_FROM_ARRAY_BUFFER(wasmBuffer)
    LET signatureBytes = NEW_BYTE_ARRAY_FROM_ARRAY_BUFFER(signatureBuffer)

    // Step 4: Perform the signature verification using the PQC library.
    // This is the core cryptographic operation, e.g., `pqcVerifier.verify(messageBytes, signatureBytes, publicKeyBytes)`
    LET isVerified = pqcVerifier.VERIFY(messageBytes, signatureBytes, publicKeyBytes)

    IF isVerified THEN
      LOG_INFO "PQC signature VERIFIED successfully for algorithm: " + algorithmName
    ELSE
      LOG_WARNING "PQC signature verification FAILED for algorithm: " + algorithmName
    END IF
    RETURN isVerified

  CATCH error
    LOG_ERROR "Exception during PQC signature verification: " + error.message
    RETURN FALSE
  END TRY
END FUNCTION

## 4. WASM Loader Integration (Equivalent to `frontend/src/codemirror/beancount.ts` modifications)

// Corresponds to Spec Section 10.2. This function orchestrates the loading and verification of the WASM module.

FUNCTION loadBeancountParserWithPQCVerification() RETURNS WASM_MODULE_INSTANCE OR NULL
  // OUTPUT: An instance of the loaded Beancount WASM parser, or NULL if loading or verification fails.

  // TEST: test_loadBeancountParser_verificationEnabled_validSig_succeeds() (Based on Spec 10.2)
  //   SETUP: `PQC_WASM_CONFIG.pqcWasmVerificationEnabled` = TRUE. Mock successful fetch for WASM & valid signature. Mock `verifyPqcWasmSignature` to return TRUE. Mock `LOAD_WASM_MODULE_FROM_BUFFER` to return a valid instance.
  //   ACTION: Call `loadBeancountParserWithPQCVerification()`.
  //   ASSERT: Returns a valid WASM_MODULE_INSTANCE. `LOAD_WASM_MODULE_FROM_BUFFER` called with correct buffer. Success logged.

  // TEST: test_loadBeancountParser_verificationEnabled_invalidSig_fails() (FR2.7)
  //   SETUP: `PQC_WASM_CONFIG.pqcWasmVerificationEnabled` = TRUE. Mock successful fetch for WASM & signature. Mock `verifyPqcWasmSignature` to return FALSE.
  //   ACTION: Call `loadBeancountParserWithPQCVerification()`.
  //   ASSERT: Returns NULL. Error logged. `NOTIFY_UI_DEGRADED_FUNCTIONALITY` called. `LOAD_WASM_MODULE_FROM_BUFFER` NOT called.

  // TEST: test_loadBeancountParser_verificationDisabled_succeeds_bypassing_verification() (FR2.9)
  //   SETUP: `PQC_WASM_CONFIG.pqcWasmVerificationEnabled` = FALSE. Mock successful fetch for WASM. Mock `LOAD_WASM_MODULE_FROM_BUFFER` to return a valid instance.
  //   ACTION: Call `loadBeancountParserWithPQCVerification()`.
  //   ASSERT: Returns a valid WASM_MODULE_INSTANCE. `verifyPqcWasmSignature` is NOT called. Warning logged.

  // TEST: test_loadBeancountParser_wasmFetchFail_fails() (EC6.4)
  //   SETUP: `PQC_WASM_CONFIG.pqcWasmVerificationEnabled` = TRUE. Mock `FETCH` for WASM to fail.
  //   ACTION: Call `loadBeancountParserWithPQCVerification()`.
  //   ASSERT: Returns NULL. Error logged. `NOTIFY_UI_DEGRADED_FUNCTIONALITY` called.

  // TEST: test_loadBeancountParser_signatureFetchFail_fails() (EC6.1, EC6.4)
  //   SETUP: `PQC_WASM_CONFIG.pqcWasmVerificationEnabled` = TRUE. Mock `FETCH` for WASM succeeds. Mock `FETCH` for signature to fail.
  //   ACTION: Call `loadBeancountParserWithPQCVerification()`.
  //   ASSERT: Returns NULL. Error logged. `NOTIFY_UI_DEGRADED_FUNCTIONALITY` called.

  // TEST: test_loadBeancountParser_missingPublicKeyConfig_fails() (EC6.2)
  //   SETUP: `PQC_WASM_CONFIG.pqcWasmVerificationEnabled` = TRUE. `PQC_WASM_CONFIG.pqcWasmPublicKeyDilithium3Base64` is NULL or empty.
  //   ACTION: Call `loadBeancountParserWithPQCVerification()`.
  //   ASSERT: Returns NULL. Error logged. `NOTIFY_UI_DEGRADED_FUNCTIONALITY` called.

  // TEST: test_loadBeancountParser_pqcLibraryInitFailure_fails() (EC6.3, handled by verifyPqcWasmSignature)
  //   SETUP: `PQC_WASM_CONFIG.pqcWasmVerificationEnabled` = TRUE. Mock successful fetch. Mock `verifyPqcWasmSignature` to effectively fail due to PQC library issues (e.g., `GET_PQC_LIBRARY_VERIFIER_FOR_ALGORITHM` returns NULL).
  //   ACTION: Call `loadBeancountParserWithPQCVerification()`.
  //   ASSERT: Returns NULL. Error logged (from `verifyPqcWasmSignature` or loader). `NOTIFY_UI_DEGRADED_FUNCTIONALITY` called.

  LET config = GET_PQC_WASM_CONFIG_VALUES() // Access the application's PQC configuration.

  // FR2.9: Check if PQC verification is disabled by configuration.
  IF config.pqcWasmVerificationEnabled IS FALSE THEN
    LOG_WARNING "PQC WASM signature verification is DISABLED via configuration. Loading WASM module directly."
    // TEST_ANCHOR: Direct WASM loading path when verification is disabled.
    TRY
      LET wasmPath = config.wasmModulePath
      LOG_INFO "Fetching WASM module (verification disabled): " + wasmPath
      LET wasmResponse = ASYNCHRONOUSLY FETCH(wasmPath)
      IF wasmResponse.ok IS FALSE THEN
        LOG_ERROR "Failed to fetch WASM module (verification disabled): " + wasmPath + ". Status: " + wasmResponse.status
        THROW NEW Error("WASM Fetch Failed (verification disabled)")
      END IF
      LET wasmBuffer = ASYNCHRONOUSLY wasmResponse.GET_ARRAY_BUFFER()
      LET wasmInstance = ASYNCHRONOUSLY LOAD_WASM_MODULE_FROM_BUFFER(wasmBuffer) // Actual WASM instantiation.
      LOG_INFO "WASM module loaded directly (PQC verification disabled): " + wasmPath
      RETURN wasmInstance
    CATCH error
      LOG_ERROR "Error loading WASM module directly (verification disabled): " + error.message
      NOTIFY_UI_DEGRADED_FUNCTIONALITY("WASM module could not be loaded (verification disabled).")
      RETURN NULL
    END TRY
  END IF

  // Proceed with PQC verification as it's enabled.
  LOG_INFO "PQC WASM signature verification is ENABLED. Starting process for: " + config.wasmModulePath
  TRY
    // FR2.2, FR2.8: Access public key from configuration.
    LET publicKeyBase64 = config.pqcWasmPublicKeyDilithium3Base64
    IF publicKeyBase64 IS NULL OR publicKeyBase64 IS EMPTY THEN
      LOG_ERROR "PQC WASM public key is not configured. Verification cannot proceed."
      THROW NEW Error("Missing PQC Public Key Configuration") // Implements EC6.2
    END IF

    LET wasmPath = config.wasmModulePath
    // FR2.3: Construct the signature file path.
    LET signaturePath = wasmPath + config.wasmSignaturePathSuffix

    // FR2.4: Asynchronously fetch the WASM binary and its PQC signature file.
    LOG_INFO "Fetching WASM module from: " + wasmPath
    LOG_INFO "Fetching PQC signature from: " + signaturePath
    // TEST_ANCHOR: Concurrent fetching of WASM module and its signature file.
    LET [wasmResponse, signatureResponse] = ASYNCHRONOUSLY PROMISE_ALL([
      FETCH(wasmPath),
      FETCH(signaturePath)
    ])

    IF wasmResponse.ok IS FALSE THEN
      LOG_ERROR "Failed to fetch WASM module: " + wasmPath + ". Status: " + wasmResponse.status
      THROW NEW Error("WASM Module Fetch Failed") // Implements EC6.4 (network error)
    END IF
    IF signatureResponse.ok IS FALSE THEN
      LOG_ERROR "Failed to fetch PQC signature: " + signaturePath + ". Status: " + signatureResponse.status
      THROW NEW Error("PQC Signature Fetch Failed") // Implements EC6.1 (file missing) and EC6.4 (network error)
    END IF

    LET wasmBuffer = ASYNCHRONOUSLY wasmResponse.GET_ARRAY_BUFFER()
    LET signatureBuffer = ASYNCHRONOUSLY signatureResponse.GET_ARRAY_BUFFER()

    // FR2.5: Verify the PQC signature.
    // TEST_ANCHOR: Invocation of the PQC signature verification function.
    LET isSignatureValid = ASYNCHRONOUSLY verifyPqcWasmSignature(
      wasmBuffer,
      signatureBuffer,
      publicKeyBase64,
      config.pqcWasmSignatureAlgorithmName // Expected to be "Dilithium3"
    )

    // FR2.6: Handle successful verification.
    IF isSignatureValid THEN
      LOG_INFO "WASM module '" + config.wasmModulePath + "' signature (" + config.pqcWasmSignatureAlgorithmName + ") VERIFIED successfully."
      // Proceed to load/initialize the WASM module using the fetched wasmBuffer.
      // TEST_ANCHOR: WASM module instantiation after successful PQC verification.
      LET wasmInstance = ASYNCHRONOUSLY LOAD_WASM_MODULE_FROM_BUFFER(wasmBuffer)
      LOG_INFO "WASM module instantiated successfully after PQC verification."
      RETURN wasmInstance
    ELSE
      // FR2.7: Handle failed verification.
      LOG_ERROR "WASM module '" + config.wasmModulePath + "' signature (" + config.pqcWasmSignatureAlgorithmName + ") verification FAILED. Module will NOT be loaded."
      // UI9.2: Inform the user about degraded functionality.
      NOTIFY_UI_DEGRADED_FUNCTIONALITY("Beancount syntax highlighting/parsing unavailable due to integrity check failure.")
      THROW NEW Error("WASM PQC Signature Verification Failed")
    END IF

  CATCH error
    LOG_ERROR "Error during PQC-verified WASM loading process: " + error.message
    // Ensure UI is notified if not already handled by a specific throw leading to notification.
    IF error.message IS NOT "WASM PQC Signature Verification Failed" AND 
       error.message IS NOT "Missing PQC Public Key Configuration" AND
       error.message IS NOT "WASM Module Fetch Failed" AND
       error.message IS NOT "PQC Signature Fetch Failed" THEN
        NOTIFY_UI_DEGRADED_FUNCTIONALITY("WASM module loading failed due to an unexpected error.")
    END IF
    RETURN NULL
  END TRY
END FUNCTION

## 5. Helper/Utility Function Stubs (Conceptual)

// These are stubs for functions that would interact with platform/library-specific APIs.

FUNCTION GET_PQC_WASM_CONFIG_VALUES() RETURNS PQC_WASM_CONFIG
  // Retrieves the PQC_WASM_CONFIG object.
  // In a real implementation, this might read from a global store, a service, or build-time injected variables.
  // TEST: test_GET_PQC_WASM_CONFIG_VALUES_returns_expected_configuration_object()
  RETURN PQC_WASM_CONFIG // Access the defined CONSTANT or its runtime equivalent.
END FUNCTION

FUNCTION DECODE_BASE64_TO_BYTE_ARRAY(base64String: STRING) RETURNS BYTE_ARRAY
  // Placeholder for a platform/library function to decode Base64 string to a byte array (e.g., Uint8Array).
  // TEST: test_DECODE_BASE64_TO_BYTE_ARRAY_decodes_valid_string_correctly()
  // TEST: test_DECODE_BASE64_TO_BYTE_ARRAY_handles_invalid_string_gracefully_returns_null_or_throws()
  RETURN PLATFORM_SPECIFIC_BASE64_DECODE(base64String)
END FUNCTION

FUNCTION NEW_BYTE_ARRAY_FROM_ARRAY_BUFFER(buffer: ARRAY_BUFFER) RETURNS BYTE_ARRAY
  // Placeholder for converting an ArrayBuffer to a PQC library-compatible byte array format (e.g., Uint8Array).
  // TEST: test_NEW_BYTE_ARRAY_FROM_ARRAY_BUFFER_creates_correct_byte_array()
  RETURN NEW Uint8Array(buffer) // Common JavaScript approach
END FUNCTION

FUNCTION LOAD_WASM_MODULE_FROM_BUFFER(wasmBuffer: ARRAY_BUFFER) RETURNS WASM_MODULE_INSTANCE
  // Placeholder for the actual WASM module instantiation logic.
  // This is highly dependent on the specific WASM module and how it's used (e.g., `WebAssembly.instantiate`, `tree-sitter` API).
  // Example from spec: `await Parser.init(); const lang = await Parser.Language.load(wasmBuffer); return lang;`
  // TEST: test_LOAD_WASM_MODULE_FROM_BUFFER_instantiates_module_successfully_from_valid_buffer()
  // TEST: test_LOAD_WASM_MODULE_FROM_BUFFER_handles_instantiation_failure_from_invalid_buffer()
  LOG_INFO "Attempting to instantiate WASM module from provided buffer..."
  // ... platform/library-specific WASM loading code ...
  LET instance = PLATFORM_SPECIFIC_WASM_LOADER(wasmBuffer)
  LOG_INFO "WASM module instantiation process completed."
  RETURN instance
END FUNCTION

FUNCTION NOTIFY_UI_DEGRADED_FUNCTIONALITY(message: STRING)
  // Placeholder for notifying the user via the UI about degraded functionality (UI9.2).
  // Could involve dispatching an event, calling a UI service, updating a reactive store state, etc.
  // TEST: test_NOTIFY_UI_DEGRADED_FUNCTIONALITY_triggers_appropriate_ui_update_or_log_for_testing()
  LOG_WARNING "UI Notification Required: " + message
  // ... code to trigger UI update (e.g., display a toast, update status message) ...
END FUNCTION

FUNCTION GET_PQC_LIBRARY_VERIFIER_FOR_ALGORITHM(algorithmName: STRING) RETURNS PQC_VERIFIER_INSTANCE
  // Placeholder for obtaining/initializing a PQC verifier object from the chosen PQC library (e.g., liboqs-js).
  // This might involve calling an initialization function if the library isn't globally initialized,
  // or creating a new verifier instance for the specified algorithm.
  // Conceptual example for liboqs-js: `new OQS.Signature(algorithmName)`
  // TEST: test_GET_PQC_LIBRARY_VERIFIER_FOR_ALGORITHM_returns_valid_verifier_for_Dilithium3()
  // TEST: test_GET_PQC_LIBRARY_VERIFIER_FOR_ALGORITHM_handles_failure_for_unsupported_algorithm_or_init_error()
  IF algorithmName IS "Dilithium3" THEN
    // This is where the actual PQC library (like liboqs-js) would be invoked.
    // It might involve asynchronous loading of the library itself if not already done.
    LET verifierInstance = NEW_PQC_LIBRARY_SIGNATURE_VERIFIER(algorithmName) // Conceptual
    IF verifierInstance IS VALID THEN
        RETURN verifierInstance
    ELSE
        LOG_ERROR "Failed to initialize PQC verifier instance for " + algorithmName + " from library."
        RETURN NULL // Or throw an error
    END IF
  ELSE
    LOG_ERROR "Attempted to get verifier for unsupported algorithm: " + algorithmName
    RETURN NULL // Or throw an error
  END IF
END FUNCTION

## 6. Build Process Stubs (Conceptual - For Context, Not Frontend Logic)

// Corresponds to Spec Section 10.3. These are NOT frontend pseudocode but describe
// the necessary build-time actions to support the frontend verification.

PROCEDURE GENERATE_PQC_SIGNED_WASM_AND_CONFIG_FILES
  // INPUT: wasmFilePath (e.g., "frontend/public/tree-sitter-beancount.wasm")
  // INPUT: privateKeyPath (e.g., "secure/fava_dilithium3_private.key")
  // INPUT: algorithmName (e.g., "Dilithium3")
  // INPUT: outputSignatureDirectory (e.g., "frontend/public/")
  // INPUT: outputFrontendConfigPath (e.g., "frontend/src/generated/pqcWasmConfig.ts")
  // GOAL: To sign the WASM module, create its signature file, and generate a frontend
  //       configuration file containing the public key and other settings. (FR2.1)

  // TEST (Build Process): test_build_process_generates_dilithium3_signature_and_config_file_correctly() (Matches Spec 10.3)
  //   ACTION: Execute the `GENERATE_PQC_SIGNED_WASM_AND_CONFIG_FILES` procedure with appropriate inputs.
  //   ASSERT: A signature file (e.g., `tree-sitter-beancount.wasm.dilithium3.sig`) is created in `outputSignatureDirectory`.
  //   ASSERT: The frontend config file at `outputFrontendConfigPath` is created and contains the correct Base64 encoded public key, `pqcWasmVerificationEnabled: true`, and `pqcWasmSignatureAlgorithmName: "Dilithium3"`.

  // Step 1: Sign the WASM file using a PQC command-line tool or script.
  LET signatureFilename = BASENAME(wasmFilePath) + ".dilithium3.sig" // Example, matches config
  LET outputSignaturePath = CONCAT(outputSignatureDirectory, signatureFilename)
  // COMMAND_LINE_EXECUTE: pqc_signing_tool_cli --algorithm algorithmName \
  //                                          --private_key privateKeyPath \
  //                                          --input_file wasmFilePath \
  //                                          --output_signature_file outputSignaturePath
  LOG_BUILD "WASM file signed. Signature saved to: " + outputSignaturePath

  // Step 2: Extract the public key from the private key and encode it as Base64.
  // COMMAND_LINE_EXECUTE: pqc_pubkey_export_tool_cli --private_key privateKeyPath \
  //                                                 --algorithm algorithmName \
  //                                                 --output_format base64 \
  //                                                 -> extractedPublicKeyBase64
  LOG_BUILD "Public key extracted and Base64 encoded."

  // Step 3: Generate the frontend configuration file.
  LET configFileContent = FORMAT_STRING(
    "export const favaPqcWasmConfig = {\n" +
    "  pqcWasmVerificationEnabled: true,\n" +
    "  pqcWasmPublicKeyDilithium3Base64: \"{0}\",\n" +
    "  pqcWasmSignatureAlgorithmName: \"{1}\",\n" +
    "  wasmModulePath: \"/path/to/{2}\",\n" + // Relative path for frontend
    "  wasmSignaturePathSuffix: \".{1}.sig\"\n" +
    "};\n",
    extractedPublicKeyBase64,
    algorithmName, // "Dilithium3"
    BASENAME(wasmFilePath) // e.g. "tree-sitter-beancount.wasm"
  )
  WRITE_FILE(outputFrontendConfigPath, configFileContent)
  LOG_BUILD "Frontend PQC configuration file generated at: " + outputFrontendConfigPath
END PROCEDURE