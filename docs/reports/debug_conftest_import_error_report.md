# Diagnosis Report: ImportError in tests/conftest.py

**Target Feature Being Blocked:** "PQC Data at Rest"
**Date:** 2025-06-02
**Reporter:** AI Debugger (Debugger Mode)

## 1. Problem Description

An `ImportError: ModuleNotFoundError: No module named 'fava'` is encountered when running `pytest`.

-   **Error Message (Core):** `ModuleNotFoundError: No module named 'fava'`
-   **File and Line:** [`tests/conftest.py:17`](tests/conftest.py:17)
-   **Problematic Line:** `from fava.application import create_app`
-   **Context:**
    -   Tests are executed from the project root directory (`c:/code/ChrisFava`).
    -   The `fava` package is located at [`src/fava/`](src/fava/).
    -   The test execution command is, for example, `pytest tests/granular/test_pqc_data_at_rest.py`.

This error prevents tests, including those for the "PQC Data at Rest" feature, from running.

## 2. Root Cause Analysis

The root cause of the `ImportError` is that the Python interpreter, when executing tests via `pytest` from the project root, cannot find the `fava` package. Python's import system searches for modules and packages in a list of directories specified by `sys.path`.

Key factors contributing to the issue:

1.  **Project Structure:** The project follows a common `src`-layout, where the main application code (the `fava` package) resides in the [`src/`](./src/) directory. This is indicated by the `[tool.setuptools.packages.find]` section in [`pyproject.toml`](./pyproject.toml:135) which specifies `where = ["src"]`.
2.  **Execution Context:** When `pytest` is run from the project root (`c:/code/ChrisFava`), the [`src/`](./src/) directory is not automatically added to `sys.path`. Therefore, an attempt to import `fava` as a top-level package (e.g., `from fava.application import ...`) fails.
3.  **Missing Installation/Path Configuration:** The [`tests/conftest.py`](tests/conftest.py:1) file directly imports `fava.application`. For this to succeed without explicit path manipulation within the file itself, the `fava` package must be "discoverable" by Python. This typically means:
    *   The package is installed in the current Python environment (e.g., globally, in a virtual environment, or in editable mode).
    *   The directory containing the `fava` package (i.e., [`src/`](./src/)) is added to the `PYTHONPATH` environment variable.
    *   `sys.path` is programmatically modified before the import occurs.

The [`tests/conftest.py`](tests/conftest.py:1) file does not currently contain any explicit `sys.path` modifications to include the [`src/`](./src/) directory. The [`pyproject.toml`](./pyproject.toml:1) file's test dependencies include `"fava[excel]"` ([`pyproject.toml:99`](./pyproject.toml:99)), strongly suggesting that the intended setup involves installing the `fava` package itself for the test environment.

Therefore, the error occurs because the `fava` package is not installed or otherwise made available on Python's search path in the environment where `pytest` is being executed.

## 3. Proposed Solutions

Two solutions are proposed, with the first being strongly recommended as it aligns with modern Python development practices and the project's existing configuration.

### 3.1. Primary (Recommended) Solution: Install the Package in Editable Mode

This is the standard and most robust method for `src`-layout projects during development and testing. Installing the package in editable mode makes it importable as if it were normally installed, but any changes to the source code in [`src/fava/`](src/fava/) are immediately reflected without needing a reinstall.

**Action:**
Open a terminal in the project root directory (`c:/code/ChrisFava`) and run the following command:
```bash
pip install -e .
```
This command uses the [`pyproject.toml`](./pyproject.toml:1) file to set up the `fava` package correctly, making it available on `sys.path`.

**Benefits:**
-   Aligns with Python best practices for project structure and dependency management.
-   Consistent with the project's [`pyproject.toml`](./pyproject.toml:1) setup (especially the `packages.find.where = ["src"]` and the test dependency on `fava` itself).
-   Ensures that the test environment closely mirrors how the package would behave when installed by users.
-   Avoids manual `sys.path` manipulation in test files.

### 3.2. Alternative Solution: Modify `sys.path` in `tests/conftest.py` (Less Recommended)

This solution involves programmatically adding the project's [`src/`](./src/) directory to `sys.path` at the beginning of the [`tests/conftest.py`](tests/conftest.py:1) file.

**Action:**
Add the following Python code snippet to the top of your [`tests/conftest.py`](tests/conftest.py:1) file, before any imports from the `fava` package:

```python
import sys
from pathlib import Path

# Add the project's 'src' directory to sys.path to allow importing 'fava'
# This conftest.py is in tests/, so src/ is ../src/ relative to this file's parent.
project_root = Path(__file__).resolve().parent.parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Original imports from fava can now proceed
# e.g., from fava.application import create_app
```

**Benefits:**
-   Can resolve the import error with a direct code change within the test setup, without requiring an external installation step.

**Drawbacks:**
-   It's generally less clean than installing the package. The test setup might diverge from how the package is imported in other contexts (e.g., when deployed or used as a library).
-   Can sometimes mask packaging issues if not handled carefully.
-   The editable install (Solution 3.1) is the more idiomatic approach for projects structured this way.

## 4. Verification Steps

1.  **Apply the chosen solution:**
    *   For Solution 3.1: Run `pip install -e .` in the project root.
    *   For Solution 3.2: Modify [`tests/conftest.py`](tests/conftest.py:1) as described.
2.  **Re-run the tests** from the project root directory (`c:/code/ChrisFava`):
    ```bash
    pytest tests/granular/test_pqc_data_at_rest.py
    ```
    Or, to run all tests:
    ```bash
    pytest
    ```
3.  **Confirm:** The `ImportError: ModuleNotFoundError: No module named 'fava'` should no longer occur, and the tests should proceed (though other test failures might be present).

## 5. Conclusion

The `ImportError` in [`tests/conftest.py`](tests/conftest.py:1) is a common issue in Python projects with an `src`-layout when the project itself has not been made available on `sys.path`. The most robust and recommended solution is to **install the `fava` package in editable mode** using `pip install -e .`. This aligns with best practices and the project's existing `pyproject.toml` configuration, ensuring that tests run in an environment that accurately reflects an installed package.