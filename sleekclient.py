import sleekxmpp
import ssl
import signals
from PySide import QtCore


class CouldNotConnectError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class SleekXMPPClient(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        super(SleekXMPPClient, self).__init__(jid, password)

        self.jabber_id = jid        

        signals.SIGNALS.messageSent.connect(self.messageSent)

        self.ssl_version = ssl.PROTOCOL_SSLv3
        self.add_event_handler('session_start', self.onStart)
        self.add_event_handler('message', self.onMessage)
        self.add_event_handler('no_auth', self.onAuthFailed)

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0199')

        if self.connect(reattempt=False):
            self.process(block=False)
        else:
            raise CouldNotConnectError,\
                  'Could not connect using %s' % self.jabber_id 

    def onStart(self, event):
        self.send_presence()
        self.get_roster()        
        signals.SIGNALS.clientConnected.emit()

    def onMessage(self, message):
        if message['type'] in ('normal', 'chat'):
            signals.SIGNALS.messageReceived.emit(message)

    def onAuthFailed(self, event):
        signals.SIGNALS.authorizationFailed.emit()

    @QtCore.Slot(str)
    def messageSent(self, to, body):        
        self.send_message(to, body)