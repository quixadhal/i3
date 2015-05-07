# -*- coding: utf-8 -*- line endings: unix -*-
__author__ = 'quixadhal'

import os
import sys
import time
import socket
import select
import log_system
import db_system

logger = log_system.init_logging()
sys.path.append(os.getcwd())

if __name__ == '__main__':
    logger.boot('System booting.')
    config = db_system.init_db()
    logger.info(config)
    logger.critical('System halted.')
