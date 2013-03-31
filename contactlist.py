import signals
import chatutils
from PySide import QtGui, QtCore
from dialogs import LoginDialog, RoomEntryDialog
from sleekclient import SleekXMPPClient, CouldNotConnectError
from widgets import Contacts, ChatWindow


class ContactList(QtGui.QMainWindow):
    '''Main window, which contains menu and widget with all contacts related
        controls. Responsible for connection, incoming messages handling,
        chat windows organization.'''

    MAIN_ICON = 'resources/main.png'
    DISCONNECTED_TRAY_ICON = 'resources/disconnected.png'
    CONNECTED_TRAY_ICON = 'resources/connected.png'
    MESSAGE_TRAY_ICON = 'resources/message.png'

    def __init__(self):
        super(ContactList, self).__init__(parent=None)
        self.client = None
        self.chatWindows = {}
        self.mucWindows = {}

        signals.getSignals().session_start.connect(self.session_start)
        signals.getSignals().rosterChanged.connect(self.addContacts)
        signals.getSignals().message_received.connect(self.message_received)
        signals.getSignals().auth_failed.connect(self.auth_failed)
        signals.getSignals().disconnected.connect(self.disconnected)
        signals.getSignals().contact_online.connect(self.contact_online)
        signals.getSignals().contact_offline.connect(self.contact_offline)
        signals.getSignals().muc_contact_online.connect(
            self.muc_contact_online)
        signals.getSignals().muc_contact_offline.connect(
            self.muc_contact_offline)
        signals.getSignals().subs_in.connect(self.subs_in)
        signals.getSignals().unsubs_in.connect(self.unsubs_in)

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

        self.loginAction = QtGui.QAction('&Log In', self)
        self.loginAction.setShortcut('Ctrl+I')
        self.loginAction.setStatusTip('Login to server')
        self.loginAction.triggered.connect(self.login)

        self.logOutAction = QtGui.QAction('&Log Out', self)
        self.logOutAction.setEnabled(False)
        self.logOutAction.setShortcut('Ctrl+O')
        self.logOutAction.setStatusTip('Log out from server')
        self.logOutAction.triggered.connect(self.logout)

        self.enterRoomAction = QtGui.QAction('&Enter Room', self)
        self.enterRoomAction.setEnabled(False)
        self.enterRoomAction.setShortcut('Ctrl+R')
        self.enterRoomAction.setStatusTip('Enter multi user chat room')
        self.enterRoomAction.triggered.connect(self.enterRoom)

        menuBar = self.menuBar()
        fileM = menuBar.addMenu('&File')
        fileM.addAction(self.loginAction)
        fileM.addAction(self.logOutAction)
        fileM.addSeparator()
        fileM.addAction(exitAction)

        roomM = menuBar.addMenu('&Room')
        roomM.addAction(self.enterRoomAction)

    def initUI(self):
        self.loginDialog = LoginDialog(self)
        self.roomDialog = RoomEntryDialog(self)
        self.contacts = Contacts(self)
        self.setCentralWidget(self.contacts)

    def initTray(self):
        exit_ = QtGui.QAction('&Exit', self)
        exit_.triggered.connect(self.close)

        tray_menu = QtGui.QMenu('Tray Context Menu')
        tray_menu.addAction(exit_)

        self.disc_icon = QtGui.QIcon(self.DISCONNECTED_TRAY_ICON)
        self.conn_icon = QtGui.QIcon(self.CONNECTED_TRAY_ICON)
        self.mess_icon = QtGui.QIcon(self.MESSAGE_TRAY_ICON)
        self.tray = QtGui.QSystemTrayIcon(self.disc_icon)
        self.tray.messageClicked.connect(self.onTrayMessageClicked)
        self.tray.activated.connect(self.onTrayActivated)
        self.tray.setContextMenu(tray_menu)
        self.tray.show()

    def openChatWindow(self, name):
        win = self.chatWindows.get(name)
        if win:
            win.show()
        else:
            self.chatWindows[name] = ChatWindow(self, name)

    def closeChatWindow(self, name):
        win = self.chatWindows.get(name)
        if win:
            win.close()
            del win

    def center(self):
        geo = self.frameGeometry()
        center = QtGui.QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())

