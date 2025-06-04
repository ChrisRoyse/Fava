# PyInstaller Missing Files Diagnostic Report (v7)

## 1. Introduction

This report diagnoses the failure of a PyInstaller build to include critical files (`fava.dist-info`, `oqs.dll`, `pyexcel.dist-info`) in the `dist/fava_pqc_dist/` directory. This occurred after introducing a new hook, [`hooks/hook-fava.py`](hooks/hook-fava.py:1), and despite the build process exiting with code 0.

## 2. Analysis of Provided Files

*   **PyInstaller Build Log:** [`docs/devops/logs/pyinstaller_build_log_with_fava_hook.txt`](docs/devops/logs/pyinstaller_build_log_with_fava_hook.txt)
*   **PyInstaller Spec File:** [`fava_pqc_installer.spec`](fava_pqc_installer.spec)
*   **Hook Files:**
    *   [`hooks/hook-fava.py`](hooks/hook-fava.py)
    *   [`hooks/hook-pyexcel.py`](hooks/hook-pyexcel.py)
    *   [`hooks/hook-lml.py`](hooks/hook-lml.py)
    *   [`hooks/hook-pyexcel_io.py`](hooks/hook-pyexcel_io.py)
    *   Other hooks in the `hooks/` directory.
*   **PyInstaller Warnings:** [`build/fava_pqc_installer/warn-fava_pqc_installer.txt`](build/fava_pqc_installer/warn-fava_pqc_installer.txt)

## 3. Diagnosis of Missing Files

### 3.1. Missing `fava.dist-info` and `pyexcel.dist-info` (and other metadata)

**Evidence:**

*   The new [`hooks/hook-fava.py`](hooks/hook-fava.py:4) uses `datas = copy_metadata('fava')`.
*   Existing hooks like [`hooks/hook-pyexcel.py`](hooks/hook-pyexcel.py:11), [`hooks/hook-lml.py`](hooks/hook-lml.py:11), and [`hooks/hook-pyexcel_io.py`](hooks/hook-pyexcel_io.py:12) also use a similar pattern: `datas = copy_metadata('package_name')`. Some then append further data using `datas += ...`.
*   The build log shows the execution order of these hooks (lines 66, 77, 78, 79 in the log).
    1.  `hook-fava.py`
    2.  `hook-pyexcel.py`
    3.  `hook-lml.py`
    4.  `hook-pyexcel_io.py`
    (Other `pyexcel-*` hooks also exist and likely follow this pattern).

**Hypothesized Root Cause:**

The way PyInstaller collects `datas` from multiple hook files when `hookspath` is used, combined with the assignment pattern `datas = ...` in each hook, is the likely cause. While PyInstaller *should* aggregate `datas` from all hooks, the observed behavior suggests that the `datas` variable from one hook might be effectively overwritten or its contributions lost due to how the next hook re-initializes `datas` in its own scope.

If PyInstaller takes the final state of the `datas` variable from each hook script and simply concatenates them, the direct assignment `datas = copy_metadata(...)` at the beginning of each subsequent hook would mean that only the `datas` from the *last* hook performing such an assignment (or the last one in the effective processing chain) for a particular type of data would "survive" if not carefully managed.

For example:
1.  `hook-fava.py` sets `datas` (in its scope) to include `fava.dist-info`.
2.  `hook-pyexcel.py` runs. It first sets `datas = copy_metadata('pyexcel')`. If PyInstaller's aggregation isn't robust or if there's an issue with how these hook-local `datas` lists are promoted to the global `Analysis` object's `datas`, the `fava.dist-info` could be lost here.
3.  `hook-lml.py` runs and does `datas = copy_metadata('lml')`, potentially overwriting what `hook-pyexcel.py` collected.

This cascading effect would explain why metadata from earlier hooks (`fava`, `pyexcel`) is missing.

### 3.2. Missing `oqs.dll`

**Evidence:**

*   The [`fava_pqc_installer.spec`](fava_pqc_installer.spec) file correctly defines `custom_binaries` to include `oqs.dll` (lines 25-37, 84):
    ```python
    liboqs_dll_path = os.path.abspath('liboqs/build/bin/Debug/oqs.dll')
    custom_binaries.append((liboqs_dll_path, '.'))
    a = Analysis(..., binaries=custom_binaries, ...)
    ```
