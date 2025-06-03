# Fava Post-Quantum Cryptography (PQC) Developer Guide v1.1 - Part 4

**Version:** 1.1
**Date:** 2025-06-03
**Audience:** Software developers contributing to Fava or integrating with its PQC features.

This document is Part 4 of the PQC Developer Guide.
*   Part 1: [PQC_Developer_Guide_v1.1_part1.md](PQC_Developer_Guide_v1.1_part1.md)
*   Part 2: [PQC_Developer_Guide_v1.1_part2.md](PQC_Developer_Guide_v1.1_part2.md)
*   Part 3: [PQC_Developer_Guide_v1.1_part3.md](PQC_Developer_Guide_v1.1_part3.md)

This part continues the discussion on Data in Transit, focusing on developer considerations.

## 5. Data in Transit (PQC-TLS Proxy) - Continued

### 5.2. Developer Considerations for Secure Operation with a Proxy

When Fava is deployed behind a PQC-TLS capable reverse proxy, developers must be mindful of the following for a secure setup:

*   **Trusted Proxy-Fava Link (CRITICAL):**
    *   The default communication between the reverse proxy and the Fava application server is plain HTTP.
    *   **This link MUST be secured if the proxy and Fava are not running on the same isolated host or within a trusted private network segment.** If this link traverses a shared or untrusted network, it becomes a vulnerability.
    *   **Recommended methods to secure this internal link:**
        1.  **Configure Fava for HTTPS (Classical TLS):** Fava itself can be configured to listen on HTTPS using standard TLS (e.g., with a self-signed certificate or one issued by an internal CA if appropriate for the trusted segment). The reverse proxy would then connect to Fava via HTTPS.
        2.  **Mutual TLS (mTLS):** For stronger authentication, mTLS can be set up between the proxy and Fava, ensuring both parties verify each other's certificates.
        3.  **IPSec or Secure Tunnel:** Use network-layer encryption like IPSec to create a secure tunnel for traffic between the proxy and Fava hosts.
        4.  **Strictly Localhost Communication:** If the proxy and Fava are on the same machine, ensure communication is strictly bound to `localhost` interfaces and firewall rules prevent external access to Fava's direct port.
    *   **Consequence of Inaction:** Failure to secure this internal link in an untrusted environment exposes unencrypted Fava data and communications between the proxy and the application, undermining the end-to-end PQC protection provided to the client.

*   **Proxy Configuration Documentation:**
    *   Developers contributing to Fava's official documentation must ensure that guides for configuring reverse proxies (e.g., Nginx, Caddy) are accurate and promote best practices for PQC-TLS.
    *   This includes recommending specific PQC hybrid KEMs (e.g., `X25519Kyber768`), TLS 1.3, use of classical certificates (as PQC certificates are not yet standard), and correct proxying to the Fava backend.
    *   Guidance on optionally setting a custom HTTP header (e.g., `X-PQC-KEM`) by the proxy (for Fava's awareness mechanism) should also be included.

*   **Fava's Logging:**
    *   Implement logging within Fava (e.g., in [`src/fava/application.py`](../../src/fava/application.py)) to record the detected PQC status (based on headers/config as discussed in Part 3). This helps administrators verify their PQC-TLS setup from Fava's perspective.
    *   Remind administrators in documentation that proxy server logs remain the primary source for detailed TLS handshake information and debugging PQC-TLS issues.

*   **No Direct PQC-TLS Implementation in Fava Core (for Proxy Deployments):**
    *   When Fava is deployed behind a reverse proxy for PQC-TLS, developers should **not** add PQC-TLS handshake or cryptographic logic into Fava's core HTTP handling for client-facing connections. Fava should continue to operate as a standard HTTP application in this setup, relying on the proxy for PQC-TLS termination.
    *   Any future considerations for direct PQC-TLS support in Fava's embedded server would be a separate architectural concern and deployment model, distinct from the primary reverse-proxy strategy.

---
End of Part 4. More content will follow in Part 5.