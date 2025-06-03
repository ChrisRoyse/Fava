# Project Master Plan: Post-Quantum Cryptography (PQC) Integration for Fava
**Role: Master Project Plan**
**Version:** 1.1
**Date:** 2025-06-02

## Changelog
*   **1.1 (2025-06-02):**
    *   Clarified "Specification Completed" status for Phase 1 to reflect iterative refinement based on Devil's Advocate critique ([`docs/devil/PQC_SPARC_Specification_Phase_Critique.md`](docs/devil/PQC_SPARC_Specification_Phase_Critique.md)) and targeted research. Specifications and MATP are now baseline v1.1.
    *   Clarified Master Plan hierarchy in Introduction: This document supersedes [`docs/Plan.MD`](docs/Plan.MD) as the operational PQC Master Plan.
    *   Updated references to PQC Specification Documents and Master Acceptance Test Plan to v1.1 versions.
    *   Revised Assumptions, Dependencies (Section 6) and Risk Management (Section 7) to align with latest research on PQC tooling (GPG, proxies, signing tools from [`docs/research/final_report/01_executive_summary_PART_1.md`](docs/research/final_report/01_executive_summary_PART_1.md) and v1.1 specs, e.g., Fava-driven encryption in [`docs/specifications/PQC_Data_At_Rest_Spec.md`](docs/specifications/PQC_Data_At_Rest_Spec.md)).
    *   Ensured NFR verification descriptions (Phase 4 & 5 AVERs) are consistent with v1.1 specifications and the v1.1 Master Acceptance Test Plan's "Basic Performance Indicator Tests."
    *   General review for coherence with all v1.1 artifacts.
*   **1.0 (Initial Version):** First draft of the PQC Master Project Plan.

## 1. Introduction
   - Project Goal: Integrate Post-Quantum Cryptography (PQC) into the Fava codebase to enhance long-term security against quantum threats.
   - Document Purpose: This document outlines the phased approach, key tasks, deliverables, and AI Verifiable End Results (AVERs) for the PQC integration project. It follows the SPARC (Specification, Pseudocode, Architecture, Refinement, Completion) methodology and serves as the central planning artifact.
   - Key Input Documents:
     - Initial Strategic Input: [`docs/Plan.MD`](docs/Plan.MD) (This [`docs/ProjectMasterPlan_PQC.md`](docs/ProjectMasterPlan_PQC.md) is the definitive, detailed, and operational Master Project Plan for the PQC integration, superseding [`docs/Plan.MD`](docs/Plan.MD) which served as an initial high-level strategic input.)
     - Research Reports Root: [`docs/research/`](docs/research/) (Contains detailed findings, PQC algorithm analysis, library evaluations, and knowledge gaps, including [`docs/research/final_report/01_executive_summary_PART_1.md`](docs/research/final_report/01_executive_summary_PART_1.md))
     - High-Level Test Strategy: [`docs/research/PQC_High_Level_Test_Strategy.md`](docs/research/PQC_High_Level_Test_Strategy.md)
     - PQC Specification Documents (v1.1) Root: [`docs/specifications/`](docs/specifications/) (Covering Data at Rest, Data in Transit, Hashing, WASM Module Integrity, Cryptographic Agility)
     - Master Acceptance Test Plan (v1.1): [`docs/tests/PQC_Master_Acceptance_Test_Plan.md`](docs/tests/PQC_Master_Acceptance_Test_Plan.md)
     - High-Level Acceptance Tests Root: [`tests/acceptance/`](tests/acceptance/)

## 2. SPARC Methodology Alignment
   - This project adheres to the SPARC framework:
     - **Specification (Phase 1 - Iteratively Refined & Baselined):** Defining *what* needs to be built. Initial outputs (v1.0 specs, research, MATP v1.0) underwent review and targeted research, leading to finalized v1.1 baseline artifacts. This Project Master Plan (v1.1) is also an output of this refined phase.
     - **Pseudocode (Phase 2):** Detailing *how* the logic will work in a language-agnostic manner.
     - **Architecture (Phase 3):** Defining the *structure* and interaction of components.
     - **Refinement (Phase 4):** Iteratively *building and testing* the features (Granular Test Creation, Test-Driven Development, Module Reviews).
     - **Completion (Phase 5):** Finalizing *integration, end-to-end testing, documentation, and deployment preparation*.
   - This Master Project Plan primarily details the activities from the Pseudocode phase onwards, leveraging the v1.1 artifacts from the completed Specification phase.

