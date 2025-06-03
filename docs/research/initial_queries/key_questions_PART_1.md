# Key Research Questions for PQC Integration in Fava - Part 1

This document outlines the initial set of key research questions to guide the investigation into integrating Post-Quantum Cryptography (PQC) into the Fava codebase. These questions are derived from the research scope, the [`docs/Plan.MD`](docs/Plan.MD) document, and the general requirements for PQC adoption.

## I. General PQC Landscape & Foundations

1.  **NIST PQC Standardization:**
    *   What are the latest updates and timelines from the NIST PQC standardization process?
    *   Which algorithms have been selected for standardization for Key Encapsulation Mechanisms (KEMs) and digital signatures?
    *   Are there any notable draft standards or new rounds of submissions relevant to Fava's use cases?
    *   What are the known security levels and characteristics (key sizes, signature sizes, performance benchmarks) of the primary standardized candidates (e.g., CRYSTALS-Kyber, CRYSTALS-Dilithium, Falcon, SPHINCS+)?
    *   What are the official OIDs (Object Identifiers) for these standardized algorithms, if available?
2.  **Cryptographic Agility for PQC:**
    *   What are current best practices for achieving cryptographic agility in software applications transitioning to PQC?
    *   How can hybrid models (classical + PQC) be effectively implemented? What are common strategies (e.g., concatenating keys, separate encryption layers)?
    *   What are the design considerations for an abstraction layer (like the proposed `CryptoService` in [`docs/Plan.MD`](docs/Plan.MD)) to support PQC?
    *   How should algorithm selection and parameter configuration be managed in an agile system?
3.  **PQC Threat Model & Security Considerations:**
    *   Beyond Shor's algorithm, what other quantum threats are relevant to the cryptographic primitives Fava uses or might use?
    *   Are there known side-channel vulnerabilities or implementation pitfalls specific to the leading PQC candidates? How can these be mitigated?
    *   What are the implications of larger PQC key/signature sizes on storage, transmission, and processing?
    *   How does PQC affect existing security protocols and practices (e.g., key exchange, certificate issuance)?

## II. PQC for Data at Rest (Encrypted Beancount Files)

4.  **Beancount & GPG PQC Support:**
    *   What is the current status of PQC support in GnuPG (GPG)?
        *   Which PQC algorithms (KEMs, signatures) are supported or planned?
        *   Are there stable releases of GPG with PQC capabilities?
        *   What is the command-line interface or API for using PQC in GPG?
    *   How does Beancount's file encryption mechanism interact with GPG?
    *   Will Beancount automatically benefit from PQC-updated GPG, or will changes be needed in Beancount's loader?
    *   Are there alternative PQC-enabled tools compatible with GPG's file format or workflow that Fava could leverage if GPG's PQC support is delayed or insufficient?
5.  **Fava-Side Decryption Abstraction:**
    *   If Fava were to implement its own PQC decryption (as a more advanced option beyond relying on Beancount/GPG), what would be the key challenges for key management?
    *   How would users securely provide PQC keys or passphrases to Fava in such a scenario?
    *   What data format or metadata would be needed within or alongside an encrypted Beancount file to indicate the PQC algorithm used if Fava handles decryption?
6.  **Suitable PQC KEMs for File Encryption:**
    *   Which NIST-standardized KEMs (e.g., CRYSTALS-Kyber) are most suitable for a hybrid file encryption scheme (e.g., PQC KEM for key wrapping, AES for bulk encryption)?
    *   What are their performance characteristics in this context?

## III. PQC for Data in Transit (HTTPS/TLS)

7.  **Server-Side TLS & Reverse Proxies:**
    *   Which common reverse proxies (Nginx, Apache, Caddy, etc.) currently offer stable support for PQC in TLS 1.3 (e.g., hybrid KEMs like X25519Kyber768)?
    *   What are the typical configuration steps for enabling PQC cipher suites in these proxies?
    *   What is the status of PQC support in Python web servers like Cheroot or in the Python `ssl` module (via OpenSSL)?
        *   Which versions of OpenSSL include robust PQC support suitable for production?
        *   Can PQC cipher suites be directly configured in Cheroot or Flask's development server?
8.  **PQC Certificates:**
    *   What is the status of PQC certificate issuance by major Certificate Authorities (CAs)?
    *   Are there PQC-signed root certificates or intermediate CAs?
    *   What are the formats for PQC public keys and signatures in X.509 certificates?
9.  **Browser PQC Support:**
    *   Which major web browsers (Chrome, Firefox, Safari, Edge) have experimental or stable support for PQC KEMs in TLS?
    *   Is this support enabled by default, or does it require user configuration?
    *   What is the impact on frontend code if the server uses PQC for TLS? (Presumably minimal, relying on browser capabilities).

## IV. PQC for Data Integrity (Hashing)

10. **Quantum Resistance of Hash Functions:**
    *   What is the consensus on the quantum resistance of SHA-2 (SHA-256, SHA-512) and SHA-3 families for collision resistance and preimage resistance?
    *   Is there an immediate need to replace SHA-256 for Fava's use cases (file integrity, optimistic concurrency) due to quantum threats?
    *   What are the arguments for/against migrating to SHA-3 (e.g., SHA3-256) or other newer hash functions for better long-term security?
11. **PQC-Specific Hash Functions:**
    *   Are there any hash functions specifically designed or favored in the PQC context, or is the recommendation generally to use existing strong hashes like SHA-3?
12. **Frontend Hashing:**
    *   If Fava transitions to a PQC-recommended hash algorithm (e.g., SHA3-256) on the backend, what are the options for implementing the same hash function in the JavaScript/WASM frontend?
        *   Does `window.crypto.subtle` support SHA-3 or other relevant hashes?
        *   What are the leading JavaScript libraries for SHA-3 or other PQC-relevant hashes, and what is their maturity?

(Continued in Part 2)