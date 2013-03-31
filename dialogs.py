import re
import chatutils
from PySide import QtGui
from PySide import QtCore


class LoginDialog(QtGui.QDialog):
    '''Dialog for login, related for credentials validation. Connection itself
        performed in ContactList class.'''

    def __init__(self, parent):
        super(LoginDialog, self).__init__(parent=parent)
        self.reg = r'[\w\d]+@[\w\d]+$'
        self.setSizeGripEnabled(False)
        self.setWindowTitle('Login')
        self.initUI()

    def initUI(self):
        self.jid = QtGui.QLineEdit()
        self.jid.editingFinished.connect(self.onCredentialsEntered)
        self.pwd = QtGui.QLineEdit()
        self.pwd.editingFinished.connect(self.onCredentialsEntered)
        self.pwd.setEchoMode(QtGui.QLineEdit.Password)

        self.login = QtGui.QPushButton('Login')
        self.login.clicked.connect(self.accept)
        self.login.setDefault(True)

        hl1 = QtGui.QHBoxLayout()
        hl1.addWidget(QtGui.QLabel('Jabber ID'))
        hl1.addWidget(self.jid)

        hl2 = QtGui.QHBoxLayout()
        hl2.addWidget(QtGui.QLabel('Password'))
        hl2.addWidget(self.pwd)

        vl = QtGui.QVBoxLayout()
        vl.addLayout(hl1)
        vl.addLayout(hl2)
        vl.addWidget(self.login)

        self.setLayout(vl)

    def clean(self):
        self.jid.clear()
        self.jid.setFocus(QtCore.Qt.OtherFocusReason)
        self.pwd.clear()

    @QtCore.Slot()
    def onCredentialsEntered(self):
        if re.match(self.reg, self.jid.text()):
            chatutils.colorWidget(self.jid)
            if len(self.pwd.text()):
                chatutils.colorWidget(self.pwd)
                self.login.setEnabled(True)
            else:
                self.showError(self.pwd)
        else:
            self.showError(self.jid)

    def showError(self, element):
        chatutils.colorWidget(element, chatutils.RED)
        element.setFocus(QtCore.Qt.OtherFocusReason)


class AddContactDialog(QtGui.QDialog):
    '''Add contact dialog, responsible for gathering operation about contact
        to add.'''

    def __init__(self, parent):
        super(AddContactDialog, self).__init__(parent=parent)
        self.setSizeGripEnabled(False)
        self.setWindowTitle('Add contact')
        self.initUI()

    def initUI(self):
        self.jid = QtGui.QLineEdit()
        add = QtGui.QPushButton('Subscribe')
        add.clicked.connect(self.subscribe)
        hl1 = QtGui.QHBoxLayout()
        hl1.addWidget(QtGui.QLabel('Jabber ID'))
        hl1.addWidget(self.jid)
        hl2 = QtGui.QHBoxLayout()
        hl2.addWidget(add)
        vl = QtGui.QVBoxLayout()
        vl.addLayout(hl1)
        vl.addLayout(hl2)
        self.setLayout(vl)

    def clean(self):
        chatutils.colorWidget(self.jid)
        self.jid.clear()

    def subscribe(self):
        if re.match(r'^[\w\d]+@[\w\d]+$', self.jid.text()):
            self.accept()
        else:
            chatutils.colorWidget(self.jid, chatutils.RED)
            return


class RoomEntryDialog(QtGui.QDialog):
    '''Room entry dialog window.
        Responsible for gathering room related info.'''

    def __init__(self, parent):
        super(RoomEntryDialog, self).__init__(parent=parent)
        self.setSizeGripEnabled(False)
        self.setWindowTitle('Enter room')
        self.initUI()

    def initUI(self):
        self.room_id = QtGui.QLineEdit()
        self.nick = QtGui.QLineEdit()
        enter = QtGui.QPushButton('Enter')
        enter.clicked.connect(self.enter)
        hl1 = QtGui.QHBoxLayout()
        hl1.addWidget(QtGui.QLabel('Room ID'))
        hl1.addWidget(self.room_id)
        hl2 = QtGui.QHBoxLayout()
        hl2.addWidget(QtGui.QLabel('Nick'))
        hl2.addWidget(self.nick)
        hl3 = QtGui.QHBoxLayout()
        hl3.addWidget(enter)
        vl = QtGui.QVBoxLayout()
        vl.addLayout(hl1)
        vl.addLayout(hl2)
        vl.addLayout(hl3)
        self.setLayout(vl)

    def enter(self):
        if re.match(r'^[\w\d]+@conference.[\w\d]+$', self.room_id.text()):
            if len(self.nick.text()):
                self.accept()
            else:
                chatutils.colorWidget(self.nick, chatutils.RED)
        else:
            chatutils.colorWidget(self.room_id, chatutils.RED)

    def clean(self):
        chatutils.colorWidget(self.room_id)
        self.room_id.clear()
        chatutils.colorWidget(self.nick)
        self.nick.clear()

    def get_credentials(self):
        return (self.room_id.text(), self.nick.text())