*   The build log confirms PyInstaller identifies this DLL early on (lines 5-6):
    `INFO: Attempting to use DLL from: C:\code\ChrisFava\liboqs\build\bin\Debug\oqs.dll`
    `INFO: Will attempt to bundle 'C:\code\ChrisFava\liboqs\build\bin\Debug\oqs.dll' as 'oqs.dll' in the bundle root directory`
*   The `COLLECT` phase in the spec uses `a.binaries` (line 175).

**Hypothesized Root Cause:**

The reason for `oqs.dll` missing is less clear-cut, as its inclusion is explicitly managed by the spec file's `binaries` list, not by the hook `datas` mechanism. Possible causes:
1.  **Issue during `COLLECT` Phase:** Although `a.binaries` is populated, an issue during the `COLLECT` step might prevent `oqs.dll` from being copied to the final distribution. This could be a subtle path issue, a file corruption, or an undocumented interaction.
2.  **UPX Interaction:** The spec file uses `upx=True` (lines 162, 179). If `oqs.dll` is incompatible with UPX compression or if UPX fails on this specific DLL, it might be silently dropped or corrupted.
3.  **Overwriting `a.binaries` (Less Likely):** While hooks typically don't modify `a.binaries` directly, if any non-standard hook or process were to re-assign `a.binaries` after the initial `Analysis` call, it could be lost. The reviewed hooks do not show this behavior.

Further investigation by inspecting `build/fava_pqc_installer/COLLECT-00.toc` is crucial for this specific file.

### 3.3. Likely Missing Fava Core Data Files (`templates`, `static`)

**Evidence:**

*   The [`fava_pqc_installer.spec`](fava_pqc_installer.spec) defines a `fava_datas` list (lines 54-61) intended to bundle Fava's templates and static assets:
    ```python
    fava_datas = [
        ('src/fava/templates', 'fava/templates'),
        ('src/fava/static', 'fava/static'),
        ('src/fava/help', 'fava/help'),
    ]
    ```
*   However, this `fava_datas` variable is **not** passed to the `datas` parameter of the `Analysis` object (line 81).
*   The [`hooks/hook-fava.py`](hooks/hook-fava.py) only adds `copy_metadata('fava')` and does not include these core Fava data directories.

**Hypothesized Root Cause:**

This is a clear oversight in the spec file. Without `fava_datas` being included in the `Analysis` object's `datas`, these essential Fava runtime files (HTML templates, JavaScript, CSS, images, WASM modules located in `src/fava/static`) will not be bundled. This would lead to runtime failures for Fava, even if the `fava.dist-info` issue were resolved.

## 4. Proposed Solutions

### 4.1. For Missing `*.dist-info` Files (Metadata)

**Recommended Approach: Centralize Metadata Collection in Spec File**

This is the most robust solution to ensure all necessary metadata is collected without relying on potentially problematic inter-hook `datas` interactions.

1.  **Modify [`fava_pqc_installer.spec`](fava_pqc_installer.spec):**
    *   Import `copy_metadata` from `PyInstaller.utils.hooks`.
    *   Create a list that aggregates metadata from all required packages.
    *   Pass this aggregated list, along with `fava_datas` (see 4.3), to the `datas` parameter of the `Analysis` constructor.

    ```python
    # At the top of the spec file, after imports
    from PyInstaller.utils.hooks import copy_metadata, collect_data_files

    # ... (keep fava_datas definition) ...

    all_metadata = []
    all_metadata.extend(copy_metadata('fava'))
    all_metadata.extend(copy_metadata('lml'))
    all_metadata.extend(copy_metadata('pyexcel'))
    all_metadata.extend(copy_metadata('pyexcel_io'))
    all_metadata.extend(copy_metadata('pyexcel_xls'))
    all_metadata.extend(copy_metadata('pyexcel_xlsx'))
    all_metadata.extend(copy_metadata('pyexcel_ods3'))
    all_metadata.extend(copy_metadata('pyexcel_text'))
    # Add any other packages for which metadata is essential

    # Combine with fava_datas and other specific data files
    # Ensure fava_datas is correctly defined as per section 3.3 / 4.3
    current_fava_datas = [
        ('src/fava/templates', 'fava/templates'),
        ('src/fava/static', 'fava/static'),
        ('src/fava/help', 'fava/help'),
    ]
    
    # Collect other specific data files that are not metadata
    pyexcel_specific_data = collect_data_files('pyexcel', include_py_files=False) # Example
    pyexcel_io_specific_data = collect_data_files('pyexcel_io', include_py_files=False) # Example

    datas_for_analysis = current_fava_datas + all_metadata + pyexcel_specific_data + pyexcel_io_specific_data
    # Add other specific_data lists as needed

    # In the Analysis call:
    a = Analysis(
        [FAVA_MAIN_SCRIPT],
        pathex=['src'],
        binaries=custom_binaries,
        datas=datas_for_analysis, # MODIFIED HERE
        hiddenimports=[...],      # Keep existing hiddenimports
        hookspath=['hooks/'],
        # ... other parameters ...
    )
    ```

