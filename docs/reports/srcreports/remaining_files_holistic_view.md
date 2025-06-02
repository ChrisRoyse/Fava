# Remaining Fava Source Files for Holistic Code Comprehension

This list tracks the Python source files in the Fava codebase prioritized for analysis to achieve a holistic understanding of the project's architecture and core functionality.

Last updated: June 2, 2025 (after Batch 11 analysis of `misc.py`, `module_base.py`, `number.py`)

Total files remaining for holistic view: 26

## Prioritized Files List:

### Top-Level Application & API (`src/fava/`)
*   `src/fava/__init__.py`
*   `src/fava/_ctx_globals_class.py`
*   `src/fava/application.py`
*   `src/fava/cli.py`
*   `src/fava/context.py`
*   `src/fava/helpers.py`
*   `src/fava/internal_api.py`
*   `src/fava/json_api.py`
*   `src/fava/serialisation.py`
*   `src/fava/template_filters.py`

### Core Logic (`src/fava/core/`)
*   `src/fava/core/query.py`
*   `src/fava/core/query_shell.py`
*   `src/fava/core/tree.py`
*   `src/fava/core/watcher.py`

### Extensions (`src/fava/ext/`)
*   `src/fava/ext/__init__.py`
*   `src/fava/ext/auto_commit.py`
*   `src/fava/ext/portfolio_list/__init__.py`

### Plugins (`src/fava/plugins/`)
*   `src/fava/plugins/__init__.py`
*   `src/fava/plugins/link_documents.py`
*   `src/fava/plugins/tag_discovered_documents.py`

### Utilities (`src/fava/util/`)
*   `src/fava/util/__init__.py`
*   `src/fava/util/date.py`
*   `src/fava/util/excel.py`
*   `src/fava/util/ranking.py`
*   `src/fava/util/sets.py`
*   `src/fava/util/unreachable.py`