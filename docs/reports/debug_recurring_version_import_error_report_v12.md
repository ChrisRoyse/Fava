# Diagnosis Report: Recurring `ImportError` for `fava.__version__` in Bundled Application

**Date:** 2025-06-03
**Target Feature:** Fava PQC Application Runtime Version Handling (Post-PyInstaller Bundling)
**Report Version:** v12
**Debugger:** AI Debugger (🎯 Debugger (SPARC Aligned & Systematic))

## 1. Issue Summary

The Fava PQC application, compiled into an installer ([`dist/fava_pqc_windows_installer_v1.1.0.exe`](dist/fava_pqc_windows_installer_v1.1.0.exe)) using PyInstaller, exhibits a runtime `ImportError` related to `fava.__version__`. This issue persists despite previous attempts to resolve it by ensuring Fava's package metadata is bundled. The error is similar to "cannot import name '__version__'" from `fava` or a `PackageNotFoundError` from `importlib.metadata.version('fava')`, ultimately preventing the application from starting correctly.

The core of the version retrieval mechanism is in [`src/fava/__init__.py`](src/fava/__init__.py:10):
```python
from contextlib import suppress
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

with suppress(PackageNotFoundError):
    __version__ = version(__name__)  # Effectively version('fava')
```
If `version('fava')` fails and raises `PackageNotFoundError`, `__version__` is not defined, leading to a subsequent `ImportError` when other modules (like [`src/fava/cli.py`](src/fava/cli.py)) try to import `fava.__version__`.

## 2. Recap of Previous Diagnosis and Current State

The previous diagnosis ([`docs/reports/debug_runtime_version_import_error_report_v6.md`](docs/reports/debug_runtime_version_import_error_report_v6.md)) correctly identified that `importlib.metadata` requires the package's `.dist-info` directory (containing the `METADATA` file) to be present at runtime. The solution involved using PyInstaller's `copy_metadata('fava')` utility.

**Current Status:**
*   The PyInstaller spec file ([`fava_pqc_installer.spec`](fava_pqc_installer.spec:81)) now includes `all_metadata.extend(copy_metadata('fava'))`, and this `all_metadata` collection is added to the `datas` argument of the `Analysis` object ([`fava_pqc_installer.spec:105`](fava_pqc_installer.spec:105), [`fava_pqc_installer.spec:113`](fava_pqc_installer.spec:113)).
*   The PyInstaller build log ([`docs/devops/logs/pyinstaller_build_log_src_files_check.txt`](docs/devops/logs/pyinstaller_build_log_src_files_check.txt:102)) confirms the inclusion of the runtime hook `pyi_rth_setuptools.py`, which is generally necessary for `importlib.metadata` to function in a frozen environment.
*   The user reports that the `fava.dist-info` directory (specifically `fava-0.1.dev20+g61365bf.d20250603.dist-info/`) appears to be bundled into the installed application's `_internal` directory.

Despite these measures, the `ImportError` recurs.

## 3. Hypothesized Root Causes for Recurring Error

Given that `copy_metadata('fava')` is in use and the `.dist-info` directory seems to be present in the bundle, the recurring error likely stems from one or more of the following:

1.  **Missing or Corrupt `METADATA` File:**
    *   **Hypothesis:** The most probable cause. While the `fava-0.1.dev20+g61365bf.d20250603.dist-info/` directory might be bundled, the crucial `METADATA` file *within* this directory could be missing, empty, corrupted, or not correctly named. `importlib.metadata.version()` specifically needs this file to extract version information.
    *   **Impact:** If `METADATA` is invalid or absent, `PackageNotFoundError` is raised, `__version__` remains undefined, leading to the `ImportError`.

2.  **Build Environment State / Incomplete Metadata Capture:**
    *   **Hypothesis:** The `fava` package was not correctly "installed" (e.g., via `pip install -e .` or a full build and install) in the Python environment used to run PyInstaller.
    *   **Impact:** If `fava` isn't properly installed, its `.dist-info` directory might not exist or might be incomplete when `copy_metadata('fava')` is called. PyInstaller might then copy nothing, or outdated/incomplete metadata, leading to runtime failure. The build log doesn't explicitly confirm what `copy_metadata('fava')` found and copied.

3.  **PyInstaller Runtime Path or Metadata Finder Issue:**
    *   **Hypothesis:** Even if the `METADATA` file is correctly bundled and valid, there might be a subtle issue with how PyInstaller's bootloader or the `pyi_rth_setuptools.py` runtime hook configures `sys.path` or `sys.meta_path`. `importlib.metadata` might still be unable to locate/access the `METADATA` file within the `_MEIPASS` temporary directory structure.
    *   **Impact:** `importlib.metadata` fails to find the package, leading to the error cascade.

4.  **Interference or Misconfiguration in `.spec` File (Less Likely):**
    *   **Hypothesis:** The aggregation of `datas` in [`fava_pqc_installer.spec`](fava_pqc_installer.spec:105) or other spec file settings could inadvertently cause the `fava.dist-info` directory to be misplaced, overwritten, or its contents altered.
    *   **Impact:** Similar to a missing/corrupt `METADATA` file.

## 4. Critical Diagnostic Steps (User Action Required)

To effectively diagnose this, the following information is crucial:

1.  **Provide Full Console Traceback:**
    *   **Action:** Run the installed `fava_pqc_windows_installer_v1.1.0.exe` (or the executable it installs, e.g., `Fava PQC.exe`) from a command prompt (`cmd.exe` or PowerShell).
    *   **Request:** Capture and provide the *entire* error message and traceback. This will confirm the exact point of failure.

