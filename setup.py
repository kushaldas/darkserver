#!/usr/bin/env python

from setuptools import setup

setup(
    name='darkserver',
    version='1.0.2',
    description="GNU build-id web service",
    long_description = "GNU build-id web service",
    platforms = ["Linux"],
    author="Kushal Das",
    author_email="mail@kushaldas.in",
    url="https://github.com/kushaldas/darkserver",
    license = "http://www.gnu.org/copyleft/gpl.html",
    packages = ['darkserverweb', 'darkserverweb.buildid', 'darkimporter', 'darkserver'],
    data_files=[('/etc/httpd/conf.d/', ['darkserver-httpd.conf']),
        ('/usr/sbin/', ['darkserver.wsgi', 'darkdashboard']),
        ('/etc/darkserver/', ['darkserverweb/settings.py', 'darkserverweb.conf',\
                            'data/koji_info.json', 'data/darkjobworker.conf',\
                            'data/redis_server.json', 'data/email.json']),
        ('/usr/share/darkserver/', ['darkjobworker.py']),
        ('/usr/share/darkserver/static', ['static/index.html', 'static/404.html', \
                                        'static/500.html']), ],
    entry_points={
        'moksha.consumer': [
            "darkserver.consumer = darkserver.consumer:DarkserverConsumer",
        ],
    },
)
