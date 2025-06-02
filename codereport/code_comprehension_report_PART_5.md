# Batch 13: Scatter Plot Logic, Select Combobox, and Sunburst Chart Component

This batch covers the data processing logic for scatter plots, a reusable Svelte component for creating accessible select comboboxes, and the Svelte component responsible for rendering sunburst hierarchical charts.

## File: `frontend/src/charts/scatterplot.ts`

### I. Overview and Purpose

[`frontend/src/charts/scatterplot.ts`](frontend/src/charts/scatterplot.ts:1) defines the data structures and parsing logic for scatter plot charts in Fava. These charts are typically used to display events over time, where each event has a date, a type, and a description. The module provides the `ScatterPlot` class to encapsulate the chart data and a `scatterplot_validator` to ensure the input JSON conforms to the expected structure. The main factory function `scatterplot` parses raw JSON into `ScatterPlot` instances.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Type Definitions:**
    *   **`ScatterPlotDatum` (Lines [`frontend/src/charts/scatterplot.ts:6-10`](frontend/src/charts/scatterplot.ts:6)):** Represents a single data point for the scatter plot.
        *   `date: Date`: The date of the event/datum.
        *   `type: string`: The category or type of the event.
        *   `description: string`: A textual description of the event.

2.  **`ScatterPlot` Class (Lines [`frontend/src/charts/scatterplot.ts:12-19`](frontend/src/charts/scatterplot.ts:12)):**
    *   **Properties:**
        *   `type = "scatterplot"`: Identifies the chart type.
        *   `name: string | null`: An optional overall name/title for the chart (passed as `label` to the parser).
        *   `data: readonly ScatterPlotDatum[]`: An array of `ScatterPlotDatum` objects representing the points to be plotted.
    *   **Constructor (Lines [`frontend/src/charts/scatterplot.ts:15-18`](frontend/src/charts/scatterplot.ts:15)):** Initializes the `name` and `data` properties.

3.  **`scatterplot_validator` (Lines [`frontend/src/charts/scatterplot.ts:21-23`](frontend/src/charts/scatterplot.ts:21)):**
    *   A validator for the raw input JSON for scatter plot data.
    *   Expects an array of objects, where each object must conform to the `ScatterPlotDatum` structure:
        *   `type: string`
        *   `date: date` (validated as a `Date` object)
        *   `description: string`

4.  **`scatterplot(label: string | null, json: unknown)` Factory Function (Lines [`frontend/src/charts/scatterplot.ts:25-31`](frontend/src/charts/scatterplot.ts:25)):**
    *   The main parser function for "scatterplot" type charts, intended for use by [`frontend/src/charts/index.ts`](frontend/src/charts/index.ts:1).
    *   Takes a `label` (chart title) and `json` (unknown data).
    *   Validates `json` using `scatterplot_validator`.
    *   If validation is successful, it maps the validated `value` (an array of `ScatterPlotDatum`) by constructing and returning a new `ScatterPlot` instance.
    *   **Return Type:** `Result<ScatterPlot, ValidationError>`. (Note: Similar to the `balances` parser in `line.ts`, the `$chartContext` parameter from the `parsers` type in `charts/index.ts` is not explicitly used by this `scatterplot` parser).

**B. Data Structures:**
*   `ScatterPlotDatum` interface.
*   `ScatterPlot` class.
*   Input JSON structure: `Array<{ type: string, date: string, description: string }>`.

### III. Code Quality Assessment

*   **Readability & Clarity:** Excellent. The types and class are straightforward. The validator and parser function are concise and easy to understand.
*   **Complexity:** Very Low. This module is simpler than those for hierarchical or multi-series line charts, as scatter plot data is typically a flat list of points.
*   **Maintainability:** High. Changes to the `ScatterPlotDatum` structure would require updates to the interface, validator, and potentially the `ScatterPlot` class, but these are co-located and simple.
*   **Testability:** High.
    *   The `ScatterPlot` class constructor is simple to test.
    *   `scatterplot_validator` can be tested with various JSON inputs.
    *   The `scatterplot` factory function can be tested by providing JSON and checking the `Result` object and the content of the `ScatterPlot` instance.
*   **Adherence to Best Practices & Idioms:**
    *   Clear separation of data structure (`ScatterPlot` class) from parsing logic.
    *   Use of a specific validator for the input data.
    *   Returning a `Result` type from the parser function for robust error handling.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **Data Integrity:** Relies on `scatterplot_validator` to ensure the input JSON conforms to the expected structure (strings for type/description, valid dates). If malformed data bypassed validation, it could lead to issues in the rendering component ([`ScatterPlot.svelte`](frontend/src/charts/ScatterPlot.svelte:1)).
*   **Secrets Management:** N/A. Event data (dates, types, descriptions) are not secrets.
*   **Input Validation & Sanitization:** `scatterplot_validator` is the primary mechanism.
*   **Error Handling & Logging:** The `scatterplot` function returns a `Result`, allowing robust error handling by the caller. No direct logging.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **`$chartContext` Usage:** As with other simple chart parsers (like `line.ts`), the `$chartContext` parameter available in the `parsers` signature in `charts/index.ts` is not used here. This is not an issue but a point of minor inconsistency if strict adherence to a common parser signature was intended for future use.
*   No significant technical debt is apparent. The module is clean and focused.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   The `ScatterPlot` class and `ScatterPlotDatum` type are consumed by [`ScatterPlot.svelte`](frontend/src/charts/ScatterPlot.svelte:1) (analyzed in Batch 12).
    *   This module's `scatterplot` parser is registered in [`frontend/src/charts/index.ts`](frontend/src/charts/index.ts:1) (analyzed in Batch 11).
*   **System-Level Interactions:**
    *   **Result Library (`../lib/result`):** Uses `Result` type.
    *   **Validation Library (`../lib/validation`):** Uses `ValidationError`, `array`, `date`, `object`, `string`.
    *   **Rendering Component:** The `ScatterPlot` objects are primarily intended for rendering by [`ScatterPlot.svelte`](frontend/src/charts/ScatterPlot.svelte:1).

## File: `frontend/src/charts/SelectCombobox.svelte`

