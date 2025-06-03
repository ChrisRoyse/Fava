# Fava PQC Integration - Release Notes v1.1

**Date:** 2025-06-03 (Corresponds to Project Master Plan v1.1)

## Overview

This document outlines the new features, configuration changes, and known issues associated with the Post-Quantum Cryptography (PQC) integration in Fava version 1.1. The PQC enhancements aim to provide long-term security against emerging quantum threats. This integration touches upon data at rest, data in transit, hashing mechanisms, WASM module integrity, and overall cryptographic agility.

Refer to the [`docs/ProjectMasterPlan_PQC.md`](docs/ProjectMasterPlan_PQC.md) for the comprehensive project details.

## 1. PQC for Data at Rest

### New Features
*   **Fava-Driven Hybrid Encryption:** Introduces a new Fava-managed hybrid encryption scheme for data at rest. This typically combines a classical key exchange (e.g., X25519) with a PQC Key Encapsulation Mechanism (KEM) (e.g., Kyber-768) to protect a symmetric encryption key (e.g., AES-256-GCM).
*   **Enhanced Key Management:** Includes robust mechanisms for passphrase derivation, secure storage, and retrieval of cryptographic keys used for PQC operations.
*   **GPG Backward Compatibility:** Maintains support for decrypting files previously encrypted with classical GPG, ensuring a smooth transition for existing users. Fava can handle both PQC-encrypted and GPG-encrypted files.
*   **Centralized CryptoService:** A new `CryptoService` module handles all PQC data at rest operations, including encryption, decryption, and key management.

### Configuration Options
*   **Encryption Scheme Selection:** Users can configure Fava to use the new PQC hybrid encryption. Specific algorithm choices (KEMs, symmetric ciphers) are managed via the Cryptographic Agility settings (see Section 5).
*   **Passphrase Management:** Configuration related to passphrase handling for the new PQC key store.
*   **GPG Integration:** Options to manage interaction with existing GPG configurations for backward compatibility.
*   Refer to `FAVA_CRYPTO_SETTINGS` (Section 5) for detailed algorithm suite configuration.

### Known Issues & Considerations
*   **Library Dependencies:** Relies on `oqs-python` for PQC algorithms and the `cryptography` library for classical cryptographic primitives (AES, X25519, SHA3). Ensure these are correctly installed and compatible.
*   **GPG Still Needed:** Classical GPG tools must remain installed if backward compatibility for GPG-encrypted files is required.
*   **Performance:** PQC operations, especially KEMs, can be more computationally intensive than their classical counterparts. While efforts are made to optimize, some performance overhead might be noticeable for very large datasets or frequent operations. (Refer to [`docs/reports/PQC_Performance_Benchmark_v1.1.md`](docs/reports/PQC_Performance_Benchmark_v1.1.md)).
*   **Algorithm Stability:** The PQC landscape is evolving. While NIST-standardized algorithms are prioritized, future changes could necessitate updates. Cryptographic agility aims to mitigate this.

## 2. PQC for Data in Transit

### New Features
*   **PQC-TLS Reverse Proxy Guidance:** Fava is designed to operate securely behind a reverse proxy configured for PQC-TLS (e.g., using X25519Kyber768 for TLS 1.3). Documentation provides guidance on setting up such a proxy.
*   **Fava Awareness Mechanisms:** Fava can be made aware of PQC-protected transit through:
    *   Checking for specific HTTP headers set by the PQC-TLS reverse proxy.
    *   Configuration flags within Fava to assert that PQC-TLS is expected.

### Configuration Options
*   **Proxy Headers:** Configuration options to specify which HTTP headers Fava should check to confirm PQC-TLS protection by the reverse proxy.
*   **`PQC_TRANSIT_EXPECTED` Flag (Example):** A boolean configuration flag (e.g., in `fava.conf` or via environment variable) to tell Fava it should expect to be running behind a PQC-TLS proxy.
*   Detailed setup instructions for recommended PQC-TLS reverse proxies are provided in the user documentation.

### Known Issues & Considerations
*   **Proxy Responsibility:** Fava itself does not perform the PQC-TLS handshake. This is entirely the responsibility of the external reverse proxy (e.g., Nginx with OQS OpenSSL, Caddy).
*   **Proxy Dependency:** Requires a correctly configured PQC-TLS enabled reverse proxy. The availability, maturity, and ease of configuration of such proxies can vary.
*   **Fallback Recommendation:** If setting up a PQC-TLS proxy is problematic, users are advised to continue using robust classical TLS (e.g., TLS 1.3 with standard cipher suites) for data in transit protection as a fallback.
*   **Configuration Alignment:** Fava's configuration must be correctly aligned with the behavior and header injection of the chosen PQC-TLS reverse proxy.

## 3. PQC Hashing

### New Features
*   **PQC-Resistant Hash Functions:** Fava now defaults to using SHA3-256 for new hashing operations where appropriate, providing better resistance against potential future quantum attacks on hash functions.
*   **Algorithm Fallback:** SHA-256 may be used as a fallback or for compatibility with existing data where necessary.
*   **Configurable Selection:** The choice of hash algorithm is configurable, managed via the Cryptographic Agility settings.
*   **Integration via CryptoService:** PQC hashing functionalities are integrated into the central `CryptoService`.

