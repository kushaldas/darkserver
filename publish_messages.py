import random
import json
import fedmsg
import time

count = 0
with open('fixtures.json', 'r') as infile:
    raw_messages= json.load(infile)
    for count,raw_message in enumerate(raw_messages):
        number = random.randint(1, 11)
        time.sleep(1)
        if raw_message['msg']['new'] != 1:
            continue
        fedmsg.publish(msg=raw_message['msg'], topic='buildsys.build.state.change')
        count += 1