## 3. Project Phases and Tasks

### Phase 1: SPARC - Specification (Iteratively Refined & Baselined)
   - **Objective:** Establish a comprehensive understanding of PQC, define detailed requirements for its integration into Fava, and outline high-level success criteria, culminating in finalized v1.1 baseline artifacts.
   - **Status:** While the initial *drafting* of specification artifacts (v1.0) was completed and reviewed, this phase underwent an iterative refinement loop based on advocate feedback ([`docs/devil/PQC_SPARC_Specification_Phase_Critique.md`](docs/devil/PQC_SPARC_Specification_Phase_Critique.md)) and further targeted research (summarized in [`docs/research/final_report/01_executive_summary_PART_1.md`](docs/research/final_report/01_executive_summary_PART_1.md) - Update from Targeted Research Cycle). The *current versions* of the specifications (v1.1 in [`docs/specifications/`](docs/specifications/)) and the Master Acceptance Test Plan (v1.1 in [`docs/tests/`](docs/tests/)) are now considered the finalized baseline for subsequent SPARC phases, having incorporated this critical feedback and gap-filling research.
   - **Key Outputs (v1.1 Baseline Artifacts):**
     - Research Reports: [`docs/research/`](docs/research/) (e.g., [`docs/research/final_report/01_executive_summary_PART_1.md`](docs/research/final_report/01_executive_summary_PART_1.md), [`docs/research/analysis/knowledge_gaps_PART_1.md`](docs/research/analysis/knowledge_gaps_PART_1.md) - updated post-targeted research)
     - High-Level Test Strategy: [`docs/research/PQC_High_Level_Test_Strategy.md`](docs/research/PQC_High_Level_Test_Strategy.md)
     - PQC Specification Documents (v1.1):
       - [`docs/specifications/PQC_Data_At_Rest_Spec.md`](docs/specifications/PQC_Data_At_Rest_Spec.md)
       - [`docs/specifications/PQC_Data_In_Transit_Spec.md`](docs/specifications/PQC_Data_In_Transit_Spec.md)
       - [`docs/specifications/PQC_Hashing_Spec.md`](docs/specifications/PQC_Hashing_Spec.md)
       - [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](docs/specifications/PQC_WASM_Module_Integrity_Spec.md)
       - [`docs/specifications/PQC_Cryptographic_Agility_Spec.md`](docs/specifications/PQC_Cryptographic_Agility_Spec.md)
     - Master Acceptance Test Plan (v1.1): [`docs/tests/PQC_Master_Acceptance_Test_Plan.md`](docs/tests/PQC_Master_Acceptance_Test_Plan.md)
     - High-Level Acceptance Tests:
       - [`tests/acceptance/PQC_Data_At_Rest_Acceptance_Tests.md`](tests/acceptance/PQC_Data_At_Rest_Acceptance_Tests.md)
       - [`tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md`](tests/acceptance/PQC_Data_In_Transit_Acceptance_Tests.md)
       - [`tests/acceptance/PQC_Hashing_Acceptance_Tests.md`](tests/acceptance/PQC_Hashing_Acceptance_Tests.md)
       - [`tests/acceptance/PQC_WASM_Module_Integrity_Acceptance_Tests.md`](tests/acceptance/PQC_WASM_Module_Integrity_Acceptance_Tests.md)
       - [`tests/acceptance/PQC_Cryptographic_Agility_Acceptance_Tests.md`](tests/acceptance/PQC_Cryptographic_Agility_Acceptance_Tests.md)
     - This Project Master Plan (v1.1): [`docs/ProjectMasterPlan_PQC.md`](docs/ProjectMasterPlan_PQC.md)
   - **AVER for Orchestrator (SPARC Specification Phase) Task Completion:** All listed Specification phase documents are at version 1.1 (or later, if further refined) in their respective directories, reflecting incorporation of feedback and targeted research. The `orchestrator-state-scribe` has been successfully dispatched to record these v1.1 baseline artifacts.

