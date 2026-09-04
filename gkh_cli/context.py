#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI context."""

import enum
from dataclasses import dataclass

import typer


#
# Classes
#
class Output(enum.StrEnum):
    """GEO Knowledge Hub CLI output format."""

    text = "text"
    json = "json"


@dataclass(frozen=True)
class Context:
    """GEO Knowledge Hub CLI context."""

    url: str | None = None
    token: str | None = None
    verify_tls: bool = True
    output: Output = Output.text


#
# Auxiliary functions
#
def context_of(ctx: typer.Context) -> Context:
    """Get the GEO Knowledge Hub CLI context from the Typer context."""

    if isinstance(ctx.obj, Context):
        return ctx.obj

    return Context()
