import os

import multiprocessing as mp

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from logger import Logger


class LogListener(QThread):
    def __init__(self, *log_paths, parent=None):
        QThread.__init__(self, parent)
        self.log_paths = []
        for elem in log_paths:
            self.log_paths.append(elem)

if __name__ == '__main__':
    pass
