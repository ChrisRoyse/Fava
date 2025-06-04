# Fava PQC Installer: `oqs.dll` Bundling Failure Diagnostic Report v3

## 1. Introduction & Symptom

This report addresses the persistent issue where `oqs.dll` is not being bundled into the `dist/fava_pqc_dist/` directory by PyInstaller when building the Fava PQC application. This occurs even after modifications to the [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec) file intended to resolve this. The PyInstaller process completes with exit code 0, as seen in [`docs/devops/logs/final_installer_compilation_log_v3.txt`](../../docs/devops/logs/final_installer_compilation_log_v3.txt), yet the target DLL remains missing from the output.

## 2. Analysis of Current State and Provided Information

*   **[`fava_pqc_installer.spec`](../../fava_pqc_installer.spec):**
    *   The current relevant lines are:
        ```python
        liboqs_dll_path = os.path.abspath('liboqs/build/bin/Debug/oqs.dll')
        # ...
        custom_binaries.append((liboqs_dll_path, '.'))
        ```
    *   This intends to take `oqs.dll` from the specified absolute path and place it into the root of the bundle (denoted by `'.'`).
    *   Print statements were added to the spec file, and their output is visible in the log:
        *   `INFO: Attempting to use DLL from: C:\code\ChrisFava\liboqs\build\bin\Debug\oqs.dll`
        *   `INFO: Will attempt to bundle 'C:\code\ChrisFava\liboqs\build\bin\Debug\oqs.dll' as 'oqs.dll' in the bundle root directory`
        These confirm that `liboqs_dll_path` is resolving to the correct absolute path and that `os.path.exists(liboqs_dll_path)` (implicitly, as the "CRITICAL WARNING" for DLL not found was not printed) is true at the time the spec file is processed by PyInstaller.

*   **[`docs/devops/logs/final_installer_compilation_log_v3.txt`](../../docs/devops/logs/final_installer_compilation_log_v3.txt):**
    *   Line 21: `527 INFO: Appending 'binaries' from .spec` - This confirms PyInstaller is processing the `binaries` list.
    *   Line 130: `24658 INFO: Warnings written to C:\code\ChrisFava\build\fava_pqc_installer\warn-fava_pqc_installer.txt` - This warning file is crucial.
    *   Line 131: `24738 INFO: Graph cross-reference written to C:\code\ChrisFava\build\fava_pqc_installer\xref-fava_pqc_installer.html` - This HTML file (if `--debug=all` was used, which is recommended) can show how files are traced.
    *   The log shows many `ERROR: Hidden import ... not found` messages for `pyexcel_io` submodules (lines 94-106). While these are unlikely to be the direct cause of `oqs.dll` not being bundled, they indicate potential underlying issues with dependency resolution or spec file completeness that might indirectly affect how PyInstaller handles other files. However, the primary focus remains on the explicit `binaries` directive.
    *   **Crucially, the log does not show any specific error or warning related to the `oqs.dll` bundling itself after the initial "INFO: Will attempt to bundle..." message.** This silence is suspicious. PyInstaller usually logs if it copies a binary or if it encounters an issue doing so.

*   **Previous Reports ([`debug_installer_launch_failure_report.md`](../../docs/reports/debug_installer_launch_failure_report.md) and [`debug_installer_launch_failure_report_v2.md`](../../docs/reports/debug_installer_launch_failure_report_v2.md)):**
    *   Report v2 hypothesized that the DLL might be nested incorrectly (e.g., `_internal\liboqs.dll\oqs.dll`). The current spec uses `'.'` as the destination, which *should* place it in the root. The previous attempt that led to report v2 used `'liboqs.dll'` as the destination, which was suspected to cause the folder issue. The change to `'.'` was intended to fix this.

## 3. Primary Hypotheses for `oqs.dll` Not Being Bundled

Given that the path resolves correctly, the file exists, and PyInstaller acknowledges the intent to bundle, the failure likely lies in a more subtle aspect of PyInstaller's processing or configuration:

