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