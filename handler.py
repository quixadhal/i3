# -*- coding: utf-8 -*- line endings: unix -*-
__author__ = 'quixadhal'

import packet


def decode_packet(text: str):
    # We assume the caller has converted the raw packet into a string,
    # stripping off the leading length bytes, and the trailing NUL.

    p = packet.I3Packet(text=text)

    pass
