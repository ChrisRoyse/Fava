# Fava Architecture: PQC Data in Transit

**Version:** 1.0
**Date:** 2025-06-02
**Author:** AI Architect Mode

## 1. Introduction

This document outlines the high-level architecture for integrating Post-Quantum Cryptography (PQC) to protect **Data in Transit** for the Fava application. This primarily concerns the security of HTTPS/TLS connections between the Fava client (user's browser) and the Fava server.

The core architectural principle for PQC Data in Transit in Fava is the **reliance on an external, PQC-capable reverse proxy** to handle all PQC TLS cryptographic operations. Fava itself **does not implement PQC TLS handshakes or cryptographic operations** for data in transit when deployed in this recommended configuration. Fava's role is to:
1.  Be potentially aware of the PQC protection status (via proxy headers or internal configuration).
2.  Provide comprehensive documentation for administrators on configuring reverse proxies for PQC TLS.
3.  (Future consideration) Allow configuration of PQC KEMs if its embedded web server and underlying Python libraries support them directly (this is out of scope for the primary reverse-proxy architecture).

This architecture aligns with the specifications in [`docs/specifications/PQC_Data_In_Transit_Spec.md`](../specifications/PQC_Data_In_Transit_Spec.md) (v1.1), the logic detailed in [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../pseudocode/PQC_Data_In_Transit_Pseudo.md) (v1.0), and supports the AI verifiable tasks in the [`docs/ProjectMasterPlan_PQC.md`](../ProjectMasterPlan_PQC.md) (v1.1, task 3.2). It also enables the execution of acceptance tests defined in [`tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md`](../../tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md) (v1.1).

## 2. Architectural Approach: Reverse Proxy Centric

The chosen approach leverages the strengths of dedicated reverse proxy software (e.g., Nginx, Caddy) that can be compiled or configured with PQC capabilities (e.g., using OpenSSL with an OQS provider). This approach offers several advantages:
*   **Separation of Concerns:** Fava focuses on its core financial reporting functionality, while the reverse proxy handles the complexities of TLS and PQC.
*   **Security Specialization:** Reverse proxies are specialized for handling network traffic and security protocols, including TLS. PQC support is more likely to be robustly implemented and maintained in these systems.
*   **Flexibility:** Administrators can choose and configure their preferred PQC-capable reverse proxy.
*   **Reduced Fava Complexity:** Fava's codebase remains largely unchanged regarding TLS cryptographic operations.

Fava's interaction with this PQC-secured environment is primarily through standard HTTP after the proxy has terminated the PQC-TLS connection.

## 3. Components and Interactions

The key components involved in PQC-secured data in transit are:

*   **User's Browser:** A modern web browser with experimental support for the chosen PQC hybrid KEM (e.g., `X25519Kyber768`).
*   **PQC-Capable Reverse Proxy:** Software like Nginx or Caddy, configured with PQC-TLS capabilities (e.g., using OQS-OpenSSL) and the recommended hybrid KEM (`X25519Kyber768`). It terminates the PQC-TLS connection from the browser.
*   **Fava Application:** The standard Fava application, running as an HTTP server behind the reverse proxy. It receives plain HTTP requests from the proxy.

### Interactions:

1.  The User's Browser initiates an HTTPS connection to the Fava domain, which resolves to the PQC-Capable Reverse Proxy.
2.  The Browser and Reverse Proxy perform a TLS 1.3 handshake, negotiating a PQC hybrid KEM (e.g., `X25519Kyber768`).
3.  A PQC-hybrid secured TLS tunnel is established between the Browser and the Reverse Proxy.
4.  The Reverse Proxy decrypts the incoming HTTPS requests and forwards them as plain HTTP requests to the Fava Application.
5.  The Fava Application processes the HTTP request and sends an HTTP response back to the Reverse Proxy.
6.  The Reverse Proxy encrypts the HTTP response using the PQC-hybrid secured TLS session and sends it back to the User's Browser.

## 4. Deployment Architecture

The following diagrams illustrate the deployment context.

### 4.1. System Context Diagram (C4 Model Level 1)

```mermaid
graph LR
    User[User] -- Interacts via --> Browser[Browser with PQC Support]
    Browser -- HTTPS (PQC-TLS, e.g., X25519Kyber768) --> ReverseProxy[PQC-Capable Reverse Proxy\n(e.g., Nginx + OQS-OpenSSL)]
    ReverseProxy -- HTTP --> FavaApp[Fava Application Server]
    FavaApp -- Reads/Writes --> BeancountFiles[Beancount Files]

    subgraph "User's Device"
        Browser
    end

    subgraph "Server Environment"
        ReverseProxy
        FavaApp
        BeancountFiles
    end

    style User fill:#lightblue,stroke:#333,stroke-width:2px
    style Browser fill:#lightyellow,stroke:#333,stroke-width:2px
    style ReverseProxy fill:#lightgreen,stroke:#333,stroke-width:2px
    style FavaApp fill:#orange,stroke:#333,stroke-width:2px
    style BeancountFiles fill:#grey,stroke:#333,stroke-width:2px
```

### 4.2. Container Diagram (C4 Model Level 2 - Focus on Server Environment)

```mermaid
graph TD
    ClientBrowser[Client Browser\n(PQC KEM Support)]
    ClientBrowser -- HTTPS (PQC-TLS with X25519Kyber768) --> PQCProxy[PQC-Capable Reverse Proxy\n(e.g., Nginx + OQS-OpenSSL)\nTerminates PQC-TLS]
    
    subgraph "Server Infrastructure"
        PQCProxy -- HTTP --> FavaInstance[Fava Application\n(Python/Flask/Cheroot)\nListens on HTTP]
        FavaInstance -- Interacts with --> FavaCore[Fava Core Logic]
        FavaCore -- Accesses --> FileSystem[File System\n(Beancount Files)]
        
        FavaInstance -- Potentially uses --> PQCProxyAwareness[FavaPQCProxyAwareness Module\n(Reads Headers/Config)]
        FavaInstance -- Utilizes for docs --> FavaDocGenerator[FavaDocumentationGenerator Module]
    end

    style ClientBrowser fill:#lightyellow,stroke:#333,stroke-width:2px
    style PQCProxy fill:#lightgreen,stroke:#333,stroke-width:2px
    style FavaInstance fill:#orange,stroke:#333,stroke-width:2px
    style FavaCore fill:#ffcc99,stroke:#333,stroke-width:1px
    style FileSystem fill:#grey,stroke:#333,stroke-width:2px
    style PQCProxyAwareness fill:#lightblue,stroke:#333,stroke-width:1px
    style FavaDocGenerator fill:#lightblue,stroke:#333,stroke-width:1px
```
*Diagram Note: `FavaPQCProxyAwareness` and `FavaDocumentationGenerator` are conceptual modules within Fava as per pseudocode, not separate deployable containers.*

### 4.3. Security Considerations for Proxy-Fava Link

**WARNING:** As depicted in the diagrams (e.g., `ReverseProxy -- HTTP --> FavaApp`), the communication between the PQC-Capable Reverse Proxy and the Fava Application server is standard HTTP by default.

*   **Trusted Environments:** This is acceptable **only if** the proxy and Fava are running on the **same host** (communicating via `localhost` or a Unix socket) or within a **physically or virtually secured private network segment** where traffic cannot be intercepted.
*   **Untrusted Environments:** If the reverse proxy and Fava application are on different hosts connected via a general network, or if the network segment between them is otherwise not trusted, **this HTTP link MUST be independently secured.**
    *   **Recommended methods include:**
        *   Configuring classical TLS for the Fava application (so it listens on HTTPS) and ensuring the proxy connects to Fava via HTTPS.
        *   Implementing mutual TLS (mTLS) for stronger authentication between the proxy and Fava.
        *   Using an IPSec tunnel or a similar network-layer encryption mechanism to protect the link.
*   **Consequence of Inaction:** Failure to secure this internal link in an untrusted environment would expose unencrypted Fava data and communications between the proxy and the application, undermining the end-to-end security goals.

## 5. Fava's Internal Architectural Considerations

While Fava does not handle PQC TLS cryptography directly in this model, its architecture includes provisions for awareness and documentation.

### 5.1. PQC Proxy Awareness (`FavaPQCProxyAwareness` Module)
As detailed in [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../pseudocode/PQC_Data_In_Transit_Pseudo.md), Fava may include logic to:
*   **Check for PQC indicator headers:** The reverse proxy might add a custom HTTP header (e.g., `X-PQC-KEM: X25519Kyber768`) to requests forwarded to Fava. Fava can inspect this header.
    *   Pseudocode: `check_pqc_proxy_headers(request_headers)`
*   **Consult Fava configuration:** An administrator might set a Fava configuration flag (e.g., `assume_pqc_tls_proxy_enabled = true`).
    *   Pseudocode: `get_pqc_status_from_config(fava_config)`
*   **Determine effective PQC status:** Combine header and configuration information for logging or informational display.
    *   Pseudocode: `determine_effective_pqc_status(request_headers, fava_config)`

**Architectural Implication:** This awareness does not alter Fava's core request processing for functionality but can be used for:
*   Enhanced logging for administrators.
*   Potentially displaying an informational status in Fava's UI (future consideration, not a primary requirement).
*   Conditional behavior for future features, if any, that might depend on PQC status.

This logic would reside within Fava's request handling pipeline, likely as middleware or an early request processing step.

### 5.2. Documentation Generation (`FavaDocumentationGenerator` Module)
A key role for Fava is to provide guidance on setting up the PQC-TLS environment.
*   Pseudocode: `generate_pqc_tls_reverse_proxy_config_guide()`, `generate_pqc_tls_contingency_guide()`, `generate_pqc_tls_future_embedded_server_guide()`.

**Architectural Implication:** Fava's build process or a dedicated CLI command could leverage this module to generate or update sections of its official documentation. This ensures that the guidance provided to users for configuring Nginx, Caddy, etc., for PQC-TLS (specifically `X25519Kyber768`) is accurate and based on current recommendations and research findings (e.g., `pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md`, `pf_pqc_tls_proxies_clients_g4_2_PART_1.md`).

### 5.3. Configuration Interfaces (Fava & Proxy)
*   **Fava Configuration:**
    *   `assume_pqc_tls_proxy_enabled` (boolean): Allows Fava to log or assume PQC protection based on admin assertion, even if no specific PQC header is detected. This is relevant for `get_pqc_status_from_config`.
    *   (Future) `pqc_tls_embedded_server_kems` (list of strings): For direct PQC-TLS via Fava's embedded server, validated by `validate_pqc_tls_embedded_server_options`. This is outside the primary reverse-proxy architecture.
*   **Reverse Proxy Configuration (Documented by Fava):**
    *   Fava's documentation will guide administrators on configuring their chosen proxy (e.g., Nginx, Caddy) to:
        *   Enable TLS 1.3.
        *   Specify PQC hybrid KEMs, prioritizing `X25519Kyber768`.
        *   Configure classical SSL certificates (as PQC certificates are not yet standard).
        *   Set up proxying to the backend Fava HTTP server.
        *   Optionally, add a custom header (e.g., `X-PQC-KEM`) to indicate to Fava that PQC was used.

## 6. Data Flow

1.  **Client (Browser) to Reverse Proxy:** HTTPS request encrypted with PQC-TLS (e.g., `X25519Kyber768`).
2.  **Reverse Proxy:** Decrypts PQC-TLS request.
3.  **Reverse Proxy to Fava:** Plain HTTP request. (Optionally with `X-PQC-KEM` header).
4.  **Fava:** Processes HTTP request. (Optionally logs PQC status based on header/config).
5.  **Fava to Reverse Proxy:** Plain HTTP response.
6.  **Reverse Proxy:** Encrypts HTTP response with PQC-TLS.
7.  **Reverse Proxy to Client (Browser):** HTTPS response encrypted with PQC-TLS.

## 7. Architectural Assumptions

*   **External PQC-TLS Termination:** Fava assumes that PQC-TLS cryptographic operations (handshake, encryption, decryption) are handled entirely by an external reverse proxy.
*   **Proxy Reliability:** The reliability and security of the PQC-TLS connection depend on the chosen reverse proxy software and its configuration.
*   **Classical Certificates:** The reverse proxy will use classical (ECC/RSA) certificates, as PQC certificates and CAs are not yet widely available. PQC hybrid KEMs work with classical certificates.
*   **Proxy-Fava Communication Link Security:** Fava communicates with the reverse proxy over plain HTTP by default. **CRITICAL ASSUMPTION & WARNING:** This architecture assumes the network segment between the reverse proxy and the Fava application server is a trusted, secure environment (e.g., strictly localhost communication on the same machine, or a physically/virtually isolated and secured private network). **If this link is not inherently secure (e.g., traverses a shared network, different hosts not in a secured zone), it MUST be independently secured.** Methods include, but are not limited to:
    *   Configuring classical TLS for this internal hop (Fava listening on HTTPS, proxy connecting via HTTPS).
    *   Implementing mutual TLS (mTLS) between the proxy and Fava.
    *   Utilizing an IPSec tunnel or similar network-level encryption.
    Failure to secure this link in non-trusted environments exposes unencrypted Fava traffic between the proxy and the application, negating the benefits of client-to-proxy PQC-TLS.
*   **Browser PQC Support:** Users wishing to benefit from PQC-TLS must use browsers with experimental support for the configured PQC KEMs.
*   **Evolving Landscape:** The PQC landscape (algorithms, library support, proxy capabilities) is evolving. Fava's documentation will need to be updated to reflect significant changes.

## 8. Alignment with Specifications and Pseudocode

*   **Specifications ([`docs/specifications/PQC_Data_In_Transit_Spec.md`](../specifications/PQC_Data_In_Transit_Spec.md) v1.1):**
    *   **FR2.1 (Fava functions correctly):** Supported, as Fava receives standard HTTP.
    *   **FR2.2 (Documentation for proxy config):** Supported via `FavaDocumentationGenerator` module.
    *   **FR2.4 (Frontend uses standard APIs):** Supported, frontend is unaware of PQC-TLS details.
    *   **FR2.5 (Fava not interfering with TLS):** Supported, Fava is not involved in the TLS handshake.
    *   **FR2.6 (Contingency plan docs):** Supported via `FavaDocumentationGenerator`.
    *   **NFR3.1 (NIST/IETF adherence):** Responsibility of the proxy; Fava docs will recommend compliant KEMs.
    *   **NFR3.3 (Usable admin docs):** Addressed by `FavaDocumentationGenerator`.
    *   **C7.1 (Dependency on proxy/libs):** This architecture is built on this constraint.
*   **Pseudocode ([`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](../pseudocode/PQC_Data_In_Transit_Pseudo.md) v1.0):**
    *   `FavaPQCProxyAwareness` module's functions (`check_pqc_proxy_headers`, `get_pqc_status_from_config`, `determine_effective_pqc_status`) are integrated as internal Fava logic for informational purposes.
    *   `FavaDocumentationGenerator` module's functions are integrated into Fava's documentation build/update process.
    *   `FavaConfigurationValidator` (for future embedded server) is noted but not central to this proxy-based architecture.
    *   Main application logic integration points (`initialize_fava_application`, `handle_incoming_request`) show how awareness logic is invoked.

## 9. Support for Acceptance Tests

This architecture directly supports the high-level acceptance tests defined in [`tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md`](../../tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md) (v1.1):
*   **PQC_DIT_001 (Happy Path with `X25519Kyber768`):** The architecture defines the setup (Fava behind PQC proxy) against which this test is run. Fava's correct functioning (API response) is key.
*   **PQC_DIT_002 (Classical Fallback):** The architecture relies on the proxy for this; Fava continues to function normally.
*   **PQC_DIT_003 (Connection Failure - No Common KEM):** Fava would not receive a request; test verifies proxy/client behavior.
*   **PQC_DIT_004 (UI Loads Correctly over PQC-TLS):** Verifies Fava serves pages correctly through the PQC-TLS channel established by the proxy.

The AVERs for these tests confirm Fava's operational correctness within the PQC-TLS environment established by the proxy.

## 10. Architectural Decision Records (ADRs)

### ADR-001: Reliance on External Reverse Proxy for PQC-TLS

*   **Status:** Decided
*   **Context:** The primary goal is to secure Fava's data in transit using Post-Quantum Cryptography. Implementing PQC-TLS directly within Fava would involve significant complexity, dependencies on evolving Python PQC libraries, and ongoing maintenance burdens related to cryptographic protocols.
*   **Decision:** Fava will rely on an external, PQC-capable reverse proxy (e.g., Nginx, Caddy compiled with OQS-OpenSSL) to handle PQC-TLS termination. Fava itself will not implement PQC-TLS cryptographic operations for client-server communication when a proxy is used.
*   **Consequences:**
    *   **Pros:**
        *   Reduces complexity within Fava.
        *   Leverages specialized, more robust PQC implementations in proxy software.
        *   Allows administrators to choose their preferred proxy solution.
        *   Easier to update PQC capabilities by updating the proxy.
        *   Fava's core functionality remains unaffected by TLS complexities.
    *   **Cons:**
        *   Adds an external dependency (the reverse proxy) for PQC-TLS.
        *   Security of the PQC-TLS connection is dependent on the proxy's implementation and configuration.
        *   The communication channel between the reverse proxy and the Fava application is plain HTTP by default. **This presents a significant security risk if the link is not on a trusted, isolated network segment (e.g., localhost or a secured private network).**
    *   **Mitigation for Cons:**
        *   Fava will provide comprehensive documentation on configuring recommended proxies for PQC-TLS.
        *   Fava's documentation and this architecture document **MUST** strongly emphasize the critical need to independently secure the proxy-to-Fava communication link (e.g., using classical TLS, mTLS, or IPSec) if it does not operate exclusively within a trusted and secured environment like localhost or a dedicated private network. This warning will be prominent.

## 11. Future Considerations

*   **Direct PQC-TLS in Fava's Embedded Server:** If Python's `ssl` module and Fava's embedded web server (e.g., Cheroot) gain robust, standardized PQC support, Fava might offer direct PQC-TLS configuration. This would be an alternative deployment model, not replacing the reverse proxy recommendation for production. The `FavaConfigurationValidator` and `generate_pqc_tls_future_embedded_server_guide` pseudocode cater to this.
*   **Enhanced PQC Status Indication:** More sophisticated ways for Fava to display or utilize the PQC status (e.g., in admin UI panels) could be explored.

This architecture provides a clear path for enabling PQC protection for Fava's data in transit by leveraging external components, minimizing changes to Fava's core, and aligning with current best practices for deploying PQC in web applications.