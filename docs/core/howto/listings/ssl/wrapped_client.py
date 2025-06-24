from typing import Any

from twisted.internet.defer import Deferred
from twisted.internet.endpoints import (
    HostnameEndpoint,
    optionsForClientTLS,
    wrapClientTLS,
)
from twisted.internet.interfaces import ITCPTransport
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.task import react
from twisted.python.failure import Failure


async def main(reactor: Any, hostname: str = "example.com") -> None:
    tcpEndpoint = HostnameEndpoint(reactor, hostname, 443)
    tlsEndpoint = wrapClientTLS(optionsForClientTLS(hostname), tcpEndpoint)

    class ExampleHTTP(Protocol):
        def makeConnection(self, transport: ITCPTransport) -> None:
            transport.write(f"GET / HTTP/1.1\r\nHost: {hostname}\r\n\r\n".encode())

        def dataReceived(self, data: bytes) -> None:
            print(f"data: {data!r}")

    await tlsEndpoint.connect(Factory.forProtocol(ExampleHTTP))
    await Deferred()


if __name__ == "__main__":
    from sys import argv

    react(main, argv[1:])
