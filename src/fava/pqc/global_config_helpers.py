# src/fava/pqc/global_config_helpers.py
"""
Placeholder helper modules for GlobalConfig, intended for mocking in tests.
"""

class FileSystemHelper:
    """Placeholder for file system operations."""
    @staticmethod
    def read_file_content(path: str) -> str:
        """Simulates reading file content."""
        # This will be mocked in tests.
        # In a real scenario, this would read from the actual file system.
        raise NotImplementedError("FileSystemHelper.read_file_content should be mocked.")

class ParserHelper:
    """Placeholder for parsing operations."""
    @staticmethod
    def parse_python_like_structure(content: str) -> dict:
        """Simulates parsing a Python-like structure."""
        # This will be mocked in tests.
        # In a real scenario, this might use ast.literal_eval or similar.
        raise NotImplementedError("ParserHelper.parse_python_like_structure should be mocked.")

class ValidatorHelper:
    """Placeholder for schema validation operations."""
    @staticmethod
    def validate_schema(data: dict, schema: dict) -> bool:
        """Simulates schema validation."""
        # This will be mocked in tests.
        # In a real scenario, this would use a schema validation library.
        raise NotImplementedError("ValidatorHelper.validate_schema should be mocked.")

# Expose instances or static methods for easier patching in tests if needed,
# matching the test structure e.g., fava.pqc.global_config.file_system.READ_FILE_CONTENT
file_system = FileSystemHelper
parser = ParserHelper
validator = ValidatorHelper