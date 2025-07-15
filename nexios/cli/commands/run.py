#!/usr/bin/env python
"""
Nexios CLI - Run server command.
"""

import os
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Optional

import click

from nexios.cli.utils import load_config_module

from ..utils import (
    _echo_error,
    _echo_info,
    _find_app_module,
    _validate_app_path,
    _validate_host,
    _validate_port,
    _validate_server,
)


@click.command()
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
def run(
    host: str,
    port: int,
    reload: bool,
    app_path: Optional[str],
    server: str,
    workers: int,
):
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

        # Load config
        _, config = load_config_module(None)

        # Merge CLI args with config (CLI args take precedence)
        options = dict(config)
        for k, v in locals().items():
            if v is not None and k != "config" and k != "app":
                options[k] = v

        # Use app_path from CLI or config, or auto-detect
        app_path = options.get("app_path")
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
        options["app_path"] = app_path

        # Support custom_command as either a string or a list (array)
        if "custom_command" in options and options["custom_command"]:
            custom_cmd = options["custom_command"]
            if isinstance(custom_cmd, (list, tuple)):
                subprocess.run(custom_cmd, check=True)
            else:
                # Assume string, run in shell
                os.system(custom_cmd)
            return

        # Use gunicorn if server is gunicorn
        if options.get("server") == "gunicorn":
            workers = options.get("workers", 4)
            host = options.get("host", "0.0.0.0")
            port = options.get("port", 8000)
            app_path = options.get("app_path", "nexios.config:app")
            cmd = f"gunicorn -w {workers} -b {host}:{port} {app_path}"
            os.system(cmd)
            return

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
        traceback.print_exc()
        _echo_error(f"Error running server: {str(e)}")
        sys.exit(1)
