#!/usr/bin/env python
"""
Nexios CLI - Ping route command.
"""

import asyncio
import sys
from typing import Optional

import click

from nexios.cli.utils import (
    _echo_error,
    _echo_info,
    _echo_success,
    _echo_warning,
    _load_app_from_path,
    load_config_module,
)

try:
    from nexios.testing.client import Client
except ImportError:
    Client = None


@click.command()
@click.argument("route_path")
@click.option(
    "--app",
    "cli_app_path",
    help="App module path in format 'module:app_variable' (e.g., 'myapp.main:app').",
)
@click.option(
    "--config",
    "config_path",
    help="Path to a Python config file that sets up the app instance.",
)
@click.option("--method", default="GET", help="HTTP method to use (default: GET)")
def ping(
    route_path: str,
    cli_app_path: Optional[str] = None,
    config_path: Optional[str] = None,
    method: str = "GET",
):
    """
    Ping a route in the Nexios app to check if it exists (returns status code).

    Examples:
      nexios ping /about --app sandbox:app
      nexios ping /api/users --config config.py
    """

    async def _ping():
        try:
            # Load config (returns None, {} if file doesn't exist)
            app, config = load_config_module(config_path)

            # Resolve app path (CLI argument takes precedence over config)
            resolved_app_path = cli_app_path or config.get("app_path")
            if not resolved_app_path:
                _echo_error(
                    "App path must be specified with --app or in config file.\n"
                    "Format: 'module:app_variable' (e.g., 'sandbox:app')"
                )
                sys.exit(1)

            _echo_info(f"Using app: {resolved_app_path}")

            # Load app instance
            app = _load_app_from_path(resolved_app_path, config_path)
            if app is None:
                _echo_error("Could not load app instance from: {resolved_app_path}")
                sys.exit(1)
            if not Client:
                _echo_error("httpx is not installed. Install with: pip install httpx")
                sys.exit(1)
                return
            async with Client(app) as client:
                resp = await client.request(method.upper(), route_path)
                click.echo(f"{route_path} [{method.upper()}] -> {resp.status_code}")

                if resp.status_code == 200:
                    _echo_success("Route exists and is reachable")
                elif resp.status_code == 404:
                    _echo_error("Route not found (404)")
                else:
                    _echo_warning(f"Unexpected status: {resp.status_code}")

        except Exception as e:
            _echo_error(f"Error pinging route: {str(e)}")
            sys.exit(1)

    asyncio.run(_ping())
