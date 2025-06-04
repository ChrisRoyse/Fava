# Diagnostic Report: Missing Fava Static/Template Files in PyInstaller Bundle (v11)

**Date:** 2025-06-03
**Target Feature:** PyInstaller bundling of Fava application files.
**Issue:** Critical Fava application files (`fava/static/app.js`, `fava/templates/index.html`) and `beancount/VERSION` are reported as MISSING or UNCONFIRMED in the PyInstaller bundle.

## 1. Introduction

This report diagnoses why Fava's own static and template files (specifically `fava/static/app.js` and `fava/templates/index.html`) and the `beancount/VERSION` file are not being correctly bundled or confirmed in the PyInstaller build, despite configurations in [`fava_pqc_installer.spec`](fava_pqc_installer.spec).

## 2. Analysis of Provided Files

### 2.1. [`fava_pqc_installer.spec`](fava_pqc_installer.spec)

*   **`current_fava_datas` Definition:**
    The `current_fava_datas` variable, responsible for Fava's application-specific files, is defined as follows (lines 93-97):
    ```python
    current_fava_datas = [
        ('src/fava/templates', 'fava/templates'),
        ('src/fava/static', 'fava/static'),
        ('src/fava/help', 'fava/help'),
    ]
    ```
    This configuration instructs PyInstaller to copy the entire contents of the `src/fava/templates` directory into `fava/templates` within the bundle, and similarly for `src/fava/static` and `src/fava/help`.
    *   **Observation:** Contrary to a suggestion in the problem description, these entries do **not** use `glob.glob` patterns. They use direct directory-to-directory mapping, which is a standard PyInstaller practice.

*   **Inclusion in `datas_for_analysis`:**
    `current_fava_datas` is correctly included in the `datas_for_analysis` list (line 105):
    ```python
    datas_for_analysis = current_fava_datas + all_metadata + pyexcel_specific_data + pyexcel_io_specific_data + [('.venv/Lib/site-packages/beancount/VERSION', 'beancount')]
    ```

*   **Usage in `Analysis` Object:**
    `datas_for_analysis` is correctly passed to the `datas` parameter of the `Analysis` object (line 113).

*   **`beancount/VERSION` Entry:**
    The entry `('.venv/Lib/site-packages/beancount/VERSION', 'beancount')` is syntactically correct for copying the specified `VERSION` file into a `beancount` directory within the bundle. The source path is relative to the spec file's location (project root).

### 2.2. [`docs/devops/logs/pyinstaller_build_log_with_beancount_metadata.txt`](docs/devops/logs/pyinstaller_build_log_with_beancount_metadata.txt)

*   The log confirms that PyInstaller processes the `datas` entries from the spec file:
    `568 INFO : Appending 'datas' from .spec`
*   The log does not contain specific "Copying data file..." messages for `app.js` or `index.html`. This is not unusual when entire directories are specified in `datas`, as PyInstaller may not log each individual file within those directories unless an error occurs or high verbosity is enabled.
*   No errors or warnings related to the specified Fava static/template paths or `beancount/VERSION` (e.g., "source path not found") are present in this log.

### 2.3. `build/fava_pqc_installer/warn-fava_pqc_installer.txt`

*   This file lists Python modules that PyInstaller could not find. These are typically optional dependencies or OS-specific modules.
*   None of the warnings in this file appear to be directly related to the mechanism of copying data files via the `datas` parameter in the spec file.

## 3. Root Cause Hypotheses

### 3.1. Fava Static/Template Files (`fava/static/app.js`, `fava/templates/index.html`)

*   **Primary Hypothesis: Source File Unavailability/Mislocation.**
    The most probable cause for `fava/static/app.js` being reported as MISSING and `fava/templates/index.html` as UNCONFIRMED is that these files are not present at their expected source locations (`src/fava/static/app.js` and `src/fava/templates/index.html`, respectively, relative to the project root) *at the time PyInstaller executes the build*. The spec file correctly instructs PyInstaller to copy the *entire contents* of `src/fava/static` to `fava/static` in the bundle (and similarly for `templates`). If `app.js` is not in `src/fava/static/`, it will not be bundled.

*   **Secondary Hypothesis: Discrepancy in Bundling Strategy Expectation.**
    The problem description mentions verifying `glob.glob` patterns. However, the provided [`fava_pqc_installer.spec`](fava_pqc_installer.spec) does *not* use `glob.glob` for `current_fava_datas`. It uses direct directory inclusion.
    *   If the *intended* strategy was to use `glob.glob` for more fine-grained control over which files are included or how their paths are mapped, the current spec does not reflect this.
    *   However, the current method (`('src/fava/static', 'fava/static')`) is a valid and common way to include all assets from a directory.

*   **Tertiary Hypothesis: Issue with Post-Build Verification.**
    The "UNCONFIRMED" status for `fava/templates/index.html` could indicate that the file *is* bundled, but the method used to verify its presence is looking in an incorrect location or has other flaws. The "MISSING" status for `app.js` is a stronger indicator of a bundling problem for that specific file.

