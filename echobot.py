import sleekxmpp
import ssl
import logging


class SleekXMPPClient(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        super(SleekXMPPClient, self).__init__(jid, password)

        self.ssl_version = ssl.PROTOCOL_SSLv3
        self.add_event_handler('session_start', self.onStart)
        self.add_event_handler('message', self.onMessage)

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0199')

        if self.connect(reattempt=False):
            logging.info('Bot connected...')
            self.process(block=False)
        else:
            print 'Could not connect!'

    def onStart(self, event):
        self.send_presence()
        self.get_roster()

    def onMessage(self, msg):
        body = msg['body']
        logging.info('Received message...\nFrom %s\n%s' % (msg['from'], body))
        if msg['type'] in ['normal', 'chat']:
            msg.reply('Echo bot answers You...\n%s' % body).send()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    client = SleekXMPPClient('echobot@free2use', 'tobohce')