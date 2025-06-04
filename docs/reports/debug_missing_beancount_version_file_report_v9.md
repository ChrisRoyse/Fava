# Debugging Report: Missing `beancount/VERSION` File in PyInstaller Bundle

**Date:** 2025-06-03
**Reporter:** AI Debugger (debugger-targeted)
**Target Feature:** Fava PQC Windows Installer - `beancount` dependency.

## 1. Issue Description

The Inno Setup installer ([`Output/fava_pqc_windows_installer_v1.1.0.exe`](Output/fava_pqc_windows_installer_v1.1.0.exe)), when run after installation, produces the following error:
`FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Program Files (x86)\\Fava PQC\\_internal\\beancount\\VERSION'`

This indicates that the `beancount/VERSION` file, which is essential for the `beancount` package's runtime operation, is not being included in the PyInstaller bundle (`dist/fava_pqc_dist/`) used by Inno Setup.

## 2. SPARC Debugging Workflow

### 2.1. Reproduce

The issue is reproduced by:
1.  Building the PyInstaller bundle using [`fava_pqc_installer.spec`](fava_pqc_installer.spec).
2.  Creating the Inno Setup installer using the output from step 1.
3.  Installing the application using the Inno Setup installer.
4.  Running the installed application (`fava_pqc_installer.exe`).
The provided runtime error output confirms successful reproduction of the issue.

### 2.2. Isolate

The error message directly points to the missing `_internal/beancount/VERSION` file. The isolation process focused on why PyInstaller is not including this specific file.

### 2.3. Analyze

The analysis involved examining the following:

*   **[`fava_pqc_installer.spec`](fava_pqc_installer.spec):**
    *   The `datas` section (lines 98-104, specifically `datas_for_analysis` on line 112) does not contain an explicit entry for `beancount/VERSION`.
    *   There is no `copy_metadata('beancount')` call. While `copy_metadata` is used for other packages (lines 81-89), it's not used for `beancount`. Even if it were, `VERSION` files at the package root are not always included by `copy_metadata` which primarily targets the `.dist-info` directory.
    *   There is no `collect_data_files('beancount')` call, which is a common way to include all non-Python data files from a package.
*   **PyInstaller Hooks:**
    *   A listing of the [`hooks`](hooks) directory confirmed there is no `hook-beancount.py`. Such a hook could have been used to collect necessary data files.
*   **PyInstaller Build Log ([`docs/devops/logs/pyinstaller_build_log_after_pyexcel_xls_install.txt`](docs/devops/logs/pyinstaller_build_log_after_pyexcel_xls_install.txt)):**
    *   The log was reviewed for any mentions of `beancount/VERSION`, or warnings/errors related to collecting `beancount` data. No such relevant entries were found, indicating PyInstaller did not attempt to or fail at including this specific file; it simply wasn't instructed to.
*   **Location of `beancount/VERSION`:**
    *   The build environment's Python `site-packages` directory is `C:\code\ChrisFava\.venv\Lib\site-packages`.
    *   A `list_files` command confirmed the `VERSION` file exists at `.venv/Lib/site-packages/beancount/VERSION`.

**Hypothesized Root Cause:**

The `beancount/VERSION` file is missing from the PyInstaller bundle because it is a non-Python data file that is not automatically detected or included by PyInstaller's default mechanisms for the `beancount` package. There are no explicit instructions in the [`fava_pqc_installer.spec`](fava_pqc_installer.spec) file (via the `datas` list, `collect_data_files('beancount')`, or `copy_metadata('beancount')`) nor a custom hook (`hook-beancount.py`) to tell PyInstaller to bundle this file.

### 2.4. Fix (Proposed)

To resolve this issue, the `beancount/VERSION` file needs to be explicitly added to the `datas` section of the [`fava_pqc_installer.spec`](fava_pqc_installer.spec) file.

**Proposed Change to [`fava_pqc_installer.spec`](fava_pqc_installer.spec):**

Add the following tuple to the `datas_for_analysis` list (or a more specific list for `beancount` data if preferred):

```python
# In the datas_for_analysis list, add:
    ('.venv/Lib/site-packages/beancount/VERSION', 'beancount'),
```

This entry tells PyInstaller to:
1.  Take the file from `.venv/Lib/site-packages/beancount/VERSION` (source path relative to the spec file's location, or an absolute path if necessary, though relative to the venv is common).
2.  Place it into a directory named `beancount` inside the bundled application's `_internal` directory (destination path within the bundle).

The application's traceback shows it's looking for `_internal\\beancount\\VERSION`, so this destination path is correct.

**Alternative (More Robust) Path Specification:**

To make the path to `beancount/VERSION` more robust and less dependent on the exact `site-packages` path, one could use `pkgutil` or `importlib.resources` within the spec file to locate the `beancount` package and then construct the path to its `VERSION` file. However, for a direct fix, the explicit path (assuming the `.venv` structure is consistent in the build environment) is the simplest.

Example using `importlib.util` (Python 3.7+) to find the file dynamically (this would be Python code at the top of the spec file):

```python
import os
import sys # Required for print to stderr
import importlib.util

# Find beancount package path
beancount_version_file_source = None
try:
    spec = importlib.util.find_spec('beancount')
    if spec and spec.origin:
        beancount_pkg_dir = os.path.dirname(spec.origin)
        beancount_version_file_path_candidate = os.path.join(beancount_pkg_dir, 'VERSION')
        if os.path.exists(beancount_version_file_path_candidate):
            beancount_version_file_source = beancount_version_file_path_candidate
        else:
            print(f"WARNING: beancount/VERSION not found at {beancount_version_file_path_candidate}", file=sys.stderr)
    else:
        print("WARNING: Could not locate beancount package spec or origin.", file=sys.stderr)
except Exception as e:
    print(f"WARNING: Error locating beancount package: {e}", file=sys.stderr)

# Later, in the datas section, you would conditionally add this:
# Example:
# global datas_for_analysis # Assuming datas_for_analysis is defined globally in the spec
# if beancount_version_file_source:
#    datas_for_analysis.append((beancount_version_file_source, 'beancount'))
# else:
#    print("CRITICAL WARNING: beancount/VERSION source path not found, will not be added to datas.", file=sys.stderr)
```
This dynamic approach is generally preferred for robustness. The simpler, direct path `.venv/Lib/site-packages/beancount/VERSION` is also a valid immediate fix if the build environment is stable. Given the current spec file structure, adding `('.venv/Lib/site-packages/beancount/VERSION', 'beancount')` directly to `datas_for_analysis` is the most straightforward application of the fix.

### 2.5. Verify (Post-Fix)

After applying the proposed fix to [`fava_pqc_installer.spec`](fava_pqc_installer.spec):
1.  Re-run the PyInstaller build process.
2.  Re-compile the Inno Setup installer.
3.  Install the application using the new installer.
4.  Run the installed application and confirm that the `FileNotFoundError` for `beancount/VERSION` no longer occurs and the application starts as expected.
5.  (Optional but recommended) Inspect the `dist/fava_pqc_dist/_internal/beancount/` directory to confirm `VERSION` is present.

## 3. Conclusion and Recommendation

The `FileNotFoundError` for `beancount/VERSION` is due to PyInstaller not being instructed to include this necessary data file.

**Recommendation:** Modify the `datas` list in [`fava_pqc_installer.spec`](fava_pqc_installer.spec) to explicitly include the `beancount/VERSION` file. The recommended entry is:
`('.venv/Lib/site-packages/beancount/VERSION', 'beancount')`
to be added to the `datas_for_analysis` list.