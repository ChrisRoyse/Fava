## Part 4: Fava's Core Ledger, Account Management, and Attribute Extraction

This part delves into the heart of Fava's data management, starting with the `src/fava/core/__init__.py` which defines the central `FavaLedger` class. It also covers modules responsible for detailed account information and extracting various ledger attributes useful for UI features like auto-completion.

### 14. File: `src/fava/core/__init__.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** This module defines the `FavaLedger` class, Fava's primary in-memory representation of a Beancount ledger. It orchestrates loading Beancount data, initializes various sub-modules (for accounts, budgets, charts, etc.), provides methods for filtering entries, and offers access to ledger-wide information. It also defines `FilteredLedger` for handling filtered views and several custom Fava-specific error classes.
*   **External Dependencies:** Numerous internal Fava modules from `fava.beans.*` and `fava.core.*`, `beancount.core.inventory`, `beancount.utils.encryption`, and standard Python libraries.

#### II. Detailed Functionality

##### A. Custom Error Classes:
*   **`EntryNotFoundForHashError(FavaAPIError)`:** Entry not found for a given hash.
*   **`StatementNotFoundError(FavaAPIError)`:** Linked statement document not found.
*   **`StatementMetadataInvalidError(FavaAPIError)`:** Statement link metadata missing or invalid.

##### B. `FilteredLedger` Class
*   **Purpose:** Represents a filtered view of the main `FavaLedger`, holding a subset of entries based on account, advanced filter string, and/or time filters.
*   **`__init__(...)`:** Applies filters to `ledger.all_entries` and determines the date span of the filtered view.
*   **Key Properties & Methods:**
    *   `end_date`: End date for price lookups.
    *   `entries_with_all_prices` (`@cached_property`): Filtered entries plus all original Price directives.
    *   `root_tree` / `root_tree_closed` (`@cached_property`): `Tree` structures (account hierarchy with balances) from filtered entries, with `root_tree_closed` capped for balance sheets.
    *   `interval_ranges(...)`: Generates `DateRange` objects for specified intervals.
    *   `prices(...)`: Retrieves price data filtered by the view's date range.
    *   `account_is_closed(...)`: Checks if an account is closed within the view's end date.

##### C. `FavaLedger` Class
*   **Purpose:** Central class managing all data for a Beancount ledger.
*   **`__init__(self, path: str, ...)`:**
    *   Stores Beancount file path, checks encryption.
    *   Initializes an LRU cache for `_get_filtered`.
    *   Instantiates numerous Fava sub-modules (e.g., `AttributesModule`, `BudgetModule`, `AccountDict`, etc.), passing `self` (the `FavaLedger` instance) for data access.
    *   Initializes a file watcher.
    *   Calls `self.load_file()` for initial data load.
*   **`load_file(self) -> None`:**
    *   Uses `load_uncached` to get entries, errors, and Beancount options.
    *   Groups entries by type, initializes `FavaPriceMap`.
    *   Parses Fava-specific options.
    *   Updates file watcher.
    *   Calls `load_file()` on all sub-modules.
    *   Calls `extensions.after_load_file()`.
*   **`_get_filtered(...) -> FilteredLedger`:** Implementation for creating `FilteredLedger` instances (cached).
*   **Key Properties:**
    *   `mtime -> int`: Timestamp of the latest file change.
    *   `errors -> Sequence[BeancountError]`: Aggregated list of all loading and module errors.
    *   `root_accounts -> tuple[str, ...]`: Five main root account names.
*   **Key Methods:**
    *   `join_path(...)`: Path relative to ledger directory.
    *   `paths_to_watch(...)`: Files/directories for watcher.
    *   `changed(self) -> bool`: Checks watcher, reloads if necessary.
    *   `interval_balances(...)`: Calculates balances for an account over intervals.
    *   `account_journal(...)`: Generates journal for an account with running balances and conversion.
    *   `get_entry(...)`: Retrieves an entry by its hash.
    *   `context(...)`: Provides balances before/after an entry and source slice.
    *   `commodity_pairs(...)`: Lists commodity pairs.
    *   `statement_path(...)`: Finds path to a linked statement document.

