"""Configuration file handling for koz."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class KozConfig(BaseModel):
    """Configuration for koz analysis.

    Attributes:
        include: List of regex patterns for files/folders to include
        exclude: List of regex patterns for files/folders to exclude
    """

    include: list[str] = Field(
        default_factory=list,
        description="List of regex patterns for files/folders to include",
    )
    exclude: list[str] = Field(
        default_factory=list,
        description="List of regex patterns for files/folders to exclude",
    )


def load_config(config_path: Path) -> KozConfig:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Loaded configuration object

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
        ValueError: If config doesn't match schema
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        data = {}

    return KozConfig(**data)


def get_default_config() -> KozConfig:
    """Get default configuration (analyze all files).

    Returns:
        Default configuration with empty include/exclude lists
    """
    return KozConfig()
