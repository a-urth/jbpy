import chatutils
import codecs
from dialogs import AddContactDialog
from PySide import QtGui
from PySide import QtCore


class Contacts(QtGui.QWidget):
    '''Main widget for contacts (main) window containing all related controls
        for contacts.'''

    ADD_CONTACT_ICON = 'resources/add_contact.png'
    DEL_CONTACT_ICON = 'resources/del_contact.png'
    CONTACT_OFFLINE_ICON = 'resources/user_out.png'
    CONTACT_ONLINE_ICON = 'resources/user_in.png'
    MESSAGE_ICON = 'resources/message.png'

    def __init__(self, parent):
        super(Contacts, self).__init__(parent)
        self.main_window = parent
        self.online_icon = QtGui.QIcon(self.CONTACT_ONLINE_ICON)
        self.offline_icon = QtGui.QIcon(self.CONTACT_OFFLINE_ICON)
        self.message_icon = QtGui.QIcon(self.MESSAGE_ICON)

        self.initUI()
        self.addContactDia = AddContactDialog(self)

    def initUI(self):
        self.contacts = QtGui.QListWidget(self)
        self.contacts.itemDoubleClicked.connect(self.onDoubleClick)
        hl1 = QtGui.QHBoxLayout()
        hl1.addWidget(self.contacts)

        add_icon = QtGui.QIcon(self.ADD_CONTACT_ICON)
        del_icon = QtGui.QIcon(self.DEL_CONTACT_ICON)

        self.add_contact = QtGui.QPushButton(add_icon, '')
        self.add_contact.clicked.connect(self.addContact)
        self.del_contact = QtGui.QPushButton(del_icon, '')
        self.del_contact.clicked.connect(self.delContact)

        hl2 = QtGui.QHBoxLayout()
        hl2.addWidget(self.add_contact)
        hl2.addWidget(self.del_contact)

        vl = QtGui.QVBoxLayout()
        vl.addLayout(hl1)
        vl.addLayout(hl2)

        self.setLayout(vl)
        self.disableAll()

    def disableAll(self):
        self.add_contact.setEnabled(False)
        self.del_contact.setEnabled(False)

    def enableAll(self):
        self.add_contact.setEnabled(True)
        self.del_contact.setEnabled(True)

    def clear(self):
        self.contacts.clear()

    def setOnline(self, contact):
        item = self.contacts.findItems(contact, QtCore.Qt.MatchExactly)[0]
        item.setIcon(self.online_icon)

    def setOffline(self, contact):
        item = self.contacts.findItems(contact, QtCore.Qt.MatchExactly)[0]
        item.setIcon(self.offline_icon)

    def setUnreadMessage(self, contact):
        item = self.contacts.findItems(contact, QtCore.Qt.MatchExactly)[0]
        item.setBackground(QtGui.QBrush(QtGui.QColor(27, 188, 224)))

    def addContacts(self, contacts):
        for contact in contacts:
            item = QtGui.QListWidgetItem(self.offline_icon, contact)
            self.contacts.addItem(item)

    def remove_contact(self, row=0, name=''):
        row_i = row
        if name:
            items = self.contacts.findItems(name, QtCore.Qt.MatchExactly)
            if len(items):
                row_i = self.contacts.row(items[0])
            else:
                return
        item = self.contacts.takeItem(row_i)
        self.main_window.closeChatWindow(item.text())
        self.main_window.client.unsubscribe_from_contact(item.text())

    @QtCore.Slot()
    def addContact(self):
        self.addContactDia.clean()
        if self.addContactDia.exec_() == QtGui.QDialog.Accepted:
            jid = self.addContactDia.jid.text()
            if len(self.contacts.findItems(jid, QtCore.Qt.MatchExactly)):
                QtGui.QMessageBox.warning(
                    self,
                    'Error',
                    'Such contact already exists.',
                    QtGui.QMessageBox.Ok)
                return
            self.main_window.client.subscribe_to_contact(jid)

    @QtCore.Slot()
    def delContact(self):
        contact = self.contacts.currentItem()
        if not contact:
            QtGui.QMessageBox.warning(
                self,
                'Error',
                'Please, select contact to delete.',
                QtGui.QMessageBox.Ok)
            return

        question = QtGui.QMessageBox.question(
                       self, 'Message',
                       'Are You sure to delete?\n%s' % contact.text(),
                       QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                       QtGui.QMessageBox.No)

        if question == QtGui.QMessageBox.Yes:
            self.remove_contact(row=self.contacts.currentRow())

    @QtCore.Slot()
    def onDoubleClick(self, item):
        item.setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.main_window.openChatWindow(item.text())


