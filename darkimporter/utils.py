import os
import sys
import json
import logging
import traceback
from email.mime.text import MIMEText
from subprocess import Popen, PIPE


msgtext = ""


def send_mail(toaddr, fromaddr, subject, message):
    """
    Helper function to send email using sendmail.

    :arg toaddr: To address.
    :arg fromaddr: From address.
    :arg subject: Subject of the email.
    :arg message: Message of the email.
    """
    msg = MIMEText(message)
    msg["From"] = fromaddr
    msg["To"] = toaddr
    msg["Subject"] = subject
    p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
    return p.communicate(msg.as_string())


def log(name='justlog', text='', logtype='info', send_mail=True):
    """
    Logs the message for the project.

    :arg name: Name of the module which is logging
    :arg text: Text message we need to log.name
    :arg type: Type of the log message
    """
    global msgtext
    if text:
        logger = logging.getLogger(name)
        if logtype == 'info':
            logger.info(text)
        elif logtype == 'debug':
            logger.debug(text)
        elif logtype == 'error':
            logger.exception(text)
            if send_mail:
                #Email the error log
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                message = ''.join(lines)
                if msgtext:
                    message = '%s\n%s' % (msgtext, message)
                toaddr = get_email_config()
                if toaddr:
                    send_mail(toaddr, 'admin@darkserver.fedoraproject.org', 'ERROR OCCURRED: in darkserver', message)

def get_email_config(path = '/etc/darkserver/email.json'):
    """
    Returns To list of the log email
    """
    if os.path.exists(path):
        with open(path) as fobj:
            data = json.load(fobj)
            return data
    else:
        return None
