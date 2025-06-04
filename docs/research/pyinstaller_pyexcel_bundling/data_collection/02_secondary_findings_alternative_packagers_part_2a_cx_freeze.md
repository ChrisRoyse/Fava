# Secondary Findings: Alternative Python Packaging Tools (Part 2a - cx_Freeze)

This document continues the exploration of alternative Python packaging tools, focusing on cx_Freeze.

## 3. cx_Freeze

cx_Freeze is another popular tool for creating executables. It works by "freezing" Python scripts.

*   **Pros:**
    *   **Simplicity:** Generally considered straightforward to use, often just requiring a `setup.py` file.
    *   **Pure Python Focus:** Handles standard Python applications well.
*   **Cons:**
    *   **C Extensions:** Relies on `setuptools` to correctly identify and bundle C extensions and their dependencies (like DLLs). This can be a point of failure for complex C libraries like `liboqs` if not all dependencies are found [2, 5].
    *   **Dynamic Imports:** Similar to PyInstaller, requires explicit listing of hidden imports or dynamically loaded modules in the `setup.py` (e.g., in `build_exe_options = {"includes": [...]}`).
    *   **Output Size:** Typically produces large executables as it bundles the Python interpreter.
    *   **Maintenance:** Historically, updates and community support have sometimes lagged behind PyInstaller.
*   **Example `setup.py` for `pyexcel` (conceptual):**
    ```python
    from cx_Freeze import setup, Executable

    build_exe_options = {
        "packages": ["os", "pyexcel", "pyexcel_io", "lml"],
        "includes": [
            "pyexcel_xls", "pyexcel_xlsx", # Add all pyexcel plugins
            "lml.plugin" 
            # Potentially specific lml plugin modules if known
        ],
        "include_files": [] # For any data files or DLLs not automatically picked up
    }
    setup(
        name="MyFavaApp",
        version="0.1",
        description="My Fava PQC Application",
        options={"build_exe": build_exe_options},
        executables=[Executable("your_script.py")]
    )
    ```

## References (from previous search contexts, applied generally)
[2] Information on build tools and `setuptools` for C extensions.
[5] Discussions on complex builds with C/C++ extensions and Python packaging.