# Copyright 2011 Red Hat Inc.
# Author: Kushal Das <kdas@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.
from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'darkserver.views.home', name='home'),
    # url(r'^darkserver/', include('darkserver.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(u(r'^static/(?P<path>.*)$'),
        'django.views.static.serve', {
            'document_root': MEDIA_ROOT,
        },  
        name='static'
    ),
    url(r'^buildids/(?P<ids>.+)', 'views.buildids'),
    url(r'^rpm2buildids/(?P<name>.+)', 'views.rpm2buildids'),
)
