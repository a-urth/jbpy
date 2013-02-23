from PySide import QtCore
#from sleekxmpp import BaseXMPP


class Signals(QtCore.QObject):

    clientConnected = QtCore.Signal()
    messageReceived = QtCore.Signal(dict)
    messageSent = QtCore.Signal(str, str)
    authorizationFailed = QtCore.Signal()


SIGNALS = Signals()