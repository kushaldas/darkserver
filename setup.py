#!/usr/bin/env python
"""ksc"""
from distutils.core import setup
from distutils.core import Command
import os



setup(name='darkserver',
      version='0.3',
      description="GNU build-id web service",
      long_description = "GNU build-id web service",
      platforms = ["Linux"],
      author="Kushal Das",
      author_email="kdas@redhat.com",
      url="https://github.com/kushaldas/darkserver",
      license = "http://www.gnu.org/copyleft/gpl.html",
      packages = ['darkserverweb'],
      data_files=[("/usr/sbin",['darkserver-import']),
          ('/etc/darkserver', ['darkserver.conf', 'darkserverweb.conf']),
          ('/etc/httpd/conf.d/', ['darkserver-httpd.conf']),
          ('/usr/sbin/', ['darkserver.wsgi']),
          ('/etc/darkserver/', ['darkserverweb/settings.py']),
          ('/usr/share/darkserver/static', ['static/index.html','static/style.css']),
          ('/usr/share/darkserver/' , ['createtable.sql']),]
      
      )
