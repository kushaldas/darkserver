import os
import sys
import logging
imppath = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, imppath)
import darkimporter.utils
from darkimporter.utils import log, send_mail, get_email_config
from mock import patch


logging.basicConfig(level=logging.INFO,\
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')


def test_log(caplog):
    log('mylog', 'test message', 'info')
    with caplog.atLevel(logging.INFO):
        assert caplog.text() == 'utils.py                    42 INFO     test message\n'
    log('mylog', 'test message', 'debug')
    assert caplog.text().split('\n')[1] == 'utils.py                    44 DEBUG    test message'


def test_exception(caplog):
    with patch('darkimporter.utils.Popen') as mock_popen:
        with patch('darkimporter.utils.get_email_config') as mock_email:
            darkimporter.utils.msgtext = 'hello'
            mock_email.return_value = "kushaldas@gmail.com"
            try:
                1/0
            except Exception, err:
                log('mylog', err.message, 'error')


def test_send_email():
    with patch('darkimporter.utils.Popen') as mock_popen:
        mock_popen.communicate.return_value = True
        assert send_mail('kushaldas@gmail.com', 'd@example.com',
                         'subject', 'test email')


def test_get_email_config(tmpdir):
    fobj = tmpdir.join('email.json')
    fobj.write('"kushaldas@gmail.com"')
    data = get_email_config(fobj.strpath)
    assert data, "kushaldas@gmail.com"


def test_get_email_config_none():
    data = get_email_config('/tmp/foobarxys.json')
    assert not data
