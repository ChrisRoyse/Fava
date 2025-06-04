# Fava PQC Windows Installer Launch Failure: Diagnostic Report v2

## 1. Problem Recap

The Fava PQC application, installed via the recompiled `fava_pqc_windows_installer_v1.1.0.exe` (which was intended to fix a missing `liboqs.dll` issue), still fails to launch. The symptom remains a command prompt briefly appearing and then closing. The `dist/` directory was cleared before the last build attempt.

## 2. Analysis of Provided Information

*   **[`fava_pqc_installer.spec`](fava_pqc_installer.spec):**
    *   The spec file attempts to bundle a DLL located at `liboqs/build/bin/Debug/oqs.dll` and rename it to `liboqs.dll` in the root of the PyInstaller bundle using the `binaries` option: `custom_binaries.append((os.path.abspath('liboqs/build/bin/Debug/oqs.dll'), 'liboqs.dll'))`.
    *   This differs from the previous recommendation in [`docs/reports/debug_installer_launch_failure_report.md`](docs/reports/debug_installer_launch_failure_report.md) which suggested sourcing `liboqs.dll` from the `oqs` Python package in `site-packages`.
*   **[`docs/reports/debug_installer_launch_failure_report.md`](docs/reports/debug_installer_launch_failure_report.md):**
    *   Correctly identified the missing `liboqs.dll` as the likely culprit in the first instance.
    *   The fix involved modifying the `.spec` file.
*   **[`fava_installer.iss`](fava_installer.iss):**
    *   This Inno Setup script appears to correctly package all files from PyInstaller's output directory (`dist/fava_pqc_dist/`) into the final installer. If PyInstaller bundles `liboqs.dll` correctly, Inno Setup should include it.
*   **[`docs/devops/logs/final_installer_compilation_log_v2_attempt2.txt`](docs/devops/logs/final_installer_compilation_log_v2_attempt2.txt):**
    *   PyInstaller log confirms the attempt: `INFO: Will attempt to bundle 'C:\code\ChrisFava\liboqs\build\bin\Debug\oqs.dll' as 'liboqs.dll'`.
    *   **Crucial Finding:** The Inno Setup section of this log (line 1452) shows: `Compressing : C:\code\ChrisFava\dist\fava_pqc_dist\_internal\liboqs.dll\oqs.dll`. This indicates that `liboqs.dll` is being treated as a *directory* in the bundled output, with the original `oqs.dll` (the one that should have been renamed and placed in the root) *inside* this directory.

## 3. New Root Cause Hypothesis

**Primary Suspected Cause: Incorrect DLL Pathing/Nesting in the Bundle**

The evidence from the Inno Setup log (compressing `_internal\liboqs.dll\oqs.dll`) strongly suggests that the `liboqs.dll` is not being placed as a file in the root of the application's runtime directory as intended. Instead, it appears a folder named `liboqs.dll` is created, and the actual DLL (still named `oqs.dll`) is placed inside it.

If the Fava PQC application, when it starts, attempts to load `liboqs.dll` (expecting it as a file, e.g., `.\liboqs.dll`), it will fail because the path `.\liboqs.dll` now points to a directory, or the actual DLL is effectively at `.\liboqs.dll\oqs.dll` which the application is not looking for. This would lead to the observed "command prompt flash and close" symptom, typical of a critical DLL loading failure at startup.

The issue likely stems from how PyInstaller's `binaries` tuple `(source, destination_in_bundle)` is interacting with the one-file build process or how Inno Setup interprets the structure. The `destination_in_bundle` being `'liboqs.dll'` might be misinterpreted if the source itself has a filename that causes path confusion.

## 4. Secondary Concerns

1.  **Source and Type of `oqs.dll`:**
    The [`fava_pqc_installer.spec`](fava_pqc_installer.spec) file currently points to a *debug* version of the DLL: `liboqs/build/bin/Debug/oqs.dll`.
    *   Debug DLLs may have dependencies on debug C runtimes (e.g., debug MSVCR DLLs) that are not present on typical user machines.
    *   It's generally recommended to use release builds of dependencies for production installers. The `oqs` Python package, when installed via pip, should contain the appropriate release version of `liboqs.dll` (often named `oqs.dll` within the package) in its `site-packages/oqs` directory.
2.  **Persistent `pyexcel_io` Hidden Import Warnings:**
    The PyInstaller build log ([`docs/devops/logs/final_installer_compilation_log_v2_attempt2.txt`](docs/devops/logs/final_installer_compilation_log_v2_attempt2.txt:99-119)) continues to show `ERROR` then `WARNING` for unresolved hidden imports related to `pyexcel_io` (e.g., `pyexcel_io.readers.csvr`). While perhaps not the direct cause of this launch failure, unresolved imports can lead to unexpected runtime errors if those specific modules are ever actually needed. These should ideally be resolved or confirmed as truly unnecessary.

## 5. Crucial Next Diagnostic Step (For User)

To confirm the exact error, the user **must** run the installed application from a command prompt:
1.  Open `cmd.exe`.
2.  Navigate to the installation directory (e.g., `cd "C:\Program Files (x86)\Fava PQC"` or `cd "C:\Program Files\Fava PQC"`). The exact path can be found by right-clicking the application shortcut, selecting Properties, and checking the "Target" or "Start in" field.
3.  Execute the main application: `.\fava_pqc_installer.exe`
4.  **Carefully copy and provide the full text of any error messages or Python tracebacks that appear in the command prompt.** This output is essential for definitive diagnosis.

## 6. Recommended Fixes & Further Diagnostic Steps (For Developers)

