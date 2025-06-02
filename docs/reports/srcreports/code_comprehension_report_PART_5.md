## Part 5: Budgets, Chart Data Generation, and Commodity Metadata

This part explores Fava's capabilities in handling budgets defined in Beancount files, generating data structures suitable for various financial charts, and managing details about commodities (like names and precisions) as defined in the ledger.

### 17. File: `src/fava/core/budgets.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** This module is responsible for parsing "budget" `Custom` directives from Beancount entries and calculating budget amounts for specified accounts and date ranges. It defines the `Budget` named tuple to represent a single budget rule and `BudgetModule` (a `FavaModule`) to manage budget data and calculations.
*   **External Dependencies:** `collections` (Counter, defaultdict), `decimal`, `typing` (NamedTuple), [`fava.core.module_base`](src/fava/core/module_base.py:1), [`fava.helpers`](src/fava/helpers.py:1), [`fava.util.date`](src/fava/util/date.py:1), [`fava.beans.abc`](src/fava/beans/abc.py:1), [`fava.core.__init__`](src/fava/core/__init__.py:1).

#### II. Detailed Functionality

##### A. `Budget(NamedTuple)`
*   **Fields:** `account: str`, `date_start: datetime.date`, `period: Interval`, `number: Decimal`, `currency: str`.

##### B. `BudgetDict = dict[str, list[Budget]]`
*   Type alias for mapping account names to lists of `Budget` entries.

##### C. `BudgetError(BeancountError)`
*   Custom error for budget parsing issues.

##### D. `BudgetModule(FavaModule)`
*   **`load_file(self) -> None`:** Parses budget `Custom` entries via `parse_budgets`.
*   **`calculate(...)`:** Calculates budget for a specific account in an interval.
*   **`calculate_children(...)`:** Calculates budget for an account and its children.

##### E. `parse_budgets(custom_entries: Sequence[Custom]) -> tuple[BudgetDict, Sequence[BudgetError]]`
*   Parses `Custom "budget"` entries (e.g., `2015-04-09 custom "budget" Expenses:Books "monthly" 20.00 EUR`) into `Budget` objects, handling errors.

##### F. `_matching_budgets(budgets: Sequence[Budget], date_active: datetime.date) -> Mapping[str, Budget]`
*   Helper to find active budget rules for an account on a specific date.

##### G. `calculate_budget(budgets: BudgetDict, ...)`
*   Calculates total budgeted amount for a single account over a date range by summing daily pro-rata portions of active budgets.

##### H. `calculate_budget_children(budgets: BudgetDict, ...)`
*   Calculates total budget for an account and its sub-accounts by summing `calculate_budget` results for each relevant child.

#### III. Code Quality Assessment
*   **Readability & Clarity:** Good.
*   **Complexity:** `calculate_budget` iterates daily, potentially intensive for very long ranges.
*   **Maintainability:** Good.
*   **Testability:** High.
*   **Adherence to Best Practices & Idioms:** Good.

#### IV. Security Analysis
*   **General Vulnerabilities:** Low risk; processes specific `Custom` entries.
*   **Input Validation & Sanitization:** `parse_budgets` handles malformed entries by creating `BudgetError`s.
*   **Post-Quantum Security Considerations:** Not applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Refactoring Opportunities:** Daily iteration in `calculate_budget` could be optimized for performance over very long periods.
*   **Technical Debt:** None apparent.

#### VI. Inter-File & System Interactions
*   `BudgetModule` is part of `FavaLedger`.
*   Consumes `Custom` directives ([`fava.beans.abc`](src/fava/beans/abc.py:1)).
*   Output used by reporting features, potentially `ChartModule`.

---

### 18. File: `src/fava/core/charts.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** The `ChartModule` generates data structures suitable for rendering various charts in Fava's web interface (hierarchy charts, interval totals, line charts, net worth). Includes custom JSON serialization.
*   **External Dependencies:** `collections` (defaultdict), `dataclasses`, `datetime`, `decimal`, `re`, `beancount.core.*`, `flask.json.provider`, `simplejson`, various `fava.beans.*`, `fava.core.*`, and `fava.util.*` modules.

#### II. Detailed Functionality

##### A. JSON Serialization Helpers:
*   **`_json_default(o: Any) -> Any`:** Custom serializer for `date`, `Amount`, `Booking`, `Position`, sets, patterns, dataclasses, `MISSING`.
*   **`dumps(...)`, `loads(...)`:** Wrappers for `simplejson` using custom default.
*   **`FavaJSONProvider(JSONProvider)`:** Flask JSON provider.

##### B. Dataclasses for Chart Data:
*   **`DateAndBalance`:** `date`, `balance: SimpleCounterInventory`.
*   **`DateAndBalanceWithBudget`:** `date`, `balance`, `account_balances`, `budgets`.

##### C. `ChartModule(FavaModule)`
*   **`hierarchy(...)`:** Generates data for hierarchical account tree charts, applying currency conversion.
*   **`interval_totals(...)`:** Calculates total balances and budgets for accounts over specified intervals (e.g., monthly bars). Handles currency conversion and optional inversion.
*   **`linechart(...)`:** Generates data for time-based line chart of an account's balance, handling currency conversion and ensuring continuity for zero balances.
*   **`net_worth(...)`:** Computes net worth (Assets + Liabilities) at interval ends, applying currency conversion.

