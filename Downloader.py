import os

import multiprocessing as mp

import requests

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from logger import Logger


class Downloader(QThread):
    def __init__(self,
                 name='Downloader',
                 nprocs=2,
                 log_dir='.',
                 parent=None):
        QThread.__init__(self, parent)
        self.name = name
        self.nprocs = nprocs
        self.log = Logger(name, save_dir=log_dir)
        self.exiting = False
        self.args = None
        self.dl_queue = mp.Queue()

    def __del__(self):
        self.exiting = True
        self.wait()

    def download(self):
        [self.dl_queue.put(None) for _ in range(self.nprocs)]
        dl_procs = [mp.Process(target=self.download_func)
                    for _ in range(self.nprocs)]

        self.log('Starting {} downloads in {} threads'
                 .format(len(self.args), self.nprocs))

        for proc in dl_procs:
            proc.start()

        [proc.join() for proc in dl_procs]
        return 0

    def download_func(self):
        while True:
            arg = self.dl_queue.get()
            if arg is None:
                break
            if self.exiting:
                self.log('Download cancel requested')
                return -1
            url, dl_path = arg
            with open(dl_path, 'wb') as file:
                res = requests.get(url, stream=True)
                if res.headers.get('content-length') is None:
                    file.write(res.content)
                else:
                    for data in res.iter_content():
                        file.write(data)
            file_name = os.path.split(dl_path)[1]
            self.log('{} written'.file_name)

    def run(self):
        self.download()
        self.log('Download of {} files completed'.format(len(self.args)))


if __name__ == '__main__':
    pa = os.path.realpath('patch.png')
    pa2 = os.path.realpath('bun.png')
    args = [('http://imgs.xkcd.com/comics/patch.png', pa),
            ('http://imgs.xkcd.com/comics/bun.png', pa2)]
    dl = Downloader()
    dl(args)
