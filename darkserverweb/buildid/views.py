# Copyright 2011 Red Hat Inc.
# Author: Kushal Das <kdas@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.
from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseServerError
import json
from dark_api import *

SERVER_VERSION = '1.0.3'

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
    return HttpResponse(find_rpm_url(name), mimetype='application/json')

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

def view404(request):
    """
    The 404 page
    """
    if os.path.isfile('/usr/share/darkserver/static/404.html'):
        path = '/usr/share/darkserver/static/404.html' # pragma: no cover
    else:
        path = '../static/404.html'
    data = open(path).read()
    return HttpResponseNotFound(data)

def view500(request):
    """
    The 500 page
    """
    if os.path.isfile('/usr/share/darkserver/static/500.html'):
        path = '/usr/share/darkserver/static/500.html' # pragma: no cover
    else:
        path = '../static/500.html'
    data = open(path).read()
    return HttpResponseServerError(data)


def serverversion(request):
    """
    The server version
    """
    return HttpResponse(json.dumps({'server-version':SERVER_VERSION}), mimetype='application/json')


