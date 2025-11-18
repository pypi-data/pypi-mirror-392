# SPDX-License-Identifier: LGPL-2.1-or-later


"""
This module contains a Formatter for Tcl commands.
"""

from string import Formatter


class TclFormatter(Formatter):
    """
    A Formatter for convenient generation of Tcl commands.
    """
    def format_field(self, value: any, format_spec: str) -> str:
        if value is None:
            return ''

        if format_spec in ['x', 'X']:
            return '0x' + super().format_field(value, format_spec)

        return super().format_field(value, format_spec)
