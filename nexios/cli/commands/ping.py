#!/usr/bin/env python
"""
Nexios CLI - Ping route command.
"""

import asyncio
import sys
from pathlib import Path

import click

from nexios.testing.client import Client
from ..utils import _echo_error, _echo_success, _echo_warning, _load_app_from_path
from nexios.cli.utils import load_config_module,_echo_info


@click.command()
@click.argument("route_path")
@click.option("--app", "app_path", help="App module path in format 'module:app_variable'. Auto-detected if not specified.")
@click.option("--config", "config_path", help="Path to a Python config file that sets up the app instance.")
@click.option("--method", default="GET", help="HTTP method to use (default: GET)")
def ping(route_path: str, app_path: str = None, config_path: str = None, method: str = "GET"):
    """
    Ping a route in the Nexios app to check if it exists (returns status code).
    """
    async def _ping():
        try:
            app, config = load_config_module(None)
            options = dict(config)
            for k, v in locals().items():
                if v is not None and k != "config" and k != "app":
                    options[k] = v
            app_path = options.get("app_path")
            if not app_path:
                project_dir = Path.cwd()
                app_path = _load_app_from_path(app_path, config_path)
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

            async with Client(app) as client:
                resp = await client.request(method.upper(), route_path)
                click.echo(f"{route_path} [{method.upper()}] -> {resp.status_code}")
                if resp.status_code == 200:
                    _echo_success("Route exists and is reachable.")
                elif resp.status_code == 404:
                    _echo_error("Route not found (404).")
                else:
                    _echo_warning(f"Route returned status: {resp.status_code}")
        except Exception as e:
            _echo_error(f"Error pinging route: {e}")
            sys.exit(1)
    asyncio.run(_ping()) 