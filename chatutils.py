import datetime
import codecs
import logging
import os


def formHtmlMessage(_from, msg):
    message = ''.join(['<p style="color:#0B615E">',
                       datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S'),
                       '</p>', '<p style="color:#B43104">', _from, '</p>',
                       '<p style="color:#190B07">', msg, '</p>', '<hr><br>'])
    return message

def writeMessageToFile(_file, msg):
    path = './history/'
    if not os.path.exists(path):
        os.mkdir(path)
    try:
        f = codecs.open(path+_file+'.txt', 'a+', 'utf8')
        f.write(msg)
        f.close()
    except IOError:
        logging.error('Cannot write to file!')