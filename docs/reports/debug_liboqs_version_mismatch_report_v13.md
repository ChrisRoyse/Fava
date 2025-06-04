# LibOQS Version Mismatch Diagnosis Report (Fava PQC Installer v1.1.0)

**Target Feature:** Fava PQC Windows Installer (`dist/fava_pqc_windows_installer_v1.1.0.exe`)
**Symptom:** `UserWarning: liboqs version (major, minor) 0.13.1-dev differs from liboqs-python version 0.12.0`
**Report Date:** 2025-06-03

## 1. Problem Description

After installing and running the `fava_pqc_windows_installer_v1.1.0.exe`, the Fava application starts, but a `UserWarning` is displayed in the console:

```
PyInstaller\loader\pyimod02_importers.py:457: UserWarning: liboqs version (major, minor) 0.13.1-dev differs from liboqs-python version 0.12.0
```

This indicates that the bundled `oqs.dll` (the C library, liboqs) is version 0.13.1-dev, while the `oqs-python` package (the Python wrapper) installed and used by Fava PQC is version 0.12.0. Such a mismatch can lead to instability, incorrect cryptographic operations, or runtime errors when Post-Quantum Cryptography (PQC) functionalities are invoked.

The Fava CLI also showing "Error: No file specified" is expected behavior when Fava is run without a Beancount file argument and is unrelated to this `liboqs` warning.

## 2. Diagnosis and Root Cause Analysis

The root cause of the version mismatch is the method by which `oqs.dll` is sourced and bundled by PyInstaller, as defined in the [`fava_pqc_installer.spec`](fava_pqc_installer.spec) file.

The relevant logic in [`fava_pqc_installer.spec`](fava_pqc_installer.spec) is:

```python
# Attempt to find the oqs.dll from a relative path
# This path assumes 'liboqs' repository is cloned adjacent to 'fava-pqc'
# and 'oqs.dll' is built in its default Debug location.
liboqs_repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'liboqs'))
liboqs_dll_path_debug = os.path.join(liboqs_repo_path, 'build', 'bin', 'Debug', 'oqs.dll')
liboqs_dll_path_release = os.path.join(liboqs_repo_path, 'build', 'bin', 'Release', 'oqs.dll')

# Prioritize Release over Debug if both exist, otherwise take what's available
if os.path.exists(liboqs_dll_path_release):
    actual_liboqs_dll_path = liboqs_dll_path_release
    # ...
elif os.path.exists(liboqs_dll_path_debug):
    actual_liboqs_dll_path = liboqs_dll_path_debug
    # ...
else:
    actual_liboqs_dll_path = None
    # ...

custom_binaries = []
if actual_liboqs_dll_path:
    custom_binaries.append((actual_liboqs_dll_path, '.')) 
    # ...
else:
    # Fallback: Try to get it from oqs.get_lib_path()
    # ...
```

**Key Findings:**

*   **Prioritization of Local Build:** The spec file explicitly prioritizes finding `oqs.dll` from a local build of the `liboqs` C library located at `../liboqs/build/bin/[Release|Debug]/oqs.dll`.
*   **Out-of-Sync Local `liboqs` Repository:** The local `liboqs` repository (adjacent to the `fava-pqc` project) is likely checked out to a more recent commit or a development branch (e.g., `main` or `develop`). This results in `liboqs` being built as version `0.13.1-dev`.
*   **Fixed `oqs-python` Version:** The Fava PQC build environment uses `oqs-python==0.12.0`. This version of the Python wrapper expects the underlying `liboqs` C library to be version 0.12.0 for correct ABI (Application Binary Interface) compatibility.
*   **Fallback Not Triggered (or Insufficient):** While the spec file includes a fallback to use `oqs.get_lib_path()` (which would typically provide the DLL bundled with or located by the `oqs-python` package itself), this fallback is only used if the prioritized local build of `oqs.dll` is *not found*. Since a 0.13.1-dev version *is* found, the fallback is not engaged.

Therefore, the installer bundles the `oqs.dll` (0.13.1-dev) from the local `liboqs` build, which is incompatible with the `oqs-python` (0.12.0) library used by the application.

## 3. Proposed Solutions (Prioritized)

The primary goal is to ensure the bundled `liboqs.dll` is version 0.12.0, matching the `oqs-python==0.12.0` requirement.

### Option 1 (Recommended): Build `liboqs` 0.12.0 from Source

This is the most robust solution as it ensures the C library is built specifically for the target version.

**Steps:**

1.  **Navigate to the local `liboqs` repository:**
    ```bash
    cd ../liboqs 
    ```
    (This path is relative to the `fava-pqc` project directory where [`fava_pqc_installer.spec`](fava_pqc_installer.spec) resides).

