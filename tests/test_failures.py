#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI tests for plugin failures."""

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
def test_a_broken_group_is_listed_as_unavailable(installed):
    installed(make_entry_point("broken"))

    result = runner.invoke(app, ["--help"])

    assert "unavailable" in result.stdout
    assert "ModuleNotFoundError" in result.stdout


def test_a_broken_group_reports_its_reason(installed):
    installed(make_entry_point("broken"))

    result = runner.invoke(app, ["broken"])

    assert result.exit_code == 2
    assert "installed but failed to load" in result.stderr
    assert "No module named 'nope'" in result.stderr


def test_a_broken_group_swallows_any_arguments(installed):
    installed(make_entry_point("broken"))

    result = runner.invoke(app, ["broken", "sub", "--unknown", "value"])

    assert result.exit_code == 2
    assert "installed but failed to load" in result.stderr


def test_a_broken_group_does_not_affect_its_siblings(installed):
    installed(
        make_entry_point("broken"),
        make_entry_point("demo", target=make_group("Demo group.")),
    )

    listing = runner.invoke(app, ["--help"])
    healthy = runner.invoke(app, ["demo", "run"])

    assert "Demo group." in listing.stdout
    assert healthy.exit_code == 0


def test_a_duplicated_name_names_both_providers(installed):
    installed(
        make_entry_point(
            "demo",
            dist_name="pkg-a",
            version="1.0",
            target=make_group(),
        ),
        make_entry_point(
            "demo",
            dist_name="pkg-b",
            version="2.0",
            target=make_group(),
        ),
    )

    result = runner.invoke(app, ["demo"])

    assert result.exit_code == 2
    assert "more than one package" in result.stderr
    assert "pkg-a 1.0" in result.stderr
    assert "pkg-b 2.0" in result.stderr


def test_a_target_that_is_not_a_typer_app_is_reported(installed):
    installed(make_entry_point("demo", target=object()))

    result = runner.invoke(app, ["demo"])

    assert result.exit_code == 2
    assert "expected typer.Typer" in result.stderr


def test_an_unknown_group_exits_two(installed):
    installed(make_entry_point("demo", target=make_group()))

    result = runner.invoke(app, ["nosuchgroup"])

    assert result.exit_code == 2


def test_a_group_exit_status_propagates(installed):
    import typer

    plugin = typer.Typer(help="Demo group.")

    @plugin.command()
    def fail():
        raise typer.Exit(code=7)

    @plugin.command()
    def other():
        pass

    installed(make_entry_point("demo", target=plugin))

    assert runner.invoke(app, ["demo", "fail"]).exit_code == 7