1.  **Correct DLL Bundling in [`fava_pqc_installer.spec`](fava_pqc_installer.spec):**
    *   **Priority Fix - Addressing Pathing:** The most direct way to address the `_internal\liboqs.dll\oqs.dll` issue is to ensure PyInstaller places the DLL correctly.
        Given the spec line: `custom_binaries.append((liboqs_dll_path, 'liboqs.dll'))`
        And `liboqs_dll_path` pointing to `liboqs/build/bin/Debug/oqs.dll`.
        The intention is for `oqs.dll` to be copied to the bundle root and named `liboqs.dll`.
        If PyInstaller is creating a *folder* named `liboqs.dll`, this is highly unusual.
        A potential workaround or more robust approach:
        ```python
        # In fava_pqc_installer.spec
        # ...
        liboqs_src_path = os.path.abspath('liboqs/build/bin/Release/oqs.dll') # Prefer Release DLL
        if not os.path.exists(liboqs_src_path):
            print(f"CRITICAL WARNING: Release oqs.dll not found at {liboqs_src_path}. Trying Debug.", file=sys.stderr)
            liboqs_src_path = os.path.abspath('liboqs/build/bin/Debug/oqs.dll')
            if not os.path.exists(liboqs_src_path):
                 print(f"CRITICAL WARNING: Debug oqs.dll also not found at {liboqs_src_path}. DLL will NOT be bundled.", file=sys.stderr)
                 liboqs_src_path = None
        
        custom_binaries = []
        if liboqs_src_path:
            # Explicitly bundle it into the root directory of the distribution.
            # The second element of the tuple is the destination *relative to the bundle root*.
            # '.' means the root.
            custom_binaries.append((liboqs_src_path, '.')) 
            # This will copy oqs.dll to the root. The application must then look for 'oqs.dll'.
            # If the application *must* find 'liboqs.dll', then the source file itself should be named 'liboqs.dll'
            # OR ensure the Python code dynamically finds 'oqs.dll' or 'liboqs.dll'.
            # Forcing the name 'liboqs.dll' in the bundle:
            # custom_binaries.append((liboqs_src_path, 'liboqs.dll')) # This was the original attempt.
            print(f"INFO: Will attempt to bundle '{liboqs_src_path}' as 'oqs.dll' (or 'liboqs.dll') in the bundle root.", file=sys.stderr)
        # ...
        ```
        **Verification:** After PyInstaller runs (before Inno Setup), inspect the `dist/fava_pqc_dist/` directory. `liboqs.dll` (or `oqs.dll`) should be present as a file directly in this folder, NOT in a subfolder like `_internal` or nested within another folder named `liboqs.dll`.

    *   **Use Release DLL:** Change `liboqs/build/bin/Debug/oqs.dll` to the path of the **Release** build of `oqs.dll` (e.g., `liboqs/build/bin/Release/oqs.dll`).

2.  **Use PyInstaller `--debug=all` Flag:**
    When the `deployment-manager` (or developer) rebuilds with PyInstaller, add the `--debug=all` flag:
    `pyinstaller --debug=all fava_pqc_installer.spec`
    This will:
    *   Prevent PyInstaller from deleting the temporary build directory (`build/fava_pqc_dist/`).
    *   Include debug archives.
    *   Make the generated executable more verbose when run from the command line, which can provide more detailed error messages if the user runs the `dist/fava_pqc_dist/fava_pqc_installer.exe` directly.
    The contents of the `build/fava_pqc_dist/` directory (especially the `xref-*.html` and `warn-*.txt` files) can be very insightful.

3.  **Dependency Walker (or similar):**
    *   If the issue persists after correcting the path and using a release DLL, use Dependency Walker (or a modern equivalent like `DependenciesGUI`) on:
        1.  The `oqs.dll` (or `liboqs.dll`) that is intended to be bundled.
        2.  The main `fava_pqc_installer.exe` found in `dist/fava_pqc_dist/` *after* PyInstaller runs.
    *   This will check if `liboqs.dll` itself has any missing system dependencies, or if the main executable is failing to find other critical DLLs.

4.  **Simplify `binaries` in `.spec` for Testing:**
    As a test, if the `(source, 'liboqs.dll')` syntax is causing the folder issue, try:
    `custom_binaries.append((os.path.abspath('liboqs/build/bin/Release/oqs.dll'), '.'))`
    This will copy `oqs.dll` to the bundle root. Then, temporarily modify the Python code (if possible, or for a test script) to explicitly load `oqs.dll` instead of `liboqs.dll` to see if this simpler bundling works. This helps isolate if the renaming/destination part of the tuple is the problem.

5.  **Address `pyexcel_io` Warnings:**
    While likely not the primary cause, investigate these:
    *   Ensure `pyexcel` and `pyexcel-io` are correctly installed in the build environment.
    *   If these modules are truly not used by Fava, they could be added to `excludes` in the `.spec` file's `Analysis` section. However, confirm they are not indirect dependencies.
    *   If they *are* needed, the hidden imports might require specific hooks or explicit additions to `hiddenimports` that correctly point to their submodules. The current entries like `'pyexcel_io.readers.csvr'` are not working.

6.  **Review Inno Setup Script ([`fava_installer.iss`](fava_installer.iss)):**
    The script seems straightforward. The line `Source: "dist\{#MyPyInstallerOutput}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs` should correctly copy the entire PyInstaller output. The issue is more likely with what PyInstaller is producing.

## 7. Conclusion

The primary hypothesis for the persistent launch failure is an incorrect bundling of `liboqs.dll` by PyInstaller, where it's nested inside a directory named `liboqs.dll` instead of being a file in the application's root. This needs to be rectified by adjusting the [`fava_pqc_installer.spec`](fava_pqc_installer.spec) file. Additionally, using a release version of `oqs.dll` and resolving other PyInstaller warnings is recommended.

The immediate next step is to obtain the console output from the user running the installed application from `cmd.exe`. This will provide the most direct evidence of the failure point.