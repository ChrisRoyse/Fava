"""Filter results module for FavaLedger."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, List, Optional, Dict, Iterator
from dataclasses import dataclass

# AccountTypes not needed for this implementation

if TYPE_CHECKING:
    from fava.beans.abc import Directive
    from fava.core.fava_options import FavaOptions

from fava.util.date import Interval
from beancount.core import inventory


@dataclass
class DateRange:
    """A date range."""
    begin: datetime.date
    end: datetime.date
    
    @property
    def end_inclusive(self) -> datetime.date:
        """The end date, inclusive."""
        return self.end - datetime.timedelta(days=1)


class SimpleInventory:
    """A simple inventory-like object that can be used as a balance."""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.data = data or {}
    
    def reduce(self, func) -> 'SimpleInventory':
        """Reduce method compatible with Fava's inventory operations."""
        # For now, just return a new instance with the same data
        # In a full implementation, this would apply the reduction function
        result_data = {}
        for key, value in self.data.items():
            try:
                result_data[key] = func(value)
            except Exception:
                # If reduction fails, keep original value
                result_data[key] = value
        return SimpleInventory(result_data)
    
    def items(self):
        """Return items like a dictionary."""
        return self.data.items()
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __bool__(self):
        """Return True if the inventory has any data."""
        return bool(self.data)
    
    def __len__(self):
        """Return the number of currencies in the inventory."""
        return len(self.data)
    
    def is_empty(self) -> bool:
        """Check if the inventory is empty."""
        return not self.data or all(amount == 0 for amount in self.data.values())


class TreeNode:
    """A tree node for account hierarchies."""
    
    def __init__(self, name: str):
        self.account = name  # Change from 'name' to 'account' to match expected structure
        self.children: List[TreeNode] = []  # Change to list to match expected structure
        self.balance: SimpleInventory = SimpleInventory()  # Use inventory with reduce method
        self.balance_children: SimpleInventory = SimpleInventory()  # Cumulative balance including children
        self.has_txns = False
        self.cost: Optional[SimpleInventory] = None
        self.cost_children: Optional[SimpleInventory] = None
        # Also keep a mapping for efficient lookups
        self._children_by_name: Dict[str, TreeNode] = {}
        
    def get(self, account: str) -> TreeNode:
        """Get a child node by account name."""
        if not account:
            return self
        
        parts = account.split(':')
        current = self
        for part in parts:
            if part not in current._children_by_name:
                new_node = TreeNode(current.account + ':' + part if current.account else part)
                current.children.append(new_node)
                current._children_by_name[part] = new_node
            current = current._children_by_name[part]
        return current
        
    def serialise_with_context(self) -> Dict[str, Any]:
        """Serialize the tree node with context."""
        return {
            'account': self.account,
            'balance': self.balance.data,
            'balance_children': self.balance_children.data,
            'children': [child.serialise_with_context() for child in self.children],
            'has_txns': self.has_txns,
            'cost': self.cost.data if self.cost else None,
            'cost_children': self.cost_children.data if self.cost_children else None
        }
        
    def serialise(self, conversion=None, prices=None, date=None, with_cost=False) -> Dict[str, Any]:
        """Serialize the tree node."""
        return self.serialise_with_context()
        
    @staticmethod
    def net_profit(options, label="Net Profit") -> TreeNode:
        """Create a net profit node."""
        node = TreeNode(label)
        return node


