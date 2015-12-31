from __future__ import print_function
import logging
from libimporter import redis_connection
from cmd2 import Cmd
import time
import sys


class Application(Cmd):
    """
    Application class which contains all logics
    """
    def __init__(self):
        Cmd.__init__(self)
        logging.basicConfig(filename='/tmp/darkdashboard.log', level=logging.INFO,\
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
        self.logger = logging.getLogger("darkdashboard")
        self.prompt = 'dark> '
        self.rdb = redis_connection()
        print(self.bold(self.colorize('Welcome to DarkServer Dashboard', 'blue')))

    def bold(self, text):
        """
        returns the text as bold
        """
        return '\033[1m' + text + '\033[0m'

    def do_commands(self, line):
        """
        Show all available commands
        """
        names = [name[3:] for name in list(set(dir(self)) - set(dir(Cmd))) if name.startswith('do_')]
        names.sort()
        print(self.colorize('Available commands: \n', 'blue'))
        for name in names:
            print(self.colorize(name, 'blue'))
        print('')

    def do_status(self, line):
        """
        Show the status of the darkserver processes
        """
        print('\n')

        while True:
            print(' ' * 79, end='\r')
            status = self.rdb.get('darkjobworker')
            print(status, end='\r')
            sys.stdout.flush()
            time.sleep(1)

    def do_queue(self, line):
        """
        Shows the queue length
        """
        status = self.rdb.llen('retaskqueue-jobqueue')
        print("retaskqueue-jobqueue: %s" % status)

