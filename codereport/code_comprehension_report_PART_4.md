# Batch 11: Chart Index, Line Chart Logic, and Line Chart Component

This batch focuses on the central chart parsing mechanism, the specific logic for handling line chart data (typically "balances" over time), and the Svelte component responsible for rendering these line/area charts.

## File: `frontend/src/charts/index.ts`

### I. Overview and Purpose

[`frontend/src/charts/index.ts`](frontend/src/charts/index.ts:1) serves as the primary dispatcher and parser for all chart data within Fava. It defines a union type `FavaChart` representing all supported chart types (Hierarchy, Bar, ScatterPlot, Line). The core functionality is encapsulated in the `parseChartData` function, which takes raw chart data (expected as an array of objects, each specifying a chart type, label, and its specific data), validates this overall structure, and then delegates the parsing of individual chart data to specialized parser functions based on the declared `type`. This module ensures that chart data from the backend is correctly transformed into the appropriate `FavaChart` objects used by the frontend rendering components.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`FavaChart` Type (Line [`frontend/src/charts/index.ts:34`](frontend/src/charts/index.ts:34)):**
    *   A TypeScript union type: `HierarchyChart | BarChart | ScatterPlot | LineChart`.
    *   This type represents any of the possible chart objects that the frontend can handle. The specific types (`HierarchyChart`, `BarChart`, etc.) are imported from their respective modules (e.g., [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1), [`./bar.ts`](frontend/src/charts/bar.ts:1)).

2.  **`parsers` Record (Lines [`frontend/src/charts/index.ts:20-32`](frontend/src/charts/index.ts:20)):**
    *   A constant object mapping chart type strings (e.g., "balances", "bar", "hierarchy", "scatterplot") to their corresponding parser functions.
    *   Each parser function is expected to take a `label` (string), `json` (unknown data), and a `$chartContext` (from [`./context.ts`](frontend/src/charts/context.ts:1)) and return a `Result<FavaChart, ValidationError>`.
    *   Example parsers imported:
        *   `balances` (from [`./line.ts`](frontend/src/charts/line.ts:1)): For line charts representing balances over time.
        *   `bar` (from [`./bar.ts`](frontend/src/charts/bar.ts:1)): For bar charts.
        *   `hierarchy` (from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1)): For hierarchical charts (treemap, sunburst, icicle).
        *   `scatterplot` (from [`./scatterplot.ts`](frontend/src/charts/scatterplot.ts:1)): For scatter plot charts.

3.  **`chart_data_validator` (Lines [`frontend/src/charts/index.ts:36-38`](frontend/src/charts/index.ts:36)):**
    *   A validator for the overall structure of the input chart data array.
    *   It expects an array of objects, where each object must have:
        *   `label: string`
        *   `type: string` (the key to look up in the `parsers` record)
        *   `data: unknown` (the raw data specific to this chart type, to be passed to the individual parser)

4.  **Custom Error Classes:**
    *   **`ChartValidationError` (Lines [`frontend/src/charts/index.ts:40-44`](frontend/src/charts/index.ts:40)):** Extends `Error`. Used when an individual chart parser returns a `ValidationError`. It includes the chart `type` and the original `cause` (the `ValidationError`).
    *   **`UnknownChartTypeError` (Lines [`frontend/src/charts/index.ts:46-50`](frontend/src/charts/index.ts:46)):** Extends `Error`. Used when a chart `type` specified in the input data does not have a corresponding entry in the `parsers` record.

5.  **`parseChartData(data: unknown, $chartContext: ChartContext)` Function (Lines [`frontend/src/charts/index.ts:52-67`](frontend/src/charts/index.ts:52)):**
    *   **Purpose:** The main entry point to parse an array of raw chart data objects.
    *   **Functionality:**
        1.  Validates the input `data` against `chart_data_validator`.
        2.  If the overall structure is valid, it uses `collect` (from `../lib/result`) to process each chart data object in the array.
        3.  For each object (`{ type, label, data }`):
            *   It looks up `parsers[type]`.
            *   If a parser exists, it calls `parser(label, data, $chartContext)`.
                *   If this individual parsing is successful (returns `Ok<FavaChart>`), the result is included.
                *   If it fails (returns `Err<ValidationError>`), the error is mapped to a new `ChartValidationError`.
            *   If no parser exists for the `type`, it returns an `Err<UnknownChartTypeError>`.
        4.  `collect` aggregates these results: if all individual parsings are successful, it returns `Ok<FavaChart[]>`. If any parsing fails, it returns the first `Err` encountered.
    *   **Return Type:** `Result<FavaChart[], ChartValidationError | UnknownChartTypeError>`.

**B. Data Structures:**
*   `FavaChart` (union type).
*   Input data structure: `Array<{ label: string, type: string, data: unknown }>`.
*   `ChartContext` (imported type, used by individual parsers).

### III. Code Quality Assessment

*   **Readability & Clarity:** Excellent. The purpose of the module as a central dispatcher is very clear. The use of a `parsers` map and the `Result` type for error handling makes the logic straightforward. Custom error types are well-defined.
*   **Complexity:** Low. The main logic in `parseChartData` is a clear sequence of validation, mapping, and error handling.
*   **Maintainability:** High. To add support for a new chart type:
    1.  Create a new parser module (e.g., `newchart.ts`) that exports a parser function and the chart's data type (e.g., `NewChart`).
    2.  Add `NewChart` to the `FavaChart` union type.
    3.  Import the parser function and add it to the `parsers` record with its corresponding type string.
    The rest of the logic in `parseChartData` remains unchanged.
