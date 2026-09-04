#
# This file is part of GEO Knowledge Hub CLI.
# Copyright (C) 2026 GEO Knowledge Hub contributors.
#
# GEO Knowledge Hub CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""GEO Knowledge Hub CLI version."""

from importlib.metadata import PackageNotFoundError, version

#
# Constants
#
try:
    __version__ = version("gkh-cli")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
