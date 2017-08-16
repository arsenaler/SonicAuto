#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

file_handle = logging.FileHandler('log.json')
file_handle.setLevel(logging.INFO)
formatter2=logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s\n')
file_handle.setFormatter(formatter2)
logger.addHandler(file_handle)
logger.setLevel(logging.INFO)


def use_logging(level):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if level == 'info':
                logger.info('now we will run %s'%func.__name__)
            elif level == 'debug':
                logger.debug('now we will debug %s'%func.__name__)
            elif level == 'warn':
                logger.warn('now the %s has warn information'%func.__name__)
                func(*args, **kwargs)
            elif level == 'critical':
                logger.critical('now the %s has critical information'%func.__name__)
            elif level == 'error':
                logger.error('now the %s has error information'%func.__name__)
            else:
                logger.exception('exception happen')
            return func(*args, **kwargs)
        return wrapper
    return decorator