1.  **Silent Filter/Exclusion:** PyInstaller might be silently filtering out the DLL for some reason not immediately obvious. This could be due to:
    *   Internal heuristics (e.g., perceiving it as a system DLL it shouldn't bundle, though unlikely for a custom path).
    *   An interaction with other settings in the spec file (e.g., `exclude_binaries=True` in the `EXE` block is correct for `COLLECT` builds, but worth noting).
2.  **Name Collision/Overwrite (Less Likely with `.` destination):** If another file named `oqs.dll` were being processed and placed in the root from a different source, it could overwrite it. However, this is less likely to result in complete absence without warnings.
3.  **COLLECT Step Issue:** The `COLLECT` step is responsible for gathering all files. If `a.binaries` is somehow empty or `oqs.dll` is removed from it between `Analysis` and `COLLECT`, it wouldn't be included. The log shows `24892 INFO: checking COLLECT` and `24925 INFO: Building COLLECT COLLECT-00.toc`, followed by success, but doesn't detail *what* it collected in terms of specific binaries.
4.  **Permissions/Locking (Still a Remote Possibility):** Although PyInstaller exits with 0, a transient lock during the copy phase for this specific file could cause a silent skip.
5.  **PyInstaller Bug/Edge Case:** It's possible there's an edge case or bug in the version of PyInstaller being used (6.14.0) related to bundling DLLs from absolute paths with a `.` destination, especially in conjunction with other complex spec file features.

## 4. Recommended Diagnostic and Fix Strategy

The strategy involves progressively isolating the issue, starting with the most direct checks and moving towards more comprehensive tests.

### Step 1: Verbose Logging & Build Artifact Inspection (Crucial Next Step)

*   **Action:** The next PyInstaller run (triggered by `deployment-manager` or manually) **MUST** use the `--debug=all` flag.
    ```bash
    pyinstaller --debug=all fava_pqc_installer.spec
    ```
*   **Rationale:** This flag is essential. It will:
    *   Prevent PyInstaller from deleting the `build/fava_pqc_installer/` directory.
    *   Generate more detailed logs.
    *   Potentially create more detailed `xref-*.html` and `warn-*.txt` files.
*   **Inspection:**
    1.  **`build/fava_pqc_installer/warn-fava_pqc_installer.txt`:** Examine this file *very carefully* for any mention of `oqs.dll`, even if it's not an explicit error.
    2.  **`build/fava_pqc_installer/xref-fava_pqc_installer.html`:** Open this file in a browser. It visualizes the dependency graph and file collection. Search for `oqs.dll` to see how (or if) PyInstaller processed it.
    3.  **`build/fava_pqc_installer/COLLECT-00.toc` (or similar TOC files):** This Table of Contents file for the `COLLECT` step lists all items that were supposed to be gathered. Check if `oqs.dll` is listed there with the correct source and destination.
    4.  **Directory `build/fava_pqc_installer/localpycos/` (if present):** Check if `oqs.dll` was mistakenly treated as Python bytecode.
    5.  **Directory `build/fava_pqc_installer/bincache/` (if present):** Check if `oqs.dll` is present here. This is where PyInstaller caches binary dependencies.

### Step 2: Modify `.spec` for More Explicit Path Debugging (If Step 1 is Inconclusive)

*   **Action:** Add more detailed print statements *inside* the spec file to trace the `custom_binaries` list just before the `Analysis` and `COLLECT` steps.
    ```python
    # In fava_pqc_installer.spec

    # ... (liboqs_dll_path definition and initial prints) ...
    custom_binaries = []
    if liboqs_dll_path:
        custom_binaries.append((liboqs_dll_path, '.'))
        print(f"INFO: custom_binaries before Analysis: {custom_binaries}", file=sys.stderr) # ADDED
    else:
        print("CRITICAL WARNING: liboqs_dll_path is None...", file=sys.stderr)

    a = Analysis(
        [FAVA_MAIN_SCRIPT],
        pathex=['src'],
        binaries=custom_binaries, # Ensure this is custom_binaries
        # ... rest of Analysis
    )
    print(f"INFO: a.binaries after Analysis: {a.binaries}", file=sys.stderr) # ADDED

    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

    exe = EXE(
        # ...
    )

    print(f"INFO: Binaries to be collected by COLLECT: {a.binaries}", file=sys.stderr) # ADDED
    coll = COLLECT(
        exe,
        a.binaries, # This is the key list for COLLECT
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='fava_pqc_dist'
    )
    ```
*   **Rationale:** This will show in the PyInstaller log exactly what the `binaries` list contains at various stages. If `oqs.dll` disappears from `a.binaries` before the `COLLECT` step, it points to an issue within the `Analysis` phase or how its attributes are populated.

### Step 3: Test with `datas` Field as an Alternative

*   **Action:** Temporarily modify the spec to use the `datas` field instead of `binaries` for `oqs.dll`.
    ```python
    # In fava_pqc_installer.spec
    # Comment out or remove from custom_binaries
    # custom_binaries.append((liboqs_dll_path, '.'))

    # Add to fava_datas (or a new list if preferred)
    if liboqs_dll_path:
        fava_datas.append((liboqs_dll_path, '.')) # Add DLL via datas
        print(f"INFO: Attempting to bundle oqs.dll via DATAS: {liboqs_dll_path}", file=sys.stderr)

    # Ensure Analysis uses the modified datas
    a = Analysis(
        # ...
        binaries=[], # Or original custom_binaries if testing oqs.dll only via datas
        datas=fava_datas,
        # ...
    )
    ```
*   **Rationale:** The `datas` mechanism is simpler and sometimes more robust for direct file copying. If this works, it suggests a problem specific to how `binaries` is handled in this context. The DLL will be treated as a generic data file but should still be usable if placed correctly.

### Step 4: Minimal Test Case (Highly Recommended for Isolation)

*   **Action:** Create and run a minimal PyInstaller setup focused *only* on bundling `oqs.dll`. A [`minimal_script.py`](../../minimal_script.py) has been created.
    Create `minimal_test.spec`:
    ```python
    # minimal_test.spec
    import os
    import sys

    block_cipher = None
    # Ensure this path is correct relative to where pyinstaller is run, or use absolute.
    # Assuming pyinstaller is run from c:\code\ChrisFava
    dll_path = os.path.abspath('liboqs/build/bin/Debug/oqs.dll')
    
    print(f"MINIMAL_TEST: Current CWD for spec: {os.getcwd()}", file=sys.stderr)
    print(f"MINIMAL_TEST: Attempting to bundle DLL: {dll_path}", file=sys.stderr)
    print(f"MINIMAL_TEST: DLL Exists: {os.path.exists(dll_path)}", file=sys.stderr)

    custom_binaries_minimal = []
    if dll_path and os.path.exists(dll_path):
        custom_binaries_minimal.append((dll_path, '.')) # Target: oqs.dll in dist/minimal_output/oqs.dll
    else:
        print(f"MINIMAL_TEST: CRITICAL - DLL not found at {dll_path}", file=sys.stderr)

    a = Analysis(['minimal_script.py'], # The dummy .py script
                 pathex=[],
                 binaries=custom_binaries_minimal,
                 datas=[],
                 hiddenimports=[],
                 hookspath=[],
                 runtime_hooks=[],
                 excludes=[])
    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
    exe = EXE(pyz, 
              a.scripts, [], 
              exclude_binaries=True, 
              name='minimal_test_exe', 
              debug=True, # Enable debug for minimal exe
              console=True)
    coll = COLLECT(exe, 
                   a.binaries, # Use a.binaries from Analysis
                   a.zipfiles, 
                   a.datas, 
                   name='minimal_output_dir') # Name of the output folder
    ```
    Run this minimal spec:
    ```bash
    pyinstaller --debug=all minimal_test.spec
    ```
    Then check the contents of `dist/minimal_output_dir/`.
*   **Rationale:** This isolates the bundling of `oqs.dll` from the complexity of the full Fava PQC spec.
    *   If `oqs.dll` **is bundled** correctly here, the problem lies within the interactions in [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec) (e.g., other binaries, datas, hiddenimports, hooks, or the sheer number of files).
    *   If `oqs.dll` **is NOT bundled** even in this minimal case, it points to a more fundamental issue:
        *   PyInstaller's ability to handle this specific DLL from this specific path.
        *   Permissions issues related to `c:\code\ChrisFava\liboqs\build\bin\Debug\oqs.dll`.
        *   A fundamental misunderstanding of the `binaries` tuple or `COLLECT` behavior for this type of file.

### Step 5: Verify DLL Integrity and Dependencies (If Still Failing)

*   **Action:** Use a tool like Dependency Walker (`depends.exe`) or `DependenciesGUI` (a modern alternative) on `c:\code\ChrisFava\liboqs\build\bin\Debug\oqs.dll`.
*   **Rationale:** Ensure the DLL itself is not corrupt and doesn't have missing dependencies that might prevent PyInstaller from processing it correctly (even if it doesn't report an error). This is less likely given PyInstaller usually reports issues with unreadable/corrupt binaries, but worth checking in persistent cases.

