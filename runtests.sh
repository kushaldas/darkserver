#!/bin/sh

pushd .
cd darkserverweb/
coverage run --source buildid  manage.py test buildid
coverage -rm --omit *tests*
popd
