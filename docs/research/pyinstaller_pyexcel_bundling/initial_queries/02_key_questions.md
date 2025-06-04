# Key Research Questions: PyInstaller and pyexcel Bundling

This document outlines the critical questions that the research aims to answer to resolve the PyInstaller bundling issues with `pyexcel` for the Fava PQC project.

## 1. PyInstaller Specific Solutions

### 1.1. Hidden Imports (`hiddenimports`)
*   What is the exhaustive list of `pyexcel` and `lml` (Lazy Module Loader) submodules, plugins (readers, writers, parsers, renderers, sources), and their dependencies that need to be explicitly declared as `hiddenimports` in the `.spec` file for `pyexcel` to function correctly when bundled?
*   Are there common patterns or naming conventions for `pyexcel` plugins (e.g., `pyexcel_io.readers.csvr`, `pyexcel_xls.xlsr`) that can help systematically identify all necessary hidden imports?
*   How does `lml`'s plugin discovery mechanism work, and how does this interact with PyInstaller's static analysis? Are there specific `lml` modules that need to be included?
*   Beyond the direct `pyexcel-*` format-specific packages (like `pyexcel-xls`, `pyexcel-xlsx`, `pyexcel-ods3`, `pyexcel-text`), what underlying libraries or modules do these plugins depend on that might also be missed by PyInstaller?
*   Are there any known issues or best practices for ordering `hiddenimports`?

### 1.2. PyInstaller Hooks
*   Are there existing community-contributed or official PyInstaller hooks specifically for `pyexcel`, `pyexcel-io`, `lml`, or any of their common plugins (`pyexcel-xls`, `pyexcel-xlsx`, etc.)?
    *   If so, where can they be found, and how are they implemented?
    *   What is their effectiveness in resolving dynamic import issues?
*   If no pre-existing hooks are available, what would be the strategy for creating custom PyInstaller hooks (runtime hooks or analysis hooks) for these libraries?
    *   What specific information would these hooks need to provide to PyInstaller (e.g., collecting submodules, data files, binaries, patching `sys.path`)?
    *   Are there examples of hooks for other libraries with similar plugin architectures that can serve as a template?
*   How can one effectively debug the hook development process to ensure all necessary modules are captured?

### 1.3. Analysis Phase Tuning
*   Are there any PyInstaller `Analysis` object parameters (beyond `hiddenimports` and `hookspath`) that could be tuned to improve the detection of `pyexcel`'s dynamically loaded modules?
    *   For example, `collect_submodules`, `collect_dynamic_libs`, `module_collection_mode`?
*   Can `--debug=all` or other PyInstaller debugging flags provide more insight into why specific imports are being missed during the Analysis phase?

### 1.4. Data Files and Binaries
*   Do `pyexcel` or its plugins require any non-Python data files (e.g., templates, configuration files) or binary dependencies (e.g., DLLs, shared objects beyond `oqs.dll`) that need to be explicitly included in the `datas` or `binaries` section of the `.spec` file?
*   How can we verify if all necessary data files for `pyexcel` plugins are being correctly bundled and are accessible at runtime within the PyInstaller environment?

## 2. Understanding the Root Cause with `lml`
*   How does `lml` (Lazy Module Loader) specifically discover and load `pyexcel` plugins?
*   What environment variables, configuration files, or entry points does `lml` use that might be affected by the PyInstaller bundling process?
*   Are there ways to configure or instruct `lml` to be more PyInstaller-friendly, or to provide PyInstaller with the necessary information about its plugins?

## 3. Alternative Packaging Tools
*   If PyInstaller solutions are overly complex or prove unreliable, what are the most viable alternative Python packaging tools for creating a standalone Windows `.exe` for an application like Fava PQC, which uses `pyexcel`, `lml`, and `oqs-python`?
    *   **Nuitka:** How well does Nuitka handle dynamic imports and plugin systems like `pyexcel`/`lml`? What is its compatibility with `oqs-python` and its C dependencies? What is the typical build process and complexity?
    *   **cx_Freeze:** What are its strengths and weaknesses regarding dynamic imports? How does it compare to PyInstaller for this use case?
    *   **Briefcase (BeeWare):** Is it suitable for packaging a web application like Fava (which runs a local server)? How does it handle complex dependencies?
    *   Other potential tools?
*   For each alternative, what are the:
    *   Pros and cons regarding ease of use, build time, and output size?
    *   Reported success rates or common issues when packaging applications with similar dependency profiles?
    *   Specific configuration steps or considerations for `pyexcel` and `oqs-python`?

## 4. Community Solutions and Best Practices
*   What solutions, workarounds, or discussions exist on platforms like Stack Overflow, GitHub issues (for PyInstaller, `pyexcel`, `lml`, and related projects), and forums regarding packaging `pyexcel` or `lml`-based applications with PyInstaller or other tools?
*   Are there any known "gotchas" or specific versions of `pyexcel`, `lml`, or PyInstaller that are known to have better or worse compatibility?
*   What general strategies are recommended for debugging "module not found" errors in PyInstaller-packaged applications, especially for dynamically imported modules?

## 5. Verification and Testing
*   Once a potential solution is identified, what is the most effective way to test its completeness and ensure all `pyexcel` functionalities (especially for XLS, XLSX, ODS, CSV, TSV) are working in the bundled application?
*   Are there minimal reproducible examples that can be created to test `pyexcel` bundling in isolation before applying solutions to the full Fava PQC application?

By addressing these questions, the research aims to provide a clear path forward for successfully packaging the Fava PQC application.