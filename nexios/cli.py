#!/usr/bin/env python
"""
Nexios CLI - Command line interface for the Nexios framework.

This module provides CLI commands for bootstrapping and running Nexios projects.
"""

import os
import sys
import click
import re
import subprocess
import socket
from pathlib import Path
from typing import Optional
from nexios.__main__ import __version__

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "auto_envvar_prefix": "NEXIOS",
}


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


# Command implementations
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


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="Nexios")
def cli():
    """
    Nexios CLI - Command line tools for the Nexios framework.
    """
    pass


@cli.command()
@click.argument("project_name", callback=_validate_project_name, required=True)
@click.option(
    "--output-dir",
    "-o",
    default=".",
    help="Directory where the project should be created.",
    type=click.Path(file_okay=False),
)
@click.option(
    "--title",
    help="Display title for the project (defaults to project name if not provided).",
    callback=_validate_project_title,
)
@click.option(
    "--template",
    "-t",
    type=click.Choice(["basic", "standard", "beta"], case_sensitive=False),
    default="basic",
    help="Template type to use for the project.",
    show_default=True,
)
def new(
    project_name: str,
    output_dir: str,
    title: Optional[str] = None,
    template: str = "basic",
):
    """
    Create a new Nexios project.

    Creates a new Nexios project with the given name in the specified directory.
    The project will be initialized with the selected template structure including
    configuration files and a main application file.

    Available template types:
    - basic: Minimal starter template with essential structure
    - standard: A complete template with commonly used features
    - beta: An advanced template with experimental features
    """
    try:
        output_path = Path(output_dir).resolve()
        project_path = output_path / project_name

        if not project_name.strip():
            _echo_error("Project name cannot be empty.")
            return

        if project_path.exists():
            _echo_error(
                f"Directory {project_path} already exists. Choose a different name or location."
            )
            return

        if not _has_write_permission(output_path):
            _echo_error(
                f"No write permission for directory {output_path}. Choose a different location or run with appropriate permissions."
            )
            return

        project_path.mkdir(parents=True, exist_ok=True)
        _echo_info(
            f"Creating new Nexios project: {project_name} using {template} template"
        )

        template_dir = Path(__file__).parent / "templates" / template.lower()

        if not template_dir.exists():
            _echo_error(
                f"Template directory for '{template}' not found: {template_dir}"
            )
            _echo_error(
                "Please ensure you have the latest version of Nexios installed."
            )
            available_templates = [
                p.name
                for p in (Path(__file__).parent / "templates").glob("*")
                if p.is_dir()
            ]
            if available_templates:
                _echo_info(f"Available templates: {', '.join(available_templates)}")
            return

        for src_path in template_dir.glob("**/*"):
            if src_path.is_dir():
                continue

            rel_path = src_path.relative_to(template_dir)
            dest_path = project_path / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                content = src_path.read_text(encoding="utf-8")
                project_title = title or project_name.replace("_", " ").title()
                content = content.replace("{{project_name}}", project_name)
                content = content.replace("{{project_name_title}}", project_title)
                content = content.replace("{{version}}", __version__)
                dest_path.write_text(content, encoding="utf-8")

            except PermissionError:
                _echo_error(
                    f"Permission denied when writing to {dest_path}. Please check your file permissions."
                )
                return
            except Exception as e:
                _echo_warning(f"Error processing template file {src_path}: {str(e)}")

        env_path = project_path / ".env"
        env_content = [
            "# Environment variables for the Nexios application",
            "DEBUG=True",
            "HOST=127.0.0.1",
            "PORT=4000",
        ]
        env_path.write_text("\n".join(env_content) + "\n", encoding="utf-8")

        _echo_success(f"Project {project_name} created successfully at {project_path}")
        _echo_info("Next steps:")
        _echo_info(f"  1. cd {project_name}")
        _echo_info("  2. pip install -r requirements.txt")
        _echo_info("  3. nexios run")

    except Exception as e:
        _echo_error(f"Error creating project: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    "--host",
    "-h",
    default="127.0.0.1",
    callback=_validate_host,
    help="Host to bind the server to.",
    show_default=True,
)
@click.option(
    "--port",
    "-p",
    default=8000,
    type=int,
    callback=_validate_port,
    help="Port to bind the server to.",
    show_default=True,
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development (uvicorn only).",
)
@click.option(
    "--app",
    "-a",
    "app_path",
    callback=_validate_app_path,
    help="App module path in format 'module:app_variable'. Auto-detected if not specified.",
)
@click.option(
    "--server",
    "-s",
    type=click.Choice(["uvicorn", "granian"], case_sensitive=False),
    default="uvicorn",
    callback=_validate_server,
    help="Server to use for running the application.",
    show_default=True,
)
@click.option(
    "--workers",
    "-w",
    type=int,
    default=1,
    help="Number of worker processes (granian only).",
    show_default=True,
)
def run(host: str, port: int, reload: bool, app_path: Optional[str], server: str, workers: int):
    """
    Run the Nexios application using the specified server.

    Automatically detects the app module if not specified, looking for:
    - main.py with 'app' variable
    - app/main.py with 'app' variable
    - src/main.py with 'app' variable

    Supports both Uvicorn (development) and Granian (production) servers.
    """
    try:
        project_dir = Path.cwd()

        if not app_path:
            app_path = _find_app_module(project_dir)
            if not app_path:
                _echo_error(
                    "Could not automatically find the app module. "
                    "Please specify it with --app option.\n"
                    "Looking for one of:\n"
                    "  - main.py with 'app' variable\n"
                    "  - app/main.py with 'app' variable\n"
                    "  - src/main.py with 'app' variable"
                )
                sys.exit(1)
            _echo_info(f"Auto-detected app module: {app_path}")

        # Check if port is available
        if _is_port_in_use(host, port):
            _echo_error(f"Port {port} is already in use on {host}")
            sys.exit(1)

        # Check server availability
        if not _check_server_installed(server):
            _echo_error(
                f"{server.capitalize()} is not installed. Please install it with:\n"
                f"pip install {server}"
            )
            sys.exit(1)

        # Prepare the command based on server choice
        if server == "uvicorn":
            cmd = [
                "uvicorn",
                app_path,
                "--host",
                host,
                "--port",
                str(port),
            ]
            if reload:
                cmd.append("--reload")
                _echo_info("Auto-reload enabled (development mode)")
        else:  # granian
            cmd = [
                "granian",
                "--host",
                host,
                "--port",
                str(port),
                "--workers",
                str(workers),
                app_path,
            ]
            _echo_info(f"Using {workers} worker process(es)")

        _echo_info(f"Starting Nexios server on http://{host}:{port} using {server}")
        _echo_info(f"Using app module: {app_path}")

        # Run the server
        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        _echo_error(f"Server exited with error: {e}")
        sys.exit(1)
    except Exception as e:
        _echo_error(f"Error running server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
