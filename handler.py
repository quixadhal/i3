# -*- coding: utf-8 -*- line endings: unix -*-
__author__ = 'quixadhal'

import log_system
from packet import I3Packet
from config import Config

logger = log_system.init_logging()


class I3Handler(object):
    def recv_startup_reply(self, packet: I3Packet):
        pass

    def send_startup_reply(self, config: Config):
        supported_services = ['auth', 'channel', 'locate', 'tell', 'who']
        extra_services = []

        packet_data = [
            'startup-req-3',
            5,
            config.router_name,
            0,
            0,
            config.password,
            config.mudlist_id,
            config.chanlist_id,
            config.login_port,
            config.i3_tcp_port,
            config.i3_udp_port,
            config.lib_version,
            config.lib_name,
            config.driver_version,
            config.mud_type,
            config.admin_email,
            supported_services,
            extra_services
        ]

        p = I3Packet(raw_data=packet_data)
        return p.bytestream

    def handle_packet(self, raw_bytestream: bytes):
        p = None
        try:
            p = I3Packet(raw_bytestream=raw_bytestream)
        except (ValueError or TypeError) as err:
            logger.error(err)
            return

        if p.data[0] in self.service_list:
            self.service_list[p.data[0]](p)
        else:
            logger.error('Unknown service, return an error packet.')

    def __init__(self):
        self.router = None
        self.mudlist = []
        self.chanlist = []
        self.service_list = {
            'startup-reply': self.recv_startup_reply,
        }
