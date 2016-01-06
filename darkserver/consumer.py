# -*- coding: utf-8 -*-

import fedmsg.consumers

from retask import Task
from retask import Queue

from darkimporter.libimporter import get_redis_config

import logging
log = logging.getLogger("fedmsg")


class DarkserverConsumer(fedmsg.consumers.FedmsgConsumer):
    topic = 'org.fedoraproject.dev.__main__.buildsys.build.state.change'
    config_key = 'darkserver.consumer.enabled'

    def __init__(self, *args, **kwargs):
        super(DarkserverConsumer, self).__init__(*args, **kwargs)
        self.config = get_redis_config()
        self.jobqueue = Queue('jobqueue', self.config)
        self.jobqueue.connect()
        print 'DarkserverConsumer ready for action'

    def consume(self, msg):
        """ Consumer the koji messages
        """
        msg_body = msg['body']

        completed = msg_body['msg']['new'] == 1

        if completed:
            build_id = msg_body['msg']['build_id']
            instance = msg_body['msg']['instance']
            release = msg_body['msg']['release'].split('.')[-1]

            info = {
                'build_id': build_id,
                'instance': instance,
                'release': release,
            }

            task = Task(info)
            self.jobqueue.enqueue(task)
            log.info("In job queue %s" % build_id)
