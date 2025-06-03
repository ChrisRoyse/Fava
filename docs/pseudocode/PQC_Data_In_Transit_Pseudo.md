# Pseudocode: PQC Data in Transit for Fava

**Version:** 1.0
**Date:** 2025-06-02

## 0. Preamble and Assumptions

This pseudocode outlines Fava's internal logic related to operating behind a Post-Quantum Cryptography (PQC) enabled TLS reverse proxy. Fava itself **DOES NOT** implement PQC TLS handshakes or cryptographic operations for data in transit when a reverse proxy is used. Its role is primarily:
1.  To be potentially aware of the PQC protection status (via proxy headers or configuration).
2.  To provide comprehensive documentation for administrators on configuring reverse proxies for PQC TLS.
3.  (Future) To potentially allow configuration of PQC KEMs if its embedded web server and underlying Python libraries support them directly.

This pseudocode focuses on these aspects of awareness, documentation generation, and future configuration validation.

## 1. Module: FavaPQCProxyAwareness
// This module contains logic for Fava to determine or assert PQC protection status.

// **TDD Anchor:** TEST `check_pqc_proxy_headers` correctly identifies known PQC indicator header
// **TDD Anchor:** TEST `check_pqc_proxy_headers` returns UNKNOWN if no PQC indicator header is present
// **TDD Anchor:** TEST `check_pqc_proxy_headers` handles malformed PQC indicator header gracefully (returns UNKNOWN)
FUNCTION `check_pqc_proxy_headers`(request_headers)
    INPUT: request_headers (Dictionary of HTTP request headers)
    OUTPUT: String ("PQC_CONFIRMED_VIA_HEADER", "PQC_ABSENT_VIA_HEADER", "PQC_UNKNOWN_VIA_HEADER")

    // Example: Reverse proxy might add a header like "X-PQC-KEM: X25519Kyber768"
    // This is a hypothetical header; actual header name and values would depend on proxy implementation.
    DEFINE known_pqc_indicator_header_name AS "X-PQC-KEM" // Or other agreed-upon header
    DEFINE recognized_pqc_kems AS LIST ["X25519Kyber768", "Kyber768"] // Example KEMs

    IF known_pqc_indicator_header_name IS PRESENT in request_headers
        LET header_value = request_headers[known_pqc_indicator_header_name]
        // **TDD Anchor:** TEST `check_pqc_proxy_headers` correctly identifies `X25519Kyber768` from header
        IF header_value IS IN recognized_pqc_kems
            RETURN "PQC_CONFIRMED_VIA_HEADER"
        ELSE
            // Header present but value not recognized or indicates non-PQC
            // **TDD Anchor:** TEST `check_pqc_proxy_headers` returns `PQC_ABSENT_VIA_HEADER` if header value indicates classical KEM
            RETURN "PQC_ABSENT_VIA_HEADER" // Or a more specific status if header indicates classical
        END IF
    ELSE
        RETURN "PQC_UNKNOWN_VIA_HEADER"
    END IF
END FUNCTION