### Phase 2: SPARC - Pseudocode
   - **Objective:** Translate the detailed v1.1 specifications into language-agnostic, detailed pseudocode for each PQC focus area, providing a clear logical blueprint for implementation.
   - **Overall AVER for Phase Completion:** All specified pseudocode documents are created in [`docs/pseudocode/`](docs/pseudocode/), reviewed for logical correctness, completeness against v1.1 specs, and clarity, and then finalized.
   - **Tasks:**
     - **2.1 Create Detailed Pseudocode for PQC Data at Rest**
       - Input: [`docs/specifications/PQC_Data_At_Rest_Spec.md`](docs/specifications/PQC_Data_At_Rest_Spec.md) (v1.1)
       - Output: [`docs/pseudocode/PQC_Data_At_Rest_Pseudo.md`](docs/pseudocode/PQC_Data_At_Rest_Pseudo.md)
       - AVER: Pseudocode document exists. It covers all functional requirements from the v1.1 spec, including logic for Fava-driven PQC hybrid encryption/decryption flows (e.g., using X25519+Kyber-768 KEMs with AES-256-GCM), key handling (passphrase derivation, storage, retrieval), interaction with classical GPG for backward compatibility, error conditions, and data format considerations. Document is reviewed and approved.
     - **2.2 Create Detailed Pseudocode for PQC Data in Transit**
       - Input: [`docs/specifications/PQC_Data_In_Transit_Spec.md`](docs/specifications/PQC_Data_In_Transit_Spec.md) (v1.1)
       - Output: [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](docs/pseudocode/PQC_Data_In_Transit_Pseudo.md)
       - AVER: Pseudocode document exists. It outlines logic for Fava's configuration documentation regarding operation behind a PQC-TLS enabled reverse proxy (e.g., X25519Kyber768), including how Fava might be made aware of or assert PQC protection (e.g., checking headers set by proxy, configuration flags). It does not detail TLS handshake (proxy's role) but focuses on Fava's operational assumptions and interactions. Document is reviewed and approved.
     - **2.3 Create Detailed Pseudocode for PQC Hashing**
       - Input: [`docs/specifications/PQC_Hashing_Spec.md`](docs/specifications/PQC_Hashing_Spec.md) (v1.1)
       - Output: [`docs/pseudocode/PQC_Hashing_Pseudo.md`](docs/pseudocode/PQC_Hashing_Pseudo.md)
       - AVER: Pseudocode document exists. It details logic for selecting PQC-resistant hash functions (e.g., SHA3-256 default, SHA-256 fallback) based on configuration, applying them to relevant data, handling algorithm choice for new vs. existing data, and error handling. Document is reviewed and approved.
     - **2.4 Create Detailed Pseudocode for PQC WASM Module Integrity**
       - Input: [`docs/specifications/PQC_WASM_Module_Integrity_Spec.md`](docs/specifications/PQC_WASM_Module_Integrity_Spec.md) (v1.1)
       - Output: [`docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md`](docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md)
       - AVER: Pseudocode document exists. It describes frontend logic for fetching the WASM module, fetching its PQC signature (e.g., Dilithium3), performing PQC signature verification using a PQC library (e.g., `liboqs-js`), and handling verification success (load module) or failure (error, fallback). Document is reviewed and approved.
     - **2.5 Create Detailed Pseudocode for PQC Cryptographic Agility**
       - Input: [`docs/specifications/PQC_Cryptographic_Agility_Spec.md`](docs/specifications/PQC_Cryptographic_Agility_Spec.md) (v1.1)
       - Output: [`docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md`](docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md)
       - AVER: Pseudocode document exists. It outlines generic mechanisms for configuring and switching cryptographic algorithms (KEMs, signature schemes, hash functions) across relevant Fava modules, including management of multiple decryption suites for data at rest. This includes how algorithm choices are stored, loaded, and passed to cryptographic operations, and how metadata about algorithm usage might be stored. Document is reviewed and approved.

