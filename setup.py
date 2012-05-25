#!/usr/bin/env python
"""darkserver"""
from distutils.core import setup
from distutils.core import Command
import os



setup(name='darkserver',
      version='0.5.90',
      description="GNU build-id web service",
      long_description = "GNU build-id web service",
      platforms = ["Linux"],
      author="Kushal Das",
      author_email="kushaldas@gmail.com",
      url="https://github.com/kushaldas/darkserver",
      license = "http://www.gnu.org/licenses/gpl-2.0.html",
      data_files=[
          ('/etc/koji-hub/plugins/', ['koji-plugin/darkserver.conf']),
          ('/usr/lib/koji-hub-plugins/', ['koji-plugin/darkserver-plugin.py']),
          ('/etc/darkserver/', ['darkserverweb.conf'])
          ]

      )
