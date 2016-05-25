import os
import sys

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
        name = str(name)

        year, month, day = map(str, [datetime.today().year,
                                     datetime.today().month,
                                     datetime.today().day])
        if len(month) == 1:
            month = '0{}'.format(month)
        if len(day) == 1:
            day = '0{}'.format(day)

        today = '-'.join([year, month, day])

        if attr:
            log_name = '_'.join([name, str(attr), today])
        else:
            log_name = '_'.join([name, today])
        log_name = ''.join([log_name, '.log'])

        if save_dir:
            save_dir = str(save_dir)
            log_path = os.path.realpath(save_dir)
            if not os.path.exists(log_path):
                try:
                    os.makedirs(log_path)
                except:
                    print('Could not make log in {}, making it in cwd'
                          .format(log_path))
                    log_path = os.getcwd()
        else:
            log_path = os.getcwd()
        self.log_path = os.path.join(log_path, log_name)

        if ovrw:
            os.unlink(self.log_path)
            self.__call__('Log Overwritten')

    def __call__(self, msg, ex=False, exit_code=-1):
        """ writes to log file and stdout
            msg: message to log
            ex: whether or not to exit
            exit_code: the exit code to emit, unused if not exiting
        """
        msg = ''.join([str(msg), '\n'])
        sys.stdout.write(msg)
        sys.stdout.flush()
        now = datetime.now().strftime("%X")
        with open(self.log_path, 'a') as log:
            log.write(' -> '.join([now, msg]))
            log.flush()
        if ex:
            exit_message = 'Exiting with code: {}\n'.format(exit_code)
            sys.stdout.write(exit_message)
            sys.stdout.flush()
            with open(self.log_path, 'a') as log:
                log.write(' -> '.join([now, exit_message]))
                log.flush()
            sys.exit(exit_code)


def main():
    pass

if __name__ == '__main__':
    main()
