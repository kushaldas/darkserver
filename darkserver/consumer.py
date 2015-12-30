# -*- coding: utf-8 -*-

import fedmsg.consumers

import logging
log = logging.getLogger("fedmsg")

class DarkserverConsumer(fedmsg.consumers.FedmsgConsumer):
    topic = 'org.fedoraproject.dev.__main__.buildsys.build.state.change'
    config_key = 'darkserver.consumer.enabled'

    def __init__(self, *args, **kwargs):
        super(DarkserverConsumer, self).__init__(*args, **kwargs)
        print 'DarkserverConsumer ready for action'

    def consume(self, msg):
        print msg
