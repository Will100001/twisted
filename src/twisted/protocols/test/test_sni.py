"""
Tests for server name indication TLS handshakes, both endpoints and protocols.
"""

from twisted.trial.unittest import SynchronousTestCase


class SNITests(SynchronousTestCase):
    def test_ok(self) -> None:
        """
        A successful connection verifies OK.
        """

    def test_nocert(self) -> None:
        """
        No certificate for the given name was found; an error was reported
        correctly.
        """

    def test_nosni(self) -> None:
        """
        No SNI was given, the default certificate was returned.
        """

    def test_nokey(self) -> None:
        """
        No private key was found for a given certificate; it should be logged
        appropriately.
        """
