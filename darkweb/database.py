#-*- coding: UTF-8 -*-
# Copyright (C) 2017 Kushal Das <mail@kushaldas.in>

import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session



BASE = declarative_base()

def create_session(db_url, debug=False):
    engine = sa.create_engine(db_url, echo=debug)
    scopedsession = scoped_session(sessionmaker(bind=engine))
    return scopedsession


class Buildid(BASE):
    "The buildid table"
    __tablename__ = 'buildid_gnubuildid'

    id = sa.Column(sa.Integer, primary_key=True)
    elfname = sa.Column(sa.TEXT, nullable=False)
    instpath = sa.Column(sa.TEXT, nullable=False)
    build_id = sa.Column(sa.TEXT, nullable=False)
    rpm_name = sa.Column(sa.TEXT, nullable=False)
    distro = sa.Column(sa.TEXT, nullable=False)
    kojibuildid = sa.Column(sa.INTEGER, nullable=False)
    koji_type = sa.Column(sa.TEXT, nullable=False)
    rpm_url = sa.Column(sa.TEXT, nullable=False)

    def __repr__(self):
        return u'<BuildID: %s %s %s %s>' % (self.elfname, self.instpath, self.build_id, self.rpm_name)