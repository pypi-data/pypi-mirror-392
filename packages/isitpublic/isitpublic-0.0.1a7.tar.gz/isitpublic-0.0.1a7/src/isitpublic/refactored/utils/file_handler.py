"""
Utility functions for file handling operations used in the public domain validator.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union


def ensure_data_directory(filepath: Union[str, Path]) -> Path:
    """
    Ensure that the data directory exists and return the proper file path.

    Args:
        filepath: Original file path

    Returns:
        Path object with proper data directory structure
    """
    filepath = Path(filepath)

    # If no explicit directory is provided, default to data directory
    if filepath.parent == Path("."):
        filepath = Path("data") / filepath.name

    # Create parent directories if they don't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)

    return filepath


def save_json_data(
    data: Dict[str, Any], filepath: Union[str, Path], indent: int = 2
) -> None:
    """
    Save data to a JSON file with proper encoding and formatting.

    Args:
        data: Data to save
        filepath: Path to save the file to
        indent: JSON indentation level
    """
    filepath = ensure_data_directory(filepath)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json_data(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load data from a JSON file.

    Args:
        filepath: Path to load the file from

    Returns:
        Loaded data dictionary
    """
    # If filepath is just a filename, assume it's in the data directory
    filepath = Path(filepath)
    if filepath.parent == Path("."):
        filepath = Path("data") / filepath

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def create_default_config_data(config_type: str) -> Dict[str, Any]:
    """
    Create default configuration data based on the config type.

    Args:
        config_type: Type of configuration ('copyright_terms', 'special_rules', or 'heuristic_indicators')

    Returns:
        Default configuration data
    """
    timestamp = datetime.now().isoformat()

    if config_type == "copyright_terms":
        return {
            "copyright_terms": {},
            "generated_at": timestamp,
            "version": "1.0",
            "description": "Copyright terms by country (years after author's death)",
        }
    elif config_type == "special_rules":
        return {
            "special_rules": {},
            "generated_at": timestamp,
            "version": "1.0",
            "description": "Special copyright rules and exceptions by jurisdiction",
        }
    elif config_type == "heuristic_indicators":
        return {
            "heuristic_indicators": {
                "title_pd_indicators": [],
                "content_pd_indicators": [],
                "historical_authors": [],
                "time_period_indicators": [],
                "genre_pd_indicators": [],
            },
            "generated_at": timestamp,
            "version": "1.0",
            "description": "Heuristic indicators used for public domain determination",
        }
    else:
        return {
            "generated_at": timestamp,
            "version": "1.0",
            "description": f"Default {config_type} configuration",
        }
