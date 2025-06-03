# PQC Deployment Security Considerations for Fava

**Version:** 1.0
**Date:** 2025-06-03

## Introduction

This document outlines critical security considerations when deploying Fava with Post-Quantum Cryptography (PQC) capabilities, specifically focusing on the PQC Data in Transit architecture. While Fava aims to support PQC-TLS through reverse proxies, administrators must be aware of potential risks and implement appropriate mitigations.

This document should be read in conjunction with:
*   [`docs/architecture/PQC_Data_In_Transit_Arch.md`](../architecture/PQC_Data_In_Transit_Arch.md)
*   [`docs/reports/security_review_PQC_Data_In_Transit.md`](../reports/security_review_PQC_Data_In_Transit.md)

## ⚠️ CRITICAL RISK: PQC-DIT-ARCH-001 - Unencrypted Reverse Proxy to Fava Communication ⚠️

The primary PQC Data in Transit architecture for Fava involves using a PQC-capable reverse proxy (e.g., Nginx, Caddy) to terminate the PQC-TLS connection from the user's browser. The proxy then forwards requests to the Fava backend application.

**By default, the communication channel between this reverse proxy and the backend Fava application server is plain HTTP.**

### The Risk

If the reverse proxy and the Fava application are **not** operating in an inherently secure environment, this plain HTTP link is vulnerable to:

*   **Eavesdropping:** An attacker on the network segment between the proxy and Fava could intercept and read all unencrypted traffic, including potentially sensitive financial data.
*   **Modification:** An attacker could modify the unencrypted traffic in transit, altering requests to Fava or responses from Fava.

This vulnerability completely **undermines the end-to-end security** that PQC-TLS aims to provide to the client. Even if the client-to-proxy connection is quantum-resistant, data exposure or tampering can occur on the internal proxy-to-Fava link.

### When is this a Risk?

This is a **HIGH SEVERITY** risk if:

*   The reverse proxy and the Fava application are running on **different hosts** connected via a general network (LAN or WAN).
*   The reverse proxy and Fava are on the same host, but the communication does not strictly use `localhost` interfaces and could be intercepted by other processes or users on that host.
*   The network segment between the proxy and Fava is otherwise considered **untrusted**.

### Mandatory Mitigation Strategies

Administrators **MUST** implement one ofalling mitigation strategies if the proxy-to-Fava link is not inherently secure (e.g., not strictly localhost on a single, secured machine or not within a dedicated, isolated, and trusted private network segment):

1.  **Configure Fava for HTTPS (Recommended for different hosts):**
    *   **Action:** Configure the Fava application itself to listen on HTTPS (using a standard TLS certificate) for the internal connection from the reverse proxy.
    *   **Proxy Configuration:** Ensure your reverse proxy connects to Fava using an `https://://...` upstream directive (e.g., `proxy_pass https://fava-internal-host:port;` in Nginx).
    *   **Details:** This requires generating and managing a TLS certificate specifically for Fava's internal-facing server. This certificate does not need to be PQC-enabled; standard TLS 1.2 or 1.3 is sufficient for this internal hop.

2.  **Implement Mutual TLS (mTLS):**
    *   **Action:** Configure mTLS for the connection between the reverse proxy and the Fava application.
    *   **Details:** This provides strong, two-way authentication. Both the proxy and Fava will need to present and validate certificates from each other. This ensures that only the authorized proxy can connect to Fava, and Fava only responds to the authorized proxy, all over an encrypted channel.

3.  **Use IPSec or Similar Network-Layer Encryption:**
    *   **Action:** If the proxy and Fava are on different hosts within an untrusted network segment, establish an IPSec tunnel (or use a similar technology like WireGuard) between the two hosts.
    *   **Details:** This encrypts all IP traffic between the two endpoints at the network layer, securing the Fava communication along with any other traffic.

4.  **Same Host Deployment: Restrict to Localhost Interfaces:**
    *   **Action:** If the reverse proxy and Fava application are running on the **same physical host**, ensure that:
        *   Fava is configured to listen **only** on a localhost interface (e.g., `127.0.0.1` for IPv4, `::1` for IPv6).
        *   The reverse proxy is configured to connect to Fava **only** via this localhost interface (e.g., `proxy_pass http://127.0.0.1:5000;` in Nginx).
    *   **Details:** This significantly reduces the attack surface by preventing external network access to the plain HTTP Fava port. However, ensure the host itself is adequately secured.

## General PQC Deployment Recommendations

*   **Stay Updated:** The PQC landscape is rapidly evolving. Regularly check for updates to your reverse proxy software, underlying PQC libraries (like liboqs), and browser PQC support.
*   **Use Recommended KEMs:** Prioritize PQC Key Encapsulation Mechanisms (KEMs) that are recommended by standards bodies (like NIST) and have seen sufficient cryptographic review. Fava's documentation will aim to reflect current best practices (e.g., `X25519Kyber768` as a hybrid KEM).
*   **Classical Certificates:** Continue to use classical (ECC/RSA) certificates for your reverse proxy's public-facing TLS. PQC certificates and CAs are not yet standardized or widely available. PQC hybrid KEMs are designed to work with classical certificates.
*   **Test Thoroughly:** After configuring PQC-TLS, thoroughly test your setup using browsers with PQC support and tools like `openssl s_client` (if compiled with PQC capabilities) to verify KEM negotiation.
*   **Monitor Logs:** Monitor your reverse proxy and Fava application logs for any errors or warnings related to TLS or PQC operations.

**Failure to properly secure the deployment, especially the proxy-to-Fava link in untrusted environments, can lead to serious security vulnerabilities.** Always prioritize a defense-in-depth strategy.