### I. Overview and Purpose

[`frontend/src/charts/SelectCombobox.svelte`](frontend/src/charts/SelectCombobox.svelte:1) is a reusable Svelte component that implements an accessible "select-only" combobox pattern. This pattern provides a dropdown list of options from which a user can select one or, optionally, multiple values. The component is designed with ARIA (Accessible Rich Internet Applications) attributes to ensure it's usable with assistive technologies. It manages its own internal state for UI interactions (like whether the dropdown is open and which item is focused) and binds its selected `value` to a Svelte store or prop provided by the parent. It supports keyboard navigation, type-to-find, and optional multi-selection logic.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/SelectCombobox.svelte:18-27`](frontend/src/charts/SelectCombobox.svelte:18), Usage Lines [`frontend/src/charts/SelectCombobox.svelte:29-34`](frontend/src/charts/SelectCombobox.svelte:29)):**
    *   `value: string = $bindable()`: The currently selected value (or comma-separated string of values if multi-select is active). This is a two-way bindable prop.
    *   `options: readonly string[]`: An array of available option strings (the raw values).
    *   `description: (option: string) => string`: A function that takes an option string (or the current `value` string) and returns its human-readable display text.
    *   `multiple_select?: (option: string) => boolean`: An optional function. If provided, it determines if a given `option` can be part of a multi-selection. If an option is selected for which this returns `true`, and all currently selected `values` also satisfy this, the new option is added/removed from a comma-separated list in `value`. Otherwise, selection replaces the current `value`.

2.  **Internal State:**
    *   `hidden = $state(true)` (Line [`frontend/src/charts/SelectCombobox.svelte:37`](frontend/src/charts/SelectCombobox.svelte:37)): Boolean indicating if the dropdown list is hidden.
    *   `index = $state(options.indexOf(value))` (Line [`frontend/src/charts/SelectCombobox.svelte:39`](frontend/src/charts/SelectCombobox.svelte:39)): The numerical index of the currently focused/active option in the `options` array. Initialized based on the initial `value`.
    *   `ul: HTMLUListElement | undefined = $state()` (Line [`frontend/src/charts/SelectCombobox.svelte:41`](frontend/src/charts/SelectCombobox.svelte:41)): A reference to the `<ul>` DOM element for the dropdown list, used for scrolling.
    *   `uid = $props.id()` (Line [`frontend/src/charts/SelectCombobox.svelte:43`](frontend/src/charts/SelectCombobox.svelte:43)): A unique ID generated for ARIA attribute linking.
    *   `listbox_id = \`combobox-listbox-${uid.toString()}\`` (Line [`frontend/src/charts/SelectCombobox.svelte:44`](frontend/src/charts/SelectCombobox.svelte:44)): ID for the listbox element.
    *   `SEPARATOR = ","` (Line [`frontend/src/charts/SelectCombobox.svelte:46`](frontend/src/charts/SelectCombobox.svelte:46)): Constant for multi-select value joining.
    *   `values = $derived(value.split(SEPARATOR))` (Line [`frontend/src/charts/SelectCombobox.svelte:47`](frontend/src/charts/SelectCombobox.svelte:47)): An array of currently selected values, derived by splitting the `value` prop (for multi-select).

3.  **`$effect` for Scrolling (Lines [`frontend/src/charts/SelectCombobox.svelte:50-57`](frontend/src/charts/SelectCombobox.svelte:50)):**
    *   An effect that runs when `hidden` or `index` changes. If the list is not hidden and an `index` is set, it scrolls the `ul` element so that the list item at `children[index]` is visible.

4.  **`actions` Object (Lines [`frontend/src/charts/SelectCombobox.svelte:60-119`](frontend/src/charts/SelectCombobox.svelte:60)):**
    *   A collection of methods to handle user interactions:
        *   `close()`: Hides the dropdown.
        *   `find_letter(key, event)`: Finds the first option starting with `key` and focuses it. Opens dropdown if hidden.
        *   `first()`: Focuses the first option. Opens dropdown.
        *   `last()`: Focuses the last option. (Mistake here: `index = 0;` should be `index = options.length - 1;`) Opens dropdown.
        *   `next()`: Focuses the next option (wraps around).
        *   `open()`: Shows the dropdown.
        *   `previous()`: Focuses the previous option (wraps around).
        *   `select(o?)`: Selects the given option `o` or the currently focused option. Handles single vs. multi-select logic based on `multiple_select` prop. Updates `value` and `index`, then closes the dropdown.
        *   `toggle()`: Toggles the visibility of the dropdown.

5.  **`key_action(event: KeyboardEvent)` Function (Lines [`frontend/src/charts/SelectCombobox.svelte:122-148`](frontend/src/charts/SelectCombobox.svelte:122)):**
    *   Maps keyboard events (`key` property) to corresponding methods in the `actions` object. Handles:
        *   Alphanumeric keys for `find_letter`.
        *   Home/End keys for `first`/`last`.
        *   Enter/Space (when dropdown open) for `select`.
        *   Escape (when dropdown open) for `close`.
        *   ArrowUp/ArrowDown for `next`/`previous` or `open`.

6.  **Rendering Logic (Lines [`frontend/src/charts/SelectCombobox.svelte:151-186`](frontend/src/charts/SelectCombobox.svelte:151)):**
    *   A root `<span>` element.
    *   A `<button type="button">` that acts as the combobox trigger:
        *   `role="combobox"`, `aria-expanded={!hidden}`, `aria-controls={listbox_id}` for ARIA.
        *   `class="muted"` (likely a general button style).
        *   `onclick={actions.toggle}`.
        *   `onblur={actions.close}`: Closes dropdown when button loses focus (important for accessibility and usability).
        *   `onkeydown`: Calls `key_action` to handle keyboard navigation.
        *   Displays `description(value)` as its text content.
    *   An `<ul>` element for the dropdown list:
        *   `hidden` attribute bound to the `hidden` state.
        *   `role="listbox"`, `id={listbox_id}` for ARIA.
        *   `bind:this={ul}` to get a reference to the DOM element.
        *   Iterates through `options` (`#each options as option, i`):
            *   Renders an `<li>` for each option.
            *   `role="option"`, `aria-selected={values.includes(option)}` for ARIA.
            *   `class:current={i === index}` to highlight the focused item.
            *   `onmousedown`: Calls `actions.select(option)` if left mouse button. This handles mouse selection.
            *   Displays `description(option)` as its text content.

