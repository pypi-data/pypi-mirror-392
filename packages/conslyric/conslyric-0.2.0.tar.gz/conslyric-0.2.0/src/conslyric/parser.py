from typing import Any, Dict

import yaml

from .exceptions import ConslyricParseError, ConslyricValidationError


class ConslyricParser:
    """
    Parses a Conslyric YAML/JSON file and performs basic validation.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: Dict[str, Any] = self._load_file()
        self._validate_schema()

    def _load_file(self) -> Dict[str, Any]:
        """Loads the content of the YAML/JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ConslyricParseError(f"File not found: {self.file_path}")
        except yaml.YAMLError as e:
            raise ConslyricParseError(f"Error parsing YAML file: {e}")

    def _validate_schema(self):
        """Validates the basic structure of the Conslyric data."""
        required_keys = ["consLyric", "metadata", "run"]
        for key in required_keys:
            if key not in self.data:
                raise ConslyricValidationError(f"Missing required key: '{key}'")

        if not isinstance(self.data["metadata"], dict):
            raise ConslyricValidationError("'metadata' must be a map.")
        if not isinstance(self.data["run"], list):
            raise ConslyricValidationError("'run' must be a list.")

        # Validate metadata keys
        required_metadata_keys = ["time", "showDefault", "sleepDefault"]
        for key in required_metadata_keys:
            if key not in self.data["metadata"]:
                raise ConslyricValidationError(
                    f"Missing required key in metadata: '{key}'"
                )

    def get_data(self) -> Dict[str, Any]:
        """Returns the parsed and validated data."""
        return self.data
