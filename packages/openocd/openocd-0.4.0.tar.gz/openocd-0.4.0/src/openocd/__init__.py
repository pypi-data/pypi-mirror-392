# SPDX-License-Identifier: LGPL-2.1-or-later

"""
Python interface library for OpenOCD.
"""


from .openocd import (
    OpenOcd,
    Client,
    ResetType,
    BreakpointType,
    WatchpointType
)