7.  **Styling (`<style>` block Lines [`frontend/src/charts/SelectCombobox.svelte:188-225`](frontend/src/charts/SelectCombobox.svelte:188)):**
    *   Styles for positioning the `<ul>` absolutely below the button.
    *   Styles for list items, including hover and "current" (focused) states.
    *   Print styles to hide the combobox.

**B. Data Structures:**
*   `string` for `value` (potentially comma-separated).
*   `readonly string[]` for `options`.
*   Functions for `description` and `multiple_select`.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The component follows the ARIA combobox pattern, and the comments explain this. The `actions` object centralizes interaction logic. Svelte 5 runes (`$props`, `$state`, `$derived`, `$bindable`, `$effect`) are used.
*   **Complexity:** Moderate to High. Implementing a fully accessible combobox with keyboard navigation, focus management, optional multi-select, and ARIA attributes involves significant state and event handling logic.
*   **Maintainability:** Moderate. The core logic is complex but well-organized. Changes to ARIA requirements or specific interaction behaviors would need careful updates.
*   **Testability:** Difficult. Thorough testing would require:
    *   A Svelte component testing environment that can simulate user events (mouse clicks, key presses, focus/blur).
    *   Testing all keyboard navigation paths.
    *   Verifying ARIA attributes are correctly set and updated.
    *   Testing single and multi-select functionality with different `options` and `multiple_select` function behaviors.
    *   Checking scroll-into-view behavior.
*   **Adherence to Best Practices & Idioms:**
    *   Good attempt to follow ARIA APG for comboboxes, which is crucial for accessibility.
    *   Use of `bind:this` for DOM element reference.
    *   Separation of interaction logic into an `actions` object.
    *   Use of Svelte's reactivity for state management.
    *   The `onblur={actions.close}` on the button is important for closing the dropdown when focus moves away.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data (Low Risk):**
        *   `description(value)` and `description(option)` are rendered as text content (Lines [`frontend/src/charts/SelectCombobox.svelte:168`](frontend/src/charts/SelectCombobox.svelte:168), [`frontend/src/charts/SelectCombobox.svelte:182`](frontend/src/charts/SelectCombobox.svelte:182)). If the `description` function itself or the strings it processes could contain unsanitized HTML, and if Svelte's default escaping was somehow bypassed (unlikely for text content), it could be an issue. Typically, `description` functions would return plain text or use i18n which should also be safe.
        *   `option` values are used in `aria-selected` checks and `value` attributes, which are generally safe.
*   **Secrets Management:** N/A. Option values/descriptions are not secrets.
*   **Input Validation & Sanitization:** The component relies on the `options` array and `value` string being well-formed. The `description` and `multiple_select` functions are assumed to be safe.
*   **Error Handling & Logging:** No explicit error handling. If props are malformed (e.g., `options` is not an array, `description` is not a function), runtime errors will occur.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **`actions.last()` Bug:** The `last` action (Line [`frontend/src/charts/SelectCombobox.svelte:81`](frontend/src/charts/SelectCombobox.svelte:81)) incorrectly sets `index = 0;`. It should be `index = options.length - 1;`.
*   **Focus Management on Close:** When the listbox is closed (e.g., via Escape or selecting an item), focus should typically return to the combobox button. This seems to be handled by `onblur` on the button itself for some cases, but explicit focus management after selection might be beneficial.
*   **Multi-select UI:** For multi-select, the selected items are joined by a comma in the button's display text (`description(value)` where `value` is "opt1,opt2"). This might not be the most user-friendly display for multiple selections. A more advanced multi-select combobox might show tags or a summary like "2 items selected". However, for a "select-only" pattern, this might be an acceptable simplification.
*   **`find_letter` Behavior:** The `find_letter` action (Line [`frontend/src/charts/SelectCombobox.svelte:67`](frontend/src/charts/SelectCombobox.svelte:67)) finds the *first* match. Standard combobox behavior often cycles through matches if the same letter is typed repeatedly, or allows for multi-character typing with a short timeout. This is a simpler implementation.
*   **Complexity of `select` action:** The logic within the `select` action for handling `multiple_select` (Lines [`frontend/src/charts/SelectCombobox.svelte:100-110`](frontend/src/charts/SelectCombobox.svelte:100)) is a bit dense. Breaking it down further or adding comments could improve readability.
*   The component is quite complex due to adhering to accessibility guidelines for a combobox. This isn't "debt" but inherent complexity for the pattern.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   This component is likely used by other components that need dropdown selection, such as [`ConversionAndInterval.svelte`](frontend/src/charts/ConversionAndInterval.svelte:1) (analyzed in Batch 9).
*   **System-Level Interactions:**
    *   **UI Framework (Svelte):** Heavily uses Svelte 5 features (`$props`, `$state`, `$derived`, `$bindable`, `$effect`).
    *   **ARIA Standards:** Designed to conform to ARIA combobox patterns.
    *   **Parent Components:** Consumed by any component needing a customizable select dropdown, passing in `options`, `value` (bindable), and `description`/`multiple_select` functions. For example, [`ConversionAndInterval.svelte`](frontend/src/charts/ConversionAndInterval.svelte:1) uses it for selecting currency conversion and time intervals.

## File: `frontend/src/charts/Sunburst.svelte`

### I. Overview and Purpose

