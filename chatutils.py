import datetime
import codecs
import logging
import os
from PySide import QtGui


RED = (237, 47, 92)
WHITE = (255, 255, 255)


def formHtmlMessage(_from, msg):
    msg = msg.replace('<', '&#60').replace('>', '&#62')

    message = ''.join([
                       '<span style="color:#0B615E">',
                       datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S'),
                       '</span>',
                       '<span style="color:#B43104">', ' - ', _from,
                       '</span>',
                       '<pre>',
                       '<span style="color:#190B07">', msg, '</span>',
                       '</pre>'
                       '<hr><br>'
                      ])
    return message


def writeMessageToFile(_file, msg):
    path = './history/'
    if not os.path.exists(path):
        os.mkdir(path)
    try:
        f = codecs.open(path + _file + '.txt', 'a+', 'utf8')
        f.seek(0)
        f.write(msg)
        f.close()
    except IOError:
        logging.error('Cannot write to file!')


def colorWidget(widget, rgb=WHITE):
    r, g, b = rgb
    style = "QWidget { background-color: %s }"
    stylesheet = style % QtGui.QColor(r, g, b).name()
    widget.setStyleSheet(stylesheet)
