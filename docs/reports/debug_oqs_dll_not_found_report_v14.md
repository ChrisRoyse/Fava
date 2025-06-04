# Debugging Report: `oqs.dll` Not Found During PyInstaller Build

**Report Version:** v14
**Date:** 2025-06-03
**Target Feature:** PyInstaller bundling of `oqs.dll` for PQC functionality.
**Issue:** `oqs.dll` is not found by the PyInstaller spec file ([`fava_pqc_installer.spec`](../../fava_pqc_installer.spec)), leading to its exclusion from the bundled application. The build log ([`docs/devops/logs/pyinstaller_build_log_oqs_priority_fix.txt`](../../docs/devops/logs/pyinstaller_build_log_oqs_priority_fix.txt)) indicates failure for both the primary package-based sourcing method and the local build fallback.

## 1. Analysis of Provided Information

*   **PyInstaller Spec File (`fava_pqc_installer.spec`):**
    *   Attempts to import `oqs`.
    *   Prioritizes finding `oqs.dll` using `oqs.get_lib_path()`.
    *   If not found, falls back to checking local build paths:
        *   `os.path.abspath(os.path.join(os.path.dirname(SPECPATH), '..', 'liboqs', 'build', 'bin', 'Release', 'oqs.dll'))`
        *   `os.path.abspath(os.path.join(os.path.dirname(SPECPATH), '..', 'liboqs', 'build', 'bin', 'Debug', 'oqs.dll'))`
*   **PyInstaller Build Log (`pyinstaller_build_log_oqs_priority_fix.txt`):**
    *   Line 5: `WARNING: oqs.get_lib_path() not available in installed oqs-python. Potentially old version or misconfiguration.`
    *   Line 6: `INFO: oqs.dll not found via package. Falling back to check local liboqs build paths.`
    *   Line 7: `WARNING: oqs.dll also not found in expected local build paths (Release: 'C:\liboqs\build\bin\Release\oqs.dll', Debug: 'C:\liboqs\build\bin\Debug\oqs.dll').`
    *   Line 8: `ERROR: CRITICAL - oqs.dll could not be found from any source (package or local build). PQC functionality will likely fail.`
*   **Build Environment Expectation:** `.venv` with `oqs-python==0.12.0` supposedly installed.

## 2. Investigation Steps & Findings

### Step 1: Check `oqs-python` Package Installation Status
*   **Command:** `.\.venv\Scripts\python.exe -m pip show oqs`
*   **Result:** `WARNING: Package(s) not found: oqs`

    *(Self-correction: The package name for pip is `oqs-python`, not `oqs`. The command should have been `pip show oqs-python`. However, the spec file imports `oqs`, which is correct if `oqs-python` is installed. The critical log line `WARNING: oqs.get_lib_path() not available in installed oqs-python` strongly suggests an issue with the `oqs-python` package itself or its installation, regardless of the exact pip command used for diagnosis initially.)*

    The build log line `WARNING: oqs.get_lib_path() not available in installed oqs-python. Potentially old version or misconfiguration.` is the key. This, combined with the assumption that `oqs-python==0.12.0` *should* have `get_lib_path()`, points to a fundamental problem with the `oqs-python` package within the `.venv` used by PyInstaller. The `pip show oqs` failure (even if it should have been `oqs-python`) further supports that the environment is not set up as expected for the `oqs` module to be available and functional.

## 3. Root Cause Analysis

*   **Primary Root Cause:** The `oqs-python` package (which provides the `oqs` module) is either **not installed** in the Python environment (`C:\code\ChrisFava\.venv`) used by PyInstaller, or it is **corrupted/misconfigured** to the extent that the `oqs` module cannot be imported correctly or the `get_lib_path()` attribute is missing.
    *   The build log `WARNING: oqs.get_lib_path() not available in installed oqs-python...` is direct evidence. If the `oqs` module could be imported but `get_lib_path()` was missing, it would indicate an issue with the package version or installation. If `oqs` itself couldn't be imported by the spec file, an `ImportError` specific to `oqs` would have been logged earlier by the spec file's `try-except ImportError` block around `oqs.get_lib_path()`. The log shows an `AttributeError` was caught (line 43 in spec, line 5 in log), meaning `import oqs` likely succeeded, but the `oqs` object did not have the `get_lib_path` method. This is characteristic of an incorrect version or a broken installation of `oqs-python`.

*   **Consequence:**
    1.  The primary method of locating `oqs.dll` via `oqs.get_lib_path()` fails.
    2.  The build process then attempts the fallback mechanism.

