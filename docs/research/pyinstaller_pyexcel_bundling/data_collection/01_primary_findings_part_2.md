# Primary Findings: PyInstaller, pyexcel, and lml Bundling (Part 2) - Hooks

This document continues the primary findings, focusing on the use of PyInstaller hooks to address issues with `pyexcel` and `lml`.

## 6. Advanced Solution: PyInstaller Hooks

While listing hidden imports can work, a more robust and maintainable solution for libraries with dynamic plugin systems like `pyexcel` (which uses `lml`) is to create custom PyInstaller hooks. Hooks are Python scripts that provide PyInstaller with additional information about how to package a library, beyond what its static analysis can determine.

### 6.1. Purpose of Hooks for Dynamic Plugins
*   **Collect Hidden Submodules**: Programmatically find and include all modules that `lml` might load dynamically.
*   **Bundle Data Files**: Ensure any non-Python files (templates, configurations) required by `pyexcel` or its plugins are included.
*   **Include Binaries**: Package any C extensions or other binary files associated with plugins.
*   **Runtime Adjustments**: Modify `sys.path` or set environment variables at runtime if plugins have specific path expectations.

### 6.2. Key PyInstaller Hook Utilities
PyInstaller provides several utility functions in `PyInstaller.utils.hooks` that are essential for writing hooks:
*   `collect_submodules(package_name)`: Collects all submodules of a given package.
*   `collect_data_files(package_name, include_py_files=False, subdir=None)`: Collects all non-Python data files from a package.
*   `collect_dynamic_libs(package_name)`: Collects all dynamic libraries (DLLs, .so, .dylib) from a package.
*   `copy_metadata(package_name)`: Collects and copies package metadata (e.g., `entry_points` from `dist-info` or `egg-info`). This can be crucial for plugin systems that rely on `pkg_resources` or `importlib.metadata` for discovery.

### 6.3. Example Hook Structure for `pyexcel` and `lml`

A hypothetical hook for `pyexcel` (e.g., `hook-pyexcel.py`) might look like this:

```python
# hook-pyexcel.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

# Initialize lists for PyInstaller
hiddenimports = []
datas = []
binaries = []

# 1. Collect pyexcel core submodules and its direct plugins
hiddenimports += collect_submodules('pyexcel')
hiddenimports += collect_submodules('pyexcel.plugins') # If plugins are directly under this namespace

# 2. Collect lml submodules, as it's the plugin loader
hiddenimports += collect_submodules('lml')
hiddenimports += collect_submodules('lml.plugin') # Specifically for plugin management parts

# 3. Explicitly add known pyexcel plugin packages
# This list would need to be comprehensive based on the application's needs
pyexcel_plugins_to_include = [
    'pyexcel_io',
    'pyexcel_xls',
    'pyexcel_xlsx',
    'pyexcel_ods3',
    'pyexcel_text',
    # Add other pyexcel-* packages used by the application
]
for plugin_pkg in pyexcel_plugins_to_include:
    hiddenimports += collect_submodules(plugin_pkg)
    datas += collect_data_files(plugin_pkg, include_py_files=True) # Include .py files if plugins are structured as data
    binaries += collect_dynamic_libs(plugin_pkg) # If any plugin has C extensions
    # Metadata might be important for lml's discovery
    datas += copy_metadata(plugin_pkg)


# 4. Collect data files from pyexcel core and lml if any
datas += collect_data_files('pyexcel')
datas += collect_data_files('lml')

# 5. Include metadata for pyexcel and lml themselves
datas += copy_metadata('pyexcel')
datas += copy_metadata('lml')

# Note: The exact submodules and data files needed can be extensive and require
# careful examination of how pyexcel and lml load and use plugins.
# The `pyexcel.plugins` namespace might not exist; plugins are often separate packages.
```

**Using the Hook:**
*   Place this file in a directory (e.g., `my_hooks`).
*   Tell PyInstaller to use this directory: `pyinstaller --additional-hooks-dir=my_hooks your_script.py`

### 6.4. Runtime Hooks for Path Adjustments

If plugins expect to be found in specific relative paths that are altered by PyInstaller's bundling (e.g., being moved into `sys._MEIPASS`), a runtime hook can adjust `sys.path` or environment variables.

*   **Example Runtime Hook (`rthook-pyexcel.py`):**
    ```python
    # rthook-pyexcel.py
    import sys
    import os

    if getattr(sys, 'frozen', False):
        # This is the directory where the bundled app's content is extracted
        meipass_dir = sys._MEIPASS
        
        # Example: If pyexcel plugins are bundled into a 'pyexcel_plugins_bundle' subdir by the main hook
        # plugin_dir_in_bundle = os.path.join(meipass_dir, 'pyexcel_plugins_bundle')
        # if os.path.isdir(plugin_dir_in_bundle) and plugin_dir_in_bundle not in sys.path:
        #     sys.path.insert(0, plugin_dir_in_bundle)
        
        # More likely, lml might need to know where to look for its plugin registration files
        # if its default scanning paths are broken. This is highly dependent on lml's internals.
        # os.environ['LML_PLUGIN_PATH'] = os.path.join(meipass_dir, 'lml_plugins_metadata_dir') 
    ```
    This runtime hook would be automatically included if named correctly (e.g., `rthooks/hook-<module>.py`) or can be specified.

### 6.5. Best Practices for Hook Development

*   **Start Small**: Begin with `hiddenimports` for the most obvious missing modules.
*   **Iterative Testing**: Build and test the application after each significant change to the hook.
*   **Use `--debug=all` (or `--debug=imports`)**: During PyInstaller build, this provides verbose output about module discovery and can help pinpoint what's missing.
*   **Inspect `build/<appname>/warn-<appname>.txt`**: This file lists modules PyInstaller couldn't find.
*   **Check `pyinstaller-hooks-contrib`**: The [pyinstaller-hooks-contrib GitHub repository](https://github.com/pyinstaller/pyinstaller-hooks-contrib) is a community-maintained collection of hooks for many popular libraries. It's a good place to check for existing `pyexcel` or `lml` hooks, or to find inspiration for creating new ones [1].
*   **Understand Library Internals**: Effective hook writing often requires some understanding of how the target library (in this case, `pyexcel` and `lml`) discovers and loads its components/plugins.

### 6.6. Specific Considerations for `lml`
`lml` (Lazy Module Loader) typically uses Python's `entry_points` mechanism (via `pkg_resources` or `importlib.metadata`) to discover plugins.
*   **`copy_metadata('package_name')`**: This PyInstaller hook utility is crucial. It ensures that the `dist-info` or `egg-info` directories, which contain the `entry_points.txt` file, are bundled. `lml` reads this file at runtime to find available plugins.
*   If `lml` is configured to scan specific directories for plugins, those directories or their contents might need to be replicated in the bundle, and `lml` might need to be informed of their new location at runtime (potentially via a runtime hook setting an environment variable or patching a config).

The strategy of using `collect_submodules` for plugin packages and `copy_metadata` for those same packages (and for `lml` itself) is likely a key combination for `pyexcel`.

## References from Search Results
[1] PyInstaller documentation or community discussions on hook best practices and contributions.
[2] Examples of hooks using `collect_data_files`.
[3] Discussions on debugging PyInstaller builds.
[4] Information on bundling data files and runtime path adjustments.
[5] General PyInstaller troubleshooting tips.