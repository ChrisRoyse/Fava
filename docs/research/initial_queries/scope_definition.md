# Research Scope Definition: Integrating Post-Quantum Cryptography into Fava

## 1. Overall Research Objective

To conduct deep and comprehensive research to inform the integration of Post-Quantum Cryptography (PQC) into the Fava codebase. This research will support the SPARC Specification phase, particularly the definition of high-level acceptance tests and the primary project planning document.

## 2. Context and Blueprint

This research is based on the overall project goal of "Integrate Post-Quantum Cryptography into the Fava codebase." Key contextual information and strategic direction are derived from:

*   **Primary Strategic Plan:** [`docs/Plan.MD`](docs/Plan.MD)
*   **Existing Fava Codebase Structure:** As detailed in various code comprehension reports (e.g., [`docs/reports/srcreports/code_comprehension_summary.md`](docs/reports/srcreports/code_comprehension_summary.md)).

## 3. Key Areas of Investigation (derived from [`docs/Plan.MD`](docs/Plan.MD))

The research will focus on the cryptographic areas identified in the strategic plan:

*   **Data at Rest:** Primarily concerning the encryption of Beancount files. This involves understanding Fava's reliance on Beancount's loader (typically GPG) and exploring PQC alternatives or PQC-updated GPG mechanisms.
*   **Data in Transit:** Focusing on HTTPS/TLS for all client-server communication. This includes server-side TLS configuration (e.g., via reverse proxies or underlying Python web servers like Cheroot) and browser capabilities.
*   **Data Integrity (Hashing):** Investigating the current use of SHA256 for file integrity and optimistic concurrency, and evaluating the need and options for transitioning to PQC-resistant hash functions (e.g., SHA-3).
*   **WASM Module Integrity:** Researching methods (e.g., PQC digital signatures) to ensure the integrity of WebAssembly modules used in the frontend (e.g., `tree-sitter-beancount.wasm`).

## 4. Cross-Cutting Concerns

Beyond specific cryptographic areas, the research will address:

*   **Cryptographic Agility:** Strategies for designing Fava to easily switch between classical, PQC, and hybrid cryptographic algorithms, primarily through abstraction layers (CryptoService).
*   **Suitable PQC Algorithms:** Identifying NIST-recommended or other suitable PQC algorithms (KEMs like CRYSTALS-Kyber; digital signatures like CRYSTALS-Dilithium, Falcon, SPHINCS+) for each application area within Fava.
*   **Performance Implications:** Analyzing the potential performance impact (e.g., key sizes, computation time) of PQC algorithms within the Fava context (Python backend, JavaScript/WASM frontend).
*   **Python PQC Libraries:** Surveying existing Python libraries for PQC (e.g., bindings for liboqs) and assessing their maturity, stability, and suitability for Fava.
*   **JavaScript/WASM PQC Libraries:** Identifying libraries for frontend PQC operations (e.g., liboqs-js) for tasks like WASM verification or PQC hashing.
*   **Impact on Architecture and Data Formats:** Assessing how PQC integration might affect Fava's existing architecture, data formats (e.g., for encrypted files), and user workflows.
*   **Security Considerations:** Investigating PQC-specific security issues, such as side-channel vulnerabilities, key management complexities (larger key sizes), and the evolving threat landscape.
*   **Challenges and Mitigation:** Identifying potential challenges in the integration process (e.g., dependency on Beancount/GPG PQC support, library maturity, user experience) and proposing mitigation strategies.
*   **Testing and Validation:** Approaches for testing PQC implementations, including unit tests, integration tests (e.g., PQC encrypted files, frontend-backend hash consistency), and TLS configuration verification.
*   **Phased Rollout/Hybrid Approaches:** Strategies for a gradual transition, potentially involving hybrid schemes (classical + PQC) as an interim step.

## 5. Exclusions (Initial Scope)

*   Detailed implementation of the `CryptoService` or other PQC-related code. The research aims to inform these implementations.
*   Modifications to Beancount itself. The research will consider Beancount's PQC readiness as an external factor.
*   Exhaustive security audit of PQC algorithms (will rely on NIST and established cryptographic community findings).

## 6. Deliverables

The primary deliverable will be a structured set of research documents within the `docs/research/` directory, culminating in a final report. These documents will provide actionable insights for the SPARC Specification phase.