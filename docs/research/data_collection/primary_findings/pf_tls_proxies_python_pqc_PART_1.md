# Primary Findings: PQC in TLS - Reverse Proxies & Python Servers - Part 1

**Date of Research:** 2025-06-02
**Source(s):** Perplexity AI Search (Query: "PQC support in reverse proxies (Nginx, Apache, Caddy) for TLS 1.3, including hybrid KEMs like X25519Kyber768. Configuration steps for PQC cipher suites. PQC support status in Python web servers (Cheroot, Flask dev server) and Python ssl module via OpenSSL versions for PQC.", Detailed Level) - *Citations in text refer to Perplexity's internal source numbering from the search result.*

This document summarizes initial findings on Post-Quantum Cryptography (PQC) support for TLS 1.3 in common reverse proxies and Python web server environments.

## 1. PQC Support in Reverse Proxies

The PQC capabilities of reverse proxies like Nginx, Apache, and Caddy are heavily dependent on the underlying SSL/TLS library, typically OpenSSL. Support for PQC, especially hybrid Key Encapsulation Mechanisms (KEMs) like X25519Kyber768, generally requires OpenSSL 3.2 or newer.

*   **Nginx:**
    *   Requires OpenSSL 3.2+ for robust hybrid KEM support.
    *   Experimental builds might be needed for full integration of specific PQC KEMs like ML-KEM-768 [5].
    *   **Example Configuration Snippet (Illustrative for X25519Kyber768):**
        ```nginx
        ssl_protocols TLSv1.3;
        ssl_ciphers TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256; // Base TLS 1.3 ciphers
        ssl_ecdh_curve X25519:Kyber768; // For hybrid key exchange
        ```
*   **Apache HTTP Server:**
    *   Native PQC support is limited until OpenSSL 3.2+ becomes standard in distributed versions.
    *   Workarounds might involve configuring existing strong classical cipher suites while awaiting broader PQC integration.
    *   **Example Configuration Snippet (Classical TLS 1.3, PQC would be similar if OpenSSL supports it):**
        ```apache
        SSLCipherSuite TLS_AES_256_GCM_SHA384:ECDHE-ECDSA-AES256-GCM-SHA384
        SSLHonorCipherOrder on
        SSLProtocol TLSv1.3
        # PQC-specific cipher strings would be added here when supported
        ```
*   **Caddy:**
    *   Caddy's automatic TLS management can make PQC customization complex.
    *   Requires compile-time integration with an OpenSSL 3.2+ version that has PQC enabled.
    *   **Example Configuration Snippet (Illustrative for X25519Kyber768):**
        ```caddy
        tls {
            protocols tls1.3
            ciphers TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256
            curves x25519_kyber768 // For hybrid key exchange
        }
        ```

## 2. Hybrid KEM Implementation (e.g., X25519Kyber768)

Hybrid KEMs combine a classical key exchange mechanism (like X25519) with a PQC KEM (like CRYSTALS-Kyber) to provide security against both classical and quantum adversaries [4].

*   **Handshake Overhead:** PQC KEMs, even in hybrid modes, increase the size of TLS handshake messages. For X25519Kyber768, this can add approximately 2.4KB [5].
*   **Security Rationale:** The connection remains secure if either the classical or the PQC component remains unbroken.
*   **Performance:** Benchmarks indicate a 15-20% increase in handshake latency for X25519Kyber768 compared to using X25519 alone [4].

## 3. PQC Support in the Python Ecosystem

Python's `ssl` module and web servers built upon it also depend on the system's OpenSSL version.

*   **Python `ssl` Module:**
    *   Requires linking against an OpenSSL 3.2+ library compiled with PQC support.
    *   **Example Code Snippet (Illustrative for configuring a context):**
        ```python
        import ssl
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # Base TLS 1.3 ciphers
        ctx.set_ciphers('TLS_AES_256_GCM_SHA384:ECDHE-ECDSA-AES256-GCM-SHA384')
        # Attempt to set hybrid curve (actual availability depends on OpenSSL & Python linkage)
        # The exact string for PQC curves/groups might vary or require newer Python versions.
        # For OpenSSL 3.2+, one might try to enable groups like 'X25519_KYBER768' if exposed.
        # ctx.set_ecdh_curve('X25519:Kyber768') # This syntax is more for older OpenSSL style curves
        # For OpenSSL 3.0+ groups:
        # ctx.set_groups(['X25519', 'kyber768']) # Hypothetical, actual API may differ
        ```
        *Note: The exact Python `ssl` API to enable specific PQC KEM groups like Kyber768 with OpenSSL 3.2+ needs verification, as direct exposure of all new OpenSSL features can lag.*
*   **Python Web Servers:**
    *   **Cheroot (used by CherryPy):** Support is experimental and would require Cheroot to be running with a Python environment linked against a PQC-enabled OpenSSL 3.2+ (potentially via a patched build or specific pyOpenSSL configuration).
    *   **Flask Development Server:** Relies on the host system's Python `ssl` module and its linked OpenSSL. PQC support is therefore indirect and dependent on the environment.
    *   **Uvicorn/ASGI Servers:** May face challenges with larger PQC certificate sizes impacting asynchronous operations, though TLS termination is often handled by a reverse proxy in production.

## 4. General Deployment Considerations for PQC TLS

*   **Certificate Management:** PQC certificates are larger (e.g., ML-DSA-65 signature part alone is ~3.9KB vs. ECDSA's ~0.5KB for the entire certificate) [5], impacting storage and transmission.
*   **Backward Compatibility:** Hybrid modes are essential during the transition to support clients that do not yet have PQC capabilities.
*   **Hardware Acceleration:** For high-traffic servers, FIPS 140-3 Level 3 HSMs are recommended for secure storage and acceleration of PQC private key operations [2].
*   **Performance Impact:** Expect an 18-25% increase in TLS handshake latency with KEMs like Kyber768 [3].
*   **Overall Status:** PQC implementations in most open-source projects are still considered experimental. Production deployments (like Cloudflare's) often use custom-patched versions [1]. Full integration is generally awaiting further finalization of NIST standards and broader library support.

## 5. Identified Knowledge Gaps from this Search

*   **Specific PQC Cipher Suite Strings:** The exact cipher suite strings or group names to be used in Nginx, Apache, Caddy, or Python's `ssl` module for various NIST PQC KEMs (beyond X25519Kyber768) are not consistently detailed.
*   **Maturity of OpenSSL 3.2+ PQC Support:** While OpenSSL 3.2 adds PQC KEMs, the maturity and stability of these implementations for production server environments need further investigation.
*   **Python `ssl` Module API for PQC Groups:** Precise API calls in Python's `ssl` module to select and configure specific PQC KEM groups (e.g., different Kyber variants) beyond general curve settings.
*   **Practical Configuration Guides:** Detailed, validated configuration guides for setting up PQC TLS on common Linux distributions with specific versions of Nginx/Apache and OpenSSL.

*(This document will be updated or appended as more information is gathered.)*