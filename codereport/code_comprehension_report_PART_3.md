# Batch 8: Chart Container, Legend, and Switcher Components

This batch focuses on higher-level Svelte components responsible for orchestrating the display of individual charts, their legends, and providing mechanisms to switch between multiple charts.

## File: `frontend/src/charts/Chart.svelte`

### I. Overview and Purpose

[`frontend/src/charts/Chart.svelte`](frontend/src/charts/Chart.svelte:1) is a Svelte component that acts as a versatile container and dispatcher for rendering various types of Fava charts. It receives a `FavaChart` data object and dynamically selects and renders the appropriate specific chart component (e.g., `BarChart.svelte`, `LineChart.svelte`). Beyond rendering the core chart visualization, this component also integrates related UI elements like chart legends (using [`ChartLegend.svelte`](frontend/src/charts/ChartLegend.svelte:1)), mode switches for chart display variations (using [`ModeSwitch.svelte`](frontend/src/charts/ModeSwitch.svelte:1)), and a toggle button to expand or collapse the chart display area. It plays a crucial role in adapting the presentation based on the chart type and user interaction by measuring its available width and passing this information to the child chart components for responsive rendering.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/Chart.svelte:19-24`](frontend/src/charts/Chart.svelte:19), Usage Line [`frontend/src/charts/Chart.svelte:26`](frontend/src/charts/Chart.svelte:26)):**
    *   `chart: FavaChart`: The primary data object defining the specific chart to be rendered (e.g., barchart, linechart data and type).
    *   `children?: Snippet`: An optional Svelte `Snippet` that allows parent components (like [`ChartSwitcher.svelte`](frontend/src/charts/ChartSwitcher.svelte:1)) to inject additional UI elements (e.g., conversion or interval selectors) into the header area of this chart container.

2.  **State Management:**
    *   `width: number | undefined = $state()` (Line [`frontend/src/charts/Chart.svelte:29`](frontend/src/charts/Chart.svelte:29)): A Svelte state variable that stores the client width of the chart's container `div`. This width is obtained using `bind:clientWidth` and is crucial for child chart components to render themselves correctly within the available space.
    *   Interaction with Svelte Stores (from `../stores/chart`):
        *   `$showCharts`: Controls the overall visibility of the chart area.
        *   `$barChartMode`, `$hierarchyChartMode`, `$lineChartMode`: Determine display modes for specific chart types.
        *   `$chartToggledCurrencies`: Used by `ChartLegend` to manage visibility of series/currencies.

3.  **Dynamic Rendering Logic:**
    *   **Header Controls (Lines [`frontend/src/charts/Chart.svelte:32-74`](frontend/src/charts/Chart.svelte:32)):**
        *   Conditionally renders a [`ChartLegend.svelte`](frontend/src/charts/ChartLegend.svelte:1) component if `$showCharts` is true. The properties passed to `ChartLegend` (like `legend`, `color`, `toggled`, `active`) are determined by the `chart.type` and current chart mode (e.g., `$barChartMode`).
        *   Conditionally renders a [`ModeSwitch.svelte`](frontend/src/charts/ModeSwitch.svelte:1) component if `$showCharts` is true and the `chart.type` supports different display modes (e.g., stacked vs. grouped for bar charts).
        *   Renders the `children` snippet if provided.
        *   Includes a button to toggle the `$showCharts` store, effectively showing or hiding the main chart visualization.
    *   **Chart Visualization Area (Lines [`frontend/src/charts/Chart.svelte:75-87`](frontend/src/charts/Chart.svelte:75)):**
        *   A `div` element whose visibility is bound to `!$showCharts`.
        *   `bind:clientWidth={width}` is used on this `div` to capture its rendered width.
        *   If `width` has been determined (i.e., the div is visible and has a width), it then dynamically renders one of the specific chart components based on `chart.type`:
            *   `chart.type === "barchart"`: Renders [`BarChart.svelte`](frontend/src/charts/BarChart.svelte:1).
            *   `chart.type === "hierarchy"`: Renders [`HierarchyContainer.svelte`](frontend/src/charts/HierarchyContainer.svelte:1).
            *   `chart.type === "linechart"`: Renders [`LineChart.svelte`](frontend/src/charts/LineChart.svelte:1).
            *   `chart.type === "scatterplot"`: Renders [`ScatterPlot.svelte`](frontend/src/charts/ScatterPlot.svelte:1).
        *   The `chart` data object and the measured `width` are passed as props to these specific chart components.

4.  **Styling:**
    *   Includes print-specific styles to hide the "show-charts" toggle button when printing (Lines [`frontend/src/charts/Chart.svelte:89-95`](frontend/src/charts/Chart.svelte:89)).

**B. Data Structures:**
*   Relies on the `FavaChart` type (an interface or union type likely defined in [`./index.ts`](frontend/src/charts/index.ts:1)) which encapsulates the data and metadata for different chart types.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The component's role as a dispatcher is clear. The use of Svelte's conditional rendering (`{#if ...}`) and component composition is idiomatic. Svelte 5 runes (`$props`, `$state`) are used.
*   **Complexity:** Moderate. The component manages several states (its own `width`, and reactive dependencies on multiple Svelte stores) and has significant conditional logic for rendering different child components and configuring their legends/controls.
*   **Maintainability:** Good. To support a new chart type, one would need to:
    1.  Import the new specific chart component.
    2.  Add an `else if` block in the chart rendering section (Lines [`frontend/src/charts/Chart.svelte:77-85`](frontend/src/charts/Chart.svelte:77)).
    3.  Potentially add conditional logic for its legend and mode switches in the header section (Lines [`frontend/src/charts/Chart.svelte:34-62`](frontend/src/charts/Chart.svelte:34)).
*   **Testability:** Difficult. Testing this component thoroughly would require a Svelte component testing environment. It would involve mocking the `FavaChart` prop for various chart types, mocking Svelte stores, and potentially asserting that the correct child components are rendered with the correct props.
*   **Adherence to Best Practices & Idioms:**
    *   Effective use of component composition.
    *   Reactive updates based on Svelte stores and props.
    *   Centralizes the logic for displaying a chart with its associated controls.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data:** The `chart` prop, which contains data like chart titles, series names, and currency codes, is passed down to child components (`BarChart`, `LineChart`, `ChartLegend`, etc.). The security depends on how these child components render this data. If they use Svelte's default text interpolation (`{value}`), it's generally safe. If any child component were to use `@html` with data from the `chart` object without proper sanitization, XSS could be a risk.
*   **Secrets Management:** N/A. Chart data is not expected to contain secrets.
*   **Input Validation & Sanitization:** The component assumes the `chart` prop is a valid and well-structured `FavaChart` object. No explicit validation is performed at this level; it relies on upstream data sources and specific chart data parsers (like in [`./bar.ts`](frontend/src/charts/bar.ts:1) or [`./line.ts`](frontend/src/charts/line.ts:1)) to provide valid data.
*   **Error Handling & Logging:** No explicit error handling. If `chart.type` is an unknown value, the corresponding specific chart component will not be rendered, failing silently in that regard.
*   **Post-Quantum Security Considerations:** N/A. This is a UI rendering component.

### V. Improvement Recommendations & Technical Debt

*   **Configuration Abstraction:** The conditional logic for rendering legends and mode switches (Lines [`frontend/src/charts/Chart.svelte:34-62`](frontend/src/charts/Chart.svelte:34)) based on `chart.type` could become cumbersome if many more chart types with unique header controls are added. A more abstract way, perhaps where each `FavaChart` object itself defines what legend/controls it needs, could be considered for extreme scalability, but the current approach is acceptable for a moderate number of chart types.
*   No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Uses [`ChartLegend.svelte`](frontend/src/charts/ChartLegend.svelte:1) for displaying chart legends.
*   **System-Level Interactions:**
    *   **Svelte Stores:** Heavily interacts with stores from [`../stores/chart.ts`](frontend/src/stores/chart.ts:1) (`barChartMode`, `chartToggledCurrencies`, `hierarchyChartMode`, `lineChartMode`, `showCharts`).
    *   **Child Chart Components:** Dynamically renders one of:
        *   [`BarChart.svelte`](frontend/src/charts/BarChart.svelte:1)
        *   [`HierarchyContainer.svelte`](frontend/src/charts/HierarchyContainer.svelte:1)
        *   [`LineChart.svelte`](frontend/src/charts/LineChart.svelte:1)
        *   [`ScatterPlot.svelte`](frontend/src/charts/ScatterPlot.svelte:1)
    *   **Other UI Components:** Uses [`ModeSwitch.svelte`](frontend/src/charts/ModeSwitch.svelte:1).
    *   **Chart Data Types:** Depends on the `FavaChart` type definition (likely from [`./index.ts`](frontend/src/charts/index.ts:1)).
    *   **Parent Components:** Expected to be used by components like [`ChartSwitcher.svelte`](frontend/src/charts/ChartSwitcher.svelte:1) that provide the `FavaChart` data.
## File: `frontend/src/charts/ChartLegend.svelte`

### I. Overview and Purpose

[`frontend/src/charts/ChartLegend.svelte`](frontend/src/charts/ChartLegend.svelte:1) is a Svelte component responsible for rendering an interactive legend for charts. It displays a list of legend items, each typically accompanied by a color swatch. Users can click on these items to toggle their visibility or set a specific item as active, which usually affects the display of the associated chart. This component is designed to be reusable across different chart types that require a legend.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/ChartLegend.svelte:6-15`](frontend/src/charts/ChartLegend.svelte:6), Usage Line [`frontend/src/charts/ChartLegend.svelte:17`](frontend/src/charts/ChartLegend.svelte:17)):**
    *   `legend: readonly string[]`: An array of strings, where each string is a label for a legend item.
    *   `color: boolean`: A boolean flag. If `true`, the color swatch next to each legend item is determined using the `$currenciesScale(item)` helper. If `false`, a default gray color (`#bbb`) is used for the swatch.
    *   `toggled?: Writable<string[]>`: An optional Svelte writable store. If provided, it's expected to hold an array of legend item names that are currently "toggled off" (inactive). Clicking a legend item will add or remove its name from this store.
    *   `active?: Writable<string | null>`: An optional Svelte writable store. If provided, it's expected to hold the name of a single legend item that is currently "active". Clicking a legend item will set its name as the value of this store. This prop is mutually exclusive with `toggled` in terms of interaction logic.

2.  **Rendering Logic (Lines [`frontend/src/charts/ChartLegend.svelte:20-40`](frontend/src/charts/ChartLegend.svelte:20)):**
    *   The component renders a `<div>` container.
    *   It iterates through the `legend` array using an `{#each ... as item (item)}` block, keyed by `item`.
    *   For each `item` in the legend:
        *   A `<button type="button">` is rendered.
        *   **`onclick` Handler (Lines [`frontend/src/charts/ChartLegend.svelte:24-32`](frontend/src/charts/ChartLegend.svelte:24)):**
            *   If the `active` store prop is provided, clicking the button sets `$active = item`.
            *   Else, if the `toggled` store prop is provided, clicking the button updates the `$toggled` store: if `item` is already in `$toggled`, it's removed; otherwise, it's added.
        *   **`class:inactive` (Line [`frontend/src/charts/ChartLegend.svelte:33`](frontend/src/charts/ChartLegend.svelte:33)):** The `inactive` class is conditionally applied.
            *   If `active` store is used: `inactive` if `item !== $active`.
            *   If `toggled` store is used: `inactive` if `$toggled?.includes(item)`.
        *   **Content of the button:**
            *   An `<i>` element (Lines [`frontend/src/charts/ChartLegend.svelte:35-36`](frontend/src/charts/ChartLegend.svelte:35)): Represents the color swatch. Its `background-color` style is set dynamically: if `color` prop is true, it uses `$currenciesScale(item)`; otherwise, it uses `'#bbb'`.
            *   A `<span>` element (Line [`frontend/src/charts/ChartLegend.svelte:37`](frontend/src/charts/ChartLegend.svelte:37)): Displays the `item` string (the legend label).

3.  **Styling (`<style>` block Lines [`frontend/src/charts/ChartLegend.svelte:42-69`](frontend/src/charts/ChartLegend.svelte:42)):**
    *   The main `<button>` is styled with `display: contents` to allow its children to flow as if the button wrapper wasn't there, while still retaining button interactivity.
    *   `.inactive span`: Applies `text-decoration: line-through` to the text of inactive items.
    *   `i` (swatch): Styles for size, margin, and border-radius.
    *   `.inactive i`: Applies `filter: grayscale()` to the swatch of inactive items.
    *   Print styles: Hides `.inactive` legend items when printing.

**B. Data Structures:**
*   Primarily deals with `string[]` for legend items and interacts with Svelte `Writable` stores of `string[]` or `string | null`.

### III. Code Quality Assessment

*   **Readability & Clarity:** Very good. The component is concise and its purpose is evident. The logic for handling `active` vs. `toggled` states is clear.
*   **Complexity:** Low. It involves basic iteration, conditional class application, and interaction with Svelte stores.
*   **Maintainability:** High. The component is small, focused, and easy to modify.
*   **Testability:** Moderate. Requires a Svelte component testing framework. Key aspects to test would be the rendering of legend items, the `onclick` behavior updating the stores, and the conditional application of the `inactive` class and styles. Mocking the Svelte stores (`toggled`, `active`) and `currenciesScale` would be necessary.
*   **Adherence to Best Practices & Idioms:**
    *   Good use of Svelte stores for managing interactive state that affects other components (the chart itself).
    *   Clear and reusable component design.
    *   Using `display: contents` for the button is a clever way to achieve semantic button behavior without disrupting the layout of its children.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data:** The `legend` prop contains an array of strings (`item`). These strings are rendered as text content within a `<span>{item}</span>` (Line [`frontend/src/charts/ChartLegend.svelte:37`](frontend/src/charts/ChartLegend.svelte:37)). Svelte's default templating automatically escapes this content, mitigating XSS risks from the legend item labels themselves.
*   **Secrets Management:** N/A. Legend items are not expected to be secrets.
*   **Input Validation & Sanitization:** The component assumes that the `legend` prop is an array of strings and that `toggled`/`active` stores are correctly typed. No specific input sanitization is performed.
*   **Error Handling & Logging:** No explicit error handling. If props are not provided as expected (e.g., `legend` is not an array), Svelte/JavaScript runtime errors might occur.
*   **Post-Quantum Security Considerations:** N/A. This is a UI rendering component.

### V. Improvement Recommendations & Technical Debt

*   **Color Customization:** The `color` prop is a boolean that switches between `$currenciesScale` and a hardcoded gray (`#bbb`). For more flexibility, this could be enhanced to accept a function that returns a color string, or a map of item-to-color. However, for its current use with currency colors, it's adequate.
*   **Accessibility:** The buttons are `display: contents`. While this helps with layout, ensure that accessibility tools still correctly interpret them as interactive buttons with their associated text. The `<i>` tag for the swatch is purely decorative; an `aria-hidden="true"` might be appropriate if it provides no information to screen readers. The text itself serves as the label.
*   No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   This component is used by [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) to display legends.
*   **System-Level Interactions:**
    *   **Svelte Stores:** Interacts with `Writable` stores passed as the `toggled` or `active` props. These stores are typically defined elsewhere (e.g., in [`../stores/chart.ts`](frontend/src/stores/chart.ts:1) like `chartToggledCurrencies`).
    *   **Chart Helpers (`./helpers.ts`):** Uses the `currenciesScale` Svelte readable store (from [`frontend/src/charts/helpers.ts`](frontend/src/charts/helpers.ts:1)) to determine colors for the swatches when `props.color` is true.
    *   **Parent Chart Components:** The functionality of this legend (toggling/activating items) is intended to influence the display of a parent chart component.
## File: `frontend/src/charts/ChartSwitcher.svelte`

### I. Overview and Purpose

[`frontend/src/charts/ChartSwitcher.svelte`](frontend/src/charts/ChartSwitcher.svelte:1) is a Svelte component designed to manage and display a collection of Fava charts, allowing the user to easily switch between them. It renders the currently selected chart using the generic [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) component and provides a set of buttons for selecting which chart to view. The component remembers the user's last selected chart across sessions (or page views, depending on store persistence) using a Svelte store. It also enhances usability by integrating keyboard shortcuts ('c' for next chart, 'C' for previous chart).

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/ChartSwitcher.svelte:10-12`](frontend/src/charts/ChartSwitcher.svelte:10), Usage Line [`frontend/src/charts/ChartSwitcher.svelte:14`](frontend/src/charts/ChartSwitcher.svelte:14)):**
    *   `charts: readonly FavaChart[]`: An array of `FavaChart` objects. Each object in this array represents a chart that can be selected and displayed.

2.  **State and Derived Logic:**
    *   **`$lastActiveChartName` (Svelte Store, Line [`frontend/src/charts/ChartSwitcher.svelte:5`](frontend/src/charts/ChartSwitcher.svelte:5)):** A writable Svelte store imported from `../stores/chart`. This store holds the `name` property of the chart that was last selected by the user.
    *   **`active_chart` (Derived Value, Lines [`frontend/src/charts/ChartSwitcher.svelte:16-18`](frontend/src/charts/ChartSwitcher.svelte:16)):** A Svelte `$derived` value. It determines the currently active chart by:
        1.  Trying to find a chart in the `charts` prop array whose `name` matches the value in `$lastActiveChartName`.
        2.  If no match is found (e.g., on first load or if the stored name is invalid), it defaults to the first chart in the `charts` array (`charts[0]`).
    *   **`shortcutPrevious` and `shortcutNext` (Derived Functions, Lines [`frontend/src/charts/ChartSwitcher.svelte:21-33`](frontend/src/charts/ChartSwitcher.svelte:21)):** These are `$derived` functions that dynamically generate `KeySpec` objects for keyboard shortcuts.
        *   `shortcutPrevious(index)`: Returns a `KeySpec` for the "Previous" chart ('C') if the button at `index` corresponds to the chart immediately preceding the `active_chart` (with wrap-around). Otherwise, returns `undefined`.
        *   `shortcutNext(index)`: Returns a `KeySpec` for the "Next" chart ('c') if the button at `index` corresponds to the chart immediately succeeding the `active_chart` (with wrap-around). Otherwise, returns `undefined`.
        These are used with the `use:keyboardShortcut` Svelte action on the selector buttons.

3.  **Rendering Logic (Lines [`frontend/src/charts/ChartSwitcher.svelte:36-56`](frontend/src/charts/ChartSwitcher.svelte:36)):**
    *   If `active_chart` is determined (i.e., `charts` prop is not empty):
        *   Renders the [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) component, passing the `active_chart` as its `chart` prop (Line [`frontend/src/charts/ChartSwitcher.svelte:37`](frontend/src/charts/ChartSwitcher.svelte:37)).
        *   It also passes [`<ConversionAndInterval />`](frontend/src/charts/ConversionAndInterval.svelte:1) as a child snippet to [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) (Line [`frontend/src/charts/ChartSwitcher.svelte:38`](frontend/src/charts/ChartSwitcher.svelte:38)), which will be rendered in the header area of the chart.
        *   Renders a `div` (conditionally hidden based on `$showCharts` store) containing the chart selector buttons (Lines [`frontend/src/charts/ChartSwitcher.svelte:40-55`](frontend/src/charts/ChartSwitcher.svelte:40)):
            *   Iterates through the `charts` prop array (`#each charts as chart, index (chart.name)`).
            *   For each `chart`, a `<button>` is rendered:
                *   `class:selected`: Applied if this `chart` is the current `active_chart`.
                *   `onclick`: Updates the `$lastActiveChartName` store to this `chart.name`.
                *   `use:keyboardShortcut`: Applies the `shortcutPrevious(index)` or `shortcutNext(index)` Svelte action if a `KeySpec` is returned by these derived functions for the current button.
                *   The button displays `chart.name` as its text.

4.  **Keyboard Shortcuts:**
    *   Uses the `keyboardShortcut` Svelte action (from `../keyboard-shortcuts`) to enable 'c' (next) and 'C' (previous) shortcuts. The shortcuts are dynamically assigned to the appropriate buttons next to/previous to the currently active chart button.

5.  **Styling (`<style>` block Lines [`frontend/src/charts/ChartSwitcher.svelte:58-93`](frontend/src/charts/ChartSwitcher.svelte:58)):**
    *   Styles for the button container `div` (margin, font size, color, text alignment).
    *   Styles for individual selector `button` elements (padding, borders, hover/selected states).
    *   Print-specific styles: Hides all chart selector buttons except for the one corresponding to the `selected` (active) chart.

**B. Data Structures:**
*   Relies on the `FavaChart` type (an interface or union type from [`./index.ts`](frontend/src/charts/index.ts:1)) and `KeySpec` type (from `../keyboard-shortcuts`).

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The component's purpose of switching between charts is clear. The use of `$derived` for `active_chart` and the dynamic shortcut assignment is logical.
*   **Complexity:** Moderate. It manages the selection state via a store, dynamically renders a child component based on this state, and implements a slightly complex derived logic for assigning keyboard shortcuts to specific buttons in a loop.
*   **Maintainability:** Good. The primary way to change the available charts is by modifying the `charts` prop passed to it. The internal logic should adapt.
*   **Testability:** Difficult. Testing this component would involve:
    *   A Svelte component testing environment.
    *   Mocking the `charts` prop with various `FavaChart` objects.
    *   Mocking Svelte stores (`$lastActiveChartName`, `$showCharts`).
    *   Mocking child components ([`Chart.svelte`](frontend/src/charts/Chart.svelte:1), [`ConversionAndInterval.svelte`](frontend/src/charts/ConversionAndInterval.svelte:1)).
    *   Verifying that the correct chart is rendered and that button clicks update the store.
    *   Testing the keyboard shortcut integration would be particularly challenging, likely requiring advanced mocking of the `keyboardShortcut` action or end-to-end style tests.
*   **Adherence to Best Practices & Idioms:**
    *   Good use of Svelte stores for persistent state (`$lastActiveChartName`).
    *   Effective use of `$derived` for reactive calculations.
    *   Component composition by using [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) as a child.
    *   Integration of keyboard shortcuts enhances user experience.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data:** The `chart.name` property from the `FavaChart` objects is rendered as text content within the selector `<button>` elements (Line [`frontend/src/charts/ChartSwitcher.svelte:52`](frontend/src/charts/ChartSwitcher.svelte:52)). This is safe due to Svelte's default text escaping. The `active_chart` object is passed to the child [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) component; any XSS risk would depend on how [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) and its subsequent children handle and render data from this object.
*   **Secrets Management:** N/A. Chart data is not expected to contain secrets.
*   **Input Validation & Sanitization:** The component assumes that the `charts` prop is an array of valid `FavaChart` objects. No explicit validation is performed here. It relies on the data source to provide well-formed chart objects.
*   **Error Handling & Logging:**
    *   If the `charts` prop is an empty array, the component will render nothing, as `active_chart` would be undefined.
    *   If `$lastActiveChartName` refers to a chart name not present in the current `charts` array, `active_chart` gracefully defaults to `charts[0]`.
*   **Post-Quantum Security Considerations:** N/A. This is a UI rendering component.

### V. Improvement Recommendations & Technical Debt

*   **Shortcut Assignment Logic:** The derived functions `shortcutPrevious` and `shortcutNext` calculate the `KeySpec` for each button within the `#each` loop. While functional, this means the derivation logic runs for every button. If performance were critical for a very large number of switchable charts (unlikely here), one might explore alternative ways to assign these specific shortcuts, perhaps by identifying the target buttons outside the loop. However, for typical use cases, this is unlikely to be an issue.
*   The component is well-structured and does not exhibit significant technical debt.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Uses [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) as a child component to render the active chart.
*   **System-Level Interactions:**
    *   **Svelte Stores:** Interacts with `lastActiveChartName` and `showCharts` stores from [`../stores/chart.ts`](frontend/src/stores/chart.ts:1).
    *   **Keyboard Shortcuts:** Uses `KeySpec` type and `keyboardShortcut` Svelte action from [`../keyboard-shortcuts.ts`](frontend/src/keyboard-shortcuts.ts:1).
    *   **Internationalization:** Uses the `_` function from [`../i18n.ts`](frontend/src/i18n.ts:1) for shortcut notes.
    *   **Child Components:** Renders [`ConversionAndInterval.svelte`](frontend/src/charts/ConversionAndInterval.svelte:1) as a child snippet within [`Chart.svelte`](frontend/src/charts/Chart.svelte:1).
    *   **Chart Data Types:** Depends on the `FavaChart` type definition (likely from [`./index.ts`](frontend/src/charts/index.ts:1)).
    *   **Application Structure:** This component is likely a key part of how reports with multiple chart visualizations are presented to the user.
## File: `frontend/src/charts/context.ts`

### I. Overview and Purpose

[`frontend/src/charts/context.ts`](frontend/src/charts/context.ts:1) defines and exports a Svelte derived store named `chartContext`. This store provides essential contextual information required for parsing chart data and rendering charts consistently across the Fava application. It consolidates data from various other Svelte stores related to currency conversion, operating currencies, and date formatting preferences.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`ChartContext` Interface (Lines [`frontend/src/charts/context.ts:8-13`](frontend/src/charts/context.ts:8)):**
    *   Defines the structure of the data provided by the `chartContext` store.
    *   `currencies: readonly string[]`: An array of currency strings that should be considered "active" or "relevant" for chart display. This list includes the user's defined operating currencies and is augmented by the currently selected conversion currency if it's not already part of the operating currencies.
    *   `dateFormat: (date: Date) => string`: A function that takes a `Date` object and returns a formatted date string. The specific formatting is determined by the user's currently selected reporting interval (e.g., "year", "month", "day").

2.  **`operatingCurrenciesWithConversion` Derived Store (Lines [`frontend/src/charts/context.ts:18-25`](frontend/src/charts/context.ts:18)):**
    *   **Purpose:** This internal derived store computes the list of currencies to be included in the `ChartContext`.
    *   **Functionality:**
        *   It derives its value from three other stores: `operating_currency` (from [`../stores/options`](../stores/options.ts:1)), `currencies` (likely all available currencies from [`../stores/index.ts`](../stores/index.ts:1)), and `conversion` (the currently selected conversion target from [`../stores/index.ts`](../stores/index.ts:1)).
        *   The logic is: if the selected `$conversion` currency is a valid currency (present in `$currencies`) AND it's not already part of the `$operating_currency` list, then the `$conversion` currency is added to a copy of the `$operating_currency` list.
        *   Otherwise, it just returns the original `$operating_currency` list.
    *   **Output:** An array of currency strings.

3.  **`chartContext` Derived Store (Lines [`frontend/src/charts/context.ts:27-33`](frontend/src/charts/context.ts:27)):**
    *   **Purpose:** The main export of this module. It provides the `ChartContext` object.
    *   **Functionality:**
        *   It derives its value from `operatingCurrenciesWithConversion` and `currentDateFormat` (from [`../stores/format`](../stores/format.ts:1)).
        *   It constructs and returns an object conforming to the `ChartContext` interface:
            *   `currencies`: Set to the value of `$operatingCurrenciesWithConversion`.
            *   `dateFormat`: Set to the value of `$currentDateFormat`.
    *   **Usage:** This store is likely consumed by chart data parsing functions (e.g., in [`./bar.ts`](frontend/src/charts/bar.ts:1), [`./line.ts`](frontend/src/charts/line.ts:1)) and potentially by chart rendering components that need access to this shared context.

**B. Data Structures:**
*   `ChartContext` interface.
*   Primarily deals with arrays of strings (currencies) and date formatting functions.

### III. Code Quality Assessment

*   **Readability & Clarity:** Excellent. The code is concise, and the purpose of each derived store and the `ChartContext` interface is clear from names and JSDoc comments.
*   **Complexity:** Low. The logic involves straightforward array manipulation and object construction based on other Svelte stores.
*   **Maintainability:** High. Changes to how operating currencies or date formats are determined would likely be made in the underlying stores, and `chartContext` would reactively update.
*   **Testability:** High. As a Svelte derived store, it can be tested by providing mock values for its dependent stores (`operating_currency`, `currencies`, `conversion`, `currentDateFormat`) and asserting the output of `get(chartContext)`.
*   **Adherence to Best Practices & Idioms:**
    *   Good use of Svelte derived stores to create reactive, memoized values from other state sources.
    *   Centralizing shared context for a specific domain (charts) is a good design pattern.

### IV. Security Analysis

*   **General Vulnerabilities:** N/A. This module primarily transforms and exposes data from other stores. It does not handle user input directly or perform actions that have security implications. The security of the currency strings or date format function would depend on the security of their source stores.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** N/A.
*   **Error Handling & Logging:** N/A. Relies on Svelte's store mechanisms.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   None apparent. The module is clean, focused, and effectively uses Svelte's reactivity.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   [`frontend/src/charts/helpers.ts`](frontend/src/charts/helpers.ts:1) does not directly import `chartContext` but relies on some of the same underlying stores (e.g., `operating_currency`, `currencies_sorted`).
    *   [`frontend/src/charts/ConversionAndInterval.svelte`](frontend/src/charts/ConversionAndInterval.svelte:1) interacts with `conversion` and `interval` stores, which indirectly influence `chartContext` via `currentDateFormat`.
*   **System-Level Interactions:**
    *   **Svelte Stores:**
        *   Depends on `conversion`, `currencies` (from [`../stores/index.ts`](../stores/index.ts:1)).
        *   Depends on `currentDateFormat` (from [`../stores/format.ts`](../stores/format.ts:1)).
        *   Depends on `operating_currency` (from [`../stores/options.ts`](../stores/options.ts:1)).
    *   **Chart Logic & Rendering:** The exported `chartContext` store is intended to be consumed by other modules in the `frontend/src/charts/` directory, such as data parsers (e.g., `bar()` in [`./bar.ts`](frontend/src/charts/bar.ts:1)) and potentially rendering components that need this contextual information.

## File: `frontend/src/charts/ConversionAndInterval.svelte`

### I. Overview and Purpose

[`frontend/src/charts/ConversionAndInterval.svelte`](frontend/src/charts/ConversionAndInterval.svelte:1) is a Svelte component that provides UI elements for selecting the currency conversion strategy and the time interval for charts and reports. It uses two instances of a reusable [`SelectCombobox.svelte`](frontend/src/charts/SelectCombobox.svelte:1) component to offer these choices to the user. The selections made in this component update global Svelte stores, which in turn affect how financial data is processed and displayed throughout the application.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props:** This component does not explicitly define or receive props in the traditional Svelte 3/4 way (no `export let ...`). It directly interacts with Svelte 5 runes and global stores.

2.  **Store Interactions:**
    *   `$conversion` (from [`../stores/index.ts`](../stores/index.ts:1)): A writable Svelte store bound to the value of the first `SelectCombobox`. This store holds the currently selected currency conversion key (e.g., "at_cost", "at_value", "units", or a currency symbol like "USD").
    *   `$interval` (from [`../stores/index.ts`](../stores/index.ts:1)): A writable Svelte store bound to the value of the second `SelectCombobox`. This store holds the currently selected time interval key (e.g., "year", "month", "day").
    *   `$conversions` (from [`../stores/chart.ts`](../stores/chart.ts:1)): A readable Svelte store providing the list of available conversion options (strings) to populate the first `SelectCombobox`.

3.  **UI Rendering:**
    *   **Conversion Selector (Lines [`frontend/src/charts/ConversionAndInterval.svelte:25-30`](frontend/src/charts/ConversionAndInterval.svelte:25)):**
        *   Renders a [`SelectCombobox.svelte`](frontend/src/charts/SelectCombobox.svelte:1) component.
        *   `bind:value={$conversion}`: Two-way binds the combobox's selected value to the `$conversion` store.
        *   `options={$conversions}`: Populates the combobox with options from the `$conversions` store.
        *   `description={conversion_description}`: Uses the `conversion_description` local function to provide human-readable labels for each conversion option.
        *   `multiple_select={is_currency_conversion}`: Uses the `is_currency_conversion` local function to determine if the combobox should allow multiple selections (though `SelectCombobox` itself might not directly support this; this prop might be for styling or specific behavior within `SelectCombobox` if it's designed to handle it). *Self-correction: `SelectCombobox` is likely a single-select component. This prop might influence its behavior or display if a currency is chosen, perhaps enabling a different mode or related UI element not visible here.*
    *   **Interval Selector (Lines [`frontend/src/charts/ConversionAndInterval.svelte:32-36`](frontend/src/charts/ConversionAndInterval.svelte:32)):**
        *   Renders a second [`SelectCombobox.svelte`](frontend/src/charts/SelectCombobox.svelte:1) component.
        *   `bind:value={$interval}`: Two-way binds the combobox's selected value to the `$interval` store.
        *   `options={INTERVALS}`: Populates the combobox with predefined interval options from `INTERVALS` (imported from `../lib/interval`).
        *   `description={(o: string) => intervalLabel(getInterval(o))}`: Uses `intervalLabel` and `getInterval` (from `../lib/interval`) to provide human-readable labels for each interval option.

4.  **Helper Functions:**
    *   **`conversion_description(option: string)` (Lines [`frontend/src/charts/ConversionAndInterval.svelte:8-19`](frontend/src/charts/ConversionAndInterval.svelte:8)):**
        *   Takes a conversion option key (string).
        *   Returns a translated, human-readable description for the option using `_()` (from `../i18n`) and `format()` for currency options.
    *   **`is_currency_conversion(option: string)` (Lines [`frontend/src/charts/ConversionAndInterval.svelte:21-23`](frontend/src/charts/ConversionAndInterval.svelte:21)):**
        *   Takes a conversion option key.
        *   Returns `true` if the option represents a specific currency (i.e., it's not one of "at_cost", "at_value", "units").

**B. Data Structures:**
*   Interacts with arrays of strings for combobox options (`$conversions`, `INTERVALS`).
*   Selected values are strings.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The component's purpose of providing conversion and interval selection is clear. The use of helper functions for descriptions enhances readability.
*   **Complexity:** Low. It primarily acts as a configurator for two `SelectCombobox` components, binding their values to global stores.
*   **Maintainability:** High. Changes to available conversion options would be managed in the `$conversions` store. Changes to interval options would be in `INTERVALS`. The display logic is straightforward.
*   **Testability:** Moderate. Requires a Svelte component testing environment. Key aspects to test would be:
    *   Correct rendering of the two `SelectCombobox` components.
    *   Ensuring options are passed correctly.
    *   Verifying that interactions with the comboboxes (selection changes) update the corresponding Svelte stores (`$conversion`, `$interval`). This would involve mocking the stores and the child `SelectCombobox` component or testing its emitted events if applicable.
*   **Adherence to Best Practices & Idioms:**
    *   Good use of component composition ([`SelectCombobox.svelte`](frontend/src/charts/SelectCombobox.svelte:1)).
    *   Effective use of Svelte stores for managing global application state.
    *   Separation of description logic into helper functions.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Descriptions (Low Risk):** The `conversion_description` and interval description functions use `_()` and `format()` from `../i18n`. If the translated strings themselves (fetched by `_()`) contained malicious HTML and the `SelectCombobox` (or underlying select/option elements) rendered these descriptions using `@html` or `innerHTML`, XSS could be possible. However, standard rendering of text in select options is typically safe. The `format` function also needs to be safe against injecting HTML through its `currency` parameter if that parameter could ever be attacker-controlled and the template string was malicious (unlikely for i18n keys).
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** The component relies on predefined lists for options (`$conversions`, `INTERVALS`). User interaction is limited to selecting from these lists.
*   **Error Handling & Logging:** No explicit error handling.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **`multiple_select` Prop:** The `multiple_select={is_currency_conversion}` prop passed to the conversion `SelectCombobox` is intriguing. If `SelectCombobox` is strictly single-select, this prop might be unused or misleading. If it *does* enable some form of multi-select behavior or related UI for currency conversions, that interaction isn't fully evident from this component alone and would depend on `SelectCombobox`'s implementation. Clarifying its role or ensuring `SelectCombobox` handles it appropriately would be good.
*   No significant technical debt apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Does not directly interact with [`frontend/src/charts/context.ts`](frontend/src/charts/context.ts:1) or [`frontend/src/charts/helpers.ts`](frontend/src/charts/helpers.ts:1) within this component, but the stores it updates (`conversion`, `interval`) are used by `chartContext` and other chart-related logic.
*   **System-Level Interactions:**
    *   **Svelte Stores:**
        *   Reads from and writes to `$conversion` and `$interval` (from [`../stores/index.ts`](../stores/index.ts:1)).
        *   Reads from `$conversions` (from [`../stores/chart.ts`](../stores/chart.ts:1)).
    *   **Child Component:** Uses [`SelectCombobox.svelte`](frontend/src/charts/SelectCombobox.svelte:1) for the UI.
    *   **Internationalization (`../i18n.ts`):** Uses `_` and `format` for descriptions.
    *   **Interval Utilities (`../lib/interval.ts`):** Uses `getInterval`, `intervalLabel`, and `INTERVALS`.
    *   **Application State:** The selections made in this component have a global impact on data display and processing throughout Fava, as they modify core Svelte stores. This component is often rendered as part of a chart's header controls (e.g., via [`ChartSwitcher.svelte`](frontend/src/charts/ChartSwitcher.svelte:1) passing it to [`Chart.svelte`](frontend/src/charts/Chart.svelte:1)).

## File: `frontend/src/charts/helpers.ts`

### I. Overview and Purpose

[`frontend/src/charts/helpers.ts`](frontend/src/charts/helpers.ts:1) provides a collection of utility functions and derived Svelte stores specifically for supporting chart generation and rendering in Fava. These helpers include functions for URL generation, numerical extent manipulation (padding, including zero), tick filtering for axes, color generation, and pre-configured D3 ordinal color scales.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`urlForTimeFilter(date: Date): string` (Lines [`frontend/src/charts/helpers.ts:14-18`](frontend/src/charts/helpers.ts:14)):**
    *   **Purpose:** Generates a URL that, when navigated to, will set Fava's time filter to the specified `date`.
    *   **Functionality:**
        *   Creates a new `URL` object based on `window.location.href`.
        *   Formats the input `date` using the `currentTimeFilterDateFormat` Svelte store (which provides a date formatting function appropriate for the current global time interval).
        *   Sets the `time` search parameter on the URL to this formatted date string.
        *   Returns the modified URL as a string.

2.  **Extent Manipulation Functions:**
    *   **`includeZero([from, to])` (Lines [`frontend/src/charts/helpers.ts:25-32`](frontend/src/charts/helpers.ts:25)):**
        *   Takes a numerical extent (a two-element array `[min, max]`) or `[undefined, undefined]`.
        *   Ensures that 0 is included within the returned extent. If the input is undefined, returns `[0, 1]`.
        *   Useful for chart Y-axes where the zero baseline should always be visible.
    *   **`padExtent([from, to])` (Lines [`frontend/src/charts/helpers.ts:39-47`](frontend/src/charts/helpers.ts:39)):**
        *   Takes a numerical extent or `[undefined, undefined]`.
        *   Pads the extent by a small factor (3% on each side: `diff * 0.03`). If input is undefined, returns `[0, 1]`.
        *   Helps prevent chart elements from touching the very edges of the plotting area.

3.  **`filterTicks(domain: string[], count: number): string[]` (Lines [`frontend/src/charts/helpers.ts:54-60`](frontend/src/charts/helpers.ts:54)):**
    *   **Purpose:** Reduces the number of ticks displayed on an axis to prevent overlap.
    *   **Functionality:**
        *   If the input `domain` (array of tick values, typically strings) has length less than or equal to `count`, returns the original domain.
        *   Otherwise, it calculates a step (`showIndices`) and filters the domain to pick approximately `count` evenly spaced ticks.

4.  **Color Generation:**
    *   **`hclColorRange(count: number, chroma = 45, luminance = 70): string[]` (Lines [`frontend/src/charts/helpers.ts:71-83`](frontend/src/charts/helpers.ts:71)):**
        *   Generates an array of `count` distinct colors using the HCL (Hue-Chroma-Luminance) color space. HCL is often preferred for data visualization as it can produce colors that are more perceptually uniform in brightness.
        *   Calculates hues by distributing them around the color wheel, with an offset.
        *   Uses `d3-color.hcl()` to create color objects and then converts them to string representations.
    *   **`colors10 = hclColorRange(10)` (Line [`frontend/src/charts/helpers.ts:85`](frontend/src/charts/helpers.ts:85)):** Pre-generated array of 10 HCL colors.
    *   **`colors15 = hclColorRange(15, 30, 80)` (Line [`frontend/src/charts/helpers.ts:86`](frontend/src/charts/helpers.ts:86)):** Pre-generated array of 15 HCL colors with slightly different chroma/luminance.

5.  **D3 Ordinal Color Scales (Derived Stores):**
    *   These are D3 `scaleOrdinal` instances, configured with specific color ranges and domains derived from Svelte stores. They are used to consistently map categorical data (like account names or currency codes) to colors.
    *   **`scatterplotScale = scaleOrdinal(colors10)` (Line [`frontend/src/charts/helpers.ts:94`](frontend/src/charts/helpers.ts:94)):** A simple ordinal scale using `colors10`. Its domain will be implicitly set by D3 based on the data it first encounters.
    *   **`treemapScale = derived(accounts, ($accounts) => scaleOrdinal(colors15).domain($accounts))` (Lines [`frontend/src/charts/helpers.ts:96-98`](frontend/src/charts/helpers.ts:96)):**
        *   Derives from the `accounts` store (list of all accounts).
        *   Creates an ordinal scale with `colors15` and explicitly sets its domain to the current list of `$accounts`. This ensures consistent color mapping for accounts in treemaps.
    *   **`sunburstScale = derived(accounts, ($accounts) => scaleOrdinal(colors10).domain($accounts))` (Lines [`frontend/src/charts/helpers.ts:100-102`](frontend/src/charts/helpers.ts:100)):**
        *   Similar to `treemapScale` but uses `colors10`. For sunburst charts.
    *   **`currenciesScale = derived([operating_currency, currencies_sorted], ([$operating_currency, $currencies_sorted]) => scaleOrdinal(colors10).domain([...$operating_currency, ...$currencies_sorted]))` (Lines [`frontend/src/charts/helpers.ts:104-111`](frontend/src/charts/helpers.ts:104)):**
        *   Derives from `operating_currency` and `currencies_sorted` stores.
        *   Creates an ordinal scale with `colors10`. Its domain is explicitly set to be the operating currencies first, followed by all other sorted currencies. This prioritizes operating currencies in the color mapping and ensures stability. This scale is used by [`ChartLegend.svelte`](frontend/src/charts/ChartLegend.svelte:1) and various chart components.

**B. Data Structures:**
*   Deals with numerical extents (`[number, number]`).
*   Arrays of strings (for tick domains, color arrays).
*   D3 scale objects (`ScaleOrdinal`).

### III. Code Quality Assessment

*   **Readability & Clarity:** Very good. Functions are generally small, well-named, and have clear JSDoc comments explaining their purpose. The use of derived stores for color scales is idiomatic Svelte.
*   **Complexity:** Low to Moderate. The color generation and scale setup involve some D3-specific concepts, but the individual functions are not overly complex.
*   **Maintainability:** High. Utility functions are self-contained. Color schemes or scale configurations can be modified in a centralized place.
*   **Testability:**
    *   Pure functions like `includeZero`, `padExtent`, `filterTicks`, and `hclColorRange` are highly testable.
    *   `urlForTimeFilter` is testable by mocking `window.location` and the `currentTimeFilterDateFormat` store.
    *   Derived stores (`treemapScale`, `sunburstScale`, `currenciesScale`) can be tested by providing mock values for their dependent stores and checking the resulting D3 scale's properties (e.g., its domain and range, or output for given inputs).
*   **Adherence to Best Practices & Idioms:**
    *   Good use of pure functions for data manipulation.
    *   Effective use of D3 for color generation and scales.
    *   Leveraging Svelte derived stores for reactive color scales that update when underlying data (like account lists or operating currencies) changes.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **`urlForTimeFilter` (Low Risk):** This function modifies `window.location.href` by adding a `time` search parameter. The value of this parameter is derived from a date formatted by `currentTimeFilterDateFormat`. If the date formatting logic or the input `date` could be manipulated to inject malicious characters that are then misinterpreted by the server or client-side URL parsing, it could theoretically lead to issues. However, standard date formatting and `URLSearchParams.set` typically handle encoding safely. The main concern would be open redirect if `window.location.href` itself could be attacker-controlled before this function is called, but that's an external precondition.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** Functions generally expect inputs of specific types (e.g., `Date`, `string[]`). No explicit security-focused sanitization is performed as these are internal helper functions operating on data assumed to be from trusted sources within the application.
*   **Error Handling & Logging:** No explicit error handling in most functions. They rely on JavaScript's default behavior for incorrect input types.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Color Palette Accessibility:** While HCL aims for perceptual uniformity, it's always good to test generated color palettes for accessibility, especially for users with color vision deficiencies. Tools exist for this. The chosen chroma/luminance values in `hclColorRange` and `colors15` might have been selected with this in mind, but it's worth noting.
*   **Domain Stability for `scatterplotScale`:** `scatterplotScale` is initialized without an explicit domain. This means its color mapping can change if the order or set of data points it first encounters changes. If stable color mapping is desired for scatter plots across different views/data subsets, its domain might also need to be derived from relevant data stores, similar to the other scales.
*   No significant technical debt is apparent. The module is well-organized.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   [`frontend/src/charts/ConversionAndInterval.svelte`](frontend/src/charts/ConversionAndInterval.svelte:1) does not directly use these helpers, but the stores it modifies (`interval`) affect `currentTimeFilterDateFormat` which is used by `urlForTimeFilter`.
    *   [`frontend/src/charts/context.ts`](frontend/src/charts/context.ts:1) uses some of the same underlying stores (e.g., `operating_currency`, `currencies`) that also feed into `currenciesScale`.
*   **System-Level Interactions:**
    *   **D3 Libraries:** Uses `d3-color` (hcl) and `d3-scale` (scaleOrdinal).
    *   **Svelte Stores:**
        *   Reads from `accounts`, `currencies_sorted` (from [`../stores/index.ts`](../stores/index.ts:1)).
        *   Reads from `currentTimeFilterDateFormat` (from [`../stores/format.ts`](../stores/format.ts:1)).
        *   Reads from `operating_currency` (from [`../stores/options.ts`](../stores/options.ts:1)).
    *   **Browser API:** `urlForTimeFilter` uses `window.location.href` and `URL`.
    *   **Various Chart Components:** Many Svelte chart components (e.g., [`BarChart.svelte`](frontend/src/charts/BarChart.svelte:1), [`LineChart.svelte`](frontend/src/charts/LineChart.svelte:1), [`ChartLegend.svelte`](frontend/src/charts/ChartLegend.svelte:1), hierarchy charts) will consume the exported color scales (`treemapScale`, `sunburstScale`, `currenciesScale`) and potentially use helper functions like `padExtent`, `includeZero`, `filterTicks`.
## File: `frontend/src/charts/hierarchy.ts`

### I. Overview and Purpose

[`frontend/src/charts/hierarchy.ts`](frontend/src/charts/hierarchy.ts:1) is a TypeScript module dedicated to processing and preparing data for hierarchical charts like treemaps, sunbursts, and icicle charts. It defines data structures for account hierarchies, provides validators for raw input data, and includes the `HierarchyChart` class which encapsulates the processed D3 hierarchy data for multiple currencies. A key function, `hierarchy_from_parsed_data`, transforms validated tree-like account data into D3 hierarchy structures, and `hierarchy` serves as the main factory function to parse raw JSON and produce `HierarchyChart` instances.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Type Definitions:**
    *   `AccountTreeNode` (Lines [`frontend/src/charts/hierarchy.ts:27-34`](frontend/src/charts/hierarchy.ts:27)): Represents the raw, validated tree node structure for an account, including its balance, balance of children, cost, and whether it has transactions.
    *   `AccountHierarchyDatum` (Lines [`frontend/src/charts/hierarchy.ts:37-41`](frontend/src/charts/hierarchy.ts:37)): The data structure used within D3 hierarchy nodes after processing. Includes `account`, `balance`, and a `dummy` flag (used by `addInternalNodesAsLeaves`).
    *   `AccountHierarchyInputDatum` (Lines [`frontend/src/charts/hierarchy.ts:43-46`](frontend/src/charts/hierarchy.ts:43)): Input structure for `addInternalNodesAsLeaves`.
    *   `AccountHierarchyNode` (Line [`frontend/src/charts/hierarchy.ts:49`](frontend/src/charts/hierarchy.ts:49)): Type alias for a D3 `HierarchyNode<AccountHierarchyDatum>`.

2.  **`addInternalNodesAsLeaves(inputDatum)` (Lines [`frontend/src/charts/hierarchy.ts:57-68`](frontend/src/charts/hierarchy.ts:57)):**
    *   **Purpose:** Transforms an input account hierarchy. If an internal node (an account with children) also has its own balance, this function effectively duplicates that node as a "dummy" leaf node among its children. This is crucial for treemaps where only leaf nodes are typically rendered, ensuring that the balances of parent accounts are also visualized.
    *   **Functionality:** Recursively processes the tree. If a node has children, it maps over them, calling itself, and then appends a new dummy leaf node representing the parent's own balance. The original parent node then has its balance cleared (effectively becoming a structural node).

3.  **`HierarchyChart` Class (Lines [`frontend/src/charts/hierarchy.ts:70-88`](frontend/src/charts/hierarchy.ts:70)):**
    *   **Properties:**
        *   `type = "hierarchy"`: Identifies the chart type.
        *   `name: string | null`: Optional name/title for the chart.
        *   `data: ReadonlyMap<string, AccountHierarchyNode>`: A map where keys are currency strings and values are the root D3 `AccountHierarchyNode` for that currency.
        *   `currencies: readonly string[]`: An array of all currency keys present in the `data` map.
        *   `treemap_currency: Writable<string> | null`: A Svelte writable store holding the currency currently selected for treemap display. Initialized to the first available currency or null if no currencies.
    *   **Constructor:** Initializes properties, populates `currencies`, and sets up `treemap_currency`.

4.  **Validators:**
    *   `inventory = record(number)` (Line [`frontend/src/charts/hierarchy.ts:93`](frontend/src/charts/hierarchy.ts:93)): A validator for balance/cost objects (records mapping currency strings to numbers).
    *   `account_hierarchy_validator: Validator<AccountTreeNode>` (Lines [`frontend/src/charts/hierarchy.ts:95-105`](frontend/src/charts/hierarchy.ts:95)): A recursive validator for the raw `AccountTreeNode` structure. It uses `lazy()` for the `children` property to handle recursion and applies `sort_children` (which sorts by account name) after validating children.

5.  **Data Processing Functions:**
    *   **`hierarchy_from_parsed_data(label, data, chartContext)` (Lines [`frontend/src/charts/hierarchy.ts:107-134`](frontend/src/charts/hierarchy.ts:107)):**
        *   Takes a label, the validated `AccountHierarchyInputDatum` (root of the account tree), and `ChartContext`.
        *   Calls `addInternalNodesAsLeaves` to preprocess the tree structure.
        *   For each currency in `chartContext.currencies`:
            *   Creates a D3 hierarchy using `d3Hierarchy(root)`.
            *   Calculates the total `root_balance` for that currency.
            *   Determines the `sign` of the `root_balance` (or defaults to 1 if zero). This is used to ensure that the treemap/sunburst visualizes either all positive contributions or all negative contributions consistently.
            *   Uses `d3Node.sum()` to assign values to nodes based on their balance for the current currency, considering the `sign` (e.g., `sign * Math.max(sign * (d.balance[currency] ?? 0), 0)` effectively takes absolute values if sign is 1, or negative absolute values if sign is -1, but only if they match the overall sign).
            *   Sorts the hierarchy nodes so that larger values appear more prominently.
            *   Stores this D3 hierarchy node in a map keyed by currency.
        *   Filters out any currency hierarchies where the total value is zero or null.
        *   Returns a new `HierarchyChart` instance.
    *   **`hierarchy(label, json, chartContext)` Factory Function (Lines [`frontend/src/charts/hierarchy.ts:141-157`](frontend/src/charts/hierarchy.ts:141)):**
        *   The main entry point for creating `HierarchyChart` instances from raw API JSON.
        *   Handles a legacy data format where the root might be nested under `{"modifier": number, "root": ...}` by checking with `hierarchy_data_with_modifier` validator and issuing a warning via `notify_warn` if the old format is detected.
        *   Validates the (potentially unwrapped) root JSON data using `account_hierarchy_validator`.
        *   If valid, calls `hierarchy_from_parsed_data` to process it and returns the `Result<HierarchyChart, ValidationError>`.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. Type definitions are clear. The purpose of `addInternalNodesAsLeaves` is well-commented. D3 hierarchy manipulation can be inherently complex, but the steps are logical.
*   **Complexity:** Moderate to High. The recursive nature of `addInternalNodesAsLeaves` and the D3 hierarchy processing (summing, sorting, handling signs) for each currency contribute to the complexity. The recursive validator is also a more advanced pattern.
*   **Maintainability:** Moderate. Changes to the D3 hierarchy processing logic would require careful understanding. Adding new ways to value/sort nodes would involve modifying `hierarchy_from_parsed_data`.
*   **Testability:** Moderate.
    *   `addInternalNodesAsLeaves` is a pure function and can be tested with various tree structures.
    *   The `HierarchyChart` class can be tested.
    *   `account_hierarchy_validator` can be unit tested.
    *   `hierarchy_from_parsed_data` and the main `hierarchy` factory function are more complex to test, requiring mock `ChartContext`, various JSON inputs, and assertions on the resulting D3 hierarchy structures (e.g., node values, children counts, sort order).
*   **Adherence to Best Practices & Idioms:**
    *   Good use of D3 for hierarchy creation and manipulation.
    *   Separation of raw data validation from D3 processing.
    *   The `HierarchyChart` class encapsulates the multi-currency D3 hierarchies.
    *   Returning a `Result` type from the factory function is good for error handling.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **Data Integrity:** Relies on the `account_hierarchy_validator` to ensure the structural integrity of input JSON. If this validator were flawed or too permissive, malformed data could lead to runtime errors during D3 processing.
    *   **Performance with Large Hierarchies:** Deeply nested or extremely wide hierarchies could lead to performance issues during recursive processing (`addInternalNodesAsLeaves`, D3 hierarchy building, summing, sorting), potentially impacting UI responsiveness. This is more of a performance/DoS concern than a typical security vulnerability unless it can be triggered with relatively small malicious input that causes disproportionate computation.
*   **Secrets Management:** N/A. Account names and balances are not secrets.
*   **Input Validation & Sanitization:** The `account_hierarchy_validator` is the primary defense for input data structure.
*   **Error Handling & Logging:** The `hierarchy` factory function returns a `Result` object, allowing callers to handle validation errors. It also uses `notify_warn` for deprecation warnings.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Clarity of `sign` Logic:** The logic in `hierarchy_from_parsed_data` involving `sign` and `Math.max(sign * balance, 0)` is a bit dense. A comment explaining *why* this specific approach is taken (e.g., to handle charts of either income or expenses consistently, or to ensure treemap values are positive) would improve readability.
*   **Validator for `hierarchy_data_with_modifier`:** The `root` property is validated as `unknown` ([`frontend/src/charts/hierarchy.ts:138`](frontend/src/charts/hierarchy.ts:138)). While the subsequent call to `account_hierarchy_validator` handles the actual structure, it might be slightly cleaner if this validator also used `lazy(() => account_hierarchy_validator)` for the root if the intent is to validate it immediately. However, the current two-step approach (check for modifier, then validate root) works.
*   The sorting of children by `sort_by_strings` ([`frontend/src/charts/hierarchy.ts:100`](frontend/src/charts/hierarchy.ts:100)) happens during validation. This is a side effect within a validator, which is slightly unconventional but ensures children are always sorted in the parsed data.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   [`HierarchyContainer.svelte`](frontend/src/charts/HierarchyContainer.svelte:1) will import and use the `HierarchyChart` class and related types.
    *   [`Icicle.svelte`](frontend/src/charts/Icicle.svelte:1) (and other hierarchy chart components like `Sunburst.svelte`, `Treemap.svelte`) will consume `AccountHierarchyNode` data from a `HierarchyChart` instance.
*   **System-Level Interactions:**
    *   **D3.js Library:** Heavily uses `d3-hierarchy` (hierarchy, HierarchyNode) and `d3-array` (sum).
    *   **Svelte Stores:** The `HierarchyChart` class creates a `writable` store for `treemap_currency`.
    *   **Validation Library (`../lib/validation`):** Core dependency for defining `account_hierarchy_validator`.
    *   **Result Utilities (`../lib/result`):** Used for the return type of `hierarchy()`.
    *   **Notification System (`../notifications`):** Uses `notify_warn`.
    *   **Sorting Utilities (`../sort`):** Uses `sort_by_strings`.
    *   **Chart Context (`./context`):** Consumes `ChartContext` for the list of currencies.
    *   **API Data:** This module is designed to process JSON data (representing account trees) fetched from a backend API.

## File: `frontend/src/charts/HierarchyContainer.svelte`

### I. Overview and Purpose

[`frontend/src/charts/HierarchyContainer.svelte`](frontend/src/charts/HierarchyContainer.svelte:1) is a Svelte component that acts as a container and dispatcher for different types of hierarchical chart visualizations (Treemap, Sunburst, Icicle). Based on the current `hierarchyChartMode` (a Svelte store) and the provided `HierarchyChart` data, it dynamically renders the appropriate specific hierarchical chart component. For Sunburst and Icicle charts, which can display multiple currencies side-by-side, it iterates over the available currencies in the chart data and renders an instance of the component for each.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/HierarchyContainer.svelte:9-12`](frontend/src/charts/HierarchyContainer.svelte:9), Usage Line [`frontend/src/charts/HierarchyContainer.svelte:14`](frontend/src/charts/HierarchyContainer.svelte:14)):**
    *   `chart: HierarchyChart`: The processed hierarchical chart data object, an instance of the `HierarchyChart` class from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1). This object contains D3 hierarchy nodes mapped by currency.
    *   `width: number`: The total width available for rendering the chart(s).

2.  **Derived State & Store Interactions:**
    *   `data = $derived(chart.data)` (Line [`frontend/src/charts/HierarchyContainer.svelte:16`](frontend/src/charts/HierarchyContainer.svelte:16)): A map of currency to `AccountHierarchyNode` from the input `chart`.
    *   `currencies = $derived(chart.currencies)` (Line [`frontend/src/charts/HierarchyContainer.svelte:17`](frontend/src/charts/HierarchyContainer.svelte:17)): An array of currency strings available in the chart data.
    *   `treemap_currency = $derived(chart.treemap_currency)` (Line [`frontend/src/charts/HierarchyContainer.svelte:19`](frontend/src/charts/HierarchyContainer.svelte:19)): A Svelte writable store (or null) from the `chart` object, indicating the selected currency for treemap display.
    *   `mode = $derived($hierarchyChartMode)` (Line [`frontend/src/charts/HierarchyContainer.svelte:20`](frontend/src/charts/HierarchyContainer.svelte:20)): The current display mode for hierarchical charts (e.g., "treemap", "sunburst", "icicle"), read from the `hierarchyChartMode` Svelte store (from `../stores/chart`).
    *   `treemap = $derived(mode === "treemap" ? data.get($treemap_currency ?? "") : undefined)` (Lines [`frontend/src/charts/HierarchyContainer.svelte:21-23`](frontend/src/charts/HierarchyContainer.svelte:21)): The D3 hierarchy node for the selected treemap currency, if mode is "treemap" and a currency is selected.
    *   `treemap_height`, `sunburst_height`, `icicle_height` (Lines [`frontend/src/charts/HierarchyContainer.svelte:25-27`](frontend/src/charts/HierarchyContainer.svelte:25)): Calculated heights for the different chart types. Treemap and Icicle heights are responsive to width, while Sunburst has a fixed height.

3.  **Rendering Logic (Lines [`frontend/src/charts/HierarchyContainer.svelte:30-73`](frontend/src/charts/HierarchyContainer.svelte:30)):**
    *   **Empty State (Line [`frontend/src/charts/HierarchyContainer.svelte:30-35`](frontend/src/charts/HierarchyContainer.svelte:30)):** If `currencies.length === 0`, displays an SVG text message "Chart is empty."
    *   **Treemap Mode (Lines [`frontend/src/charts/HierarchyContainer.svelte:36-42`](frontend/src/charts/HierarchyContainer.svelte:36)):** If `mode === "treemap"` and `treemap` data (for the selected `$treemap_currency`) is available:
        *   Renders a single [`Treemap.svelte`](frontend/src/charts/Treemap.svelte:1) component, passing the `treemap` data, `$treemap_currency`, `width`, and `treemap_height`.
    *   **Sunburst Mode (Lines [`frontend/src/charts/HierarchyContainer.svelte:43-57`](frontend/src/charts/HierarchyContainer.svelte:43)):** If `mode === "sunburst"`:
        *   Renders an SVG container.
        *   Iterates through `[...data]` (all currency-hierarchy pairs). For each `[chart_currency, d]`:
            *   Renders a [`Sunburst.svelte`](frontend/src/charts/Sunburst.svelte:1) component within a transformed `<g>` element.
            *   The width for each Sunburst is `width / currencies.length` to fit them side-by-side.
    *   **Icicle Mode (Lines [`frontend/src/charts/HierarchyContainer.svelte:58-72`](frontend/src/charts/HierarchyContainer.svelte:58)):** If `mode === "icicle"`:
        *   Renders an SVG container.
        *   Iterates through `[...data]`. For each `[chart_currency, d]`:
            *   Renders an [`Icicle.svelte`](frontend/src/charts/Icicle.svelte:1) component within a transformed `<g>` element.
            *   The width for each Icicle is `width / currencies.length`.

**B. Data Structures:**
*   Primarily interacts with the `HierarchyChart` class instance and its properties (especially the `data` map of currency to `AccountHierarchyNode`).

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The component acts as a clear dispatcher based on the `mode`. The use of `$derived` for intermediate state is clean.
*   **Complexity:** Moderate. Manages different rendering paths for three types of hierarchical charts and handles multi-currency display for Sunburst/Icicle by iterating and dividing width.
*   **Maintainability:** Good. Adding a new hierarchical chart type would involve:
    1.  Importing the new component.
    2.  Adding a new mode to `hierarchyChartMode` store's possible values.
    3.  Adding an `else if mode === "newmode"` block in the template.
*   **Testability:** Difficult. Requires a Svelte component testing environment. Testing would involve:
    *   Mocking the `chart: HierarchyChart` prop with data for various currencies and structures.
    *   Mocking the `hierarchyChartMode` store to switch between modes.
    *   Asserting that the correct child components ([`Treemap.svelte`](frontend/src/charts/Treemap.svelte:1), [`Sunburst.svelte`](frontend/src/charts/Sunburst.svelte:1), [`Icicle.svelte`](frontend/src/charts/Icicle.svelte:1)) are rendered with appropriate props (data, width, height).
*   **Adherence to Best Practices & Idioms:**
    *   Effective use of Svelte's conditional rendering and component composition.
    *   Reactive updates based on Svelte stores and derived props.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data:** The `HierarchyChart` object (`chart` prop) contains account names and currency codes. These are passed down to child components ([`Treemap.svelte`](frontend/src/charts/Treemap.svelte:1), [`Sunburst.svelte`](frontend/src/charts/Sunburst.svelte:1), [`Icicle.svelte`](frontend/src/charts/Icicle.svelte:1)). Security depends on how these children render this text data. If they use Svelte's default text interpolation, it's safe. The "Chart is empty." message is translated using `_()` from i18n, which should also be safe if translations are plain text.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** Assumes the `chart` prop is a valid `HierarchyChart` instance, which itself should have been created from validated data by `hierarchy.ts`.
*   **Error Handling & Logging:** If `currencies.length === 0`, it displays a message. If `mode` is "treemap" but `$treemap_currency` is null or its data is missing, the treemap won't render, failing somewhat silently for that specific case.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Height Calculation:** `sunburst_height` is fixed at 500 ([`frontend/src/charts/HierarchyContainer.svelte:26`](frontend/src/charts/HierarchyContainer.svelte:26)), while treemap and icicle heights are responsive. Making sunburst height also responsive or configurable could be an improvement if fixed height is not always desirable.
*   **Repetitive Multi-Currency Logic:** The iteration and `<g transform>` logic for Sunburst and Icicle modes are very similar. If more multi-currency chart types were added, this could be abstracted into a helper component or function, but for two types, it's acceptable.
*   No major technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Critically depends on the `HierarchyChart` class and related types from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1).
    *   Renders [`Icicle.svelte`](frontend/src/charts/Icicle.svelte:1) as a child component.
*   **System-Level Interactions:**
    *   **Svelte Stores:** Reads from `hierarchyChartMode` (from `../stores/chart.ts`). The `chart.treemap_currency` is also a store.
    *   **Child Chart Components:** Dynamically renders [`Treemap.svelte`](frontend/src/charts/Treemap.svelte:1), [`Sunburst.svelte`](frontend/src/charts/Sunburst.svelte:1), in addition to `Icicle.svelte`.
    *   **Internationalization (`../i18n.ts`):** Uses `_()` for the "Chart is empty" message.
    *   **Parent Components:** This container is likely used within a more general chart display component like [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) when `chart.type` is "hierarchy".

## File: `frontend/src/charts/Icicle.svelte`

### I. Overview and Purpose

[`frontend/src/charts/Icicle.svelte`](frontend/src/charts/Icicle.svelte:1) is a Svelte component that renders an icicle chart visualization using SVG. Icicle charts are a way to represent hierarchical data, where nodes are arranged as adjacent rectangles, and the hierarchy flows typically from left-to-right or top-to-bottom. This component takes a D3 hierarchy node (specifically an `AccountHierarchyNode` from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1)) and dimensions as props, and uses D3's `partition` layout to calculate the positions and sizes of the rectangles. It includes features like tooltips, hover/focus interactions, and makes each node a clickable link to the corresponding account's report page.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/Icicle.svelte:15-20`](frontend/src/charts/Icicle.svelte:15), Usage Line [`frontend/src/charts/Icicle.svelte:22`](frontend/src/charts/Icicle.svelte:22)):**
    *   `data: AccountHierarchyNode`: The root D3 hierarchy node for the account data to be visualized.
    *   `currency: string`: The currency context for the values being displayed.
    *   `width: number`: The total width for the icicle chart.
    *   `height: number`: The total height for the icicle chart.

2.  **D3 Layout and Data Processing:**
    *   `root = $derived(partition<AccountHierarchyDatum>()(data))` (Line [`frontend/src/charts/Icicle.svelte:24`](frontend/src/charts/Icicle.svelte:24)): Uses D3's `partition` layout generator. The `partition` layout subdivides a root node's area among its children. For an icicle chart, this typically means `size` would be `[width, height]` or `[height, width]` depending on orientation, but here it seems to be applied to the `data` node directly, and then x/y coordinates (`d.x0, d.x1, d.y0, d.y1`) are used which are normalized by `partition` (0 to 1 range for depth, and 0 to 1 for breadth based on value).
    *   `nodes = $derived(root.descendants().filter((d) => !d.data.dummy))` (Line [`frontend/src/charts/Icicle.svelte:25`](frontend/src/charts/Icicle.svelte:25)): Gets all descendant nodes from the partitioned `root` and filters out any "dummy" nodes (which were added by `addInternalNodesAsLeaves` in `hierarchy.ts` and are not meant for direct rendering in this type of chart).

3.  **Interaction State:**
    *   `current: string | null = $state(null)` (Line [`frontend/src/charts/Icicle.svelte:27`](frontend/src/charts/Icicle.svelte:27)): A Svelte state variable to store the account name of the currently hovered/focused node. Used for highlighting.

4.  **Tooltip Generation:**
    *   **`tooltipText(d: AccountHierarchyNode)` (Lines [`frontend/src/charts/Icicle.svelte:29-39`](frontend/src/charts/Icicle.svelte:29)):**
        *   Generates content for the tooltip when hovering over a node `d`.
        *   Displays the node's value in the given `currency` (formatted using `$ctx.amount`) and its percentage of the root's total value (formatted using `formatPercentage`).
        *   Also displays the account name (`d.data.account`), emphasized.
        *   Uses `domHelpers` (from [`./tooltip`](./tooltip.ts:1)) to construct the tooltip content as an array of Nodes/strings.

5.  **SVG Rendering (Lines [`frontend/src/charts/Icicle.svelte:42-87`](frontend/src/charts/Icicle.svelte:42)):**
    *   Renders a top-level SVG `<g>` element.
    *   `onmouseleave`: Clears the `current` highlighted state.
    *   Iterates through `nodes` (`#each nodes as d (d.data.account)`). For each node `d`:
        *   Renders a `<g>` for the node.
        *   `use:followingTooltip={() => tooltipText(d)}`: Attaches the tooltip.
        *   `class:current`: Conditionally applies the `current` class if this node or its ancestor is the `current` hovered/focused node (`current.startsWith(account)`).
        *   Wraps the visual elements in an `<a>` tag (Lines [`frontend/src/charts/Icicle.svelte:56-84`](frontend/src/charts/Icicle.svelte:56)):
            *   `href={$urlForAccount(account)}`: Links to the account's report page.
            *   `aria-label={account}`.
            *   `onmouseover` / `onfocus`: Set `current = account` to highlight this node and its descendants.
            *   **`<rect>` Element (Lines [`frontend/src/charts/Icicle.svelte:66-74`](frontend/src/charts/Icicle.svelte:66)):**
                *   The visual representation of the icicle segment.
                *   `fill={$sunburstScale(account)}`: Color determined by the `sunburstScale` (note: uses sunburstScale, not a specific icicle scale).
                *   `width`, `height`, `x`, `y` attributes are calculated based on `d.x0, d.x1, d.y0, d.y1` (normalized coordinates from D3 `partition`) multiplied by the component's `width` and `height` props. This maps the normalized D3 layout coordinates to screen pixel coordinates.
            *   **`<text>` Element (Lines [`frontend/src/charts/Icicle.svelte:75-83`](frontend/src/charts/Icicle.svelte:75)):**
                *   Displays the leaf name of the account (`leaf(account)`).
                *   Positioned in the middle of the rectangle.
                *   `visibility`: Hidden if the rectangle height (`height * (d.x1 - d.x0)`) is too small (less than 14px).

6.  **Styling (`<style>` block Lines [`frontend/src/charts/Icicle.svelte:89-99`](frontend/src/charts/Icicle.svelte:89)):**
    *   CSS for hover/focus effects: When the main `<g>` is hovered or focused-within, child `<g>` elements are slightly faded (`opacity: 0.7`).
    *   The child `<g>` that has the `current` class (or is an ancestor of `current`) has its opacity restored to `1`.

**B. Data Structures:**
*   Consumes `AccountHierarchyNode` (D3 hierarchy node).
*   Generates `TooltipContent` (array of Nodes/strings).

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The use of D3 `partition` is standard for this type of chart. Svelte's reactive declarations and templating make the rendering logic relatively clear.
*   **Complexity:** Moderate. Involves D3 layout calculations, SVG rendering, and interaction handling (tooltips, hover/focus).
*   **Maintainability:** Moderate. Changes to the visual representation or interaction logic would involve modifying SVG attributes and event handlers. The core D3 layout logic is fairly stable.
*   **Testability:** Difficult. Requires a Svelte component testing environment. Would involve:
    *   Mocking the `data: AccountHierarchyNode` prop with various hierarchy structures.
    *   Mocking Svelte stores (`$ctx`, `$urlForAccount`, `$sunburstScale`).
    *   Snapshot testing for the rendered SVG.
    *   Testing interactions like hover/focus and tooltip generation.
*   **Adherence to Best Practices & Idioms:**
    *   Correct use of D3 `partition` layout for icicle charts.
    *   Integration of D3 with Svelte for rendering.
    *   Use of ARIA attributes (`aria-label`, `role="img"`) for accessibility.
    *   Providing tooltips and hover/focus feedback.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data (Low Risk):**
        *   Account names (`d.data.account`, `leaf(account)`) are rendered as text content in `<text>` elements and `aria-label`. This is generally safe with Svelte's escaping.
        *   Tooltip content generated by `tooltipText` uses `domHelpers.t` and `domHelpers.em`. If these helpers correctly create text nodes or escape content, it's safe. The currency amounts are formatted numbers.
        *   `$urlForAccount(account)` generates URLs. If `account` names could contain characters that break URL structure or inject JavaScript into `href` (very unlikely for typical account names and if `urlForAccount` is robust), it could be an issue.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** Assumes the input `data` prop is a valid D3 `AccountHierarchyNode` that has been processed from trusted/validated sources.
*   **Error Handling & Logging:** No explicit error handling. Relies on D3 and Svelte runtime.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Color Scale:** Uses `$sunburstScale` ([`frontend/src/charts/Icicle.svelte:68`](frontend/src/charts/Icicle.svelte:68)). While this might be intentional for consistency, if a different color scheme is desired specifically for icicle charts, a dedicated `icicleScale` could be created in [`./helpers.ts`](frontend/src/charts/helpers.ts:1).
*   **Text Visibility Logic:** The magic number `14` for text visibility ([`frontend/src/charts/Icicle.svelte:80`](frontend/src/charts/Icicle.svelte:80)) could be a named constant or prop for better clarity and configurability.
*   **Orientation:** This icicle chart appears to be horizontally oriented (hierarchy flows left-to-right, based on `width * (d.y1 - d.y0)` for rect width and `height * (d.x1 - d.x0)` for rect height). If a vertical orientation were needed, the x/y coordinate usage would need to be swapped.
*   No major technical debt.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   This component is rendered by [`HierarchyContainer.svelte`](frontend/src/charts/HierarchyContainer.svelte:1) when the mode is "icicle".
    *   It consumes `AccountHierarchyNode` data, which is prepared by logic in [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1).
*   **System-Level Interactions:**
    *   **D3.js Library:** Uses `d3-hierarchy` (partition).
    *   **Svelte Stores:**
        *   Reads from `$ctx` (from `../stores/format.ts`) for amount formatting.
        *   Reads from `$urlForAccount` (from `../helpers.ts`) for generating links.
        *   Reads from `$sunburstScale` (from [`./helpers.ts`](frontend/src/charts/helpers.ts:1)) for node colors.
    *   **Formatting Utilities (`../format.ts`):** Uses `formatPercentage`.
    *   **Account Utilities (`../lib/account.ts`):** Uses `leaf()` to get the leaf part of an account name.
    *   **Tooltip System (`./tooltip.ts`):** Uses `domHelpers` and `followingTooltip` action.