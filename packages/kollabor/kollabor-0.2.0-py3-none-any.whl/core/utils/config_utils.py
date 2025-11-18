"""Configuration utilities for Kollabor."""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def get_config_directory() -> Path:
    """Get the Kollabor configuration directory.

    Resolution order:
    1. Local .kollabor/ in current directory (project-specific override)
    2. Global ~/.kollabor/ (default for most users)

    Returns:
        Path to the configuration directory
    """
    local_config_dir = Path.cwd() / ".kollabor"
    global_config_dir = Path.home() / ".kollabor"

    if local_config_dir.exists():
        return local_config_dir
    else:
        return global_config_dir


def ensure_config_directory() -> Path:
    """Get and ensure the configuration directory exists.

    Returns:
        Path to the configuration directory
    """
    config_dir = get_config_directory()
    config_dir.mkdir(exist_ok=True)
    return config_dir
