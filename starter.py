import sys
import logging
from PySide import QtGui
from contactlist import ContactList


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    app = QtGui.QApplication([])
    form = ContactList()
    form.show()
    sys.exit(app.exec_())