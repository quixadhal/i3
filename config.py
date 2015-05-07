# -*- coding: utf-8 -*- line endings: unix -*-
__author__ = 'quixadhal'


from sqlalchemy import Column, Integer, String, Boolean, DateTime
import log_system
from db_system import DataBase, Session

logger = log_system.init_logging()


class Config(DataBase):
    __tablename__ = 'config'
    router_name = Column(String, primary_key=True)
    password = Column(Integer)
    mudlist_id = Column(Integer)
    chanlist_id = Column(Integer)
    login_port = Column(Integer)
    i3_tcp_port = Column(Integer)
    i3_udp_port = Column(Integer)
    lib_version = Column(String)
    lib_name = Column(String)
    driver_version = Column(String)
    mud_type = Column(String)
    admin_email = Column(String)

    def __repr__(self):
        return "<Config(" + \
               "router_name = '%s'," \
               "password = %d," \
               "mudlist_id = %d," \
               "chanlist_id = %d," \
               "login_port = %d," \
               "i3_tcp_port = %d," \
               "i3_udp_port = %d," \
               "lib_version = '%s'," \
               "lib_name = '%s'," \
               "driver_version = '%s'," \
               "mud_type = '%s'," \
               "admin_email = '%s'," \
               ")>" % (
                   self.router_name,
                   self.password,
                   self.mudlist_id,
                   self.chanlist_id,
                   self.login_port,
                   self.i3_tcp_port,
                   self.i3_udp_port,
                   self.lib_version,
                   self.lib_name,
                   self.driver_version,
                   self.mud_type,
                   self.admin_email
               )


def setup_default():
    logger.info('Initializing default config entry')
    session = Session()
    config = Config()
    config.router_name = '*i4'
    config.password = 0
    config.mudlist_id = 0
    config.chanlist_id = 0
    config.login_port = 1234
    config.i3_tcp_port = 1235
    config.i3_udp_port = 1235
    config.lib_version = 'Py3 0.1'
    config.lib_name = 'Py3'
    config.driver_version = 'Py3 0.1'
    config.mud_type = 'I3 client'
    config.admin_email = 'quixadhal@gmail.com'
    session.add(config)
    session.commit()
