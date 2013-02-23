import datetime
import signals
import chatutils
from PySide import QtGui
from PySide import QtCore


class ChatWindow(QtGui.QMainWindow):

    def __init__(self, parent, title):
        super(ChatWindow, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle(title)
        self.resize(600, 500)        

        self.chat = ChatWidget(self, parent.jid, title)
        self.setCentralWidget(self.chat)

        self.center()
        self.show()

    def center(self):
        geo = self.frameGeometry()
        center = QtGui.QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())

    def closeEvent(self, event):
        self.hide()
        event.ignore()


class ChatWidget(QtGui.QWidget):

    def __init__(self, parent, owner_jid, target_jid):
        super(ChatWidget, self).__init__(parent)

        self.owner_jid = owner_jid
        self.target_jid = target_jid

        self.chat = QtGui.QTextEdit()
        self.chat.setReadOnly(True)
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
            signals.SIGNALS.messageSent.emit(self.target_jid, msg)