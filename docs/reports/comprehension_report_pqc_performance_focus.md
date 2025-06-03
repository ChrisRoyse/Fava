# Code Comprehension Report: PQC Performance Focus

## Executive Summary

This report analyzes the Fava PQC (Post-Quantum Cryptography) codebase to identify modules and operations critical for performance benchmarking against NFRs defined in the PQC v1.1 specifications and [`docs/ProjectMasterPlan_PQC.md`](../ProjectMasterPlan_PQC.md).

## Analysis Scope

**Analyzed Files:**
- [`src/fava/crypto/service.py`](../../src/fava/crypto/service.py) - Backend hashing service
- [`src/fava/crypto/handlers.py`](../../src/fava/crypto/handlers.py) - Hybrid PQC encryption handlers
- [`src/fava/crypto/keys.py`](../../src/fava/crypto/keys.py) - PQC KEM operations and key derivation
- [`src/fava/core/ledger.py`](../../src/fava/core/ledger.py) - File encryption/decryption integration
- [`src/fava/pqc/proxy_awareness.py`](../../src/fava/pqc/proxy_awareness.py) - PQC-TLS proxy detection
- [`src/fava/application.py`](../../src/fava/application.py) - Flask app PQC initialization
- [`frontend/src/lib/pqcCrypto.ts`](../../frontend/src/lib/pqcCrypto.ts) - Frontend PQC operations
- [`frontend/src/lib/wasmLoader.ts`](../../frontend/src/lib/wasmLoader.ts) - WASM module loading with PQC verification
- [`src/fava/pqc/backend_crypto_service.py`](../../src/fava/pqc/backend_crypto_service.py) - Cryptographic agility framework
- [`src/fava/pqc/global_config.py`](../../src/fava/pqc/global_config.py) - PQC configuration management

## Key Performance-Critical Areas

### 1. Data at Rest (Hybrid PQC Encryption)

**Primary Components:**
- **[`HybridPqcHandler`](../../src/fava/crypto/handlers.py:45)** - Core hybrid encryption implementation
- **[`OQSKEMAdapter`](../../src/fava/crypto/keys.py:15)** - PQC KEM operations wrapper
- **[`HybridPqcCryptoHandler`](../../src/fava/pqc/backend_crypto_service.py:89)** - Service-level handler

**Performance-Critical Operations:**
- **KEM Encapsulation/Decapsulation:** [`OQSKEMAdapter.encap_secret()`](../../src/fava/crypto/keys.py:25) and [`decap_secret()`](../../src/fava/crypto/keys.py:35)
- **Hybrid Encryption:** [`HybridPqcHandler.encrypt_content()`](../../src/fava/crypto/handlers.py:55) combining Kyber-768 + AES-256-GCM
- **Key Derivation:** [`Argon2id.derive()`](../../src/fava/crypto/keys.py:85) for passphrase-based keys

**Dependencies:**
- `oqs-python` library for PQC algorithms
- `cryptography` library for classical crypto (AES-GCM, HKDF)
- `argon2-cffi` for password-based key derivation

### 2. Data in Transit (PQC-TLS Awareness)

**Primary Components:**
- **[`determine_effective_pqc_status()`](../../src/fava/pqc/proxy_awareness.py:15)** - PQC-TLS detection logic

**Performance Considerations:**
- Header parsing overhead for `X-PQC-KEM` detection
- Configuration lookup performance
- Per-request PQC status determination

### 3. PQC Hashing

**Backend Implementation:**
- **[`HashingService`](../../src/fava/crypto/service.py:15)** - Centralized hashing service
- **[`hash_data()`](../../src/fava/crypto/service.py:35)** - SHA3-256 vs SHA256 selection

**Frontend Implementation:**
- **[`calculateConfiguredHash()`](../../frontend/src/lib/pqcCrypto.ts:45)** - Frontend hashing with `js-sha3`

**Performance-Critical Operations:**
- SHA3-256 computation using `hashlib.sha3_256` or `pysha3` fallback
- Frontend SHA3-256 via `js-sha3` library
- Hash algorithm selection logic

### 4. PQC WASM Module Integrity

**Primary Components:**
- **[`verifyPqcWasmSignature()`](../../frontend/src/lib/pqcCrypto.ts:15)** - Dilithium3 signature verification
- **[`loadBeancountParserWithPQCVerification()`](../../frontend/src/lib/wasmLoader.ts:25)** - WASM loading with verification

**Performance-Critical Operations:**
- Dilithium3 signature verification using global `OQS` object
- WASM module loading and validation
- Public key processing and signature validation