class ChatWindow(QtGui.QMainWindow):
    '''Window, which contains main chat widget.
        All messages related logic is in ChatWidget class.'''

    def __init__(self, parent, id_, nick='', muc=False):
        super(ChatWindow, self).__init__(parent)
        self.id_ = id_
        self.is_muc = muc
        self.nick = nick
        self.client = parent.client
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.resize(600, 500)

        if self.is_muc:
            self.chat = MUChatWidget(self, parent.jid, id_)
            self.setWindowTitle(id_ + ' - ' + nick)
        else:
            self.setWindowTitle(id_)
            self.chat = ChatWidget(self, parent.jid, id_)
        self.setCentralWidget(self.chat)

        self.center()
        self.show()

    def center(self):
        geo = self.frameGeometry()
        center = QtGui.QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())

    def closeEvent(self, event):
        if self.is_muc:
            self.client.leave_muc(self.id_, self.nick)
            event.accept()
        self.hide()
        event.ignore()


class ChatWidget(QtGui.QWidget):
    '''Main widget for chat window. Responsible for messages display and
        send.'''

    def __init__(self, parent, owner_jid, target_jid):
        super(ChatWidget, self).__init__(parent)
        self.main_window = parent
        self.owner_jid = owner_jid
        self.target_jid = target_jid

        self.chat = QtGui.QTextEdit()
        self.chat.setReadOnly(True)

        try:
            _filename = ['./history/', self.target_jid, '.txt']
            #Filling message area with last 20 lines if history
            f = codecs.open(''.join(_filename), 'r', 'utf8')
            for i in range(20):
                self.writeMessageToArea(f.readline())
        except IOError:
            #If there is no history file - do nothing
            pass

        self.msg = QtGui.QTextEdit()
        self.msg.setFocus()

        vl = QtGui.QVBoxLayout()
        vl.addWidget(self.chat, stretch=6)
        vl.addWidget(self.msg, stretch=1)

        self.setLayout(vl)

    def writeMessageToArea(self, msg):
        self.chat.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.chat.insertHtml(msg)
        self.chat.ensureCursorVisible()

    def keyPressEvent(self, event):
        enter = QtCore.Qt.Key_Return
        if event.key() == enter and (event.modifiers() & QtCore.Qt.CTRL):
            msg = self.msg.toPlainText()
            messageHtml = chatutils.formHtmlMessage(self.owner_jid, msg)
            self.writeMessageToArea(messageHtml)
            chatutils.writeMessageToFile(self.target_jid, messageHtml)

            self.msg.clear()
            self.main_window.client.send_message(
                mto=self.target_jid,
                mbody=msg,
                )


class MUChatWidget(QtGui.QWidget):
    '''Main widget for MUC window. Responsible for messages display and
        send.'''

    def __init__(self, parent, owner_jid, room_id):
        super(MUChatWidget, self).__init__(parent)
        self.main_window = parent
        self.owner_jid = owner_jid
        self.room_id = room_id

        self.chat = QtGui.QTextEdit()
        self.chat.setReadOnly(True)

        try:
            _filename = ['./history/', self.room_id, '.txt']
            #Filling message area with last 20 lines if history
            f = codecs.open(''.join(_filename), 'r', 'utf8')
            for i in range(20):
                self.writeMessageToArea(f.readline())
        except IOError:
            #If there is no history file - do nothing
            pass

        self.contacts = QtGui.QListWidget(self)

        hl = QtGui.QHBoxLayout()
        hl.addWidget(self.chat, stretch=4)
        hl.addWidget(self.contacts, stretch=1)

        self.msg = QtGui.QTextEdit()
        self.msg.setFocus()

        vl = QtGui.QVBoxLayout()
        vl.addLayout(hl, stretch=6)
        vl.addWidget(self.msg, stretch=1)

        self.setLayout(vl)

    def writeMessageToArea(self, msg):
        self.chat.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.chat.insertHtml(msg)
        self.chat.ensureCursorVisible()

    def keyPressEvent(self, event):
        enter = QtCore.Qt.Key_Return
        if event.key() == enter and (event.modifiers() & QtCore.Qt.CTRL):
            msg = self.msg.toPlainText()
            messageHtml = chatutils.formHtmlMessage(self.owner_jid, msg)
            chatutils.writeMessageToFile(self.room_id, messageHtml)

            self.msg.clear()
            self.main_window.client.send_message(
                mto=self.room_id,
                mbody=msg,
                mtype='groupchat',
                )

    def addContact(self, contact):
        item = QtGui.QListWidgetItem(contact)
        self.contacts.addItem(item)

    def delContact(self, contact):
        items = self.contacts.findItems(contact, QtCore.Qt.MatchExactly)
        if len(items):
            row_i = self.contacts.row(items[0])
        else:
            return
        self.contacts.takeItem(row_i)
