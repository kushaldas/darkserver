#!/usr/bin/env python
"""darkserver"""
from distutils.core import setup
from distutils.core import Command
import os



setup(name='darkserver',
      version='0.8.2',
      description="GNU build-id web service",
      long_description = "GNU build-id web service",
      platforms = ["Linux"],
      author="Kushal Das",
      author_email="kushaldas@gmail.com",
      url="https://github.com/kushaldas/darkserver",
      license = "http://www.gnu.org/copyleft/gpl.html",
      packages = ['darkserverweb', 'darkserverweb.buildid', 'configs/darkimporter'],
      data_files=[('/etc/httpd/conf.d/', ['configs/darkserver-httpd.conf']),
          ('/usr/sbin/', ['darkserver.wsgi', 'darkbuildqueue',\
                          'darkjobworker', 'darkproducer', 'darkdashboard']),
          ('/etc/darkserver/', ['darkserverweb/settings.py', 'configs/darkserverweb.conf',\
                                'configs/dark-distros.json', 'configs/darkjobworker.conf',\
                                'configs/redis_server.json', 'configs/email.json']),
          ('/usr/share/darkserver/static', ['static/index.html', 'static/404.html', \
                                            'static/500.html']), ]

      )