*   **Testability:** High.
    *   `parseChartData` can be tested by providing various raw `data` inputs (valid, invalid structure, unknown types, data causing individual parser errors) and mock `ChartContext`.
    *   Assertions can be made on the `Result` (whether it's `Ok` or `Err`) and the type/content of the parsed charts or errors.
    *   Individual parsers are tested in their own modules.
*   **Adherence to Best Practices & Idioms:**
    *   Good use of a dispatcher pattern (the `parsers` map).
    *   Effective use of the `Result` type for robust error handling, avoiding exceptions for predictable parsing failures.
    *   Clear separation of concerns: this module handles routing to parsers; individual parsers handle type-specific logic.
    *   Use of a dedicated validator (`chart_data_validator`) for the input structure.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **Data Integrity:** The security and correctness of the parsed charts depend heavily on the individual parser functions (e.g., `bar`, `hierarchy`) and their respective validators. This module itself ensures the *structure* of the incoming array of chart definitions is as expected, but the content of `data: unknown` is passed through. If an individual parser has a vulnerability (e.g., mishandles malformed data leading to excessive computation or errors), that would be the source.
    *   **Resource Exhaustion (Indirect):** If a malicious actor could provide an extremely large array of chart definitions, or chart data that causes an individual parser to consume excessive resources, it could impact performance. The `collect` function processes each item; a very large number of items would naturally take longer.
*   **Secrets Management:** N/A. Chart definitions (labels, types) are not secrets.
*   **Input Validation & Sanitization:** `chart_data_validator` validates the structure of the array of chart definitions. The `unknown` data payload for each chart is the responsibility of the individual parsers.
*   **Error Handling & Logging:** Excellent error handling using the `Result` type and custom error classes. This allows callers to gracefully handle parsing failures. No direct logging is done here, but the error objects provide sufficient information for callers to log if needed.
*   **Post-Quantum Security Considerations:** N/A. This is data parsing logic.

### V. Improvement Recommendations & Technical Debt

*   None apparent. The module is clean, well-structured, and robust.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Imports `LineChart` type and `balances` parser from [`./line.ts`](frontend/src/charts/line.ts:1).
*   **System-Level Interactions:**
    *   **Result Library (`../lib/result`):** Uses `collect`, `err`, `Result` type.
    *   **Validation Library (`../lib/validation`):** Uses `ValidationError`, `array`, `object`, `string`, `unknown`.
    *   **Individual Chart Parsers:**
        *   [`./bar.ts`](frontend/src/charts/bar.ts:1) (imports `BarChart` type and `bar` parser).
        *   [`./context.ts`](frontend/src/charts/context.ts:1) (imports `ChartContext` type).
        *   [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1) (imports `HierarchyChart` type and `hierarchy` parser).
        *   [`./scatterplot.ts`](frontend/src/charts/scatterplot.ts:1) (imports `ScatterPlot` type and `scatterplot` parser).
    *   **Consumers:** This module's `parseChartData` function is likely called when Fava receives chart data from the backend API, to prepare it for rendering by components like [`ChartSwitcher.svelte`](frontend/src/charts/ChartSwitcher.svelte:1) and [`Chart.svelte`](frontend/src/charts/Chart.svelte:1).

## File: `frontend/src/charts/line.ts`

### I. Overview and Purpose

[`frontend/src/charts/line.ts`](frontend/src/charts/line.ts:1) is responsible for defining the structure and parsing logic for line charts, specifically those representing account balances over time. It introduces the `LineChart` class, which encapsulates multiple series of data points (e.g., one series per currency). The module provides a validator for the expected raw JSON input (an array of date-balance records) and a factory function `balances` that parses this JSON into a `LineChart` instance. It also defines how tooltips for these charts should be generated.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Type Definitions:**
    *   **`LineChartDatum` (Lines [`frontend/src/charts/line.ts:14-18`](frontend/src/charts/line.ts:14)):** Represents a single point on a line chart.
        *   `name: string`: The name of the series this datum belongs to (typically a currency).
        *   `date: Date`: The date of the data point.
        *   `value: number`: The numerical value of the data point.
    *   **`LineChartSeries` (Lines [`frontend/src/charts/line.ts:23-26`](frontend/src/charts/line.ts:23)):** Represents a single line (series) in the chart.
        *   `name: string`: The name of the series (e.g., currency).
        *   `values: readonly LineChartDatum[]`: An array of data points for this series.

2.  **`LineChart` Class (Lines [`frontend/src/charts/line.ts:34-56`](frontend/src/charts/line.ts:34)):**
    *   **Properties:**
        *   `type = "linechart"`: Identifies the chart type.
        *   `name: string | null`: An optional overall name/title for the chart (passed as `label` to the parser).
        *   `data: readonly LineChartSeries[]`: Stores the actual series data. Sorted by the number of values in descending order in the constructor (Line [`frontend/src/charts/line.ts:47`](frontend/src/charts/line.ts:47)).
        *   `series_names: readonly string[]`: An array of all series names present in the chart.
        *   `tooltipText: (c: FormatterContext, d: LineChartDatum) => TooltipContent`: A function to generate tooltip content for a given datum.
    *   **Constructor (Lines [`frontend/src/charts/line.ts:39-49`](frontend/src/charts/line.ts:39)):** Initializes properties. Sorts the input `data` array by the length of `values` in each series, ensuring series with more data points might be processed or rendered with some priority if needed (though rendering order is usually by iteration).
    *   **`filter(hidden_names: readonly string[])` Method (Lines [`frontend/src/charts/line.ts:52-55`](frontend/src/charts/line.ts:52)):**
        *   Takes an array of series names (`hidden_names`) to exclude.
        *   Returns a new array of `LineChartSeries` containing only those series whose names are not in `hidden_names_set`. Used by the rendering component to react to legend toggling.

3.  **`balances_validator` (Line [`frontend/src/charts/line.ts:58`](frontend/src/charts/line.ts:58)):**
    *   A validator for the raw input JSON for balance charts.
    *   Expects an array of objects, where each object must have:
        *   `date: date` (validated as a `Date` object)
        *   `balance: record(number)` (an object mapping currency strings to numerical values)

4.  **`balances_from_parsed_data(label, parsed_data)` Function (Lines [`frontend/src/charts/line.ts:60-85`](frontend/src/charts/line.ts:60)):**
    *   **Purpose:** Transforms validated and parsed raw data into a `LineChart` instance.
    *   **Functionality:**
        1.  Takes a `label` (chart title) and `parsed_data` (the output from `balances_validator`).
        2.  Initializes a `Map<string, LineChartDatum[]>` called `groups` to collect data points for each currency.
        3.  Iterates through `parsed_data`. For each `{ date_val, balance }` record:
            *   Iterates through `Object.entries(balance)`. For each `[currency, value]`:
                *   Creates a `LineChartDatum` object.
                *   Appends this datum to the appropriate currency's array in the `groups` map.
        4.  Converts the `groups` map into an array of `LineChartSeries`.
        5.  Defines a `tooltipText` function using `domHelpers` (from [`./tooltip`](frontend/src/charts/tooltip.ts:1)) to format the amount and date for tooltips.
        6.  Returns a new `LineChart` instance with the processed data and tooltip function.

5.  **`balances(label, json)` Factory Function (Lines [`frontend/src/charts/line.ts:87-93`](frontend/src/charts/line.ts:87)):**
    *   The main parser function for "balances" type charts, intended to be used by [`frontend/src/charts/index.ts`](frontend/src/charts/index.ts:1).
    *   Takes a `label` (string | null) and `json` (unknown data).
    *   Validates `json` using `balances_validator`.
    *   If validation is successful, it maps the `parsedData` by calling `balances_from_parsed_data` to create and return the `LineChart`.
    *   **Return Type:** `Result<LineChart, ValidationError>`. (Note: The `$chartContext` parameter, though part of the signature in `charts/index.ts`'s `parsers` type, is not used by this specific `balances` parser).

**B. Data Structures:**
*   `LineChartDatum`, `LineChartSeries`, `LineChart` class.
*   Input JSON structure: `Array<{ date: string, balance: Record<string, number> }>`.
*   `TooltipContent` (imported type).
*   `FormatterContext` (imported type, used by `tooltipText`).

### III. Code Quality Assessment

*   **Readability & Clarity:** Very good. The types are well-defined, and the class structure for `LineChart` is clear. The parsing logic in `balances_from_parsed_data` is easy to follow.
*   **Complexity:** Low to Moderate. The data transformation from an array of date-balance records to a structure grouped by series (currency) is the main piece of logic. D3 `sort` is used.
*   **Maintainability:** High. The `LineChart` class is self-contained. Changes to the input JSON structure would primarily affect `balances_validator` and `balances_from_parsed_data`.
*   **Testability:** High.
    *   The `LineChart` class methods (constructor, `filter`) can be unit tested.
    *   `balances_validator` can be tested with various JSON inputs.
    *   `balances_from_parsed_data` is a pure function (given its inputs) and can be tested by providing mock parsed data and asserting the structure of the returned `LineChart`.
    *   The main `balances` factory function can be tested by providing JSON and checking the `Result` object.
*   **Adherence to Best Practices & Idioms:**
    *   Clear separation of data structure (`LineChart` class) from parsing logic.
    *   Use of a specific validator for the input data.
    *   Returning a `Result` type from the main parser function.
    *   The `tooltipText` function is part of the `LineChart` object, making tooltip generation specific to the chart type.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **Data Integrity:** Relies on `balances_validator` to ensure the input JSON conforms to the expected structure (dates, records of numbers). If malformed numbers or dates that bypass validation were somehow provided, it could lead to runtime errors or incorrect chart rendering.
    *   **Performance with Large Datasets:** Processing a very large number of date entries or many currencies could impact performance in `balances_from_parsed_data` due to nested loops and map operations.
*   **Secrets Management:** N/A. Dates, currency names, and balances are not secrets.
*   **Input Validation & Sanitization:** `balances_validator` is the primary mechanism. It ensures dates are valid and balances are numbers.
*   **Error Handling & Logging:** The `balances` function returns a `Result`, allowing robust error handling by the caller (typically [`frontend/src/charts/index.ts`](frontend/src/charts/index.ts:1)). No direct logging in this module.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **`$chartContext` Usage:** The `balances` parser function signature in [`frontend/src/charts/index.ts`](frontend/src/charts/index.ts:1) includes `$chartContext`, but it's not used in [`frontend/src/charts/line.ts`](frontend/src/charts/line.ts:87). This is a minor inconsistency. If context (like preferred date formatting for tooltips, or a specific set of currencies to prioritize/filter at parsing time) were needed, it could be utilized. For now, it's harmless.
*   **Tooltip Date Formatting:** The tooltip uses `day(d.date)` (Line [`frontend/src/charts/line.ts:83`](frontend/src/charts/line.ts:83)), which is a specific date format. If the tooltip's date format should adapt to the global interval settings (like other parts of Fava), it might need to use `c.dateFormat(d.date)` from the `FormatterContext` or a date formatter from `ChartContext`.
*   No significant technical debt is apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   This module's `balances` parser and `LineChart` type are imported and used by [`frontend/src/charts/index.ts`](frontend/src/charts/index.ts:1).
    *   The `LineChart` class and `LineChartDatum` type are used by [`LineChart.svelte`](frontend/src/charts/LineChart.svelte:1).
*   **System-Level Interactions:**
    *   **D3.js Library (`d3-array`):** Uses `sort`.
    *   **Formatting Utilities (`../format.ts`):** Imports `FormatterContext` and `day`.
    *   **Result Library (`../lib/result`):** Uses `Result` type.
    *   **Validation Library (`../lib/validation`):** Uses `ValidationError`, `array`, `date`, `number`, `object`, `record`.
    *   **Tooltip Utilities (`./tooltip.ts`):** Imports `TooltipContent` and `domHelpers`.
    *   **Rendering Component:** The `LineChart` objects produced by this module are consumed by [`LineChart.svelte`](frontend/src/charts/LineChart.svelte:1) for rendering.

## File: `frontend/src/charts/LineChart.svelte`

### I. Overview and Purpose

[`frontend/src/charts/LineChart.svelte`](frontend/src/charts/LineChart.svelte:1) is a Svelte component designed to render line charts and area charts. It takes a `LineChart` data object (from [`./line.ts`](frontend/src/charts/line.ts:1)) and a `width` as properties. The component uses D3.js for calculating scales, axes, and path data for lines/areas. It supports multiple series (e.g., one line per currency), interactive tooltips on hover (using a quadtree for efficient searching), and can switch between "line" and "area" display modes based on a Svelte store. It also visually desaturates parts of the chart that represent future dates.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/LineChart.svelte:16-19`](frontend/src/charts/LineChart.svelte:16), Usage Line [`frontend/src/charts/LineChart.svelte:21`](frontend/src/charts/LineChart.svelte:21)):**
    *   `chart: LineChart`: The `LineChart` data object containing series information and the tooltip generation function.
    *   `width: number`: The total width available for the chart.

2.  **Layout and Dimensions:**
    *   `margin`, `height`, `innerWidth`, `innerHeight` (Lines [`frontend/src/charts/LineChart.svelte:24-27`](frontend/src/charts/LineChart.svelte:24)): Standard D3 margin convention to define the plotting area. `height` is fixed at 250.

3.  **Data Processing & State:**
    *   `data = $derived(chart.filter($chartToggledCurrencies))` (Line [`frontend/src/charts/LineChart.svelte:29`](frontend/src/charts/LineChart.svelte:29)): Filters the chart's series based on the `$chartToggledCurrencies` store (from `../stores/chart`), allowing users to hide/show specific currency lines via a legend.
    *   `allValues = $derived(data.flatMap((d) => d.values))` (Line [`frontend/src/charts/LineChart.svelte:32`](frontend/src/charts/LineChart.svelte:32)): A flattened array of all `LineChartDatum` points from the visible series. Used for calculating extents and populating the quadtree.

4.  **D3 Scales:**
    *   `xExtent = $derived(...)` (Lines [`frontend/src/charts/LineChart.svelte:34-37`](frontend/src/charts/LineChart.svelte:34)): Calculates the date range (min/max) across all visible series. Defaults to `today` if no data.
    *   `x = $derived(scaleUtc([0, innerWidth]).domain(xExtent))` (Line [`frontend/src/charts/LineChart.svelte:38`](frontend/src/charts/LineChart.svelte:38)): D3 UTC time scale for the X-axis.
    *   `valueExtent = $derived(extent(allValues, (v) => v.value))` (Line [`frontend/src/charts/LineChart.svelte:39`](frontend/src/charts/LineChart.svelte:39)): Calculates the value range (min/max) across all visible data points.
    *   `yExtent = $derived(...)` (Lines [`frontend/src/charts/LineChart.svelte:41-43`](frontend/src/charts/LineChart.svelte:41)): Adjusts `valueExtent`. If `$lineChartMode` is "area", it uses `includeZero` (from [`./helpers`](frontend/src/charts/helpers.ts:1)) to ensure the Y-axis starts at zero.
    *   `y = $derived(scaleLinear([innerHeight, 0]).domain(padExtent(yExtent)))` (Line [`frontend/src/charts/LineChart.svelte:45`](frontend/src/charts/LineChart.svelte:45)): D3 linear scale for the Y-axis. `padExtent` (from [`./helpers`](frontend/src/charts/helpers.ts:1)) adds a small margin to the domain.

5.  **D3 Quadtree for Tooltips (Lines [`frontend/src/charts/LineChart.svelte:48-54`](frontend/src/charts/LineChart.svelte:48)):**
    *   `quad = $derived(quadtree(allValues, (d) => x(d.date), (d) => y(d.value)))`: Creates a D3 quadtree from all data points. This allows for efficient finding of the nearest data point to the mouse cursor for tooltip display.

6.  **D3 Shape Generators:**
    *   `lineShape = $derived(...)` (Lines [`frontend/src/charts/LineChart.svelte:56-60`](frontend/src/charts/LineChart.svelte:56)): D3 line generator using `curveStepAfter` for a stepped appearance.
    *   `areaShape = $derived(...)` (Lines [`frontend/src/charts/LineChart.svelte:63-69`](frontend/src/charts/LineChart.svelte:69)): D3 area generator, also using `curveStepAfter`. The baseline `y0` is set to `y(0)` (or `innerHeight` if 0 is off-scale) for area charts.

7.  **D3 Axes:**
    *   `xAxis = $derived(axisBottom(x).tickSizeOuter(0))` (Line [`frontend/src/charts/LineChart.svelte:72`](frontend/src/charts/LineChart.svelte:72)): Bottom X-axis.
    *   `yAxis = $derived(axisLeft(y).tickPadding(6).tickSize(-innerWidth).tickFormat($short))` (Lines [`frontend/src/charts/LineChart.svelte:73-75`](frontend/src/charts/LineChart.svelte:73)): Left Y-axis with grid lines (`tickSize(-innerWidth)`) and short number formatting (`$short` store from `../stores/format`).

8.  **Tooltip Logic:**
    *   `tooltipFindNode: TooltipFindNode = (xPos, yPos) => ...` (Lines [`frontend/src/charts/LineChart.svelte:77-80`](frontend/src/charts/LineChart.svelte:77)): A function compatible with the `positionedTooltip` action. It uses `quad.find(xPos, yPos)` to find the nearest datum and then returns its screen coordinates and tooltip content (generated by `chart.tooltipText`).
    *   `use:positionedTooltip={tooltipFindNode}` (Line [`frontend/src/charts/LineChart.svelte:93`](frontend/src/charts/LineChart.svelte:93)): Applies the tooltip behavior to the main chart `<g>` element.

9.  **Future Data Desaturation:**
    *   `futureFilter = $derived(xExtent[1] > today ? "url(#desaturateFuture)" : undefined)` (Lines [`frontend/src/charts/LineChart.svelte:82-84`](frontend/src/charts/LineChart.svelte:82)): Determines if an SVG filter should be applied to desaturate parts of the chart representing dates after "today".
    *   SVG `<filter id="desaturateFuture">` (Lines [`frontend/src/charts/LineChart.svelte:88-91`](frontend/src/charts/LineChart.svelte:88)): Defines an SVG filter using `feColorMatrix` to reduce saturation. The `x` attribute on `feColorMatrix` is intended to limit the filter's application area horizontally, starting from `x(today)`. *Correction: The `x` attribute on `feColorMatrix` is not standard for controlling the filter region; filter regions are typically controlled by `filterUnits`, `primitiveUnits` on the `<filter>` element or `x, y, width, height` on the filter primitive itself if supported, or by applying the filter to a specific group that is clipped. This specific usage might be a custom interpretation or rely on specific browser behavior not universally guaranteed.* A more common way to apply effects to parts of a shape is to split the shape or use a clip path with a mask.
    *   The `.desaturate` class (Line [`frontend/src/charts/LineChart.svelte:144`](frontend/src/charts/LineChart.svelte:144)) is also used on individual circles if their date is after today.

10. **SVG Rendering (Lines [`frontend/src/charts/LineChart.svelte:87-127`](frontend/src/charts/LineChart.svelte:87)):**
    *   Renders an SVG element with a `viewBox`.
    *   Includes the `<filter>` definition.
    *   A main `<g>` element for chart content, transformed by the margin, with the tooltip action.
    *   Renders X and Y axes using the [`Axis.svelte`](frontend/src/charts/Axis.svelte:1) component.
    *   Conditionally renders areas (`<g class="area">`) if `$lineChartMode === "area"`:
        *   Iterates through `data` (filtered series).
        *   Renders a `<path>` for each series using `areaShape` and colors from `$currenciesScale`.
    *   Renders lines (`<g class="lines">`):
        *   Iterates through `data`.
        *   Renders a `<path>` for each series using `lineShape` and colors from `$currenciesScale`.
    *   Conditionally renders circles at data points (`<g>`) if `$lineChartMode === "line"`:
        *   Iterates through `data` and then `d.values`.
        *   Renders a `<circle>` for each data point, colored by `$currenciesScale`.
        *   Applies `class:desaturate` if `v.date > today`.

**B. Data Structures:**
*   Consumes `LineChart` and `LineChartDatum` from [`./line.ts`](frontend/src/charts/line.ts:1).
*   Uses D3 scales, axes, shapes, and quadtree.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The use of Svelte's reactive `$derived` declarations makes the data flow for scales and shapes clear. D3 concepts are applied in a standard way.
*   **Complexity:** Moderate to High. Combines D3's data manipulation and rendering logic with Svelte's reactivity and component model. Managing extents, scales, shapes, axes, and interactive tooltips involves a fair amount of interconnected logic.
*   **Maintainability:** Moderate. Changes to chart appearance (e.g., different curve types, styling) would involve modifying D3 shape generators or SVG attributes. Adding new interactive features could increase complexity.
*   **Testability:** Difficult. Requires a Svelte component testing environment. Would involve:
    *   Mocking the `chart: LineChart` prop with various data scenarios.
    *   Mocking Svelte stores (`$chartToggledCurrencies`, `$lineChartMode`, `$ctx`, `$short`, `$currenciesScale`).
    *   Snapshot testing for the rendered SVG structure.
    *   Testing interactions (tooltip display on hover).
    *   Verifying correct application of styles/filters (e.g., desaturation).
*   **Adherence to Best Practices & Idioms:**
    *   Standard D3 margin convention and scale/axis setup.
    *   Use of D3 quadtree for efficient hover detection.
    *   Reactive updates based on Svelte stores and props.
    *   Component composition (using [`Axis.svelte`](frontend/src/charts/Axis.svelte:1)).

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data (Low Risk):** The primary data displayed (values, dates) are numerical or date objects, formatted by D3 or trusted formatters. Series names (currencies) are used for colors via `$currenciesScale` and keys in loops; if rendered as text directly by a child component without escaping (not apparent here), it could be a risk, but `Axis.svelte` and D3's axis rendering are generally safe. Tooltip content is generated by `chart.tooltipText`, which uses `domHelpers` from [`./tooltip.ts`](frontend/src/charts/tooltip.ts:1); the security of tooltips depends on `domHelpers` correctly sanitizing or creating safe text nodes.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** Assumes the input `chart` prop is a valid, well-structured `LineChart` object, which should have been created from validated data by [`./line.ts`](frontend/src/charts/line.ts:1).
*   **Error Handling & Logging:** No explicit error handling for invalid data beyond what D3 or Svelte might do. If `chart` data is malformed (e.g., non-numeric values where numbers are expected), D3 scales or shape generators might produce errors or unexpected output.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **SVG Filter for Future Data:** As noted, the `x` attribute on `feColorMatrix` (Line [`frontend/src/charts/LineChart.svelte:89`](frontend/src/charts/LineChart.svelte:89)) is not a standard way to define a filter's application region. A more robust approach would be to either:
    1.  Split the line/area paths into two segments (past/future) and apply a class/style directly to the future segment.
    2.  Use a `<clipPath>` to define the "future" region and apply the filter only to elements within that clipped region, or use the clipPath to render the future part with different styling.
    The current `class:desaturate` on circles (Line [`frontend/src/charts/LineChart.svelte:119`](frontend/src/charts/LineChart.svelte:119)) is a more direct and reliable method for discrete elements.
*   **Fixed Height:** The chart `height` is fixed at 250 (Line [`frontend/src/charts/LineChart.svelte:25`](frontend/src/charts/LineChart.svelte:25)). Making this responsive or configurable via a prop could increase flexibility.
*   **Tooltip `positionedTooltip`:** The `positionedTooltip` action is imported from [`./tooltip`](frontend/src/charts/tooltip.ts:1). Its implementation details would determine its robustness and performance.
*   No major technical debt is immediately apparent, aside from the potentially non-standard SVG filter usage.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   Consumes `LineChart` and `LineChartDatum` types from [`./line.ts`](frontend/src/charts/line.ts:1).
*   **System-Level Interactions:**
    *   **D3.js Libraries:** Heavily uses `d3-array` (extent, max, min), `d3-axis` (axisBottom, axisLeft), `d3-quadtree` (quadtree), `d3-scale` (scaleLinear, scaleUtc), `d3-shape` (area, curveStepAfter, line).
    *   **Svelte Stores:**
        *   `chartToggledCurrencies`, `lineChartMode` (from `../stores/chart.ts`).
        *   `ctx`, `short` (from `../stores/format.ts`).
    *   **Child Components:** Uses [`Axis.svelte`](frontend/src/charts/Axis.svelte:1).
    *   **Chart Helpers (`./helpers.ts`):** Uses `currenciesScale`, `includeZero`, `padExtent`.
    *   **Tooltip System (`./tooltip.ts`):** Uses `TooltipFindNode` type and `positionedTooltip` action.
    *   **Parent Components:** This component is rendered by [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) when the `chart.type` is "linechart".
## File: `frontend/src/charts/ModeSwitch.svelte`

### I. Overview and Purpose

[`frontend/src/charts/ModeSwitch.svelte`](frontend/src/charts/ModeSwitch.svelte:1) is a generic Svelte component designed to render a set of radio button-like toggle switches. It's used to control a Svelte store that has a predefined set of possible string values, each associated with a display name. This component allows users to select one option from several, updating the provided store. It's typically used in Fava for switching between different display modes for charts (e.g., "line" vs "area" for line charts, or "treemap" vs "sunburst" for hierarchy charts).

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/ModeSwitch.svelte:4-7`](frontend/src/charts/ModeSwitch.svelte:4), Usage Line [`frontend/src/charts/ModeSwitch.svelte:9`](frontend/src/charts/ModeSwitch.svelte:9)):**
    *   `store: LocalStoreSyncedStore<T>`: This is the primary prop. It expects a Svelte store that conforms to the `LocalStoreSyncedStore<T>` interface (likely defined in `../lib/store.ts`). This interface presumably provides:
        *   A way to get and set the store's current value (string `T`).
        *   A method `values()` (Line [`frontend/src/charts/ModeSwitch.svelte:13`](frontend/src/charts/ModeSwitch.svelte:13)) that returns an iterable (e.g., array of tuples) of `[option_value: T, display_name: string]`.
    *   The generic `T extends string` indicates the store's value and option keys are strings.

