#!/usr/bin/env python
"""
Nexios CLI - URLs listing command.
"""

import sys
from pathlib import Path

import click

from nexios.cli.utils import load_config_module

from ..utils import _echo_error, _echo_info, _find_app_module


@click.command()
@click.option(
    "--app",
    "app_path",
    # required=True,
    help="App module path in format 'module:app_variable'.",
)
@click.option(
    "--config",
    "config_path",
    help="Path to a Python config file that sets up the app instance.",
)
def urls(app_path: str = None, config_path: str = None):
    """
    List all registered URLs in the Nexios application.
    """
    try:
        project_dir = Path.cwd()
        # Load config
        app, config = load_config_module(None)
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

        # Attach config to app

        if app is None:
            _echo_error(
                "Could not load the app instance. Please check your app_path or config."
            )
            sys.exit(1)

        routes = app.get_all_routes()
        click.echo(f"{'METHODS':<15} {'PATH':<40} {'NAME':<20} {'SUMMARY'}")
        click.echo("-" * 90)
        for route in routes:
            methods = (
                ",".join(route.methods) if getattr(route, "methods", None) else "-"
            )
            path = getattr(route, "raw_path", getattr(route, "path", "-")) or "-"
            name = getattr(route, "name", None) or "-"
            summary = getattr(route, "summary", None) or ""
            click.echo(f"{methods:<15} {path:<40} {name:<20} {summary}")
    except Exception as e:
        _echo_error(f"Error listing URLs: {e}")
        sys.exit(1)
