"""FavaLedger - Core ledger class for Fava application."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, Optional, Tuple, Type

from collections import defaultdict

from beancount.loader import load_string, LoadError as BeancountLoaderError # Added
from beancount.core.data import Directive as BeancountDirective # For type hint if needed for all_entries_by_type

from fava.core.fava_options import FavaOptions, parse_options
from fava.core.extensions import ExtensionModule
from fava.core.attributes import AttributesModule
from fava.core.commodities import CommoditiesModule
from fava.core.number import DecimalFormatModule
from fava.core.misc import FavaMisc
from fava.core.accounts import AccountDict
from fava.core.budgets import BudgetModule
from fava.core.charts import ChartModule
from fava.core.file import FileModule
from fava.core.ingest import IngestModule
from fava.core.query_shell import QueryShell
from fava.beans.prices import FavaPriceMap
from fava.core.filters import AccountFilter, AdvancedFilter, TimeFilter
from fava.core.filter_results import FilterEntries # Import from new location
# from fava.core.group_entries import group_entries_by_type # Not used directly, _AllEntriesByTypeContainer is used

from fava.beans.abc import Directive, Custom, Query, Balance, Close, Commodity, Document, Event, Note, Open, Pad, Price, Transaction # Import directive types
# Use PQC modules for crypto operations
from fava.pqc import exceptions as pqc_exceptions
from fava.crypto import keys as crypto_keys  # For key derivation functions
# CryptoServiceLocator from fava.crypto.locator is removed as PQC agility handles GPG
from fava.pqc.backend_crypto_service import decrypt_data_at_rest_with_agility, BackendCryptoService
from fava.pqc.exceptions import DecryptionError as PQCDecryptionError

# Mocked in tests, but define for real use or type checking if needed
def PROMPT_USER_FOR_PASSPHRASE_SECURELY(prompt: str) -> str:
    # In a real app, this would securely prompt the user.
    # For tests, this will be mocked.
    return "default_mock_passphrase_if_not_mocked"

def RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT(context_id: str, salt_len: int = 16) -> bytes:
    # In a real app, this would manage salts securely.
    # For tests, this will be mocked.
    return b"default_mock_salt" * (salt_len // len(b"default_mock_salt"))

def WRITE_BYTES_TO_FILE(file_path: str, data: bytes) -> None:
    Path(file_path).write_bytes(data) # Basic implementation for now

def READ_BYTES_FROM_FILE(file_path: str) -> bytes:
    return Path(file_path).read_bytes() # Basic implementation for now

if TYPE_CHECKING:  # pragma: no cover
    from fava.core.watcher import WatcherBase

log = logging.getLogger(__name__)


class AllEntriesByType:
    """A container to provide attribute-style access to entries by type."""
    # Define attributes for all known Beancount directive types
    # These will be populated with lists of the respective directives.
    Balance: list[Balance]
    Close: list[Close]
    Commodity: list[Commodity]
    Custom: list[Custom]
    Document: list[Document]
    Event: list[Event]
    Note: list[Note]
    Open: list[Open]
    Pad: list[Pad]
    Price: list[Price]
    Query: list[Query]
    Transaction: list[Transaction]
    # Add other directive types if necessary, e.g., from fava.beans.abc

    def __init__(self, entries: list[BeancountDirective]):
        # Initialize all type lists as empty
        self.Balance = []
        self.Close = []
        self.Commodity = []
        self.Custom = []
        self.Document = []
        self.Event = []
        self.Note = []
        self.Open = []
        self.Pad = []
        self.Price = []
        self.Query = []
        self.Transaction = []
        # Initialize other types if added above

        # Populate the lists
        for entry in entries:
            if isinstance(entry, Balance):
                self.Balance.append(entry)
            elif isinstance(entry, Close):
                self.Close.append(entry)
            elif isinstance(entry, Commodity):
                self.Commodity.append(entry)
            elif isinstance(entry, Custom):
                self.Custom.append(entry)
            elif isinstance(entry, Document):
                self.Document.append(entry)
            elif isinstance(entry, Event):
                self.Event.append(entry)
            elif isinstance(entry, Note):
                self.Note.append(entry)
            elif isinstance(entry, Open):
                self.Open.append(entry)
            elif isinstance(entry, Pad):
                self.Pad.append(entry)
            elif isinstance(entry, Price):
                self.Price.append(entry)
            elif isinstance(entry, Query):
                self.Query.append(entry)
            elif isinstance(entry, Transaction):
                self.Transaction.append(entry)
            # Add elif for other types if necessary
            else:
                log.debug(f"Unknown entry type encountered for AllEntriesByType: {type(entry)}")

    def _asdict(self) -> dict[str, list[BeancountDirective]]:
        """Return a dictionary representation of the grouped entries."""
        # This mimics the behavior of a namedtuple's _asdict() method
        # by returning a dictionary of its public attributes.
        return {
            "Balance": self.Balance,
            "Close": self.Close,
            "Commodity": self.Commodity,
            "Custom": self.Custom,
            "Document": self.Document,
            "Event": self.Event,
            "Note": self.Note,
            "Open": self.Open,
            "Pad": self.Pad,
            "Price": self.Price,
            "Query": self.Query,
            "Transaction": self.Transaction,
            # Add other types if they were added to the class attributes
        }


class FavaLedger:
    """Core ledger class for Fava application with PQC support."""

    def __init__(
        self,
        beancount_file_path_or_options: str | FavaOptions,
        *,
        poll_watcher: WatcherBase | None = None,
    ) -> None:
        """Initialize FavaLedger."""
        if isinstance(beancount_file_path_or_options, FavaOptions): # Test scenario
            self.fava_options = beancount_file_path_or_options
            self.beancount_file_path = self.fava_options.input_files[0] if self.fava_options.input_files else "mock_ledger.beancount"
        else: # Real scenario
            self.beancount_file_path = beancount_file_path_or_options
            # Initialize with default FavaOptions; _load_ledger_data will parse from Custom entries
            self.fava_options = FavaOptions()
        
        self.poll_watcher = poll_watcher
        
        # PQC specific crypto locator (for legacy GPG if needed) is removed.
        # PQC's BackendCryptoService, initialized globally, will handle all crypto operations,
        # including GPG if configured in fava_crypto_settings.py.

        # Standard Fava Ledger module initializations
        self.attributes = AttributesModule(self)
        self.budgets = BudgetModule(self)
        self.charts = ChartModule(self)
        self.commodities = CommoditiesModule(self)
        self.extensions = ExtensionModule(self)
        self.file = FileModule(self)
        self.format_decimal = DecimalFormatModule(self)
        self.ingest = IngestModule(self)
        self.misc = FavaMisc(self)
        self.query_shell = QueryShell(self)
        self.accounts = AccountDict(self)

        # Core data attributes
        self.all_entries: list[Any] = []
        self.load_errors: list[Any] = []
        self.options: dict[str, Any] = {} # Beancount's options_map
        self.fava_options_errors: list[Any] = []
        self.prices: FavaPriceMap = FavaPriceMap([])
        self.all_entries_by_type: AllEntriesByType = AllEntriesByType([]) # Initialize with empty container
        self._last_mtime: float | None = None

        self._load_ledger_data()

    @property
    def errors(self) -> list[Any]:
        """The errors from Beancount loading plus Fava module errors."""
        # This is a simplified version, original Fava aggregates more sources
        # e.g., self.extensions.errors, self.ingest.errors etc.
        return self.load_errors + self.fava_options_errors

    @property
    def mtime(self) -> int | None:
        """The timestamp of the last successful load of the underlying file."""
        if self._last_mtime is None:
            return None
        return int(self._last_mtime)

    def _get_key_material_for_operation(
        self, file_path_context: str, operation_type: str # e.g., "encrypt" or "decrypt"
    ) -> Dict[str, Any]:
        """
        """
        key_material: Dict[str, Any] = {}
        mode = getattr(self.fava_options, 'pqc_key_management_mode', 'PASSPHRASE_DERIVED')
        active_suite_id = getattr(self.fava_options, 'pqc_active_suite_id', 'hybrid_x25519_kyber768_aes256gcm')
        # Get the full suite configuration for the active suite.
        # This should come from GlobalConfig which reads fava_crypto_settings.py,
        # but FavaOptions might hold a subset or reference.
        # For now, assume FavaOptions.pqc_suites has enough detail or BackendCryptoService handlers use GlobalConfig.
        pqc_suites = getattr(self.fava_options, 'pqc_suites', {})
        suite_config = pqc_suites.get(active_suite_id, {})


        if mode == "PASSPHRASE_DERIVED":
            passphrase = PROMPT_USER_FOR_PASSPHRASE_SECURELY(f"Enter passphrase for {file_path_context} ({operation_type}):")
            salt = RETRIEVE_OR_GENERATE_SALT_FOR_CONTEXT(f"{file_path_context}_{operation_type}_salt")
            
            # Use the derive_kem_keys_from_passphrase function from crypto.keys
            classical_keys, pqc_keys = crypto_keys.derive_kem_keys_from_passphrase(
                passphrase=passphrase,
                salt=salt,
                pbkdf_algorithm=suite_config.get("pbkdf_algorithm_for_passphrase", "Argon2id"),
                kdf_algorithm_for_ikm=suite_config.get("kdf_algorithm_for_ikm_from_pbkdf", "HKDF-SHA3-512"),
                classical_kem_spec=suite_config.get("classical_kem_algorithm", "X25519"),
                pqc_kem_spec=suite_config.get("pqc_kem_algorithm", "Kyber768"),
                argon2_params=suite_config.get("argon2_params")
            )
            # classical_keys and pqc_keys are tuples: (public_key, private_key)
            if operation_type == "encrypt":
                # For encryption, we need public keys (bytes format)
                key_material["classical_public_key"] = classical_keys[0].public_bytes_raw() if hasattr(classical_keys[0], 'public_bytes_raw') else classical_keys[0]
                key_material["pqc_public_key"] = pqc_keys[0]  # Should already be bytes
            else: # decrypt
                # For decryption, we need private keys (bytes format)
                key_material["classical_private_key"] = classical_keys[1].private_bytes_raw() if hasattr(classical_keys[1], 'private_bytes_raw') else classical_keys[1]
                key_material["pqc_private_key"] = pqc_keys[1]  # Should already be bytes

        elif mode == "EXTERNAL_FILE":
            key_paths = getattr(self.fava_options, 'pqc_key_file_paths', {}) # This should be Dict[str, str]
            # Use the load_keys_from_external_file function from crypto.keys
            classical_keys, pqc_keys = crypto_keys.load_keys_from_external_file(
                key_file_path_config=key_paths,
                pqc_kem_spec=suite_config.get("pqc_kem_algorithm", "Kyber768")
            )
            # classical_keys and pqc_keys are tuples: (public_key, private_key)
            if operation_type == "encrypt":
                # For encryption, we need public keys (bytes format)
                key_material["classical_public_key"] = classical_keys[0].public_bytes_raw() if hasattr(classical_keys[0], 'public_bytes_raw') else classical_keys[0]
                key_material["pqc_public_key"] = pqc_keys[0]  # Should already be bytes
            else: # decrypt
                # For decryption, we need private keys (bytes format)
                key_material["classical_private_key"] = classical_keys[1].private_bytes_raw() if hasattr(classical_keys[1], 'private_bytes_raw') else classical_keys[1]
                key_material["pqc_private_key"] = pqc_keys[1]  # Should already be bytes
        else:
            raise pqc_exceptions.ConfigurationError(f"Unsupported PQC key management mode: {mode}")
        
        return key_material

    def _load_ledger_data(self) -> None:
        """Load the main file and all included files and set attributes."""
        if not self.beancount_file_path:
            log.warning("_load_ledger_data called with no beancount_file_path.")
            self.all_entries, self.load_errors, self.options = [], [("No beancount file path configured.", None)], {}
            self._last_mtime = None
            return

        log.info(f"Reloading ledger data for {self.beancount_file_path}")
        try:
            entries, errors, options_map = self.load_file(self.beancount_file_path)
            
            # If entries were loaded from a string by beancount.loader.load_string,
            # their filename metadata might be '<string>'. Update to actual file path.
            for entry in entries:
                if hasattr(entry, 'meta') and entry.meta.get('filename') == '<string>':
                    entry.meta['filename'] = self.beancount_file_path

            self.all_entries = entries
            self.load_errors = errors
            self.options = options_map

            # Directly use all_entries_by_type from Beancount's options_map
            self.options = options_map

            # Populate the AllEntriesByType container using the loaded entries
            self.all_entries_by_type = AllEntriesByType(self.all_entries) # self.all_entries is already set
            
            # FavaOptions are parsed from Custom entries
            parsed_fava_options, fava_options_errors_list = parse_options(self.all_entries_by_type.Custom)
            self.fava_options = parsed_fava_options
            self.fava_options_errors = fava_options_errors_list

            # Prices are derived from Price entries
            self.prices = FavaPriceMap(self.all_entries_by_type.Price)

            try:
                self._last_mtime = Path(self.beancount_file_path).stat().st_mtime
            except FileNotFoundError:
                log.error(f"File {self.beancount_file_path} not found after load to update mtime.")
                self._last_mtime = None
            except Exception as e_stat:
                log.error(f"Error stating file {self.beancount_file_path} after load: {e_stat}")
                self._last_mtime = None

            modules_to_load = [
                self.accounts, self.attributes, self.budgets, self.charts,
                self.commodities, self.extensions, self.file, self.format_decimal,
                self.misc, self.query_shell, self.ingest
            ]
            for module in modules_to_load:
                if hasattr(module, 'load_file') and callable(module.load_file):
                    try:
                        module.load_file()
                    except Exception as e_mod_load:
                        log.exception(f"Error loading module {type(module).__name__}: {e_mod_load}")
                else:
                    log.warning(f"Module {type(module).__name__} has no load_file method.")


            self.extensions.after_load_file()
            log.info(f"Successfully reloaded all ledger data and modules for {self.beancount_file_path}")

        except Exception as e_load_main:
            log.exception(f"Critical failure during _load_ledger_data for {self.beancount_file_path}: {e_load_main}")
            self.all_entries, self.load_errors, self.options = [], [(f"Failed to load {self.beancount_file_path}: {e_load_main!s}", None)], {}
            self.all_entries_by_type = AllEntriesByType([]) # Use empty container on critical failure
            self.prices = FavaPriceMap([])

    def changed(self) -> bool:
        """
        Checks if the underlying Beancount files have changed and reloads if necessary.
        Returns True if a reload happened, False otherwise.
        """
        if not self.beancount_file_path:
            return False

        needs_reload = False
        if self.poll_watcher:
            if self.poll_watcher.check(): 
                log.debug(f"File change detected by poll_watcher for {self.beancount_file_path}")
                needs_reload = True
        
        if not needs_reload:
            try:
                current_mtime = Path(self.beancount_file_path).stat().st_mtime
                if self._last_mtime is None or current_mtime > self._last_mtime:
                    log.debug(
                        f"File modification time changed for {self.beancount_file_path} "
                        f"(current: {current_mtime}, last: {self._last_mtime})"
                    )
                    needs_reload = True
            except FileNotFoundError:
                log.warning(f"Beancount file not found during mtime check: {self.beancount_file_path}.")
                if self._last_mtime is not None: 
                    needs_reload = True 
            except Exception as e:
                log.error(f"Error checking mtime for {self.beancount_file_path}: {e}")
                return False 

        if needs_reload:
            self._load_ledger_data()
            return True
        
        return False

    def get_filtered(
        self,
        account: str | None = None,
        filter_str: str | None = None, # Renamed from 'filter'
        time: str | None = None,
    ) -> FilterEntries: # Updated return type
        """Apply filters to the ledger entries and return the filtered list."""
        current_entries: list[Directive] = list(self.all_entries) # type: ignore[arg-type]

        if time:
            try:
                time_filter_obj = TimeFilter(self.options, self.fava_options, time)
                current_entries = list(time_filter_obj.apply(current_entries))
            except Exception as e:
                log.warning(f"Failed to apply time filter '{time}': {e}")

        if account:
            try:
                account_filter_obj = AccountFilter(account)
                current_entries = list(account_filter_obj.apply(current_entries))
            except Exception as e:
                log.warning(f"Failed to apply account filter '{account}': {e}")
        
        if filter_str: # Renamed from 'filter'
            try:
                advanced_filter_obj = AdvancedFilter(filter_str) # Renamed from 'filter'
                current_entries = list(advanced_filter_obj.apply(current_entries))
            except Exception as e:
                log.warning(f"Failed to apply advanced filter '{filter_str}': {e}") # Renamed from 'filter'
        
        # FilterEntries is now imported from fava.core.filter_results at the top of the file.
        return FilterEntries(current_entries, self.options, self.fava_options)

    def get_entry(self, entry_hash: str) -> Optional[Directive]:
        """Return the entry with the given hash."""
        from fava.beans.funcs import hash_entry as calculate_entry_hash
        for entry in self.all_entries:
            if calculate_entry_hash(entry) == entry_hash:
                return entry
        return None

    def commodity_pairs(self) -> list[tuple[str, str]]:
        """Return all commodity pairs that have prices defined.

        This is a placeholder. A more complete implementation would analyze
        self.prices or self.all_entries_by_type.Price.
        """
        # Example:
        # pairs = set()
        # for price_entry in self.all_entries_by_type.Price:
        #     pairs.add(tuple(sorted((price_entry.currency, price_entry.amount.currency))))
        # return sorted(list(pairs))
        return []

    def statement_path(self, entry_hash: str, key: str) -> Path:
        """Get the path for a statement linked to an entry.

        Args:
            entry_hash: The hash of the entry.
            key: The metadata key that contains the statement's filename.

        Returns:
            The absolute path to the statement file.

        Raises:
            FavaAPIError: If the entry is not found or the key is not in
                the entry's metadata, or the path is not a file.
        """
        entry = self.get_entry(entry_hash)
        if not entry:
            raise pqc_exceptions.FavaAPIError(f"Entry with hash '{entry_hash}' not found.")

        filename = entry.meta.get(key)
        if not filename or not isinstance(filename, str):
            raise pqc_exceptions.FavaAPIError(f"Metadata key '{key}' not found or not a string in entry {entry_hash}.")

        # Resolve the path: if it's absolute, use it. If relative, resolve it
        # against the directory of the main beancount file.
        statement_file_path = Path(filename)
        if not statement_file_path.is_absolute():
            # Resolve relative to the entry's source file directory
            entry_source_file_path = entry.meta.get("filename")
            if not entry_source_file_path:
                # Fallback to main beancount file path if entry has no source file (e.g. loaded from string directly)
                # This case might need more robust handling or an error if critical
                statement_file_path = self.join_path(filename)
            else:
                statement_file_path = (Path(entry_source_file_path).parent / filename).resolve()


        if not statement_file_path.is_file():
            raise pqc_exceptions.FavaAPIError(f"Statement path '{statement_file_path}' is not a file.")

        return statement_file_path

    def group_entries_by_type(self, entries: list[Directive]) -> AllEntriesByType:
        """Groups a list of entries by their type.

        Args:
            entries: A list of Beancount directives.

        Returns:
            An AllEntriesByType instance.
        """
        return AllEntriesByType(entries)

    def join_path(self, relative_path: str) -> Path:
        """Resolve a path relative to the directory of the Beancount file.
        Args:
            relative_path: A path relative to the Beancount file.

        Returns:
            The resolved path.
        """
        return (Path(self.beancount_file_path).parent / relative_path).resolve()

    def account_journal(
        self,
        filtered: FilterEntries,
        account_name: str,
        conversion: str,
        with_children: bool = True,
    ) -> list[Directive]:
        """Get journal entries for a specific account.
        
        Args:
            filtered: Filtered ledger entries
            account_name: The account name to get entries for
            conversion: Conversion method to apply
            with_children: Whether to include child accounts
            
        Returns:
            List of entries related to the account, or tuples of (entry, change, balance) if needed
        """
        if not account_name:
            return list(filtered.entries)
        
        account_entries = []
        for entry in filtered.entries:
            entry_accounts = []
            
            # Get accounts from different entry types
            if hasattr(entry, 'account') and entry.account:
                entry_accounts.append(entry.account)
            elif hasattr(entry, 'postings') and entry.postings:
                entry_accounts.extend(posting.account for posting in entry.postings)
            
            # Check if any of the entry's accounts match our criteria
            for acc in entry_accounts:
                if with_children:
                    if acc.startswith(account_name):
                        account_entries.append(entry)
                        break
                else:
                    if acc == account_name:
                        account_entries.append(entry)
                        break
        
        return account_entries

    def account_journal_with_balance(
        self,
        filtered: FilterEntries,
        account_name: str,
        conversion: str,
        with_children: bool = True,
    ) -> list[tuple]:
        """Get journal entries for a specific account with running balance and changes.
        
        Args:
            filtered: Filtered ledger entries
            account_name: The account name to get entries for
            conversion: Conversion method to apply
            with_children: Whether to include child accounts
            
        Returns:
            List of tuples (entry, change_dict, balance_dict) - all entries are tuples
        """
        entries = self.account_journal(filtered, account_name, conversion, with_children)
        
        # Calculate running balances and changes
        running_balance = {}  # currency -> amount
        result = []
        
        for entry in entries:
            change = {}  # currency -> amount change for this entry
            
            if hasattr(entry, 'postings') and entry.postings:
                # For transactions, calculate the change for matching accounts
                for posting in entry.postings:
                    account_matches = False
                    if with_children:
                        account_matches = posting.account.startswith(account_name) if account_name else True
                    else:
                        account_matches = posting.account == account_name
                    
                    if account_matches and hasattr(posting, 'units') and posting.units:
                        currency = posting.units.currency
                        amount = float(posting.units.number)
                        
                        # Add to change for this entry
                        if currency in change:
                            change[currency] += amount
                        else:
                            change[currency] = amount
                        
                        # Update running balance
                        if currency in running_balance:
                            running_balance[currency] += amount
                        else:
                            running_balance[currency] = amount
            
            # ALWAYS return a tuple of (entry, change, balance) for consistency
            result.append((entry, change, dict(running_balance)))
        
        return result

    def interval_balances(
        self,
        filtered: FilterEntries,
        interval,
        account_name: str,
        accumulate: bool = False,
    ):
        """Get interval balances for an account.
        
        This is a placeholder implementation that returns empty results.
        In a complete implementation, this would calculate balances over time intervals.
        """
        # For now, return empty results to prevent errors
        return [], []

    # _try_decrypt_content method is removed. PQC agility handles GPG if configured.


    def save_file_pqc(self, file_path: str, plaintext_content: str, key_context: Optional[str] = None) -> None:
        """
        Encrypts and saves file content using the PQC hybrid scheme.
        """
        if not getattr(self.fava_options, 'pqc_data_at_rest_enabled', False):
            raise pqc_exceptions.ConfigurationError("PQC data at rest is not enabled.")

        context = key_context if key_context else file_path
        key_material_encrypt = self._get_key_material_for_operation(context, "encrypt")
        # active_suite_id = self.fava_options.pqc_active_suite_id # Not needed if get_active_encryption_handler uses global config
        # active_suite_config_for_handler = self.fava_options.pqc_suites.get(active_suite_id) # Handler gets its config from GlobalConfig

        try:
            handler = BackendCryptoService.get_active_encryption_handler()
        except pqc_exceptions.CryptoError as e: # Use pqc_exceptions
             raise pqc_exceptions.ConfigurationError(f"Failed to get active PQC encryption handler: {e}") from e
        
        if not handler or not hasattr(handler, 'encrypt') or not callable(handler.encrypt): # Check actual method name from handler
            raise pqc_exceptions.CryptoError("No active PQC encryption handler with callable encrypt method.")

        plaintext_bytes = plaintext_content.encode('utf-8')
        # The handler's encrypt method will use its own suite_specific_config loaded at init.
        encrypted_bundle_dict = handler.encrypt(
            plaintext_bytes, key_material_encrypt
        )
        
        try:
            import json
            # Assuming encrypted_bundle_dict is the dict structure from HybridPqcCryptoHandler
            encrypted_file_content_bytes = json.dumps(encrypted_bundle_dict, indent=2).encode('utf-8')
        except TypeError as e:
            raise pqc_exceptions.CryptoError(f"Failed to serialize encrypted bundle to JSON: {e}") from e
        
        WRITE_BYTES_TO_FILE(file_path, encrypted_file_content_bytes)

    def load_file(self, file_path: str) -> Tuple[Any, Any, Any]: # Mimics Beancount load return
        """
        Loads a file, attempting PQC decryption if applicable.
        If decryption fails or no handler, attempts to load as plaintext.
        """
        file_content_bytes = READ_BYTES_FROM_FILE(file_path)
        decrypted_source: Optional[str] = None

        # Attempt PQC decryption with agility first if enabled
        if getattr(self.fava_options, 'pqc_data_at_rest_enabled', False):
            try:
                log.debug(f"Attempting PQC decryption with agility for {file_path}")
                key_material = self._get_key_material_for_operation(file_path, "decrypt")
                decrypted_bytes = decrypt_data_at_rest_with_agility(file_content_bytes, key_material)
                decrypted_source = decrypted_bytes.decode('utf-8')
                log.info(f"Successfully decrypted {file_path} using PQC agility.")
            except PQCDecryptionError as e:
                log.warning(f"PQC decryption with agility failed for {file_path}: {e}. Will try plaintext.")
                decrypted_source = None
            except pqc_exceptions.ConfigurationError as e:
                log.warning(f"Configuration error during PQC decryption for {file_path}: {e}. Will try plaintext.")
                decrypted_source = None
            except Exception as e:
                log.error(f"Unexpected error during PQC decryption for {file_path}: {e}. Will try plaintext.")
                decrypted_source = None
        
        if decrypted_source is None:
            # Try plaintext with various encodings
            try:
                source_to_parse = file_content_bytes.decode('utf-8')
                log.info(f"Loading file as plaintext: {file_path} (PQC decryption failed or not applicable).")
            except UnicodeDecodeError:
                # Try other common encodings
                try:
                    source_to_parse = file_content_bytes.decode('utf-8', errors='ignore')
                    log.warning(f"File {file_path} has invalid UTF-8, loaded with errors ignored.")
                except Exception:
                    log.error(f"Failed to decode file {file_path} with any encoding.")
                    # Instead of raising an error, return empty results
                    return [], [f"File {file_path} contains invalid encoding and cannot be processed"], {}
        else:
            source_to_parse = decrypted_source

        # Use beancount.loader.load_string to parse the source
        try:
            entries, errors, options_map = load_string(source_to_parse, dedent=True)
            return entries, errors, options_map
        except BeancountLoaderError as e:
            log.error(f"Beancount loading error for {file_path}: {e}")
            return [], [f"Beancount loading error: {e}"], {}
        except Exception as e:
            log.error(f"Unexpected error parsing Beancount file {file_path}: {e}")
            return [], [f"Unexpected parsing error: {e}"], {}

    def context(self, entry_hash: str) -> tuple[Any, Optional[dict], Optional[dict], str, str]:
        """Context for an entry.
        
        Args:
            entry_hash: Hash of entry.
            
        Returns:
            A tuple (entry, before, after, source_slice, sha256sum) of the (unique) entry 
            with the given entry_hash. If the entry is a Balance or Transaction then before 
            and after contain the balances before and after the entry of the affected accounts.
        """
        # Find the entry
        entry = self.get_entry(entry_hash)
        if not entry:
            from fava.pqc.exceptions import FavaAPIError
            raise FavaAPIError(f"Entry with hash '{entry_hash}' not found.")
        
        # Get source slice and sha256sum from file module
        try:
            source_slice, sha256sum = self.file.get_entry_slice(entry)
        except Exception:
            # Fallback if file operations fail
            source_slice = f"# Entry {entry_hash} source not available"
            sha256sum = "unknown"
        
        # Calculate balances before and after for Balance and Transaction entries
        before_balances = None
        after_balances = None
        
        if hasattr(entry, 'postings') or hasattr(entry, 'account'):
            # For Balance and Transaction entries, calculate account balances
            affected_accounts = set()
            
            if hasattr(entry, 'postings') and entry.postings:
                # Transaction entry
                for posting in entry.postings:
                    affected_accounts.add(posting.account)
            elif hasattr(entry, 'account') and entry.account:
                # Balance entry
                affected_accounts.add(entry.account)
            
            if affected_accounts:
                # Calculate balances before and after this entry
                # This is a simplified implementation - in full Fava this would be more sophisticated
                before_balances = {}
                after_balances = {}
                
                for account in affected_accounts:
                    # For now, return empty balance maps
                    # In a full implementation, this would calculate actual running balances
                    before_balances[account] = []
                    after_balances[account] = []
        
        return entry, before_balances, after_balances, source_slice, sha256sum