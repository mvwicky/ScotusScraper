import os
import sys
import shutil
import urllib
import typing
import datetime

import requests
from bs4 import BeautifulSoup

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from DocDialog import DocDialog
from Downloader import Downloader

try:
    test = QString('Test')
except NameError:
    QString = str

class ScotusScraper(QMainWindow):
    ''' the main class that runs the entire program
        - member variables (non-inherited):
            - dim: the dimensions of the window 
            - base_url: the url of the supreme court website
            - trans_base: where to find argument transcripts 
            - save_dir: the base directory where files are saved
            - downloader: thread to download files
            - log_name: the name of the log file 
            - con: on screen console 
    '''
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.dim = (850, 500)

        self.base_url = 'http://supremecourt.gov/' 
        self.trans_base = '{}oral_arguments/'.format(self.base_url)
        self.save_dir = '{}\\SCOTUS\\'.format(os.getcwd())

        self.downloader = Downloader() 
        self.connect(self.downloader, SIGNAL('output(QString)'), self.send_message)

        script_name = (sys.argv[0].split('\\')[-1]).replace('.py', '.log')
        log_dir = '{}\\logs\\'.format(os.getcwd())
        self.log_name = '{}{}'.format(log_dir,script_name)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                err_log = logger('ErrorLog')
                err_log('Problem making log directory', ex=True, exitCode=-1)

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
            except :
                self.send_message('Problem making save directory')
                sys.exit(-1)
            else:
                msg = 'Save directory created: {}'.format(self.save_dir)
                self.send_message(msg)

        for year in range(2010, 2016):
            year_button = QPushButton(str(year), self)
            year_button.connect(year_button, SIGNAL('clicked()'), 
                                self.year_button_press)
            grid.addWidget(year_button, grid.rowCount(), 0)

        r = grid.rowCount()

        folder_button = QPushButton('Select Save Folder', self)
        clear_con_button = QPushButton('Clear Console', self)
        cancel_button = QPushButton('Cancel Download', self)
        clean_button = QPushButton('Clean', self)
        clear_log_button = QPushButton('Clear Log File', self)


        folder_button.connect(folder_button, SIGNAL('clicked()'), self.choose_save_folder)
        clear_con_button.connect(clear_con_button, SIGNAL('clicked()'), self.clear_console)
        cancel_button.connect(cancel_button, SIGNAL('clicked()'), self.cancel_download)
        clean_button.connect(clean_button, SIGNAL('clicked()'), self.clean)
        clear_log_button.connect(clear_log_button, SIGNAL('clicked()'), self.clear_log)

        buttons = [ folder_button,clear_con_button, cancel_button,
                    clean_button, clear_log_button ]

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
    def send_message(self, msg: str):
        msg = str(msg)
        self.statusBar().showMessage(msg)
        self.con.append('-> {}'.format(msg))
        sys.stdout.write('{}\n'.format(msg))
        sys.stdout.flush()
        now = datetime.datetime.now().strftime('%c')
        with open(self.log_name, 'a') as log:
            log.write('{} -> {}\n'.format(now, msg))
            log.flush()
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
                        self.send_message('Deleted folder: {}'.format(file_path))
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
        with open(self.log_name, 'w') as log:
            pass
        self.send_message('Log Cleared')
    def clear_console(self):
        self.send_message('Console Cleared')
        self.con.clear()
    def choose_save_folder(self):
        new_dir = QFileDialog.getExistingDirectory(caption="Select Save Folder", options=QFileDialog.ShowDirsOnly)
        self.save_dir = '{}\\'.format(new_dir)
        self.send_message('Save directory changed to: {}'.format(self.save_dir))
    def update_download_progress(self, val: str):
        msg = '[{}{}]'.format(('=' * val), ('  ' * (50 - val)))
        self.statusBar().showMessage(msg)
    def remove_not_allowed_chars(self, inp: str) -> str:
        for c in ('<','>',':','"','/','\\','|','?','*'):
            inp = inp.replace(c, '')
        return inp
    def year_button_press(self):
        year = self.sender().text()
        year_dir = '{}{}\\'.format(self.save_dir, year)
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
        self.send_message('Getting argument audio')
        audio = { 'media': '{}media/audio/mp3files/'.format(self.base_url), # url where media files are stored
                  'dir': '{}{}\\Argument Audio\\'.format(self.save_dir, year),  # local directory to save the files
                  'url': '{}oral_arguments/argument_audio/{}'.format(self.base_url, year), # specific url for this year
                  'soup': '', 'links': [], 'dockets': [], 'names': [], 'filenames': [], 'urls': [], 
                  'pairs': [] }  
        if not os.path.exists(audio['dir']):
            self.send_message('No directory for: {}'.format(audio['dir']))
            try: 
                os.makedirs(audio['dir'])
            except:
                self.send_message('Problem creating: {}'.format(audio['dir']))
                return 0
            else:
                self.send_message('Created: {}'.format(audio['dir']))
        audio['soup'] = BeautifulSoup(urllib.request.urlopen(audio['url']), 'lxml')
        for row in audio['soup'].find_all('tr'):
            for a in row.find_all('a', class_=None):
                if '../audio/' in a.get('href'):
                    audio['links'].append(a.get('href')) # link is the href in the <a> tag
                    audio['dockets'].append(a.string) # docket is the text inside the <a></a> block
                    audio['names'].append(row.find('span').string) # case name is stored inside a span next to the <a>
        audio['urls'] = ['{}{}.mp3'.format(audio['media'], i) for i in audio['dockets']]
        for d, n in zip(audio['dockets'], audio['names']):
            name = '{}'.format(self.remove_not_allowed_chars('{}-{}'.format(d, n)))
            filename = '{}{}.mp3'.format(audio['dir'], name)
            audio['filenames'].append(filename)
        audio['pairs'] = [(i, j) for i, j in zip(audio['urls'], audio['filenames'])]
        self.downloader(audio['pairs'])
    def get_slip_opinions(self, year):
        self.send_message('Getting slip opinions')
        year_dir = '{}{}\\'.format(self.save_dir, year)
        slip = { 'dir': '{}Slip Opinions\\'.format(year_dir), 
                 'url': '{}opinions/slipopinion/{}'.format(self.base_url, str(int(year) - 2000)), 
                 'soup': '', 'links': [], 'dockets': [], 'names': [], 'filenames': [],  'urls': [], 
                 'pairs': [] }      
        if not os.path.exists(slip['dir']):
            self.send_message('No directory for: {}'.format(slip['dir']))
            try:
                os.makedirs(slip['dir'])
            except:
                self.send_message('Problem creating: {}'.format(slip['dir']))
                return 0
            else:
                self.send_message('Created: {}'.format(slip['dir']))
        slip['soup'] = BeautifulSoup(urllib.request.urlopen(slip['url']), 'lxml')
        for row in slip['soup'].find_all('tr'):
            for a in row.find_all('a'):
                if '/opinions/{}pdf/'.format(str(int(year) - 2000)) in a.get('href'):
                    if ' v. ' in a.string:
                        slip['links'].append(a.get('href'))
                        slip['names'].append(a.string)
                        for cell in row.find_all('td')[2::10]:
                            docket = cell.string.replace(', ', '-').replace('.', '')
                            slip['dockets'].append(docket)
        slip['urls'] = ['http://supremecourt.gov{}'.format(i) for i in slip['links']]
        for d, n in zip(slip['dockets'], slip['names']):
            name = '{}{}.pdf'.format(slip['dir'], self.remove_not_allowed_chars('{}-{}'.format(d, n)))
            slip['filenames'].append(name)
        slip['pairs'] = [(i, j) for i, j in zip(slip['urls'], slip['filenames'])]
        self.downloader(slip['pairs'])
    def get_argument_transcripts(self, year):
        self.send_message('Getting argument transcripts for {}'.format(year))
        trans = { 'dir': '{}{}\\Argument Transcripts\\'.format(self.save_dir, year),
                  'url': '{}oral_arguments/argument_transcript/{}'.format(self.base_url, year),
                  'soup': '', 'links': [], 'dockets': [],'names': [], 'filenames': [], 'pairs': [] }
        if not os.path.exists(trans['dir']):
            self.send_message('No directory for: {}'.format(trans['dir']))
            try:
                os.makedirs(trans['dir'])
            except:
                self.send_message('Problem creating: {}'.format(trans['dir']))
                return 0 
            else:
                self.send_message('Created: {}'.format(trans['dir']))
        trans_url = '{}argument_transcript/{}'.format(self.trans_base, year)
        trans['soup'] = BeautifulSoup(urllib.request.urlopen(trans_url), 'lxml')
        for cell in trans['soup'].find_all('td'):
            for a in cell.find_all('a'):
                if 'argument_transcripts' in a.get('href'):
                    link = a.get('href').replace('../', '')
                    docket = (link.replace('argument_transcripts/', '')).replace('.pdf', '')
                    trans['dockets'].append(docket)
                    link = '{}{}'.format(self.trans_base, link)
                    trans['links'].append(link)
                    name = cell.find('span').string
                    trans['names'].append(name)
                    file_name = '{}{}{}'.format(trans['dir'], 
                                self.remove_not_allowed_chars('{}-{}'.format(docket, name)), '.pdf')
                    trans['filenames'].append(file_name)
                    trans['pairs'].append((link, file_name))
        self.downloader(trans['pairs'])


def main():
    app = QApplication(sys.argv)
    scraper = ScotusScraper()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 