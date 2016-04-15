import os

import multiprocessing as mp

from multiprocessing import Queue, Process, cpu_count

import requests

from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    test = QString('Test')
except NameError:
    QString = str


def download_par(link_url_tups):
    arg = link_url_tups
    num_files = len(arg)

    nprocs = 2
    in_queue = Queue(1)
    out_queue = Queue()
    procs = [Process(target=download_func,
                     args=(download, in_queue, out_queue))
             for _ in range(nprocs)]
    for proc in procs:
        proc.daemon = True
        proc.start()

    sent = [in_queue.put((i, x)) for i, x in enumerate(arg)]
    [in_queue.put((None, None)) for _ in range(nprocs)]
    ret = [out_queue.get() for _ in range(len(sent))]

    [proc.join() for proc in procs]

    return [x for i, x, in ret]


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
    def __init__(self, nprocs=2, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.nprocs = nprocs
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
            self.emit(SIGNAL('output(QString)'), 'No arguments received')
            return 0
        num_files = len(self.arg)
        start_msg = 'Starting download of {} files'.format(num_files)
        self.emit(SIGNAL('QString'), start_msg)

        in_queue = Queue(1)
        out_queue = Queue()
        procs = [Process(target=download_func,
                         args=(download, in_queue, out_queue))
                 for _ in range(self.nprocs)]

        for proc in procs:
            proc.daemon = True
            proc.start()

        sent = [in_queue.put((i, x)) for i, x in enumerate(arg)]
        [in_queue.put((None, None)) for _ in range(nprocs)]
        ret = [out_queue.get() for _ in range(len(sent))]

        [proc.join() for proc in procs]

        return [x for i, x, in ret]

        for proc in procs:
            proc.daemon = True
            proc.start()
        sent = [in_queue.put((i, x)) for i, x in enumerate(self.arg)]
        [in_queue.put((None, None)) for _ in range(cpu_count())]
        ret = [out_queue.get() for _ in range(len(sent))]

        [proc.join for proc in procs]
        return [x for i, x in ret]

    def download(self, q_in, q_out):
        while True:
            i, x = q_in.get()
            if i is None:
                break
            ret = 0
            if os.path.isfile(arg[1]):
                self.emit(SIGNAL('output(QString)'),
                          QString('File {} already exists, skipping'
                                  .format(arg[1])))
                ret = -1
            else:
                with open(x[1], 'wb') as file:
                    res = requests.get(x[0], stream=True)
                    dl_msg = 'Downloading: {}'.format(x[0])
                    self.emit(SIGNAL('output(QString)'), dl_msg)
                    if res.headers.get('content-length') is None:
                        file.write(res.content)
                    else:
                        t_len = float(res.headers.get('content-length'))
                        fmt_len = '{}K'.format(total_length / 1000)
                        len_msg = 'Total Length: {}'.format(fmt_len)
                        self.emit(SIGNAL('output(QString)'), QString(len_msg))
                        for data in res.iter_content():
                            file.write(data)
                        done_msg = 'Saved to: {}'.format(x[1])
                        self.emit(SIGNAL('output(QString)'), done_msg)
                        ret = 0
            q_out.put((i, ret))

    def run(self):
        self.download_par()
        self.emit(SIGNAL('output(QString)'),
                  QString('Download of {} files completed'
                          .format(len(self.arg))))