[`frontend/src/charts/Sunburst.svelte`](frontend/src/charts/Sunburst.svelte:1) is a Svelte component that renders a sunburst chart. Sunburst charts are used to visualize hierarchical data, where each level of the hierarchy is represented by a ring, and segments within rings represent child nodes. This component uses D3.js for layout (`partition`) and shape generation (`arc`). It displays the account name and balance of the currently hovered segment (or the root) in the center of the chart. Segments are interactive, linking to the corresponding account's report page and highlighting related segments on hover/focus.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/Sunburst.svelte:17-22`](frontend/src/charts/Sunburst.svelte:17), Usage Line [`frontend/src/charts/Sunburst.svelte:24`](frontend/src/charts/Sunburst.svelte:24)):**
    *   `data: AccountHierarchyNode`: The root D3 hierarchy node (from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1)) for the account data.
    *   `currency: string`: The currency context for the balances being displayed.
    *   `width: number`: The total width for the sunburst chart.
    *   `height: number`: The total height for the sunburst chart.

2.  **Layout and Dimensions:**
    *   `radius = $derived(Math.min(width, height) / 2)` (Line [`frontend/src/charts/Sunburst.svelte:26`](frontend/src/charts/Sunburst.svelte:26)): Calculates the outer radius of the sunburst based on the smaller of width/height.

3.  **D3 Data Processing:**
    *   `root = $derived(partition<AccountHierarchyDatum>()(data))` (Line [`frontend/src/charts/Sunburst.svelte:28`](frontend/src/charts/Sunburst.svelte:28)): Applies D3's `partition` layout to the input `data`. The partition layout assigns `x0, x1, y0, y1` coordinates to each node, suitable for radial layouts.
    *   `nodes = $derived(root.descendants().filter((d) => !d.data.dummy && d.depth > 0))` (Lines [`frontend/src/charts/Sunburst.svelte:29-31`](frontend/src/charts/Sunburst.svelte:29)): Gets all descendant nodes from the partitioned `root`, filtering out "dummy" nodes and the root node itself (depth > 0), as these are not directly rendered as arcs.

4.  **Interaction State:**
    *   `current: AccountHierarchyNode | null = $state(null)` (Line [`frontend/src/charts/Sunburst.svelte:33`](frontend/src/charts/Sunburst.svelte:33)): Stores the currently hovered/focused hierarchy node. Used to display its details in the center and for highlighting.

5.  **`$effect.pre` for Resetting `current` (Lines [`frontend/src/charts/Sunburst.svelte:35-42`](frontend/src/charts/Sunburst.svelte:35)):**
    *   A Svelte "pre" effect that observes changes to the `data` prop.
    *   When `data` changes (meaning a new chart is being rendered), it uses `untrack` to set `current = null`. This ensures that hover state from a previous chart doesn't persist.

6.  **Text Display Logic:**
    *   **`balanceText(d: AccountHierarchyNode)` (Lines [`frontend/src/charts/Sunburst.svelte:44-50`](frontend/src/charts/Sunburst.svelte:44)):**
        *   Generates the text to display the balance of node `d`.
        *   Shows the formatted amount (`$ctx.amount`) and its percentage of the root's total value (`formatPercentage`), if the total is non-zero.
    *   The central text elements (Lines [`frontend/src/charts/Sunburst.svelte:73-78`](frontend/src/charts/Sunburst.svelte:73)) display the account name and balance text of `(current ?? root)`.

7.  **D3 Scales and Arc Generator:**
    *   `x = scaleLinear([0, 2 * Math.PI])` (Line [`frontend/src/charts/Sunburst.svelte:52`](frontend/src/charts/Sunburst.svelte:52)): A D3 linear scale mapping the `d.x0, d.x1` values (typically 0-1 range from partition for angle) to radians (0 to 2π).
    *   `y = $derived(scaleSqrt([0, radius]))` (Line [`frontend/src/charts/Sunburst.svelte:53`](frontend/src/charts/Sunburst.svelte:53)): A D3 square root scale mapping `d.y0, d.y1` values (depth/radius) to actual pixel radii. `scaleSqrt` is often used for radial charts because it makes areas proportional to values, rather than radii.
    *   `arcShape = $derived(...)` (Lines [`frontend/src/charts/Sunburst.svelte:54-60`](frontend/src/charts/Sunburst.svelte:54)): D3 arc generator configured to use the `x` and `y` scales to draw the segments of the sunburst.

8.  **SVG Rendering (Lines [`frontend/src/charts/Sunburst.svelte:63-96`](frontend/src/charts/Sunburst.svelte:63)):**
    *   A top-level `<g>` element, translated to center the sunburst within the `width`/`height`.
    *   `onmouseleave`: Clears the `current` highlighted state.
    *   An invisible `<circle r={radius}>` (Line [`frontend/src/charts/Sunburst.svelte:72`](frontend/src/charts/Sunburst.svelte:72)): This might be to ensure the mouseleave event on the main `<g>` triggers correctly even when not over a path, or to define the bounds for some interaction.
    *   Two `<text>` elements in the center to display the `account` and `balanceText` of the `current` (or `root`) node.
    *   Iterates through `nodes` (`#each nodes as d`):
        *   Renders an `<a>` tag for each node, linking to the account's report page (`$urlForAccount`).
        *   Inside the `<a>`, a `<path>` element is rendered for the arc segment:
            *   `onmouseover` / `onfocus`: Set `current = d`.
            *   `class:half`: Applies the `half` class (for opacity) if `current` is set and the current segment `d` is not an ancestor of or equal to `current`. This highlights the hovered segment and its children.
            *   `fill-rule="evenodd"`.
            *   `fill={$sunburstScale(d.data.account)}`: Color from `sunburstScale` (from [`./helpers.ts`](frontend/src/charts/helpers.ts:1)).
            *   `d={arcShape(d)}`: Path data generated by the D3 arc generator.

9.  **Styling (`<style>` block Lines [`frontend/src/charts/Sunburst.svelte:98-114`](frontend/src/charts/Sunburst.svelte:98)):**
    *   `.half { opacity: 0.5; }`: Style for de-emphasizing non-hovered segments.
    *   Styles for central text elements (`.account`, `.balance`).
    *   `path { cursor: pointer; }`.

