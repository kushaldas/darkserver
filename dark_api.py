#!/usr/bin/env python
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
import MySQLdb
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('/etc/darkserver.conf')
dbhost = config.get('darkserver','host')
dbuser =  config.get('darkserver','user')
dbpassword = config.get('darkserver','password')
dbname =  config.get('darkserver','database')
conn = None
try:
    conn = MySQLdb.connect (host = dbhost,
                            user = dbuser,
                            passwd = dbpassword,
                            db = dbname)
except Exception, error:
    print error.message
CURSOR = conn.cursor ()

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

def find_buildids(values):
    """
    Return the buildid details
    """
    try:
        ids = values['id']
    except:
        return json.dumps({'error':'wrong url parameter'})
    
    ids = ids.split(',')
    sql = "SELECT elfname, installpath, buildid, rpm_name, distro from dark_gnubuildid where" + \
           " buildid in ('%s')" % "','".join(ids)
    
    CURSOR.execute(sql)
    row = CURSOR.fetchone()
    import pprint 

    
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
        
    

if __name__ == '__main__':
    from pprint import pprint
    pprint(parsepath('/rpm?name=yum&base=105&release=78'))
