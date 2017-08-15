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


file_handle = logging.FileHandler('log.txt')
file_handle.setLevel(logging.INFO)
formatter2=logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s\n')
file_handle.setFormatter(formatter2)
logger.addHandler(file_handle)
logger.setLevel(logging.INFO)