2.  **Rendering Logic (Lines [`frontend/src/charts/ModeSwitch.svelte:12-19`](frontend/src/charts/ModeSwitch.svelte:12)):**
    *   Renders a `<span>` container.
    *   Iterates through `store.values()` using an `#each` block. For each `[option, name]` pair:
        *   Renders a `<label>` element styled as a `button`.
        *   `class:muted={$store !== option}`: Applies the `muted` class if the current `option` is not the one selected in the `$store`. This visually indicates the inactive options.
        *   Inside the label, an `<input type="radio">` is rendered:
            *   `bind:group={$store}`: This is the core Svelte two-way binding for radio button groups. It links the selected radio button's `value` to the `$store`.
            *   `value={option}`: Sets the value of this specific radio button.
        *   The `name` (display name for the option) is rendered as the text content of the label.

3.  **Styling (`<style>` block Lines [`frontend/src/charts/ModeSwitch.svelte:21-35`](frontend/src/charts/ModeSwitch.svelte:21)):**
    *   `input { display: none; }`: The actual radio input elements are hidden. The clickable `<label>` elements provide the UI.
    *   `label + label { margin-left: 0.125rem; }`: Adds a small left margin to subsequent labels for spacing.
    *   `@media print`: Hides all labels when printing. This implies that mode switches are not relevant for printed output, and the chart will print in its currently selected mode.

