#!/cygdrive/c/Anaconda3/python.exe

import os
import sys

import multiprocessing as mp

import requests
from bs4 import BeautifulSoup, SoupStrainer

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from logger import Logger


class ScotusParser(QThread):
    def __init__(self, name='Parser', log_dir='.', save_dir='.', parent=None):
        QThread.__init__(self, parent)
        self.name = name

        self.log_dir = os.path.realpath(log_dir)
        self.save_dir = os.path.realpath(save_dir)

        self.log = Logger(name=self.name, save_dir=self.log_dir)

        self.base_url = 'http://supremecourt.gov'

    @staticmethod
    def fmt_name(inp):
        """ cleans up file names/removes explicity disallowed characters """
        not_allowed_chars = '<>:"/\\|?*'  # Explicity not allowed characters
        for char in not_allowed_chars:
            inp = inp.replace(char, '')
        for char in ', ':  # I personally don't want these (spaces and commas)
            inp = inp.replace(char, '')
        inp = inp.replace('..', '.').replace('v.', '_v_')  # looks weird
        return os.path.normpath(inp)

    def make_dir(self, dir_path):
        if not os.path.exists(dir_path) or os.path.isfile(dir_path):
            self.log('Directory does not exist: {}'.format(dir_path))
            try:
                os.makedirs(dir_path)
            except OSError as e:
                self.log('Problem creating: {}'.format(dir_path))
                return False
            else:
                self.log('Directory created: {}'.format(dir_path))
                return True
        else:
            self.log('Directory exists: {}'.format(dir_path))
            return True

    def argument_audio(self, year):
        year = int(year)
        pairs = []
        self.log('Finding argument audio for {}'.format(year))
        audio = {'media': '/'.join([self.base_url, 'media/audio/mp3files']),
                 'dir': os.path.join(self.save_dir,
                                     str(year),
                                     'Argument_Audio'),
                 'url': '/'.join([self.base_url,
                                  'oral_arguments/argument_audio',
                                  str(year)]),
                 'search': '../audio/{year}/'.format(year=year)}

        if not self.make_dir(audio['dir']):
            return pairs

        res = requests.get(audio['url'])
        if res.status_code == 404:
            self.log('Got 404 from {}'.format(audio['url']))
            return pairs
        soup = BeautifulSoup(res.content, 'lxml')
        for rows in soup('tr'):
            for a in rows('a', class_=None):
                if audio['search'] in a.get('href'):
                    link = a.get('href')
                    docket = a.string
                    name = rows.find('span').string
                    name = self.fmt_name('{}-{}.mp3'.format(docket, name))
                    file_path = os.path.join(audio['dir'], name)
                    url = '/'.join([audio['media'], '{}.mp3'.format(docket)])
                    pairs.append((url, file_path))

                    url = url.replace(self.base_url, '')
                    file_path = os.path.relpath(file_path)
                    self.log('Found: ({url}, {file})'
                             .format(url=url, file=file_path))
        return pairs

    def slip_opinions(self, year):
        year = int(year)
        pairs = []
        self.log('Finding slip opinions for {}'.format(year))
        slip = {'dir': os.path.join(self.save_dir, str(year), 'Slip Opinions'),
                'url': '/'.join([self.base_url,
                                 'opinions',
                                 'slipopinion',
                                 str(year-2000)]),
                'filter': SoupStrainer('table', class_='table table-bordered')}

        if not self.make_dir(slip['dir']):
            return pairs

        res = requests.get(slip['url'])
        if res.status_code == 404:
            self.log('Got 404 from {}'.format(slip['url']))
            return pairs

        soup = BeautifulSoup(res.content, 'lxml', parse_only=slip['filter'])
        for rows in soup('tr'):
            docket, name = None, None
            for i, cell in enumerate(rows('td')):
                if i == 2:
                    docket = cell.string
                elif i == 3:
                    a = cell.find('a')
                    link = a.get('href')
                    url = ''.join([self.base_url, link])
                    name = a.string
            if docket and name:
                file_name = self.fmt_name('{}-{}.pdf'.format(docket, name))
                file_path = os.path.join(slip['dir'], file_name)
                pairs.append((url, file_path))

                url = url.replace(self.base_url, '')
                file_path = os.path.relpath(file_path)
                self.log('Found: ({url}, {file})'
                         .format(url=url, file=file_path))
        return pairs

    def argument_transcripts(self, year):
        year = int(year)
        pairs = []
        self.log('Finding argument transcripts for {}'.format(year))
        script = {'dir': os.path.join(self.save_dir,
                                      str(year),
                                      'Argument Transcripts'),
                  'url': '/'.join([self.base_url,
                                   'oral_arguments',
                                   'argument_transcript',
                                   str(year)]),
                  'search': '../argument_transcripts/'}

        if not self.make_dir(script['dir']):
            return pairs

        res = requests.get(script['url'])
        if res.status_code == 404:
            self.log('Got 404 from {}'.format(script['url']))
            return pairs

        soup = BeautifulSoup(res.content, 'lxml')
        for cell in soup('td'):
            for a in cell('a'):
                if script['search'] in a.get('href'):
                    link = a.get('href').replace('../', '')
                    docket = link.replace('argument_transcripts/', '')
                    docket = docket.replace('.pdf', '')
                    url = '/'.join([self.base_url, 'oral_arguments', link])
                    name = cell.find('span').string
                    file_name = self.fmt_name('{}-{}.pdf'.format(docket, name))
                    file_path = os.path.join(script['dir'], file_name)
                    pairs.append((url, file_path))

                    url = url.replace(self.base_url, '')
                    file_path = os.path.relpath(file_path)
                    self.log('Found: ({url}, {file})'
                             .format(url=url, file=file_path))
        return pairs


if __name__ == '__main__':
    p = ScotusParser(log_dir='logs', save_dir='SCOTUS')
    p.argument_audio(2015)
    p.slip_opinions(2015)
    p.argument_transcripts(2015)
