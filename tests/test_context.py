#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI tests for context."""

import typer
from typer.testing import CliRunner

from gkh_cli import Context, Output, context_of
from gkh_cli.cli import app
from tests.conftest import make_entry_point, make_group

#
# Constants
#
runner = CliRunner()


#
# Tests
#
def run(*args):
    return runner.invoke(app, [*args, "demo", "run"])


def test_flags_reach_the_group(installed):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    # invoke the plugin with flags
    result = run("--url", "https://example.org", "--token", "secret")

    # assert
    assert "url='https://example.org'" in result.stdout
    assert "token='secret'" in result.stdout


def test_environment_reaches_the_group(installed, monkeypatch):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    # set the environment variables
    monkeypatch.setenv("GKH_BASE_URL", "https://from-env.org")
    monkeypatch.setenv("GKH_API_TOKEN", "env-secret")

    # invoke the plugin
    result = run()

    # assert
    assert "url='https://from-env.org'" in result.stdout
    assert "token='env-secret'" in result.stdout


def test_a_flag_wins_over_the_environment(installed, monkeypatch):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    # set the environment variables
    monkeypatch.setenv("GKH_BASE_URL", "https://from-env.org")

    # invoke the plugin with flags
    result = run("--url", "https://from-flag.org")

    # assert
    assert "url='https://from-flag.org'" in result.stdout


def test_tls_verification_is_on_by_default(installed):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    # invoke the plugin
    assert "verify_tls=True" in run().stdout


def test_tls_verification_can_be_turned_off(installed):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    # invoke the plugin with the flag
    assert "verify_tls=False" in run("--no-verify-tls").stdout


def test_output_defaults_to_text(installed):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    assert "Output.text" in run().stdout


def test_output_accepts_json(installed):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    assert "Output.json" in run("--output", "json").stdout


def test_output_rejects_anything_else(installed):
    # install a plugin that prints the context
    installed(make_entry_point("demo", target=make_group()))

    # invoke the plugin with an invalid output format
    result = run("--output", "yaml")

    assert result.exit_code == 2
    assert "is not one of 'text', 'json'" in result.stderr


def test_context_of_defaults_outside_the_umbrella():
    standalone = typer.Typer()
    seen = []

    @standalone.command()
    def check(ctx: typer.Context):
        seen.append(context_of(ctx))

    result = CliRunner().invoke(standalone, [])

    assert result.exit_code == 0
    assert seen == [Context(url=None, token=None, verify_tls=True, output=Output.text)]