### Phase 3: SPARC - Architecture
   - **Objective:** Define the high-level system and module architecture for integrating PQC components into Fava, based on the pseudocode, identifying new components, modifications to existing ones, and their interactions.
   - **Overall AVER for Phase Completion:** All specified architecture documents are created in [`docs/architecture/`](docs/architecture/), include diagrams and narrative descriptions, are reviewed for soundness, feasibility, and alignment with v1.1 specs/pseudocode, and then finalized.
   - **Tasks:**
     - **3.1 Design Architecture for PQC Data at Rest Integration**
       - Input: [`docs/pseudocode/PQC_Data_At_Rest_Pseudo.md`](docs/pseudocode/PQC_Data_At_Rest_Pseudo.md), Fava's existing file handling and GPG architecture.
       - Output: [`docs/architecture/PQC_Data_At_Rest_Arch.md`](docs/architecture/PQC_Data_At_Rest_Arch.md) (Component diagrams, sequence diagrams, data flow diagrams).
       - AVER: Architecture document exists. It clearly defines the `CryptoService` for PQC data at rest, including Fava-driven hybrid encryption/decryption, interaction with classical GPG, new/modified components, data flow, and interfaces. Reviewed and approved.
     - **3.2 Design Architecture for PQC Data in Transit Considerations**
       - Input: [`docs/pseudocode/PQC_Data_In_Transit_Pseudo.md`](docs/pseudocode/PQC_Data_In_Transit_Pseudo.md), Fava's deployment architecture.
       - Output: [`docs/architecture/PQC_Data_In_Transit_Arch.md`](docs/architecture/PQC_Data_In_Transit_Arch.md) (Deployment diagrams showing Fava and PQC proxy, configuration interfaces).
       - AVER: Architecture document exists. It clarifies Fava's architectural assumptions when operating with PQC-TLS via a reverse proxy, including necessary configuration points within Fava documentation to align with proxy behavior. Reviewed and approved.
     - **3.3 Design Architecture for PQC Hashing Integration**
       - Input: [`docs/pseudocode/PQC_Hashing_Pseudo.md`](docs/pseudocode/PQC_Hashing_Pseudo.md), relevant Fava modules.
       - Output: [`docs/architecture/PQC_Hashing_Arch.md`](docs/architecture/PQC_Hashing_Arch.md) (Identifying modules requiring PQC hashing, abstraction layers for hashing via `CryptoService`).
       - AVER: Architecture document exists. It specifies where PQC hashing will be implemented (e.g., `CryptoService`, specific classes), how algorithm selection is managed architecturally, and any necessary abstraction layers to simplify usage. Reviewed and approved.
     - **3.4 Design Architecture for PQC WASM Module Integrity**
       - Input: [`docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md`](docs/pseudocode/PQC_WASM_Module_Integrity_Pseudo.md), Fava's frontend architecture.
       - Output: [`docs/architecture/PQC_WASM_Module_Integrity_Arch.md`](docs/architecture/PQC_WASM_Module_Integrity_Arch.md) (Frontend component diagrams, interaction with signature/module sources, PQC verification library (`liboqs-js`) integration).
       - AVER: Architecture document exists. It details the frontend components involved in fetching the WASM module and its signature, integrating the PQC verification logic, and managing the UI based on verification outcome. Reviewed and approved.
     - **3.5 Design Architecture for Cryptographic Agility Mechanisms**
       - Input: [`docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md`](docs/pseudocode/PQC_Cryptographic_Agility_Pseudo.md), overall Fava architecture.
       - Output: [`docs/architecture/PQC_Cryptographic_Agility_Arch.md`](docs/architecture/PQC_Cryptographic_Agility_Arch.md) (Configuration management system, `CryptoService` factory patterns, metadata handling, support for multiple decryption suites).
       - AVER: Architecture document exists. It describes the system-wide architectural patterns for achieving cryptographic agility, including how configurations are managed, how cryptographic services are instantiated with selected algorithms, and how algorithm metadata is associated with data. Reviewed and approved.

