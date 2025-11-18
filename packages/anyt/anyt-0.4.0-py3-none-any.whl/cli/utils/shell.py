"""Shell detection and configuration utilities."""

import os
from pathlib import Path


def detect_shell() -> tuple[str, Path]:
    """Detect current shell and config file location.

    Returns:
        Tuple of (shell_name, config_path)

    Examples:
        >>> shell_name, config_path = detect_shell()
        >>> shell_name
        'zsh'
        >>> config_path
        PosixPath('/Users/user/.zshrc')
    """
    shell = os.environ.get("SHELL", "")

    if "zsh" in shell:
        return "zsh", Path.home() / ".zshrc"
    elif "bash" in shell:
        # Check which exists: .bashrc or .bash_profile
        bashrc = Path.home() / ".bashrc"
        bash_profile = Path.home() / ".bash_profile"
        return "bash", bashrc if bashrc.exists() else bash_profile
    elif "fish" in shell:
        return "fish", Path.home() / ".config" / "fish" / "config.fish"
    else:
        return "unknown", Path.home() / ".profile"


def get_shell_export_command(shell_name: str, api_key: str) -> str:
    """Get the shell-specific export command for setting API key.

    Args:
        shell_name: Name of the shell (zsh, bash, fish, unknown)
        api_key: The API key value to export

    Returns:
        Shell-specific command to export the API key

    Examples:
        >>> get_shell_export_command("zsh", "anyt_agent_xyz")
        'export ANYT_API_KEY=anyt_agent_xyz'
        >>> get_shell_export_command("fish", "anyt_agent_xyz")
        'set -x ANYT_API_KEY anyt_agent_xyz'
    """
    if shell_name == "fish":
        return f"set -x ANYT_API_KEY {api_key}"
    else:
        return f"export ANYT_API_KEY={api_key}"


def get_persistence_command(shell_name: str, config_path: Path, api_key: str) -> str:
    """Get command to persist API key to shell profile.

    Args:
        shell_name: Name of the shell (zsh, bash, fish, unknown)
        config_path: Path to shell config file
        api_key: The API key value to persist

    Returns:
        Command to add API key to shell profile

    Examples:
        >>> get_persistence_command("zsh", Path("~/.zshrc"), "anyt_agent_xyz")
        "echo 'export ANYT_API_KEY=anyt_agent_xyz' >> ~/.zshrc"
    """
    export_cmd = get_shell_export_command(shell_name, api_key)

    if shell_name == "fish":
        return f"echo '{export_cmd}' >> {config_path}"
    else:
        return f"echo '{export_cmd}' >> {config_path}"


def get_source_command(shell_name: str, config_path: Path) -> str:
    """Get command to reload shell configuration.

    Args:
        shell_name: Name of the shell (zsh, bash, fish, unknown)
        config_path: Path to shell config file

    Returns:
        Command to reload shell config

    Examples:
        >>> get_source_command("zsh", Path("~/.zshrc"))
        'source ~/.zshrc'
        >>> get_source_command("fish", Path("~/.config/fish/config.fish"))
        'source ~/.config/fish/config.fish'
    """
    return f"source {config_path}"
