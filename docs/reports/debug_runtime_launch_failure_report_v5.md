# Fava PQC Runtime Launch Failure Diagnostic Report v5

## 1. Issue Description

The Fava PQC application, installed using `dist/fava_pqc_windows_installer_v1.1.0.exe`, fails to launch correctly. Users report a command prompt window appearing briefly with debug messages, then closing automatically, preventing the application from running. This occurs despite a successful PyInstaller build (exit code 0) that included `debug=True` in the `EXE` object, and hooks for `pyexcel` and `lml`, and bundled `oqs.dll`.

## 2. Objective

Diagnose the runtime launch failure by first capturing the debug messages displayed in the fleeting command prompt.

## 3. Critical Next Step: Capture Console Output

To diagnose this issue, we **urgently need the full output** from the command prompt when the application attempts to run. Please follow these steps precisely:

1.  **Open Command Prompt:**
    *   Press the Windows key.
    *   Type `cmd.exe`.
    *   Right-click on "Command Prompt" and select "Run as administrator" (this might provide more detailed error messages, though standard user should also work for capturing). If issues persist, try without administrator first.
2.  **Navigate to the Installation Directory:**
    *   The application is typically installed in `C:\Program Files\Fava PQC` or `C:\Program Files (x86)\Fava PQC`. You can verify this by checking the properties of the desktop or Start Menu shortcut created by the installer.
    *   In the command prompt window, type `cd "C:\Program Files\Fava PQC"` and press Enter.
    *   **Note:** If Fava PQC is installed in a different location, please adjust the path accordingly. For example, if it's in `C:\Program Files (x86)\Fava PQC`, use `cd "C:\Program Files (x86)\Fava PQC"`.
3.  **Run the Executable:**
    *   Once you are in the correct directory (the prompt should show the path, e.g., `C:\Program Files\Fava PQC>`), type the executable name `fava_pqc_installer.exe` and press Enter.
    *   The executable name is confirmed from the PyInstaller spec file ([`fava_pqc_installer.spec:158`](fava_pqc_installer.spec:158)).
4.  **Copy All Output:**
    *   The application will attempt to run, and messages will appear in the command prompt window. Even if it closes quickly, because you launched it from an *already open* command prompt, the messages will remain visible.
    *   **Crucially, select and copy ALL text** from the command prompt window. This includes any error messages, Python tracebacks, debug output, and any other text that appears after you run the command.
    *   To copy: Right-click anywhere in the command prompt window and select "Mark". Then, drag your mouse to select all the text. Press Enter or right-click again to copy the selected text.
5.  **Provide the Captured Output:**
    *   Paste the copied text into the section below.

## 4. User-Provided Console Output

**(Please paste all copied text from the command prompt here after running the executable as described above. This information is ESSENTIAL for diagnosis.)**

```
[PASTE CONSOLE OUTPUT HERE]
```

## 5. Preliminary Analysis of Potential Runtime Issues (Pending Console Output)

Given that the PyInstaller build process completed successfully and included:
*   The `debug=True` flag ([`fava_pqc_installer.spec:159`](fava_pqc_installer.spec:159)), which should provide more verbose output.
*   Custom hooks for `pyexcel`, `lml`, and other dependencies ([`fava_pqc_installer.spec:139`](fava_pqc_installer.spec:139)).
*   Explicit bundling of `oqs.dll` ([`fava_pqc_installer.spec:36`](fava_pqc_installer.spec:36)).

The runtime failure suggests issues that are not detectable at build time, such as:

*   **Missing Data Files or Incorrect Paths at Runtime:**
    *   While PyInstaller hooks aim to bundle necessary data files (like templates, static assets, or plugin-specific files for `pyexcel`), some might be missed or paths might be resolved incorrectly in the bundled environment. The `debug=True` output might show `FileNotFoundError` or similar.
    *   The application might be trying to access resources using paths relative to the source code structure, which no longer exist in the bundled app. PyInstaller's `sys._MEIPASS` should be used for accessing bundled files, but not all parts of the application or its dependencies might be using it correctly.
*   **DLL Loading or Initialization Issues:**
    *   **`oqs.dll`:** Although bundled, there could be issues with its dependencies on the target system, or how it's being loaded/initialized by the `oqs` Python wrapper at runtime. The console output might show "DLL load failed" errors, or tracebacks originating from the `oqs` module.
    *   **Other C-extensions:** Dependencies like `pyexcel` plugins might themselves rely on C extensions that have runtime loading issues not caught by PyInstaller.
*   **Python Environment Issues within the Bundle:**
    *   An `ImportError` for a module that was thought to be included, or a submodule that wasn't correctly picked up despite hooks.
    *   Conflicts or issues with how standard library modules behave in the frozen environment.
*   **`pyexcel` Plugin Runtime Problems:**
    *   Even if `pyexcel` and its `io` component are bundled via hooks, specific plugins (e.g., for `.ods`, `.xlsx`) might have their own runtime dependencies or initialization routines that fail in the bundled environment. The error messages might point to a specific `pyexcel` plugin.
*   **Application Logic Errors Triggered at Startup:**
    *   A bug in Fava PQC's startup sequence that only manifests in the bundled environment (e.g., related to configuration loading, early PQC initializations).
*   **Permissions Issues:**
    *   The application might be trying to write to a location it doesn't have access to (e.g., a log file in a restricted directory). Running from an admin command prompt (as suggested for capture) might bypass this, but it's worth noting.

## 6. Initial Hypotheses (to be refined with console output)

1.  **Most Likely: `ImportError` or `FileNotFoundError` related to `pyexcel` or one of its plugins/dependencies.** Given the past issues with `pyexcel` bundling, a runtime failure related to it remains a strong possibility. The hooks might not have captured everything needed for *runtime* operation of all desired `pyexcel` features.
2.  **Possible: `oqs.dll` loading or path issue at runtime.** The DLL might be present but not found/loadable by the Python `oqs` wrapper due to how paths are resolved or if it has further system dependencies not met.
3.  **Less Likely (but possible): A core Fava or PQC module path issue.** A part of the application might be trying to access a file (template, static asset, config) using an incorrect path in the bundled environment.

## 7. Next Steps

1.  **Obtain and Analyze Console Output:** This is the absolute priority. The specific error messages and tracebacks will guide further investigation.
2.  **If `ImportError`:** Identify the missing module. Update PyInstaller hooks or `hiddenimports` in [`fava_pqc_installer.spec`](fava_pqc_installer.spec).
3.  **If `FileNotFoundError`:** Identify the missing file and its expected location. Update PyInstaller `datas` in [`fava_pqc_installer.spec`](fava_pqc_installer.spec) or correct path usage in the code.
4.  **If DLL Load Failed:**
    *   For `oqs.dll`: Investigate how `oqs-python` finds/loads the DLL at runtime in a bundled app. Consider if `oqs.dll` itself has dependencies that are missing on the target system.
    *   For other DLLs: Identify the source (likely a dependency) and ensure it's correctly bundled and its own dependencies are met.
5.  **Examine PyInstaller Warnings:** Review the PyInstaller build log again for any warnings that might have been overlooked, even if the build exited with code 0.
6.  **Iterate on the PyInstaller Spec:** Based on the findings, refine [`fava_pqc_installer.spec`](fava_pqc_installer.spec) and rebuild the application and installer.

This report will be updated once the console output is provided.