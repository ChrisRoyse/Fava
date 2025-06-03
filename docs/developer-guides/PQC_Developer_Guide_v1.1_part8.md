# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 8

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 8 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   Part 2: [PQC_Developer_Guide_v1.1_part2.md](PQC_Developer_Guide_v1.1_part2.md)
*   Part 3: [PQC_Developer_Guide_v1.1_part3.md](PQC_Developer_Guide_v1.1_part3.md)
*   Part 4: [PQC_Developer_Guide_v1.1_part4.md](PQC_Developer_Guide_v1.1_part4.md)
*   Part 5: [PQC_Developer_Guide_v1.1_part5.md](PQC_Developer_Guide_v1.1_part5.md)
*   Part 6: [PQC_Developer_Guide_v1.1_part6.md](PQC_Developer_Guide_v1.1_part6.md)
*   Part 7: [PQC_Developer_Guide_v1.1_part7.md](PQC_Developer_Guide_v1.1_part7.md)

This part continues detailing Fava's Cryptographic Agility Framework.

## 8. Cryptographic Agility Framework - Continued

### 8.2. Adding or Modifying Cryptographic Schemes

The agility framework facilitates adding or modifying schemes:

1.  **Define New Suite in `FAVA_CRYPTO_SETTINGS`:**
    *   Add a new entry to `data_at_rest.suites` with a unique `suite_id`.
    *   Specify parameters (KEMs, symmetric cipher, KDFs, PBKDF, key management mode).
2.  **Implement/Update `CryptoHandler` (Backend):**
    *   For new primitive combinations, adapt existing handlers (e.g., `HybridPqcCryptoHandler`).
    *   For entirely new primitives, create a new class implementing `CryptoHandler`.
    *   Update `BackendCryptoService` (in `src/fava/pqc/backend_crypto_service.py` or `src/fava/pqc/app_startup.py`) to recognize and instantiate the new/updated handler.

---
End of Part 8. More content will follow in Part 9.