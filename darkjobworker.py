#!/usr/bin/env python2
import json
import logging


import pika
import ConfigParser
from darkimporter import libimporter
from darkimporter.libimporter import do_buildid_import
from darkimporter.libimporter import create_rundir

from systemd.journal import JournalHandler

log = logging.getLogger('darkserver')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

def callback(ch, method, properties, body):
    data = json.loads(body)
    log.info('Received message %s' % data)
    try:
        instance = data['instance']
        idx = data['build_id']
        distro = data['release']
        log.info("Import started %s" % idx)
        do_buildid_import(instance, idx, distro, "darkjobworker")
        log.info("Import finished %s" % idx)
    except Exception, err:
        log.error(str(err))
        return
    print "one more done."
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    libimporter.loadconfig()
    create_rundir()
    config = ConfigParser.SafeConfigParser()
    config.read(['./data/rabbitmq.cfg', '/etc/darkserver/rabbitmq.cfg'])
    args = {key: val for key, val in config.items('rabbitmq')} if config.has_section('rabbitmq') else {}
    params = pika.ConnectionParameters(**args)

    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare('darkserver_importer', durable=True)
    # Make sure we leave any other messages in the queue
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue='darkserver_importer')
    try:
        log.info('Starting consuming')
        channel.start_consuming()
    except:
        log.error('Error occurred', exc_info=True)
    finally:
        channel.cancel()
        connection.close()
