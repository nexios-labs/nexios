#!/usr/bin/env python
"""
Nexios CLI - URLs listing command.
"""

import sys
from pathlib import Path

import click

from nexios.cli.utils import _echo_info, _find_app_module, load_config_module

from ..utils import _echo_error, _load_app_from_path


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
        # Load config (optional)
        app, config = load_config_module(config_path)
        
        # If app_path wasn't provided in CLI args, check config
        if not app_path and "app_path" in config:
            app_path = config["app_path"]
            
        if not app_path:
            _echo_error(
                "App path must be specified with --app or in config file."
            )
            sys.exit(1)

        # Load app instance using app_path
        app = _load_app_from_path(app_path, config_path)
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