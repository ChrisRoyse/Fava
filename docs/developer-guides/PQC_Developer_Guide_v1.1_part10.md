# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 10

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 10 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   ... (Parts 2-8) ...
*   Part 9: [PQC_Developer_Guide_v1.1_part9.md](PQC_Developer_Guide_v1.1_part9.md)

This part continues detailing Fava's Cryptographic Agility Framework.

## 8. Cryptographic Agility Framework - Continued

### 8.2. Adding or Modifying Cryptographic Schemes - Continued

Continuing from Part 9:

6.  **Testing:**
    *   Thoroughly test the new configuration and any new handler implementations. This includes:
        *   Granular tests for the new `CryptoHandler` (if a new class was created).
        *   Integration tests to ensure Fava can encrypt and decrypt data correctly with the new suite.
        *   Tests to verify correct fallback behavior if `decryption_attempt_order` is modified and multiple suites are involved.
        *   Specific tests for new hashing algorithms or WASM signature verification schemes, ensuring both backend and frontend components behave as expected.

### 8.3. Management of Multiple Decryption Suites for Data at Rest

Fava's ability to handle files encrypted with different cryptographic schemes over time is a key aspect of its cryptographic agility. This is crucial as cryptographic standards evolve or if users have files encrypted with older Fava PQC configurations.

*   **`suite_id_used` in `EncryptedFileBundle`:**
    *   As detailed in Part 2 (Section 3.4 of the overall guide, referring to the `EncryptedFileBundle` structure), when Fava encrypts a file using its PQC hybrid scheme, the `suite_id` of the `active_encryption_suite_id` (from `FAVA_CRYPTO_SETTINGS`) used at the time of encryption is stored within the `EncryptedFileBundle` metadata. This `suite_id_used` field is a string identifier like "HYBRID_X25519_MLKEM768_AES256GCM".

*   **Targeted Decryption Attempt:**
    *   When Fava attempts to decrypt a file, its first strategy is to look for this `suite_id_used` metadata within the file's header or bundle structure.
    *   If a `suite_id_used` is successfully parsed from the file, Fava requests the specific `CryptoHandler` corresponding to that `suite_id` from the `BackendCryptoService`.
    *   A decryption attempt is then made using this directly identified handler. This is the most efficient approach, as it avoids trial-and-error with multiple handlers.

---
End of Part 10. More content will follow in Part 11.