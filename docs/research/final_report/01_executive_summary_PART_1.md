# Executive Summary: Research on PQC Integration for Fava (Initial Cycle)

**Date:** 2025-06-02
**Research Objective:** To conduct deep and comprehensive research relevant to integrating Post-Quantum Cryptography (PQC) into the Fava codebase, informing the SPARC Specification phase.

This document summarizes the findings and outcomes of the initial research cycle focused on Post-Quantum Cryptography (PQC) integration for the Fava project. The research leveraged the strategic guidance from [`docs/Plan.MD`](../../Plan.MD) and existing code comprehension reports.

## Key Findings & Insights (Initial Cycle)

1.  **NIST PQC Standardization is Progressing:** NIST has finalized initial standards (ML-KEM/Kyber, ML-DSA/Dilithium, SLH-DSA/SPHINCS+ in August 2024) and continues to select more algorithms (HQC in March 2025, Falcon draft expected 2025). This provides a solid foundation for PQC algorithm choices. However, specific OIDs and detailed, consolidated performance benchmarks for all variants require further targeted lookup in official FIPS documents.

2.  **Cryptographic Agility is Paramount:** The PQC landscape is dynamic. Best practices emphasize designing systems with cryptographic agility, primarily through abstraction layers (like Fava's proposed `CryptoService`) and support for hybrid (classical + PQC) modes during transition.

3.  **Ecosystem Maturity Varies:**
    *   **GnuPG (GPG):** Stable releases currently lack native PQC support, a critical factor for Fava's encrypted Beancount files if relying solely on GPG. Experimental work is ongoing.
    *   **TLS & Certificates:** PQC in TLS (via hybrid KEMs) is emerging, with reverse proxies being the recommended deployment strategy for applications like Fava. PQC CA certificate issuance is not expected before 2026. Browser support for PQC KEMs is experimental.
    *   **Hashing:** SHA-3 (or SHAKE variants) is recommended over SHA-256 for long-term quantum resistance. Frontend SHA-3 requires JavaScript libraries due to lack of native browser API support.
    *   **WASM Integrity:** PQC digital signatures (e.g., Dilithium) offer stronger security than SRI alone. `liboqs-js` is a key library for frontend verification.
    *   **Libraries:** `liboqs` (C library) and its Python (`oqs-python`) and JavaScript (`liboqs-js`) wrappers are central to accessing PQC implementations. Standard Python libraries are yet to fully integrate PQC.

4.  **Resource Implications:** PQC algorithms generally involve larger key/signature sizes and can have performance overheads compared to classical cryptography. This needs careful consideration for Fava's performance and user experience.

5.  **Identified Knowledge Gaps:** Numerous specific knowledge gaps have been identified across all research areas (detailed in [`docs/research/analysis/knowledge_gaps_PART_1.md`](../../analysis/knowledge_gaps_PART_1.md)). These include precise performance metrics, final OID lists, specific PQC support details in GPG and standard Python libraries, and maturity of certain frontend libraries.

## Research Process & Deliverables (Initial Cycle)

*   **Methodology:** A recursive, self-learning approach was adopted.
    *   **Initialization & Scoping:** Defined research scope, key questions, and information sources based on [`docs/Plan.MD`](../../Plan.MD).
    *   **Initial Data Collection:** Conducted broad AI-powered searches (via Perplexity MCP tool) based on key questions.
    *   **Targeted Research (Limited):** Conducted initial targeted searches to fill high-priority gaps (e.g., FIPS details, OID structure).
    *   **First-Pass Analysis & Gap Identification:** Synthesized findings, identified patterns, and consolidated knowledge gaps.
*   **Documentation Created:**
    *   Initial Queries: Scope, Key Questions (Parts 1-2), Information Sources.
    *   Data Collection (Primary Findings): Seven documents covering NIST status, crypto agility, security models, GPG/Beancount, Fava-side decryption, TLS/proxies, hashing, WASM integrity, PQC libraries, FIPS details, and OID structures.
    *   Analysis: Knowledge Gaps, Expert Insights (initial), Identified Patterns, Contradictions.
    *   This Executive Summary and a Methodology document.

## Current Status & Next Steps

This initial research cycle has successfully established a foundational understanding of the PQC landscape relevant to Fava and has produced a structured set of preliminary research documents. Key areas of PQC application within Fava, as outlined in [`docs/Plan.MD`](../../Plan.MD), have been investigated at a high level.

The research is currently at the end of the first major iteration of data collection and analysis. A significant number of knowledge gaps remain, as documented in [`docs/research/analysis/knowledge_gaps_PART_1.md`](../../analysis/knowledge_gaps_PART_1.md).

**The immediate next step is to undertake further targeted research cycles to address these identified knowledge gaps.** This will involve more specific queries to the AI search tool, focusing on obtaining concrete data points (e.g., exact OIDs, detailed performance benchmarks from FIPS documents or reputable sources, specific library APIs and maturity).

This initial body of research provides a strong starting point for the SPARC Specification phase, particularly for high-level planning and identifying areas requiring deeper specification based on PQC constraints and opportunities. The findings will help in defining realistic high-level acceptance tests for PQC-enhanced features.

---
## Update: Findings from Targeted Research Cycle (2025-06-02)

A targeted follow-up research cycle was conducted to address critical knowledge gaps identified previously and points raised in the Devil's Advocate critique ([`docs/devil/PQC_SPARC_Specification_Phase_Critique.md`](../../../docs/devil/PQC_SPARC_Specification_Phase_Critique.md)). This cycle focused on PQC algorithm metrics, OIDs, hybrid schemes, Python PQC library ecosystem, external tooling dependencies, and contingency planning.

**Key Resolutions and New Insights:**

1.  **PQC Algorithm Metrics & Selection (G1):**
    *   **NIST FIPS Details (G1.1):** Confirmed latest status of FIPS 203 (ML-KEM), 204 (ML-DSA), 205 (SLH-DSA). No substantive changes since Aug 2024. Supporting docs like SP 800-227 (ML-KEM guidelines) are emerging. (See: [`docs/research/data_collection/primary_findings/pf_nist_fips_updates_g1_1_PART_1.md`](../data_collection/primary_findings/pf_nist_fips_updates_g1_1_PART_1.md))
    *   **OIDs for X.509 (G1.2):** IETF drafts define OID structures for ML-KEM, ML-DSA, etc., though final assignments are pending. (See: [`docs/research/data_collection/primary_findings/pf_pqc_oids_x509_g1_2_PART_1.md`](../data_collection/primary_findings/pf_pqc_oids_x509_g1_2_PART_1.md))
    *   **Performance Benchmarks (G1.3):** Concrete benchmarks (latency, throughput, memory) for Kyber, Dilithium, Falcon, SPHINCS+ in C (relevant for Python wrappers) gathered. (See: [`docs/research/data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_performance_benchmarks_g1_3_PART_1.md))
    *   **Security Levels (G1.4):** NIST PQC security levels (1-5) and their classical equivalents (AES, SHA) mapped to specific parameter sets for the target algorithms. (See: [`docs/research/data_collection/primary_findings/pf_pqc_security_levels_g1_4_PART_1.md`](../data_collection/primary_findings/pf_pqc_security_levels_g1_4_PART_1.md))

2.  **Hybrid PQC Schemes (G2):**
    *   **Best Practices (G2.1):** Documented methods for hybrid KEMs (secret concatenation, KDF usage) and signatures (concatenation), referencing IETF drafts and NIST SP 800-56C. (See: [`docs/research/data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md`](../data_collection/primary_findings/pf_hybrid_pqc_schemes_g2_1_PART_1.md))
    *   **Fava Recommendations (G2.2):** Specific hybrid algorithm pairings (e.g., X25519+Kyber768, ECDSA+Dilithium3) and construction methods proposed for Fava's data-at-rest, data-in-transit, and WASM signing use cases. (See: [`docs/research/data_collection/primary_findings/pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md`](../data_collection/primary_findings/pf_hybrid_pqc_fava_recommendations_g2_2_PART_1.md))

3.  **PQC Library Ecosystem - Python Focus (G3):**
    *   **`oqs-python` Deep Dive (G3.1):** Analyzed current maintenance, security (Trail of Bits audit of liboqs), community support, and ease of use for target PQC algorithms. `oqs-python` remains the primary viable option. (See: [`docs/research/data_collection/primary_findings/pf_oqs_python_analysis_g3_1_PART_1.md`](../data_collection/primary_findings/pf_oqs_python_analysis_g3_1_PART_1.md))
    *   **Alternatives to `oqs-python` (G3.2):** Mature, comprehensive alternatives are scarce. `pyoqs_sdk` appears less maintained. Custom integrations or bindings to other C/Rust PQC libs are significant undertakings. (See: [`docs/research/data_collection/primary_findings/pf_oqs_python_alternatives_g3_2_PART_1.md`](../data_collection/primary_findings/pf_oqs_python_alternatives_g3_2_PART_1.md))
    *   **JS/WASM PQC Libraries (G3.3):** `liboqs-js` re-evaluated as the primary option for frontend PQC. Alternatives are algorithm-specific or less mature. Bundle size and WASM performance are key considerations. (See: [`docs/research/data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_js_wasm_libs_g3_3_PART_1.md))

4.  **External Tooling & Dependencies (G4) & Contingency Planning:**
    *   **GPG PQC Support (G4.1):** Official GPG PQC support is still distant. Contingencies involve Fava-guided hybrid encryption using `oqs-python` or standalone PQC tools. (See: [`docs/research/data_collection/primary_findings/pf_gpg_pqc_status_g4_1_PART_1.md`](../data_collection/primary_findings/pf_gpg_pqc_status_g4_1_PART_1.md) and [`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](../data_collection/primary_findings/pf_tooling_contingency_PART_1.md))
    *   **PQC-TLS Reverse Proxies (G4.2):** Nginx/Caddy PQC support is experimental, requiring custom builds with PQC-OpenSSL. Contingencies include application-layer PQC over classical TLS. (See: [`docs/research/data_collection/primary_findings/pf_pqc_tls_proxies_clients_g4_2_PART_1.md`](../data_collection/primary_findings/pf_pqc_tls_proxies_clients_g4_2_PART_1.md) and [`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](../data_collection/primary_findings/pf_tooling_contingency_PART_1.md))
    *   **PQC CLI Signing Tool (G4.3):** Utilities from `liboqs` or custom Python scripts using `oqs-python` are primary options for WASM signing. (See: [`docs/research/data_collection/primary_findings/pf_pqc_cli_signing_tools_g4_3_PART_1.md`](../data_collection/primary_findings/pf_pqc_cli_signing_tools_g4_3_PART_1.md) and [`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](../data_collection/primary_findings/pf_tooling_contingency_PART_1.md))

**Overall Status after Targeted Research:**
The targeted research cycle has successfully addressed the critical knowledge gaps concerning PQC algorithm details, hybrid scheme construction, library choices, and external tooling. The updated [`docs/research/analysis/knowledge_gaps_PART_1.md`](../../analysis/knowledge_gaps_PART_1.md) reflects these resolutions. This significantly strengthens the foundation for finalizing Fava's PQC integration specifications and defining realistic acceptance tests. While the PQC ecosystem is still evolving, particularly for user-friendly tooling like GPG, the research provides actionable strategies and contingency plans for Fava.