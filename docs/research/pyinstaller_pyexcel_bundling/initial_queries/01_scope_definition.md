# Research Scope Definition: PyInstaller and pyexcel Bundling Issues

## 1. Summary of the Problem

The Fava PQC Windows `.exe` installer project is currently blocked. The primary issue is persistent "Hidden import not found" errors when using PyInstaller. These errors are specifically related to the `pyexcel` library and its plugin-based architecture, which relies on `lml` (Lazy Module Loader) for dynamically loading plugins like `pyexcel-xls`, `pyexcel-xlsx`, `pyexcel-ods3`, `pyexcel-text`, and various `pyexcel_io` readers and writers.

Despite numerous attempts to explicitly include these modules via the `hiddenimports` directive in the `fava_pqc_installer.spec` file, PyInstaller fails to detect and bundle all necessary components. This results in a non-functional packaged application that cannot perform Excel file operations.

## 2. Goal of the Research

The goal of this research is to identify robust and actionable solutions for packaging the Fava PQC Python application using PyInstaller, ensuring all `pyexcel` and `lml` related components are correctly bundled.

If PyInstaller proves unsuitable or overly complex for this specific combination of dependencies, the research should suggest and evaluate viable alternative packaging tools for creating a standalone Windows `.exe` installer.

## 3. Key Libraries and Components Involved

*   **Application:** Fava PQC (a derivative of Fava)
*   **Primary Packaging Tool:** PyInstaller
*   **Problematic Libraries:**
    *   `pyexcel`
    *   `lml` (Lazy Module Loader, used by `pyexcel`)
    *   `pyexcel-io`
    *   `pyexcel-xls`
    *   `pyexcel-xlsx`
    *   `pyexcel-ods` / `pyexcel-ods3`
    *   `pyexcel-text` (and its sub-plugins for CSV, TSV, etc.)
*   **Other Critical Libraries:**
    *   `fava` (core application)
    *   `oqs-python` (for Post-Quantum Cryptography)
*   **Build Files:**
    *   [`fava_pqc_installer.spec`](../../../../fava_pqc_installer.spec)
    *   [`docs/devops/logs/pyinstaller_build_log_v10.txt`](../../../../docs/devops/logs/pyinstaller_build_log_v10.txt)

## 4. Target Output of the Fava PQC Project

A standalone Windows `.exe` installer that bundles the Fava PQC application with all its dependencies, enabling users to install and run the application without needing a separate Python environment.

## 5. Scope of this Research Document

This research will focus on:
*   Investigating advanced PyInstaller configurations, including hooks, `hiddenimports` strategies, and Analysis phase tuning, to resolve the `pyexcel` and `lml` bundling issues.
*   Identifying and evaluating alternative Python-to-executable packaging tools (e.g., Nuitka, cx_Freeze, Briefcase) as potential replacements for PyInstaller if necessary.
*   Gathering community solutions, best practices, and documented examples related to packaging Python applications with similar dynamic import and plugin architectures.
*   Providing actionable recommendations, including potential code examples or `.spec` file modifications.