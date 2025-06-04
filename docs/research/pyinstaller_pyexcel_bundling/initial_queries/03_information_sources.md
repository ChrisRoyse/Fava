# Information Sources: PyInstaller and pyexcel Bundling Research

This document outlines the primary and secondary sources of information that will be consulted to answer the key research questions regarding PyInstaller and `pyexcel` bundling issues for the Fava PQC project.

## 1. Primary Sources (Directly Related to the Technologies)

### 1.1. Official Documentation
*   **PyInstaller:**
    *   Main Documentation: [https://pyinstaller.readthedocs.io/en/stable/](https://pyinstaller.readthedocs.io/en/stable/)
    *   Specific sections of interest:
        *   How PyInstaller Works
        *   Using Spec Files
        *   Hidden Imports
        *   Hooks (including writing custom hooks, hook development)
        *   Analysis object parameters
        *   Bundling Data Files
        *   Debugging PyInstaller
        *   Supported Packages / Known Issues
*   **`pyexcel` and its ecosystem:**
    *   `pyexcel` Documentation: [https://pyexcel.readthedocs.io/en/latest/](https://pyexcel.readthedocs.io/en/latest/)
    *   `pyexcel-io` Documentation: [https://pyexcel-io.readthedocs.io/en/latest/](https://pyexcel-io.readthedocs.io/en/latest/)
    *   `lml` (Lazy Module Loader) Documentation: [https://lml.readthedocs.io/en/latest/](https://lml.readthedocs.io/en/latest/) (or its GitHub repository if docs are sparse)
    *   Documentation for specific `pyexcel` plugins (e.g., `pyexcel-xls`, `pyexcel-xlsx`, `pyexcel-ods3`, `pyexcel-text`). These are often found on their PyPI pages or linked from the main `pyexcel` docs.
*   **`oqs-python` (liboqs):**
    *   GitHub Repository & README: [https://github.com/open-quantum-safe/oqs-python](https://github.com/open-quantum-safe/oqs-python)
    *   Any specific notes on packaging or binary dependencies.

### 1.2. Source Code Repositories (for understanding internals and issue tracking)
*   **PyInstaller:** [https://github.com/pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller)
    *   Issues section: Searching for `pyexcel`, `lml`, dynamic imports, plugin issues.
    *   Hooks directory: [https://github.com/pyinstaller/pyinstaller-hooks-contrib](https://github.com/pyinstaller/pyinstaller-hooks-contrib) and built-in hooks.
*   **`pyexcel`:** [https://github.com/pyexcel/pyexcel](https://github.com/pyexcel/pyexcel)
*   **`pyexcel-io`:** [https://github.com/pyexcel/pyexcel-io](https://github.com/pyexcel/pyexcel-io)
*   **`lml`:** [https://github.com/pyexcel/lml](https://github.com/pyexcel/lml)
*   **Various `pyexcel` plugins:** e.g., [https://github.com/pyexcel/pyexcel-xls](https://github.com/pyexcel/pyexcel-xls), etc.
    *   Their issue trackers for packaging-related problems.

### 1.3. Alternative Packaging Tool Documentation
*   **Nuitka:** [https://nuitka.net/doc/user-manual.html](https://nuitka.net/doc/user-manual.html)
*   **cx_Freeze:** [https://cx-freeze.readthedocs.io/en/latest/](https://cx-freeze.readthedocs.io/en/latest/)
*   **Briefcase (BeeWare):** [https://briefcase.readthedocs.io/en/latest/](https://briefcase.readthedocs.io/en/latest/)

## 2. Secondary Sources (Community Knowledge and Discussions)

### 2.1. Q&A Sites and Forums
*   **Stack Overflow:** Searching for tags and keywords like `pyinstaller`, `pyexcel`, `lml`, `hidden-import`, `python`, `packaging`, `exe`.
*   **Reddit:** Subreddits like r/Python, r/learnpython.
*   **Specific library mailing lists or discussion forums** (if they exist for PyInstaller or `pyexcel`).

### 2.2. Blog Posts and Tutorials
*   Articles written by developers who have encountered and solved similar packaging issues with PyInstaller or other tools, especially concerning dynamic imports or plugin systems.
*   Tutorials on advanced PyInstaller usage or creating custom hooks.

### 2.3. AI Search Tools (via MCP)
*   Using the `perplexity-mcp` or similar general AI search tools to:
    *   Find solutions to specific error messages.
    *   Discover discussions about `pyexcel` and PyInstaller.
    *   Compare alternative packaging tools for specific use cases.
    *   Get summaries of how plugin systems like `lml` work.
    *   Request code examples for PyInstaller hooks.

## 3. Internal Project Context (Provided by User)

*   **`fava_pqc_installer.spec` file:** The current PyInstaller configuration.
*   **`docs/devops/logs/pyinstaller_build_log_v10.txt`:** The build log showing current errors.
*   **User Blueprint / Initial Prompt:** Provides the overall context and specific pain points.

## 4. Strategy for Using Sources

1.  **Start with Official Documentation:** Understand the intended behavior and features of PyInstaller, `pyexcel`, and `lml`.
2.  **Consult GitHub Issues:** Look for existing bug reports, feature requests, or discussions related to the problem. This is often where undocumented issues or workarounds are found.
3.  **Search Community Platforms:** Broaden the search to Stack Overflow and blogs for practical solutions and experiences from other developers.
4.  **Leverage AI Search:** Use AI tools for targeted queries, summarizing complex topics, and finding niche information.
5.  **Analyze Alternatives:** If PyInstaller solutions seem insufficient, consult the documentation for Nuitka, cx_Freeze, and Briefcase.
6.  **Iterate:** Findings from one source may lead to new search queries or areas of focus in other sources.

This list will be refined as the research progresses and new potential sources are identified.