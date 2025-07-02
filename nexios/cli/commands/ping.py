#!/usr/bin/env python
"""
Nexios CLI - Ping route command.
"""

import asyncio
import sys
from typing import Optional

import click

from nexios.testing.client import Client
from ..utils import _echo_error, _echo_success, _echo_warning, _load_app_from_path


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
            app = _load_app_from_path(app_path, config_path)
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