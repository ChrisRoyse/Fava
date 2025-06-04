# Detailed Findings: PyInstaller, `pyexcel`, and `lml` Interactions

This section consolidates the detailed findings regarding the challenges and solutions when packaging applications using PyInstaller, specifically when they involve `pyexcel` and its `lml` (Lazy Module Loader) plugin system.

The primary issues revolve around PyInstaller's static analysis capabilities versus the dynamic nature of `pyexcel`'s plugin loading.

## Key Areas of Investigation:

1.  **Root Cause Analysis:** Understanding why PyInstaller misses dynamically loaded `pyexcel` plugins.
    *   For full details, refer to: [`../../data_collection/01_primary_findings_part_1.md`](../../data_collection/01_primary_findings_part_1.md)

2.  **PyInstaller Hook Strategies:** Exploring the use of PyInstaller hooks as a robust solution for including `pyexcel` plugins, their dependencies, and associated metadata. This includes the critical role of `copy_metadata` for `lml`'s `entry_point` discovery.
    *   For full details, refer to: [`../../data_collection/01_primary_findings_part_2.md`](../../data_collection/01_primary_findings_part_2.md)

These linked documents provide the comprehensive findings from the data collection phase concerning PyInstaller's interaction with `pyexcel` and `lml`. They cover:
*   The conflict between static analysis and dynamic loading.
*   Commonly missed dependencies.
*   Solutions involving `hiddenimports`.
*   The structure and best practices for creating PyInstaller hooks, including `collect_submodules`, `collect_data_files`, `copy_metadata`, and runtime hooks.
*   Specific considerations for `lml`'s plugin discovery mechanism.
*   Diagnostic techniques for troubleshooting.

This approach ensures that the final report remains organized while providing direct access to the detailed research artifacts.