### Phase 4: SPARC - Refinement (Iterative)
   - **Objective:** Implement PQC features in an iterative, test-driven manner, ensuring each component is robust, secure, and performs adequately. This phase involves cycles of Granular Test Specification & Generation, Feature Implementation, and Module-Level Reviews.
   - **Overall AVER for Phase Completion:** All PQC features across all focus areas are implemented according to their v1.1 specifications, pseudocode, and architecture. All granular tests for these features pass. Security and optimization reviews are completed, and critical findings are addressed. The codebase is stable, and relevant high-level acceptance tests pass for the implemented features. Performance meets NFRs as verified by Basic Performance Indicator Tests.
   - **Iterative Sub-Phases (repeated for each PQC focus area and its sub-features):**
     - **4.X.A Granular Test Specification & Generation**
       - Input: Spec ([`docs/specifications/PQC_Area_Spec.md`](docs/specifications/PQC_Area_Spec.md) v1.1), Pseudocode ([`docs/pseudocode/PQC_Area_Pseudo.md`](docs/pseudocode/PQC_Area_Pseudo.md)), Architecture ([`docs/architecture/PQC_Area_Arch.md`](docs/architecture/PQC_Area_Arch.md)).
       - Output: Granular Test Plan ([`docs/test-plans/PQC_Area_Feature_Test_Plan.md`](docs/test-plans/PQC_Area_Feature_Test_Plan.md)), Test Code ([`tests/granular/test_pqc_area_feature.py`](tests/granular/test_pqc_area_feature.py) or similar).
       - AVER: Granular test plan document exists. Test code file exists, containing stubs for tests covering key functionalities, edge cases, and error conditions derived from pseudocode/spec. Tests are runnable and initially failing or skipped (TDD).
     - **4.X.B Feature Implementation & Iteration (TDD)**
       - Input: Granular tests, Pseudocode, Architecture.
       - Output: Implemented code for the PQC feature/sub-feature within the Fava codebase.
       - AVER: All granular tests defined in 4.X.A for the specific feature/sub-feature pass. Code is committed to a feature branch. Code review comments (initial pass) are addressed.
     - **4.X.C Module-Level Review & Refinement (Security, Optimization, Code Quality)**
       - Input: Implemented code for the feature/module.
       - Output: Review reports (e.g., [`docs/reports/review_PQC_Area_Feature_Security.md`](docs/reports/review_PQC_Area_Feature_Security.md), [`docs/reports/review_PQC_Area_Feature_Optimization.md`](docs/reports/review_PQC_Area_Feature_Optimization.md)), refined code.
       - AVER: Security and optimization review reports exist for the module. Any critical or high-priority issues identified are addressed in the code. All granular tests for the feature still pass. Basic Performance Indicator Tests for the module align with NFRs in v1.1 specs.

