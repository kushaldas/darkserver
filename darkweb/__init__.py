#-*- coding: UTF-8 -*-
# Copyright (C) 2017 Kushal Das <mail@kushaldas.in>

import os
import flask
import ConfigParser
import database
from flask import jsonify




APP = flask.Flask(__name__)
SESSION = None

config = ConfigParser.SafeConfigParser()
config.read(['./data/darkweb.cfg', '/etc/darkserver/darkweb.cfg'])
args = {key: val for key, val in config.items('database')} if config.has_section('database') else {}
if args.get('engine','') == 'postgres':
    db_url = "postgresql://{0}:{1}@{2}/{3}".format(args['username'], args['password'],args['host'],args['dbname'])
    SESSION = database.create_session(db_url)


@APP.route('/buildids/<buildid>')
def buildids(buildid):
    "Returns the details for the given buildid"
    ids = buildid.split(",")
    rows = SESSION.query(database.Buildid).filter(database.Buildid.build_id.in_(ids))
    result = []
    for row in rows:
        data = {}
        data['buildid'] = row.build_id
        data['elf'] = os.path.join(row.instpath,row.elfname)
        data['rpm'] = row.rpm_name
        data['distro'] = row.distro
        data['url'] = row.rpm_url
        result.append(data)

    return jsonify(result)

@APP.route('/rpm2buildids/<rpm>')
def rpm2buildids(rpm):
    "Returns the details for the given rpm"
    if rpm.endswith('.rpm'):
        rpm = rpm[:-4]
    rows = SESSION.query(database.Buildid).filter(database.Buildid.rpm_name == rpm)
    result = []
    for row in rows:
        data = {}
        data['buildid'] = row.build_id
        data['elf'] = os.path.join(row.instpath,row.elfname)
        data['rpm'] = row.rpm_name
        data['distro'] = row.distro
        data['url'] = row.rpm_url
        result.append(data)
    return jsonify(result)

@APP.route('/package/<rpm>')
def package(rpm):
    "Returns the download URL for the given rpm"
    if rpm.endswith('.rpm'):
        rpm = rpm[:-4]
    rows = SESSION.query(database.Buildid).filter(database.Buildid.rpm_name == rpm)
    result = {}
    for row in rows:
        result['url'] = row.rpm_url
    return jsonify(result)

@APP.route('/serverversion')
def version():
    return jsonify({'server-version': '2.0'})

@APP.route('/')
def index():
    data = """<html>
<body>
<pre>
 __    __     _                             _              ___           _
/ / /\ \ \___| | ___  ___  _ __ ___   ___  | |_  ___      /   \__ _ _ __| | _____  ___ _ ____   _____ _ __
\ \/  \/ / _ \ |/ __|/ _ \| '_ ` _ \ / _ \ | __|/ _ \    / /\ / _` | '__| |/ / __|/ _ \ '__\ \ / / _ \ '__|
 \  /\  /  __/ | (__| (_) | | | | | |  __/ | |_| (_) |  / /_// (_| | |  |   <\__ \  __/ |   \ V /  __/ |
  \/  \/ \___|_|\___|\___/|_| |_| |_|\___|  \__|\___/  /___,' \__,_|_|  |_|\_\___/\___|_|    \_/ \___|_|



API details
===========

    * Call to find server version
        https://darkserver.fedoraproject.org/serverversion

       This will return a dictionary like {'server-version':'0.1'}

    * Call to get GNU build-id details
        https://darkserver.fedoraproject.org/buildids/0d0669e4ce89ffb335e36d41eacf3dfd04072e17

        This will return a dictionary of build-id details of 0d0669e4ce89ffb335e36d41eacf3dfd04072e17

    * Call to get GNU build-id details of an RPM
        https://darkserver.fedoraproject.org/rpm2buildids/argyllcms-1.3.6-1.fc16.i686

        This will return a dictionary of build-id details of the rpm argyllcms-1.3.6-1.fc16.i686

    * Call to get download url of a RPM
        https://darkserver.fedoraproject.org/package/argyllcms-debuginfo-1.3.6-1.fc16.i686

        This will return a download URL of the rpm in a dictionary.


==========

Send any queries to kushal@fedoraproject.org or find him on IRC, nick: kushal, #fedora-apps on freenode server.
</pre>
</body>
</html>"""
    return data