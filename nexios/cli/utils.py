#!/usr/bin/env python
"""
Nexios CLI - Shared utilities and helper functions.
"""

import importlib.util
import os
import re
import socket
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

import click

from nexios.utils.app import get_app_instance

if TYPE_CHECKING:
    from nexios.application import NexiosApp


# Utility functions
def _echo_success(message: str) -> None:
    """Print a success message."""
    click.echo(click.style(f"✓ {message}", fg="green"))


def _echo_error(message: str) -> None:
    """Print an error message."""
    click.echo(click.style(f"✗ {message}", fg="red"), err=True)


def _echo_info(message: str) -> None:
    """Print an info message."""
    click.echo(click.style(f"ℹ {message}", fg="blue"))


def _echo_warning(message: str) -> None:
    """Print a warning message."""
    click.echo(click.style(f"⚠ {message}", fg="yellow"))


def _has_write_permission(path: Path) -> bool:
    """Check if we have write permission for the given path."""
    if path.exists():
        return os.access(path, os.W_OK)
    return os.access(path.parent, os.W_OK)


def _is_port_in_use(host: str, port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def _check_server_installed(server: str) -> bool:
    """Check if the specified server is installed."""
    try:
        subprocess.run([server, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# Validation functions
def _validate_project_name(ctx, param, value):
    """Validate the project name for directory and Python module naming rules."""
    if not value:
        return value

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", value):
        raise click.BadParameter(
            "Project name must start with a letter and contain only letters, "
            "numbers, and underscores."
        )
    return value


def _validate_project_title(ctx, param, value):
    """Validate that the project title does not contain special characters."""
    if not value:
        return value

    if re.search(r"[^a-zA-Z0-9_\s-]", value):
        raise click.BadParameter(
            "Project title should contain only letters, numbers, spaces, underscores, and hyphens."
        )
    return value


def _validate_host(ctx, param, value):
    """Validate hostname format."""
    if value not in ("localhost", "127.0.0.1") and not re.match(
        r"^[a-zA-Z0-9]([a-zA-Z0-9\-\.]{0,61}[a-zA-Z0-9])?$", value
    ):
        raise click.BadParameter(f"Invalid hostname: {value}")
    return value


def _validate_port(ctx, param, value):
    """Validate that the port is within the valid range."""
    if not 1 <= value <= 65535:
        raise click.BadParameter(f"Port must be between 1 and 65535, got {value}.")
    return value


def _validate_app_path(ctx, param, value):
    """Validate module:app format."""
    if value and not re.match(
        r"^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*:[a-zA-Z0-9_]+$", value
    ):
        raise click.BadParameter(
            f"App path must be in the format 'module:app_variable' or 'module.submodule:app_variable', got {value}."
        )
    return value


def _validate_server(ctx, param, value):
    """Validate server choice."""
    if value and value not in ("uvicorn", "granian"):
        raise click.BadParameter("Server must be either 'uvicorn' or 'granian'")
    return value


# App loading functions
def _find_app_module(project_dir: Path) -> Optional[str]:
    """Try to find the app module in the project directory."""
    # Check for main.py with app variable
    main_py = project_dir / "main.py"
    if main_py.exists():
        return "main:app"

    # Check for app/main.py
    app_main = project_dir / "app" / "main.py"
    if app_main.exists():
        return "app.main:app"

    # Check for src/main.py
    src_main = project_dir / "src" / "main.py"
    if src_main.exists():
        return "src.main:app"

    return None


def _find_cli_config_file() -> str | None:
    """Search for nexios.cli.py in the current directory only."""
    cwd = Path.cwd()
    candidate = cwd / "nexios.cli.py"
    if candidate.exists():
        return str(candidate)
    return None


def _load_app_from_string(app_path: str) -> "NexiosApp":
    """Load app from module:app format string."""
    if ":" not in app_path:
        raise RuntimeError("App path must be in format 'module:app'")

    module_name, app_var = app_path.split(":", 1)
    mod = importlib.import_module(module_name)
    app = getattr(mod, app_var, None)
    if app is None:
        raise RuntimeError(f"No '{app_var}' found in module '{module_name}'")

    return app


def _load_app_from_path(app_path: str = None, config_path: str = None) -> "NexiosApp":
    """
    Load the Nexios app instance from the given app_path (module:app) or config file.
    If not provided, auto-detect using the same logic as _find_app_module.
    Now also auto-searches for nexios.cli.py in the current directory.
    """
    # Prefer explicit config_path
    if config_path:
        spec = importlib.util.spec_from_file_location("nexios_config", config_path)
        config_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_mod)  # type: ignore
        if hasattr(config_mod, "app"):
            app_value = config_mod.app
            # Handle case where app is a string (module:app format)
            if isinstance(app_value, str):
                return _load_app_from_string(app_value)
            return app_value
        raise RuntimeError(f"No 'app' found in config file: {config_path}")

    # Auto-search for config file
    auto_config = _find_cli_config_file()
    if auto_config:
        spec = importlib.util.spec_from_file_location("nexios_config", auto_config)
        config_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_mod)  # type: ignore
        if hasattr(config_mod, "app"):
            app_value = config_mod.app
            # Handle case where app is a string (module:app format)
            if isinstance(app_value, str):
                return _load_app_from_string(app_value)
            return app_value
        raise RuntimeError(f"No 'app' found in config file: {auto_config}")

    # Use provided app_path or auto-detect
    if not app_path:
        app_path = _find_app_module(Path.cwd())
        if not app_path:
            raise RuntimeError(
                "Could not find app instance. Please specify --app or --config, or provide a nexios.cli.py file."
            )

    return _load_app_from_string(app_path)


def load_config_module(config_path: Optional[str] = None) -> Tuple[Any, Dict[str, Any]]:
    """
    Load the Nexios config file (nexios.config.py) and return (app, config_dict).
    If config file doesn't exist, return (None, {}).
    """
    config_file = config_path or os.path.join(os.getcwd(), "nexios.config.py")
    if not os.path.exists(config_file):
        return None, {}

    spec = importlib.util.spec_from_file_location("nexios_config", config_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load config file: {config_file}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["nexios_config"] = module
    spec.loader.exec_module(module)

    app_path = getattr(module, "app_path", None)
    app = get_app_instance(app_path) if app_path else None

    # Collect all top-level variables except built-ins and 'app'
    config = {
        k: v
        for k, v in vars(module).items()
        if not k.startswith("__") and k != "app" and not isinstance(v, ModuleType)
    }
    return app, config


def load_config_only(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load the Nexios config file (nexios.config.py) and return only the config dict,
    without loading or importing the app instance. This avoids circular imports.
    """
    config_file = config_path or os.path.join(os.getcwd(), "nexios.config.py")
    if not os.path.exists(config_file):
        return {}

    spec = importlib.util.spec_from_file_location("nexios_config", config_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load config file: {config_file}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["nexios_config"] = module
    spec.loader.exec_module(module)

    # Collect all top-level variables except built-ins and 'app'
    config = {
        k: v
        for k, v in vars(module).items()
        if not k.startswith("__") and k != "app" and not isinstance(v, ModuleType)
    }
    return config


def get_config() -> Dict[str, Any]:
    """
    Return the loaded config (all variables except 'app') from nexios.config.py.
    """
    config = load_config_only()
    return config
