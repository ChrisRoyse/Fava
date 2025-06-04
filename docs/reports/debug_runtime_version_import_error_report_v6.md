# Diagnosis Report: `ImportError` for `__version__` in Fava PQC Bundled Application

**Date:** 2025-06-03
**Target Feature:** Fava PQC Application Runtime Initialization / Version Handling
**Report Version:** v6
**Debugger:** AI Debugger (🎯 Debugger (SPARC Aligned & Systematic))

## 1. Issue Summary

The Fava PQC application, when bundled using PyInstaller and run via the generated executable (`fava_pqc_installer.exe`), fails at startup with the following error:

```
Traceback (most recent call last):
  File "fava/cli.py", line 14, in <module>
ImportError: cannot import name '__version__' from 'fava' (C:\Program Files (x86)\Fava PQC\_internal\fava\__init__.py)
```

This indicates that the `__version__` attribute, expected to be available in the `fava` module, is not found when the application's command-line interface ([`src/fava/cli.py`](src/fava/cli.py:14)) attempts to import it.

## 2. Analysis of Relevant Files

### 2.1. `src/fava/__init__.py` (Version Definition)

The `__version__` attribute in Fava is defined dynamically using `importlib.metadata`:

```python
# src/fava/__init__.py, lines 5-10
from contextlib import suppress
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

with suppress(PackageNotFoundError):
    __version__ = version(__name__)
```

Here, `version(__name__)` is effectively `importlib.metadata.version('fava')`. If the packaging metadata for "fava" cannot be found, `PackageNotFoundError` is raised. The `suppress` block catches this exception, meaning `__version__` will not be assigned in such cases.

### 2.2. `src/fava/cli.py` (Version Import)

The command-line interface script attempts to import `__version__` directly from the `fava` package:

```python
# src/fava/cli.py, line 14
from fava import __version__
```

If `__version__` was not defined in [`src/fava/__init__.py`](src/fava/__init__.py:10) (due to the `PackageNotFoundError` mentioned above), this import statement will fail with an `ImportError`. This script also uses `__version__` for the `--version` option:

```python
# src/fava/cli.py, line 104
@click.version_option(version=__version__, prog_name="fava")
```

### 2.3. `fava_pqc_installer.spec` (PyInstaller Configuration)

The PyInstaller spec file ([`fava_pqc_installer.spec`](fava_pqc_installer.spec)) includes:
*   `pathex=['src']` ([`fava_pqc_installer.spec:83`](fava_pqc_installer.spec:83)): This allows PyInstaller to locate the `fava` package source files within the `src/` directory.
*   `hookspath=['hooks/']` ([`fava_pqc_installer.spec:139`](fava_pqc_installer.spec:139)): Specifies a directory for custom PyInstaller hooks.
*   The `datas` section ([`fava_pqc_installer.spec:54`](fava_pqc_installer.spec:54)) correctly includes Fava's templates and static assets but does not explicitly include distribution metadata (e.g., `fava.dist-info`) for the `fava` package itself.

## 3. Root Cause Analysis

The root cause of the `ImportError` is the absence of Fava's own package metadata within the PyInstaller bundle. The sequence of events is as follows:

1.  **Metadata Lookup Failure:** Inside the bundled application, when [`src/fava/__init__.py`](src/fava/__init__.py:10) is executed, `importlib.metadata.version('fava')` attempts to find the installed version of the `fava` package. Since PyInstaller, by default for source-based packages, might not include the `*.dist-info` directory (which contains this metadata), the lookup fails and `PackageNotFoundError` is raised.
2.  **`__version__` Undefined:** Due to the `with suppress(PackageNotFoundError):` block in [`src/fava/__init__.py`](src/fava/__init__.py:9), the error is caught, and program execution continues. However, the critical consequence is that the `__version__` variable is never assigned within the `fava` module's namespace.
3.  **Import Failure:** Subsequently, when [`src/fava/cli.py`](src/fava/cli.py:14) executes `from fava import __version__`, Python cannot find the name `__version__` in the `fava` module, leading to the observed `ImportError`.

This is a common issue when packaging applications that use `importlib.metadata` to determine their own version, as PyInstaller needs explicit instructions to include such metadata.

## 4. Proposed Solution & Justification

To resolve this issue, Fava's package metadata must be included in the PyInstaller bundle. The recommended approach is:

**1. Ensure Fava is "Installed" in the Build Environment:**
   For `importlib.metadata` (and PyInstaller's `copy_metadata` utility) to function correctly, the `fava` package itself should be "installed" in the Python environment where PyInstaller is executed. This can be an editable install:
   ```bash
   # From the root of the Fava project (c:/code/ChrisFava)
   pip install -e .
   ```
   This ensures that the necessary `fava.dist-info` (or `fava.egg-info`) directory is created and discoverable by packaging tools.

**2. Create a PyInstaller Hook for Fava:**
   Create a new hook file named `hook-fava.py` inside the existing `hooks/` directory (which is specified in [`fava_pqc_installer.spec:139`](fava_pqc_installer.spec:139) via `hookspath`).

   **File: `hooks/hook-fava.py`**
   ```python
   from PyInstaller.utils.hooks import copy_metadata

   # This tells PyInstaller to find and include the metadata
   # for the 'fava' package.
   datas = copy_metadata('fava')
   ```

**Justification:**
*   `copy_metadata('fava')` is the standard PyInstaller utility for collecting package distribution metadata.
*   Placing this in a hook file ensures that the metadata is included whenever the application is bundled.
*   This approach allows `importlib.metadata.version('fava')` to correctly resolve the package version at runtime within the bundled application.

## 5. Alternative Considerations (Less Ideal)

If, for some reason, installing `fava` (even editably) in the build environment is not feasible, alternatives include:
*   **Hardcoding the version:** Set `__version__ = "your_static_version"` in [`src/fava/__init__.py`](src/fava/__init__.py:10). This loses the benefit of dynamic versioning.
*   **Build-time version injection:** Modify the build process to replace a placeholder in [`src/fava/__init__.py`](src/fava/__init__.py:10) with the actual version string. This adds complexity to the build.

The hook-based approach is generally preferred for its cleanliness and integration with standard Python packaging practices.

## 6. Verification Steps (Conceptual)

After implementing the proposed solution (ensuring `fava` is installed and adding the `hook-fava.py` file):

1.  Delete any previous PyInstaller build artifacts (e.g., `build/` and `dist/` directories).
2.  Re-run the PyInstaller command using the [`fava_pqc_installer.spec`](fava_pqc_installer.spec) file.
3.  Execute the newly bundled `fava_pqc_installer.exe`.
4.  Confirm that the `ImportError` no longer occurs and the application starts as expected.
5.  Optionally, if Fava has a command like `fava_pqc_installer.exe --version`, run it to verify that the correct version is reported.

This approach should resolve the `ImportError` and allow the Fava PQC application to correctly access its version information at runtime.