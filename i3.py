# -*- coding: utf-8 -*- line endings: unix -*-
__author__ = 'quixadhal'

import os
import sys
import time
import log_system


logger = log_system.init_logging()
sys.path.append(os.getcwd())

if __name__ == '__main__':
    logger.boot('System booting.')
    logger.critical('System halted.')
