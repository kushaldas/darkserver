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

def buildids(request, ids):
    return HttpResponse(json.dumps({'id':ids}), mimetype='application/json')

def buildids(request, name):
    return HttpResponse(json.dumps({'name':name}), mimetype='application/json')