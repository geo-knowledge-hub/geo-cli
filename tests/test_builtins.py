#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI tests for built-in plugins."""

from typer.testing import CliRunner

from gkh_cli.cli import INSTALL_HINT, app
from tests.conftest import make_entry_point, make_group

#
# Constants
#
runner = CliRunner()


#
# Tests
#
def test_plugins_lists_each_group_with_its_provider(installed):
    installed(
        make_entry_point(
            name="demo",
            dist_name="demo-plugin",
            version="3.1",
            target=make_group(),
        ),
    )

    # invoke the plugins command
    result = runner.invoke(app, ["plugins"])

    # assert the command exited successfully
    assert result.exit_code == 0

    # assert the plugin is listed
    assert "demo" in result.stdout
    assert "demo-plugin 3.1" in result.stdout
    assert "demo_plugin.cli:app" in result.stdout


def test_plugins_says_what_to_install_when_there_is_nothing(installed):
    # present no entry points
    installed()

    # invoke the plugins command
    result = runner.invoke(app, ["plugins"])

    # assert the command exited successfully
    assert result.exit_code == 0

    # assert the hint is in the output
    assert INSTALL_HINT in result.stdout


def test_plugins_loads_no_group(installed):
    # present an entry point that does not point at a TyperGroup
    entry_points = installed(make_entry_point("demo", target=make_group()))

    # invoke the plugins command
    runner.invoke(app, ["plugins"])

    # assert the entry point was not loaded
    assert entry_points[0].loads == []


def test_a_group_cannot_shadow_a_builtin(installed):
    # present an entry point that shadows the builtin plugins command
    installed(make_entry_point("plugins", target=make_group("Impostor.")))

    result = runner.invoke(app, ["plugins"])

    # assert the command exited successfully
    assert result.exit_code == 0
    assert "plugins" in result.stdout
