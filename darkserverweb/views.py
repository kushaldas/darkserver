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

def buildids(request, ids):
    """
    Return the build-id details
    """
    return HttpResponse(find_buildids(ids), mimetype='application/json')

def rpm2buildids(request, name):
    """
    Return the build-id details for a given rpm
    """
    return HttpResponse(find_rpm_details(name), mimetype='application/json')

def index(request):
    """
    The index page
    """
    data = {'Message': 'Welcome to Darkserver, a GNU build-id details provider'}
    data['buildids'] = "Pass a comma separated build-ids for details to /buildids/"
    data['rpm2buildids'] = "Pass a rpm name to /rpm2buildids"
    return HttpResponse(json.dumps(data), mimetype='application/json')
    
    