#### III. Code Quality Assessment
*   **Readability & Clarity:** Generally good; `FavaLedger` is large but modularized internally. Type hints are crucial.
*   **Complexity:** `FavaLedger` is complex due to its orchestrating role. Caching helps performance.
*   **Maintainability:** Moderate for `FavaLedger` due to size; sub-modules improve this.
*   **Testability:** `FilteredLedger` is testable. `FavaLedger` requires more integration testing.
*   **Adherence to Best Practices & Idioms:** Good use of caching, module system, dependency injection.

#### IV. Security Analysis
*   **General Vulnerabilities:** Potential for Path Traversal if file paths are untrusted. Filter Injection if filter strings from users are not handled carefully. Relies on Beancount parser's robustness.
*   **Secrets Management:** External if file is encrypted.
*   **Input Validation & Sanitization:** Relies on Beancount for parsing; filter safety depends on filter classes.
*   **Error Handling & Logging:** Defines custom errors; aggregates errors from modules.
*   **Post-Quantum Security Considerations:** Not directly applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Refactoring Opportunities:** Consider breaking down large methods in `FavaLedger` or moving more logic to specialized modules.
*   **Potential Bugs/Edge Cases:** `type: ignore` comments need review. File system interactions.
*   **Technical Debt:** Size of `FavaLedger`. `type: ignore` comments. Untested encrypted file paths.
*   **Performance Considerations:** Loading is I/O and CPU bound. Caching is used for frequently accessed computed data.

#### VI. Inter-File & System Interactions
*   `FavaLedger` is the central Fava orchestrator.
*   Uses [`fava.beans.load`](src/fava/beans/load.py:1).
*   Initializes and uses most other `fava.core.*` modules.
*   Uses types/functions from `fava.beans.*`.

---

### 15. File: `src/fava/core/accounts.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** Defines `AccountData` to store metadata (close date, Open directive meta, up-to-date status) for individual accounts, and `AccountDict` (a `FavaModule`) to hold `AccountData` for all accounts. Includes helpers for status and balance directive generation.
*   **External Dependencies:** `dataclasses`, [`fava.beans.abc`](src/fava/beans/abc.py:1), [`fava.beans.flags`](src/fava/beans/flags.py:1), [`fava.beans.funcs`](src/fava/beans/funcs.py:1), [`fava.core.conversion`](src/fava/core/conversion.py:1), [`fava.core.group_entries`](src/fava/core/group_entries.py:1), [`fava.core.module_base`](src/fava/core/module_base.py:1), [`fava.core.tree`](src/fava/core/tree.py:1), [`fava.util.date`](src/fava/util/date.py:1).

#### II. Detailed Functionality

##### A. `get_last_entry(...) -> Directive | None`
*   **Purpose:** Finds the last significant directive for an account, ignoring unrealized gain/loss transactions.

##### B. `uptodate_status(...) -> Literal["green", "yellow", "red"] | None`
*   **Purpose:** Determines "up-to-date" status based on last entry (Balance success/fail, or Transaction).

##### C. `balance_string(tree_node: TreeNode) -> str`
*   **Purpose:** Generates Beancount `balance` directive string for today for an account's balances.

##### D. `@dataclass(frozen=True) LastEntry`
*   **Fields:** `date: datetime.date`, `entry_hash: str`.

##### E. `@dataclass AccountData`
*   **Fields:** `close_date`, `meta` (from Open), `uptodate_status`, `balance_string` (if not green), `last_entry`.

##### F. `AccountDict(FavaModule, dict[str, AccountData])`
*   **Purpose:** Maps account names to `AccountData`.
*   **`load_file(self) -> None`:** Populates itself by processing `Open` and `Close` directives and other entries to determine `last_entry`, `uptodate_status`, etc., for each account.
*   **`all_balance_directives(self) -> str`:** Concatenates suggested balance directives for accounts not 'green'.

#### III. Code Quality Assessment
*   **Readability & Clarity:** Good.
*   **Complexity:** `load_file` processes many entries but logic is understandable.
*   **Maintainability:** Good.
*   **Testability:** High.
*   **Adherence to Best Practices & Idioms:** Good use of `dataclass`, `FavaModule`.

#### IV. Security Analysis
*   **General Vulnerabilities:** Not applicable (processes internal data).
*   **Post-Quantum Security Considerations:** Not applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Technical Debt:** None apparent.
*   **Performance Considerations:** `load_file` iterates entries; acceptable as one-time cost per load.