## 5. Definitive Explanation & Fix (To Be Determined by Above Steps)

The definitive explanation hinges on the results of the diagnostic steps above, particularly Step 1 (Verbose Logging & Build Artifact Inspection) and Step 4 (Minimal Test Case).

**If the Minimal Test Case (Step 4) SUCCEEDS:**
The issue is likely an interaction within the main [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec).
*   **Potential Cause:** Another binary/data entry might conflict, or a hook might be interfering. The `xref` and `warn` files from `--debug=all` on the main spec will be key.
*   **Potential Fix:**
    1.  Carefully review `a.binaries` and `a.datas` in the main spec (using print statements from Step 2) to see if `oqs.dll` is correctly listed before the `COLLECT` phase.
    2.  Try moving the `custom_binaries.append((liboqs_dll_path, '.'))` entry to be the *very first* item added to `binaries` or `datas` to see if order matters.
    3.  Systematically comment out other `binaries` or `datas` entries in the main spec to see if one of them is causing an issue.

**If the Minimal Test Case (Step 4) FAILS:**
The issue is more fundamental to PyInstaller's handling of this DLL.
*   **Potential Cause:**
    *   PyInstaller bug with this specific DLL type/path/name combination.
    *   File system permissions preventing PyInstaller's access in a way that doesn't trigger an immediate error but fails the copy.
    *   The DLL is of a type that PyInstaller's heuristics decide to exclude silently when using `binaries` (less likely for an explicit path).
