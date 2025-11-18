"""Configuration utilities for Kollabor."""

from pathlib import Path
import logging
import shutil

logger = logging.getLogger(__name__)


def get_config_directory() -> Path:
    """Get the Kollabor configuration directory.

    Resolution order:
    1. Local .kollabor-cli/ in current directory (project-specific override)
    2. Global ~/.kollabor-cli/ (default for most users)

    Returns:
        Path to the configuration directory
    """
    local_config_dir = Path.cwd() / ".kollabor-cli"
    global_config_dir = Path.home() / ".kollabor-cli"

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


def get_system_prompt_path() -> Path:
    """Get the system prompt file path, preferring local over global.

    Resolution order:
    1. Local .kollabor-cli/system_prompt/default.md (project-specific override)
    2. Global ~/.kollabor-cli/system_prompt/default.md (global default)

    Returns:
        Path to the system prompt file
    """
    local_config_dir = Path.cwd() / ".kollabor-cli"
    global_config_dir = Path.home() / ".kollabor-cli"

    local_system_prompt = local_config_dir / "system_prompt" / "default.md"
    global_system_prompt = global_config_dir / "system_prompt" / "default.md"

    # If local exists, use it (override)
    if local_system_prompt.exists():
        return local_system_prompt
    # Otherwise use global
    else:
        return global_system_prompt


def initialize_system_prompt() -> None:
    """Initialize system prompt by copying default.md to config directories.

    Copies the bundled system_prompt/default.md to:
    1. Global ~/.kollabor-cli/system_prompt/default.md (if not exists)
    2. Local .kollabor-cli/system_prompt/default.md (if local config dir exists and file not exists)

    This allows users to customize their system prompts, with local overriding global.
    """
    # Find the bundled system prompt file
    try:
        # Try to find it in the package installation directory
        package_dir = Path(__file__).parent.parent.parent  # Go up from core/utils/ to package root
        bundled_system_prompt = package_dir / "system_prompt" / "default.md"

        if not bundled_system_prompt.exists():
            # Fallback for development mode
            bundled_system_prompt = Path.cwd() / "system_prompt" / "default.md"

        if not bundled_system_prompt.exists():
            logger.warning("Could not find bundled system_prompt/default.md")
            return

        # Initialize global system prompt
        global_config_dir = Path.home() / ".kollabor-cli"
        global_config_dir.mkdir(exist_ok=True)
        global_system_prompt_dir = global_config_dir / "system_prompt"
        global_system_prompt_dir.mkdir(exist_ok=True)
        global_system_prompt_file = global_system_prompt_dir / "default.md"

        if not global_system_prompt_file.exists():
            shutil.copy2(bundled_system_prompt, global_system_prompt_file)
            logger.info(f"Initialized global system prompt: {global_system_prompt_file}")

        # Initialize local system prompt if local config directory exists
        local_config_dir = Path.cwd() / ".kollabor-cli"
        if local_config_dir.exists():
            local_system_prompt_dir = local_config_dir / "system_prompt"
            local_system_prompt_dir.mkdir(exist_ok=True)
            local_system_prompt_file = local_system_prompt_dir / "default.md"

            if not local_system_prompt_file.exists():
                shutil.copy2(bundled_system_prompt, local_system_prompt_file)
                logger.info(f"Initialized local system prompt: {local_system_prompt_file}")

    except Exception as e:
        logger.error(f"Failed to initialize system prompt: {e}")
