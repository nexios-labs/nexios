#!/usr/bin/env python
"""
Nexios CLI - Interactive shell command.
"""

import sys
from typing import Optional

import click

from ..utils import _echo_error, _echo_info, _load_app_from_path


@click.command()
@click.option("--app", "app_path", help="App module path in format 'module:app_variable'. Auto-detected if not specified.")
@click.option("--config", "config_path", help="Path to a Python config file that sets up the app instance.")
@click.option("--ipython", is_flag=True, help="Force use of IPython shell (default: auto-detect)")
def shell(app_path: str = None, config_path: str = None, ipython: bool = False):
    """
    Start an interactive shell with the Nexios app context loaded.
    
    This provides an interactive environment where you can:
    - Access your app instance as 'app'
    - Test routes and handlers
    - Inspect app configuration
    - Debug and experiment with your application
    """
    try:
        # Load the app
        app = _load_app_from_path(app_path, config_path)
        _echo_info(f"Loaded app: {app}")
        
        # Prepare the shell environment
        shell_vars = {
            'app': app,
            'NexiosApp': type(app),
        }
        
        # Try to import common modules that might be useful
        try:
            from nexios.testing.client import Client
            shell_vars['Client'] = Client
            _echo_info("Test client available as 'Client'")
        except ImportError:
            pass
            
        try:
            from nexios.http.request import Request
            from nexios.http.response import Response
            shell_vars['Request'] = Request
            shell_vars['Response'] = Response
            _echo_info("Request/Response classes available")
        except ImportError:
            pass
            
        try:
            from nexios.config import MakeConfig
            shell_vars['MakeConfig'] = MakeConfig
            _echo_info("MakeConfig available for configuration")
        except ImportError:
            pass
        
        # Try to start IPython if available
        if ipython or not _try_start_regular_shell(shell_vars):
            _try_start_ipython_shell(shell_vars)
            
    except Exception as e:
        _echo_error(f"Error starting shell: {e}")
        sys.exit(1)


def _try_start_ipython_shell(shell_vars: dict) -> bool:
    """Try to start IPython shell."""
    try:
        import IPython
        from IPython.terminal.embed import InteractiveShellEmbed
        
        _echo_info("Starting IPython shell...")
        _echo_info("Available variables: app, Client, Request, Response, MakeConfig")
        _echo_info("Type 'exit' or press Ctrl+D to exit")
        
        # Create IPython shell with custom banner
        banner = """
Nexios Interactive Shell
=======================
Available variables:
- app: Your Nexios application instance
- Client: Test client for making requests
- Request: Request class
- Response: Response class  
- MakeConfig: Configuration class

Examples:
  # Test a route
  async with Client(app) as client:
      resp = await client.get('/')
      print(resp.status_code)
      
  # Inspect app
  print(app.get_all_routes())
  print(app.config)
"""
        
        shell = InteractiveShellEmbed(banner1=banner)
        shell(local_ns=shell_vars)
        return True
        
    except ImportError:
        _echo_error("IPython not available. Install with: pip install ipython")
        return False


def _try_start_regular_shell(shell_vars: dict) -> bool:
    """Try to start regular Python shell."""
    try:
        import code
        
        _echo_info("Starting Python shell...")
        _echo_info("Available variables: app, Client, Request, Response, MakeConfig")
        _echo_info("Type 'exit()' or press Ctrl+D to exit")
        
        # Create interactive console
        console = code.InteractiveConsole(shell_vars)
        console.interact(banner="Nexios Interactive Shell\nAvailable: app, Client, Request, Response, MakeConfig")
        return True
        
    except Exception:
        return False 