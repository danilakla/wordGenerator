import json
from typing import Any, Union

class ConfigService:
    def __init__(self, config_source: Union[dict, str, None] = None):
        """
        Initialize the ConfigService with either:
        - A dictionary
        - A JSON string
        - A path to a JSON file
        - Nothing (load later with load_from_file)
        
        Args:
            config_source: Either a dictionary, JSON string, or file path
        """
        self.config = {}
        
        if config_source is not None:
            if isinstance(config_source, dict):
                self.config = config_source
            else:
                # Try to interpret as JSON string first, then as file path
                try:
                    self.config = json.loads(config_source)
                except json.JSONDecodeError:
                    self.load_from_file(config_source)
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file contains invalid JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Dot notation path (e.g., "documentFormatting.general.margins.top")
            default: Default value if key not found
            
        Returns:
            The configuration value or default if not found
        """
        keys = key.split('.')
        current = self.config
        
        try:
            for k in keys:
                if k.isdigit() and isinstance(current, list):
                    current = current[int(k)]
                else:
                    current = current[k]
            return current
        except (KeyError, IndexError, TypeError):
            return default
    
    def __getitem__(self, key: str) -> Any:
        """Enable dictionary-style access with dot notation keys."""
        value = self.get(key)
        if value is None:
            raise KeyError(f"Key not found: {key}")
        return value
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the configuration."""
        try:
            self[key]  # Uses __getitem__ which raises KeyError if not found
            return True
        except KeyError:
            return False
    
    def to_dict(self) -> dict:
        """Return the entire configuration as a dictionary."""
        return self.config
    
    def to_json(self, indent: int = 2) -> str:
        """Return the entire configuration as a JSON string."""
        return json.dumps(self.config, indent=indent, ensure_ascii=False)

