# -*- coding: utf-8 -*-

import os
import json
import ConfigParser
import pika
import fedmsg.consumers


import logging
log = logging.getLogger("fedmsg")

class DarkserverConsumer(fedmsg.consumers.FedmsgConsumer):
    topic = 'org.fedoraproject.prod.buildsys.build.state.change'
    config_key = 'darkserver.consumer.enabled'

    def __init__(self, *args, **kwargs):
        super(DarkserverConsumer, self).__init__(*args, **kwargs)
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(['./data/rabbitmq.cfg', '/etc/darkserver/rabbitmq.cfg'])
        args = {key: val for key, val in self.config.items('rabbitmq')} if self.config.has_section('rabbitmq') else {}
        self.params = pika.ConnectionParameters(**args)
        log.info('DarkserverConsumer ready for action')

    def consume(self, msg):
        """ Consumer the koji messages
        """
        msg_body = msg['body']

        completed = msg_body['msg']['new'] == 1

        if completed:
            build_id = msg_body['msg']['build_id']
            instance = msg_body['msg']['instance']
            release = msg_body['msg']['release'].split('.')[-1]

            if release != 'el5':
                info = {
                    'build_id': build_id,
                    'instance': instance,
                    'release': release,
                }

                self.submit_data(info)
                log.info("In job queue %s" % build_id)

    def submit_data(self, data):
        "Submits the data to rabbitmq"
        # We reconnect everytime, since we won't get a notification if
        # the connection was closed.
        connection = pika.BlockingConnection(self.params)
        channel = connection.channel()
        channel.queue_declare('darkserver_importer', durable=True)
        channel.basic_publish(exchange='',
                              routing_key='darkserver_importer',
                              body=json.dumps(data),
                              properties=pika.BasicProperties(
                                delivery_mode=2
                              ))
        connection.close()
