import os
import sys
import logging
imppath = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, imppath)
from darkimporter.utils import log, send_mail


logging.basicConfig(level=logging.INFO,\
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

def test_log(caplog):
    log('mylog', 'test message', 'info')
    with caplog.atLevel(logging.INFO):
        assert caplog.text() == 'utils.py                    42 INFO     test message\n'
