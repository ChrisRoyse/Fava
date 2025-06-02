# Batch 15: CodeMirror Beancount Language Features (Autocomplete, Fold, Format)

This batch delves into the CodeMirror editor extensions specifically tailored for the Beancount language. It covers autocompletion logic, code folding for Beancount's hierarchical structure, and a command to format Beancount source code using a backend service.

## File: `frontend/src/codemirror/beancount-autocomplete.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/beancount-autocomplete.ts`](frontend/src/codemirror/beancount-autocomplete.ts:1) provides a CodeMirror `CompletionSource` for the Beancount language. This source offers context-aware autocompletion suggestions for various Beancount elements, including directives, accounts, currencies, payees, tags, and links. It leverages Svelte stores for dynamic completion options (like existing accounts or tags) and the CodeMirror syntax tree to understand the current parsing context.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Directive Lists:**
    *   `undatedDirectives` (Line [`frontend/src/codemirror/beancount-autocomplete.ts:12`](frontend/src/codemirror/beancount-autocomplete.ts:12)): Array of Beancount directives that do not require a date (e.g., "option", "plugin").
    *   `datedDirectives` (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:13-26`](frontend/src/codemirror/beancount-autocomplete.ts:13)): Array of Beancount directives that are typically preceded by a date (e.g., "open", "close", "balance", "*").

2.  **Helper Functions for Completions:**
    *   `opts(s: readonly string[]): Completion[]` (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:29-30`](frontend/src/codemirror/beancount-autocomplete.ts:29)): Maps an array of strings to an array of CodeMirror `Completion` objects (each having a `label`).
    *   `res(s: readonly string[], from: number): CompletionResult` (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:33-36`](frontend/src/codemirror/beancount-autocomplete.ts:33)): Creates a CodeMirror `CompletionResult` object from an array of strings and a starting position `from`.

3.  **`beancountCompletion: CompletionSource` (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:38-134`](frontend/src/codemirror/beancount-autocomplete.ts:38)):**
    *   This is the main exported CodeMirror completion source function. It takes a `CompletionContext` and returns a `CompletionResult` or `null`.
    *   **Contextual Logic:**
        *   **Tags (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:39-46`](frontend/src/codemirror/beancount-autocomplete.ts:39)):** If the text before the cursor matches `#<word>`, suggests tags from the `tags` Svelte store.
        *   **Links (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:48-55`](frontend/src/codemirror/beancount-autocomplete.ts:48)):** If it matches `^<word>`, suggests links from the `links` Svelte store.
        *   **Indented Accounts (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:57-65`](frontend/src/codemirror/beancount-autocomplete.ts:57)):** If the current line is indented and starts with an uppercase letter (suggesting a posting), offers accounts from the `accounts` Svelte store.
        *   **Snippets (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:67-70`](frontend/src/codemirror/beancount-autocomplete.ts:67)):** If the cursor is after a number at the start of a line (likely a date), offers `beancountSnippets()` (from [`./beancount-snippets.ts`](frontend/src/codemirror/beancount-snippets.ts:1)).
        *   **Undated Directives (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:72-79`](frontend/src/codemirror/beancount-autocomplete.ts:72)):** If at the very start of a non-empty line, suggests `undatedDirectives`.
        *   **Syntax Tree Analysis (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:81-132`](frontend/src/codemirror/beancount-autocomplete.ts:81)):**
            *   Uses `syntaxTree(context.state).resolve(context.pos, -1)` to get the syntax node immediately before the cursor.
            *   The `match(...)` helper function (Lines [`frontend/src/codemirror/beancount-autocomplete.ts:92-98`](frontend/src/codemirror/beancount-autocomplete.ts:92)) checks if the names of the current node and its preceding siblings match a given sequence of node types (e.g., "string", "flag" to suggest payees).
            *   Based on these syntax tree patterns, it provides completions for:
                *   Payees (after a transaction flag like `*` or `!`).
                *   Dated directives (after a date).
                *   Accounts (after `open`, `close`, `balance`, `pad`, `note`, `document` directives, or as a second account in a `pad` directive).
                *   Currencies (after a number, or as part of `open`, `commodity`, `price` directives).
    *   If no specific context matches, returns `null`.

**B. Data Structures:**
*   `Completion`, `CompletionResult`, `CompletionSource`, `CompletionContext` (CodeMirror types).
*   Arrays of strings for directive lists.
*   Svelte stores (`accounts`, `currencies`, `links`, `payees`, `tags`) are used as sources for completion options.

### III. Code Quality Assessment

*   **Readability & Clarity:** Moderate to Good. The initial regex-based matches are clear. The syntax tree-based matching logic (`match` function and its usage) is more complex but necessary for accurate contextual completions. Comments explaining the patterns would be beneficial.
*   **Complexity:** Moderate to High. Providing accurate, context-aware autocompletion for a structured language like Beancount involves handling many different syntactic situations. The combination of regex matching and syntax tree traversal contributes to this complexity.
*   **Maintainability:** Moderate.
    *   Adding new simple completions (like new tags/links if they weren't store-based) would be easy.
    *   Modifying or adding new syntax-tree-based completion rules requires understanding the Beancount grammar as defined for CodeMirror (likely in `beancount.ts` or a related grammar file) and how it translates to node names in the syntax tree.
    *   The reliance on specific node names (e.g., "BALANCE", "OPEN", "PAD") means changes to the underlying grammar could break these completions.
*   **Testability:** Difficult. Testing CodeMirror completion sources typically requires a CodeMirror editor instance and a way to trigger completion at specific points in a document with specific content. Asserting the correctness of suggested options and their `from` positions would be involved. Unit testing parts of the logic (like the `match` function if it were exported, or individual regexes) might be possible.
*   **Adherence to Best Practices & Idioms:**
    *   Uses CodeMirror's recommended `CompletionSource` pattern.
    *   Leverages `syntaxTree` for contextual understanding, which is more robust than purely regex-based approaches for complex grammars.
    *   Integrates with Svelte stores for dynamic completion data.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **Data Injection into Completions (Low Risk):** Completion options are primarily sourced from Svelte stores (`accounts`, `currencies`, etc.) or predefined lists. If the data in these stores could be maliciously crafted (e.g., an account name containing HTML/script characters that CodeMirror or the rendering of the completion list doesn't sanitize), it could theoretically lead to XSS in the completion dropdown. However, CodeMirror's completion rendering is generally robust, and Beancount data itself usually has a restricted character set.
*   **Secrets Management:** N/A. Completion data is not secret.
*   **Input Validation & Sanitization:** The `context.matchBefore()` regexes are fairly specific. The syntax tree provides structured input. The main concern is the integrity of data from Svelte stores.
*   **Error Handling & Logging:** The function returns `null` if no completions are found, which is standard for CodeMirror. No explicit error logging. If Svelte stores are unavailable or malformed, `store_get()` might error.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Clarity of `match` function:** The `match` function and its usage with arrays of node types could be made more readable with more descriptive variable names or comments explaining each specific pattern being checked. For example, instead of just `match("string", "flag")`, a comment like `// After a transaction string (payee/narration) and a flag (*, !)` would help.
*   **Robustness to Grammar Changes:** Tightly coupling completion logic to specific syntax node names (e.g., "BALANCE", "OPEN") makes it somewhat brittle if the Beancount grammar definition for CodeMirror changes these names. Using more abstract grammar queries or helper functions provided by the language package (if available) could improve this.
*   **Performance:** For very large Beancount files, repeated `syntaxTree(context.state)` calls could have minor performance implications, though CodeMirror is generally optimized. Extensive Svelte store lookups (`store_get()`) on each completion trigger should also be efficient as stores are typically reactive and optimized.
*   The magic numbers `1`, `4` in `tag.from + 1`, `link.from + 1`, `nodeTypesBefore[i]` are generally okay in context but worth noting.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Uses `beancountSnippets` from [`./beancount-snippets.ts`](frontend/src/codemirror/beancount-snippets.ts:1).
*   **System-Level Interactions:**
    *   **CodeMirror Libraries:**
        *   `@codemirror/autocomplete`: Uses `Completion`, `CompletionResult`, `CompletionSource`, `CompletionContext` types.
        *   `@codemirror/language`: Uses `syntaxTree`.
    *   **Svelte Stores (`../stores/index.ts`):** Reads from `accounts`, `currencies`, `links`, `payees`, `tags` stores using `get as store_get`.
    *   **CodeMirror Setup:** This `beancountCompletion` source is intended to be included in the CodeMirror editor setup (likely in [`./setup.ts`](frontend/src/codemirror/setup.ts:1) or [`./beancount.ts`](frontend/src/codemirror/beancount.ts:1)) to enable autocompletion for Beancount files.

## File: `frontend/src/codemirror/beancount-fold.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/beancount-fold.ts`](frontend/src/codemirror/beancount-fold.ts:1) provides a CodeMirror `foldService` specifically for Beancount files. This service enables code folding for sections defined by Beancount's asterisk-based header levels (e.g., `* Title`, `** Subtitle`). It allows users to collapse sections of their Beancount document to get a better overview.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`MAXDEPTH` Constant (Line [`frontend/src/codemirror/beancount-fold.ts:3`](frontend/src/codemirror/beancount-fold.ts:3)):**
    *   `const MAXDEPTH = 100;`
    *   Used as a default return value by `headerLevel` if a line is not a header, effectively meaning "no folding" or "deeper than any actual header".

2.  **`headerLevel(line: string): number` Function (Lines [`frontend/src/codemirror/beancount-fold.ts:5-8`](frontend/src/codemirror/beancount-fold.ts:5)):**
    *   Takes a line of text as input.
    *   Uses a regular expression `/^\*+/` to find a sequence of one or more asterisks at the beginning of the line.
    *   If found, returns the length of the matched asterisk sequence (e.g., `*` -> 1, `**` -> 2).
    *   If not found, returns `MAXDEPTH`.

3.  **`beancountFold` Fold Service (Lines [`frontend/src/codemirror/beancount-fold.ts:10-27`](frontend/src/codemirror/beancount-fold.ts:10)):**
    *   Registered using `foldService.of(...)`. This is the standard way to provide a folding implementation to CodeMirror.
    *   The callback function receives the editor document (`doc`), and the start (`lineStart`) and end (`lineEnd`) character offsets of the line for which folding information is being requested.
    *   **Logic:**
        1.  Gets the `startLine` object from `doc.lineAt(lineStart)`.
        2.  Determines the `level` of this `startLine` using `headerLevel()`.
        3.  If `level === MAXDEPTH` (i.e., the start line is not a header), it returns `null` (no foldable range starting here).
        4.  Initializes `end` to `startLine.to` (the end of the starting header line).
        5.  Iterates through subsequent lines (`lineNo` from `startLine.number + 1` up to `totalLines`):
            *   Gets the current `line`.
            *   If `headerLevel(line.text)` is less than or equal to the initial `level`, it means a new header of the same or higher level has been found, so the current foldable section ends *before* this line. The loop breaks.
            *   Otherwise (the current line is a sub-header or content within the section), updates `end` to `line.to` (the end of this content line).
        6.  Returns a fold range object: `{ from: lineEnd, to: end }`.
            *   `from: lineEnd`: The folding widget (e.g., triangle) is typically placed at the end of the header line. `lineEnd` is the character offset of the end of the line for which folding was requested (the header line).
            *   `to: end`: The character offset where the folded region ends.

**B. Data Structures:**
*   CodeMirror document and line objects.
*   Fold range object: `{ from: number, to: number }`.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The logic for determining header levels and iterating to find the end of a foldable section is straightforward.
*   **Complexity:** Low. It's a relatively simple line-by-line scan based on a clear pattern (asterisk prefixes).
*   **Maintainability:** High. The folding logic is self-contained and depends only on the asterisk-prefix convention for headers.
*   **Testability:** Moderate. Testing CodeMirror fold services usually involves setting up an editor state with specific content and then querying the fold ranges. The `headerLevel` function itself is easily unit-testable.
*   **Adherence to Best Practices & Idioms:**
    *   Correctly uses `foldService.of()` for registering the folding logic.
    *   The returned fold range `{ from, to }` matches CodeMirror's expectations.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **Performance with Extremely Long Sections:** If a foldable section is extremely long (many thousands of lines without a new header of the same or higher level), the `while` loop could take a noticeable time. However, for typical Beancount files, this is unlikely to be an issue. CodeMirror itself has optimizations for handling large documents.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** The input is editor content. The `headerLevel` regex is specific. No security-sensitive operations.
*   **Error Handling & Logging:** Returns `null` when no foldable range is found, as expected by CodeMirror. No explicit error logging.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **`MAXDEPTH` Usage:** The name `MAXDEPTH` might be slightly misleading as it's used as a sentinel value indicating "not a header" rather than an actual maximum depth of folding. A name like `NOT_A_HEADER_LEVEL` could be clearer, but its current usage is functional.
*   The logic correctly identifies foldable regions based on Beancount's common header convention. No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:** None.
*   **System-Level Interactions:**
    *   **CodeMirror Libraries:**
        *   `@codemirror/language`: Uses `foldService`.
    *   **CodeMirror Setup:** This `beancountFold` service is intended to be included in the CodeMirror editor setup (likely in [`./setup.ts`](frontend/src/codemirror/setup.ts:1) or [`./beancount.ts`](frontend/src/codemirror/beancount.ts:1)) to enable code folding in Beancount files.

## File: `frontend/src/codemirror/beancount-format.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/beancount-format.ts`](frontend/src/codemirror/beancount-format.ts:1) defines a CodeMirror `Command` named `beancountFormat`. This command, when executed, sends the entire content of the CodeMirror editor to a backend API endpoint (`format_source`) for formatting. Upon receiving the formatted source code, it replaces the editor's content with the result. It also includes error notification if the formatting fails.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`beancountFormat: Command` (Lines [`frontend/src/codemirror/beancount-format.ts:7-16`](frontend/src/codemirror/beancount-format.ts:7)):**
    *   A CodeMirror `Command` is a function that takes the editor view (`cm` or `target`) as an argument and typically returns `true` if it handled the command, `false` otherwise.
    *   **Functionality:**
        1.  Retrieves the entire document content using `cm.state.sliceDoc()`.
        2.  Makes an asynchronous HTTP PUT request to the `format_source` API endpoint (using `put` from `../api/index.ts`). The request body contains `{ source: <editor_content> }`.
        3.  **On Success (Promise `then` block, Lines [`frontend/src/codemirror/beancount-format.ts:9-11`](frontend/src/codemirror/beancount-format.ts:9)):**
            *   Receives the formatted `data` (presumably a string) from the API.
            *   Dispatches a CodeMirror transaction to replace the entire editor content with this `data`. It uses `replaceContents` (from [`./editor-transactions.ts`](frontend/src/codemirror/editor-transactions.ts:1)), a helper function likely designed to create the appropriate changes/transaction for a full content replacement.
        4.  **On Error (Promise `catch` block, Lines [`frontend/src/codemirror/beancount-format.ts:12-14`](frontend/src/codemirror/beancount-format.ts:12)):**
            *   Calls `notify_err` (from `../notifications.ts`) to display an error notification to the user. The error message includes details from the caught `error`.
        5.  Returns `true` to indicate the command was handled.

**B. Data Structures:**
*   `Command` (CodeMirror type).
*   Editor state and document content (strings).
*   API request/response (JSON object for request, string for response).

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The command's purpose and flow (get content, send to API, update editor or show error) are clear.
*   **Complexity:** Low. It's a straightforward asynchronous operation with success/error handling. The complexity of actual formatting is delegated to the backend.
*   **Maintainability:** High. Changes to the API endpoint or request/response structure would require updates here and in `../api/index.ts`. The core logic is simple.
*   **Testability:** Moderate to Difficult.
    *   Testing CodeMirror commands usually involves an editor instance.
    *   The API call (`put`) would need to be mocked to test the success and error paths without making actual network requests.
    *   Assertions would verify that `cm.dispatch` is called with the correct transaction on success, and `notify_err` is called on failure.
*   **Adherence to Best Practices & Idioms:**
    *   Correctly defines a CodeMirror `Command`.
    *   Uses asynchronous operations (Promises) for network requests.
    *   Separates editor interaction from the API call logic (which is in `../api/index.ts`).
    *   Provides user feedback on success (content update) and failure (notification).

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **Trust in Backend Formatter:** The primary security consideration is the trust placed in the `format_source` backend API. If the backend formatter could be compromised to return malicious content (e.g., JavaScript if the editor were ever to interpret its content as HTML, though unlikely for a plain text Beancount editor), and if that content could somehow be executed, it would be a vulnerability. However, for a text-based format like Beancount, the risk is usually that the formatter might corrupt the data or introduce syntax errors, not typically XSS within the editor itself.
    *   **Data Sent to Backend:** The entire source code is sent to the backend. If the Beancount file contains sensitive information and the backend service is not trusted or the connection is not secure (though `put` likely uses HTTPS), this could be a data exposure risk. This is inherent in using a server-side formatting tool.
*   **Secrets Management:** N/A for this frontend module. Secrets related to the API would be handled by the `put` implementation or backend.
*   **Input Validation & Sanitization:** The input is the editor's content, which is user-generated Beancount code. No specific sanitization is done here before sending to the backend; the backend formatter is responsible for handling (and hopefully preserving or correctly formatting) all valid Beancount syntax.
*   **Error Handling & Logging:** Good user-facing error handling via `notify_err`. No detailed client-side logging of the error object itself, but the notification system might handle that.
*   **Post-Quantum Security Considerations:** N/A for the formatting logic itself. Depends on the security of the HTTPS connection to the backend.

### V. Improvement Recommendations & Technical Debt

*   **User Feedback During Formatting:** The formatting is an asynchronous operation. For very large files, it might take some time. Providing immediate feedback to the user (e.g., a "Formatting..." message or a spinner) could improve the user experience, rather than the UI being unresponsive until the promise resolves.
*   **Diffing and Partial Updates:** Replacing the entire editor content (`replaceContents`) can be disruptive (e.g., losing cursor position, scroll position, selection if not carefully managed by `replaceContents`). For more sophisticated formatting integration, some editors compute a diff between the original and formatted text and apply only the necessary changes. This is significantly more complex to implement. Given this is a command, a full replacement might be acceptable.
*   No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:** None.
*   **System-Level Interactions:**
    *   **CodeMirror Libraries (`@codemirror/view`):** Uses `Command` type and interacts with the editor view (`cm`).
    *   **API Layer (`../api/index.ts`):** Uses the `put` function to make HTTP requests.
    *   **Notification System (`../notifications.ts`):** Uses `notify_err` to display errors.
    *   **Editor Transactions (`./editor-transactions.ts`):** Uses `replaceContents` to update the editor document.
    *   **CodeMirror Setup:** This `beancountFormat` command would be made available to the user, e.g., through a keybinding or a button in the editor interface, configured during CodeMirror setup.
    *   **Backend Service:** Relies on an external backend service at the `format_source` endpoint to perform the actual Beancount code formatting.
---
## Batch 16: Beancount CodeMirror Extensions (Highlighting, Indentation, Snippets)

This batch continues the examination of CodeMirror extensions for Beancount, focusing on syntax highlighting, automatic indentation, and code snippets.

## File: `frontend/src/codemirror/beancount-highlight.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/beancount-highlight.ts`](frontend/src/codemirror/beancount-highlight.ts:1) defines custom CodeMirror `HighlightStyle` rules for both Beancount editor content and Beancount Query Language (BQL). It maps specific Lezer grammar tags to CSS custom properties, allowing for themeable syntax highlighting.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`beancountEditorHighlight: HighlightStyle` (Lines [`frontend/src/codemirror/beancount-highlight.ts:4-66`](frontend/src/codemirror/beancount-highlight.ts:4)):**
    *   Defines highlighting for standard Beancount file content.
    *   Maps various `tags` from `@lezer/highlight` to specific CSS `var()` custom properties.
    *   **Examples of Mappings:**
        *   Dates (`tags.special(tags.number)`) -> `var(--editor-date)`
        *   Accounts (`tags.className`) -> `var(--editor-account)`
        *   Comments (`tags.comment`) -> `var(--editor-comment)`
        *   Sections (`tags.special(tags.lineComment)`) -> `var(--editor-comment)` with additional border and font weight.
        *   Currencies (`tags.unit`) -> `var(--editor-currencies)`
        *   Directives (`tags.keyword`) -> `var(--editor-directive)`
        *   Option names (`tags.standard(tags.string)`) -> `var(--editor-class)`
        *   Tags/Links (`tags.labelName`) -> `var(--editor-label-name)`
        *   Numbers (`tags.number`) -> `var(--editor-number)`
        *   Payees/Narrations (`tags.string`) -> `var(--editor-string)`
        *   Invalid tokens (`tags.invalid`) -> `var(--editor-invalid)` with a background color.

2.  **`beancountQueryHighlight: HighlightStyle` (Lines [`frontend/src/codemirror/beancount-highlight.ts:68-104`](frontend/src/codemirror/beancount-highlight.ts:68)):**
    *   Defines highlighting for BQL queries.
    *   Similarly maps Lezer tags to CSS custom properties specific to BQL theming.
    *   **Examples of Mappings:**
        *   Keywords (SELECT, WHERE) (`tags.keyword`) -> `var(--bql-keywords)`
        *   Values (various tags like `tags.typeName`, `tags.className`, `tags.number`) -> `var(--bql-values)`
        *   Strings (`tags.string`, etc.) -> `var(--bql-string)`
        *   Errors (various tags like `tags.name`, `tags.deleted`) -> `var(--bql-errors)`

**B. Data Structures:**
*   `HighlightStyle` (CodeMirror type).
*   Arrays of style definitions, each mapping a Lezer `tag` to CSS properties (primarily `color`, but also `fontWeight`, `border`, etc.).

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The structure is declarative and easy to understand if one is familiar with Lezer tags and CodeMirror `HighlightStyle`.
*   **Complexity:** Low. It's a mapping exercise. The complexity lies in the underlying Lezer grammar that produces these tags.
*   **Maintainability:** High. Adding or modifying styles is straightforward. Changes depend on the stability of Lezer tags and the defined CSS custom properties.
*   **Testability:** Difficult directly. Testing highlighting typically involves visual inspection or complex DOM/style assertions within an editor instance. The correctness depends on the grammar assigning the right tags.
*   **Adherence to Best Practices & Idioms:**
    *   Correctly uses `HighlightStyle.define()` from `@codemirror/language`.
    *   Leverages standard Lezer `tags` for semantic highlighting.
    *   Uses CSS custom properties for themability, which is a good practice.

### IV. Security Analysis

*   **General Vulnerabilities:** N/A. Syntax highlighting definitions do not typically introduce security vulnerabilities.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** N/A.
*   **Error Handling & Logging:** If CSS custom properties are not defined, the browser's default for that CSS property (e.g., default color) would apply, leading to incorrect or missing highlighting, but not runtime errors in this module.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Tag Specificity/Consistency:** The mapping of Lezer tags to semantic roles in Beancount/BQL is crucial. Any inconsistencies or overly broad tag usage in the grammar could lead to less precise highlighting. This is more a concern for the grammar definition than this styling module itself.
*   **Comments for BQL Tag Choices:** Some of the tag choices for BQL highlighting (e.g., `tags.deleted` for errors) might seem non-obvious without context from the BQL grammar. Brief comments explaining why certain generic tags are used for specific BQL elements could be helpful.
*   No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:** None.
*   **System-Level Interactions:**
    *   **CodeMirror Libraries:**
        *   `@codemirror/language`: Uses `HighlightStyle`.
        *   `@lezer/highlight`: Uses `tags`.
    *   **CSS Stylesheets:** Relies on CSS custom properties (e.g., `--editor-date`, `--bql-keywords`) being defined elsewhere in the application's stylesheets for the actual colors and styles to take effect.
    *   **Beancount/BQL Grammars:** The effectiveness of these highlight styles is entirely dependent on the corresponding Lezer grammars (e.g., in [`beancount.ts`](frontend/src/codemirror/beancount.ts:1), [`bql.ts`](frontend/src/codemirror/bql.ts:1)) correctly tagging tokens.
    *   **CodeMirror Setup:** These `HighlightStyle` instances would be included as extensions in the CodeMirror editor setup (e.g., in [`./setup.ts`](frontend/src/codemirror/setup.ts:1)) to apply the styling.

## File: `frontend/src/codemirror/beancount-indent.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/beancount-indent.ts`](frontend/src/codemirror/beancount-indent.ts:1) provides a CodeMirror `indentService` tailored for Beancount's typical indentation style. It aims to automatically indent lines that should be postings under a transaction or directive, while leaving top-level entries (like dated transactions or directives) unindented.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`beancountIndent: IndentService` (Lines [`frontend/src/codemirror/beancount-indent.ts:3-15`](frontend/src/codemirror/beancount-indent.ts:3)):**
    *   An `indentService` callback function that CodeMirror calls to determine the desired indentation for a line when the user presses Enter or an indentation command is invoked.
    *   **Logic:**
        1.  `textAfterPos = context.textAfterPos(pos)`: Gets the text on the current line immediately after the cursor's current position (`pos`).
        2.  **Date Check (Lines [`frontend/src/codemirror/beancount-indent.ts:5-8`](frontend/src/codemirror/beancount-indent.ts:5)):**
            *   If `textAfterPos` starts with whitespace followed by a four-digit number (e.g., `  2023`), it assumes this is a date for a new top-level entry.
            *   Returns `0` (no indentation). This handles cases where the user might be pasting or typing a new dated entry on a new line that might otherwise inherit indentation.
        3.  `line = context.state.doc.lineAt(pos)`: Gets the full content of the current line where the cursor is.
        4.  **Previous/Current Line Indent Check (Lines [`frontend/src/codemirror/beancount-indent.ts:10-13`](frontend/src/codemirror/beancount-indent.ts:10)):**
            *   Checks if the current `line.text` matches `/^\s+\S+/` (starts with one or more spaces then a non-space character, i.e., is already indented).
            *   OR, checks if `line.text` matches `/^\d\d\d\d/` (starts with a four-digit number, i.e., is a dated entry).
            *   If either is true, it implies the *next* line (created by pressing Enter) should be indented by `context.unit` (the editor's standard indentation unit, e.g., 2 spaces). This is typical for postings under a transaction.
        5.  **Default (Line [`frontend/src/codemirror/beancount-indent.ts:14`](frontend/src/codemirror/beancount-indent.ts:14)):**
            *   If none of the above conditions are met, returns `0` (no indentation).

**B. Data Structures:**
*   `IndentContext` (CodeMirror type).
*   Editor document and line objects.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The conditions for indentation are expressed with relatively simple regular expressions. Comments explain the intent.
*   **Complexity:** Low to Moderate. The logic involves a few conditional checks based on the current line's content and the text immediately following the cursor.
*   **Maintainability:** High. The indentation rules are specific to Beancount's common style and are self-contained.
*   **Testability:** Moderate. Testing indent services typically requires a CodeMirror editor instance and simulating user actions (like pressing Enter at various positions) to verify the resulting indentation. The regexes themselves could be unit-tested.
*   **Adherence to Best Practices & Idioms:**
    *   Correctly uses `indentService.of()` for registering the indentation logic.
    *   Uses `context.unit` for the indentation amount, respecting editor configuration.

### IV. Security Analysis

*   **General Vulnerabilities:** N/A. Indentation logic does not typically introduce security vulnerabilities.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** N/A.
*   **Error Handling & Logging:** No explicit error handling; the service returns an indentation level.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Clarity of Regex `??` Condition:** The condition `^\s+\S+/.exec(line.text) ?? /^\d\d\d\d/.exec(line.text)` uses the nullish coalescing operator `??`. While functional, explicitly separating these conditions with an `||` and perhaps more comments might slightly improve readability for those less familiar with `??` in this context, especially since the comment "The previous (or this one?) line was indented" refers to the outcome of this combined check. However, this is a minor point.
*   The service seems to cover common Beancount indentation scenarios well. No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:** None.
*   **System-Level Interactions:**
    *   **CodeMirror Libraries (`@codemirror/language`):** Uses `indentService` and `IndentContext`.
    *   **CodeMirror Setup:** This `beancountIndent` service would be included as an extension in the CodeMirror editor setup (e.g., in [`./setup.ts`](frontend/src/codemirror/setup.ts:1) or [`./beancount.ts`](frontend/src/codemirror/beancount.ts:1)) to enable automatic indentation.

## File: `frontend/src/codemirror/beancount-snippets.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/beancount-snippets.ts`](frontend/src/codemirror/beancount-snippets.ts:1) defines a set of code snippets for Beancount, intended to be used with CodeMirror's autocompletion feature. These snippets help users quickly insert common Beancount entry structures.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`todayAsString(): string` (Imported from `../format`):**
    *   A utility function that returns the current date formatted as a string (e.g., "YYYY-MM-DD").

2.  **`beancountSnippets: () => readonly Completion[]` Function (Lines [`frontend/src/codemirror/beancount-snippets.ts:6-16`](frontend/src/codemirror/beancount-snippets.ts:6)):**
    *   This function is called to get the list of Beancount snippets.
    *   It dynamically generates the `today` string using `todayAsString()`.
    *   Returns an array of `Completion` objects, each created using `snippetCompletion` from `@codemirror/autocomplete`.
    *   **Current Snippet:**
        *   **Template:**
            ```
            ${today} * "{}" "{}"
              Account:A  Amount
              Account:B
            ```
            (Note: `#{*}` and `#{}` are CodeMirror snippet placeholders for cursor positions/tab stops. `#{Account:A}` is a placeholder with a label.)
        *   **Label:** `${today} * transaction` (e.g., "2023-10-27 * transaction")
        *   This snippet creates a basic transaction structure with today's date, placeholders for flag, payee, narration, two account postings, and an amount.

**B. Data Structures:**
*   `Completion` (CodeMirror type).
*   Array of `Completion` objects.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The snippet definition is clear, and the use of `todayAsString` makes the dynamic date part understandable.
*   **Complexity:** Low. It defines a simple data structure (an array of snippet objects).
*   **Maintainability:** High. Adding new snippets is a matter of adding more `snippetCompletion` calls to the returned array.
*   **Testability:** Moderate. Testing snippets usually involves triggering autocompletion in a CodeMirror instance and verifying that the correct snippet is inserted and that placeholders work as expected. The `todayAsString` function itself can be unit-tested separately.
*   **Adherence to Best Practices & Idioms:**
    *   Correctly uses `snippetCompletion` for defining snippets.
    *   Making `beancountSnippets` a function allows for dynamic content (like the current date) if needed, which is a good pattern.

### IV. Security Analysis

*   **General Vulnerabilities:** N/A. Snippet definitions are static or use benign dynamic data (current date) and do not typically pose security risks.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** N/A.
*   **Error Handling & Logging:** If `todayAsString()` were to fail, it might impact snippet generation. Otherwise, no specific error handling in this module.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **More Snippets:** The file currently defines only one snippet. Expanding this with more common Beancount entries (e.g., `open`, `balance`, `price`, `option`, `plugin`, different transaction structures) would significantly enhance usability.
*   **Snippet Organization:** If the number of snippets grows large, organizing them (e.g., by category or by grouping related snippets) might be beneficial, though for a small set, a flat list is fine.
*   No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:** None directly, but `beancount-autocomplete.ts` (from Batch 15) calls `beancountSnippets()` to include these snippets in its completion results when appropriate (e.g., after typing a date at the start of a line).
*   **System-Level Interactions:**
    *   **CodeMirror Libraries (`@codemirror/autocomplete`):** Uses `Completion` and `snippetCompletion`.
    *   **Formatting Utilities (`../format.ts`):** Uses `todayAsString` to get the current date.
    *   **Autocompletion System:** These snippets are intended to be consumed by an autocompletion source (like [`beancount-autocomplete.ts`](frontend/src/codemirror/beancount-autocomplete.ts:1)) and presented to the user in the CodeMirror editor.
---
## Batch 17: Beancount Language Setup, BQL Autocomplete & Grammar

This batch focuses on the main Beancount language setup for CodeMirror, including its Tree-sitter parser integration, and then delves into the Beancount Query Language (BQL) by examining its autocompletion logic and the static grammar definitions that support it.

## File: `frontend/src/codemirror/beancount.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/beancount.ts`](frontend/src/codemirror/beancount.ts:1) is a crucial file that orchestrates the setup of the Beancount language support for CodeMirror. It integrates a Tree-sitter based parser for Beancount, along with various language-specific extensions like autocompletion, folding, formatting, highlighting, and indentation. The goal is to provide a rich editing experience for Beancount files within Fava.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Tree-sitter Parser Loading (`loadBeancountParser` function, Lines [`frontend/src/codemirror/beancount.ts:23-31`](frontend/src/codemirror/beancount.ts:23)):**
    *   Asynchronously loads the `web-tree-sitter` WASM module and the specific `tree-sitter-beancount.wasm` grammar.
    *   Initializes a `TSParser` instance and sets its language to the loaded Beancount grammar.
    *   Returns a promise that resolves to the configured `TSParser`.
    *   Uses `import.meta.resolve` to get the correct paths to WASM files, which is a modern way to handle asset paths relative to the module.

2.  **Language Facet (`beancountLanguageFacet`, Line [`frontend/src/codemirror/beancount.ts:33`](frontend/src/codemirror/beancount.ts:33)):**
    *   A CodeMirror `LanguageFacet` used to provide language-specific data and configurations.

3.  **Language Support Extensions (`beancountLanguageSupportExtensions`, Lines [`frontend/src/codemirror/beancount.ts:34-45`](frontend/src/codemirror/beancount.ts:34)):**
    *   An array of CodeMirror extensions that constitute the Beancount language support:
        *   `beancountFold` (from [`./beancount-fold.ts`](frontend/src/codemirror/beancount-fold.ts:1)): Enables code folding.
        *   `syntaxHighlighting(beancountEditorHighlight)` (from [`./beancount-highlight.ts`](frontend/src/codemirror/beancount-highlight.ts:1)): Applies syntax highlighting.
        *   `beancountIndent` (from [`./beancount-indent.ts`](frontend/src/codemirror/beancount-indent.ts:1)): Provides automatic indentation.
        *   `keymap`: Binds `Ctrl-D` (or `Meta-D` on Mac) to the `beancountFormat` command (from [`./beancount-format.ts`](frontend/src/codemirror/beancount-format.ts:1)).
        *   `beancountLanguageFacet.of(...)`: Configures language-specific features:
            *   `autocomplete: beancountCompletion` (from [`./beancount-autocomplete.ts`](frontend/src/codemirror/beancount-autocomplete.ts:1)): Sets up autocompletion.
            *   `commentTokens: { line: ";" }`: Defines ";" as the line comment character.
            *   `indentOnInput: /^\s+\d\d\d\d/`: A regex that triggers re-indentation when typed, specifically for lines starting with a date (helps ensure correct indentation after typing a date).
        *   `highlightTrailingWhitespace()`: A standard CodeMirror extension to highlight trailing whitespace.

4.  **Node Props for Highlighting (`props` array, Lines [`frontend/src/codemirror/beancount.ts:48-67`](frontend/src/codemirror/beancount.ts:48)):**
    *   Defines mappings from Tree-sitter node names (produced by the Beancount grammar) to Lezer `tags` used for syntax highlighting. This is how `beancountEditorHighlight` knows which styles to apply.
    *   Examples:
        *   `account` node -> `tags.className`
        *   `currency` node -> `tags.unit`
        *   `date` node -> `tags.special(tags.number)`
        *   Directive names (e.g., `BALANCE`, `OPEN`) -> `tags.keyword`
        *   `tag`, `link` nodes -> `tags.labelName`
    *   Also adds the `beancountLanguageFacet` to the top-level node type using `languageDataProp.add`.

5.  **Singleton Parser Loading (`load_parser` variable, Line [`frontend/src/codemirror/beancount.ts:70`](frontend/src/codemirror/beancount.ts:70)):**
    *   A module-level variable to store the promise returned by `loadBeancountParser()`, ensuring the parser is loaded only once.

6.  **`getBeancountLanguageSupport(): Promise<LanguageSupport>` Function (Lines [`frontend/src/codemirror/beancount.ts:77-89`](frontend/src/codemirror/beancount.ts:77)):**
    *   The main exported function to get the fully configured `LanguageSupport` object for Beancount.
    *   It ensures the Tree-sitter parser is loaded (or awaits its loading if already in progress) using the `load_parser` singleton.
    *   Creates a new CodeMirror `Language` instance, providing:
        *   The `beancountLanguageFacet`.
        *   A `LezerTSParser` instance (from [`./tree-sitter-parser.ts`](frontend/src/codemirror/tree-sitter-parser.ts:1)), which adapts the loaded Tree-sitter parser for use with CodeMirror's Lezer-based system, using the defined `props` for highlighting and specifying "beancount_file" as the top node name.
        *   An empty array for dialect definitions (Beancount doesn't have dialects in this context).
        *   The language name "beancount".
    *   Finally, constructs and returns a `LanguageSupport` object, combining the created `Language` with the `beancountLanguageSupportExtensions`.

**B. Data Structures:**
*   `TSParser`, `TSLanguage` (from `web-tree-sitter`).
*   `LanguageFacet`, `Language`, `LanguageSupport` (CodeMirror types).
*   Arrays of extensions and node properties.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The code is well-structured, with clear separation of concerns (parser loading, extension definitions, language setup). Comments explain key parts.
*   **Complexity:** Moderate. Integrating an external parser (Tree-sitter) with CodeMirror's Lezer system involves several moving parts and understanding of both systems' APIs. The asynchronous nature of parser loading also adds a layer of complexity.
*   **Maintainability:** Good.
    *   Adding/removing extensions is straightforward by modifying `beancountLanguageSupportExtensions`.
    *   Updating highlighting tags involves changing the `props` array.
    *   The Tree-sitter grammar (`tree-sitter-beancount.wasm`) is an external dependency; updating it would require replacing the WASM file.
*   **Testability:** Difficult. Testing the entire language support setup requires a full CodeMirror environment. Individual imported extensions (autocomplete, fold, etc.) have their own testability characteristics (analyzed previously). The parser loading logic could be tested by mocking `TSParser.init` and `TSLanguage.load`.
*   **Adherence to Best Practices & Idioms:**
    *   Correctly uses CodeMirror's `Language`, `LanguageSupport`, and `LanguageFacet` APIs.
    *   Properly handles asynchronous parser loading and ensures it's done only once.
    *   Uses `import.meta.resolve` for robust asset path resolution.
    *   The use of `LezerTSParser` is the standard way to bridge Tree-sitter parsers with CodeMirror.

### IV. Security Analysis

*   **WASM Loading and Execution:** The primary security consideration is the loading and execution of WASM modules (`tree-sitter.wasm`, `tree-sitter-beancount.wasm`). These are sourced from `node_modules` (implying they are part of the trusted build process) or locally. The integrity of these WASM files is crucial. If they were compromised, malicious code could potentially be executed within the browser's WASM sandbox.
*   **`import.meta.resolve`:** While generally safe for resolving module paths, if the build process or deployment could be manipulated to alter these paths to point to malicious WASM files, it would be a risk.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** N/A for this setup module. The parser itself handles the Beancount source code.
*   **Error Handling & Logging:** The `loadBeancountParser` function is async and returns a Promise. If `TSParser.init` or `TSLanguage.load` fails, the promise will reject. The calling code (e.g., in editor setup) should handle this potential rejection to prevent unhandled promise rejections.
*   **Post-Quantum Security Considerations:** N/A for the language setup logic itself. Depends on the security of fetching WASM assets if done over a network.

### V. Improvement Recommendations & Technical Debt

*   **Error Handling for Parser Loading:** While the promise from `loadBeancountParser` will reject on error, explicitly adding `.catch()` in `getBeancountLanguageSupport` to log or handle parser loading failures could be beneficial for debugging, though the ultimate responsibility lies with the consumer of `getBeancountLanguageSupport`.
*   **Clarity of `props` for Directives:** The string `"BALANCE CLOSE COMMODITY CUSTOM DOCUMENT EVENT NOTE OPEN PAD PRICE TRANSACTION QUERY"` in `props` is long. While functional, if more keywords were added, it might become unwieldy. This is a minor point.
*   The code is generally clean and follows modern JavaScript/TypeScript practices. No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:** None directly with `bql-autocomplete.ts` or `bql-grammar.ts` as this file sets up Beancount language support, not BQL.
*   **System-Level Interactions:**
    *   **CodeMirror Libraries:** Extensive use of `@codemirror/language`, `@codemirror/view`, `@lezer/highlight`.
    *   **Web Tree-sitter:** Uses `TSLanguage` and `TSParser` from `web-tree-sitter`.
    *   **Local WASM Files:**
        *   `../../node_modules/web-tree-sitter/tree-sitter.wasm` (core Tree-sitter engine)
        *   `./tree-sitter-beancount.wasm` (Beancount specific grammar)
    *   **Local Modules (Beancount Extensions):**
        *   [`./beancount-autocomplete.ts`](frontend/src/codemirror/beancount-autocomplete.ts:1)
        *   [`./beancount-fold.ts`](frontend/src/codemirror/beancount-fold.ts:1)
        *   [`./beancount-format.ts`](frontend/src/codemirror/beancount-format.ts:1)
        *   [`./beancount-highlight.ts`](frontend/src/codemirror/beancount-highlight.ts:1)
        *   [`./beancount-indent.ts`](frontend/src/codemirror/beancount-indent.ts:1)
    *   **Parser Adapter:**
        *   [`./tree-sitter-parser.ts`](frontend/src/codemirror/tree-sitter-parser.ts:1): `LezerTSParser` bridges Tree-sitter and Lezer.
    *   **Build System:** Relies on the build system (e.g., Vite, Webpack) to correctly handle WASM imports and `import.meta.resolve`.
    *   **Editor Setup:** The exported `getBeancountLanguageSupport` function is intended to be called by the main editor setup code (e.g., in [`./setup.ts`](frontend/src/codemirror/setup.ts:1) or a Svelte component that hosts the editor) to instantiate Beancount language features.

## File: `frontend/src/codemirror/bql-autocomplete.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/bql-autocomplete.ts`](frontend/src/codemirror/bql-autocomplete.ts:1) provides a CodeMirror `CompletionSource` for the Beancount Query Language (BQL). It offers autocompletion suggestions for BQL keywords, columns, functions, and commands, based on a predefined grammar/list of terms from [`./bql-grammar.ts`](frontend/src/codemirror/bql-grammar.ts:1).

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Grammar Import (`bqlGrammar`, Line [`frontend/src/codemirror/bql-autocomplete.ts:3`](frontend/src/codemirror/bql-autocomplete.ts:3)):**
    *   Imports `columns`, `functions`, and `keywords` arrays from [`./bql-grammar.ts`](frontend/src/codemirror/bql-grammar.ts:1).

2.  **Completion Option Generation:**
    *   `completions` (Line [`frontend/src/codemirror/bql-autocomplete.ts:7`](frontend/src/codemirror/bql-autocomplete.ts:7)): An array combining all BQL columns, functions (with an opening parenthesis appended, e.g., `sum(`), and keywords.
    *   `allCompletionOptions` (Line [`frontend/src/codemirror/bql-autocomplete.ts:8`](frontend/src/codemirror/bql-autocomplete.ts:8)): Maps the `completions` array to CodeMirror `Completion` objects (each having a `label`). These are used for general BQL autocompletion.
    *   `commands` (Lines [`frontend/src/codemirror/bql-autocomplete.ts:10-21`](frontend/src/codemirror/bql-autocomplete.ts:10)): A predefined list of top-level BQL commands (e.g., "select", "balances", "help").
    *   `firstWordCompletions` (Line [`frontend/src/codemirror/bql-autocomplete.ts:22`](frontend/src/codemirror/bql-autocomplete.ts:22)): Maps the `commands` array to `Completion` objects. These are suggested when the cursor is at the very beginning of the BQL input.

3.  **`bqlCompletion: CompletionSource` (Lines [`frontend/src/codemirror/bql-autocomplete.ts:24-33`](frontend/src/codemirror/bql-autocomplete.ts:24)):**
    *   The main exported CodeMirror completion source function.
    *   `token = context.matchBefore(/\w+/)`: Tries to match a word character sequence before the cursor.
    *   If no word is matched (`!token`), returns `null`.
    *   **First Word Context (Lines [`frontend/src/codemirror/bql-autocomplete.ts:29-31`](frontend/src/codemirror/bql-autocomplete.ts:29)):** If `token.from === 0` (the matched word starts at the beginning of the input), it returns `firstWordCompletions`.
    *   **General Context (Line [`frontend/src/codemirror/bql-autocomplete.ts:32`](frontend/src/codemirror/bql-autocomplete.ts:32)):** Otherwise, it returns `allCompletionOptions`.

**B. Data Structures:**
*   Arrays of strings (for keywords, columns, functions, commands).
*   Arrays of `Completion` objects.
*   `CompletionSource`, `CompletionContext` (CodeMirror types).

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The logic is simple and easy to follow. The separation of first-word completions from general completions is clear.
*   **Complexity:** Low. It's primarily based on matching a preceding word and offering options from predefined lists.
*   **Maintainability:** High. Adding new keywords, columns, or functions involves updating the lists in [`./bql-grammar.ts`](frontend/src/codemirror/bql-grammar.ts:1). The completion logic itself is stable.
*   **Testability:** Moderate. Testing CodeMirror completion sources typically requires an editor instance. However, the logic is simple enough that its core behavior (which list is returned based on cursor position) could be reasoned about or tested with mocked contexts.
*   **Adherence to Best Practices & Idioms:**
    *   Uses CodeMirror's `CompletionSource` pattern.
    *   `context.matchBefore(/\w+/)` is a standard way to get context for word-based completions.
    *   Separating grammar definitions ([`./bql-grammar.ts`](frontend/src/codemirror/bql-grammar.ts:1)) from completion logic is good practice.

### IV. Security Analysis

*   **General Vulnerabilities:** Low Risk. Completion options are sourced from static, predefined lists in [`./bql-grammar.ts`](frontend/src/codemirror/bql-grammar.ts:1). If these lists were somehow to include malicious strings and CodeMirror's rendering was vulnerable, there might be a theoretical XSS risk in the completion dropdown, but this is highly unlikely with standard text-based keywords.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** The `context.matchBefore()` regex is simple. No security-sensitive operations.
*   **Error Handling & Logging:** Returns `null` if no completions are appropriate, which is standard. No explicit error logging.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Contextual Awareness:** The current autocompletion is not deeply context-aware beyond the first word. For example, after typing `SELECT`, it doesn't specifically prioritize columns, or after a function name, it doesn't hint at parameters. Implementing more sophisticated contextual BQL autocompletion would require parsing the BQL input (e.g., using a Lezer grammar for BQL, as seen with `beancount.ts`). This would be a significant enhancement but also a considerable increase in complexity.
*   **Function Snippets:** For functions, simply completing `sum(` might be less helpful than providing a snippet like `sum(${expression})`. This could be achieved using `snippetCompletion`.
*   No significant technical debt for its current scope. The main "debt" is the lack of deeper contextual awareness, which is a feature limitation rather than a flaw in the current implementation.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Critically depends on [`./bql-grammar.ts`](frontend/src/codemirror/bql-grammar.ts:1) for its lists of columns, functions, and keywords.
*   **System-Level Interactions:**
    *   **CodeMirror Libraries (`@codemirror/autocomplete`):** Uses `CompletionSource`, `Completion`, `CompletionContext`.
    *   **CodeMirror Setup:** This `bqlCompletion` source would be included in the CodeMirror setup for BQL editors (e.g., in [`./bql.ts`](frontend/src/codemirror/bql.ts:1) or the query editor component) to enable BQL autocompletion.

## File: `frontend/src/codemirror/bql-grammar.ts`

### I. Overview and Purpose

[`frontend/src/codemirror/bql-grammar.ts`](frontend/src/codemirror/bql-grammar.ts:1) serves as a static data store for the Beancount Query Language (BQL). It exports an object containing lists of BQL columns, functions, and keywords. This data is primarily consumed by other CodeMirror extensions, such as BQL autocompletion ([`./bql-autocomplete.ts`](frontend/src/codemirror/bql-autocomplete.ts:1)) and potentially for syntax highlighting or validation if a more sophisticated BQL parser were implemented.

### II. Detailed Functionality

**A. Key Components & Features:**

The file exports a single default object with three main properties:

1.  **`columns: string[]` (Lines [`frontend/src/codemirror/bql-grammar.ts:2-41`](frontend/src/codemirror/bql-grammar.ts:2)):**
    *   An array of strings, where each string is a valid column name that can be used in BQL `SELECT` statements (e.g., "account", "date", "balance", "payee", "meta").
    *   Contains 39 column names.

2.  **`functions: string[]` (Lines [`frontend/src/codemirror/bql-grammar.ts:42-110`](frontend/src/codemirror/bql-grammar.ts:42)):**
    *   An array of strings, where each string is a valid BQL function name (e.g., "abs", "convert", "date_diff", "sum", "parent").
    *   Contains 68 function names.

3.  **`keywords: string[]` (Lines [`frontend/src/codemirror/bql-grammar.ts:111-140`](frontend/src/codemirror/bql-grammar.ts:111)):**
    *   An array of strings, where each string is a BQL keyword (e.g., "SELECT", "FROM", "WHERE", "GROUP", "BY", "ORDER", "AND", "OR", "TRUE", "FALSE").
    *   Contains 29 keyword names.

**B. Data Structures:**
*   A single JavaScript object with three properties, each being an array of strings.

### III. Code Quality Assessment

*   **Readability & Clarity:** Excellent. The file is purely declarative, consisting of well-formatted lists of strings.
*   **Complexity:** Very Low. It's a static data definition.
*   **Maintainability:** Very High. Adding, removing, or modifying BQL terms is a simple matter of editing the respective arrays.
*   **Testability:** Testable by importing the default export and asserting the contents/length of the arrays.
*   **Adherence to Best Practices & Idioms:**
    *   Separating static grammar data from logic (like autocompletion) is a good practice, promoting modularity.
    *   The lists appear to be alphabetically sorted, which aids in readability and finding items.

### IV. Security Analysis

*   **General Vulnerabilities:** N/A. This file contains static string data and does not perform any operations that could introduce vulnerabilities.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** N/A.
*   **Error Handling & Logging:** N/A.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Source of Truth:** It's important that these lists accurately reflect the BQL grammar supported by the Fava backend. Any discrepancies could lead to incorrect autocompletions or issues if these lists were used for validation. Regular synchronization with the backend BQL parser's capabilities would be necessary if the backend grammar evolves. This isn't technical debt in the code itself, but a maintenance consideration.
*   **Categorization of Keywords:** Keywords could potentially be further categorized (e.g., clauses, operators, boolean literals) if more granular autocompletion or syntax highlighting were desired, but for the current usage, a single list is sufficient.
*   No technical debt is apparent within the file itself.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   This file is directly imported and used by [`./bql-autocomplete.ts`](frontend/src/codemirror/bql-autocomplete.ts:1) to provide the lists of terms for autocompletion.
*   **System-Level Interactions:**
    *   **BQL Autocompletion:** As mentioned, it's a primary data source for BQL autocompletion.
    *   **Potential Future Uses:** Could be used by a BQL syntax highlighter (if not using a full Lezer grammar for BQL) or a simple client-side BQL validator, though current highlighting ([`./beancount-highlight.ts`](frontend/src/codemirror/beancount-highlight.ts:1)) uses a different approach for BQL.
    *   **Fava Backend:** Implicitly, the accuracy of these lists depends on the BQL implementation in the Fava Python backend.