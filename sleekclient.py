import sleekxmpp
import ssl
import signals


class CouldNotConnectError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class SleekXMPPClient(sleekxmpp.ClientXMPP):
    '''Connection client class. Responsible for all incoming/outgoing
        messages handle. Passes signals to responsible components.'''

    def __init__(self, jid, password):
        super(SleekXMPPClient, self).__init__(jid, password)

        self.jabber_id = jid
        self.connected = False
        self.auto_authorize = None

        self.ssl_version = ssl.PROTOCOL_SSLv3
        self.add_event_handler('session_start', self.onStart)
        self.add_event_handler('message', self.onMessage, threaded=True)
        self.add_event_handler('failed_auth', self.onAuthFailed)
        self.add_event_handler("disconnected", self.onDisconnect)
        self.add_event_handler("got_online", self.onOnline)
        self.add_event_handler("got_offline", self.onOffline)
        self.add_event_handler("presence_subscribe", self.onSubscribe)
        self.add_event_handler("presence_unsubscribed", self.onUnSubscribed)

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0199')

    def connect_(self):
        if self.connect(reattempt=False):
            self.connected = True
            self.process(block=False)
            return True
        else:
            raise (CouldNotConnectError),\
                  'Could not connect using %s' % self.jabber_id

    def subscribeApprove(self, approve, to):
        if approve:
            self.send_presence(pto=to, ptype='subscribed')
            #If there was no subscription from us, we send it
            #and add to our contact list
            if not self.client_roster[to]['to']:
                self.send_presence(pto=to, ptype='subscribe')
                signals.getSignals().rosterChanged.emit([str(to)])
        else:
            self.send_presence(pto=to, ptype='unsubscribed')

    def onStart(self, event):
        self.send_presence()
        self.get_roster()
        signals.getSignals().session_start.emit(self.client_roster)

    def onMessage(self, message):
        if str(message['from']).split('/')[0] not in self.client_roster:
            return
        signals.getSignals().message_received.emit(message)

    def onAuthFailed(self, event):
        signals.getSignals().auth_failed.emit()

    def onDisconnect(self, event):
        self.connected = False
        signals.getSignals().disconnected.emit()

    def onOnline(self, presence):
        if 'conference' in str(presence['from']):
            return
        else:
            signals.getSignals().contact_online.emit(presence)

    def onOffline(self, presence):
        if 'conference' in str(presence['from']):
            return
        else:
            signals.getSignals().contact_offline.emit(presence)

    def onSubscribe(self, presence):
        signals.getSignals().subs_in.emit(str(presence['from']))

    def onUnSubscribed(self, presence):
        signals.getSignals().unsubs_in.emit(str(presence['from']))

    def subscribe_to_contact(self, to):
        self.send_presence(pto=to, ptype='subscribe')
        signals.getSignals().rosterChanged.emit([to])

    def unsubscribe_from_contact(self, who):
        self.send_presence(pto=who, ptype='unsubscribed')
        self.update_roster(who, subscription='remove')

    def enter_room(self, room_id, nick):
        self.register_plugin('xep_0045')
        self.add_event_handler(
            'muc::%s::got_online' % room_id,
            self.muc_online,
            )
        self.add_event_handler(
            'muc::%s::got_offline' % room_id,
            self.muc_offline,
            )

        self.plugin['xep_0045'].joinMUC(room_id, nick, wait=True)

    def leave_muc(self, room_id, nick):
        self.plugin['xep_0045'].leaveMUC(room_id, nick)

    def muc_online(self, presence):
        signals.getSignals().muc_contact_online.emit(presence)

    def muc_offline(self, presence):
        signals.getSignals().muc_contact_offline.emit(presence)
