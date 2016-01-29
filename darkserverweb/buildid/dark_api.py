# Copyright 2011 Red Hat Inc.
# Author: Kushal Das <kdas@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import os
import json
import koji
import hashlib
import MySQLdb
import ConfigParser
from .models import *


def parsepath(path):
    """
    Parse the url and send the details back in a tuple
    """

    data = path.split('?')
    values = {}
    if len(data) > 1:
        for x in data[1].split('&'):
            tmp = x.split('=')
            values[tmp[0]] = tmp[1]

    return data[0], values

def find_rpm_details(name):
    """
    Return GNU build-id details for a rpm
    """
    if name.endswith('.rpm'):
        name = name[:-4]

    rows = Gnubuildid.objects.filter(rpm_name=name)
    result = []
    for row in rows:
        data = {}
        data['buildid'] = row.build_id
        data['elf'] = os.path.join(row.instpath,row.elfname)
        data['rpm'] = row.rpm_name
        data['distro'] = row.distro
        data['url'] = row.rpm_url
        result.append(data)

    return json.dumps(result)

def find_buildids(ids):
    """
    Return the buildid details
    """

    ids = ids.split(',')

    rows = Gnubuildid.objects.filter(build_id__in=ids)
    result = []
    for row in rows:
        data = {}
        data['buildid'] = row.build_id
        data['elf'] = os.path.join(row.instpath,row.elfname)
        data['rpm'] = row.rpm_name
        data['distro'] = row.distro
        data['url'] = row.rpm_url
        result.append(data)

    return json.dumps(result)


def find_rpm_url(name):
    "Find the rpm download URL"
    if name.endswith('.rpm'):
        name = name[:-4]
    url = ''
    rows = Gnubuildid.objects.filter(rpm_name=name)

    if len(rows) > 0:
        url = rows[0].rpm_url
    return json.dumps({'url':url})


if __name__ == '__main__':
    from pprint import pprint
    pprint(parsepath('/rpm?name=yum&base=105&release=78'))