class FilterEntries:
    """Filter entries result container."""
    
    def __init__(
        self,
        entries: List[Directive],
        options: Dict[str, Any],
        fava_options: FavaOptions
    ):
        self.entries = entries
        self.options = options
        self.fava_options = fava_options
        
        # Calculate date range from entries
        dates = []
        for entry in entries:
            if hasattr(entry, 'date'):
                dates.append(entry.date)
        
        if dates:
            self.date_range = DateRange(min(dates), max(dates))
        else:
            # Default date range if no entries
            today = datetime.date.today()
            self.date_range = DateRange(today, today)
        
        # Build account trees
        self.root_tree = self._build_tree(closed=False)
        self.root_tree_closed = self._build_tree(closed=True)
        
        # Create entries with all prices (for now, just use entries as-is)
        self.entries_with_all_prices = list(entries)
        
    def _build_tree(self, closed: bool = False) -> TreeNode:
        """Build the account tree from entries."""
        root = TreeNode('')
        
        # Build tree structure from accounts in entries and calculate balances
        account_balances: Dict[str, Dict[str, float]] = {}
        
        for entry in self.entries:
            if hasattr(entry, 'account') and entry.account:
                # For non-transaction entries (like Open, Close)
                if entry.account not in account_balances:
                    account_balances[entry.account] = {}
            elif hasattr(entry, 'postings') and entry.postings:
                # For transaction entries
                for posting in entry.postings:
                    if hasattr(posting, 'account'):
                        account = posting.account
                        if account not in account_balances:
                            account_balances[account] = {}
                        
                        # Add posting amount to balance
                        if hasattr(posting, 'units') and posting.units:
                            currency = posting.units.currency
                            amount = float(posting.units.number)
                            if currency in account_balances[account]:
                                account_balances[account][currency] += amount
                            else:
                                account_balances[account][currency] = amount
        
        # Create tree nodes for all accounts and set their balances
        for account, balance in account_balances.items():
            node = root.get(account)
            node.balance = SimpleInventory(balance.copy())
            node.balance_children = SimpleInventory(balance.copy())
            node.has_txns = any(amount != 0 for amount in balance.values())
        
        # Calculate cumulative balances (balance_children)
        # This is a simplified version - in real Fava this would be more complex
        self._calculate_balance_children(root)
            
        return root
    
    def _calculate_balance_children(self, node: TreeNode) -> None:
        """Calculate cumulative balances for all children."""
        # First, recursively calculate for all children
        for child in node.children:
            self._calculate_balance_children(child)
            
            # Add child's balance_children to this node's balance_children
            for currency, amount in child.balance_children.items():
                if currency in node.balance_children.data:
                    node.balance_children.data[currency] += amount
                else:
                    node.balance_children.data[currency] = amount
    
    @property
    def end_date(self) -> datetime.date:
        """The end date of the filtered entries."""
        return self.date_range.end
    
    @property
    def begin_date(self) -> datetime.date:
        """The begin date of the filtered entries."""
        return self.date_range.begin
    
    def interval_ranges(self, interval: Interval) -> List[DateRange]:
        """Generate date ranges for the specified interval."""
        ranges = []
        current_date = self.date_range.begin
        
        # For now, create a simple implementation that generates monthly intervals
        while current_date <= self.date_range.end:
            if interval == Interval.MONTH:
                # Move to start of month
                start = current_date.replace(day=1)
                # Move to start of next month, then subtract one day
                if start.month == 12:
                    next_month = start.replace(year=start.year + 1, month=1)
                else:
                    next_month = start.replace(month=start.month + 1)
                end = next_month - datetime.timedelta(days=1)
                
                ranges.append(DateRange(start, end))
                current_date = next_month
                
            elif interval == Interval.YEAR:
                # Move to start of year
                start = current_date.replace(month=1, day=1)
                # Move to start of next year
                next_year = start.replace(year=start.year + 1)
                end = next_year - datetime.timedelta(days=1)
                
                ranges.append(DateRange(start, end))
                current_date = next_year
                
            elif interval == Interval.DAY:
                ranges.append(DateRange(current_date, current_date))
                current_date += datetime.timedelta(days=1)
                
            else:
                # Default to the entire range for unknown intervals
                ranges.append(self.date_range)
                break
        
        return ranges
    
    @property
    def entries_with_balances_from_realization(self):
        """Provide compatibility with original Fava API."""
        return self.entries
    
    @property
    def prices(self):
        """Provide access to price entries."""
        from fava.beans.prices import FavaPriceMap
        price_entries = [e for e in self.entries if hasattr(e, '__class__') and e.__class__.__name__ == 'Price']
        return FavaPriceMap(price_entries)
    
    def get_account_entries(self, account_name: str) -> List[Directive]:
        """Get entries for a specific account."""
        entries = []
        for entry in self.entries:
            if hasattr(entry, 'account') and entry.account == account_name:
                entries.append(entry)
            elif hasattr(entry, 'postings'):
                for posting in entry.postings:
                    if hasattr(posting, 'account') and posting.account == account_name:
                        entries.append(entry)
                        break 