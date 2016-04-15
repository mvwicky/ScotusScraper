import sys
import os

from datetime import datetime


class Logger(object):
    """class that logs output to a log file and stdout"""
    def __init__(self, name, attr=None, save_dir=None, ovrw=False):
        """Constructor
           name: the name for the log file
           attr: an optional additional name for the file
           save_dir: folder name to save in
           ovrw: whether or not to overwrite and existing file
        """
        year = datetime.today().year
        month = datetime.today().month
        day = datetime.today().day
        today = '-'.join(map(str, [year, month, day]))

        if attr:  # use just script name
            log_name = '_'.join([name, attr, today])
        else:  # use script name and supplied attr
            log_name = '_'.join([name, today])

        log_name = '.'.join([log_name, 'log'])

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
        msg = str(msg)
        sys.stdout.write(''.join([msg, '\n']))
        sys.stdout.flush()
        now = datetime.now().strftime("%X")
        with open(self.log_path, 'a') as log:
            log.write(' -> '.join([now, msg]))
            log.write('\n')
            log.flush()
        if ex:
            exitMessage = 'Exiting with code: {}'.format(exitCode)
            sys.stdout.write(''.join([exitMessage, '\n']))
            sys.stdout.flush()
            with open(self.log_path, 'a') as log:
                log.write(' -> '.join([now, exitMessage]))
                log.write('\n')
                log.flush()
            sys.exit(exitCode)

    def delete_log(self):
        try:
            os.unlink(self.log_path)
        except:
            self('Problem deleting log file')


def main():
    pass

if __name__ == '__main__':
    main()