**B. Data Structures:**
*   Interacts with a `LocalStoreSyncedStore<T>` Svelte store.
*   The `store.values()` method is expected to yield pairs of `[string, string]`.

### III. Code Quality Assessment

*   **Readability & Clarity:** Excellent. The component is very concise and its purpose as a mode switcher based on a store is immediately clear. The use of Svelte's `bind:group` is idiomatic.
*   **Complexity:** Very Low. It's a simple wrapper around radio button functionality, styled to look like toggle buttons.
*   **Maintainability:** High. The component is generic and driven entirely by the `store` prop. Changes to available modes or their names would be handled within the store's definition, not this component.
*   **Testability:** Moderate. Requires a Svelte component testing environment. Key aspects to test:
    *   Rendering of labels based on `store.values()`.
    *   Correct initial state based on the store's value.
    *   Clicking a label updates the `$store` correctly.
    *   Conditional application of the `muted` class.
    *   Mocking the `LocalStoreSyncedStore` interface would be necessary.
*   **Adherence to Best Practices & Idioms:**
    *   Good use of `bind:group` for radio button behavior.
    *   Styling labels to act as custom radio buttons is a common UI pattern.
    *   Generic component design makes it reusable for any store conforming to the expected interface.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data (Low Risk):** The `name` (display name) from `store.values()` is rendered as text content within the `<label>` (Line [`frontend/src/charts/ModeSwitch.svelte:16`](frontend/src/charts/ModeSwitch.svelte:16)). Svelte's default templating escapes this, mitigating XSS if the display names were to come from a less trusted source (though typically these are hardcoded or from i18n keys). The `option` values are used in `bind:group` and `value` attributes, which are not typically XSS vectors for radio inputs.