2.  **Identify and Checkout the Correct `liboqs` Version:**
    *   The `oqs-python==0.12.0` package requires a corresponding `liboqs` 0.12.0 C library.
    *   Search for a git tag in the `liboqs` repository that corresponds to version 0.12.0. Common tag formats are `0.12.0`, `v0.12.0`, or similar.
    *   You may need to consult the `oqs-python` 0.12.0 release notes or its source code (e.g., `setup.py` or CI scripts if it uses `liboqs` as a submodule) to find the exact `liboqs` C library tag or commit hash it was built against.
    *   Example checkout (replace `<tag_for_0.12.0>` with the actual tag):
        ```bash
        git fetch --all --tags
        git checkout tags/<tag_for_0.12.0> -b branch_for_0.12.0
        ```

3.  **Clean Previous Build Artifacts (Recommended):**
    *   If a `build` directory exists, remove it or clean it to ensure a fresh build:
        ```bash
        # Option A: Remove build directory
        rm -rf build 
        # Option B: If CMake was used and build system supports it
        # cmake --build build --target clean 
        ```

4.  **Rebuild `liboqs`:**
    *   Follow the standard build instructions for `liboqs` to produce `oqs.dll`. This typically involves CMake. Ensure you are building a Release version.
    *   Example CMake commands (these might vary slightly based on `liboqs` build system and your environment):
        ```bash
        cmake -S . -B build -DOQS_USE_OPENSSL=OFF # Or ON, depending on requirements
        cmake --build build --config Release --parallel
        ```
    *   Verify that `oqs.dll` is created in the path expected by the [`fava_pqc_installer.spec`](fava_pqc_installer.spec) file (e.g., `../liboqs/build/bin/Release/oqs.dll`).

5.  **Re-run PyInstaller for Fava PQC:**
    *   With the correctly versioned `oqs.dll` (0.12.0) in place, rebuild the Fava PQC installer:
        ```bash
        pyinstaller fava_pqc_installer.spec
        ```
    *   The spec file should now pick up the 0.12.0 DLL from your local `liboqs` build.

### Option 2: Modify `fava_pqc_installer.spec` to Prioritize `oqs.get_lib_path()`

If managing a local build of `liboqs` at a specific version is cumbersome, an alternative is to modify the spec file to prioritize the `oqs.dll` provided by the `oqs-python` package itself. This DLL is generally guaranteed to be compatible.

**Modification to [`fava_pqc_installer.spec`](fava_pqc_installer.spec):**

Change the logic for `custom_binaries` to attempt sourcing from `oqs.get_lib_path()` *first*.

```python
# --- Start of modified section in fava_pqc_installer.spec ---
custom_binaries = []
oqs_lib_path_from_pkg = None

# Attempt to get oqs.dll from the oqs-python package first
try:
    import oqs
    oqs_lib_path_from_pkg = oqs.get_lib_path()
    if oqs_lib_path_from_pkg and os.path.exists(oqs_lib_path_from_pkg):
        custom_binaries.append((oqs_lib_path_from_pkg, '.'))
        print(f"INFO: Successfully sourced oqs.dll from oqs-python package: {oqs_lib_path_from_pkg}")
        print(f"INFO: Will bundle oqs.dll from: {oqs_lib_path_from_pkg}")
    else:
        oqs_lib_path_from_pkg = None # Reset if path is invalid or file doesn't exist
        print("WARNING: oqs.get_lib_path() did not return a valid path or file for oqs.dll.")
except ImportError:
    print("WARNING: oqs-python package not found. Cannot source oqs.dll from it.")
except Exception as e:
    oqs_lib_path_from_pkg = None
    print(f"WARNING: Error when trying to use oqs.get_lib_path(): {e}")

# Fallback to local liboqs build ONLY if oqs.get_lib_path() failed
if not oqs_lib_path_from_pkg:
    print("INFO: oqs.dll not sourced from package. Attempting local liboqs build path.")
    liboqs_repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'liboqs'))
    liboqs_dll_path_debug = os.path.join(liboqs_repo_path, 'build', 'bin', 'Debug', 'oqs.dll')
    liboqs_dll_path_release = os.path.join(liboqs_repo_path, 'build', 'bin', 'Release', 'oqs.dll')
    actual_liboqs_dll_path = None

    if os.path.exists(liboqs_dll_path_release):
        actual_liboqs_dll_path = liboqs_dll_path_release
        print(f"INFO: Attempting to use Release DLL from local build: {actual_liboqs_dll_path}")
    elif os.path.exists(liboqs_dll_path_debug):
        actual_liboqs_dll_path = liboqs_dll_path_debug
        print(f"INFO: Attempting to use Debug DLL from local build: {actual_liboqs_dll_path}")
    
    if actual_liboqs_dll_path:
        custom_binaries.append((actual_liboqs_dll_path, '.'))
        print(f"INFO: Will attempt to bundle '{actual_liboqs_dll_path}' as 'oqs.dll' from local build.")
    else:
        print("CRITICAL WARNING: oqs.dll not found via oqs.get_lib_path() NOR in expected local build paths. PQC functionality will likely fail.")
# --- End of modified section ---
```

