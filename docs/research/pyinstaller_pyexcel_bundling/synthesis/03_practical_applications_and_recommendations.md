# Practical Applications and Recommendations for Fava PQC

This document translates the synthesized insights into practical applications and concrete recommendations for resolving the PyInstaller bundling issues for the Fava PQC Windows `.exe` installer.

## I. Immediate PyInstaller Strategy for Fava PQC

**Recommendation 1: Adopt a Hook-Centric Approach with Comprehensive Metadata.**

*   **Application:**
    1.  **Create/Refine `hook-lml.py`:**
        *   Ensure it includes `hiddenimports += collect_submodules('lml')`.
        *   Crucially, add `datas += copy_metadata('lml')`. This is to ensure `entry_points.txt` or similar metadata used by `lml` for plugin discovery is included in the bundle.
    2.  **Create/Refine Hooks for `pyexcel` and its Plugins (e.g., `hook-pyexcel.py`, `hook-pyexcel_io.py`, `hook-pyexcel_xls.py`, etc., or a consolidated hook):**
        *   For `pyexcel` itself and each `pyexcel-*` plugin package that Fava PQC utilizes (e.g., `pyexcel-io`, `pyexcel-xls`, `pyexcel-xlsx`, `pyexcel-ods3`, `pyexcel-text`):
            *   `hiddenimports += collect_submodules('package_name')`
            *   `datas += copy_metadata('package_name')` (Essential for `lml` to find these plugins via their entry points).
            *   `datas += collect_data_files('package_name')` (To catch any non-Python data files specific to a plugin).
            *   `binaries += collect_dynamic_libs('package_name')` (If any plugin unexpectedly contains or depends on a C extension).
    3.  **Create/Refine `hook-oqs.py` (or integrate into main spec):**
        *   Ensure `oqs.dll` (and any other required `.dll` from `liboqs`) is explicitly included. Use `collect_dynamic_libs('oqs')` if `oqs-python` structures its package to allow this, or a direct `binaries=[('path/to/oqs.dll', '.')]` entry in the `.spec` file, ensuring the path is correct relative to the build environment.
    4.  **Consolidate Hooks:** Place all custom hooks in a dedicated directory (e.g., `build_hooks/`) and add `hookspath=['build_hooks/']` to the `Analysis` call in `fava_pqc_installer.spec`.

*   **Rationale:** This directly addresses the dynamic loading of `pyexcel` plugins via `lml` (by including their metadata) and ensures all their code and necessary C libraries for `oqs-python` are bundled. This is more robust than relying solely on an extensive list of `hiddenimports` in the spec file.

**Recommendation 2: Systematically Verify and Augment `hiddenimports` in `fava_pqc_installer.spec`.**

*   **Application:**
    1.  Review the current `hiddenimports` in `fava_pqc_installer.spec`.
    2.  Cross-reference with the errors in `docs/devops/logs/pyinstaller_build_log_v10.txt`. Many of the `pyexcel_io.readers.*` and `pyexcel_io.writers.*` errors might be resolved by the `copy_metadata` approach in hooks, as `lml` should then be able to find them.
    3.  However, explicitly list core plugin modules if they are directly imported anywhere or if `copy_metadata` proves insufficient for certain plugins. For example, if `pyexcel-xls` is used, `hiddenimports=['pyexcel_xls']` is still good practice.
*   **Rationale:** `hiddenimports` can catch top-level packages that hooks might assume are found, providing a safety net.

**Recommendation 3: Implement Rigorous Build Analysis and Runtime Testing.**

*   **Application:**
    1.  Always build with `--log-level=DEBUG` (or `--debug=imports`) to get detailed logs from PyInstaller.
    2.  Carefully examine the `build/fava_pqc_installer/warn-fava_pqc_installer.txt` file after every build for clues about missing modules.
    3.  Test the bundled `.exe` in a **clean Windows environment** (e.g., a virtual machine) that does not have Python or any Fava PQC development dependencies installed.
    4.  Specifically test all Excel/spreadsheet import/export functionalities that Fava PQC is expected to support.
    5.  Test all PQC functionalities to ensure `oqs.dll` is correctly loaded and functioning.
*   **Rationale:** Catches issues early and ensures the application is truly standalone.

## II. Addressing Knowledge Gaps (If Initial Strategy is Insufficient)

**Recommendation 4: Investigate `lml`'s Precise Plugin Discovery for `pyexcel`.**

*   **Application:** If `copy_metadata` in hooks doesn't fully resolve `pyexcel` plugin issues:
    1.  Examine the `lml` source code, particularly how it interacts with `pkg_resources.iter_entry_points` or `importlib.metadata.entry_points`.
    2.  Check if `pyexcel` or `lml` uses any custom environment variables or configuration files for plugin paths that might be disrupted by PyInstaller's bundling.
    3.  If necessary, add logging to `lml` or `pyexcel` within Fava PQC (in a development branch) to trace how it attempts to find and load plugins when run normally versus when bundled. This can reveal incorrect paths or missing metadata.
*   **Rationale:** Understanding the exact mechanism is key to crafting perfect hooks or runtime adjustments.

**Recommendation 5: Iteratively Refine Hooks and `hiddenimports`.**

*   **Application:** Based on build warnings and runtime testing failures:
    1.  If a specific `pyexcel_io.readers.xyz` is still not found, ensure `pyexcel-io`'s metadata is copied and `pyexcel_io` submodules are collected.
    2.  If `pyexcel_xls` fails, ensure `pyexcel-xls` metadata is copied, its submodules collected, and also that underlying libraries like `xlrd` and `xlwt` are included as `hiddenimports` if not picked up automatically.
*   **Rationale:** Packaging complex applications is often an iterative refinement process.

## III. Contingency Planning

**Recommendation 6: Prepare to Evaluate Nuitka if PyInstaller Remains Problematic.**

*   **Application:** If, after diligent application of hook strategies and debugging, PyInstaller cannot reliably bundle Fava PQC (especially if `oqs-python` or `lml` issues persist):
    1.  Set up a Nuitka build environment (including a C compiler like MinGW or MSVC for Windows).
    2.  Attempt to build a minimal Fava PQC version with Nuitka, focusing on:
        *   Including `oqs-python` (Nuitka should handle C extensions well).
        *   Including `pyexcel` and its plugins. This will likely require Nuitka-specific flags like `--include-package=pyexcel_xls` and potentially `--include-package-data` for the `dist-info` directories of `lml` and `pyexcel` plugins (equivalent to `copy_metadata`).
    3.  Compare build complexity, output size, and runtime stability.
*   **Rationale:** Nuitka offers a fundamentally different approach (compilation to C) that might bypass some of PyInstaller's static analysis limitations, particularly for C extensions and potentially for module discovery.

## IV. General Best Practices

**Recommendation 7: Version Pinning.**

*   **Application:** Once a working build configuration is achieved (with PyInstaller or an alternative), pin the versions of Python, PyInstaller, `pyexcel` (and all its plugins), `lml`, `oqs-python`, and other critical dependencies in `requirements.txt` or a similar dependency management file.
*   **Rationale:** Prevents unexpected build breakages due to updates in dependencies.

By systematically applying these recommendations, starting with the PyInstaller hook-centric strategy, it should be possible to achieve a reliable build for Fava PQC.