**B. Data Structures:**
*   Consumes `AccountHierarchyNode` and `AccountHierarchyDatum` from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1).
*   Uses D3 scales, partition layout, and arc generator.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. Standard D3 patterns for sunbursts are used. Svelte's reactivity simplifies state management for hover effects.
*   **Complexity:** Moderate to High. Involves D3 radial layouts, arc generation, and interactive highlighting logic. The interaction of `current` state with `class:half` for opacity requires careful understanding.
*   **Maintainability:** Moderate. Changes to the visual appearance or interaction logic would involve modifying D3 setup or SVG attributes.
*   **Testability:** Difficult. Requires a Svelte component testing environment. Would involve:
    *   Mocking the `data: AccountHierarchyNode` prop.
    *   Mocking Svelte stores/helpers (`$ctx`, `$urlForAccount`, `$sunburstScale`).
    *   Snapshot testing for SVG.
    *   Testing interactions (hover/focus, central text updates, highlighting).
*   **Adherence to Best Practices & Idioms:**
    *   Correct use of D3 `partition` and `arc` for sunbursts.
    *   Integration of D3 with Svelte.
    *   Using ARIA `role="img"` and `aria-label` on links for accessibility.
    *   The `$effect.pre` with `untrack` is a good way to reset component state when a major prop like `data` changes.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data (Low Risk):**
        *   Account names (`d.data.account`) are used in `$sunburstScale`, `$urlForAccount`, `aria-label`, and displayed in the central text. Svelte's default text escaping and robust URL generation should make this safe.
        *   Balance text involves formatted numbers and currency symbols, generally safe.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** Assumes the input `data` prop is a valid `AccountHierarchyNode`, processed from trusted/validated sources by [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1).
*   **Error Handling & Logging:** No explicit error handling. Relies on D3 and Svelte. Malformed hierarchy data could cause D3 to error.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Highlighting Logic (`class:half`):** The condition `!current.data.account.startsWith(d.data.account)` (Line [`frontend/src/charts/Sunburst.svelte:88`](frontend/src/charts/Sunburst.svelte:88)) is used to dim segments not part of the hovered path. This string-based check assumes account names correctly reflect the hierarchy for `startsWith` to work as an ancestor check. While common in Beancount, a more robust way might involve checking D3 node ancestry directly (e.g., `d.ancestors().includes(current)` or similar).
*   **Central Text Update:** The central text updates on hover. For very rapid mouse movements over many small segments, this could lead to rapid text changes. Debouncing or a slight delay could be considered if this becomes an issue, but is likely fine.
*   No major technical debt apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   None directly with `scatterplot.ts` or `SelectCombobox.svelte`.
*   **System-Level Interactions:**
    *   **D3.js Libraries:** Uses `d3-hierarchy` (partition), `d3-scale` (scaleLinear, scaleSqrt), `d3-shape` (arc).
    *   **Svelte Framework:** Uses `$props`, `$state`, `$derived`, `$effect.pre`, `untrack`.
    *   **Formatting Utilities (`../format.ts`):** Uses `formatPercentage`.
    *   **URL Helpers (`../helpers.ts`):** Uses `urlForAccount`.
    *   **Svelte Stores (`../stores/format.ts`):** Uses `$ctx` for amount formatting.
    *   **Chart Helpers (`./helpers.ts`):** Uses `sunburstScale`.
    *   **Hierarchy Logic (`./hierarchy.ts`):** Consumes `AccountHierarchyNode`, `AccountHierarchyDatum`.
    *   **Parent Components:** Rendered by [`HierarchyContainer.svelte`](frontend/src/charts/HierarchyContainer.svelte:1) when the mode is "sunburst".
## File: `frontend/src/charts/tooltip.ts`

### I. Overview and Purpose

[`frontend/src/charts/tooltip.ts`](frontend/src/charts/tooltip.ts:1) is a TypeScript module that provides a global tooltip system for Fava charts. It manages a single, lazily created `HTMLDivElement` that serves as the tooltip container. The module exports Svelte actions (`followingTooltip`, `positionedTooltip`) to attach tooltip behavior to SVG elements, along with helper functions (`domHelpers`) for constructing tooltip content from basic HTML elements and text nodes.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Global Tooltip Element (`tooltip` IIFE, Lines [`frontend/src/charts/tooltip.ts:5-15`](frontend/src/charts/tooltip.ts:5)):**
    *   An Immediately Invoked Function Expression (IIFE) that manages a singleton `HTMLDivElement` for the tooltip.
    *   The `div` is created only when `tooltip()` is first called (lazy initialization).
    *   It's styled with the class `tooltip` and appended to `document.body`.
    *   Subsequent calls to `tooltip()` return the same instance.

2.  **`hide()` Function (Lines [`frontend/src/charts/tooltip.ts:18-21`](frontend/src/charts/tooltip.ts:18)):**
    *   Retrieves the global tooltip element.
    *   Sets its `opacity` style to "0" to hide it.

3.  **`domHelpers` Object (Lines [`frontend/src/charts/tooltip.ts:24-41`](frontend/src/charts/tooltip.ts:24)):**
    *   A collection of utility functions to create simple DOM nodes for tooltip content:
        *   `br()`: Creates a `<br>` element.
        *   `em(content: string)`: Creates an `<em>` element with the given text content.
        *   `t(text: string)`: Creates a `Text` node.
        *   `pre(content: string)`: Creates a `<pre>` element with the given text content.
    *   These helpers allow chart-specific tooltip functions to construct content without directly manipulating `innerHTML`, promoting safer content creation.

4.  **`TooltipContent` Type (Line [`frontend/src/charts/tooltip.ts:43`](frontend/src/charts/tooltip.ts:43)):**
    *   `export type TooltipContent = (HTMLElement | Text)[];`
    *   Defines the expected structure for tooltip content: an array of `HTMLElement` or `Text` nodes.

5.  **`followingTooltip` Svelte Action (Lines [`frontend/src/charts/tooltip.ts:51-76`](frontend/src/charts/tooltip.ts:51)):**
    *   **Purpose:** A Svelte action for SVG elements. It makes a tooltip appear and follow the mouse cursor when hovering over the element.
    *   **Parameters:**
        *   `node: SVGElement`: The SVG element to attach the action to.
        *   `text: () => TooltipContent`: A getter function that returns the `TooltipContent` to be displayed.
    *   **Behavior:**
        *   On `mouseenter`: Retrieves the global tooltip, populates it with content from `getter()`.
        *   On `mousemove`: Updates the tooltip's `left` and `top` style to follow the `event.pageX` and `event.pageY` (with a slight vertical offset for `top`). Sets opacity to "1" to show it.
        *   On `mouseleave`: Calls `hide()` to hide the tooltip.
    *   **Return Object:** Implements the Svelte action contract:
        *   `destroy`: Calls `hide()` when the element is unmounted.
        *   `update(t)`: Allows the `getter` function to be updated if the tooltip content needs to change reactively.

