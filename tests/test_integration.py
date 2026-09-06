#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI end-to-end tests."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

#
# Constants
#
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(shutil.which("uv") is None, reason="needs uv"),
]

#
# Constants
#
ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"


#
# Fixtures
#
@pytest.fixture(scope="module")
def gkh(tmp_path_factory):
    """Install gkh-cli and the fixture plugins into a throwaway environment."""
    venv = tmp_path_factory.mktemp("venv") / "env"

    # create a virtual environment
    subprocess.run(["uv", "venv", "--python", sys.executable, str(venv)], check=True)

    # install the dependencies
    python = venv / "bin" / "python"
    targets = [str(ROOT), str(FIXTURES / "demo_plugin"), str(FIXTURES / "broken_plugin")]

    # install the dependencies
    subprocess.run(["uv", "pip", "install", "--python", str(python), *targets], check=True)

    # return the path to the gkh CLI
    return venv / "bin" / "gkh"


def run(gkh, *args):
    """Run the gkh CLI with the given arguments."""
    return subprocess.run([str(gkh), *args], capture_output=True, text=True)


def test_the_console_script_is_installed(gkh):
    """Test that the console script is installed."""
    result = run(gkh, "--version")

    assert result.returncode == 0
    assert result.stdout.startswith("gkh-cli ")


def test_version_names_the_installed_plugins(gkh):
    """Test that the version command names the installed plugins."""
    result = run(gkh, "--version")

    assert "demo: demo-plugin 1.2.3" in result.stdout
    assert "broken: broken-plugin 0.0.1" in result.stdout


def test_a_real_plugin_is_discovered_and_runs(gkh):
    """Test that a real plugin is discovered and runs."""
    result = run(gkh, "demo", "show")

    assert result.returncode == 0
    assert "url=None" in result.stdout


def test_the_shared_context_reaches_a_real_plugin(gkh):
    """Test that the shared context reaches a real plugin."""
    result = run(gkh, "--url", "https://example.org", "--output", "json", "demo", "show")

    assert "url=https://example.org" in result.stdout
    assert "output=json" in result.stdout


def test_a_real_broken_plugin_is_contained(gkh):
    """Test that a real broken plugin is contained."""
    listing = run(gkh, "--help")
    invoked = run(gkh, "broken", "sub", "--unknown")
    healthy = run(gkh, "demo", "show")

    assert "unavailable" in listing.stdout
    assert "Demo group." in listing.stdout

    assert invoked.returncode == 2
    assert "installed but failed to load" in invoked.stderr
    assert "Traceback" not in invoked.stderr

    assert healthy.returncode == 0


def test_a_real_plugin_exit_status_propagates(gkh):
    """Test that a real plugin exit status propagates."""
    assert run(gkh, "demo", "fail").returncode == 7


def test_shell_completion_lists_the_groups(gkh):
    """Test that shell completion lists the groups."""
    result = subprocess.run(
        [str(gkh)],
        capture_output=True,
        text=True,
        env={
            "PATH": "/usr/bin:/bin",
            "_GKH_COMPLETE": "complete_bash",
            "COMP_WORDS": "gkh ",
            "COMP_CWORD": "1",
        },
    )

    assert "demo" in result.stdout