2.  **Inspect Bundled `fava.dist-info` Directory and `METADATA` File:**
    *   **Action:** Navigate to the directory where the application is installed (e.g., `C:\Program Files (x86)\Fava PQC\`).
    *   Inside this directory, find the `_internal` subdirectory (or similar, based on PyInstaller's output structure).
    *   Locate the `fava-0.1.dev20+g61365bf.d20250603.dist-info` directory (the exact version string might vary slightly if the build changed).
    *   **Request:**
        *   Confirm this directory exists.
        *   Check if a file named `METADATA` (case-sensitive, though Windows is case-insensitive for filenames, the content matters) exists *inside* this `.dist-info` directory.
        *   If `METADATA` exists, what is its file size? (Is it empty?)
        *   If possible, open `METADATA` with a text editor. Does it contain lines like `Name: fava`, `Version: 0.1.dev20+g61365bf.d20250603`, etc.? It should resemble a standard Python package metadata file.

## 5. Further Diagnostic and Solution Strategies (Developer Actions)

Based on the user's feedback from step 4, the following actions should be considered:

1.  **Verify Build Environment and Process:**
    *   **Action:** Before running PyInstaller, ensure the `fava` package is properly installed in the build environment. The recommended way is an editable install from the project root:
        ```bash
        pip install -e .
        ```
    *   Ensure that this installation creates a valid `src/fava.egg-info` or `fava.dist-info` directory containing a `METADATA` file.
    *   Always perform a clean PyInstaller build: delete the `build/` and `dist/` directories before each PyInstaller run.

2.  **Inspect PyInstaller Output Directory (Pre-Installer):**
    *   **Action:** After PyInstaller finishes (creating the `dist/fava_pqc_dist` directory) but *before* running Inno Setup to create the final installer:
        *   Inspect `dist/fava_pqc_dist/_internal/`.
        *   Verify that `fava-VERSION.dist-info/METADATA` is present, correctly named, and contains valid content. This helps isolate whether the issue is with PyInstaller bundling or the Inno Setup packaging step.

3.  **Alternative: Robust Version Handling (Bypass `importlib.metadata` for Self-Versioning):**
    *   **Rationale:** If issues with `importlib.metadata` in a frozen environment persist, a more robust method for Fava to know its own version is to bake it in during the build.
    *   **Action:**
        1.  Modify `pyproject.toml` (if using Hatch, Flit, or a modern build backend) or `setup.py` (if using setuptools directly) to generate a `_version.py` file during the build process. This file would contain `__version__ = "actual.version.string"`.
        2.  In [`src/fava/__init__.py`](src/fava/__init__.py), change the version import:
            ```python
            # from contextlib import suppress
            # from importlib.metadata import PackageNotFoundError
            # from importlib.metadata import version

            # with suppress(PackageNotFoundError):
            #     __version__ = version(__name__)
            
            from ._version import __version__ # Assuming _version.py is created in src/fava/
            ```
        3.  Ensure `_version.py` is included by PyInstaller (it should be if it's part of the `fava` package).
    *   **Benefit:** This decouples runtime version access from the complexities of `importlib.metadata` in frozen applications for the application's own version.

4.  **Debugging PyInstaller Runtime (Advanced):**
    *   If the `METADATA` file is confirmed to be present and valid in the bundle, but the error persists:
        *   Temporarily add debug prints to [`src/fava/__init__.py`](src/fava/__init__.py) (just before the `importlib.metadata` call) in the frozen application to inspect `sys.path`, `sys.meta_path`, and the behavior of `importlib.metadata.distribution('fava').files`.
            ```python
            # In src/fava/__init__.py, for temporary debugging:
            import sys
            print(f"FROZEN_DEBUG: sys.path = {sys.path}")
            print(f"FROZEN_DEBUG: sys.meta_path = {sys.meta_path}")
            try:
                from importlib.metadata import distribution
                dist = distribution('fava')
                print(f"FROZEN_DEBUG: Found distribution for fava: {dist}")
                if hasattr(dist, 'files'):
                    print(f"FROZEN_DEBUG: Files for fava dist: {[str(f) for f in dist.files]}")
                else:
                    print("FROZEN_DEBUG: dist.files not available.")
            except Exception as e_debug:
                print(f"FROZEN_DEBUG: Error inspecting fava distribution: {e_debug}")
            
            # Original version logic follows
            from contextlib import suppress
            from importlib.metadata import PackageNotFoundError
            from importlib.metadata import version

            with suppress(PackageNotFoundError):
                __version__ = version(__name__)
            ```
        *   This requires rebuilding the application with these debug lines, installing, and running from the console to see the output. This can help understand if `importlib.metadata`'s finders are correctly configured by `pyi_rth_setuptools.py`.

## 6. Conclusion

The recurring `ImportError` for `fava.__version__`, despite `copy_metadata('fava')` being used, points to a problem with either the integrity/presence of the `METADATA` file within the bundled `fava.dist-info` directory, or an issue with the build environment leading to incomplete metadata capture. Less likely, but possible, is a runtime path issue for `importlib.metadata`.

**Immediate action is required from the user to provide the full console traceback and inspect the bundled `METADATA` file.** This information will be critical in pinpointing the exact failure point and guiding further resolution efforts. Subsequent steps will involve verifying the build environment and potentially adopting a more robust versioning scheme if metadata bundling issues persist.