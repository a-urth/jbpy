from PySide import QtGui
from PySide import QtCore


class LoginDialog(QtGui.QDialog):

    def __init__(self, parent):
        super(LoginDialog, self).__init__(parent=parent)
        self.parent = parent
        self.setSizeGripEnabled(False)
        self.setWindowTitle('Login')
        self.initUI()

    def initUI(self):
        self.jid = QtGui.QLineEdit()
        self.pwd = QtGui.QLineEdit()
        self.pwd.setEchoMode(QtGui.QLineEdit.Password)

        login = QtGui.QPushButton('Login')
        login.setDefault(True)
        login.clicked.connect(self.accept)
        exit = QtGui.QPushButton('Cancel')
        exit.clicked.connect(self.reject)

        hl1 = QtGui.QHBoxLayout()
        hl1.addWidget(QtGui.QLabel('Jabber ID'))
        hl1.addWidget(self.jid)

        hl2 = QtGui.QHBoxLayout()
        hl2.addWidget(QtGui.QLabel('Password'))
        hl2.addWidget(self.pwd)

        hl3 = QtGui.QHBoxLayout()
        hl3.addWidget(login)
        hl3.addWidget(exit)

        vl = QtGui.QVBoxLayout()
        vl.addLayout(hl1)
        vl.addLayout(hl2)
        vl.addLayout(hl3)

        self.setLayout(vl)