# Code Comprehension Report: Fava Utilities (Ranking, Sets, Unreachable)

**Date:** June 2, 2025
**Analyzer:** Roo (AI Assistant)
**Target Files:**
*   [`src/fava/util/ranking.py`](src/fava/util/ranking.py) (Exponential Decay Ranking)
*   [`src/fava/util/sets.py`](src/fava/util/sets.py) (Set Utilities)
*   [`src/fava/util/unreachable.py`](src/fava/util/unreachable.py) (Unreachable Code Helper)

## 1. Overview and Purpose

This report covers three small, specialized utility modules from Fava:

*   **[`src/fava/util/ranking.py`](src/fava/util/ranking.py)**: Implements an `ExponentialDecayRanker` class. This class is designed to rank items in a list based on a scoring system where the value of an interaction (a "like") decays exponentially over time. This is useful for ranking items by recency and frequency of interaction.
*   **[`src/fava/util/sets.py`](src/fava/util/sets.py)**: Provides a simple utility function `add_to_set` for adding an element to a set, creating the set if it doesn't exist or is `None`. This is particularly useful for working with Beancount entry attributes like `tags` and `links` which can be `None` or a `frozenset`.
*   **[`src/fava/util/unreachable.py`](src/fava/util/unreachable.py)**: Contains a helper function `assert_never` and a custom exception `UnreachableCodeAssertionError`. This is a common pattern used with type checkers (like Mypy) to assert that a certain branch of code should be unreachable if the type system is correctly understood and all cases (e.g., in an Enum or a series of `isinstance` checks) are handled.

These utilities provide specific, focused functionalities that contribute to Fava's overall code quality, data management, and potentially to features involving user interaction or preference tracking. In the context of a primary project planning document, AI verifiable tasks might relate to the correctness of ranking algorithms if used in user-facing features, or to the robustness of code paths verified by `assert_never`.

## 2. Functionality and Key Components

### 2.1. `src/fava/util/ranking.py`: Exponential Decay Ranker

This module provides a class for ranking items based on time-decayed interactions.

*   **Constants**:
    *   `ZERO = 0.0`
    *   `DEFAULT_RATE = math.log(2) * 1 / 365`: The default decay rate, chosen so that an interaction from one year ago counts half as much as one from today.
*   **`ExponentialDecayRanker` Class**:
    *   **Purpose**: To maintain scores for items where each "like" or interaction contributes to the score, and the contribution decays exponentially over time.
    *   **Scoring Logic**: The score `s` is effectively `Σ exp(RATE * l)`, where `l` is the time of the "like" (as ordinal date). The class stores the logarithm of this sum to avoid very large numbers. The formula `higher + math.log1p(math.exp(lower - higher))` is a numerically stable way to compute `log(exp(higher) + exp(lower))`.
    *   **`__slots__ = ("list", "rate", "scores")`**: Optimizes memory usage.
    *   **`__init__(self, list_: Sequence[str] | None = None, rate: float = DEFAULT_RATE)`**:
        *   `list_`: An optional sequence of items to be ranked. If provided, `sort()` will sort this list. Otherwise, `sort()` will sort all items that have received at least one "like".
        *   `rate`: The decay rate.
        *   `scores`: A dictionary mapping items (strings) to their current log-score.
    *   **`update(self, item: str, date: datetime.date)`**:
        *   Registers a "like" for `item` on the given `date`.
        *   Updates the item's score using the numerically stable log-sum-exp trick. `date.toordinal()` converts the date to a numerical time value.
    *   **`get(self, item: str) -> float`**: Returns the current score for an item, or `ZERO` (0.0) if the item has no score.
    *   **`sort(self) -> list[str]`**: Returns a list of items sorted by their rank (score) in descending order. If `self.list` was provided at initialization, it sorts that list; otherwise, it sorts all items present in `self.scores`.

### 2.2. `src/fava/util/sets.py`: Set Utilities

This module provides a single utility function for working with sets.

*   **`add_to_set(set_: AbstractSet[str] | None, new: str) -> set[str]`**:
    *   Takes an optional existing set (`set_`, which can be `None` or any `AbstractSet` like `frozenset`) and a string `new` to add.
    *   If `set_` is `None`, it creates a new set containing just `new`.
    *   If `set_` exists, it converts `set_` to a mutable `set`, adds `new` using `union`, and returns the new mutable set.
    *   This is particularly useful for updating immutable `frozenset` attributes on Beancount entries (like `tags` or `links`) by creating a new modified set.

### 2.3. `src/fava/util/unreachable.py`: Unreachable Code Helper

This module provides a mechanism for static type checking to verify exhaustiveness.

*   **`UnreachableCodeAssertionError(AssertionError)` Class**: A custom exception raised when `assert_never` is called.
*   **`assert_never(_: Never) -> Never` Function**:
    *   This function takes an argument of type `Never` (from `typing`). `Never` indicates that a certain point in the code should not be reachable.
    *   If this function is somehow called at runtime (meaning an assumption about code paths was wrong), it raises `UnreachableCodeAssertionError`.
    *   Its primary use is with type checkers like Mypy. If all cases of an Enum or all types in a Union are handled in an `if/elif/else` chain, the `else` block might call `assert_never` with the variable that was being checked. If the type checker can prove all cases were handled, it knows the `else` is unreachable. If a case was missed, the type checker will complain that the variable passed to `assert_never` is not of type `Never`.
    *   Marked with `pragma: no cover` as it's intended to not be reached at runtime if code logic and typing are correct.

## 3. Code Structure and Modularity

