# Executive Summary: Research on PyInstaller and `pyexcel` Bundling for Fava PQC

This research was undertaken to address persistent "Hidden import not found" errors encountered when packaging the Fava PQC Windows `.exe` installer using PyInstaller. These errors primarily stem from the interaction between PyInstaller's static analysis and the dynamic plugin loading mechanisms of the `pyexcel` library, which utilizes `lml` (Lazy Module Loader). The `oqs-python` library, a C-extension based dependency for quantum-safe cryptography, adds another layer of complexity.

**Key Findings:**

1.  **Root Cause:** The core issue is PyInstaller's difficulty in automatically detecting modules that `pyexcel` (via `lml`) loads dynamically at runtime, particularly its various format-specific plugins (e.g., `pyexcel-xls`, `pyexcel-xlsx`). This is a common challenge with libraries employing plugin architectures or significant dynamic imports.
2.  **PyInstaller Solutions - Hooks are Key:**
    *   Simply listing `hiddenimports` in the `.spec` file is often insufficient or becomes unwieldy.
    *   The most robust solution within PyInstaller involves creating custom **hooks**. These hooks should utilize PyInstaller utilities like `collect_submodules()` (to gather all code within plugin packages), `collect_data_files()` (for any non-Python assets), and critically, `copy_metadata()`.
    *   `copy_metadata('package_name')` is vital for `lml` and `pyexcel` plugins if `lml` relies on `entry_points` (defined in package metadata like `dist-info`/`egg-info` folders) for plugin discovery.
    *   Specific hooks are also needed for `oqs-python` to ensure its C shared library (`oqs.dll`) and any other binary dependencies are correctly bundled.
3.  **Alternative Packaging Tools:**
    *   **Nuitka:** Compiles Python to C, offering potentially better handling of C extensions (like `oqs-python`) and more advanced static analysis. It's a strong alternative if PyInstaller proves too problematic but introduces the complexity of a C build toolchain.
    *   **cx_Freeze:** Simpler than Nuitka but faces similar challenges to PyInstaller regarding dynamic imports and C extension dependencies, requiring careful manual configuration.
    *   **Briefcase:** Primarily focused on GUI applications and packaging full environments; likely less suitable for Fava PQC's current architecture.
4.  **Knowledge Gaps:**
    *   An exhaustive, verified list of all `pyexcel` plugins and their specific sub-dependencies required by Fava PQC needs compilation.
    *   The precise plugin discovery mechanism of `lml` within the `pyexcel` context (solely `entry_points` vs. other methods) requires confirmation to perfect hook strategies.
    *   Practical, tested examples of PyInstaller hooks for the `pyexcel`/`lml` combination are not readily available and would need to be developed/adapted.

**Core Recommendations:**

1.  **Prioritize a Hook-Centric PyInstaller Strategy:** Develop comprehensive PyInstaller hooks for `lml`, `pyexcel` (and its core dependencies like `pyexcel-io`), and each `pyexcel-*` plugin used by Fava PQC. These hooks must leverage `copy_metadata()` and `collect_submodules()`. A separate hook or spec file configuration is needed for `oqs-python` to bundle its C libraries.
2.  **Systematic Debugging:** Employ rigorous testing in clean environments and meticulous analysis of PyInstaller build logs (`warn-...txt` file and `--log-level=DEBUG` output) during development.
3.  **Investigate `lml` Internals:** If issues persist, a deeper dive into `lml`'s plugin loading mechanism within `pyexcel` is warranted to ensure hooks are correctly targeting its discovery process.
4.  **Contingency - Nuitka:** If a robust PyInstaller solution remains elusive, Nuitka should be the primary alternative explored, despite its increased build complexity.

**Conclusion:**
Successfully packaging Fava PQC with PyInstaller is achievable but requires a detailed understanding of its dependencies' dynamic behaviors and a methodical approach to crafting PyInstaller hooks. The `copy_metadata` utility is likely a critical component for ensuring `lml` can find `pyexcel` plugins. While alternative tools exist, refining the PyInstaller solution should be the primary focus, leveraging the strategies outlined in this research. Further targeted investigation into the identified knowledge gaps would enhance the robustness of the chosen solution.

This research provides a foundational understanding and actionable pathways. The next steps involve implementing and iteratively testing the recommended PyInstaller hook strategy.