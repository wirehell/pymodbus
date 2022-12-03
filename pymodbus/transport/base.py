"""Base for all transport types.

:meta private:
"""
from __future__ import annotations

from abc import abstractmethod
from typing import Any, List

from pymodbus.framer import ModbusFramer
from pymodbus.logging import Log


class BaseTransport:
    """Base class for transport types.

    BaseTransport contains functions common to all transport types and client/server.

    This class is not available in the pymodbus API, and should not be referenced in Applications.

    Properties:
        close_comm_on_error: bool = False
        - If true the comm port/socket is closed when an error occurs
        connected: bool = False
        - True if the transport layer is connected (READONLY)
        reconnect_delay: int = 0
        - delay in milliseconds for first reconnect
        reconnect_current_delay: int = 0
        - current delay in milliseconds for next reconnect (doubles with every try)
        reconnect_delay_max: int = 0
        - max delay in milliseconds for next reconnect, resets to reconnect_delay
        retries_send: int = 0
        - number of times to retry a send operation
        retry_on_empty: bool = False
        - retry read when receiving nothing (warning e.g. tcp uses this to signal EOF)
        silent_interval: int = 0
        - pause between sending packets
        timeout_connect: int = 10
        - Max. time in milliseconds for connect to be successful
        timeout_comm: int = 5
        - Max. time in milliseconds for recv/send to be successful
    """

    def __init__(
        self,
        framer: ModbusFramer,
        comm_name: str,
        slaves: List[int],
    ) -> None:
        """Initialize a transport instance."""
        # local variables
        self.framer = framer
        self.comm_name = comm_name
        self.slaves = slaves
        self.transport: Any = None

        # property variables
        self.ps_close_comm_on_error: bool = False
        self.ps_reconnect_delay: int = 0
        self.ps_reconnect_delay_max: int = 0
        self.ps_retries_send: int = 0
        self.ps_retry_on_empty: bool = False
        self.ps_silent_interval: int = 0
        self.ps_timeout_connect: int = 10
        self.ps_timeout_comm: int = 5
        self.ps_connected: bool = False

    # -------------------------- #
    # Transport external methods #
    # -------------------------- #
    def connection_made(self, transport):
        """Call when a connection is made.

        The transport argument is the transport representing the connection.
        """
        self.transport = transport
        Log.debug("Connected on transport {}", transport)
        self.ps_connected = True
        self.cb_connection_made()

    def connection_lost(self, reason):
        """Call when the connection is lost or closed.

        The argument is either an exception object or None
        """
        self.ps_connected = False
        if reason:
            Log.debug(
                "Connection lost due to {} on transport {}", reason, self.transport
            )
        self.cb_connection_lost(reason)

    def data_received(self, data):
        """Call when some data is received.

        data is a non-empty bytes object containing the incoming data.
        """
        Log.debug("recv: {}", data, ":hex")
        # self.framer.processIncomingPacket(data, self._handle_response, unit=0)

    def send(self, request: bytes) -> bool:
        """Send request."""
        return self.cb_send(request)

    def close(self) -> None:
        """Close the underlying socket connection (call **sync/async**)."""
        # raise NotImplementedException

    # -------------------------- #
    # Transport callback methods #
    # -------------------------- #
    @abstractmethod
    def cb_connection_made(self) -> bool:
        """Handle low level."""

    @abstractmethod
    def cb_connection_lost(self, _reason) -> bool:
        """Handle low level."""

    @abstractmethod
    def cb_send(self, _request) -> bool:
        """Handle low level."""

    @abstractmethod
    def cb_close(self) -> bool:
        """Handle low level."""

    # ----------------------------------------------------------------------- #
    # The magic methods
    # ----------------------------------------------------------------------- #
    def __enter__(self) -> BaseTransport:
        """Implement the client with enter block."""
        return self

    async def __aenter__(self):
        """Implement the client with enter block."""
        return self

    def __exit__(self, _class, _value, _traceback) -> None:
        """Implement the client with exit block."""
        self.close()

    async def __aexit__(self, _class, _value, _traceback) -> None:
        """Implement the client with exit block."""
        self.close()

    def __str__(self) -> str:
        """Build a string representation of the connection."""
        return f"{self.__class__.__name__}({self.comm_name})"
