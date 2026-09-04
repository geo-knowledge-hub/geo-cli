#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI main module."""

from typing import Annotated

import typer
from typer.core import TyperCommand, TyperGroup

from gkh_cli import plugins as plugins_utils
from gkh_cli.context import Context, Output
from gkh_cli.version import __version__

#
# Constants
#
INSTALL_HINT = (
    "No command groups are installed. Install one, for example: uv tool install gkh-deploy"
)


#
# Auxiliary functions
#
def _show_version(value: bool) -> None:
    """Print the version of GEO Knowledge Hub CLI and dependencies."""
    if not value:
        return

    typer.echo(f"gkh-cli {__version__}")

    for ep in plugins_utils.discover():
        typer.echo(f"  {ep.name}: {ep.dist.name} {ep.dist.version}")

    raise typer.Exit()


#
# Classes
#
class PluginGroup(TyperGroup):
    """GEO Knowledge Hub CLI plugin group."""

    def list_commands(self, ctx: typer.Context) -> list[str]:
        """List available plugins."""
        contributed = {ep.name for ep in plugins_utils.discover()}

        return sorted(set(super().list_commands(ctx)) | contributed)

    def get_command(self, ctx: typer.Context, name: str) -> TyperGroup | TyperCommand | None:
        """Get plugin by name."""
        builtin = super().get_command(ctx, name)

        if builtin is not None:
            return builtin

        return plugins_utils.resolve(name)


#
# Main CLI application
#
app = typer.Typer(cls=PluginGroup, no_args_is_help=True)


#
# CLI main options
#
Url = Annotated[
    str | None,
    typer.Option(
        "--url", envvar="GKH_BASE_URL", help="Base URL of the GEO Knowledge Hub instance."
    ),
]

Token = Annotated[
    str | None,
    typer.Option("--token", envvar="GKH_API_TOKEN", help="Personal access token."),
]

NoVerifyTls = Annotated[
    bool,
    typer.Option(
        "--no-verify-tls",
        envvar="GKH_NO_VERIFY_TLS",
        help="Skip TLS verification, for instances with self-signed certificates.",
    ),
]

OutputFormat = Annotated[
    Output,
    typer.Option("--output", help="How plugins should present results."),
]

Version = Annotated[
    bool,
    typer.Option(
        "--version",
        callback=_show_version,
        is_eager=True,
        help="Show the version of GEO Knowledge Hub CLI and dependencies.",
    ),
]


@app.callback()
def main(
    ctx: typer.Context,
    url: Url = None,
    token: Token = None,
    no_verify_tls: NoVerifyTls = False,
    output: OutputFormat = Output.text,
    version: Version = False,
) -> None:
    """GEO Knowledge Hub CLI.

    Plugins come from separately installed packages. Run `gkh plugins` to see which
    ones are available.
    """
    ctx.obj = Context(
        url=url,
        token=token,
        verify_tls=not no_verify_tls,
        output=output,
    )


@app.command()
def plugins() -> None:
    """List available plugins."""
    found = plugins_utils.discover()

    if not found:
        typer.echo(INSTALL_HINT)

        return

    for ep in found:
        typer.echo(f"{ep.name}\t{ep.dist.name} {ep.dist.version}\t{ep.value}")
