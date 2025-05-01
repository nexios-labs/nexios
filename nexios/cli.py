#!/usr/bin/env python
"""
Nexios CLI - Command line interface for the Nexios framework.

This module provides CLI commands for bootstrapping new Nexios projects
and running development servers.
"""

import os
import sys
import shutil
import click
import re
import socket
import subprocess
import platform
from pathlib import Path
from string import Template
from typing import Optional, List, Union, Callable
import importlib.util
import pkg_resources

from nexios.__main__ import __version__, ascii_art

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "auto_envvar_prefix": "NEXIOS",
}


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


def _is_port_in_use(host: str, port: int) -> bool:
    """Check if the specified port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True


def _validate_hostname(hostname: str) -> bool:
    """Validate hostname format."""
    # Check for valid hostname or IP address format
    if hostname == "localhost" or hostname == "127.0.0.1":
        return True

    # Check for valid IP address
    try:
        socket.inet_aton(hostname)
        return True
    except socket.error:
        # Not a valid IP, check hostname format
        if re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9\-\.]{0,61}[a-zA-Z0-9])?$", hostname):
            return True
    return False


def _is_virtualenv_active() -> bool:
    """Check if running in an active virtual environment."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def _has_write_permission(path: Path) -> bool:
    """Check if we have write permission for the given path."""
    if path.exists():
        return os.access(path, os.W_OK)

    # If the path doesn't exist, check the parent directory
    parent = path.parent
    return os.access(parent, os.W_OK)


def _check_granian_installed() -> bool:
    """Check if granian is installed."""
    try:
        pkg_resources.get_distribution("granian")
        return True
    except pkg_resources.DistributionNotFound:
        return False


def _check_uvicorn_installed() -> bool:
    """Check if uvicorn is installed."""
    try:
        pkg_resources.get_distribution("uvicorn")
        return True
    except pkg_resources.DistributionNotFound:
        return False


def _check_python_version() -> bool:
    """Check if Python version is compatible."""
    import sys

    return sys.version_info >= (3, 9)


def _validate_host(ctx, param, value):
    """Validate hostname format."""
    if not _validate_hostname(value):
        raise click.BadParameter(f"Invalid hostname: {value}")
    return value


def _validate_project_name(ctx, param, value):
    """Validate the project name for directory and Python module naming rules."""
    if not value:
        return value

    # Check if the name is valid for both a directory and a Python module
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", value):
        raise click.BadParameter(
            "Project name must start with a letter and contain only letters, "
            "numbers, and underscores."
        )
    return value


def _validate_port(ctx, param, value):
    """Validate that the port is within the valid range."""
    if not 1 <= value <= 65535:
        raise click.BadParameter(f"Port must be between 1 and 65535, got {value}.")
    return value


def _validate_workers(ctx, param, value):
    """Validate worker count."""
    if value < 1:
        raise click.BadParameter(f"Worker count must be at least 1, got {value}.")
    return value


def _validate_app_path(ctx, param, value):
    """Validate module:app format."""
    if not re.match(r"^[a-zA-Z0-9_]+:[a-zA-Z0-9_]+$", value):
        raise click.BadParameter(
            f"App path must be in the format 'module:app_variable', got {value}."
        )
    return value


def _validate_project_title(ctx, param, value):
    """Validate that the project title does not contain special characters."""
    if not value:
        return value

    # Check if the title contains any special characters that might cause issues
    if re.search(r"[^a-zA-Z0-9_\s-]", value):
        raise click.BadParameter(
            "Project title should contain only letters, numbers, spaces, underscores, and hyphens."
        )
    return value


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="Nexios")
def cli():
    """
    Nexios CLI - Command line tools for the Nexios framework.

    Nexios is a modern, high-performance framework for building scalable applications.
    """
    pass


