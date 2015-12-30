#!/usr/bin/env python
import os
import sys
import json
import logging
import requests
import fedmsg

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

url = 'https://apps.fedoraproject.org/datagrepper/raw'
params = {
    'topic': 'org.fedoraproject.prod.buildsys.build.state.change',
    'rows_per_page': 100,
}


FILEPATH = os.getcwd() + '/fixtures.json'

if os.path.exists(FILEPATH) and not os.stat(FILEPATH).st_size == 0:
    choice = int(raw_input("A fixture file with data already exists. "
                           "Do you want to continue? (0-Yes, 1-No)\n"))

    if choice:
        sys.exit(0)

with open('fixtures.json', 'w') as outfile:
    counter = 1
    builds = []
    result_dict = []

    while True:
        try:
            params.update({'page': counter})

            logger.debug('Sending request to datagrepper')
            resp = requests.get(url, params=params)

            if resp.status_code != 200:
                continue

            logger.debug('Fetched request from datagrepper')

            if callable(resp.json):
                result_dict.extend(resp.json()['raw_messages'])
            else:
                result_dict.extend(resp.json)

            counter += 1
        except KeyboardInterrupt:
            choice = int(raw_input("Enter your choice (0:continue, 1:quit)\n"))
            if choice:
                json.dump(result_dict, outfile)
                sys.exit(0)
            else:
                logger.info(builds)
                print '\n'.join(msg_ids)
