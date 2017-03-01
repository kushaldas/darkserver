#!/usr/bin/env python

from setuptools import setup

setup(
    name='darkserver',
    version='2.0',
    description="GNU build-id web service",
    long_description = "GNU build-id web service",
    platforms = ["Linux"],
    author="Kushal Das",
    author_email="mail@kushaldas.in",
    url="https://github.com/kushaldas/darkserver",
    license = "http://www.gnu.org/copyleft/gpl.html",
    packages = ['darkweb', 'darkserverweb.buildid', 'darkimporter', 'darkserver'],
    data_files=[('/etc/httpd/conf.d/', ['darkserver-httpd.conf']),
        ('/usr/sbin/', ['darkserver.wsgi',]),
        ('/etc/darkserver/', ['data/koji_info.json', 'data/darkjobworker.conf',]),
        ('/usr/share/darkserver/', ['darkjobworker.py']),],
    entry_points={
        'moksha.consumer': [
            "darkserver.consumer = darkserver.consumer:DarkserverConsumer",
        ],
    },
)
