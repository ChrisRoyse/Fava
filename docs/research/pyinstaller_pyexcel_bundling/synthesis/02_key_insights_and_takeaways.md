# Key Insights and Takeaways

This document distills the most critical insights and actionable takeaways from the research into packaging Fava PQC, focusing on PyInstaller, `pyexcel`, `lml`, and `oqs-python`.

## Overarching Insights

1.  **Dynamic Imports are PyInstaller's Achilles' Heel:** The core difficulty stems from PyInstaller's reliance on static analysis, which inherently struggles with libraries like `pyexcel` that use `lml` for dynamic plugin loading. This is a well-known pattern, not unique to `pyexcel`.
    *   **Takeaway:** Expect to provide significant manual guidance to PyInstaller for such libraries.

2.  **Hooks are a Necessity, Not a Luxury:** For complex libraries with plugins and metadata dependencies (like `pyexcel` using `lml` for `entry_points`), simple `hiddenimports` are often insufficient. Well-crafted PyInstaller hooks are essential for robust and maintainable solutions.
    *   **Takeaway:** Investing time in developing or finding good hooks is crucial. The `copy_metadata` utility is likely paramount for `lml`.

3.  **C Extensions Add Another Dimension of Complexity:** Packaging `oqs-python` (a CFFI wrapper for `liboqs`) requires ensuring the C library (`oqs.dll`) and any of its own runtime dependencies are correctly bundled and found.
    *   **Takeaway:** This needs specific attention in the PyInstaller configuration, separate from Python module issues.

4.  **No "Magic Bullet" Alternative:** While tools like Nuitka offer theoretical advantages (especially for C extensions), they come with their own complexities (e.g., C compiler toolchain). Switching tools isn't a simple fix and involves a new learning curve.
    *   **Takeaway:** Exhaust PyInstaller solutions first, with Nuitka as a primary, more involved, fallback.

## Actionable Takeaways for Fava PQC Packaging

1.  **Prioritize PyInstaller Hook Development:**
    *   **For `lml`:** Ensure a hook (or spec file entries) uses `copy_metadata('lml')` and `collect_submodules('lml')`. This is vital if `lml` uses `entry_points` for plugin discovery.
    *   **For `pyexcel` and each `pyexcel-*` plugin (e.g., `pyexcel-io`, `pyexcel-xls`, `pyexcel-xlsx`, `pyexcel-ods3`, `pyexcel-text`):**
        *   Use `copy_metadata('plugin_package_name')` to ensure `lml` can discover them via `entry_points`.
        *   Use `collect_submodules('plugin_package_name')` to include all their Python code.
        *   Use `collect_data_files('plugin_package_name')` if they bundle any non-Python data.
    *   **For `oqs-python`:** Ensure `oqs.dll` (and any other necessary binaries) are included, likely via `collect_dynamic_libs('oqs')` or explicit `binaries` entries.

2.  **Systematic `hiddenimports` (as a supplement or initial step):**
    *   Audit the Fava PQC codebase to identify all `pyexcel` functionalities used.
    *   Map these functionalities to their respective `pyexcel-*` plugin packages.
    *   List these plugin packages and their core modules (e.g., `pyexcel_xls`, `pyexcel_xlsx.xlsx`) as `hiddenimports`. This complements the hook strategy.
    *   The user's current `.spec` file is a starting point but needs to be cross-referenced with the build log errors and `lml`'s expected module names.

3.  **Thoroughly Analyze PyInstaller Build Output:**
    *   Pay close attention to `build/.../warn-...txt` for clues about missing modules.
    *   Use `--log-level=DEBUG` (or `--debug=imports`) during PyInstaller builds for verbose import tracing.

4.  **Iterative Testing in Clean Environments:**
    *   After each significant change to the `.spec` file or hooks, build and test the application in an environment that does not have Python or the project's development libraries installed. This is the only way to confirm true self-containment.
    *   Test all `pyexcel` import/export functionalities used by Fava PQC.

5.  **Investigate `lml`'s Exact Discovery Mechanism:**
    *   Confirm if `lml` (as used by `pyexcel`) relies *solely* on `entry_points`. If it also scans directories or has other discovery methods, hooks might need to be adapted (e.g., replicating directory structures or using runtime hooks to set environment variables like `LML_PLUGIN_PATH`). This is a key knowledge gap.

6.  **Version Pinning and Compatibility Checks:**
    *   Once a working configuration is found, pin the versions of PyInstaller, `pyexcel`, its plugins, `lml`, and `oqs-python` to avoid future breakages due to updates.
    *   If problems persist, check issue trackers for known incompatibilities between specific versions of these libraries.

7.  **Consider Nuitka as a Strategic Alternative:**
    *   If PyInstaller solutions become overly convoluted or fail to resolve issues with `oqs-python` or `lml` interactions, Nuitka is the most promising alternative.
    *   Be prepared for the setup of a C compiler toolchain (MSVC or MinGW on Windows) and a potentially more complex build command. Nuitka will also require guidance for `lml` plugins, likely via `--include-package-data` for `dist-info` folders.

By focusing on these insights and takeaways, a more structured and effective approach can be taken to resolve the Fava PQC packaging issues.