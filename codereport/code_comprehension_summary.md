# Fava Frontend Code Comprehension Summary

This file tracks the progress of the code comprehension and quality assessment report for the Fava frontend codebase.

- Part 1: Analysis of core application initialization ([`frontend/src/main.ts`](frontend/src/main.ts)) and client-side routing ([`frontend/src/router.ts`](frontend/src/router.ts)).
- Part 1 (cont.): Analysis of WASM ambient declarations ([`frontend/src/ambient.d.ts`](frontend/src/ambient.d.ts)), an autocomplete Svelte component ([`frontend/src/AutocompleteInput.svelte`](frontend/src/AutocompleteInput.svelte)), and a clipboard utility ([`frontend/src/clipboard.ts`](frontend/src/clipboard.ts)).
- Part 1 (cont.): Analysis of document upload handling ([`frontend/src/document-upload.ts`](frontend/src/document-upload.ts)), frontend extension framework ([`frontend/src/extensions.ts`](frontend/src/extensions.ts)), and formatting utilities ([`frontend/src/format.ts`](frontend/src/format.ts)).
- Part 2: Analysis of URL helpers ([`frontend/src/helpers.ts`](frontend/src/helpers.ts)), internationalization ([`frontend/src/i18n.ts`](frontend/src/i18n.ts)), and keyboard shortcut management ([`frontend/src/keyboard-shortcuts.ts`](frontend/src/keyboard-shortcuts.ts)).
- Part 2 (cont.): Analysis of logging utilities ([`frontend/src/log.ts`](frontend/src/log.ts)), the notification system ([`frontend/src/notifications.ts`](frontend/src/notifications.ts)), and Svelte custom element rendering ([`frontend/src/svelte-custom-elements.ts`](frontend/src/svelte-custom-elements.ts)).
- Part 2 (cont.): Analysis of the API interaction layer ([`frontend/src/api/index.ts`](frontend/src/api/index.ts)) and its response validators ([`frontend/src/api/validators.ts`](frontend/src/api/validators.ts)).
- Part 2 (cont.): Analysis of chart components: D3 axis wrapper ([`frontend/src/charts/Axis.svelte`](frontend/src/charts/Axis.svelte)), bar chart data processing ([`frontend/src/charts/bar.ts`](frontend/src/charts/bar.ts)), and bar chart rendering ([`frontend/src/charts/BarChart.svelte`](frontend/src/charts/BarChart.svelte)).
### Part 3: Charting Containers, Legends, and Switching Logic

*   **File:** [`codereport/code_comprehension_report_PART_3.md`](codereport/code_comprehension_report_PART_3.md)
*   **Batch 8:**
    *   [`frontend/src/charts/Chart.svelte`](frontend/src/charts/Chart.svelte): A versatile container component that dynamically renders different types of Fava charts (Bar, Line, Hierarchy, ScatterPlot) based on the provided `FavaChart` data object. It manages chart width, integrates legends and mode switches, and allows chart visibility toggling.
    *   [`frontend/src/charts/ChartLegend.svelte`](frontend/src/charts/ChartLegend.svelte): A reusable component for displaying interactive chart legends. Supports toggling item visibility or setting an active item, with customizable color swatches.
    *   [`frontend/src/charts/ChartSwitcher.svelte`](frontend/src/charts/ChartSwitcher.svelte): Manages a collection of Fava charts, allowing users to switch between them using buttons or keyboard shortcuts. It remembers the last active chart and renders it using the `Chart.svelte` component.
*   [`frontend/src/charts/context.ts`](frontend/src/charts/context.ts): Defines the `chartContext` Svelte derived store, providing essential data (active currencies, date formatting functions) for chart parsing and rendering.
    *   [`frontend/src/charts/ConversionAndInterval.svelte`](frontend/src/charts/ConversionAndInterval.svelte): A Svelte component offering UI selectors for currency conversion strategies and time intervals, updating global stores that influence chart displays.
    *   [`frontend/src/charts/helpers.ts`](frontend/src/charts/helpers.ts): A utility module with functions for URL generation (time filter), numerical extent manipulation, axis tick filtering, HCL color generation, and pre-configured D3 ordinal color scales for charts.
