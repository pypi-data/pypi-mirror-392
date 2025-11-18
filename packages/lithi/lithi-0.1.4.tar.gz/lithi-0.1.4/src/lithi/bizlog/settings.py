"""Settings for this app."""

from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, Field
from xdg_base_dirs import xdg_cache_home, xdg_config_home

from lithi.bizlog.brand import get_name
from lithi.core.config import Configuration


def get_app_config_dirpath() -> Path:
    """
    Get the configuration directory path.

    This path is based on the XDG configuration home.

    Returns:
        Path: The absolute path to the configuration directory.
    """
    return Path(xdg_config_home()) / get_name()


def get_app_cache_dirpath() -> Path:
    """
    Get the cache directory path.

    This path is based on the XDG cache home.

    Returns:
        Path: The absolute path to the cache directory.
    """
    return Path(xdg_cache_home()) / get_name()


class SessionConfig(BaseModel):
    """Session configuration model."""

    target: str = "sim"
    config: Any | None = None


class DefaultConfig(BaseModel):
    """Default configuration model."""

    session_name: str | None = None


class Settings(Configuration):
    """Application settings."""

    FILEPATH: ClassVar[Path] = Path(get_app_config_dirpath()) / "settings.json"

    default: DefaultConfig = Field(default_factory=DefaultConfig)
    sessions: dict[str, SessionConfig] = Field(default_factory=dict)
