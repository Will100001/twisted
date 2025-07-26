"""
Generic forwarder from a stream server listener to a stream client.
"""

from dataclasses import dataclass, field
from typing import Any

from zope.interface import implementer

from twisted.internet.defer import Deferred
from twisted.internet.interfaces import (
    IAddress,
    IProtocol,
    IProtocolFactory,
    IStreamClientEndpoint,
)
from twisted.internet.protocol import Factory
from twisted.python.failure import Failure


@implementer(IProtocol)
@dataclass
class _ForwardingListener:
    _forwardTo: IStreamClientEndpoint
    _transport: Any = field(init=False)
    _otherTransport: Any = field(init=False)

    def makeConnection(self, transport: Any) -> None:
        self._transport = transport

        async def _() -> None:
            transport.pauseProducing()
            proto: Any = await self._forwardTo.connect(
                Factory.forProtocol(_ForwardingConnection)
            )
            self._otherTransport = proto.transport
            proto.transport.registerProducer(transport)
            transport.registerProducer(proto.transport)
            transport.resumeProducing()

        Deferred.fromCoroutine(_())

    def connectionMade(self) -> None:
        ...

    def dataReceived(self, data: bytes) -> None:
        self._transport.write(data)

    def connectionLost(self, reason: Failure) -> None:
        if self._otherTransport is None:
            return
        transport, self._otherTransport = self._otherTransport, None

        transport.loseConnection()
        transport.unregisterProducer()


@implementer(IProtocol)
@dataclass
class _ForwardingConnection:
    _otherTransport: Any

    def makeConnection(self, transport: Any) -> None:
        ...

    def connectionMade(self) -> None:
        ...

    def dataReceived(self, data: bytes) -> None:
        self._otherTransport.write(data)

    def connectionLost(self, reason: Failure) -> None:
        if self._otherTransport is None:
            return
        transport, self._otherTransport = self._otherTransport, None

        transport.loseConnection()
        transport.unregisterProducer()


@implementer(IProtocolFactory)
@dataclass
class EndpointForwarderFactory:
    _forwardTo: IStreamClientEndpoint

    def doStart(self) -> None:
        """
        start listening.
        """

    def doStop(self) -> None:
        """
        stopped listening.
        """

    def buildProtocol(self, addr: IAddress) -> IProtocol:
        """
        build a protocol
        """
        return _ForwardingListener(self._forwardTo)
