from PySide import QtGui
from PySide import QtCore


class Contacts(QtGui.QWidget):

    ADD_CONTACT_ICON = 'resources/add_contact.png'
    DEL_CONTACT_ICON = 'resources/del_contact.png'
    LIST_ICON = 'resources/user_out.png'

    def __init__(self, parent):
        super(Contacts, self).__init__(parent)
        self.parent = parent

        self.initUI()

    def initUI(self):
        self.contacts = QtGui.QListWidget(self)
        self.contacts.itemDoubleClicked.connect(self.onDoubleClick)
        hl1 = QtGui.QHBoxLayout()
        hl1.addWidget(self.contacts)

        add_icon = QtGui.QIcon(self.ADD_CONTACT_ICON)
        del_icon = QtGui.QIcon(self.DEL_CONTACT_ICON)

        self.add_contact = QtGui.QPushButton(add_icon, '')
        self.del_contact = QtGui.QPushButton(del_icon, '')

        hl2 = QtGui.QHBoxLayout()
        hl2.addWidget(self.add_contact)
        hl2.addWidget(self.del_contact)

        vl = QtGui.QVBoxLayout()
        vl.addLayout(hl1)
        vl.addLayout(hl2)

        self.setLayout(vl)

    def addContacts(self, contacts):
        for contact in contacts:            
            item = QtGui.QListWidgetItem(QtGui.QIcon(self.LIST_ICON), contact)
            self.contacts.addItem(item)

    def onDoubleClick(self, item):
        self.parent.openChatWindow(item.text())