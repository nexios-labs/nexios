#!/usr/bin/env python
"""
Nexios CLI - URLs listing command.
"""

import sys
from pathlib import Path

import click

from ..utils import _echo_error, _load_app_from_path
from nexios.cli.utils import load_config_module,_find_app_module,_echo_info


@click.command()
@click.option("--app", "app_path", help="App module path in format 'module:app_variable'. Auto-detected if not specified.")
@click.option("--config", "config_path", help="Path to a Python config file that sets up the app instance.")
def urls(app_path: str = None, config_path: str = None):
    """
    List all registered URLs in the Nexios application.
    """
    try:
        app, config = load_config_module(None)
        options = dict(config)
        for k, v in locals().items():
            if v is not None and k != "config" and k != "app":
                options[k] = v
        app_path = options.get("app_path")
        if not app_path:
            project_dir = Path.cwd()
            app_path = _find_app_module(project_dir)
            if not app_path:
                _echo_error("Could not automatically find the app module. Please specify it with --app option. ...")
                sys.exit(1)
            _echo_info(f"Auto-detected app module: {app_path}")
        options["app_path"] = app_path

        # Load app instance if not present, using app_path
        if app is None and app_path:
            app = _load_app_from_path(app_path, config_path)
        if app is None:
            _echo_error("Could not load the app instance. Please check your app_path or config.")
            sys.exit(1)

        routes = app.get_all_routes()
        click.echo(f"{'METHODS':<15} {'PATH':<40} {'NAME':<20} {'SUMMARY'}")
        click.echo("-" * 90)
        for route in routes:
            methods = ",".join(route.methods) if getattr(route, 'methods', None) else "-"
            path = getattr(route, 'raw_path', getattr(route, 'path', '-')) or "-"
            name = getattr(route, 'name', None) or "-"
            summary = getattr(route, 'summary', None) or ""
            click.echo(f"{methods:<15} {path:<40} {name:<20} {summary}")
    except Exception as e:
        _echo_error(f"Error listing URLs: {e}")
        sys.exit(1) 