This change ensures that if `oqs-python` can provide a valid path to its own `oqs.dll` (which should be version 0.12.0), that version is used. The local build path becomes a true fallback.

### Option 3 (Not Recommended): Update `oqs-python`

Updating `oqs-python` to a version compatible with `liboqs` 0.13.1-dev could resolve the warning. However, this is not recommended because:
*   `0.13.1-dev` implies a development (potentially unstable) version of `liboqs`. Relying on dev versions for a release is risky.
*   Updating `oqs-python` might introduce breaking API changes or other compatibility issues with Fava PQC or its other dependencies.
*   The project seems to have standardized on `oqs-python==0.12.0` for the current Fava PQC release.

## 4. Verification Steps (Post-Fix)

After applying one of the recommended solutions and rebuilding the installer:

1.  **Install and Run:** Install the new `fava_pqc_windows_installer_vX.Y.Z.exe`. Run Fava from the installed location.
2.  **Check Console Output:** Verify that the `UserWarning` regarding the `liboqs` version mismatch is no longer present.
3.  **(Optional) Programmatic Check:** For robust verification, consider adding a small piece of code at Fava's startup (perhaps under a debug flag or in a specific test mode for the bundled application) to programmatically check the versions:
    ```python
    # Example (conceptual, actual API might differ slightly)
    import oqs
    import oqs.rand # to ensure lib is loaded
    
    try:
        # Get version from the loaded C library (liboqs.dll)
        # The exact way to get this might be via oqs.capi.OQS_VERSION_TEXT or similar
        # For oqs-python 0.12.0, it might be harder to directly query the C lib version string
        # without calling a C function that returns it.
        # However, oqs-python itself performs this check internally, leading to the warning.
        # The absence of the warning is the primary indicator.
        
        # Get version from oqs-python package
        python_wrapper_version = oqs.VERSION # e.g., "0.12.0"
        
        print(f"INFO: oqs-python (wrapper) version: {python_wrapper_version}")
        # If the warning is gone, it implies the internal check passed.
        # A more direct check of the DLL's reported version would be ideal if easily accessible.
        # For instance, if oqs.dll exports a function like `OQS_version()` that returns a string.
        
        # The warning itself comes from:
        # oqs_python_version_arr = [int(x) for x in VERSION.split(".")]
        # liboqs_version_arr = [
        #     capi.OQS_VERSION_MAJOR,
        #     capi.OQS_VERSION_MINOR,
        #     capi.OQS_VERSION_PATCH,
        # ]
        # if oqs_python_version_arr[0:2] != liboqs_version_arr[0:2]:
        #    warnings.warn(...)
        # So, ensuring capi.OQS_VERSION_MAJOR and MINOR match the python wrapper is key.
        
        major_match = oqs.capi.OQS_VERSION_MAJOR == int(python_wrapper_version.split('.')[0])
        minor_match = oqs.capi.OQS_VERSION_MINOR == int(python_wrapper_version.split('.')[1])

        if major_match and minor_match:
            print(f"SUCCESS: liboqs DLL version ({oqs.capi.OQS_VERSION_MAJOR}.{oqs.capi.OQS_VERSION_MINOR}.{oqs.capi.OQS_VERSION_PATCH}) matches oqs-python wrapper major/minor version.")
        else:
            print(f"ERROR: liboqs DLL version ({oqs.capi.OQS_VERSION_MAJOR}.{oqs.capi.OQS_VERSION_MINOR}.{oqs.capi.OQS_VERSION_PATCH}) still mismatches oqs-python wrapper major/minor version ({python_wrapper_version}).")

    except Exception as e:
        print(f"Error during programmatic version check: {e}")
    ```
4.  **Test PQC Functionality:** Perform basic PQC operations (if easily testable from the Fava CLI or UI once a file is loaded) to ensure no runtime errors occur.

By following these steps, the `liboqs` version mismatch should be resolved, leading to a more stable and reliable Fava PQC application.