6.  **`TooltipFindNode` Type (Lines [`frontend/src/charts/tooltip.ts:79-82`](frontend/src/charts/tooltip.ts:79)):**
    *   `export type TooltipFindNode = (x: number, y: number) => [number, number, TooltipContent] | undefined;`
    *   Defines the signature for a function used by `positionedTooltip`. This function takes x/y coordinates (relative to the container) and should return:
        *   An array `[tooltipX, tooltipY, content]` where `tooltipX` and `tooltipY` are the desired coordinates for the tooltip (also relative to the container), and `content` is the `TooltipContent`.
        *   Or `undefined` if no tooltip should be shown for the given coordinates.

7.  **`positionedTooltip` Svelte Action (Lines [`frontend/src/charts/tooltip.ts:92-116`](frontend/src/charts/tooltip.ts:92)):**
    *   **Purpose:** A Svelte action for `SVGGElement` containers. It shows a tooltip based on finding a nearby data point or region within the container.
    *   **Parameters:**
        *   `node: SVGGElement`: The SVG group element to attach to.
        *   `find: TooltipFindNode`: The function described above to locate a target and get its content.
    *   **Behavior:**
        *   On `mousemove`:
            *   Gets mouse coordinates relative to the `node` using `d3-selection.pointer(event)`.
            *   Calls the `find(xPointer, yPointer)` function.
            *   If `find` returns a result `[x, y, content]` and the node's screen transformation matrix (`getScreenCTM()`) is available:
                *   Retrieves the global tooltip, sets its opacity to "1", and populates it with `content`.
                *   Calculates the absolute screen position for the tooltip by transforming the returned `x, y` using the `matrix` and adding `window.scrollX/Y`.
                *   Sets the tooltip's `left` and `top` style.
            *   If `find` returns `undefined`, calls `hide()`.
        *   On `mouseleave`: Calls `hide()`.
    *   **Return Object:** Implements the Svelte action contract:
        *   `destroy`: Calls `hide()`. (Note: No `update` method is provided for this action, meaning the `find` function cannot be reactively updated after initialization via this action's interface).

**B. Data Structures:**
*   `TooltipContent` (array of DOM nodes).
*   `TooltipFindNode` (function type).

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The separation of the global tooltip element, helper functions, and Svelte actions is clear. The purpose of each action is well-commented.
*   **Complexity:** Moderate. Managing a global singleton DOM element for the tooltip and correctly positioning it based on mouse events and SVG transformations involves some intricacy. The Svelte action pattern is used effectively.
*   **Maintainability:** Good. The module is focused on tooltip functionality. Changes to tooltip styling would be in CSS (for the `.tooltip` class). Modifications to positioning logic are contained within the actions.
*   **Testability:** Moderate to Difficult.
    *   `domHelpers` are simple pure functions and easily testable.
    *   The Svelte actions (`followingTooltip`, `positionedTooltip`) are harder to test in isolation as they interact with the DOM, browser events, and a global tooltip element. This would typically require a browser-like testing environment (e.g., Playwright, Cypress, or Vitest with JSDOM and event simulation).
    *   Testing the lazy initialization of the tooltip `div` and its correct appending to `document.body` would also need a DOM environment.
*   **Adherence to Best Practices & Idioms:**
    *   Lazy initialization of the global tooltip element is a good performance practice.
    *   Using Svelte actions to encapsulate DOM manipulation and event listener setup/teardown is idiomatic Svelte.
    *   Providing `domHelpers` encourages safer content creation over direct `innerHTML` manipulation.
    *   The use of `node.getScreenCTM()` in `positionedTooltip` is necessary for correctly positioning a global HTML tooltip relative to SVG content that might be transformed.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Tooltip Content:** The primary security concern would be if the `TooltipContent` (arrays of `HTMLElement | Text` nodes) passed to `tooltip().replaceChildren(...content)` could contain malicious scripts.
        *   The `domHelpers` themselves (`em`, `t`, `pre`) create elements and set `textContent`, which is safe against XSS.
        *   If a consumer of these actions were to construct `HTMLElement`s for `TooltipContent` using unsafe methods (e.g., setting `innerHTML` with untrusted data) *before* passing them to the tooltip system, that would be the source of the vulnerability. The tooltip module itself, by accepting pre-constructed nodes, relies on the caller to provide safe content.
        *   The `followingTooltip` and `positionedTooltip` actions receive content via a getter function or the `find` function. The safety depends on how these functions generate their `TooltipContent`.
*   **Secrets Management:** N/A. Tooltips display data, not secrets.
*   **Input Validation & Sanitization:** The module assumes the `TooltipContent` array contains valid, safe DOM nodes. No explicit validation or sanitization of this content is performed by the tooltip module itself.
*   **Error Handling & Logging:** No explicit error handling. If `getter()` or `find()` functions throw errors, these would propagate.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **`positionedTooltip` Update Method:** The `positionedTooltip` action does not provide an `update` method in its return object. This means if the `find` function passed to it needs to change reactively based on other component state, the action would not automatically pick up the new `find` function. The action would need to be re-applied (which Svelte might do if the prop changes, but an explicit `update` is cleaner).
*   **Tooltip Styling:** The tooltip `div` is created with only `className = "tooltip"`. All styling (including initial `display: none` or `visibility: hidden` before first show, positioning, background, border, etc.) is assumed to be handled by external CSS. This is fine but means the module isn't fully self-contained visually.
*   **Global Singleton Management:** While a global singleton tooltip is common, care must be taken if multiple independent parts of an application (outside of Fava charts) also wanted to use a similar tooltip system, as they might conflict. For Fava's charts, it's likely a controlled environment.
*   **Accessibility of Tooltips:** Standard HTML tooltips (e.g., `title` attribute) have some accessibility built-in. Custom `div`-based tooltips need careful ARIA treatment if they are to be announced by screen readers. This module focuses on visual presentation; accessibility would depend on how the triggering elements are marked up and whether the tooltip content should be discoverable by assistive technologies beyond mouse hover. Often, important information in a tooltip should also be available through other means.
*   No major technical debt apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   The Svelte actions and `domHelpers` from this module are used by [`Treemap.svelte`](frontend/src/charts/Treemap.svelte:1) (and other chart components like `LineChart.svelte`, `Icicle.svelte`, `ScatterPlot.svelte`, `Sunburst.svelte`) to provide interactive tooltips.
*   **System-Level Interactions:**
    *   **D3.js Library (`d3-selection`):** Uses `pointer` for mouse coordinate calculations within SVG.
    *   **Svelte Framework:** Defines and uses Svelte `Action` interface.
    *   **Browser DOM API:** Directly creates and manipulates `HTMLDivElement`, `HTMLBRElement`, `HTMLElement`, `Text`, `HTMLPreElement`. Appends tooltip to `document.body`. Uses `MouseEvent`, `window.scrollX/Y`, `getScreenCTM()`.
    *   **CSS:** Relies on an external CSS class `.tooltip` for styling the tooltip `div`.
    *   **Various Chart Components:** This module is a core utility for providing tooltips across many Fava charts.

## File: `frontend/src/charts/Treemap.svelte`

### I. Overview and Purpose

[`frontend/src/charts/Treemap.svelte`](frontend/src/charts/Treemap.svelte:1) is a Svelte component that renders a treemap visualization. Treemaps are used to display hierarchical data as a set of nested rectangles, where the area of each rectangle is proportional to its value. This component uses D3.js for the treemap layout and Svelte for rendering the SVG elements. It displays account names within the rectangles (if space permits) and provides tooltips with balance information on hover. Each rectangle links to the corresponding account's report page.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/Treemap.svelte:17-22`](frontend/src/charts/Treemap.svelte:17), Usage Line [`frontend/src/charts/Treemap.svelte:24`](frontend/src/charts/Treemap.svelte:24)):**
    *   `data: AccountHierarchyNode`: The root D3 hierarchy node (from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1)) for the account data. This data is expected to have been pre-processed by `addInternalNodesAsLeaves` in `hierarchy.ts` so that parent accounts with their own balances are represented as "dummy" leaves.
    *   `width: number`: The total width for the treemap.
    *   `height: number`: The total height for the treemap.
    *   `currency: string`: The currency context for the balances being displayed.

