#!/usr/bin/env python
"""
Nexios CLI - Main entry point for all CLI commands.
"""

import click

from nexios.__main__ import __version__
from nexios.cli.commands import new, ping, run, shell, urls

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "auto_envvar_prefix": "NEXIOS",
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="Nexios")
def cli():
    """
    Nexios CLI - Command line tools for the Nexios framework.
    """
    pass


# Import and register all CLI commands

# Register commands
cli.add_command(new)
cli.add_command(run)
cli.add_command(urls)
cli.add_command(ping)
cli.add_command(shell)
