# Research Methodology

This section details the methodology employed to investigate the PyInstaller bundling issues for the Fava PQC application, particularly concerning `pyexcel`, `lml`, and `oqs-python` dependencies.

## 1. Research Goal and Scope

*   **Primary Goal:** To identify robust and actionable solutions for successfully packaging the Fava PQC Python application into a standalone Windows `.exe` installer using PyInstaller, ensuring all `pyexcel` (with its `lml` plugin system) and `oqs-python` (with its C extension) components are correctly bundled and functional. A secondary goal was to explore viable alternative packaging tools if PyInstaller solutions proved overly complex or insufficient.
*   **Scope Definition:** The research focused on:
    *   Understanding the interaction between PyInstaller's static analysis and dynamic module loading (specifically `lml`).
    *   Identifying necessary hidden imports, data files, and metadata for `pyexcel` and its plugins.
    *   Developing strategies for PyInstaller hooks.
    *   Ensuring the `oqs-python` C extension (`oqs.dll`) is correctly bundled.
    *   Evaluating alternative tools (Nuitka, cx_Freeze, Briefcase) based on their ability to handle these complex dependencies.
    *   The initial scope was documented in [`../../initial_queries/01_scope_definition.md`](../../initial_queries/01_scope_definition.md).

## 2. Research Approach: Recursive Self-Learning Model

A structured, recursive self-learning approach was adopted, encompassing several conceptual stages:

*   **Stage 1: Initialization and Scoping:**
    *   Reviewed the user's initial problem statement, the provided `fava_pqc_installer.spec` file, and the `pyinstaller_build_log_v10.txt`.
    *   Defined the research scope, formulated key research questions ([`../../initial_queries/02_key_questions.md`](../../initial_queries/02_key_questions.md)), and brainstormed potential information sources ([`../../initial_queries/03_information_sources.md`](../../initial_queries/03_information_sources.md)).

*   **Stage 2: Initial Data Collection:**
    *   Utilized a general AI search tool (MCP: `github.com/pashpashpash/perplexity-mcp`) to gather information based on the key questions.
    *   Queries focused on:
        *   Troubleshooting PyInstaller hidden import errors for `pyexcel` and `lml`.
        *   Strategies for creating PyInstaller hooks for dynamic plugin systems.
        *   Comparison of alternative packaging tools (Nuitka, cx_Freeze, Briefcase) for complex dependencies.
    *   Findings were documented in:
        *   [`../../data_collection/01_primary_findings_part_1.md`](../../data_collection/01_primary_findings_part_1.md)
        *   [`../../data_collection/01_primary_findings_part_2.md`](../../data_collection/01_primary_findings_part_2.md)
        *   [`../../data_collection/02_secondary_findings_alternative_packagers_part_1.md`](../../data_collection/02_secondary_findings_alternative_packagers_part_1.md)
        *   [`../../data_collection/02_secondary_findings_alternative_packagers_part_2a_cx_freeze.md`](../../data_collection/02_secondary_findings_alternative_packagers_part_2a_cx_freeze.md)
        *   [`../../data_collection/02_secondary_findings_alternative_packagers_part_2b_briefcase_conclusion.md`](../../data_collection/02_secondary_findings_alternative_packagers_part_2b_briefcase_conclusion.md)

*   **Stage 3: First-Pass Analysis and Gap Identification:**
    *   Analyzed the collected data to identify common themes, patterns, and discrepancies.
    *   Documented these in:
        *   [`../../analysis/01_identified_patterns.md`](../../analysis/01_identified_patterns.md)
        *   [`../../analysis/02_contradictions_and_discrepancies.md`](../../analysis/02_contradictions_and_discrepancies.md)
    *   Crucially, identified knowledge gaps that would require further targeted research or empirical testing. These were documented in [`../../analysis/03_knowledge_gaps.md`](../../analysis/03_knowledge_gaps.md).

*   **Stage 4: Targeted Research Cycles (Conceptual - Not Executed in this Cycle):**
    *   This stage was planned but not executed due to operational constraints of a single research cycle.
    *   If pursued, it would involve formulating specific queries to address the gaps identified in Stage 3 (e.g., deep dives into `lml` source code, searching for specific `pyexcel` hook examples, testing `oqs-python` with Nuitka).

*   **Stage 5: Synthesis and Final Report Generation:**
    *   Synthesized all validated findings from the initial data collection and analysis.
    *   Developed an integrated model to explain the packaging challenges ([`../../synthesis/01_integrated_model.md`](../../synthesis/01_integrated_model.md)).
    *   Distilled key insights and actionable takeaways ([`../../synthesis/02_key_insights_and_takeaways.md`](../../synthesis/02_key_insights_and_takeaways.md)).
    *   Formulated practical applications and recommendations for Fava PQC ([`../../synthesis/03_practical_applications_and_recommendations.md`](../../synthesis/03_practical_applications_and_recommendations.md)).
    *   Compiled this final report.

## 3. Information Sources

A variety of information sources were planned for consultation, as detailed in [`../../initial_queries/03_information_sources.md`](../../initial_queries/03_information_sources.md). For this initial research cycle, the primary method of data collection was the AI search tool. Future cycles would involve more direct consultation of:
*   Official documentation (PyInstaller, `pyexcel`, `lml`, `oqs-python`, Nuitka, cx_Freeze, Briefcase).
*   Source code repositories and issue trackers.
*   Community forums (Stack Overflow, GitHub discussions).

## 4. Constraints and Limitations

*   **Single Operational Cycle:** This research was conducted within the constraints of a single operational cycle. This limited the depth of targeted research into specific knowledge gaps.
*   **Reliance on AI Search:** The initial data collection heavily relied on the outputs of an AI search tool. While efficient for broad information gathering, it may not capture all nuances or the very latest discussions available through direct manual browsing of forums or issue trackers.
*   **No Empirical Testing:** This research phase did not include practical experimentation (e.g., actually writing and testing PyInstaller hooks or attempting builds with Nuitka). Recommendations are based on information analysis rather than empirical validation.

Despite these limitations, the methodology aimed to provide a structured, comprehensive, and actionable initial body of research to guide the Fava PQC packaging efforts.