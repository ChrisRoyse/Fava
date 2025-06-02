## Part 6: Currency Conversion, Document Management, and Extension System

This part delves into Fava's mechanisms for handling commodity conversions, managing document paths related to Beancount entries, and the system for loading and interacting with Fava extensions.

### 20. File: `src/fava/core/conversion.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** This module provides functions and classes for commodity conversion strategies. It defines ways to convert inventory positions to their value at cost, market value, or in units, and allows conversion to specific target currencies using price data. These functions are also intended as template filters.
*   **External Dependencies:** `abc`, [`fava.core.inventory`](src/fava/core/inventory.py:1), `typing`, `datetime`, `beancount.core.inventory`, [`fava.beans.prices`](src/fava/beans/prices.py:1), [`fava.beans.protocols`](src/fava/beans/protocols.py:1).

#### II. Detailed Functionality

##### A. Position Attribute Helpers:
*   **`get_units(pos: Position) -> Amount`:** Returns units of a `Position`.
*   **`get_cost(pos: Position) -> Amount`:** Returns total cost of a `Position`; falls back to units if no cost.

##### B. Value Calculation:
*   **`get_market_value(...) -> Amount`:** Calculates market value of a `Position` using prices, defaults to cost or units if price is unavailable.
*   **`convert_position(...) -> Amount`:** Converts a `Position` to a `target_currency`, trying direct then two-step conversion via cost currency; falls back to units.

##### C. Inventory Reduction:
*   **`simple_units(...) -> SimpleCounterInventory`:** Reduces Beancount `Inventory` to summed units per currency.
*   **`units(...) -> SimpleCounterInventory`:** Reduces Fava `CounterInventory` to summed units per currency.

##### D. `Conversion` ABC and Implementations:
*   **`Conversion(ABC)`:** Abstract base for conversion strategies.
    *   `apply(...)`: Abstract method.
*   **`_AtCostConversion`:** Converts inventory to total cost.
*   **`_AtValueConversion`:** Converts inventory to market value.
*   **`_UnitsConversion`:** Converts inventory to units.
*   **`_CurrencyConversion`:** Converts inventory to specified currency (or chain of currencies).

##### E. Predefined Instances & Factory:
*   `AT_COST`, `AT_VALUE`, `UNITS`.
*   **`conversion_from_str(value: str) -> Conversion`:** Parses string to `Conversion` object.
*   **`cost_or_value(...) -> SimpleCounterInventory`:** Main function to apply a conversion strategy to an inventory.

#### III. Code Quality Assessment
*   **Readability & Clarity:** Good; strategy pattern is clear.
*   **Complexity:** Conversion logic has conditional paths.
*   **Maintainability:** Good; new strategies are easy to add.
*   **Testability:** High.
*   **Adherence to Best Practices & Idioms:** Good use of ABCs.

#### IV. Security Analysis
*   **General Vulnerabilities:** Not applicable (internal financial calculations).
*   **Post-Quantum Security Considerations:** Not applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Refactoring Opportunities:** Clarify `get_cost` fallback.
*   **Performance Considerations:** Iterative; depends on inventory size and price lookups.

#### VI. Inter-File & System Interactions
*   Crucial for displaying aggregated values in consistent currencies.
*   Uses `FavaPriceMap` ([`fava.beans.prices`](src/fava/beans/prices.py:1)), `Position` ([`fava.beans.protocols`](src/fava/beans/protocols.py:1)), `CounterInventory` ([`fava.core.inventory`](src/fava/core/inventory.py:1)).
*   Used by reporting, charts ([`fava.core.charts`](src/fava/core/charts.py:1)), and templates.

---

### 21. File: `src/fava/core/documents.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** Provides helper functions for managing and locating document files linked to Beancount entries, including path construction and validation.
*   **External Dependencies:** `os`, `pathlib`, [`fava.helpers`](src/fava/helpers.py:1), `typing`, [`fava.core.__init__`](src/fava/core/__init__.py:1).

#### II. Detailed Functionality

##### A. Custom Error Classes:
*   **`NotADocumentsFolderError(FavaAPIError)`:** Specified folder is not a configured document folder.
*   **`NotAValidAccountError(FavaAPIError)`:** Account name for path construction is invalid.

##### B. `is_document_or_import_file(filename: str, ledger: FavaLedger) -> bool`
*   Checks if `filename` is a linked `Document` directive or within a Fava import directory.

##### C. `filepath_in_document_folder(...) -> Path`
*   Constructs a standardized absolute path for a document associated with an account within a specified documents folder.
*   Validates `documents_folder` and `account`. Sanitizes `filename` (replaces path separators with spaces).

#### III. Code Quality Assessment
*   **Readability & Clarity:** Good; custom errors are helpful.
*   **Complexity:** Low.
*   **Maintainability:** Good.
*   **Testability:** High.
*   **Adherence to Best Practices & Idioms:** Good use of `pathlib`, custom exceptions.

#### IV. Security Analysis
*   **General Vulnerabilities:** Path Traversal is a key concern if inputs to `filepath_in_document_folder` are not properly controlled upstream or if sanitization is insufficient. Validation against configured document folders and filename sanitization are important mitigations.
*   **Input Validation & Sanitization:** Validates `documents_folder`, `account`. Sanitizes `filename` for path separators.
*   **Post-Quantum Security Considerations:** Not applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Technical Debt:** None apparent.

