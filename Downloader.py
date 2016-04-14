import os

import requests

from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    test = QString('Test')
except NameError:
    QString = str


class Downloader(QThread):
    """downloads the requested documents"""
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.arg = None

    def __del__(self):
        self.exiting = True
        self.wait()

    def __call__(self, arg):
        """arg: a list of tuples consisting of a url and a filename"""
        self.arg = arg
        self.exiting = False
        self.start()

    def run(self):
        """ get the file using requests, download"""
        self.emit(
            SIGNAL('output(QString)'),
            QString('Starting download of {} files'.format(len(self.arg))))
        self.emit(SIGNAL('total_files(int)'), len(self.arg))
        for i, arg in enumerate(self.arg):
            if self.exiting:
                self.emit(SIGNAL('output(QString)'), 'Cancelling download')
                return 0
            if os.path.isfile(arg[1]):
                self.emit(SIGNAL('output(QString)'),
                          QString('File {} already exists, skipping'
                                  .format(arg[1])))
                continue
            with open(arg[1], 'wb') as f:
                res = requests.get(arg[0], stream=True)
                self.emit(SIGNAL('output(QString)'), QString('Downloading: {}'
                                                             .format(arg[0])))
                self.emit(SIGNAL('output(int)'), i+1)
                if res.headers.get('content-length') is None:
                    f.write(res.content)
                else:
                    total_length = float(res.headers.get('content-length'))
                    fmt_len = '{}K'.format(total_length / 1000)
                    len_msg = 'Total Length: {}'.format(fmt_len)
                    self.emit(SIGNAL('output(QString)'), QString(len_msg))
                    for data in res.iter_content():
                        f.write(data)
                self.emit(SIGNAL('output(QString)'), QString('Saved to: {}'
                                                             .format(arg[1])))
        self.emit(SIGNAL('output(QString)'),
                  QString('Download of {} files completed'
                          .format(len(self.arg))))