### 3.2. `beancount/VERSION`

*   **Primary Hypothesis: Source File Unavailability.**
    The entry `('.venv/Lib/site-packages/beancount/VERSION', 'beancount')` is correct. If this file is UNCONFIRMED in the bundle, the most likely reason is that the source file (`C:/code/ChrisFava/.venv/Lib/site-packages/beancount/VERSION`) does not exist or is not accessible during the PyInstaller build process.

## 4. Recommended Actions and Solutions

1.  **Verify Source File Presence and Paths (Crucial First Step):**
    *   **Action:** Before running PyInstaller, meticulously verify the existence and exact paths of the following files:
        *   `src/fava/static/app.js`
        *   `src/fava/templates/index.html`
        *   `.venv/Lib/site-packages/beancount/VERSION` (This path is relative to the project root where the spec file resides).
    *   **Rationale:** This will confirm whether PyInstaller is being provided with the correct source materials. Pay attention to case sensitivity if building on/for case-sensitive filesystems, though Windows is generally case-insensitive.

2.  **Inspect PyInstaller Output Directory:**
    *   **Action:** After a build, manually inspect the contents of the output directory `dist/fava_pqc_dist/_internal/`. Specifically check:
        *   `dist/fava_pqc_dist/_internal/fava/static/` (for `app.js` and other static assets)
        *   `dist/fava_pqc_dist/_internal/fava/templates/` (for `index.html` and other templates)
        *   `dist/fava_pqc_dist/_internal/beancount/` (for `VERSION`)
    *   **Rationale:** This direct inspection will confirm what PyInstaller actually bundled, bypassing any potentially flawed automated checks.

3.  **Address `glob.glob` Discrepancy:**
    *   **Action:** Clarify the intended bundling strategy.
        *   If the current strategy in [`fava_pqc_installer.spec`](fava_pqc_installer.spec) (i.e., copying entire `src/fava/static` and `src/fava/templates` directories) is the desired approach, then focus on ensuring these source directories are correctly populated (as per step 1).
        *   If the original intent (as hinted by the problem description's focus on `glob.glob`) was to use `glob.glob` for more selective file inclusion or complex path mapping, the spec file needs to be modified accordingly. For example, to explicitly add `app.js`:
          ```python
          current_fava_datas = [
              ('src/fava/static/app.js', 'fava/static'), 
              ('src/fava/templates/index.html', 'fava/templates'), 
          ]
          ```
          However, for bundling entire asset directories, the current spec's approach `('src/fava/static', 'fava/static')` is generally preferred for simplicity and completeness if all contents are needed.
    *   **Rationale:** Aligning the spec with the actual requirements is key. The current spec's method is robust if the source directories are correct.

4.  **Consider Explicit File Listing as a Fallback (If Directory Copying Fails Unexplainedly):**
    *   **Action:** If, after confirming source files exist (Step 1), the directory copy method `('src/fava/static', 'fava/static')` still fails to include `app.js`, consider explicitly listing critical files as a temporary diagnostic step or workaround:
        ```python
        current_fava_datas = [
            ('src/fava/templates', 'fava/templates'), 
            ('src/fava/static/app.js', 'fava/static'), 
            ('src/fava/static/other_critical_asset.css', 'fava/static'),
            ('src/fava/help', 'fava/help'),
        ]
        ```
    *   **Rationale:** This can help isolate whether the issue is with copying a specific file versus processing the directory as a whole.

5.  **For `beancount/VERSION`:**
    *   The spec entry is correct. If it's missing from the bundle, the issue is almost certainly that the source file `.venv/Lib/site-packages/beancount/VERSION` was not found by PyInstaller. Double-check its existence and path relative to the spec file.

## 5. Conclusion

The primary hypothesis for the missing Fava static/template files (especially `fava/static/app.js`) and the unconfirmed `beancount/VERSION` is the **unavailability of these files at their specified source locations during the PyInstaller build process.** The [`fava_pqc_installer.spec`](fava_pqc_installer.spec) itself appears to be correctly configured for including these files using standard PyInstaller `datas` collection methods for directories and individual files.

The discrepancy noted in the problem description regarding `glob.glob` usage versus the actual spec content (direct directory inclusion) should be clarified to ensure the spec aligns with the intended bundling strategy. However, the current spec's method is valid.

**Immediate recommended actions are to:**
1.  Verify the existence and precise paths of all source files (`src/fava/static/app.js`, `src/fava/templates/index.html`, `.venv/Lib/site-packages/beancount/VERSION`) *before* initiating the PyInstaller build.
2.  Manually inspect the PyInstaller output directory (`dist/fava_pqc_dist/_internal/`) to confirm the presence or absence of these files at their expected bundled locations.

If source files are confirmed to exist but are still missing from the bundle, further investigation into PyInstaller's behavior with these specific paths or potential (unlogged) errors would be needed, possibly by trying explicit file additions as a diagnostic step.