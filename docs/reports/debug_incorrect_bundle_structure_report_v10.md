# PyInstaller Bundle Structure Diagnosis Report (v10)

## 1. Problem Description

The PyInstaller build for `fava_pqc_installer` completes with exit code 0, but the output directory `dist/fava_pqc_dist/` only contains an `_internal/` subdirectory. Critical data files and directories specified in `fava_pqc_installer.spec` (via direct tuples, `copy_metadata`, and `collect_data_files`) are missing from their expected top-level locations or specified subdirectories within the bundle.

Missing items include: `oqs.dll`, `fava.dist-info/`, `pyexcel.dist-info/`, `lml.dist-info/`, `pyexcel_xls.dist-info/`, `beancount/VERSION`, `beancount.dist-info/`, and Fava's own static/template files.

## 2. Analysis of Inputs

### 2.1. `fava_pqc_installer.spec`

*   **`datas_for_analysis` Construction (line 104):** This list, passed to `Analysis(datas=...)`, is correctly formed by concatenating:
    *   `current_fava_datas`: Specifies Fava's `templates`, `static` files, and `help` files to be placed in corresponding subdirectories (e.g., `fava/static`).
    *   `all_metadata`: Uses `copy_metadata()` for various packages. This function should yield `(source_path, 'package_name.dist-info')` tuples, correctly targeting the bundle root for these metadata directories.
    *   `pyexcel_specific_data`, `pyexcel_io_specific_data`: Uses `collect_data_files()`.
    *   A specific entry for `('.venv/Lib/site-packages/beancount/VERSION', 'beancount')`.
*   **`custom_binaries` (line 36):** Includes `(liboqs_dll_path, '.')` for `oqs.dll`, correctly targeting the bundle root.
*   **Omission:** `copy_metadata('beancount')` is missing from the `all_metadata` collection (lines 81-89). This directly accounts for the missing `beancount.dist-info/` directory.
*   **Overall Structure:** The spec file appears to correctly define the sources and destinations for most of the missing files according to standard PyInstaller practices.

### 2.2. `docs/devops/logs/pyinstaller_build_log_with_beancount_version.txt`

*   The build completes successfully (exit code 0).
*   PyInstaller acknowledges the custom `oqs.dll` and intends to bundle it at the root (log line 12).
*   PyInstaller reports appending `binaries` and `datas` from the spec file (log lines 25-26).
*   The `COLLECT` stage reports successful completion (log line 137: `INFO: Building COLLECT COLLECT-00.toc completed successfully.`).
*   **Significant Finding:** The log lacks the typical "Copying data file..." or "Copying binary..." messages during the `COLLECT` phase for the items specified in `a.datas` (from `datas_for_analysis`) and `a.binaries` (from `custom_binaries`). This suggests these files are not being processed for copying by `COLLECT` as expected.

### 2.3. `build/fava_pqc_installer/warn-fava_pqc_installer.txt`

*   Contains numerous "missing module" warnings. While some are expected on Windows, the repeated warnings for `collections.abc` are unusual for Python 3.13.3 and might indicate broader, subtle environment or hook issues.
*   No warnings directly point to problems with data file collection or path resolution for the `datas` entries.

## 3. Hypothesized Root Cause(s)

1.  **Primary Hypothesis: Issue with PyInstaller's `COLLECT` Stage:**
    The most likely cause is that the `COLLECT` stage of PyInstaller is not correctly processing the `a.datas` and `a.binaries` lists to physically copy files and create directories at the top level of the `dist/fava_pqc_dist/` bundle. The fact that only an `_internal/` subdirectory is present, and the absence of explicit file copying logs during `COLLECT`, strongly supports this. This could stem from:
    *   A bug or regression in the PyInstaller version used (log indicates `6.14.0`, which might be a non-standard or development version).
    *   The `COLLECT` stage misinterpreting destination paths (e.g., `.` for bundle root, or simple directory names like `fava/static`) under certain conditions in this version.

2.  **Secondary (Definite but Specific) Issue: Missing `beancount.dist-info/`:**
    The `beancount.dist-info/` directory is missing because the spec file does not include `copy_metadata('beancount')` in the `all_metadata` list.

