from PySide import QtCore


class Signals(QtCore.QObject):

    session_start = QtCore.Signal(dict)

    rosterChanged = QtCore.Signal(dict)

    message_received = QtCore.Signal(dict)

    auth_failed = QtCore.Signal()

    disconnected = QtCore.Signal()

    contact_online = QtCore.Signal(dict)

    muc_contact_online = QtCore.Signal(dict)

    contact_offline = QtCore.Signal(dict)

    muc_contact_offline = QtCore.Signal(dict)

    subs_in = QtCore.Signal(str)

    unsubs_in = QtCore.Signal(str)


_SIGNALS = Signals()


def getSignals():
    return _SIGNALS