*   **Potential Fix:**
    1.  **Try `datas` in minimal spec:** If `binaries=[(dll_path, '.')]` fails in minimal, try `datas=[(dll_path, '.')]` in `minimal_test.spec`. If `datas` works, it's a strong indicator of an issue with the `binaries` handling for this file. The solution for the main spec would then be to use `datas` for `oqs.dll`.
    2.  **Copy Manually as a Pre-build Step:** As a last resort, if PyInstaller refuses to bundle it directly via the spec, a pre-build script could copy `oqs.dll` into a temporary location within the build context (e.g., into a folder that *is* being processed by `datas`) and have the spec pick it up from there. This is a workaround, not a root cause fix.
    3.  **Check PyInstaller Version & Issues:** Look for known issues with PyInstaller 6.14.0 related to DLL bundling on Windows. Consider testing with a slightly older or newer version of PyInstaller if available.

## 6. Conclusion (Preliminary)

The path to `oqs.dll` seems correctly resolved by the spec file, and the file exists. The failure of PyInstaller to include it in `dist/fava_pqc_dist/` despite explicit instructions and no logged errors during the bundling phase points to a subtle issue. The most promising next steps are:
1.  **Run PyInstaller with `--debug=all` on [`fava_pqc_installer.spec`](../../fava_pqc_installer.spec) and meticulously examine the `warn` file, `xref` file, and `COLLECT` TOC.**
2.  **Execute the minimal test case (`minimal_test.spec`)** to isolate the problem.

The results of these two steps will significantly narrow down the root cause and guide the final fix. The `pyexcel_io` hidden import errors, while secondary, should also be addressed eventually to ensure a clean build, but are not the primary suspect for the `oqs.dll` issue.