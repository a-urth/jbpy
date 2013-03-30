import pytest
from sleekclient import SleekXMPPClient, CouldNotConnectError


def test_login():
    client = SleekXMPPClient('dummy@cebuad002', 'dummy')
    assert client.connect_() is True
    client.disconnect(wait=True)


def test_wrong_login():
    with pytest.raises(CouldNotConnectError):
        SleekXMPPClient('asd@asd', 'asd').connect_()
