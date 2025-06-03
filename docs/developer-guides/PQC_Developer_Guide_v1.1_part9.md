# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 9

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 9 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   ... (Parts 2-7) ...
*   Part 8: [PQC_Developer_Guide_v1.1_part8.md](PQC_Developer_Guide_v1.1_part8.md)

This part continues detailing Fava's Cryptographic Agility Framework, focusing on adding/modifying schemes.

## 8. Cryptographic Agility Framework - Continued

### 8.2. Adding or Modifying Cryptographic Schemes - Continued

Continuing from Part 8:

3.  **Update `decryption_attempt_order`:**
    *   If you want Fava to be able to decrypt files that were encrypted with this new suite (or an older suite you are now adding full support for), add the new `suite_id` to the `FAVA_CRYPTO_SETTINGS.data_at_rest.decryption_attempt_order` list.
    *   Consider its position in the list based on likelihood or preference (e.g., more common or recent suites earlier).
4.  **Set as `active_encryption_suite_id`:**
    *   To use the new suite for encrypting *new* files, update the `FAVA_CRYPTO_SETTINGS.data_at_rest.active_encryption_suite_id` setting to the `suite_id` of your new suite.
5.  **Hashing/WASM Integrity Agility:**
    *   **For new hash algorithms:**
        *   Update `FAVA_CRYPTO_SETTINGS.hashing.default_algorithm` if it's to be the new default.
        *   Add implementation logic to backend `HashingService` (in `src/fava/pqc/hashers.py` or `backend_crypto_service.py`).
        *   Add implementation logic to frontend `calculateHash` (in `frontend/src/lib/pqcCrypto.ts`). This might involve new JS library dependencies.
    *   **For new WASM signature algorithms:**
        *   Update `FAVA_CRYPTO_SETTINGS.wasm_integrity` settings (algorithm name, public key via `/api/pqc_config`).
        *   Update `PqcVerificationService` (in `frontend/src/lib/pqcCrypto.ts`) to use `liboqs-js` with the new algorithm.
        *   The build process for signing `tree-sitter-beancount.wasm` must be updated.

---
End of Part 9. More content will follow in Part 10.