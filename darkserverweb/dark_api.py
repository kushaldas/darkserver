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
import MySQLdb
import ConfigParser
from buildid.models import *

config = ConfigParser.ConfigParser()
config.read('/etc/darkserver/darkserverweb.conf')
dbhost = config.get('darkserverweb','host')
dbuser =  config.get('darkserverweb','user')
dbpassword = config.get('darkserverweb','password')
dbname =  config.get('darkserverweb','database')
conn = None
try:
    conn = MySQLdb.connect (host = dbhost,
                            user = dbuser,
                            passwd = dbpassword,
                            db = dbname)
except Exception, error:
    print error.message

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
        result.append(data)

    return json.dumps(result)


def get_koji_download_url(pkg_name, \
                kojiurl="http://koji.fedoraproject.org/kojihub", \
                pkg_url="http://koji.fedoraproject.org/packages"):
    """Returns download URL for packages from koji
    """
    if not pkg_name.endswith('.rpm'):
        pkg_name = pkg_name + '.rpm'
    kc = koji.ClientSession(kojiurl, \
                                {'debug': False, 'password': None, \
                                     'debug_xmlrpc': False, 'user': None})
    rpm_result = kc.search(pkg_name, "rpm", "glob")
    if not rpm_result:
        return json.dumps({'error': 'rpm not found'})
    rpm_id = rpm_result[0]["id"]
    rpm_info = kc.getRPM(rpm_id)
    fname = koji.pathinfo.rpm(rpm_info)
    parent_build_id = rpm_info["build_id"]
    parent_build_info = kc.getBuild(parent_build_id)
    url = '%s/%s/%s/%s/%s' % (pkg_url, parent_build_info['name'], \
                                  parent_build_info['version'], \
                                  parent_build_info['release'], \
                                  fname)
    return json.dumps({'url':url})


def write_info(username, password, data):
    user = Darkuser.objects.filter(name=username,password=password)
    if len(user) == 1:
        info = json.loads(data)
        if type(info) == type([1,2]):
            for row in info:
                if len(row) == 5:
                    g = Gnubuildid()
                    g.elfname = row[0]
                    g.instpath = row[1]
                    g.build_id = row[2]
                    g.rpm_name = row[3]
                    g.distro = row[4]
                    g.save()
        else:
            return "Wrong json data " + str(type(info))
        return "Authenticated, information saved"
    return "Wrong credentials"

if __name__ == '__main__':
    from pprint import pprint
    pprint(parsepath('/rpm?name=yum&base=105&release=78'))