2.  **D3 Treemap Layout:**
    *   `tree = treemap<AccountHierarchyDatum>().paddingInner(2).round(true)` (Line [`frontend/src/charts/Treemap.svelte:26`](frontend/src/charts/Treemap.svelte:26)): Creates a D3 treemap layout generator.
        *   `.paddingInner(2)`: Adds 2px padding between sibling cells.
        *   `.round(true)`: Rounds x, y, width, height to integers.
    *   `root = $derived(tree.size([width, height])(data.copy()))` (Line [`frontend/src/charts/Treemap.svelte:27`](frontend/src/charts/Treemap.svelte:27)): Applies the treemap layout to a *copy* of the input `data`.
        *   `.size([width, height])`: Sets the dimensions for the layout.
        *   `data.copy()`: It's important to use `.copy()` because D3 layouts often mutate the input hierarchy (e.g., by adding `x0, y0, x1, y1` properties).
    *   `leaves = $derived(root.leaves().filter((d) => d.value != null && d.value !== 0))` (Lines [`frontend/src/charts/Treemap.svelte:28-30`](frontend/src/charts/Treemap.svelte:28)): Gets all leaf nodes from the laid-out `root` and filters out those with no value or a zero value, as these typically shouldn't be rendered.

3.  **Color Logic (`fill(d: AccountHierarchyNode)` function, Lines [`frontend/src/charts/Treemap.svelte:32-38`](frontend/src/charts/Treemap.svelte:32)):**
    *   Determines the fill color for a treemap cell `d`.
    *   If the node `d` is a "dummy" node (representing a parent's own balance) and has a parent, it uses the parent node for color determination. This ensures the dummy leaf representing the parent's balance gets the same color as other children of that parent.
    *   If the effective node is at depth 1 (a direct child of the invisible root) or has no parent, it uses `$treemapScale(node.data.account)`.
    *   Otherwise (for deeper nodes), it uses `$treemapScale(node.parent.data.account)`. This means all children of a given parent share the same base color, which is a common treemap coloring strategy to show group affiliation. `$treemapScale` is from [`./helpers.ts`](frontend/src/charts/helpers.ts:1).

4.  **Tooltip Content (`tooltipText(d: AccountHierarchyNode)` function, Lines [`frontend/src/charts/Treemap.svelte:40-50`](frontend/src/charts/Treemap.svelte:40)):**
    *   Generates `TooltipContent` (from [`./tooltip.ts`](frontend/src/charts/tooltip.ts:1)) for a given treemap node `d`.
    *   Displays the node's value formatted with currency (`$ctx.amount`) and its percentage of the root's total value (`formatPercentage`).
    *   Displays the full account name (`d.data.account`), emphasized.
    *   Uses `domHelpers` from [`./tooltip.ts`](frontend/src/charts/tooltip.ts:1).

5.  **Text Visibility Logic (`setVisibility` Svelte Action, Lines [`frontend/src/charts/Treemap.svelte:53-64`](frontend/src/charts/Treemap.svelte:53)):**
    *   A custom Svelte action for SVG `<text>` elements.
    *   **Purpose:** To hide the text if its computed length is too large for the containing rectangle, or if the rectangle is too short.
    *   **Parameters:**
        *   `node: SVGTextElement`: The text element.
        *   `param: HierarchyRectangularNode<AccountHierarchyDatum>` (named `d` in the `update` function): The D3 node corresponding to the text's rectangle.
    *   **Behavior:**
        *   The `update` function (called on init and when `param` changes):
            *   Gets the computed text length using `node.getComputedTextLength()`.
            *   Sets `node.style.visibility` to "hidden" if the rectangle width (`d.x1 - d.x0`) is not greater than `length + 4` (4px padding) OR if the rectangle height (`d.y1 - d.y0`) is not greater than 14px. Otherwise, sets it to "visible".

6.  **SVG Rendering (Lines [`frontend/src/charts/Treemap.svelte:67-87`](frontend/src/charts/Treemap.svelte:67)):**
    *   Renders an SVG element with a `viewBox`.
    *   Iterates through `leaves` (`#each leaves as d`):
        *   For each leaf node `d`:
            *   Renders a `<g>` element, translated to the node's position (`d.x0, d.y0`).
            *   Applies the `followingTooltip` action (from [`./tooltip.ts`](frontend/src/charts/tooltip.ts:1)) with `tooltipText(d)`.
            *   Renders a `<rect>`:
                *   `fill={fill(d)}`: Fill color determined by the `fill` function.
                *   `width={d.x1 - d.x0}`, `height={d.y1 - d.y0}`: Dimensions from D3 layout.
            *   Renders an `<a>` tag linking to the account's report page (`$urlForAccount(account)`).
                *   Inside the `<a>`, a `<text>` element:
                    *   Applies the `setVisibility` action with node `d`.
                    *   Positioned in the center of the rectangle.
                    *   `text-anchor="middle"`.
                    *   Displays the leaf part of the account name (`leaf(account)` from `../lib/account`).

7.  **Styling (`<style>` block Lines [`frontend/src/charts/Treemap.svelte:90-94`](frontend/src/charts/Treemap.svelte:90)):**
    *   `svg { shape-rendering: crispedges; }`: Optimizes rendering for sharp edges, common for treemaps.

**B. Data Structures:**
*   Consumes `AccountHierarchyNode` and `AccountHierarchyDatum` from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1).
*   Uses D3 treemap layout and its node structure (`HierarchyRectangularNode`).
*   Generates `TooltipContent`.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The use of D3 treemap layout is standard. Svelte's reactive declarations (`$derived`) and templating make the rendering logic clear. The `fill` logic and `setVisibility` action are well-defined.
*   **Complexity:** Moderate. Involves D3 layout, SVG rendering, custom Svelte action for text visibility, and tooltip integration.
*   **Maintainability:** Moderate. Changes to visual appearance (e.g., padding, rounding, color scheme) would involve modifying D3 setup or the `fill` function. The `setVisibility` action is fairly specific to this component's needs.
*   **Testability:** Difficult. Requires a Svelte component testing environment. Would involve:
    *   Mocking the `data: AccountHierarchyNode` prop with various hierarchy structures.
    *   Mocking Svelte stores/helpers (`$ctx`, `$urlForAccount`, `$treemapScale`, `leaf`, `formatPercentage`).
    *   Snapshot testing for the rendered SVG.
    *   Testing tooltip interactions.
    *   Testing the `setVisibility` action (e.g., by checking `style.visibility` under different text length / rect size scenarios).
