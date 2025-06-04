# Knowledge Gaps and Areas for Further Research

This document identifies key knowledge gaps based on the initial data collection and analysis. Addressing these gaps is essential for providing a comprehensive solution for packaging the Fava PQC application.

## 1. `pyexcel` and `lml` Internals with PyInstaller

*   **Gap 1.1: Exhaustive List of `pyexcel` Plugins and Dependencies:**
    *   **Description:** While the need for `hiddenimports` is clear, a definitive, exhaustive list of *all* `pyexcel` plugins (readers, writers, formatters, sources, e.g., `pyexcel-xls`, `pyexcel-xlsx`, `pyexcel-ods3`, `pyexcel-text`, `pyexcel-handsontable`, `pyexcel-pygal`, etc.), their specific module names as expected by `lml`/`importlib`, and all their *own* underlying dependencies (e.g., `xlrd`, `xlwt`, `openpyxl`, `odfpy`, `lxml`) is not yet compiled. The existing `.spec` file attempts this but is incomplete according to the build log.
    *   **Why it matters:** Without this, `hiddenimports` will remain a trial-and-error process.
    *   **Next Step:** Detailed audit of `pyexcel` documentation, `lml`'s plugin registration (likely via `entry_points`), and the Fava PQC codebase to identify all used `pyexcel` functionalities and their corresponding plugins.

*   **Gap 1.2: Precise `lml` Plugin Discovery Mechanism:**
    *   **Description:** The exact mechanism `lml` uses to discover `pyexcel` plugins needs to be confirmed. Is it solely `entry_points` (via `pkg_resources` or `importlib.metadata`), or does it also involve directory scanning or other dynamic methods?
    *   **Why it matters:** This directly impacts the PyInstaller hook strategy. If `entry_points` are key, then `copy_metadata` is vital. If directory scanning is involved, hooks might need to replicate that structure or inform `lml` of new paths.
    *   **Next Step:** Investigate `lml` source code and its documentation (if detailed enough) specifically in the context of how `pyexcel` registers and loads its plugins. Search for issues related to `lml` and PyInstaller.

*   **Gap 1.3: Data Files and Non-Python Assets for `pyexcel` Plugins:**
    *   **Description:** It's unclear if any `pyexcel` plugins require specific non-Python data files (e.g., templates, default configurations, icons for specific renderers if any are used) that PyInstaller might miss.
    *   **Why it matters:** Missing data files can lead to runtime errors even if all Python modules are present.
    *   **Next Step:** Review documentation for each `pyexcel` plugin used by Fava PQC for mentions of data files. Test plugin functionality thoroughly in a bundled app.

## 2. PyInstaller Hook Implementation Details

*   **Gap 2.1: Proven PyInstaller Hook for `pyexcel` + `lml`:**
    *   **Description:** While the components of a hook ( `collect_submodules`, `collect_data_files`, `copy_metadata`) are known, a complete, tested, and community-vetted PyInstaller hook specifically for the `pyexcel` ecosystem (and its `lml` dependency) is not yet identified. The examples provided so far are conceptual.
    *   **Why it matters:** A proven hook would save significant development and testing time.
    *   **Next Step:** Search more targetedly in `pyinstaller-hooks-contrib` and broader GitHub for existing hooks for `pyexcel`, `pyexcel-io`, `lml`, or libraries with similar `entry_point`-based plugin systems.

*   **Gap 2.2: Runtime Hook Necessities for `lml`:**
    *   **Description:** It's unknown if `lml` or `pyexcel` plugins require specific runtime path adjustments (via `sys.path` modification or environment variables) when bundled by PyInstaller, especially concerning how `lml` finds plugin metadata or the plugins themselves if `sys._MEIPASS` is involved.
    *   **Why it matters:** Runtime hooks might be necessary if `lml`'s discovery is path-sensitive and broken by bundling.
    *   **Next Step:** Analyze `lml`'s behavior in a bundled environment. This might require instrumenting `lml` or `pyexcel` with logging to see how it attempts to load plugins.

## 3. `oqs-python` Bundling Specifics

*   **Gap 3.1: Comprehensive `oqs-python` Dependencies for PyInstaller:**
    *   **Description:** Beyond the `oqs.dll` (or equivalent .so/.dylib), it's not fully clear if `oqs-python` has other implicit dependencies (e.g., specific versions of MSVC redistributables on Windows if statically linked, or other system libraries) that PyInstaller needs to bundle.
    *   **Why it matters:** Missing C-level dependencies will cause the application to fail at startup or when `oqs-python` functions are called.
    *   **Next Step:** Consult `oqs-python` documentation or community channels regarding PyInstaller best practices or known issues. Examine its build process for clues about runtime dependencies.

## 4. Alternative Packager Practicalities

*   **Gap 4.1: Practical Experience with Nuitka for `oqs-python` + `pyexcel`:**
    *   **Description:** While Nuitka is theoretically strong for C extensions, practical examples or reports of successfully packaging a complex application with both C extensions like `oqs-python` AND a dynamic plugin system like `pyexcel`/`lml` using Nuitka are lacking in the initial research.
    *   **Why it matters:** Theoretical advantages don't always translate to easy implementation.
    *   **Next Step:** Search for Nuitka user experiences, tutorials, or issues specifically involving `oqs-python` (or similar CFFI-based libraries with significant C components) and `pyexcel` (or other `lml`-based plugin systems).

## 5. Version Compatibility

*   **Gap 5.1: Known Version Conflicts/Compatibilities:**
    *   **Description:** It's unknown if specific versions of PyInstaller, `pyexcel` (and its plugins), `lml`, or `oqs-python` have better or worse compatibility with each other regarding packaging.
    *   **Why it matters:** Version incompatibilities can be a subtle source of issues.
    *   **Next Step:** When researching solutions, note library versions mentioned in successful reports or bug discussions. Check changelogs for relevant fixes or known issues.

Addressing these knowledge gaps through targeted research or empirical testing will be the focus of subsequent research cycles.