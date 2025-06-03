# Primary Findings: PQC-TLS Reverse Proxies and Client Tools (Addressing Gap G4.2)

**Date Compiled:** 2025-06-02
**Research Focus:** G4.2: Maturity and stability of PQC-TLS enabled reverse proxies (e.g., OpenSSL 3.2+ with PQC, specific Nginx/Caddy builds). Availability of PQC-aware client tools for testing these proxies.
**Source:** AI Search (Perplexity MCP) - Query: "Maturity and stability of PQC-TLS enabled reverse proxies like Nginx or Caddy when compiled with PQC-capable OpenSSL (e.g., OpenSSL 3.2+ with OQS provider). Are there stable builds or official support? What is the availability of PQC-aware client tools (e.g., curl, OpenSSL s_client variants) for testing these PQC-TLS proxy setups? Cite project documentation, PQC community experiments, or security reports."

This document summarizes findings on the maturity, stability, and availability of PQC-TLS enabled reverse proxies and associated client testing tools.

## PQC-TLS Enabled Reverse Proxies

The integration of Post-Quantum Cryptography into TLS, particularly for key exchange, is an active area of development. Reverse proxies like Nginx and Caddy can support PQC-TLS by being compiled against PQC-capable TLS libraries, primarily OpenSSL configured with a PQC provider like the OQS (Open Quantum Safe) provider.

**1. Nginx with PQC-TLS:**

*   **Maturity & Stability:**
    *   Experimental. Official Nginx builds do not include PQC support out-of-the-box.
    *   Requires Nginx to be custom compiled with a version of OpenSSL that supports PQC (e.g., OpenSSL 3.2+ or 3.5+ linked with the OQS provider or `liboqs`).
    *   Cloudflare documentation suggests Nginx needs to be compiled with OpenSSL 3.5+ for robust PQC support.
    *   Community experiments (e.g., by Cromwell International, as cited in search results) demonstrate feasibility but highlight potential "quirks" and the need for careful configuration (e.g., setting `OPENSSL_CONF` environment variables correctly).
    *   Stability can be impacted by the experimental nature of the OQS provider and the specifics of the OpenSSL version used. Issues like those encountered when compiling Nginx with OpenSSL 3.2 for HTTP/3 suggest that integration isn't always seamless.
*   **Official Support:** No official PQC-enabled Nginx binaries. Support relies on community efforts and individual builds.
*   **Configuration Example (Conceptual):**
    ```nginx
    # nginx.conf
    http {
        server {
            listen 443 ssl http2;
            server_name pq.example.com;

            ssl_certificate         /path/to/pqc_hybrid_cert.pem; # May need hybrid certs
            ssl_certificate_key     /path/to/pqc_hybrid_key.pem;

            ssl_protocols           TLSv1.3;
            # Cipher suite configuration would depend on OpenSSL/OQS provider capabilities
            # e.g., ssl_ecdh_curve X25519Kyber768; (syntax may vary)
            # or specific PQC-enabled cipher suites if defined.
            # ssl_ciphers             <PQC_Hybrid_Cipher_Suite>:<Classical_Cipher_Suites>;
            ...
        }
    }
    ```

**2. Caddy with PQC-TLS:**

*   **Maturity & Stability:**
    *   Caddy v2.10.0+ is reported to support PQC when compiled against PQC-capable TLS libraries (OpenSSL 3.2+ or BoringSSL with PQC patches).
    *   However, user reports indicate potential stability issues or TLS handshake failures (e.g., `tlsv1 alert internal error`) when using Caddy with certain OpenSSL 3.2.x versions, possibly related to PQC configurations or bugs in the underlying TLS library.
    *   As with Nginx, stability is tied to the maturity of the PQC integrations in the TLS library Caddy uses.
*   **Official Support:** Caddy itself has shown willingness to support modern TLS features. Official support for PQC depends on its build process and the linked TLS library.
*   **Configuration Example (Conceptual Caddyfile):**
    ```caddyfile
    # Caddyfile
    pq.example.com {
        tls /path/to/pqc_hybrid_cert.pem /path/to/pqc_hybrid_key.pem {
            protocols tls1.3
            # Curve or group preference for PQC KEMs
            # e.g., curves X25519Kyber768 
            # or specific PQC-enabled cipher suites
        }
        reverse_proxy localhost:8080
    }
    ```

## Availability of PQC-Aware Client Tools for Testing

Testing PQC-TLS setups requires client tools that can negotiate PQC key exchange mechanisms.

*   **Web Browsers:**
    *   **Chrome:** Recent versions (e.g., Chrome 131+) have experimental support for certain hybrid PQC KEMs like `X25519Kyber768`. This is often enabled via flags or originates from experiments by entities like Cloudflare.
    *   **Firefox:** Similar to Chrome, recent versions (e.g., Firefox 132+) may include experimental PQC KEM support.
    *   **Edge:** Recent versions (e.g., Edge 131+) also reportedly support `X25519Kyber768`.
*   **Command-Line Tools:**
    *   **OpenSSL `s_client`:**
        *   Requires OpenSSL 3.2+ (preferably 3.5+ for better support) compiled with PQC capabilities (e.g., linked with `liboqs` or using the OQS provider 0.7.0+).
        *   Can be used to test specific PQC groups/KEMs:
            ```bash
            openssl s_client -connect pq.example.com:443 -groups X25519Kyber768
            # or for specific signature algorithms if testing certs:
            # openssl s_client -connect pq.example.com:443 -sigalgs_list dilithium3
            ```
    *   **`curl`:**
        *   Standard `curl` builds usually do not include PQC support.
        *   Requires `curl` to be compiled against a PQC-enabled TLS library (like a PQC-patched OpenSSL or BoringSSL). Cloudflare, for instance, uses a fork of Go (which `curl` can use for HTTP/3 and TLS) that includes PQC support.
*   **Other Tools/Libraries:**
    *   The OQS project provides example client applications and integrations (e.g., `oqs-openssl` demo applications) that can be used for testing.

## Summary and Key Risks:

*   **Maturity:** PQC-TLS in reverse proxies is still largely experimental and relies on custom builds and configurations. Official, stable, out-of-the-box PQC support in mainstream proxy distributions is not yet common.
*   **Stability:** Dependent on the stability of PQC implementations in underlying TLS libraries (OpenSSL, BoringSSL) and the OQS provider. Bugs or incompatibilities can arise.
*   **Client Tooling:** While PQC-aware client tools and browser support are emerging (especially for hybrid KEMs like X25519Kyber768), they are often tied to very recent versions or experimental flags. This can make comprehensive testing challenging.
*   **Standardization Lag:** The PQC algorithms themselves are standardized by NIST, but their integration into TLS (cipher suites, KEM identifiers) is still an ongoing IETF process. This can lead to interoperability issues as drafts evolve.
*   **Performance:** PQC operations, especially KEMs, can add latency to TLS handshakes compared to classical ECDHE. This needs to be considered and benchmarked.

For Fava, deploying PQC-TLS would currently mean relying on a self-managed, custom-built reverse proxy setup. This requires expertise in compiling Nginx/Caddy with PQC-enabled OpenSSL and keeping all components updated. Testing would primarily use PQC-enabled `openssl s_client` and modern browsers with experimental PQC features.

This information addresses knowledge gap G4.2 concerning PQC-TLS enabled reverse proxies and client tools.