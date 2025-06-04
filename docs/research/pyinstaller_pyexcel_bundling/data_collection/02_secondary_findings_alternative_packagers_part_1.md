# Secondary Findings: Alternative Python Packaging Tools (Part 1)

This document explores alternative Python packaging tools to PyInstaller, considering their suitability for applications with complex dependencies like C extensions (e.g., `oqs-python`) and dynamic plugin systems (e.g., `pyexcel` using `lml`). This is relevant if PyInstaller solutions prove overly complex or insufficient.

## 1. Overview of Alternatives

The primary alternatives to PyInstaller considered are Nuitka, cx_Freeze, and Briefcase. Each has different strengths and weaknesses regarding the key challenges of this research.

| Feature                 | PyInstaller (Baseline)          | Nuitka                               | cx_Freeze                             | Briefcase (BeeWare)                     |
|-------------------------|---------------------------------|--------------------------------------|---------------------------------------|-----------------------------------------|
| **Primary Approach**    | Bundles Python interpreter & bytecode | Compiles Python to C, then to exe  | Freezes scripts with interpreter    | Packages full app environment           |
| **C Extension Support** | Good, but may need manual `.spec` tuning for DLLs/SOs | Excellent (compiles C code directly) | Fair (relies on `setuptools` detection) | Fair (relies on `setuptools` detection) |
| **Dynamic Imports**     | Static analysis + explicit `hiddenimports`/hooks | Advanced static analysis, often better detection; may need plugin flags | Requires explicit `includes` in `setup.py` | Often requires manual bundling/pathing  |
| **Output Size**         | Large                           | Moderate to Large (can be smaller if optimized) | Large                                 | Very Large (includes full Python env)   |
| **Build Complexity**    | Moderate (Spec file)            | High (C compiler toolchain needed)   | Low to Moderate (`setup.py`)          | Moderate to High (BeeWare toolchain)    |
| **Windows EXE Focus**   | Strong, mature support          | Strong, requires MSVC/MinGW          | Good, generally straightforward       | Good, but more focused on GUI apps      |
| **Community/Maturity**  | Very High                       | Moderate, Active                     | Moderate, Older                       | Moderate (as part of BeeWare)         |

*References for general packaging challenges with C extensions: [4], [5] from previous search result contexts, indicating build systems like Meson or Scikit-build are preferred for complex C/C++ extensions, though these are for library building, not final executable packaging.*

## 2. Nuitka

Nuitka compiles Python code into C code, which is then compiled into an executable. This can offer performance benefits and potentially more robust dependency handling.

*   **Pros:**
    *   **C Extension Handling:** Excellent. Because it compiles to C, it can often integrate C extensions more seamlessly, including those like `oqs-python` that rely on underlying C libraries.
    *   **Dynamic Imports:** Its static analysis is generally more advanced than PyInstaller's and can sometimes automatically detect more dynamic imports. However, explicit flags like `--include-plugin-directory` or `--include-package` might still be needed for `lml`-style plugins.
    *   **Performance:** Compiled code can run faster.
    *   **Output Size:** Can sometimes produce smaller executables if LTO (Link Time Optimization) is used and unnecessary parts of Python are excluded.
*   **Cons:**
    *   **Build Complexity:** Requires a C compiler (MSVC on Windows, or MinGW). Setup can be more involved.
    *   **Build Time:** Compilation can be significantly slower than PyInstaller or cx_Freeze.
    *   **Plugin Systems:** While better, it's not guaranteed to find all `lml` plugins without hints.
*   **Example for `oqs-python` & `pyexcel` (conceptual):**
    ```bash
    nuitka --standalone --mingw64 \
           --enable-plugin=numpy \
           --include-package=oqs \
           --include-package=pyexcel \
           --include-package=pyexcel_io \
           --include-package=pyexcel_xls # ... and other pyexcel plugins
           --include-plugin-directory=path/to/lml_plugin_metadirs # If lml scans dirs
           your_script.py