# PyInstaller Build Failures Diagnosis Report v4

## 1. Introduction

This report diagnoses the consistent PyInstaller build failures encountered while attempting to build both the main Fava PQC application (using [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec)) and a minimal test case (using [`minimal_test.spec`](../../minimal_test.spec)). Both build attempts resulted in an exit code of 1, and the target `oqs.dll` was not found in the respective output directories.

This analysis is based on the provided PyInstaller logs, specifically the error message indicating an issue with command-line options.

## 2. Log Analysis Findings

The critical error message identified from the PyInstaller log output ([`docs/devops/logs/pyinstaller_debug_build_log_v4.txt`](../../docs/devops/logs/pyinstaller_debug_build_log_v4.txt)) is:

```
ERROR: option(s) not allowed:
  --debug
makespec options not valid when a .spec file is given
```

This message indicates that the PyInstaller command was executed with the `--debug` flag (or a variant like `--debug=all`) at the same time a `.spec` file was provided as input.

## 3. Root Cause Analysis

The primary root cause of the build failures is the **incorrect usage of the `--debug` command-line option with PyInstaller when a `.spec` file is specified.**

PyInstaller distinguishes between:
*   **Generating a new `.spec` file:** Options like `--debug`, `--name`, `--onefile`, etc. (referred to as `makespec` options) are used here.
*   **Building from an existing `.spec` file:** In this mode, `makespec` options are generally not allowed on the command line because their equivalents are configured *within* the `.spec` file itself.

The error message "makespec options not valid when a .spec file is given" explicitly states this conflict. When PyInstaller encounters this invalid command-line argument combination, it terminates prematurely, before it can correctly parse the spec file and perform the bundling operations.

## 4. Impact on Builds

This premature termination due to invalid arguments directly leads to the observed symptoms:
*   **Exit Code 1:** PyInstaller exits with an error status.
*   **`oqs.dll` Not Found:** The bundling process, which includes copying `oqs.dll` as specified in the `binaries` section of the spec files, is never properly executed.
*   **Incomplete Build Artifacts:** The `build/` and `dist/` directories will likely be incomplete or missing critical components.

## 5. Recommendations

To resolve these build failures, the PyInstaller command invocation needs to be corrected.

1.  **Remove Conflicting Command-Line Option:**
    *   When running PyInstaller with [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec) or [`minimal_test.spec`](../../minimal_test.spec), **remove the `--debug` or `--debug=all` flag from the command line.**

    For example, instead of:
    ```bash
    pyinstaller --debug=all fava_pqc_installer.spec
    ```
    Use:
    ```bash
    pyinstaller fava_pqc_installer.spec
    ```

2.  **Correctly Enabling Debug Output (If Still Needed):**
    *   **For PyInstaller's Build Process Logging:** To get verbose logging from PyInstaller itself during the build process when using a spec file, use the `--loglevel` option:
        ```bash
        pyinstaller --loglevel=DEBUG fava_pqc_installer.spec
        ```
        Valid levels typically include `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`, `CRITICAL`.

    *   **For Debugging the Bundled Application:** If the goal of `--debug` was to create a debug-friendly version of the *bundled application* (e.g., with console visible, unstripped binaries for easier debugging of the Python code itself when run), this is controlled within the `.spec` file, primarily in the `EXE` object:
        ```python
        # In your .spec file (e.g., fava_pqc_installer.spec)
        exe = EXE(
            pyz,
            a.scripts,
            # ... other parameters
            debug=True,  # This creates a debug build of your application
            console=True, # Ensure console is true for CLI apps or to see prints
            strip=False, # Avoid stripping symbols if you need to debug the exe
            # ...
        )
        ```
        The [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec) already has `debug=False` and `console=True` in its `EXE` definition. If application-level debugging is needed, `debug` can be set to `True` here.

## 6. Verifying the Fix

After applying the recommended changes to the PyInstaller command:
1.  Re-run the PyInstaller build for both the main application and the minimal test case.
2.  Check for an exit code of 0.
3.  Verify that `oqs.dll` (or `liboqs.dll` as intended for the bundle destination) is present in the `dist/<output_folder_name>/` directory.
4.  If the build succeeds, attempt to run the generated executable to ensure basic functionality.

## 7. Further Investigation (If Necessary)

If removing the conflicting `--debug` flag and using `--loglevel=DEBUG` does not resolve the issue, or if new errors appear in the full log:
*   **Examine the full PyInstaller output** (from `docs/devops/logs/pyinstaller_debug_build_log_v4.txt`) for subsequent errors that might have been masked by the initial command-line parsing failure.
*   **Inspect `build/<spec_name>/warn-*.txt` files:** These files (e.g., `build/fava_pqc_dist/warn-fava_pqc_dist.txt`) contain warnings about missing modules or other issues encountered during the `Analysis` phase. These might provide clues if the DLL is correctly specified but still not found due to other reasons (e.g., path issues within the spec that only manifest once the command is correct, or unmet dependencies of `oqs.dll` itself, though PyInstaller might not always detect the latter).
*   **Verify DLL Path in Spec:** Double-check the `liboqs_dll_path` in [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec) and `dll_path` in [`minimal_test.spec`](../../minimal_test.spec) to ensure they correctly point to the `oqs.dll` file relative to the location where PyInstaller is being executed. The current spec files use `os.path.abspath`, which should be robust if the relative path from the workspace root (`liboqs/build/bin/Debug/oqs.dll`) is correct. The print statements in the spec files (`INFO: Attempting to use DLL from...` and `MINIMAL_TEST_SPEC: Attempting to bundle DLL...`) should confirm the path PyInstaller resolves.

However, the provided error message is a strong indicator that the command-line invocation is the immediate problem.

## 8. Conclusion

The PyInstaller build failures are most likely due to an incorrect command-line invocation, specifically using the `--debug` option simultaneously with a `.spec` file. Correcting the command as recommended should allow PyInstaller to proceed with the build process as defined in the spec files.