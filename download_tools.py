import os

from multiprocessing import Queue, Process, cpu_count

import requests

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from logger import Logger

QString = str


def download_func(func, q_in, q_out):
    while True:
        i, x = q_in.get()
        if i is None:
            break
        q_out.put((i, func(x)))


def download(arg):
    with open(arg[1], 'wb') as file:
        res = requests.get(arg[0], stream=True)
        if res.headers.get('content-length') is None:
            file.write(res.content)
        else:
            for data in res.iter_content():
                file.write(data)
    return 0


class Downloader(QThread):
    """downloads the requested documents"""
    def __init__(self, name='Downloader', nprocs=2, log_dir='.', parent=None):
        QThread.__init__(self, parent)
        self.name = name
        self.nprocs = nprocs
        self.log = Logger(self.name, save_dir='logs')
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

    def download_par(self):
        if not self.arg:
            self.log('No arguments received')
            return 0
        num_files = len(self.arg)
        start_msg = 'Starting download of {} files'.format(num_files)

        in_queue = Queue(1)
        out_queue = Queue()
        procs = [Process(target=download_func,
                         args=(download, in_queue, out_queue))
                 for _ in range(self.nprocs)]

        for proc in procs:
            proc.daemon = False
            proc.start()

        sent = [in_queue.put((i, x)) for i, x in enumerate(self.arg)]
        [in_queue.put((None, None)) for _ in range(self.nprocs)]
        ret = [out_queue.get() for _ in range(len(sent))]

        [proc.join() for proc in procs]

        return [x for i, x, in ret]

    def run(self):
        self.download_par()
        self.log('Download of {} files completed'.format(len(self.arg)))


if __name__ == '__main__':
    pass