*   **Secrets Management:** N/A. Mode names/values are not secrets.
*   **Input Validation & Sanitization:** Relies on the `store` prop conforming to the `LocalStoreSyncedStore` interface and providing valid string options/names. No validation within this component.
*   **Error Handling & Logging:** No explicit error handling. If the `store` prop is malformed (e.g., `values()` doesn't return the expected structure), Svelte/JavaScript runtime errors might occur during rendering.
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Accessibility:**
    *   While hiding `input type="radio"` and styling labels is common, ensure that keyboard navigation and screen reader announcements still work correctly. Standard browser behavior for radio groups (arrow key navigation once one is focused) should ideally be preserved or replicated if the label styling interferes.
    *   The `<span>` wrapper (Line [`frontend/src/charts/ModeSwitch.svelte:12`](frontend/src/charts/ModeSwitch.svelte:12)) could benefit from a `role="radiogroup"` and an `aria-labelledby` or `aria-label` if there's a conceptual label for the entire group of switches, to improve semantics for assistive technologies.
*   No significant technical debt is apparent. The component is small and focused.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   This component is likely used by chart containers like [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) to switch modes for specific chart types (e.g., bar charts, line charts, hierarchy charts).
*   **System-Level Interactions:**
    *   **Svelte Stores (`../lib/store.ts`):** Critically depends on a Svelte store that implements the `LocalStoreSyncedStore<T>` interface. Examples of such stores in Fava include `barChartMode`, `lineChartMode`, `hierarchyChartMode` (from `../stores/chart.ts`).
    *   **UI Framework (Svelte):** Uses Svelte's `$props`, `bind:group`, and `#each` block.

## File: `frontend/src/charts/query-charts.ts`

### I. Overview and Purpose

[`frontend/src/charts/query-charts.ts`](frontend/src/charts/query-charts.ts:1) provides a utility function `getQueryChart` that attempts to generate a chart (either a `HierarchyChart` or a `LineChart`) from the result table of a Fava SQL query (`QueryResultTable`). This allows users to visualize the output of certain BQL queries directly as charts if the query result structure matches specific patterns.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **`getQueryChart(table: QueryResultTable, $chartContext: ChartContext)` Function (Lines [`frontend/src/charts/query-charts.ts:10-38`](frontend/src/charts/query-charts.ts:10)):**
    *   **Purpose:** To intelligently determine if a `QueryResultTable` can be visualized as a standard Fava chart and, if so, to parse it into the appropriate chart object.
    *   **Input:**
        *   `table: QueryResultTable`: The result data from a BQL query, likely including column type information and rows of data. (Type `QueryResultTable` is from [`../reports/query/query_table.ts`](frontend/src/reports/query/query_table.ts:1)).
        *   `$chartContext: ChartContext`: The standard chart context (from [`./context.ts`](frontend/src/charts/context.ts:1)), needed by the underlying chart parsers like `hierarchy_from_parsed_data`.
    *   **Logic:**
        1.  **Column Check (Lines [`frontend/src/charts/query-charts.ts:14-18`](frontend/src/charts/query-charts.ts:14)):**
            *   It expects exactly two columns in the query result. If not, it returns `null` (no chart can be generated).
        2.  **Hierarchy Chart Pattern (Lines [`frontend/src/charts/query-charts.ts:19-30`](frontend/src/charts/query-charts.ts:19)):**
            *   Checks if the first column's data type (`dtype`) is "str" (string) and the second column's `dtype` is "Inventory".
            *   If this pattern matches, it assumes the query result represents a hierarchical structure (e.g., accounts and their balances).
            *   It maps the rows (`[string, Inventory][]`) to an array of `{ group: string, balance: Record<string, number> }`.
            *   Uses `stratify` (from `../lib/tree`) to convert this flat list of grouped balances into a tree structure. The `stratify` function likely takes the group string (account name) and splits it by a delimiter (e.g., ':') to build the hierarchy.
            *   The callback to `stratify` creates nodes with `{ account, balance }`.
            *   Sets the root account name to "(root)".
            *   Calls `hierarchy_from_parsed_data` (from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1)) with `null` label, the stratified `root`, and `$chartContext` to generate a `HierarchyChart`.
        3.  **Line Chart (Balances over Time) Pattern (Lines [`frontend/src/charts/query-charts.ts:31-37`](frontend/src/charts/query-charts.ts:31)):**
            *   Checks if the first column's `dtype` is "date" and the second column's `dtype` is "Inventory".
            *   If this pattern matches, it assumes the query result represents balances over time.
            *   It maps the rows (`[Date, Inventory][]`) to an array of `{ date: Date, balance: Record<string, number> }`.
            *   Calls `balances_from_parsed_data` (from [`./line.ts`](frontend/src/charts/line.ts:1)) with `null` label and the transformed balance data to generate a `LineChart`.
        4.  **No Match (Line [`frontend/src/charts/query-charts.ts:38`](frontend/src/charts/query-charts.ts:38)):** If neither pattern matches, returns `null`.
    *   **Return Type:** `HierarchyChart | LineChart | null`.

