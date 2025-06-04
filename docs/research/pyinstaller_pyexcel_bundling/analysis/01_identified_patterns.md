# Identified Patterns: PyInstaller, pyexcel, and Alternative Packagers

This document outlines common patterns and recurring themes identified during the initial data collection phase of the research into packaging Fava PQC, specifically addressing issues with PyInstaller, `pyexcel`, `lml`, and considering alternative packaging tools.

## 1. PyInstaller and Dynamic/Plugin-Based Libraries (`pyexcel`, `lml`)

*   **Pattern:** PyInstaller's static analysis consistently struggles with libraries that use dynamic import mechanisms or plugin architectures like `lml` (used by `pyexcel`).
    *   **Evidence:** Multiple search results and primary findings ([`01_primary_findings_part_1.md`](../data_collection/01_primary_findings_part_1.md:1), [`01_primary_findings_part_2.md`](../data_collection/01_primary_findings_part_2.md:1)) confirm this is the root cause of "hidden import not found" errors.
    *   **Implication:** Manual intervention is almost always required.

*   **Pattern:** The most common and direct solution for PyInstaller is explicit enumeration of missing modules via `hiddenimports`.
    *   **Evidence:** Seen in user-provided `.spec` file attempts and across multiple search snippets.
    *   **Implication:** Can be tedious and error-prone for libraries with many plugins; requires knowing all possible dynamically loaded modules.

*   **Pattern:** PyInstaller Hooks (especially using `collect_submodules` and `copy_metadata`) are the recommended robust solution for complex dynamic libraries.
    *   **Evidence:** Detailed in [`01_primary_findings_part_2.md`](../data_collection/01_primary_findings_part_2.md:1). `copy_metadata` is particularly important for `lml` if it relies on `entry_points` for plugin discovery.
    *   **Implication:** Requires more understanding of PyInstaller's hooking system and the library's internal structure but offers better maintainability.

*   **Pattern:** Data files and non-Python dependencies associated with plugins are often overlooked and require explicit inclusion (e.g., via `datas` in hooks or spec files).
    *   **Evidence:** Mentioned in hook best practices ([`01_primary_findings_part_2.md`](../data_collection/01_primary_findings_part_2.md:1)).
    *   **Implication:** Incomplete functionality if these are missed, even if Python modules are found.

## 2. C Extensions (e.g., `oqs-python`)

*   **Pattern:** Packaging applications with C extensions introduces another layer of complexity, primarily around bundling the correct shared libraries (.dll, .so) and ensuring they are found at runtime.
    *   **Evidence:** Discussed in the context of alternative packagers ([`02_secondary_findings_alternative_packagers_part_1.md`](../data_collection/02_secondary_findings_alternative_packagers_part_1.md:1), [`02_secondary_findings_alternative_packagers_part_2a_cx_freeze.md`](../data_collection/02_secondary_findings_alternative_packagers_part_2a_cx_freeze.md:1), [`02_secondary_findings_alternative_packagers_part_2b_briefcase_conclusion.md`](../data_collection/02_secondary_findings_alternative_packagers_part_2b_briefcase_conclusion.md:1)).
    *   **Implication:** Requires careful configuration in the chosen packaging tool to include these binaries and potentially adjust runtime search paths.

*   **Pattern:** Tools that compile Python to C (like Nuitka) are often suggested as potentially more robust for handling C extensions.
    *   **Evidence:** Nuitka's description in [`02_secondary_findings_alternative_packagers_part_1.md`](../data_collection/02_secondary_findings_alternative_packagers_part_1.md:1).
    *   **Implication:** Nuitka might simplify bundling C dependencies but introduces its own build complexities (C compiler requirement).

## 3. Alternative Packaging Tools

*   **Pattern:** No single alternative packaging tool is a "silver bullet"; each has trade-offs regarding ease of use, handling of complex dependencies, output size, and build process.
    *   **Evidence:** Comparison table and detailed analysis in secondary findings documents.
    *   **Implication:** Choice of alternative depends on prioritizing specific factors (e.g., C extension support vs. build simplicity).

*   **Pattern:** Nuitka stands out for potentially better C extension handling but has a steeper learning curve and build requirements.
    *   **Evidence:** [`02_secondary_findings_alternative_packagers_part_1.md`](../data_collection/02_secondary_findings_alternative_packagers_part_1.md:1).
    *   **Implication:** A strong contender if PyInstaller solutions for `oqs-python` combined with `pyexcel` are insufficient.

*   **Pattern:** cx_Freeze is simpler but may offer less robust support for the complexities of `lml` and `oqs-python` without significant manual configuration.
    *   **Evidence:** [`02_secondary_findings_alternative_packagers_part_2a_cx_freeze.md`](../data_collection/02_secondary_findings_alternative_packagers_part_2a_cx_freeze.md:1).
    *   **Implication:** Might require similar levels of manual effort as PyInstaller for hidden imports.

*   **Pattern:** Briefcase appears less suited for the Fava PQC project's nature (local web server) and its current challenges.
    *   **Evidence:** [`02_secondary_findings_alternative_packagers_part_2b_briefcase_conclusion.md`](../data_collection/02_secondary_findings_alternative_packagers_part_2b_briefcase_conclusion.md:1).
    *   **Implication:** Likely not a primary alternative to explore further for this specific problem.

## 4. General Debugging and Problem Solving

*   **Pattern:** Thoroughly inspecting build logs (especially PyInstaller's `warn-<appname>.txt`) is critical for identifying missing modules.
    *   **Evidence:** Mentioned in PyInstaller diagnostic techniques ([`01_primary_findings_part_1.md`](../data_collection/01_primary_findings_part_1.md:1)).
    *   **Implication:** This should be a standard step in any debugging attempt.

*   **Pattern:** Testing the bundled application in a clean environment is essential to confirm true self-containment and catch runtime errors.
    *   **Evidence:** Standard best practice, mentioned in [`01_primary_findings_part_1.md`](../data_collection/01_primary_findings_part_1.md:1).
    *   **Implication:** Development environment testing can be misleading.

These identified patterns will help guide the subsequent analysis stages, particularly in formulating specific strategies for PyInstaller and evaluating the viability of alternatives.