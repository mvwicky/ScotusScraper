import os

import multiprocessing as mp

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
        self.queue = mp.Queue()

    def __del__(self):
        self.exiting = True
        self.wait()

    def __call__(self, arg):
        """arg: a list of tuples consisting of a url and a filename"""
        self.arg = arg
        self.exiting = False
        self.start()

    def download(self):
        """ get the file using requests, download"""
        while True:
            if self.exiting:
                self.emit(SIGNAL('output(QString)'), 'Cancelling download')
                return 0
            if os.path.isfile(arg[1]):
                self.emit(SIGNAL('output(QString)'),
                          QString('File {} already exists, skipping'
                                  .format(arg[1])))
                continue
            arg = self.queue.get()
            if arg is None:
                break
            res = requests.get(arg[0], stream=True)
            self.emit(SIGNAL('output(QString)'), QString('Downloading: {}'
                                                         .format(res.url)))
            self.emit(SIGNAL('output(int)'), i+1)
            with open(arg[1], 'wb') as f:
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

    def run(self):
        self.emit(
            SIGNAL('output(QString)'),
            QString('Starting download of {} files'.format(len(self.arg))))
        self.emit(SIGNAL('total_files(int)'), len(self.arg))

        for arg in self.arg:
            self.queue.put(arg)
        nprocs = 4
        procs = [mp.Process(target=self.download) for _ in range(nprocs)]
        [self.queue.put(None) for _ in range(nprocs)]

        for proc in procs:
            proc.start()
        [proc.join() for proc in procs]

        self.emit(SIGNAL('output(QString)'),
                  QString('Download of {} files completed'
                          .format(len(self.arg))))