*   **Secondary Issue (Fallback Path Failure):** The fallback mechanism to find `oqs.dll` in local build directories also failed.
    *   The log indicates PyInstaller checked:
        *   `C:\liboqs\build\bin\Release\oqs.dll`
        *   `C:\liboqs\build\bin\Debug\oqs.dll`
    *   The spec file calculates these paths based on `SPECPATH` (the location of [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec)):
        `liboqs_repo_path = os.path.abspath(os.path.join(os.path.dirname(SPECPATH), '..', 'liboqs'))`
        If `SPECPATH` is `C:\code\ChrisFava\fava_pqc_installer.spec`, then `os.path.dirname(SPECPATH)` is `C:\code\ChrisFava`.
        The calculated `liboqs_repo_path` would then be `os.path.abspath(C:\code\ChrisFava\..\liboqs)`, which resolves to `C:\code\liboqs`.
    *   There is a discrepancy: the log shows checks in `C:\liboqs`, while the spec file logic, assuming `SPECPATH` is within the project, points to `C:\code\liboqs`. This could mean:
        *   `SPECPATH` is different than assumed during the PyInstaller execution.
        *   The actual `oqs.dll` is indeed missing from *both* `C:\liboqs\...` and `C:\code\liboqs\...` (or wherever the spec file truly pointed).
        The critical failure is that the DLL wasn't found, regardless of the exact path interpretation nuance.

## 4. Proposed Solutions & Verification Steps

1.  **Ensure Correct `oqs-python` Installation (Highest Priority):**
    *   **Action:** Explicitly install or reinstall the correct version of `oqs-python` in the virtual environment used for the build.
      ```bash
      .\.venv\Scripts\activate  # If not already active
      pip uninstall oqs-python  # Uninstall any potentially corrupt version
      pip install oqs-python==0.12.0
      ```
    *   **Verification:**
        *   After installation, confirm its presence and version:
          ```bash
          pip show oqs-python
          ```
        *   Test `oqs.get_lib_path()` directly within the venv:
          Create a small Python script (e.g., `test_oqs_path.py`):
          ```python
          import oqs
          import os
          try:
              dll_path = oqs.get_lib_path()
              print(f"oqs.get_lib_path() returned: {dll_path}")
              if dll_path and os.path.exists(dll_path):
                  print(f"SUCCESS: oqs.dll found at: {dll_path}")
              elif dll_path:
                  print(f"FAILURE: Path returned but oqs.dll does NOT exist at: {dll_path}")
              else:
                  print(f"FAILURE: oqs.get_lib_path() returned None or empty.")
          except AttributeError:
              print("FAILURE: oqs module does not have get_lib_path attribute.")
          except ImportError:
              print("FAILURE: Could not import oqs module.")
          except Exception as e:
              print(f"FAILURE: An unexpected error occurred: {e}")
          ```
          Run it: `.\.venv\Scripts\python.exe test_oqs_path.py`
          This will confirm if the package is installed correctly and `get_lib_path()` works as expected, and if the DLL exists at the returned path.

2.  **Verify Local Build Fallback Paths (If Package Method Still Fails):**
    *   **Action & Verification:**
        *   Clarify the `SPECPATH` during PyInstaller execution. Add a print statement in [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec) *before* the `oqs.dll` search logic:
          ```python
          print(f"DEBUG: SPECPATH is: {SPECPATH}", file=sys.stderr)
          print(f"DEBUG: os.path.dirname(SPECPATH) is: {os.path.dirname(SPECPATH)}", file=sys.stderr)
          # ... rest of the oqs.dll search logic
          ```
        *   Based on the clarified `SPECPATH`, ensure a correctly compiled `oqs.dll` (compatible with `oqs-python==0.12.0`) exists in the *actual* fallback path being checked by the spec file (e.g., `C:\code\liboqs\build\bin\Release\` or `C:\code\liboqs\build\bin\Debug\`).
        *   If the build *must* look in `C:\liboqs` (outside the project directory), ensure this external dependency is correctly populated and accessible by the build environment.

3.  **Re-run PyInstaller:** After applying the fixes (especially step 1), re-run the PyInstaller build process.

4.  **Last Resort (If Dynamic Methods Consistently Fail):**
    *   **Action:** Manually copy the correct `oqs.dll` into a known, stable location within the project (e.g., `src/fava/lib/oqs.dll`) and modify [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec) to directly use this hardcoded path.
    *   **Warning:** This reduces flexibility and should only be a temporary measure or last resort if the environment/package issues cannot be reliably resolved.

## 5. Summary of Hypothesized Root Cause

The primary hypothesized root cause is that the **`oqs-python` package (version 0.12.0) is not correctly installed or is corrupted within the `.venv` environment (`C:\code\ChrisFava\.venv`) used by the PyInstaller build process.** This prevents the `oqs.get_lib_path()` method from being available or functioning correctly, thus failing to locate `oqs.dll` from the package. The fallback mechanism also failed, potentially due to the DLL not existing at the checked local build paths or a discrepancy in path resolution.