*   [`frontend/src/charts/hierarchy.ts`](frontend/src/charts/hierarchy.ts): Handles data processing and D3 hierarchy preparation for treemaps, sunbursts, and icicle charts, including validation and the `HierarchyChart` class.
    *   [`frontend/src/charts/HierarchyContainer.svelte`](frontend/src/charts/HierarchyContainer.svelte): A Svelte component that dispatches to specific hierarchical chart components (Treemap, Sunburst, Icicle) based on the selected mode and data.
    *   [`frontend/src/charts/Icicle.svelte`](frontend/src/charts/Icicle.svelte): Svelte component for rendering icicle charts using D3 partition layout, including tooltips and interactions.
## Part 4: Chart Index, Line Chart Logic, and Line Chart Component

*   **Batch 11:**
    *   [`frontend/src/charts/index.ts`](frontend/src/charts/index.ts): Central dispatcher for parsing all Fava chart data, mapping chart types to specific parser functions.
    *   [`frontend/src/charts/line.ts`](frontend/src/charts/line.ts): Defines the `LineChart` class and logic for parsing balance data into line chart series, including tooltip generation.
    *   [`frontend/src/charts/LineChart.svelte`](frontend/src/charts/LineChart.svelte): Svelte component for rendering line and area charts using D3, supporting multiple series, tooltips, and mode switching.
*   [`frontend/src/charts/ModeSwitch.svelte`](frontend/src/charts/ModeSwitch.svelte): A generic Svelte component for rendering radio button-like toggles to control a store with predefined string options.
    *   [`frontend/src/charts/query-charts.ts`](frontend/src/charts/query-charts.ts): Utility to generate a `HierarchyChart` or `LineChart` from `QueryResultTable` data if it matches specific structural patterns.
    *   [`frontend/src/charts/ScatterPlot.svelte`](frontend/src/charts/ScatterPlot.svelte): Svelte component for rendering scatter plot charts using D3, typically with dates on the X-axis and categories on the Y-axis.
## Part 5: Scatter Plot Logic, Select Combobox, and Sunburst Chart

*   **Batch 13:**
    *   [`frontend/src/charts/scatterplot.ts`](frontend/src/charts/scatterplot.ts): Defines data structures (`ScatterPlotDatum`, `ScatterPlot` class) and parsing logic for scatter plot charts.
    *   [`frontend/src/charts/SelectCombobox.svelte`](frontend/src/charts/SelectCombobox.svelte): A reusable Svelte component implementing an accessible select-only combobox with ARIA attributes, keyboard navigation, and optional multi-select.
    *   [`frontend/src/charts/Sunburst.svelte`](frontend/src/charts/Sunburst.svelte): Svelte component for rendering interactive sunburst hierarchical charts using D3, displaying central text on hover and linking segments to account pages.
*   [`frontend/src/charts/tooltip.ts`](frontend/src/charts/tooltip.ts): Manages a global tooltip system with Svelte actions (`followingTooltip`, `positionedTooltip`) for chart interactions and DOM helpers for content creation.
    *   [`frontend/src/charts/Treemap.svelte`](frontend/src/charts/Treemap.svelte): Svelte component for rendering D3-based treemap charts, displaying hierarchical data as nested rectangles with tooltips and text visibility logic.
## Part 6: CodeMirror Beancount Language Features (Autocomplete, Fold, Format)

*   **File:** [`codereport/code_comprehension_report_PART_6.md`](codereport/code_comprehension_report_PART_6.md)
*   **Batch 15:**
    *   [`frontend/src/codemirror/beancount-autocomplete.ts`](frontend/src/codemirror/beancount-autocomplete.ts:1): Provides a CodeMirror `CompletionSource` for Beancount, offering context-aware autocompletion for directives, accounts, currencies, payees, tags, and links, using Svelte stores and syntax tree analysis.
    *   [`frontend/src/codemirror/beancount-fold.ts`](frontend/src/codemirror/beancount-fold.ts:1): Implements a CodeMirror `foldService` for Beancount, enabling folding of sections based on asterisk-prefixed headers.
    *   [`frontend/src/codemirror/beancount-format.ts`](frontend/src/codemirror/beancount-format.ts:1): Defines a CodeMirror `Command` (`beancountFormat`) that sends editor content to a backend API for formatting and updates the editor with the result.