*   **Adherence to Best Practices & Idioms:**
    *   Correct use of D3 `treemap` layout.
    *   Using `.copy()` on hierarchy data before passing to layout is good practice.
    *   Filtering out zero-value leaves is sensible.
    *   Custom Svelte action (`setVisibility`) for DOM-dependent logic is a good Svelte pattern.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data (Low Risk):**
        *   Account names (`d.data.account`, `leaf(account)`) are used for colors, URLs, and rendered as text content. Svelte's default text escaping, robust URL generation by `$urlForAccount`, and safe color scaling should mitigate risks.
        *   Tooltip content generated by `tooltipText` uses `domHelpers` which create text nodes or use `textContent`, generally safe.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** Assumes the input `data` prop is a valid `AccountHierarchyNode`, processed from trusted/validated sources by [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1), including the `addInternalNodesAsLeaves` transformation.
*   **Error Handling & Logging:** No explicit error handling. Relies on D3 and Svelte. Malformed hierarchy data could cause D3 layout to error.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Text Fitting Algorithm:** The `setVisibility` action uses `getComputedTextLength()`. For more sophisticated text fitting (e.g., word wrapping, scaling font size, truncation with ellipsis), more advanced techniques would be needed, but this would significantly increase complexity. The current approach is a reasonable heuristic for simple hiding.
*   **Coloring Strategy:** The `fill` function's logic (coloring by parent at depth > 1) is a specific choice. Alternative treemap coloring strategies exist (e.g., by value, by depth, sequential colors for siblings). This is a design choice rather than debt.
*   **Performance with Many Leaves:** Rendering and running the `setVisibility` action for a very large number of leaf nodes could have performance implications, as `getComputedTextLength()` can cause reflows. For extremely large treemaps, canvas rendering or virtualized SVG might be considered, but for typical Fava use cases, SVG is likely fine.
*   No major technical debt apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Uses `domHelpers` and `followingTooltip` from [`./tooltip.ts`](frontend/src/charts/tooltip.ts:1).
*   **System-Level Interactions:**
    *   **D3.js Libraries:** Uses `d3-hierarchy` (treemap, HierarchyRectangularNode).
    *   **Svelte Framework:** Uses Svelte 5 runes (`$props`, `$derived`), Svelte `Action` interface.
    *   **Formatting Utilities (`../format.ts`):** Uses `formatPercentage`.
    *   **URL Helpers (`../helpers.ts`):** Uses `urlForAccount`.
    *   **Account Lib (`../lib/account.ts`):** Uses `leaf`.
    *   **Svelte Stores (`../stores/format.ts`):** Uses `$ctx` for amount formatting.
    *   **Chart Helpers (`./helpers.ts`):** Uses `$treemapScale`.
    *   **Hierarchy Logic (`./hierarchy.ts`):** Consumes `AccountHierarchyNode`, `AccountHierarchyDatum`.
    *   **Parent Components:** This component is rendered by [`HierarchyContainer.svelte`](frontend/src/charts/HierarchyContainer.svelte:1) when the mode is "treemap".