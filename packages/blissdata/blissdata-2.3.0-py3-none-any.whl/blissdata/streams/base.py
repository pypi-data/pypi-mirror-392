# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
from . import (
    BaseStream,
    BaseView,
    Cursor,
    CursorGroup,
    EventRange,
    StreamDefinition,
)
from .default import (
    View,
    Stream,
    BrokenStream,
    BrokenPluginStream,
    MissingPluginStream,
)

from blissdata.deprecation import warn_deprecated

warn_deprecated(__name__, "blissdata.streams' and 'blissdata.streams.default", "3")

__all__ = [
    "BaseStream",
    "BaseView",
    "Cursor",
    "CursorGroup",
    "EventRange",
    "StreamDefinition",
    "View",
    "Stream",
    "BrokenStream",
    "BrokenPluginStream",
    "MissingPluginStream",
]
