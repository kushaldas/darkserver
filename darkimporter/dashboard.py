from __future__ import print_function
import logging
from libimporter import redis_connection
from cmd2 import Cmd
import time
import sys
import os


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

        line = line.strip()
        if not line or not line.startswith('darkjobworker:'):
            self.print_all_status()
            return
        while True:
            print(' ' * 79, end='\r')
            status = self.rdb.get(line)
            print(status, end='\r')
            sys.stdout.flush()
            time.sleep(1)

    def do_queue(self, line):
        """
        Shows the queue length
        """
        status = self.rdb.llen('retaskqueue-jobqueue')
        status2 = self.rdb.llen('retaskqueue-buildqueue')
        print("retaskqueue-jobqueue: %s" % status)
        print("retaskqueue-buildqueue: %s" % status2)

    def do_shutdown(self, line):
        """
        Shutdown various processes

        Example calls:
        shutdown darkproducer
        shutdown darkbuildqueue
        shutdown darkjobworker:8390

        """
        line = line.strip()
        if not line:
            return
        if line.startswith('darkjobworker:'):
            process_id = line.split(':')[1]
            self.rdb.set('shutdown:%s' % process_id, 1)
        elif line.startswith('darkproducer'):
            process_id = self.get_process_id('darkproducer')
            if process_id:
                self.rdb.set('shutdown:%s' % process_id, 1)
        elif line.startswith('darkbuildqueue'):
            process_id = self.get_process_id('darkbuildqueue')
            if process_id:
                self.rdb.set('shutdown:%s' % process_id, 1)
        elif line.startswith('workers'):
            for key in self.rdb.keys('darkjobworker:*'):
                process_id = key.split(':')[1]
                self.rdb.set('shutdown:%s' % process_id, 1)
                print("Setting shutdown notice to %s" % key)

    def print_all_status(self):
        """
        Print status of running processes.
        """
        producer = self.rdb.get('darkproducer-status')
        color = 'green' if producer == '1' else 'red'
        status = 'running' if producer == '1' else 'stopped'
        print(self.bold("Producer\t\t"), end='')
        print(self.bold(self.colorize(status, color)), end='\n')

        # For Build worker
        builder = self.rdb.get('darkbuildqueue-status')
        color = 'green' if builder == '1' else 'red'
        status = 'running' if builder == '1' else 'stopped'
        print(self.bold("Buildworker\t\t"), end='')
        print(self.bold(self.colorize(status, color)), end='\n')

        # Print all running darkjobworker
        print(self.bold('\nRunning instances of darkjobworker:'))
        for key in self.rdb.keys('darkjobworker:*'):
            print(key)

        print('\n')

    def get_process_id(self, name):
        if os.path.exists('/var/run/darkserver/%s.pid' % name):
            process_id = open('/var/run/darkserver/%s.pid' % name).read()
            process_id = process_id.strip()
            return process_id
        else:
            return None
