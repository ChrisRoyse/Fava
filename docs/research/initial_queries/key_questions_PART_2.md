# Key Research Questions for PQC Integration in Fava - Part 2

This document continues the list of key research questions for integrating Post-Quantum Cryptography (PQC) into Fava.

## V. PQC for WASM Module Integrity

13. **PQC Digital Signatures for WASM:**
    *   Which NIST-standardized digital signature algorithms (e.g., CRYSTALS-Dilithium, Falcon, SPHINCS+) are most suitable for signing WASM modules?
        *   Consider signature size, verification speed, and key generation complexity.
    *   What tools or libraries are available for generating PQC signatures during a build process (Python-based or command-line)?
    *   How would the PQC public key for verification be securely distributed with Fava's frontend?
14. **Frontend WASM Signature Verification:**
    *   What JavaScript/WASM libraries are available and mature enough for verifying PQC digital signatures in the browser (e.g., liboqs-js or similar)?
    *   What is the performance overhead of PQC signature verification on the client-side?
    *   How would this integrate with the existing WASM loading mechanism in `frontend/src/codemirror/beancount.ts`?
15. **Alternative/Complementary WASM Integrity Mechanisms:**
    *   How does Subresource Integrity (SRI) compare to PQC digital signatures for WASM integrity? Can they be used complementarily?
    *   Are there other emerging standards or best practices for ensuring WASM module integrity in web applications?

## VI. PQC Libraries & Tooling

16. **Python PQC Libraries:**
    *   What is the current state of `liboqs` (Open Quantum Safe) and its Python bindings (`oqs-python`)?
        *   Which PQC algorithms are well-supported and tested?
        *   What is the stability and maturity of the library for production use?
        *   Are there installation considerations or dependencies for Fava's environment?
    *   Are there other promising Python PQC libraries or frameworks emerging?
    *   What is the timeline or likelihood of PQC algorithms being integrated into Python's standard `hashlib`, `ssl`, or the `cryptography` package?
17. **JavaScript/WASM PQC Libraries (Frontend):**
    *   Beyond `liboqs-js`, are there other viable JavaScript or WASM-compiled PQC libraries for frontend use (signatures, hashing)?
    *   What is their maturity, browser compatibility, and bundle size impact?
18. **Build-time PQC Tools:**
    *   What tools are needed for a build process that incorporates PQC (e.g., signing WASM modules, potentially pre-encrypting assets if applicable)?

## VII. Implementation & Integration Strategy

19. **`CryptoService` Abstraction Layer:**
    *   What specific interfaces and methods should the backend `CryptoService` (Python) and a potential frontend crypto abstraction (TypeScript) expose to cover all identified PQC use cases (KEMs, signatures, hashing)?
    *   How should configuration for these services be managed and loaded from Fava's options?
    *   What error handling and reporting mechanisms are needed for cryptographic operations?
20. **Performance Benchmarking:**
    *   What are the expected performance impacts (latency, throughput, CPU/memory usage) of introducing PQC KEMs, signatures, and hashes in Fava's critical paths (e.g., file loading, API requests, content saving)?
    *   How can these be benchmarked effectively in Fava's context?
21. **Key Management for Fava-Handled PQC:**
    *   If Fava were to directly manage PQC keys (e.g., for a Fava-specific file encryption format), what are secure practices for key generation, storage, derivation, and user interaction? (This is a complex area, initial focus might be on leveraging external tools like PQC-GPG).
22. **User Experience (UX) for PQC:**
    *   How will PQC integration affect Fava users, particularly concerning encrypted Beancount files?
    *   What guidance, documentation, or UI changes are needed to help users manage PQC keys or understand new security features?
    *   How can the transition be made as seamless as possible?
23. **Phased Rollout & Hybrid Modes:**
    *   What are the specific technical steps and considerations for implementing the phased rollout proposed in [`docs/Plan.MD`](docs/Plan.MD) (Abstraction -> Hybrid -> Pure PQC)?
    *   What are the security trade-offs of hybrid modes versus pure PQC modes?
24. **Dependency Management:**
    *   How will PQC library dependencies be managed in Fava's `pyproject.toml` and frontend package management?
    *   Are there potential conflicts or compatibility issues with existing dependencies?

## VIII. Testing & Validation

25. **PQC Test Vectors:**
    *   Where can official or reliable test vectors be found for the chosen PQC algorithms to ensure correct implementation of cryptographic primitives?
26. **Integration Testing Strategies:**
    *   How can end-to-end PQC scenarios be tested? (e.g., creating a Beancount file with PQC-GPG, loading it in Fava; verifying a PQC-signed WASM module).
    *   What tools can be used to test PQC TLS configurations (e.g., `testssl.sh` with PQC support, or specific client tools)?
27. **Security Testing for PQC:**
    *   Beyond functional testing, are there specific security testing methodologies relevant to PQC implementations (e.g., checking for side-channel leakage if Fava implements raw PQC)?

## IX. Documentation & Community

28. **Developer and User Documentation:**
    *   What specific documentation will be needed for developers contributing to Fava's PQC features?
    *   What documentation will be needed for Fava users regarding PQC setup, usage, and security implications?
29. **Monitoring the PQC Landscape:**
    *   What are reliable sources (mailing lists, conferences, research groups) for ongoing monitoring of PQC developments, new attacks, or changes in standardization?