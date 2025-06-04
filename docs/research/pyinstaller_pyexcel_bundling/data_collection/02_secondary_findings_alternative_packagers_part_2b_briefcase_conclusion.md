# Secondary Findings: Alternative Python Packaging Tools (Part 2b - Briefcase & Conclusion)

This document concludes the exploration of alternative Python packaging tools, focusing on Briefcase, overall considerations for the Fava PQC project, and a summary conclusion.

## 4. Briefcase (BeeWare)

Briefcase is part of the BeeWare suite, designed to help package Python applications for distribution, including as standalone native applications. It's often associated with GUI applications but can be used for others.

*   **Pros:**
    *   **Cross-Platform Intent:** Aims for a unified way to package for Windows, macOS, Linux, and mobile.
    *   **Modern Tooling:** Uses `pyproject.toml` for configuration.
*   **Cons:**
    *   **Primary Focus on GUI Apps:** While it can package non-GUI apps, its strengths and much of its ecosystem are geared towards GUI development (e.g., using Toga).
    *   **C Extensions & Complex Dependencies:** Relies on the underlying Python packaging (pip, setuptools) to handle C extensions during the app's bundling phase. Complex libraries like `oqs-python` might require significant manual configuration in `pyproject.toml` or custom build steps [1, 5].
    *   **Dynamic Plugins (`lml`):** Likely requires manual inclusion of plugin files and ensuring they are discoverable in the bundled app structure.
    *   **Output Size:** Tends to create very large bundles because it often packages a more complete Python environment to ensure cross-platform compatibility and ease of use for its target (GUI) applications.
    *   **Maturity for CLI/Server Apps:** Less proven for complex command-line or local server applications compared to PyInstaller or Nuitka.
*   **Considerations:**
    Briefcase might be overkill or not the best fit for a local web application like Fava unless the goal is to leverage other BeeWare tools for a native-feeling UI wrapper in the future. Its approach to bundling is more about creating a self-contained project environment.

## 5. Key Considerations for Fava PQC

*   **`oqs-python` Dependency:** This is a critical factor. Nuitka's C compilation approach might be inherently more robust for `oqs-python` and its `liboqs` C library. PyInstaller and cx_Freeze will depend heavily on correctly identifying and bundling all necessary DLLs/shared objects.
*   **`pyexcel` and `lml`:** All alternatives will likely require some form of explicit instruction to include all necessary `pyexcel` plugins, similar to PyInstaller's `hiddenimports` or hooks. Nuitka's advanced analysis might reduce this burden slightly.
*   **Ease of Debugging:** PyInstaller has a large community and many documented issues/solutions. Switching to a new tool means a new learning curve for debugging its specific bundling quirks.

**Conclusion for Secondary Findings:**
While PyInstaller has its challenges, especially with `lml`, the alternatives also present their own complexities. Nuitka appears to be the most promising alternative if PyInstaller proves intractable for `oqs-python` combined with `pyexcel`, due to its C compilation nature. However, it also introduces the complexity of managing a C build environment. cx_Freeze is simpler but might offer less robust handling of the C extensions and dynamic plugins. Briefcase seems less suited for this specific type of application.

The primary effort should remain on solving the PyInstaller issues, with Nuitka as the leading fallback option to investigate if PyInstaller efforts are exhausted.

## References (from previous search contexts, applied generally)
[1] Discussions on packaging tools and GUI application dependencies.
[5] Discussions on complex builds with C/C++ extensions and Python packaging.