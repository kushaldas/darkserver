#!/usr/bin/env python
import os
import sys
import time
import logging

import darkimporter.utils as utils
from darkimporter import libimporter
from darkimporter.libimporter import do_buildid_import
from darkimporter.libimporter import create_rundir, log_status
from darkimporter.libimporter import remove_redis_keys, get_redis_config
from darkimporter.utils import log
from retask.queue import Queue
from retask.task import Task

                

if __name__ == '__main__':
    libimporter.loadconfig()
    create_rundir()
    key = 'darkjobworker'
    config = get_redis_config()
    jobqueue = Queue('jobqueue', config)
    jobqueue.connect()
    log_status('darkjobworker', 'Starting worker module')
    while True:

        if jobqueue.length == 0:
            log(key, "Sleeping, no jobqueue job", 'info')
            time.sleep(60)
            continue
        try:
            task = jobqueue.dequeue()
            if not task:
                continue
            instance = task.data['instance']
            idx = task.data['build_id']
            distro = task.data['release']
            utils.msgtext = task.data['instance']
            log(key, "Import started %s" % idx, 'info')
            do_buildid_import(instance, idx, distro, key)
            log(key, "Import finished %s" % idx, 'info')
        except Exception, err:
            log(key, str(err), 'error')
        print "one more done or crashed"
    remove_redis_keys('darkjobworker')