@cli.command()
def version():
    """Display the Nexios version information."""
    click.echo(ascii_art)
    click.echo(f"Nexios version: {__version__}")
    click.echo("For more information, visit: https://nexios-labs.gitbook.io/nexios")


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
        # Convert to Path objects for cross-platform compatibility
        output_path = Path(output_dir).resolve()
        project_path = output_path / project_name

        # Check for empty project name
        if not project_name.strip():
            _echo_error("Project name cannot be empty.")
            return

        # Check if project directory already exists
        if project_path.exists():
            _echo_error(
                f"Directory {project_path} already exists. Choose a different name or location."
            )
            return

        # Check write permissions on the parent directory
        if not _has_write_permission(output_path):
            _echo_error(
                f"No write permission for directory {output_path}. Choose a different location or run with appropriate permissions."
            )
            return

        # Create the project directory
        project_path.mkdir(parents=True, exist_ok=True)
        _echo_info(
            f"Creating new Nexios project: {project_name} using {template} template"
        )

        # Get the template directory
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

        # Copy template files with pathlib for cross-platform compatibility
        for src_path in template_dir.glob("**/*"):
            # Skip directories, we'll create them as needed
            if src_path.is_dir():
                continue

            # Calculate relative path from template root
            rel_path = src_path.relative_to(template_dir)
            # Create destination path
            dest_path = project_path / rel_path

            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Read template content
            try:
                content = src_path.read_text(encoding="utf-8")

                # Replace template variables
                project_title = title or project_name.replace("_", " ").title()
                content = content.replace("{{project_name}}", project_name)
                content = content.replace("{{project_name_title}}", project_title)
                content = content.replace("{{version}}", __version__)

                # Write processed content
                dest_path.write_text(content, encoding="utf-8")

                # Make main.py executable on Unix-like systems
                if dest_path.name == "main.py" and platform.system() != "Windows":
                    try:
                        dest_path.chmod(
                            dest_path.stat().st_mode | 0o111
                        )  # Add executable bit
                    except PermissionError:
                        _echo_warning(
                            f"Unable to set executable permissions on {dest_path}. You may need to set them manually."
                        )

            except PermissionError:
                _echo_error(
                    f"Permission denied when writing to {dest_path}. Please check your file permissions."
                )
                return
            except Exception as e:
                _echo_warning(f"Error processing template file {src_path}: {str(e)}")

        # Create .env file (not included in template as it shouldn't be in version control)
        env_path = project_path / ".env"
        env_content = [
            "# Environment variables for the Nexios application",
            "DEBUG=True",
            "HOST=127.0.0.1",
            "PORT=4000",
        ]
        env_path.write_text("\n".join(env_content) + "\n", encoding="utf-8")

        _echo_success(f"Project {project_name} created successfully at {project_path}")

        # Check if virtualenv is active and provide appropriate instructions
        if _is_virtualenv_active():
            _echo_info("Next steps:")
            _echo_info(f"  1. cd {project_name}")
            _echo_info("  2. pip install -r requirements.txt")
            _echo_info("  3. nexios run")
        else:
            _echo_info("Next steps:")
            _echo_info(f"  1. cd {project_name}")
            _echo_info("  2. Create and activate a virtual environment (recommended)")
            _echo_info("  3. pip install -r requirements.txt")
            _echo_info("  4. nexios run")

        _echo_info("\nAlternatively, if you prefer Poetry:")
        _echo_info(f"  1. cd {project_name}")
        _echo_info("  2. poetry install")
        _echo_info("  3. poetry run nexios run")

    except Exception as e:
        _echo_error(f"Error creating project: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option(
    "--app",
    "-a",
    default="main:app",
    help="Application import path (module:app_variable).",
    callback=_validate_app_path,
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind the server to.",
    callback=_validate_host,
)
@click.option(
    "--port",
    "-p",
    default=4000,
    type=int,
    help="Port to bind the server to.",
    callback=_validate_port,
)
@click.option(
    "--reload/--no-reload",
    default=True,
    help="Enable/disable auto-reload on code changes.",
)
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(
        ["critical", "error", "warning", "info", "debug", "trace"], case_sensitive=False
    ),
    help="Log level for the server.",
)
@click.option(
    "--workers",
    default=1,
    type=int,
    help="Number of worker processes.",
    callback=_validate_workers,
)
@click.option(
    "--interface",
    default="asgi",
    type=click.Choice(["asgi", "wsgi", "asgi-http"], case_sensitive=False),
    help="Server interface type (Granian only).",
)
@click.option(
    "--http-protocol",
    default="auto",
    type=click.Choice(["h11", "h2", "auto"], case_sensitive=False),
    help="HTTP protocol to use (Granian only).",
)
@click.option(
    "--threading/--no-threading",
    default=False,
    help="Enable/disable threading (Granian only).",
)
@click.option(
    "--access-log/--no-access-log",
    default=True,
    help="Enable/disable access logging.",
)
@click.option(
    "--server",
    type=click.Choice(["auto", "uvicorn", "granian"], case_sensitive=False),
    default="auto",
    help="Server to use for running the application. Auto will prefer Uvicorn.",
)
def run(
    app: str,
    host: str,
    port: int,
    reload: bool,
    log_level: str,
    workers: int,
    interface: str,
    http_protocol: str,
    threading: bool,
    access_log: bool,
    server: str,
):
    """
    Run the Nexios development server.

    Launches a development server using either Uvicorn (default) or Granian
    with the specified options. The server will automatically reload on code
    changes by default. Logs access requests and other information by default.
    """
    # Check Python version compatibility
    if not _check_python_version():
        _echo_error("Nexios requires Python 3.9 or higher.")
        sys.exit(1)

    # Detect available servers
    uvicorn_available = _check_uvicorn_installed()
    granian_available = _check_granian_installed()
    
    # Determine which server to use based on availability and user preference
    use_uvicorn = False
    use_granian = False
    
    if server == "auto":
        # Auto mode: prefer Uvicorn, fall back to Granian
        if uvicorn_available:
            use_uvicorn = True
            _echo_info("Using Uvicorn server (default)")
        elif granian_available:
            use_granian = True
            _echo_info("Using Granian server (Uvicorn not available)")
        else:
            _echo_error(
                "Neither Uvicorn nor Granian is installed. Please install at least one with: "
                "pip install uvicorn or pip install nexios[granian]"
            )
            sys.exit(1)
    elif server == "uvicorn":
        # Explicitly requested Uvicorn
        if uvicorn_available:
            use_uvicorn = True
            _echo_info("Using Uvicorn server (as requested)")
        else:
            _echo_error(
                "Uvicorn is not installed but was explicitly requested. "
                "Please install it with: pip install uvicorn"
            )
            sys.exit(1)
    elif server == "granian":
        # Explicitly requested Granian
        if granian_available:
            use_granian = True
            _echo_info("Using Granian server (as requested)")
        else:
            _echo_error(
                "Granian is not installed but was explicitly requested. "
                "Please install it with: pip install nexios[granian]"
            )
            sys.exit(1)

    # Try to load Nexios configuration if available
    config = None
    try:
        from nexios.config import get_config

        config = get_config()
        _echo_info("Using Nexios configuration for server settings")
    except (ImportError, RuntimeError):
        _echo_info("No Nexios configuration found, using command line parameters")

    try:
        # Check if app file exists in current directory
        app_module = app.split(":")[0]
        app_var = app.split(":")[1]

        if not Path(app_module + ".py").exists() and app_module != "main":
            _echo_warning(
                f"Application file '{app_module}.py' not found in current directory."
            )
            _echo_warning(
                "Make sure you're in the correct project directory or specify the correct app path."
            )

        # Try to import the module to validate it exists and get config
        try:
            if Path(app_module + ".py").exists():
                spec = importlib.util.spec_from_file_location(
                    app_module, Path(app_module + ".py")
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Check if the app variable exists in the module
                    if not hasattr(module, app_var):
                        _echo_warning(
                            f"App variable '{app_var}' not found in module '{app_module}'."
                        )
                        _echo_warning(f"Available variables: {', '.join(dir(module))}")

                    # Try to get the config from the module if it exists
                    if not config and hasattr(module, "app_config"):
                        config = module.app_config
                        _echo_info("Found configuration in application module")
        except Exception as e:
            _echo_warning(f"Error importing module '{app_module}': {str(e)}")
            _echo_warning("This may cause issues when starting the server.")

        # Override command line parameters with config values if available
        if config:
            try:
                # Get server settings from config if they exist
                if hasattr(config, "server"):
                    server_config = config.server
                    host = server_config.get("host", host)
                    port = server_config.get("port", port)
                    workers = server_config.get("workers", workers)
                    log_level = server_config.get("log_level", log_level)
                    reload = server_config.get("reload", reload)
                    interface = server_config.get("interface", interface)
                    http_protocol = server_config.get("http_protocol", http_protocol)
                    threading = server_config.get("threading", threading)
                    access_log = server_config.get("access_log", access_log)
                    
                    # Check for server preference in config
                    if "server" in server_config:
                        server_pref = server_config.get("server", "auto").lower()
                        if server_pref in ["uvicorn", "granian", "auto"] and server == "auto":
                            server = server_pref
                            # Re-evaluate server selection based on config preference
                            if server == "uvicorn" and uvicorn_available:
                                use_uvicorn = True
                                use_granian = False
                                _echo_info("Using Uvicorn server (from config)")
                            elif server == "granian" and granian_available:
                                use_uvicorn = False
                                use_granian = True
                                _echo_info("Using Granian server (from config)")
                    
                    _echo_info("Using server configuration from config")
            except Exception as e:
                _echo_warning(f"Error loading server config: {str(e)}")
                _echo_warning("Using command line parameters instead")

        # Check if port is already in use
        if _is_port_in_use(host, port):
            _echo_error(
                f"Port {port} is already in use. Try a different port with --port option."
            )
            return

        # Display Nexios ASCII art
        click.echo(ascii_art)

        _echo_info(f"Starting development server at http://{host}:{port}")
        if reload:
            _echo_info("Auto-reload is enabled. Press CTRL+C to stop.")

        # Prepare server command based on selected server
        server_cmd = []
        
        if use_uvicorn:
            # Prepare uvicorn command
            server_cmd = [
                "uvicorn",
                app,
                "--host",
                host,
                "--port",
                str(port),
                "--log-level",
                log_level,
            ]

            if reload:
                server_cmd.append("--reload")

            if workers > 1:
                server_cmd.extend(["--workers", str(workers)])
                
            if access_log:
                server_cmd.append("--access-log")
            else:
                server_cmd.append("--no-access-log")
                
        elif use_granian:
            # Prepare granian command
            server_cmd = [
                "granian",
                "--interface",
                interface,
                "--host",
                host,
                "--port",
                str(port),
                "--log-level",
                log_level,
                "--http",
                http_protocol,
                app,
            ]

            if reload:
                server_cmd.append("--reload")

            if workers > 1:
                server_cmd.extend(["--workers", str(workers)])

            if threading:
                server_cmd.append("--threading")

            if access_log:
                server_cmd.append("--access-log")
        
        # Log the command for debugging purposes
        _echo_info(f"Running command: {' '.join(server_cmd)}")

        # Run the server process
        process = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        # Stream the output with improved exception handling
        try:
            # Process output and handle keyboard interrupts
            while True:
                try:
                    line = process.stdout.readline()
                    if not line:
                        break
                    click.echo(line.rstrip())
                except KeyboardInterrupt:
                    # Handle graceful termination on Ctrl+C
                    _echo_info("\nStopping server...")
                    process.terminate()
                    process.wait()
                    _echo_info("Server stopped.")
                    return

            # Wait for process to complete
            return_code = process.wait()
            if return_code != 0:
                _echo_error(f"Server exited with code {return_code}")
                sys.exit(return_code)
            _echo_info("Server stopped.")

        except Exception as e:
            # Ensure process is terminated on any exception
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                pass
            _echo_error(f"Error while running server: {str(e)}")
    except Exception as e:
        _echo_error(f"Error running server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