*   **Batch 16:**
    *   [`frontend/src/codemirror/beancount-highlight.ts`](frontend/src/codemirror/beancount-highlight.ts:1): Defines CodeMirror `HighlightStyle` rules for Beancount editor content and BQL, mapping Lezer grammar tags to CSS custom properties for themeable syntax highlighting.
    *   [`frontend/src/codemirror/beancount-indent.ts`](frontend/src/codemirror/beancount-indent.ts:1): Provides a CodeMirror `indentService` for Beancount, automatically indenting postings under transactions/directives while leaving top-level entries unindented.
    *   [`frontend/src/codemirror/beancount-snippets.ts`](frontend/src/codemirror/beancount-snippets.ts:1): Defines Beancount code snippets for CodeMirror autocompletion, including a dynamic snippet for a new transaction with today's date.
*   **Batch 17:**
    *   [`frontend/src/codemirror/beancount.ts`](frontend/src/codemirror/beancount.ts:1): Orchestrates Beancount language support for CodeMirror, integrating a Tree-sitter parser (via WASM) and extensions for autocompletion, folding, formatting, highlighting, and indentation.
    *   [`frontend/src/codemirror/bql-autocomplete.ts`](frontend/src/codemirror/bql-autocomplete.ts:1): Provides a CodeMirror `CompletionSource` for BQL, offering suggestions for keywords, columns, functions, and commands based on definitions from `bql-grammar.ts`.
    *   [`frontend/src/codemirror/bql-grammar.ts`](frontend/src/codemirror/bql-grammar.ts:1): A static data store defining BQL columns, functions, and keywords, used primarily for BQL autocompletion.
## Part 7: BQL Stream Parser, BQL Language Setup, and Editor Transactions

*   **File:** [`codereport/code_comprehension_report_PART_7.md`](codereport/code_comprehension_report_PART_7.md)
*   **Batch 18:**
    *   [`frontend/src/codemirror/bql-stream-parser.ts`](frontend/src/codemirror/bql-stream-parser.ts:1): Defines a CodeMirror `StreamParser` for BQL, providing basic tokenization for syntax highlighting based on regexes and predefined grammar terms.
    *   [`frontend/src/codemirror/bql.ts`](frontend/src/codemirror/bql.ts:1): Sets up BQL language support for CodeMirror, integrating the `bqlStreamParser` and `bqlCompletion` for autocompletion.
    *   [`frontend/src/codemirror/editor-transactions.ts`](frontend/src/codemirror/editor-transactions.ts:1): A utility module with helper functions to create CodeMirror `TransactionSpec` objects for common editor operations like replacing content, scrolling to a line, and setting diagnostic errors.
