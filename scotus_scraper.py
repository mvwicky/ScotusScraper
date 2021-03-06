#!/cygdrive/c/Anaconda3/python.exe

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


QString = str


class ScotusScraper(QMainWindow):
    """ the main class that runs the entire program
        - member variables (non-inherited):
            - dim: the dimensions of the window
            - base_url: the url of the supreme court website
            - save_dir: the base directory where files are saved
            - downloader: thread to download files
            - log_name: the name of the log file
            - con: on screen console
    """
    def __init__(self, parent=None, nprocs=4):
        QMainWindow.__init__(self, parent)
        self.dim = (850, 500)

        self.nprocs = nprocs
        self.base_url = 'http://supremecourt.gov/'
        self.trans_base = '{}oral_arguments/'.format(self.base_url)
        self.save_dir = os.path.abspath('SCOTUS')

        self.downloader_name = 'Scotus_Downloader'
        self.log_dir = os.path.realpath('logs')

        self.log = Logger('ScotusScraper', save_dir='logs')

        self.con = QTextEdit(self)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Scotus Scraper')
        self.setWindowIcon(QIcon('Seal.png'))
        grid = QGridLayout()

        self.con.setReadOnly(True)
        self.con.setAcceptRichText(False)

        if not os.path.exists(self.save_dir):
            self.send_message('No save directory')
            try:
                os.makedirs(self.save_dir)
            except:
                self.log('Problem making save directory', ex=True)
            else:
                msg = 'Save directory created: {}'.format(self.save_dir)
                self.send_message(msg)

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

        buttons = [folder_button, clear_con_button, cancel_button,
                   clean_button, clear_log_button]

        for i, button in enumerate(buttons):
            grid.addWidget(button, r + (40 + i), 0)

        grid.addWidget(self.con, 1, 1, grid.rowCount(), 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)

        self.mainWidget = QWidget(self)
        self.mainWidget.setLayout(grid)
        self.setCentralWidget(self.mainWidget)
        self.resize(*self.dim)
        self.center()
        self.send_message('Opening')
        self.statusBar().showMessage('')
        self.show()

    def closeEvent(self, event):
        self.send_message('Closing')
        self.downloader.quit()
        event.accept()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def send_message(self, msg):
        msg = str(msg)
        self.con.append('-> {}'.format(msg))
        self.log(msg)

    def clean(self):
        if os.path.exists(self.save_dir):
            if not os.listdir(self.save_dir):
                self.send_message('Nothing to clean')
                return 0
            for file in os.listdir(self.save_dir):
                file_path = os.path.join(self.save_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        self.send_message('Deleted file: {}'.format(file_path))
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        self.send_message('Deleted folder: {}'
                                          .format(file_path))
                except Exception as e:
                    print(e)
            if os.listdir(self.save_dir):
                self.send_message('Problem cleaning {}'.format(self.save_dir))
        else:
            self.send_message('Directory not found: {}'.format(self.save_dir))

    def cancel_download(self):
        self.send_message('Stopping Download')
        self.downloader.exiting = True

    def clear_log(self):
        self.log.delete_log()
        self.send_message('Log Cleared')

    def clear_console(self):
        self.send_message('Console Cleared')
        self.con.clear()

    def choose_save_folder(self):
        new_dir = QFileDialog.getExistingDirectory(
                    caption="Select Save Folder",
                    options=QFileDialog.ShowDirsOnly)
        if new_dir:
            self.save_dir = '{}\\'.format(new_dir)
            self.send_message('Save directory changed to: {}'
                              .format(self.save_dir))
        else:
            self.send_message('Save directory not changed')

    def set_total_files(self, val):
        self.statusBar().showMessage('')
        self.total_files = val

    def update_download_progress(self, val):
        msg = '{} of {} Downloaded'.format(val, self.total_files)
        self.statusBar().showMessage(msg)

    @staticmethod
    def fmt_name(inp):
        not_allowed_chars = '<>:"/\\|?*'  # Explicity not allowed characters
        for char in not_allowed_chars:
            inp = inp.replace(char, '')
        for char in ', ':  # I personally don't want these (spaces and commas)
            inp = inp.replace(char, '')
        inp = inp.replace('..', '.')  # looks weird
        return inp.replace('v.', '_v_')  # Make the vs. a little nicer

    def year_button_press(self):
        year = self.sender().text()
        year_dir = os.path.join(self.save_dir, year)
        res = DocDialog.dec_ret()
        if 'Cancel' in res:
            return
        if not os.path.exists(year_dir):
            self.send_message('No directory for: {}'.format(year))
            try:
                os.makedirs(year_dir)
            except:
                self.send_message('Problem creating: {}'.format(year_dir))
                return 0
            else:
                self.send_message('Directory created: {}'.format(year_dir))
        if 'Audio' in res:
            self.get_argument_audio(year)
        elif 'Slip' in res:
            self.get_slip_opinions(year)
        elif 'Transcript' in res:
            self.get_argument_transcripts(year)
        elif 'All' in res:
            self.get_argument_audio(year)
            self.get_slip_opinions(year)
            self.get_argument_transcripts(year)

    def get_argument_audio(self, year):
        self.send_message('Getting argument audio for {}'.format(year))
        audio = {'media': '{}media/audio/mp3files/'.format(self.base_url),
                 'dir': os.path.join(self.save_dir, year, 'Argument Audio'),
                 'url': '{}oral_arguments/argument_audio/{}'
                        .format(self.base_url, year)}
        if not os.path.exists(audio['dir']):
            self.send_message('No directory for: {}'.format(audio['dir']))
            try:
                os.makedirs(audio['dir'])
            except:
                self.send_message('Problem creating: {}'.format(audio['dir']))
                return 0
            else:
                self.send_message('Created: {}'.format(audio['dir']))
        res = requests.get(audio['url'])
        if res.status_code == 404:
            self.send_message('Got 404 from {}'.format(audio['url']))
            return -1
        soup = BeautifulSoup(res.content, 'lxml')
        pairs = []
        link_search = '../audio/{year}/'.format(year=year)
        for rows in soup('tr'):
            for a in rows('a', class_=None):
                if link_search in a.get('href'):
                    link = a.get('href')
                    docket = a.string
                    name = rows.find('span').string
                    name = self.fmt_name('{}-{}.mp3'.format(docket, name))
                    url = '{}{}.mp3'.format(audio['media'], docket)
                    file_path = os.path.join(audio['dir'], name)
                    pairs.append((url, file_path))
        Downloader(pairs,
                   self.downloader_name,
                   self.nprocs,
                   self.log_dir,
                   self)

    def get_slip_opinions(self, year):
        year = int(year)
        self.send_message('Getting slip opinions for {}'.format(year))
        slip = {'dir': os.path.join(self.save_dir, str(year), 'Slip Opinions'),
                'url': '{}opinions/slipopinion/{}'
                       .format(self.base_url, str(year-2000))}
        if not os.path.exists(slip['dir']):
            self.send_message('No directory for: {}'.format(slip['dir']))
            try:
                os.makedirs(slip['dir'])
            except:
                self.send_message('Problem creating: {}'.format(slip['dir']))
                return 0
            else:
                self.send_message('Created: {}'.format(slip['dir']))
        res = requests.get(slip['url'])
        table_filter = SoupStrainer('table',
                                    class_='table table-bordered')
        soup = BeautifulSoup(res.content, 'lxml', parse_only=table_filter)
        pairs = []
        for rows in soup('tr'):
            docket, name = None, None
            for i, cell in enumerate(rows('td')):
                if i == 2:
                    docket = cell.string
                if i == 3:
                    a = cell.find('a')
                    link = a.get('href')
                    url = ''.join([self.base_url, link])
                    name = a.string
            if docket and name:
                file_name = self.fmt_name('{}-{}.pdf'.format(docket, name))
                file_path = os.path.join(slip['dir'], file_name)
                pairs.append((url, file_path))
        self.downloader(pairs)

    def get_argument_transcripts(self, year):
        self.send_message('Getting argument transcripts for {}'.format(year))
        trans = {'dir': os.path.join(self.save_dir, year,
                                     'Argument Transcripts'),
                 'url': '{}oral_arguments/argument_transcript/{}'
                        .format(self.base_url, year)}
        if not os.path.exists(trans['dir']):
            self.send_message('No directory for: {}'.format(trans['dir']))
            try:
                os.makedirs(trans['dir'])
            except:
                self.send_message('Problem creating: {}'.format(trans['dir']))
                return 0
            else:
                self.send_message('Created: {}'.format(trans['dir']))
        res = requests.get(trans['url'])
        soup = BeautifulSoup(res.content, 'lxml')
        pairs = []
        link_search = '../argument_transcripts/'
        for cell in soup('td'):
            for a in cell('a'):
                if link_search in a.get('href'):
                    link = a.get('href').replace('../', '')
                    docket = link.replace('argument_transcripts/', '')
                    docket = docket.replace('.pdf', '')
                    link = '{}oral_arguments/{}'.format(self.base_url, link)
                    name = cell.find('span').string
                    file_name = self.fmt_name('{}-{}.pdf'.format(docket, name))
                    file_path = os.path.join(trans['dir'], file_name)
                    pairs.append((link, file_path))
        self.downloader(pairs)


def main():
    app = QApplication(sys.argv)
    scraper = ScotusScraper(None, 2)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