### Phase 5: SPARC - Completion
   - **Objective:** Ensure all PQC features are cohesively integrated, the entire system passes end-to-end acceptance testing, final documentation is produced, and the application is prepared for potential deployment.
   - **Overall AVER for Phase Completion:** All high-level acceptance tests in [`tests/acceptance/`](tests/acceptance/) (aligned with v1.1 MATP) pass consistently in the fully integrated environment. Final user and developer documentation is complete and accurate. Performance benchmarks (derived from Basic Performance Indicator Tests) meet NFRs from v1.1 specifications, or deviations are justified. Deployment artifacts (if applicable for this stage) are prepared.
   - **Tasks:**
     - **5.1 System Integration & Full Acceptance Testing**
       - Input: All implemented and unit-tested PQC features, High-Level Acceptance Tests ([`tests/acceptance/`](tests/acceptance/)), v1.1 MATP ([`docs/tests/PQC_Master_Acceptance_Test_Plan.md`](docs/tests/PQC_Master_Acceptance_Test_Plan.md)).
       - Output: Fully integrated Fava application with all PQC enhancements. Comprehensive test execution report.
       - AVER: All high-level acceptance tests pass. A test execution report is generated ([`docs/reports/PQC_Acceptance_Test_Report_v1.1.md`](docs/reports/PQC_Acceptance_Test_Report_v1.1.md)), detailing pass/fail status for each test and linking to AVER evidence, including verification of performance NFRs via Basic Performance Indicator Tests.
     - **5.2 Final Documentation Update (User & Developer)**
       - Input: All project artifacts (v1.1 specs, architecture, code, test reports), implemented application.
       - Output: Updated/new user documentation (e.g., explaining new PQC-related configurations, Fava-driven PQC encryption usage), developer documentation (e.g., detailing PQC modules, cryptographic agility framework). Saved in relevant [`docs/`](docs/) subdirectories.
       - AVER: [`docs/PQC_User_Guide_v1.1.md`](docs/PQC_User_Guide_v1.1.md) (or updates to existing user docs) and [`docs/PQC_Developer_Guide_v1.1.md`](docs/PQC_Developer_Guide_v1.1.md) (or updates to existing dev docs) are created/updated, accurately reflecting all PQC features, configurations, and considerations. These documents are reviewed for clarity and completeness.
     - **5.3 Performance Benchmarking & Optimization (Post-Integration)**
       - Input: Fully integrated PQC-enhanced Fava application, v1.1 NFR performance targets.
       - Output: Performance benchmark report ([`docs/reports/PQC_Performance_Benchmark_v1.1.md`](docs/reports/PQC_Performance_Benchmark_v1.1.md)), any critical optimizations implemented.
       - AVER: Benchmark report exists, comparing performance of key Fava operations with and without PQC features enabled, using data from Basic Performance Indicator Tests. Performance meets NFRs defined in v1.1 specifications, or any significant degradations are documented, justified, and accepted.
     - **5.4 Prepare Deployment Package & Release Notes (Conceptual for this project stage)**
       - Input: Final integrated and tested code, all documentation.
       - Output: Conceptual deployment artifacts (e.g., list of changes for packaging), [`RELEASE_NOTES_PQC_v1.1.md`](RELEASE_NOTES_PQC_v1.1.md).
       - AVER: A `RELEASE_NOTES_PQC_v1.1.md` document is created, summarizing all PQC-related changes, new features, configuration options, and known issues. Build process for creating a distributable version of Fava with PQC changes is tested and successful.

## 4. Timeline & Milestones (High-Level - Subject to Refinement)
   - **Phase 1 (Specification):** Completed [Actual Completion Date of Specification Phase v1.1 Baseline]
   - **Phase 2 (Pseudocode):** Estimated [e.g., 2-3 Sprints / 4-6 Weeks]
   - **Phase 3 (Architecture):** Estimated [e.g., 1-2 Sprints / 2-4 Weeks] (Can overlap with Pseudocode)
   - **Phase 4 (Refinement):** Estimated [e.g., 6-8 Sprints / 12-16 Weeks] (Iterative, largest phase)
   - **Phase 5 (Completion):** Estimated [e.g., 2-3 Sprints / 4-6 Weeks]
   *(Note: Durations are illustrative and depend on resource allocation and complexity discovered.)*

## 5. Roles and Responsibilities (Illustrative for AI Swarm)
   - **Project Orchestrator (e.g., UBER Orchestrator, SPARC Phase Orchestrators):** Manages overall project flow, delegates tasks to specialized AI modes, ensures phase transitions.
   - **Research Modes (e.g., `research-planner-strategic`, `researcher-high-level-tests`):** Conduct foundational and specialized research.
   - **Specification Mode (e.g., `spec-writer-comprehensive`):** Creates detailed requirement documents (v1.1).
   - **Pseudocode Mode (e.g., `pseudocode-writer`):** Develops logical blueprints based on v1.1 specs.
   - **Architecture Mode (e.g., `architect-highlevel-module`):** Designs system and module structures.
   - **Testing Modes (e.g., `tester-acceptance-plan-writer`, `spec-to-testplan-converter`, `tester-tdd-master`):** Define test strategies, plans (v1.1 MATP), and implement tests.
   - **Coding Mode (e.g., `coder-test-driven`):** Implements features based on TDD principles.
   - **Review Modes (e.g., `devils-advocate-critical-evaluator`, `security-reviewer-module`, `optimizer-module`):** Evaluate artifacts and code for quality, security, and performance.
   - **Documentation Mode (e.g., `docs-writer-feature`):** Creates and updates user and developer documentation.
   - **Human Oversight/Product Owner:** Provides strategic direction, resolves ambiguities, approves major milestones, and accepts final deliverables.

