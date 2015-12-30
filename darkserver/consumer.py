# -*- coding: utf-8 -*-

import fedmsg.consumers

import logging
log = logging.getLogger("fedmsg")

class DarkserverConsumer(fedmsg.consumers.FedmsgConsumer):
    topic = 'org.fedoraproject.prod.buildsys.build.state.change'
    config_key = 'darkserver.consumer.enabled'

    def consume(self, msg):
        print msg
