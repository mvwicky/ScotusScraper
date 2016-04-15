import sys
import os

from datetime import datetime


class Logger(object):
    """class that logs output to a log file and stdout"""
    def __init__(self, name, save_dir=None, attr=None, ovrw=False):
        """Constructor
           name: the name for the log file
           attr: an optional additional name for the file
           save_dir: folder name to save in
           ovrw: whether or not to overwrite and existing file
        """
        [name, save_dir] = map(str, [name, save_dir])

        today = '-'.join(map(str, [datetime.today().year,
                                   datetime.today().month,
                                   datetime.today().day]))

        if attr:
            log_name = '_'.join([name, str(attr), today])
        else:
            log_name = '_'.join([name, today])
        log_name = ''.join([log_name, '.log'])

        if save_dir:
            self.log_path = os.path.abspath(save_dir)
            if not os.path.exists(self.log_path):
                try:
                    os.makedirs(self.log_path)
                except:
                    self.log_path = os.getcwd()
        else:
            self.log_path = os.getcwd()
        self.log_path = os.path.join(self.log_path, log_name)

        if ovrw:
            log = open(self.log_path, 'w')
            log.close()

    def __call__(self, msg, ex=False, exitCode=-1):
        """ writes to log file and stdout
            msg: message to log
            ex: whether or not to exit
            exitCode: the exit code to emit, unused if not exiting
        """
        msg = ''.join([str(msg), '\n'])
        sys.stdout.write(msg)
        sys.stdout.flush()
        now = datetime.now().strftime("%X")
        with open(self.log_path, 'a') as log:
            log.write(' -> '.join([now, msg]))
            log.flush()
        if ex:
            exitMessage = 'Exiting with code: {}\n'.format(exitCode)
            sys.stdout.write(exitMessage)
            sys.stdout.flush()
            with open(self.log_path, 'a') as log:
                log.write(' -> '.join([now, exitMessage]))
                log.flush()
            sys.exit(exitCode)


def main():
    pass

if __name__ == '__main__':
    main()
