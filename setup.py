#!/usr/bin/env python
"""darkserver"""
from distutils.core import setup
from distutils.core import Command
import os



setup(name='darkserver',
      version='0.5.3',
      description="GNU build-id web service",
      long_description = "GNU build-id web service",
      platforms = ["Linux"],
      author="Kushal Das",
      author_email="kushaldas@gmail.com",
      url="https://github.com/kushaldas/darkserver",
      license = "http://www.gnu.org/copyleft/gpl.html",
      packages = ['darkserverweb','darkserverweb.buildid'],
      data_files=[('/etc/httpd/conf.d/', ['darkserver-httpd.conf']),
          ('/usr/sbin/', ['darkserver.wsgi']),
          ('/etc/darkserver/', ['darkserverweb/settings.py','darkserverweb.conf']),
          ('/etc/koji-hub/plugins/', ['koji-plugin/darkserver.conf']),
          ('/usr/lib/koji-hub-plugins/', ['koji-plugin/darkserver-plugin.py']),
          ('/usr/share/darkserver/static', ['static/index.html','static/404.html', \
                                            'static/500.html']),]

      )
