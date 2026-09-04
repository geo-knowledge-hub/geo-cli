#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI tests for plugin discovery."""

from typer.testing import CliRunner

from gkh_cli.cli import app
from tests.conftest import make_entry_point, make_group

#
# Constants
#
runner = CliRunner()


#
# Tests
#
def test_a_group_is_listed_with_its_help(installed):
    installed(make_entry_point("demo", target=make_group("Demo group.")))

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "demo" in result.stdout
    assert "Demo group." in result.stdout


def test_a_group_runs(installed):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    # invoke the plugin with the run command
    result = runner.invoke(app, ["demo", "run"])

    assert result.exit_code == 0


def test_groups_are_listed_in_order(installed):
    # install plugins
    installed(
        make_entry_point("zulu", target=make_group()),
        make_entry_point("alpha", target=make_group()),
    )

    result = runner.invoke(app, ["--help"])
    commands = result.stdout[result.stdout.index("Commands") :]

    assert commands.index("alpha") < commands.index("zulu")


def test_a_single_command_group_keeps_its_subcommand(installed):
    installed(
        make_entry_point(
            "demo",
            target=make_group("Demo group.", commands=("run",)),
        ),
    )

    result = runner.invoke(app, ["demo", "run"])

    assert result.exit_code == 0


def test_a_single_command_group_keeps_its_help(installed):
    installed(
        make_entry_point(
            "demo",
            target=make_group("Demo group.", commands=("run",)),
        ),
    )

    result = runner.invoke(app, ["--help"])

    assert "Demo group." in result.stdout


def test_help_loads_every_group(installed):
    entry_points = installed(
        make_entry_point("demo", target=make_group()),
        make_entry_point("other", dist_name="other-plugin", target=make_group()),
    )

    runner.invoke(app, ["--help"])

    assert [ep.loads for ep in entry_points] == [["demo"], ["other"]]


def test_invoking_one_group_does_not_load_the_others(installed):
    entry_points = installed(
        make_entry_point("demo", target=make_group()),
        make_entry_point("other", dist_name="other-plugin", target=make_group()),
    )

    runner.invoke(app, ["demo", "run"])

    assert [ep.loads for ep in entry_points] == [["demo"], []]


def test_version_loads_no_group(installed):
    entry_points = installed(make_entry_point("demo", target=make_group()))

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert entry_points[0].loads == []


def test_version_names_every_group(installed):
    installed(
        make_entry_point(
            "demo",
            dist_name="demo-plugin",
            version="2.5",
            target=make_group(),
        ),
    )

    result = runner.invoke(app, ["--version"])

    assert "demo: demo-plugin 2.5" in result.stdout