## 4. Proposed Actionable Steps & Solutions

1.  **Address Missing `beancount.dist-info/`:**
    Modify [`fava_pqc_installer.spec`](fava_pqc_installer.spec:1) by adding `copy_metadata('beancount')` to the `all_metadata` list:
    ```python
    # Around line 88 in fava_pqc_installer.spec
    all_metadata.extend(copy_metadata('pyexcel_text')) # Existing line
    all_metadata.extend(copy_metadata('beancount'))    # Add this line
    ```

2.  **Investigate the `COLLECT` Stage Behavior (Most Critical):**
    *   **Examine `build/fava_pqc_installer/COLLECT-00.toc`:** This Table of Contents file is crucial. It lists all files that the `COLLECT` stage *intended* to bundle and their target paths within `fava_pqc_dist`.
        *   If files are listed with correct destinations (e.g., `oqs.dll` targeting the root, `fava/static/...` targeting `fava/static/`) but are not in `dist/fava_pqc_dist/`, then `COLLECT` is failing the copy operation.
        *   If files are listed with incorrect destinations (e.g., paths prefixed with `_internal/`), then `COLLECT` (or `Analysis` feeding it) is misinterpreting destination paths.
        *   If files are missing entirely from the TOC, then `Analysis` isn't populating `a.datas` or `a.binaries` as expected, despite the spec appearing correct.
    *   **Increase PyInstaller Log Verbosity:** Run PyInstaller with a higher log level to potentially get more details from the `COLLECT` stage:
        ```bash
        pyinstaller --loglevel=DEBUG fava_pqc_installer.spec
        ```
    *   **Test with a Minimal `datas` Configuration:** Simplify `datas_for_analysis` in the spec to a single, known-good entry to see if *any* data file can be correctly placed. For example:
        ```python
        # In fava_pqc_installer.spec, replace the datas_for_analysis line with:
        datas_for_analysis = [('src/fava/static/favicon.ico', '.')] 
        # Also, temporarily simplify binaries:
        # custom_binaries = [] # or just one known good binary
        ```
        Rebuild and check if `dist/fava_pqc_dist/favicon.ico` appears. This helps isolate whether the issue is with all `datas` entries or specific types (e.g., directories, metadata from hooks).
    *   **Experiment with PyInstaller Version:** The version `6.14.0` indicated in the logs might be a development or pre-release version. Consider testing with the latest official stable release of PyInstaller (e.g., 6.8.0 as of late May 2024, or whatever is current) to rule out a version-specific bug. This would require setting up a separate environment or adjusting the current one.
        ```bash
        pip install --upgrade PyInstaller
        # or to a specific stable version
        pip install PyInstaller==X.Y.Z
        ```
    *   **Verify Source File Accessibility:** Double-check that all source paths specified in `datas_for_analysis` and `custom_binaries` are correct, exist, and are readable by the user running PyInstaller at build time. While `Analysis` usually catches non-existent files, subtle issues might persist.

## 5. Summary of Missing Items and Their Expected Collection Method

*   `oqs.dll`: Via `custom_binaries` to bundle root (`.`).
*   `fava.dist-info/`: Via `copy_metadata('fava')` to bundle root.
*   `pyexcel.dist-info/`: Via `copy_metadata('pyexcel')` to bundle root.
*   `lml.dist-info/`: Via `copy_metadata('lml')` to bundle root.
*   `pyexcel_xls.dist-info/`: Via `copy_metadata('pyexcel_xls')` to bundle root.
*   `beancount/VERSION`: Via direct tuple `('path/to/VERSION', 'beancount')`.
*   `beancount.dist-info/`: **Currently not collected.** Add `copy_metadata('beancount')`.
*   Fava's static/template files (e.g., `fava/static/...`): Via `current_fava_datas` like `('src/fava/static', 'fava/static')`.

The primary focus should be on understanding why the `COLLECT` step is not populating `dist/fava_pqc_dist/` as expected, with the inspection of `COLLECT-00.toc` being the most immediate and informative diagnostic step.