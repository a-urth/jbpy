import signals
import chatutils
import logging
from PySide import QtGui
from PySide import QtCore
from login import LoginDialog
from sleekclient import SleekXMPPClient, CouldNotConnectError
from contacts import Contacts
from chatwindow import ChatWindow


class ContactList(QtGui.QMainWindow):

    MAIN_ICON = 'resources/main.png'
    DISCONNECTED_TRAY_ICON = 'resources/disconnected.png'
    CONNECTED_TRAY_ICON = 'resources/connected.png'

    def __init__(self):
        super(ContactList, self).__init__(parent=None)        
        self.client = None
        self.chatWindows = {}

        signals.SIGNALS.clientConnected.connect(self.onConnect)
        signals.SIGNALS.messageReceived.connect(self.messageReceived)
        signals.SIGNALS.authorizationFailed.connect(self.authorizationFailed)

        self.setWindowTitle('JBPY')
        self.statusBar()        
        self.resize(200, 500)
        self.center()
        self.setWindowIcon(QtGui.QIcon(self.MAIN_ICON))        

        self.initMenu()
        self.initUI()
        self.initTray()        

    def initMenu(self):
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit Application')
        exitAction.triggered.connect(self.close)

        loginAction = QtGui.QAction('&Login', self)
        loginAction.setShortcut('Ctrl+L')
        loginAction.setStatusTip('Login to server')
        loginAction.triggered.connect(self.login)

        menuBar = self.menuBar()
        fileM = menuBar.addMenu('&File')
        fileM.addAction(loginAction)
        fileM.addSeparator()
        fileM.addAction(exitAction)

    def initUI(self):
        self.loginDialog = LoginDialog(self)
        self.contacts = Contacts(self)
        self.setCentralWidget(self.contacts)

    def initTray(self):
        self.disc_icon = QtGui.QIcon(self.DISCONNECTED_TRAY_ICON)
        self.conn_icon = QtGui.QIcon(self.CONNECTED_TRAY_ICON)
        self.tray = QtGui.QSystemTrayIcon(self.disc_icon)
        self.tray.show()        

    def connect(self):
        self.jid = self.loginDialog.jid.text()
        pwd = self.loginDialog.pwd.text()
        try:
            self.client = SleekXMPPClient(self.jid, pwd)
            return True
        except CouldNotConnectError, e:
            QtGui.QMessageBox.warning(self, 'Error', str(e),
                                      QtGui.QMessageBox.Ok)
            return False

    def openChatWindow(self, name):
        win = self.chatWindows.get(name)
        if win:
            win.show()
        else:
            self.chatWindows[name] = ChatWindow(self, name)

    def center(self):
        geo = self.frameGeometry()
        center = QtGui.QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())

    def closeEvent(self, event):
        question = QtGui.QMessageBox.question(self, 'Message',
                    'Are You sure to quit?',
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No)

        if question == QtGui.QMessageBox.Yes:
            if self.client:
                self.client.disconnect(wait=True)
            event.accept()
        else:
            event.ignore()    

    @QtCore.Slot()    
    def login(self):        
        if self.client:
            QtGui.QMessageBox.information(self, 'Info',
            'You already connected!', QtGui.QMessageBox.Ok)
            return
        if self.loginDialog.exec_() == QtGui.QDialog.Accepted:
            if self.connect():            
                self.setWindowTitle(' - '.join(['JBPY', self.jid]))
                self.tray.setIcon(self.conn_icon)

    @QtCore.Slot()
    def messageReceived(self, message):        
        _from = str(message['from']).split('/')[0]
        body = message['body']
        area = self.chatWindows.get(_from)
        message = chatutils.formHtmlMessage(_from, body)
        if area:
            area.chat.writeMessageToArea(message)
        chatutils.writeMessageToFile(_from, message)

    @QtCore.Slot()
    def onConnect(self):
        self.contacts.addContacts(self.client.client_roster)

    @QtCore.Slot()
    def authorizationFailed(self):
        QtGui.QMessageBox.warning(self, 'Error', 'Wrong login or password!',
                                  QtGui.QMessageBox.Ok)