// **TDD Anchor:** TEST `get_pqc_status_from_config` returns `PQC_ASSUMED_ENABLED` if config flag is true
// **TDD Anchor:** TEST `get_pqc_status_from_config` returns `PQC_ASSUMED_DISABLED` if config flag is false or absent
FUNCTION `get_pqc_status_from_config`(fava_config)
    INPUT: fava_config (Fava's application configuration object)
    OUTPUT: String ("PQC_ASSUMED_ENABLED_VIA_CONFIG", "PQC_ASSUMED_DISABLED_VIA_CONFIG")

    // Example: A Fava config option like `assume_pqc_tls_proxy = true`
    DEFINE pqc_config_flag_name AS "assume_pqc_tls_proxy_enabled"

    IF fava_config CONTAINS pqc_config_flag_name AND fava_config[pqc_config_flag_name] IS TRUE
        RETURN "PQC_ASSUMED_ENABLED_VIA_CONFIG"
    ELSE
        RETURN "PQC_ASSUMED_DISABLED_VIA_CONFIG"
    END IF
END FUNCTION

// **TDD Anchor:** TEST `determine_effective_pqc_status` prioritizes header information over config
// **TDD Anchor:** TEST `determine_effective_pqc_status` falls back to config if header is UNKNOWN
// **TDD Anchor:** TEST `determine_effective_pqc_status` returns `PQC_STATUS_UNCERTAIN` if both header and config are non-conclusive
FUNCTION `determine_effective_pqc_status`(request_headers, fava_config)
    INPUT: request_headers, fava_config
    OUTPUT: String (e.g., "PQC_CONFIRMED_VIA_HEADER", "PQC_ASSUMED_ENABLED_VIA_CONFIG", "PQC_STATUS_UNCERTAIN")

    LET header_status = `check_pqc_proxy_headers`(request_headers)

    IF header_status IS "PQC_CONFIRMED_VIA_HEADER"
        RETURN "PQC_CONFIRMED_VIA_HEADER"
    ELSE IF header_status IS "PQC_ABSENT_VIA_HEADER"
        RETURN "PQC_ABSENT_VIA_HEADER"
    ELSE // header_status is "PQC_UNKNOWN_VIA_HEADER"
        LET config_status = `get_pqc_status_from_config`(fava_config)
        IF config_status IS "PQC_ASSUMED_ENABLED_VIA_CONFIG"
            RETURN "PQC_ASSUMED_ENABLED_VIA_CONFIG"
        ELSE
            RETURN "PQC_STATUS_UNCERTAIN" // Or "PQC_ASSUMED_DISABLED_VIA_CONFIG" if that's the default
        END IF
    END IF
END FUNCTION

## 2. Module: FavaDocumentationGenerator
// This module outlines logic for generating PQC-related documentation sections.
// The actual content is based on templates and current PQC research/recommendations.

// **TDD Anchor:** TEST `generate_pqc_tls_reverse_proxy_config_guide` for Nginx includes `X25519Kyber768`
// **TDD Anchor:** TEST `generate_pqc_tls_reverse_proxy_config_guide` for Caddy includes `X25519Kyber768`
// **TDD Anchor:** TEST `generate_pqc_tls_reverse_proxy_config_guide` includes disclaimer about experimental nature
// **TDD Anchor:** TEST `generate_pqc_tls_reverse_proxy_config_guide` includes link to OQS project or relevant resources
// **TDD Anchor:** TEST `generate_pqc_tls_reverse_proxy_config_guide` mentions classical certificates with hybrid KEMs
FUNCTION `generate_pqc_tls_reverse_proxy_config_guide`(proxy_type, kem_recommendation, relevant_research_docs)
    INPUT: proxy_type (String, e.g., "Nginx", "Caddy")
    INPUT: kem_recommendation (String, e.g., "X25519Kyber768")
    INPUT: relevant_research_docs (List of Strings, e.g., ["pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md"])
    OUTPUT: String (Markdown formatted documentation section)

    LET doc_content = ""
    APPEND "# Securing Fava with Post-Quantum TLS (Experimental) via " + proxy_type TO doc_content
    APPEND "\n\nTo protect Fava's data in transit against future quantum threats, configure your " + proxy_type + " reverse proxy to use Post-Quantum Cryptography (PQC) hybrid Key Encapsulation Mechanisms (KEMs) for TLS 1.3." TO doc_content
    APPEND "\nThe currently recommended hybrid KEM is `" + kem_recommendation + "`." TO doc_content
    APPEND "\nThis setup relies on experimental features in browsers and server software. Always consult the latest official documentation for " + proxy_type + ", OpenSSL (or its variant), and the OQS project." TO doc_content
    APPEND "\nRefer to Fava's research documents for more background: " + JOIN(relevant_research_docs, ", ") TO doc_content

    IF proxy_type IS "Nginx"
        APPEND "\n\n### Example: Nginx with OpenSSL (OQS Provider or PQC-enabled build)" TO doc_content
        APPEND "\nThis example assumes Nginx compiled with an OpenSSL version that supports `" + kem_recommendation + "`." TO doc_content
        APPEND "\n1. **Install/Compile PQC-enabled Nginx and OpenSSL.** (Refer to OQS project and Nginx documentation)." TO doc_content
        APPEND "\n2. **Configure Nginx:**" TO doc_content
        APPEND "\n   In your Nginx server block for Fava:" TO doc_content
        APPEND "\n   ```nginx" TO doc_content
        APPEND "\n   server {" TO doc_content
        APPEND "\n       listen 443 ssl http2;" TO doc_content
        APPEND "\n       listen [::]:443 ssl http2;" TO doc_content
        APPEND "\n       server_name fava.example.com;" TO doc_content
        APPEND "\n" TO doc_content
        APPEND "\n       # Enable PQC KEMs (e.g., " + kem_recommendation + ")" TO doc_content
        APPEND "\n       # Consult your OpenSSL/Nginx-OQS version documentation for specific directives." TO doc_content
        APPEND "\n       # Example for TLS 1.3 groups (syntax may vary):" TO doc_content
        APPEND "\n       # ssl_conf_command Groups " + kem_recommendation + ":X25519:secp256r1; # Prioritize PQC hybrid" TO doc_content
        APPEND "\n" TO doc_content
        APPEND "\n       ssl_protocols TLSv1.3;" TO doc_content
        APPEND "\n       ssl_prefer_server_ciphers off;" TO doc_content
        APPEND "\n       ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';" TO doc_content
        APPEND "\n" TO doc_content
        APPEND "\n       ssl_certificate /path/to/your/fullchain.pem; # Standard ECC/RSA certificate" TO doc_content
        APPEND "\n       ssl_certificate_key /path/to/your/privkey.pem;" TO doc_content
        APPEND "\n" TO doc_content
        APPEND "\n       location / {" TO doc_content
        APPEND "\n           proxy_pass http://localhost:5000; # Assuming Fava runs on port 5000" TO doc_content
        APPEND "\n           proxy_set_header Host $host;" TO doc_content
        APPEND "\n           # ... other proxy headers" TO doc_content
        APPEND "\n       }" TO doc_content
        APPEND "\n   }" TO doc_content
        APPEND "\n   ```" TO doc_content
        APPEND "\n3. **Test:** Use a browser with experimental PQC support or `openssl s_client -groups " + kem_recommendation + " ...`." TO doc_content
    ELSE IF proxy_type IS "Caddy"
        // **TDD Anchor:** TEST `generate_pqc_tls_reverse_proxy_config_guide` provides Caddy specific example if proxy_type is Caddy
        APPEND "\n\n### Example: Caddy" TO doc_content
        APPEND "\nCaddy may support PQC KEMs through custom builds or future official support. Consult Caddy documentation for enabling specific KEMs like `" + kem_recommendation + "`." TO doc_content
        APPEND "\nExample (conceptual Caddyfile snippet):" TO doc_content
        APPEND "\n   ```caddyfile" TO doc_content
        APPEND "\n   fava.example.com {" TO doc_content
        APPEND "\n       reverse_proxy localhost:5000" TO doc_content
        APPEND "\n       tls {" TO doc_content
        APPEND "\n           # Hypothetical directive for PQC KEMs" TO doc_content
        APPEND "\n           # key_exchange_algorithms " + kem_recommendation + " x25519" TO doc_content
        APPEND "\n       }" TO doc_content
        APPEND "\n   }" TO doc_content
        APPEND "\n   ```" TO doc_content
    END IF

    APPEND "\n\n**Note:** The PQC landscape and software support are rapidly evolving. Use classical certificates; PQC CAs are not yet standard. Hybrid KEMs like `" + kem_recommendation + "` work with classical certificates." TO doc_content
    APPEND "\nEnsure your OpenSSL configuration (`openssl.cnf`) enables PQC providers/algorithms if using a modular setup." TO doc_content

    RETURN doc_content
END FUNCTION

// **TDD Anchor:** TEST `generate_pqc_tls_contingency_guide` includes recommending application-layer PQC as a contingency
// **TDD Anchor:** TEST `generate_pqc_tls_contingency_guide` references relevant research doc `pf_tooling_contingency_PART_1.md`
FUNCTION `generate_pqc_tls_contingency_guide`(contingency_research_doc)
    INPUT: contingency_research_doc (String, e.g., "pf_tooling_contingency_PART_1.md")
    OUTPUT: String (Markdown formatted documentation section)

    LET doc_content = ""
    APPEND "## Contingency Planning for PQC-TLS" TO doc_content
    APPEND "\n\nIf PQC-TLS reverse proxies prove unstable or too complex for your environment at this time, consider the following:" TO doc_content
    APPEND "\n*   **Fallback to Classical TLS:** Ensure your proxy configuration allows fallback to robust classical TLS (e.g., TLS 1.3 with ECDHE and AES-GCM) if PQC negotiation fails or is not supported by the client." TO doc_content
    APPEND "\n*   **Application-Layer PQC:** For extremely sensitive data, and as an interim measure, you might explore application-layer PQC encryption for specific data fields before they are transmitted over a classical TLS channel. This adds complexity and is not a full substitute for PQC-TLS." TO doc_content
    APPEND "\n*   **Monitor Developments:** Keep abreast of updates in PQC standards, browser support, and proxy software capabilities." TO doc_content
    APPEND "\n\nRefer to Fava's research on tooling and contingencies: " + contingency_research_doc TO doc_content

    RETURN doc_content
END FUNCTION

// **TDD Anchor:** TEST `generate_pqc_tls_future_embedded_server_guide` is generated if `supported_kems` is not empty
// **TDD Anchor:** TEST `generate_pqc_tls_future_embedded_server_guide` mentions dependency on Python SSL/Cheroot PQC support
// **TDD Anchor:** TEST `generate_pqc_tls_future_embedded_server_guide` shows example config option `pqc_tls_embedded_server_kems`
FUNCTION `generate_pqc_tls_future_embedded_server_guide`(supported_kems_by_fava_embedded)
    INPUT: supported_kems_by_fava_embedded (List of Strings, e.g. ["X25519Kyber768"])
    OUTPUT: String (Markdown formatted documentation section)

    IF supported_kems_by_fava_embedded IS EMPTY
        RETURN "" // Do not generate this section if Fava's embedded server has no PQC support
    END IF

    LET doc_content = ""
    APPEND "## (Future) PQC-TLS with Fava's Embedded Web Server" TO doc_content
    APPEND "\n\n**Note:** This is a forward-looking section. Direct PQC-TLS support in Fava's embedded server (e.g., Cheroot via Flask's development server) depends on the Python `ssl` module and underlying libraries gaining robust PQC cipher suite support, which is not standard as of this writing." TO doc_content
    APPEND "\n\nShould such support become available, Fava might allow configuration of PQC KEMs via Fava options." TO doc_content
    APPEND "\nExample hypothetical Fava configuration option:" TO doc_content
    APPEND "\n```python" TO doc_content
    APPEND "\n# In your Fava configuration file" TO doc_content
    APPEND "\nPQC_TLS_EMBEDDED_SERVER_KEMS = [\"" + JOIN(supported_kems_by_fava_embedded, "\", \"") + "\"]" TO doc_content
    APPEND "\n```" TO doc_content
    APPEND "\nThis would instruct Fava's embedded server, if capable, to negotiate one of the specified PQC KEMs." TO doc_content
    APPEND "\nThis is **not recommended for production use**; a dedicated reverse proxy is always preferred for production deployments." TO doc_content

    RETURN doc_content
END FUNCTION


## 3. Module: FavaConfigurationValidator
// This module is for validating Fava configuration options, specifically future PQC options for the embedded server.

// **TDD Anchor:** TEST `validate_pqc_tls_embedded_server_options` accepts valid KEM list (e.g., ["X25519Kyber768"])
// **TDD Anchor:** TEST `validate_pqc_tls_embedded_server_options` rejects empty KEM list if PQC enabled for embedded
// **TDD Anchor:** TEST `validate_pqc_tls_embedded_server_options` rejects KEM list with unknown/unsupported KEMs
// **TDD Anchor:** TEST `validate_pqc_tls_embedded_server_options` passes if `pqc_tls_embedded_server_kems` is not present
FUNCTION `validate_pqc_tls_embedded_server_options`(fava_config, known_supported_pqc_kems_by_python_env)
    INPUT: fava_config (Fava's application configuration object)
    INPUT: known_supported_pqc_kems_by_python_env (List of PQC KEMs actually supported by the current Python SSL/server environment)
    OUTPUT: List of validation_errors (empty if valid)

    LET errors = []
    DEFINE config_option_name AS "pqc_tls_embedded_server_kems" // Matches Data Model 8.

    IF fava_config CONTAINS config_option_name
        LET configured_kems = fava_config[config_option_name]

        IF known_supported_pqc_kems_by_python_env IS EMPTY
            APPEND "Configuration option '" + config_option_name + "' is set, but the current Fava/Python environment does not support PQC KEMs for the embedded server." TO errors
            RETURN errors // Early exit if underlying support is missing
        END IF

        IF TYPEOF(configured_kems) IS NOT LIST
            APPEND "'" + config_option_name + "' must be a list of KEM strings." TO errors
            RETURN errors
        END IF

        IF configured_kems IS EMPTY
            APPEND "'" + config_option_name + "' is set but contains no KEMs. Provide a list of desired KEMs or remove the option." TO errors
        ELSE
            FOR EACH kem IN configured_kems
                IF kem IS NOT IN known_supported_pqc_kems_by_python_env
                    APPEND "KEM '" + kem + "' in '" + config_option_name + "' is not supported by the current Fava/Python environment. Supported: " + JOIN(known_supported_pqc_kems_by_python_env, ", ") TO errors
                END IF
            END FOR
        END IF
    END IF
    RETURN errors
END FUNCTION

## 4. Main Application Logic (Conceptual Integration Points)

PROCEDURE `initialize_fava_application`(fava_config)
    INPUT: fava_config

    // ... other Fava initialization ...

    // **TDD Anchor:** TEST Fava logs assumed PQC status from config during initialization if `assume_pqc_tls_proxy_enabled` is true
    LET pqc_config_status = `get_pqc_status_from_config`(fava_config)
    LOG "Initial PQC assumption based on config: " + pqc_config_status

    // For future embedded server PQC:
    // **TDD Anchor:** TEST Fava initialization fails if `pqc_tls_embedded_server_kems` contains invalid KEMs
    // This assumes `known_supported_pqc_kems_by_python_env` is determined at startup based on environment capabilities.
    LET known_env_kems = DETECT_AVAILABLE_PYTHON_PQC_KEMS() // Hypothetical function
    LET validation_errors = `validate_pqc_tls_embedded_server_options`(fava_config, known_env_kems)
    IF validation_errors IS NOT EMPTY
        LOG_ERROR "Invalid PQC TLS embedded server configuration: " + JOIN(validation_errors, "; ")
        // Optionally, prevent startup or disable embedded HTTPS if critical error
    END IF

    // ...
END PROCEDURE

PROCEDURE `handle_incoming_request`(request, fava_config)
    INPUT: request (object containing headers, body, etc.)
    INPUT: fava_config

    // ... other request handling ...

    // **TDD Anchor:** TEST Effective PQC status is logged for an incoming request if verbose logging is enabled
    LET effective_pqc_status = `determine_effective_pqc_status`(request.headers, fava_config)
    IF fava_config.verbose_logging IS TRUE
        LOG "Effective PQC status for request to " + request.path + ": " + effective_pqc_status
    END IF

    // Fava's core functionality (FR2.1) should operate irrespective of this status,
    // as TLS termination is handled by the proxy. This status is for information/logging.
    // **TDD Anchor:** (Relates to E2E test `test_fava_api_accessible_via_x25519kyber768_tls_proxy`)
    // Fava processes the request normally here.

    // ...
END PROCEDURE

// Hypothetical function, actual implementation depends on Python environment capabilities
FUNCTION `DETECT_AVAILABLE_PYTHON_PQC_KEMS`()
    OUTPUT: List of Strings (e.g., ["X25519Kyber768"] or empty list)
    // This would involve checking versions of OpenSSL, Python's ssl module,
    // and potentially the web server (Cheroot) for PQC KEM support.
    // For now, assume it returns an empty list or a predefined list for testing.
    // **TDD Anchor:** TEST `DETECT_AVAILABLE_PYTHON_PQC_KEMS` returns empty list if no PQC support in Python env
    // **TDD Anchor:** TEST `DETECT_AVAILABLE_PYTHON_PQC_KEMS` returns list of supported KEMs if present in Python env
    RETURN [] // Default to no support for current pseudocode
END FUNCTION