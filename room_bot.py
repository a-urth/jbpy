import sleekxmpp
import ssl
import logging


class SleekXMPPClient(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, room):
        super(SleekXMPPClient, self).__init__(jid, password)

        self.room = room
        self.nick = 'ECHOBOT'
        self.reply_message = 'Hello, %s! Welcome to our room.'

        self.ssl_version = ssl.PROTOCOL_SSLv3
        self.add_event_handler('session_start', self.onStart)
        self.add_event_handler('groupchat_message', self.onGroupMessage)
        self.add_event_handler(
            'muc::%s::got_online' % self.room,
            self.onMUConline,
            )

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0199')
        self.register_plugin('xep_0045')

        if self.connect():
            logging.info('Bot connected...')
            self.process(block=False)
        else:
            print 'Could not connect!'

    def onStart(self, event):
        self.send_presence()
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(
            self.room,
            self.nick,
            wait=True
            )

    def onGroupMessage(self, msg):
        body = msg['body']
        logging.info('Received message...\nFrom %s\n%s' % (msg['from'], body))
        if body.startswith(self.nick):
            msg.reply("Please, don't write to me, I'm just a bot.").send()
        pass

    def onMUConline(self, presence):
        if presence['muc']['nick'] != self.nick:
            self.send_message(
                mto=presence['from'].bare,
                mbody=self.reply_message % presence['muc']['nick'],
                mtype='groupchat',
                )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    client = SleekXMPPClient(
        'echobot@cebuad002',
        'tobohce',
        'room@conference.cebuad002',
        )
