# SPDX-License-Identifier: LGPL-2.1-or-later

"""
This module provides an OpenOCD Tcl interface class.
"""

import socket
from enum import Enum
from types import TracebackType
from typing_extensions import Self, deprecated
from openocd.tclformatter import TclFormatter


class ResetType(Enum):
    """Target reset type."""

    RUN = 'run'
    """Start target code execution after reset."""
    HALT = 'halt'
    """Halt the target after reset."""
    INIT = 'init'
    """Halt the target after reset and execute the ``reset-init`` script."""


class BreakpointType(Enum):
    """Breakpoint type."""

    SW = 'sw'
    """Software breakpoint."""
    HW = 'hw'
    """Hardware breakpoint."""


class WatchpointType(Enum):
    """Watchpoint type."""

    READ = 'r'
    """Read access watchpoint."""
    WRITE = 'w'
    """Write access watchpoint."""
    ACCESS = 'a'
    """Read / write access watchpoint."""


class Client:
    """
    An OpenOCD Tcl interface class.

    Parameters
    ----------
    host : str, optional
        Hostname of the OpenOCD server.
    port : int, optional
        Port of the OpenOCD Tcl interface.
    timeout : float, optional
        Connection and socket timeout in seconds or None for infinite timeout.
    """
    COMMAND_TOKEN = '\x1a'

    def __init__(
            self,
            host: str = 'localhost',
            port: int = 6666,
            timeout: int | None = None) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._buffer_size = 4096

        self._fmt = TclFormatter().format

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(
            self,
            _type: type[BaseException] | None,
            value: BaseException | None,
            traceback: TracebackType | None) -> None:
        try:
            self._exit()
        finally:
            self.close()

    def _exit(self) -> None:
        self.execute('exit')

    @property
    def host(self) -> str:
        """Hostname of the OpenOCD server."""
        return self._host

    @property
    def port(self) -> int:
        """Port number of the OpenOCD Tcl interface."""
        return self._port

    def connect(self) -> None:
        """Establish a connection to the OpenOCD server."""
        self._socket = socket.create_connection((self.host, self.port),
                                                timeout=self._timeout)

    def close(self) -> None:
        """Close the connection."""
        self._socket.close()

    def execute(self, command: str) -> str:
        """
        Execute an arbitrary OpenOCD command.

        Parameters
        ----------
        command : str
            Command string.

        Returns
        -------
        str
            Result of the executed command.
        """
        data = (command + OpenOcd.COMMAND_TOKEN).encode('utf-8')
        self._socket.send(data)

        try:
            result = self._recv()
        except socket.timeout:
            result = None

        return result

    def _recv(self) -> str:
        data = bytes()

        while True:
            tmp = self._socket.recv(self._buffer_size)
            data += tmp

            if bytes(OpenOcd.COMMAND_TOKEN, encoding='utf-8') in tmp:
                break

        data = data.decode('utf-8').strip()

        # Strip trailing command token.
        data = data[:-1]

        return data

    def reset(self, reset_type: ResetType | None = None) -> None:
        """
        Perform a target reset

        Parameters
        ----------
        reset_type : openocd.ResetType, optional
            Determines what should happen after the target reset. If not
            provided or ``None``, target code execution is started after reset.
        """
        if reset_type is not None:
            reset_type = reset_type.value

        self.execute(self._fmt('reset {:s}', reset_type))

    def resume(self, address: int | None = None) -> None:
        """
        Resume the target execution.

        Parameters
        ----------
        address : int, optional
            If provided, resume the target execution at `address` instead of
            the current code position.
        """
        self.execute(self._fmt('resume {:x}', address))

    def halt(self) -> None:
        """Halt the target execution."""
        self.execute('halt')

    def shutdown(self) -> None:
        """Shutdown the OpenOCD server."""
        self.execute('shutdown')

    def step(self, address: int | None = None) -> None:
        """
        Perform a single-step on the target.

        Parameters
        ----------
        address : int, optional
            If provided, perform the single-step at `address` instead of the
            current code position.
        """
        self.execute(self._fmt('step {:x}', address))

    def targets(self) -> list[str]:
        """
        Get the names of all available targets.

        Returns
        -------
        list of str
            Names of all available targets.
        """
        return self.execute('target names').splitlines()

    def target_types(self) -> list[str]:
        """
        Get all supported target types.

        Returns
        -------
        list of str
            Types of all supported targets.
        """
        return self.execute('target types').splitlines()

    def current_target(self) -> str:
        """
        Get the name of the current target.

        Returns
        -------
        str
            Name of the current target.
        """
        return self.execute('target current')

    def read_memory(
            self,
            address: int,
            count: int,
            width: int,
            phys: bool = False) -> list[int]:
        """
        Read from target memory.

        Parameters
        ----------
        address : int
            Target memory address.
        count : int
            Number of words to read.
        width : int
            Memory access bit size.
        phys : bool, optional
            If this is set to True, treat the memory address as physical
            instead of virtual.

        Returns
        -------
        list of int
            List of words read from target memory.
        """

        if phys:
            phys = 'phys'
        else:
            phys = None

        response = self.execute(self._fmt('read_memory {:x} {:d} {:d} {:s}',
                                address, width, count, phys))
        return [int(x, 0) for x in response.split(' ')]

    def write_memory(
            self,
            address: int,
            data: list[int],
            width: int,
            phys: bool = False) -> None:
        """
        Write to target memory.

        Parameters
        ----------
        address : int
            Target memory address.
        data : list of int
            List of words to write to the target memory.
        width : int
            Memory access bit size.
        phys : bool, optional
            If this is set to True, treat the memory address as physical
            instead of virtual.
        """

        if phys:
            phys = 'phys'
        else:
            phys = None

        tcl_list = '{' + ' '.join([hex(x) for x in data]) + '}'
        response = self.execute(self._fmt('write_memory {:x} {:d} {:s} {:s}',
                                address, width, tcl_list, phys))

        if response != '':
            raise Exception(response)

    def read_registers(
            self,
            registers: list[str],
            force: bool = False) -> dict[str, int]:
        """
        Read target registers.

        Parameters
        ----------
        registers : list of str
            Register names.
        force : bool
            If set to True, register values are read directly from the target,
            bypassing any caching.

        Returns
        -------
        dict
            Dictionary containing the read register names and corresponding
            values.
        """

        if force:
            force = '-force'
        else:
            force = None

        tcl_list = '{' + ' '.join(registers) + '}'
        response = self.execute(self._fmt('get_reg {:s} {:s}',
                                force, tcl_list)).split(' ')

        registers = response[::2]
        values = [int(x, 0) for x in response[1::2]]

        return dict(zip(registers, values))

    def write_registers(self, values: dict[str, int]) -> None:
        """
        Write target registers.

        Parameters
        ----------
        values : dict
            Dictionary with register names and the corresponding values.
        """

        tcl_dict = ' '.join([self._fmt('{:s} {:x}', register, value) for
                            (register, value) in values.items()])
        response = self.execute(self._fmt('set_reg {{{:s}}}', tcl_dict))

        if response != '':
            raise Exception(response)

    def add_breakpoint(
            self,
            address: int,
            length: int,
            type_: BreakpointType) -> None:
        """
        Add a breakpoint.

        Parameters
        ----------
        address : int
            Breakpoint address.
        length : int
            Breakpoint length.
        type_ : BreakpointType
            Breakpoint type.
        """

        if type_ == BreakpointType.SW:
            type_ = None
        else:
            type_ = type_.value

        self.execute(self._fmt('bp {:x} {:d} {:s}',
                     address, length, type_))

    def remove_breakpoint(self, address: int) -> None:
        """
        Remove a breakpoint.

        Parameters
        ----------
        address : int
            Breakpoint address.
        """
        self.execute(self._fmt('rbp {:x}', address))

    def remove_all_breakpoints(self) -> None:
        """
        Remove all breakpoints.
        """
        self.execute('rbp all')

    def add_watchpoint(
            self,
            address: int,
            length: int,
            type_: WatchpointType = WatchpointType.ACCESS,
            value: int | None = None,
            mask: int | None = None) -> None:
        """
        Add a watchpoint.

        Parameters
        ----------
        address : int
            Watchpoint address.
        length : int
            Watchpoint length.
        type_ : WatchpointType, optional
            Watchpoint type.
        value : int, optional
            Value used to determine whether the watchpoint should be triggered.
        mask : int, optional
            Bit mask for specifying bits of `value` that are to be ignored for
            the comparison.
        """

        self.execute(self._fmt('wp {:x} {:d} {:s} {:x} {:x}',
                     address, length, type_.value, value, mask))

    def remove_watchpoint(self, address: int) -> None:
        """
        Remove a watchpoint.

        Parameters
        ----------
        address : int
            Watchpoint address.
        """
        self.execute(self._fmt('rwp {:x}', address))

    def remove_all_watchpoints(self) -> None:
        """
        Remove all watchpoints.
        """
        self.execute('rwp all')

    def add_script_search_dir(self, directory: str) -> None:
        """
        Add a directory to the search path for scripts.

        Parameters
        ----------
        directory : str
            Directory path.
        """
        self.execute(self._fmt('add_script_search_dir {{{:s}}}', directory))


@deprecated(
    'The "OpenOcd" class has been deprecated in 0.4.0, use "Client" instead')
class OpenOcd(Client):
    pass
