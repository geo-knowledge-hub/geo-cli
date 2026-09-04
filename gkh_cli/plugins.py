#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI plugins."""

from importlib.metadata import EntryPoint, entry_points

import typer
from typer.core import TyperCommand, TyperGroup
from typer.main import get_command, get_group

#
# Constants
#
GROUP = "gkh.commands"


#
# Auxiliary functions
#
def discover() -> list[EntryPoint]:
    """Discover all plugins available in the system."""
    found = entry_points(group=GROUP)

    # return plugins installed
    return sorted(found, key=lambda ep: (ep.name, ep.dist.name))


def load(ep: EntryPoint) -> TyperGroup:
    """Turn one entry point into a plugin.

    Args:
        ep: Entry point to load.

    Returns:
        Plugin.

    Raises:
        Exception: whatever importing the plugin raised.
        TypeError: when the entry point does not point at a TyperGroup.
    """
    target = ep.load()

    if not isinstance(target, typer.Typer):
        raise TypeError(f"{ep.value} is {type(target).__name__}, expected typer.Typer")

    return get_group(target)


def unavailable(name: str, reason: str) -> TyperCommand:
    """Build a stand-in for a plugin that is installed but cannot be loaded.

    Args:
        name (str): Name of the plugin.

        reason (str): Reason why the plugin cannot be loaded.

    Returns:
        TyperCommand: stand-in plugin.
    """
    stub = typer.Typer()

    @stub.command(
        help=f"(unavailable: {reason})",
        context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    )
    def _report() -> None:
        typer.echo(f"gkh: command group '{name}' is installed but failed to load.", err=True)
        typer.echo(f"gkh: {reason}", err=True)

        raise typer.Exit(code=2)

    # get the command from the stub
    command = get_command(stub)
    command.name = name

    # set the name of the command
    return command


def resolve(name: str) -> TyperGroup | TyperCommand | None:
    """Look up one plugin by name.

    Args:
        name (str): Name of the plugin.

    Returns:
        TyperGroup | TyperCommand | None: plugin or None if the plugin is not found.
    """
    matches = [ep for ep in discover() if ep.name == name]

    # no matches, return None
    if not matches:
        return None

    # more than one match, return a stand-in
    if len(matches) > 1:
        providers = ", ".join(f"{ep.dist.name} {ep.dist.version}" for ep in matches)

        return unavailable(name, f"provided by more than one package: {providers}")

    # load the plugin
    try:
        command = load(matches[0])
    except Exception as exc:
        return unavailable(name, f"{type(exc).__name__}: {exc}")

    # set the name of the plugin
    command.name = name

    # return the plugin
    return command