**B. Data Structures:**
*   `QueryResultTable`, `Inventory` (from [`../reports/query/query_table.ts`](frontend/src/reports/query/query_table.ts:1)).
*   `ChartContext` (from [`./context.ts`](frontend/src/charts/context.ts:1)).
*   `HierarchyChart` (from [`./hierarchy.ts`](frontend/src/charts/hierarchy.ts:1)).
*   `LineChart` (from [`./line.ts`](frontend/src/charts/line.ts:1)).

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The function clearly checks for specific patterns in the query result table structure to decide which chart type to generate.
*   **Complexity:** Moderate. The logic involves understanding the structure of `QueryResultTable`, transforming row data, and then calling specialized chart parsing functions. The use of `stratify` implies a non-trivial tree construction process.
*   **Maintainability:** Moderate. To support generating new chart types from query results, new pattern-checking blocks (`if ... else if ...`) would need to be added, along with calls to their respective data transformation and chart parsing functions.
*   **Testability:** Moderate to High.
    *   The function can be tested by creating mock `QueryResultTable` objects with different column types and row data.
    *   Mock `$chartContext` would be needed.
    *   Assertions would check if the correct chart type (or `null`) is returned, and potentially inspect the structure of the generated chart data (though detailed data validation is the job of the underlying parsers).
    *   The `stratify` function itself should ideally have its own tests.
*   **Adherence to Best Practices & Idioms:**
    *   Pattern matching on data structure to determine behavior is a common approach.
    *   Reuses existing chart data parsing logic (`hierarchy_from_parsed_data`, `balances_from_parsed_data`), promoting DRY.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **Data Integrity from Query:** The function assumes that the `dtype` property in `QueryResultTable` accurately reflects the type of data in the rows. If a BQL query could somehow produce a table where `dtype` is "Inventory" but the actual row data is not a valid `Inventory` object, the subsequent destructuring or access to `inv.value` (Lines [`frontend/src/charts/query-charts.ts:22`](frontend/src/charts/query-charts.ts:22), [`frontend/src/charts/query-charts.ts:34`](frontend/src/charts/query-charts.ts:34)) could lead to runtime errors. The underlying chart parsers (`hierarchy_from_parsed_data`, `balances_from_parsed_data`) likely perform their own validation, which would mitigate this.
    *   **Performance with Large Query Results:** If the `QueryResultTable` contains a very large number of rows, the `map` operations and especially the `stratify` function could be performance-intensive.