#### III. Code Quality Assessment
*   **Readability & Clarity:** Good; some methods are dense due to aggregation logic. Dataclasses aid clarity.
*   **Complexity:** Varies by chart type; involves iteration, aggregation, and conversion.
*   **Maintainability:** Good; each chart has its own method. JSON serialization is a specific point.
*   **Testability:** High with mock ledger data.
*   **Adherence to Best Practices & Idioms:** Good use of dataclasses, iterators.

#### IV. Security Analysis
*   **General Vulnerabilities:** Risk of XSS if JSON output containing ledger strings is rendered unescaped by the frontend.
*   **Input Validation & Sanitization:** Assumes valid ledger data.
*   **Post-Quantum Security Considerations:** Not applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Refactoring Opportunities:** Long methods like `interval_totals` could be broken down.
*   **Performance Considerations:** Chart data generation can be intensive; module seems designed with this in mind.

#### VI. Inter-File & System Interactions
*   `ChartModule` is part of `FavaLedger`.
*   Uses `FilteredLedger`, `FavaLedger.prices`, `FavaLedger.budgets`, `cost_or_value`, `Tree`.
*   JSON output consumed by Fava's frontend.

---

### 19. File: `src/fava/core/commodities.py`

#### I. Overview and Purpose

*   **Primary Responsibility:** The `CommoditiesModule` extracts and stores metadata about commodities/currencies (full names, display precisions) from Beancount `Commodity` directives.
*   **External Dependencies:** `contextlib`, `decimal`, `typing`, [`fava.core.module_base`](src/fava/core/module_base.py:1), [`fava.core.__init__`](src/fava/core/__init__.py:1).

#### II. Detailed Functionality

##### A. `CommoditiesModule(FavaModule)`
*   **`__init__(...)`:** Initializes `names` (dict symbol to full name) and `precisions` (dict symbol to int precision).
*   **`load_file(self) -> None`:** Iterates `Commodity` directives, extracts "name" and "precision" from metadata, storing them. Handles potential `ValueError` for precision conversion.
*   **`name(self, commodity: str) -> str`:** Returns the full name for a commodity symbol, or the symbol itself if no name is defined.

#### III. Code Quality Assessment
*   **Readability & Clarity:** Excellent; small and focused.
*   **Complexity:** Minimal.
*   **Maintainability:** High.
*   **Testability:** High.
*   **Adherence to Best Practices & Idioms:** Good. `suppress(ValueError)` is clean.

#### IV. Security Analysis
*   **General Vulnerabilities:** Not applicable.
*   **Post-Quantum Security Considerations:** Not applicable.

#### V. Improvement Recommendations & Technical Debt
*   **Technical Debt:** None.
*   **Performance Considerations:** Excellent.

#### VI. Inter-File & System Interactions
*   `CommoditiesModule` is part of `FavaLedger`.
*   Processes `Commodity` directives ([`fava.beans.abc`](src/fava/beans/abc.py:1)).
*   Data used for display formatting throughout Fava (e.g., by number formatting modules).

---
### Batch 7 Summary: Inter-File & System Interactions

*   **[`src/fava/core/budgets.py`](src/fava/core/budgets.py:1)** (Item 17): Defines `BudgetModule` for parsing budget `Custom` entries and calculating budget values. It is instantiated by `FavaLedger` (Batch 6) and processes `Custom` directives from [`fava.beans.abc`](src/fava/beans/abc.py:1) (Batch 1). Its output is used by other Fava components, notably `ChartModule` in this batch for displaying budget comparisons.

*   **[`src/fava/core/charts.py`](src/fava/core/charts.py:1)** (Item 18): Contains `ChartModule`, responsible for generating diverse data structures for Fava's charts. As a `FavaModule`, it's managed by `FavaLedger`. It heavily relies on `FilteredLedger` (Batch 6) for accessing ledger data, `FavaLedger.prices` (for `FavaPriceMap` - Batch 4) for currency information, and the `BudgetModule` (this batch) for incorporating budget data into charts. It also uses `cost_or_value` from [`fava.core.conversion`](src/fava/core/conversion.py:1) and `Tree` from [`fava.core.tree`](src/fava/core/tree.py:1). Its JSON-serialized output is consumed by Fava's frontend.

*   **[`src/fava/core/commodities.py`](src/fava/core/commodities.py:1)** (Item 19): Features `CommoditiesModule`, which extracts metadata like full names and display precisions from `Commodity` directives. Managed by `FavaLedger`, it processes `Commodity` directives defined in [`fava.beans.abc`](src/fava/beans/abc.py:1) (Batch 1). This metadata is vital for consistent and accurate display formatting of financial figures throughout the Fava application.

This batch showcases how Fava builds higher-level financial analysis and presentation features (budgets, charts) and manages essential presentational details (commodity metadata). These modules are highly interconnected, with `ChartModule` serving as a significant consumer of data prepared by `BudgetModule`, `FavaPriceMap`, and commodity details from `CommoditiesModule`, all under the orchestration of `FavaLedger`.