#### VI. Inter-File & System Interactions
*   `AccountDict` is a component of `FavaLedger`.
*   Uses types from `fava.beans.*` and helpers from `fava.core.*`.
*   Data used by other Fava modules for display and filtering.

---

### 16. File: `src/fava/core/attributes.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** The `AttributesModule` extracts and ranks various ledger attributes (accounts, currencies, payees, links, tags, years) primarily for auto-completion in Fava's UI.
*   **External Dependencies:** [`fava.core.module_base`](src/fava/core/module_base.py:1), [`fava.util.date`](src/fava/util/date.py:1), [`fava.util.ranking`](src/fava/util/ranking.py:1), [`fava.beans.abc`](src/fava/beans/abc.py:1), [`fava.core.__init__`](src/fava/core/__init__.py:1).

#### II. Detailed Functionality

##### A. `get_active_years(...) -> list[str]`
*   **Purpose:** Determines active calendar or fiscal years from entries.

##### B. `AttributesModule(FavaModule)`
*   **`load_file(self) -> None`:**
    *   Extracts and sorts unique `links` and `tags`.
    *   Populates `years` using `get_active_years`.
    *   Uses `ExponentialDecayRanker` to rank `accounts`, `currencies`, and `payees` based on their occurrence and recency in transactions.
*   **`payee_accounts(self, payee: str) -> Sequence[str]`:** Ranks accounts used with a specific payee.
*   **`payee_transaction(self, payee: str) -> Transaction | None`:** Gets the last transaction for a payee.

#### III. Code Quality Assessment
*   **Readability & Clarity:** Good.
*   **Complexity:** `load_file` involves iterations and ranking; efficient for its purpose.
*   **Maintainability:** Good.
*   **Testability:** High.
*   **Adherence to Best Practices & Idioms:** Good use of `FavaModule`, `ExponentialDecayRanker`.

#### IV. Security Analysis
*   **General Vulnerabilities:** Not applicable (processes internal data).
*   **Post-Quantum Security Considerations:** Not applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Refactoring Opportunities:** Minor streamlining in `get_active_years` possible.
*   **Performance Considerations:** `load_file` iterates entries multiple times; potentially optimizable but likely acceptable.

#### VI. Inter-File & System Interactions
*   `AttributesModule` is a component of `FavaLedger`.
*   Consumes data from `FavaLedger`.
*   Its output (ranked lists) is used by Fava's UI for auto-completion and filtering.

---
### Batch 6 Summary: Inter-File & System Interactions

*   **[`src/fava/core/__init__.py`](src/fava/core/__init__.py:1)** (Item 14) defines `FavaLedger`, the central class representing the loaded Beancount ledger. It orchestrates loading via modules like [`fava.beans.load`](src/fava/beans/load.py:1) (Part 3) and initializes numerous sub-modules within `fava.core.*`, including `AccountDict` and `AttributesModule` from this batch. It also defines `FilteredLedger` for creating filtered views of the ledger data.

*   **[`src/fava/core/accounts.py`](src/fava/core/accounts.py:1)** (Item 15) introduces `AccountDict` (a `FavaModule`) and the `AccountData` structure. `FavaLedger` instantiates `AccountDict`, which then populates itself during the `load_file` phase by processing all ledger entries (especially `Open` and `Close` directives) to gather metadata, close dates, and up-to-date status for each account. This data is then accessible via `FavaLedger.accounts`.

*   **[`src/fava/core/attributes.py`](src/fava/core/attributes.py:1)** (Item 16) defines `AttributesModule` (a `FavaModule`), also instantiated and managed by `FavaLedger`. This module iterates through all ledger entries after loading to extract and rank attributes like accounts, payees, tags, links, currencies, and active years, primarily to support auto-completion features in Fava's user interface.

This batch reveals Fava's core architectural pattern: `FavaLedger` acts as a facade and coordinator, loading raw Beancount data and then delegating to specialized modules (like `AccountDict` for account-specific details and `AttributesModule` for ledger-wide attributes) to process and structure this data for various application features. These modules depend on `FavaLedger` for access to the complete set of entries and options.