*   **Secrets Management:** N/A. Query results are not expected to contain secrets.
*   **Input Validation & Sanitization:** Relies on the structure of `QueryResultTable` and the types indicated by `dtype`. The main validation is implicitly handled by the specific chart data constructors/parsers it calls.
*   **Error Handling & Logging:** Returns `null` if no suitable chart pattern is found. Does not perform explicit error logging itself; errors during the underlying chart parsing would be handled by those functions (e.g., they might return `Result` types, though this function doesn't seem to be typed to return a `Result`). *Self-correction: `hierarchy_from_parsed_data` returns a `HierarchyChart` directly, not a `Result`. `balances_from_parsed_data` also returns `LineChart` directly. This means any validation errors within those would likely throw exceptions if not handled internally by them.*
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Error Handling:** The functions `hierarchy_from_parsed_data` and `balances_from_parsed_data` are imported and called. `hierarchy_from_parsed_data` is used by the `hierarchy` factory in `hierarchy.ts` which *does* return a `Result`. `balances_from_parsed_data` is used by the `balances` factory in `line.ts` which also returns a `Result`. It seems `getQueryChart` is calling the "from_parsed_data" variants directly. If these can throw errors (e.g., if `stratify` fails or data is malformed in a way not caught by `dtype` checks), `getQueryChart` might be more robust if it wrapped these calls in try-catch blocks or if there were versions of these functions that also returned `Result` types. Given the context of Fava, it's possible that the data flowing into `QueryResultTable` is already heavily sanitized/validated by the backend.
*   **Extensibility:** If many more query-to-chart patterns were to be added, the series of `if/else if` checks could become long. A more extensible approach might involve a registry of pattern matchers and corresponding chart generators, but for two patterns, the current approach is fine.
*   **Clarity of `stratify`:** The `stratify` function's behavior (especially how it uses `(d) => d.group` to build the hierarchy from potentially colon-separated account names) is critical but opaque from this file alone. Good documentation or clearer naming in `../lib/tree.ts` would be important.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   None directly with `ModeSwitch.svelte` or `ScatterPlot.svelte`.
*   **System-Level Interactions:**
    *   **Tree Utilities (`../lib/tree.ts`):** Uses `stratify`.
    *   **Query Table Types (`../reports/query/query_table.ts`):** Depends on `Inventory` and `QueryResultTable` types.
    *   **Chart Context (`./context.ts`):** Uses `ChartContext`.
    *   **Hierarchy Chart Logic (`./hierarchy.ts`):** Uses `HierarchyChart` type and `hierarchy_from_parsed_data` function.
    *   **Line Chart Logic (`./line.ts`):** Uses `LineChart` type and `balances_from_parsed_data` function.
    *   **Consumer:** This function is likely used in the Query report/editor interface (e.g., [`Query.svelte`](frontend/src/reports/query/Query.svelte:1)) to offer an automatic chart visualization if the query results are suitable.

## File: `frontend/src/charts/ScatterPlot.svelte`

### I. Overview and Purpose

[`frontend/src/charts/ScatterPlot.svelte`](frontend/src/charts/ScatterPlot.svelte:1) is a Svelte component for rendering scatter plot charts. It takes a `ScatterPlot` data object (from [`./scatterplot.ts`](frontend/src/charts/scatterplot.ts:1)) and a `width` as properties. The X-axis typically represents dates, and the Y-axis represents categorical "types" (e.g., event types). Each data point is rendered as a circle. The component includes D3-based scales and axes, interactive tooltips on hover (using a quadtree), and desaturates points that represent future dates.

### II. Detailed Functionality

**A. Key Components & Features:**

1.  **Props (Interface `Props` Lines [`frontend/src/charts/ScatterPlot.svelte:14-17`](frontend/src/charts/ScatterPlot.svelte:14), Usage Line [`frontend/src/charts/ScatterPlot.svelte:19`](frontend/src/charts/ScatterPlot.svelte:19)):**
    *   `chart: ScatterPlot`: The `ScatterPlot` data object, which contains an array of `ScatterPlotDatum` items.
    *   `width: number`: The total width for the chart.

2.  **Layout and Dimensions:**
    *   `margin`, `height`, `innerWidth`, `innerHeight` (Lines [`frontend/src/charts/ScatterPlot.svelte:22-25`](frontend/src/charts/ScatterPlot.svelte:22)): Standard D3 margin convention. `height` is fixed at 250.

3.  **D3 Scales:**
    *   `dateExtent = $derived(extent(chart.data, (d) => d.date))` (Line [`frontend/src/charts/ScatterPlot.svelte:28`](frontend/src/charts/ScatterPlot.svelte:28)): Calculates the min/max date range from the data.
    *   `x = $derived(scaleUtc([0, innerWidth]).domain(dateExtent[0] ? dateExtent : [0, 1]))` (Lines [`frontend/src/charts/ScatterPlot.svelte:29-31`](frontend/src/charts/ScatterPlot.svelte:29)): D3 UTC time scale for the X-axis. Defaults to `[0, 1]` domain if `dateExtent` is undefined (empty data).
    *   `y = $derived(scalePoint([innerHeight, 0]).domain(chart.data.map((d) => d.type)).padding(1))` (Lines [`frontend/src/charts/ScatterPlot.svelte:32-36`](frontend/src/charts/ScatterPlot.svelte:32)): D3 point scale for the Y-axis. A point scale is used for ordinal data (the "types") and distributes points evenly along the axis. `padding(1)` adds space equivalent to one step before the first point and after the last.

4.  **D3 Axes:**
    *   `xAxis = $derived(axisBottom(x).tickSizeOuter(0))` (Line [`frontend/src/charts/ScatterPlot.svelte:39`](frontend/src/charts/ScatterPlot.svelte:39)): Bottom X-axis.
    *   `yAxis = $derived(axisLeft(y).tickPadding(6).tickSize(-innerWidth).tickFormat((d) => d))` (Lines [`frontend/src/charts/ScatterPlot.svelte:40-45`](frontend/src/charts/ScatterPlot.svelte:40)): Left Y-axis with grid lines. `tickFormat((d) => d)` displays the type strings directly as tick labels.

5.  **D3 Quadtree for Tooltips (Lines [`frontend/src/charts/ScatterPlot.svelte:48-54`](frontend/src/charts/ScatterPlot.svelte:48)):**
    *   `quad = $derived(quadtree([...chart.data], (d) => x(d.date), (d) => y(d.type) ?? 0))`: Creates a D3 quadtree for efficient nearest-neighbor searching for tooltips. Uses `y(d.type) ?? 0` in case a type is not found in the scale's domain (though `scalePoint` should map all domain items).

6.  **Tooltip Logic:**
    *   **`tooltipText(d: ScatterPlotDatum)` (Lines [`frontend/src/charts/ScatterPlot.svelte:56-58`](frontend/src/charts/ScatterPlot.svelte:56)):** Generates tooltip content, displaying the datum's `description` and its `date` (formatted using `day` from `../format`).
    *   **`tooltipFindNode: TooltipFindNode = (xPos, yPos) => ...` (Lines [`frontend/src/charts/ScatterPlot.svelte:60-63`](frontend/src/charts/ScatterPlot.svelte:60)):** Function for `positionedTooltip`. Uses `quad.find` to locate the nearest point and returns its screen coordinates and tooltip content.

7.  **SVG Rendering (Lines [`frontend/src/charts/ScatterPlot.svelte:66-85`](frontend/src/charts/ScatterPlot.svelte:66)):**
    *   Renders an SVG element with a `viewBox`.
    *   A main `<g>` element for chart content, transformed by margin, with the `positionedTooltip` action.
    *   Renders X and Y axes using the [`Axis.svelte`](frontend/src/charts/Axis.svelte:1) component.
    *   Iterates through `chart.data` (`#each chart.data as dot (...)`):
        *   For each `dot` (a `ScatterPlotDatum`):
            *   Renders a `<circle>` element.
            *   `r="5"`: Fixed radius of 5px.
            *   `fill={scatterplotScale(dot.type)}`: Fill color determined by `scatterplotScale` (from [`./helpers.ts`](frontend/src/charts/helpers.ts:1)) based on the `dot.type`.
            *   `cx={x(dot.date)}`, `cy={y(dot.type)}`: Position determined by the D3 scales.
            *   `class:desaturate={dot.date > today}`: Applies the `desaturate` class if the dot's date is in the future.

8.  **Styling (`<style>` block Lines [`frontend/src/charts/ScatterPlot.svelte:87-95`](frontend/src/charts/ScatterPlot.svelte:87)):**
    *   `svg > g { pointer-events: all; }`: Ensures the main group receives mouse events for tooltips.
    *   `.desaturate { filter: saturate(50%); }`: CSS filter to reduce saturation for future data points.

**B. Data Structures:**
*   Consumes `ScatterPlot` and `ScatterPlotDatum` from [`./scatterplot.ts`](frontend/src/charts/scatterplot.ts:1).
*   Uses D3 scales, axes, and quadtree.

### III. Code Quality Assessment

*   **Readability & Clarity:** Good. The structure is similar to other D3-based Svelte chart components in Fava (e.g., `LineChart.svelte`). The use of `$derived` for scales and axes is clear.
*   **Complexity:** Moderate. Involves D3 scale and axis calculations, SVG rendering, and quadtree-based tooltip interaction.
*   **Maintainability:** Moderate. Changes to visual appearance or interaction would involve modifying D3 setup or SVG attributes.
*   **Testability:** Difficult. Similar to `LineChart.svelte`, requires a Svelte component testing environment. Would involve:
    *   Mocking the `chart: ScatterPlot` prop.
    *   Mocking Svelte stores/helpers (`day`, `scatterplotScale`).
    *   Snapshot testing for SVG.
    *   Testing tooltip interactions.
*   **Adherence to Best Practices & Idioms:**
    *   Standard D3 setup for scales and axes.
    *   Use of quadtree for efficient hover detection.
    *   Reactive updates via Svelte's `$derived`.

### IV. Security Analysis

*   **General Vulnerabilities:**
    *   **XSS from Data (Low Risk):**
        *   `dot.type` is used with `scatterplotScale` for color and as a key in the `#each` loop. If rendered as text by `Axis.svelte` (for Y-axis labels), Svelte/D3's default escaping should protect it.
        *   `dot.description` and `dot.date` are used in `tooltipText`. The security depends on `domHelpers` (from [`./tooltip.ts`](frontend/src/charts/tooltip.ts:1)) correctly creating text nodes or escaping content. Dates are formatted by `day`.
*   **Secrets Management:** N/A.
*   **Input Validation & Sanitization:** Assumes the input `chart` prop is a valid `ScatterPlot` object, created from validated data by [`./scatterplot.ts`](frontend/src/charts/scatterplot.ts:1).
*   **Error Handling & Logging:** No explicit error handling. D3 or Svelte might produce errors if data is malformed (e.g., `dot.date` is not a valid Date, `dot.type` is not in `y.domain()`).
*   **Post-Quantum Security Considerations:** N/A.

### V. Improvement Recommendations & Technical Debt

*   **Y-Axis Scale Robustness:** `y(d.type) ?? 0` is used in the quadtree accessor (Line [`frontend/src/charts/ScatterPlot.svelte:52`](frontend/src/charts/ScatterPlot.svelte:52)) and tooltip positioning (Line [`frontend/src/charts/ScatterPlot.svelte:62`](frontend/src/charts/ScatterPlot.svelte:62)). `scalePoint.domain()` is set from `chart.data.map((d) => d.type)`. If a `dot.type` somehow wasn't in this domain (e.g., data changes after initial scale setup without full reactivity on the domain), `y(d.type)` would be `undefined`. The `?? 0` provides a fallback, but it might place the point incorrectly at the top of the chart. Ensuring the domain of `y` is always perfectly in sync with all `dot.type` values encountered is important. Svelte's reactivity usually handles this if `chart.data` is the sole source for the domain.
*   **Fixed Height:** Chart `height` is fixed at 250. Making it responsive or a prop could be an improvement.
*   **Color Scale:** Uses `scatterplotScale` from [`./helpers.ts`](frontend/src/charts/helpers.ts:1). This scale is defined as `scaleOrdinal(colors10)` without an explicit domain set initially. This means the color mapping might change if the set or order of `dot.type` values changes between chart renderings, unless the data consistently presents types in an order that makes D3's implicit domain assignment stable. For more stable color mapping, `scatterplotScale` could be derived with an explicit domain like other scales in `helpers.ts`.
*   No major technical debt apparent.

### VI. Inter-File & System Interactions

*   **Interactions within Batch:**
    *   None directly with `ModeSwitch.svelte` or `query-charts.ts`.
*   **System-Level Interactions:**
    *   **D3.js Libraries:** Uses `d3-array` (extent), `d3-axis` (axisBottom, axisLeft), `d3-quadtree` (quadtree), `d3-scale` (scalePoint, scaleUtc).
    *   **Formatting Utilities (`../format.ts`):** Uses `day`.
    *   **Child Components:** Uses [`Axis.svelte`](frontend/src/charts/Axis.svelte:1).
    *   **Chart Helpers (`./helpers.ts`):** Uses `scatterplotScale`.
    *   **Scatter Plot Logic (`./scatterplot.ts`):** Consumes `ScatterPlot` and `ScatterPlotDatum` types.
    *   **Tooltip System (`./tooltip.ts`):** Uses `TooltipFindNode` type, `domHelpers`, and `positionedTooltip` action.
    *   **Parent Components:** This component is rendered by [`Chart.svelte`](frontend/src/charts/Chart.svelte:1) when `chart.type` is "scatterplot".