# ---ACTIONS---
    def login(self):
        self.loginDialog.clean()
        if self.loginDialog.exec_() == QtGui.QDialog.Accepted:
            self.jid = self.loginDialog.jid.text()
            pwd = self.loginDialog.pwd.text()
            try:
                self.client = SleekXMPPClient(self.jid, pwd)
                self.client.connect_()
            except CouldNotConnectError, e:
                QtGui.QMessageBox.warning(
                    self,
                    'Error',
                    str(e),
                    QtGui.QMessageBox.Ok)

    def logout(self):
        if self.client and self.client.connected:
            self.client.disconnect(wait=True)

    def enterRoom(self):
        self.roomDialog.clean()
        if self.roomDialog.exec_() == QtGui.QDialog.Accepted:
            room_id, nick = self.roomDialog.get_credentials()
            self.client.enter_room(room_id, nick)
            self.mucWindows[room_id] = ChatWindow(
                self,
                room_id,
                nick,
                muc=True,
                )

    def closeEvent(self, event):
        question = QtGui.QMessageBox.question(
                       self,
                       'Message',
                       'Are You sure to quit?',
                       QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                       QtGui.QMessageBox.No)

        if question == QtGui.QMessageBox.Yes:
            self.logout()
            event.accept()
        else:
            event.ignore()

    def changeEvent(self, event):
        '''Overloaded changeEvent for catching
            if window activated, change tray icon'''
        if event.type() == QtCore.QEvent.ActivationChange:
            self.tray.setIcon(self.conn_icon)
        event.accept()

# ---EXTERNAL SIGNALS---
    @QtCore.Slot()
    def onTrayMessageClicked(self):
        self.tray.setIcon(self.conn_icon)
        if self.isMinimized():
            self.showNormal()
        self.activateWindow()

    @QtCore.Slot()
    def onTrayActivated(self, reason):
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            self.tray.setIcon(self.conn_icon)
            if self.isMinimized():
                self.showNormal()
                self.activateWindow()
            else:
                self.showMinimized()

    @QtCore.Slot()
    def addContacts(self, contacts):
        self.contacts.addContacts(contacts)

    @QtCore.Slot()
    def session_start(self, roster):
        self.setWindowTitle(' - '.join(['JBPY', self.jid]))
        self.tray.setIcon(self.conn_icon)
        self.loginAction.setEnabled(False)
        self.logOutAction.setEnabled(True)
        self.enterRoomAction.setEnabled(True)
        self.contacts.enableAll()
        self.addContacts(roster)

    @QtCore.Slot()
    def message_received(self, message):
        _from, nick = str(message['from']).split('/')
        body = message['body']
        is_muc = message['type'] == 'groupchat'
        if is_muc:
            area = self.mucWindows.get(_from)
            _from = nick
        else:
            area = self.chatWindows.get(_from)

        message = chatutils.formHtmlMessage(_from, body)
        chatutils.writeMessageToFile(_from, message)

        if area:
            #if there is created window - write there
            area.chat.writeMessageToArea(message)
            #if window is visible, then there is nothing to do
            if area.isVisible() and area.isActiveWindow():
                print 'visible and active'
                return
        #if there is no window or window is invisible
        #show tray notification (if possible)
        #and change icon in contact list (onlu for normal messages)
        if not is_muc:
            self.contacts.setUnreadMessage(_from)
        self.tray.setIcon(self.mess_icon)
        if self.tray.supportsMessages():
            self.tray.showMessage(
                _from,
                body,
                QtGui.QSystemTrayIcon.Information,
                3)

    @QtCore.Slot()
    def disconnected(self):
        self.logOutAction.setEnabled(False)
        self.loginAction.setEnabled(True)
        self.enterRoomAction.setEnabled(False)
        self.tray.setIcon(self.disc_icon)
        self.contacts.disableAll()
        self.contacts.clear()

    @QtCore.Slot()
    def contact_online(self, message):
        name = str(message['from']).split('/')[0]
        self.contacts.setOnline(name)

    @QtCore.Slot()
    def contact_offline(self, message):
        name = str(message['from']).split('/')[0]
        self.contacts.setOffline(name)

    @QtCore.Slot()
    def muc_contact_online(self, presence):
        room, nick = str(presence['from']).split('/')
        win = self.mucWindows[room]
        win.chat.addContact(nick)

    @QtCore.Slot()
    def muc_contact_offline(self, presence):
        room, nick = str(presence['from']).split('/')
        win = self.mucWindows[room]
        win.chat.delContact(nick)

    @QtCore.Slot()
    def subs_in(self, _from):
        question = QtGui.QMessageBox.question(
                       self,
                       'Message',
                       '%s\nSend subscribe request to You.\n'
                       'Do You approve?' % _from,
                       QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                       QtGui.QMessageBox.Yes)

        if question == QtGui.QMessageBox.Yes:
            self.client.subscribeApprove(True, _from)
        else:
            self.client.subscribeApprove(False, _from)

    @QtCore.Slot()
    def unsubs_in(self, _from):
        QtGui.QMessageBox.warning(
            self,
            'Error',
            '%s\nUnsubscribed from You\n'
            'If it exists in Your list'
            'It will be removed' % _from,
            QtGui.QMessageBox.Ok)
        self.contacts.remove_contact(name=_from)

    @QtCore.Slot()
    def auth_failed(self):
        self.logout()
        QtGui.QMessageBox.warning(
            self,
            'Error',
            'Wrong jid or password!',
            QtGui.QMessageBox.Ok)