### Configuration Options
*   **Default Hash Algorithm:** Configurable default hash algorithm (e.g., SHA3-256).
*   **Algorithm Suite Configuration:** Specific hash algorithm choices are part of the broader `FAVA_CRYPTO_SETTINGS` (see Section 5).
*   Options to manage hashing for new versus existing data structures if algorithm transitions are needed.

### Known Issues & Considerations
*   **Library Dependency:** Relies on the `cryptography` library for SHA3 support.
*   **Performance:** SHA3 algorithms can have different performance characteristics compared to SHA-2. This is generally minor for typical hashing use cases in Fava but has been considered.
*   **Data Compatibility:** When changing hash algorithms, consider implications for verifying existing data that used older hash functions. Fava aims to handle this gracefully where possible.

## 4. PQC WASM Module Integrity

### New Features
*   **Frontend PQC Signature Verification:** Fava's WebAssembly (WASM) modules are now signed using a PQC digital signature algorithm (e.g., Dilithium3).
*   **Client-Side Verification:** The Fava frontend performs PQC signature verification of the WASM module before execution, ensuring its integrity and authenticity against tampering. This uses a PQC JavaScript library (e.g., `liboqs-js`).
*   **Enhanced Security:** Protects against scenarios where WASM modules might be maliciously modified in transit or on a compromised CDN.
*   **Error Handling:** If verification fails, Fava will prevent the WASM module from loading and display an appropriate error or attempt a safe fallback if designed.

### Configuration Options
*   **User-Facing Configuration:** This feature is largely transparent to end-users and primarily a built-in security enhancement. There are typically no direct user-configurable options for the verification process itself.
*   **Developer/Build Process:**
    *   The public key for WASM verification is embedded in the Fava frontend.
    *   The WASM signing process (using e.g., Dilithium3 private key) is part of Fava's build and release pipeline.

### Known Issues & Considerations
*   **Build Tool Dependency:** The build process requires PQC signing tools (e.g., `oqs-python` scripts or `liboqs` CLI utilities) to sign the WASM modules with Dilithium3.
*   **JavaScript Library Dependency:** The frontend relies on a PQC JavaScript library (e.g., `liboqs-js`) for signature verification. This adds a small overhead to the initial frontend load.
*   **Key Management (Developer):** Secure management of the PQC private key used for signing WASM modules is critical for developers/maintainers.
*   **Browser Compatibility:** Ensure the JavaScript PQC library is compatible with supported web browsers.

## 5. PQC Cryptographic Agility

### New Features
*   **Configurable Algorithms:** Fava now offers a framework for cryptographic agility, allowing administrators to configure and switch between different cryptographic algorithms for:
    *   Key Encapsulation Mechanisms (KEMs) for data at rest.
    *   Digital Signature schemes (primarily for internal uses like WASM signing, potentially extendable).
    *   Hash functions.
*   **Centralized Configuration:** Algorithm choices are managed through a centralized configuration mechanism, primarily via the `FAVA_CRYPTO_SETTINGS` environment variable.
*   **Multiple Decryption Suites:** For data at rest, Fava can manage and attempt decryption with multiple algorithm suites. This allows for graceful migration from older (possibly classical or earlier PQC) schemes to newer ones without requiring immediate re-encryption of all data.
*   **Metadata for Algorithms:** Mechanisms are in place to associate data with the cryptographic algorithm suite used for its protection, facilitating correct decryption.
*   **`CryptoService` Factory:** The `CryptoService` can be instantiated with specific algorithm choices based on the configuration, promoting modularity.

### Configuration Options
*   **`FAVA_CRYPTO_SETTINGS` Environment Variable:** This is the primary method for defining cryptographic suites. It typically accepts a JSON-formatted string specifying preferred and supported algorithms for KEMs, signatures, and hashes.
    *   Example structure (conceptual):
        ```json
        {
          "data_at_rest_suites": [
            {"kem": "Kyber-768", "symmetric": "AES-256-GCM", "classical_kem": "X25519", "id": "pqc_hybrid_v1"},
            {"gpg": true, "id": "gpg_v1"}
          ],
          "default_data_at_rest_suite_id": "pqc_hybrid_v1",
          "wasm_signature_suite": {"sig": "Dilithium3", "id": "dilithium3_v1"},
          "default_hash_suite": {"hash": "SHA3-256", "id": "sha3_256_v1"}
        }
        ```
*   **Configuration File Options:** Potentially, some aspects of crypto agility might also be configurable via Fava's standard configuration files, complementing or overriding environment variables for certain deployment scenarios.

### Known Issues & Considerations
*   **Configuration Complexity:** Defining and managing cryptographic suites can be complex. Clear documentation and sensible defaults are provided.
*   **Algorithm Availability:** The configurable algorithms are limited to those supported by the integrated PQC libraries (`oqs-python`, `liboqs-js`, `cryptography`).
*   **Interoperability:** When migrating between algorithm suites, ensure that data encrypted with one suite can be decrypted correctly, especially if relying on the "multiple decryption suites" feature. Thorough testing during migration is recommended.
*   **Security Implications:** Incorrectly configuring cryptographic agility (e.g., selecting weak algorithms or mismanaging keys) can have severe security consequences. Administrators should understand the implications of their choices.

---
**Note:** This document is a summary. For detailed specifications, architecture, and testing information, please refer to the full project documentation suite located in the `docs/` directory of the Fava project.