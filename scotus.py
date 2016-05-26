#!C:\Anaconda3\python.exe

import os
import sys
import shutil
import datetime

import multiprocessing as mp

import requests
from bs4 import BeautifulSoup, SoupStrainer

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from doc_dialog import DocDialog
from downloader import Downloader
from logger import Logger
from log_listener import LogListener
from scotus_parser import ScotusParser


QString = str


class Scotus(QMainWindow):
    def __init__(self, parent=None, nprocs=4):
        QMainWindow.__init__(self, parent)
        self.dim = (850, 500)

        self.nprocs = nprocs
        self.save_dir = os.path.realpath('SCOTUS')
        self.log_dir = os.path.realpath('logs')

        self.log = Logger(name='Main', save_dir=self.log_dir)
        self.downloader = Downloader(name='Downloader',
                                     nprocs=self.nprocs,
                                     log_dir=self.log_dir,
                                     parent=self)
        self.parser = ScotusParser(name='Parser',
                                   log_dir=self.log_dir,
                                   save_dir=self.save_dir,
                                   parent=self)
        self.listener = LogListener(self.log.log_path,
                                    self.downloader.log.log_path,
                                    self.parser.log.log_path,
                                    parent=self)

        self.con = QTextEdit(self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('ScotusScraper')
        self.setWindowIcon(QIcon('Seal.png'))
        grid = QGridLayout()

        self.con.setReadOnly(True)
        self.con.setAcceptRichText(False)

        if not os.path.exists(self.save_dir):
            self.log('No save directory')
            try:
                os.makedirs(self.save_dir)
            except OSError:
                self.log('Problem making save directory')
                sys.exit(-1)
            else:
                self.log('Directory created: {}'.format(self.save_dir))

        for year in range(2010, 2016):
            year_button = QPushButton(str(year), self)
            year_button.connect(year_button,
                                SIGNAL('clicked()'),
                                self.year_button_press)
            grid.addWidget(year_button, grid.rowCount(), 0)

        r = grid.rowCount()

        folder_button = QPushButton('Select Save Folder', self)
        clear_con_button = QPushButton('Clear Console', self)
        cancel_button = QPushButton('Cancel Download', self)
        clean_button = QPushButton('Clean', self)
        clear_log_button = QPushButton('Clear Log File', self)

        folder_button.connect(folder_button,
                              SIGNAL('clicked()'),
                              self.choose_save_folder)
        clear_con_button.connect(clear_con_button,
                                 SIGNAL('clicked()'),
                                 self.clear_console)
        cancel_button.connect(cancel_button,
                              SIGNAL('clicked()'),
                              self.cancel_download)
        clean_button.connect(clean_button,
                             SIGNAL('clicked()'),
                             self.clean)
        clear_log_button.connect(clear_log_button,
                                 SIGNAL('clicked()'),
                                 self.clear_log)

        buttons = [folder_button,
                   clear_con_button,
                   cancel_button,
                   clean_button,
                   clear_log_button]

        for i, button in enumerate(buttons):
            grid.addWidget(button, r + i + 40, 0)

        grid.addWidget(self.con, 1, 1, grid.rowCount(), 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)

        self.mainWidget = QWidget(self)
        self.mainWidget.setLayout(grid)
        self.setCentralWidget(self.mainWidget)
        self.resize(*self.dim)
        self.center()
        self.log('Opening')
        self.statusBar().showMessage('')
        self.show()

    def closeEvent(self, event):
        self.log('Closing')
        event.accept()

    def year_button_press(self):
        pass

    def choose_save_folder(self):
        pass

    def clear_console(self):
        pass

    def cancel_download(self):
        pass

    def clean(self):
        pass

    def clear_log(self):
        pass

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    n = os.cpu_count()
    if n:
        scrap = Scotus(parent=None, nprocs=int(n/2))
    else:
        scrap = Scotus(parent=None, nprocs=2)
    sys.exit(app.exec_())
