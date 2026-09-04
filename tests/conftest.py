#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI tests fixtures."""

from dataclasses import dataclass, field

import pytest
import typer

from gkh_cli import plugins


@dataclass
class FakeDist:
    """Fake distribution."""

    name: str
    version: str


@dataclass
class FakeEntryPoint:
    """Fake entry point."""

    name: str
    value: str
    dist: FakeDist
    target: object = None
    loads: list = field(default_factory=list)

    def load(self):
        """Load the entry point."""
        self.loads.append(self.name)

        if self.target is None:
            raise ModuleNotFoundError("No module named 'nope'")

        return self.target


def make_group(help_text="A group.", commands=("run", "other")):
    """Build a Typer plugin that prints the shared context it received."""
    app = typer.Typer(help=help_text)

    for name in commands:

        @app.command(name)
        def _command(ctx: typer.Context):
            typer.echo(f"obj={ctx.obj}")

    return app


def make_entry_point(name, dist_name="demo-plugin", version="1.0", **kwargs):
    """Build a fake entry point."""

    return FakeEntryPoint(
        name=name,
        value=f"{dist_name.replace('-', '_')}.cli:app",
        dist=FakeDist(dist_name, version),
        **kwargs,
    )


@pytest.fixture
def installed(monkeypatch):
    """Present the given entry points as the installed plugins."""

    def install(*entry_points):
        monkeypatch.setattr(plugins, "entry_points", lambda group: list(entry_points))

        return entry_points

    return install
