# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
from .deprecation import warn_deprecated

warn_deprecated(__name__, "blissdata", "3")

from . import Scan  # noqa: F401, E402