**Dependencies:**
- `liboqs-js` library (global `OQS` object)
- WASM module signature and public key data

### 5. Cryptographic Agility

**Primary Components:**
- **[`BackendCryptoService`](../../src/fava/pqc/backend_crypto_service.py:15)** - Handler registry and management
- **[`decrypt_data_at_rest_with_agility()`](../../src/fava/pqc/backend_crypto_service.py:145)** - Multi-handler decryption

**Performance-Critical Operations:**
- Handler registration and lookup
- Multiple decryption attempts with different suites
- Configuration-based algorithm selection
- Suite compatibility checking

## Data Flow Analysis

### Encryption Flow (Data at Rest)
1. [`FavaLedger.save_file_pqc()`](../../src/fava/core/ledger.py:85) → 
2. [`BackendCryptoService.get_active_encryption_handler()`](../../src/fava/pqc/backend_crypto_service.py:55) →
3. [`HybridPqcHandler.encrypt_content()`](../../src/fava/crypto/handlers.py:55) →
4. [`OQSKEMAdapter.encap_secret()`](../../src/fava/crypto/keys.py:25) + AES-GCM encryption

### Decryption Flow (Data at Rest)
1. [`FavaLedger.load_file()`](../../src/fava/core/ledger.py:45) →
2. [`decrypt_data_at_rest_with_agility()`](../../src/fava/pqc/backend_crypto_service.py:145) →
3. Multiple handler attempts →
4. [`HybridPqcHandler.decrypt_content()`](../../src/fava/crypto/handlers.py:95) →
5. [`OQSKEMAdapter.decap_secret()`](../../src/fava/crypto/keys.py:35) + AES-GCM decryption

## Performance Benchmarking Recommendations

### Critical Metrics to Measure
1. **KEM Operations:** Kyber-768 encapsulation/decapsulation latency
2. **Hybrid Encryption:** End-to-end encryption/decryption throughput
3. **Hash Performance:** SHA3-256 vs SHA256 comparison (backend/frontend)
4. **WASM Verification:** Dilithium3 signature verification time
5. **Agility Overhead:** Multi-handler decryption performance impact

### Benchmark Target Areas
- [`OQSKEMAdapter`](../../src/fava/crypto/keys.py:15) operations under various data sizes
- [`HybridPqcHandler`](../../src/fava/crypto/handlers.py:45) full encryption/decryption cycles
- [`HashingService`](../../src/fava/crypto/service.py:15) performance across different data volumes
- Frontend [`verifyPqcWasmSignature()`](../../frontend/src/lib/pqcCrypto.ts:15) latency
- [`decrypt_data_at_rest_with_agility()`](../../src/fava/pqc/backend_crypto_service.py:145) with multiple suites

## Dependencies and External Libraries

### Backend Dependencies
- **oqs-python:** Core PQC algorithm implementations
- **cryptography:** Classical crypto operations (AES-GCM, HKDF, X25519)
- **argon2-cffi:** Password-based key derivation
- **pysha3:** SHA3 fallback implementation

### Frontend Dependencies
- **js-sha3:** SHA3-256 implementation
- **liboqs-js:** PQC operations (Dilithium3 verification)

## Potential Performance Issues

1. **KEM Operation Latency:** Kyber-768 operations may have significant latency compared to classical algorithms
2. **Multiple Decryption Attempts:** Agility mechanism may cause performance degradation with many configured suites
3. **WASM Verification Overhead:** Dilithium3 signature verification adds startup latency
4. **Hash Algorithm Selection:** Dynamic algorithm selection adds conditional overhead
5. **Memory Usage:** PQC algorithms typically require more memory than classical counterparts

## Integration Points

### Application Initialization
- [`create_app()`](../../src/fava/application.py:45) initializes PQC services
- [`GlobalConfig.get_crypto_settings()`](../../src/fava/pqc/global_config.py:25) loads configuration

### File Operations
- [`FavaLedger`](../../src/fava/core/ledger.py:15) integrates PQC encryption into file I/O
- Transparent encryption/decryption for Beancount files

### Frontend Integration
- WASM module loading with integrity verification
- Frontend hashing for data validation

## Conclusion

The Fava PQC implementation provides a comprehensive framework for post-quantum cryptography with emphasis on hybrid approaches and cryptographic agility. Performance benchmarking should focus on the identified critical operations, particularly KEM operations, hybrid encryption cycles, and the overhead introduced by agility mechanisms. The modular design allows for targeted optimization of individual components while maintaining system-wide compatibility.
