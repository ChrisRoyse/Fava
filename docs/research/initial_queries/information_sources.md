# Potential Information Sources for PQC Integration Research

This document lists potential information sources to be consulted during the research phase for integrating Post-Quantum Cryptography (PQC) into Fava.

## I. Official Standards Bodies & Competitions

1.  **NIST (National Institute of Standards and Technology) PQC Standardization Project:**
    *   **Website:** Official NIST PQC pages.
    *   **Documents:** Published standards (FIPS), draft standards, official reports, workshop proceedings, and presentations.
    *   **Focus:** Definitive information on selected algorithms (Kyber, Dilithium, Falcon, SPHINCS+, etc.), their specifications, security analyses, and official test vectors.
2.  **IETF (Internet Engineering Task Force):**
    *   **Working Groups:** Relevant WGs like `tls`, `lamps` (for X.509), `cfrg` (Crypto Forum Research Group).
    *   **RFCs & Internet-Drafts:** Standards and proposals for PQC in TLS, X.509 certificates, and other internet protocols.
    *   **Focus:** How PQC algorithms are integrated into network protocols and data formats.

## II. Cryptographic Research & Community

3.  **IACR (International Association for Cryptologic Research):**
    *   **Publications:** ePrint Archive, proceedings from conferences like Crypto, Eurocrypt, Asiacrypt, PKC, TCC.
    *   **Focus:** Cutting-edge research on PQC algorithms, security analyses, new attacks, and implementation techniques.
4.  **Open Quantum Safe (OQS) Project:**
    *   **Website & GitHub:** `openquantumsafe.org`, `github.com/open-quantum-safe`
    *   **Components:** `liboqs` (C library), `oqs-provider` (for OpenSSL 3), language bindings (e.g., `oqs-python`), `liboqs-js`.
    *   **Focus:** Open-source implementations of PQC algorithms, integration into existing cryptographic libraries.
5.  **PQCRYPTO (Post-Quantum Cryptography for Long-Term Security):**
    *   **Website & Reports:** (European project, largely concluded but resources still valuable).
    *   **Focus:** Initial research and recommendations that fed into NIST's process.
6.  **Academic Research Papers:**
    *   Search on Google Scholar, Semantic Scholar, university research group pages.
    *   **Focus:** Specific algorithm analyses, performance benchmarks, side-channel attack research, implementation best practices.
7.  **Security Conferences & Workshops:**
    *   Real World Crypto (RWC), USENIX Security, IEEE S&P, ACM CCS, PQCrypto Conference series.
    *   **Focus:** Practical aspects, real-world deployments, new vulnerabilities, and industry perspectives.

## III. Software & Library Documentation

8.  **GnuPG (GPG):**
    *   **Website, Mailing Lists, Source Code:** `gnupg.org`.
    *   **Focus:** Official announcements and documentation regarding PQC support in GPG.
9.  **OpenSSL:**
    *   **Website, Documentation, GitHub:** `openssl.org`.
    *   **Focus:** PQC algorithm support (via OQS provider or native), TLS PQC cipher suites.
10. **Python Cryptographic Libraries:**
    *   **`cryptography` package:** Documentation and issue trackers for potential future PQC support.
    *   **`oqs-python` (if used):** Specific documentation for the Python bindings to liboqs.
11. **JavaScript Cryptographic Libraries:**
    *   **`liboqs-js` (if used):** Documentation and examples.
    *   **Web Cryptography API (MDN):** For current browser-native crypto capabilities and potential future PQC additions.
    *   Libraries for SHA-3 or other hashes if not browser-native.
12. **Web Server Documentation (Nginx, Apache, Caddy, etc.):**
    *   **Official Documentation:** For configuring TLS, cipher suites, and specifically PQC support if available.
13. **Browser Vendor Documentation & Blogs:**
    *   Chrome, Firefox, Safari, Edge security blogs and development notes.
    *   **Focus:** Announcements and details about experimental or stable PQC support in TLS.

## IV. Fava Project & Dependencies

14. **Fava Codebase:**
    *   [`docs/Plan.MD`](docs/Plan.MD): The primary strategic document.
    *   Existing source code (`src/`) and code comprehension reports.
    *   **Focus:** Understanding current cryptographic touchpoints and architectural constraints.
15. **Beancount Documentation & Community:**
    *   Beancount mailing list, issue trackers.
    *   **Focus:** Discussions or plans related to PQC, especially for encrypted file handling.

## V. General Technology & News Outlets

16. **Tech News Sites & Blogs specializing in Security/Cryptography:**
    *   (e.g., The Hacker News, Bleeping Computer, Krebs on Security, Schneier on Security blog).
    *   **Focus:** Broader updates, industry adoption trends, major vulnerability disclosures.

This list will be refined and expanded as the research progresses and specific knowledge gaps are identified. The primary tool for accessing many of these will be the AI search MCP tool.