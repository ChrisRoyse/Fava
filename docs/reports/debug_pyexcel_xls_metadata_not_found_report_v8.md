# PyInstaller Build Failure: `pyexcel_xls` Metadata Not Found

**Report Version:** v8
**Date:** 2025-06-03
**Feature Debugged:** PyInstaller build process for Fava PQC Installer
**Issue:** `importlib.metadata.PackageNotFoundError: No package metadata was found for pyexcel_xls`

## 1. Problem Description

The PyInstaller build process, when executing the [`fava_pqc_installer.spec`](../../../fava_pqc_installer.spec) file, fails with an `importlib.metadata.PackageNotFoundError`. This error specifically occurs when the spec file attempts to gather metadata for the `pyexcel_xls` package using the `copy_metadata('pyexcel_xls')` utility function. This prevents the successful creation of the Fava application bundle.

## 2. Analysis of Provided Context

### 2.1. PyInstaller Build Log Analysis ([`docs/devops/logs/pyinstaller_build_log_post_centralized_datas.txt`](../../../docs/devops/logs/pyinstaller_build_log_post_centralized_datas.txt))

-   **Error Message:** The log explicitly states:
    ```
    importlib.metadata.PackageNotFoundError: No package metadata was found for pyexcel_xls
    ```
-   **Traceback:** The traceback indicates the error originates from:
    -   [`fava_pqc_installer.spec:85`](../../../fava_pqc_installer.spec:85): `all_metadata.extend(copy_metadata('pyexcel_xls'))`
    -   This calls `PyInstaller.utils.hooks.copy_metadata`, which in turn calls `importlib.metadata.distribution('pyexcel_xls')`.
    -   The `PackageNotFoundError` is raised by `importlib.metadata` when it cannot find a distribution matching the name `pyexcel_xls`.
-   **Python Environment:** The build is executed within the Python environment: `C:\code\ChrisFava\.venv`.

### 2.2. PyInstaller Spec File Analysis ([`fava_pqc_installer.spec`](../../../fava_pqc_installer.spec))

-   The relevant line in the spec file is:
    ```python
    # fava_pqc_installer.spec, line 85
    all_metadata.extend(copy_metadata('pyexcel_xls'))
    ```
-   The name `pyexcel_xls` is used to request metadata. `importlib.metadata` normalizes distribution names by converting hyphens to underscores and making them lowercase. If the package is named `pyexcel-xls` on PyPI, then `pyexcel_xls` is the correct canonical name for `importlib.metadata` to use.

## 3. Root Cause Hypothesis

The primary hypothesized root cause is:

**The `pyexcel-xls` package is not installed in the Python virtual environment (`C:\code\ChrisFava\.venv`) used by PyInstaller during the build process.**

If the package is not installed, `importlib.metadata` will be unable to locate its `*.dist-info` directory, which contains the necessary metadata files (like `METADATA`, `RECORD`, `entry_points.txt`), leading directly to the `PackageNotFoundError`.

Alternative, less likely causes:
-   A corrupted installation of `pyexcel-xls` where its metadata files are missing or inaccessible.
-   An issue with `sys.path` within the PyInstaller execution context that prevents `importlib.metadata` from scanning the correct `site-packages` directory (though the log indicates the correct venv is being used).

## 4. Recommended Solution and Verification Steps

The proposed solution focuses on ensuring the `pyexcel-xls` package is correctly installed and accessible in the build environment.

### 4.1. Ensure `pyexcel-xls` Installation

1.  **Activate the virtual environment:**
    Open a terminal or command prompt.
    ```bash
    cd C:\code\ChrisFava
    .\.venv\Scripts\activate
    ```

2.  **Install `pyexcel-xls`:**
    Within the activated virtual environment, install the package using pip:
    ```bash
    pip install pyexcel-xls
    ```
    This command will fetch `pyexcel-xls` and its dependencies from PyPI and install them into `C:\code\ChrisFava\.venv\Lib\site-packages`.

### 4.2. Verify Installation and Metadata Accessibility

1.  **Check pip installation:**
    Still within the activated environment, confirm pip sees the package:
    ```bash
    pip show pyexcel-xls
    ```
    This should display information about the installed package, including its location.

2.  **Verify with `importlib.metadata`:**
    Run a Python interpreter from the virtual environment:
    ```bash
    python
    ```
    Then, execute the following Python code:
    ```python
    import importlib.metadata
    try:
        dist = importlib.metadata.distribution('pyexcel_xls')
        print(f"Successfully found: {dist.metadata['Name']} (version {dist.version})")
        print(f"Metadata location (example file): {next(iter(dist.files), 'N/A')}")
    except importlib.metadata.PackageNotFoundError:
        print("Error: 'pyexcel_xls' metadata still not found after installation attempt.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    ```
    This script should successfully find and print the package details. If it still fails, there might be a more complex issue with the environment or the package's structure.

### 4.3. Re-run PyInstaller Build

After confirming `pyexcel-xls` is installed and its metadata is accessible, re-run the PyInstaller build command:
```bash
cd C:\code\ChrisFava
pyinstaller --noconfirm fava_pqc_installer.spec
```
The build should now proceed past the `copy_metadata('pyexcel_xls')` step without the `PackageNotFoundError`.

## 5. Conclusion

The `importlib.metadata.PackageNotFoundError: No package metadata was found for pyexcel_xls` error strongly indicates that the `pyexcel-xls` package is missing from the PyInstaller build environment. Installing this package into the `C:\code\ChrisFava\.venv` virtual environment is the most direct and likely solution to resolve the issue.