2.  **Modify Hook Files (e.g., [`hooks/hook-fava.py`](hooks/hook-fava.py), [`hooks/hook-pyexcel.py`](hooks/hook-pyexcel.py), etc.):**
    *   Remove the lines `datas = copy_metadata(...)` from these hooks.
    *   The hooks should now primarily focus on `hiddenimports` or collecting data files *not* handled by `copy_metadata` (using `collect_data_files` and *appending* to `datas` if that list is already being managed robustly, or returning them for the spec file to aggregate). If the spec file handles all `datas` centrally, hooks might only need to provide `hiddenimports`.

    Example for [`hooks/hook-pyexcel.py`](hooks/hook-pyexcel.py) (if spec handles all metadata):
    ```python
    from PyInstaller.utils.hooks import collect_submodules, collect_data_files

    # If all metadata is handled by spec, this hook might only need:
    hiddenimports = collect_submodules('pyexcel')
    
    # If pyexcel has non-metadata data files not covered by spec's collect_data_files:
    # datas = collect_data_files('pyexcel', include_py_files=False) 
    # Ensure this 'datas' is appended, not assigned, if other hooks also define 'datas'.
    # Best to handle all datas in spec if possible.
    ```

### 4.2. For Missing `oqs.dll`

1.  **Inspect `COLLECT-00.toc`:** Examine the file `build/fava_pqc_installer/COLLECT-00.toc`. This Table of Contents file lists all items PyInstaller intended to include in the `COLLECT` phase. Check if `oqs.dll` (or its full path) is listed and what its destination is. This is the most critical first step.
2.  **Disable UPX Temporarily:** In [`fava_pqc_installer.spec`](fava_pqc_installer.spec), change `upx=True` to `upx=False` in both the `EXE` (line 162) and `COLLECT` (line 179) sections. Rebuild and check if `oqs.dll` is included. This will rule out UPX-related issues.
3.  **Test with Simplified Spec:** If the above doesn't help, create a minimal test spec file that only attempts to bundle `oqs.dll` with a very simple Python script. This can help isolate if the issue is with `oqs.dll` itself or an interaction within the larger Fava spec.
4.  **Verify DLL Path and Integrity:** Double-check that the path `liboqs/build/bin/Debug/oqs.dll` is correct relative to the spec file execution directory and that the DLL file itself is not corrupted and is the correct architecture (e.g., 64-bit). The log indicates it *is* found initially.

### 4.3. For Fava Core Data Files (`templates`, `static`, `help`)

1.  **Modify [`fava_pqc_installer.spec`](fava_pqc_installer.spec):**
    *   As outlined in section 4.1, ensure the `fava_datas` list (or an equivalent, like `current_fava_datas` in the example) is correctly defined and included in the `datas_for_analysis` list that is passed to the `datas` parameter of the `Analysis` object.
    ```python
    # Ensure this is defined:
    current_fava_datas = [
        ('src/fava/templates', 'fava/templates'),
        ('src/fava/static', 'fava/static'), # This includes JS, WASM, CSS, images
        ('src/fava/help', 'fava/help'),
    ]

    # And ensure it's part of the list passed to Analysis:
    # datas_for_analysis = current_fava_datas + all_metadata + ...
    # a = Analysis(..., datas=datas_for_analysis, ...)
    ```

## 5. Conclusion

The primary reasons for the missing `*.dist-info` files are likely due to the way `datas` assignments in individual hooks interact, potentially leading to data from earlier hooks being overwritten or not aggregated correctly by PyInstaller. The missing `oqs.dll` requires further specific investigation, starting with the `COLLECT-00.toc` file. A critical oversight is that Fava's own essential data files (templates, static assets) are not being bundled due to the `fava_datas` list in the spec file not being utilized in the `Analysis` call.

Implementing the proposed solutions, particularly centralizing `datas` collection in the spec file and correcting the `fava_datas` usage, should resolve the issues with metadata and Fava's core data files. Further diagnostic steps are provided for the `oqs.dll` issue.