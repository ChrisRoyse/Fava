# Fava PQC Windows Installer Launch Failure: Diagnostic Report

## 1. Problem

Installed Fava PQC (via `dist/fava_pqc_windows_installer_v1.1.0.exe`) fails to launch; a command prompt briefly appears and closes.

## 2. Root Cause Hypothesis

**Missing `liboqs.dll` in the PyInstaller bundle.** The `oqs-python` library requires this native C DLL. If PyInstaller doesn't bundle it, the application crashes on startup when trying to use PQC features. This is indicated by `oqs_binaries = []` in [`fava_pqc_installer.spec:42`](fava_pqc_installer.spec:42).

## 3. Key Files Analysis

*   **[`fava_pqc_installer.spec`](fava_pqc_installer.spec):** Lacks explicit instruction to bundle `liboqs.dll`.
*   **[`fava_installer.iss`](fava_installer.iss):** Correctly packages PyInstaller's output. If `liboqs.dll` is in PyInstaller's output, Inno Setup will include it.
*   **[`docs/devops/logs/final_installer_compilation_log.txt`](docs/devops/logs/final_installer_compilation_log.txt):** Incomplete, suggesting potential Inno Setup build issues, but the primary symptom points to the PyInstaller bundle.

## 4. Recommended Fixes & Diagnostics

### 4.1. User Diagnostics (Immediate)

1.  **Run from Command Prompt:**
    *   Open `cmd.exe`.
    *   `cd "C:\Program Files\Fava PQC"` (or actual install path).
    *   Run `.\fava_pqc_installer.exe`.
    *   Capture any error messages (likely `ImportError` or missing DLL).
2.  **Check Windows Event Viewer:** Review "Application" logs for errors.

### 4.2. Developer Fixes (Build Process)

1.  **Crucial: Bundle `liboqs.dll` with PyInstaller:**
    *   **Locate `liboqs.dll`:** It's in your Python build environment's `site-packages/oqs/` directory (e.g., `venv/Lib/site-packages/oqs/liboqs.dll`) after `oqs-python` is installed. It is NOT directly from the `liboqs-python` source checkout unless pre-built there.
    *   **Modify [`fava_pqc_installer.spec`](fava_pqc_installer.spec):**
        ```python
        # At the top of fava_pqc_installer.spec, after block_cipher:
        import os
        import sys
        try:
            import oqs
            oqs_package_dir = os.path.dirname(oqs.__file__)
            # Adjust 'liboqs.dll' if the actual filename is different on Windows
            liboqs_dll_path = os.path.join(oqs_package_dir, 'liboqs.dll')
            if not os.path.exists(liboqs_dll_path):
                print(f"WARNING: liboqs.dll not found at {liboqs_dll_path}", file=sys.stderr)
                # Set to a placeholder or handle error to prevent PyInstaller from failing if not found,
                # but this means the bundle will be broken. Best to ensure it's found.
                liboqs_dll_path = None 
        except ImportError:
            print("WARNING: oqs module not found. Cannot locate liboqs.dll.", file=sys.stderr)
            liboqs_dll_path = None
        
        custom_binaries = []
        if liboqs_dll_path:
            # The tuple is (source_path, destination_in_bundle)
            # '.' means the DLL will be in the root of the bundled app directory.
            custom_binaries.append((liboqs_dll_path, '.'))
        else:
            print("CRITICAL WARNING: liboqs.dll path not determined. It will NOT be bundled.", file=sys.stderr)

        # In the Analysis call, update the 'binaries' argument:
        a = Analysis(
            [FAVA_MAIN_SCRIPT],
            pathex=['src'],
            binaries=custom_binaries, # MODIFIED HERE
            datas=fava_datas,
            hiddenimports=[ # Ensure 'oqs' is in hiddenimports
                'oqs',
                # ... other hiddenimports ...
            ],
            # ... rest of Analysis parameters ...
        )
        ```
    *   **Verify:** After PyInstaller, check `dist/fava_pqc_dist/` for `liboqs.dll`.

2.  **Test PyInstaller Output:** Run `dist/fava_pqc_dist/fava_pqc_installer.exe` directly before Inno Setup packaging.

3.  **Frontend Assets:** Ensure `src/fava/static/` contains all built JS/CSS/WASM before PyInstaller.

4.  **Full Inno Setup Log:** Capture and review the complete `iscc.exe` log.

## 5. Conclusion

The application fails because `liboqs.dll` is not included in the installation. Modifying [`fava_pqc_installer.spec`](fava_pqc_installer.spec) as shown above to explicitly find and bundle this DLL from the `oqs-python` package (within the build environment's `site-packages`) is the primary solution. This ensures PyInstaller includes it, and subsequently, Inno Setup packages it into the final installer, making it available when the user runs the installed application.