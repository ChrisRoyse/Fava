# Fava PQC: Post-Quantum Cryptography Enhancements

## 1. Project Overview

Fava PQC is an enhanced version of the Fava web interface for Beancount, fortified with Post-Quantum Cryptography (PQC) to provide long-term security for financial data against threats from both classical and quantum computers. This project integrates a comprehensive suite of PQC capabilities, transforming Fava into a quantum-resistant financial data management platform while maintaining backward compatibility with existing workflows.

The primary goal of Fava PQC is to ensure the confidentiality, integrity, and authenticity of user data in an era of emerging quantum threats. This is achieved through a modular, agile, and robust cryptographic architecture that supports hybrid encryption schemes, PQC-resistant hashing, and strong integrity verification for application components.

## 2. Key Features

Fava PQC introduces several major enhancements to secure user data across different aspects of the application.

### Data at Rest: Hybrid PQC Encryption

To protect Beancount files stored on disk, Fava implements a sophisticated hybrid encryption scheme. This approach combines the strengths of both classical and post-quantum cryptography to ensure robust security.

- **Hybrid Scheme**: The default encryption suite is `X25519_KYBER768_AES256GCM`. This combines:
    - **X25519**: A fast and widely-used classical Elliptic Curve Diffie-Hellman (ECDH) key exchange.
    - **Kyber-768**: A NIST-selected PQC Key Encapsulation Mechanism (KEM) providing Level 3 security against quantum attacks.
    - **AES-256-GCM**: A strong, authenticated symmetric cipher for encrypting the actual data.
- **Backward Compatibility**: Fava remains fully backward compatible with Beancount files encrypted using classical GPG. The system can automatically detect the encryption format and use the appropriate decryption method.
- **Fava-Driven Encryption**: Users can now encrypt their Beancount files directly within Fava using the configured PQC hybrid scheme, simplifying the user workflow and reducing reliance on external PQC tools.

### Data in Transit: PQC-TLS Protection

Fava secures client-server communication by leveraging PQC-capable reverse proxies.

- **PQC-TLS**: Fava is designed to be deployed behind a reverse proxy (e.g., Nginx, Caddy) that is configured to use PQC hybrid KEMs for TLS 1.3. The recommended KEM is `X25519Kyber768`, which protects the TLS session against quantum eavesdropping.
- **Proxy Awareness**: Fava can be configured to be aware of the PQC protection provided by the proxy, allowing for enhanced logging and security assertions.

### PQC Hashing: Enhanced Data Integrity

To ensure the integrity of data, Fava has been upgraded to use PQC-resistant hash functions.

- **SHA3-256**: The default hashing algorithm is now SHA3-256, a FIPS 202 standard that offers better resistance to future attacks compared to the SHA-2 family.
- **Agility**: SHA-256 remains a configurable option for backward compatibility or specific needs.
- **Consistent Hashing**: The hashing mechanism is applied consistently across the backend (for file integrity checks) and the frontend (for optimistic concurrency control in the editor).

### WASM Module Integrity: PQC Digital Signatures

To protect against supply chain attacks and ensure the authenticity of critical frontend components, Fava uses PQC digital signatures.

- **Dilithium3 Signatures**: The `tree-sitter-beancount.wasm` module, which is crucial for client-side parsing, is signed with the Dilithium3 PQC signature algorithm (NIST Level 3).
- **Frontend Verification**: Before the WASM module is loaded, the Fava frontend verifies this signature using the `liboqs-js` library. If the signature is invalid, the module is not loaded, preventing the execution of potentially tampered code.

### Cryptographic Agility

Recognizing the evolving nature of cryptography, Fava PQC is built on a foundation of cryptographic agility.

- **Configurable Algorithms**: All cryptographic operations (data at rest encryption, hashing) are managed through a centralized configuration system. Administrators can switch algorithms and suites without changing the application's core code.
- **Modular Architecture**: A dedicated `CryptoService` layer abstracts all cryptographic logic, making it easier to add, update, or replace algorithms in the future.
- **Legacy Support**: The system is designed to decrypt data encrypted with older, configured PQC suites, ensuring smooth transitions as cryptographic standards evolve.

## 3. Architecture

The PQC enhancements are integrated into Fava through a new, modular `CryptoService` layer. This layer is responsible for abstracting all cryptographic operations and is a key enabler of cryptographic agility.

- **Backend `CryptoService`**: A central service in the Python backend that manages cryptographic handlers for different schemes (e.g., `HybridPqcHandler`, `GpgHandler`). It uses a factory pattern to instantiate the correct handler based on configuration and file metadata.
- **Key Management**: The architecture supports two primary key management modes for PQC data at rest:
    1.  **Passphrase-Derived Keys**: PQC keys are securely derived from a user-provided passphrase using Argon2id and HKDF.
    2.  **External Key Files**: Users can provide paths to externally managed PQC key files.
- **Frontend Crypto Facade**: A corresponding abstraction layer in the frontend (`pqcCryptoFacade.ts`) handles client-side cryptographic needs like hashing and WASM signature verification, driven by configuration provided from the backend.

This architecture decouples the core Fava application logic from the underlying cryptographic implementations, making the system more secure, maintainable, and future-proof.

## 4. Configuration and Usage

Configuring and using the new PQC features is designed to be straightforward.

### Configuration

PQC features are managed through a centralized `FAVA_CRYPTO_SETTINGS` object within Fava's options. Key settings include:

- **Data at Rest**:
    - `active_encryption_suite_id`: Set the default hybrid suite for new encryptions.
    - `decryption_attempt_order`: Define the order of suites to try when decrypting.
    - `key_management_mode`: Choose between `PASSPHRASE_DERIVED` and `EXTERNAL_KEY_FILE`.
- **Hashing**:
    - `default_algorithm`: Set the hashing algorithm (e.g., "SHA3-256").
- **WASM Integrity**:
    - `verification_enabled`: Enable or disable WASM signature verification.

### Usage

- **Encrypting a File**: Use the Fava UI or CLI to encrypt a Beancount file. You will be prompted for a passphrase or to provide key file details based on your configuration.
- **Decrypting a File**: Simply open the encrypted file in Fava. The system will automatically detect the encryption scheme and use the appropriate key material to decrypt it.
- **PQC-TLS**: Configure a PQC-capable reverse proxy according to Fava's documentation and access Fava through it. No changes are needed on the client-side, provided you are using a browser with experimental PQC support.

## 5. Security and Performance

### Security Posture

Fava PQC is designed with a defense-in-depth security model:

- **Quantum Resistance**: Core cryptographic operations are protected against quantum attacks using NIST-selected PQC algorithms.
- **Hybrid Approach**: The hybrid encryption scheme for data at rest ensures security against both classical and quantum adversaries.
- **Integrity and Authenticity**: PQC hashing and digital signatures protect against data and application tampering.
- **Secure Key Management**: Robust key derivation (Argon2id + HKDF) and handling practices are implemented.

### Performance

Performance has been a key consideration in the design of Fava PQC.

- **PQC Operations**: PQC algorithms like Kyber-768 and Dilithium3 have been chosen for their balance of security and performance.
- **Overhead**: While PQC operations introduce some overhead compared to classical cryptography, they are optimized to ensure that application responsiveness is not significantly degraded. Performance targets are defined in the specifications to keep encryption and decryption latency within acceptable bounds for a smooth user experience.
- **Benchmarking**: The system has undergone performance benchmarking to validate that it meets the defined non-functional requirements.