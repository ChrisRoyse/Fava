# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 3

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 3 of the PQC Developer Guide.
*   Part 1 can be found [here](PQC_Developer_Guide_v1.1_part1.md).
*   Part 2 can be found [here](PQC_Developer_Guide_v1.1_part2.md).

This part focuses on how Fava can be made aware of PQC protection when operating behind a reverse proxy.

## 5. Data in Transit (PQC-TLS Proxy)

Fava's approach to securing data in transit with PQC relies on deploying Fava behind a reverse proxy that is PQC-TLS capable. Fava itself does not directly implement PQC-TLS cryptographic handshakes.

### 5.1. Fava's Awareness Mechanisms

While Fava doesn't handle the PQC-TLS itself, it can be made aware of the PQC protection status for logging or informational purposes. This is detailed in [`docs/architecture/PQC_Data_In_Transit_Arch.md`](../../docs/architecture/PQC_Data_In_Transit_Arch.md).

*   **HTTP Header Checking:**
    *   The PQC-capable reverse proxy can be configured to add a custom HTTP header to requests it forwards to Fava (e.g., `X-PQC-KEM: X25519Kyber768`).
    *   Fava's request handling logic (e.g., in middleware within [`src/fava/application.py`](../../src/fava/application.py)) can inspect incoming requests for such headers. This is primarily for logging.

*   **Configuration Flags:**
    *   An administrator can set a flag in Fava's configuration (e.g., `FAVA_CRYPTO_SETTINGS.data_in_transit.assume_pqc_tls_proxy = true`).
    *   This allows Fava to log or assume PQC protection even if specific headers are not present or configured on the proxy.

*   **Determining Effective PQC Status:**
    *   Fava can combine information from detected headers and configuration flags to determine an "effective PQC status."
    *   This status is primarily for logging. It does not change how Fava processes the actual content of requests or responses.

---
End of Part 3. More content will follow in Part 4.