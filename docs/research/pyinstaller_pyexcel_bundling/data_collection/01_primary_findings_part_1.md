# Primary Findings: PyInstaller, pyexcel, and lml Bundling (Part 1)

This document outlines the initial findings from research into resolving "Hidden import not found" errors when packaging Python applications using PyInstaller, specifically when `pyexcel` and its `lml` (Lazy Module Loader) plugin system are involved.

## 1. Root Cause: Dynamic Plugin Loading vs. Static Analysis

The fundamental issue lies in the conflict between `lml`'s dynamic plugin loading mechanism and PyInstaller's static dependency analysis [2, 3].

*   **Dynamic Plugin Loading by `lml`**: `pyexcel` utilizes `lml` to discover and load its I/O plugins (e.g., for XLS, XLSX, CSV formats) at runtime. This is often done via methods like `lml.plugin.PluginManager.load_me_now()` [2, 3]. Because these imports are not explicitly present as static `import` statements in the codebase that PyInstaller analyzes, PyInstaller cannot automatically detect them.
*   **PyInstaller's Static Analysis**: PyInstaller primarily works by analyzing `import` statements in the Python scripts to determine dependencies. When modules are loaded dynamically (e.g., using `importlib` or plugin systems like `lml`), PyInstaller often misses these "hidden" imports [4].

## 2. Consequences of Missed Dynamic Imports

When PyInstaller fails to detect these dynamically loaded plugins:
*   The necessary plugin modules (e.g., `pyexcel_xls.xlsr`, `pyexcel_io.readers.csvr`) are not included in the bundled application.
*   At runtime, when `pyexcel` attempts to use a specific file format, `lml` tries to load the corresponding plugin. Since the plugin module is missing from the bundle, a `ModuleNotFoundError` or similar error occurs, often manifesting as a "Hidden import not found" warning during the build and an error during execution.

## 3. Key Dependencies Often Missed

Based on initial findings, common modules and submodules that PyInstaller might miss include:

*   **Core `pyexcel-io` modules**: These handle the basic I/O operations. Examples include:
    *   `pyexcel_io.readers.csvr`
    *   `pyexcel_io.readers.tsv`
    *   And corresponding writers.
*   **Format-specific plugin modules**: These implement the logic for particular file formats. Examples include:
    *   `pyexcel_xls.xlsr` (for reading XLS files)
    *   `pyexcel_xlsx.xlsxr` (for reading XLSX files)
    *   `pyexcel_ods.odsr` (for reading ODS files)
*   **Underlying libraries for formats**: Plugins often depend on other libraries. For example:
    *   `openpyxl` (for XLSX)
    *   `xlwt` (for writing older XLS)
    *   `xlrd` (for reading older XLS)
*   **Specific submodules of underlying libraries**: Sometimes, libraries like Pandas, when interacting with Excel files, might import specific submodules of `openpyxl` (e.g., `openpyxl.styles`) which also need to be explicitly included [1, 5].

## 4. Initial Solutions and Workarounds Identified

The most frequently suggested initial approaches to address these issues are:

### 4.1. Explicitly Listing Hidden Imports

The primary and most direct solution is to manually inform PyInstaller about these missing modules using the `--hidden-import` command-line option or by adding them to the `hiddenimports` list in the `.spec` file [3, 4, 5].

*   **Example Command-Line Usage:**
    ```bash
    pyinstaller your_script.py \
    --hidden-import=pyexcel_io.readers.csvr \
    --hidden-import=pyexcel_xls.xlsr \
    --hidden-import=pyexcel_xlsx.xlsxr \
    --hidden-import=openpyxl \
    --hidden-import=openpyxl.styles \
    --hidden-import=xlwt
    ```
*   **Comprehensive Enumeration**: For applications using many `pyexcel` features, a more extensive list of plugins might be needed [3]:
    ```bash
    # Example from a user successfully bundling pyexcel
    --hidden-import=pyexcel_io.database.importers.django \
    --hidden-import=pyexcel_io.database.exporters.sqlalchemy \
    --hidden-import=pyexcel_xlsx \
    --hidden-import=pyexcel_ods \
    --hidden-import=pyexcel_odsr
    ```

### 4.2. PyInstaller Hook Files

For more complex scenarios or to better organize hidden imports, PyInstaller hooks can be used. A hook file (e.g., `hook-pyexcel.py`) can programmatically collect necessary submodules.

*   **Example Hook Snippet:**
    ```python
    # In hook-pyexcel.py
    from PyInstaller.utils.hooks import collect_submodules

    hiddenimports = []
    hiddenimports += collect_submodules('pyexcel_io')
    hiddenimports += collect_submodules('pyexcel_xls')
    hiddenimports += collect_submodules('pyexcel_xlsx')
    # Add other pyexcel plugins as needed
    ```
    This hook file would then be specified to PyInstaller using the `--additional-hooks-dir` option.

### 4.3. Runtime Validation/Patching

A technique involves adding code to the main script to force `lml` to load plugins early, potentially aiding PyInstaller's detection or ensuring plugins are available.

*   **Example Runtime Code:**
    ```python
    import lml
    # Assuming IOPluginInfo is a way to get all plugin names
    # This part needs verification based on pyexcel/lml specifics
    # from pyexcel.plugins import IOPluginInfo 

    # class ForcedPluginLoader:
    #     def __init__(self):
    #         # This needs to be adapted to how pyexcel/lml actually list plugins
    #         # For example, if IOPluginInfo().plugins gives a list of module names:
    #         # for plugin_module_name in IOPluginInfo().plugins:
    #         #     try:
    #         #         lml.plugin.PluginManager.load_me_now(plugin_module_name)
    #         #     except Exception as e:
    #         #         print(f"Could not force load plugin {plugin_module_name}: {e}")

    # ForcedPluginLoader() # Instantiate early in your script
    ```
    *Note: The exact implementation of `ForcedPluginLoader` needs to be verified against the `pyexcel` and `lml` APIs for listing and loading plugins.*

## 5. Diagnostic Techniques

Identifying exactly which imports are missing is crucial:

*   **Analyze Build Warnings**: PyInstaller often generates a `warn-your_script.txt` file in the build directory. This file lists modules that PyInstaller couldn't find. Look for warnings related to `pyexcel`, `lml`, or specific plugin names.
    *   Example warning: `missing module named 'pyexcel_io.readers.csvr' - imported by lml.plugin (top-level)`
*   **Runtime Testing in a Clean Environment**: After building the executable, run it in a clean environment (one without Python or the project's development libraries installed) to ensure it's truly standalone and to catch any runtime `ModuleNotFoundError` exceptions.

## References from Search Results

[1] GitHub Issue/Stack Overflow discussing `openpyxl` issues with Pandas and PyInstaller.
[2] GitHub Issue discussing `pyexcel` and `lml` dynamic loading with PyInstaller.
[3] GitHub Issue/Forum post showing a user adding multiple `pyexcel_io` hidden imports.
[4] PyInstaller Documentation on hidden imports.
[5] Forum post/Issue detailing problems with Excel writers like `openpyxl` and PyInstaller.

This first part of the primary findings establishes the nature of the problem and common high-level solutions. Further research will delve deeper into specific hook implementations, the exhaustive list of plugins, and alternative packaging tools.