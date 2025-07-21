"""FilteredLedger implementation that wraps FavaLedger with filtering capabilities."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from fava.core.filter_results import FilterEntries
from fava.util.date import Interval

if TYPE_CHECKING:
    from fava.core.ledger import FavaLedger
    from fava.beans.abc import Directive


class FilteredLedger:
    """A wrapper around FavaLedger that applies filtering to entries."""
    
    def __init__(
        self,
        ledger: FavaLedger,
        *,
        account: str | None = None,
        filter_str: str | None = None,
        time: str | None = None,
    ) -> None:
        self.ledger = ledger
        self.account = account
        self.filter_str = filter_str
        self.time = time
        
        # Apply filtering using the ledger's get_filtered method
        self._filter_result = ledger.get_filtered(
            account=account,
            filter_str=filter_str,
            time=time
        )
    
    @property
    def entries(self) -> List[Directive]:
        """Get the filtered entries."""
        return self._filter_result.entries
    
    @property
    def entries_with_all_prices(self) -> List[Directive]:
        """Get entries including all price entries."""
        # This should return all price entries from the ledger, regardless of filtering
        return self.ledger.all_entries_by_type.Price
    
    @property
    def date_range(self) -> Optional[Any]:
        """Get the date range of the filtered entries."""
        if not self._filter_result.entries:
            return None
        return self._filter_result.date_range
    
    def prices(self, base_currency: str, quote_currency: str) -> List[Any]:
        """Get price entries for the given currency pair."""
        # Filter price entries for the specific currency pair
        price_entries = []
        for entry in self.entries_with_all_prices:
            if (hasattr(entry, '__class__') and 
                entry.__class__.__name__ == 'Price' and
                hasattr(entry, 'currency') and 
                hasattr(entry, 'amount')):
                # Check if this price entry matches our currency pair
                if (entry.currency == base_currency and 
                    hasattr(entry.amount, 'currency') and
                    entry.amount.currency == quote_currency):
                    price_entries.append(entry)
                elif (entry.currency == quote_currency and 
                      hasattr(entry.amount, 'currency') and
                      entry.amount.currency == base_currency):
                    price_entries.append(entry)
        return price_entries
    
    def interval_ranges(self, interval: Interval) -> List[Any]:
        """Get interval ranges for the filtered entries."""
        if not self.entries:
            return []
        return self._filter_result.interval_ranges(interval)
    
    def account_is_closed(self, account_name: str) -> bool:
        """Check if an account is closed in the filtered ledger."""
        # Look for Close entries for this account within our filtered entries
        for entry in self.entries:
            if (hasattr(entry, '__class__') and 
                entry.__class__.__name__ == 'Close' and
                hasattr(entry, 'account') and
                entry.account == account_name):
                return True
        return False