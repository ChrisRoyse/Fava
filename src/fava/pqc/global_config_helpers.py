# src/fava/pqc/global_config_helpers.py
"""
Helper modules for GlobalConfig, with safer parsing and basic validation.
"""
import ast
from typing import Any, Dict
# Assuming PQCInternalParsingError is correctly defined in .exceptions
# If not, this import needs to be adjusted or the exception handled differently.
from .exceptions import ParsingError as PQCInternalParsingError

class FileSystemHelper:
    """Placeholder for file system operations."""
    @staticmethod
    def read_file_content(path: str) -> str:
        """Reads file content safely."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {path}")
        except IOError as e:
            raise IOError(f"Failed to read configuration file {path}: {e}") from e

class ParserHelper:
    """Helper for parsing configuration content safely."""
    @staticmethod
    def parse_python_like_structure(content: str) -> Dict[str, Any]:
        """
        Safely parses a string that should represent a Python dictionary.
        Uses ast.literal_eval to prevent arbitrary code execution.
        """
        try:
            # Handle CONFIG = {...} format by extracting the assignment value
            if 'CONFIG = ' in content:
                # Parse the file as AST and extract the CONFIG assignment
                tree = ast.parse(content)
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == 'CONFIG':
                                # Evaluate the assigned value safely
                                parsed = ast.literal_eval(node.value)
                                if not isinstance(parsed, dict):
                                    raise PQCInternalParsingError("CONFIG is not a dictionary.")
                                return parsed
                raise PQCInternalParsingError("CONFIG assignment not found in file.")
            else:
                # Direct dictionary literal
                parsed = ast.literal_eval(content)
                if not isinstance(parsed, dict):
                    raise PQCInternalParsingError("Parsed content is not a dictionary.")
                return parsed
        except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as e:
            # These are exceptions ast.literal_eval can raise for malformed input
            raise PQCInternalParsingError(
                f"Failed to safely parse Python-like structure: {e}"
            ) from e

class ValidatorHelper:
    """Helper for schema validation operations."""
    @staticmethod
    def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validates the data against a simple expected schema.
        For the placeholder schema {"version": 1}, it checks:
        1. 'version' key exists in data.
        2. The value of 'version' is an integer.
        A more comprehensive schema validator would be needed for complex schemas.
        """
        if not isinstance(data, dict):
            return False # Should be caught by parser, but defensive check.

        # Validate against the provided schema structure (e.g., FAVA_CRYPTO_SETTINGS_ExpectedSchema)
        for schema_key in schema:
            if schema_key not in data:
                return False # A key expected by the schema is missing in the data

        # Specific check for 'version' key as per placeholder schema
        if "version" in schema: # If 'version' is part of the schema to check
            if "version" not in data or not isinstance(data.get("version"), int):
                return False
        
        # This validation is basic and tailored to the simple placeholder schema.
        # A production system would use a more robust schema definition and validation library.
        return True

# Expose instances or static methods for easier patching in tests if needed,
# matching the test structure e.g., fava.pqc.global_config.file_system.READ_FILE_CONTENT
file_system = FileSystemHelper
parser = ParserHelper
validator = ValidatorHelper