## 6. Assumptions and Dependencies
   - **Assumptions:**
     - NIST PQC standardization process for selected algorithms (Kyber, Dilithium) will remain stable enough not to require major rework of v1.1 specs.
     - Chosen PQC libraries (`oqs-python`, `liboqs-js`) will be reasonably mature, performant, and stable for Fava's use cases as per latest research.
     - Fava's core architecture is adaptable to the proposed PQC integrations, including the `CryptoService` model.
   - **Dependencies:**
     - Availability and stability of selected PQC Python libraries (`oqs-python` for backend Kyber, Dilithium signing if used in build tools; `cryptography` for AES, X25519, SHA3).
     - For Data in Transit: Availability of a PQC-enabled reverse proxy solution (e.g., Nginx with OQS OpenSSL, Caddy) supporting `X25519Kyber768`.
     - For WASM Integrity: Availability of PQC signature verification library usable in a WASM/JavaScript environment (`liboqs-js` for Dilithium3). Build tools for Dilithium3 signing (e.g., `oqs-python` scripts or `liboqs` CLI utilities).
     - Classical GPG tools are still required for backward compatibility in Data at Rest decryption.

## 7. Risk Management (High-Level Summary)
   - **Technical Risks:**
     - **PQC Algorithm/Library Instability:** Selected PQC standards change significantly post-v1.1, or chosen libraries (`oqs-python`, `liboqs-js`) have critical bugs/vulnerabilities not caught in research.
       - *Mitigation:* Prioritize NIST-standardized algorithms. Select libraries with active maintenance and known audits (e.g., Trail of Bits for liboqs). Implement cryptographic agility. Allocate buffer time for potential library issues. Contingency plans from research ([`docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md`](docs/research/data_collection/primary_findings/pf_tooling_contingency_PART_1.md)) considered.
     - **Performance Degradation:** PQC operations significantly slow down Fava beyond NFRs in v1.1 specs.
       - *Mitigation:* Early and continuous performance benchmarking (Basic Performance Indicator Tests). Optimize critical code paths. Chosen PQC schemes (Kyber-768, Dilithium3, SHA3-256) have performance profiles considered in v1.1 NFRs. Clearly communicate performance trade-offs.
     - **Integration Complexity:** Integrating PQC (especially Fava-driven encryption, `CryptoService`) into Fava's existing codebase proves more complex than anticipated.
       - *Mitigation:* Modular architectural design (`CryptoService`). Iterative development with frequent integration. Thorough code reviews.
   - **External Risks:**
     - **Toolchain Support Maturation:**
       - *PQC-TLS Reverse Proxies:* Maturity and ease of configuration for PQC-TLS proxies may vary.
         - *Mitigation:* Provide detailed documentation based on latest stable configurations. Suggest fallback to classical TLS if PQC setup is problematic for an administrator.
       - *PQC CLI Signing Tools for WASM:* Availability of user-friendly, stable CLI tools for Dilithium3 signing.
         - *Mitigation:* Rely on `oqs-python` scripts or `liboqs` utilities as per research ([`docs/research/data_collection/primary_findings/pf_pqc_cli_signing_tools_g4_3_PART_1.md`](docs/research/data_collection/primary_findings/pf_pqc_cli_signing_tools_g4_3_PART_1.md)). Document build process clearly.
   - *(Refer to [`docs/tests/PQC_Master_Acceptance_Test_Plan.md`](docs/tests/PQC_Master_Acceptance_Test_Plan.md) (v1.1) for more detailed testing-related risks and mitigations, including test data generation.)*

## 8. Communication Plan
   - **Regular Status Updates:** Weekly/Bi-weekly summaries of progress, impediments, and next steps (channel to be defined, e.g., project management tool, dedicated communication channel).
   - **Milestone Reviews:** Formal reviews at the end of each major SPARC phase (Pseudocode, Architecture, Refinement iterations, Completion).
   - **Artifact Repository:** All documents and code managed in the project's version control system (e.g., Git).
   - **Issue Tracking:** Use of an issue tracker for bugs, tasks, and enhancements.

---
This Master Project Plan is a living document. It will be reviewed and updated at the beginning and end of each phase, and as significant changes or new information arise.