*   **Batch 19:**
    *   [`frontend/src/codemirror/ruler.ts`](frontend/src/codemirror/ruler.ts:1): Defines a CodeMirror `ViewPlugin` to display a vertical ruler at a specified column, used for the `currency_column` in Beancount.
    *   [`frontend/src/codemirror/setup.ts`](frontend/src/codemirror/setup.ts:1): Central module for configuring various CodeMirror editor instances (Beancount, BQL, previews) with base extensions, language support, and custom features.
    *   [`frontend/src/codemirror/tree-sitter-parser.ts`](frontend/src/codemirror/tree-sitter-parser.ts:1): Implements `LezerTSParser`, an adapter to use Tree-sitter parsers (like Beancount's WASM grammar) within CodeMirror 6's Lezer parsing system, enabling incremental parsing and tree conversion.
*   **Batch 20:**
    *   [`frontend/src/editor/DeleteButton.svelte`](frontend/src/editor/DeleteButton.svelte:1): A Svelte component for a delete button with "Deleting..." visual feedback, taking `deleting` state and `onDelete` callback props.
    *   [`frontend/src/editor/DocumentPreviewEditor.svelte`](frontend/src/editor/DocumentPreviewEditor.svelte:1): A Svelte component that displays a read-only CodeMirror editor, fetching and showing document content from a given URL.
    *   [`frontend/src/editor/SaveButton.svelte`](frontend/src/editor/SaveButton.svelte:1): A Svelte component for a save button, with "Saving..." feedback, disabled state based on `changed` prop, and Control/Meta+S keyboard shortcut integration.
## Part 8: Beancount Entry Slice Editor

*   **File:** [`codereport/code_comprehension_report_PART_8.md`](codereport/code_comprehension_report_PART_8.md)
*   **Batch 21:**
    *   [`frontend/src/editor/SliceEditor.svelte`](frontend/src/editor/SliceEditor.svelte:1): A Svelte component for editing individual Beancount entry "slices" using CodeMirror, with save/delete functionality via API calls, optimistic concurrency control (SHA256 sum), and optional page reload.
*   **Batch 22:**
    *   [`frontend/src/entries/amount.ts`](frontend/src/entries/amount.ts:1): Defines an `Amount` class (number, currency) with formatting and validation.
    *   [`frontend/src/entries/cost.ts`](frontend/src/entries/cost.ts:1): Defines a `Cost` class (number, currency, optional date, optional label) with formatting and validation.
    *   [`frontend/src/entries/index.ts`](frontend/src/entries/index.ts:1): Central module for Beancount entry types (`Posting`, `Balance`, `Document`, `Event`, `Note`, `Transaction`), including an `EntryBase` class, individual validators, and a tagged union `entryValidator`.
*   **Batch 23:**
    *   [`frontend/src/entries/metadata.ts`](frontend/src/entries/metadata.ts:1): Defines the `EntryMetadata` class for managing key-value metadata (string, boolean, number) for Beancount entries/postings, with immutable update methods, string conversion helpers, and a static validator.
    *   [`frontend/src/entries/position.ts`](frontend/src/entries/position.ts:1): Defines the `Position` class, representing an `Amount` of units and an optional `Cost` basis, with a static validator.
## Part 9: Entry Form Components (Account Input, Add Metadata Button, Balance Form)

*   **File:** [`codereport/code_comprehension_report_PART_9.md`](codereport/code_comprehension_report_PART_9.md)
*   **Batch 24:**
    *   [`frontend/src/entry-forms/AccountInput.svelte`](frontend/src/entry-forms/AccountInput.svelte:1): A Svelte component wrapping `AutocompleteInput` for Beancount account names, with suggestions filtered by closed status based on a date, and validation against known accounts.
    *   [`frontend/src/entry-forms/AddMetadataButton.svelte`](frontend/src/entry-forms/AddMetadataButton.svelte:1): A simple Svelte button component that adds a new, empty key-value pair to a bound `EntryMetadata` object.
    *   [`frontend/src/entry-forms/Balance.svelte`](frontend/src/entry-forms/Balance.svelte:1): A Svelte component providing a form for Beancount `Balance` entries, including fields for date, account, amount (number/currency), and metadata, using child components for specialized inputs.
*   **Batch 25:**
    *   [`frontend/src/entry-forms/Entry.svelte`](frontend/src/entry-forms/Entry.svelte:1): A Svelte dispatcher component that renders the appropriate form (`BalanceSvelte`, `NoteSvelte`, `TransactionSvelte`) based on the type of the input `Entry` object.
    *   [`frontend/src/entry-forms/EntryMetadata.svelte`](frontend/src/entry-forms/EntryMetadata.svelte:1): A Svelte component for editing `EntryMetadata` key-value pairs, allowing modification, deletion, and addition of metadata items.
    *   [`frontend/src/entry-forms/Note.svelte`](frontend/src/entry-forms/Note.svelte:1): A Svelte component providing a form for Beancount `Note` entries, including fields for date, account, comment (textarea), and metadata.
*   **Batch 26:**
    *   [`frontend/src/entry-forms/Posting.svelte`](frontend/src/entry-forms/Posting.svelte:1): Svelte component for a single transaction posting line, with fields for account and amount, metadata editing, drag-and-drop reordering, and deletion.
    *   [`frontend/src/entry-forms/Transaction.svelte`](frontend/src/entry-forms/Transaction.svelte:1): Svelte component for the main transaction form, including date, flag, payee, narration (with tags/links), metadata, and a list of postings managed by `Posting.svelte`. Features payee-based account suggestions and transaction autofill.
## Part 10: Journal Logic, Filters, and Account Utilities

*   **File:** [`codereport/code_comprehension_report_PART_10.md`](codereport/code_comprehension_report_PART_10.md)
*   **Batch 27:**
    *   [`frontend/src/journal/index.ts`](frontend/src/journal/index.ts:1): Defines the `FavaJournal` custom HTML element, which manages journal display, mounts `JournalFilters.svelte`, handles interactive filtering (via clicks on tags, payees, metadata), and toggles entry visibility. Includes filter string manipulation helpers.
    *   [`frontend/src/journal/JournalFilters.svelte`](frontend/src/journal/JournalFilters.svelte:1): Svelte component rendering toggle buttons for filtering the journal by entry types/subtypes and aspects (metadata, postings), interacting with the `$journalShow` store.
    *   [`frontend/src/lib/account.ts`](frontend/src/lib/account.ts:1): Utility module with functions for Beancount account name manipulation (parent, leaf, ancestors, internal accounts, descendant checks).
*   **Batch 28:**
    *   [`frontend/src/lib/array.ts`](frontend/src/lib/array.ts:1): General array utilities (NonEmptyArray, move).
    *   [`frontend/src/lib/dom.ts`](frontend/src/lib/dom.ts:1): DOM utilities for reading JSON from script tags.
    *   [`frontend/src/lib/equals.ts`](frontend/src/lib/equals.ts:1): Shallow array equality check.
*   **Batch 29:**
    *   [`frontend/src/lib/errors.ts`](frontend/src/lib/errors.ts:1): Utility for formatting error messages with causes.
    *   [`frontend/src/lib/events.ts`](frontend/src/lib/events.ts:1): Custom event emitter (`Events`) and DOM event delegation (`delegate`).
    *   [`frontend/src/lib/fetch.ts`](frontend/src/lib/fetch.ts:1): Fetch API wrappers for JSON and text responses, including mtime handling.
*   **Batch 30:**
    *   [`frontend/src/lib/focus.ts`](frontend/src/lib/focus.ts:1): DOM focus management utilities.
    *   [`frontend/src/lib/fuzzy.ts`](frontend/src/lib/fuzzy.ts:1): Fuzzy string matching, filtering, and highlighting.
    *   [`frontend/src/lib/interval.ts`](frontend/src/lib/interval.ts:1): Definitions and utilities for time intervals.
### Part 11: Core Library Utilities (Continued)

*   **Batch 31:**
    *   [`frontend/src/lib/iso4217.ts`](frontend/src/lib/iso4217.ts:1): Set of ISO 4217 currency codes.
    *   [`frontend/src/lib/json.ts`](frontend/src/lib/json.ts:1): Robust JSON parsing utility using `Result` type.
    *   [`frontend/src/lib/objects.ts`](frontend/src/lib/objects.ts:1): Utility to check if an object is empty.
*   **Batch 32:**
    *   [`frontend/src/lib/paths.ts`](frontend/src/lib/paths.ts:1): Path manipulation utilities (basename, ext, documentHasAccount).
    *   [`frontend/src/lib/result.ts`](frontend/src/lib/result.ts:1): Rust-inspired `Result` type (Ok, Err) for error handling.
    *   [`frontend/src/lib/set.ts`](frontend/src/lib/set.ts:1): Utility to toggle an element in a Set.
*   **Batch 33:** `frontend/src/lib/store.ts`, `frontend/src/lib/tree.ts`, `frontend/src/lib/validation.ts` (Svelte store utilities including localStorage sync, tree stratification for accounts, comprehensive data validation library).
*   **Batch 34:** `frontend/src/modals/AddEntry.svelte`, `frontend/src/modals/Context.svelte`, `frontend/src/modals/DocumentUpload.svelte` (Modal dialogs for adding entries, viewing entry context, and uploading documents).
### Part 12: Modal Dialogs Continued

*   **Batch 35:** `frontend/src/modals/EntryContext.svelte`, `frontend/src/modals/Export.svelte`, `frontend/src/modals/ModalBase.svelte` (Modal for entry context display, export modal, and the base modal component with accessibility features).
*   **Batch 36:** `frontend/src/modals/Modals.svelte` (Modal orchestrator component that instantiates all other modals).
*   **Batch 37:** `frontend/src/reports/ReportLoadError.svelte`, `frontend/src/reports/route.svelte.ts`, `frontend/src/reports/route.ts` (Svelte component for displaying report load errors, a utility for updateable Svelte props, and the core TypeScript module for client-side report routing logic and lifecycle management).
*   **Batch 38:** `frontend/src/reports/routes.ts` (Central aggregator for all client-side rendered report route definitions).

### Part 13: Account Report Implementation

*   **File:** [`codereport/code_comprehension_report_PART_13.md`](codereport/code_comprehension_report_PART_13.md)
*   **Batch 39:** `frontend/src/reports/accounts/index.ts`, `frontend/src/reports/accounts/AccountReport.svelte` (Route definition, data loading, and Svelte component for displaying account-specific reports including journal, balances, and changes views, with chart integration).
*   **Batch 40:** `frontend/src/reports/commodities/index.ts`, `frontend/src/reports/commodities/Commodities.svelte`, `frontend/src/reports/commodities/CommodityTable.svelte` (Route definition, data loading, main Svelte component, and table sub-component for the Commodities report, including price history and chart integration).
*   **Batch 41:** `frontend/src/reports/documents/index.ts`, `frontend/src/reports/documents/stores.ts`, `frontend/src/reports/documents/Documents.svelte` (Route definition, Svelte stores, and main Svelte component for the "Documents" report, featuring a three-pane layout for account tree, document table, document preview, and move/rename functionality).

### Part 14: Documents Report - UI Panes

*   **File:** [`codereport/code_comprehension_report_PART_14.md`](codereport/code_comprehension_report_PART_14.md)
*   **Batch 42:** `frontend/src/reports/documents/Accounts.svelte`, `frontend/src/reports/documents/DocumentPreview.svelte`, `frontend/src/reports/documents/Table.svelte` (Svelte components for the "Documents" report UI: recursive account tree with drag-and-drop move support, multi-type document previewer, and a filterable/sortable document table with selection and drag initiation).
*   **Batch 43:** `frontend/src/reports/editor/AppMenu.svelte`, `frontend/src/reports/editor/AppMenuItem.svelte`, `frontend/src/reports/editor/AppMenuSubItem.svelte` (Svelte components for building a hierarchical application menu: menubar container, top-level menu items with dropdowns, and individual actionable sub-items).
*   **Batch 44:** `frontend/src/reports/editor/Editor.svelte`, `frontend/src/reports/editor/EditorMenu.svelte`, `frontend/src/reports/editor/index.ts` (Core components for the "Editor" report: the Svelte component housing the CodeMirror editor, the menu integration for editor-specific actions, and the route definition/data loading module).

### Part 15: Editor Report - Utilities and Other Reports

*   **File:** [`codereport/code_comprehension_report_PART_15.md`](codereport/code_comprehension_report_PART_15.md)
*   **Batch 45:** `frontend/src/reports/editor/Key.svelte` (A utility Svelte component for displaying keyboard shortcuts using `<kbd>` tags).
*   **Batch 46:** `frontend/src/reports/errors/Errors.svelte`, `frontend/src/reports/errors/index.ts` (The "Errors" report, displaying Beancount processing errors in a sortable table with links to source and accounts, and its dataless route definition).
*   **Batch 47:** `frontend/src/reports/events/Events.svelte`, `frontend/src/reports/events/EventTable.svelte`, `frontend/src/reports/events/index.ts` (The "Events" report, which groups events by type, displays them in sortable tables, includes a scatter plot chart, and its route definition).