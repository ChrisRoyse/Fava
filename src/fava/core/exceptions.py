"""Core exceptions for Fava."""

from fava.helpers import FavaAPIError


class EntryNotFoundForHashError(FavaAPIError):
    """Exception raised when an entry cannot be found for a given hash."""

    def __init__(self, entry_hash: str) -> None:
        super().__init__(f"Entry with hash '{entry_hash}' not found.")
        self.entry_hash = entry_hash


class StatementNotFoundError(FavaAPIError):
    """Statement not found."""

    def __init__(self) -> None:
        super().__init__("Statement not found.")


class StatementMetadataInvalidError(FavaAPIError):
    """Statement metadata not found or invalid."""

    def __init__(self, key: str) -> None:
        super().__init__(
            f"Statement path at key '{key}' missing or not a string."
        )