#### VI. Inter-File & System Interactions
*   Used by Fava features for document linking and retrieval.
*   Relies on `FavaLedger` for options, document entries, and attributes.

---

### 22. File: `src/fava/core/extensions.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** Manages Fava extensions through `ExtensionModule`. Handles discovery, loading from `Custom "fava-extension"` directives, instantiation, and provides lifecycle hooks for extensions.
*   **External Dependencies:** `dataclasses`, `pathlib`, `typing`, [`fava.core.module_base`](src/fava/core/module_base.py:1), [`fava.ext`](src/fava/ext/__init__.py:1) (for base classes, errors, discovery), [`fava.beans.abc`](src/fava/beans/abc.py:1), [`fava.core.__init__`](src/fava/core/__init__.py:1).

#### II. Detailed Functionality

##### A. `@dataclass ExtensionDetails`
*   **Fields:** `name: str`, `report_title: str | None`, `has_js_module: bool`. For frontend.

##### B. `ExtensionModule(FavaModule)`
*   **`load_file(self) -> None`:**
    *   Parses `Custom "fava-extension"` entries.
    *   Uses `fava.ext.find_extensions` to locate and import extension classes.
    *   Instantiates extensions, passing `FavaLedger` and configuration. Handles errors.
*   **`extension_details` (Property):** List of `ExtensionDetails` for frontend.
*   **`get_extension(...)`:** Retrieves a loaded extension instance.
*   **Lifecycle Hook Methods:** (`after_load_file`, `before_request`, `after_entry_modified`, etc.) Iterate through loaded extensions and call corresponding methods on them. Many marked `no cover`.

#### III. Code Quality Assessment
*   **Readability & Clarity:** Good.
*   **Complexity:** `load_file` is complex due to dynamic loading and error handling.
*   **Maintainability:** Good; centralized extension management.
*   **Testability:** Requires mock extensions and `Custom` entries.
*   **Adherence to Best Practices & Idioms:** Good use of `FavaModule`, hook system.

#### IV. Security Analysis
*   **General Vulnerabilities:** **Code Execution is the primary risk.** Loading extensions from untrusted sources allows arbitrary code execution with Fava's privileges. Relies on user trust for configured extensions.
*   **Secrets Management:** Extensions might handle secrets; this module enables that possibility.
*   **Input Validation & Sanitization:** Extensions responsible for their own config validation.
*   **Error Handling & Logging:** Catches `ExtensionConfigError`; other extension errors might propagate.
*   **Post-Quantum Security Considerations:** Not applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Potential Bugs/Edge Cases:** Error handling within extension hooks. Extension state management on reloads.
*   **Technical Debt:** `pragma: no cover` on several hook dispatch loops.

#### VI. Inter-File & System Interactions
*   `ExtensionModule` is part of `FavaLedger`.
*   Parses `Custom` entries ([`fava.beans.abc`](src/fava/beans/abc.py:1)).
*   Uses `fava.ext` for discovery and base types.
*   Extensions get `FavaLedger` access, enabling broad interaction.

---
### Batch 8 Summary: Inter-File & System Interactions

*   **[`src/fava/core/conversion.py`](src/fava/core/conversion.py:1)** (Item 20): This module is central to Fava's ability to present financial data in various forms (at cost, market value, specific currencies). It defines the `Conversion` strategy pattern and provides concrete implementations. It heavily relies on `FavaPriceMap` from [`fava.beans.prices`](src/fava/beans/prices.py:1) (Batch 4) for price information and operates on `Position` objects (Batch 1/2) and `CounterInventory` (from [`fava.core.inventory`](src/fava/core/inventory.py:1), to be analyzed). Its primary function, `cost_or_value`, is widely used by other core modules like [`fava.core.charts`](src/fava/core/charts.py:1) (Batch 7) and any reporting or display logic requiring normalized monetary values.

*   **[`src/fava/core/documents.py`](src/fava/core/documents.py:1)** (Item 21): Provides utilities for managing paths related to Beancount `Document` entries. It interacts closely with `FavaLedger` (Batch 6) to access ledger options (like `documents` folders), all loaded `Document` entries (from `all_entries_by_type`), and account attributes. This module is key for features that link transactions to physical or digital documents, ensuring paths are constructed correctly and validated against the ledger's configuration.

*   **[`src/fava/core/extensions.py`](src/fava/core/extensions.py:1)** (Item 22): Defines the `ExtensionModule`, which is Fava's system for discovering, loading, and managing user-defined extensions. It parses `Custom "fava-extension"` entries (from [`fava.beans.abc`](src/fava/beans/abc.py:1) - Batch 1) to find extension configurations. It uses functionalities from the `fava.ext` package for locating and instantiating `FavaExtensionBase` subclasses. Loaded extensions are provided with the `FavaLedger` instance (Batch 6), granting them extensive access to ledger data and Fava's functionalities, and can hook into various lifecycle events.

This batch highlights Fava's capabilities in advanced data manipulation (currency conversion), auxiliary data management (document linking), and extensibility. These modules are integral to providing a rich user experience beyond basic ledger viewing, enabling sophisticated financial analysis and custom feature integration. They demonstrate a layered architecture, building upon the core ledger data and structures established in earlier analyzed modules.