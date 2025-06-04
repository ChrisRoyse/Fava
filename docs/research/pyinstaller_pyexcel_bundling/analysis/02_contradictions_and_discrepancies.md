# Contradictions and Discrepancies

During the initial data collection and pattern identification phase, few direct contradictions have emerged. However, some discrepancies in approach, emphasis, or level of detail exist, alongside areas where information is less definitive.

## 1. Specificity of `hiddenimports` for `pyexcel` Plugins

*   **Discrepancy/Varying Detail:** While the general solution of using `hiddenimports` for `pyexcel` plugins is consistently mentioned ([`01_primary_findings_part_1.md`](../data_collection/01_primary_findings_part_1.md:1)), the exact, exhaustive list of *all* necessary plugins and their sub-dependencies (e.g., `pyexcel_io.readers.csvr`, `pyexcel_xls.xlsr`, `pyexcel_xlsx`, underlying libraries like `openpyxl`, `xlwt`, `xlrd`, etc.) is not readily available as a single, definitive source. Different users report success by including different subsets, suggesting a trial-and-error approach is common.
*   **Implication:** A comprehensive list tailored to Fava PQC's specific `pyexcel` usage will likely need to be compiled through careful analysis of the Fava PQC codebase, the `pyexcel` documentation, and potentially iterative testing. The user's existing `.spec` file shows an attempt at this, but the build log indicates it's incomplete.

## 2. Effectiveness and Complexity of PyInstaller Hooks for `lml`

*   **Varying Emphasis/Lack of Specific Examples:** While PyInstaller hooks are presented as a more robust solution ([`01_primary_findings_part_2.md`](../data_collection/01_primary_findings_part_2.md:1)), concrete, widely adopted, and tested hook examples specifically for `pyexcel` interacting with `lml`'s `entry_points` or dynamic scanning are not abundant in initial findings. The provided hook examples are somewhat generic or conceptual.
*   **Discrepancy in Approach:** The most critical aspect for `lml` (if it uses `entry_points`) is likely `copy_metadata`. However, if `lml` also performs directory scanning or other dynamic behaviors, hooks might need to be more complex (e.g., replicating directory structures or using runtime hooks to adjust paths). The exact mechanism `lml` uses in `pyexcel` needs to be confirmed to tailor the hook effectively.
*   **Implication:** Developing an effective hook might require deeper investigation into `lml`'s plugin discovery mechanism within the `pyexcel` context and potentially more complex hook logic than simple `collect_submodules`.

## 3. Handling of C Extensions by Alternative Packagers

*   **Varying Claims/Focus:**
    *   Nuitka is often touted for superior C extension handling due to its compilation-to-C nature ([`02_secondary_findings_alternative_packagers_part_1.md`](../data_collection/02_secondary_findings_alternative_packagers_part_1.md:1)).
    *   cx_Freeze and Briefcase rely more on standard `setuptools` mechanisms, which can be less reliable for complex C dependencies or those with many associated non-Python files (like DLLs) ([`02_secondary_findings_alternative_packagers_part_2a_cx_freeze.md`](../data_collection/02_secondary_findings_alternative_packagers_part_2a_cx_freeze.md:1), [`02_secondary_findings_alternative_packagers_part_2b_briefcase_conclusion.md`](../data_collection/02_secondary_findings_alternative_packagers_part_2b_briefcase_conclusion.md:1)).
*   **Implication:** The "best" alternative for `oqs-python` is not definitively clear without practical testing. While Nuitka seems theoretically better, its increased build complexity is a trade-off.

## 4. Runtime Path Issues

*   **Implicit vs. Explicit:** The necessity for runtime path adjustments (e.g., via runtime hooks) for plugins is often an implicit concern. It's not always clear from initial documentation whether a library's plugins will correctly locate their data files or other dependencies once bundled, especially if PyInstaller restructures paths (e.g., `sys._MEIPASS`).
*   **Implication:** This might be a "silent failure" point that only becomes apparent during runtime testing of specific plugin functionalities. Proactive consideration in hook design (e.g., bundling data files correctly and ensuring plugins can find them) is needed.

## 5. "Best" `lml` Interaction Strategy

*   **Lack of Consensus/Clarity:** There isn't a single, clearly documented "best way" for `lml`-based plugin systems to interact with PyInstaller. Solutions often appear to be case-by-case fixes.
*   **Implication:** This research may need to synthesize a recommended approach based on understanding `lml`'s core mechanisms (entry points, scanning) and PyInstaller's capabilities (`copy_metadata`, `collect_data_files`, hooks).

These points highlight areas where further targeted research or empirical testing will be necessary to arrive at definitive solutions for the Fava PQC project.