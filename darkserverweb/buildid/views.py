# Copyright 2011 Red Hat Inc.
# Author: Kushal Das <kdas@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.
from django.http import HttpResponse
import json
from dark_api import *

SERVER_VERSION = '0.5'

def buildids(request, ids):
    """
    Returns the build-id details
    """
    return HttpResponse(find_buildids(ids), mimetype='application/json')

def rpm2buildids(request, name):
    """
    Returns the build-id details for a given rpm
    """
    return HttpResponse(find_rpm_details(name), mimetype='application/json')

def package(request, name):
    """
    Returns the package download url from koji
    """
    return HttpResponse(get_koji_download_url(name), mimetype='application/json')

def index(request):
    """
    The index page
    """
    if os.path.isfile('/usr/share/darkserver/static/index.html'):
        path = '/usr/share/darkserver/static/index.html' # pragma: no cover
    else:
        path = '../static/index.html'
    data = open(path).read()
    return HttpResponse(data)

def serverversion(request):
    """
    The server version
    """
    return HttpResponse(json.dumps({'server-version':SERVER_VERSION}), mimetype='application/json')