*   **`ranking.py`**: A single class, well-encapsulated. Its logic is specific to the exponential decay ranking algorithm.
*   **`sets.py`**: A single, simple utility function. Highly modular.
*   **`unreachable.py`**: A single function and a custom exception. Very focused and modular, serving a specific role in static analysis and runtime assertion.

All three modules are small, focused, and exhibit excellent modularity.

## 4. Dependencies

### Internal (Fava):
*   None directly in these files, but `sets.py` is used by other Fava modules (e.g., plugins) when modifying entry attributes. `unreachable.py` is used in `fava.util.date`.

### Python Standard Library:
*   `math` (in `ranking.py`)
*   `typing.TYPE_CHECKING`, `typing.Never`
*   `datetime.date` (type hint in `ranking.py`)
*   `collections.abc.Sequence`, `collections.abc.Set` (type hints)

### External:
*   None.

## 5. Code Quality and Readability

*   **Type Hinting**: All modules use type hints effectively, contributing to clarity. `unreachable.py`'s core purpose is tied to the type system via `typing.Never`.
*   **Clarity and Comments**:
    *   `ranking.py`: The docstring for `ExponentialDecayRanker` clearly explains the mathematical rationale behind the scoring mechanism, including the log-sum-exp trick for numerical stability. Method docstrings are clear.
    *   `sets.py`: The `add_to_set` function has a clear docstring explaining its behavior with `None` inputs.
    *   `unreachable.py`: Docstrings explain the purpose of `assert_never` in the context of type checking.
*   **`ranking.py` Numerical Stability**: The use of `higher + math.log1p(math.exp(lower - higher))` in `ExponentialDecayRanker.update` is a good practice for numerical stability when calculating `log(exp(a) + exp(b))`.
*   **`sets.py` Immutability Handling**: `add_to_set` correctly handles potentially immutable input sets (like `frozenset`) by always returning a new mutable `set`. This aligns with how Beancount entry attributes are often handled (create a new entry with modified attributes).
*   **Modularity Assessment**: Excellent. Each module and its components have a very specific, well-defined purpose.
*   **Technical Debt Identification**: No significant technical debt is apparent. These modules are small, clean, and serve their specific purposes well. The `pragma: no cover` on `assert_never` and its exception is standard as this code ideally shouldn't execute.

## 6. Security Considerations

*   **`ranking.py`**: The inputs are item strings and dates. No direct external interactions or file system access. If item strings were to come from untrusted user input and were extremely long or numerous, it could lead to high memory usage in the `scores` dictionary, but this is a general consideration for any data structure holding user input. No specific vulnerabilities are apparent.
*   **`sets.py`**: Operates on basic Python data types. No security implications.
*   **`unreachable.py`**: A development and type-checking tool. No direct security implications.

These utilities have a very low security risk profile.

## 7. Potential Issues and Areas for Refinement

*   **`ranking.py` - Floating Point Precision**: While the log-sum-exp trick improves stability, all floating-point arithmetic is subject to precision limits. For an extremely long history of "likes" or very disparate scores, precision issues could theoretically accumulate, but this is unlikely to be a practical problem for typical use cases.
*   **`ranking.py` - `DEFAULT_RATE`**: The choice of `DEFAULT_RATE` is based on a specific heuristic (half-life of one year). Different applications might require different decay rates, which is why `rate` is a configurable parameter.
*   **`sets.py` - Performance**: For very frequent calls in a performance-critical loop, the repeated creation of new sets (`set(set_).union(...)`) could have a minor performance overhead compared to mutating an existing mutable set. However, given its typical use case (e.g., modifying Beancount entry attributes, which often involves creating new entry objects anyway), this is generally not an issue and prioritizes correctness with potentially immutable inputs.

## 8. Contribution to AI Verifiable Outcomes (in context of a Primary Project Planning Document)

While these utilities are more foundational or developer-oriented, they can still contribute indirectly to AI verifiable outcomes:

*   **`ranking.py` - Verifiable Ranking Logic**: If Fava were to use the `ExponentialDecayRanker` for features like "suggested accounts" or "frequently used payees" based on user interaction history:
    *   *AI Verifiable Task Example*: "Given a sequence of interactions (item, date), the system shall rank items according to the `ExponentialDecayRanker` logic. The AI will provide a test set of interactions and verify that the top N ranked items match the expected output calculated independently." This ensures the ranking algorithm itself is implemented and used correctly.
*   **`sets.py` - Data Integrity for Set-Like Attributes**: Correctly handling sets (especially `tags` and `links` on Beancount entries) is crucial for data consistency.
    *   *AI Verifiable Task Example*: "When a 'document-linking' plugin adds a link to an entry that previously had no links, the entry's `links` attribute must become a set containing exactly the new link." The `add_to_set` utility helps ensure this, and an AI task could verify the state of entries after such operations.
*   **`unreachable.py` - Code Robustness and Correctness**: The use of `assert_never` helps create more robust code by ensuring all logical paths are considered during development (with type checker assistance). This indirectly contributes to the reliability of features that AI tasks might verify.
    *   *AI Verifiable Task Example*: While not directly testing `assert_never`, an AI task verifying a feature whose correctness relies on exhaustive case handling (e.g., processing all types of `Interval` in `fava.util.date`) benefits from the increased confidence that `assert_never` provides during development that no interval type was missed. If a new `Interval` type were added without updating the logic, `assert_never` (and the type checker) would flag it, preventing a runtime bug that an AI task might later uncover.

In essence, `ranking.py` could be directly verifiable if its output is user-facing. `sets.py` and `unreachable.py` contribute more to the overall quality and correctness of the codebase, which in turn makes it easier to build reliable features that can then be subjected to AI verification. They are tools for building better, more verifiable software.