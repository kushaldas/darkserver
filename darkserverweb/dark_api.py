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

    sql = "SELECT elfname, installpath, buildid, rpm_name, distro from dark_gnubuildid where" + \
        " rpm_name='%s'" % name

    CURSOR = conn.cursor ()
    CURSOR.execute(sql)
    row = CURSOR.fetchone()

    result = []
    while row:
        data = {}
        data['buildid'] = row[2]
        data['elf'] = os.path.join(row[1],row[0])
        data['rpm'] = row[3]
        data['distro'] = row[4]
        result.append(data)
        row = CURSOR.fetchone()

    return json.dumps(result)

def find_buildids(ids):
    """
    Return the buildid details
    """

    ids = ids.split(',')
    sql = "SELECT elfname, installpath, buildid, rpm_name, distro from dark_gnubuildid where" + \
           " buildid in ('%s')" % "','".join(ids)
    CURSOR = conn.cursor ()
    CURSOR.execute(sql)
    row = CURSOR.fetchone()


    result = []
    while row:
        data = {}
        data['buildid'] = row[2]
        data['elf'] = os.path.join(row[1],row[0])
        data['rpm'] = row[3]
        data['distro'] = row[4]
        result.append(data)
        row = CURSOR.fetchone()

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


if __name__ == '__main__':
    from pprint import pprint
    pprint(parsepath('/rpm?name=yum&base=105&release=78'))
