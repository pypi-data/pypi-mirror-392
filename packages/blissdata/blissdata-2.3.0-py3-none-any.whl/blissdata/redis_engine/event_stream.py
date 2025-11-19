# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
from blissdata.deprecation import warn_deprecated

warn_deprecated(__name__, "blissdata.streams.event_stream", "3")

from blissdata.streams.event_stream import EventStream  # noqa F401, E402
